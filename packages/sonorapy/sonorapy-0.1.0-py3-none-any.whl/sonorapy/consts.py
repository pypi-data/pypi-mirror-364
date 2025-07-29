# -*- coding: utf-8 -*-
import numpy as np

# Octave bands
f_octave_names = np.array([63, 125, 250, 500, 1000, 2000, 4000, 8000])

# Third octave bands
f_3octave_names = np.array(
    [
        16,
        20,
        25,
        31.5,
        40,
        50,
        63,
        80,
        100,
        125,
        160,
        200,
        250,
        315,
        400,
        500,
        630,
        800,
        1000,
        1250,
        1600,
        2000,
        2500,
        3150,
        4000,
        5000,
        6300,
        8000,
        10000,
    ]
)

# A-filter in third octave bands
a_3bands = np.array(
    [
        -56.7,
        -50.5,
        -44.7,
        -39.4,
        -34.6,
        -30.2,
        -26.2,
        -22.5,
        -19.1,
        -16.1,
        -13.4,
        -10.9,
        -8.6,
        -6.6,
        -4.8,
        -3.2,
        -1.9,
        -0.8,
        0.0,
        0.6,
        1.0,
        1.2,
        1.3,
        1.2,
        1.0,
        0.5,
        -0.1,
        -1.1,
        -2.5,
    ]
)

# Room temperature in celcius
Tc_room = 20


def calc_3octave_bands(fc_range=None):
    """
    Get third octave bands, corners, and nomimal name

    Parameters:
        fc_range (list): Elements indicating (center) frequency range.

    Returns:
        center, left, right and nominal frequency
    """
    G = 10 ** (3 / 10)
    freqs = 1000 * G ** (np.arange(-18 - 0.5, 5 + 0.5, 0.5) / 3)
    f3o_l = freqs[:-2:2]
    f3o_c = freqs[1:-1:2]
    f3o_r = freqs[2::2]
    f3o_id = f_3octave_names[f_3octave_names < f3o_r[-1]]
    if fc_range is not None:
        mask = (f3o_c >= fc_range[0]) & (f3o_c <= fc_range[1])
        f3o_l = f3o_l[mask]
        f3o_c = f3o_c[mask]
        f3o_r = f3o_r[mask]
        f3o_id = f3o_id[mask]
    return f3o_c, f3o_l, f3o_r, f3o_id


f3o_c, f3o_l, f3o_r, f3o_id = calc_3octave_bands()
