"""
Agentic fiducial correction — 3-pass segment-first, all-leads architecture.

Processing order per beat:
  Pass 1 → P-WAVE agent   : corrects pon, ppeak, poff  for all 12 leads
  Pass 2 → QRS agent      : corrects qrson, q, r, s, qrsoff for all 12 leads
  Pass 3 → T-WAVE agent   : corrects ton, tpeak, toff  for all 12 leads

Each pass receives a single tall image showing ALL 12 leads stacked, zoomed to
that segment's time window (10ms grid, labeled ticks, current markers as dashed
lines). Cross-lead consistency is validated after every set_fiducial call.

LangGraph StateGraph manages each pass: agent node parses JSON tool calls,
tools node executes them. Three sequential passes share the same FiducialTable
deep copy so corrections accumulate.

Public entry point: run_fiducial_correction(record, fiducials, features, beat_idx)
"""

from __future__ import annotations

import base64
import copy
import json
import re
from typing import Any, Annotated, Optional

import numpy as np
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage, AIMessage
from langchain_ollama import ChatOllama

from pipeline.schemas import FiducialTable

# ── Column index constants ─────────────────────────────────────────────────────
COL_PON, COL_PPEAK, COL_POFF = 0, 1, 2
COL_QRSON, COL_Q, COL_R, COL_S, COL_QRSOFF = 3, 4, 5, 6, 7
COL_TON, COL_TPEAK, COL_TOFF = 9, 10, 11

_POINT_TO_COL: dict[str, int] = {
    "pon": COL_PON, "ppeak": COL_PPEAK, "poff": COL_POFF,
    "qrson": COL_QRSON, "q": COL_Q, "r": COL_R,
    "s": COL_S, "qrsoff": COL_QRSOFF,
    "ton": COL_TON, "tpeak": COL_TPEAK, "toff": COL_TOFF,
}
_ORDERED_POINTS = ["pon", "ppeak", "poff", "qrson", "q", "r", "s", "qrsoff", "ton", "tpeak", "toff"]
_OPTIONAL_POINTS = {"pon", "ppeak", "poff", "q", "s", "ton", "tpeak", "toff"}
_POINT_LABELS = {
    "pon": "P-onset", "ppeak": "P-peak", "poff": "P-offset",
    "qrson": "QRS-onset", "q": "Q-nadir", "r": "R-peak",
    "s": "S-nadir", "qrsoff": "QRS-offset (J-point)",
    "ton": "T-onset", "tpeak": "T-peak", "toff": "T-offset",
}
_PHYS_RANGES = {
    "p_duration":   (40,  250),
    "pr_interval":  (80,  350),
    "qrs_duration": (40,  220),
    "qt_interval":  (200, 600),
}

# Standard 12-lead order (clinical layout)
LEAD_ORDER = ["I", "II", "III", "aVR", "aVL", "aVF", "V1", "V2", "V3", "V4", "V5", "V6"]

# Segment → which fiducial points each pass owns
_PASS_POINTS = {
    "p":   ["pon", "ppeak", "poff"],
    "qrs": ["qrson", "q", "r", "s", "qrsoff"],
    "t":   ["ton", "tpeak", "toff"],
}

# Colors for fiducial markers on the zoomed strip
_MARKER_COLORS = {
    "pon": "#3498DB", "ppeak": "#3498DB", "poff": "#3498DB",
    "qrson": "#E74C3C", "q": "#7F8C8D", "r": "#E74C3C",
    "s": "#E67E22", "qrsoff": "#F1C40F",
    "ton": "#9B59B6", "tpeak": "#9B59B6", "toff": "#9B59B6",
}

# ── LangGraph state ────────────────────────────────────────────────────────────

class CorrectionState(TypedDict):
    messages:  Annotated[list, add_messages]
    accepted:  bool
    iteration: int


# ── System prompts (one per pass) ─────────────────────────────────────────────

_TOOL_FORMAT = """
## How to call tools
Respond with a JSON array inside a ```json block:
```json
[
  {"tool": "tool_name", "args": {"arg1": "value1"}},
  {"tool": "another_tool", "args": {}}
]
```
Multiple tools execute in order. Call accept_changes when done with this segment.

## IMPORTANT — reading the image
The RED portion of the signal is the segment you are correcting.
Black signal = context only (do not correct those markers in this pass).
Dashed vertical lines = current fiducial markers for THIS segment.

## Available tools

### INSPECTION — get current state
get_all_fiducial_positions()
  → Current positions for all leads (ms from beat window start, R≈400ms)

get_cross_lead_consistency(point)
  → Min/max/std of one fiducial point across all leads — flags outliers

### MATH/RULER — precise signal analysis
ruler(start_ms, end_ms)
  → Duration between two time points in ms (the ruler tool)

measure_slope(lead, t1_ms, t2_ms)
  → Rate of change between two points: slope_mv_per_ms, rise_mv, run_ms

measure_area(lead, start_ms, end_ms)
  → Signal integral vs baseline: area_mv_ms, above_baseline, below_baseline

find_inflection_point(lead, start_ms, end_ms)
  → Where slope changes direction (true peak/nadir) — uses second derivative

find_local_max(lead, start_ms, end_ms)
  → Exact peak position + amplitude in search window

find_local_min(lead, start_ms, end_ms)
  → Exact trough position + amplitude in search window

find_onset(lead, start_ms, end_ms)
  → First signal deviation from isoelectric baseline (left→right)

find_offset(lead, start_ms, end_ms)
  → Last signal deviation before baseline return (right→left)

measure_amplitude(lead, time_ms)
  → Signal amplitude in mV at exact time

get_baseline_level(lead)
  → Isoelectric baseline + noise floor

zoom_lead(lead, start_ms, end_ms)
  → Zoomed image of one lead only — use when uncertain about one lead

### WRITE — set corrected positions
set_fiducial(lead, point, time_ms)
  → Move marker (validated). Points: pon ppeak poff qrson q r s qrsoff ton tpeak toff

set_fiducial_all_leads(point, time_ms)
  → Set same point across all leads (forbidden for r — must vary per lead)

mark_absent(lead, point)
  → Mark optional point absent (pon ppeak poff q s ton tpeak toff only)

mark_absent_all_leads(point)
  → Mark point absent in every lead (use for AFib: no P-waves anywhere)

accept_changes()
  → Finalize this segment pass
"""

_P_SYSTEM = """You are an expert ECG fiducial inspector reviewing P-WAVE marker positions across all 12 leads.
The RED signal is the P-wave region you must correct. Black signal is context only — do not move QRS/T markers here.
Use ruler, measure_slope, find_inflection_point, find_onset, find_offset to locate exact boundaries mathematically before calling set_fiducial.

## P-wave — medical context
- P-wave = atrial depolarization. Precedes QRS by PR interval (120–200ms normal).
- Duration: 80–120ms (up to 200ms in left atrial enlargement)
- Amplitude: 0.1–0.3mV normal
- Expected polarity by lead:
    Upright  : I, II, aVF, V4, V5, V6
    Inverted : aVR (always inverted — normal)
    Variable : III, aVL, V1, V2, V3 (depends on axis)
- P-ONSET is the same atrial depolarization front → should be within ±15ms across leads
- P-OFFSET should be within ±20ms across leads
- ABSENT P-waves in ALL leads → atrial fibrillation (mark all absent)
- Bifid (notched) P in I, II → left atrial enlargement (LAE)
- Peaked (tall, narrow) P in II, III → right atrial enlargement (RAE)
- The pipeline has poor P-detection (12% detection rate). Expect most markers to be wrong.

## Your task
1. Call get_all_fiducial_positions() to see current P-wave markers
2. Call get_cross_lead_consistency("pon") and ("poff") to check spread
3. For each lead: use find_onset/find_offset to locate P boundaries, find_local_max for P-peak
4. Correct misplaced markers with set_fiducial. Use set_fiducial_all_leads for consistent onset/offset.
5. Call zoom_lead if uncertain about one specific lead
6. Call accept_changes when all P-wave markers are correct
""" + _TOOL_FORMAT

_QRS_SYSTEM = """You are an expert ECG fiducial inspector reviewing QRS complex marker positions across all 12 leads.
The RED signal is the QRS region you must correct. Black signal is context only — do not move P/T markers here.
Use ruler, measure_slope, find_inflection_point, find_onset, find_offset, find_local_max/min to locate exact QRS boundaries and peaks mathematically before calling set_fiducial.

## QRS complex — medical context
- QRS = ventricular depolarization. Most visible and reliable waveform.
- Duration: 60–100ms normal; >120ms = bundle branch block (LBBB or RBBB)

## CRITICAL: R-PEAK CONDUCTION SHIFT
The electrical wavefront travels through the ventricle at finite speed.
R-peak MUST NOT be identical in all leads — this is a pipeline detection error.
Expected timing sequence (earlier → later):
  V1, V2 (septal) → V3, V4 (anterior) → V5, V6 (lateral) → II, III, aVF (inferior)
Typical spread: 5–15ms from earliest to latest lead
If all leads show R=400ms → wrong. Use find_local_max per lead to find true R-peak.

## QRS-onset
- Should be within ±15ms across all leads (same ventricular activation start)
- Use find_onset to locate where QRS first deflects from baseline

## Morphology by lead
- V1, V2: often rS or QS (small r, deep S) in normal hearts
- V4–V6: Rs or R (dominant R, small or no S)
- aVR: inverted QRS (negative) — large Q or QS pattern
- I, V6: broad notched R in LBBB; RSR' in V1 in RBBB
- Pathological Q: duration ≥40ms OR amplitude ≥25% of R height

## Your task
1. Call get_all_fiducial_positions() to see all QRS markers
2. Call get_cross_lead_consistency("r") — if std < 2ms, R-peaks are suspiciously identical
3. Per lead: use find_local_max for R, find_local_min for S and Q
4. Use find_onset for qrson (should be similar across leads), find_offset for qrsoff
5. Correct misplaced markers. Set qrson/qrsoff consistently with set_fiducial_all_leads.
6. Set r, q, s per-lead individually (they vary by lead)
7. Call accept_changes when complete
""" + _TOOL_FORMAT

_T_SYSTEM = """You are an expert ECG fiducial inspector reviewing T-WAVE and ST-segment marker positions across all 12 leads.
The RED signal is the T-wave/ST region you must correct. Black signal is context only — do not move P/QRS markers here.
Use ruler, measure_slope, measure_area, find_inflection_point, find_onset, find_offset to locate exact T-wave boundaries and peak mathematically before calling set_fiducial.

## T-wave — medical context
- T-wave = ventricular repolarization. Follows QRS after ST segment.
- Duration: 130–250ms

## T-WAVE CONCORDANCE RULE (critical)
T-wave direction should match QRS direction in the same lead:
  Lead has dominant positive QRS → T-wave should be upright (positive)
  Lead has dominant negative QRS → T-wave should be inverted
  EXCEPTIONS: aVR always inverted; V1 often inverted (normal)
Discordant T-wave = pathological (ischemia, Wellens, etc.)

## T-WAVE PATTERNS
- Hyperacute T (tall, wide, asymmetric): early STEMI — T-onset earlier than expected
- Wellens syndrome (deep symmetric T-inversion in V2–V4): critical LAD stenosis
- Symmetric T-inversion: more pathological than asymmetric
- Flat T-wave: ischemia, hypokalemia
- Peaked narrow T: hyperkalemia

## T-OFFSET (defines QTc — very important)
- All leads should have similar toff — variation >40ms = measurement error
- QTc normal: 350–450ms (Bazett formula: QT / √RR)
- Use find_offset per lead to find where T-wave returns to baseline

## T-ONSET
- Begins where signal first deviates from isoelectric ST segment
- Should be within ±25ms across leads
- T-peak is typically at 60–70% of QT interval from QRS-onset

## Your task
1. Call get_all_fiducial_positions() to see current T-wave markers
2. Call get_cross_lead_consistency("toff") — toff variation >40ms = error
3. Per lead: find_local_max for tpeak; find_onset for ton; find_offset for toff
4. Check concordance: compare T polarity with QRS dominant direction per lead
5. Correct markers with set_fiducial. Use set_fiducial_all_leads for toff to enforce QT consistency.
6. Call accept_changes when complete
""" + _TOOL_FORMAT


# ── Rendering ─────────────────────────────────────────────────────────────────

def render_all_leads_segment_strip(
    record, fid: FiducialTable, beat_idx: int, segment: str, features=None
) -> Optional[bytes]:
    """
    Render all 12 leads stacked vertically, zoomed to one segment's time window.

    segment: "p" | "qrs" | "t"
    Returns PNG bytes or None on failure.
    """
    import io
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.ticker as ticker

    # Determine time window from reference lead (II)
    ref_lead = "II" if "II" in fid.fpt else list(fid.fpt.keys())[0]
    ref_fpt = fid.fpt[ref_lead]
    row = ref_fpt[beat_idx]
    fs = fid.fs

    r = int(row[COL_R])
    if r < 0:
        return None
    half_win = int(0.4 * fs)
    win_start = max(0, r - half_win)

    def s2ms(col):
        v = int(row[col])
        return (v - win_start) / fs * 1000 if v >= 0 else None

    r_ms = s2ms(COL_R) or 400.0
    qrson_ms = s2ms(COL_QRSON) or (r_ms - 40)
    qrsoff_ms = s2ms(COL_QRSOFF) or (r_ms + 60)
    pon_ms = s2ms(COL_PON) or (qrson_ms - 120)
    poff_ms = s2ms(COL_POFF) or (qrson_ms - 20)
    toff_ms = s2ms(COL_TOFF) or (qrsoff_ms + 220)

    if segment == "p":
        t_start = max(0, pon_ms - 50)
        t_end = qrson_ms + 10
        title_seg = "P-WAVE"
        seg_points = _PASS_POINTS["p"]
    elif segment == "qrs":
        t_start = max(0, qrson_ms - 30)
        t_end = qrsoff_ms + 50
        title_seg = "QRS COMPLEX"
        seg_points = _PASS_POINTS["qrs"]
    else:  # t
        t_start = max(0, qrsoff_ms - 30)
        t_end = toff_ms + 50
        title_seg = "ST–T WAVE"
        seg_points = _PASS_POINTS["t"]

    # Leads to plot — use LEAD_ORDER, but only available leads
    available = [l for l in LEAD_ORDER if l in fid.fpt and l in record.lead_names]
    if not available:
        return None

    n = len(available)
    fig_h = max(8.0, n * 1.4)
    duration_ms = t_end - t_start
    fig_w = max(7.0, duration_ms / 40.0 * 2.8)

    fig, axes = plt.subplots(n, 1, figsize=(fig_w, fig_h), squeeze=False)
    fig.suptitle(
        f"Beat {beat_idx + 1} — {title_seg} — All Leads | "
        f"10ms grid | dashed lines = current markers",
        fontsize=9, fontweight="bold",
    )

    safe_start = fid.safe_window_start_sample

    for row_idx, lead in enumerate(available):
        ax = axes[row_idx, 0]
        li = record.lead_names.index(lead)
        sig_all = record.morphology_signal[li].astype(float) / 1000.0

        # Window for this lead
        lead_fpt = fid.fpt[lead]
        lead_row = lead_fpt[beat_idx]
        lead_r = int(lead_row[COL_R])
        if lead_r < 0:
            ax.set_visible(False)
            continue
        lead_win_start = max(0, lead_r - half_win)

        i0 = max(0, lead_win_start + round(t_start * fs / 1000))
        i1 = min(len(sig_all) - safe_start, lead_win_start + round(t_end * fs / 1000))
        sig = sig_all[safe_start + i0: safe_start + i1]
        if len(sig) == 0:
            ax.set_visible(False)
            continue
        t_ms = np.arange(len(sig)) / fs * 1000 + t_start

        # Signal
        ax.plot(t_ms, sig, "k-", linewidth=1.3, zorder=3)

        # Baseline
        qrson_v = int(lead_row[COL_QRSON])
        if qrson_v >= 0:
            bl_end = safe_start + qrson_v
            bl_start = max(0, bl_end - int(0.03 * fs))
            baseline = float(np.median(sig_all[bl_start:bl_end]))
        else:
            baseline = float(np.median(sig[:max(1, int(0.01 * fs))]))
        ax.axhline(baseline, color="#27AE60", linewidth=0.6, linestyle="--", alpha=0.5)

        # Fiducial markers for this segment
        for pt in seg_points:
            col = _POINT_TO_COL[pt]
            v = int(lead_row[col])
            if v < 0:
                continue
            t = (v - lead_win_start) / fs * 1000
            if not (t_start - 5 <= t <= t_end + 5):
                continue
            color = _MARKER_COLORS.get(pt, "gray")
            ax.axvline(t, color=color, linewidth=1.0, linestyle="--", alpha=0.85, zorder=4)
            sig_idx = np.argmin(np.abs(t_ms - t))
            y_val = float(sig[sig_idx]) if sig_idx < len(sig) else baseline
            ax.text(
                t, y_val,
                f"{pt}\n{t:.0f}",
                fontsize=5.5, ha="center", va="bottom" if y_val >= baseline else "top",
                color=color, fontweight="bold", zorder=5,
            )

        # Grid
        ax.xaxis.set_minor_locator(ticker.MultipleLocator(10))
        ax.xaxis.set_major_locator(ticker.MultipleLocator(50))
        ax.yaxis.set_minor_locator(ticker.MultipleLocator(0.1))
        ax.yaxis.set_major_locator(ticker.MultipleLocator(0.5))
        ax.grid(which="minor", color="#F0F0F0", linewidth=0.3)
        ax.grid(which="major", color="#D5D5D5", linewidth=0.6)

        # Dynamic y-axis
        sig_max = float(np.max(sig))
        sig_min = float(np.min(sig))
        margin = max(0.15, (sig_max - sig_min) * 0.25)
        ax.set_ylim(sig_min - margin, sig_max + margin)
        ax.set_xlim(t_start, t_end)

        # Lead label
        ax.set_ylabel(lead, fontsize=8, fontweight="bold", rotation=0, labelpad=28, va="center")
        ax.tick_params(labelsize=6, length=2)
        if row_idx < n - 1:
            ax.set_xticklabels([])
        else:
            ax.set_xlabel("ms from beat window start (R-peak ≈ 400ms)", fontsize=8)

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    buf.seek(0)
    return buf.read()


def render_segment_focused_strip(
    record, fid: FiducialTable, beat_idx: int, segment: str, features=None
) -> Optional[bytes]:
    """
    Render all 12 leads stacked with the target segment highlighted RED, everything else BLACK.

    This is the FiducialAgent's primary input: the segment being corrected stands out visually
    so the agent can focus on exact boundary detection without distraction from other waveforms.

    segment: "p" | "qrs" | "t"
    Returns PNG bytes or None on failure.
    """
    import io
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.ticker as ticker

    ref_lead = "II" if "II" in fid.fpt else list(fid.fpt.keys())[0]
    ref_fpt = fid.fpt[ref_lead]
    row = ref_fpt[beat_idx]
    fs = fid.fs

    r = int(row[COL_R])
    if r < 0:
        return None
    half_win = int(0.4 * fs)
    win_start = max(0, r - half_win)

    def s2ms(col):
        v = int(row[col])
        return (v - win_start) / fs * 1000 if v >= 0 else None

    r_ms    = s2ms(COL_R)     or 400.0
    qrson_ms = s2ms(COL_QRSON) or (r_ms - 40)
    qrsoff_ms = s2ms(COL_QRSOFF) or (r_ms + 60)
    pon_ms  = s2ms(COL_PON)   or (qrson_ms - 120)
    poff_ms = s2ms(COL_POFF)  or (qrson_ms - 20)
    toff_ms = s2ms(COL_TOFF)  or (qrsoff_ms + 220)
    ton_ms  = s2ms(COL_TON)   or (qrsoff_ms + 30)

    # Time window for the view (full beat context)
    t_start = max(0.0, pon_ms - 60)
    t_end   = toff_ms + 60

    # Red time range — the segment being corrected
    _seg_red = {
        "p":   (max(0.0, pon_ms - 20), poff_ms + 10),
        "qrs": (max(0.0, qrson_ms - 20), qrsoff_ms + 20),
        "t":   (max(0.0, qrsoff_ms - 10), toff_ms + 30),
    }
    red_start, red_end = _seg_red[segment]

    seg_labels = {"p": "P-WAVE", "qrs": "QRS COMPLEX", "t": "ST–T WAVE"}
    seg_points = _PASS_POINTS[segment]

    available = [l for l in LEAD_ORDER if l in fid.fpt and l in record.lead_names]
    if not available:
        return None

    n = len(available)
    duration_ms = t_end - t_start
    fig_h = max(8.0, n * 1.4)
    fig_w = max(8.0, duration_ms / 40.0 * 2.8)

    fig, axes = plt.subplots(n, 1, figsize=(fig_w, fig_h), squeeze=False)
    fig.patch.set_facecolor("white")
    fig.suptitle(
        f"Beat {beat_idx + 1} — {seg_labels[segment]} FOCUS  |  "
        f"RED = target segment  |  black = context  |  dashes = current markers",
        fontsize=9, fontweight="bold",
    )

    safe_start = fid.safe_window_start_sample

    for row_idx, lead in enumerate(available):
        ax = axes[row_idx, 0]
        li = record.lead_names.index(lead)
        sig_all = record.morphology_signal[li].astype(float) / 1000.0

        lead_fpt = fid.fpt[lead]
        lead_row = lead_fpt[beat_idx]
        lead_r = int(lead_row[COL_R])
        if lead_r < 0:
            ax.set_visible(False)
            continue
        lead_win_start = max(0, lead_r - half_win)

        i0 = max(0, lead_win_start + round(t_start * fs / 1000))
        i1 = min(len(sig_all) - safe_start, lead_win_start + round(t_end * fs / 1000))
        sig = sig_all[safe_start + i0: safe_start + i1]
        if len(sig) == 0:
            ax.set_visible(False)
            continue
        t_ms = np.arange(len(sig)) / fs * 1000 + t_start

        # Plot: black for context, red for target segment
        black_mask = (t_ms < red_start) | (t_ms > red_end)
        red_mask   = (t_ms >= red_start) & (t_ms <= red_end)
        if black_mask.any():
            ax.plot(t_ms[black_mask], sig[black_mask], color="#222222", linewidth=1.0,
                    solid_capstyle="round", zorder=3)
        if red_mask.any():
            ax.plot(t_ms[red_mask], sig[red_mask], color="#E74C3C", linewidth=2.0,
                    solid_capstyle="round", zorder=4)

        # Baseline
        qrson_v = int(lead_row[COL_QRSON])
        if qrson_v >= 0:
            bl_end = safe_start + qrson_v
            bl_start = max(0, bl_end - int(0.03 * fs))
            baseline = float(np.median(sig_all[bl_start:bl_end]))
        else:
            baseline = float(np.median(sig[:max(1, int(0.01 * fs))]))
        ax.axhline(baseline, color="#27AE60", linewidth=0.5, linestyle="--", alpha=0.4)

        # Fiducial markers — only for points in this segment
        for pt in seg_points:
            col = _POINT_TO_COL[pt]
            v = int(lead_row[col])
            if v < 0:
                continue
            t = (v - lead_win_start) / fs * 1000
            if not (t_start - 5 <= t <= t_end + 5):
                continue
            color = _MARKER_COLORS.get(pt, "gray")
            ax.axvline(t, color=color, linewidth=1.2, linestyle="--", alpha=0.9, zorder=5)
            sig_idx = np.argmin(np.abs(t_ms - t))
            y_val = float(sig[sig_idx]) if sig_idx < len(sig) else baseline
            ax.text(t, y_val, f"{pt}\n{t:.0f}",
                    fontsize=5.5, ha="center", va="bottom" if y_val >= baseline else "top",
                    color=color, fontweight="bold", zorder=6)

        # Grid
        ax.xaxis.set_minor_locator(ticker.MultipleLocator(10))
        ax.xaxis.set_major_locator(ticker.MultipleLocator(50))
        ax.yaxis.set_minor_locator(ticker.MultipleLocator(0.1))
        ax.yaxis.set_major_locator(ticker.MultipleLocator(0.5))
        ax.grid(which="minor", color="#F0F0F0", linewidth=0.3)
        ax.grid(which="major", color="#D5D5D5", linewidth=0.6)

        sig_max = float(np.max(sig))
        sig_min = float(np.min(sig))
        margin = max(0.15, (sig_max - sig_min) * 0.25)
        ax.set_ylim(sig_min - margin, sig_max + margin)
        ax.set_xlim(t_start, t_end)
        ax.set_ylabel(lead, fontsize=8, fontweight="bold", rotation=0, labelpad=28, va="center")
        ax.tick_params(labelsize=6, length=2)
        if row_idx < n - 1:
            ax.set_xticklabels([])
        else:
            ax.set_xlabel("ms from beat window start (R-peak ≈ 400ms)", fontsize=8)

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    buf.seek(0)
    return buf.read()


# ── Tool executor ──────────────────────────────────────────────────────────────

class ToolExecutor:
    """Executes tool calls for one pass (one segment, all leads)."""

    def __init__(self, record, fid: FiducialTable, features, beat_idx: int, segment: str):
        self.record = record
        self.fid = fid           # shared reference — mutations accumulate across passes
        self.features = features
        self.beat_idx = beat_idx
        self.segment = segment   # "p" | "qrs" | "t"
        self.changes: list[dict] = []
        self.accepted = False

    # ── Coordinate helpers ────────────────────────────────────────────────────

    def _win_start(self, lead: str) -> int:
        fpt = self.fid.fpt[lead] if lead in self.fid.fpt else list(self.fid.fpt.values())[0]
        r = int(fpt[self.beat_idx, COL_R])
        return max(0, r - int(0.4 * self.fid.fs))

    def _s2ms(self, lead: str, sample: int) -> Optional[float]:
        return None if sample < 0 else (sample - self._win_start(lead)) / self.fid.fs * 1000

    def _ms2s(self, lead: str, ms: float) -> int:
        return self._win_start(lead) + round(ms * self.fid.fs / 1000)

    def _lead_sig(self, lead: str) -> np.ndarray:
        li = self.record.lead_names.index(lead)
        return self.record.morphology_signal[li].astype(float) / 1000.0

    def _sig_window(self, lead: str, start_ms: float, end_ms: float):
        sig_all = self._lead_sig(lead)
        safe = self.fid.safe_window_start_sample
        ws = self._win_start(lead)
        i0 = max(0, ws + round(start_ms * self.fid.fs / 1000))
        i1 = min(len(sig_all) - safe, ws + round(end_ms * self.fid.fs / 1000))
        sig = sig_all[safe + i0: safe + i1]
        t_ms = np.arange(len(sig)) / self.fid.fs * 1000 + start_ms
        return sig, t_ms

    def _baseline(self, lead: str) -> float:
        fpt = self.fid.fpt[lead] if lead in self.fid.fpt else list(self.fid.fpt.values())[0]
        qrson = int(fpt[self.beat_idx, COL_QRSON])
        if qrson < 0:
            return 0.0
        sig_all = self._lead_sig(lead)
        safe = self.fid.safe_window_start_sample
        end = safe + qrson
        start = max(0, end - int(0.03 * self.fid.fs))
        return float(np.median(sig_all[start:end]))

    # ── Validation ────────────────────────────────────────────────────────────

    def _validate(self, lead: str) -> tuple[bool, str]:
        fpt = self.fid.fpt[lead] if lead in self.fid.fpt else list(self.fid.fpt.values())[0]
        row = fpt[self.beat_idx]
        pts = {nm: self._s2ms(lead, int(row[col])) for nm, col in _POINT_TO_COL.items()}

        prev_nm, prev_t = None, None
        for nm in _ORDERED_POINTS:
            t = pts[nm]
            if t is None:
                continue
            if prev_t is not None and t <= prev_t:
                return False, (f"Ordering: {_POINT_LABELS[nm]} ({t:.0f}ms) "
                               f"must follow {_POINT_LABELS[prev_nm]} ({prev_t:.0f}ms)")
            prev_nm, prev_t = nm, t

        for key, ep, sp in [("p_duration", "poff", "pon"), ("pr_interval", "qrson", "pon"),
                             ("qrs_duration", "qrsoff", "qrson"), ("qt_interval", "toff", "qrson")]:
            t0, t1 = pts.get(sp), pts.get(ep)
            if t0 is None or t1 is None:
                continue
            dur = t1 - t0
            lo, hi = _PHYS_RANGES[key]
            if not (lo <= dur <= hi):
                return False, f"{key}: {dur:.0f}ms outside [{lo}–{hi}ms]"
        return True, ""

    # ── Tools ─────────────────────────────────────────────────────────────────

    def get_all_fiducial_positions(self) -> dict:
        result = {}
        for lead in [l for l in LEAD_ORDER if l in self.fid.fpt]:
            fpt = self.fid.fpt[lead]
            row = fpt[self.beat_idx]
            result[lead] = {
                nm: {"time_ms": round(t, 1) if (t := self._s2ms(lead, int(row[col]))) is not None else None,
                     "detected": int(row[col]) >= 0}
                for nm, col in _POINT_TO_COL.items()
            }
        return {"positions": result, "note": "R-peak ≈ 400ms (beat window reference)"}

    def get_cross_lead_consistency(self, point: str) -> dict:
        if point not in _POINT_TO_COL:
            return {"error": f"Unknown point '{point}'"}
        col = _POINT_TO_COL[point]
        vals = {}
        for lead in [l for l in LEAD_ORDER if l in self.fid.fpt]:
            v = int(self.fid.fpt[lead][self.beat_idx, col])
            t = self._s2ms(lead, v)
            if t is not None:
                vals[lead] = round(t, 1)

        if len(vals) < 2:
            return {"point": point, "detected_in": list(vals.keys()), "note": "Too few leads to compare"}

        times = list(vals.values())
        std = float(np.std(times))
        spread = max(times) - min(times)
        flag = ""
        if point == "r" and std < 2.0:
            flag = "WARNING: R-peaks nearly identical across leads — likely pipeline error (should vary 5–15ms)"
        elif point in ("pon", "qrson", "ton") and spread > 30:
            flag = f"WARNING: {point} spread {spread:.0f}ms — too large, check outliers"
        elif point in ("toff", "qrsoff") and spread > 40:
            flag = f"WARNING: {point} spread {spread:.0f}ms — QT/QRS duration will be inconsistent"

        return {
            "point": point,
            "per_lead_ms": vals,
            "min_ms": round(min(times), 1),
            "max_ms": round(max(times), 1),
            "mean_ms": round(float(np.mean(times)), 1),
            "std_ms": round(std, 1),
            "spread_ms": round(spread, 1),
            "flag": flag,
        }

    def find_local_max(self, lead: str, start_ms: float, end_ms: float) -> dict:
        try:
            from scipy.ndimage import uniform_filter1d
            sig, t_ms = self._sig_window(lead, start_ms, end_ms)
            if len(sig) == 0:
                return {"error": "Empty window"}
            idx = int(np.argmax(uniform_filter1d(sig.astype(float), size=3)))
            return {"time_ms": round(float(t_ms[idx]), 1), "amplitude_mv": round(float(sig[idx]), 4)}
        except Exception as e:
            return {"error": str(e)}

    def find_local_min(self, lead: str, start_ms: float, end_ms: float) -> dict:
        try:
            from scipy.ndimage import uniform_filter1d
            sig, t_ms = self._sig_window(lead, start_ms, end_ms)
            if len(sig) == 0:
                return {"error": "Empty window"}
            idx = int(np.argmin(uniform_filter1d(sig.astype(float), size=3)))
            return {"time_ms": round(float(t_ms[idx]), 1), "amplitude_mv": round(float(sig[idx]), 4)}
        except Exception as e:
            return {"error": str(e)}

    def find_onset(self, lead: str, start_ms: float, end_ms: float) -> dict:
        try:
            sig, t_ms = self._sig_window(lead, start_ms, end_ms)
            if len(sig) == 0:
                return {"error": "Empty window"}
            baseline = self._baseline(lead)
            noise = float(np.std(sig[:max(1, int(0.02 * self.fid.fs))]))
            thresh = 2.5 * max(noise, 0.008)
            for i, s in enumerate(sig):
                if abs(float(s) - baseline) > thresh:
                    return {"time_ms": round(float(t_ms[i]), 1),
                            "amplitude_mv": round(float(s), 4),
                            "baseline_mv": round(baseline, 4)}
            return {"time_ms": None, "note": "No onset detected"}
        except Exception as e:
            return {"error": str(e)}

    def find_offset(self, lead: str, start_ms: float, end_ms: float) -> dict:
        try:
            sig, t_ms = self._sig_window(lead, start_ms, end_ms)
            if len(sig) == 0:
                return {"error": "Empty window"}
            baseline = self._baseline(lead)
            noise = float(np.std(sig[-max(1, int(0.02 * self.fid.fs)):]))
            thresh = 2.5 * max(noise, 0.008)
            for i in range(len(sig) - 1, -1, -1):
                if abs(float(sig[i]) - baseline) > thresh:
                    return {"time_ms": round(float(t_ms[i]), 1),
                            "amplitude_mv": round(float(sig[i]), 4),
                            "baseline_mv": round(baseline, 4)}
            return {"time_ms": None, "note": "No offset detected"}
        except Exception as e:
            return {"error": str(e)}

    # ── Math / ruler tools ────────────────────────────────────────────────────

    def ruler(self, start_ms: float, end_ms: float) -> dict:
        duration = end_ms - start_ms
        return {"start_ms": round(start_ms, 1), "end_ms": round(end_ms, 1),
                "duration_ms": round(duration, 1)}

    def measure_slope(self, lead: str, t1_ms: float, t2_ms: float) -> dict:
        try:
            a1 = self.measure_amplitude(lead, t1_ms)
            a2 = self.measure_amplitude(lead, t2_ms)
            if "error" in a1 or "error" in a2:
                return {"error": "amplitude lookup failed"}
            rise = a2["amplitude_mv"] - a1["amplitude_mv"]
            run = t2_ms - t1_ms
            if abs(run) < 1e-6:
                return {"error": "t1_ms == t2_ms"}
            return {"slope_mv_per_ms": round(rise / run, 6),
                    "rise_mv": round(rise, 4),
                    "run_ms": round(run, 1),
                    "t1_ms": round(t1_ms, 1), "t2_ms": round(t2_ms, 1)}
        except Exception as e:
            return {"error": str(e)}

    def measure_area(self, lead: str, start_ms: float, end_ms: float) -> dict:
        try:
            sig, t_ms = self._sig_window(lead, start_ms, end_ms)
            if len(sig) == 0:
                return {"error": "Empty window"}
            baseline = self._baseline(lead)
            dt = 1.0 / self.fid.fs * 1000  # ms per sample
            diff = sig.astype(float) - baseline
            area_total = float(np.trapz(diff, dx=dt))
            above = float(np.trapz(np.maximum(diff, 0), dx=dt))
            below = float(np.trapz(np.minimum(diff, 0), dx=dt))
            return {"area_mv_ms": round(area_total, 4),
                    "above_baseline_mv_ms": round(above, 4),
                    "below_baseline_mv_ms": round(below, 4),
                    "duration_ms": round(end_ms - start_ms, 1)}
        except Exception as e:
            return {"error": str(e)}

    def find_inflection_point(self, lead: str, start_ms: float, end_ms: float) -> dict:
        try:
            from scipy.ndimage import uniform_filter1d
            sig, t_ms = self._sig_window(lead, start_ms, end_ms)
            if len(sig) < 5:
                return {"error": "Window too short for derivative"}
            smooth = uniform_filter1d(sig.astype(float), size=5)
            d1 = np.gradient(smooth)
            d2 = np.gradient(d1)
            # Find zero-crossings of d2 (sign changes)
            signs = np.sign(d2)
            crossings = np.where(np.diff(signs) != 0)[0]
            if len(crossings) == 0:
                return {"time_ms": None, "note": "No inflection found in window"}
            # Return the inflection with largest |d1| (steepest slope change)
            best = crossings[np.argmax(np.abs(d1[crossings]))]
            return {"time_ms": round(float(t_ms[best]), 1),
                    "amplitude_mv": round(float(sig[best]), 4),
                    "all_inflections_ms": [round(float(t_ms[c]), 1) for c in crossings]}
        except Exception as e:
            return {"error": str(e)}

    def measure_amplitude(self, lead: str, time_ms: float) -> dict:
        try:
            sig, t_ms = self._sig_window(lead, time_ms - 2, time_ms + 2)
            if len(sig) == 0:
                return {"error": "Empty"}
            baseline = self._baseline(lead)
            amp = float(sig[len(sig) // 2])
            return {"time_ms": time_ms, "amplitude_mv": round(amp, 4),
                    "vs_baseline_mv": round(amp - baseline, 4)}
        except Exception as e:
            return {"error": str(e)}

    def get_baseline_level(self, lead: str) -> dict:
        try:
            baseline = self._baseline(lead)
            fpt = self.fid.fpt[lead] if lead in self.fid.fpt else list(self.fid.fpt.values())[0]
            qrson = int(fpt[self.beat_idx, COL_QRSON])
            sig_all = self._lead_sig(lead)
            safe = self.fid.safe_window_start_sample
            end = safe + qrson
            start = max(0, end - int(0.03 * self.fid.fs))
            noise = float(np.std(sig_all[start:end]))
            return {"baseline_mv": round(baseline, 4), "noise_std_mv": round(noise, 4),
                    "threshold_mv": round(2.5 * max(noise, 0.008), 4)}
        except Exception as e:
            return {"error": str(e)}

    def zoom_lead(self, lead: str, start_ms: float, end_ms: float) -> tuple[dict, Optional[bytes]]:
        """Zoomed strip of ONE lead — used for uncertain cases."""
        try:
            import io
            import matplotlib
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt
            import matplotlib.ticker as ticker

            sig, t_ms = self._sig_window(lead, start_ms, end_ms)
            if len(sig) == 0:
                return {"error": "Empty"}, None

            baseline = self._baseline(lead)
            fpt = self.fid.fpt[lead] if lead in self.fid.fpt else list(self.fid.fpt.values())[0]
            lead_row = fpt[self.beat_idx]

            fig, ax = plt.subplots(figsize=(max(6.0, (end_ms - start_ms) / 40 * 2.5), 3.5))
            ax.plot(t_ms, sig, "k-", linewidth=1.5)
            ax.axhline(baseline, color="#27AE60", linewidth=0.7, linestyle="--", alpha=0.6)

            for pt in _PASS_POINTS[self.segment]:
                col = _POINT_TO_COL[pt]
                v = int(lead_row[col])
                if v < 0:
                    continue
                t = self._s2ms(lead, v)
                if t is None or not (start_ms - 5 <= t <= end_ms + 5):
                    continue
                color = _MARKER_COLORS.get(pt, "gray")
                ax.axvline(t, color=color, linewidth=1.2, linestyle="--", alpha=0.9)
                sig_idx = np.argmin(np.abs(t_ms - t))
                y = float(sig[sig_idx]) if sig_idx < len(sig) else baseline
                ax.annotate(f"{pt}\n{t:.0f}ms", xy=(t, y), xytext=(0, 12),
                            textcoords="offset points", fontsize=7, ha="center",
                            color=color, fontweight="bold",
                            arrowprops=dict(arrowstyle="-", color=color, lw=0.6))

            ax.xaxis.set_minor_locator(ticker.MultipleLocator(10))
            ax.xaxis.set_major_locator(ticker.MultipleLocator(50))
            ax.yaxis.set_minor_locator(ticker.MultipleLocator(0.1))
            ax.grid(which="minor", color="#F0F0F0", linewidth=0.4)
            ax.grid(which="major", color="#D0D0D0", linewidth=0.7)
            ax.set_title(f"ZOOM — Lead {lead} | {start_ms:.0f}–{end_ms:.0f}ms", fontsize=9)
            ax.set_xlabel("ms", fontsize=8)
            ax.set_ylabel("mV", fontsize=8)
            sig_range = float(np.max(sig) - np.min(sig))
            margin = max(0.15, sig_range * 0.2)
            ax.set_ylim(float(np.min(sig)) - margin, float(np.max(sig)) + margin)
            ax.set_xlim(start_ms, end_ms)

            plt.tight_layout()
            buf = io.BytesIO()
            plt.savefig(buf, format="png", dpi=200, bbox_inches="tight", facecolor="white")
            plt.close(fig)
            buf.seek(0)
            return {"lead": lead, "status": "rendered"}, buf.read()
        except Exception as e:
            return {"error": str(e)}, None

    def set_fiducial(self, lead: str, point: str, time_ms: float) -> dict:
        if lead not in self.fid.fpt:
            return {"ok": False, "error": f"Lead '{lead}' not found"}
        if point not in _POINT_TO_COL:
            return {"ok": False, "error": f"Unknown point '{point}'"}
        col = _POINT_TO_COL[point]
        fpt = self.fid.fpt[lead]
        old_s = int(fpt[self.beat_idx, col])
        old_ms = self._s2ms(lead, old_s)
        fpt[self.beat_idx, col] = np.int32(self._ms2s(lead, time_ms))
        ok, err = self._validate(lead)
        if not ok:
            fpt[self.beat_idx, col] = np.int32(old_s)
            return {"ok": False, "error": err}
        self.changes.append({"lead": lead, "point": point, "label": _POINT_LABELS[point],
                             "old_ms": round(old_ms, 1) if old_ms is not None else None,
                             "new_ms": round(time_ms, 1)})
        return {"ok": True, "lead": lead, "point": point,
                "old_ms": round(old_ms, 1) if old_ms is not None else None,
                "new_ms": round(time_ms, 1)}

    def set_fiducial_all_leads(self, point: str, time_ms: float) -> dict:
        if point == "r":
            return {"ok": False, "error": "R-peak must vary per lead — use set_fiducial per lead"}
        results = {}
        for lead in [l for l in LEAD_ORDER if l in self.fid.fpt]:
            results[lead] = self.set_fiducial(lead, point, time_ms)
        ok_count = sum(1 for r in results.values() if r.get("ok"))
        return {"point": point, "time_ms": time_ms,
                "applied_to": ok_count, "results": results}

    def mark_absent(self, lead: str, point: str) -> dict:
        if point not in _OPTIONAL_POINTS:
            return {"ok": False, "error": f"'{point}' cannot be absent"}
        if lead not in self.fid.fpt:
            return {"ok": False, "error": f"Lead '{lead}' not found"}
        col = _POINT_TO_COL[point]
        old_ms = self._s2ms(lead, int(self.fid.fpt[lead][self.beat_idx, col]))
        self.fid.fpt[lead][self.beat_idx, col] = np.int32(-1)
        self.changes.append({"lead": lead, "point": point, "label": _POINT_LABELS[point],
                             "old_ms": round(old_ms, 1) if old_ms is not None else None,
                             "new_ms": None, "action": "absent"})
        return {"ok": True, "lead": lead, "point": point, "result": "absent"}

    def mark_absent_all_leads(self, point: str) -> dict:
        if point not in _OPTIONAL_POINTS:
            return {"ok": False, "error": f"'{point}' cannot be absent"}
        results = {}
        for lead in [l for l in LEAD_ORDER if l in self.fid.fpt]:
            results[lead] = self.mark_absent(lead, point)
        return {"point": point, "marked_absent_in": [l for l, r in results.items() if r.get("ok")]}

    def accept_changes(self) -> dict:
        self.accepted = True
        return {"status": "accepted", "pass": self.segment,
                "total_changes": len(self.changes),
                "summary": [f"{c['lead']} {c['label']}: "
                            f"{c.get('old_ms','?')} → {c.get('new_ms','absent')}"
                            for c in self.changes]}

    def dispatch(self, name: str, args: dict) -> tuple[dict, Optional[bytes]]:
        m = {
            "get_all_fiducial_positions": lambda: (self.get_all_fiducial_positions(), None),
            "get_cross_lead_consistency": lambda: (self.get_cross_lead_consistency(**args), None),
            # Math/ruler tools
            "ruler":                      lambda: (self.ruler(**args), None),
            "measure_slope":              lambda: (self.measure_slope(**args), None),
            "measure_area":               lambda: (self.measure_area(**args), None),
            "find_inflection_point":      lambda: (self.find_inflection_point(**args), None),
            # Signal analysis
            "find_local_max":             lambda: (self.find_local_max(**args), None),
            "find_local_min":             lambda: (self.find_local_min(**args), None),
            "find_onset":                 lambda: (self.find_onset(**args), None),
            "find_offset":                lambda: (self.find_offset(**args), None),
            "measure_amplitude":          lambda: (self.measure_amplitude(**args), None),
            "get_baseline_level":         lambda: (self.get_baseline_level(**args), None),
            "zoom_lead":                  lambda: self.zoom_lead(**args),
            # Write
            "set_fiducial":               lambda: (self.set_fiducial(**args), None),
            "set_fiducial_all_leads":     lambda: (self.set_fiducial_all_leads(**args), None),
            "mark_absent":                lambda: (self.mark_absent(**args), None),
            "mark_absent_all_leads":      lambda: (self.mark_absent_all_leads(**args), None),
            "accept_changes":             lambda: (self.accept_changes(), None),
        }
        # Gemma sometimes copies trailing () from the prompt — strip it
        name = name.rstrip("()")
        fn = m.get(name)
        if fn is None:
            return {"error": f"Unknown tool: '{name}'"}, None
        try:
            return fn()
        except TypeError as e:
            return {"error": f"Bad args for {name}: {e}"}, None


# ── JSON parser ────────────────────────────────────────────────────────────────

def _parse_tool_calls(text: str) -> list[dict]:
    tick3 = "`" * 3
    blocks = re.findall(tick3 + r"json\s*([\s\S]*?)" + tick3, text, re.IGNORECASE)
    if not blocks:
        blocks = re.findall(r"(\[\s*\{[\s\S]*?\}\s*\])", text)
    for block in blocks:
        try:
            parsed = json.loads(block.strip())
            if isinstance(parsed, list) and all(isinstance(t, dict) and "tool" in t for t in parsed):
                return parsed
        except json.JSONDecodeError:
            continue
    return []


def _img_block(png: bytes) -> dict:
    b64 = base64.b64encode(png).decode()
    return {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}}


# ── Morphology system prompts ─────────────────────────────────────────────────

_P_MORPH_SYSTEM = """You are a clinical ECG cardiologist performing comprehensive P-wave morphology analysis.

## P-wave morphology — what to assess per lead
- Shape: upright / inverted / biphasic (positive-then-negative or negative-then-positive) / flat / absent
- Amplitude in mV
- Duration in ms
- Symmetry: symmetric vs notched (bifid)

## Clinical patterns to identify
- NORMAL: upright in I, II, aVF, V4-V6; inverted in aVR; variable in III, aVL, V1-V3
- LEFT ATRIAL ENLARGEMENT (LAE / P-mitrale): notched bifid P in I/II (duration >120ms), deep negative terminal in V1
- RIGHT ATRIAL ENLARGEMENT (RAE / P-pulmonale): peaked P in II/III/aVF (>2.5mm), tall P in V1/V2
- ATRIAL FIBRILLATION: absent P-waves, irregular baseline, no organized atrial activity
- WANDERING PACEMAKER: varying P-wave morphology and PR interval beat-to-beat
- ECTOPIC ATRIAL RHYTHM: inverted P in II/III/aVF (retrograde conduction)
- FIRST-DEGREE AV BLOCK (context): PR interval >200ms (note for RAG)

## Output
Respond with a JSON object only:
```json
{
  "segment": "p",
  "per_lead": {
    "LEAD_NAME": {"shape": "...", "amplitude_mv": 0.0, "duration_ms": 0, "flag": "or null"}
  },
  "global_findings": ["finding 1", "finding 2"],
  "rhythm_implication": "sinus / afib / ectopic / etc",
  "confidence": "high / medium / low"
}
```
"""

_QRS_MORPH_SYSTEM = """You are a clinical ECG cardiologist performing comprehensive QRS morphology analysis.

## DUAL-SOURCE REASONING: IMAGE + PIPELINE QRS PATTERNS
You receive two sources of evidence — use BOTH:

1. **Visual image** (red signal = target QRS segment): Assess QRS width, notching, dominant deflection direction, presence of initial Q wave.
2. **Pipeline QRS pattern per lead** (in measurements block): Computed zero-crossing analysis — more precise than visual estimates.

## Pipeline QRS Pattern Interpretation Guide
- `QS` = no R wave, entirely negative → **pathological Q-wave in this lead** (prior/ongoing MI)
  - QS in II/III/aVF → **inferior MI**
  - QS in V1-V4 → **anterior MI**
- `rS` = small r followed by deep S → typical LBBB-V1, or posterior MI (V1)
- `RSR'` = M-shape → **RBBB** in V1/V2 pattern
- `qRs` = small q, tall R, small s → **normal** (e.g., V5/V6 in normal QRS)
- `fragmented` = multiple notches/deflections → **fragmented QRS** (prior MI scar, CMP)
- `Rs` = R then S dominant negative → normal or LBBB-lateral
- `monophasic_R` = pure R, no S, no Q → LBBB in V5/V6

## Clinical QRS Patterns to Identify
- **LBBB**: QRS ≥120ms, QS or rS in V1/V2, monophasic R in V5/V6, no septal q in I/V5/V6
- **RBBB**: QRS ≥120ms, RSR' in V1/V2, wide slurred S in I/V5/V6
- **LBBB + STEMI (Sgarbossa)**: If concordant ST mentioned in measurements → report separately
- **LVH**: High voltage — R in aVL >11mm, Sokolow-Lyon (R V5/V6 + S V1) >35mm
- **PATHOLOGICAL Q-WAVE**: QS or Q ≥40ms OR ≥25% of R height
  - QS in III/aVF → **inferior MI** (prior or acute)
  - QS in V1-V4 → **anterior MI**
  - QS in I/aVL/V5-V6 → **lateral MI**
- **DELTA WAVE (WPW)**: slurred upstroke (preexcitation) at QRS onset
- **R-WAVE PROGRESSION**: R should increase V1→V5; if R still small in V3-V4 → poor progression = anterior ischemia
- **AXIS**: I positive + aVF negative = left axis deviation; I negative + aVF positive = right axis

## Output
Respond with a JSON object only:
```json
{
  "segment": "qrs",
  "per_lead": {
    "LEAD_NAME": {"dominant": "positive/negative/biphasic", "r_mv": 0.0, "s_mv": 0.0, "q_mv": 0.0, "flag": "or null e.g. 'QS=inferior MI'"}
  },
  "global_findings": ["finding 1 with lead names", "finding 2"],
  "qrs_axis": "normal / left / right / extreme",
  "bbb": "none / LBBB / RBBB / IVCD",
  "confidence": "high / medium / low"
}
```
"""

_T_MORPH_SYSTEM = """You are a clinical ECG cardiologist performing comprehensive T-wave and ST-segment morphology analysis.

## DUAL-SOURCE REASONING: IMAGE + SHAPE MEASUREMENTS
You receive two sources of evidence — use BOTH:

1. **Visual image** (red signal = target T/ST segment): Assess J-point position relative to the flat isoelectric baseline (TP segment before P-wave). Even subtle 0.5–1mm elevation visible above the baseline grid line is clinically significant.

2. **Pipeline shape measurements** (in the measurements block): These include ST CURVATURE and T-wave SYMMETRY which are computed from signal shape, not absolute amplitude — they are WANDER-RESISTANT and reliable even when amplitude measurements appear small.

## Shape-Based Diagnostic Rules (APPLY THESE FIRST)

### ST Curvature → Territory
- `convex` curvature in II + III + aVF → **INFERIOR STEMI** (even if amplitude <0.1 mV)
- `convex` curvature in V1 + V2 + V3 → **ANTERIOR STEMI** (J-point domed = coved pattern)
- `concave` curvature diffusely → **Pericarditis** (smiley-face ST)
- `convex` in V1/V2 alone + T-inversion → **Brugada Type 1**

### T-Wave Symmetry → Pattern
- Symmetry >0.85 in II/III/aVF → **hyperacute T** or **Wellens** (depends on direction)
- Symmetry <0.5 in II/III/aVF → **asymmetric** = LVH strain, normal variant, NOT ischemia
- Biphasic/notched T-wave detailed morphology → Wellens Type A, LQT2

### QS Pattern (from QRS pass) → Prior MI
If the QRS measurements block mentions QS in III/aVF or II/III/aVF → **inferior MI (established or acute)** — this combined with convex curvature = ongoing STEMI.

## Reciprocal Change Rule
ALWAYS check opposite territory when you find any ST elevation:
- Inferior elevation (II/III/aVF) → expect depression in I, aVL (reciprocal)
- Anterior elevation (V1-V4) → expect depression in II, III, aVF
- If elevation and depression match in opposite territories → CONFIRMS ischemia diagnosis

## T-wave and ST — what to assess per lead
- ST deviation from baseline in mV (elevation = positive, depression = negative)
  - Use visual image for direction and rough magnitude
  - ST curvature confirms shape
- ST shape: flat / upsloping / downsloping / saddle-back / convex-upward (domed)
- T-wave direction: upright / inverted / flat / biphasic
- T-wave amplitude and symmetry

## Clinical patterns
- INFERIOR STEMI: convex ST + elevation in II/III/aVF + reciprocal depression I/aVL
- ANTERIOR STEMI: ST elevation V1-V4, tall T-waves
- HYPERACUTE T: tall symmetric T-waves (symmetry>0.85), preceding ST elevation
- NSTEMI: horizontal/downsloping depression ≥0.5mm ≥2 contiguous leads
- WELLENS: symmetric deep T-inversion V2-V3 (Type B) or biphasic T V2-V3 (Type A)
- DE WINTER: upsloping ST depression + tall peaked T in V1-V4 (STEMI equivalent)

## Output
Respond with a JSON object only — use EXACT lead names from the image:
```json
{
  "segment": "t",
  "per_lead": {
    "LEAD_NAME": {"t_direction": "upright/inverted/flat/biphasic", "t_amplitude_mv": 0.0, "st_deviation_mv": 0.0, "st_shape": "flat/upsloping/downsloping/convex-upward/saddle-back", "flag": "null or clinical note"}
  },
  "global_findings": ["specific finding with lead names e.g. 'ST elevation in II/III/aVF with convex curvature — inferior STEMI pattern'"],
  "ischemia_territory": "none / inferior / anterior / lateral / posterior (choose ONE primary territory; if both inferior and anterior are involved, choose whichever has QS waves or the clearer convex pattern)",
  "confidence": "high / medium / low"
}
```
"""

_MORPH_PROMPTS = {"p": _P_MORPH_SYSTEM, "qrs": _QRS_MORPH_SYSTEM, "t": _T_MORPH_SYSTEM}


def _build_measurements_text(features, segment: str) -> str:
    """Build a concise measurements text block for the MorphologyAgent.

    Includes both scalar intervals and per-lead shape features (curvature,
    symmetry, QRS pattern) which are wander-resistant and clinically actionable
    even when absolute amplitude measurements are small.
    """
    lines = [f"## Pipeline Measurements — {segment.upper()} segment"]
    try:
        if segment == "p":
            lines += [
                f"- HR: {features.heart_rate_ventricular_bpm:.0f} bpm",
                f"- PR interval: {features.pr_interval_ms} ms",
                f"- P duration: {getattr(features, 'p_duration_ms', 'N/A')} ms",
                f"- P axis: {getattr(features, 'p_axis_deg', 'N/A')}°",
            ]
            pr_dep = getattr(features, "pr_depression_mv", None)
            if pr_dep and isinstance(pr_dep, dict):
                sig_pr = {l: v for l, v in pr_dep.items() if v is not None and v >= 0.05}
                if sig_pr:
                    lines.append(f"- PR depression (pericarditis sign): {sig_pr}")

        elif segment == "qrs":
            lines += [
                f"- QRS duration: {features.qrs_duration_global_ms} ms",
                f"- QRS axis: {features.qrs_axis_deg:.0f}°",
                f"- LBBB: {features.lbbb} | RBBB: {features.rbbb} | WPW: {features.wpw_pattern}",
            ]
            # QRS pattern per lead (QS, rS, RSR', etc.) — key for BBB and Q-wave detection
            qrs_pat = getattr(features, "qrs_pattern", None)
            if qrs_pat and isinstance(qrs_pat, dict):
                lines.append("- QRS pattern per lead (QS=pathological Q, RSR'=RBBB, rS=LBBB-V1):")
                for lead, pat in qrs_pat.items():
                    lines.append(f"    {lead}: {pat}")
            # Concordance — only flag when relevant
            concord = getattr(features, "concordance_analysis", None)
            if concord and isinstance(concord, dict):
                concordant = [l for l, v in concord.items() if v == "concordant"]
                if concordant:
                    lines.append(f"- CONCORDANT ST in: {', '.join(concordant)} (Sgarbossa criterion 1/2)")
            # R-wave amplitude per lead for LVH/progression
            r_amp = getattr(features, "r_amplitude_mv", None)
            if r_amp and isinstance(r_amp, dict):
                lines.append("- R amplitude per lead (mV):")
                for lead, val in r_amp.items():
                    if val is not None:
                        lines.append(f"    {lead}: {val:.3f}")
            # Q amplitude
            q_amp = getattr(features, "q_amplitude_mv", None)
            q_dur = getattr(features, "q_duration_ms", None)
            if q_amp and q_dur:
                path_q = {l: f"{q_amp.get(l, 0):.3f}mV/{q_dur.get(l, 0):.0f}ms"
                          for l in q_amp if q_amp.get(l, 0) is not None and q_amp.get(l, 0) < -0.05}
                if path_q:
                    lines.append(f"- Significant Q waves: {path_q}")

        elif segment == "t":
            lines += [
                f"- QTc (Bazett): {features.qtc_bazett_ms:.0f} ms",
                f"- T axis: {getattr(features, 't_axis_deg', 'N/A')}°",
            ]
            # T amplitude per lead
            t_amp = getattr(features, "t_amplitude_mv", None)
            if t_amp and isinstance(t_amp, dict):
                lines.append("- T amplitude per lead (mV) — values from pipeline:")
                for lead, val in t_amp.items():
                    if val is not None:
                        lines.append(f"    {lead}: {val:+.3f}")
            # ST curvature — shape-based, wander-resistant (MOST IMPORTANT for STEMI)
            st_curv = getattr(features, "st_curvature", None)
            if st_curv and isinstance(st_curv, dict):
                lines.append("- ST curvature per lead (shape-based, wander-resistant):")
                lines.append("  CLINICAL KEY: convex=STEMI/ischemia, concave=pericarditis/benign, linear=nonspecific")
                for lead, curv in st_curv.items():
                    lines.append(f"    {lead}: {curv}")
            # T-wave symmetry index
            t_sym = getattr(features, "t_symmetry_index", None)
            if t_sym and isinstance(t_sym, dict):
                lines.append("- T-wave symmetry index (1.0=symmetric, <0.7=asymmetric):")
                lines.append("  CLINICAL KEY: symmetric (>0.85) in II/III/aVF = hyperacute/ischemic T")
                for lead, val in t_sym.items():
                    if val is not None:
                        lines.append(f"    {lead}: {val:.2f}")
            # T detailed morphology
            t_morph = getattr(features, "t_detailed_morphology", None)
            if t_morph and isinstance(t_morph, dict):
                lines.append("- T-wave detailed morphology per lead:")
                for lead, m in t_morph.items():
                    lines.append(f"    {lead}: {m}")
            # ST deviation (amplitude-based, may be near-zero due to subtle changes or wander)
            st_elev = getattr(features, "st_elevation_mv", None)
            st_dep = getattr(features, "st_depression_mv", None)
            any_st = False
            st_lines = []
            if st_elev and isinstance(st_elev, dict):
                for lead, val in st_elev.items():
                    if val and val >= 0.05:
                        st_lines.append(f"    {lead}: +{val:.3f} mV (elevation)")
                        any_st = True
            if st_dep and isinstance(st_dep, dict):
                for lead, val in st_dep.items():
                    if val and val >= 0.05:
                        st_lines.append(f"    {lead}: -{val:.3f} mV (depression)")
                        any_st = True
            if any_st:
                lines.append("- Pipeline ST amplitudes ≥0.5mm (NOTE: may be underestimated due to baseline wander):")
                lines.extend(st_lines)
            else:
                lines.append("- Pipeline ST amplitudes: all <0.5mm (subtle — rely on ST CURVATURE above for shape diagnosis)")
            # QRS pattern cross-reference — critical for ischemia territory decision
            qrs_pat = getattr(features, "qrs_pattern", None)
            if qrs_pat and isinstance(qrs_pat, dict):
                inf_qs = [l for l in ["II", "III", "aVF"] if qrs_pat.get(l) == "QS"]
                ant_qs = [l for l in ["V1", "V2", "V3", "V4"] if qrs_pat.get(l) == "QS"]
                if inf_qs:
                    lines.append(f"- QRS CROSS-REFERENCE: QS pattern in {', '.join(inf_qs)} → prior/ongoing INFERIOR MI")
                    lines.append("  When ST curvature is also convex in II/aVF → INFERIOR STEMI (even if V1/V2 also elevated due to RV involvement)")
                if ant_qs:
                    lines.append(f"- QRS CROSS-REFERENCE: QS pattern in {', '.join(ant_qs)} → prior/ongoing ANTERIOR MI")
    except Exception:
        pass
    return "\n".join(lines)


# ── FiducialAgent (LangGraph loop) ────────────────────────────────────────────

_FIDUCIAL_PROMPTS = {"p": _P_SYSTEM, "qrs": _QRS_SYSTEM, "t": _T_SYSTEM}


def _run_fiducial_agent(
    record, fid: FiducialTable, features, beat_idx: int,
    segment: str, png: bytes, model: str, stream: bool = False,
    logger: Optional["WorkflowLogger"] = None,
) -> list[dict]:
    """
    LangGraph tool-calling loop for one segment.
    Receives the red/black focused strip, uses math tools to correct fiducial positions.
    Mutates fid in place. Returns change log.
    """
    executor = ToolExecutor(record, fid, features, beat_idx, segment)
    llm = ChatOllama(model=model, temperature=0.1)
    if logger:
        logger.log(beat_idx, segment, "fiducial", "start", {"model": model})

    # Build approximate time ranges from reference lead for coordinate orientation
    ref_lead = "II" if "II" in fid.fpt else list(fid.fpt.keys())[0]
    ref_row = fid.fpt[ref_lead][beat_idx]
    _fs = fid.fs
    _ws = max(0, int(ref_row[COL_R]) - int(0.4 * _fs))

    def _approx_ms(col):
        v = int(ref_row[col])
        return round((v - _ws) / _fs * 1000) if v >= 0 else None

    r_approx    = _approx_ms(COL_R)     or 400
    qrson_approx = _approx_ms(COL_QRSON) or (r_approx - 60)
    qrsoff_approx = _approx_ms(COL_QRSOFF) or (r_approx + 60)
    pon_approx   = _approx_ms(COL_PON)   or (qrson_approx - 130)
    poff_approx  = _approx_ms(COL_POFF)  or (qrson_approx - 20)
    toff_approx  = _approx_ms(COL_TOFF)  or (qrsoff_approx + 240)
    ton_approx   = _approx_ms(COL_TON)   or (qrsoff_approx + 40)

    _coord_hint = {
        "p":   f"P-wave region: ~{pon_approx}–{poff_approx}ms. R-peak at ~{r_approx}ms.",
        "qrs": f"QRS region: ~{qrson_approx}–{qrsoff_approx}ms. R-peak at ~{r_approx}ms.",
        "t":   f"T-wave region: ~{ton_approx}–{toff_approx}ms. QRS-offset at ~{qrsoff_approx}ms.",
    }[segment]

    system_prompt = _FIDUCIAL_PROMPTS[segment]
    context = (
        f"\nBeat {beat_idx + 1} | Leads: {[l for l in LEAD_ORDER if l in fid.fpt]}\n"
        f"Confidence: {json.dumps({k: round(v, 2) for k, v in (fid.fiducial_confidence or {}).items()}, indent=0)}\n"
        f"COORDINATE SYSTEM: All times are ms from beat window start. {_coord_hint}\n"
        f"X-axis range in image: read the tick labels to get exact ms values.\n"
        f"Correct ONLY {_PASS_POINTS[segment]} markers. The RED signal is your target."
    )
    initial_content = [
        {"type": "text", "text": system_prompt + context},
        {"type": "text", "text": f"--- ALL 12 LEADS — {segment.upper()} FOCUS (red=target, black=context) ---"},
        _img_block(png),
    ]

    def agent_node(state: CorrectionState) -> dict:
        resp = llm.invoke(state["messages"])
        calls = _parse_tool_calls(resp.content)
        print(f"  [fiducial:{segment}] agent → {len(calls)} tool call(s)")
        return {"messages": [resp], "iteration": state["iteration"] + 1}

    def tools_node(state: CorrectionState) -> dict:
        last = state["messages"][-1]
        calls = _parse_tool_calls(last.content)
        result_lines, new_images = [], []

        for tc in calls:
            name = tc.get("tool", "")
            args = tc.get("args", {})
            print(f"  [fiducial:{segment}] tool: {name}({args})")
            res, img = executor.dispatch(name, args)
            result_lines.append(f"### {name}\n{json.dumps(res, indent=2)}")
            if img:
                new_images.append((args.get("lead", name), img))
            if logger:
                logger.log(beat_idx, segment, "fiducial", "tool_call",
                           {"tool": name, "args": args, "result": res})

        text = "## Tool Results\n\n" + "\n\n".join(result_lines)
        if new_images:
            content = [{"type": "text", "text": text}]
            for label, img in new_images:
                content.extend([{"type": "text", "text": f"--- zoom: {label} ---"}, _img_block(img)])
            msg = HumanMessage(content=content)
        else:
            msg = HumanMessage(content=text)

        return {"messages": [msg], "accepted": executor.accepted}

    def route(state: CorrectionState) -> str:
        if state["accepted"] or state["iteration"] >= 8:
            return END
        last = state["messages"][-1]
        if isinstance(last, AIMessage):
            return "tools" if _parse_tool_calls(last.content) else END
        return "agent"

    g = StateGraph(CorrectionState)
    g.add_node("agent", agent_node)
    g.add_node("tools", tools_node)
    g.set_entry_point("agent")
    g.add_conditional_edges("agent", route, {"tools": "tools", END: END})
    g.add_conditional_edges("tools", route, {"agent": "agent", END: END})
    graph = g.compile()

    init: CorrectionState = {
        "messages": [HumanMessage(content=initial_content)],
        "accepted": False,
        "iteration": 0,
    }

    if stream:
        for event in graph.stream(init):
            pass
    else:
        graph.invoke(init)

    print(f"  [fiducial:{segment}] done — {len(executor.changes)} corrections")
    if logger:
        logger.log(beat_idx, segment, "fiducial", "complete", {
            "n_corrections": len(executor.changes),
            "changes": executor.changes,
        })
    return executor.changes


# ── Workflow logger ────────────────────────────────────────────────────────────

class WorkflowLogger:
    """
    Writes a live JSONL log of every step taken by both agents.
    Each line is a JSON object: {ts, beat, segment, agent, event, data}.
    """

    def __init__(self, out_path: Optional[str] = None):
        self.out_path = out_path
        self._fh = None
        if out_path:
            self._fh = open(out_path, "w")

    def log(self, beat_idx: int, segment: str, agent: str, event: str, data: Any = None):
        import time as _time
        entry = {
            "ts": round(_time.time(), 3),
            "beat": beat_idx + 1,
            "segment": segment,
            "agent": agent,
            "event": event,
        }
        if data is not None:
            entry["data"] = data
        line = json.dumps(entry, default=str)
        print(f"  LOG [{entry['beat']}:{segment}:{agent}] {event}" +
              (f" — {data}" if data else ""))
        if self._fh:
            self._fh.write(line + "\n")
            self._fh.flush()

    def close(self):
        if self._fh:
            self._fh.close()
            self._fh = None

    def __del__(self):
        self.close()


_NULL_LOGGER = None  # set in run_fiducial_correction


def _get_logger() -> Optional["WorkflowLogger"]:
    return _NULL_LOGGER


# ── MorphologyAgent measurement tools ─────────────────────────────────────────

_MORPH_TOOL_FORMAT = """
## Measurement Tools
Call tools by outputting a ```json array. ALWAYS include "args" with the exact keys shown below.

Example call structure:
```json
[
  {"tool": "measure_st_deviation", "args": {"lead": "II"}},
  {"tool": "measure_st_deviation", "args": {"lead": "III"}},
  {"tool": "measure_height_from_baseline", "args": {"lead": "II", "time_ms": 640}},
  {"tool": "measure_t_symmetry", "args": {"lead": "II"}}
]
```

Tool reference (copy args keys exactly):
- "measure_height_from_baseline"  →  args: {"lead": "LEAD", "time_ms": NUMBER}
- "measure_st_deviation"          →  args: {"lead": "LEAD"}
- "measure_segment_slope"         →  args: {"lead": "LEAD", "start_ms": NUMBER, "end_ms": NUMBER}
- "measure_t_symmetry"            →  args: {"lead": "LEAD"}

After receiving tool results, output your final JSON report.
"""


class MorphologyToolExecutor:
    """Lightweight measurement-only tool executor for the MorphologyAgent."""

    def __init__(self, record, fid: FiducialTable, beat_idx: int):
        self.record = record
        self.fid = fid
        self.beat_idx = beat_idx

    def _lead_sig(self, lead: str) -> np.ndarray:
        li = self.record.lead_names.index(lead)
        return self.record.morphology_signal[li].astype(float) / 1000.0

    def _win_start(self, lead: str) -> int:
        fpt = self.fid.fpt[lead] if lead in self.fid.fpt else list(self.fid.fpt.values())[0]
        r = int(fpt[self.beat_idx, COL_R])
        return max(0, r - int(0.4 * self.fid.fs))

    def _ms2idx(self, lead: str, ms: float) -> int:
        return self._win_start(lead) + round(ms * self.fid.fs / 1000)

    def _baseline(self, lead: str) -> float:
        fpt = self.fid.fpt[lead] if lead in self.fid.fpt else list(self.fid.fpt.values())[0]
        qrson = int(fpt[self.beat_idx, COL_QRSON])
        if qrson < 0:
            return 0.0
        sig_all = self._lead_sig(lead)
        safe = self.fid.safe_window_start_sample
        end = safe + qrson
        return float(np.median(sig_all[max(0, end - int(0.03 * self.fid.fs)):end]))

    def _sig_at(self, lead: str, time_ms: float) -> float:
        sig_all = self._lead_sig(lead)
        safe = self.fid.safe_window_start_sample
        idx = safe + self._ms2idx(lead, time_ms)
        idx = max(0, min(len(sig_all) - 1, idx))
        return float(sig_all[idx])

    def measure_height_from_baseline(self, lead: str, time_ms: float) -> dict:
        try:
            bl = self._baseline(lead)
            amp = self._sig_at(lead, time_ms)
            return {"lead": lead, "time_ms": time_ms,
                    "amplitude_mv": round(amp, 4),
                    "height_from_baseline_mv": round(amp - bl, 4),
                    "baseline_mv": round(bl, 4)}
        except Exception as e:
            return {"error": str(e)}

    def measure_st_deviation(self, lead: str) -> dict:
        try:
            fpt = self.fid.fpt[lead] if lead in self.fid.fpt else list(self.fid.fpt.values())[0]
            row = fpt[self.beat_idx]
            qrsoff = int(row[COL_QRSOFF])
            if qrsoff < 0:
                return {"error": "qrsoff not detected"}
            j60_ms = (qrsoff - self._win_start(lead)) / self.fid.fs * 1000 + 60
            bl = self._baseline(lead)
            st = self._sig_at(lead, j60_ms)
            deviation = st - bl
            flag = ""
            if deviation >= 0.1:
                flag = f"ST ELEVATION {deviation*10:.1f}mm"
            elif deviation <= -0.05:
                flag = f"ST DEPRESSION {abs(deviation)*10:.1f}mm"
            return {"lead": lead, "j60_ms": round(j60_ms, 1),
                    "st_deviation_mv": round(deviation, 4),
                    "flag": flag or "isoelectric"}
        except Exception as e:
            return {"error": str(e)}

    def measure_segment_slope(self, lead: str, start_ms: float, end_ms: float) -> dict:
        try:
            sig_all = self._lead_sig(lead)
            safe = self.fid.safe_window_start_sample
            i0 = safe + self._ms2idx(lead, start_ms)
            i1 = safe + self._ms2idx(lead, end_ms)
            i0 = max(0, min(len(sig_all) - 1, i0))
            i1 = max(0, min(len(sig_all) - 1, i1))
            if i1 <= i0:
                return {"error": "Empty window"}
            seg = sig_all[i0:i1]
            t = np.arange(len(seg)) / self.fid.fs * 1000
            slope = float(np.polyfit(t, seg, 1)[0])
            shape = "upsloping" if slope > 0.002 else ("downsloping" if slope < -0.002 else "flat")
            return {"lead": lead, "slope_mv_per_ms": round(slope, 6), "shape": shape}
        except Exception as e:
            return {"error": str(e)}

    def measure_t_symmetry(self, lead: str) -> dict:
        try:
            fpt = self.fid.fpt[lead] if lead in self.fid.fpt else list(self.fid.fpt.values())[0]
            row = fpt[self.beat_idx]
            ton = int(row[COL_TON])
            tpeak = int(row[COL_TPEAK])
            toff = int(row[COL_TOFF])
            ws = self._win_start(lead)
            if ton < 0 or tpeak < 0 or toff < 0:
                return {"error": "T-wave markers not detected"}
            asc = (tpeak - ton) / self.fid.fs * 1000
            desc = (toff - tpeak) / self.fid.fs * 1000
            if desc < 1:
                return {"error": "Descending limb too short"}
            ratio = round(asc / desc, 3)
            symmetry = "symmetric" if 0.85 <= ratio <= 1.15 else ("asymmetric" if ratio < 0.85 else "wide-ascending")
            return {"lead": lead, "ascending_ms": round(asc, 1), "descending_ms": round(desc, 1),
                    "ratio": ratio, "symmetry": symmetry}
        except Exception as e:
            return {"error": str(e)}

    def dispatch(self, name: str, args: dict) -> dict:
        m = {
            "measure_height_from_baseline": self.measure_height_from_baseline,
            "measure_st_deviation":         self.measure_st_deviation,
            "measure_segment_slope":        self.measure_segment_slope,
            "measure_t_symmetry":           self.measure_t_symmetry,
        }
        name = name.rstrip("()")
        fn = m.get(name)
        if fn is None:
            return {"error": f"Unknown morphology tool: '{name}'"}
        try:
            return fn(**args)
        except TypeError as e:
            return {"error": f"Bad args for {name}: {e}"}


def _run_morphology_agent(
    record, fid: FiducialTable, features, beat_idx: int,
    segment: str, png: bytes, model: str,
    logger: Optional["WorkflowLogger"] = None,
) -> dict:
    """
    Two-turn morphology analysis:
      Turn 1: Gemma views image + measurements, calls measurement tools.
      Turn 2: Gemma receives tool results, outputs final JSON report.

    Returns structured JSON morphology report.
    """
    from openai import OpenAI
    client = OpenAI(base_url="http://localhost:11434/v1", api_key="local")

    measurements = _build_measurements_text(features, segment)
    system_prompt = _MORPH_PROMPTS[segment] + _MORPH_TOOL_FORMAT
    valid_leads = [l for l in LEAD_ORDER if l in fid.fpt]
    morph_exec = MorphologyToolExecutor(record, fid, beat_idx)

    # Build coordinate hint from fiducials
    _ref = "II" if "II" in fid.fpt else list(fid.fpt.keys())[0]
    _rrow = fid.fpt[_ref][beat_idx]
    _rws = max(0, int(_rrow[COL_R]) - int(0.4 * fid.fs))
    def _m(col):
        v = int(_rrow[col])
        return round((v - _rws) / fid.fs * 1000) if v >= 0 else None
    _qrsoff_m = _m(COL_QRSOFF) or 460
    _toff_m   = _m(COL_TOFF)   or (_qrsoff_m + 250)
    _ton_m    = _m(COL_TON)    or (_qrsoff_m + 40)
    _coord_hint_m = {
        "p":   f"P-wave RED region is approximately {_m(COL_PON) or 250}–{_m(COL_POFF) or 330}ms.",
        "qrs": f"QRS RED region is approximately {_m(COL_QRSON) or 340}–{_qrsoff_m}ms. R-peak ~{_m(COL_R) or 400}ms.",
        "t":   f"T-wave RED region is approximately {_ton_m}–{_toff_m}ms. Use these ranges in measurement tools.",
    }[segment]

    turn1_content = [
        {"type": "text", "text": system_prompt},
        {
            "type": "text",
            "text": (
                f"## Image — Beat {beat_idx + 1}\n"
                f"Leads in order (top to bottom): {valid_leads}\n"
                f"Only use these exact lead names in your JSON.\n"
                f"RED = {segment.upper()} segment. Black = context.\n"
                f"COORDINATES: {_coord_hint_m}\n"
                f"{measurements}\n\n"
                f"Step 1: Call measurement tools to get precise numbers. "
                f"Step 2: Output your final JSON report."
            ),
        },
        _img_block(png),
    ]

    if logger:
        logger.log(beat_idx, segment, "morphology", "start",
                   {"valid_leads": valid_leads, "model": model})

    messages = [{"role": "user", "content": turn1_content}]

    try:
        # Turn 1 — Gemma may call measurement tools
        resp1 = client.chat.completions.create(
            model=model, messages=messages, temperature=0.05, max_tokens=800,
        )
        raw1 = resp1.choices[0].message.content

        # Parse and execute any tool calls from turn 1
        tool_calls = _parse_tool_calls(raw1)
        tool_results = []
        for tc in tool_calls:
            name = tc.get("tool", "")
            args = tc.get("args", {})
            result = morph_exec.dispatch(name, args)
            tool_results.append({"tool": name, "args": args, "result": result})
            if logger:
                logger.log(beat_idx, segment, "morphology", "tool_call",
                           {"tool": name, "args": args, "result": result})

        # If tools were called, do turn 2 with results
        tick3 = "`" * 3
        if tool_calls:
            results_text = (
                "## Measurement Results\n" + json.dumps(tool_results, indent=2) +
                "\n\n"
                "STOP. Do NOT call any more tools. Do NOT output a JSON array.\n"
                "Based on the measurements above and the image, output your final clinical "
                f"JSON report for the {segment.upper()} segment as a single ```json {{...}}``` object "
                "(not a list). Include global_findings, per_lead, and confidence."
            )
            messages.append({"role": "assistant", "content": raw1})
            messages.append({"role": "user", "content": results_text})
            resp2 = client.chat.completions.create(
                model=model, messages=messages, temperature=0.05, max_tokens=2000,
            )
            raw_final = resp2.choices[0].message.content
        else:
            raw_final = raw1

        # Parse final JSON report — try multiple strategies
        blocks = re.findall(tick3 + r"json\s*([\s\S]*?)" + tick3, raw_final, re.IGNORECASE)
        blocks += re.findall(tick3 + r"\s*([\s\S]*?)" + tick3, raw_final)
        # Also find the largest {…} span
        brace_spans = re.findall(r"(\{[\s\S]*\})", raw_final)
        blocks += brace_spans
        report = None
        for b in blocks:
            b = b.strip()
            if not b:
                continue
            try:
                candidate = json.loads(b)
                # Accept any dict; skip lists (tool call arrays) and tool result dicts
                if isinstance(candidate, dict) and "tool" not in candidate:
                    report = candidate
                    break
            except json.JSONDecodeError:
                pass
        if report is None:
            # Last resort: try the raw final output as-is after trimming to first {...}
            m = re.search(r"\{", raw_final)
            if m:
                try:
                    report = json.loads(raw_final[m.start():])
                except json.JSONDecodeError:
                    pass
        if report is None:
            report = {"segment": segment, "raw_response": raw_final,
                      "global_findings": [], "confidence": "low"}

        # Normalize key variants Gemma commonly uses
        if "global_findings" not in report and "findings" in report:
            report["global_findings"] = report["findings"]
        if "ischemia_territory" not in report and "ischemia" in report:
            report["ischemia_territory"] = report["ischemia"]

        # Strip hallucinated lead names
        valid_set = set(valid_leads)
        per_lead = report.get("per_lead", {})
        report["per_lead"] = {k: v for k, v in per_lead.items() if k in valid_set}
        report["_tool_measurements"] = tool_results  # preserve for workflow log

        if logger:
            logger.log(beat_idx, segment, "morphology", "complete", {
                "findings": report.get("global_findings", []),
                "ischemia": report.get("ischemia_territory", ""),
                "confidence": report.get("confidence", ""),
                "n_tool_calls": len(tool_calls),
            })

        print(f"  [morphology:{segment}] findings: {report.get('global_findings', [])}")
        return report

    except Exception as e:
        if logger:
            logger.log(beat_idx, segment, "morphology", "error", {"error": str(e)})
        print(f"  [morphology:{segment}] ERROR: {e}")
        return {"segment": segment, "error": str(e), "global_findings": [], "confidence": "none"}


# ── Dual pass (FiducialAgent + MorphologyAgent for one segment) ───────────────

def run_dual_pass(
    record, fid: FiducialTable, features, beat_idx: int,
    segment: str, model: str, stream: bool = False,
    logger: Optional["WorkflowLogger"] = None,
) -> tuple[list[dict], dict]:
    """
    Run FiducialAgent then MorphologyAgent for one segment.

    FiducialAgent:   sees red/black strip, uses math tools, corrects marker positions (mutates fid).
    MorphologyAgent: sees corrected strip, calls measurement tools, returns clinical report.

    Returns (changes, morph_report).
    """
    print(f"\n  ── {segment.upper()} pass ──")
    if logger:
        logger.log(beat_idx, segment, "pass", "start")

    print(f"  [{segment}] Rendering focused strip (red=target, black=context)...")
    png = render_segment_focused_strip(record, fid, beat_idx, segment, features)
    if png is None:
        print(f"  [{segment}] Render failed — skipping")
        return [], {}

    # 1. FiducialAgent — corrects positions
    changes = _run_fiducial_agent(
        record, fid, features, beat_idx, segment, png, model, stream, logger=logger
    )

    # 2. Re-render with corrected fiducials
    png_corrected = render_segment_focused_strip(record, fid, beat_idx, segment, features)
    if png_corrected is None:
        png_corrected = png

    # 3. MorphologyAgent — clinical interpretation with measurement tools
    morph = _run_morphology_agent(
        record, fid, features, beat_idx, segment, png_corrected, model, logger=logger
    )

    if logger:
        logger.log(beat_idx, segment, "pass", "complete",
                   {"n_corrections": len(changes),
                    "findings": morph.get("global_findings", [])})
    return changes, morph


# ── Pre-agent sanitizer ────────────────────────────────────────────────────────

def _sanitize_p_ordering(fid: FiducialTable, beat_idx: int) -> list[dict]:
    """
    Fix corrupted P-wave fiducial ordering before agents run.

    PTBXL leads I, aVR (and sometimes V4–V6) are detected with poff placed
    before ppeak in the raw data, making the entire ordering chain invalid and
    blocking all QRS corrections via the _validate() guard.

    Strategy: if poff <= ppeak, advance poff to ppeak + 2 samples (~4ms at 500Hz),
    clamped to stay at least 2 samples before qrson.
    """
    changes = []
    for lead in LEAD_ORDER:
        if lead not in fid.fpt:
            continue
        row = fid.fpt[lead][beat_idx]
        ppeak = int(row[COL_PPEAK])
        poff = int(row[COL_POFF])
        qrson = int(row[COL_QRSON])
        if ppeak < 0 or poff < 0:
            continue
        if poff <= ppeak:
            new_poff = ppeak + 2
            if qrson > 0 and new_poff >= qrson:
                new_poff = qrson - 2
            if new_poff > ppeak:
                fid.fpt[lead][beat_idx, COL_POFF] = new_poff
                changes.append({
                    "lead": lead, "point": "poff",
                    "old_sample": poff, "new_sample": new_poff,
                    "reason": "sanitize: poff <= ppeak",
                })
    return changes


# ── Public entry point ─────────────────────────────────────────────────────────

def run_fiducial_correction(
    record,
    fiducials: FiducialTable,
    features,
    beat_idx: int = 0,
    model: str = "gemma3:12b",
    stream: bool = False,
    workflow_log_path: Optional[str] = None,
) -> tuple[FiducialTable, list[dict], dict]:
    """
    Dual-agent 3-pass fiducial correction across all leads.

    For each segment (P → QRS → T):
      1. FiducialAgent: inspects red/black focused strip, uses math+ruler tools to correct positions.
      2. MorphologyAgent: calls measurement tools (st_deviation, height, slope, symmetry),
         then outputs clinical morphology JSON report.

    Args:
        workflow_log_path: If set, writes a live JSONL log of every agent step to this path.

    Returns (corrected_FiducialTable, full_change_log, morphology_reports).
    morphology_reports: {"p": {...}, "qrs": {...}, "t": {...}}
    """
    logger = WorkflowLogger(workflow_log_path) if workflow_log_path else None
    if logger:
        import time as _t
        logger.log(beat_idx, "all", "session", "start",
                   {"model": model, "n_beats": fiducials.n_beats})

    fid = copy.deepcopy(fiducials)
    sanitize_changes = _sanitize_p_ordering(fid, beat_idx)
    if sanitize_changes:
        print(f"  [sanitize] Fixed {len(sanitize_changes)} P-ordering violations: "
              f"{[c['lead'] for c in sanitize_changes]}")
    all_changes = []
    morphology_reports: dict[str, dict] = {}

    for segment in ["p", "qrs", "t"]:
        changes, morph = run_dual_pass(
            record, fid, features, beat_idx, segment, model, stream, logger=logger
        )
        all_changes.extend(changes)
        morphology_reports[segment] = morph

    # Boost confidence for corrected points
    corrected_pts = {c["point"] for c in all_changes}
    for pt in corrected_pts:
        if pt in (fid.fiducial_confidence or {}):
            fid.fiducial_confidence[pt] = max(fid.fiducial_confidence[pt], 0.75)

    if logger:
        logger.log(beat_idx, "all", "session", "complete", {
            "total_corrections": len(all_changes),
            "segments_reported": list(morphology_reports.keys()),
        })
        logger.close()

    print(f"\n  [correction] Beat {beat_idx}: {len(all_changes)} corrections | "
          f"morphology reports: {list(morphology_reports.keys())}")
    return fid, all_changes, morphology_reports
