# -*- coding: utf-8 -*-
import numpy as np
from scipy.fft import rfft, rfftfreq
from scipy.signal import butter, filtfilt, sosfiltfilt


# %% Freq Analysis
def get_time_idx(t, t_axis):
    """
    Find the index in t_axis closest to a given time value.

    Parameters:
    t (float): The time value to find.
    t_axis (array-like): The time axis array.

    Returns:
    int: The index closest to t in t_axis.
    """
    idx = (np.abs(t_axis - t)).argmin()
    return idx


def cut_signal(t, x, t_min, t_max):
    """
    Cut a signal within a given time range.

    Parameters:
    t (array-like): The time axis array.
    x (array-like): The signal array.
    t_min (float): The minimum time for cutting.
    t_max (float): The maximum time for cutting.

    Returns:
    tuple: The cut time and signal arrays.
    """
    t_min = get_time_idx(t_min, t)
    t_max = get_time_idx(t_max, t) + 1
    t_cut = t[t_min:t_max]
    x_cut = x[t_min:t_max]
    return (t_cut, x_cut)


def calc_fft(t, p_t, t_min=None, t_max=None, f_res=None, window=False):
    """
    Compute the Fast Fourier Transform (FFT) of a signal.

    Parameters:
    t (array-like): The time axis array.
    x (array-like): The signal array.
    t_min (float, optional): The minimum time for FFT calculation.
    t_max (float, optional): The maximum time for FFT calculation.
    f_res (float, optional): The frequency resolution.

    Returns:
    tuple: The frequency and FFT arrays.
    """

    if t_min is not None:
        t_min = get_time_idx(t_min, t)
    if t_max is not None:
        t_max = get_time_idx(t_max, t) + 1
    p_t_cut = p_t[t_min:t_max]
    dt = t[1] - t[0]

    # Apply window to the signal
    win = np.hanning(p_t_cut.size) if window else np.ones(p_t_cut.size)
    p_t_cut *= win
    p_f_complex = rfft(p_t_cut)
    f = rfftfreq(len(p_t_cut), dt)
    p_f = np.abs(p_f_complex / (np.sum(win) / 2))
    p_f[0] /= 2
    return f, p_f


def calc_fft_power(t, p_t, t_min=None, t_max=None, f_res=None, window=False):
    """
    Compute the Fast Fourier Transform (FFT) of a signal.

    Parameters:
    t (array-like): The time axis array.
    x (array-like): The signal array.
    t_min (float, optional): The minimum time for FFT calculation.
    t_max (float, optional): The maximum time for FFT calculation.
    f_res (float, optional): The frequency resolution.

    Returns:
    tuple: The frequency and FFT arrays.
    """
    f, pf = calc_fft(t, p_t, t_min, t_max, f_res, window)
    dt = t[1] - t[0]
    pf2 = np.abs(pf) ** 2
    pf2[0] *= 2
    pf2 *= len(p_t) * dt
    return f, pf2


def calc_fft_db(t, p_t, t_min=None, t_max=None, f_res=None, p0=2e-5, window=False):
    """
    Compute the FFT of a signal in decibels (dB).

    Parameters:
    t (array-like): The time axis array.
    x (array-like): The signal array.
    t_min (float, optional): The minimum time for FFT calculation.
    t_max (float, optional): The maximum time for FFT calculation.
    p0 (float, optional): The reference pressure level.
    window (bool, optional): Whether to apply a window function to the signal.

    Returns:
    tuple: The frequency array and FFT in dB.
    """
    f, p_f = calc_fft(t, p_t, t_min, t_max, f_res, window)
    # Ignore divide by zero error
    with np.errstate(divide="ignore"):
        p_f_db = 20 * np.log10(p_f / p0)
    return (f, p_f_db)


def filter_lowpass(t, data, cutoff, order=6):
    """
    Apply a low-pass filter to a signal.

    Parameters:
    t (array-like): The time axis array.
    data (array-like): The signal array.
    cutoff (float): The cutoff frequency.
    order (int, optional): The order of the filter.

    Returns:
    array-like: The filtered signal.
    """
    fs = 1 / (t[1] - t[0])
    nyq = 0.5 * fs  # Nyquist Frequency
    normal_cutoff = cutoff / nyq
    # Get the filter coefficients
    b, a = butter(order, normal_cutoff, btype="low", analog=False)
    y = filtfilt(b, a, data)
    return y


def calc_3rd_octaves(t, p_in, level="LE", zero_padding=50000):
    """
    Calculates 3rd octave bands for the given time-domain signal.

    Parameters:
        t (array): Time array
        p_in (array): Time-domain input signal
        level (str, optional): The level to calculate ('LE' or 'Leq')
        zero_padding (int, optional): Zero padding for the signal on both sides

    Returns:
        tuple: Filtered signal in dB, center frequencies, lower and upper frequencies for each band
        (signal_bandfiltered_dB, freq_c, freq_lo, freq_up)
    """
    dt = t[1] - t[0]
    fs = 1.0 / (dt)
    nyquistRate = fs / 2
    p0 = 2e-5

    # Zero padding to ensure that the signal is sufficiently long for the IIR filters
    p_padded = np.pad(p_in, (zero_padding, zero_padding), mode="constant")

    # calculate mid frequencies
    G = 10 ** (3 / 10)
    # freqs = 1000 * G ** (np.arange(-18 - 0.5, 5 + 0.5, 0.5) / 3)
    freqs = 1000 * G ** (np.arange(-18 - 0.5, 8 + 0.5, 0.5) / 3)
    freq_c = freqs[1:-1:2]
    freq_up = freqs[2::2]
    freq_lo = freqs[:-2:2]

    signal_bandfiltered = np.zeros((len(freq_c), len(p_padded)))
    signal_bandfiltered_level = np.zeros(len(freq_c))
    # loop through bands
    for i, (lower, upper) in enumerate(zip(freq_lo, freq_up)):
        # Determine numerator (b) and denominator (a) coefficients of the digital
        # Infinite Impulse Response (IIR) filter.
        sos = butter(
            N=3,
            Wn=np.array([lower, upper]) / nyquistRate,
            btype="bandpass",
            output="sos",
        )
        # Filter signal
        signal_bandfiltered[i, :] = sosfiltfilt(sos, p_padded)
        if level == "LE":  # Average over time
            signal_bandfiltered_level[i] = np.sum(signal_bandfiltered[i, :] ** 2) * dt
        elif level == "Leq":  # Average over time for 1 sec
            signal_bandfiltered_level[i] = np.mean(signal_bandfiltered[i, :] ** 2)
    # Convert to dB
    signal_bandfiltered_dB = 10 * np.log10(signal_bandfiltered_level / p0**2)
    return signal_bandfiltered_dB, freq_c, freq_lo, freq_up


def calc_3rd_octaves_from_fft(f, p_f, dt=None, p0=2e-5):
    # I'm assuming the f is calculated from rfft (half sided spectrum, last value represents max freq)
    if dt is None:
        dt = 1 / (f[-1] * 2)

    # Define third octave band center frequencies
    G = 10 ** (3 / 10)
    freqs = 1000 * G ** (np.arange(-18 - 0.5, 5 + 0.5, 0.5) / 3)
    freq_c = freqs[1:-1:2]
    freq_up = freqs[2::2]
    freq_lo = freqs[:-2:2]

    nf = len(p_f)  # Total number of data points in FFT
    bands = []
    for lower, upper in zip(freq_lo, freq_up):
        # Find indices corresponding to the current band
        band_indices = np.where((f >= lower) & (f <= upper))[0]
        band_energy = np.sum(p_f[band_indices] ** 2) * dt * nf  # LE
        bands.append(band_energy)

    # Convert to dB
    bands = np.array(bands)

    # Ignore divide by zero error
    with np.errstate(divide="ignore"):
        bands_dB_LE = 10 * np.log10(bands / p0**2)
    return bands_dB_LE, freq_c, freq_lo, freq_up


def calc_3rd_octaves_from_fft_db(f, p_f_db, dt=None, p0=2e-5):
    p_f = 10 ** (p_f_db / 20)
    if p0 is None:
        # Calculate reference level (constant frequency amplitude)
        p_3, f_3, f_3l, f_3u = calc_3rd_octaves_from_fft(f, p_f, dt)
        p_3_ref, _, _, _ = calc_3rd_octaves_from_fft(f, p_f * 0 + 1, dt)
        p_3 -= p_3_ref
    else:
        p_3, f_3, _, _ = calc_3rd_octaves_from_fft(f, p_f, dt, p0=p0)
    return p_3, f_3, f_3l, f_3u


def calc_energy(t, p):
    dt = t[1] - t[0]

    Et = np.sum(np.abs(p) ** 2) * dt

    _, pf = calc_fft(t, p)
    pf2 = np.abs(pf) ** 2
    pf2[0] *= 2
    Ef = np.sum(pf2) * len(p) * dt

    return Et, Ef
