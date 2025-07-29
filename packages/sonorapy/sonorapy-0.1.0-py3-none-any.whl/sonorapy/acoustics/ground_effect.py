# -*- coding: utf-8 -*-
import numpy as np


def wofz(z, N):
    """
    Computes the Faddeeva function, also known as w(z).

    Parameters:
        z (complex): The complex number for which w(z) is calculated.
        N (int): Number of terms in the rational series.

    Returns:
        complex: The value of w(z).

    Notes:
        The function computes w(z) = exp(-z^2) erfc(-iz) using a rational
        series with N terms. Assumes that Im(z) >= 0.
        Algorithm is based on Weideman 1994.
    """
    M = 2 * N
    M2 = 2 * M
    k = np.arange(-M + 1, M)
    L = np.sqrt(N / np.sqrt(2))
    theta = k * np.pi / M
    t = L * np.tan(theta / 2)
    f = np.exp(-(t**2)) * (L**2 + t**2)
    f = np.append([0], f)
    a = np.real(np.fft.fft(np.fft.fftshift(f))) / M2
    a = a[1 : N + 1][::-1]
    Z = (L + 1j * z) / (L - 1j * z)
    p = np.polyval(a, Z)
    w = 2 * p / (L - 1j * z) ** 2 + (1 / np.sqrt(np.pi)) / (L - 1j * z)
    return w


def ground_effect(f, Z, D, Hr, Hs, c0=344):
    """
    Calculates the ground effect for sound propagation.

    Parameters:
        f (array): Frequency vector in Hz.
        Z (array): Impedance vector at each frequency.
        D (float): Horizontal distance in meters.
        Hr (float): Receiver height in meters.
        Hs (float): Source height in meters.
        c0 (float, optional): Speed of sound in m/s. Default is 344.

    Returns:
        array: Ground effect in dB.
    """
    # Conjugate signal since this code uses another e**jw convention
    Z = Z.conj()

    # Geometry
    Ddir = np.sqrt((Hr - Hs) ** 2 + D**2)
    Drefl = np.sqrt((Hr + Hs) ** 2 + D**2)
    delay = (Drefl - Ddir) / c0  # time delay in sec
    SinChi = (Hr + Hs) / Drefl

    # Spherical wave reflection factor
    rp = (SinChi - 1 / Z) / (SinChi + 1 / Z)  # plane wave reflection factor
    w = (1 + 1j) / 2 * np.sqrt(2 * np.pi / c0 * f * Drefl) * (SinChi + 1 / Z)
    F = np.zeros_like(w)
    for jj in np.arange(w.size):
        F[jj] = 1 + 1j * np.sqrt(np.pi) * w[jj] * wofz(w[jj], 100)

    # Compute the ground effect
    Q = rp + (1 - rp) * F
    # Sum of contributions relative to direct sound
    A = 1 + Q * np.exp(1j * 2 * np.pi * f * delay) / Drefl * Ddir
    GrFXexact = 20 * np.log10(np.abs(A))
    return GrFXexact
