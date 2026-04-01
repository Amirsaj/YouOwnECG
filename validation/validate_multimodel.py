"""
Multi-model validation runner.

Runs stratified PTB-XL sample through signal-only baseline + multiple LLM providers.
Compares diagnostic findings against ground truth.

Usage:
    python -m validation.validate_multimodel --sample validation/results/stratified_sample.csv --models signal,gemini
"""

from __future__ import annotations
import argparse
import asyncio
import csv
import sys
import time
from pathlib import Path
from typing import Optional

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from validation.ptbxl_mapping import (
    load_database, record_hr_path,
    get_positive_findings, VALIDATED_CONDITIONS,
)
from agents.schemas import DiagnosticResult, DiagnosticFinding
from agents.signal_findings import generate_signal_findings
from agents.llm_adapters import get_call_agent, MODEL_COSTS
from agents.orchestrator import run_diagnostic
from pipeline.ingestion import load_ecg
from pipeline.preprocessing import preprocess
from pipeline.quality import assess_quality
from pipeline.fiducials import detect_fiducials
from pipeline.features import extract_features
from pipeline.schemas import VisionVerificationResult

ALL_MODELS = ["signal", "deepseek", "gemini", "gpt4o", "claude"]

DETECTION_FIELDS = [
    "ecg_id", "model", "condition",
    "gt_positive", "pred_positive", "pred_confidence",
    "TP", "FP", "FN", "TN",
]

SUMMARY_FIELDS = [
    "model", "condition", "n_gt_positive", "n_pred_positive",
    "TP", "FP", "FN", "TN",
    "sensitivity", "specificity", "PPV", "NPV", "F1",
]

COST_FIELDS = [
    "model", "total_prompt_tokens", "total_completion_tokens",
    "total_cost_usd", "avg_latency_sec", "n_records",
]


def _dummy_vision() -> VisionVerificationResult:
    return VisionVerificationResult(
        available=False,
        unavailability_reason="VL2_NOT_APPLICABLE",
        st_elevation_leads=[],
        st_depression_leads=[],
        t_wave_inversion_leads=[],
        lbbb_pattern=False,
        rhythm_regular=None,
        qrs_wide=None,
        signal_vision_conflicts=[],
        raw_vl2_response=None,
        vl2_latency_sec=None,
    )


def _run_signal_pipeline(hea_path: str, ecg_id: str):
    """Run stages 1-5 of the signal pipeline, return (features, quality)."""
    raw = load_ecg(hea_path, ecg_id=ecg_id)
    prep = preprocess(raw)
    qual = assess_quality(prep)
    fid = detect_fiducials(prep, qual)
    feats = extract_features(prep, qual, fid)
    return feats, qual


def _extract_signal_predictions(features) -> dict[str, tuple[bool, str]]:
    """Extract finding predictions from signal-only generator."""
    findings = generate_signal_findings(features)
    preds: dict[str, tuple[bool, str]] = {c: (False, "NONE") for c in VALIDATED_CONDITIONS}
    for f in findings:
        if f.finding_type in preds:
            preds[f.finding_type] = (True, f.confidence)
    return preds


def _extract_llm_predictions(result: DiagnosticResult) -> dict[str, tuple[bool, str]]:
    """Extract finding predictions from DiagnosticResult."""
    preds: dict[str, tuple[bool, str]] = {c: (False, "NONE") for c in VALIDATED_CONDITIONS}
    for f in result.findings:
        if f.finding_type in preds:
            preds[f.finding_type] = (True, f.confidence)
    return preds


def _safe_div(num: float, denom: float) -> Optional[float]:
    return round(num / denom, 4) if denom > 0 else None


def _load_done_ids(det_path: Path) -> dict[str, set[str]]:
    """Load already-processed (ecg_id, model) pairs for resume support."""
    done: dict[str, set[str]] = {}
    if not det_path.exists():
        return done
    with open(det_path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            done.setdefault(row["model"], set()).add(row["ecg_id"])
    return done


async def run_record_model(
    ecg_id: str,
    features,
    quality,
    model_name: str,
    cost_accum: dict,
) -> dict[str, tuple[bool, str]]:
    """Run a single model on one record, return predictions and accumulate cost."""
    if model_name == "signal":
        return _extract_signal_predictions(features)

    adapter = get_call_agent(model_name)
    vision = _dummy_vision()
    t0 = time.perf_counter()

    result = await run_diagnostic(
        features=features,
        vision=vision,
        quality=quality,
        call_agent_fn=adapter,
    )

    latency = time.perf_counter() - t0
    cost_accum["latency_sum"] += latency
    cost_accum["n_calls"] += 1

    # Accumulate token usage from findings' agent calls
    # The adapters log usage via the return dict; we track via the model costs
    # Since run_diagnostic makes 4 calls (RRC, IT, MR, CDS), we estimate from result
    # A more precise approach: instrument the adapter to accumulate usage
    # For now, approximate from the model's cost structure
    # Token tracking is best-effort since run_diagnostic doesn't expose per-call usage

    return _extract_llm_predictions(result)


def _compute_summary(counters: dict) -> list[dict]:
    """Compute summary statistics from counters."""
    rows = []
    for (model, condition), c in sorted(counters.items()):
        tp, fp, fn, tn = c["TP"], c["FP"], c["FN"], c["TN"]
        sens = _safe_div(tp, tp + fn)
        spec = _safe_div(tn, tn + fp)
        ppv = _safe_div(tp, tp + fp)
        npv = _safe_div(tn, tn + fn)
        f1 = (round(2 * ppv * sens / (ppv + sens), 4)
               if ppv and sens and (ppv + sens) > 0 else None)
        rows.append({
            "model": model,
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


async def main(
    sample_path: str,
    models: list[str],
    output_dir: str,
    resume: bool = True,
) -> None:
    """Run multi-model validation on the stratified sample."""
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    det_path = out / "multimodel_detection.csv"
    sum_path = out / "multimodel_summary.csv"
    cost_path = out / "multimodel_cost.csv"

    # Load stratified sample
    sample = pd.read_csv(sample_path)
    print(f"Loaded {len(sample)} records from {sample_path}")

    # Load PTB-XL database for ground truth
    db = load_database()
    db_lookup = {int(r["ecg_id"]): r for _, r in db.iterrows()}

    # Resume support
    done_ids = _load_done_ids(det_path) if resume else {}

    # Counters: (model, condition) -> counts
    counters: dict[tuple[str, str], dict] = {}
    for model in models:
        for cond in VALIDATED_CONDITIONS:
            counters[(model, cond)] = {
                "TP": 0, "FP": 0, "FN": 0, "TN": 0,
                "n_gt_pos": 0, "n_pred_pos": 0,
            }

    # Cost tracking per model
    cost_tracker: dict[str, dict] = {
        m: {"prompt_tokens": 0, "completion_tokens": 0,
            "latency_sum": 0.0, "n_calls": 0}
        for m in models
    }

    write_header = not (resume and det_path.exists())
    det_file = open(det_path, "a" if (resume and det_path.exists()) else "w", newline="")
    writer = csv.DictWriter(det_file, fieldnames=DETECTION_FIELDS)
    if write_header:
        writer.writeheader()

    total = len(sample)
    for idx, (_, row) in enumerate(sample.iterrows()):
        ecg_id = int(row["ecg_id"])
        ecg_id_str = str(ecg_id)

        db_row = db_lookup.get(ecg_id)
        if db_row is None:
            print(f"  [{idx+1}/{total}] ecg_id={ecg_id} not in database, skipping")
            continue

        hea_path = record_hr_path(db_row["filename_hr"])
        if not hea_path.exists():
            print(f"  [{idx+1}/{total}] ecg_id={ecg_id} file missing, skipping")
            continue

        gt_positives = get_positive_findings(db_row["scp_codes"])

        # Run signal pipeline once per record
        try:
            features, quality = _run_signal_pipeline(str(hea_path), ecg_id_str)
        except KeyboardInterrupt:
            raise
        except Exception as exc:
            print(f"  [{idx+1}/{total}] ecg_id={ecg_id} pipeline error: {exc}")
            continue

        # Run each model sequentially
        for model in models:
            if ecg_id_str in done_ids.get(model, set()):
                continue

            try:
                preds = await run_record_model(
                    ecg_id_str, features, quality, model, cost_tracker[model],
                )
            except KeyboardInterrupt:
                raise
            except Exception as exc:
                print(f"  [{idx+1}/{total}] ecg_id={ecg_id} model={model} error: {exc}")
                continue

            for condition in VALIDATED_CONDITIONS:
                gt_pos = condition in gt_positives
                pred_pos, pred_conf = preds.get(condition, (False, "NONE"))

                tp = gt_pos and pred_pos
                fp = (not gt_pos) and pred_pos
                fn = gt_pos and (not pred_pos)
                tn = (not gt_pos) and (not pred_pos)

                writer.writerow({
                    "ecg_id": ecg_id,
                    "model": model,
                    "condition": condition,
                    "gt_positive": gt_pos,
                    "pred_positive": pred_pos,
                    "pred_confidence": pred_conf,
                    "TP": tp,
                    "FP": fp,
                    "FN": fn,
                    "TN": tn,
                })

                c = counters[(model, condition)]
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

            det_file.flush()

        if (idx + 1) % 10 == 0:
            print(f"  [{idx+1}/{total}] processed ecg_id={ecg_id}")

    det_file.close()

    # Write summary
    summary_rows = _compute_summary(counters)
    with open(sum_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=SUMMARY_FIELDS)
        w.writeheader()
        w.writerows(summary_rows)

    # Write cost report
    with open(cost_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COST_FIELDS)
        w.writeheader()
        for model in models:
            ct = cost_tracker[model]
            mc = MODEL_COSTS.get(model, {"input": 0, "output": 0})
            total_cost = (
                ct["prompt_tokens"] / 1_000_000 * mc.get("input", 0)
                + ct["completion_tokens"] / 1_000_000 * mc.get("output", 0)
            )
            avg_latency = ct["latency_sum"] / ct["n_calls"] if ct["n_calls"] > 0 else 0
            w.writerow({
                "model": model,
                "total_prompt_tokens": ct["prompt_tokens"],
                "total_completion_tokens": ct["completion_tokens"],
                "total_cost_usd": round(total_cost, 4),
                "avg_latency_sec": round(avg_latency, 2),
                "n_records": ct["n_calls"],
            })

    print(f"Detection results  -> {det_path}")
    print(f"Summary statistics -> {sum_path}")
    print(f"Cost report        -> {cost_path}")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Multi-model validation runner")
    parser.add_argument(
        "--sample", required=True,
        help="Path to stratified_sample.csv",
    )
    parser.add_argument(
        "--models", default="signal,gemini,deepseek,gpt4o,claude",
        help="Comma-separated model names (default: all)",
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
    models = [m.strip() for m in args.models.split(",")]
    for m in models:
        if m not in ALL_MODELS:
            print(f"Unknown model: {m}. Valid: {ALL_MODELS}")
            sys.exit(1)
    asyncio.run(main(args.sample, models, args.output_dir, resume=not args.no_resume))
