# -*- coding: utf-8 -*-
import numpy as np
import scipy.signal as signal


def get3rdOctaves(t, p_in):
    """
    Calculates 3rd octave bands for the given time-domain signal.

    Parameters:
        t (array): Time array
        p_in (array): Time-domain input signal

    Returns:
        tuple: Filtered signal in dB, center frequencies, lower and upper frequencies for each band
        (signal_bandfiltered_dB, freq_c, freq_lo, freq_up)
    """
    fs = 1.0 / (t[1] - t[0])
    nyquistRate = fs / 2
    p0 = 2e-5  # Reference pressure

    # Calculate mid frequencies
    G = 10 ** (3 / 10)
    freqs = 1000 * G ** (np.arange(-18 - 0.5, 5 + 0.5, 0.5) / 3)
    freq_c = freqs[1:-1:2]
    freq_up = freqs[2::2]
    freq_lo = freqs[:-2:2]

    # Initialize arrays
    signal_bandfiltered = np.zeros((len(freq_c), len(p_in)))
    signal_bandfiltered_rms = np.zeros(len(freq_c))

    # Loop through bands
    for i, (lower, upper) in enumerate(zip(freq_lo, freq_up)):
        # Create bandpass filter
        # Determine numerator (b) and denominator (a) coefficients of the digital
        # Infinite Impulse Response (IIR) filter.
        sos = signal.butter(
            N=6,
            Wn=np.array([lower, upper]) / nyquistRate,
            btype="bandpass",
            output="sos",
        )
        # Filter signal
        signal_bandfiltered[i, :] = signal.sosfiltfilt(sos, p_in)
        # Calculate RMS value
        signal_bandfiltered_rms[i] = np.sqrt(
            np.mean(np.power(signal_bandfiltered[i, :], 2))
        )

    # Convert to dB
    signal_bandfiltered_dB = 20 * np.log10(signal_bandfiltered_rms / p0)
    return signal_bandfiltered_dB, freq_c, freq_lo, freq_up


def bands2SPL(pf):
    """
    Converts 3rd octave band levels to a single sound pressure level (SPL).

    Parameters:
        pf (array): Array of 3rd octave band levels in dB

    Returns:
        float: Equivalent sound pressure level in dB
    """
    return 10 * np.log10(np.sum(10 ** (pf / 10)))
