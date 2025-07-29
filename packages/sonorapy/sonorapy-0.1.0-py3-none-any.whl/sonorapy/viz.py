# -*- coding: utf-8 -*-
import os

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import ScalarFormatter
from scipy.interpolate import interp1d

from .acoustics.ground_effect import ground_effect
from .acoustics.impedance import z_iir1, z_miki
from .analysis import (
    calc_3rd_octaves,
    calc_3rd_octaves_from_fft,
    calc_3rd_octaves_from_fft_db,
    calc_fft,
    calc_fft_db,
)
from .common import mean_absolute_error, relative_error
from .h5 import get_h5_dataset, get_h5_dataset_names
from .io import (
    create_video_from_images,
    get_c0,
    get_dx,
    get_point_sensors,
    get_sim_name,
    get_snr0_position,
)


# %% Surfaces
def viz_surf(z_surf, x_axis, y_axis):
    """
    Visualizes the 3D surface represented by the z_surface array using matplotlib.

    Parameters:
        z_surf (numpy.ndarray): A 2D array of surface elevation data.
        x_axis (numpy.ndarray): Array of x-coordinates.
        y_axis (numpy.ndarray): Array of y-coordinates.

    Returns:
        None: Displays a 3D plot of the surface.
    """
    Nx = x_axis.size
    Ny = y_axis.size
    Nz = z_surf.max() - z_surf.min()

    # Create a meshgrid for plotting
    x_grid, y_grid = np.meshgrid(x_axis, y_axis, indexing="ij")

    fig, ax = plt.subplots(subplot_kw={"projection": "3d"}, figsize=(4, 4))
    surf = ax.plot_surface(x_grid, y_grid, z_surf, cmap="viridis")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    ax.set_title("Surface")

    # Calculate the aspect ratio based on the range of each axis
    aspect_ratio = [Nx, Ny, Nz]
    ax.set_box_aspect(aspect_ratio)

    # Add a color bar to provide scale for the elevation data
    fig.colorbar(surf, ax=ax, shrink=0.3, aspect=5, pad=0.2)

    plt.tight_layout()
    plt.show()

    return fig, ax


def viz_surf_spectra(z_surf, x_axis, y_axis, nexp=7):
    """
    Visualizes the power spectral density (PSD) of the surface elevation array and its histogram.

    Parameters:
        z_surf (numpy.ndarray): A 2D array of surface elevation data.
        x_axis (numpy.ndarray): Array of x-coordinates.
        y_axis (numpy.ndarray): Array of y-coordinates.
        terrain_roughness_factor (float): The roughness factor for theoretical spectrum comparison.
        nexp (int): Exponent to define the size of the window for the PSD calculation.

    Returns:
        None: Displays the PSD plots and histogram of the surface elevations.
    """
    from scipy.signal import hann, welch

    # Compute sampling frequency based on grid spacing
    dx = x_axis[1] - x_axis[0]
    fs = 1 / dx

    # Calculate PSD along middle row and column
    window_size = 2**nexp
    window = hann(window_size)
    noverlap = window_size // 2

    Fx, PSDx = welch(
        z_surf[z_surf.shape[0] // 2, :], window=window, noverlap=noverlap, fs=fs
    )
    Fy, PSDy = welch(
        z_surf[:, z_surf.shape[1] // 2], window=window, noverlap=noverlap, fs=fs
    )

    # Compute PSD along diagonals
    diagonal_xy = np.diag(z_surf)
    diagonal_mxy = np.diag(np.fliplr(z_surf))
    Fxy, PSDxy = welch(
        diagonal_xy, window=window, noverlap=noverlap, fs=fs / np.sqrt(2)
    )
    Fmxy, PSDmxy = welch(
        diagonal_mxy, window=window, noverlap=noverlap, fs=fs / np.sqrt(2)
    )

    # Convert PSD to dB, handling zeros appropriately
    PSDdBx = 10 * np.log10(np.where(PSDx > 0, PSDx, np.nan))
    PSDdBy = 10 * np.log10(np.where(PSDy > 0, PSDy, np.nan))
    PSDdBxy = 10 * np.log10(np.where(PSDxy > 0, PSDxy, np.nan))
    PSDdBmxy = 10 * np.log10(np.where(PSDmxy > 0, PSDmxy, np.nan))

    # Plot PSDs and theoretical spectrum
    fig, axs = plt.subplots(1, 2, figsize=(8, 4))
    fig.suptitle("Surface Spectral Analysis")
    axs[0].plot(Fx, PSDdBx, label="X")
    axs[0].plot(Fy, PSDdBy, label="Y")
    axs[0].plot(Fxy, PSDdBxy, label="Diagonal")
    axs[0].plot(Fmxy, PSDdBmxy, label="Anti-Diagonal")
    axs[0].set_xscale("log")
    axs[0].set_xlabel("Spatial Frequency (1/m)")
    axs[0].set_ylabel("PSD (dB re 1 m²)")
    axs[0].legend()
    axs[0].set_title("Power Spectral Density")
    axs[1].hist(z_surf.ravel(), bins="auto")
    axs[1].set_xlabel("Elevation (m)")
    axs[1].set_ylabel("Frequency")
    axs[1].set_title("Elevation Histogram")

    plt.tight_layout()
    plt.show()

    return fig, axs


def viz_vns_3d(s_bcs):
    # Unpack boundary conditions
    bc_xn, bc_xp, bc_yn, bc_yp, bc_zn, bc_zp = s_bcs

    # Visualization
    fig = plt.figure()
    ax = fig.add_subplot(111, projection="3d")

    # Boundary conditions and arrow properties
    length = 0.5
    ax.quiver(bc_xn[:, 0], bc_xn[:, 1], bc_xn[:, 2], -length, 0, 0, color="r")
    ax.quiver(bc_xp[:, 0], bc_xp[:, 1], bc_xp[:, 2], length, 0, 0, color="g")
    ax.quiver(bc_yn[:, 0], bc_yn[:, 1], bc_yn[:, 2], 0, -length, 0, color="m")
    ax.quiver(bc_yp[:, 0], bc_yp[:, 1], bc_yp[:, 2], 0, length, 0, color="y")
    ax.quiver(bc_zn[:, 0], bc_zn[:, 1], bc_zn[:, 2], 0, 0, -length, color="c")
    ax.quiver(bc_zp[:, 0], bc_zp[:, 1], bc_zp[:, 2], 0, 0, length, color="k")

    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")

    plt.tight_layout()
    plt.show()


def viz_vns_2d(s_bcs, direction="XZ", plane=0):
    # Unpack boundary conditions
    bc_xn, bc_xp, bc_yn, bc_yp, bc_zn, bc_zp = s_bcs

    # Visualization
    fig, ax = plt.subplots()

    # Selecting the appropriate plane
    if direction == "XY":
        plane_idx = 2  # Z-axis index
        x_idx, y_idx = 0, 1
    elif direction == "XZ":
        plane_idx = 1  # Y-axis index
        x_idx, y_idx = 0, 2
    elif direction == "YZ":
        plane_idx = 0  # X-axis index
        x_idx, y_idx = 1, 2

    # Filter for the specified plane
    bc_xn = bc_xn[bc_xn[:, plane_idx] == plane]
    bc_xp = bc_xp[bc_xp[:, plane_idx] == plane]
    bc_yn = bc_yn[bc_yn[:, plane_idx] == plane]
    bc_yp = bc_yp[bc_yp[:, plane_idx] == plane]
    bc_zn = bc_zn[bc_zn[:, plane_idx] == plane]
    bc_zp = bc_zp[bc_zp[:, plane_idx] == plane]

    # Boundary conditions and arrow properties
    length = 0.0001
    # H Note, only tested for XZ plane, not other ones, use with caution (error should be obvious)
    if direction in ["XY", "XZ"]:
        ax.quiver(bc_xn[:, x_idx], bc_xn[:, y_idx], -length, 0, color="r", label="xn")
        ax.quiver(bc_xp[:, x_idx], bc_xp[:, y_idx], length, 0, color="g", label="xp")
    if direction in ["XY", "YZ"]:
        ax.quiver(bc_yn[:, x_idx], bc_yn[:, y_idx], 0, -length, color="m", label="yn")
        ax.quiver(bc_yp[:, x_idx], bc_yp[:, y_idx], 0, length, color="y", label="yp")
    if direction in ["XZ", "YZ"]:
        ax.quiver(bc_zn[:, x_idx], bc_zn[:, y_idx], 0, -length, color="c", label="zn")
        ax.quiver(bc_zp[:, x_idx], bc_zp[:, y_idx], 0, length, color="k", label="zp")

    ax.set_xlabel("X" if x_idx == 0 else "Y")
    ax.set_ylabel("Z" if y_idx == 2 else ("X" if y_idx == 0 else "Y"))
    plt.legend()

    plt.show()


# %% Fields
def viz_field_lines(
    h5_file, sensor_key="Full", field_name="p(x,y,z)", skip=0, viz=True
):
    # TODO: Need to fix this. 3D data read from h5 is not in same ordering ... instead of xyz seems to be zyx.
    ijk = get_snr0_position(h5_file)["ijk"]

    field_sensors_root = "/Output/Sensors/Fields/" + sensor_key + "/"
    dset_nms = get_h5_dataset_names(h5_file, field_sensors_root)
    dset_nms.sort(key=int)
    dset_paths = [field_sensors_root + idx for idx in dset_nms]

    x = get_h5_dataset(h5_file, field_sensors_root, "X")
    y = get_h5_dataset(h5_file, field_sensors_root, "Y")
    z = get_h5_dataset(h5_file, field_sensors_root, "Z")
    nx = np.size(x)
    ny = np.size(y)
    nz = np.size(z)

    lines_x = []
    lines_y = []
    lines_z = []

    print("Extracting", np.size(dset_paths), "fields")
    for dset, dset_id in zip(dset_paths, dset_nms):
        p_dset = get_h5_dataset(h5_file, dset, field_name)

        print(p_dset.shape, nx, ny, nz)
        i_idx = ijk[0]
        j_idx = ijk[1]
        k_idx = ijk[2]

        lines_x.append(p_dset[:, j_idx, k_idx])
        lines_y.append(p_dset[i_idx, :, k_idx])
        lines_z.append(p_dset[:, j_idx, k_idx])

    # y_min = np.min(lines_x)
    # y_max = np.max(lines_x)

    if viz:
        import matplotlib.animation as animation

        global ani

        fig, axs = plt.subplots(1, 3, figsize=(15, 5))

        def update(i):
            for ax in axs:
                ax.clear()

            axs[0].plot(x, lines_x[i], label="X")
            axs[1].plot(y, lines_y[i], label="Y")
            axs[2].plot(z, lines_z[i], label="Z")

            axs[0].set_title("X (t={})".format(i))
            axs[1].set_title("Y (t={})".format(i))
            axs[2].set_title("Z (t={})".format(i))

            # axs[0].set_ylim([y_min, y_max])
            # axs[1].set_ylim([y_min, y_max])
            # axs[2].set_ylim([y_min, y_max])

            for ax in axs:
                ax.legend()

        ani = animation.FuncAnimation(
            fig, update, frames=len(lines_x), interval=1000, blit=False
        )
        plt.show()

    return lines_x, lines_y, lines_z, x, y, z


def viz_field_slice(
    h5_file,
    sensor_key="Subset/0",
    field_name="p(x,y,z)",
    skip=0,
    viz=True,
    color_scale=1.0,
):
    sensor_root = "/Output/Sensors/Fields/" + sensor_key + "/"
    dset_nms = get_h5_dataset_names(h5_file, sensor_root)
    dset_nms.sort(key=int)
    dset_paths = [sensor_root + idx for idx in dset_nms]

    x = get_h5_dataset(h5_file, sensor_root, "X")
    y = get_h5_dataset(h5_file, sensor_root, "Y")
    z = get_h5_dataset(h5_file, sensor_root, "Z")

    nx = np.size(x)
    ny = np.size(y)
    nz = np.size(z)

    slice_data = []

    print("Extracting", np.size(dset_paths), "slices")
    for dset in dset_paths:
        p_dset = get_h5_dataset(h5_file, dset, field_name)
        p_dset = np.squeeze(p_dset)
        slice_data.append(p_dset)

    vmax = np.max(np.abs(slice_data)) * color_scale
    vmin = -vmax

    if viz:
        import matplotlib.animation as animation

        global ani
        fig, ax = plt.subplots()

        def init():
            im = ax.imshow(
                slice_data[0],
                extent=(x[0], x[-1], z[0], z[-1]),
                vmin=vmin,
                vmax=vmax,
                cmap="RdBu",
                origin="lower",
            )
            # plt.colorbar(im, ax=ax, label="Pressure")
            plt.title("2D Acoustic FDTD Simulation")

        def update(i):
            ax.clear()
            ax.set_title(f"2D Slice (t={i})")
            im = ax.imshow(
                slice_data[i],
                extent=(x[0], x[-1], z[0], z[-1]),
                vmin=vmin,
                vmax=vmax,
                cmap="bwr",
                origin="lower",
            )
            # plt.colorbar(im, ax=ax, label="Pressure")
            return (im,)

        ani = animation.FuncAnimation(
            fig,
            update,
            init_func=init,
            frames=len(slice_data),
            interval=1000,
            blit=False,
        )
        plt.show()

    return slice_data, x, y


# %% Points
def viz_points(
    of_name,
    window=False,
    level="LE",
    start_idx=1,
    ref_idx=1,
    db_drop=0,
    f_min=112,
    f_max=2239,
):
    """We use the convention that the first point is at the source, and the second is used as a reference"""
    sim_name = get_sim_name(of_name)
    pts = get_point_sensors(of_name)

    # Source data
    src_pt = pts[0]
    src_xyz = src_pt["xyz"]

    # Reference data
    ref_pt = pts[ref_idx]
    ref_xyz = ref_pt["xyz"]
    ref_snr_d = np.linalg.norm(ref_xyz - src_xyz)
    (ref_f0, ref_pf0) = calc_fft_db(ref_pt["t"], ref_pt["p"], window=window)
    (ref_pbf0, freq_c, freq_lo, freq_up) = calc_3rd_octaves(
        ref_pt["t"], ref_pt["p"], level
    )

    fig, axs = plt.subplots(1, 3, figsize=(15, 5))
    for pt in pts[start_idx:]:
        snr_t = pt["t"]
        if len(snr_t) == 0:
            print("Sensor", pt["id"], "skipped: no data")
            continue
        snr_p = pt["p"]
        snr_xyz = pt["xyz"]
        snr_src_d = np.linalg.norm(snr_xyz - src_xyz)

        (snr_f0, snr_pf0) = calc_fft_db(snr_t, snr_p, window=window)
        (snr_pbf0, freq_c, freq_lo, freq_up) = calc_3rd_octaves(snr_t, snr_p, level)

        axs[0].plot(snr_t, snr_p, label=f"d = {snr_src_d:.2f}")
        axs[0].set_xlabel("[s]")
        axs[0].set_ylabel("[Pa]")
        axs[0].legend()
        axs[0].grid(True)

        axs[1].plot(snr_f0, snr_pf0)
        if db_drop != 0 and pt["id"] != ref_idx:
            axs[1].plot(
                ref_f0,
                ref_pf0 - db_drop * np.log2(snr_src_d / ref_snr_d),
                ":",
                color="C0",
            )
        axs[1].set_xlabel("[Hz]")
        axs[1].set_ylabel("SPL [dB]")
        axs[1].set_xlim(f_min, f_max)
        axs[1].set_xscale("log")
        axs[1].set_xticks([125, 250, 500, 1000, 2000])
        axs[1].xaxis.set_major_formatter(ScalarFormatter())
        axs[1].grid(True)

        axs[2].plot(freq_c, snr_pbf0, ".-")
        if db_drop != 0 and pt["id"] != ref_idx:
            axs[2].plot(
                freq_c,
                ref_pbf0 - db_drop * np.log2(snr_src_d / ref_snr_d),
                ":",
                color="C0",
            )
        axs[2].set_ylabel(level + " [dB]")
        if level == "LE":
            axs[2].set_ylabel("$L_E$ [dB]")
        axs[2].set_xlim(f_min, f_max)
        axs[2].set_xscale("log")
        axs[2].set_xscale("log")
        axs[2].set_xticks([125, 250, 500, 1000, 2000])
        axs[2].xaxis.set_major_formatter(ScalarFormatter())
        axs[2].grid(True)

    fig.suptitle(sim_name)
    plt.tight_layout()
    return (fig, axs)


def viz_adiv(
    of_name,
    level="LE",
    octaves_only=True,
    ref_idx=1,
    db_drop=20,
    f_min=112,
    f_max=2239,
    title=None,
):
    """We use the convention that the first point is at the source, and the second is used as a reference"""
    sim_name = get_sim_name(of_name)
    pts = get_point_sensors(of_name)

    # Source data
    src_pt = pts[0]
    src_xyz = src_pt["xyz"]

    # Get distances to source and octave bands
    dists = []
    third_octave_bands = []
    for pt in pts[ref_idx:]:
        snr_t = pt["t"]
        if len(snr_t) == 0:
            print("Sensor", pt["id"], "skipped: no data")
            continue
        snr_p = pt["p"]
        snr_xyz = pt["xyz"]
        snr_src_d = np.linalg.norm(snr_xyz - src_xyz)
        dists.append(snr_src_d)

        (snr_pbf0, freq_c, freq_lo, freq_up) = calc_3rd_octaves(snr_t, snr_p, level)
        third_octave_bands.append(snr_pbf0)
    dists = np.array(dists)
    third_octave_bands = np.array(third_octave_bands).T

    # Analytical comparison at distance doublings
    dists_anly = 2 ** np.arange(np.ceil(np.log2(np.max(dists))) + 1)
    adiv_anly = db_drop * np.log10(dists_anly) + 11

    fig, axs = plt.subplots(1, 2, figsize=(12, 5))
    axs[0].plot(
        dists_anly, adiv_anly, "kx:", label="Theory", markersize=8, markeredgewidth=2
    )
    for i, data in enumerate(third_octave_bands):
        if octaves_only == True and i % 3 != 0:
            continue
        if freq_c[i] < f_min or freq_c[i] > f_max:
            continue
        data = data[0] - data + 11
        axs[0].plot(dists, data, ".", label=f"{freq_c[i]:.0f} Hz", markersize=8)
    axs[0].set_xlabel("Distance [m]", fontsize=12)
    axs[0].set_ylabel("$A_{div}$ [dB]", fontsize=12)
    axs[0].set_xscale("log")
    axs[0].tick_params(axis="both", which="major", labelsize=12)
    axs[0].grid(True)

    # Subplot for differences
    for i, data in enumerate(third_octave_bands):
        if octaves_only == True and i % 3 != 0:
            continue
        if freq_c[i] < f_min or freq_c[i] > f_max:
            continue
        data = data[0] - data + 11
        # Interpolate analytical to distances
        interp_adiv = np.interp(np.log2(dists), np.log2(dists_anly), adiv_anly)
        diff = data - interp_adiv
        axs[1].plot(dists, diff, ".", linewidth=2, markersize=8)
    axs[1].set_xlabel("Distance [m]", fontsize=12)
    axs[1].set_ylabel("Error [dB]", fontsize=12)
    # axs[1].set_title("Difference from Theory", fontsize=12)
    axs[1].set_xscale("log")
    axs[1].tick_params(axis="both", which="major", labelsize=12)
    axs[1].grid(True)

    fig.legend(loc=7, fontsize=12)
    if title is None:
        fig.suptitle("Free Field: " + sim_name)
    else:
        fig.suptitle(title)
    fig.tight_layout(w_pad=1.5)
    fig.subplots_adjust(right=0.85)

    return (fig, axs)


def viz_points_maxnorm(
    of_name,
    window=False,
    level="LE",
    start_idx=1,
    end_idx=None,
    f_min=112,
    f_max=2239,
):
    """We use the convention that the first point is at the source, and the second is used as a reference"""
    sim_name = get_sim_name(of_name)
    pts = get_point_sensors(of_name)
    c0 = get_c0(of_name)

    # Source data
    src_pt = pts[0]
    src_xyz = src_pt["xyz"]

    fig, axs = plt.subplots(1, 2, figsize=(10, 5))
    for pt in pts[start_idx:end_idx]:
        snr_t = pt["t"]
        if len(snr_t) == 0:
            print("Sensor", pt["id"], "skipped: no data")
            continue
        snr_p = pt["p"]
        snr_xyz = pt["xyz"]
        snr_src_d = np.linalg.norm(snr_xyz - src_xyz)

        (snr_f0, snr_pf0) = calc_fft_db(snr_t, snr_p, window=window)
        (snr_pbf0, freq_c, freq_lo, freq_up) = calc_3rd_octaves(snr_t, snr_p, level)

        axs[0].plot(snr_t, snr_p, label=f"d = {snr_src_d:.2f}")
        axs[0].set_xlabel("[s]")
        axs[0].set_ylabel("[Pa]")
        axs[0].grid(True)

        # axs[1].plot(snr_t-snr_t[0], snr_p/np.max(snr_p))
        axs[1].plot(snr_t - snr_src_d / c0, snr_p / np.max(snr_p))
        axs[1].set_xlabel("[s]")
        axs[1].set_ylabel("[Pa]")
        axs[1].grid(True)

    fig.legend(loc=7)
    fig.suptitle(sim_name)
    fig.tight_layout(w_pad=1.5)
    fig.subplots_adjust(right=0.85)
    return (fig, axs)


def viz_points_compare(
    ofile_eval,
    ofile_ref,
    acceptable_relative_error=1e-8,
    verbose=True,
    window=False,
    f_min=112,
    f_max=2239,
):
    identical = True

    name_ref = get_sim_name(ofile_ref)
    name_eval = get_sim_name(ofile_eval)
    if verbose:
        print("Comparing", name_ref, "and", name_eval)

    pts_ref = get_point_sensors(ofile_ref)
    pts_eval = get_point_sensors(ofile_eval)

    for r, e in zip(pts_ref, pts_eval):
        r_t = r["t"]
        r_p = r["p"]
        e_t = e["t"]
        e_p = e["p"]
        if len(r_t) == 0:
            if verbose:
                print(" Sensor", r["id"], "skipped: no data")
            continue
        if len(e_t) == 0:
            if verbose:
                print(" Sensor", e["id"], "skipped: no data")
            continue

        if np.shape(r_t) != np.shape(e_t):
            if verbose:
                print(
                    " Point",
                    r["id"],
                    "shape mismatch, interpolating into reference grid",
                )
            fint = interp1d(e_t, e_p, bounds_error=False)
            e_t = r_t
            e_p = fint(e_t)
        if (r_t != e_t).all():
            if verbose:
                print(" Point", r["id"], "skipped: time axis not comparable")
            continue
        if (r_p == e_p).all():
            if verbose:
                print(" Point", r["id"], "identical")
            identical &= True
            continue
        if np.isclose(r_p, e_p).all():
            if verbose:
                print(" Point", r["id"], "close but not identical")
            # continue
        else:
            if verbose:
                print(" Point", r["id"], "not similar")
        identical = False

        mae = mean_absolute_error(r_p, e_p)
        rel_err = relative_error(r_p, e_p)

        # if rel_err > acceptable_relative_error:
        if True:
            (r_f0, r_pf0) = calc_fft_db(r_t, r_p, window=window)
            (e_f0, e_pf0) = calc_fft_db(e_t, e_p, window=window)

            # Calculate the pointwise errors
            p_abs_err = np.abs(r_p - e_p)
            p_rel_err = np.abs(
                (r_p - e_p) / (np.abs(r_p) + np.abs(e_p) + np.finfo(float).eps)
            )

            pf_abs_err = np.abs(r_pf0 - e_pf0)
            pf_rel_err = np.abs(
                (r_pf0 - e_pf0) / (np.abs(r_pf0) + np.abs(e_pf0) + np.finfo(float).eps)
            )

            fig, axs = plt.subplots(2, 2, figsize=(10, 8))
            axs[0, 0].plot(r_t, r_p, label=name_ref, linestyle="-")
            axs[0, 0].plot(e_t, e_p, label=name_eval, linestyle="--")
            axs[0, 0].set_xlabel("Time [s]")
            axs[0, 0].set_ylabel("[Pa]")
            axs[0, 0].grid(True)
            axs[0, 0].legend()

            axs[1, 0].plot(r_t, p_abs_err, color="blue", alpha=0.5)
            axs[1, 0].set_xlabel("Time [s]")
            axs[1, 0].set_ylabel("Absolute Error", color="blue")
            axs[1, 0].tick_params(axis="y", labelcolor="blue")
            # Secondary y-axis
            axs102 = axs[1, 0].twinx()
            axs102.plot(r_t, p_rel_err, color="red", alpha=0.5)
            axs102.set_ylabel("Relative Error", color="red")
            axs102.tick_params(axis="y", labelcolor="red")
            axs[1, 0].grid(True)

            axs[0, 1].plot(r_f0, r_pf0)
            axs[0, 1].plot(e_f0, e_pf0)
            axs[0, 1].set_xlabel("[Hz]")
            axs[0, 1].set_ylabel("SPL [dB]")
            axs[0, 1].set_xlim(f_min, f_max)
            axs[0, 1].set_xscale("log")
            axs[0, 1].set_xticks([125, 250, 500, 1000, 2000])
            axs[0, 1].xaxis.set_major_formatter(ScalarFormatter())
            axs[0, 1].grid(True)

            axs[1, 1].plot(r_f0, pf_abs_err, color="blue", alpha=0.5)
            axs[1, 1].set_xlabel("[Hz]")
            axs[1, 1].set_ylabel("Absolute Error", color="blue")
            axs[1, 1].tick_params(axis="y", labelcolor="blue")
            axs[1, 1].set_xlim(f_min, f_max)
            axs[1, 1].set_xscale("log")
            axs[1, 1].set_xticks([125, 250, 500, 1000, 2000])
            axs[1, 1].xaxis.set_major_formatter(ScalarFormatter())
            # axs[1,1].grid(True)
            # Secondary y-axis
            axs112 = axs[1, 1].twinx()
            axs112.plot(e_f0, pf_rel_err, color="red", alpha=0.5)
            axs112.set_ylabel("Relative Error", color="red")
            axs112.tick_params(axis="y", labelcolor="red")
            axs[1, 1].grid(True)

            fig.suptitle("Point " + str(r["id"]))
            plt.tight_layout()

            print(f"  MAE: {mae:.6f}")
            print(f"  MRE: {rel_err:.6f}")

    return identical


def viz_agr(
    of_ge,
    of_ff,
    k=1,
    sigma=None,
    bc_params=None,
    level="LE",
    octaves_only=True,
    start_idx=1,
    db_drop=20,
    f_min=112,
    f_max=2239,
    window=False,
    height_axis_index=2,
):
    sim_name = get_sim_name(of_ge)

    pts_ref = get_point_sensors(of_ff)
    pts_eval = get_point_sensors(of_ge)

    dx = get_dx(of_ge)
    c0 = get_c0(of_ge)

    # Source data
    src0_pt = pts_eval[0]
    src0_xyz = src0_pt["xyz"]

    h1 = src0_xyz[height_axis_index]
    h0 = (k - 1) * dx + 0.5 * dx  # include half grid step offset
    h = h1 - h0
    x0 = src0_xyz[0]

    for pt_ref, pt_eval in zip(pts_ref[start_idx:], pts_eval[start_idx:]):
        snr_p0 = pt_ref["p"]

        snr_t1 = pt_eval["t"]
        snr_p1 = pt_eval["p"]
        snr_xyz1 = pt_eval["xyz"]

        snr_dist = snr_xyz1 - src0_xyz
        d_x = snr_dist[0]
        d_y = snr_dist[height_axis_index]
        d_r = np.linalg.norm(snr_dist)

        dt = snr_t1[1] - snr_t1[0]

        (xf0, pf0) = calc_fft(snr_t1, snr_p0)
        (xf1, pf1) = calc_fft(snr_t1, snr_p1)
        (xf0_db, pf0_db) = calc_fft_db(snr_t1, snr_p0)
        (xf1_db, pf1_db) = calc_fft_db(snr_t1, snr_p1)
        (pf0_3, f_3, _, _) = calc_3rd_octaves(snr_t1, snr_p0)
        (pf1_3, _, _, _) = calc_3rd_octaves(snr_t1, snr_p1)

        p_sim = 20 * np.log10(np.abs(pf1) / np.abs(pf0))
        p_sim_db = pf1_db - pf0_db
        p_sim_3 = pf1_3 - pf0_3
        if sigma is not None:
            p_anlytc_sigma = ground_effect(
                xf1, z_miki(xf1, sigma), d_x, h, h + d_y, c0=c0
            )
            p_anlytc_sigma_3o, _, _, _ = calc_3rd_octaves_from_fft_db(
                xf1, p_anlytc_sigma, p0=None
            )
        if bc_params is not None:
            bc_a1 = bc_params[0]
            bc_b0 = bc_params[1]
            bc_b1 = bc_params[2]
            p_anlytc_bc = ground_effect(
                xf1, z_iir1(xf1, bc_a1, bc_b0, bc_b1), d_x, h, h + d_y, c0=c0
            )
            p_anlytc_bc_3o, _, _, _ = calc_3rd_octaves_from_fft_db(
                xf1, p_anlytc_bc, p0=None
            )

        fig, axs = plt.subplots(1, 2, figsize=(10, 4))
        #
        axs[0].plot(xf1, p_sim, label="Simulation")
        if sigma is not None:
            axs[0].plot(xf1, p_anlytc_sigma, label=f"Theory (Miki: $\sigma = {sigma}$)")
        if bc_params is not None:
            axs[0].plot(xf1, p_anlytc_bc, label="Theory (IIR)")
        axs[0].set_xscale("log")
        axs[0].set_xlabel("f [Hz]")
        axs[0].set_ylabel("$A_{gr}$ [dB]")
        axs[0].legend()
        axs[0].set_title(f"x,y = {d_x:.1f}, {d_y:.1f} m")
        # axs[0].set_ylim([0, 7])
        # axs[0].set_ylim(bottom=0)
        axs[0].set_xticks([125, 250, 500, 1000, 2000])
        axs[0].set_xlim([f_min, f_max])
        axs[0].xaxis.set_major_formatter(ScalarFormatter())
        #
        axs[1].plot(f_3, p_sim_3, ".-", label="Simulation")
        if sigma is not None:
            axs[1].plot(
                f_3, p_anlytc_sigma_3o, ".-", label=f"Theory (Miki: $\sigma = {sigma}$)"
            )
        if bc_params is not None:
            axs[1].plot(f_3, p_anlytc_bc_3o, ".-", label="Theory (IIR)")
        axs[1].set_xscale("log")
        axs[1].set_xlabel("f [Hz]")
        axs[1].set_ylabel("$A_{gr}$ [dB]")
        axs[1].legend()
        axs[1].set_title(f"x,y = {d_x:.1f}, {d_y:.1f} m")
        # axs[1].set_ylim([0, 7])
        # axs[1].set_ylim(bottom=0)
        axs[1].set_xticks([125, 250, 500, 1000, 2000])
        axs[1].set_xlim([f_min, f_max])
        axs[1].xaxis.set_major_formatter(ScalarFormatter())
        # Show the plots
        plt.tight_layout()  # Automatically adjust subplot parameters to give specified padding
        plt.show()


# %% Plots
def plot_complex(f, y):
    """
    Plots the real part, imaginary part, magnitude, and phase angle of complex values against frequency.

    Parameters:
        f (ndarray): The frequency values corresponding to the complex values.
        y (ndarray): The complex values to be plotted.

    Returns:
        matplotlib.figure.Figure: The figure object containing the plots.
    """
    fig, axs = plt.subplots(2, 2, figsize=(10, 8))
    # Real part
    axs[0, 0].plot(f, np.real(y))
    axs[0, 0].set_xscale("log")
    axs[0, 0].set_title("Real Part")
    axs[0, 0].set_xlabel("Frequency (Hz)")
    axs[0, 0].set_ylabel("Real Value")
    # Imaginary part
    axs[0, 1].plot(f, np.imag(y))
    axs[0, 1].set_xscale("log")
    axs[0, 1].set_title("Imaginary Part")
    axs[0, 1].set_xlabel("Frequency (Hz)")
    axs[0, 1].set_ylabel("Imaginary Value")
    # Magnitude
    axs[1, 0].plot(f, np.abs(y))
    axs[1, 0].set_xscale("log")
    axs[1, 0].set_yscale("log")
    axs[1, 0].set_title("Magnitude")
    axs[1, 0].set_xlabel("Frequency (Hz)")
    axs[1, 0].set_ylabel("Magnitude")
    # Phase angle
    axs[1, 1].plot(f, np.angle(y, deg=True))
    axs[1, 1].set_xscale("log")
    axs[1, 1].set_title("Phase Angle")
    axs[1, 1].set_xlabel("Frequency (Hz)")
    axs[1, 1].set_ylabel("Phase (Degrees)")
    plt.tight_layout()
    plt.show()
    return fig, axs


# %% Voxels
def viz_voxels_plotly(voxels, x_axis=None, y_axis=None, z_axis=None, step=50):
    import plotly.io as pio

    pio.renderers.default = "browser"
    import plotly.graph_objects as go

    x, y, z = voxels.nonzero()
    c = voxels[voxels != 0]
    fig = go.Figure(
        data=[
            go.Scatter3d(
                x=x[::step],
                y=y[::step],
                z=z[::step],
                mode="markers",
                marker=dict(
                    color=c[::step],
                    # colorscale='Viridis',
                    opacity=0.8,
                ),
            )
        ]
    )

    # tight layout
    fig.update_layout(margin=dict(l=0, r=0, b=0, t=0))
    fig.show()


def get_cube(limits=None):
    """get the vertices, edges, and faces of a cuboid defined by its limits

    limits = np.array([[x_min, x_max],
                       [y_min, y_max],
                       [z_min, z_max]])
    """
    v = np.array(
        [
            [0, 0, 0],
            [0, 0, 1],
            [0, 1, 0],
            [0, 1, 1],
            [1, 0, 0],
            [1, 0, 1],
            [1, 1, 0],
            [1, 1, 1],
        ],
        dtype=int,
    )

    if limits is not None:
        v = limits[np.arange(3)[np.newaxis, :].repeat(8, axis=0), v]

    e = np.array(
        [
            [0, 1],
            [0, 2],
            [0, 4],
            [1, 3],
            [1, 5],
            [2, 3],
            [2, 6],
            [3, 7],
            [4, 5],
            [4, 6],
            [5, 7],
            [6, 7],
        ],
        dtype=int,
    )

    f = np.array(
        [
            [0, 2, 3, 1],
            [0, 4, 5, 1],
            [0, 4, 6, 2],
            [1, 5, 7, 3],
            [2, 6, 7, 3],
            [4, 6, 7, 5],
        ],
        dtype=int,
    )

    return v, e, f


def viz_voxels(voxels, x=None, y=None, z=None, step=1):
    if x is None:
        x = np.arange(voxels.shape[0])
    if y is None:
        y = np.arange(voxels.shape[1])
    if z is None:
        z = np.arange(voxels.shape[2])

    unique_values = np.unique(voxels[voxels != 0])

    fig = plt.figure()
    ax = fig.add_subplot(111, projection="3d")
    for value in unique_values:
        pos = np.where(voxels == value)
        ax.scatter(
            x[pos[0]][::step],
            y[pos[1]][::step],
            z[pos[2]][::step],
            label=f"{value}",
            alpha=0.8,
        )
    ax.set_xlabel("x [m]")
    ax.set_ylabel("y [m]")
    ax.set_zlabel("z [m]")

    limits = np.array([[x[0], x[-1]], [y[0], y[-1]], [z[0], z[-1]]])

    v, e, f = get_cube(limits)
    for i, j in e:
        ax.plot(*v[[i, j], :].T, color="0.8", ls="-")
    ax.plot(*v.T, marker="o", color="0.6", ls="")
    plt.show()

    # Set the aspect ratio
    max_range = (
        np.array([x.max() - x.min(), y.max() - y.min(), z.max() - z.min()]).max() / 2.0
    )
    mid_x = (x.max() + x.min()) * 0.5
    mid_y = (y.max() + y.min()) * 0.5
    mid_z = (z.max() + z.min()) * 0.5
    ax.set_xlim(mid_x - max_range, mid_x + max_range)
    ax.set_ylim(mid_y - max_range, mid_y + max_range)
    ax.set_zlim(mid_z - max_range, mid_z + max_range)

    fig.legend()

    return ax


def viz_voxels_sparse(voxels_sparse, x=None, y=None, z=None):
    xmin = voxels_sparse[:, 0].min()
    xmax = voxels_sparse[:, 0].max()
    ymin = voxels_sparse[:, 1].min()
    ymax = voxels_sparse[:, 1].max()
    zmin = voxels_sparse[:, 2].min()
    zmax = voxels_sparse[:, 2].max()
    if x is None:
        x = np.arange(xmin, xmax + 1)
    if y is None:
        y = np.arange(ymin, ymax + 1)
    if z is None:
        z = np.arange(zmin, zmax + 1)

    fig = plt.figure()
    ax = fig.add_subplot(111, projection="3d")
    ax.scatter(
        x[voxels_sparse[:, 0]],
        y[voxels_sparse[:, 1]],
        z[voxels_sparse[:, 2]],
        c="black",
    )
    ax.set_xlabel("x [m]")
    ax.set_ylabel("y [m]")
    ax.set_zlabel("z [m]")

    limits = np.array([[x[0], x[-1]], [y[0], y[-1]], [z[0], z[-1]]])

    v, e, f = get_cube(limits)
    for i, j in e:
        ax.plot(*v[[i, j], :].T, color="0.8", ls="-")
    ax.plot(*v.T, marker="o", color="0.6", ls="")
    plt.show()

    return ax


def viz_voxels_slice(
    voxels,
    plane="z",
    index=None,
    dx=None,
    add_labels=True,
    srcs_ijk=None,
    rcvs_ijk=None,
    skip_indices=None,
    xlim=None,
    ylim=None,
    title=None,
    viz=True,
):

    import matplotlib.patheffects as pe
    from matplotlib.cm import get_cmap

    if skip_indices is None:
        skip_indices = []

    if plane == "x":
        y = np.arange(voxels.shape[1])
        z = np.arange(voxels.shape[2])
        if index is None:
            index = int(voxels.shape[0] / 2)
        slice_data = voxels[index, :, :]
        x_min, x_max = 0, voxels.shape[1]
        y_min, y_max = 0, voxels.shape[2]
        axis_x_name = "j"
        axis_y_name = "k"
        sec_x_name = "y"
        sec_y_name = "z"
    elif plane == "y":
        x = np.arange(voxels.shape[0])
        z = np.arange(voxels.shape[2])
        if index is None:
            index = int(voxels.shape[1] / 2)
        slice_data = voxels[:, index, :]
        x_min, x_max = 0, voxels.shape[0]
        y_min, y_max = 0, voxels.shape[2]
        axis_x_name = "i"
        axis_y_name = "k"
        sec_x_name = "x"
        sec_y_name = "z"
    elif plane == "z":
        x = np.arange(voxels.shape[0])
        y = np.arange(voxels.shape[1])
        if index is None:
            index = int(voxels.shape[2] / 2)
        slice_data = voxels[:, :, index]
        x_min, x_max = 0, voxels.shape[0]
        y_min, y_max = 0, voxels.shape[1]
        axis_x_name = "i"
        axis_y_name = "j"
        sec_x_name = "x"
        sec_y_name = "y"

    unique_values = np.unique(voxels[voxels != 0])
    if len(unique_values) == 0:
        print(f"No materials in {plane}={index}")
        return

    # cmap = get_cmap('tab10', unique_values[-1]+1)
    cmap = get_cmap("Pastel1")

    fig, ax = plt.subplots(dpi=300)
    for value in unique_values:
        if value in skip_indices:
            continue

        pos = np.where(slice_data == value)
        if plane == "x":
            axis_x_name = "j"
            axis_y_name = "k"
            if pos[0].size > 0:
                ax.scatter(
                    y[pos[0]], z[pos[1]], color=cmap(value - 1), label=f"{value}", s=0.5
                )
                centroid_x = y[pos[0]].mean()
                centroid_y = z[pos[1]].mean()
        elif plane == "y":
            axis_x_name = "i"
            axis_y_name = "k"
            if pos[0].size > 0:
                ax.scatter(
                    x[pos[0]], z[pos[1]], color=cmap(value - 1), label=f"{value}", s=0.5
                )
                centroid_x = x[pos[0]].mean()
                centroid_y = z[pos[1]].mean()
        elif plane == "z":
            axis_x_name = "i"
            axis_y_name = "j"
            if pos[0].size > 0:
                ax.scatter(
                    x[pos[0]], y[pos[1]], color=cmap(value - 1), label=f"{value}", s=0.5
                )
                centroid_x = x[pos[0]].mean()
                centroid_y = y[pos[1]].mean()

        if pos[0].size > 0 and add_labels:
            ax.text(
                centroid_x,
                centroid_y,
                f"{value}",
                color="black",
                ha="center",
                va="center",
                path_effects=[pe.withStroke(linewidth=2, foreground="white")],
            )

    if srcs_ijk is not None:
        if plane == "x":
            srcs_on_plane = srcs_ijk[srcs_ijk[:, 0] == index]
            ax.scatter(
                srcs_on_plane[:, 1],
                srcs_on_plane[:, 2],
                color="tab:blue",
                label="Sources",
                marker=".",
            )
        elif plane == "y":
            srcs_on_plane = srcs_ijk[srcs_ijk[:, 1] == index]
            ax.scatter(
                srcs_on_plane[:, 0],
                srcs_on_plane[:, 2],
                color="tab:blue",
                label="Sources",
                marker=".",
            )
        elif plane == "z":
            srcs_on_plane = srcs_ijk[srcs_ijk[:, 2] == index]
            ax.scatter(
                srcs_on_plane[:, 0],
                srcs_on_plane[:, 1],
                color="tab:blue",
                label="Sources",
                marker=".",
            )

    if rcvs_ijk is not None:
        if plane == "x":
            rcvs_on_plane = rcvs_ijk[rcvs_ijk[:, 0] == index]
            ax.scatter(
                rcvs_on_plane[:, 1],
                rcvs_on_plane[:, 2],
                color="tab:red",
                label="Receivers",
                marker=".",
            )
        elif plane == "y":
            rcvs_on_plane = rcvs_ijk[rcvs_ijk[:, 1] == index]
            ax.scatter(
                rcvs_on_plane[:, 0],
                rcvs_on_plane[:, 2],
                color="tab:red",
                label="Receivers",
                marker=".",
            )
        elif plane == "z":
            rcvs_on_plane = rcvs_ijk[rcvs_ijk[:, 2] == index]
            ax.scatter(
                rcvs_on_plane[:, 0],
                rcvs_on_plane[:, 1],
                color="tab:red",
                label="Receivers",
                marker=".",
            )

    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)
    ax.set_xlabel(f"{axis_x_name} [idx]")
    ax.set_ylabel(f"{axis_y_name} [idx]")

    if title is None:
        ax.set_title(f"Voxels in {plane.upper()} Plane: {index}")
    else:
        ax.set_title(title)

    # Set aspect ratio to equal for both axes
    ax.set_aspect("equal")

    if dx is not None:
        secax_x = ax.secondary_xaxis(
            "top", functions=(lambda i: i * dx, lambda x: x / dx)
        )
        secax_x.set_xlabel(f"{sec_x_name} [m]")
        secax_y = ax.secondary_yaxis(
            "right", functions=(lambda i: i * dx, lambda y: y / dx)
        )
        secax_y.set_ylabel(f"{sec_y_name} [m]")

    ax.grid(True, which="both")
    if xlim is not None:
        ax.set_xlim(xlim)
    if ylim is not None:
        ax.set_ylim(ylim)

    fig.tight_layout()

    if viz == False:
        plt.close(fig)
    else:
        plt.show()

    return fig, ax


def save_voxels_slices(
    voxels,
    save_path,
    prefix,
    axes,
    video=False,
    dx=None,
    add_labels=True,
    srcs_ijk=None,
    rcvs_ijk=None,
    skip_indices=None,
):
    if axes == "x":
        n = voxels.shape[0]
    elif axes == "y":
        n = voxels.shape[1]
    elif axes == "z":
        n = voxels.shape[2]
    print(f"Saving {n} slices in {axes} direction")
    print(f"Saving to {save_path}")
    for i in range(n):
        fig, ax = viz_voxels_slice(
            voxels,
            axes,
            index=i,
            viz=False,
            dx=dx,
            add_labels=add_labels,
            srcs_ijk=srcs_ijk,
            rcvs_ijk=rcvs_ijk,
            skip_indices=skip_indices,
        )
        file_path = os.path.join(save_path, f"{prefix}_{axes}_{i}.png")
        fig.savefig(file_path, dpi=300)
        # Print progress every 10%
        if i % max(1, n // 10) == 0:
            progress_percent = (i / n) * 100
            print(f"Progress: {progress_percent:.0f}%")
    if video:
        create_video_from_images(
            save_path,
            f"{prefix}_{axes}_%d.png",
            f"{prefix}_{axes}",
            framerate=10,
            crf=18,
            pix_fmt="yuv420p",
        )


def viz_voxels_projection(
    voxels,
    plane="z",
    dx=None,
    add_labels=True,
    srcs_ijk=None,
    rcvs_ijk=None,
    skip_indices=None,
    xlim=None,
    ylim=None,
    title=None,
    viz=True,
):
    """
    Projects all voxels onto a specified plane and visualizes the result.
    The projection is performed by taking the maximum value along the axis
    orthogonal to the plane.

    Parameters:
        voxels (ndarray): A 3D numpy array of voxels.
        plane (str): The plane onto which to project ('x', 'y', or 'z'). Default is 'z'.
        dx (float, optional): Grid spacing for adding secondary axes.
        add_labels (bool): If True, add material labels.
        srcs_ijk (ndarray, optional): Array of source coordinates (i,j,k) to overlay.
        rcvs_ijk (ndarray, optional): Array of receiver coordinates (i,j,k) to overlay.
        skip_indices (list, optional): List of material values to skip in the visualization.
        xlim (tuple, optional): Limits for the x-axis.
        ylim (tuple, optional): Limits for the y-axis.
        title (str, optional): Title for the plot.
        viz (bool): If True, display the plot; if False, just return the figure and axis.

    Returns:
        tuple: (fig, ax) of the matplotlib figure and axis.
    """
    import matplotlib.patheffects as pe
    from matplotlib.cm import get_cmap

    if skip_indices is None:
        skip_indices = []

    if plane == "x":
        # Project along x-axis (axis 0)
        projection = np.max(voxels, axis=0)
        x_axis = np.arange(voxels.shape[1])
        y_axis = np.arange(voxels.shape[2])
        x_min, x_max = 0, voxels.shape[1]
        y_min, y_max = 0, voxels.shape[2]
        axis_x_name = "j"
        axis_y_name = "k"
        sec_x_name = "y"
        sec_y_name = "z"
    elif plane == "y":
        # Project along y-axis (axis 1)
        projection = np.max(voxels, axis=1)
        x_axis = np.arange(voxels.shape[0])
        y_axis = np.arange(voxels.shape[2])
        x_min, x_max = 0, voxels.shape[0]
        y_min, y_max = 0, voxels.shape[2]
        axis_x_name = "i"
        axis_y_name = "k"
        sec_x_name = "x"
        sec_y_name = "z"
    elif plane == "z":
        # Project along z-axis (axis 2)
        projection = np.max(voxels, axis=2)
        x_axis = np.arange(voxels.shape[0])
        y_axis = np.arange(voxels.shape[1])
        x_min, x_max = 0, voxels.shape[0]
        y_min, y_max = 0, voxels.shape[1]
        axis_x_name = "i"
        axis_y_name = "j"
        sec_x_name = "x"
        sec_y_name = "y"
    else:
        raise ValueError("Plane must be one of 'x', 'y', or 'z'.")

    unique_values = np.unique(projection[projection != 0])
    if len(unique_values) == 0:
        print(f"No materials found in the projection on {plane}-plane.")
        return

    cmap = get_cmap("Pastel1")

    fig, ax = plt.subplots(dpi=300)
    # Loop over each material key and plot its projected locations
    for value in unique_values:
        if value in skip_indices:
            continue

        pos = np.where(projection == value)
        if pos[0].size > 0:
            # Depending on the plane, assign axes appropriately.
            if plane in ["x", "z"]:
                ax.scatter(
                    x_axis[pos[0]],
                    y_axis[pos[1]],
                    color=cmap(value - 1),
                    label=f"{value}",
                    s=0.5,
                )
                centroid_x = x_axis[pos[0]].mean()
                centroid_y = y_axis[pos[1]].mean()
            elif plane == "y":
                ax.scatter(
                    x_axis[pos[0]],
                    y_axis[pos[1]],
                    color=cmap(value - 1),
                    label=f"{value}",
                    s=0.5,
                )
                centroid_x = x_axis[pos[0]].mean()
                centroid_y = y_axis[pos[1]].mean()

            if add_labels:
                ax.text(
                    centroid_x,
                    centroid_y,
                    f"{value}",
                    color="black",
                    ha="center",
                    va="center",
                    path_effects=[pe.withStroke(linewidth=2, foreground="white")],
                )

    # Overlay source and receiver positions if provided
    if srcs_ijk is not None:
        if plane == "x":
            ax.scatter(
                srcs_ijk[:, 1],
                srcs_ijk[:, 2],
                color="tab:blue",
                label="Sources",
                marker=".",
            )
        elif plane == "y":
            ax.scatter(
                srcs_ijk[:, 0],
                srcs_ijk[:, 2],
                color="tab:blue",
                label="Sources",
                marker=".",
            )
        elif plane == "z":
            ax.scatter(
                srcs_ijk[:, 0],
                srcs_ijk[:, 1],
                color="tab:blue",
                label="Sources",
                marker=".",
            )

    if rcvs_ijk is not None:
        if plane == "x":
            ax.scatter(
                rcvs_ijk[:, 1],
                rcvs_ijk[:, 2],
                color="tab:red",
                label="Receivers",
                marker=".",
            )
        elif plane == "y":
            ax.scatter(
                rcvs_ijk[:, 0],
                rcvs_ijk[:, 2],
                color="tab:red",
                label="Receivers",
                marker=".",
            )
        elif plane == "z":
            ax.scatter(
                rcvs_ijk[:, 0],
                rcvs_ijk[:, 1],
                color="tab:red",
                label="Receivers",
                marker=".",
            )

    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)
    ax.set_xlabel(f"{axis_x_name} [idx]")
    ax.set_ylabel(f"{axis_y_name} [idx]")

    if title is None:
        ax.set_title(f"Projection of Voxels onto {plane.upper()} Plane")
    else:
        ax.set_title(title)

    # Set aspect ratio to equal for both axes
    ax.set_aspect("equal")

    if dx is not None:
        secax_x = ax.secondary_xaxis(
            "top", functions=(lambda i: i * dx, lambda x: x / dx)
        )
        secax_x.set_xlabel(f"{sec_x_name} [m]")
        secax_y = ax.secondary_yaxis(
            "right", functions=(lambda i: i * dx, lambda y: y / dx)
        )
        secax_y.set_ylabel(f"{sec_y_name} [m]")

    ax.grid(True, which="both")
    if xlim is not None:
        ax.set_xlim(xlim)
    if ylim is not None:
        ax.set_ylim(ylim)

    fig.tight_layout()

    if viz:
        plt.show()
    else:
        plt.close(fig)

    return fig, ax
