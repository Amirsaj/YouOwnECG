"""
Stratified PTB-XL sampler for cost-effective multi-model validation.

Produces a balanced sample of N records covering all validated disease
conditions plus normal ECGs. Used as input for multi-model LLM comparison.

Usage:
    python -m validation.stratified_sample [--n-total 300] [--seed 42]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from validation.ptbxl_mapping import (
    load_database, get_positive_findings, SCP_TO_FINDING, VALIDATED_CONDITIONS,
)


def create_stratified_sample(
    n_total: int = 300,
    min_per_condition: int = 15,
    normal_fraction: float = 0.30,
    seed: int = 42,
    strat_fold: int | None = None,
    output_path: Path | None = None,
) -> pd.DataFrame:
    """
    Create a stratified sample from PTB-XL ensuring disease coverage.

    Algorithm:
    1. Load PTB-XL database, parse SCP codes
    2. For each condition, identify all records with that condition (likelihood >= 50)
    3. Identify NORM records (only NORM/SR with likelihood >= 50)
    4. Mandatory fill: ensure min_per_condition records per disease
    5. Normal fill: add normals to reach normal_fraction of total
    6. Top-up: fill remaining budget proportionally
    """
    rng = np.random.RandomState(seed)

    db = load_database()
    if strat_fold is not None:
        db = db[db['strat_fold'] == strat_fold].copy()

    records = []
    for _, row in db.iterrows():
        ecg_id = int(row['ecg_id'])
        scp = row['scp_codes']
        findings = get_positive_findings(scp, min_likelihood=50.0)
        valid_findings = findings & set(VALIDATED_CONDITIONS)
        is_normal = len(valid_findings) == 0 and any(
            code in scp and scp[code] >= 50
            for code in ['NORM', 'SR']
        )
        records.append({
            'ecg_id': ecg_id,
            'filename_hr': row.get('filename_hr', ''),
            'scp_codes': str(scp),
            'conditions': '|'.join(sorted(valid_findings)) if valid_findings else '',
            'is_normal': is_normal,
            'strat_fold': int(row.get('strat_fold', 0)),
            'n_conditions': len(valid_findings),
        })

    df = pd.DataFrame(records)
    print(f"Total records in pool: {len(df)}")
    print(f"  Normal: {df['is_normal'].sum()}")
    for cond in sorted(VALIDATED_CONDITIONS):
        n = df['conditions'].str.contains(cond, na=False).sum()
        print(f"  {cond}: {n}")

    selected_ids = set()

    # Step 1: Mandatory fill -- ensure min_per_condition per disease
    for cond in VALIDATED_CONDITIONS:
        cond_records = df[df['conditions'].str.contains(cond, na=False)]
        already_selected = cond_records[cond_records['ecg_id'].isin(selected_ids)]
        available = cond_records[~cond_records['ecg_id'].isin(selected_ids)]

        need = max(0, min_per_condition - len(already_selected))
        if need > 0 and len(available) > 0:
            n_pick = min(need, len(available))
            picked = available.sample(n=n_pick, random_state=rng)
            selected_ids.update(picked['ecg_id'].tolist())

    print(f"\nAfter mandatory disease fill: {len(selected_ids)} records")

    # Step 2: Normal fill
    n_normals_target = int(n_total * normal_fraction)
    normal_records = df[df['is_normal'] & ~df['ecg_id'].isin(selected_ids)]
    current_normals = df[df['is_normal'] & df['ecg_id'].isin(selected_ids)]
    need_normals = max(0, n_normals_target - len(current_normals))
    if need_normals > 0 and len(normal_records) > 0:
        n_pick = min(need_normals, len(normal_records))
        picked = normal_records.sample(n=n_pick, random_state=rng)
        selected_ids.update(picked['ecg_id'].tolist())

    print(f"After normal fill: {len(selected_ids)} records")

    # Step 3: Top-up to reach n_total
    remaining_budget = n_total - len(selected_ids)
    if remaining_budget > 0:
        available = df[~df['ecg_id'].isin(selected_ids)]
        if len(available) > 0:
            n_pick = min(remaining_budget, len(available))
            picked = available.sample(n=n_pick, random_state=rng)
            selected_ids.update(picked['ecg_id'].tolist())

    sample = df[df['ecg_id'].isin(selected_ids)].copy()
    sample = sample.sort_values('ecg_id').reset_index(drop=True)

    print(f"\n=== FINAL SAMPLE: {len(sample)} records ===")
    print(f"  Normal: {sample['is_normal'].sum()}")
    for cond in sorted(VALIDATED_CONDITIONS):
        n = sample['conditions'].str.contains(cond, na=False).sum()
        print(f"  {cond}: {n}")

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        sample.to_csv(output_path, index=False)
        print(f"\nSaved to {output_path}")

    return sample


def main():
    parser = argparse.ArgumentParser(description="Create stratified PTB-XL sample")
    parser.add_argument("--n-total", type=int, default=300)
    parser.add_argument("--min-per-condition", type=int, default=15)
    parser.add_argument("--normal-fraction", type=float, default=0.30)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--strat-fold", type=int, default=None,
                        help="Limit to specific PTB-XL fold (1-10)")
    parser.add_argument("--output", type=str, default=None)
    args = parser.parse_args()

    output = Path(args.output) if args.output else Path(__file__).parent / "results" / "stratified_sample.csv"

    create_stratified_sample(
        n_total=args.n_total,
        min_per_condition=args.min_per_condition,
        normal_fraction=args.normal_fraction,
        seed=args.seed,
        strat_fold=args.strat_fold,
        output_path=output,
    )


if __name__ == "__main__":
    main()
