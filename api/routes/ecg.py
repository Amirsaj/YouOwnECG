"""
ECG analysis routes.

POST /ecg/analyze       — upload ECG file(s), run full pipeline, return DiagnosticResult
GET  /ecg/{ecg_id}      — retrieve stored DiagnosticResult
GET  /ecg/{ecg_id}/signal — retrieve per-lead signal data, fiducials, and per-lead features

WFDB format requires both .hea and .dat files; upload both as multipart/form-data.
Single-file formats (EDF, SCP-ECG, CSV) require only one file.
"""

from __future__ import annotations
import json
import os
import shutil
import uuid
from pathlib import Path
from typing import List

import numpy as np
from fastapi import APIRouter, File, UploadFile, HTTPException, Depends, BackgroundTasks, Header, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from api.db import get_db, save_result, load_result, _result_to_dict
from pipeline.runner import run_pipeline
from agents.orchestrator import run_diagnostic

router = APIRouter(prefix="/ecg", tags=["ecg"])

UPLOAD_DIR = "data/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {".hea", ".dat", ".edf", ".scp", ".csv"}


def _save_signal_data(
    ecg_id: str,
    prep,         # PreprocessedECGRecord
    fiducials,    # FiducialTable
    features,     # FeatureObject
) -> None:
    """Save per-lead signal, fiducials, and per-lead features for frontend rendering."""
    s0 = prep.safe_window_start_sample
    s1 = prep.safe_window_end_sample
    leads = prep.lead_names
    fs = prep.fs

    # Signal: safe window only, downsampled to 250 Hz for transfer efficiency
    # (still enough for morphology rendering at typical screen widths)
    step = max(1, int(fs / 250))
    sig_safe = prep.preprocessed_signal[:, s0:s1]
    morph_safe = prep.morphology_signal[:, s0:s1]

    signal_data = {}
    for i, lead in enumerate(leads):
        signal_data[lead] = {
            "filtered": sig_safe[i, ::step].tolist(),
            "raw": morph_safe[i, ::step].tolist(),
        }

    # Fiducials: per-lead beat data
    fid_data = {}
    fpt_dict = fiducials.fpt  # dict[str, np.ndarray] — lead → (n_beats, 13) FPT
    for lead in leads:
        fpt = fpt_dict.get(lead)
        if fpt is None or len(fpt) == 0:
            fid_data[lead] = []
            continue
        beats = []
        for beat in fpt:
            b = {
                "pon": int(beat[0]) if beat[0] >= 0 else None,
                "ppeak": int(beat[1]) if beat[1] >= 0 else None,
                "poff": int(beat[2]) if beat[2] >= 0 else None,
                "qrson": int(beat[3]) if beat[3] >= 0 else None,
                "q": int(beat[4]) if beat[4] >= 0 else None,
                "r": int(beat[5]) if beat[5] >= 0 else None,
                "s": int(beat[6]) if beat[6] >= 0 else None,
                "qrsoff": int(beat[7]) if beat[7] >= 0 else None,
                "ton": int(beat[9]) if beat[9] >= 0 else None,
                "tpeak": int(beat[10]) if beat[10] >= 0 else None,
                "toff": int(beat[11]) if beat[11] >= 0 else None,
            }
            # Scale indices for downsampling
            for k, v in b.items():
                if v is not None:
                    b[k] = v // step
            beats.append(b)
        fid_data[lead] = beats

    # Per-lead feature values for annotations
    per_lead = {}
    for lead in leads:
        per_lead[lead] = {}
        if features.st_elevation_mv and lead in features.st_elevation_mv:
            per_lead[lead]["st_elevation_mv"] = features.st_elevation_mv.get(lead)
        if features.st_depression_mv and lead in features.st_depression_mv:
            per_lead[lead]["st_depression_mv"] = features.st_depression_mv.get(lead)
        if features.t_amplitude_mv and lead in features.t_amplitude_mv:
            per_lead[lead]["t_amplitude_mv"] = features.t_amplitude_mv.get(lead)
        if features.t_morphology and lead in features.t_morphology:
            per_lead[lead]["t_morphology"] = features.t_morphology.get(lead)
        if features.r_amplitude_mv and lead in features.r_amplitude_mv:
            per_lead[lead]["r_amplitude_mv"] = features.r_amplitude_mv.get(lead)
        if features.s_amplitude_mv and lead in features.s_amplitude_mv:
            per_lead[lead]["s_amplitude_mv"] = features.s_amplitude_mv.get(lead)
        if features.st_morphology and lead in features.st_morphology:
            per_lead[lead]["st_morphology"] = features.st_morphology.get(lead)

    payload = {
        "ecg_id": ecg_id,
        "leads": leads,
        "fs": fs / step,  # effective sample rate after downsampling
        "original_fs": fs,
        "downsample_step": step,
        "safe_window_duration_sec": (s1 - s0) / fs,
        "n_samples": len(sig_safe[0, ::step]),
        "signal": signal_data,
        "fiducials": fid_data,
        "per_lead_features": per_lead,
        "global_features": {
            "heart_rate_bpm": _to_json(features.heart_rate_ventricular_bpm),
            "pr_interval_ms": _to_json(features.pr_interval_ms),
            "qrs_duration_ms": _to_json(features.qrs_duration_global_ms),
            "qt_interval_ms": _to_json(features.qt_interval_ms),
            "qtc_bazett_ms": _to_json(features.qtc_bazett_ms),
            "qrs_axis_deg": _to_json(features.qrs_axis_deg),
            "dominant_rhythm": features.dominant_rhythm,
            "rhythm_regular": _to_json(features.rhythm_regular),
            "lbbb": _to_json(features.lbbb),
            "rbbb": _to_json(features.rbbb),
            "wpw_pattern": _to_json(features.wpw_pattern),
        },
    }

    out_path = Path(UPLOAD_DIR) / ecg_id / "signal_data.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(payload, f)


def _to_json(val):
    """Convert numpy types to JSON-safe Python types."""
    if isinstance(val, (np.floating, np.float32, np.float64)):
        return round(float(val), 4)
    if isinstance(val, np.bool_):
        return bool(val)
    if isinstance(val, (np.integer,)):
        return int(val)
    return val


@router.post("/analyze")
async def analyze_ecg(
    request: Request,
    files: List[UploadFile] = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
):
    """
    Upload ECG file(s) and run the full YouOwnECG pipeline.

    For WFDB format: upload both .hea and .dat files.
    For single-file formats (EDF, SCP-ECG, CSV): upload one file.
    DeepSeek agents are called if DEEPSEEK_API_KEY is set; otherwise
    a signal-only result is returned (useful for local testing).
    """
    for f in files:
        ext = os.path.splitext(f.filename or "")[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type {ext!r}. Accepted: {ALLOWED_EXTENSIONS}",
            )

    ecg_id = str(uuid.uuid4())
    upload_subdir = os.path.join(UPLOAD_DIR, ecg_id)
    os.makedirs(upload_subdir, exist_ok=True)

    hea_path = None
    primary_path = None

    for upload in files:
        original_name = upload.filename or f"ecg{os.path.splitext(upload.filename or '')[1]}"
        dest = os.path.join(upload_subdir, original_name)
        try:
            with open(dest, "wb") as f:
                shutil.copyfileobj(upload.file, f)
        finally:
            upload.file.close()
        ext = os.path.splitext(original_name)[1].lower()
        if ext == ".hea":
            hea_path = dest
        elif ext in {".edf", ".scp", ".csv"}:
            primary_path = dest

    # For WFDB, primary entry point is the .hea file
    entry_path = hea_path or primary_path
    if entry_path is None:
        # .dat-only upload — not supported without .hea
        raise HTTPException(status_code=400, detail="No recognised entry-point file (.hea, .edf, .scp, .csv) found.")


    # Run SDA-1 pipeline
    try:
        features, vision = await run_pipeline(entry_path, ecg_id=ecg_id, vl2_client=None)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Pipeline error: {exc}")

    # Save signal data for disease dashboard rendering
    try:
        from pipeline.ingestion import load_ecg as _load
        from pipeline.preprocessing import preprocess as _preprocess
        from pipeline.fiducials import detect_fiducials as _detect_fid
        from pipeline.quality import assess_quality as _assess_q

        _raw = _load(entry_path, ecg_id=ecg_id)
        _prep = _preprocess(_raw)
        _qual = _assess_q(_prep)
        _fid = _detect_fid(_prep, _qual)
        _save_signal_data(ecg_id, _prep, _fid, features)
    except Exception:
        pass  # signal data is optional — don't block analysis

    # Run SDA-2 agents (if API key available)
    api_key = os.environ.get("DEEPSEEK_API_KEY", "")
    db = await get_db()

    if api_key:
        try:
            # Quality report needed for orchestrator
            from pipeline.ingestion import load_ecg
            from pipeline.preprocessing import preprocess
            from pipeline.quality import assess_quality

            raw = load_ecg(entry_path, ecg_id=ecg_id)
            prep = preprocess(raw)
            quality = assess_quality(prep)

            rag_store = getattr(request.app.state, "rag_store", None)
            result = await run_diagnostic(features, vision, quality, db=db, rag_store=rag_store)
        except Exception as exc:
            await db.close()
            raise HTTPException(status_code=500, detail=f"Agent error: {exc}")
    else:
        # Signal-only result — generate findings from features using deterministic rules
        from agents.schemas import DiagnosticResult
        from agents.signal_findings import generate_signal_findings, generate_stat_alerts
        from agents.context_builder import build_measurements_block
        from pipeline.quality import assess_quality
        from pipeline.ingestion import load_ecg
        from pipeline.preprocessing import preprocess

        raw = load_ecg(entry_path, ecg_id=ecg_id)
        prep = preprocess(raw)
        quality = assess_quality(prep)

        findings = generate_signal_findings(features)
        stat_alerts = generate_stat_alerts(findings)

        result = DiagnosticResult(
            ecg_id=ecg_id,
            findings=findings,
            stat_alerts=stat_alerts,
            measurements=build_measurements_block(features),
            overall_quality=quality.overall_quality,
            pipeline_version="1.0.0",
            model_version="signal-only",
        )

    await save_result(db, result)
    await db.close()

    return JSONResponse(content=_result_to_dict(result))


@router.get("/{ecg_id}")
async def get_ecg_result(ecg_id: str):
    """Retrieve a stored DiagnosticResult by ECG ID."""
    db = await get_db()
    result = await load_result(db, ecg_id)
    await db.close()

    if result is None:
        raise HTTPException(status_code=404, detail=f"ECG ID {ecg_id!r} not found")

    return JSONResponse(content=result)


@router.get("/{ecg_id}/signal")
async def get_signal_data(ecg_id: str, leads: str = ""):
    """
    Retrieve per-lead signal waveforms, fiducial points, and per-lead features.

    Optional query param `leads` (comma-separated) to filter specific leads.
    Returns full signal data if no filter is provided.
    """
    signal_path = Path(UPLOAD_DIR) / ecg_id / "signal_data.json"
    if not signal_path.exists():
        raise HTTPException(status_code=404, detail=f"Signal data not found for ECG ID {ecg_id!r}")

    with open(signal_path) as f:
        data = json.load(f)

    # Optional lead filtering for disease dashboards
    if leads:
        requested = [l.strip() for l in leads.split(",")]
        data["signal"] = {l: v for l, v in data["signal"].items() if l in requested}
        data["fiducials"] = {l: v for l, v in data["fiducials"].items() if l in requested}
        data["per_lead_features"] = {l: v for l, v in data["per_lead_features"].items() if l in requested}
        data["leads"] = [l for l in data["leads"] if l in requested]

    return JSONResponse(content=data)


# Permitted roles for override (Node 3.4)
_OVERRIDE_ROLES = {"CARDIOLOGIST", "PHYSICIAN"}


class OverrideRequest(BaseModel):
    finding_type: str
    reason: str
    user_role: str
    user_id: str


@router.post("/{ecg_id}/override")
async def override_finding(ecg_id: str, body: OverrideRequest):
    """
    Record a clinical override for a finding.
    Requires user_role ∈ {CARDIOLOGIST, PHYSICIAN} (Node 3.4).
    Logged to agent_audit_log as override entry.
    """
    if body.user_role not in _OVERRIDE_ROLES:
        raise HTTPException(
            status_code=403,
            detail=f"Role {body.user_role!r} is not permitted to override findings.",
        )

    db = await get_db()
    result = await load_result(db, ecg_id)
    if result is None:
        await db.close()
        raise HTTPException(status_code=404, detail=f"ECG ID {ecg_id!r} not found")

    import uuid, json
    call_id = str(uuid.uuid4())
    try:
        await db.execute(
            """
            INSERT INTO agent_audit_log
              (call_id, ecg_id, agent_name, model_id, prompt_tokens, completion_tokens,
               reasoning_tokens, latency_sec)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                call_id, ecg_id,
                f"OVERRIDE:{body.user_id}:{body.user_role}",
                f"override:{body.finding_type}:{body.reason[:120]}",
                0, 0, 0, 0.0,
            ),
        )
        await db.commit()
    except Exception:
        pass  # fail-open: audit failure must not block clinical workflow
    finally:
        await db.close()

    return {"status": "recorded", "call_id": call_id}
