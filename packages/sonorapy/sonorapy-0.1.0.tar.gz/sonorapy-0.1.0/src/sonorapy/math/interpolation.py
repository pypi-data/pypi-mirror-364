# -*- coding: utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt

def log_interp(zz, xx, yy):
    """
    Perform interpolation on logarithmically scaled data.

    Parameters:
    zz (array-like): The x-coordinates at which to evaluate the interpolated values.
    xx (array-like): The x-coordinates of the data points.
    yy (array-like): The y-coordinates of the data points.

    Returns:
    array-like: Interpolated values at zz.
    """
    # Interpolate in the log-space and then transform back
    logz = np.log10(zz)
    logx = np.log10(xx)
    logy = np.log10(yy)
    return np.power(10.0, np.interp(logz, logx, logy))

def logx_interp(zz, xx, yy):
    """
    Perform interpolation with logarithmically scaled x-axis and linearly scaled y-axis.

    Parameters:
    zz (array-like): The x-coordinates at which to evaluate the interpolated values.
    xx (array-like): The x-coordinates of the data points.
    yy (array-like): The y-coordinates of the data points.

    Returns:
    array-like: Interpolated values at zz.
    """
    # Interpolate in the log-space for x-axis and linear space for y-axis
    logz = np.log10(zz)
    logx = np.log10(xx)
    return np.interp(logz, logx, yy)