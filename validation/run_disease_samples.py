"""
Run all disease test samples through the pipeline and record results.

Reads disease_test_samples.csv, runs each record through the signal processing
pipeline + signal_findings detector, and writes detailed results to
disease_sample_results.csv.
"""

from __future__ import annotations
import csv
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from validation.ptbxl_mapping import PTBXL_DIR, get_positive_findings
from pipeline.ingestion import load_ecg
from pipeline.preprocessing import preprocess
from pipeline.quality import assess_quality
from pipeline.fiducials import detect_fiducials
from pipeline.features import extract_features
from agents.signal_findings import generate_signal_findings, generate_stat_alerts

SAMPLES_CSV = Path(__file__).parent / "disease_test_samples.csv"
RESULTS_CSV = Path(__file__).parent / "disease_sample_results.csv"

RESULT_FIELDS = [
    "ecg_id", "expected_condition", "scp_codes",
    "detected_findings", "detected_confidences",
    "expected_detected", "false_negatives", "extra_findings",
    "stat_alerts",
    "hr_bpm", "pr_ms", "qrs_ms", "qtc_ms", "axis_deg",
    "lbbb", "rbbb", "wpw", "dominant_rhythm",
    "quality", "error",
]


def run():
    import ast
    samples = []
    with open(SAMPLES_CSV) as f:
        for row in csv.DictReader(f):
            samples.append(row)

    print(f"Processing {len(samples)} records...")

    results = []
    for i, sample in enumerate(samples):
        ecg_id = sample["ecg_id"]
        condition = sample["condition"]
        scp_str = sample["scp_codes"]
        filename_hr = sample["filename_hr"]

        hea_path = PTBXL_DIR / (filename_hr + ".hea")
        if not hea_path.exists():
            results.append({
                "ecg_id": ecg_id, "expected_condition": condition,
                "scp_codes": scp_str, "error": "file_not_found",
            })
            continue

        try:
            raw = load_ecg(str(hea_path), ecg_id=str(ecg_id))
            prep = preprocess(raw)
            qual = assess_quality(prep)
            fid = detect_fiducials(prep, qual)
            feats = extract_features(prep, qual, fid)

            findings = generate_signal_findings(feats)
            stat_alerts = generate_stat_alerts(findings)

            finding_types = [f.finding_type for f in findings]
            finding_confs = [f.confidence for f in findings]

            # Check if expected condition was detected
            expected_detected = condition in finding_types

            # Parse ground truth to find all expected conditions
            try:
                scp_dict = ast.literal_eval(scp_str)
            except Exception:
                scp_dict = {}
            gt_findings = get_positive_findings(scp_dict, min_likelihood=50.0)
            false_negatives = [c for c in gt_findings if c not in finding_types]
            extra = [f for f in finding_types if f not in gt_findings]

            results.append({
                "ecg_id": ecg_id,
                "expected_condition": condition,
                "scp_codes": scp_str,
                "detected_findings": "|".join(finding_types),
                "detected_confidences": "|".join(finding_confs),
                "expected_detected": expected_detected,
                "false_negatives": "|".join(false_negatives),
                "extra_findings": "|".join(extra),
                "stat_alerts": "|".join(a.finding_type for a in stat_alerts),
                "hr_bpm": round(feats.heart_rate_ventricular_bpm, 1) if feats.heart_rate_ventricular_bpm else None,
                "pr_ms": round(feats.pr_interval_ms, 1) if feats.pr_interval_ms else None,
                "qrs_ms": round(feats.qrs_duration_global_ms, 1) if feats.qrs_duration_global_ms else None,
                "qtc_ms": round(feats.qtc_bazett_ms, 1) if feats.qtc_bazett_ms else None,
                "axis_deg": round(feats.qrs_axis_deg, 1) if feats.qrs_axis_deg else None,
                "lbbb": feats.lbbb,
                "rbbb": feats.rbbb,
                "wpw": feats.wpw_pattern,
                "dominant_rhythm": feats.dominant_rhythm,
                "quality": qual.overall_quality,
                "error": None,
            })

            status = "OK" if expected_detected else "MISS"
            extra_str = f" +extra:{','.join(extra)}" if extra else ""
            print(f"  [{i+1:3d}/{len(samples)}] {status} ecg={ecg_id} expect={condition} "
                  f"found=[{','.join(finding_types)}]{extra_str}")

        except Exception as exc:
            results.append({
                "ecg_id": ecg_id, "expected_condition": condition,
                "scp_codes": scp_str, "error": str(exc)[:200],
            })
            print(f"  [{i+1:3d}/{len(samples)}] ERR ecg={ecg_id} expect={condition}: {exc}")

    # Write results
    with open(RESULTS_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=RESULT_FIELDS)
        writer.writeheader()
        for r in results:
            # Fill missing fields
            for field in RESULT_FIELDS:
                if field not in r:
                    r[field] = None
            writer.writerow(r)

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY BY CONDITION")
    print("=" * 70)
    from collections import defaultdict
    stats = defaultdict(lambda: {"total": 0, "detected": 0, "missed": 0, "error": 0})
    for r in results:
        cond = r["expected_condition"]
        stats[cond]["total"] += 1
        if r.get("error"):
            stats[cond]["error"] += 1
        elif r.get("expected_detected"):
            stats[cond]["detected"] += 1
        else:
            stats[cond]["missed"] += 1

    print(f"{'Condition':<20} {'Total':>5} {'Det':>5} {'Miss':>5} {'Err':>5} {'Sens':>8}")
    print("-" * 55)
    total_det = total_all = 0
    for cond in sorted(stats.keys()):
        s = stats[cond]
        valid = s["detected"] + s["missed"]
        sens = f"{s['detected']/valid:.0%}" if valid > 0 else "N/A"
        print(f"{cond:<20} {s['total']:>5} {s['detected']:>5} {s['missed']:>5} {s['error']:>5} {sens:>8}")
        total_det += s["detected"]
        total_all += valid

    overall = f"{total_det/total_all:.0%}" if total_all > 0 else "N/A"
    print("-" * 55)
    print(f"{'OVERALL':<20} {sum(s['total'] for s in stats.values()):>5} "
          f"{total_det:>5} {total_all - total_det:>5} "
          f"{sum(s['error'] for s in stats.values()):>5} {overall:>8}")

    print(f"\nResults saved to {RESULTS_CSV}")


if __name__ == "__main__":
    run()
