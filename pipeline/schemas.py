"""
Dataclass schemas for all pipeline stages (SDA-1).

Each stage in the sacred pipeline produces one of these records.
The order is inviolable: RawECGRecord → PreprocessedECGRecord →
QualityReport → FiducialTable → FeatureObject → VisionVerificationResult.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
import numpy as np


# ---------------------------------------------------------------------------
# Node 1.1 — Ingestion
# ---------------------------------------------------------------------------

@dataclass
class RawECGRecord:
    """Output of the ingestion stage. 12-lead signal at original sampling rate."""
    ecg_id: str
    signal: np.ndarray          # shape (12, N) — float32, µV (already calibrated)
    fs: float                   # sampling frequency Hz
    lead_names: list[str]       # 12 standard lead names in signal row order
    duration_sec: float         # total recording duration
    source_format: str          # "wfdb" | "scp" | "edf" | "csv"
    patient_sex: Optional[str]  # "M" | "F" | None (PHI-stripped)
    patient_age: Optional[int]  # years | None (PHI-stripped)
    device_id: Optional[str]    # equipment identifier (non-PHI)


# ---------------------------------------------------------------------------
# Node 1.2 — Preprocessing
# ---------------------------------------------------------------------------

@dataclass
class PreprocessedECGRecord:
    """Output of the preprocessing stage."""
    ecg_id: str
    preprocessed_signal: np.ndarray   # shape (12, N) — bandpass filtered, 500 Hz, float32
    morphology_signal: np.ndarray     # shape (12, N) — raw amplitude at 500 Hz (no filter), float32
    fs: float                         # always 500.0 after resampling
    lead_names: list[str]
    duration_sec: float
    # Safe analysis window (excludes 3s edge transients from filtfilt)
    safe_window_start_sample: int
    safe_window_end_sample: int
    # Flags set during preprocessing
    wander_detected: bool             # FFT band-power fraction 0.05–0.5 Hz > 0.15
    wander_corrected: bool
    patient_sex: Optional[str]
    patient_age: Optional[int]


# ---------------------------------------------------------------------------
# Node 1.3 — Quality Assessment
# ---------------------------------------------------------------------------

QUALITY_LEVELS = ("GOOD", "ACCEPTABLE", "POOR", "UNUSABLE")

@dataclass
class LeadQuality:
    lead: str
    quality: str                    # one of QUALITY_LEVELS
    snr_db: Optional[float]
    flat_line: bool
    clipping: bool
    high_frequency_noise: bool


@dataclass
class QualityReport:
    """Output of the quality assessment stage."""
    ecg_id: str
    lead_quality: dict[str, LeadQuality]   # keyed by lead name
    overall_quality: str                   # worst lead quality present
    usable_leads: list[str]                # GOOD or ACCEPTABLE
    poor_leads: list[str]                  # POOR
    unusable_leads: list[str]              # UNUSABLE
    # Bootstrap R-peak positions (internal to quality — NOT for clinical use)
    _bootstrap_r_peaks: dict[str, np.ndarray]  # lead → sample indices; private
    # Required-lead coverage for each analysis domain
    ischemia_coverage: float               # fraction of 11 territory leads that are usable
    rhythm_coverage: float                 # fraction of rhythm leads (II, V1, aVR) usable


# ---------------------------------------------------------------------------
# Node 1.4 — Fiducial Detection
# ---------------------------------------------------------------------------

@dataclass
class FiducialTable:
    """
    Output of the fiducial detection stage.

    fpt: dict mapping lead_name → np.ndarray of shape (n_beats, 13).
    Columns (0-indexed):
      0  Pon    1  Ppeak   2  Poff
      3  QRSon  4  Q       5  R       6  S      7  QRSoff
      8  L(J)   9  Ton    10  Tpeak  11  Toff   12  beat_class
    Sample index -1 = not detected.
    beat_class: 0=normal, 1=PVC, 2=PAC, -1=unknown
    """
    ecg_id: str
    fpt: dict[str, np.ndarray]      # lead → (n_beats, 13) int32 array
    n_beats: int                    # beats in the safe analysis window
    total_recording_beats: int      # beats across full recording (includes edge beats)
    fs: float
    safe_window_start_sample: int
    safe_window_end_sample: int
    condition_corrections_applied: bool   # True if AFib/irregular corrections applied
    # Per-fiducial-type confidence scores (0.0–1.0)
    fiducial_confidence: dict[str, float] = field(default_factory=dict)  # e.g. {"pon": 0.85, "r": 0.99, ...}


# ---------------------------------------------------------------------------
# Node 1.5 — Feature Extraction
# ---------------------------------------------------------------------------

@dataclass
class BeatSummary:
    """
    Compressed beat-level summary (~600 tokens). Output of Node 2.5 logic,
    populated during feature extraction for use by agents.
    """
    n_beats: int
    beat_class_counts: dict[str, int]   # {"normal": N, "pvc": N, "pac": N, "unknown": N}
    dominant_rhythm: str
    rhythm_regular: bool
    rr_intervals_ms: list[float]        # all RR intervals
    rr_mean_ms: float
    rr_cv: float                        # coefficient of variation
    beat_pattern: Optional[str]         # "BIGEMINY_PVC" | "BIGEMINY_PAC" | "TRIGEMINY" | None
    dropped_beat_context: Optional[str] # description of pause/dropped beat if detected
    # Per-beat detail injected for specific conditions (NEEDS_PER_BEAT_DETAIL)
    per_beat_detail: Optional[dict]     # None unless a condition requiring detail is active


@dataclass
class FeatureObject:
    """
    Output of feature extraction (Node 1.5). All computed ECG features.
    Passed to SDA-2 agents via BeatSummary + diagnostic findings.
    """
    ecg_id: str

    # --- Rate & Rhythm ---
    heart_rate_ventricular_bpm: Optional[float]
    heart_rate_atrial_bpm: Optional[float]
    av_ratio: Optional[float]
    rhythm_regular: bool
    dominant_rhythm: str               # "sinus" | "afib" | "aflutter" | "junctional" | "paced" | "unknown"
    rhythm_notes: list[str]

    # --- Intervals (ms) ---
    pr_interval_ms: Optional[float]
    qrs_duration_global_ms: Optional[float]
    qt_interval_ms: Optional[float]
    qtc_bazett_ms: Optional[float]
    qtc_fridericia_ms: Optional[float]
    qtc_framingham_ms: Optional[float]
    qtc_hodges_ms: Optional[float]

    # --- Axis (degrees) ---
    p_axis_deg: Optional[float]
    qrs_axis_deg: Optional[float]
    t_axis_deg: Optional[float]

    # --- ST measurements (per lead, mV) ---
    st_elevation_mv: dict[str, Optional[float]]    # lead → value
    st_depression_mv: dict[str, Optional[float]]
    st_morphology: dict[str, Optional[str]]        # lead → "upsloping"|"downsloping"|"horizontal"|"saddle"
    j_point_mv: dict[str, Optional[float]]

    # --- T wave (per lead) ---
    t_amplitude_mv: dict[str, Optional[float]]
    t_morphology: dict[str, Optional[str]]         # "upright"|"inverted"|"biphasic"|"flat"|"hyperacute"
    t_qrs_ratio: dict[str, Optional[float]]
    symmetric_t_inversion: dict[str, bool]

    # --- P wave ---
    p_duration_ms: Optional[float]
    p_amplitude_mv: Optional[float]
    p_terminal_force_v1_mv_s: Optional[float]     # mV·s; threshold > 0.04
    p_wave_present: bool
    p_morphology_notes: list[str]

    # --- QRS morphology ---
    r_amplitude_mv: dict[str, Optional[float]]
    s_amplitude_mv: dict[str, Optional[float]]
    q_duration_ms: dict[str, Optional[float]]      # Q nadir to QRS onset (corrected)
    q_amplitude_mv: dict[str, Optional[float]]
    qrs_fragmented: dict[str, bool]                # fQRS per lead
    r_progression: str                             # "normal"|"poor"|"reverse"
    intrinsicoid_deflection_ms: dict[str, Optional[float]]

    # --- LVH / RVH / Low voltage ---
    lvh_sokolow_lyon_mv: Optional[float]
    lvh_cornell_mv: Optional[float]
    lvh_cornell_product_mv_ms: Optional[float]
    lvh_romhilt_estes_score: Optional[int]
    lvh_lewis_index_mv: Optional[float]
    lvh_criteria_met: list[str]
    rvh_criteria_met: list[str]
    low_voltage_limb: bool
    low_voltage_precordial: bool

    # --- Special patterns (bool flags) ---
    lbbb: bool
    rbbb: bool
    lafb: bool
    lpfb: bool
    wpw_pattern: bool
    brugada_type1_pattern: bool
    brugada_type2or3_pattern: bool
    de_winter_pattern: bool
    early_repolarization_pattern: bool
    pericarditis_pattern: bool
    hyperacute_t_pattern: bool
    electrical_alternans: bool
    epsilon_wave_suspected: bool
    u_wave_prominent: bool
    osborn_wave: bool

    # --- QT dispersion ---
    qt_per_lead_ms: dict[str, Optional[float]]       # QT interval per lead
    qt_dispersion_ms: Optional[float]                 # max(QT) - min(QT) across leads

    # --- Tpeak-to-Tend ---
    tpe_interval_ms: Optional[float]                  # Tpeak to Toff interval (SCD risk)

    # --- Pathological Q waves ---
    pathological_q_wave: dict[str, bool]              # per lead: duration >40ms OR depth >25% R

    # --- R/S ratio ---
    r_s_ratio: dict[str, Optional[float]]             # R/S ratio per lead

    # --- R-wave progression index ---
    r_progression_index: Optional[float]              # V1-V6 transition zone index (numeric)

    # --- PR depression ---
    pr_depression_mv: dict[str, Optional[float]]      # PR segment depression per lead

    # --- Measurement normal/abnormal flags ---
    measurement_flags: dict[str, str]                  # measurement → "normal"|"borderline"|"abnormal"

    # --- HRV (simple) ---
    sdnn_ms: Optional[float]
    rmssd_ms: Optional[float]

    # --- Signal quality caps (for confidence scoring) ---
    lead_quality_cap: dict[str, float]   # lead → 0.0–1.0

    # --- Beat summary ---
    beat_summary: BeatSummary

    # --- Morphology analysis (from pipeline/morphology.py) ---
    qrs_pattern: dict[str, str] = field(default_factory=dict)         # lead → "QS"|"rS"|"RSR'"|"qRs"|etc
    st_curvature: dict[str, str] = field(default_factory=dict)        # lead → "concave"|"convex"|"linear"|"coved"
    t_symmetry_index: dict[str, Optional[float]] = field(default_factory=dict)  # lead → 0.0-1.0
    t_detailed_morphology: dict[str, str] = field(default_factory=dict)  # lead → detailed T-wave type
    concordance_analysis: dict[str, str] = field(default_factory=dict)   # lead → "concordant"|"discordant"
    av_relationship: str = "unknown"  # "1:1"|"dissociated"|"wenckebach"|"2:1"|"variable"


# ---------------------------------------------------------------------------
# Node 1.6 — Vision Pipeline
# ---------------------------------------------------------------------------

@dataclass
class SignalVisionConflict:
    lead: str
    finding_type: str       # e.g. "st_elevation"
    signal_value: str       # e.g. "+0.28 mV"
    vision_value: str       # e.g. "no ST elevation visible"
    conflict_type: str      # "SIGNAL_ONLY" | "VISION_ONLY" | "BOTH_OPPOSITE"


@dataclass
class VisionVerificationResult:
    """Advisory output of the VL2 vision pipeline. Never overwrites signal features."""
    available: bool
    unavailability_reason: Optional[str]   # None | "VL2_TIMEOUT" | "VL2_NOT_APPLICABLE" | "VL2_ERROR"

    # VL2-reported findings (all advisory)
    st_elevation_leads: list[str]
    st_depression_leads: list[str]
    t_wave_inversion_leads: list[str]
    lbbb_pattern: bool
    rhythm_regular: Optional[bool]
    qrs_wide: Optional[bool]

    # Conflicts between signal pipeline and VL2
    signal_vision_conflicts: list[SignalVisionConflict]

    # Raw VL2 response (for audit trail)
    raw_vl2_response: Optional[str]
    vl2_latency_sec: Optional[float]
