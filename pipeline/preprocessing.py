"""
Node 1.2 — Signal Preprocessing.

Resamples to 500 Hz, applies bandpass filter (0.5–40 Hz) to produce
preprocessed_signal, and captures morphology_signal (raw amplitude at 500 Hz,
no filter). Baseline wander is detected via FFT band-power and corrected
with a median filter if present. The safe analysis window (3s margins)
is computed and stored to avoid filtfilt edge transients in downstream analysis.
"""

from __future__ import annotations
import numpy as np
from scipy.signal import butter, filtfilt, resample_poly
from math import gcd
from pipeline.schemas import RawECGRecord, PreprocessedECGRecord

TARGET_FS = 500.0
BANDPASS_LOW_HZ = 0.5
BANDPASS_HIGH_HZ = 40.0
BANDPASS_ORDER = 4

# Wander detection: if low-frequency band-power fraction > threshold, wander is present
WANDER_BAND_LOW_HZ = 0.05
WANDER_BAND_HIGH_HZ = 0.5
WANDER_POWER_THRESHOLD = 0.15

# Safe window: exclude 3 seconds from each end to eliminate filtfilt edge transients
EDGE_MARGIN_SEC = 3.0


def preprocess(record: RawECGRecord) -> PreprocessedECGRecord:
    """
    Preprocess a RawECGRecord.

    Steps:
      1. Resample to TARGET_FS (500 Hz) if needed
      2. Capture morphology_signal (resampled but unfiltered)
      3. Detect baseline wander
      4. Apply baseline wander correction if detected
      5. Apply bandpass filter (0.5–40 Hz) to produce preprocessed_signal
      6. Compute safe analysis window
    """
    signal = record.signal.astype(np.float32)
    fs_in = record.fs

    # Step 1: Resample to 500 Hz
    if abs(fs_in - TARGET_FS) > 0.5:
        signal = _resample(signal, fs_in, TARGET_FS)

    # Step 2: Capture morphology_signal (raw amplitude, no filter)
    morphology_signal = signal.copy()

    # Step 3: Detect wander
    wander_detected = _detect_wander(signal, TARGET_FS)

    # Step 4: Wander correction (median filter subtraction)
    wander_corrected = False
    if wander_detected:
        signal = _correct_wander(signal, TARGET_FS)
        wander_corrected = True

    # Step 5: Bandpass filter on the full signal length (filtfilt requires full signal)
    preprocessed_signal = _bandpass_filter(signal, TARGET_FS)

    # Step 6: Safe window
    n_samples = preprocessed_signal.shape[1]
    edge_samples = int(EDGE_MARGIN_SEC * TARGET_FS)
    safe_start = edge_samples
    safe_end = n_samples - edge_samples
    if safe_end <= safe_start:
        # Recording shorter than 6s — use full signal (no safe margin possible)
        safe_start = 0
        safe_end = n_samples

    return PreprocessedECGRecord(
        ecg_id=record.ecg_id,
        preprocessed_signal=preprocessed_signal,
        morphology_signal=morphology_signal,
        fs=TARGET_FS,
        lead_names=record.lead_names,
        duration_sec=n_samples / TARGET_FS,
        safe_window_start_sample=safe_start,
        safe_window_end_sample=safe_end,
        wander_detected=wander_detected,
        wander_corrected=wander_corrected,
        patient_sex=record.patient_sex,
        patient_age=record.patient_age,
    )


def _resample(signal: np.ndarray, fs_in: float, fs_out: float) -> np.ndarray:
    """Polyphase resampling to avoid aliasing. Uses integer up/down factors."""
    fs_in_int = int(round(fs_in))
    fs_out_int = int(round(fs_out))
    g = gcd(fs_in_int, fs_out_int)
    up = fs_out_int // g
    down = fs_in_int // g
    resampled = np.stack([
        resample_poly(signal[i], up, down).astype(np.float32)
        for i in range(signal.shape[0])
    ])
    return resampled


def _detect_wander(signal: np.ndarray, fs: float) -> bool:
    """
    Detect baseline wander using FFT band-power fraction.
    Returns True if any lead has low-frequency power fraction > WANDER_POWER_THRESHOLD.
    """
    n = signal.shape[1]
    freqs = np.fft.rfftfreq(n, d=1.0 / fs)
    for lead_sig in signal:
        power = np.abs(np.fft.rfft(lead_sig)) ** 2
        total_power = power.sum()
        if total_power == 0:
            continue
        wander_mask = (freqs >= WANDER_BAND_LOW_HZ) & (freqs <= WANDER_BAND_HIGH_HZ)
        wander_fraction = power[wander_mask].sum() / total_power
        if wander_fraction > WANDER_POWER_THRESHOLD:
            return True
    return False


def _correct_wander(signal: np.ndarray, fs: float) -> np.ndarray:
    """
    Baseline wander correction via median filter subtraction.
    Window: 600 ms (one beat at ~100 bpm) rounded up to odd number of samples.
    """
    from scipy.ndimage import median_filter
    window_samples = int(0.6 * fs)
    if window_samples % 2 == 0:
        window_samples += 1
    corrected = np.stack([
        (lead_sig - median_filter(lead_sig, size=window_samples)).astype(np.float32)
        for lead_sig in signal
    ])
    return corrected


def _bandpass_filter(signal: np.ndarray, fs: float) -> np.ndarray:
    """Apply 4th-order Butterworth bandpass filter (0.5–40 Hz) with zero-phase filtfilt."""
    nyq = fs / 2.0
    low = BANDPASS_LOW_HZ / nyq
    high = BANDPASS_HIGH_HZ / nyq
    b, a = butter(BANDPASS_ORDER, [low, high], btype="band")
    filtered = np.stack([
        filtfilt(b, a, lead_sig).astype(np.float32)
        for lead_sig in signal
    ])
    return filtered
