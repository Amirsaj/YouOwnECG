"""Run selected PTB-XL patients through YouOwnECG pipeline with DeepSeek."""

import asyncio
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

PTBXL_ROOT = Path("/Users/amirsadjadtaleban/Documents/PTBXL/ptb-xl-a-comprehensive-electrocardiographic-feature-dataset-1.0.1")
SELECTED = Path("/Users/amirsadjadtaleban/Documents/NewECG_Agentic/validation/selected_patients.json")
OUTPUT = Path(__file__).resolve().parent / "results" / "deepseek_comparison_youownecg.json"


async def run_one(ecg_id: int, wfdb_path: str) -> dict:
    """Run one patient through the full YouOwnECG pipeline with DeepSeek agents."""
    from pipeline.ingestion import load_ecg
    from pipeline.preprocessing import preprocess
    from pipeline.quality import assess_quality
    from pipeline.fiducials import detect_fiducials
    from pipeline.features import extract_features
    from pipeline.schemas import VisionVerificationResult
    from agents.orchestrator import run_diagnostic
    from agents.deepseek import call_agent

    t0 = time.time()
    result = {
        "ecg_id": ecg_id,
        "findings": [],
        "stat_alerts": [],
        "measurements": {},
        "errors": [],
        "latency_sec": 0.0,
        "usage": {"prompt_tokens": 0, "completion_tokens": 0},
    }

    try:
        raw = load_ecg(wfdb_path + ".hea", ecg_id=str(ecg_id))
        prep = preprocess(raw)
        qual = assess_quality(prep)
        fid = detect_fiducials(prep, qual)
        feats = extract_features(prep, qual, fid)
    except Exception as e:
        result["errors"].append(f"Signal pipeline error: {e}")
        result["latency_sec"] = time.time() - t0
        return result

    no_vision = VisionVerificationResult(
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

    try:
        diag = await run_diagnostic(
            features=feats,
            vision=no_vision,
            quality=qual,
            db=None,
            rag_store=None,
            call_agent_fn=call_agent,
            record=prep,
            fiducials=fid,
        )

        for f in diag.findings:
            result["findings"].append({
                "finding_type": f.finding_type,
                "confidence": f.confidence,
                "agent": f.agent_source,
                "clinical_summary": f.clinical_summary,
            })

        for a in diag.stat_alerts:
            result["stat_alerts"].append({
                "finding_type": a.finding_type,
                "confidence": a.confidence,
                "message": a.message,
            })

        result["measurements"] = diag.measurements if isinstance(diag.measurements, dict) else {}

    except Exception as e:
        result["errors"].append(f"Diagnostic error: {e}")

    result["latency_sec"] = time.time() - t0
    return result


async def main():
    with open(SELECTED) as f:
        selected = json.load(f)

    all_results = {}
    for disease, patients in selected.items():
        all_results[disease] = []
        for p in patients:
            eid = p["ecg_id"]
            wfdb_path = str(PTBXL_ROOT / p["file_hr"])
            print(f"[YouOwnECG] Running ecg_id={eid} for {disease}...", flush=True)
            r = await run_one(eid, wfdb_path)
            all_results[disease].append(r)
            finding_types = [f["finding_type"] for f in r["findings"]]
            print(f"  -> findings: {finding_types}, errors: {r['errors']}", flush=True)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT, "w") as f:
        json.dump(all_results, f, indent=2, default=str)
    print(f"\nSaved to {OUTPUT}")


if __name__ == "__main__":
    asyncio.run(main())
