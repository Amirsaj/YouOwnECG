"""
Side-by-side comparison of pipeline narration vs Claude Vision assessment.

Runs a single ECG record through both paths and displays results for human review.
"""

from __future__ import annotations
import csv
import sys
import time
from pathlib import Path
from typing import Optional

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from validation.ptbxl_mapping import PTBXL_DIR, get_positive_findings
from pipeline.ingestion import load_ecg
from pipeline.preprocessing import preprocess
from pipeline.quality import assess_quality
from pipeline.fiducials import detect_fiducials
from pipeline.features import extract_features
from pipeline.narrator import narrate_ecg
from agents.signal_findings import generate_signal_findings

RESULTS_DIR = Path(__file__).parent / "comparisons"
RESULTS_DIR.mkdir(exist_ok=True)


def run_pipeline_narration(ecg_id: int) -> dict:
    """
    Run full pipeline on a PTB-XL record and return narration + findings.

    Returns dict with: narration, findings, features, record, fiducials, quality, scp_codes
    """
    subfolder = f"{(ecg_id - 1) // 1000 * 1000:05d}"
    hea_path = str(PTBXL_DIR / f"records500/{subfolder}/{ecg_id:05d}_hr.hea")

    raw = load_ecg(hea_path, ecg_id=str(ecg_id))
    prep = preprocess(raw)
    qual = assess_quality(prep)
    fid = detect_fiducials(prep, qual)
    feats = extract_features(prep, qual, fid)

    narration = narrate_ecg(prep, fid, feats)
    findings = generate_signal_findings(feats)

    return {
        "narration": narration,
        "findings": findings,
        "features": feats,
        "record": prep,
        "fiducials": fid,
        "quality": qual,
    }


def run_claude_assessment(record, fiducials, features, client=None) -> str:
    """Run Claude Vision assessment on the same record."""
    from rl.vision_reward import get_claude_visual_assessment
    return get_claude_visual_assessment(record, fiducials, features, client=client)


def format_findings(findings) -> str:
    """Format findings list as readable text."""
    if not findings:
        return "  (no findings)"
    lines = []
    for f in findings:
        lines.append(f"  - {f.finding_type} ({f.confidence}): {f.clinical_summary}")
    return "\n".join(lines)


def format_key_measurements(features) -> str:
    """Format key measurements as readable text."""
    f = features
    lines = [
        f"  HR: {f.heart_rate_ventricular_bpm:.0f} bpm" if f.heart_rate_ventricular_bpm else "  HR: None",
        f"  PR: {f.pr_interval_ms} ms" if f.pr_interval_ms else "  PR: None",
        f"  QRS: {f.qrs_duration_global_ms} ms" if f.qrs_duration_global_ms else "  QRS: None",
        f"  QTc: {f.qtc_bazett_ms:.0f} ms" if f.qtc_bazett_ms else "  QTc: None",
        f"  Axis: {f.qrs_axis_deg:.0f}°" if f.qrs_axis_deg else "  Axis: None",
        f"  Rhythm: {f.dominant_rhythm} ({'regular' if f.rhythm_regular else 'irregular'})",
        f"  LBBB: {f.lbbb}  RBBB: {f.rbbb}  WPW: {f.wpw_pattern}",
        f"  Quality: {f.beat_summary.n_beats} beats detected",
    ]
    return "\n".join(lines)


def compare_record(
    ecg_id: int,
    ground_truth_scp: Optional[dict] = None,
    claude_client=None,
    skip_claude: bool = False,
) -> dict:
    """
    Run both pipeline and Claude narrations on one record.
    Returns dict with all data for human review.
    """
    print(f"\n{'='*80}")
    print(f" ECG RECORD: {ecg_id}")
    print(f"{'='*80}")

    # Ground truth
    if ground_truth_scp:
        gt_findings = get_positive_findings(ground_truth_scp, min_likelihood=50.0)
        print(f"\nGROUND TRUTH (PTB-XL): {', '.join(gt_findings) if gt_findings else 'NORM'}")
    else:
        gt_findings = set()

    # Pipeline
    print("\n--- Running pipeline ---")
    t0 = time.time()
    pipeline = run_pipeline_narration(ecg_id)
    t_pipeline = time.time() - t0
    print(f"Pipeline completed in {t_pipeline:.1f}s")

    print(f"\n{'─'*40}")
    print("KEY MEASUREMENTS:")
    print(format_key_measurements(pipeline["features"]))
    print(f"\nPIPELINE FINDINGS:")
    print(format_findings(pipeline["findings"]))

    print(f"\n{'─'*40}")
    print("PIPELINE NARRATION:")
    print(f"{'─'*40}")
    print(pipeline["narration"])

    # Claude
    claude_text = None
    if not skip_claude:
        print(f"\n{'─'*40}")
        print("--- Running Claude Vision ---")
        t0 = time.time()
        try:
            claude_text = run_claude_assessment(
                pipeline["record"], pipeline["fiducials"],
                pipeline["features"], client=claude_client,
            )
            t_claude = time.time() - t0
            print(f"Claude completed in {t_claude:.1f}s")
        except Exception as e:
            print(f"Claude error: {e}")
            claude_text = f"ERROR: {e}"

        print(f"\n{'─'*40}")
        print("CLAUDE VISION ASSESSMENT:")
        print(f"{'─'*40}")
        print(claude_text)

    result = {
        "ecg_id": ecg_id,
        "ground_truth": gt_findings,
        "pipeline_narration": pipeline["narration"],
        "pipeline_findings": [f.finding_type for f in pipeline["findings"]],
        "claude_assessment": claude_text,
        "measurements": format_key_measurements(pipeline["features"]),
        "record": pipeline["record"],
        "fiducials": pipeline["fiducials"],
        "features": pipeline["features"],
    }

    # Save to file
    save_path = RESULTS_DIR / f"ecg_{ecg_id}.txt"
    with open(save_path, "w") as f:
        f.write(f"ECG ID: {ecg_id}\n")
        f.write(f"Ground Truth: {gt_findings}\n")
        f.write(f"Pipeline Findings: {result['pipeline_findings']}\n\n")
        f.write("=== PIPELINE NARRATION ===\n")
        f.write(pipeline["narration"])
        f.write("\n\n=== CLAUDE ASSESSMENT ===\n")
        f.write(claude_text or "(skipped)")
    print(f"\nSaved to {save_path}")

    return result


def compare_from_csv(
    csv_path: str = "validation/disease_test_samples.csv",
    condition: Optional[str] = None,
    n: int = 1,
    skip_claude: bool = False,
):
    """
    Pick records from the disease test samples CSV and run comparisons.

    Args:
        csv_path: Path to disease_test_samples.csv
        condition: Filter by condition (e.g. "anterior_stemi"). None = pick first.
        n: Number of records to compare
        skip_claude: If True, skip Claude API call (for testing pipeline only)
    """
    import ast

    rows = []
    with open(csv_path) as f:
        for row in csv.DictReader(f):
            if condition and row["condition"] != condition:
                continue
            rows.append(row)

    if not rows:
        print(f"No records found for condition={condition}")
        return

    claude_client = None
    if not skip_claude:
        try:
            from rl.vision_reward import get_claude_client
            claude_client = get_claude_client()
        except ValueError as e:
            print(f"Warning: {e}")
            print("Proceeding without Claude Vision (pipeline narration only)\n")
            skip_claude = True

    results = []
    for row in rows[:n]:
        ecg_id = int(row["ecg_id"])
        try:
            scp = ast.literal_eval(row["scp_codes"])
        except Exception:
            scp = {}

        result = compare_record(
            ecg_id, ground_truth_scp=scp,
            claude_client=claude_client, skip_claude=skip_claude,
        )
        results.append(result)

    return results


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Compare pipeline vs Claude narration")
    parser.add_argument("--ecg-id", type=int, help="Specific ECG ID to compare")
    parser.add_argument("--condition", type=str, help="PTB-XL condition to pick from")
    parser.add_argument("-n", type=int, default=1, help="Number of records")
    parser.add_argument("--skip-claude", action="store_true", help="Skip Claude API call")
    args = parser.parse_args()

    if args.ecg_id:
        compare_record(args.ecg_id, skip_claude=args.skip_claude)
    else:
        compare_from_csv(condition=args.condition, n=args.n, skip_claude=args.skip_claude)
