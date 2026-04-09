"""
Segment-specific vision agents for ECG shape classification.

Each segment (P, QRS, ST, T) has its own specialized agent prompt that
contains ALL the medical knowledge about possible shapes for that segment.
When classifying, the strip image is sent to Gemma with the segment-specific
prompt, and Gemma returns a shape classification + description.
"""

from __future__ import annotations
import base64
import os
from typing import Optional


GEMMA_BASE_URL = "http://localhost:11434/v1"
GEMMA_MODEL = os.environ.get("GEMMA_MODEL", "gemma3:27b")


def _fmt(val, fmt="{:.2f}"):
    """Safe format that handles None."""
    if val is None:
        return "?"
    try:
        return fmt.format(val)
    except (ValueError, TypeError):
        return str(val)


def _build_segment_lead_measurements(features, segment: str, lead: str) -> str:
    """
    Build segment-specific pipeline measurements for ONE lead.

    Returns a markdown-formatted block with only the measurements relevant
    to the specified segment (P, QRS, ST, T) in the specified lead.
    """
    if not features:
        return ""

    f = features
    lines = [f"PIPELINE MEASUREMENTS for lead {lead} (median across all detected beats — verify visually):"]

    if segment == "P":
        # P-wave fields are global only (not per-lead)
        p_dur = getattr(f, "p_duration_ms", None)
        p_amp = getattr(f, "p_amplitude_mv", None)
        pr = f.pr_interval_ms
        p_axis = getattr(f, "p_axis_deg", None)
        p_present = getattr(f, "p_wave_present", None)
        if p_amp is not None:
            lines.append(f"  • P amplitude (global): {_fmt(p_amp, '{:+.2f}')} mV")
        if p_dur is not None:
            lines.append(f"  • P duration (global): {p_dur:.0f} ms")
        if pr is not None:
            lines.append(f"  • PR interval (global): {pr} ms")
        if p_axis is not None:
            lines.append(f"  • P axis (global): {p_axis:.0f}°")
        if p_present is False:
            lines.append(f"  • Pipeline flag: P-wave NOT consistently detected (possible AFib/junctional)")

    elif segment == "QRS":
        r = f.r_amplitude_mv.get(lead)
        s = f.s_amplitude_mv.get(lead)
        q = f.q_amplitude_mv.get(lead)
        q_dur = f.q_duration_ms.get(lead) if f.q_duration_ms else None
        qrs_pat = f.qrs_pattern.get(lead, "") if f.qrs_pattern else ""
        path_q = f.pathological_q_wave.get(lead, False) if f.pathological_q_wave else False
        if r is not None:
            lines.append(f"  • R amplitude: {_fmt(r)} mV")
        if s is not None:
            lines.append(f"  • S amplitude: {_fmt(s)} mV")
        if q is not None and q > 0.05:
            q_str = f"  • Q amplitude: {_fmt(q)} mV"
            if q_dur:
                q_str += f" / {q_dur:.0f} ms"
            if path_q:
                q_str += " ← FLAGGED PATHOLOGICAL"
            lines.append(q_str)
        if f.qrs_duration_global_ms is not None:
            lines.append(f"  • QRS duration (global): {f.qrs_duration_global_ms} ms")
        if f.qrs_axis_deg is not None:
            lines.append(f"  • QRS axis (global): {f.qrs_axis_deg:.0f}°")
        if qrs_pat:
            lines.append(f"  • QRS pattern (computed): {qrs_pat}")
        bbb_flags = []
        if f.lbbb:
            bbb_flags.append("LBBB")
        if f.rbbb:
            bbb_flags.append("RBBB")
        if f.wpw_pattern:
            bbb_flags.append("WPW")
        if bbb_flags:
            lines.append(f"  • Conduction flags: {', '.join(bbb_flags)}")

    elif segment == "ST":
        st_e = f.st_elevation_mv.get(lead)
        st_d = f.st_depression_mv.get(lead)
        j_pt = f.j_point_mv.get(lead) if f.j_point_mv else None
        st_morph = f.st_morphology.get(lead, "")
        st_curv = f.st_curvature.get(lead, "") if f.st_curvature else ""
        concordance = f.concordance_analysis.get(lead, "") if f.concordance_analysis else ""
        # Need QRS direction context for concordance interpretation
        r = f.r_amplitude_mv.get(lead)
        s = f.s_amplitude_mv.get(lead)
        if st_e is not None and st_e > 0.01:
            lines.append(f"  • ST elevation: ↑{_fmt(st_e)} mV")
        if st_d is not None and st_d > 0.01:
            lines.append(f"  • ST depression: ↓{_fmt(st_d)} mV")
        if (st_e is None or st_e <= 0.01) and (st_d is None or st_d <= 0.01):
            lines.append("  • ST level: isoelectric (within ±0.01 mV)")
        if j_pt is not None:
            lines.append(f"  • J-point level: {_fmt(j_pt, '{:+.2f}')} mV vs PR baseline")
        if st_morph:
            lines.append(f"  • ST slope (computed): {st_morph}")
        if st_curv:
            lines.append(f"  • ST curvature (computed): {st_curv}")
        if r is not None and s is not None:
            qrs_dir = "POSITIVE" if r > s else "NEGATIVE"
            lines.append(f"  • Terminal QRS direction in this lead: {qrs_dir} (R={_fmt(r)}, S={_fmt(s)})")
        if concordance:
            lines.append(f"  • Pipeline concordance flag: {concordance.upper()} (ST direction vs terminal QRS)")
        bbb_flags = []
        if f.lbbb:
            bbb_flags.append("LBBB")
        if f.rbbb:
            bbb_flags.append("RBBB")
        if bbb_flags:
            lines.append(f"  • Conduction: {', '.join(bbb_flags)} → expect SECONDARY ST changes (read BBB block below)")

    elif segment == "T":
        t_a = f.t_amplitude_mv.get(lead)
        t_morph = f.t_morphology.get(lead, "")
        t_qrs = f.t_qrs_ratio.get(lead) if hasattr(f, "t_qrs_ratio") and f.t_qrs_ratio else None
        t_sym = f.t_symmetry_index.get(lead) if hasattr(f, "t_symmetry_index") and f.t_symmetry_index else None
        sym_inv = f.symmetric_t_inversion.get(lead, False) if hasattr(f, "symmetric_t_inversion") and f.symmetric_t_inversion else False
        r = f.r_amplitude_mv.get(lead)
        s = f.s_amplitude_mv.get(lead)
        if t_a is not None:
            lines.append(f"  • T amplitude: {_fmt(t_a, '{:+.2f}')} mV")
        if t_qrs is not None:
            lines.append(f"  • T/QRS ratio: {t_qrs:.2f}")
        if t_sym is not None:
            lines.append(f"  • T symmetry index: {t_sym:.2f} (1.0 = symmetric)")
        if t_morph:
            lines.append(f"  • T morphology (computed): {t_morph}")
        if sym_inv:
            lines.append(f"  • Symmetric T inversion: FLAGGED")
        if r is not None and s is not None:
            qrs_dir = "POSITIVE" if r > s else "NEGATIVE"
            lines.append(f"  • Terminal QRS direction in this lead: {qrs_dir}")
        if f.qtc_bazett_ms is not None:
            lines.append(f"  • QTc Bazett (global): {f.qtc_bazett_ms:.0f} ms")
        bbb_flags = []
        if f.lbbb:
            bbb_flags.append("LBBB")
        if f.rbbb:
            bbb_flags.append("RBBB")
        if bbb_flags:
            lines.append(f"  • Conduction: {', '.join(bbb_flags)} → expect SECONDARY T changes")

    if len(lines) == 1:
        return ""
    return "\n".join(lines)


def _build_bbb_context_for_segment(features, segment: str) -> str:
    """
    BBB context block — only injected for ST and T agents (where BBB matters most).

    The Sgarbossa false-positive in the prior comparison happened because the LLM
    didn't understand that ST changes opposite to terminal QRS are EXPECTED in LBBB.
    This block makes that crystal clear.
    """
    if not features or not (features.lbbb or features.rbbb):
        return ""
    if segment not in ("ST", "T", "QRS"):
        return ""

    if features.lbbb:
        if segment == "ST":
            return (
                "\n⚠ CRITICAL — LBBB IS PRESENT. ST INTERPRETATION CHANGES:\n"
                "Normal LBBB pattern (NOT pathology — do NOT call these abnormal):\n"
                "  • V1-V3 (deep S wave, NEGATIVE QRS): ST ELEVATION is EXPECTED (discordant)\n"
                "  • V5-V6, I, aVL (tall R wave, POSITIVE QRS): ST DEPRESSION is EXPECTED (discordant)\n"
                "  • Discordance = ST direction OPPOSITE to terminal QRS direction = NORMAL in LBBB\n\n"
                "Sgarbossa criteria (the ONLY way to call STEMI in LBBB):\n"
                "  • Concordant ST elevation ≥1mm in any lead (ST UP where QRS is also UP) = STEMI\n"
                "  • Concordant ST depression ≥1mm in V1-V3 (ST DOWN where QRS is also DOWN) = STEMI\n"
                "  • Discordant ST elevation >5mm OR >25% of S-wave depth = STEMI (Smith-modified)\n\n"
                "BEFORE flagging Sgarbossa-positive: check the QRS direction line in the measurements above.\n"
                "If terminal QRS is NEGATIVE and ST is ELEVATED → that is DISCORDANT (expected, NOT Sgarbossa).\n"
                "If terminal QRS is POSITIVE and ST is ELEVATED → that is CONCORDANT (potential Sgarbossa+).\n"
            )
        elif segment == "T":
            return (
                "\n⚠ LBBB CONTEXT — T-wave interpretation:\n"
                "Discordant T waves (opposite to terminal QRS) are EXPECTED in LBBB:\n"
                "  • V1-V3: upright T waves are normal secondary change\n"
                "  • V5-V6, I, aVL: inverted T waves are normal secondary change\n"
                "Concordant T inversion (T inverted where QRS is also negative) may indicate ischemia.\n"
            )
        elif segment == "QRS":
            return (
                "\n⚠ LBBB CONTEXT — expected QRS morphology:\n"
                "  • Wide QRS ≥120ms\n"
                "  • V1: deep QS or rS (no R-wave or tiny r)\n"
                "  • V5-V6, I, aVL: broad notched/slurred monophasic R, NO septal q-wave\n"
                "  • Look for fragmented/notched R (slurred upstroke) — characteristic of LBBB\n"
            )

    if features.rbbb:
        if segment == "QRS":
            return (
                "\n⚠ RBBB CONTEXT — expected QRS morphology:\n"
                "  • Wide QRS ≥120ms\n"
                "  • V1-V2: rSR' (M-shaped) with R' usually taller than R\n"
                "  • V5-V6, I, aVL: broad terminal S wave (slurred)\n"
            )
        elif segment in ("ST", "T"):
            return (
                f"\n⚠ RBBB CONTEXT — secondary {segment} changes expected in V1-V3 only:\n"
                "  • Discordant ST depression and T inversion in V1-V3 are NORMAL secondary changes\n"
                "  • STEMI/ischemia criteria still apply normally in lateral and inferior leads\n"
            )

    return ""


SEGMENT_VERIFY_INSTRUCTION = """
PIPELINE VERIFICATION INSTRUCTIONS:
- The pipeline measurements above are an ANCHOR. Verify them against the strip.
- If you AGREE with a pipeline number, mention it explicitly: e.g. "Pipeline ST↑0.14mV in V3 — confirmed visually".
- If you DISAGREE, flag it: e.g. "Pipeline says isoelectric but I see 1mm ST elevation — DISAGREE".
- Pipeline ST values are MEDIANS across all beats, so this specific beat may differ.
- Fiducial detection has known errors (P 88% missed, QRS-on 67% missed, MAE 13-26ms) — trust your eyes for fiducial placement.
- The green dashed line on the image is the isoelectric (PR) reference. Measure ST relative to IT, not zero.
"""


# ── P-WAVE AGENT ──────────────────────────────────────────────────────────

P_WAVE_AGENT = """You are the P-WAVE SPECIALIST. Analyze ONLY the P-wave in this ECG strip.

The P-wave is the first small deflection BEFORE the QRS complex, marked with a blue (P) label.
It represents atrial depolarization.

POSSIBLE P-WAVE SHAPES (pick the one that best matches):

P1 — Normal Upright: smooth dome shape, amplitude 0.05-0.25 mV, duration 80-120ms
  → Normal sinus rhythm

P2 — P-Pulmonale (Peaked): tall (>0.25 mV), narrow base, sharp apex
  → Right atrial enlargement, cor pulmonale, COPD

P3 — P-Mitrale (Notched/Bifid): M-shaped with TWO humps, duration >120ms, notch between peaks
  → Left atrial enlargement, mitral stenosis

P4 — Inverted: single negative peak below baseline
  → Ectopic atrial rhythm, junctional rhythm, or normal in aVR

P5 — Biphasic: initial upright + terminal negative component (especially in V1)
  → Left atrial enlargement (terminal negative force >1mm deep x 1mm wide)

P6 — Flat/Absent: amplitude <0.05 mV, essentially no visible P-wave
  → Atrial fibrillation, severe hyperkalemia, junctional rhythm

P7 — Buried in T: P-wave distorts the preceding T-wave, not independently visible
  → SVT, atrial flutter, atrial tachycardia

For EACH lead visible in this strip, describe the P-wave separately:

LEAD: [lead name]
SHAPE: P[1-7]
NAME: [shape name]
AMPLITUDE: [estimated in mV]
DURATION: [estimated in ms]
POLARITY: [upright/inverted/biphasic/flat]
DESCRIPTION: [what you see in THIS lead specifically]
CONFIDENCE: [HIGH/MEDIUM/LOW]

(Repeat for each lead in the strip)
"""


# ── QRS AGENT ─────────────────────────────────────────────────────────────

QRS_AGENT = """You are the QRS COMPLEX SPECIALIST. Analyze ONLY the QRS complex in this ECG strip.

The QRS complex is the large deflection in the middle, marked with Q (gray), R (red), S (orange) labels.
It represents ventricular depolarization.

POSSIBLE QRS SHAPES (pick the one that best matches):

Q1 — qRs (Normal): small q-wave (<40ms), dominant R, small s
  → Normal septal depolarization

Q2 — Rs: tall R + small s, no initial q-wave
  → Normal variant

Q3 — rS: small r + deep S (S dominates)
  → Normal in V1-V2, or LBBB pattern

Q4 — QS: entirely negative, NO R-wave at all
  → Old transmural MI, or LBBB in V1

Q5 — RSR' (M-shaped): TWO positive peaks (R then R') with S valley between
  → RBBB pattern (especially V1-V2)

Q6 — Monophasic R: single broad positive deflection, no S, often notched
  → LBBB in lateral leads (I, aVL, V5-V6)

Q7 — Delta Wave: slurred/slow initial upstroke, QRS wide (>110ms)
  → WPW pre-excitation

Q8 — Fragmented: multiple notches/deflections within QRS (>4 extra peaks)
  → Prior MI scar, cardiomyopathy

Q9 — Pathological Q: deep (>25% of R) or wide (>40ms) initial negative
  → Old myocardial infarction

Q10 — Wide Non-specific: QRS >120ms without BBB morphology
  → Hyperkalemia, drug toxicity

Q11 — Low Voltage: very small QRS (<0.5mV limb, <1.0mV precordial)
  → Pericardial effusion, obesity, COPD

Q12 — Epsilon Wave: small positive notch AFTER QRS offset, before T
  → ARVC

For EACH lead visible in this strip, describe the QRS separately:

LEAD: [lead name]
SHAPE: Q[1-12]
NAME: [shape name]
WIDTH: [narrow (<120ms) / wide (≥120ms)]
R_AMPLITUDE: [estimated in mV]
S_AMPLITUDE: [estimated in mV]
PATTERN: [specific pattern like rSR', qRs, QS, etc.]
DESCRIPTION: [what you see in THIS lead specifically]
CONFIDENCE: [HIGH/MEDIUM/LOW]

(Repeat for each lead in the strip)
"""


# ── ST SEGMENT AGENT ──────────────────────────────────────────────────────

ST_AGENT = """You are the ST SEGMENT SPECIALIST. Analyze ONLY the ST segment in this ECG strip.

The ST segment runs from the J-point (yellow marker, end of QRS) to the T-wave onset.
Compare the ST level to the GREEN DASHED BASELINE (isoelectric PR reference).

POSSIBLE ST SHAPES (pick the one that best matches):

ST1 — Isoelectric: flat, ON the green baseline (±0.5mm)
  → Normal

ST2 — Concave-Up Elevation (Smiley): curves UPWARD like a smile, elevated above baseline
  → Early repolarization, pericarditis (benign patterns)

ST3 — Convex Elevation (Frowning/Tombstone): curves DOWNWARD at top, dome-shaped, above baseline
  → Acute STEMI (dangerous pattern!)

ST4 — Coved: convex dome that descends smoothly into inverted T (no gap)
  → Brugada Type 1 (V1-V2 only)

ST5 — Horizontal Depression: flat BELOW the green baseline
  → Demand ischemia, subendocardial ischemia

ST6 — Downsloping Depression: slopes DOWN from J-point, below baseline
  → LVH strain, digitalis effect

ST7 — Upsloping Depression: J-point is BELOW baseline but slopes UP toward tall T
  → de Winter pattern (STEMI equivalent!) — must be combined with tall T

ST8 — Scooped (Reverse Checkmark): concave-down depression curving into inverted T
  → Digitalis effect

CRITICAL: Measure ST level relative to the GREEN DASHED BASELINE, NOT relative to zero.
The J-point (yellow marker) may be above or below zero due to the preceding S-wave depth.

CRITICAL — CONCORDANCE vs DISCORDANCE (for BBB cases):
- DISCORDANT = ST direction OPPOSITE to terminal QRS direction (NORMAL in LBBB/RBBB)
- CONCORDANT = ST direction SAME as terminal QRS direction (ABNORMAL — Sgarbossa+ in LBBB)
- Before calling Sgarbossa-positive depression in V1-V3, check that QRS is NEGATIVE there
  AND that the ST is also pointing DOWN (not just elevated above a deeply depressed J-point)

For EACH lead visible in this strip, describe the ST segment separately:

LEAD: [lead name]
SHAPE: ST[1-8]
NAME: [shape name]
J_POINT_LEVEL: [mm above or below green baseline]
CURVATURE: [concave-up / convex / linear / coved / scooped]
DESCRIPTION: [what you see in THIS lead specifically]
CONFIDENCE: [HIGH/MEDIUM/LOW]

(Repeat for each lead in the strip)
"""


# ── T-WAVE AGENT ──────────────────────────────────────────────────────────

T_WAVE_AGENT = """You are the T-WAVE SPECIALIST. Analyze ONLY the T-wave in this ECG strip.

The T-wave is the deflection AFTER the ST segment, marked with a purple (T) label.
It represents ventricular repolarization.

POSSIBLE T-WAVE SHAPES (pick the one that best matches):

T1 — Normal Upright: asymmetric dome (slow rise, quick fall), 0.1-0.5mV
  → Normal repolarization

T2 — Hyperacute (STEMI): tall, BROAD-based (>200ms wide), symmetric
  → Early acute STEMI, de Winter. KEY: BROAD base distinguishes from hyperkalemia

T3 — Peaked Tented (Hyperkalemia): tall, NARROW-based (<160ms), sharp point like a tent
  → Hyperkalemia. KEY: NARROW base + sharp apex distinguishes from STEMI hyperacute

T4 — Deep Symmetric Inversion: inverted V-shape, both limbs similar slope
  → Wellens Type B (V2-V3), NSTEMI, post-STEMI

T5 — Asymmetric Inversion (Strain): slow descent + rapid return, inverted
  → LVH strain (lateral leads), RVH strain (V1-V4)

T6 — Biphasic Pos-Neg (Wellens A): starts positive then crosses to negative
  → Wellens Type A (V2-V3), critical LAD lesion

T7 — Biphasic Neg-Pos: starts negative then crosses to positive
  → Less common ischemia variant

T8 — Notched/Bifid: TWO humps (double-peaked) same polarity, notch between
  → LQT2 (hERG mutation)

T9 — Flat: minimal deflection (<0.05mV)
  → Ischemia, hypokalemia, hypothyroidism

T10 — Giant Inversion: very deep (>1.0mV), symmetric, widespread
  → Apical HCM (Yamaguchi syndrome)

T11 — T-wave Alternans: amplitude alternates beat-to-beat (compare with next beat)
  → Imminent TdP risk (STAT!)

T12 — Juvenile Pattern: inverted in V1-V3, normal in young patients (<25 years)
  → Normal age-dependent variant

T13 — de Winter T: tall symmetric peaked, paired with upsloping ST depression
  → de Winter pattern. MUST have ST depression too (combined ST+T pattern)

T14 — Concordant/Discordant (BBB): T direction relative to terminal QRS
  → Concordant = concerning in BBB. Discordant = expected secondary change

CRITICAL for distinguishing T2 vs T3:
- T2 (STEMI hyperacute): BROAD base, amplitude/width ratio LOW
- T3 (Hyperkalemia peaked): NARROW base, amplitude/width ratio HIGH, sharp tent-like apex

For EACH lead visible in this strip, describe the T-wave separately:

LEAD: [lead name]
SHAPE: T[1-14]
NAME: [shape name]
AMPLITUDE: [estimated in mV, positive or negative]
WIDTH: [estimated in ms]
SYMMETRY: [symmetric / asymmetric (which limb longer?)]
POLARITY: [upright / inverted / biphasic / flat]
DESCRIPTION: [what you see in THIS lead specifically]
CONFIDENCE: [HIGH/MEDIUM/LOW]

(Repeat for each lead in the strip)
"""


SEGMENT_AGENTS = {
    "P": P_WAVE_AGENT,
    "QRS": QRS_AGENT,
    "ST": ST_AGENT,
    "T": T_WAVE_AGENT,
}


def classify_shape_with_vision(
    image_bytes: bytes,
    segment: str,
    lead: str,
    beat_idx: int,
    measurements: str = "",
    features=None,
) -> dict:
    """
    Send a strip image to Gemma with segment-specific agent prompt.

    Args:
        image_bytes: PNG strip image
        segment: "P" | "QRS" | "ST" | "T"
        lead: lead name (e.g. "V1")
        beat_idx: zero-indexed beat
        measurements: legacy free-text measurements (kept for backward compat)
        features: FeatureObject — if provided, segment-specific pipeline numbers
                  + BBB context will be injected into the prompt as an anchor

    Returns dict with: shape, name, description, confidence, raw_response
    """
    agent_prompt = SEGMENT_AGENTS.get(segment)
    if not agent_prompt:
        return {"error": f"Unknown segment: {segment}"}

    try:
        import urllib.request
        urllib.request.urlopen("http://localhost:11434/api/tags", timeout=2)
    except Exception:
        return {"error": "Gemma not running. Start with ./GemmaAPI/start.sh"}

    from openai import OpenAI
    client = OpenAI(base_url=GEMMA_BASE_URL, api_key="local")

    b64 = base64.b64encode(image_bytes).decode()

    # Measurements are annotated directly on the image — no text injection
    prompt = (
        f"Lead: {lead} | Beat: {beat_idx + 1} | Segment: {segment}\n"
        f"{measurements}\n\n"
        f"{agent_prompt}"
    )

    response = client.chat.completions.create(
        model=GEMMA_MODEL,
        messages=[{
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}},
                {"type": "text", "text": prompt},
            ]
        }],
        max_tokens=500,
    )

    raw = response.choices[0].message.content

    # Parse response — extract per-lead results
    result = {"raw_response": raw, "segment": segment, "lead": lead, "beat": beat_idx}

    # Parse multiple leads
    leads_parsed = []
    current_lead = {}
    for line in raw.split("\n"):
        line = line.strip()
        if line.startswith("LEAD:"):
            if current_lead.get("lead"):
                leads_parsed.append(current_lead)
            current_lead = {"lead": line.split(":", 1)[1].strip()}
        elif line.startswith("SHAPE:"):
            current_lead["shape"] = line.split(":", 1)[1].strip()
        elif line.startswith("NAME:"):
            current_lead["name"] = line.split(":", 1)[1].strip()
        elif line.startswith("CONFIDENCE:"):
            current_lead["confidence"] = line.split(":", 1)[1].strip()
        elif line.startswith("DESCRIPTION:"):
            current_lead["description"] = line.split(":", 1)[1].strip()
        elif line.startswith("AMPLITUDE:"):
            current_lead["amplitude"] = line.split(":", 1)[1].strip()
        elif line.startswith("DURATION:") or line.startswith("WIDTH:"):
            current_lead["duration"] = line.split(":", 1)[1].strip()
        elif line.startswith("POLARITY:"):
            current_lead["polarity"] = line.split(":", 1)[1].strip()
        elif line.startswith("SYMMETRY:"):
            current_lead["symmetry"] = line.split(":", 1)[1].strip()
        elif line.startswith("PATTERN:"):
            current_lead["pattern"] = line.split(":", 1)[1].strip()
        elif line.startswith("R_AMPLITUDE:"):
            current_lead["r_amplitude"] = line.split(":", 1)[1].strip()
        elif line.startswith("S_AMPLITUDE:"):
            current_lead["s_amplitude"] = line.split(":", 1)[1].strip()
        elif line.startswith("J_POINT_LEVEL:"):
            current_lead["j_point"] = line.split(":", 1)[1].strip()
        elif line.startswith("CURVATURE:"):
            current_lead["curvature"] = line.split(":", 1)[1].strip()

    if current_lead.get("lead"):
        leads_parsed.append(current_lead)

    result["leads"] = leads_parsed

    # Also set top-level from first lead for backward compat
    if leads_parsed:
        first = leads_parsed[0]
        result["shape"] = first.get("shape")
        result["name"] = first.get("name")
        result["confidence"] = first.get("confidence")
        result["description"] = first.get("description")

    return result
