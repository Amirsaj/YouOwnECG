"""
Main iteration runner for human-in-the-loop narration improvement.

Usage:
    # Compare a specific record (pipeline only, no Claude):
    python3 rl/iterate.py --ecg-id 6174 --skip-claude

    # Compare worst-performing condition with Claude:
    python3 rl/iterate.py --condition anterior_stemi

    # Run batch of N records for a condition:
    python3 rl/iterate.py --condition rbbb -n 3

    # Run all conditions, 1 record each, pipeline only:
    python3 rl/iterate.py --all --skip-claude

    # Show current progress:
    python3 rl/iterate.py --status
"""

from __future__ import annotations
import csv
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

LOG_PATH = Path(__file__).parent / "iteration_log.csv"
LOG_FIELDS = ["timestamp", "ecg_id", "condition", "pipeline_findings",
              "ground_truth", "feedback", "action_taken"]


def log_iteration(ecg_id: int, condition: str, pipeline_findings: list,
                  ground_truth: set, feedback: str = "", action: str = ""):
    """Append one row to the iteration log."""
    exists = LOG_PATH.exists()
    with open(LOG_PATH, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=LOG_FIELDS)
        if not exists:
            writer.writeheader()
        writer.writerow({
            "timestamp": datetime.now().isoformat(),
            "ecg_id": ecg_id,
            "condition": condition,
            "pipeline_findings": "|".join(pipeline_findings),
            "ground_truth": "|".join(ground_truth),
            "feedback": feedback,
            "action_taken": action,
        })


def show_status():
    """Show iteration progress summary."""
    if not LOG_PATH.exists():
        print("No iterations logged yet.")
        return

    from collections import defaultdict
    stats = defaultdict(int)
    total = 0
    with open(LOG_PATH) as f:
        for row in csv.DictReader(f):
            stats[row["condition"]] += 1
            total += 1

    print(f"\nIteration Progress ({total} total reviews):")
    print(f"{'Condition':<20} {'Reviews':>8}")
    print("-" * 30)
    for cond in sorted(stats.keys()):
        print(f"{cond:<20} {stats[cond]:>8}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Human-in-the-loop narration improvement")
    parser.add_argument("--ecg-id", type=int, help="Specific ECG ID")
    parser.add_argument("--condition", type=str, help="PTB-XL condition to review")
    parser.add_argument("-n", type=int, default=1, help="Number of records")
    parser.add_argument("--skip-claude", action="store_true", help="Skip Claude Vision API")
    parser.add_argument("--all", action="store_true", help="1 record per condition")
    parser.add_argument("--status", action="store_true", help="Show progress")
    args = parser.parse_args()

    if args.status:
        show_status()
        return

    from rl.compare_narrations import compare_record, compare_from_csv

    if args.ecg_id:
        compare_record(args.ecg_id, skip_claude=args.skip_claude)
    elif args.all:
        conditions = [
            "anterior_stemi", "inferior_stemi", "lateral_stemi",
            "rbbb", "wpw_pattern", "lbbb",
            "first_degree_avb", "afib", "long_qt",
            "lafb", "lvh",
        ]
        for cond in conditions:
            print(f"\n{'#'*80}")
            print(f" CONDITION: {cond}")
            print(f"{'#'*80}")
            compare_from_csv(condition=cond, n=1, skip_claude=args.skip_claude)
    else:
        compare_from_csv(
            condition=args.condition, n=args.n,
            skip_claude=args.skip_claude,
        )


if __name__ == "__main__":
    main()
