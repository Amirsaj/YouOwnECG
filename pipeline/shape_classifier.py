"""
ECG Morphology Shape Classifier.

Classifies each ECG segment (P, QRS, ST, T) into one of the 41 defined shapes
using scale-invariant geometric features + normalized waveform template matching.

The classifier does NOT make diagnostic conclusions — it identifies the SHAPE
and reports geometric measurements. The LLM combines shapes into diagnoses.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
import numpy as np
from scipy.signal import resample, savgol_filter

from pipeline.shape_templates import (
    ShapeTemplate, get_shapes_for_segment, SHAPE_BY_CODE
)


RESAMPLE_LENGTH = 64  # fixed-length normalized waveform


@dataclass
class ShapeClassification:
    code: str                     # "T3"
    name: str                     # "Peaked Tented (Hyperkalemia)"
    confidence: float             # 0.0 - 1.0
    features: dict                # computed geometric features
    runner_up: Optional[str]      # second-best match code
    runner_up_confidence: float = 0.0


@dataclass
class SegmentFeatures:
    """Scale-invariant geometric features extracted from one segment."""
    symmetry: float = 0.5        # area-based symmetry index (0-1)
    base_width_ratio: float = 0.5 # width at 50% amplitude / total width
    peak_sharpness: float = 0.0  # |2nd deriv at peak| / |amplitude|
    n_peaks: int = 1             # amplitude-gated peak count
    polarity: str = "positive"   # "positive" | "negative" | "biphasic"
    curvature: float = 0.0       # parabolic fit coefficient (normalized)
    slope_ratio: float = 1.0     # initial slope / max slope (QRS only)
    amplitude_mv: float = 0.0    # absolute amplitude for context
    duration_ms: float = 0.0     # segment duration for context
    normalized_waveform: Optional[np.ndarray] = None  # 64-sample [-1, +1]


def extract_segment_features(
    signal: np.ndarray,
    onset: int,
    peak: int,
    offset: int,
    fs: float,
    segment_type: str = "T",
    baseline_ref: Optional[float] = None,
) -> SegmentFeatures:
    """
    Extract scale-invariant geometric features from a signal segment.

    Args:
        signal: full lead signal (µV)
        onset, peak, offset: sample indices defining the segment
        fs: sample rate
        segment_type: "P" | "QRS" | "ST" | "T"
        baseline_ref: isoelectric baseline value (µV). If None, estimated.
    """
    n = len(signal)
    if onset < 0 or peak < 0 or offset < 0:
        return SegmentFeatures()
    if not (0 <= onset < n and 0 <= peak < n and 0 <= offset < n):
        return SegmentFeatures()
    if not (onset < peak < offset) and segment_type != "ST":
        return SegmentFeatures()
    if offset - onset < 5:
        return SegmentFeatures()

    # For ST segment: onset=J-point, offset=T-onset, peak not meaningful
    if segment_type == "ST":
        seg = signal[onset:offset].astype(np.float64)
        peak_idx_in_seg = len(seg) // 2  # midpoint
    else:
        seg = signal[onset:offset].astype(np.float64)
        peak_idx_in_seg = peak - onset

    # Baseline
    if baseline_ref is not None:
        bl = baseline_ref
    else:
        bl_start = max(0, onset - int(0.02 * fs))
        bl_seg = signal[bl_start:onset].astype(np.float64)
        bl = float(np.mean(bl_seg)) if len(bl_seg) > 3 else float(seg[0])

    centered = seg - bl
    amplitude = float(centered[peak_idx_in_seg])
    amplitude_mv = amplitude / 1000.0
    duration_ms = len(seg) / fs * 1000.0

    # ── Smooth for feature extraction ──
    if len(centered) > 11:
        smoothed = savgol_filter(centered, min(11, len(centered) | 1), 3)
    else:
        smoothed = centered.copy()

    # ── Feature 1: Symmetry (area-based) ──
    ascending = smoothed[:peak_idx_in_seg + 1]
    descending = smoothed[peak_idx_in_seg:]
    asc_area = float(np.sum(np.abs(ascending)))
    desc_area = float(np.sum(np.abs(descending)))
    symmetry = min(asc_area, desc_area) / max(asc_area, desc_area) if max(asc_area, desc_area) > 0 else 0.5

    # ── Feature 2: Base Width Ratio ──
    abs_centered = np.abs(smoothed)
    peak_amp = float(np.max(abs_centered))
    if peak_amp > 0:
        half_amp = peak_amp * 0.5
        above_half = abs_centered >= half_amp
        width_at_50 = float(np.sum(above_half))
        bwr = width_at_50 / len(smoothed)
    else:
        bwr = 0.5

    # ── Feature 3: Peak Sharpness (normalized curvature) ──
    if len(smoothed) > 4 and peak_idx_in_seg > 0 and peak_idx_in_seg < len(smoothed) - 1:
        d2 = np.diff(smoothed, n=2)
        if peak_idx_in_seg - 1 < len(d2):
            curvature_at_peak = float(d2[peak_idx_in_seg - 1])
            sharpness = abs(curvature_at_peak) / max(abs(amplitude), 1.0)
        else:
            sharpness = 0.0
    else:
        sharpness = 0.0

    # ── Feature 4: Number of Peaks ──
    from scipy.signal import find_peaks
    abs_gate = max(peak_amp * 0.10, 30.0)  # 10% of peak-to-peak or 30µV
    pos_peaks, _ = find_peaks(smoothed, prominence=abs_gate)
    neg_peaks, _ = find_peaks(-smoothed, prominence=abs_gate)
    n_peaks_total = len(pos_peaks) + len(neg_peaks)
    n_peaks_total = max(1, n_peaks_total)

    # ── Feature 5: Polarity ──
    mean_val = float(np.mean(centered))
    if segment_type == "T" or segment_type == "P":
        # Check for biphasic: significant positive AND negative phases
        pos_area = float(np.sum(np.maximum(centered, 0)))
        neg_area = float(np.sum(np.maximum(-centered, 0)))
        total_area = pos_area + neg_area
        if total_area > 0 and pos_area / total_area > 0.15 and neg_area / total_area > 0.15:
            polarity = "biphasic"
        elif amplitude > 20:  # 20 µV threshold
            polarity = "positive"
        elif amplitude < -20:
            polarity = "negative"
        else:
            polarity = "flat"
    else:
        polarity = "positive" if amplitude > 0 else "negative"

    # ── Feature 6: Curvature Coefficient (parabolic fit) ──
    if len(smoothed) > 5:
        x = np.linspace(-1, 1, len(smoothed))
        try:
            coeffs = np.polyfit(x, smoothed, 2)
            curvature = float(coeffs[0])  # a coefficient of ax² + bx + c
            # Normalize by segment length squared
            curvature_norm = curvature * (len(smoothed) ** 2) / max(peak_amp, 1.0)
        except np.linalg.LinAlgError:
            curvature_norm = 0.0
    else:
        curvature_norm = 0.0

    # ── Feature 7: Slope Ratio (QRS delta wave) ──
    slope_ratio = 1.0
    if segment_type == "QRS" and len(smoothed) > 5:
        d1 = np.abs(np.diff(smoothed))
        max_slope = float(np.max(d1)) if len(d1) > 0 else 1.0
        initial_n = max(1, int(0.020 * fs))  # first 20ms
        initial_slope = float(np.max(d1[:initial_n])) if len(d1) >= initial_n else float(np.max(d1))
        slope_ratio = initial_slope / max_slope if max_slope > 0 else 1.0

    # ── Normalized waveform (64 samples, [-1, +1]) ──
    if len(centered) >= 4:
        resampled = resample(centered, RESAMPLE_LENGTH)
        max_abs = float(np.max(np.abs(resampled)))
        if max_abs > 0:
            normalized = resampled / max_abs
        else:
            normalized = resampled
    else:
        normalized = np.zeros(RESAMPLE_LENGTH)

    return SegmentFeatures(
        symmetry=round(symmetry, 3),
        base_width_ratio=round(bwr, 3),
        peak_sharpness=round(sharpness, 4),
        n_peaks=n_peaks_total,
        polarity=polarity,
        curvature=round(curvature_norm, 3),
        slope_ratio=round(slope_ratio, 3),
        amplitude_mv=round(amplitude_mv, 3),
        duration_ms=round(duration_ms, 1),
        normalized_waveform=normalized,
    )


def classify_segment_shape(
    signal: np.ndarray,
    onset: int,
    peak: int,
    offset: int,
    fs: float,
    segment_type: str,
    baseline_ref: Optional[float] = None,
    lead_context=None,  # Optional[LeadContext] from pipeline.lead_context
) -> ShapeClassification:
    """
    Classify a signal segment into one of the defined shapes.

    Uses feature-based matching + optional DTW waveform matching.
    When lead_context is provided, adjusts scoring based on:
    - Whether the lead is aVR (shapes are interpreted inversely)
    - Whether the T-wave inversion is normal for this lead
    - BBB secondary change expectations
    - J-point position relative to baseline

    Returns the best match with confidence score.
    """
    features = extract_segment_features(
        signal, onset, peak, offset, fs, segment_type, baseline_ref
    )

    templates = get_shapes_for_segment(segment_type)
    if not templates:
        return ShapeClassification(
            code="?", name="Unknown", confidence=0.0,
            features=_features_dict(features), runner_up=None
        )

    scores = []
    for tmpl in templates:
        score = _score_template_match(features, tmpl, lead_context)
        scores.append((tmpl, score))

    # Sort by score descending
    scores.sort(key=lambda x: -x[1])
    best = scores[0]
    runner = scores[1] if len(scores) > 1 else None

    # Confidence: how much better is best vs runner-up
    if runner and runner[1] > 0:
        separation = (best[1] - runner[1]) / max(best[1], 0.01)
        confidence = min(1.0, 0.5 + separation * 0.5)
    else:
        confidence = min(1.0, best[1])

    return ShapeClassification(
        code=best[0].code,
        name=best[0].name,
        confidence=round(confidence, 2),
        features=_features_dict(features),
        runner_up=runner[0].code if runner else None,
        runner_up_confidence=round(runner[1], 2) if runner else 0.0,
    )


def _score_template_match(features: SegmentFeatures, tmpl: ShapeTemplate,
                          lead_context=None) -> float:
    """Score how well features match a template. Higher = better match.

    When lead_context is provided, applies bonuses/penalties:
    - aVR: shapes are expected to be inverted
    - BBB leads: discordant ST-T are expected (not pathological)
    - J-point position: affects ST shape interpretation
    """
    score = 0.0
    max_score = 0.0

    # Symmetry match
    lo, hi = tmpl.symmetry_range
    max_score += 1.0
    if lo <= features.symmetry <= hi:
        # Distance from center of range
        center = (lo + hi) / 2
        half_range = (hi - lo) / 2 + 0.01
        dist = abs(features.symmetry - center) / half_range
        score += 1.0 - dist * 0.5
    else:
        # Penalty: how far outside
        if features.symmetry < lo:
            score -= (lo - features.symmetry) * 2
        else:
            score -= (features.symmetry - hi) * 2

    # Base width ratio match
    lo, hi = tmpl.base_width_ratio_range
    max_score += 1.0
    if lo <= features.base_width_ratio <= hi:
        center = (lo + hi) / 2
        half_range = (hi - lo) / 2 + 0.01
        dist = abs(features.base_width_ratio - center) / half_range
        score += 1.0 - dist * 0.5

    # Peak sharpness match
    lo, hi = tmpl.peak_sharpness_range
    max_score += 1.0
    if lo <= features.peak_sharpness <= hi:
        score += 1.0
    elif features.peak_sharpness < lo:
        score -= min(1.0, (lo - features.peak_sharpness))

    # Number of peaks match
    lo, hi = tmpl.n_peaks
    max_score += 1.5
    if lo <= features.n_peaks <= hi:
        score += 1.5
    else:
        score -= abs(features.n_peaks - (lo + hi) / 2) * 0.3

    # Polarity match
    max_score += 2.0
    if tmpl.polarity == "any":
        score += 2.0
    elif tmpl.polarity == features.polarity:
        score += 2.0
    elif tmpl.polarity == "biphasic" and features.polarity == "biphasic":
        score += 2.0
    else:
        score -= 1.0  # polarity mismatch is significant

    # Curvature match (for ST shapes)
    lo, hi = tmpl.curvature_range
    if lo != -float('inf') or hi != float('inf'):
        max_score += 1.0
        if lo <= features.curvature <= hi:
            score += 1.0

    # Slope ratio (for QRS delta wave)
    lo, hi = tmpl.slope_ratio_range
    if tmpl.segment == "QRS":
        max_score += 1.0
        if lo <= features.slope_ratio <= hi:
            score += 1.0

    # DTW match against template waveform (if available)
    if tmpl.template is not None and features.normalized_waveform is not None:
        max_score += 2.0
        dtw_dist = _fast_dtw_distance(features.normalized_waveform, tmpl.template)
        dtw_score = max(0, 2.0 - dtw_dist * 2.0)
        score += dtw_score

    # ── Lead-context adjustments ──
    if lead_context is not None:
        max_score += 2.0  # context contributes up to 2 points

        # aVR: everything is normally inverted
        if lead_context.is_avr:
            # In aVR, "inverted" T is normal → don't boost pathological T shapes
            if tmpl.segment == "T" and tmpl.polarity == "negative":
                score += 0.5  # mild boost — inverted is expected here
            # ST elevation in aVR is significant (global ischemia, de Winter reciprocal)
            if tmpl.segment == "ST" and tmpl.code in ("ST2", "ST3"):
                score += 1.5  # strong boost — ST elevation in aVR is diagnostically important

        # BBB: discordant ST-T changes are expected (secondary, not pathological)
        if lead_context.lbbb or lead_context.rbbb:
            terminal = lead_context.terminal_qrs_polarity
            if terminal and tmpl.segment in ("ST", "T"):
                # Discordant = ST/T opposite to terminal QRS = EXPECTED
                is_discordant = (
                    (terminal == "positive" and tmpl.polarity == "negative") or
                    (terminal == "negative" and tmpl.polarity == "positive")
                )
                if is_discordant:
                    # Reduce score for pathological shapes — this is expected BBB change
                    if tmpl.code in ("T4", "T5", "T10", "ST3", "ST5", "ST6"):
                        score -= 0.5  # penalize pathological interpretation
                    score += 1.0  # boost "expected secondary change" interpretation

        # J-point position context
        if lead_context.j_point_mv is not None and tmpl.segment == "ST":
            j = lead_context.j_point_mv
            # If J-point is above baseline but shape says "depression"
            if j > 0.05 and tmpl.code in ("ST5", "ST6", "ST7"):
                score -= 0.5  # penalize — J-point is above baseline, not depressed
            # If J-point is below baseline but shape says "elevation"
            if j < -0.05 and tmpl.code in ("ST2", "ST3"):
                score -= 0.5  # penalize — J-point is below baseline

        # T-wave inversion normality
        if tmpl.segment == "T" and tmpl.polarity == "negative":
            from pipeline.lead_context import is_t_inversion_normal
            if is_t_inversion_normal(lead_context.lead_name, lead_context.qrs_axis_deg):
                # T inversion is normal in this lead — don't score pathological shapes high
                if tmpl.code in ("T4", "T5", "T10"):
                    score -= 0.5

        # Lead-specific template context (from shape template)
        if tmpl.lead_context:
            territory = lead_context.territory
            for lead_pattern, expected in tmpl.lead_context.items():
                if territory in lead_pattern or lead_context.lead_name in lead_pattern:
                    score += 1.0  # bonus for matching lead-specific expectation

    # Normalize to 0-1 range
    return max(0.0, score / max(max_score, 1.0))


@dataclass
class CompositeMatch:
    code: str                     # "C1"
    name: str                     # "de Winter"
    clinical_name: str
    confidence: float
    segments_matched: dict        # {"ST": "ST7", "T": "T13"}
    criteria_note: str = ""


def detect_composite_patterns(
    shape_results: dict[str, ShapeClassification],
) -> list[CompositeMatch]:
    """
    Check if individual segment shapes form a known composite pattern.

    Args:
        shape_results: {"P": ShapeClassification, "QRS": ..., "ST": ..., "T": ...}

    Returns:
        List of matched composite patterns with confidence.
    """
    from pipeline.shape_templates import get_composite_patterns

    matches = []
    for pattern in get_composite_patterns():
        all_match = True
        matched_segs = {}
        min_conf = 1.0

        for seg, valid_codes in pattern.required_shapes.items():
            if seg not in shape_results:
                all_match = False
                break
            cls = shape_results[seg]
            if cls.code in valid_codes:
                matched_segs[seg] = cls.code
                min_conf = min(min_conf, cls.confidence)
            else:
                all_match = False
                break

        if all_match:
            matches.append(CompositeMatch(
                code=pattern.code,
                name=pattern.name,
                clinical_name=pattern.clinical_name,
                confidence=round(min_conf, 2),
                segments_matched=matched_segs,
                criteria_note=pattern.cross_segment_criteria,
            ))

    return matches


def _fast_dtw_distance(a: np.ndarray, b: np.ndarray) -> float:
    """Simple Euclidean distance between normalized waveforms (fast DTW approximation)."""
    if len(a) != len(b):
        b = resample(b, len(a))
    return float(np.sqrt(np.mean((a - b) ** 2)))


def _features_dict(f: SegmentFeatures) -> dict:
    """Convert SegmentFeatures to a plain dict for JSON serialization."""
    return {
        "symmetry": f.symmetry,
        "base_width_ratio": f.base_width_ratio,
        "peak_sharpness": f.peak_sharpness,
        "n_peaks": f.n_peaks,
        "polarity": f.polarity,
        "curvature": f.curvature,
        "slope_ratio": f.slope_ratio,
        "amplitude_mv": f.amplitude_mv,
        "duration_ms": f.duration_ms,
    }
