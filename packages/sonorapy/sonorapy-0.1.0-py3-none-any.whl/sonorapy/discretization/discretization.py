# -*- coding: utf-8 -*-
import os

import matplotlib.pyplot as plt
import numpy as np
import scipy.io as sio
from scipy.interpolate import interp1d

from ..h5 import find_h5_dataset, find_h5_group, get_h5_attribute
from ..viz import viz_surf, viz_surf_spectra, viz_vns_2d, viz_vns_3d


# %% Common - Manipulations
def pad_axes(axis, n_left, n_right, dx=None):
    """
    Pads an axis array on both sides with a specified number of elements.

    Parameters:
        axis (ndarray): Array representing the axis to be padded.
        n_left (int): Number of elements to pad on the left side.
        n_right (int): Number of elements to pad on the right side.
        dx (float, optional): Spacing between elements in the axis. If None, the spacing is calculated from the first two elements of the axis. Defaults to None.

    Returns:
        ndarray: A new array with the left and right padding added to the original axis.
    """
    # Set the spacing between elements if not provided
    if dx == None:
        dx = axis[1] - axis[0]
    n_padding = np.arange(-n_left, 0) * dx + axis[0]
    p_padding = np.arange(1, n_right + 1) * dx + axis[-1]
    return np.concatenate((n_padding, axis, p_padding))


# %%
def mat2vn(mat_id, voxels, viz=False, plot_view=None):
    """
    Extract directional edges for a specific material ID from a 3D voxel grid.

    Parameters:
        mat_id (int): Identifier for the voxel type to extract.
        voxels (ndarray): 3D array representing the voxel grid.
        plot (bool, optional): If True, visualize the result. Defaults to False.
        plot_view (str, optional): The view angle for the plot ('XY', 'XZ', 'YZ'). Defaults to None.

    Returns:
        tuple: Sets of coordinates for directional edges in each direction (xn, xp, yn, yp, zn, zp).
    """
    # Create a binary mask where the specified material ID is present
    bin_mask = np.zeros_like(voxels)
    bin_mask[voxels == mat_id] = 1

    # Calculate the differences in the binary mask to find edges for each direction
    a_xn = bin_mask[1:, :, :] - bin_mask[:-1, :, :]
    bc_xn = np.array(np.where(a_xn == 1)).T + [1, 0, 0]

    a_xp = bin_mask[:-1, :, :] - bin_mask[1:, :, :]
    bc_xp = np.array(np.where(a_xp == 1)).T

    a_yn = bin_mask[:, 1:, :] - bin_mask[:, :-1, :]
    bc_yn = np.array(np.where(a_yn == 1)).T + [0, 1, 0]

    a_yp = bin_mask[:, :-1, :] - bin_mask[:, 1:, :]
    bc_yp = np.array(np.where(a_yp == 1)).T

    a_zn = bin_mask[:, :, 1:] - bin_mask[:, :, :-1]
    bc_zn = np.array(np.where(a_zn == 1)).T + [0, 0, 1]

    a_zp = bin_mask[:, :, :-1] - bin_mask[:, :, 1:]
    bc_zp = np.array(np.where(a_zp == 1)).T

    # Sort indices by X-Fastest
    if bc_xn.size != 0:
        bc_xn = bc_xn[np.lexsort((bc_xn[:, 0], bc_xn[:, 1], bc_xn[:, 2]))]
    if bc_xp.size != 0:
        bc_xp = bc_xp[np.lexsort((bc_xp[:, 0], bc_xp[:, 1], bc_xp[:, 2]))]
    if bc_yn.size != 0:
        bc_yn = bc_yn[np.lexsort((bc_yn[:, 0], bc_yn[:, 1], bc_yn[:, 2]))]
    if bc_yp.size != 0:
        bc_yp = bc_yp[np.lexsort((bc_yp[:, 0], bc_yp[:, 1], bc_yp[:, 2]))]
    if bc_zn.size != 0:
        bc_zn = bc_zn[np.lexsort((bc_zn[:, 0], bc_zn[:, 1], bc_zn[:, 2]))]
    if bc_zp.size != 0:
        bc_zp = bc_zp[np.lexsort((bc_zp[:, 0], bc_zp[:, 1], bc_zp[:, 2]))]

    if viz:
        # Visualization
        fig = plt.figure()
        ax = fig.add_subplot(111, projection="3d")

        # Boundary conditions
        # Arrow properties
        length = 0.5
        ax.quiver(bc_xn[:, 0], bc_xn[:, 1], bc_xn[:, 2], -length, 0, 0, color="r")
        ax.quiver(bc_xp[:, 0], bc_xp[:, 1], bc_xp[:, 2], length, 0, 0, color="g")
        ax.quiver(bc_yn[:, 0], bc_yn[:, 1], bc_yn[:, 2], 0, -length, 0, color="m")
        ax.quiver(bc_yp[:, 0], bc_yp[:, 1], bc_yp[:, 2], 0, length, 0, color="y")
        ax.quiver(bc_zn[:, 0], bc_zn[:, 1], bc_zn[:, 2], 0, 0, -length, color="c")
        ax.quiver(bc_zp[:, 0], bc_zp[:, 1], bc_zp[:, 2], 0, 0, length, color="k")

        ax.set_box_aspect([voxels.shape[0], voxels.shape[1], voxels.shape[2]])

        if plot_view == "XY":
            ax.view_init(
                elev=90.0, azim=-90.0
            )  # looking down the Z-axis onto the XY plane
        elif plot_view == "XZ":
            ax.view_init(
                elev=0.0, azim=-90.0
            )  # looking in the direction of the Y-axis onto the XZ plane
        elif plot_view == "YZ":
            ax.view_init(
                elev=0.0, azim=0.0
            )  # looking in the direction of the X-axis onto the YZ plane

        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_zlabel("Z")
        plt.legend()

        plt.show()

    return (bc_xn, bc_xp, bc_yn, bc_yp, bc_zn, bc_zp)


def mats2vn(voxels, viz=False, plot_view=None):
    """
    Extract directional edges for all material IDs from a 3D voxel grid and optionally visualize them.

    Parameters:
        voxels (ndarray): 3D array representing the voxel grid.
        plot (bool, optional): If True, visualize the result. Defaults to False.
        plot_view (str, optional): Specifies the view angle for the plot ('XY', 'XZ', 'YZ'). Defaults to None.

    Returns:
        dict: A dictionary with material IDs as keys and tuples of coordinates for the directional edges in each direction as values.
    """
    results = {}

    # Extract unique material IDs, excluding the background (assumed to be zero)
    mat_ids = np.unique(voxels)
    mat_ids = mat_ids[mat_ids != 0]

    # Generate a combined mask for all material IDs
    mask = np.isin(voxels, mat_ids)

    # Perform XOR operation to find edge differences for all materials at once
    a_xn = mask[1:, :, :] ^ mask[:-1, :, :]
    a_xp = mask[:-1, :, :] ^ mask[1:, :, :]
    a_yn = mask[:, 1:, :] ^ mask[:, :-1, :]
    a_yp = mask[:, :-1, :] ^ mask[:, 1:, :]
    a_zn = mask[:, :, 1:] ^ mask[:, :, :-1]
    a_zp = mask[:, :, :-1] ^ mask[:, :, 1:]

    # Process each material ID to find its edges
    for mat_id in mat_ids:
        # Identify the coordinates of edges and adjust for boundary offsets
        bc_xn = np.array(np.where((a_xn == 1) & (voxels[1:, :, :] == mat_id))).T + [
            1,
            0,
            0,
        ]
        bc_xp = np.array(np.where((a_xp == 1) & (voxels[:-1, :, :] == mat_id))).T
        bc_yn = np.array(np.where((a_yn == 1) & (voxels[:, 1:, :] == mat_id))).T + [
            0,
            1,
            0,
        ]
        bc_yp = np.array(np.where((a_yp == 1) & (voxels[:, :-1, :] == mat_id))).T
        bc_zn = np.array(np.where((a_zn == 1) & (voxels[:, :, 1:] == mat_id))).T + [
            0,
            0,
            1,
        ]
        bc_zp = np.array(np.where((a_zp == 1) & (voxels[:, :, :-1] == mat_id))).T

        # Sort the edge coordinates by X-Fastest
        if bc_xn.size != 0:
            bc_xn = bc_xn[np.lexsort((bc_xn[:, 0], bc_xn[:, 1], bc_xn[:, 2]))]
        if bc_xp.size != 0:
            bc_xp = bc_xp[np.lexsort((bc_xp[:, 0], bc_xp[:, 1], bc_xp[:, 2]))]
        if bc_yn.size != 0:
            bc_yn = bc_yn[np.lexsort((bc_yn[:, 0], bc_yn[:, 1], bc_yn[:, 2]))]
        if bc_yp.size != 0:
            bc_yp = bc_yp[np.lexsort((bc_yp[:, 0], bc_yp[:, 1], bc_yp[:, 2]))]
        if bc_zn.size != 0:
            bc_zn = bc_zn[np.lexsort((bc_zn[:, 0], bc_zn[:, 1], bc_zn[:, 2]))]
        if bc_zp.size != 0:
            bc_zp = bc_zp[np.lexsort((bc_zp[:, 0], bc_zp[:, 1], bc_zp[:, 2]))]

        # Store the edges for each material ID in the results dictionary
        results[mat_id] = (bc_xn, bc_xp, bc_yn, bc_yp, bc_zn, bc_zp)

    if viz:
        id_to_color = {
            mat_id: color
            for mat_id, color in zip(
                mat_ids, plt.cm.jet(np.linspace(0, 1, len(mat_ids)))
            )
        }

        def adjust_color(color, factor):
            return [min(max(c * factor, 0), 1) for c in color]

        fig = plt.figure()
        ax = fig.add_subplot(111, projection="3d")

        # Plot edges for each material ID with directional color coding
        for mat_id, (bc_xn, bc_xp, bc_yn, bc_yp, bc_zn, bc_zp) in results.items():
            base_color = id_to_color[mat_id]
            colors = [
                adjust_color(base_color, f) for f in [1.0, 0.9, 0.8, 0.7, 0.6, 0.5]
            ]
            length = 0.5
            ax.quiver(
                bc_xn[:, 0], bc_xn[:, 1], bc_xn[:, 2], -length, 0, 0, color=colors[0]
            )
            ax.quiver(
                bc_xp[:, 0], bc_xp[:, 1], bc_xp[:, 2], length, 0, 0, color=colors[1]
            )
            ax.quiver(
                bc_yn[:, 0], bc_yn[:, 1], bc_yn[:, 2], 0, -length, 0, color=colors[2]
            )
            ax.quiver(
                bc_yp[:, 0], bc_yp[:, 1], bc_yp[:, 2], 0, length, 0, color=colors[3]
            )
            ax.quiver(
                bc_zn[:, 0], bc_zn[:, 1], bc_zn[:, 2], 0, 0, -length, color=colors[4]
            )
            ax.quiver(
                bc_zp[:, 0], bc_zp[:, 1], bc_zp[:, 2], 0, 0, length, color=colors[5]
            )

        # Set the view angle
        if plot_view == "XY":
            ax.view_init(
                elev=90.0, azim=-90.0
            )  # looking down the Z-axis onto the XY plane
        elif plot_view == "XZ":
            ax.view_init(
                elev=0.0, azim=-90.0
            )  # looking in the direction of the Y-axis onto the XZ plane
        elif plot_view == "YZ":
            ax.view_init(
                elev=0.0, azim=0.0
            )  # looking in the direction of the X-axis onto the YZ plane
        plt.show()

    return results


def calc_qw_params(x1, y1, z1, qw_params={}):
    """
    Generate parameters for Quasi-Wavelets (QW) in a 3D domain.

    Parameters:
        x1, y1, z1 (float): Dimensions of the 3D domain.
        qw_params (dict, optional): Dictionary of additional parameters.

    Returns:
        tuple: Arrays containing the coordinates (xi, yi, zi) and coefficients (ci, ai) for the QWs.
    """
    # a1 is the largest QW radius
    a1 = qw_params.get("a1", 1)
    # l means that a2 is typically a1*l = 100 / 2 = 50,
    # However densification factor K subdivides it further
    l = qw_params.get("l", 0.5)  # ratio of adjacent eddies, fixed standard value
    # 1 corresponds to largest, N to smallest
    # Though in reality we have N*K classes
    N = qw_params.get("N", 5)  # number of size classes 1,...,N
    # "Fractional" component by which to further subdivide "integer" size classes
    K = qw_params.get("K", 4)  # densification factor
    # following values can be set, here chosen like in Ostashev(2006),p.336
    beta = qw_params.get("beta", 0)  # power-law exponent for packing fraction
    lambd = qw_params.get("lambd", 1 / 3)  # power-law exponent for amplitude
    phi1 = qw_params.get("phi1", 0.1)
    q1 = qw_params.get("q1", 1)
    seed = qw_params.get("seed", 42)

    # Number of QW per total size class
    n = np.array([1 + (j - 1) / K for j in np.arange(1, N * K + 1)])
    a_n = np.array([a1 * l ** (n_ - 1) for n_ in n])
    print("Sizes (a_n):", a_n)
    # size of area
    V = x1 * y1 * z1

    # Calculate resulting values
    phi = l**beta
    phi_n = np.array([phi1 * phi ** (n_ - 1) for n_ in n])
    q = l**lambd
    q_n = np.array([q1 * q ** (n_ - 1) for n_ in n])

    # Number of quasi-wavelets (QW) per size class n
    Nn = phi_n * V / (K * a_n**3)
    rng = np.random.default_rng(seed)
    nn = rng.poisson(Nn)
    nn_total = nn.sum()
    print("QWs / a_n:", nn)
    print("QWs total:", "{:,}".format(nn_total))
    h = rng.choice([-1, 1], size=nn_total)
    coords = rng.uniform(0, [x1, y1, z1], size=(nn_total, 3))
    xi, yi, zi = coords.T
    ai = -np.pi / (2 * a_n.repeat(nn) ** 2)
    ci = h * q_n.repeat(nn)
    return xi, yi, zi, ci, ai


qw_params = {
    "a1": 10,  # a1 is the largest QW radius
    "l": 0.5,  # ratio of adjacent eddies, fixed standard value
    "N": 4,  # 5, # number of size classes 1,...,N
    "K": 4,  # 4, # densification factor
    "beta": 0,  # power-law exponent for packing fraction
    "lambd": 1 / 3,  # power-law exponent for amplitude
    "phi1": 0.1,
    "q1": 1,
    "seed": 42,
}


def surf_k2ijk(k, Ni, Nj, Nk):
    """
    Generate surface grid indices for height k in a ijk grid.

    Parameters:
        k (int): The level of the grid surface to extract.
        Ni, Nj, Nk (int): Dimensions of the 3D grid.

    Returns:
        ndarray: Array of indices on the surface at level k.
    """
    # Create mesh grid of indices for each dimension
    ii, jj = np.meshgrid(range(Ni), range(Nj), indexing="ij")
    # Stack the indices into a (Ni*Nj, 3) array with constant k
    ijk = np.stack((ii.ravel(), jj.ravel(), np.full(Ni * Nj, k)), axis=-1)
    # Sort the array so the first column (i index) changes fastest
    ijk = ijk[np.lexsort((ijk[:, 0], ijk[:, 1], ijk[:, 2]))]
    return ijk


def surf_j2ijk(j, Ni, Nj, Nk):
    """
    Generate surface grid indices for height j in a ijk grid.

    Parameters:
        j (int): The level of the grid surface to extract.
        Ni, Nj, Nk (int): Dimensions of the 3D grid.

    Returns:
        ndarray: Array of indices on the surface at level k.
    """
    ii, kk = np.meshgrid(range(Ni), range(Nk), indexing="ij")
    # Stack the indices into a (Ni*Nk, 3) array with constant k
    ijk = np.stack((ii.ravel(), np.full(Ni * Nk, j), kk.ravel()), axis=-1)
    # Sort the array so the first column (i index) changes fastest
    ijk = ijk[np.lexsort((ijk[:, 0], ijk[:, 1], ijk[:, 2]))]
    return ijk


def surf_perlin_noise(
    x_axis,
    y_axis,
    seed=0,
    scale=1.0,
    octaves=1,
    persistence=0.5,
    lacunarity=2.0,
    z_max=1.0,
    k_min=0,
    viz=False,
    return_heights_z=False,
):
    """
    Generate Perlin noise over a 2D grid and optionally visualize the noise pattern.

    Parameters:
        x_axis (ndarray): X-coordinates of the grid.
        y_axis (ndarray): Y-coordinates of the grid.
        seed (int): Random number generator seed for reproducibility.
        scale (float): Scale factor for the noise pattern.
        octaves (int): Number of layers of noise to generate.
        persistence (float): Amplitude decay for each octave (determines roughness).
        lacunarity (float): Frequency growth per octave (determines detail).
        z_max (float): Maximum height of the noise pattern.
        k_min (int): Minimum height offset of the noise pattern in k-index.
        visualize (bool): If True, visualizes the noise pattern.
        return_heights_z (bool): If True, returns the z-heights array in meters along with the noise pattern.


    Returns:
        ndarray: Perlin noise values. If return_heights is True, also returns the z-heights array.
    """

    # Function to smooth transitions between noise values
    def fade(t):
        return t * t * t * (t * (t * 6 - 15) + 10)

    # Function to linearly interpolate between two values
    def lerp(t, a, b):
        return (1 - t) * a + t * b

    # Function to compute dot product of gradient vector and the distance vector
    def gradient(h, x, y):
        vectors = np.array([[0, 1], [0, -1], [1, 0], [-1, 0]])
        g = vectors[h % 4]
        return g[:, :, 0] * x + g[:, :, 1] * y

    # Create grid of points
    x, y = np.meshgrid(x_axis, y_axis, indexing="ij")

    # Seed the random number generator for permutation table
    rng = np.random.default_rng(seed)
    p = rng.permutation(256)
    p = np.stack([p, p]).flatten()

    # Precompute grid coordinates scaled by Perlin noise parameters
    x_scaled = x / scale
    y_scaled = y / scale

    # Initialize result array
    z_perlin = np.zeros_like(x)

    # Generate noise for each octave
    for octave in range(octaves):
        # Calculate frequency and amplitude
        freq = lacunarity**octave
        amp = persistence**octave

        # Compute integer coordinates and fractional remainder for interpolation
        xi = np.floor(x_scaled * freq).astype(int)
        yi = np.floor(y_scaled * freq).astype(int)
        xf = x_scaled * freq - xi
        yf = y_scaled * freq - yi

        # Calculate fade curves
        u = fade(xf)
        v = fade(yf)

        # Hash coordinates for gradient computation
        xi = xi % 256
        yi = yi % 256

        # Compute gradients at the corners of a unit square
        n00 = gradient(p[p[xi] + yi], xf, yf)
        n01 = gradient(p[p[xi] + yi + 1], xf, yf - 1)
        n11 = gradient(p[p[xi + 1] + yi + 1], xf - 1, yf - 1)
        n10 = gradient(p[p[xi + 1] + yi], xf - 1, yf)

        # Interpolate between gradient values
        x1 = lerp(u, n00, n10)
        x2 = lerp(u, n01, n11)
        z_perlin += lerp(v, x1, x2) * amp

        # Scale coordinates for next octave
        x_scaled *= lacunarity
        y_scaled *= lacunarity

    # Normalize and scale noise values
    z_perlin -= z_perlin.min()
    z_perlin /= z_perlin.max()
    z_perlin *= z_max

    # Compute height levels
    dx = x_axis[1] - x_axis[0]
    k_terrain = np.ceil(z_perlin / dx).astype(int) + k_min

    if viz:
        # Plot the generated Perlin noise and its discretization
        fig, axs = plt.subplots(1, 2)
        im0 = axs[0].imshow(
            z_perlin.T,
            origin="lower",
            extent=[x_axis[0], x_axis[-1], y_axis[0], y_axis[-1]],
        )
        fig.colorbar(im0, ax=axs[0], fraction=0.046, pad=0.04)
        axs[0].set_title("Perlin Noise")

        im1 = axs[1].imshow(
            k_terrain.T,
            origin="lower",
            extent=[x_axis[0], x_axis[-1], y_axis[0], y_axis[-1]],
        )
        fig.colorbar(im1, ax=axs[1], fraction=0.046, pad=0.04)
        axs[1].set_title("Perlin Terrain")
        plt.tight_layout()
        plt.show()

        viz_surf(z_perlin, x_axis, y_axis)
        viz_surf(k_terrain, x_axis, y_axis)
        viz_surf_spectra(z_perlin, x_axis, y_axis, nexp=6)

    # Return height levels or both height levels and noise values
    if return_heights_z:
        return k_terrain, z_perlin
    else:
        return k_terrain


def surf2vn(k_surface, viz=False):
    """
    Convert a 2D terrain surface to directional edges above the surface.

    Parameters:
        k_surface (ndarray): 2D array representing the terrain height at each point in k-indices.
        viz (bool, optional): Flag to visualize the 3D voxel grid. Defaults to False.

    Returns:
        tuple: Sets of coordinates for directional edges in each direction (xn, xp, yn, yp, zn, zp).
    """
    # Dimensions of the input surface
    I, J = k_surface.shape
    # Determine the maximum height value in the 2D array
    K = np.max(k_surface)

    # Initialize a 3D voxel grid based on the terrain surface
    terr_vox = np.zeros((I, J, K + 2))
    # Fill the voxel grid: 1 where the terrain is present, 0 elsewhere
    for i in range(I):
        for j in range(J):
            k_value = k_surface[i, j]
            terr_vox[i, j, : k_value + 1] = 1

    if viz:
        x, y, z = np.where(terr_vox == 1)

        fig = plt.figure(figsize=(10, 5))

        # Display the height profile of the terrain
        ax0 = fig.add_subplot(121)
        im = ax0.imshow(k_surface, cmap="viridis", origin="lower", aspect="auto")
        ax0.set_title("Height Profile")
        ax0.set_xlabel("X Index")
        ax0.set_ylabel("Y Index")
        plt.colorbar(im, ax=ax0, fraction=0.046, pad=0.04)  # Adjust colorbar size

        # Display the 3D scatter plot of the voxel grid
        ax1 = fig.add_subplot(122, projection="3d")
        ax1.scatter(x, y, z, s=1, alpha=0.5)  # Decrease marker size for visibility
        ax1.set_title("Voxel Grid Visualization")
        ax1.set_xlabel("X Index")
        ax1.set_ylabel("Y Index")
        ax1.set_zlabel("Z Index (Height)")

        plt.tight_layout()
        plt.show()

    return mat2vn(1, terr_vox, viz=viz, plot_view="XZ")


def surf2vn_multi(k_surface, sigmas, viz=False):
    """
    Convert a 2D terrain surface to directional edges above the surface.

    Parameters:
        k_surface (ndarray): 2D array representing the terrain height at each point in k-indices.
        viz (bool, optional): Flag to visualize the 3D voxel grid. Defaults to False.

    Returns:
        tuple: Sets of coordinates for directional edges in each direction (xn, xp, yn, yp, zn, zp).
    """
    bcs = surf2vn(k_surface, viz=viz)
    out = {}
    for sk, sv in sigmas.items():
        # Get i indices of sigmas
        i_idxs = sv["i"]
        s_bcs = []
        for bc in bcs:
            s_bcs.append(bc[np.isin(bc[:, 0], i_idxs)])
        out[sk] = s_bcs

        if viz:
            viz_vns_3d(s_bcs)

    return out


def surf_spectral_synthesis(
    x_axis,
    y_axis,
    roughness_factor=0.0005,
    fc=0.5,
    Nmodes=1000,
    z_max=1.0,
    k_min=0,
    viz=False,
    return_heights_z=False,
):
    """
    Generates a synthetic terrain surface using spectral synthesis.

    Parameters:
        x_axis (ndarray): The x-coordinates of the terrain.
        y_axis (ndarray): The y-coordinates of the terrain.
        z_max (float): The amplitude of the terrain heights.
        roughness_factor (float): Controls the roughness of the terrain.
        fc (float): The cutoff frequency, determining the largest feature size.
        Nmodes (int): The number of spectral modes to use in the synthesis.
        k_min (int): The minimum level for the terrain.
        viz (bool): Whether to visualize the terrain.
        return_z_heights (bool): Whether to return the z-heights along with the k surface.

    Returns:
        ndarray: A 2D array representing the terrain surface levels. Optionally returns the z-heights.
    """
    # Compute the spatial resolution and spectral resolution
    dx = x_axis[1] - x_axis[0]
    Nx = x_axis.size
    Ny = y_axis.size
    fs = 1 / dx
    dk = 2 * np.pi * (fs / 2 - fc) / Nmodes

    # Random phase shifts
    theta = 2 * np.pi * np.random.rand(Nmodes)
    alpha = 2 * np.pi * np.random.rand(Nmodes)

    # Calculate directional components of wave vectors
    cosTheta = np.cos(theta)
    sinTheta = np.sin(theta)

    # Wave numbers for each mode
    km = 2 * np.pi * fc + dk * np.arange(Nmodes)
    iy = np.arange(1, Ny + 1)
    z_ss = np.zeros((Nx, Ny))

    # Loop over all modes to construct the terrain
    for ii in range(Nmodes):
        kmx = km[ii] * cosTheta[ii] * dx
        kmy = km[ii] * sinTheta[ii] * dx
        ampl = np.sqrt(roughness_factor / km[ii] ** 2)
        ampl = ampl * np.sqrt(dk * 4 * np.pi)
        for ix in np.arange(1, Nx + 1):
            mode = ampl * np.cos(kmx * ix + kmy * iy + alpha[ii])
            z_ss[ix - 1, :] += mode

    # Normalize the terrain heights
    z_ss -= z_ss.min()
    z_ss /= z_ss.max()
    z_ss *= z_max

    # Compute height levels
    k_terrain = np.ceil(z_ss / dx).astype(int) + k_min

    if viz:
        fig, axs = plt.subplots(1, 2)
        im0 = axs[0].imshow(
            z_ss.T,
            origin="lower",
            extent=[x_axis[0], x_axis[-1], y_axis[0], y_axis[-1]],
        )
        fig.colorbar(im0, ax=axs[0], fraction=0.046, pad=0.04)
        axs[0].set_title("Perlin Noise")

        im1 = axs[1].imshow(
            k_terrain.T,
            origin="lower",
            extent=[x_axis[0], x_axis[-1], y_axis[0], y_axis[-1]],
        )
        fig.colorbar(im1, ax=axs[1], fraction=0.046, pad=0.04)
        axs[1].set_title("Perlin Terrain")
        plt.tight_layout()
        plt.show()

        viz_surf(z_ss, x_axis, y_axis)
        viz_surf(k_terrain, x_axis, y_axis)
        viz_surf_spectra(z_ss, x_axis, y_axis, nexp=6)

    if return_heights_z:
        return k_terrain, z_ss
    else:
        return k_terrain


def disc_terrain_atlas(
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
        ax.plot(src_xyz[0], src_xyz[2], ".", label="Source")
        # ax.plot(rcv_xyz[0], rcv_xyz[2], '.', label='Receiver')
        ax.plot(rcv_a_xyz[0], rcv_a_xyz[2], ".", label="Receiver a")
        ax.plot(rcv_b_xyz[0], rcv_b_xyz[2], ".", label="Receiver b")
        ax.plot(rcv_c_xyz[0], rcv_c_xyz[2], ".", label="Receiver c")
        ax.legend()
        ax.set_title(i_name + " profile (" + str(profile_idx) + ")")
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


# %% Sim4Life H5 Plugin
def get_voxels_s4l(h5f):
    """
    Extract the voxel grid from a Sim4Life acoustic simulation H5 input file that has the necessary discretization (voxeling) data.

    Parameters:
    - h5f (str): The path to the H5 file.

    Returns:
    tuple: (origin, dx, dims, voxels)
    """
    # Axis are defined at points, voxels at cell centers
    # Get dimensions
    axis_x = find_h5_dataset(h5f, "/Meshes", "axis_x")
    axis_y = find_h5_dataset(h5f, "/Meshes", "axis_y")
    axis_z = find_h5_dataset(h5f, "/Meshes", "axis_z")
    # Get voxels
    voxels = find_h5_dataset(h5f, "/Meshes", "voxels")
    # Get material id look up table
    grp_lut = find_h5_group(h5f, "/Meshes", "name_map")
    N_mats = get_h5_attribute(h5f, grp_lut, "_num_entries")
    mats_lut = []
    for i in range(N_mats):
        mat_name = get_h5_attribute(h5f, grp_lut, f"_{i}")
        # String data is probably in bytes. Convert it
        if isinstance(mat_name, bytes):
            mat_name = mat_name.decode("utf-8")
        mats_lut.append(mat_name)

    Nx = np.size(axis_x) - 1
    Ny = np.size(axis_y) - 1
    Nz = np.size(axis_z) - 1
    dims = np.array([Nx, Ny, Nz])
    dx = axis_x[1] - axis_x[0]

    origin = np.array([axis_x[0], axis_y[0], axis_z[0]]) + dx / 2

    return (origin, dx, dims, voxels, mats_lut)


# %%
