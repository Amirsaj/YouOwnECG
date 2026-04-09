"""
Vision LLM ECG assessment — OpenAI GPT-4o (image) with Gemini/Claude fallback.

For each RR interval, renders territory-grouped beat strips on clinical grid paper:
  - Septal (V1, V2)
  - Anterior (V3, V4)
  - Lateral (I, aVL, V5, V6)
  - Inferior (II, III, aVF)

Each strip has fiducial point markers and labeled ECG segments.
All providers receive actual images — no text-only fallback.
"""

from __future__ import annotations
import base64
import io
import os
import time
from pathlib import Path
from typing import Optional

import numpy as np

# ── Territory definitions ─────────────────────────────────────────────────

TERRITORIES = {
    "septal":   {"leads": ["V1", "V2"],             "artery": "LAD septal"},
    "anterior": {"leads": ["V3", "V4"],             "artery": "LAD"},
    "lateral":  {"leads": ["I", "aVL", "V5", "V6"], "artery": "LCx"},
    "inferior": {"leads": ["II", "III", "aVF"],      "artery": "RCA/LCx"},
}

# FPT column indices
COL_PON, COL_PPEAK, COL_POFF = 0, 1, 2
COL_QRSON, COL_Q, COL_R, COL_S, COL_QRSOFF = 3, 4, 5, 6, 7
COL_TON, COL_TPEAK, COL_TOFF = 9, 10, 11

# Model configs
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
OPENAI_MODEL = os.environ.get("OPENAI_VISION_MODEL", "gpt-4o")
CLAUDE_MODEL = "claude-sonnet-4-20250514"

# Known fiducial accuracy issues
FIDUCIAL_PROBLEMS = """
IMPORTANT — FIDUCIAL POINT ACCURACY WARNING:
The automated fiducial detection has known limitations:

| Point     | Detection Rate | Mean Absolute Error |
|-----------|---------------|---------------------|
| P-onset   | 12%           | 26.3 ms             |
| P-peak    | 19%           | 13.0 ms             |
| P-offset  | 17%           | 27.4 ms             |
| QRS-onset | 33%           | 12.3 ms             |
| Q-peak    | 34%           | 5.7 ms              |
| R-peak    | 36%           | 6.1 ms              |
| S-peak    | 32%           | 7.5 ms              |
| QRS-offset| 32%           | 13.6 ms             |
| T-onset   | 12%           | 25.9 ms             |
| T-peak    | 27%           | 11.1 ms             |
| T-offset  | 23%           | 11.8 ms             |

Key issues:
1. P-wave points frequently MISSED (12-19%). If absent, P-wave may still exist.
2. QRS onset/offset MAE ~13ms → PR and QRS duration uncertain by ±13-26ms.
3. T-onset poorly detected (12%). J-T segment boundaries unreliable.
4. R-peak and Q-peak most reliable (MAE 5-6ms).

If a fiducial marker appears misplaced, FLAG it:
"[CORRECTION] Lead X: <point> off by ~Nms — true position at <description>"
"""


# ── Provider detection ────────────────────────────────────────────────────

def _detect_provider() -> str:
    """Gemma local first (free), then OpenAI, Gemini, Claude."""
    if _gemma_available():
        return "gemma"
    if os.environ.get("OPENAI_API_KEY"):
        return "openai"
    if os.environ.get("GEMINI_API_KEY"):
        return "gemini"
    if os.environ.get("ANTHROPIC_API_KEY"):
        return "claude"
    raise ValueError("No vision API available. Start GemmaAPI (./start.sh) or set OPENAI_API_KEY/GEMINI_API_KEY/ANTHROPIC_API_KEY")


def _gemma_available() -> bool:
    """Check if local Gemma server is running."""
    try:
        import urllib.request
        req = urllib.request.urlopen("http://localhost:11434/api/tags", timeout=2)
        return req.status == 200
    except Exception:
        return False


# ── Image rendering ──────────────────────────────────────────────────────

def render_ecg_full_image(record) -> bytes:
    from pipeline.vision import render_ecg_image
    return render_ecg_image(record)


def _plot_segmented_signal(ax, sig, t_ms, win_start: int, fs: float, fpt_beat) -> None:
    """
    Plot the ECG signal with segment-specific colors so the LLM can visually
    identify P / QRS / ST / T without relying on text labels.

    Color scheme (matches standard cardiology annotation conventions):
      P wave     → blue      (#3498DB)
      QRS        → red       (#E74C3C)   thick — most prominent
      ST segment → orange    (#E67E22)
      T wave     → purple    (#9B59B6)
      Baseline   → dark gray (#555555)   thin

    Segments are determined by fiducial points. If a boundary is missing (−1),
    the affected segment falls back to dark gray so the plot never breaks.
    """
    def _x(col_idx):
        s = int(fpt_beat[col_idx])
        return (s - win_start) / fs * 1000 if s >= 0 else None

    p_on  = _x(COL_PON)
    p_off = _x(COL_POFF)
    q_on  = _x(COL_QRSON)
    q_off = _x(COL_QRSOFF)
    t_on  = _x(COL_TON)
    t_off = _x(COL_TOFF)

    # Define colored spans: (x_start, x_end, color, linewidth)
    total = t_ms[-1]
    segments = []

    # Leading baseline (before P-onset)
    if p_on is not None and p_on > 0:
        segments.append((0, p_on, '#555555', 1.2))
    else:
        p_on = 0

    # P wave
    p_end = p_off if p_off is not None else (q_on if q_on is not None else total)
    segments.append((p_on, p_end, '#3498DB', 1.8))

    # PR segment (P-off to QRS-on)
    if q_on is not None and p_end < q_on:
        segments.append((p_end, q_on, '#555555', 1.2))

    # QRS
    q_start = q_on if q_on is not None else p_end
    q_end   = q_off if q_off is not None else (q_start + 0.12 * 1000)
    segments.append((q_start, q_end, '#E74C3C', 2.2))

    # ST segment (QRS-off to T-on)
    st_start = q_end
    st_end   = t_on if t_on is not None else (q_end + 0.08 * 1000)
    if st_end > st_start:
        segments.append((st_start, st_end, '#E67E22', 1.8))

    # T wave
    t_start = st_end
    t_end   = t_off if t_off is not None else (t_start + 0.16 * 1000)
    segments.append((t_start, t_end, '#9B59B6', 1.8))

    # Trailing baseline
    if t_end < total:
        segments.append((t_end, total, '#555555', 1.2))

    # Plot each segment by masking t_ms
    for x0, x1, color, lw in segments:
        mask = (t_ms >= x0) & (t_ms <= x1)
        if mask.any():
            ax.plot(t_ms[mask], sig[mask], color=color, linewidth=lw, solid_capstyle='round')

    # Thin legend strip — tiny colored dots in top-left corner
    legend_items = [('P', '#3498DB'), ('QRS', '#E74C3C'), ('ST', '#E67E22'), ('T', '#9B59B6')]
    for i, (name, color) in enumerate(legend_items):
        ax.text(t_ms[-1] * (0.01 + i * 0.06), 1.92, name,
                fontsize=5.5, color=color, fontweight='bold', ha='left', va='top')


def _draw_lead_measurements(ax, lead: str, features, t_max: float, y_top: float = 1.78) -> None:
    """
    Draw pipeline measurement annotations inside a single lead subplot.

    Shows R/S/Q amplitudes, ST elevation/depression (color-coded), T amplitude,
    QRS pattern, concordance flag, and a BBB warning badge when relevant.
    All values are MEDIANS across the recording — the disclaimer is baked into
    the image text so the LLM always sees it alongside the numbers.
    """
    lines = []
    colors = []

    r_a = features.r_amplitude_mv.get(lead)
    s_a = features.s_amplitude_mv.get(lead)
    q_a = features.q_amplitude_mv.get(lead)
    st_e = features.st_elevation_mv.get(lead)
    st_d = features.st_depression_mv.get(lead)
    j_pt = features.j_point_mv.get(lead) if features.j_point_mv else None
    t_a = features.t_amplitude_mv.get(lead)
    qrs_pat = features.qrs_pattern.get(lead, "") if features.qrs_pattern else ""
    concordance = features.concordance_analysis.get(lead, "") if features.concordance_analysis else ""
    path_q = features.pathological_q_wave.get(lead, False) if features.pathological_q_wave else False

    amp_parts = []
    if r_a is not None:
        amp_parts.append(f"R={r_a:.2f}")
    if s_a is not None and s_a > 0.05:
        amp_parts.append(f"S={s_a:.2f}")
    if q_a is not None and q_a > 0.05:
        q_str = f"Q={q_a:.2f}"
        if path_q:
            q_str += "!"
        amp_parts.append(q_str)
    if amp_parts:
        lines.append(" | ".join(amp_parts) + " mV")
        colors.append('#333')

    # ST — color-coded: red for elevation, blue for depression, gray for iso
    if st_e is not None and st_e > 0.01:
        j_str = f" J={j_pt:+.2f}" if j_pt is not None else ""
        lines.append(f"ST↑{st_e:.2f}mV{j_str}  [median]")
        colors.append('#C0392B')
    elif st_d is not None and st_d > 0.01:
        j_str = f" J={j_pt:+.2f}" if j_pt is not None else ""
        lines.append(f"ST↓{st_d:.2f}mV{j_str}  [median]")
        colors.append('#2471A3')
    else:
        j_str = f" J={j_pt:+.2f}" if j_pt is not None else ""
        lines.append(f"ST≈iso{j_str}")
        colors.append('#777')

    # T amplitude
    if t_a is not None:
        lines.append(f"T={t_a:+.2f}mV")
        colors.append('#8E44AD' if t_a < -0.05 else '#333')

    # QRS pattern
    if qrs_pat:
        lines.append(f"QRS: {qrs_pat}")
        colors.append('#555')

    # Concordance — orange if discordant ST expected
    if concordance:
        c_color = '#E67E22' if concordance == 'discordant' else '#E74C3C'
        lines.append(concordance.upper())
        colors.append(c_color)

    # BBB flag — bold red if LBBB/RBBB
    bbb_flags = []
    if features.lbbb:
        bbb_flags.append("LBBB")
    if features.rbbb:
        bbb_flags.append("RBBB")
    if bbb_flags:
        lines.append("⚠ " + "+".join(bbb_flags))
        colors.append('#C0392B')

    if not lines:
        return

    # Stack lines vertically in top-right corner, each with its own color
    y_step = 0.28 * (y_top / 2.0)  # scale step proportionally to axis height
    for i, (line, color) in enumerate(zip(lines, colors)):
        ax.text(
            t_max * 0.985, y_top - i * y_step,
            line,
            fontsize=5.5, ha='right', va='top', color=color,
            fontweight='bold' if color == '#C0392B' else 'normal',
            bbox=dict(boxstyle='round,pad=0.12', facecolor='white',
                      edgecolor=color, linewidth=0.4, alpha=0.45),
        )


def _draw_global_badge(fig, features, beat_idx: int) -> None:
    """
    Draw the global measurement badge at the bottom of the figure.

    Includes HR/PR/QRS/QTc/Axis/Rhythm plus a prominent BBB flag.
    Beat index and RR interval are shown when available.
    """
    hr = features.heart_rate_ventricular_bpm
    pr = features.pr_interval_ms or '?'
    qrs = features.qrs_duration_global_ms or '?'
    qtc = f"{features.qtc_bazett_ms:.0f}" if features.qtc_bazett_ms else '?'
    axis = f"{features.qrs_axis_deg:.0f}°" if features.qrs_axis_deg is not None else '?'
    rhythm = features.dominant_rhythm or '?'
    regular = 'regular' if features.rhythm_regular else 'irregular'

    rr_str = ""
    bs = features.beat_summary
    if bs and bs.rr_intervals_ms and beat_idx > 0 and beat_idx - 1 < len(bs.rr_intervals_ms):
        rr_val = bs.rr_intervals_ms[beat_idx - 1]
        rr_str = f" | RR={rr_val:.0f}ms"

    bbb_flags = []
    if features.lbbb:
        bbb_flags.append("LBBB")
    if features.rbbb:
        bbb_flags.append("RBBB")
    if features.wpw_pattern:
        bbb_flags.append("WPW")
    bbb_str = ("  ⚠ " + "+".join(bbb_flags)) if bbb_flags else ""

    meas_text = (
        f"Beat {beat_idx + 1} | HR={hr:.0f}bpm | PR={pr}ms | QRS={qrs}ms | "
        f"QTc={qtc}ms | Axis={axis} | {rhythm} ({regular}){rr_str}"
        f"{bbb_str}"
        f"  [MEDIAN values — verify visually]"
    )

    bbb_color = '#C0392B' if bbb_flags else '#555'
    fig.text(
        0.01, 0.002, meas_text,
        fontsize=6, color=bbb_color if bbb_flags else '#666',
        fontweight='bold' if bbb_flags else 'normal',
        bbox=dict(boxstyle='round,pad=0.2', facecolor='#FEF9E7' if bbb_flags else 'white',
                  edgecolor='#E74C3C' if bbb_flags else '#bbb',
                  linewidth=0.8 if bbb_flags else 0.4, alpha=0.5),
    )


def render_territory_beat_strip(
    record, fiducials, beat_idx: int, territory: str, territory_leads: list[str],
    features=None,
) -> Optional[tuple]:
    """
    Render one beat for one territory on clinical grid paper.
    Includes: baseline reference line, beat/segment annotations, measurement overlay.
    Returns (image_bytes, missing_fiducials_dict) or None.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    morph = record.morphology_signal
    fs = record.fs
    leads = record.lead_names
    lead_idx = {l: i for i, l in enumerate(leads)}
    s0 = record.safe_window_start_sample

    ref_lead = "II" if "II" in fiducials.fpt else list(fiducials.fpt.keys())[0]
    ref_fpt = fiducials.fpt[ref_lead]
    if beat_idx >= len(ref_fpt):
        return None

    beat = ref_fpt[beat_idx]
    r_peak = int(beat[COL_R])
    if r_peak < 0:
        r_peak = int(beat[COL_QRSON])
    if r_peak < 0:
        return None

    # Window: R1 - RR*0.1 to R2 + RR*0.1
    if beat_idx + 1 < len(ref_fpt):
        next_r = int(ref_fpt[beat_idx + 1][COL_R])
        if next_r < 0:
            next_r = int(ref_fpt[beat_idx + 1][COL_QRSON])
        if next_r <= 0:
            next_r = r_peak + int(0.8 * fs)
    else:
        next_r = r_peak + int(0.8 * fs)

    rr_len = next_r - r_peak
    pad = int(rr_len * 0.1)
    win_start = max(0, r_peak - pad)

    # Expand window to include P-wave if detected in any lead
    for tl in territory_leads:
        lf = fiducials.fpt.get(tl, ref_fpt)
        if beat_idx < len(lf):
            p_on = int(lf[beat_idx, COL_PON])
            p_pk = int(lf[beat_idx, COL_PPEAK])
            earliest_p = p_on if p_on >= 0 else p_pk
            if earliest_p >= 0:
                # Include P-wave with a small margin before it
                p_margin = int(0.03 * fs)  # 30ms before P-onset
                win_start = min(win_start, max(0, earliest_p - p_margin))

    win_end = min(morph.shape[1] - s0, next_r + pad)

    # Also expand window to include next beat's R-peak
    # (we want R1 → P₂ → R₂ visible in the strip)
    win_end = min(morph.shape[1] - s0, next_r + int(rr_len * 0.05) + 1)

    available_leads = [l for l in territory_leads if l in lead_idx]
    if not available_leads:
        return None

    n_leads = len(available_leads)
    duration_s = (win_end - win_start) / fs
    mv_range = 4.0
    width_mm = duration_s * 25
    height_mm_per_lead = mv_range * 10
    total_height_mm = height_mm_per_lead * n_leads
    scale = 2.5
    fig_w = max(8, width_mm / 25.4 * scale)
    fig_h = max(3, total_height_mm / 25.4 * scale + 0.6)

    all_missing = {}
    fig, axes = plt.subplots(n_leads, 1, figsize=(fig_w, fig_h), squeeze=False)
    fig.patch.set_facecolor('white')

    for j, lead in enumerate(available_leads):
        ax = axes[j, 0]
        ax.set_facecolor('white')
        idx = lead_idx[lead]
        sig = morph[idx, s0 + win_start:s0 + win_end].astype(float) / 1000.0
        t_ms = np.arange(len(sig)) / fs * 1000
        t_max = t_ms[-1] if len(t_ms) > 0 else 1

        # Clinical grid paper (black, low opacity)
        for x in np.arange(0, t_max + 40, 40):
            ax.axvline(x, color='#000000', linewidth=0.3, alpha=0.08)
        for y_g in np.arange(-2, 2.01, 0.1):
            ax.axhline(y_g, color='#000000', linewidth=0.3, alpha=0.08)
        for x in np.arange(0, t_max + 200, 200):
            ax.axvline(x, color='#000000', linewidth=0.6, alpha=0.15)
        for y_g in np.arange(-2, 2.01, 0.5):
            ax.axhline(y_g, color='#000000', linewidth=0.6, alpha=0.15)

        ax.axhline(0, color='#555', linewidth=0.5, alpha=0.4)

        # ── PR segment baseline reference (green dashed, low opacity) ──
        lead_fpt_bl = fiducials.fpt.get(lead, ref_fpt)
        if beat_idx < len(lead_fpt_bl):
            b_bl = lead_fpt_bl[beat_idx]
            qrs_on_bl = int(b_bl[COL_QRSON])
            if qrs_on_bl > 0:
                bl_start = max(0, qrs_on_bl - int(0.02 * fs))
                bl_seg = sig[max(0, bl_start - win_start):max(0, qrs_on_bl - win_start)]
                if len(bl_seg) > 2:
                    bl_val = float(np.mean(bl_seg)) / 1000.0  # mV
                    ax.axhline(bl_val, color='#27AE60', linewidth=1.0, linestyle='--',
                               alpha=0.25, label='baseline')

        # Plot signal with segment-specific colors (P=blue, QRS=red, ST=orange, T=purple)
        if beat_idx < len(fiducials.fpt.get(lead, ref_fpt)):
            _plot_segmented_signal(ax, sig, t_ms, win_start, fs,
                                   fiducials.fpt.get(lead, ref_fpt)[beat_idx])
        else:
            ax.plot(t_ms, sig, color='#333333', linewidth=1.5)

        # Fiducial markers — draw current beat AND next beat's P-wave
        lead_fpt = fiducials.fpt.get(lead, ref_fpt)

        fid_points_current = [
            ("P",  COL_PPEAK,  "#3498DB"),
            ("Q",  COL_Q,      "#7F8C8D"),
            ("R",  COL_R,      "#E74C3C"),
            ("S",  COL_S,      "#E67E22"),
            ("J",  COL_QRSOFF, "#F1C40F"),
            ("T",  COL_TPEAK,  "#9B59B6"),
        ]
        # Next beat: draw P and R (to show the full R-to-R + next P)
        fid_points_next = [
            ("P₂", COL_PPEAK,  "#3498DB"),
            ("R₂", COL_R,      "#E74C3C"),
        ]

        tick_len = 0.45
        label_offset = 0.12
        drawn = []
        missing = []

        # Current beat fiducials
        if beat_idx < len(lead_fpt):
            b = lead_fpt[beat_idx]
            for name, col, color in fid_points_current:
                sample_idx = int(b[col])
                if sample_idx < 0:
                    missing.append(name)
                    continue
                x_ms = (sample_idx - win_start) / fs * 1000
                if x_ms < 0 or x_ms > t_max:
                    missing.append(name)
                    continue
                sig_idx = sample_idx - win_start
                sig_val = sig[sig_idx] if 0 <= sig_idx < len(sig) else 0.0
                drawn.append((name, x_ms, color, sig_val))

        # Next beat fiducials (P₂ and R₂)
        if beat_idx + 1 < len(lead_fpt):
            b_next = lead_fpt[beat_idx + 1]
            for name, col, color in fid_points_next:
                sample_idx = int(b_next[col])
                if sample_idx < 0:
                    continue
                x_ms = (sample_idx - win_start) / fs * 1000
                if x_ms < 0 or x_ms > t_max:
                    continue
                sig_idx = sample_idx - win_start
                sig_val = sig[sig_idx] if 0 <= sig_idx < len(sig) else 0.0
                drawn.append((name, x_ms, color, sig_val))

        direction_map = {"P": False, "Q": False, "R": True, "S": False, "J": True, "T": False,
                         "P₂": False, "R₂": True}
        prev_x = -999
        prev_dir = None
        for i, (name, x_ms, color, sig_val) in enumerate(drawn):
            goes_up = direction_map.get(name, i % 2 == 0)

            if abs(x_ms - prev_x) < 15:
                if prev_dir is not None:
                    goes_up = not prev_dir

            if goes_up:
                tick_end = sig_val + tick_len
                label_y = tick_end + label_offset
                va = 'bottom'
            else:
                tick_end = sig_val - tick_len
                label_y = tick_end - label_offset
                va = 'top'

            ax.plot([x_ms, x_ms], [sig_val, tick_end],
                    color=color, linewidth=1.5, alpha=0.7, solid_capstyle='round')
            ax.plot(x_ms, sig_val, 'o', color=color, markersize=4, zorder=5)
            ax.text(x_ms, label_y, name, fontsize=8, ha='center', va=va,
                    color=color, fontweight='bold',
                    bbox=dict(boxstyle='round,pad=0.2', facecolor='white',
                              edgecolor=color, linewidth=0.6, alpha=0.95))
            prev_x = x_ms
            prev_dir = goes_up

        if missing:
            all_missing[lead] = missing
            miss_str = "Not detected: " + ", ".join(missing)
            ax.text(t_max * 0.98, -1.85, miss_str, fontsize=6.5,
                    ha='right', va='bottom', color='#C0392B', style='italic',
                    bbox=dict(boxstyle='round,pad=0.2', facecolor='#FDEDEC',
                              edgecolor='#E74C3C', linewidth=0.5, alpha=0.9))

        ax.text(3, 1.6, lead, fontsize=10, fontweight='bold', color='#000',
                bbox=dict(boxstyle='square,pad=0.3', facecolor='white',
                          edgecolor='#000', linewidth=1.2))

        # Dynamic y-axis — compute before drawing markers so positions scale correctly
        sig_peak = float(np.max(sig)) if len(sig) else 2.0
        sig_trough = float(np.min(sig)) if len(sig) else -2.0
        y_top = max(2.0, sig_peak * 1.15)
        y_bot = min(-2.0, sig_trough * 1.15)

        # ── Beat boundary markers (R₁ start, R₂ end) ──
        r_pos_ms = (r_peak - win_start) / fs * 1000
        next_r_ms = (next_r - win_start) / fs * 1000
        r_label_y = y_top * 0.96
        if 0 < r_pos_ms < t_max:
            ax.axvline(r_pos_ms, color='#E74C3C', linewidth=0.8, linestyle=':', alpha=0.3)
            ax.text(r_pos_ms + 3, r_label_y, 'R₁', fontsize=6, color='#E74C3C', alpha=0.5)
        if 0 < next_r_ms < t_max:
            ax.axvline(next_r_ms, color='#E74C3C', linewidth=0.8, linestyle=':', alpha=0.3)
            ax.text(next_r_ms + 3, r_label_y, 'R₂', fontsize=6, color='#E74C3C', alpha=0.5)
        ax.set_xlim(0, t_max)
        ax.set_ylim(y_bot, y_top)

        # ── Per-lead measurements overlay — every lead, right side ──
        if features is not None:
            _draw_lead_measurements(ax, lead, features, t_max, y_top=y_top)

        # Clip-warning banner if true peak exceeds ±2 mV
        if sig_peak > 2.0 or sig_trough < -2.0:
            clip_parts = []
            if sig_peak > 2.0:
                clip_parts.append(f"R-peak = {sig_peak:.2f} mV (exceeds grid)")
            if sig_trough < -2.0:
                clip_parts.append(f"S-trough = {sig_trough:.2f} mV (exceeds grid)")
            ax.text(t_max * 0.5, y_top * 0.92, "⚠ HIGH VOLTAGE: " + " | ".join(clip_parts),
                    fontsize=6, ha='center', va='top', color='#C0392B', fontweight='bold',
                    bbox=dict(boxstyle='round,pad=0.2', facecolor='#FDEDEC',
                              edgecolor='#E74C3C', linewidth=0.8, alpha=0.9))

        ax.set_aspect(40 / 0.1, adjustable='box')
        ax.tick_params(labelsize=6, length=2)
        if j < n_leads - 1:
            ax.set_xticklabels([])
        else:
            ax.set_xlabel("ms", fontsize=8)
        ax.set_ylabel("mV", fontsize=7)

    # ── Global measurements badge on the figure ──
    if features is not None:
        _draw_global_badge(fig, features, beat_idx)

    fig.suptitle(
        f"Beat {beat_idx + 1} — {territory.upper()} "
        f"({', '.join(available_leads)}) — {TERRITORIES[territory]['artery']}",
        fontsize=10, fontweight='bold', color='#333'
    )
    fig.text(0.99, 0.005, "25 mm/s | 10 mm/mV", fontsize=6, ha='right', color='#999')

    plt.tight_layout(rect=[0, 0.01, 1, 0.95])
    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=150, bbox_inches="tight", facecolor='white')
    plt.close(fig)
    buf.seek(0)
    return buf.read(), all_missing


def render_all_beat_territory_strips(record, fiducials, max_beats: int = 3, features=None) -> list[dict]:
    ref_lead = "II" if "II" in fiducials.fpt else list(fiducials.fpt.keys())[0]
    n_beats = min(max_beats, len(fiducials.fpt[ref_lead]))
    strips = []
    for beat_idx in range(n_beats):
        for territory, info in TERRITORIES.items():
            result = render_territory_beat_strip(
                record, fiducials, beat_idx, territory, info["leads"], features=features
            )
            if result:
                img, missing = result
                strips.append({
                    "beat": beat_idx + 1,
                    "territory": territory,
                    "leads": info["leads"],
                    "artery": info["artery"],
                    "image": img,
                    "missing_fiducials": missing,
                })
    return strips


# ── Prompt ────────────────────────────────────────────────────────────────

SINGLE_BEAT_PROMPT = """You are an expert cardiologist analyzing ONE COMPLETE RR INTERVAL on clinical grid paper.

HOW TO READ THIS STRIP:
- R₁ (red dotted line, left) marks the START of this beat
- R₂ (red dotted line, right) marks the END (next beat's R-peak)
- GREEN DASHED LINE = isoelectric baseline (PR segment reference)
  → Measure ALL ST elevation/depression relative to this green line
- Bottom-left: global measurements (HR, PR, QRS, QTc)
- Top-right of first lead: per-lead measurements (R amplitude, ST level, T amplitude)

CARDIAC CYCLE (left to right):
  P-wave → PR segment (at green baseline) → QRS (Q→R→S) → J-point (yellow marker)
  → ST segment (compare to green baseline!) → T-wave → TP segment → P₂ → R₂

Territories shown:
- Septal (V1, V2) — LAD septal perforators
- Anterior (V3, V4) — LAD
- Lateral (I, aVL, V5, V6) — LCx
- Inferior (II, III, aVF) — RCA/LCx

Fiducial markers: P (blue↓), Q (gray↓), R (red↑), S (orange↓), J-point (yellow↑), T (purple↓)
Next beat: P₂ (blue↓), R₂ (red↑)
Grid: small boxes = 1mm (40ms × 0.1mV), large boxes = 5mm (200ms × 0.5mV)

""" + FIDUCIAL_PROBLEMS + """

Narrate THIS SINGLE BEAT — ALL leads in ALL territories:

## SEPTAL (V1, V2)
For each lead:
- P wave: present/absent, polarity, amplitude (mV), duration (ms)
- PR interval: duration (ms)
- Q-R: Q wave present? depth, duration, pathological (>40ms or >25% R)?
- R-S: R amplitude (mV), R' present? slurred upstroke? notching?
- S-J: J-point level (mm above/below baseline)
- J-T: ST curvature (concave/convex/coved/linear), ST elevation/depression (mm)
- T wave: polarity, amplitude (mV), symmetry, peaked/notched/biphasic?
- Baseline: isoelectric? artifact?

## ANTERIOR (V3, V4)
(same per-lead structure)

## LATERAL (I, aVL, V5, V6)
(same per-lead structure)

## INFERIOR (II, III, aVF)
(same per-lead structure)

## FIDUCIAL CORRECTIONS
Flag any misplaced markers: "[CORRECTION] Lead X: <point> off by ~Nms"

## BEAT SUMMARY
- Key abnormalities
- Cross-territory ST concordance
- Confidence per finding
"""


def _beat_measurements_text(record, fiducials, features, beat_idx: int) -> str:
    """Per-beat measurement summary for prompt preview."""
    f = features
    lines = []
    for territory, info in TERRITORIES.items():
        available = [l for l in info["leads"] if l in record.lead_names]
        if not available:
            continue
        lines.append(f"\n  {territory.upper()} ({', '.join(available)}) — {info['artery']}:")
        for lead in available:
            r = f.r_amplitude_mv.get(lead)
            s = f.s_amplitude_mv.get(lead)
            st_e = f.st_elevation_mv.get(lead)
            st_d = f.st_depression_mv.get(lead)
            t_a = f.t_amplitude_mv.get(lead)
            st_m = f.st_morphology.get(lead, "")
            t_m = f.t_morphology.get(lead, "")
            line = f"    {lead:>4}: R={r:.2f}" if r else f"    {lead:>4}: R=?"
            if s: line += f" S={s:.2f}"
            if st_e and st_e > 0.01: line += f" ST↑{st_e:.2f}"
            if st_d and st_d > 0.01: line += f" ST↓{st_d:.2f}"
            if t_a: line += f" T={t_a:+.2f}"
            if st_m: line += f" [{st_m}]"
            if t_m: line += f" T:{t_m}"
            lines.append(line)

    return f"=== Beat {beat_idx + 1} measurements ===\n" + "\n".join(lines)


def _measurements_context(features) -> str:
    f = features
    return (
        "\nPipeline measurements:\n"
        f"- HR: {f.heart_rate_ventricular_bpm:.0f} bpm | "
        f"PR: {f.pr_interval_ms} ms | QRS: {f.qrs_duration_global_ms} ms\n"
        f"- QTc Bazett: {f.qtc_bazett_ms} ms | Fridericia: {f.qtc_fridericia_ms} ms\n"
        f"- Axis: QRS={f.qrs_axis_deg}° P={f.p_axis_deg}° T={f.t_axis_deg}°\n"
        f"- Rhythm: {f.dominant_rhythm} ({'regular' if f.rhythm_regular else 'irregular'})\n"
        f"- LVH: Sokolow={f.lvh_sokolow_lyon_mv}mV Cornell={f.lvh_cornell_mv}mV RE={f.lvh_romhilt_estes_score}\n"
        f"- R-progression: {f.r_progression}\n"
        "\nProvide YOUR independent visual assessment. Note any discrepancies."
    )


# ── Gemma 3 Local (vision via Ollama) ─────────────────────────────────────

GEMMA_BASE_URL = "http://localhost:11434/v1"
GEMMA_MODEL = os.environ.get("GEMMA_MODEL", "gemma3:27b")


def _call_gemma_single_beat(record, fiducials, features, beat_idx: int) -> str:
    """One local Gemma 3 call for one beat — sends 4 territory images."""
    from openai import OpenAI
    client = OpenAI(base_url=GEMMA_BASE_URL, api_key="local")

    content = [{"type": "text", "text": f"Analyze Beat {beat_idx + 1} of this ECG. "
                f"4 territory-grouped strips follow:"}]

    for territory, info in TERRITORIES.items():
        result = render_territory_beat_strip(record, fiducials, beat_idx, territory, info["leads"], features=features)
        if result:
            img, missing = result
            caption = f"\n{territory.upper()} ({', '.join(info['leads'])}) — {info['artery']}"
            if missing:
                miss_lines = [f"  {lead}: {', '.join(pts)} NOT DETECTED" for lead, pts in missing.items()]
                caption += "\nDETECTION UNCERTAINTY:\n" + "\n".join(miss_lines)
            content.append({"type": "text", "text": caption})
            b64 = base64.b64encode(img).decode()
            content.append({"type": "image_url",
                "image_url": {"url": f"data:image/png;base64,{b64}"}})

    content.append({"type": "text",
        "text": SINGLE_BEAT_PROMPT + _measurements_context(features)})

    response = client.chat.completions.create(
        model=GEMMA_MODEL,
        messages=[{"role": "user", "content": content}],
        max_tokens=3000,
    )
    return response.choices[0].message.content


# ── OpenAI GPT-4o (vision) ───────────────────────────────────────────────

def _call_openai_single_beat(record, fiducials, features, beat_idx: int) -> str:
    """One GPT-4o call for one beat — sends 4 territory images."""
    from openai import OpenAI
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    content = [{"type": "text", "text": f"Analyze Beat {beat_idx + 1} of this ECG. "
                f"4 territory-grouped strips follow:"}]

    for territory, info in TERRITORIES.items():
        result = render_territory_beat_strip(record, fiducials, beat_idx, territory, info["leads"], features=features)
        if result:
            img, missing = result
            caption = f"\n{territory.upper()} ({', '.join(info['leads'])}) — {info['artery']}"
            if missing:
                miss_lines = [f"  {lead}: {', '.join(pts)} NOT DETECTED" for lead, pts in missing.items()]
                caption += "\nDETECTION UNCERTAINTY:\n" + "\n".join(miss_lines)
            content.append({"type": "text", "text": caption})
            b64 = base64.b64encode(img).decode()
            content.append({"type": "image_url",
                "image_url": {"url": f"data:image/png;base64,{b64}", "detail": "high"}})

    content.append({"type": "text",
        "text": SINGLE_BEAT_PROMPT + _measurements_context(features)})

    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[{"role": "user", "content": content}],
        max_tokens=3000,
    )
    return response.choices[0].message.content


# ── Gemini (vision) ───────────────────────────────────────────────────────

def _call_gemini_single_beat(record, fiducials, features, beat_idx: int) -> str:
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

    parts = [types.Part.from_text(text=f"Analyze Beat {beat_idx + 1} of this ECG. "
             f"4 territory-grouped strips follow:")]

    for territory, info in TERRITORIES.items():
        result = render_territory_beat_strip(record, fiducials, beat_idx, territory, info["leads"], features=features)
        if result:
            img, missing = result
            caption = f"\n{territory.upper()} ({', '.join(info['leads'])}) — {info['artery']}"
            if missing:
                miss_lines = [f"  {lead}: {', '.join(pts)} NOT DETECTED" for lead, pts in missing.items()]
                caption += "\nDETECTION UNCERTAINTY:\n" + "\n".join(miss_lines)
            parts.append(types.Part.from_text(text=caption))
            parts.append(types.Part.from_bytes(data=img, mime_type="image/png"))

    parts.append(types.Part.from_text(
        text=SINGLE_BEAT_PROMPT + _measurements_context(features)))

    models_to_try = [GEMINI_MODEL, "gemini-2.5-flash-lite", "gemini-2.0-flash-lite"]
    last_err = None
    for model in models_to_try:
        for attempt in range(2):
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=[types.Content(role="user", parts=parts)],
                    config=types.GenerateContentConfig(max_output_tokens=3000, temperature=0.1),
                )
                return response.text
            except Exception as e:
                last_err = e
                if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                    if attempt < 1:
                        time.sleep(35)
                        continue
                    break
                raise
    raise last_err


# ── Claude (vision) ──────────────────────────────────────────────────────

def _call_claude_single_beat(record, fiducials, features, beat_idx: int) -> str:
    import anthropic
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    content = [{"type": "text", "text": f"Analyze Beat {beat_idx + 1} of this ECG. "
                f"4 territory-grouped strips follow:"}]

    for territory, info in TERRITORIES.items():
        result = render_territory_beat_strip(record, fiducials, beat_idx, territory, info["leads"], features=features)
        if result:
            img, missing = result
            caption = f"\n{territory.upper()} ({', '.join(info['leads'])}) — {info['artery']}"
            if missing:
                miss_lines = [f"  {lead}: {', '.join(pts)} NOT DETECTED" for lead, pts in missing.items()]
                caption += "\nDETECTION UNCERTAINTY:\n" + "\n".join(miss_lines)
            content.append({"type": "text", "text": caption})
            b64 = base64.b64encode(img).decode()
            content.append({"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": b64}})

    content.append({"type": "text",
        "text": SINGLE_BEAT_PROMPT + _measurements_context(features)})

    response = client.messages.create(
        model=CLAUDE_MODEL, max_tokens=3000,
        messages=[{"role": "user", "content": content}],
    )
    return response.content[0].text


# ── Public API ────────────────────────────────────────────────────────────

def assess_single_beat(record, fiducials, features, beat_idx: int,
                       provider: Optional[str] = None) -> tuple[str, str]:
    """One vision LLM call for one beat. Returns (narration_text, provider_used)."""
    if provider is None:
        provider = _detect_provider()

    # Build fallback chain — all vision-capable providers
    providers_to_try = [provider]
    for p in ["gemma", "openai", "gemini", "claude"]:
        if p != provider and p not in providers_to_try:
            has_key = (
                (p == "gemma" and _gemma_available()) or
                (p == "openai" and os.environ.get("OPENAI_API_KEY")) or
                (p == "gemini" and os.environ.get("GEMINI_API_KEY")) or
                (p == "claude" and os.environ.get("ANTHROPIC_API_KEY"))
            )
            if has_key:
                providers_to_try.append(p)

    last_err = None
    for p in providers_to_try:
        try:
            if p == "gemma":
                text = _call_gemma_single_beat(record, fiducials, features, beat_idx)
            elif p == "openai":
                text = _call_openai_single_beat(record, fiducials, features, beat_idx)
            elif p == "gemini":
                text = _call_gemini_single_beat(record, fiducials, features, beat_idx)
            elif p == "claude":
                text = _call_claude_single_beat(record, fiducials, features, beat_idx)
            return text, p
        except Exception as e:
            last_err = e
            continue
    raise last_err


def get_visual_assessment(record, fiducials, features, provider=None) -> tuple[str, str]:
    """Assess all beats, one call per beat. Combine results."""
    ref_lead = "II" if "II" in fiducials.fpt else list(fiducials.fpt.keys())[0]
    n_beats = min(3, len(fiducials.fpt[ref_lead]))

    all_narrations = []
    used_provider = None
    for beat_idx in range(n_beats):
        text, p = assess_single_beat(record, fiducials, features, beat_idx, provider)
        used_provider = p
        all_narrations.append(f"{'='*60}\nBEAT {beat_idx + 1} (via {p})\n{'='*60}\n\n{text}")

    return "\n\n".join(all_narrations), used_provider or "unknown"


# Back-compat alias
def get_claude_visual_assessment(record, fiducials, features, client=None,
                                  include_beat_strips=True) -> str:
    text, _ = get_visual_assessment(record, fiducials, features)
    return text
