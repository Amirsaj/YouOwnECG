"""
Module D — Pipeline Timing.

Measures wall-clock latency per pipeline stage over N records.

Output: results/pipeline_timing.csv
"""

from __future__ import annotations
import csv
import sys
import time
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from validation.ptbxl_mapping import load_database, record_hr_path

OUTPUT_FILE = Path(__file__).parent / "results" / "pipeline_timing.csv"

FIELDNAMES = ["ecg_id", "stage", "latency_ms"]


def run(
    n_records: int = 100,
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

    done_ids: set[str] = set()
    if skip_existing and out_path.exists():
        with open(out_path) as f:
            for row in csv.DictReader(f):
                done_ids.add(row["ecg_id"])

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
                timings: dict[str, float] = {}

                t0 = time.perf_counter()
                raw = load_ecg(str(hea_path), ecg_id=ecg_id_str)
                timings["ingest"] = (time.perf_counter() - t0) * 1000

                t0 = time.perf_counter()
                prep = preprocess(raw)
                timings["preprocess"] = (time.perf_counter() - t0) * 1000

                t0 = time.perf_counter()
                qual = assess_quality(prep)
                timings["quality"] = (time.perf_counter() - t0) * 1000

                t0 = time.perf_counter()
                fid = detect_fiducials(prep, qual)
                timings["fiducials"] = (time.perf_counter() - t0) * 1000

                t0 = time.perf_counter()
                feats = extract_features(prep, qual, fid)
                timings["features"] = (time.perf_counter() - t0) * 1000

                timings["total"] = sum(timings.values())

                for stage, latency in timings.items():
                    writer.writerow({
                        "ecg_id": ecg_id,
                        "stage": stage,
                        "latency_ms": round(latency, 2),
                    })

            except KeyboardInterrupt:
                raise
            except Exception as exc:
                print(f"  ERROR ecg_id={ecg_id}: {exc}", file=sys.stderr)
                continue

    print(f"Module D complete → {out_path}")
    return out_path
