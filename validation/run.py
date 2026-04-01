"""
Validation CLI entry point.

Usage:
  python -m validation.run --all --n-records 10          # smoke test
  python -m validation.run --fiducials --n-records 500
  python -m validation.run --measurements --n-records 500
  python -m validation.run --diseases --n-records 0      # all records
  python -m validation.run --timing --n-records 100
  python -m validation.run --all --skip-existing         # resume
  python -m validation.run --diseases --strat-fold 10    # test fold only
"""

from __future__ import annotations
import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def _hms(seconds: float) -> str:
    h, rem = divmod(int(seconds), 3600)
    m, s = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def main() -> None:
    parser = argparse.ArgumentParser(description="YouOwnECG validation framework")
    parser.add_argument("--all",          action="store_true", help="Run all 4 modules")
    parser.add_argument("--fiducials",    action="store_true", help="Module A: fiducial detection accuracy")
    parser.add_argument("--measurements", action="store_true", help="Module B: interval & measurement accuracy")
    parser.add_argument("--diseases",     action="store_true", help="Module C: disease detection performance")
    parser.add_argument("--timing",       action="store_true", help="Module D: pipeline timing")
    parser.add_argument("--n-records",    type=int, default=0,
                        help="Limit to first N records (0 = all, default 0)")
    parser.add_argument("--output-dir",   type=str, default=None,
                        help="Output directory for CSV files (default: validation/results)")
    parser.add_argument("--ptbxl-dir",    type=str, default=None,
                        help="Override PTB-XL dataset path")
    parser.add_argument("--strat-fold",   type=int, default=None,
                        help="Run only records with this PTB-XL strat_fold (1-10)")
    parser.add_argument("--skip-existing", action="store_true",
                        help="Skip already-processed records (resume support)")
    parser.add_argument("--min-likelihood", type=float, default=50.0,
                        help="SCP code likelihood threshold for Module C (default 50.0)")
    args = parser.parse_args()

    if args.ptbxl_dir:
        import os
        os.environ["PTBXL_DIR"] = args.ptbxl_dir

    output_dir = Path(args.output_dir) if args.output_dir else Path(__file__).parent / "results"
    output_dir.mkdir(parents=True, exist_ok=True)

    run_fiducials    = args.all or args.fiducials
    run_measurements = args.all or args.measurements
    run_diseases     = args.all or args.diseases
    run_timing       = args.all or args.timing

    if not any([run_fiducials, run_measurements, run_diseases, run_timing]):
        parser.print_help()
        sys.exit(1)

    kwargs = dict(
        n_records=args.n_records,
        output_dir=output_dir,
        skip_existing=args.skip_existing,
        strat_fold=args.strat_fold,
    )

    total_start = time.perf_counter()

    if run_fiducials:
        print("\n" + "="*60)
        print("MODULE A — Fiducial Detection Accuracy")
        print("="*60)
        t0 = time.perf_counter()
        from validation.validate_fiducials import run as run_fid
        run_fid(**kwargs)
        print(f"Elapsed: {_hms(time.perf_counter() - t0)}")

    if run_measurements:
        print("\n" + "="*60)
        print("MODULE B — Interval & Measurement Accuracy")
        print("="*60)
        t0 = time.perf_counter()
        from validation.validate_measurements import run as run_meas
        run_meas(**kwargs)
        print(f"Elapsed: {_hms(time.perf_counter() - t0)}")

    if run_diseases:
        print("\n" + "="*60)
        print("MODULE C — Disease Detection Performance")
        print("="*60)
        t0 = time.perf_counter()
        from validation.validate_diseases import run as run_dis
        run_dis(**kwargs, min_likelihood=args.min_likelihood)
        print(f"Elapsed: {_hms(time.perf_counter() - t0)}")

    if run_timing:
        n = args.n_records if args.n_records > 0 else 100
        print("\n" + "="*60)
        print(f"MODULE D — Pipeline Timing ({n} records)")
        print("="*60)
        t0 = time.perf_counter()
        from validation.validate_timing import run as run_time
        run_time(**{**kwargs, "n_records": n})
        print(f"Elapsed: {_hms(time.perf_counter() - t0)}")

    print(f"\nAll done. Total time: {_hms(time.perf_counter() - total_start)}")
    print(f"Results in: {output_dir}")


if __name__ == "__main__":
    main()
