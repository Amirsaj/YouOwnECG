"""
Test fiducial refinement on 3 diverse patients.

Picks one normal sinus, one AFib, and one LBBB record from PTB-XL,
runs the full pipeline, and compares PR/QRS/QT intervals against
ecgdeli_features.csv ground truth.

Usage:
    python -m validation.test_refinement
"""

from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd

from validation.ptbxl_mapping import load_database, record_hr_path, PTBXL_DIR


FEATURES_CSV = PTBXL_DIR / "features" / "ecgdeli_features.csv"

INTERVAL_MAP = {
    "PR": ("pr_interval_ms", "PR_Int_Global"),
    "QRS": ("qrs_duration_global_ms", "QRS_Dur_Global"),
    "QT": ("qt_interval_ms", "QT_Int_Global"),
}


def _find_test_records(db: pd.DataFrame) -> dict[str, int]:
    """Find one ecg_id for each category: NORM, AFIB, CLBBB."""
    targets = {"NORM": None, "AFIB": None, "CLBBB": None}

    for _, row in db.iterrows():
        codes = row["scp_codes"]
        if not codes:
            continue
        code_names = set(codes.keys())
        high_conf = {c for c, v in codes.items() if v >= 80.0}

        if targets["NORM"] is None:
            if high_conf <= {"NORM", "SR"} and len(high_conf) > 0:
                targets["NORM"] = int(row["ecg_id"])

        if targets["AFIB"] is None and "AFIB" in high_conf:
            targets["AFIB"] = int(row["ecg_id"])

        if targets["CLBBB"] is None and "CLBBB" in high_conf:
            targets["CLBBB"] = int(row["ecg_id"])

        if all(v is not None for v in targets.values()):
            break

    return targets


def _run_pipeline(ecg_id: int, db: pd.DataFrame):
    """Run ingestion through features for a single record."""
    from pipeline.ingestion import load_ecg
    from pipeline.preprocessing import preprocess
    from pipeline.quality import assess_quality
    from pipeline.fiducials import detect_fiducials
    from pipeline.features import extract_features

    row = db[db["ecg_id"] == ecg_id].iloc[0]
    hea_path = record_hr_path(row["filename_hr"])

    raw = load_ecg(str(hea_path), ecg_id=str(ecg_id))
    prep = preprocess(raw)
    qual = assess_quality(prep)
    fid = detect_fiducials(prep, qual)
    feats = extract_features(prep, qual, fid)
    return feats


def main() -> None:
    print("Loading PTB-XL database ...")
    db = load_database()
    gt_feats = pd.read_csv(FEATURES_CSV, index_col="ecg_id")
    print(f"  {len(db)} records in database, {len(gt_feats)} in features CSV\n")

    targets = _find_test_records(db)
    print("Selected test records:")
    for category, eid in targets.items():
        print(f"  {category}: ecg_id={eid}")
    print()

    missing = [k for k, v in targets.items() if v is None]
    if missing:
        print(f"Could not find records for: {missing}")
        sys.exit(1)

    # Header
    print(f"{'Category':<8} {'ecg_id':>6}  {'Interval':<5}  "
          f"{'GT (ms)':>8}  {'Ours (ms)':>9}  {'Error (ms)':>10}  {'Abs Err':>7}")
    print("-" * 72)

    all_errors = {k: [] for k in INTERVAL_MAP}

    for category, ecg_id in targets.items():
        if ecg_id not in gt_feats.index:
            print(f"  {category}: ecg_id={ecg_id} not in features CSV, skipping")
            continue

        gt_row = gt_feats.loc[ecg_id]

        try:
            feats = _run_pipeline(ecg_id, db)
        except Exception as e:
            print(f"  {category}: pipeline failed for ecg_id={ecg_id}: {e}")
            continue

        for interval_name, (feat_attr, gt_col) in INTERVAL_MAP.items():
            gt_val = gt_row.get(gt_col)
            pred_val = getattr(feats, feat_attr, None)

            if gt_val is None or pd.isna(gt_val) or pred_val is None:
                print(f"{category:<8} {ecg_id:>6}  {interval_name:<5}  "
                      f"{'N/A':>8}  {'N/A':>9}  {'---':>10}  {'---':>7}")
                continue

            gt_f = float(gt_val)
            pred_f = float(pred_val)
            err = pred_f - gt_f
            abs_err = abs(err)
            all_errors[interval_name].append(abs_err)

            print(f"{category:<8} {ecg_id:>6}  {interval_name:<5}  "
                  f"{gt_f:>8.1f}  {pred_f:>9.1f}  {err:>+10.1f}  {abs_err:>7.1f}")

    # Summary
    print("\n" + "=" * 72)
    print("MAE Summary (across 3 test records):")
    for interval_name, errors in all_errors.items():
        if errors:
            mae = np.mean(errors)
            print(f"  {interval_name:<5}  MAE = {mae:.1f} ms  (n={len(errors)})")
        else:
            print(f"  {interval_name:<5}  no valid comparisons")


if __name__ == "__main__":
    main()
