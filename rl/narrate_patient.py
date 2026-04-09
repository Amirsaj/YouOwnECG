"""
Dual-agent narration for one patient.

Runs FiducialAgent + MorphologyAgent per segment per beat, then synthesizes
the per-segment morphology reports into a complete clinical ECG narrative.

Usage:
    python3 rl/narrate_patient.py [--ecg_id 210] [--beats 0,1,2] [--model gemma3:12b]
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from validation.ptbxl_mapping import PTBXL_DIR, get_positive_findings
from pipeline.ingestion import load_ecg
from pipeline.preprocessing import preprocess
from pipeline.quality import assess_quality
from pipeline.fiducials import detect_fiducials
from pipeline.features import extract_features
from pipeline.fiducial_correction_agent import run_fiducial_correction


# ── Narrative formatter ────────────────────────────────────────────────────────

def _fmt_per_lead(per_lead: dict, fields: list[str], flag_key: str = "flag") -> str:
    """Format per-lead findings as a compact multi-column block."""
    lines = []
    for lead, data in per_lead.items():
        parts = [f"{lead}:"]
        for f in fields:
            v = data.get(f)
            if v is not None:
                parts.append(f"{f}={v}")
        flag = data.get(flag_key)
        if flag:
            parts.append(f"[{flag}]")
        lines.append("  " + " ".join(str(p) for p in parts))
    return "\n".join(lines)


def format_beat_narration(beat_idx: int, morphology_reports: dict, features) -> str:
    """
    Build a structured clinical narrative for one beat from 3-segment morphology reports.
    """
    sections = [f"=== Beat {beat_idx + 1} ===\n"]

    # ── Global measurements (from features) ───────────────────────────────────
    try:
        sections.append(
            f"Rhythm: {features.dominant_rhythm}  |  "
            f"HR: {features.heart_rate_ventricular_bpm:.0f} bpm  |  "
            f"PR: {features.pr_interval_ms} ms  |  "
            f"QRS: {features.qrs_duration_global_ms} ms  |  "
            f"QTc: {features.qtc_bazett_ms:.0f} ms  |  "
            f"Axis: {features.qrs_axis_deg:.0f}°  |  "
            f"LBBB: {features.lbbb}  RBBB: {features.rbbb}\n"
        )
    except Exception:
        pass

    # ── P-wave ────────────────────────────────────────────────────────────────
    p_rep = morphology_reports.get("p", {})
    if p_rep and "error" not in p_rep:
        sections.append("── P-WAVE ──")
        rhythm_impl = p_rep.get("rhythm_implication", "")
        confidence = p_rep.get("confidence", "")
        findings = p_rep.get("global_findings", [])
        per_lead = p_rep.get("per_lead", {})

        if findings:
            sections.append("  Findings: " + "; ".join(findings))
        if rhythm_impl:
            sections.append(f"  Rhythm implication: {rhythm_impl}")
        if per_lead:
            sections.append("  Per-lead:")
            sections.append(_fmt_per_lead(per_lead, ["shape", "amplitude_mv", "duration_ms"]))
        if confidence:
            sections.append(f"  Confidence: {confidence}")
        sections.append("")

    # ── QRS complex ───────────────────────────────────────────────────────────
    qrs_rep = morphology_reports.get("qrs", {})
    if qrs_rep and "error" not in qrs_rep:
        sections.append("── QRS COMPLEX ──")
        bbb = qrs_rep.get("bbb", "")
        axis = qrs_rep.get("qrs_axis", "")
        findings = qrs_rep.get("global_findings", [])
        per_lead = qrs_rep.get("per_lead", {})

        if findings:
            sections.append("  Findings: " + "; ".join(findings))
        if bbb:
            sections.append(f"  Bundle branch: {bbb}")
        if axis:
            sections.append(f"  Axis: {axis}")
        if per_lead:
            sections.append("  Per-lead:")
            sections.append(_fmt_per_lead(per_lead, ["dominant", "r_mv", "s_mv", "q_mv"]))
        sections.append("")

    # ── ST–T wave ─────────────────────────────────────────────────────────────
    t_rep = morphology_reports.get("t", {})
    if t_rep and "error" not in t_rep:
        sections.append("── ST–T WAVE ──")
        ischemia = t_rep.get("ischemia_territory", "")
        findings = t_rep.get("global_findings", [])
        per_lead = t_rep.get("per_lead", {})
        confidence = t_rep.get("confidence", "")

        if findings:
            sections.append("  Findings: " + "; ".join(findings))
        if ischemia and ischemia != "none":
            sections.append(f"  *** ISCHEMIA TERRITORY: {ischemia.upper()} ***")
        if per_lead:
            sections.append("  Per-lead:")
            sections.append(_fmt_per_lead(per_lead, ["t_direction", "t_amplitude_mv", "st_deviation_mv", "st_shape"]))
        if confidence:
            sections.append(f"  Confidence: {confidence}")
        sections.append("")

    return "\n".join(sections)


def build_full_narration(
    ecg_id: int,
    beat_results: list[dict],
    features,
    ground_truth: list[str],
) -> str:
    """Assemble per-beat sections into a complete ECG narration document."""
    header = [
        f"# ECG Narration — Dual-Agent (FiducialAgent + MorphologyAgent)",
        f"ECG ID: {ecg_id}",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Ground Truth: {ground_truth}",
        "",
        "## Global Summary",
    ]

    try:
        header += [
            f"- Rhythm: {features.dominant_rhythm}",
            f"- Heart Rate: {features.heart_rate_ventricular_bpm:.0f} bpm",
            f"- PR interval: {features.pr_interval_ms} ms",
            f"- QRS duration: {features.qrs_duration_global_ms} ms",
            f"- QTc (Bazett): {features.qtc_bazett_ms:.0f} ms",
            f"- QRS axis: {features.qrs_axis_deg:.0f}°",
            f"- LBBB: {features.lbbb} | RBBB: {features.rbbb} | WPW: {features.wpw_pattern}",
            "",
        ]
        # Shape-based features (wander-resistant, clinically actionable)
        header.append("### Shape Features (pipeline, wander-resistant)")
        st_curv = getattr(features, "st_curvature", None)
        if st_curv:
            convex = [l for l, v in st_curv.items() if v == "convex"]
            concave = [l for l, v in st_curv.items() if v == "concave"]
            if convex:
                header.append(f"- ST convex (STEMI/ischemia shape): {', '.join(convex)}")
            if concave:
                header.append(f"- ST concave (pericarditis/benign shape): {', '.join(concave)}")
        qrs_pat = getattr(features, "qrs_pattern", None)
        if qrs_pat:
            qs_leads = [l for l, v in qrs_pat.items() if v == "QS"]
            frag = [l for l, v in qrs_pat.items() if v == "fragmented"]
            rsrp = [l for l, v in qrs_pat.items() if v == "RSR'"]
            if qs_leads:
                header.append(f"- QS pattern (pathological Q): {', '.join(qs_leads)}")
            if frag:
                header.append(f"- Fragmented QRS: {', '.join(frag)}")
            if rsrp:
                header.append(f"- RSR' pattern (RBBB): {', '.join(rsrp)}")
        t_sym = getattr(features, "t_symmetry_index", None)
        if t_sym:
            sym_leads = [l for l, v in t_sym.items() if v is not None and v >= 0.85]
            asym_leads = [l for l, v in t_sym.items() if v is not None and v < 0.5]
            if sym_leads:
                header.append(f"- Symmetric T (hyperacute/ischemic): {', '.join(sym_leads)}")
            if asym_leads:
                header.append(f"- Asymmetric T (LVH strain/normal): {', '.join(asym_leads)}")
        header.append("")
    except Exception:
        pass

    beat_sections = []
    for br in beat_results:
        beat_sections.append(
            format_beat_narration(br["beat_idx"], br["morphology_reports"], features)
        )

    # Aggregate cross-beat ischemia findings
    all_ischemia = []
    all_global_t = []
    all_global_qrs = []
    all_qrs_flags = []
    _VALID_TERRITORIES = {"inferior", "anterior", "lateral", "posterior"}
    for br in beat_results:
        t_rep = br["morphology_reports"].get("t", {})
        isch = (t_rep.get("ischemia_territory") or "none").lower().strip()
        # Normalise compound values like "inferior/anterior" → primary territory
        if "/" in isch or "+" in isch or "," in isch:
            parts = [p.strip() for p in isch.replace("+", "/").replace(",", "/").split("/")]
            # Prefer inferior > anterior > lateral > posterior
            for pref in ("inferior", "anterior", "lateral", "posterior"):
                if pref in parts:
                    isch = pref
                    break
        if isch in _VALID_TERRITORIES:
            all_ischemia.append(isch)
        all_global_t.extend(t_rep.get("global_findings", []))
        qrs_rep = br["morphology_reports"].get("qrs", {})
        all_global_qrs.extend(qrs_rep.get("global_findings", []))
        # Collect QRS per-lead flags (pathological Q, etc.)
        for lead_data in qrs_rep.get("per_lead", {}).values():
            flag = lead_data.get("flag") if isinstance(lead_data, dict) else None
            if flag and flag not in (None, "null", ""):
                all_qrs_flags.append(flag)

    summary_lines = ["## Cross-Beat Summary"]

    # Shape-based diagnosis (curvature + QRS pattern) — most reliable
    st_curv = getattr(features, "st_curvature", None)
    qrs_pat = getattr(features, "qrs_pattern", None)
    if st_curv:
        inferior_convex = all(st_curv.get(l, "unknown") == "convex" for l in ["II", "aVF"] if l in st_curv)
        anterior_convex = sum(1 for l in ["V1", "V2", "V3"] if st_curv.get(l) == "convex") >= 2
        if inferior_convex:
            summary_lines.append("- SHAPE DIAGNOSIS: Convex ST curvature in inferior leads (II/aVF) → INFERIOR STEMI pattern")
        if anterior_convex:
            summary_lines.append("- SHAPE DIAGNOSIS: Convex ST curvature in anterior leads (V1/V2/V3) → ANTERIOR STEMI pattern")
    if qrs_pat:
        inf_qs = [l for l in ["II", "III", "aVF"] if qrs_pat.get(l) == "QS"]
        if inf_qs:
            summary_lines.append(f"- QS waves in {', '.join(inf_qs)} → pathological Q-waves, inferior MI (established or acute)")

    if all_ischemia:
        most_common = max(set(all_ischemia), key=all_ischemia.count)
        summary_lines.append(f"- Agent ischemia consensus: {most_common.upper()} ({all_ischemia.count(most_common)}/{len(beat_results)} beats)")
    if all_global_t:
        unique_t = list(dict.fromkeys(all_global_t))[:6]
        summary_lines.append(f"- ST/T findings: {'; '.join(unique_t)}")
    if all_global_qrs:
        unique_qrs = list(dict.fromkeys(all_global_qrs))[:6]
        summary_lines.append(f"- QRS findings: {'; '.join(unique_qrs)}")
    summary_lines.append("")

    return "\n".join(header) + "\n".join(summary_lines) + "\n\n## Beat-by-Beat\n\n" + "\n".join(beat_sections)


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ecg_id", type=int, default=210)
    parser.add_argument("--beats", type=str, default="0,1,2,3",
                        help="Comma-separated beat indices to process")
    parser.add_argument("--model", type=str, default="gemma3:12b")
    parser.add_argument("--out_dir", type=str, default=None,
                        help="Output directory (default: rl/judgment/<disease>_patient_<id>/)")
    args = parser.parse_args()

    beat_indices = [int(b.strip()) for b in args.beats.split(",")]
    eid = args.ecg_id

    print(f"\nDual-agent narration — ECG {eid} | beats {beat_indices} | model {args.model}")

    # ── Load ──
    subfolder = f"{(eid - 1) // 1000 * 1000:05d}"
    hea = str(PTBXL_DIR / f"records500/{subfolder}/{eid:05d}_hr.hea")
    raw = load_ecg(hea, ecg_id=str(eid))
    prep = preprocess(raw)
    qual = assess_quality(prep)
    fid = detect_fiducials(prep, qual)
    feats = extract_features(prep, qual, fid)

    print(f"  Beats in recording: {fid.n_beats}")
    beat_indices = [b for b in beat_indices if b < fid.n_beats]
    print(f"  Processing: {beat_indices}")

    # Ground truth
    ground_truth = []
    try:
        import ast, pandas as pd
        df = pd.read_csv(PTBXL_DIR / "ptbxl_database.csv")
        row = df[df.ecg_id == eid].iloc[0]
        scp = ast.literal_eval(row["scp_codes"])
        ground_truth = sorted(get_positive_findings(scp, min_likelihood=50.0))
    except Exception as e:
        print(f"  GT lookup failed: {e}")

    # ── Output directory ──
    if args.out_dir:
        out_dir = Path(args.out_dir)
    else:
        judgment_dir = Path(__file__).parent / "judgment"
        candidates = list(judgment_dir.glob(f"*_patient_{eid}"))
        out_dir = candidates[0] if candidates else judgment_dir / f"patient_{eid}"
    out_dir.mkdir(parents=True, exist_ok=True)

    # ── Run dual-agent per beat ──
    beat_results = []
    for beat_idx in beat_indices:
        print(f"\n{'='*50}\nBeat {beat_idx + 1}/{fid.n_beats}\n{'='*50}")
        workflow_log = str(out_dir / f"workflow_beat{beat_idx + 1}.jsonl")
        corrected_fid, changes, morph_reports = run_fiducial_correction(
            prep, fid, feats, beat_idx=beat_idx, model=args.model,
            workflow_log_path=workflow_log,
        )
        print(f"  Workflow log: {workflow_log}")
        # Use corrected fiducials for next beats
        fid = corrected_fid
        beat_results.append({
            "beat_idx": beat_idx,
            "changes": changes,
            "morphology_reports": morph_reports,
        })
        print(f"  Beat {beat_idx + 1}: {len(changes)} corrections | "
              f"morph segments: {list(morph_reports.keys())}")

    # ── Build narration ──
    narration = build_full_narration(eid, beat_results, feats, ground_truth)

    # ── Save ──
    narration_path = out_dir / "dual_agent_narration.md"
    narration_path.write_text(narration)
    print(f"\n{'='*50}")
    print(f"Narration saved to: {narration_path}")

    raw_path = out_dir / "dual_agent_morph_raw.json"
    raw_path.write_text(json.dumps(beat_results, indent=2, default=str))
    print(f"Raw JSON saved to: {raw_path}")

    print("\n--- NARRATION PREVIEW ---")
    print(narration[:3000])


if __name__ == "__main__":
    main()
