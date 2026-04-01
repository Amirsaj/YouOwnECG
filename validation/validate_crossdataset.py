"""
Cross-dataset signal-only validation runner.

Runs signal pipeline + generate_signal_findings on Chapman-Shaoxing, CPSC 2018,
and Georgia datasets. Compares against SNOMED-CT ground truth from .hea headers.

Usage:
    python -m validation.validate_crossdataset --datasets chapman,cpsc2018 --n-per-dataset 500
"""

from __future__ import annotations
import argparse
import csv
import random
import sys
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pipeline.ingestion import load_ecg
from pipeline.preprocessing import preprocess
from pipeline.quality import assess_quality
from pipeline.fiducials import detect_fiducials
from pipeline.features import extract_features
from agents.signal_findings import generate_signal_findings

# SNOMED-CT code -> finding_type mapping (PhysioNet Challenge 2020 datasets)
SNOMED_TO_FINDING: dict[str, str] = {
    "164889003": "afib",
    "195080001": "afib",
    "164890007": "aflutter",
    "270492004": "first_degree_avb",
    "164909002": "lbbb",
    "445118002": "lbbb",
    "59118001": "rbbb",
    "713427006": "rbbb",
    "445211001": "lafb",
    "164873001": "lvh",
    "251146004": "low_voltage",
    "111975006": "long_qt",
    "164947007": "pericarditis",
    "164865005": "anterior_stemi",
    "164861001": "inferior_stemi",
    "426177001": "sinus_bradycardia",
    "426627000": "sinus_bradycardia",
    "427084000": "sinus_tachycardia",
    "17338001": "wpw_pattern",
}

# Conditions we can evaluate (intersection of SNOMED mapping and signal detectors)
CROSS_CONDITIONS = sorted(set(SNOMED_TO_FINDING.values()))

DATASET_PATHS = {
    "chapman": Path(
        "/Users/amirsadjadtaleban/Documents/YouOwnECG/DB/WFDB_ChapmanShaoxing/"
    ),
    "cpsc2018": Path(
        "/Users/amirsadjadtaleban/Documents/YouOwnECG/DB/physionet.org/files/"
        "challenge-2020/1.0.2/training/cpsc_2018/"
    ),
    "georgia": Path(
        "/Users/amirsadjadtaleban/Documents/YouOwnECG/DB/physionet.org/files/"
        "challenge-2020/1.0.2/training/georgia/"
    ),
}

DETECTION_FIELDS = [
    "dataset", "record_id", "condition",
    "gt_positive", "pred_positive", "pred_confidence",
    "TP", "FP", "FN", "TN",
]

SUMMARY_FIELDS = [
    "dataset", "condition", "n_gt_positive", "n_pred_positive",
    "TP", "FP", "FN", "TN",
    "sensitivity", "specificity", "PPV", "NPV", "F1",
]


def parse_snomed_from_header(hea_path: str) -> list[str]:
    """Extract SNOMED-CT codes from PhysioNet Challenge 2020 .hea file."""
    codes = []
    with open(hea_path) as f:
        for line in f:
            # Handle both "# Dx:" (PhysioNet standard) and "#Dx:" formats
            stripped = line.strip()
            if stripped.startswith("# Dx:") or stripped.startswith("#Dx:"):
                dx_part = stripped.split("Dx:", 1)[1].strip()
                codes = [c.strip() for c in dx_part.split(",") if c.strip()]
                break
    return codes


def get_gt_findings(snomed_codes: list[str]) -> set[str]:
    """Map SNOMED codes to finding_type set."""
    findings = set()
    for code in snomed_codes:
        mapped = SNOMED_TO_FINDING.get(code)
        if mapped:
            findings.add(mapped)
    return findings


def discover_hea_files(dataset_path: Path) -> list[Path]:
    """Find all .hea files in a dataset directory (recursive)."""
    return sorted(dataset_path.rglob("*.hea"))


def _extract_predictions(features) -> dict[str, tuple[bool, str]]:
    """Run signal-only findings and extract predictions for cross-dataset conditions."""
    findings = generate_signal_findings(features)
    preds: dict[str, tuple[bool, str]] = {c: (False, "NONE") for c in CROSS_CONDITIONS}
    for f in findings:
        if f.finding_type in preds:
            preds[f.finding_type] = (True, f.confidence)
    return preds


def _safe_div(num: float, denom: float) -> Optional[float]:
    return round(num / denom, 4) if denom > 0 else None


def _compute_summary(counters: dict) -> list[dict]:
    rows = []
    for (dataset, condition), c in sorted(counters.items()):
        tp, fp, fn, tn = c["TP"], c["FP"], c["FN"], c["TN"]
        sens = _safe_div(tp, tp + fn)
        spec = _safe_div(tn, tn + fp)
        ppv = _safe_div(tp, tp + fp)
        npv = _safe_div(tn, tn + fn)
        f1 = (round(2 * ppv * sens / (ppv + sens), 4)
               if ppv and sens and (ppv + sens) > 0 else None)
        rows.append({
            "dataset": dataset,
            "condition": condition,
            "n_gt_positive": c["n_gt_pos"],
            "n_pred_positive": c["n_pred_pos"],
            "TP": tp, "FP": fp, "FN": fn, "TN": tn,
            "sensitivity": sens,
            "specificity": spec,
            "PPV": ppv,
            "NPV": npv,
            "F1": f1,
        })
    return rows


def run_dataset(
    dataset_name: str,
    dataset_path: Path,
    n_records: int,
    output_dir: Path,
    resume: bool = True,
) -> tuple[Path, Path]:
    """Run signal-only validation on one dataset."""
    det_path = output_dir / f"{dataset_name}_detection.csv"
    sum_path = output_dir / f"{dataset_name}_summary.csv"

    # Discover records
    hea_files = discover_hea_files(dataset_path)
    if not hea_files:
        print(f"  No .hea files found in {dataset_path}")
        return det_path, sum_path

    print(f"  Found {len(hea_files)} records in {dataset_name}")

    # Sample
    if n_records > 0 and n_records < len(hea_files):
        random.seed(42)
        hea_files = random.sample(hea_files, n_records)

    # Resume support
    done_ids: set[str] = set()
    if resume and det_path.exists():
        with open(det_path) as f:
            reader = csv.DictReader(f)
            for row in reader:
                done_ids.add(row["record_id"])
        print(f"  Resuming: {len(done_ids)} records already processed")

    counters: dict[tuple[str, str], dict] = {}
    for cond in CROSS_CONDITIONS:
        counters[(dataset_name, cond)] = {
            "TP": 0, "FP": 0, "FN": 0, "TN": 0,
            "n_gt_pos": 0, "n_pred_pos": 0,
        }

    write_header = not (resume and det_path.exists())
    det_file = open(det_path, "a" if (resume and det_path.exists()) else "w", newline="")
    writer = csv.DictWriter(det_file, fieldnames=DETECTION_FIELDS)
    if write_header:
        writer.writeheader()

    total = len(hea_files)
    processed = 0

    for idx, hea_path in enumerate(hea_files):
        record_id = hea_path.stem
        if record_id in done_ids:
            continue

        # Parse ground truth from header
        snomed_codes = parse_snomed_from_header(str(hea_path))
        gt_positives = get_gt_findings(snomed_codes)

        # Run signal pipeline
        try:
            raw = load_ecg(str(hea_path), ecg_id=record_id)
            prep = preprocess(raw)
            qual = assess_quality(prep)
            fid = detect_fiducials(prep, qual)
            feats = extract_features(prep, qual, fid)
            preds = _extract_predictions(feats)
        except KeyboardInterrupt:
            raise
        except Exception as exc:
            print(f"  [{idx+1}/{total}] {record_id} error: {exc}", file=sys.stderr)
            continue

        for condition in CROSS_CONDITIONS:
            gt_pos = condition in gt_positives
            pred_pos, pred_conf = preds.get(condition, (False, "NONE"))

            tp = gt_pos and pred_pos
            fp = (not gt_pos) and pred_pos
            fn = gt_pos and (not pred_pos)
            tn = (not gt_pos) and (not pred_pos)

            writer.writerow({
                "dataset": dataset_name,
                "record_id": record_id,
                "condition": condition,
                "gt_positive": gt_pos,
                "pred_positive": pred_pos,
                "pred_confidence": pred_conf,
                "TP": tp,
                "FP": fp,
                "FN": fn,
                "TN": tn,
            })

            c = counters[(dataset_name, condition)]
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

        processed += 1
        if processed % 50 == 0:
            det_file.flush()
            print(f"  [{processed}/{total}] processed {record_id}")

    det_file.close()

    # Write summary
    summary_rows = _compute_summary(counters)
    with open(sum_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=SUMMARY_FIELDS)
        w.writeheader()
        w.writerows(summary_rows)

    print(f"  {dataset_name}: {processed} records processed")
    print(f"  Detection -> {det_path}")
    print(f"  Summary   -> {sum_path}")
    return det_path, sum_path


def main(
    datasets: list[str],
    n_per_dataset: int,
    output_dir: str,
    resume: bool = True,
) -> None:
    """Run cross-dataset validation across specified datasets."""
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    for ds_name in datasets:
        ds_path = DATASET_PATHS.get(ds_name)
        if ds_path is None:
            print(f"Unknown dataset: {ds_name}. Valid: {list(DATASET_PATHS.keys())}")
            continue
        if not ds_path.exists():
            print(f"Dataset path does not exist: {ds_path}")
            continue

        print(f"Running {ds_name}...")
        run_dataset(ds_name, ds_path, n_per_dataset, out, resume=resume)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Cross-dataset signal-only validation")
    parser.add_argument(
        "--datasets", default="chapman,cpsc2018,georgia",
        help="Comma-separated dataset names (default: all)",
    )
    parser.add_argument(
        "--n-per-dataset", type=int, default=500,
        help="Number of records to sample per dataset (0 = all)",
    )
    parser.add_argument(
        "--output-dir", default="validation/results",
        help="Output directory for results",
    )
    parser.add_argument(
        "--no-resume", action="store_true",
        help="Do not resume from existing results",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    datasets = [d.strip() for d in args.datasets.split(",")]
    main(datasets, args.n_per_dataset, args.output_dir, resume=not args.no_resume)
