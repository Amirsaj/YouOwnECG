"""
Visual narrator — uses vision LLM to describe ECG morphology from images.

Instead of computing mathematical features and classifying shapes,
this renders the actual ECG strip and asks a vision model to describe
what it sees in medical language.

Flow per beat:
  1. Render 4 territory strip images (septal, anterior, lateral, inferior)
  2. Send each to Gemma/GPT-4o with medical prompt
  3. Collect per-lead morphology descriptions
  4. Combine into narration text for the specialist agent
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


def _build_per_lead_measurements_table(features, leads_subset=None) -> str:
    """
    Build a per-lead measurements table from FeatureObject.

    Returns a multi-line text block with one line per lead containing
    R, S, Q, ST elevation/depression, T amplitude, and morphology tags.

    Args:
        features: FeatureObject
        leads_subset: optional list of lead names to include (e.g. just one territory's leads)
    """
    f = features
    leads = leads_subset or list(f.r_amplitude_mv.keys())

    lines = []
    for lead in leads:
        r = f.r_amplitude_mv.get(lead)
        s = f.s_amplitude_mv.get(lead)
        q = f.q_amplitude_mv.get(lead)
        q_dur = f.q_duration_ms.get(lead)
        st_e = f.st_elevation_mv.get(lead)
        st_d = f.st_depression_mv.get(lead)
        j_pt = f.j_point_mv.get(lead) if f.j_point_mv else None
        t_a = f.t_amplitude_mv.get(lead)
        st_morph = f.st_morphology.get(lead, "")
        st_curv = f.st_curvature.get(lead, "") if f.st_curvature else ""
        t_morph = f.t_morphology.get(lead, "")
        qrs_pat = f.qrs_pattern.get(lead, "") if f.qrs_pattern else ""
        path_q = f.pathological_q_wave.get(lead, False) if f.pathological_q_wave else False

        parts = []
        if r is not None:
            parts.append(f"R={_fmt(r)}mV")
        if s is not None and s > 0.05:
            parts.append(f"S={_fmt(s)}mV")
        if q is not None and q > 0.05:
            q_str = f"Q={_fmt(q)}mV"
            if q_dur:
                q_str += f"/{q_dur:.0f}ms"
            if path_q:
                q_str += "(PATH)"
            parts.append(q_str)
        if st_e is not None and st_e > 0.01:
            parts.append(f"ST↑{_fmt(st_e)}mV")
        if st_d is not None and st_d > 0.01:
            parts.append(f"ST↓{_fmt(st_d)}mV")
        if (st_e is None or st_e <= 0.01) and (st_d is None or st_d <= 0.01):
            parts.append("ST=isoelectric")
        if j_pt is not None:
            parts.append(f"J={_fmt(j_pt, '{:+.2f}')}mV")
        if t_a is not None:
            parts.append(f"T={_fmt(t_a, '{:+.2f}')}mV")

        # Morphology tags
        morph_tags = []
        if qrs_pat:
            morph_tags.append(f"QRS:{qrs_pat}")
        if st_morph:
            morph_tags.append(f"ST-slope:{st_morph}")
        if st_curv:
            morph_tags.append(f"ST-curve:{st_curv}")
        if t_morph:
            morph_tags.append(f"T:{t_morph}")

        morph_str = " | ".join(morph_tags) if morph_tags else ""
        meas_str = " | ".join(parts) if parts else "no data"

        lines.append(f"  {lead:>4}: {meas_str}" + (f"  [{morph_str}]" if morph_str else ""))

    return "\n".join(lines)


def _build_global_measurements_block(features, beat_idx: int = None, total_beats: int = None) -> str:
    """Build the global measurements block with disclaimer."""
    f = features
    rr = ""
    if beat_idx is not None and beat_idx > 0 and f.beat_summary.rr_intervals_ms:
        if beat_idx - 1 < len(f.beat_summary.rr_intervals_ms):
            rr_val = f.beat_summary.rr_intervals_ms[beat_idx - 1]
            inst_hr = 60000 / rr_val if rr_val > 0 else None
            rr = f" | RR(prev)={rr_val:.0f}ms"
            if inst_hr:
                rr += f" (inst HR={inst_hr:.0f})"

    bbb_flags = []
    if f.lbbb:
        bbb_flags.append("LBBB")
    if f.rbbb:
        bbb_flags.append("RBBB")
    if f.wpw_pattern:
        bbb_flags.append("WPW")
    bbb_str = " | ".join(bbb_flags) if bbb_flags else "none"

    beat_info = ""
    if beat_idx is not None and total_beats is not None:
        beat_info = f"Beat {beat_idx + 1} of {total_beats}{rr}\n"

    return (
        f"{beat_info}"
        f"Global: HR={_fmt(f.heart_rate_ventricular_bpm, '{:.0f}')}bpm | "
        f"PR={f.pr_interval_ms or '?'}ms | QRS={f.qrs_duration_global_ms or '?'}ms | "
        f"QTc={_fmt(f.qtc_bazett_ms, '{:.0f}')}ms | "
        f"Axis={_fmt(f.qrs_axis_deg, '{:.0f}')}° | Conduction={bbb_str}\n"
        f"Rhythm: {f.dominant_rhythm} ({'regular' if f.rhythm_regular else 'irregular'})"
    )


def _build_bbb_context(features) -> str:
    """If BBB present, return Sgarbossa/discordance context. Else empty string."""
    if not (features.lbbb or features.rbbb):
        return ""

    if features.lbbb:
        return (
            "\n⚠ LBBB CONTEXT — STEMI assessment changes:\n"
            "- Expected DISCORDANT ST changes: V1-V3 ST elevation, V5-V6 ST depression (NORMAL in LBBB)\n"
            "- Sgarbossa criteria for STEMI in LBBB:\n"
            "  • Concordant ST elevation ≥1mm in any lead = STEMI\n"
            "  • Concordant ST depression ≥1mm in V1-V3 = STEMI\n"
            "  • Discordant ST elevation >5mm OR >25% of S-wave depth = STEMI (modified Smith)\n"
            "- Do NOT call expected discordant ST changes 'normal' or 'isoelectric'\n"
            "- Pay attention to whether ST direction matches terminal QRS direction (concordant) or opposes it (discordant)\n"
        )
    else:  # RBBB
        return (
            "\n⚠ RBBB CONTEXT — STEMI assessment changes:\n"
            "- Expected secondary changes only in V1-V3 (ST depression, T inversion)\n"
            "- STEMI criteria still apply normally in lateral (I, aVL, V5-V6) and inferior (II, III, aVF) leads\n"
        )


PIPELINE_DISCLAIMER = """
⚠ DISCLAIMERS for the pipeline measurements above:
- ST elevation/depression values are MEDIANS across all detected beats — THIS specific beat may differ
- Fiducial detection has known errors: P-wave 88% missed, QRS-onset 67% missed, MAE 13-26ms
- Use the pipeline numbers as an ANCHOR but VERIFY VISUALLY against the strip image
- If you see ST changes the pipeline didn't detect (or vice versa), explicitly note the disagreement
- The green dashed line on the image is the isoelectric reference — measure ST relative to it
"""

VISUAL_DESCRIBE_PROMPT = """You are an expert cardiologist. You are given ECG strips for ONE beat across 4 coronary territories on clinical grid paper (25mm/s, 10mm/mV).

Fiducial markers: P (blue↓), Q (gray↓), R (red↑), S (orange↓), J-point (yellow↑), T (purple↓).
Next beat's P₂ and R₂ are also marked. The GREEN DASHED LINE on each strip = isoelectric baseline (PR reference).

You also receive PIPELINE MEASUREMENTS that the signal-processing pipeline already computed for these leads. These are an ANCHOR — verify them visually, agree where correct, flag disagreements where wrong.

For EACH lead in EACH territory, describe the morphology segment by segment:

**P wave**: shape (upright dome / peaked / notched-bifid / inverted / flat / absent), amplitude, duration
**PR segment**: level relative to green baseline
**QRS complex**: pattern (qRs / Rs / rS / QS / RSR' / monophasic-R / delta-wave), width (narrow/wide), R height, S depth, Q if present
**ST segment**: shape AND level relative to GREEN BASELINE (isoelectric / elevated-concave / elevated-convex / elevated-coved / depressed-horizontal / depressed-downsloping / depressed-upsloping / scooped). State millimeters above/below baseline.
**ST-T junction**: continuous or gapped, J-point level vs green baseline
**T wave**: shape (normal-asymmetric / symmetric-inverted / asymmetric-inverted / peaked-narrow / peaked-broad / biphasic-pos-neg / biphasic-neg-pos / notched-bifid / flat), amplitude, symmetry
**Baseline**: stable / wandering / noisy
**Pipeline agreement**: did the pipeline measurement for this lead match what you see? If not, what differs?

CRITICAL RULES:
- Use ONLY descriptive morphology terms. Do NOT name diseases (no "STEMI", "LBBB", "WPW", etc).
- ALWAYS measure ST relative to the GREEN DASHED BASELINE, not relative to zero.
- If the pipeline reports ST elevation/depression in a lead, look HARD at that lead — confirm or refute.
- If you see ST changes the pipeline missed, explicitly state: "Pipeline missed: <lead> shows <description>".
- Be concise — 3-4 lines per lead maximum, but DO mention numbers (mm or mV).

GEOMETRIC POLARITY CONVENTION (supplements the clinical vocabulary above; does NOT replace it):

In addition to the clinical shape descriptors already requested (upright/inverted/biphasic for P and T, etc.), ALWAYS also state the GEOMETRIC position of the dominant deflection relative to the GREEN DASHED BASELINE and its amplitude in mV. The clinical vocabulary remains required for downstream token compatibility (T_INVERTED, P_BIPHASIC_DEEP_V1, ST_ELEVATED, concordant/discordant Sgarbossa logic, etc.); the geometric phrasing is an additive anchor.

For each segment, append a geometry clause to the shape clause:
- P wave: "{shape descriptor — dome / peaked / notched-bifid / flat / inverted / biphasic-pos-neg}; dominant deflection {ABOVE / BELOW / straddling} the green baseline at {±X.XX} mV"
- QRS components: report each component (q, r, s, R', s') as ABOVE or BELOW the green baseline with mV amplitude, in addition to any shape label (rS, QS, Rs, qR, etc.)
- T wave: "{shape — upright / inverted / symmetric-inverted / biphasic-pos-neg / flat}; peak/trough {ABOVE / BELOW} the green baseline at {±X.XX} mV"

Token compatibility: when emitting per-segment flags (the `flags: <TOKEN>; <TOKEN>` line consumed downstream), continue to use the canonical-token vocabulary (P_BIFID_MITRALE, P_PEAKED_PULMONALE, P_BIPHASIC_DEEP_V1, P_FLUTTER_SAWTOOTH, ST_ELEVATED, ST_BORDERLINE_ELEVATED, ST_DEPRESSED, ST_BORDERLINE_DEPRESSED, T_INVERTED, T_HYPERACUTE, PATHOLOGICAL_Q, PACER_SPIKE_BEFORE_P, PACER_SPIKE_BEFORE_QRS). These tokens have fixed downstream meanings and must continue to be emitted on the same beats they would have been emitted before. The geometric clause is additive natural-language context, not a replacement for the token line.

Why: clinical labels depend on lead identity and sign convention; geometry (above / below the green dashed baseline) is invariant to lead-naming or sign-flip artifacts. Adding the geometric anchor lets the reasoner detect sign-flip / electrode-reversal cases without weakening the canonical token pipeline. (Reference: AHA/ACCF/HRS 2007 Recommendations for the Standardization and Interpretation of the ECG — Part I.)
"""


def _get_vision_client():
    """Get vision LLM client — Gemma local first, then OpenAI."""
    try:
        import urllib.request
        urllib.request.urlopen("http://localhost:11434/api/tags", timeout=2)
        from openai import OpenAI
        return OpenAI(base_url=GEMMA_BASE_URL, api_key="local"), GEMMA_MODEL
    except Exception:
        pass

    if os.environ.get("OPENAI_API_KEY"):
        from openai import OpenAI
        return OpenAI(api_key=os.environ["OPENAI_API_KEY"]), "gpt-4o"

    if os.environ.get("GEMINI_API_KEY"):
        return None, "gemini"  # handled separately

    raise ValueError("No vision LLM available. Start GemmaAPI or set OPENAI_API_KEY")


def describe_beat_visually(
    record,
    fiducials,
    features,
    beat_idx: int,
    territories: dict = None,
) -> dict[str, str]:
    """
    Render territory strip images and ask vision LLM to describe each.

    Args:
        record: PreprocessedECGRecord
        fiducials: FiducialTable
        features: FeatureObject
        beat_idx: which beat
        territories: override territory dict. Default = standard 4 territories.

    Returns:
        dict mapping territory name to LLM description text.
        e.g. {"septal": "V1: P upright dome...\nV2: P upright dome...",
              "anterior": "V3: ...\nV4: ...", ...}
    """
    from rl.vision_reward import render_territory_beat_strip, TERRITORIES

    if territories is None:
        territories = TERRITORIES

    client, model = _get_vision_client()

    # Render ALL territory images — measurements are annotated directly on the images
    territory_images = {}
    all_missing = {}
    for territory, info in territories.items():
        result = render_territory_beat_strip(
            record, fiducials, beat_idx, territory, info["leads"], features=features
        )
        if result:
            img_bytes, missing = result
            territory_images[territory] = img_bytes
            if missing:
                all_missing[territory] = missing

    if not territory_images:
        return {"error": "No strips rendered"}

    # Build ONE batched message with ALL 4 territory images
    content = []
    for territory, info in territories.items():
        if territory not in territory_images:
            continue

        b64 = base64.b64encode(territory_images[territory]).decode()
        territory_header = (
            f"\n=== {territory.upper()} ({', '.join(info['leads'])}) — {info['artery']} ==="
        )
        content.append({"type": "text", "text": territory_header})
        if model != "gemini":
            content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/png;base64,{b64}"}
            })

    # Prompt only — no text-based measurement tables (those are on the images)
    content.append({
        "type": "text",
        "text": (
            f"{VISUAL_DESCRIBE_PROMPT}\n\n"
            "Describe EACH of the 4 territories above separately. "
            "Pipeline measurements are annotated on each image — read them from the image "
            "and explicitly confirm or refute each one visually."
        )
    })

    # ONE call with all images
    if model == "gemini":
        descriptions = _call_gemini_batch(territory_images, territories, measurements)
    else:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": content}],
            max_tokens=3000,
        )
        raw_text = response.choices[0].message.content

        # Split response by territory headers
        descriptions = _split_by_territory(raw_text, territories)

    return descriptions


def _split_by_territory(text: str, territories: dict) -> dict:
    """Split a batched response into per-territory sections."""
    descriptions = {}
    territory_names = list(territories.keys())

    # Try splitting by territory headers in the response
    import re
    for i, territory in enumerate(territory_names):
        pattern = re.compile(
            rf'(?:^|\n)\s*(?:\*\*)?{territory.upper()}(?:\*\*)?[\s:(*]',
            re.IGNORECASE
        )
        matches = list(pattern.finditer(text))
        if matches:
            start = matches[0].start()
            # Find end: next territory header or end of text
            end = len(text)
            for next_t in territory_names[i + 1:]:
                next_pattern = re.compile(
                    rf'(?:^|\n)\s*(?:\*\*)?{next_t.upper()}(?:\*\*)?[\s:(*]',
                    re.IGNORECASE
                )
                next_matches = list(next_pattern.finditer(text[start + 1:]))
                if next_matches:
                    end = start + 1 + next_matches[0].start()
                    break
            descriptions[territory] = text[start:end].strip()

    # If parsing failed, return the whole thing under "all"
    if not descriptions:
        descriptions = {territory_names[0]: text}
        for t in territory_names[1:]:
            descriptions[t] = "(see above — response was not split by territory)"

    return descriptions


def _call_gemini_batch(territory_images: dict, territories: dict, measurements: str) -> dict:
    """Batch all territory images into one Gemini call."""
    from google import genai
    from google.genai import types
    import os

    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

    parts = []
    for territory, info in territories.items():
        if territory not in territory_images:
            continue
        parts.append(types.Part.from_text(
            text=f"\n--- {territory.upper()} ({', '.join(info['leads'])}) — {info['artery']} ---"
        ))
        parts.append(types.Part.from_bytes(
            data=territory_images[territory], mime_type="image/png"
        ))

    parts.append(types.Part.from_text(
        text=f"{measurements}\n\nDescribe EACH territory separately.\n\n{VISUAL_DESCRIBE_PROMPT}"
    ))

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[types.Content(role="user", parts=parts)],
        config=types.GenerateContentConfig(max_output_tokens=3000, temperature=0.1),
    )
    return _split_by_territory(response.text, territories)


def _call_gemini_describe(img_b64: str, prompt: str) -> str:
    """Fallback: use Gemini for visual description."""
    from google import genai
    from google.genai import types
    import base64 as b64mod

    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    img_bytes = b64mod.b64decode(img_b64)

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[types.Content(role="user", parts=[
            types.Part.from_bytes(data=img_bytes, mime_type="image/png"),
            types.Part.from_text(text=prompt),
        ])],
        config=types.GenerateContentConfig(max_output_tokens=800, temperature=0.1),
    )
    return response.text


def build_visual_narration(
    record,
    fiducials,
    features,
    max_beats: int = 3,
) -> str:
    """
    Build full narration using vision-based morphology description.

    For each beat: renders 4 territory images → sends to vision LLM →
    collects descriptions → combines into narration text.

    Returns formatted narration string ready for the specialist agent.
    """
    from pipeline.narrator import _global_overview, _rhythm_pattern_summary

    ref_lead = "II" if "II" in fiducials.fpt else list(fiducials.fpt.keys())[0]
    n_beats = min(max_beats, len(fiducials.fpt[ref_lead]))
    rr_intervals = features.beat_summary.rr_intervals_ms or []

    sections = []

    # Global overview (from signal processing — reliable measurements)
    sections.append(_global_overview(features, n_beats))

    # Per-beat visual descriptions
    for beat_i in range(n_beats):
        beat_lines = [f"\n{'='*50}\nBeat {beat_i + 1}/{n_beats}"]

        if beat_i > 0 and beat_i - 1 < len(rr_intervals):
            rr = rr_intervals[beat_i - 1]
            inst_hr = 60000 / rr if rr > 0 else None
            beat_lines.append(f"RR: {rr:.0f} ms" + (f" (HR: {inst_hr:.0f} bpm)" if inst_hr else ""))

        if features.pr_interval_ms is not None:
            beat_lines.append(f"PR interval (global): {features.pr_interval_ms:.0f} ms")

        # Get visual descriptions for all 4 territories
        descriptions = describe_beat_visually(record, fiducials, features, beat_i)

        for territory, desc in descriptions.items():
            beat_lines.append(f"\n  {territory.upper()}:")
            for line in desc.strip().split("\n"):
                beat_lines.append(f"    {line}")

        sections.append("\n".join(beat_lines))

    # Rhythm summary (from signal processing)
    sections.append(_rhythm_pattern_summary(features, rr_intervals))

    return "\n".join(sections)
