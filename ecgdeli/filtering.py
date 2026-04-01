"""
ECG Filtering algorithms - Python port of ECGdeli Filtering/ folder.

Includes:
  - isoline_correction : remove DC offset via histogram mode
  - ecg_high_filter    : highpass Butterworth / Gaussian filter
  - ecg_low_filter     : lowpass Butterworth / Gaussian / smooth filter
  - ecg_high_low_filter: bandpass filter
  - ecg_baseline_removal: overlapping median-window baseline removal
  - notch_filter       : 50/60 Hz notch filter
"""

import numpy as np
from scipy import signal as sp_signal
from scipy.interpolate import PchipInterpolator


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _ensure_2d_col(arr):
    """Return (arr_2d, was_1d).  Always makes arr column-major (N x C)."""
    if arr.ndim == 1:
        return arr[:, np.newaxis].astype(float), True
    if arr.shape[0] < arr.shape[1]:
        return arr.T.astype(float), True   # was row-vector/row-major
    return arr.astype(float), False


def _sp0_extend(col_vec, n_left, n_right):
    """Constant (edge-value) padding on both sides of a 1D column vector."""
    left = np.full(n_left, col_vec[0])
    right = np.full(n_right, col_vec[-1])
    return np.concatenate([left, col_vec, right])


def _gaussian_hp_kernel(sigma, n=None):
    """1D highpass Gaussian kernel: δ - lowpass_gauss."""
    if n is None:
        n = 2 * int(round(4 * sigma)) + 1
    x = np.arange(n) - (n - 1) / 2.0
    h_lp = np.exp(-x ** 2 / (2 * sigma ** 2))
    h_lp /= h_lp.sum()
    h_hp = -h_lp.copy()
    h_hp[(n - 1) // 2] += 1.0
    return h_hp


def _gaussian_lp_kernel(sigma, n=None):
    """1D lowpass Gaussian kernel."""
    if n is None:
        n = 2 * int(round(4 * sigma)) + 1
    x = np.arange(n) - (n - 1) / 2.0
    h = np.exp(-x ** 2 / (2 * sigma ** 2))
    h /= h.sum()
    return h


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def isoline_correction(ecg_signal, n_bins=None):
    """Remove DC offset from every channel by subtracting the histogram mode.

    Parameters
    ----------
    ecg_signal : array (N,) or (N, C)
    n_bins     : number of histogram bins (default min(1024, N))

    Returns
    -------
    filtered : same shape as input
    offsets  : 1-D array of length C with the removed offset per channel
    """
    arr, was_1d = _ensure_2d_col(ecg_signal)
    N, C = arr.shape
    if n_bins is None:
        n_bins = min(1024, N)

    filtered = np.zeros_like(arr)
    offsets = np.zeros(C)

    for i in range(C):
        counts, edges = np.histogram(arr[:, i], bins=n_bins)
        centers = (edges[:-1] + edges[1:]) / 2.0
        offsets[i] = centers[np.argmax(counts)]
        filtered[:, i] = arr[:, i] - offsets[i]

    if was_1d:
        return filtered[:, 0], offsets
    return filtered, offsets


def ecg_high_filter(ecg_signal, samplerate, highpass_freq, filter_type='B'):
    """Highpass filter an ECG signal.

    Parameters
    ----------
    ecg_signal     : 1-D or 2-D numpy array (N,) or (N, C)
    samplerate     : sampling frequency in Hz
    highpass_freq  : cutoff frequency in Hz
    filter_type    : 'B'/'Butterworth' (default), 'G'/'Gauss', 'S'/'Smooth'

    Returns
    -------
    filtered : same shape as input
    """
    arr, was_1d = _ensure_2d_col(ecg_signal)
    N, C = arr.shape

    l = int(round(samplerate * 10))
    fc = min(highpass_freq, samplerate / 2 - 1)
    ft = filter_type.upper()[0]

    # Build extended signal (sp0 padding)
    ext = np.zeros((l + N + l, C))
    for i in range(C):
        ext[:, i] = _sp0_extend(arr[:, i], l, l)

    if ft in ('S', 'B'):
        sos = sp_signal.butter(3, 2 * fc / samplerate, btype='high', output='sos')
        for j in range(C):
            ext[:, j] = sp_signal.sosfiltfilt(sos, ext[:, j])
    elif ft == 'G':
        sigma = samplerate / (2 * np.pi * fc)
        h = _gaussian_hp_kernel(sigma)
        for i in range(C):
            ext[:, i] = np.convolve(ext[:, i], h, mode='same')

    filtered = ext[l:l + N, :]
    filtered, _ = isoline_correction(filtered)
    if isinstance(filtered, np.ndarray) and filtered.ndim == 1:
        filtered = filtered[:, np.newaxis]

    if was_1d:
        return filtered[:, 0]
    return filtered


def ecg_low_filter(ecg_signal, samplerate, lowpass_freq, filter_type='B'):
    """Lowpass filter an ECG signal.

    Parameters
    ----------
    ecg_signal    : 1-D or 2-D numpy array (N,) or (N, C)
    samplerate    : sampling frequency in Hz
    lowpass_freq  : cutoff frequency in Hz
    filter_type   : 'B'/'Butterworth' (default), 'G'/'Gauss', 'S'/'Smooth'

    Returns
    -------
    filtered : same shape as input
    """
    arr, was_1d = _ensure_2d_col(ecg_signal)
    N, C = arr.shape

    l = int(round(samplerate * 10))
    fc = min(lowpass_freq, samplerate / 2 - 1)
    ft = filter_type.upper()[0]

    ext = np.zeros((l + N + l, C))
    for i in range(C):
        ext[:, i] = _sp0_extend(arr[:, i], l, l)

    if ft == 'S':
        nw = max(1, int(round(samplerate / fc)))
        kernel = np.ones(nw) / nw
        for i in range(C):
            ext[:, i] = np.convolve(ext[:, i], kernel, mode='same')
    elif ft == 'G':
        sigma = samplerate / (2 * np.pi * fc)
        h = _gaussian_lp_kernel(sigma)
        for i in range(C):
            ext[:, i] = np.convolve(ext[:, i], h, mode='same')
    else:  # Butterworth
        sos = sp_signal.butter(3, 2 * fc / samplerate, btype='low', output='sos')
        for j in range(C):
            ext[:, j] = sp_signal.sosfiltfilt(sos, ext[:, j])

    filtered = ext[l:l + N, :]
    filtered, _ = isoline_correction(filtered)
    if isinstance(filtered, np.ndarray) and filtered.ndim == 1:
        filtered = filtered[:, np.newaxis]

    if was_1d:
        return filtered[:, 0]
    return filtered


def ecg_high_low_filter(ecg_signal, samplerate, hp_freq, lp_freq, filter_type='B'):
    """Bandpass filter: highpass then lowpass.

    Parameters
    ----------
    ecg_signal  : 1-D or 2-D numpy array
    samplerate  : sampling frequency in Hz
    hp_freq     : highpass cutoff in Hz
    lp_freq     : lowpass cutoff in Hz
    filter_type : 'B'/'Butterworth' (default), 'G'/'Gauss', 'S'/'Smooth'

    Returns
    -------
    filtered : same shape as input
    """
    filtered = ecg_high_filter(ecg_signal, samplerate, hp_freq, filter_type)
    filtered = ecg_low_filter(filtered, samplerate, lp_freq, filter_type)
    return filtered


def ecg_baseline_removal(ecg_signal, samplerate, window_length, overlap):
    """Remove baseline wander using overlapping median-filter windows.

    A sliding window computes local medians; they are PCHIP-interpolated to
    form the baseline estimate, which is then subtracted.

    Parameters
    ----------
    ecg_signal    : 1-D or 2-D numpy array (N,) or (N, C)
    samplerate    : sampling frequency in Hz
    window_length : window length in seconds
    overlap       : fractional overlap [0, 1)  or 1 (every sample is a center)

    Returns
    -------
    filtered_signal : baseline-removed signal (same shape as input)
    baseline        : estimated baseline (same shape as input)
    """
    arr, was_1d = _ensure_2d_col(ecg_signal)
    L, C = arr.shape
    arr = arr.astype(float)

    wl = int(round(window_length * samplerate))
    if wl % 2 == 0:
        wl += 1
    whl = (wl - 1) // 2

    if 0 <= overlap < 1:
        N_win = max(1, int((L - wl * overlap) / (wl * (1 - overlap))))
        center = (np.round(wl * (1 - overlap) * np.arange(N_win))
                  .astype(int) + whl)
        center = center[center < L]
    elif overlap == 1:
        center = np.arange(L)
    else:
        raise ValueError("overlap must be in [0, 1]")

    baseline = np.zeros_like(arr)
    filtered = np.zeros_like(arr)

    for j in range(C):
        bp = np.zeros(len(center))
        for i, c in enumerate(center):
            lo = max(c - whl, 0)
            hi = min(c + whl + 1, L)
            bp[i] = np.median(arr[lo:hi, j])

        if len(center) >= 2:
            pchip = PchipInterpolator(center, bp, extrapolate=True)
            baseline[:, j] = pchip(np.arange(L))
        else:
            baseline[:, j] = bp[0] if len(bp) else 0.0

        filtered[:, j] = arr[:, j] - baseline[:, j]
        # Isoline correction on this channel
        f_ch, off = isoline_correction(filtered[:, j])
        filtered[:, j] = f_ch
        baseline[:, j] += off[0] if np.ndim(off) > 0 else float(off)

    if was_1d:
        return filtered[:, 0], baseline[:, 0]
    return filtered, baseline


def notch_filter(ecg_signal, samplerate, notch_freq=50.0, bandwidth=1.0):
    """IIR notch (bandstop) filter.

    Parameters
    ----------
    ecg_signal  : 1-D or 2-D numpy array
    samplerate  : sampling frequency in Hz
    notch_freq  : center frequency to remove (default 50 Hz)
    bandwidth   : -3 dB bandwidth in Hz (default 1 Hz)

    Returns
    -------
    filtered : same shape as input
    """
    arr, was_1d = _ensure_2d_col(ecg_signal)
    N, C = arr.shape

    w0 = notch_freq / (samplerate / 2)
    Q = notch_freq / bandwidth
    b, a = sp_signal.iirnotch(w0, Q)

    filtered = np.zeros_like(arr)
    for j in range(C):
        filtered[:, j] = sp_signal.filtfilt(b, a, arr[:, j])

    if was_1d:
        return filtered[:, 0]
    return filtered
