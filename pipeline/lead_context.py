"""
Lead context for shape classification.

Provides per-lead anatomical context, normal expected morphology,
territory mapping, and axis-aware interpretation. This is the
foundation for lead-aware shape classification.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional


# ── Lead axes (degrees) ───────────────────────────────────────────────────

LEAD_AXIS = {
    "I": 0, "II": 60, "III": 120,
    "aVR": -150, "aVL": -30, "aVF": 90,
    # Precordial leads don't have a single frontal axis
    "V1": None, "V2": None, "V3": None,
    "V4": None, "V5": None, "V6": None,
}

# ── Territory mapping ─────────────────────────────────────────────────────

LEAD_TERRITORY = {
    "V1": "septal",    "V2": "septal",
    "V3": "anterior",  "V4": "anterior",
    "I": "lateral",    "aVL": "lateral",  "V5": "lateral",  "V6": "lateral",
    "II": "inferior",  "III": "inferior", "aVF": "inferior",
    "aVR": "cavity",   # aVR faces the heart cavity — everything inverted
}

TERRITORY_LEADS = {
    "septal":   ["V1", "V2"],
    "anterior": ["V3", "V4"],
    "lateral":  ["I", "aVL", "V5", "V6"],
    "inferior": ["II", "III", "aVF"],
    "cavity":   ["aVR"],
}

# Reciprocal territory pairs
RECIPROCAL_TERRITORIES = {
    "anterior": "inferior",
    "inferior": "anterior",
    "lateral":  "septal",
    "septal":   "lateral",
}

# ── Normal expected morphology per lead ───────────────────────────────────

NORMAL_MORPHOLOGY = {
    # For each lead: expected P polarity, QRS pattern, T polarity
    # These are for NORMAL axis (~+60°)
    "I":   {"p": "upright", "qrs": "qRs_positive", "t": "upright", "st": "isoelectric"},
    "II":  {"p": "upright", "qrs": "qRs_positive", "t": "upright", "st": "isoelectric"},
    "III": {"p": "variable", "qrs": "variable", "t": "variable", "st": "isoelectric"},
    "aVR": {"p": "inverted", "qrs": "negative", "t": "inverted", "st": "isoelectric"},
    "aVL": {"p": "variable", "qrs": "variable", "t": "variable", "st": "isoelectric"},
    "aVF": {"p": "upright", "qrs": "qRs_positive", "t": "upright", "st": "isoelectric"},
    "V1":  {"p": "biphasic", "qrs": "rS", "t": "variable_may_invert", "st": "isoelectric"},
    "V2":  {"p": "biphasic", "qrs": "RS", "t": "upright", "st": "isoelectric"},
    "V3":  {"p": "upright", "qrs": "RS_transition", "t": "upright", "st": "isoelectric"},
    "V4":  {"p": "upright", "qrs": "Rs", "t": "upright", "st": "isoelectric"},
    "V5":  {"p": "upright", "qrs": "qRs", "t": "upright", "st": "isoelectric"},
    "V6":  {"p": "upright", "qrs": "qRs", "t": "upright", "st": "isoelectric"},
}


@dataclass
class LeadContext:
    """Full context for interpreting a shape in a specific lead."""
    lead_name: str
    territory: str                           # "septal" | "anterior" | "lateral" | "inferior" | "cavity"
    lead_axis_deg: Optional[int]             # frontal plane axis angle (None for precordial)

    # From FeatureObject (passed in)
    qrs_axis_deg: Optional[float] = None     # patient's QRS axis
    j_point_mv: Optional[float] = None       # J-point value relative to baseline (mV)
    st_elevation_mv: Optional[float] = None  # measured ST elevation
    st_depression_mv: Optional[float] = None # measured ST depression
    s_wave_endpoint_mv: Optional[float] = None  # where S-wave ends (mV relative to baseline)
    isoelectric_baseline_uv: float = 0.0     # PR segment baseline (µV)

    # QRS context for concordance assessment
    terminal_qrs_polarity: Optional[str] = None  # "positive" | "negative"
    lbbb: bool = False
    rbbb: bool = False

    # Horizontal rotation context
    r_progression: str = "normal"            # "normal" | "poor" | "reverse" | "early" | "indeterminate"
    transition_zone: Optional[float] = None  # R/S crossover lead index (3.5 = between V3-V4, normal)
    horizontal_rotation: str = "normal"      # "normal" | "clockwise" | "counterclockwise"

    # Normal expected values for this lead
    normal_t_polarity: str = "upright"       # what T-wave should be in this lead normally
    normal_qrs_pattern: str = "positive"     # what QRS should look like
    is_avr: bool = False                     # special handling for aVR

    # Derived flags
    is_reciprocal_lead: bool = False         # True if this lead shows reciprocal changes
    is_transition_shifted: bool = False      # True if this lead is affected by abnormal rotation


def build_lead_context(
    lead: str,
    features=None,  # FeatureObject
    beat_idx: int = 0,
    signal=None,     # raw lead signal (µV)
    fpt_beat=None,   # single beat FPT row
    fs: float = 500.0,
) -> LeadContext:
    """
    Build full lead context from available data.

    Args:
        lead: lead name
        features: FeatureObject (for axis, ST measurements, BBB flags)
        beat_idx: which beat
        signal: raw signal for this lead (µV)
        fpt_beat: FPT row for this beat
        fs: sample rate
    """
    territory = LEAD_TERRITORY.get(lead, "unknown")
    axis_deg = LEAD_AXIS.get(lead)
    normal = NORMAL_MORPHOLOGY.get(lead, {})

    ctx = LeadContext(
        lead_name=lead,
        territory=territory,
        lead_axis_deg=axis_deg,
        normal_t_polarity=normal.get("t", "upright"),
        normal_qrs_pattern=normal.get("qrs", "positive"),
        is_avr=(lead == "aVR"),
    )

    if features is not None:
        ctx.qrs_axis_deg = features.qrs_axis_deg
        ctx.st_elevation_mv = features.st_elevation_mv.get(lead)
        ctx.st_depression_mv = features.st_depression_mv.get(lead)
        ctx.lbbb = features.lbbb
        ctx.rbbb = features.rbbb

        # S-wave endpoint
        s_amp = features.s_amplitude_mv.get(lead)
        r_amp = features.r_amplitude_mv.get(lead)
        if s_amp is not None and r_amp is not None:
            ctx.s_wave_endpoint_mv = -s_amp if s_amp > 0 else 0.0

        # Horizontal rotation from R-wave progression
        ctx.r_progression = features.r_progression
        ctx.transition_zone = features.r_progression_index
        ctx.horizontal_rotation = _classify_horizontal_rotation(
            features.r_progression, features.r_progression_index
        )

        # Adjust precordial expectations based on rotation
        if lead in ("V1", "V2", "V3", "V4", "V5", "V6"):
            _adjust_for_rotation(ctx)

    # J-point from signal if available
    if signal is not None and fpt_beat is not None:
        qrs_off = int(fpt_beat[7])  # COL_QRSOFF
        qrs_on = int(fpt_beat[3])   # COL_QRSON
        if qrs_off > 0 and qrs_on > 0 and qrs_off < len(signal):
            # Isoelectric baseline from PR segment
            iso_start = max(0, qrs_on - int(0.02 * fs))
            iso_seg = signal[iso_start:qrs_on]
            if len(iso_seg) > 3:
                baseline = float(iso_seg.mean())
            else:
                baseline = float(signal[qrs_on]) if qrs_on < len(signal) else 0.0
            ctx.isoelectric_baseline_uv = baseline
            j_val = float(signal[qrs_off]) - baseline
            ctx.j_point_mv = j_val / 1000.0

            # Terminal QRS polarity (last 40ms)
            terminal_start = max(qrs_on, qrs_off - int(0.04 * fs))
            terminal_seg = signal[terminal_start:qrs_off]
            if len(terminal_seg) > 0:
                terminal_mean = float(terminal_seg.mean()) - baseline
                ctx.terminal_qrs_polarity = "positive" if terminal_mean > 0 else "negative"

    # Axis-aware: adjust normal expectations based on actual QRS axis
    if ctx.qrs_axis_deg is not None:
        _adjust_for_axis(ctx)

    return ctx


def _classify_horizontal_rotation(r_progression: str, transition_zone: Optional[float]) -> str:
    """
    Classify horizontal heart rotation from R-wave progression.

    Normal: transition at V3-V4 (index 3.0-4.0)
    Clockwise: transition delayed to V5-V6 (index > 4.5) — COPD, obesity
    Counterclockwise: transition early at V1-V2 (index < 2.5) — posterior MI, tall/thin
    """
    if transition_zone is not None:
        if transition_zone < 2.5:
            return "counterclockwise"
        elif transition_zone > 4.5:
            return "clockwise"
        else:
            return "normal"

    # Fallback to string progression
    if r_progression == "poor":
        return "clockwise"  # most common cause of poor R progression
    elif r_progression == "reverse":
        return "clockwise"
    elif r_progression == "early":
        return "counterclockwise"
    return "normal"


def _adjust_for_rotation(ctx: LeadContext):
    """
    Adjust precordial lead expectations based on horizontal rotation.

    Clockwise rotation (COPD/obesity):
      - V1-V3 show persistent rS (poor R) — normal for this patient
      - V4 may still show rS instead of R>S transition
      - V5-V6 transition zone shifts here
      - Small R in V1-V3 is NOT anterior MI, it's rotation

    Counterclockwise rotation (tall/thin, posterior MI):
      - V1-V2 show tall R early — may mimic RVH or posterior MI
      - Transition happens very early
      - Tall R in V1 needs context: is it rotation or pathology?
    """
    lead = ctx.lead_name
    tz = ctx.transition_zone
    rotation = ctx.horizontal_rotation

    if rotation == "clockwise":
        # V1-V3: rS pattern is EXPECTED (not pathological poor R progression)
        if lead in ("V1", "V2", "V3"):
            ctx.normal_qrs_pattern = "rS_expected_rotation"
            ctx.is_transition_shifted = True
        # V4: may still show rS instead of transition
        if lead == "V4":
            ctx.normal_qrs_pattern = "variable_rotation"
            ctx.is_transition_shifted = True
        # V5-V6: transition here, may have smaller R than expected
        if lead in ("V5", "V6") and tz and tz > 5:
            ctx.normal_qrs_pattern = "late_transition"
            ctx.is_transition_shifted = True

    elif rotation == "counterclockwise":
        # V1-V2: tall R is expected (not RVH or posterior MI necessarily)
        if lead in ("V1", "V2"):
            ctx.normal_qrs_pattern = "tall_R_expected_rotation"
            ctx.is_transition_shifted = True
        # V3-V4: R already dominant, transition already passed
        if lead in ("V3", "V4"):
            ctx.normal_qrs_pattern = "R_dominant_early_transition"
            ctx.is_transition_shifted = True


def _adjust_for_axis(ctx: LeadContext):
    """Adjust normal expected morphology based on actual QRS axis."""
    axis = ctx.qrs_axis_deg
    lead = ctx.lead_name

    if axis is None:
        return

    # Left axis deviation (< -30°)
    if axis < -30:
        if lead == "III":
            ctx.normal_qrs_pattern = "negative"  # QRS negative in III with LAD
            ctx.normal_t_polarity = "variable"
        if lead == "aVF":
            ctx.normal_qrs_pattern = "negative"
            ctx.normal_t_polarity = "variable"
        if lead == "II":
            ctx.normal_qrs_pattern = "small_or_isoelectric"
        if lead in ("I", "aVL"):
            ctx.normal_qrs_pattern = "tall_positive"

    # Right axis deviation (> +90°)
    elif axis > 90:
        if lead == "I":
            ctx.normal_qrs_pattern = "small_or_negative"
            ctx.normal_t_polarity = "variable"
        if lead == "aVL":
            ctx.normal_qrs_pattern = "negative"
            ctx.normal_t_polarity = "variable"
        if lead in ("III", "aVF"):
            ctx.normal_qrs_pattern = "tall_positive"

    # Extreme axis (±180°)
    if abs(axis) > 150:
        # Almost everything negative — VT, severe hyperK, etc.
        ctx.normal_qrs_pattern = "abnormal_extreme"


def is_t_inversion_normal(lead: str, qrs_axis_deg: Optional[float] = None,
                           age: Optional[int] = None) -> bool:
    """Check if T-wave inversion is a normal finding in this lead."""
    # V1: T inversion is normal
    if lead == "V1":
        return True
    # aVR: T inversion is normal (everything inverted)
    if lead == "aVR":
        return True
    # V2-V3 with age < 25: juvenile pattern
    if lead in ("V2", "V3") and age is not None and age < 25:
        return True
    # III with LAD: T inversion expected
    if lead == "III" and qrs_axis_deg is not None and qrs_axis_deg < -30:
        return True
    # aVL with RAD
    if lead == "aVL" and qrs_axis_deg is not None and qrs_axis_deg > 90:
        return True
    return False


def get_reciprocal_territory(territory: str) -> Optional[str]:
    """Get the reciprocal territory for a given territory."""
    return RECIPROCAL_TERRITORIES.get(territory)


def get_reciprocal_leads(territory: str) -> list[str]:
    """Get leads that show reciprocal changes for a given territory."""
    recip = get_reciprocal_territory(territory)
    if recip:
        return TERRITORY_LEADS.get(recip, [])
    return []


def detect_dextrocardia(features) -> bool:
    """
    Detect possible dextrocardia or limb lead reversal.

    Signs:
    - Lead I: globally negative (P inverted, QRS negative, T inverted)
    - R-wave progression: decreasing V1→V6 (reversed)
    - aVR: looks like normal Lead I (P upright, QRS positive)
    """
    if features is None:
        return False

    # Check Lead I: R amplitude should normally be positive/dominant
    r_i = features.r_amplitude_mv.get("I", 0) or 0
    s_i = features.s_amplitude_mv.get("I", 0) or 0

    # If S > R in Lead I AND R progression is reversed → possible dextrocardia
    lead_i_negative = s_i > r_i * 1.5 if r_i > 0 else False

    # Check reversed R-wave progression
    r_prog = features.r_progression
    reversed_prog = r_prog in ("reverse", "poor")

    # Check axis — extreme right or northwest
    axis = features.qrs_axis_deg
    extreme_axis = axis is not None and (axis > 150 or axis < -150)

    return lead_i_negative and (reversed_prog or extreme_axis)


def detect_heart_position(features) -> dict:
    """
    Detect overall heart position characteristics.

    Returns dict with:
      rotation: "normal" | "clockwise" | "counterclockwise"
      axis_category: "normal" | "lad" | "rad" | "extreme"
      transition_zone: float or None
      dextrocardia: bool
      low_voltage: bool
    """
    if features is None:
        return {"rotation": "normal", "axis_category": "normal",
                "transition_zone": None, "dextrocardia": False, "low_voltage": False}

    # Axis
    axis = features.qrs_axis_deg
    if axis is None:
        axis_cat = "indeterminate"
    elif -30 <= axis <= 90:
        axis_cat = "normal"
    elif -90 <= axis < -30:
        axis_cat = "lad"
    elif 90 < axis <= 180:
        axis_cat = "rad"
    else:
        axis_cat = "extreme"

    # Rotation
    rotation = _classify_horizontal_rotation(
        features.r_progression, features.r_progression_index
    )

    # Low voltage
    low_v = features.low_voltage_limb or features.low_voltage_precordial

    return {
        "rotation": rotation,
        "axis_category": axis_cat,
        "transition_zone": features.r_progression_index,
        "dextrocardia": detect_dextrocardia(features),
        "low_voltage": low_v,
    }
