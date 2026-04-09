"""
Shape descriptor — samples N evenly-spaced points from a segment.

Instead of classifying into predefined categories (which introduces bias),
this describes the shape by its actual sampled values. The LLM reads the
point values and interprets the morphology itself.

For each segment (P, QRS, ST, T):
  1. Extract the signal between fiducial points
  2. Remove baseline
  3. Normalize amplitude to [-1, +1]
  4. Sample N evenly-spaced points
  5. Report: the N values + key measurements (amplitude, duration, etc.)
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
import numpy as np
from scipy.signal import resample


@dataclass
class ShapeDescriptor:
    """Raw shape description — N sampled points + measurements."""
    segment: str             # "P" | "QRS" | "ST" | "T"
    n_points: int            # number of sampled points
    points: list[float]      # N normalized values in [-1, +1]
    amplitude_mv: float      # peak amplitude in mV
    duration_ms: float       # segment duration in ms
    polarity: str            # "positive" | "negative" | "biphasic"
    area_positive: float     # normalized positive area (0-1)
    area_negative: float     # normalized negative area (0-1)
    peak_position: float     # where the peak is (0=start, 1=end)
    slope_start: float       # slope at first 20% of segment
    slope_end: float         # slope at last 20% of segment
    baseline_mv: float       # baseline reference used


def describe_shape(
    signal: np.ndarray,
    onset: int,
    peak: int,
    offset: int,
    fs: float,
    segment_type: str = "T",
    n_points: int = 12,
    baseline_ref: Optional[float] = None,
) -> Optional[ShapeDescriptor]:
    """
    Describe a segment shape by sampling N evenly-spaced points.

    Args:
        signal: full lead signal (µV)
        onset, peak, offset: sample indices
        fs: sample rate
        segment_type: "P" | "QRS" | "ST" | "T"
        n_points: number of evenly-spaced sample points (default 12)
        baseline_ref: isoelectric baseline (µV). If None, estimated.

    Returns:
        ShapeDescriptor or None if segment invalid.
    """
    n = len(signal)
    if onset < 0 or offset < 0 or onset >= n or offset >= n:
        return None
    if offset <= onset or offset - onset < 3:
        return None

    seg = signal[onset:offset].astype(np.float64)
    seg_len = len(seg)

    # Baseline
    if baseline_ref is not None:
        bl = baseline_ref
    else:
        bl_start = max(0, onset - int(0.02 * fs))
        bl_seg = signal[bl_start:onset].astype(np.float64)
        bl = float(np.mean(bl_seg)) if len(bl_seg) > 3 else float(seg[0])

    centered = seg - bl
    duration_ms = seg_len / fs * 1000.0

    # Amplitude
    peak_idx = peak - onset if onset <= peak <= offset else seg_len // 2
    if 0 <= peak_idx < seg_len:
        amplitude = float(centered[peak_idx])
    else:
        amplitude = float(centered[np.argmax(np.abs(centered))])
    amplitude_mv = amplitude / 1000.0

    # Normalize to [-1, +1]
    max_abs = float(np.max(np.abs(centered)))
    if max_abs > 0:
        normalized = centered / max_abs
    else:
        normalized = centered

    # Sample N evenly-spaced points
    indices = np.linspace(0, seg_len - 1, n_points).astype(int)
    points = [round(float(normalized[i]), 3) for i in indices]

    # Polarity
    pos_area = float(np.sum(np.maximum(normalized, 0))) / max(seg_len, 1)
    neg_area = float(np.sum(np.maximum(-normalized, 0))) / max(seg_len, 1)
    total = pos_area + neg_area
    if total > 0:
        pos_frac = pos_area / total
        neg_frac = neg_area / total
    else:
        pos_frac = neg_frac = 0.5

    if pos_frac > 0.7:
        polarity = "positive"
    elif neg_frac > 0.7:
        polarity = "negative"
    elif pos_frac > 0.15 and neg_frac > 0.15:
        polarity = "biphasic"
    else:
        polarity = "flat"

    # Peak position (0=start, 1=end)
    abs_peak_idx = int(np.argmax(np.abs(normalized)))
    peak_pos = abs_peak_idx / max(seg_len - 1, 1)

    # Slopes
    n20 = max(1, seg_len // 5)
    slope_start = float(np.mean(np.diff(normalized[:n20]))) if n20 > 1 else 0.0
    slope_end = float(np.mean(np.diff(normalized[-n20:]))) if n20 > 1 else 0.0

    return ShapeDescriptor(
        segment=segment_type,
        n_points=n_points,
        points=points,
        amplitude_mv=round(amplitude_mv, 3),
        duration_ms=round(duration_ms, 1),
        polarity=polarity,
        area_positive=round(pos_frac, 3),
        area_negative=round(neg_frac, 3),
        peak_position=round(peak_pos, 3),
        slope_start=round(slope_start, 4),
        slope_end=round(slope_end, 4),
        baseline_mv=round(bl / 1000.0, 3),
    )


def format_shape_for_narration(desc: ShapeDescriptor) -> str:
    """
    Format a shape descriptor as a compact string for the narration.

    Example output:
      "T-shape(12pts): [0.1, 0.3, 0.6, 0.9, 1.0, 0.8, 0.4, 0.1, -0.1, -0.3, -0.5, -0.7]
       amp=0.45mV dur=280ms pol=positive peak@0.35 slopes:+0.05/-0.04"
    """
    pts_str = "[" + ", ".join(f"{p:+.2f}" for p in desc.points) + "]"
    return (
        f"{desc.segment}-shape({desc.n_points}pts): {pts_str} "
        f"amp={desc.amplitude_mv:+.2f}mV dur={desc.duration_ms:.0f}ms "
        f"pol={desc.polarity} peak@{desc.peak_position:.2f} "
        f"slopes:{desc.slope_start:+.3f}/{desc.slope_end:+.3f}"
    )
