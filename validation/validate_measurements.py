"""
Module B — Interval & Measurement Accuracy.

Compares YouOwnECG FeatureObject values against the PTB-XL
ecgdeli_features.csv ground truth (532 columns) and heart_axis from
ptbxl_database.csv.

Output: results/measurement_accuracy.csv
"""

from __future__ import annotations
import csv
import sys
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from validation.ptbxl_mapping import load_database, record_hr_path, PTBXL_DIR

OUTPUT_FILE = Path(__file__).parent / "results" / "measurement_accuracy.csv"

PTBXL_LEADS = ["I", "II", "III", "aVR", "aVL", "aVF", "V1", "V2", "V3", "V4", "V5", "V6"]

FIELDNAMES = [
    "ecg_id", "measurement", "lead",
    "gt_value", "pred_value", "error", "abs_error", "pct_error",
]


def _pct_error(pred, gt) -> Optional[float]:
    if gt is None or gt == 0:
        return None
    return round((pred - gt) / abs(gt) * 100, 4)


def run(
    n_records: int = 0,
    output_dir: Optional[Path] = None,
    skip_existing: bool = False,
    strat_fold: Optional[int] = None,
) -> Path:
    from pipeline.ingestion import load_ecg
    from pipeline.preprocessing import preprocess
    from pipeline.quality import assess_quality
    from pipeline.fiducials import detect_fiducials
    from pipeline.features import extract_features

    out_path = Path(output_dir) / OUTPUT_FILE.name if output_dir else OUTPUT_FILE
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Load PTB-XL ground truth
    features_csv = PTBXL_DIR / "features" / "ecgdeli_features.csv"
    print("Loading ecgdeli_features.csv ...")
    gt_feats = pd.read_csv(features_csv, index_col="ecg_id")
    print(f"  {len(gt_feats)} records, {len(gt_feats.columns)} columns")

    db = load_database()
    # Merge heart_axis into gt_feats from ptbxl_database.csv
    axis_map = dict(zip(db["ecg_id"].astype(int), db["heart_axis"]))

    if strat_fold is not None:
        db = db[db["strat_fold"] == strat_fold]
    if n_records > 0:
        db = db.head(n_records)

    done_ids: set[str] = set()
    if skip_existing and out_path.exists():
        with open(out_path) as f:
            reader = csv.DictReader(f)
            for row in reader:
                done_ids.add(row["ecg_id"])
        print(f"Resuming: {len(done_ids)} records already processed")

    write_header = not (skip_existing and out_path.exists())
    with open(out_path, "a" if skip_existing else "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        if write_header:
            writer.writeheader()

        for _, row in db.iterrows():
            ecg_id = int(row["ecg_id"])
            ecg_id_str = str(ecg_id)
            if ecg_id_str in done_ids:
                continue

            hea_path = record_hr_path(row["filename_hr"])
            if not hea_path.exists():
                continue
            if ecg_id not in gt_feats.index:
                continue

            gt_row = gt_feats.loc[ecg_id]

            try:
                raw_ecg = load_ecg(str(hea_path), ecg_id=ecg_id_str)
                prep = preprocess(raw_ecg)
                qual = assess_quality(prep)
                fid = detect_fiducials(prep, qual)
                feats = extract_features(prep, qual, fid)

                rows = []

                def _add(measurement, lead, gt_val, pred_val):
                    if gt_val is None or pd.isna(gt_val) or pred_val is None:
                        return
                    gt_f = float(gt_val)
                    pred_f = float(pred_val)
                    err = round(pred_f - gt_f, 4)
                    rows.append({
                        "ecg_id": ecg_id,
                        "measurement": measurement,
                        "lead": lead,
                        "gt_value": round(gt_f, 4),
                        "pred_value": round(pred_f, 4),
                        "error": err,
                        "abs_error": abs(err),
                        "pct_error": _pct_error(pred_f, gt_f),
                    })

                # --- Global intervals ---
                _add("pr_ms", "global",
                     gt_row.get("PR_Int_Global"), feats.pr_interval_ms)
                _add("qrs_ms", "global",
                     gt_row.get("QRS_Dur_Global"), feats.qrs_duration_global_ms)
                _add("qt_ms", "global",
                     gt_row.get("QT_Int_Global"), feats.qt_interval_ms)

                # QTc: use QT_IntCorr_II as proxy (Bazett from PTB-XL)
                qtc_gt = gt_row.get("QT_IntCorr_II")
                _add("qtc_bazett_ms", "global", qtc_gt, feats.qtc_bazett_ms)

                # Heart rate from RR_Mean_Global
                rr_gt = gt_row.get("RR_Mean_Global")
                if rr_gt and not pd.isna(rr_gt) and float(rr_gt) > 0:
                    hr_gt = 60000.0 / float(rr_gt)
                    _add("heart_rate_bpm", "global", hr_gt,
                         feats.heart_rate_ventricular_bpm)

                # Heart axis (some records have text values like "LAD" — skip those)
                axis_gt = pd.to_numeric(axis_map.get(ecg_id), errors="coerce")
                if axis_gt is not None and not pd.isna(axis_gt):
                    _add("qrs_axis_deg", "global", float(axis_gt),
                         feats.qrs_axis_deg)

                # --- Per-lead amplitudes & ST ---
                for lead in PTBXL_LEADS:
                    _add(f"r_amp_mv",  lead,
                         gt_row.get(f"R_Amp_{lead}"),
                         feats.r_amplitude_mv.get(lead))
                    _add(f"s_amp_mv",  lead,
                         gt_row.get(f"S_Amp_{lead}"),
                         feats.s_amplitude_mv.get(lead))
                    _add(f"t_amp_mv",  lead,
                         gt_row.get(f"T_Amp_{lead}"),
                         feats.t_amplitude_mv.get(lead))
                    _add(f"st_elev_mv", lead,
                         gt_row.get(f"ST_Elev_{lead}"),
                         feats.st_elevation_mv.get(lead))
                    _add(f"pr_ms", lead,
                         gt_row.get(f"PR_Int_{lead}"),
                         feats.pr_interval_ms)    # global value, per-lead GT
                    _add(f"qtc_ms", lead,
                         gt_row.get(f"QT_IntCorr_{lead}"),
                         feats.qtc_bazett_ms)

                writer.writerows(rows)

            except KeyboardInterrupt:
                raise
            except Exception as exc:
                print(f"  ERROR ecg_id={ecg_id}: {exc}", file=sys.stderr)
                continue

    print(f"Module B complete → {out_path}")
    return out_path
