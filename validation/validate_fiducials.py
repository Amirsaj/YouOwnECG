"""
Module A — Fiducial Detection Accuracy.

For each PTB-XL record, compare our ecgdeli-based predicted fiducials
against the PTB-XL ground-truth .atr annotations (from the original
MATLAB ecgdeli toolbox).

Beat matching: nearest predicted R-peak within ±50 ms of GT R-peak.
Error tolerance window: ±50 ms per fiducial after beat alignment.

Output: results/fiducial_accuracy.csv
"""

from __future__ import annotations
import csv
import os
import sys
import traceback
from pathlib import Path
from typing import Optional

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from validation.ptbxl_mapping import (
    load_database, record_hr_path, load_gt_fiducials,
    FIDUCIAL_NAMES,
)

TOLERANCE_MS = 50.0
OUTPUT_FILE = Path(__file__).parent / "results" / "fiducial_accuracy.csv"
PTBXL_LEADS = ["I", "II", "III", "aVR", "aVL", "aVF", "V1", "V2", "V3", "V4", "V5", "V6"]

FIELDNAMES = [
    "ecg_id", "lead", "beat_idx", "fiducial",
    "gt_sample", "pred_sample", "error_ms", "abs_error_ms", "detected",
]


def run(
    n_records: int = 0,
    output_dir: Optional[Path] = None,
    skip_existing: bool = False,
    strat_fold: Optional[int] = None,
) -> Path:
    """
    Run Module A over PTB-XL records.

    Parameters
    ----------
    n_records : 0 = all
    skip_existing : resume from existing output file
    strat_fold : if set, only run records with this strat_fold value
    """
    from pipeline.ingestion import load_ecg
    from pipeline.preprocessing import preprocess
    from pipeline.quality import assess_quality
    from pipeline.fiducials import detect_fiducials

    out_path = Path(output_dir) / OUTPUT_FILE.name if output_dir else OUTPUT_FILE
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Load already-processed records for resume support
    done_ids: set[str] = set()
    if skip_existing and out_path.exists():
        with open(out_path) as f:
            reader = csv.DictReader(f)
            for row in reader:
                done_ids.add(row["ecg_id"])
        print(f"Resuming: {len(done_ids)} records already processed")

    db = load_database()
    if strat_fold is not None:
        db = db[db["strat_fold"] == strat_fold]
    if n_records > 0:
        db = db.head(n_records)

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

            try:
                raw = load_ecg(str(hea_path), ecg_id=ecg_id_str)
                prep = preprocess(raw)
                qual = assess_quality(prep)
                fid = detect_fiducials(prep, qual)
                fs = prep.fs
                safe_start = prep.safe_window_start_sample
                tol_samples = int(TOLERANCE_MS / 1000.0 * fs)

                for lead in PTBXL_LEADS:
                    gt_fids = load_gt_fiducials(ecg_id, lead)
                    if gt_fids is None:
                        continue
                    # GT R-peaks for beat matching
                    gt_r = np.array(gt_fids.get(5, []), dtype=int)
                    if len(gt_r) == 0:
                        continue

                    # Predicted FPT for this lead (indices in safe-window space)
                    pred_fpt = fid.fpt.get(lead)
                    if pred_fpt is None or len(pred_fpt) == 0:
                        # All fiducials for all GT beats → not detected
                        for beat_idx, gt_r_sample in enumerate(gt_r):
                            for col, fname in FIDUCIAL_NAMES.items():
                                gt_sample = gt_fids.get(col, [None] * (beat_idx + 1))
                                gt_val = gt_sample[beat_idx] if beat_idx < len(gt_sample) else None
                                if gt_val is None:
                                    continue
                                writer.writerow({
                                    "ecg_id": ecg_id,
                                    "lead": lead,
                                    "beat_idx": beat_idx,
                                    "fiducial": fname,
                                    "gt_sample": gt_val,
                                    "pred_sample": None,
                                    "error_ms": None,
                                    "abs_error_ms": None,
                                    "detected": False,
                                })
                        continue

                    # Predicted R-peaks in full-recording space
                    pred_r_local = pred_fpt[:, 5]  # safe-window indices
                    pred_r_global = np.where(
                        pred_r_local >= 0,
                        pred_r_local + safe_start,
                        -1,
                    )

                    for beat_idx, gt_r_sample in enumerate(gt_r):
                        # Find nearest predicted beat
                        valid_mask = pred_r_global >= 0
                        if not valid_mask.any():
                            matched_beat_idx = None
                        else:
                            diffs = np.abs(pred_r_global[valid_mask] - gt_r_sample)
                            nearest = diffs.argmin()
                            if diffs[nearest] <= tol_samples:
                                # Map back to full pred_fpt index
                                valid_indices = np.where(valid_mask)[0]
                                matched_beat_idx = valid_indices[nearest]
                            else:
                                matched_beat_idx = None

                        for col, fname in FIDUCIAL_NAMES.items():
                            gt_col_vals = gt_fids.get(col, [])
                            gt_val = gt_col_vals[beat_idx] if beat_idx < len(gt_col_vals) else None
                            if gt_val is None:
                                continue

                            if matched_beat_idx is None:
                                pred_sample = None
                                error_ms = None
                                abs_error_ms = None
                                detected = False
                            else:
                                pred_local = int(pred_fpt[matched_beat_idx, col])
                                if pred_local < 0:
                                    pred_sample = None
                                    error_ms = None
                                    abs_error_ms = None
                                    detected = False
                                else:
                                    pred_sample = pred_local + safe_start
                                    error_ms = round((pred_sample - gt_val) / fs * 1000, 2)
                                    abs_error_ms = abs(error_ms)
                                    detected = abs_error_ms <= TOLERANCE_MS

                            writer.writerow({
                                "ecg_id": ecg_id,
                                "lead": lead,
                                "beat_idx": beat_idx,
                                "fiducial": fname,
                                "gt_sample": gt_val,
                                "pred_sample": pred_sample,
                                "error_ms": error_ms,
                                "abs_error_ms": abs_error_ms,
                                "detected": detected,
                            })

            except KeyboardInterrupt:
                raise
            except Exception as exc:
                print(f"  ERROR ecg_id={ecg_id}: {exc}", file=sys.stderr)
                continue

        print(f"Module A complete → {out_path}")
    return out_path
