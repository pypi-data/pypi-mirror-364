# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import ScalarFormatter
from scipy.interpolate import interp1d

from .analysis import calc_3rd_octaves, calc_energy, calc_fft_db
from .common import mean_absolute_error, relative_error
from .h5 import get_h5_dataset, get_h5_dataset_names
from .io import get_c0, get_point_sensors, get_sim_name, get_snr0_position


# %% Surfaces
def get_pt_energy(of_name, src_idx=0, ref_idx=1):
    """
    Visualizes the 3D surface represented by the z_surface array using matplotlib.

    Parameters:
        z_surf (numpy.ndarray): A 2D array of surface elevation data.
        x_axis (numpy.ndarray): Array of x-coordinates.
        y_axis (numpy.ndarray): Array of y-coordinates.

    Returns:
        None: Displays a 3D plot of the surface.
    """
    pts = get_point_sensors(of_name)
    pt_src = pts[src_idx]
    pt_ref = pts[ref_idx]
    xyz_src = pt_src["xyz"]
    enrg_ref = calc_energy(pt_ref["t"], pt_ref["p"])[0]
    energies = []
    dists = []
    for pt in pts[ref_idx:]:
        pt_d = np.linalg.norm(pt["xyz"] - xyz_src)
        enrg = calc_energy(pt["t"], pt["p"])[0]
        enrg_db = 10 * np.log10(enrg / enrg_ref)
        energies.append(enrg_db)
        dists.append(pt_d)
    return np.array(energies), np.array(dists)
