"""
Stationary Wavelet Transform (SWT) denoising for ECG signals.

Decomposes the 500Hz signal into frequency bands using sym8 wavelet:
  Level 1 detail: 125-250 Hz  → threshold (noise)
  Level 2 detail: 62.5-125 Hz → threshold (noise)
  Level 3 detail: 31-62.5 Hz  → threshold (noise)
  Level 4 detail: 15.6-31 Hz  → KEEP (QRS energy)
  Approximation:  0-15.6 Hz   → KEEP (P/T waves, baseline)

Noise estimation: MAD (median absolute deviation / 0.6745) — robust to QRS spikes.
Thresholding: Donoho-Johnstone universal soft threshold (σ × √(2 ln N)).
SWT is shift-invariant — no edge artifacts at beat boundaries.
Preserves beat-to-beat variability (PVCs, etc.) because it operates on
frequency content, not beat templates.
"""

from __future__ import annotations
import numpy as np
import pywt


WAVELET = "sym8"
SWT_LEVELS = 4         # 4 levels of decomposition
THRESHOLD_LEVELS = 3   # only threshold levels 1-3 (>31 Hz), keep level 4


def _mad_sigma(coeffs: np.ndarray) -> float:
    """Estimate noise standard deviation using MAD (robust to outliers)."""
    return float(np.median(np.abs(coeffs))) / 0.6745


def _soft_threshold(coeffs: np.ndarray, thresh: float) -> np.ndarray:
    """Donoho-Johnstone soft thresholding: shrink toward zero."""
    return np.sign(coeffs) * np.maximum(np.abs(coeffs) - thresh, 0)


def denoise_lead(signal_1d: np.ndarray, fs: float = 500.0) -> np.ndarray:
    """
    Denoise a single-lead ECG signal using SWT.

    Args:
        signal_1d: 1D array of ECG samples (µV or mV, any unit)
        fs: sample rate (default 500 Hz)

    Returns:
        Denoised signal, same length and unit as input.
    """
    n = len(signal_1d)

    # SWT requires signal length to be a multiple of 2^levels
    pad_len = 0
    required = 2 ** SWT_LEVELS
    if n % required != 0:
        pad_len = required - (n % required)

    sig = np.pad(signal_1d.astype(np.float64), (0, pad_len), mode='symmetric')

    # Decompose
    coeffs = pywt.swt(sig, WAVELET, level=SWT_LEVELS)
    # coeffs is list of (cA, cD) tuples, from coarsest to finest
    # coeffs[0] = (cA4, cD4), coeffs[1] = (cA3, cD3), ..., coeffs[3] = (cA1, cD1)
    # Actually pywt.swt returns from level=SWT_LEVELS down to level=1

    # Threshold detail coefficients for levels 1-3 (finest = most noise)
    # pywt.swt output order: index 0 = level SWT_LEVELS (coarsest), last = level 1 (finest)
    for level_idx in range(SWT_LEVELS):
        actual_level = SWT_LEVELS - level_idx  # 4, 3, 2, 1
        cA, cD = coeffs[level_idx]

        if actual_level <= THRESHOLD_LEVELS:
            # Levels 1-3: threshold the detail coefficients
            sigma = _mad_sigma(cD)
            n_eff = len(cD)
            thresh = sigma * np.sqrt(2 * np.log(n_eff))
            cD_clean = _soft_threshold(cD, thresh)
            coeffs[level_idx] = (cA, cD_clean)
        # Level 4: keep untouched (QRS energy)

    # Reconstruct
    denoised = pywt.iswt(coeffs, WAVELET)

    # Remove padding
    denoised = denoised[:n]

    return denoised.astype(signal_1d.dtype)


def denoise_ecg(signal: np.ndarray, fs: float = 500.0) -> np.ndarray:
    """
    Denoise a multi-lead ECG signal using SWT.

    Args:
        signal: (n_leads, n_samples) array
        fs: sample rate

    Returns:
        Denoised signal, same shape as input.
    """
    denoised = np.zeros_like(signal)
    for i in range(signal.shape[0]):
        denoised[i] = denoise_lead(signal[i], fs)
    return denoised
