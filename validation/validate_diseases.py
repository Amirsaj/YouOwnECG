"""
Module C — Disease Detection Accuracy.

Derives signal-only finding_type predictions from FeatureObject flags and
measurements, then compares against PTB-XL SCP code ground truth
(likelihood >= 50%).

Output:
  results/disease_detection.csv  — per record × condition row
  results/disease_summary.csv    — aggregate stats per condition
"""

from __future__ import annotations
import csv
import sys
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from validation.ptbxl_mapping import (
    load_database, record_hr_path,
    get_positive_findings, VALIDATED_CONDITIONS,
)

OUTPUT_DETECTION = Path(__file__).parent / "results" / "disease_detection.csv"
OUTPUT_SUMMARY   = Path(__file__).parent / "results" / "disease_summary.csv"

DETECTION_FIELDS = [
    "ecg_id", "condition", "scp_codes",
    "gt_positive", "pred_positive", "pred_confidence",
    "true_positive", "false_positive", "false_negative", "true_negative",
]

# ST elevation thresholds for signal-only STEMI detection (mV)
# Mirrors features.py thresholds
_STEMI_THRESH = 0.1   # 1 mm for most leads
_STEMI_ANTERIOR_THRESH = 0.15   # 1.5 mm V2-V3 (female-safe conservative threshold)


def _predict_findings(feats) -> dict[str, tuple[bool, str]]:
    """
    Derive signal-only finding predictions from FeatureObject.

    Returns dict: finding_type → (is_positive, confidence)
    """
    preds: dict[str, tuple[bool, str]] = {c: (False, "NONE") for c in VALIDATED_CONDITIONS}

    # --- Conduction ---
    if feats.lbbb:
        preds["lbbb"] = (True, "HIGH")
    if feats.rbbb:
        preds["rbbb"] = (True, "HIGH")
    if feats.wpw_pattern:
        preds["wpw_pattern"] = (True, "HIGH")
    if feats.lafb:
        preds["lafb"] = (True, "MEDIUM")
    if feats.pr_interval_ms is not None and feats.pr_interval_ms > 200:
        preds["first_degree_avb"] = (True, "HIGH" if feats.pr_interval_ms > 220 else "MEDIUM")

    # --- Rhythm ---
    if feats.dominant_rhythm == "afib":
        preds["afib"] = (True, "HIGH")
    elif feats.dominant_rhythm == "afib_possible":
        preds["afib"] = (True, "LOW")

    # --- Hypertrophy ---
    if feats.lvh_criteria_met and len(feats.lvh_criteria_met) >= 1:
        conf = "HIGH" if len(feats.lvh_criteria_met) >= 2 else "MEDIUM"
        preds["lvh"] = (True, conf)

    if feats.low_voltage_limb or feats.low_voltage_precordial:
        preds["low_voltage"] = (True, "HIGH")

    # --- STEMI (signal-only, territory-based) ---
    st_elev = feats.st_elevation_mv or {}
    lbbb_active = feats.lbbb

    if not lbbb_active:
        anterior_leads = ["V1", "V2", "V3", "V4"]
        ant_pos = [l for l in anterior_leads if (st_elev.get(l) or 0) >= _STEMI_ANTERIOR_THRESH]
        if len(ant_pos) >= 2:
            preds["anterior_stemi"] = (True, "HIGH" if len(ant_pos) >= 3 else "MEDIUM")
        elif feats.hyperacute_t_pattern or feats.de_winter_pattern:
            preds["anterior_stemi"] = (True, "MEDIUM")

        inferior_leads = ["II", "III", "aVF"]
        inf_pos = [l for l in inferior_leads if (st_elev.get(l) or 0) >= _STEMI_THRESH]
        if len(inf_pos) >= 2:
            preds["inferior_stemi"] = (True, "HIGH")

        lateral_leads = ["I", "aVL", "V5", "V6"]
        lat_pos = [l for l in lateral_leads if (st_elev.get(l) or 0) >= _STEMI_THRESH]
        if len(lat_pos) >= 2:
            preds["lateral_stemi"] = (True, "HIGH" if len(lat_pos) >= 3 else "MEDIUM")

    # --- Long QT ---
    qtc = feats.qtc_bazett_ms
    if qtc is not None and qtc >= 500:
        preds["long_qt"] = (True, "HIGH")
    elif qtc is not None and qtc >= 460:
        preds["long_qt"] = (True, "MEDIUM")

    # --- Pericarditis ---
    if feats.pericarditis_pattern:
        preds["pericarditis"] = (True, "MEDIUM")

    return preds


def run(
    n_records: int = 0,
    output_dir: Optional[Path] = None,
    skip_existing: bool = False,
    strat_fold: Optional[int] = None,
    min_likelihood: float = 50.0,
) -> tuple[Path, Path]:
    from pipeline.ingestion import load_ecg
    from pipeline.preprocessing import preprocess
    from pipeline.quality import assess_quality
    from pipeline.fiducials import detect_fiducials
    from pipeline.features import extract_features

    det_path = Path(output_dir) / OUTPUT_DETECTION.name if output_dir else OUTPUT_DETECTION
    sum_path = Path(output_dir) / OUTPUT_SUMMARY.name if output_dir else OUTPUT_SUMMARY
    det_path.parent.mkdir(parents=True, exist_ok=True)

    done_ids: set[str] = set()
    if skip_existing and det_path.exists():
        with open(det_path) as f:
            reader = csv.DictReader(f)
            for row in reader:
                done_ids.add(row["ecg_id"])
        print(f"Resuming: {len(done_ids)} records already processed")

    db = load_database(min_likelihood=min_likelihood)
    if strat_fold is not None:
        db = db[db["strat_fold"] == strat_fold]
    if n_records > 0:
        db = db.head(n_records)

    # Counters per condition for summary
    counters: dict[str, dict] = {
        c: {"TP": 0, "FP": 0, "FN": 0, "TN": 0, "n_gt_pos": 0, "n_pred_pos": 0}
        for c in VALIDATED_CONDITIONS
    }

    write_header = not (skip_existing and det_path.exists())
    with open(det_path, "a" if skip_existing else "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=DETECTION_FIELDS)
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

            scp_str = str(row["scp_codes"])
            gt_positives = get_positive_findings(row["scp_codes"], min_likelihood)

            try:
                raw_ecg = load_ecg(str(hea_path), ecg_id=ecg_id_str)
                prep = preprocess(raw_ecg)
                qual = assess_quality(prep)
                fid = detect_fiducials(prep, qual)
                feats = extract_features(prep, qual, fid)
                predictions = _predict_findings(feats)
            except KeyboardInterrupt:
                raise
            except Exception as exc:
                print(f"  ERROR ecg_id={ecg_id}: {exc}", file=sys.stderr)
                continue

            for condition in VALIDATED_CONDITIONS:
                gt_pos = condition in gt_positives
                pred_pos, pred_conf = predictions.get(condition, (False, "NONE"))

                tp = gt_pos and pred_pos
                fp = (not gt_pos) and pred_pos
                fn = gt_pos and (not pred_pos)
                tn = (not gt_pos) and (not pred_pos)

                writer.writerow({
                    "ecg_id": ecg_id,
                    "condition": condition,
                    "scp_codes": scp_str,
                    "gt_positive": gt_pos,
                    "pred_positive": pred_pos,
                    "pred_confidence": pred_conf,
                    "true_positive": tp,
                    "false_positive": fp,
                    "false_negative": fn,
                    "true_negative": tn,
                })

                c = counters[condition]
                if gt_pos:
                    c["n_gt_pos"] += 1
                if pred_pos:
                    c["n_pred_pos"] += 1
                if tp:
                    c["TP"] += 1
                if fp:
                    c["FP"] += 1
                if fn:
                    c["FN"] += 1
                if tn:
                    c["TN"] += 1

    _write_summary(counters, sum_path)
    print(f"Module C complete → {det_path}")
    print(f"Module C summary → {sum_path}")
    return det_path, sum_path


def _write_summary(counters: dict, sum_path: Path) -> None:
    summary_fields = [
        "condition", "n_gt_positive", "n_pred_positive",
        "TP", "FP", "FN", "TN",
        "sensitivity", "specificity", "PPV", "NPV", "F1", "accuracy",
    ]
    rows = []
    for condition, c in counters.items():
        tp, fp, fn, tn = c["TP"], c["FP"], c["FN"], c["TN"]
        total = tp + fp + fn + tn

        def _safe(num, denom):
            return round(num / denom, 4) if denom > 0 else None

        sensitivity = _safe(tp, tp + fn)
        specificity = _safe(tn, tn + fp)
        ppv         = _safe(tp, tp + fp)
        npv         = _safe(tn, tn + fn)
        f1 = round(2 * ppv * sensitivity / (ppv + sensitivity), 4) \
             if ppv and sensitivity and (ppv + sensitivity) > 0 else None
        accuracy    = _safe(tp + tn, total)

        rows.append({
            "condition": condition,
            "n_gt_positive": c["n_gt_pos"],
            "n_pred_positive": c["n_pred_pos"],
            "TP": tp, "FP": fp, "FN": fn, "TN": tn,
            "sensitivity": sensitivity,
            "specificity": specificity,
            "PPV": ppv,
            "NPV": npv,
            "F1": f1,
            "accuracy": accuracy,
        })

    with open(sum_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=summary_fields)
        writer.writeheader()
        writer.writerows(rows)
