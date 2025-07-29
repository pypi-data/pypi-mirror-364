# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit

from ..acoustics import ground_effect


def reflection_coeff(z0, z1):
    """
    Calculate reflection coefficient from two impedances

    Parameters:
        z0, z1 (float/array): Impedances

    Returns:
        float/array: Reflection coefficient.

    Notes:
        (z1-z0)/(z1+z0)
    """
    return (z1 - z0) / (z1 + z0)


def transmission_coeff(z0, z1):
    """
    Calculate transmission coefficient from two impedances

    Parameters:
        z0, z1 (float/array): Impedances [SI]

    Returns:
        float/array: Reflection coefficient [0,1]

    Notes:
        2*z1/(z1+z0)
    """
    return 2 * z1 / (z1 + z0)


def absorption_coeff(r):
    """
    Calculate absorption coefficient from reflection coefficient

    Parameters:
        r (float/array): Reflection coefficient [0,1]

    Returns:
        float/array: Absorption coefficient [0,1]

    Notes:
        1 - abs(R)**2
    """
    return 1 - np.abs(r) ** 2


def absorption2impedance(a, z0):
    """
    Calculate normalized impedance (z/z0) from absorption (a) and characteristic impedance (z0)

    Parameters:
        a (float): Absorption coefficient [0,1]
        z0 (float): Characteristic impedance. Typically rho*c or air [SI]

    Returns:
        float: Normalized impedance factor k []

    Notes:
        Assuming the following relations and assuming normalized impedance is real:
        alpha = 1 - R**2
        R = (z1 - z0)/(z1 + z0)
        z1 = k * z0

        Two possible solutions for k, but only use positive one
        k1 = -(a + 2 * np.sqrt(1 - a) - 2)/a
        k2 = (-a + 2 * np.sqrt(1 - a) + 2)/a
    """
    coef = (-a + 2 * np.sqrt(1 - a) + 2) / a
    assert np.all(reflection_coeff(z0, coef * z0) >= 0)
    return coef


def z_bc2(f, a2n, a1n, a0, a1):
    """
    Calculate normalized impedance coefficient (Z/Z0) for BC2 model

    Parameters:
        f (array): Frequency [Hz]
        a2n, a1n, a0, a1 (float): Model parameters.

    Returns:
        array: Normalized impedance []

    Notes:
        a2n * (jw)**-2 + a1n * (jw)**-1 + a0 + a1 * (jw)
    """
    jomega = 1j * 2 * np.pi * f
    return a2n * jomega**-2 + a1n * jomega**-1 + a0 + a1 * jomega


def z_bc1(f, a1n, a0, a1):
    """
    Calculate normalized impedance coefficient (Z/Z0) for BC1 model

    Parameters:
        f (array): Frequency [Hz]
        a1n, a0, a1 (float): Model parameters.

    Returns:
        array: Normalized impedance []

    Notes:
        a1n * (jw)**-1 + a0 + a1 * (jw)
    """
    return z_bc2(f, 0, a1n, a0, a1)


def z_bc2_kurt(f, sigma):
    """
    Normalized impedance coefficient (Z/Z0) for BC2 model using pre-defined lookup table for sigma

    Parameters:
        f (array): Frequency [Hz]
        sigma (float): Static air flow resistivity [kPa s m^-2]

    Returns:
        array: Normalized impedance []

    Notes:
        Heutschi, Kurt, Matthias Horvath, and Jan Hofmann. "Simulation of ground impedance in
        finite difference time domain calculations of outdoor sound propagation." 2005.
    """
    lut_bc2 = np.array(
        [
            [50, -1.86e6, 4.54e3, 2.56, 0.0],
            [100, -4.58e6, 8.49e3, 3.14, 0.0],
            [150, -8.23e6, 1.21e4, 3.44, 0.0],
            [200, -1.22e7, 1.54e4, 3.68, 0.0],
            [300, -2.09e7, 2.22e4, 4.29, 0.0],
            [1000, -9.19e7, 6.36e4, 6.93, 0.0],
            [20000, -2.44e9, 8.10e5, 32.6, 0.0],
        ]
    )

    if sigma in lut_bc2[:, 0]:
        i = np.where(lut_bc2[:, 0] == sigma)[0][0]
        a2n = lut_bc2[i, 1]
        a1n = lut_bc2[i, 2]
        a0 = lut_bc2[i, 3]
        a1 = lut_bc2[i, 4]
        return z_bc2(f, a2n, a1n, a0, a1)
    else:
        print("Sigma", sigma, "not found")
        return []


def z_bc1_kurt(f, sigma):
    """
    Normalized impedance coefficients (Z/Z0) for BC1 model using pre-defined lookup table for sigma.

    Parameters:
        f (array): Frequency [Hz]
        sigma (float): Static air flow resistivity [kPa s m^-2]

    Returns:
        array: Normalized impedance []

    Notes:
        Heutschi, Kurt, Matthias Horvath, and Jan Hofmann. "Simulation of ground impedance in
        finite difference time domain calculations of outdoor sound propagation." 2005.
    """
    lut_bc1 = np.array(
        [
            [50, 4.60e3, 4.65, 0.0],
            [100, 8.46e3, 5.78, 0.0],
            [150, 1.20e4, 6.63, 0.0],
            [200, 1.57e4, 7.06, 0.0],
            [300, 2.20e4, 8.13, 0.0],
            [1000, 6.32e4, 12.4, 0.0],
            [20000, 7.75e5, 46.7, 0.0],
        ]
    )

    if sigma in lut_bc1[:, 0]:
        i = np.where(lut_bc1[:, 0] == sigma)[0][0]
        a1n = lut_bc1[i, 1]
        a0 = lut_bc1[i, 2]
        a1 = lut_bc1[i, 3]
        return z_bc1(f, a1n, a0, a1)
    else:
        print("Sigma", sigma, "not found")
        return []


def z_db(f, sigma):
    """
    Normalized impedance (Z/Z0) for DB model

    Parameters:
        f (array): Frequency [Hz]
        sigma (float): Static air flow resistivity [kPa s m^-2]

    Returns:
        array: Normalized impedance []

    Notes:
        1 + 9.08 * (f/sigma)**-.75 - 1j*11.9 * (f/sigma)**-.73
        Using e**(jw t) convention
    """
    return 1 + 9.08 * (f / sigma) ** -0.75 - 1j * 11.9 * (f / sigma) ** -0.73


def k_db(f, sigma, c0):
    """
    Wavenumber for DB model

    Parameters:
        f (array): Frequency [Hz]
        sigma (float): Static air flow resistivity [kPa s m^-2]
        c0 (float): Speed of sound [m s^-1]

    Returns:
        array: Wavenumber [m^-1]

    Notes:
        w / c0 * ( 1 + 10.8 * (f/sigma)**-0.70 - 1j * 10.3 * (f/sigma)**-0.59 )
        Using e**(jw t) convention
    """
    return (
        2
        * np.pi
        * f
        / c0
        * (1 + 10.8 * (f / sigma) ** -0.70 - 1j * 10.3 * (f / sigma) ** -0.59)
    )


def z_miki(f, sigma):
    """
    Normalized impedance (Z/Z0) for Miki model

    Parameters:
        f (array): Frequency [Hz]
        sigma (float): Static air flow resistivity [kPa s m^-2]

    Returns:
        array: Normalized impedance []

    Notes:
        1 + 5.50 * (f/sigma)**-.632 - 1j*8.43 * (f/sigma)**-.632
        Using e**(jw t) convention
    """
    return 1 + 5.50 * (f / sigma) ** -0.632 - 1j * 8.43 * (f / sigma) ** -0.632


def k_miki(f, sigma, c0):
    """
    Wavenumber for Miki model

    Parameters:
        f (array): Frequency [Hz]
        sigma (float): Static air flow resistivity [kPa s m^-2]
        c0 (float): Speed of sound [m s^-1]

    Returns:
        array: Wavenumber [m^-1]

    Notes:
        w / c0 * (1 + 7.81*(f/sigma)**-0.618 - 1j*11.41 * (f/sigma)**-.618)
        Using e**(jw t) convention
    """
    return (
        2
        * np.pi
        * f
        / c0
        * (1 + 7.81 * (f / sigma) ** -0.618 - 1j * 11.41 * (f / sigma) ** -0.618)
    )


def z_iir1(f, a1, b0, b1):
    """
    Normalized impedance (Z/Z0) for IIR1 model

    Parameters:
        f (array): Frequency [Hz]
        a2n, a1n, a0, a1 (float): Model parameters.

    Returns:
        array: Normalized impedance []

    Notes:
        (b0 + b1 * jw) / (1 + a1 * jw)
    """
    jomega = 1j * 2 * np.pi * f
    return (b0 + b1 * jomega) / (1 + a1 * jomega)


def z_poles(f, a0, a1, b0, b1):
    """
    Normalized impedance (Z/Z0) for poles model

    Parameters:
        f (array): Frequency [Hz]
        a0, a1, b0, b1 (float): Model parameters.

    Returns:
        array: Normalized impedance []

    Notes:
        a0 / (a1 - jw) + b0 / (b1 - jw)
    """
    jomega = 1j * 2 * np.pi * f
    return a0 / (a1 - jomega) + b0 / (b1 - jomega)


def z_rational(f, a1, a2, b0, b1, b2):
    """
    Normalized impedance (Z/Z0) for rational model

    Parameters:
        f (array): Frequency [Hz]
        a1, a2, b0, b1, b2 (float): Model parameters.

    Returns:
        array: Normalized impedance []

    Notes:
        (b0 + b1 * jw + b2 * jw**2) / (1 + a1 * jw + a2 * jw**2)
    """
    jomega = 1j * 2 * np.pi * f
    return (b0 + b1 * jomega + b2 * jomega**2) / (1 + a1 * jomega + a2 * jomega**2)


def z_layered_backed(k, z, d):
    """
    Complex impedance for layered absorber with rigid backing

    Parameters:
        k (float): Wavenumber [m^-1]
        z (float): Impedance [kPa s m^-2]
        d (float): Thickness [m]

    Returns:
        array: Complex impedance [SI]
    """
    return -1j * z / np.tan(d * k)


# %% Fit
def fit_zcomplex(
    f, out, z_func, p_init=None, log_fit=True, bounds=(0, np.inf), plot=False
):
    """
    Fits complex data to a given impedance model

    Parameters:
        f (array): Frequency [Hz]
        out (array): Complex impedance
        z_func (function): Impedance model function to fit
        p_init (array): Initial guess for the parameters. If None, a default will be used
        log_fit (bool): Whether to fit output data in log space
        bounds (tuple): Bounds for the parameters, default (0, np.inf)
        plot (bool): Whether to plot the data and fit

    Returns:
        array: Fitted parameters

    Notes:
        Algorithm is based on https://stackoverflow.com/questions/50203879/curve-fitting-of-complex-data/50203979
    """
    out_real, out_imag = np.real(out), np.imag(out)
    if log_fit:
        out_real = 10 * np.log10(out_real**2)
        out_imag = 10 * np.log10(out_imag**2)
    out_stacked = np.hstack([out_real, out_imag])

    def stacked_model(f, *params):
        z_val = z_func(f, *params)
        N = len(f) // 2
        z_real, z_imag = np.real(z_val[:N]), np.imag(z_val[N:])
        if log_fit:
            z_real = 10 * np.log10(z_real**2)
            z_imag = 10 * np.log10(z_imag**2)
        return np.hstack([z_real, z_imag])

    # Determine the number of parameters required by z_func if p_init is not provided
    if p_init is None:
        import inspect

        params_count = len(inspect.signature(z_func).parameters) - 1
        p_init = np.ones(params_count)

    popt, _ = curve_fit(
        stacked_model,
        np.hstack([f, f]),
        out_stacked,
        p0=p_init,
        bounds=bounds,
        maxfev=10000,
    )

    if plot:
        plot_fit(f, out, z_func, popt)

    return popt


def fit_zmag(f, out, z_func, p_init=None, log_fit=True, bounds=(0, np.inf), plot=False):
    """
    Fits magnitude data to a given impedance model.

    Parameters:
        f (array): Frequency [Hz]
        out (array): Absolute value of impedance
        z_func (function): Impedance model function
        p_init (list or array): Initial guess for the parameters. If None, a default will be used
        log_fit (bool): Whether to use logarithmic fit
        bounds (tuple): Bounds for the parameters, default (0, np.inf)
        plot (bool): Whether to plot the data and fit

    Returns:
        array: Fitted parameters

    Notes:
        Algorithm is based on https://stackoverflow.com/questions/50203879/curve-fitting-of-complex-data/50203979
    """
    # Make sure all magnitudes are greater than or equal to 0
    assert np.all(out >= 0)

    out_mag = np.copy(out)
    if log_fit:
        out_mag = np.log10(out)

    def model(f, *params):
        z_val = np.abs(z_func(f, *params))
        if log_fit:
            z_val = np.log10(z_val)
        return z_val

    # Determine the number of parameters required by z_func if p_init is not provided
    if p_init is None:
        import inspect

        params_count = len(inspect.signature(z_func).parameters) - 1
        p_init = np.ones(params_count)

    popt, _ = curve_fit(model, f, out_mag, p0=p_init, bounds=bounds, maxfev=10000)

    if plot:
        plot_fit(f, out, z_func, popt)

    return popt


def plot_fit(f, out, z_func, popt):
    """
    Plots the real and imaginary parts, magnitude, and phase of the data and fit.

    Parameters:
        f (array): Frequency vector.
        out (array): Complex impedance data.
        z_func (function): Impedance model function.
        popt (array): Fitted parameters.
    """
    z_fit = z_func(f, *popt)
    # TODO: Improve
    plt.figure()
    plt.subplot(221)
    plt.plot(f, np.real(out), f, np.real(z_fit))
    plt.xscale("log")
    plt.title("Real")
    plt.legend(["Z", "Z Fit"])
    plt.subplot(222)
    plt.plot(f, -np.imag(out), f, -np.imag(z_fit))
    plt.xscale("log")
    plt.title("-Imag")
    plt.subplot(223)
    plt.plot(f, np.abs(out), f, np.abs(z_fit))
    plt.xscale("log")
    plt.title("Abs")
    plt.subplot(224)
    plt.plot(f, np.angle(out, deg=True), f, np.angle(z_fit, deg=True))
    plt.xscale("log")
    plt.title("Phase")
    plt.tight_layout()
    plt.show()


def fit_groundeffect(f, out, D, Hr, Hs, z_func, plot=False):
    """
    Fits ground effect data to a given impedance model.

    Parameters:
        f (array): Frequency [Hz]
        out (array): Ground effect data
        D, Hr, Hs (float): Distance and heights
        z_func (function): Impedance model function
        plot (bool): Whether to plot the data and fit

    Returns:
        array: Fitted parameters
    """

    def gfx_func(f, *params):
        z = z_func(f, *params)
        return ground_effect(f, z, D, Hr, Hs)

    popt, _ = curve_fit(gfx_func, f, out, maxfev=10000)

    if plot:
        gfx_fit = gfx_func(f, *popt)
        plt.figure()
        plt.plot(f, out, f, gfx_fit)
        plt.xscale("log")
        plt.legend(["GFX", "GFX Fit"])
        plt.tight_layout()
        plt.show()

    return popt


def get_miki_iir1_params(sigma, fmin=112, fmax=2239):
    """
    Get IIR1 model fit parameters from Miki model for a given sigma

    Parameters:
        sigma (float): Static air flow resistivity [kPa s m^-2]
        fmin, fmax (float): Frequency range on which to optimize [Hz]
        c0 (float): Speed of sound [m s^-1]

    Returns:
        array: IIR1 model parameters

    Notes:
        We first use a linear fit, and then use that as initial guess for a log fit
    """
    f_train_lin = np.linspace(fmin, fmax, 10000)
    f_train = np.geomspace(fmin, fmax, 10000)

    # Use linear fit first, and then use that as initial guess for log fit
    z_params_guess = fit_zcomplex(
        f_train, z_miki(f_train_lin, sigma), z_iir1, log_fit=False
    )
    z_params = fit_zcomplex(
        f_train, z_miki(f_train, sigma), z_iir1, p_init=z_params_guess, log_fit=True
    )
    return z_params


def get_db_iir1_params(sigma, fmin=112, fmax=2239):
    """
    Get IIR1 model fit parameters from Miki model for a given sigma

    Parameters:
        sigma (float): Static air flow resistivity [kPa s m^-2]
        fmin, fmax (float): Frequency range on which to optimize [Hz]
        c0 (float): Speed of sound [m s^-1]

    Returns:
        array: IIR1 model parameters

    Notes:
        We first use a linear fit, and then use that as initial guess for a log fit
    """
    f_train_lin = np.linspace(fmin, fmax, 10000)
    f_train = np.geomspace(fmin, fmax, 10000)

    # Use linear fit first, and then use that as initial guess for log fit
    z_params_guess = fit_zcomplex(
        f_train, z_db(f_train_lin, sigma), z_iir1, log_fit=False
    )
    z_params = fit_zcomplex(
        f_train, z_db(f_train, sigma), z_iir1, p_init=z_params_guess, log_fit=True
    )
    return z_params
