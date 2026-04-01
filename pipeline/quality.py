"""
Node 1.3 — Quality Assessment.

Assesses signal quality per lead using SNR estimation, flat-line detection,
clipping detection, and high-frequency noise scoring. Uses an internal bootstrap
R-peak detector (NOT the clinical FiducialTable from Node 1.4). The bootstrap
R-peaks are stored as a private field (_bootstrap_r_peaks) and must not be
used for clinical feature extraction.
"""

from __future__ import annotations
import numpy as np
from scipy.signal import find_peaks, butter, filtfilt
from pipeline.schemas import PreprocessedECGRecord, QualityReport, LeadQuality, QUALITY_LEVELS

# Minimum leads required for each analysis domain
REQUIRED_LEADS = {
    "rhythm": ["II", "V1", "aVR"],
    "ischemia": ["I", "II", "III", "aVL", "aVF", "V1", "V2", "V3", "V4", "V5", "V6"],
    "axis": ["I", "aVF"],
    "lvh": ["I", "aVL", "V1", "V5", "V6"],
}

# Thresholds
SNR_GOOD_DB = 20.0
SNR_ACCEPTABLE_DB = 12.0
SNR_POOR_DB = 6.0
FLATLINE_AMPLITUDE_UV = 10.0      # lead considered flat if amplitude range < 10 µV
CLIPPING_PERCENTILE = 99.5        # if ≥ 0.5% of samples are at signal max/min → clipping
HF_NOISE_THRESHOLD_RATIO = 0.35   # HF power fraction above 35% → high-frequency noise


def assess_quality(record: PreprocessedECGRecord) -> QualityReport:
    """
    Assess signal quality for each lead in the safe analysis window.

    Returns QualityReport with per-lead quality levels and coverage metrics.
    """
    safe = record.preprocessed_signal[
        :,
        record.safe_window_start_sample:record.safe_window_end_sample,
    ]
    fs = record.fs

    lead_quality_map: dict[str, LeadQuality] = {}
    bootstrap_r_peaks: dict[str, np.ndarray] = {}

    for i, lead in enumerate(record.lead_names):
        sig = safe[i]
        lq, r_peaks = _assess_lead(sig, lead, fs)
        lead_quality_map[lead] = lq
        bootstrap_r_peaks[lead] = r_peaks

    usable = [l for l, q in lead_quality_map.items() if q.quality in ("GOOD", "ACCEPTABLE")]
    poor = [l for l, q in lead_quality_map.items() if q.quality == "POOR"]
    unusable = [l for l, q in lead_quality_map.items() if q.quality == "UNUSABLE"]

    # Worst quality present
    quality_rank = {q: i for i, q in enumerate(QUALITY_LEVELS)}
    overall = max(lead_quality_map.values(), key=lambda q: quality_rank[q.quality]).quality

    # Coverage fractions
    ischemia_coverage = _coverage_fraction(usable, REQUIRED_LEADS["ischemia"])
    rhythm_coverage = _coverage_fraction(usable, REQUIRED_LEADS["rhythm"])

    return QualityReport(
        ecg_id=record.ecg_id,
        lead_quality=lead_quality_map,
        overall_quality=overall,
        usable_leads=usable,
        poor_leads=poor,
        unusable_leads=unusable,
        _bootstrap_r_peaks=bootstrap_r_peaks,
        ischemia_coverage=ischemia_coverage,
        rhythm_coverage=rhythm_coverage,
    )


def _assess_lead(sig: np.ndarray, lead: str, fs: float) -> tuple[LeadQuality, np.ndarray]:
    """Assess a single lead signal. Returns (LeadQuality, bootstrap_r_peaks array)."""
    flat = _detect_flatline(sig)
    clipping = _detect_clipping(sig)
    hf_noise = _detect_hf_noise(sig, fs)
    snr_db = _estimate_snr(sig, fs) if not flat else None

    # Bootstrap R-peak detection (internal only — NOT clinical FPT)
    r_peaks = _bootstrap_r_peaks(sig, fs) if not flat else np.array([], dtype=np.int32)

    quality = _classify_quality(flat, clipping, hf_noise, snr_db, r_peaks, fs)

    return LeadQuality(
        lead=lead,
        quality=quality,
        snr_db=snr_db,
        flat_line=flat,
        clipping=clipping,
        high_frequency_noise=hf_noise,
    ), r_peaks


def _classify_quality(
    flat: bool,
    clipping: bool,
    hf_noise: bool,
    snr_db: Optional[float],
    r_peaks: np.ndarray,
    fs: float,
) -> str:
    if flat or len(r_peaks) == 0:
        return "UNUSABLE"
    if clipping:
        return "POOR"
    # HF noise alone → POOR; SNR confirms
    if hf_noise:
        return "POOR"
    if snr_db is None:
        return "POOR"
    if snr_db >= SNR_GOOD_DB:
        return "GOOD"
    if snr_db >= SNR_ACCEPTABLE_DB:
        return "ACCEPTABLE"
    if snr_db >= SNR_POOR_DB:
        return "POOR"
    return "UNUSABLE"


def _detect_flatline(sig: np.ndarray) -> bool:
    return (sig.max() - sig.min()) < FLATLINE_AMPLITUDE_UV


def _detect_clipping(sig: np.ndarray) -> bool:
    """Clipping: ≥ 0.5% of samples at the maximum or minimum amplitude."""
    n = len(sig)
    sig_max = sig.max()
    sig_min = sig.min()
    at_max = np.sum(sig >= sig_max * 0.999) / n
    at_min = np.sum(sig <= sig_min * 1.001) / n
    clip_fraction = (1 - CLIPPING_PERCENTILE / 100)
    return at_max > clip_fraction or at_min > clip_fraction


def _detect_hf_noise(sig: np.ndarray, fs: float) -> bool:
    """
    High-frequency noise: power in 25–45 Hz band as fraction of total power.
    ECG signal above 25 Hz is noise; threshold 0.35 = 35% HF power.
    """
    n = len(sig)
    freqs = np.fft.rfftfreq(n, d=1.0 / fs)
    power = np.abs(np.fft.rfft(sig)) ** 2
    total = power.sum()
    if total == 0:
        return False
    hf_mask = freqs >= 25.0
    hf_fraction = power[hf_mask].sum() / total
    return hf_fraction > HF_NOISE_THRESHOLD_RATIO


def _estimate_snr(sig: np.ndarray, fs: float) -> float:
    """
    SNR estimate: RMS of signal band (0.5–25 Hz) / RMS of noise band (25–45 Hz).
    Returns value in dB.
    """
    nyq = fs / 2.0
    b_sig, a_sig = butter(4, [0.5 / nyq, 25.0 / nyq], btype="band")
    b_noise, a_noise = butter(4, [25.0 / nyq, min(45.0, nyq * 0.99) / nyq], btype="band")
    sig_band = filtfilt(b_sig, a_sig, sig)
    noise_band = filtfilt(b_noise, a_noise, sig)
    rms_sig = np.sqrt(np.mean(sig_band ** 2))
    rms_noise = np.sqrt(np.mean(noise_band ** 2))
    if rms_noise == 0:
        return 60.0
    return float(20 * np.log10(rms_sig / rms_noise))


def _bootstrap_r_peaks(sig: np.ndarray, fs: float) -> np.ndarray:
    """
    Simple bootstrap R-peak detector for quality assessment only.
    Uses threshold-based peak detection after light smoothing.
    NOT the clinical fiducial detector — do not use for feature extraction.
    """
    # Light lowpass to reduce noise before peak detection
    nyq = fs / 2.0
    b, a = butter(4, 20.0 / nyq, btype="low")
    smoothed = filtfilt(b, a, sig)
    smoothed_abs = np.abs(smoothed)

    # Minimum distance: 300 ms (200 bpm maximum)
    min_dist = int(0.3 * fs)
    threshold = 0.5 * np.percentile(smoothed_abs, 95)

    peaks, _ = find_peaks(smoothed_abs, height=threshold, distance=min_dist)
    return peaks.astype(np.int32)


def _coverage_fraction(usable_leads: list[str], required: list[str]) -> float:
    if not required:
        return 1.0
    covered = sum(1 for l in required if l in usable_leads)
    return covered / len(required)


# Fix type hint import
from typing import Optional
