"""
Node 1.6 — Vision Pipeline (DeepSeek-VL2).

Renders the ECG as a 12-lead image and sends it to DeepSeek-VL2 for visual
verification. VL2 output is advisory only — it never overwrites signal features.
Runs with a 15-second timeout (MAX_VL2_WAIT_SEC). On timeout or error, returns
a VisionVerificationResult with available=False.

The rendered image uses morphology_signal (raw amplitude, 500 Hz, no filter).
Mandatory rendering elements: calibration pulse, lead labels, speed/gain annotation.
"""

from __future__ import annotations
import asyncio
import base64
import io
import time
from typing import Optional

import numpy as np
from pipeline.schemas import (
    PreprocessedECGRecord,
    FeatureObject,
    VisionVerificationResult,
    SignalVisionConflict,
)

MAX_VL2_WAIT_SEC = 15.0
SAMPLES_PER_STRIP = 1500      # 3 seconds at 500 Hz
CALIBRATION_PULSE_MV = 1.0    # 1 mV calibration pulse
CALIBRATION_PULSE_DURATION_MS = 200
SHOW_SPEED_GAIN_ANNOTATION = True
SHOW_LEAD_LABELS = True

# Layout: 3 rows × 4 columns + rhythm strip
ECG_LAYOUT = [
    ["I",   "aVR", "V1", "V4"],
    ["II",  "aVL", "V2", "V5"],
    ["III", "aVF", "V3", "V6"],
]
RHYTHM_LEAD = "II"


async def run_vision_pipeline(
    record: PreprocessedECGRecord,
    features: FeatureObject,
    vl2_client,           # openai.AsyncOpenAI configured for DeepSeek-VL2 endpoint
) -> VisionVerificationResult:
    """
    Render the ECG and send to VL2 for visual verification.
    Returns a VisionVerificationResult (advisory only).

    Times out after MAX_VL2_WAIT_SEC and returns unavailable result.
    """
    try:
        result = await asyncio.wait_for(
            _vl2_verify(record, features, vl2_client),
            timeout=MAX_VL2_WAIT_SEC,
        )
        return result
    except asyncio.TimeoutError:
        return VisionVerificationResult(
            available=False,
            unavailability_reason="VL2_TIMEOUT",
            st_elevation_leads=[],
            st_depression_leads=[],
            t_wave_inversion_leads=[],
            lbbb_pattern=False,
            rhythm_regular=None,
            qrs_wide=None,
            signal_vision_conflicts=[],
            raw_vl2_response=None,
            vl2_latency_sec=MAX_VL2_WAIT_SEC,
        )
    except Exception as exc:
        return VisionVerificationResult(
            available=False,
            unavailability_reason="VL2_ERROR",
            st_elevation_leads=[],
            st_depression_leads=[],
            t_wave_inversion_leads=[],
            lbbb_pattern=False,
            rhythm_regular=None,
            qrs_wide=None,
            signal_vision_conflicts=[],
            raw_vl2_response=str(exc),
            vl2_latency_sec=None,
        )


async def _vl2_verify(
    record: PreprocessedECGRecord,
    features: FeatureObject,
    vl2_client,
) -> VisionVerificationResult:
    """Render ECG, send to VL2, parse response, detect conflicts."""
    t0 = time.monotonic()

    # Render ECG image
    img_bytes = render_ecg_image(record)
    img_b64 = base64.b64encode(img_bytes).decode("utf-8")

    prompt = _build_vl2_prompt(features)

    response = await vl2_client.chat.completions.create(
        model="deepseek-vl2",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{img_b64}"},
                    },
                    {"type": "text", "text": prompt},
                ],
            }
        ],
        max_tokens=512,
    )

    latency = time.monotonic() - t0
    raw_text = response.choices[0].message.content

    vl2_result = _parse_vl2_response(raw_text)
    conflicts = _detect_conflicts(features, vl2_result)

    return VisionVerificationResult(
        available=True,
        unavailability_reason=None,
        st_elevation_leads=vl2_result.get("st_elevation_leads", []),
        st_depression_leads=vl2_result.get("st_depression_leads", []),
        t_wave_inversion_leads=vl2_result.get("t_wave_inversion_leads", []),
        lbbb_pattern=vl2_result.get("lbbb_pattern", False),
        rhythm_regular=vl2_result.get("rhythm_regular"),
        qrs_wide=vl2_result.get("qrs_wide"),
        signal_vision_conflicts=conflicts,
        raw_vl2_response=raw_text,
        vl2_latency_sec=latency,
    )


def _build_vl2_prompt(features: FeatureObject) -> str:
    return (
        "You are an expert electrocardiographer reviewing a 12-lead ECG image. "
        "The image shows a standard 12-lead ECG with a calibration pulse and lead labels. "
        "Paper speed: 25 mm/s. Gain: 10 mm/mV.\n\n"
        "Please identify the following findings VISUALLY from the image. "
        "Respond ONLY with a JSON object with these exact keys:\n"
        "{\n"
        '  "st_elevation_leads": ["V2", "V3"],  // leads with visible ST elevation\n'
        '  "st_depression_leads": [],             // leads with visible ST depression\n'
        '  "t_wave_inversion_leads": [],          // leads with inverted T waves\n'
        '  "lbbb_pattern": false,                 // true if LBBB pattern visible\n'
        '  "rhythm_regular": true,                // null if cannot determine\n'
        '  "qrs_wide": false                      // true if QRS appears wide (>120ms)\n'
        "}\n\n"
        "If you cannot determine a finding from the image, use null for that field. "
        "Do not include any explanation — JSON only."
    )


def _parse_vl2_response(raw_text: str) -> dict:
    """Extract JSON from VL2 response. Returns empty dict on parse failure."""
    import json
    import re

    # Extract JSON block
    match = re.search(r"\{.*\}", raw_text, re.DOTALL)
    if not match:
        return {}
    try:
        data = json.loads(match.group(0))
        return {
            "st_elevation_leads": data.get("st_elevation_leads") or [],
            "st_depression_leads": data.get("st_depression_leads") or [],
            "t_wave_inversion_leads": data.get("t_wave_inversion_leads") or [],
            "lbbb_pattern": bool(data.get("lbbb_pattern", False)),
            "rhythm_regular": data.get("rhythm_regular"),
            "qrs_wide": data.get("qrs_wide"),
        }
    except (json.JSONDecodeError, ValueError):
        return {}


def _detect_conflicts(features: FeatureObject, vl2: dict) -> list[SignalVisionConflict]:
    """
    Compare signal pipeline features against VL2 visual findings.
    Returns list of conflicts (advisory — do not overwrite signal features).
    """
    conflicts = []

    # ST elevation conflicts
    for lead in features.st_elevation_mv:
        sig_has_elev = (features.st_elevation_mv.get(lead) or 0) > 0.1
        vl2_has_elev = lead in vl2.get("st_elevation_leads", [])
        if sig_has_elev and not vl2_has_elev:
            conflicts.append(SignalVisionConflict(
                lead=lead,
                finding_type="st_elevation",
                signal_value=f"+{features.st_elevation_mv[lead]:.2f} mV",
                vision_value="no ST elevation visible",
                conflict_type="SIGNAL_ONLY",
            ))
        elif not sig_has_elev and vl2_has_elev:
            conflicts.append(SignalVisionConflict(
                lead=lead,
                finding_type="st_elevation",
                signal_value="no elevation detected",
                vision_value="ST elevation visible",
                conflict_type="VISION_ONLY",
            ))

    # LBBB conflict
    sig_lbbb = features.lbbb
    vl2_lbbb = vl2.get("lbbb_pattern", False)
    if sig_lbbb and not vl2_lbbb:
        conflicts.append(SignalVisionConflict(
            lead="global",
            finding_type="lbbb",
            signal_value="LBBB detected",
            vision_value="no LBBB visible",
            conflict_type="SIGNAL_ONLY",
        ))
    elif not sig_lbbb and vl2_lbbb:
        conflicts.append(SignalVisionConflict(
            lead="global",
            finding_type="lbbb",
            signal_value="no LBBB detected",
            vision_value="LBBB pattern visible",
            conflict_type="VISION_ONLY",
        ))

    return conflicts


# ---------------------------------------------------------------------------
# ECG image rendering
# ---------------------------------------------------------------------------

def render_ecg_image(record: PreprocessedECGRecord) -> bytes:
    """
    Render a standard 12-lead ECG image from morphology_signal.

    Mandatory elements: calibration pulse, lead labels, speed/gain annotation.
    Returns PNG bytes.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.gridspec as gridspec

    morph = record.morphology_signal
    fs = record.fs
    leads = record.lead_names
    lead_idx = {l: i for i, l in enumerate(leads)}

    # Use the safe window
    start = record.safe_window_start_sample
    end = min(start + SAMPLES_PER_STRIP, record.safe_window_end_sample)

    fig = plt.figure(figsize=(22, 14), facecolor="white")
    gs = gridspec.GridSpec(4, 4, figure=fig, hspace=0.4, wspace=0.1)

    # 3×4 grid
    for row_idx, row_leads in enumerate(ECG_LAYOUT):
        for col_idx, lead in enumerate(row_leads):
            ax = fig.add_subplot(gs[row_idx, col_idx])
            _render_lead_strip(ax, morph, lead_idx, lead, start, end, fs)

    # Rhythm strip (full width, bottom row)
    ax_rhythm = fig.add_subplot(gs[3, :])
    _render_lead_strip(ax_rhythm, morph, lead_idx, RHYTHM_LEAD, start, end, fs, is_rhythm=True)

    # Speed/gain annotation
    if SHOW_SPEED_GAIN_ANNOTATION:
        fig.text(0.01, 0.02, "25 mm/s  |  10 mm/mV", fontsize=9, color="gray")

    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=100, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return buf.read()


def _render_lead_strip(
    ax,
    morph: np.ndarray,
    lead_idx: dict[str, int],
    lead: str,
    start: int,
    end: int,
    fs: float,
    is_rhythm: bool = False,
) -> None:
    """Render a single lead strip on the given axes."""
    ax.set_facecolor("white")

    # ECG grid
    for x in np.arange(0, (end - start) / fs, 0.04):  # minor: 1 mm at 25 mm/s
        ax.axvline(x, color="#FFCCCC", linewidth=0.3)
    for x in np.arange(0, (end - start) / fs, 0.2):   # major: 5 mm
        ax.axvline(x, color="#FF9999", linewidth=0.6)
    for y in np.arange(-2, 2, 0.1):
        ax.axhline(y, color="#FFCCCC", linewidth=0.3)
    for y in np.arange(-2, 2, 0.5):
        ax.axhline(y, color="#FF9999", linewidth=0.6)

    # Calibration pulse (1 mV, 200 ms) — prepended before signal
    cal_samples = int(CALIBRATION_PULSE_DURATION_MS / 1000 * fs)
    t_cal = np.linspace(-cal_samples / fs, 0, cal_samples)
    cal_signal = np.zeros(cal_samples)
    cal_mid = cal_samples // 2
    cal_signal[cal_mid // 2: cal_mid // 2 + cal_mid] = CALIBRATION_PULSE_MV * 1000  # µV

    if lead in lead_idx:
        sig = morph[lead_idx[lead], start:end].astype(float) / 1000.0  # µV → mV
        t_sig = np.arange(len(sig)) / fs
        ax.plot(t_sig, sig, color="black", linewidth=0.8, antialiased=True)
    else:
        t_sig = np.arange(end - start) / fs
        ax.plot(t_sig, np.zeros(end - start), color="gray", linewidth=0.5)

    # Lead label
    if SHOW_LEAD_LABELS:
        ax.text(0.01, 0.95, lead, transform=ax.transAxes, fontsize=9,
                fontweight="bold", va="top", color="black")

    ax.set_ylim(-2, 2)
    ax.set_xlim(0, (end - start) / fs)
    ax.axis("off")
