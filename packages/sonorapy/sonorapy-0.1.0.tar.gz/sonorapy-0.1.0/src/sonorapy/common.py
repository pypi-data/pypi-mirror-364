# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import numpy as np


def log_interp(zz, xx, yy):
    logz = np.log10(zz)
    logx = np.log10(xx)
    logy = np.log10(yy)
    return np.power(10.0, np.interp(logz, logx, logy))


def logx_interp(zz, xx, yy):
    logz = np.log10(zz)
    logx = np.log10(xx)
    return np.interp(logz, logx, yy)


def getClosestIdxFromTime(t, t_axis):
    """
    Given a time value, find the index and time in t_axis closest to it
    idx = getClosestIdxFromTime(t, t_axis)
    """
    idx = (np.abs(t_axis - t)).argmin()
    return idx


def cutSignal(t, x, t_min, t_max):
    t_min = getClosestIdxFromTime(t_min, t)
    t_max = getClosestIdxFromTime(t_max, t) + 1
    t = t[t_min:t_max]
    x = x[t_min:t_max]
    return (t, x)


def padAxes(axis, n_left, n_right, dx=None):
    if dx == None:
        dx = axis[1] - axis[0]
    n_padding = np.arange(-n_left, 0) * dx + axis[0]
    p_padding = np.arange(1, n_right + 1) * dx + axis[-1]
    return np.concatenate((n_padding, axis, p_padding))


def mean_absolute_error(a, b):
    return np.mean(np.abs(a - b))


def root_mean_squared_error(a, b):
    return np.sqrt(np.mean(np.square(a - b)))


def normalized_cross_correlation(a, b):
    a_mean = np.mean(a)
    b_mean = np.mean(b)
    a_std = np.std(a)
    b_std = np.std(b)
    return np.mean((a - a_mean) * (b - b_mean)) / (a_std * b_std)


def relative_error(a, b, abs_threshold=1e-12):
    abs_diff = np.abs(a - b)
    rel_diff = abs_diff / (np.abs(a) + np.abs(b) + np.finfo(float).eps)
    return np.mean(np.where(abs_diff < abs_threshold, 0, rel_diff))
