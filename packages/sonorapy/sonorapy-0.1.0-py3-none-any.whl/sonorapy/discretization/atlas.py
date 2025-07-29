# -*- coding: utf-8 -*-
import os

import matplotlib.pyplot as plt
import numpy as np
import scipy.io as sio
from scipy.interpolate import interp1d

from ..viz import viz_surf, viz_surf_spectra, viz_vns_2d, viz_vns_3d


def disc_terrain(
    root_dir="",
    location="Baden",
    profile_idx=0,
    src_x_min=-5,
    rcv_x_max=5,  # in m
    dx=0.02,
    i0_padding=1,  # Boundary layer and X0 PML thickness (1 + x0_pml_thickness)
    k_padding=1,  # Boundary layer thickness
    skip_if_barrier=False,
    plot=True,
    verbose=False,
):
    """
    Processes a given location profile and performs various operations like cropping, cutting and discretizing the domain.

    Parameters:
    - location (str): The location for which the profile is needed
    - version (int): The version number of the profile to be used
    - src_x_min (float): The x-coordinate minimum limit for the source
    - rcv_x_max (float): The x-coordinate maximum limit for the receiver
    - dx (float): The discretization parameter
    - k_padding (int): The padding for the z-axis

    Returns:
    None. Outputs are printed and a plot is displayed.
    """
    # Open file
    mat_fname = os.path.join(root_dir, f"{location}_Profiles_2.mat")
    mat_contents = sio.loadmat(mat_fname, squeeze_me=True)

    # Take simulation domain padding into account (Boundary layer and PML)
    profiles = mat_contents["profile"]
    i_name = mat_contents["nameCombi"][profile_idx]
    i_barriers = mat_contents["barriers"][profile_idx]
    i_sigma = mat_contents["sigma"][profile_idx]
    i_receiver = mat_contents["receiver"][profile_idx]  #
    i_receiver_a = mat_contents["receiver"][profile_idx // 3 * 3 + 0]
    i_receiver_b = mat_contents["receiver"][profile_idx // 3 * 3 + 1]
    i_receiver_c = mat_contents["receiver"][profile_idx // 3 * 3 + 2]

    if verbose:
        print("Profile:", profile_idx)
        print(" Name:", i_name)
        if np.any(~np.isnan(i_barriers)):
            print(" Barriers:", i_barriers.shape)
            if skip_if_barrier:
                assert False
        print(" Sigmas:", np.unique(i_sigma))
        print(" S-R Distance", np.sqrt(i_receiver[0] ** 2 + i_receiver[2] ** 2))

    x = profiles[profile_idx][0]
    z = profiles[profile_idx][2]
    if verbose:
        print(" X:", np.min(x), np.max(x), "d:", np.max(x) - np.min(x))
        print(" Z:", np.min(z), np.max(z), "d:", np.max(z) - np.min(z))

    # We don't need the entire coordinates
    # We only care for the domain around the source and reciever
    x_min = 0 + src_x_min
    if rcv_x_max is None:
        x_max = x[-1]
    else:
        x_max = i_receiver[0] + rcv_x_max
    idx_min = np.argmin(x < x_min)
    if idx_min != 0:
        idx_min -= 1
    idx_max = np.argmin(x < x_max)
    # Filtered (cut) axes
    x_cut = x[idx_min : idx_max + 1]
    z_cut = z[idx_min : idx_max + 1]
    if verbose:
        print(
            " X cut:", np.min(x_cut), np.max(x_cut), "d:", np.max(x_cut) - np.min(x_cut)
        )
        print(
            " Z cut:", np.min(z_cut), np.max(z_cut), "d:", np.max(z_cut) - np.min(z_cut)
        )

    ## Discretize (xyz)
    # Axes
    x_axis_tmp = np.arange(x_min, x_max, dx)
    z_axis_tmp = np.arange(
        np.min(z_cut) - k_padding * dx, np.max(z_cut) + k_padding * dx, dx
    )
    if verbose:
        print(
            " X discrete:",
            np.min(x_axis_tmp),
            np.max(x_axis_tmp),
            "d:",
            np.max(x_axis_tmp) - np.min(x_axis_tmp),
        )
        print(
            " Z discrete:",
            np.min(z_axis_tmp),
            np.max(z_axis_tmp),
            "d:",
            np.max(z_axis_tmp) - np.min(z_axis_tmp),
        )
    x_offset = x_axis_tmp[0] + i0_padding * dx
    z_offset = z_axis_tmp[0]

    x_axis = x_axis_tmp - x_offset
    z_axis = z_axis_tmp - z_offset
    src_xyz = np.array([-x_offset, 0, -z_offset])
    rcv_xyz = i_receiver + np.array([-x_offset, 0, -z_offset])

    rcv_a_xyz = i_receiver_a + np.array([-x_offset, 0, -z_offset])
    rcv_b_xyz = i_receiver_b + np.array([-x_offset, 0, -z_offset])
    rcv_c_xyz = i_receiver_c + np.array([-x_offset, 0, -z_offset])

    if verbose:
        print(
            " X final:",
            np.min(x_axis),
            np.max(x_axis),
            "d:",
            np.max(x_axis) - np.min(x_axis),
        )
        print(
            " Z final:",
            np.min(z_axis),
            np.max(z_axis),
            "d:",
            np.max(z_axis) - np.min(z_axis),
        )

    # Create (linear) interpolator to go from original data to any arbitrary x
    f = interp1d(x - x_offset, z - z_offset)
    z_new = f(x_axis)
    # Create (nearest neighbor) interpolator to go from original sigma to any arbitrary x
    f_nn = interp1d(x - x_offset, i_sigma, kind="nearest")
    sigma_new = f_nn(x_axis)

    if plot:
        fig, ax = plt.subplots()
        ax.plot(x - x_offset, z - z_offset, "o-", label="Terrain")
        for sig in np.unique(sigma_new):
            ax.plot(
                x_axis[sigma_new == sig],
                z_new[sigma_new == sig],
                ".",
                label="$\sigma = {}$".format(sig),
            )
        ax.plot(src_xyz[0], src_xyz[2], "o", label="Source")
        ax.plot(
            [rcv_a_xyz[0], rcv_b_xyz[0], rcv_c_xyz[0]],
            [rcv_a_xyz[2], rcv_b_xyz[2], rcv_c_xyz[2]],
            "o",
            label="Receivers",
        )
        ax.legend()
        ax.set_title(f"Profile {profile_idx}: {i_name}")
        ax.set_xlabel("m")
        ax.set_ylabel("m")

    ## Discretize (ijk)
    if verbose:
        Lx = x_axis.size
        Lz = z_axis.size
        print("2D size (Lx, Lz, N)", Lx, Lz, Lx * Lz)

    return {
        "name": i_name,
        "x": x_axis,
        "z": z_axis,
        "z_terr": z_new,
        "sigma_terr": sigma_new,
        "src_xyz": src_xyz,
        # "rcv_xyz": rcv_xyz}
        "rcv_xyz": np.array([rcv_a_xyz, rcv_b_xyz, rcv_c_xyz]),
    }
