"""
Interactive narration comparison dashboard.

Serves a single-page web app with:
  - 12-lead ECG waveform viewer (zoomable, per-lead, fiducial markers)
  - Beat-level zoom strips
  - Side-by-side narration panels (pipeline vs Claude)
  - Condition checklist with TP/FP/FN highlighting
  - Record picker filtered by condition
  - Measurement summary badges

Usage:
    python3 rl/dashboard.py                      # default port 8050
    python3 rl/dashboard.py --port 8050
"""

from __future__ import annotations
import ast
import base64
import csv
import io
import json
import os
import sys
from pathlib import Path

import numpy as np

# Ensure project root on path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from flask import Flask, render_template_string, request, jsonify

from validation.ptbxl_mapping import PTBXL_DIR, get_positive_findings, VALIDATED_CONDITIONS
from pipeline.ingestion import load_ecg
from pipeline.preprocessing import preprocess
from pipeline.quality import assess_quality
from pipeline.fiducials import detect_fiducials
from pipeline.features import extract_features
from pipeline.narrator import narrate_ecg
from agents.signal_findings import generate_signal_findings, generate_stat_alerts

app = Flask(__name__)

# Cache loaded records to avoid re-processing
_cache: dict[int, dict] = {}

SAMPLES_CSV = Path(__file__).parent.parent / "validation" / "disease_test_samples.csv"

# ─── Data helpers ────────────────────────────────────────────────────────

def _load_samples() -> list[dict]:
    rows = []
    if SAMPLES_CSV.exists():
        with open(SAMPLES_CSV) as f:
            for row in csv.DictReader(f):
                rows.append(row)
    return rows


def _process_record(ecg_id: int, force_reload: bool = False) -> dict:
    if ecg_id in _cache and not force_reload:
        return _cache[ecg_id]

    subfolder = f"{(ecg_id - 1) // 1000 * 1000:05d}"
    hea = str(PTBXL_DIR / f"records500/{subfolder}/{ecg_id:05d}_hr.hea")

    raw = load_ecg(hea, ecg_id=str(ecg_id))
    prep = preprocess(raw)
    qual = assess_quality(prep)
    fid = detect_fiducials(prep, qual)
    feats = extract_features(prep, qual, fid)
    narr = narrate_ecg(prep, fid, feats)
    findings = generate_signal_findings(feats)
    stat_alerts = generate_stat_alerts(findings)

    result = {
        "record": prep,
        "fiducials": fid,
        "features": feats,
        "narration": narr,
        "findings": findings,
        "stat_alerts": stat_alerts,
        "quality": qual,
    }
    _cache[ecg_id] = result
    return result


def _ecg_signals_json(record, fiducials) -> dict:
    """Extract per-lead waveform data as JSON-serializable arrays."""
    morph = record.morphology_signal
    fs = record.fs
    leads = record.lead_names
    s0 = record.safe_window_start_sample
    s1 = record.safe_window_end_sample

    signals = {}
    for i, lead in enumerate(leads):
        sig = morph[i, s0:s1].astype(float) / 1000.0  # µV → mV
        # Downsample for browser if > 2500 samples
        if len(sig) > 2500:
            step = len(sig) // 2500
            sig = sig[::step]
            t = np.arange(len(sig)) * step / fs
        else:
            t = np.arange(len(sig)) / fs
        signals[lead] = {
            "time": t.tolist(),
            "amplitude": sig.tolist(),
        }

    # Fiducial markers for reference lead
    fid_markers = {}
    for lead in leads:
        if lead not in fiducials.fpt:
            continue
        fpt = fiducials.fpt[lead]
        markers = []
        for beat_idx, beat in enumerate(fpt):
            m = {"beat": beat_idx + 1}
            col_names = ["pon", "ppeak", "poff", "qrson", "q", "r", "s", "qrsoff",
                         "l", "ton", "tpeak", "toff"]
            for ci, name in enumerate(col_names):
                val = int(beat[ci])
                if val >= 0:
                    m[name] = round(val / fs, 4)  # convert to seconds
            markers.append(m)
        fid_markers[lead] = markers

    return {"signals": signals, "fiducials": fid_markers, "fs": fs}


def _get_vision_assessment(ecg_id: int) -> tuple[str, str]:
    """Get vision LLM assessment. Returns (text, provider)."""
    data = _process_record(ecg_id)
    try:
        from rl.vision_reward import get_visual_assessment
        text, provider = get_visual_assessment(
            data["record"], data["fiducials"], data["features"]
        )
        return text, provider
    except Exception as e:
        return f"Vision LLM unavailable: {e}", "error"


# ─── Routes ──────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template_string(DASHBOARD_HTML)


@app.route("/api/samples")
def api_samples():
    """Return list of available test samples."""
    rows = _load_samples()
    conditions = sorted(set(r["condition"] for r in rows))
    return jsonify({"samples": rows, "conditions": conditions})


REVIEWS_DIR = Path(__file__).parent / "reviews"
REVIEWS_DIR.mkdir(exist_ok=True)

RUNS_DIR = Path(__file__).parent / "runs"
RUNS_DIR.mkdir(exist_ok=True)


@app.route("/api/save_run", methods=["POST"])
def api_save_run():
    """Persist a complete run (gemma + llm narrations + RAG diagnosis)."""
    from datetime import datetime
    payload = request.get_json()

    ecg_id = payload.get("ecg_id")
    condition = payload.get("condition", "unknown")
    patient_num = payload.get("patient_num")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    date_human = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Filename: condition_patientN_ecgID_YYYYMMDD_HHMMSS.json
    pnum_str = f"_patient{patient_num}" if patient_num else ""
    filename = f"{condition}{pnum_str}_ecg{ecg_id}_{timestamp}.json"
    filepath = RUNS_DIR / filename

    payload["saved_at"] = date_human
    payload["filename"] = filename

    with open(filepath, "w") as f:
        json.dump(payload, f, indent=2)

    return jsonify({"status": "saved", "filename": filename, "path": str(filepath)})


@app.route("/api/list_runs")
def api_list_runs():
    """List saved runs with metadata."""
    runs = []
    for f in sorted(RUNS_DIR.glob("*.json"), reverse=True):
        try:
            with open(f) as fp:
                data = json.load(fp)
            runs.append({
                "filename": f.name,
                "ecg_id": data.get("ecg_id"),
                "condition": data.get("condition"),
                "saved_at": data.get("saved_at"),
                "has_gemma": bool(data.get("gemma_results")),
                "has_llm": bool(data.get("llm_results")),
                "has_rag": bool(data.get("rag_result")),
            })
        except Exception:
            continue
    return jsonify({"runs": runs})


@app.route("/api/load_run/<filename>")
def api_load_run(filename: str):
    """Load a saved run by filename."""
    filepath = RUNS_DIR / filename
    if not filepath.exists():
        return jsonify({"error": "Not found"}), 404
    with open(filepath) as f:
        return jsonify(json.load(f))


@app.route("/api/disease_tracker")
def api_disease_tracker():
    """Show which diseases have been reviewed (2 samples each)."""
    samples = _load_samples()

    # Group by condition
    from collections import defaultdict
    by_cond = defaultdict(list)
    for s in samples:
        by_cond[s["condition"]].append(int(s["ecg_id"]))

    # Check which have review .md files
    tracker = []
    for cond in sorted(by_cond.keys()):
        ecg_ids = by_cond[cond]
        reviewed = []
        for i, eid in enumerate(ecg_ids[:2]):
            md_path = REVIEWS_DIR / f"{cond}_patient{i+1}.md"
            reviewed.append({
                "ecg_id": eid,
                "patient_num": i + 1,
                "reviewed": md_path.exists(),
                "md_file": str(md_path.name),
            })
        tracker.append({
            "condition": cond,
            "total_samples": len(ecg_ids),
            "patients": reviewed,
            "done": all(p["reviewed"] for p in reviewed),
        })

    return jsonify({"tracker": tracker})


@app.route("/api/save_review", methods=["POST"])
def api_save_review():
    """Save a review .md file for a disease+patient."""
    payload = request.get_json()
    condition = payload["condition"]
    patient_num = payload["patient_num"]
    ecg_id = payload["ecg_id"]
    content = payload["content"]

    md_path = REVIEWS_DIR / f"{condition}_patient{patient_num}.md"
    with open(md_path, "w") as f:
        f.write(content)

    return jsonify({"status": "saved", "path": str(md_path)})


@app.route("/api/load_review/<condition>/<int:patient_num>")
def api_load_review(condition: str, patient_num: int):
    """Load existing review .md file."""
    md_path = REVIEWS_DIR / f"{condition}_patient{patient_num}.md"
    if md_path.exists():
        return jsonify({"content": md_path.read_text(), "exists": True})
    return jsonify({"content": "", "exists": False})


TEMPLATES_JSON = Path(__file__).parent.parent / "pipeline" / "shape_templates.json"


@app.route("/api/shapes/<int:ecg_id>/<int:beat_idx>")
def api_shapes(ecg_id: int, beat_idx: int):
    """Classify all 4 segment shapes for one beat across all leads with lead context."""
    data = _process_record(ecg_id)
    from pipeline.shape_classifier import classify_segment_shape
    from pipeline.lead_context import build_lead_context, detect_heart_position
    from pipeline.fiducials import (
        COL_PON, COL_PPEAK, COL_POFF, COL_QRSON, COL_R,
        COL_QRSOFF, COL_TON, COL_TPEAK, COL_TOFF,
    )

    s0 = data["record"].safe_window_start_sample
    fs = data["record"].fs
    feats = data["features"]
    results = {}
    lead_contexts = {}

    for lead in data["record"].lead_names:
        if lead not in data["fiducials"].fpt:
            continue
        fpt = data["fiducials"].fpt[lead]
        if beat_idx >= len(fpt):
            continue

        li = data["record"].lead_names.index(lead)
        sig = data["record"].morphology_signal[li, s0:data["record"].safe_window_end_sample].astype(float)
        beat = fpt[beat_idx]

        # Build lead context
        ctx = build_lead_context(lead, features=feats, beat_idx=beat_idx,
                                  signal=sig, fpt_beat=beat, fs=fs)

        lead_contexts[lead] = {
            "territory": ctx.territory,
            "is_avr": ctx.is_avr,
            "j_point_mv": round(ctx.j_point_mv, 3) if ctx.j_point_mv else None,
            "terminal_qrs": ctx.terminal_qrs_polarity,
            "normal_qrs": ctx.normal_qrs_pattern,
            "normal_t": ctx.normal_t_polarity,
            "rotation": ctx.horizontal_rotation,
            "transition_shifted": ctx.is_transition_shifted,
            "lbbb": ctx.lbbb,
            "rbbb": ctx.rbbb,
        }

        lead_shapes = {}

        # P-wave
        p_on, p_pk, p_off = int(beat[COL_PON]), int(beat[COL_PPEAK]), int(beat[COL_POFF])
        if p_on >= 0 and p_pk >= 0 and p_off >= 0:
            cls = classify_segment_shape(sig, p_on, p_pk, p_off, fs, "P", lead_context=ctx)
            lead_shapes["P"] = {"code": cls.code, "name": cls.name, "confidence": cls.confidence,
                                "features": cls.features, "runner_up": cls.runner_up}

        # QRS
        qrs_on, r_pk, qrs_off = int(beat[COL_QRSON]), int(beat[COL_R]), int(beat[COL_QRSOFF])
        if qrs_on >= 0 and r_pk >= 0 and qrs_off >= 0:
            cls = classify_segment_shape(sig, qrs_on, r_pk, qrs_off, fs, "QRS", lead_context=ctx)
            lead_shapes["QRS"] = {"code": cls.code, "name": cls.name, "confidence": cls.confidence,
                                  "features": cls.features, "runner_up": cls.runner_up}

        # ST
        j_point = int(beat[COL_QRSOFF])
        t_on = int(beat[COL_TON])
        if j_point >= 0 and t_on >= 0 and t_on > j_point:
            st_mid = (j_point + t_on) // 2
            cls = classify_segment_shape(sig, j_point, st_mid, t_on, fs, "ST", lead_context=ctx)
            lead_shapes["ST"] = {"code": cls.code, "name": cls.name, "confidence": cls.confidence,
                                 "features": cls.features, "runner_up": cls.runner_up}

        # T-wave
        t_on2, t_pk, t_off = int(beat[COL_TON]), int(beat[COL_TPEAK]), int(beat[COL_TOFF])
        if t_on2 >= 0 and t_pk >= 0 and t_off >= 0:
            cls = classify_segment_shape(sig, t_on2, t_pk, t_off, fs, "T", lead_context=ctx)
            lead_shapes["T"] = {"code": cls.code, "name": cls.name, "confidence": cls.confidence,
                                "features": cls.features, "runner_up": cls.runner_up}

        results[lead] = lead_shapes

    # Detect composite patterns per lead
    from pipeline.shape_classifier import detect_composite_patterns, ShapeClassification
    composites = {}
    for lead, lead_shapes in results.items():
        shape_cls = {}
        for seg, info in lead_shapes.items():
            shape_cls[seg] = ShapeClassification(
                code=info["code"], name=info["name"], confidence=info["confidence"],
                features=info["features"], runner_up=info["runner_up"]
            )
        comps = detect_composite_patterns(shape_cls)
        if comps:
            composites[lead] = [{"code": c.code, "name": c.name,
                                  "clinical_name": c.clinical_name,
                                  "confidence": c.confidence,
                                  "segments": c.segments_matched} for c in comps]

    heart_pos = detect_heart_position(feats)

    return jsonify({
        "ecg_id": ecg_id, "beat": beat_idx,
        "shapes": results,
        "composites": composites,
        "lead_contexts": lead_contexts,
        "heart_position": heart_pos,
    })


@app.route("/api/shape_waveform/<int:ecg_id>/<int:beat_idx>/<lead>/<segment>")
def api_shape_waveform(ecg_id: int, beat_idx: int, lead: str, segment: str):
    """Return the normalized 64-sample waveform for one segment + its shape features."""
    data = _process_record(ecg_id)
    from pipeline.shape_classifier import extract_segment_features
    from pipeline.fiducials import (
        COL_PON, COL_PPEAK, COL_POFF, COL_QRSON, COL_R,
        COL_QRSOFF, COL_TON, COL_TPEAK, COL_TOFF,
    )

    if lead not in data["fiducials"].fpt:
        return jsonify({"error": f"Lead {lead} not found"})

    fpt = data["fiducials"].fpt[lead]
    if beat_idx >= len(fpt):
        return jsonify({"error": f"Beat {beat_idx} out of range"})

    s0 = data["record"].safe_window_start_sample
    fs = data["record"].fs
    li = data["record"].lead_names.index(lead)
    sig = data["record"].morphology_signal[li, s0:data["record"].safe_window_end_sample].astype(float)
    beat = fpt[beat_idx]

    seg_map = {
        "P": (int(beat[COL_PON]), int(beat[COL_PPEAK]), int(beat[COL_POFF])),
        "QRS": (int(beat[COL_QRSON]), int(beat[COL_R]), int(beat[COL_QRSOFF])),
        "ST": (int(beat[COL_QRSOFF]), (int(beat[COL_QRSOFF]) + int(beat[COL_TON])) // 2, int(beat[COL_TON])),
        "T": (int(beat[COL_TON]), int(beat[COL_TPEAK]), int(beat[COL_TOFF])),
    }
    if segment not in seg_map:
        return jsonify({"error": f"Unknown segment {segment}"})

    onset, peak, offset = seg_map[segment]
    feats = extract_segment_features(sig, onset, peak, offset, fs, segment)

    waveform = feats.normalized_waveform.tolist() if feats.normalized_waveform is not None else []

    return jsonify({
        "lead": lead, "beat": beat_idx, "segment": segment,
        "waveform": waveform,
        "features": {
            "symmetry": feats.symmetry, "base_width_ratio": feats.base_width_ratio,
            "peak_sharpness": feats.peak_sharpness, "n_peaks": feats.n_peaks,
            "polarity": feats.polarity, "curvature": feats.curvature,
            "amplitude_mv": feats.amplitude_mv, "duration_ms": feats.duration_ms,
        },
    })


@app.route("/api/segment_agent/<int:ecg_id>/<int:beat_idx>/<lead>/<segment>")
def api_segment_agent(ecg_id: int, beat_idx: int, lead: str, segment: str):
    """Run segment-specific vision agent (P/QRS/ST/T specialist) on one lead."""
    import base64 as b64mod
    data = _process_record(ecg_id)
    from rl.vision_reward import render_territory_beat_strip, TERRITORIES

    # Find which territory this lead belongs to
    territory = None
    territory_leads = None
    for t, info in TERRITORIES.items():
        if lead in info["leads"]:
            territory = t
            territory_leads = info["leads"]
            break
    if not territory:
        return jsonify({"error": f"Lead {lead} not in any territory"})

    # Render the strip
    result = render_territory_beat_strip(
        data["record"], data["fiducials"], beat_idx, territory, territory_leads,
        features=data["features"],
    )
    if not result:
        return jsonify({"error": "Could not render strip"})

    img_bytes, _ = result

    # Build measurements context
    f = data["features"]
    meas = (
        f"HR:{f.heart_rate_ventricular_bpm:.0f}bpm "
        f"PR:{f.pr_interval_ms}ms QRS:{f.qrs_duration_global_ms}ms "
        f"QTc:{f.qtc_bazett_ms:.0f}ms Axis:{f.qrs_axis_deg:.0f}°"
    )

    # Measurements are annotated on the image — just run the segment agent
    from pipeline.segment_agents import classify_shape_with_vision, SEGMENT_AGENTS
    result = classify_shape_with_vision(img_bytes, segment, lead, beat_idx, meas)

    result["image"] = b64mod.b64encode(img_bytes).decode()
    result["prompt"] = (
        f"Lead: {lead} | Beat: {beat_idx + 1} | Segment: {segment}\n"
        f"{meas}\n\n"
        f"{SEGMENT_AGENTS.get(segment, '')}"
    )

    return jsonify(result)


@app.route("/api/save_template", methods=["POST"])
def api_save_template():
    """Save a curated shape template example."""
    payload = request.get_json()
    # Load existing templates
    if TEMPLATES_JSON.exists():
        with open(TEMPLATES_JSON) as f:
            templates = json.load(f)
    else:
        templates = []

    templates.append({
        "ecg_id": payload["ecg_id"],
        "lead": payload["lead"],
        "beat_idx": payload["beat_idx"],
        "segment": payload["segment"],
        "shape_code": payload["shape_code"],
        "waveform": payload["waveform"],
        "features": payload["features"],
        "notes": payload.get("notes", ""),
    })

    with open(TEMPLATES_JSON, "w") as f:
        json.dump(templates, f, indent=2)

    return jsonify({"status": "saved", "total_templates": len(templates)})


@app.route("/api/templates_summary")
def api_templates_summary():
    """Return count of curated templates per shape code."""
    if not TEMPLATES_JSON.exists():
        return jsonify({"templates": {}})
    with open(TEMPLATES_JSON) as f:
        templates = json.load(f)
    from collections import Counter
    counts = Counter(t["shape_code"] for t in templates)
    return jsonify({"templates": dict(counts), "total": len(templates)})


@app.route("/api/visual_narrate/<int:ecg_id>/<int:beat_idx>")
def api_visual_narrate(ecg_id: int, beat_idx: int):
    """Get vision-based morphology description for one beat, including the images sent."""
    import base64 as b64mod
    data = _process_record(ecg_id)
    try:
        from pipeline.visual_narrator import describe_beat_visually
        from rl.vision_reward import render_territory_beat_strip, TERRITORIES

        # Get descriptions
        descriptions = describe_beat_visually(
            data["record"], data["fiducials"], data["features"], beat_idx
        )

        # Also render the images that were sent (so user can see them)
        swt = request.args.get("swt", "1") == "1"
        rec = _apply_swt(data["record"]) if swt else data["record"]

        images = {}
        for territory, info in TERRITORIES.items():
            result = render_territory_beat_strip(
                rec, data["fiducials"], beat_idx, territory, info["leads"],
                features=data["features"],
            )
            if result:
                img, _ = result
                images[territory] = b64mod.b64encode(img).decode()

        return jsonify({
            "beat": beat_idx,
            "descriptions": descriptions,
            "images": images,
            "status": "ok",
        })
    except Exception as e:
        return jsonify({"beat": beat_idx, "descriptions": {}, "images": {}, "status": f"error: {e}"})


@app.route("/api/clear_cache")
def api_clear_cache():
    _cache.clear()
    return jsonify({"status": "cache cleared"})


@app.route("/api/correct_fiducials/<int:ecg_id>/<int:beat_idx>", methods=["POST"])
def api_correct_fiducials(ecg_id: int, beat_idx: int):
    """
    Run Gemma 12B agentic fiducial correction on one beat.

    Gemma inspects rendered strip images, calls tools to move fiducial markers,
    re-renders, and accepts when satisfied. Corrected FiducialTable is stored
    back in the cache so subsequent calls use corrected fiducials.

    Returns JSON with change log and final territory images (base64).
    """
    import base64 as b64mod
    from pipeline.fiducial_correction_agent import run_fiducial_correction
    from rl.vision_reward import render_territory_beat_strip, TERRITORIES

    model = request.args.get("model", "gemma3:12b")

    try:
        data = _process_record(ecg_id)
    except Exception as e:
        return jsonify({"error": f"Failed to load ECG {ecg_id}: {e}"}), 404

    record = data["record"]
    fiducials = data["fiducials"]
    features = data["features"]

    if beat_idx >= fiducials.n_beats:
        return jsonify({
            "error": f"beat_idx {beat_idx} out of range (n_beats={fiducials.n_beats})"
        }), 400

    try:
        corrected_fid, change_log, morphology_reports = run_fiducial_correction(
            record, fiducials, features, beat_idx=beat_idx, model=model
        )
    except Exception as e:
        return jsonify({"error": f"Correction failed: {e}"}), 500

    # Store corrected fiducials back in cache so downstream calls benefit
    _cache[ecg_id]["fiducials"] = corrected_fid

    # Render final territory images with corrected fiducials
    final_images = {}
    for territory, info in TERRITORIES.items():
        result = render_territory_beat_strip(
            record, corrected_fid, beat_idx, territory, info["leads"], features=features
        )
        if result:
            img_bytes, _ = result
            final_images[territory] = b64mod.b64encode(img_bytes).decode()

    return jsonify({
        "ecg_id": ecg_id,
        "beat_idx": beat_idx,
        "model": model,
        "n_changes": len(change_log),
        "changes": change_log,
        "corrected_confidence": corrected_fid.fiducial_confidence,
        "final_images": final_images,
        "morphology_reports": morphology_reports,
    })


@app.route("/api/record/<int:ecg_id>")
def api_record(ecg_id: int):
    """Process a record and return all data for the dashboard."""
    # Find ground truth from samples CSV
    gt_scp = {}
    condition = "unknown"
    for row in _load_samples():
        if int(row["ecg_id"]) == ecg_id:
            try:
                gt_scp = ast.literal_eval(row["scp_codes"])
            except Exception:
                pass
            condition = row["condition"]
            break

    gt_findings = get_positive_findings(gt_scp, min_likelihood=50.0)

    data = _process_record(ecg_id)
    feats = data["features"]
    findings = data["findings"]

    pred_types = {f.finding_type for f in findings}

    # Condition checklist
    checklist = []
    all_conditions = sorted(set(VALIDATED_CONDITIONS) | gt_findings | pred_types)
    for cond in all_conditions:
        in_gt = cond in gt_findings
        in_pred = cond in pred_types
        if in_gt and in_pred:
            status = "TP"
        elif in_pred and not in_gt:
            status = "FP"
        elif in_gt and not in_pred:
            status = "FN"
        else:
            status = "TN"
        conf = next((f.confidence for f in findings if f.finding_type == cond), None)
        checklist.append({
            "condition": cond,
            "status": status,
            "in_gt": in_gt,
            "in_pred": in_pred,
            "confidence": conf,
        })

    # Measurements
    measurements = {
        "hr_bpm": round(feats.heart_rate_ventricular_bpm, 1) if feats.heart_rate_ventricular_bpm else None,
        "pr_ms": feats.pr_interval_ms,
        "qrs_ms": feats.qrs_duration_global_ms,
        "qtc_ms": round(feats.qtc_bazett_ms, 1) if feats.qtc_bazett_ms else None,
        "axis_deg": round(feats.qrs_axis_deg, 1) if feats.qrs_axis_deg else None,
        "rhythm": feats.dominant_rhythm,
        "regular": feats.rhythm_regular,
        "lbbb": feats.lbbb,
        "rbbb": feats.rbbb,
        "wpw": feats.wpw_pattern,
        "quality": data["quality"].overall_quality,
        "n_beats": feats.beat_summary.n_beats,
    }

    # Findings detail
    findings_list = []
    for f in findings:
        findings_list.append({
            "type": f.finding_type,
            "confidence": f.confidence,
            "summary": f.clinical_summary,
            "detail": f.technical_detail,
            "stat": f.stat_alert_fires,
        })

    # ECG signals
    sig_data = _ecg_signals_json(data["record"], data["fiducials"])

    # Heart position context
    from pipeline.lead_context import detect_heart_position
    heart_pos = detect_heart_position(feats)

    return jsonify({
        "ecg_id": ecg_id,
        "condition": condition,
        "ground_truth": sorted(gt_findings),
        "measurements": measurements,
        "findings": findings_list,
        "checklist": checklist,
        "narration": data["narration"],
        "stat_alerts": [a.finding_type for a in data["stat_alerts"]],
        "signals": sig_data["signals"],
        "fiducials": sig_data["fiducials"],
        "fs": sig_data["fs"],
        "heart_position": heart_pos,
    })


@app.route("/api/vision/<int:ecg_id>")
def api_vision(ecg_id: int):
    """Get vision LLM assessment — all beats."""
    text, provider = _get_vision_assessment(ecg_id)
    return jsonify({"assessment": text, "provider": provider})


@app.route("/api/vision/<int:ecg_id>/beat/<int:beat_idx>")
def api_vision_beat(ecg_id: int, beat_idx: int):
    """Get vision LLM assessment for a single beat."""
    data = _process_record(ecg_id)
    swt = request.args.get("swt", "1") == "1"
    provider_override = request.args.get("provider")  # "openai", "gemma", "gemini", "claude"
    rec = _apply_swt(data["record"]) if swt else data["record"]
    try:
        from rl.vision_reward import assess_single_beat
        text, provider = assess_single_beat(
            rec, data["fiducials"], data["features"], beat_idx,
            provider=provider_override,
        )
        return jsonify({"beat": beat_idx, "assessment": text, "provider": provider})
    except Exception as e:
        return jsonify({"beat": beat_idx, "assessment": f"Error: {e}", "provider": "error"})


def _apply_swt(record):
    """Apply SWT denoising to the morphology signal, return a copy."""
    from rl.swt_denoise import denoise_ecg
    import copy
    rec = copy.copy(record)
    rec.morphology_signal = denoise_ecg(record.morphology_signal, record.fs)
    return rec


@app.route("/api/beat_prompt/<int:ecg_id>/<int:beat_idx>")
def api_beat_prompt(ecg_id: int, beat_idx: int):
    """Return the exact prompt + images that would be sent for one beat call."""
    import base64 as b64mod
    data = _process_record(ecg_id)
    from rl.vision_reward import (
        render_territory_beat_strip, TERRITORIES,
        SINGLE_BEAT_PROMPT, FIDUCIAL_PROBLEMS,
        _measurements_context, _beat_measurements_text,
    )

    swt = request.args.get("swt", "1") == "1"
    rec = _apply_swt(data["record"]) if swt else data["record"]

    # Render territory images
    images = []
    all_missing = {}
    for territory, info in TERRITORIES.items():
        result = render_territory_beat_strip(
            rec, data["fiducials"], beat_idx, territory, info["leads"],
            features=data["features"],
        )
        if result:
            img, missing = result
            images.append({
                "territory": territory,
                "leads": info["leads"],
                "artery": info["artery"],
                "image_b64": b64mod.b64encode(img).decode(),
                "missing_fiducials": missing,
            })
            if missing:
                all_missing.update(missing)

    # Build text prompt
    beat_text = _beat_measurements_text(
        data["record"], data["fiducials"], data["features"], beat_idx
    )
    prompt_text = (
        f"Narrate Beat {beat_idx + 1} of this ECG.\n\n"
        f"{beat_text}\n\n"
        f"{_measurements_context(data['features'])}\n\n"
        f"{SINGLE_BEAT_PROMPT}"
    )

    return jsonify({
        "beat": beat_idx,
        "images": images,
        "prompt": prompt_text,
        "missing_fiducials": all_missing,
    })


@app.route("/api/diagnose", methods=["POST"])
def api_diagnose():
    """Run RAG diagnosis using the vision LLM narration (and optionally pipeline narration)."""
    payload = request.get_json()
    ecg_id = payload["ecg_id"]
    vision_narration = payload["vision_narration"]
    include_pipeline = payload.get("include_pipeline_narration", False)

    data = _process_record(ecg_id)

    # Build the narration to send to RAG
    if include_pipeline:
        combined_narration = (
            "=== PIPELINE SIGNAL NARRATION ===\n"
            f"{data['narration']}\n\n"
            "=== VISION LLM NARRATION ===\n"
            f"{vision_narration}"
        )
    else:
        combined_narration = vision_narration

    try:
        import asyncio
        from pipeline.diagnostic_rag import run_two_stage_diagnosis

        loop = asyncio.new_event_loop()
        result = loop.run_until_complete(
            run_two_stage_diagnosis(combined_narration, data["features"])
        )
        loop.close()

        # Format result
        if isinstance(result, dict):
            parts = []
            if result.get("stage1_observations"):
                parts.append(f"## STAGE 1 — OBSERVATIONS\n{json.dumps(result['stage1_observations'], indent=2)}")
            if result.get("stage2_validated"):
                parts.append(f"\n## STAGE 2 — VALIDATED FINDINGS\n{json.dumps(result['stage2_validated'], indent=2)}")
            diagnosis_text = "\n".join(parts) if parts else str(result)
        else:
            diagnosis_text = str(result)

        return jsonify({"diagnosis": diagnosis_text, "provider": "rag"})
    except Exception as e:
        # Fallback: send to DeepSeek as a diagnosis prompt
        try:
            diagnosis = _run_llm_diagnosis(combined_narration, data["features"])
            return jsonify({"diagnosis": diagnosis, "provider": "llm-fallback"})
        except Exception as e2:
            return jsonify({"diagnosis": f"RAG error: {e}\nFallback error: {e2}", "provider": "error"})


def _run_llm_diagnosis(narration: str, features) -> str:
    """Fallback: use DeepSeek/Gemini to diagnose from narration."""
    from rl.vision_reward import _detect_provider, get_openai_client, DEEPSEEK_MODEL

    provider = _detect_provider()
    if provider == "deepseek":
        client = get_openai_client()
        prompt = (
            "You are a senior cardiologist. Based on the following ECG narration, "
            "provide a structured diagnosis.\n\n"
            f"{narration}\n\n"
            "Provide:\n"
            "## FINDINGS\n"
            "List each finding with confidence (HIGH/MEDIUM/LOW)\n\n"
            "## PRIMARY DIAGNOSIS\n\n"
            "## DIFFERENTIAL\n\n"
            "## RECOMMENDED ACTIONS\n"
            "Include STAT actions if any critical findings\n"
        )
        resp = client.chat.completions.create(
            model=DEEPSEEK_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=3000,
        )
        return resp.choices[0].message.content
    raise ValueError(f"No suitable provider for diagnosis (have: {provider})")


@app.route("/api/strips/<int:ecg_id>")
def api_strips(ecg_id: int):
    """Return rendered territory beat strip images as base64 for preview."""
    data = _process_record(ecg_id)
    from rl.vision_reward import render_all_beat_territory_strips, render_ecg_full_image
    import base64 as b64mod

    # Full 12-lead
    full_img = render_ecg_full_image(data["record"])
    full_b64 = b64mod.b64encode(full_img).decode()

    # Territory strips
    strips = render_all_beat_territory_strips(
        data["record"], data["fiducials"], max_beats=3, features=data["features"]
    )
    strip_data = []
    for s in strips:
        strip_data.append({
            "beat": s["beat"],
            "territory": s["territory"],
            "leads": s["leads"],
            "artery": s["artery"],
            "image": b64mod.b64encode(s["image"]).decode(),
        })

    return jsonify({"full_image": full_b64, "strips": strip_data})


# ─── Dashboard HTML ──────────────────────────────────────────────────────

DASHBOARD_HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>YouOwnECG — Narration Dashboard</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
:root {
  --bg: #0f1117;
  --surface: #1a1d27;
  --surface2: #232733;
  --border: #2d3140;
  --text: #e1e4eb;
  --text2: #8b90a0;
  --accent: #4f8ff7;
  --green: #2ecc71;
  --red: #e74c3c;
  --orange: #f39c12;
  --yellow: #f1c40f;
  --pink: #f4c2c2;
  --grid-minor: rgba(244,194,194,0.15);
  --grid-major: rgba(244,194,194,0.35);
}
body { font-family: 'SF Mono', 'Fira Code', 'JetBrains Mono', monospace; background: var(--bg); color: var(--text); font-size: 13px; }
a { color: var(--accent); }
h1, h2, h3 { font-weight: 600; }

/* ── Top bar ── */
.topbar { display: flex; align-items: center; gap: 16px; padding: 10px 20px; background: var(--surface); border-bottom: 1px solid var(--border); position: fixed; top: 0; left: 0; right: 0; z-index: 200; height: 50px; }
.topbar h1 { font-size: 15px; color: var(--accent); white-space: nowrap; }
.topbar select, .topbar button { background: var(--surface2); border: 1px solid var(--border); color: var(--text); padding: 6px 12px; border-radius: 6px; font-family: inherit; font-size: 12px; cursor: pointer; }
.topbar select:hover, .topbar button:hover { border-color: var(--accent); }
.topbar button.primary { background: var(--accent); color: #fff; border-color: var(--accent); }
.topbar .spacer { flex: 1; }
#status-text { color: var(--text2); font-size: 11px; }

/* ── Layout ── */
.dashboard { display: grid; grid-template-columns: 1fr 1fr; grid-template-rows: auto auto auto; gap: 8px; padding: 8px 8px 200px 8px; min-height: calc(100vh - 50px); }
html, body { overflow-y: auto; }

/* ── Panels ── */
.panel { background: var(--surface); border: 1px solid var(--border); border-radius: 8px; overflow: hidden; display: flex; flex-direction: column; }
.panel-header { padding: 8px 12px; background: var(--surface2); border-bottom: 1px solid var(--border); display: flex; align-items: center; justify-content: space-between; flex-shrink: 0; }
.panel-header h2 { font-size: 12px; text-transform: uppercase; letter-spacing: 1px; color: var(--text2); }
.panel-body { padding: 10px; overflow-y: auto; flex: 1; }

/* ── ECG Viewer (spans full width) ── */
.ecg-panel { grid-column: 1 / -1; height: 400px; min-height: 300px; resize: vertical; overflow: auto; }
.ecg-canvas-wrap { position: relative; width: 100%; height: 100%; overflow: hidden; }
canvas#ecg-canvas { width: 100%; height: 100%; cursor: crosshair; }

/* ── Narration panels ── */
.narration-panel { min-height: 300px; max-height: 600px; resize: vertical; overflow: auto; }
.ecg-controls { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; }
.ecg-controls button { padding: 3px 10px; font-size: 11px; background: var(--surface); border: 1px solid var(--border); color: var(--text); border-radius: 4px; cursor: pointer; }
.ecg-controls button:hover { border-color: var(--accent); }
.ecg-controls button.active { background: var(--accent); color: #fff; border-color: var(--accent); }
.ecg-controls .sep { width: 1px; height: 18px; background: var(--border); }
.zoom-label { font-size: 11px; color: var(--text2); }
.lead-toggle { display: inline-flex; gap: 2px; }
.lead-toggle label { font-size: 10px; padding: 2px 6px; background: var(--surface2); border: 1px solid var(--border); border-radius: 3px; cursor: pointer; color: var(--text2); }
.lead-toggle label.active { background: var(--accent); color: #fff; border-color: var(--accent); }

/* ── Measurements bar ── */
.meas-bar { grid-column: 1 / -1; }
.badges { display: flex; gap: 8px; flex-wrap: wrap; }
.badge { padding: 4px 10px; border-radius: 5px; font-size: 12px; background: var(--surface2); border: 1px solid var(--border); }
.badge .label { color: var(--text2); font-size: 10px; }
.badge .value { font-weight: 700; margin-left: 4px; }
.badge.alert { border-color: var(--red); background: rgba(231,76,60,0.1); }
.badge.warn { border-color: var(--orange); background: rgba(243,156,18,0.1); }
.badge.stat { border-color: var(--red); background: var(--red); color: #fff; font-weight: 700; animation: pulse 1.5s infinite; }
@keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.7; } }

/* ── Narration panels ── */
.narration-text { white-space: pre-wrap; font-size: 12px; line-height: 1.6; color: var(--text); }
.narration-text .section-header { color: var(--accent); font-weight: 700; }

/* ── Checklist ── */
.checklist { grid-row: 3; }
.check-item { display: flex; align-items: center; gap: 8px; padding: 5px 8px; border-radius: 4px; margin-bottom: 3px; font-size: 12px; }
.check-item.TP { background: rgba(46,204,113,0.12); }
.check-item.FP { background: rgba(243,156,18,0.12); }
.check-item.FN { background: rgba(231,76,60,0.12); }
.check-item.TN { opacity: 0.4; }
.check-dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }
.check-dot.TP { background: var(--green); }
.check-dot.FP { background: var(--orange); }
.check-dot.FN { background: var(--red); }
.check-dot.TN { background: var(--border); }
.check-label { flex: 1; }
.check-conf { color: var(--text2); font-size: 11px; }
.check-status { font-size: 10px; font-weight: 700; padding: 1px 6px; border-radius: 3px; }
.check-status.TP { background: var(--green); color: #000; }
.check-status.FP { background: var(--orange); color: #000; }
.check-status.FN { background: var(--red); color: #fff; }

/* ── Loading ── */
.rag-opt { color: var(--text2); background: transparent; }
.rag-opt.active { color: #fff; background: var(--accent); }

.loading { display: flex; align-items: center; justify-content: center; height: 100%; color: var(--text2); }
.spinner { width: 20px; height: 20px; border: 2px solid var(--border); border-top-color: var(--accent); border-radius: 50%; animation: spin 0.8s linear infinite; margin-right: 10px; }
@keyframes spin { to { transform: rotate(360deg); } }
</style>
</head>
<body>

<!-- Top Bar -->
<div class="topbar">
  <h1>YouOwnECG Narration Lab</h1>
  <select id="cond-filter"><option value="">All conditions</option></select>
  <select id="record-picker"><option value="">Select record...</option></select>
  <button class="primary" onclick="loadRecord()">Load</button>
  <div class="sep" style="width:1px;height:20px;background:var(--border)"></div>
  <label style="font-size:11px;color:var(--text2);">Beats:</label>
  <select id="n-beats" style="width:50px;">
    <option value="1">1</option>
    <option value="2">2</option>
    <option value="3" selected>3</option>
    <option value="4">4</option>
    <option value="5">5</option>
    <option value="6">6</option>
  </select>
  <label style="font-size:11px;color:var(--text2);margin-left:4px;">
    <input type="checkbox" id="swt-toggle" checked style="margin-right:3px;">SWT Denoise
  </label>
  <button onclick="showStrips()">Show Beat Strips</button>
  <button onclick="runVision()">Run Vision LLM</button>
  <button onclick="runVisualNarration()">Visual Narrate</button>
  <div style="display:flex;gap:2px;align-items:center;border:1px solid var(--border);border-radius:4px;padding:1px 3px;">
    <label style="font-size:9px;color:var(--text2);white-space:nowrap;">Send to RAG:</label>
    <label style="font-size:10px;cursor:pointer;padding:2px 5px;border-radius:3px;" id="rag-opt-meas" class="rag-opt active" onclick="toggleRagOpt('meas')">
      <input type="checkbox" id="rag-chk-meas" checked style="display:none;">📊 Measurements
    </label>
    <label style="font-size:10px;cursor:pointer;padding:2px 5px;border-radius:3px;" id="rag-opt-gemma" class="rag-opt" onclick="toggleRagOpt('gemma')">
      <input type="checkbox" id="rag-chk-gemma" style="display:none;">👁 Visual Gemma
    </label>
    <label style="font-size:10px;cursor:pointer;padding:2px 5px;border-radius:3px;" id="rag-opt-llm" class="rag-opt" onclick="toggleRagOpt('llm')">
      <input type="checkbox" id="rag-chk-llm" style="display:none;">🤖 Visual LLM
    </label>
  </div>
  <button id="btn-diagnose" onclick="runDiagnosis()" class="primary">Diagnose</button>
  <button onclick="showShapeEditor()">Shapes</button>
  <div class="spacer"></div>
  <span id="status-text">Ready</span>
</div>

<!-- Spacer for fixed topbar -->
<div style="height:50px;"></div>

<!-- Dashboard Grid -->
<div class="dashboard">

  <!-- ECG Viewer -->
  <div class="panel ecg-panel">
    <div class="panel-header">
      <h2>12-Lead ECG</h2>
      <div class="ecg-controls">
        <select id="territory-select" onchange="selectTerritory()" style="font-size:11px;">
          <option value="all">All 12 leads</option>
          <option value="septal">Septal (V1, V2)</option>
          <option value="anterior">Anterior (V3, V4)</option>
          <option value="lateral">Lateral (I, aVL, V5, V6)</option>
          <option value="inferior">Inferior (II, III, aVF)</option>
          <option value="precordial">Precordial (V1-V6)</option>
          <option value="limb">Limb (I, II, III, aVR, aVL, aVF)</option>
          <option value="rhythm">Rhythm (II)</option>
        </select>
        <div class="sep"></div>
        <div class="lead-toggle" id="lead-toggles"></div>
        <div class="sep"></div>
        <button onclick="zoomIn()">Zoom +</button>
        <button onclick="zoomOut()">Zoom −</button>
        <button onclick="resetZoom()">Reset</button>
        <button onclick="toggleFiducials()" id="fid-btn">Fiducials: ON</button>
        <span class="zoom-label" id="zoom-label">1.0x</span>
      </div>
    </div>
    <div class="panel-body ecg-canvas-wrap">
      <canvas id="ecg-canvas"></canvas>
    </div>
  </div>

  <!-- Measurement Badges -->
  <div class="panel meas-bar">
    <div class="panel-body">
      <div class="badges" id="meas-badges">
        <span class="badge"><span class="label">Load a record to begin</span></span>
      </div>
    </div>
  </div>

  <!-- Pipeline Narration -->
  <div class="panel narration-panel">
    <div class="panel-header"><h2>Pipeline Narration</h2></div>
    <div class="panel-body">
      <div class="narration-text" id="pipeline-narration">
        <div class="loading">Select a record above</div>
      </div>
    </div>
  </div>

  <!-- Vision Assessment -->
  <div class="panel narration-panel">
    <div class="panel-header"><h2 id="vision-title">Vision LLM Assessment</h2></div>
    <div class="panel-body">
      <div class="narration-text" id="claude-narration">
        <div class="loading">Click "Run Vision LLM" after loading a record</div>
      </div>
    </div>
  </div>

  <!-- Beat Strip Images (spans full width) -->
  <div class="panel" id="strips-panel" style="grid-column:1/-1;display:none;">
    <div class="panel-header">
      <h2>Territory Beat Strips (images sent to LLM)</h2>
      <button onclick="document.getElementById('strips-panel').style.display='none'" style="font-size:10px;background:none;border:1px solid var(--border);color:var(--text2);cursor:pointer;padding:2px 8px;border-radius:4px;">Close</button>
    </div>
    <div class="panel-body" id="strips-container" style="display:flex;flex-wrap:wrap;gap:12px;align-items:flex-start;">
    </div>
  </div>

  <!-- Condition Checklist (spans both columns at bottom would be nice but let's keep it simple) -->
  <!-- Actually put it as a sidebar-style below the Claude panel -->
</div>

<!-- Shape Template Editor Panel -->
<div class="panel" id="shape-panel" style="grid-column:1/-1;display:none;">
  <div class="panel-header">
    <h2>Shape Template Editor</h2>
    <div style="display:flex;gap:8px;align-items:center;">
      <select id="shape-beat" style="font-size:11px;width:80px;" onchange="loadShapes()">
        <option value="0">Beat 1</option><option value="1">Beat 2</option><option value="2">Beat 3</option>
      </select>
      <button onclick="loadShapes()" style="font-size:10px;padding:3px 8px;">Classify</button>
      <button onclick="document.getElementById('shape-panel').style.display='none'" style="font-size:10px;padding:3px 8px;">Close</button>
    </div>
  </div>
  <div class="panel-body" id="shape-body" style="font-size:11px;">
    <div style="color:var(--text2);">Load a record, then click "Classify Shapes" in the top bar.</div>
  </div>
</div>

<!-- Disease Review Tracker Panel -->
<div class="panel" id="tracker-panel" style="grid-column:1/-1;">
  <div class="panel-header">
    <h2>Disease Review Tracker (2 patients per disease)</h2>
    <button onclick="loadTracker()" style="font-size:10px;background:var(--accent);color:#fff;border:none;padding:3px 10px;border-radius:4px;cursor:pointer;">Refresh</button>
  </div>
  <div class="panel-body" id="tracker-body" style="display:flex;flex-wrap:wrap;gap:6px;"></div>
</div>

<!-- Review Notes Modal -->
<div id="review-modal" style="display:none;position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.7);z-index:300;padding:60px 20px 20px;">
  <div style="max-width:700px;margin:0 auto;background:var(--surface);border:1px solid var(--border);border-radius:8px;max-height:calc(100vh - 80px);overflow:auto;">
    <div style="padding:12px 16px;background:var(--surface2);border-bottom:1px solid var(--border);display:flex;justify-content:space-between;align-items:center;">
      <h3 id="review-title" style="font-size:13px;color:var(--accent);"></h3>
      <button onclick="closeReviewModal()" style="background:none;border:1px solid var(--border);color:var(--text2);padding:3px 10px;border-radius:4px;cursor:pointer;">Close</button>
    </div>
    <div style="padding:16px;">
      <textarea id="review-content" style="width:100%;height:400px;background:var(--bg);border:1px solid var(--border);color:var(--text);font-family:inherit;font-size:12px;padding:10px;border-radius:4px;resize:vertical;" placeholder="Write your review notes here...&#10;&#10;## Findings&#10;- ...&#10;&#10;## Issues Found&#10;- ...&#10;&#10;## Changes Made&#10;- ..."></textarea>
      <div style="margin-top:10px;display:flex;gap:8px;">
        <button onclick="saveReview()" class="primary" style="padding:6px 16px;border-radius:4px;cursor:pointer;background:var(--accent);color:#fff;border:none;">Save Review</button>
        <span id="review-save-status" style="font-size:11px;color:var(--text2);line-height:30px;"></span>
      </div>
    </div>
  </div>
</div>

<!-- Condition checklist overlay panel (bottom strip) -->
<div style="position:fixed;bottom:0;left:0;right:0;background:var(--surface);border-top:1px solid var(--border);max-height:180px;overflow-y:auto;z-index:100;" id="checklist-panel">
  <div style="padding:6px 12px;display:flex;align-items:center;justify-content:space-between;background:var(--surface2);border-bottom:1px solid var(--border);">
    <h2 style="font-size:12px;text-transform:uppercase;letter-spacing:1px;color:var(--text2);">Condition Checklist</h2>
    <button onclick="document.getElementById('checklist-panel').style.display=document.getElementById('checklist-panel').style.display==='none'?'block':'none'" style="font-size:10px;background:none;border:none;color:var(--text2);cursor:pointer;">Toggle ▲</button>
  </div>
  <div style="padding:8px 12px;display:flex;flex-wrap:wrap;gap:4px;" id="checklist-items">
  </div>
</div>

<script>
// ─── State ───
let DATA = null;
let SIGNALS = {};
let FIDUCIALS = {};
let zoomLevel = 1.0;
let panOffset = 0;
let activeLeads = ['II','V1','V5'];
let showFiducials = true;
let isDragging = false;
let dragStartX = 0;

// ─── Init ───
async function init() {
  const resp = await fetch('/api/samples');
  const {samples, conditions} = await resp.json();

  const condSel = document.getElementById('cond-filter');
  conditions.forEach(c => {
    const o = document.createElement('option');
    o.value = c; o.textContent = c;
    condSel.appendChild(o);
  });
  condSel.onchange = () => filterRecords(samples);

  window._samples = samples;
  filterRecords(samples);
}

function filterRecords(samples) {
  const cond = document.getElementById('cond-filter').value;
  const picker = document.getElementById('record-picker');
  picker.innerHTML = '<option value="">Select record...</option>';
  const filtered = cond ? samples.filter(s => s.condition === cond) : samples;
  filtered.forEach(s => {
    const o = document.createElement('option');
    o.value = s.ecg_id;
    o.textContent = `ECG ${s.ecg_id} — ${s.condition}`;
    picker.appendChild(o);
  });
}

// ─── Load Record ───
async function loadRecord() {
  const ecgId = document.getElementById('record-picker').value;
  if (!ecgId) return;

  setStatus('Loading...');
  document.getElementById('pipeline-narration').innerHTML = '<div class="loading"><div class="spinner"></div>Processing pipeline...</div>';

  try {
    const resp = await fetch(`/api/record/${ecgId}`);
    DATA = await resp.json();
    SIGNALS = DATA.signals;
    FIDUCIALS = DATA.fiducials;

    renderMeasurements();
    renderNarration();
    renderChecklist();
    setupLeadToggles();
    resetZoom();
    drawECG();
    setStatus(`ECG ${ecgId} loaded — ${DATA.condition}`);
  } catch (e) {
    setStatus(`Error: ${e.message}`);
  }
}

// ─── Show Beat Strips + Prompt ───
async function showStrips() {
  if (!DATA) { alert('Load a record first'); return; }
  setStatus('Rendering beat strips + prompts...');
  const panel = document.getElementById('strips-panel');
  const container = document.getElementById('strips-container');
  container.innerHTML = '<div class="loading"><div class="spinner"></div>Rendering...</div>';
  panel.style.display = '';

  const nBeatsMax = DATA.measurements.n_beats || 1;
  const nBeats = Math.min(parseInt(document.getElementById('n-beats').value) || 3, nBeatsMax);
  container.innerHTML = '';

  for (let b = 0; b < nBeats; b++) {
    setStatus(`Rendering beat ${b+1}/${nBeats}...`);
    try {
      const swt = document.getElementById('swt-toggle').checked ? '1' : '0';
      const resp = await fetch(`/api/beat_prompt/${DATA.ecg_id}/${b}?swt=${swt}`);
      const {beat, images, prompt, missing_fiducials} = await resp.json();

      // Beat header
      const header = document.createElement('div');
      header.style.cssText = 'width:100%;border-top:2px solid var(--accent);margin-top:16px;padding-top:8px;';
      header.innerHTML = `<h3 style="color:var(--accent);font-size:14px;margin-bottom:8px;">
        BEAT ${beat+1} — LLM CALL PREVIEW</h3>`;
      container.appendChild(header);

      // Images (what gets uploaded)
      const imgRow = document.createElement('div');
      imgRow.style.cssText = 'display:grid;grid-template-columns:1fr 1fr;gap:8px;width:100%;';
      images.forEach(img => {
        const card = document.createElement('div');
        let missHtml = '';
        if (img.missing_fiducials && Object.keys(img.missing_fiducials).length > 0) {
          const items = Object.entries(img.missing_fiducials).map(
            ([lead, pts]) => `${lead}: ${pts.join(', ')}`
          ).join(' | ');
          missHtml = `<div style="font-size:9px;color:#E74C3C;background:#FDEDEC;padding:2px 6px;border-radius:3px;margin-top:2px;">
            ⚠ Not detected: ${items}</div>`;
        }
        card.innerHTML = `
          <div style="font-size:10px;font-weight:bold;color:var(--orange);margin-bottom:2px;text-transform:uppercase;">
            IMAGE → ${img.territory} (${img.leads.join(', ')}) — ${img.artery}
          </div>
          ${missHtml}
          <img src="data:image/png;base64,${img.image_b64}"
               style="width:100%;border:1px solid var(--border);border-radius:4px;background:white;">
        `;
        imgRow.appendChild(card);
      });
      container.appendChild(imgRow);

      // Prompt text (collapsible)
      const promptDiv = document.createElement('div');
      promptDiv.style.cssText = 'width:100%;margin-top:8px;';
      promptDiv.innerHTML = `
        <details>
          <summary style="cursor:pointer;font-size:11px;color:var(--accent);font-weight:bold;margin-bottom:4px;">
            PROMPT TEXT (click to expand)
          </summary>
          <pre style="white-space:pre-wrap;font-size:10px;line-height:1.4;color:var(--text2);
                      background:var(--surface2);padding:8px;border-radius:4px;border:1px solid var(--border);
                      max-height:400px;overflow-y:auto;">${prompt.replace(/</g,'&lt;')}</pre>
        </details>
      `;
      container.appendChild(promptDiv);

    } catch (e) {
      container.innerHTML += `<div style="color:var(--red)">Beat ${b+1} error: ${e.message}</div>`;
    }
  }
  setStatus(`${nBeats} beat previews rendered — verify images before running LLM`);
}

// ─── RAG source toggles ───
function toggleRagOpt(key) {
  const chk = document.getElementById('rag-chk-' + key);
  const lbl = document.getElementById('rag-opt-' + key);
  chk.checked = !chk.checked;
  lbl.className = 'rag-opt' + (chk.checked ? ' active' : '');
}

// ─── Visual Narration (image → description per beat) ───
async function runVisualNarration() {
  if (!DATA) { alert('Load a record first'); return; }
  const el = document.getElementById('claude-narration');
  const nBeatsMax = DATA.measurements.n_beats || 1;
  const nBeats = Math.min(parseInt(document.getElementById('n-beats').value) || 3, nBeatsMax);

  el.innerHTML = `<div class="loading"><div class="spinner"></div>Visual narration: beat 1/${nBeats}...</div>`;
  setStatus('Running visual narration (image → Gemma)...');

  let allResults = [];
  for (let i = 0; i < nBeats; i++) {
    setStatus(`Visual narration: beat ${i+1}/${nBeats}...`);
    el.innerHTML = `<div class="loading"><div class="spinner"></div>Beat ${i+1}/${nBeats} — sending images to vision LLM...</div>`
      + allResults.map(r => `<div style="border-bottom:2px solid var(--border);margin-bottom:12px;padding-bottom:12px;">
          <div style="color:var(--accent);font-weight:bold;font-size:13px;margin-bottom:6px;">BEAT ${r.beat+1} — Visual Description</div>
          ${Object.entries(r.descriptions).map(([t,d]) =>
            `<div style="margin-bottom:8px;"><span style="color:var(--orange);font-weight:bold;text-transform:uppercase;">${t}:</span>
            <pre style="white-space:pre-wrap;font-size:11px;margin-top:2px;color:var(--text);">${d}</pre></div>`
          ).join('')}
        </div>`).join('');

    try {
      const swt = document.getElementById('swt-toggle').checked ? '1' : '0';
      const resp = await fetch(`/api/visual_narrate/${DATA.ecg_id}/${i}?swt=${swt}`);
      const data = await resp.json();
      if (data.status === 'ok') {
        allResults.push({beat: i, descriptions: data.descriptions, images: data.images || {}});
      } else {
        allResults.push({beat: i, descriptions: {error: data.status}, images: {}});
      }
    } catch (e) {
      allResults.push({beat: i, descriptions: {error: e.message}, images: {}});
    }
  }

  // Save Gemma results separately
  GEMMA_RESULTS = allResults.map(r => ({
    beat: r.beat,
    text: Object.entries(r.descriptions).map(([t,d]) => `${t.toUpperCase()}:\n${d}`).join('\n\n'),
    provider: 'gemma-visual'
  }));
  // Combined for backward-compat
  VISION_RESULTS = [...GEMMA_RESULTS, ...LLM_RESULTS];

  el.innerHTML = allResults.map(r => `<div style="border-bottom:2px solid var(--border);margin-bottom:16px;padding-bottom:12px;">
    <div style="color:var(--accent);font-weight:bold;font-size:13px;margin-bottom:8px;">BEAT ${r.beat+1} — Visual Morphology (image → Gemma)</div>
    ${Object.entries(r.descriptions).map(([t,d]) => {
      const imgB64 = r.images?.[t] || '';
      const imgHtml = imgB64
        ? `<img src="data:image/png;base64,${imgB64}" style="width:100%;border:1px solid var(--border);border-radius:4px;background:white;margin-bottom:4px;">`
        : '';
      return `<div style="margin-bottom:12px;border:1px solid var(--border);border-radius:6px;overflow:hidden;">
        <div style="padding:4px 8px;background:var(--surface2);font-size:11px;font-weight:bold;color:var(--orange);text-transform:uppercase;">
          ${t} — Image sent to Gemma ↓
        </div>
        <div style="padding:8px;">
          ${imgHtml}
          <pre style="white-space:pre-wrap;font-size:11px;margin-top:6px;color:var(--text);line-height:1.5;">${d}</pre>
        </div>
      </div>`;
    }).join('')}
  </div>`).join('');

  document.getElementById('vision-title').textContent = 'Visual Narration (image → Gemma)';
  // RAG button always visible
  setStatus(`Visual narration complete — ${nBeats} beats described`);
  saveCurrentRun();
}

// ─── Vision LLM (per-beat) ───
let VISION_RESULTS = [];     // combined for backward-compat
let GEMMA_RESULTS = [];      // visual narrate (Gemma local)
let LLM_RESULTS = [];        // openai/cloud llm
let RAG_RESULT = null;       // last RAG diagnosis

async function runVision() {
  if (!DATA) { alert('Load a record first'); return; }
  const el = document.getElementById('claude-narration');
  // Don't wipe Gemma results
  LLM_RESULTS = [];
  // RAG button always visible
  const nBeatsMax = DATA.measurements.n_beats || 1;
  const nBeats = Math.min(parseInt(document.getElementById('n-beats').value) || 3, nBeatsMax);
  el.innerHTML = `<div class="loading"><div class="spinner"></div>Running LLM for ${nBeats} beats (one call per beat)...</div>`;
  setStatus(`Calling LLM for beat 1/${nBeats}...`);

  let results = [];
  let provider = '';
  for (let i = 0; i < nBeats; i++) {
    setStatus(`Calling LLM for beat ${i+1}/${nBeats}...`);
    el.innerHTML = `<div class="loading"><div class="spinner"></div>Beat ${i+1}/${nBeats}...</div>`
      + results.map(r => `<div style="border-top:1px solid var(--border);margin-top:8px;padding-top:8px;">
          <div style="color:var(--accent);font-weight:bold;font-size:12px;">BEAT ${r.beat+1} (${r.provider})</div>
          <pre style="white-space:pre-wrap;font-size:11px;margin-top:4px;">${r.text}</pre></div>`).join('');

    try {
      const swt = document.getElementById('swt-toggle').checked ? '1' : '0';
      const resp = await fetch(`/api/vision/${DATA.ecg_id}/beat/${i}?swt=${swt}&provider=openai`);
      const data = await resp.json();
      provider = data.provider;
      results.push({beat: i, text: data.assessment, provider: data.provider});
    } catch (e) {
      results.push({beat: i, text: `Error: ${e.message}`, provider: 'error'});
    }
  }

  // Final render — all beats
  el.innerHTML = results.map(r =>
    `<div style="border-bottom:2px solid var(--border);margin-bottom:12px;padding-bottom:12px;">
      <div style="color:var(--accent);font-weight:bold;font-size:13px;margin-bottom:6px;">
        BEAT ${r.beat+1} narration (${r.provider})
      </div>
      <pre style="white-space:pre-wrap;font-size:12px;line-height:1.5;">${r.text}</pre>
    </div>`
  ).join('');

  LLM_RESULTS = results;
  VISION_RESULTS = [...GEMMA_RESULTS, ...LLM_RESULTS];

  // Re-render BOTH Gemma and LLM results so we don't lose Gemma display
  if (GEMMA_RESULTS.length > 0) {
    el.innerHTML = ''
      + '<div style="border-bottom:3px solid var(--orange);margin-bottom:12px;padding-bottom:6px;color:var(--orange);font-weight:bold;font-size:13px;">VISUAL NARRATION (Gemma local) — preserved</div>'
      + GEMMA_RESULTS.map(r => `<div style="border-bottom:1px solid var(--border);margin-bottom:8px;padding-bottom:8px;">
          <div style="color:var(--accent);font-weight:bold;font-size:12px;">Gemma Beat ${r.beat+1}</div>
          <pre style="white-space:pre-wrap;font-size:10px;line-height:1.4;color:var(--text2);">${r.text.replace(/</g,'&lt;')}</pre>
        </div>`).join('')
      + '<div style="border-bottom:3px solid var(--accent);margin:12px 0 6px;padding-bottom:6px;color:var(--accent);font-weight:bold;font-size:13px;">VISION LLM (cloud)</div>'
      + LLM_RESULTS.map(r =>
          `<div style="border-bottom:2px solid var(--border);margin-bottom:12px;padding-bottom:12px;">
            <div style="color:var(--accent);font-weight:bold;font-size:13px;margin-bottom:6px;">
              BEAT ${r.beat+1} narration (${r.provider})
            </div>
            <pre style="white-space:pre-wrap;font-size:12px;line-height:1.5;">${r.text}</pre>
          </div>`
        ).join('');
    if (RAG_RESULT) appendRagResult(el);
  }
  document.getElementById('vision-title').textContent = `Vision Assessment — per-beat (${provider})`;
  // RAG button always visible
  setStatus(`${nBeats} beat narrations loaded via ${provider} — click "Run RAG Diagnosis" to diagnose`);
  saveCurrentRun();
}

// ─── RAG Diagnosis ───
async function saveCurrentRun() {
  if (!DATA) return;
  // Determine patient number (from disease tracker if available)
  let patientNum = null;
  try {
    const resp = await fetch('/api/disease_tracker');
    const {tracker} = await resp.json();
    for (const d of tracker) {
      if (d.condition === DATA.condition) {
        for (const p of d.patients) {
          if (p.ecg_id === DATA.ecg_id) {
            patientNum = p.patient_num;
            break;
          }
        }
      }
      if (patientNum) break;
    }
  } catch (e) { /* ignore */ }

  const payload = {
    ecg_id: DATA.ecg_id,
    condition: DATA.condition,
    patient_num: patientNum,
    ground_truth: DATA.ground_truth,
    measurements: DATA.measurements,
    gemma_results: GEMMA_RESULTS,
    llm_results: LLM_RESULTS,
    rag_result: RAG_RESULT,
    pipeline_findings: DATA.findings,
  };

  try {
    const resp = await fetch('/api/save_run', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(payload),
    });
    const {filename} = await resp.json();
    setStatus(`Run saved: ${filename}`);
  } catch (e) {
    console.error('Save failed:', e);
  }
}

function appendRagResult(el) {
  if (!RAG_RESULT) return;
  // Remove existing RAG result if any
  const existing = el.querySelector('.rag-result-block');
  if (existing) existing.remove();

  const diagDiv = document.createElement('div');
  diagDiv.className = 'rag-result-block';
  diagDiv.style.cssText = 'border-top:3px solid var(--green);margin-top:16px;padding-top:12px;';
  diagDiv.innerHTML = `
    <div style="color:var(--green);font-weight:bold;font-size:14px;margin-bottom:8px;">
      RAG DIAGNOSIS (${RAG_RESULT.provider}) — ${RAG_RESULT.sources}
      <span style="font-size:10px;color:var(--text2);font-weight:normal;margin-left:8px;">${RAG_RESULT.timestamp}</span>
    </div>
    <pre style="white-space:pre-wrap;font-size:12px;line-height:1.5;">${RAG_RESULT.diagnosis}</pre>
  `;
  el.appendChild(diagDiv);
}

async function runDiagnosis() {
  if (!DATA) { alert('Load a record first'); return; }

  const useMeas = document.getElementById('rag-chk-meas').checked;
  const useGemma = document.getElementById('rag-chk-gemma').checked;
  const useLLM = document.getElementById('rag-chk-llm').checked;

  if (!useMeas && !useGemma && !useLLM) { alert('Select at least one source'); return; }

  const selected = [];
  if (useMeas) selected.push('Measurements');
  if (useGemma) selected.push('Visual Gemma');
  if (useLLM) selected.push('Visual LLM');
  setStatus(`Running RAG diagnosis (${selected.join(' + ')})...`);

  // Build measurement block
  const m = DATA.measurements;
  const measText = [
    'ECG MEASUREMENTS (signal processing):',
    `HR: ${m.hr_bpm||'?'} bpm | Rhythm: ${m.rhythm} (${m.regular?'regular':'irregular'})`,
    `PR: ${m.pr_ms||'?'} ms | QRS: ${m.qrs_ms||'?'} ms | QTc: ${m.qtc_ms||'?'} ms`,
    `Axis: ${m.axis_deg||'?'}° | LBBB: ${m.lbbb} | RBBB: ${m.rbbb} | WPW: ${m.wpw}`,
    `Quality: ${m.quality} | Beats: ${m.n_beats}`,
  ].join('\n');

  // Separate visual gemma results from LLM results
  const gemmaResults = VISION_RESULTS.filter(r => r.provider === 'gemma-visual' || r.provider === 'gemma');
  const llmResults = VISION_RESULTS.filter(r => r.provider !== 'gemma-visual' && r.provider !== 'gemma');

  let parts = [];
  if (useMeas) parts.push(measText);
  if (useGemma && gemmaResults.length > 0) {
    parts.push('=== VISUAL NARRATION (Gemma local) ===\n' +
      gemmaResults.map(r => `Beat ${r.beat+1}:\n${r.text}`).join('\n\n'));
  }
  if (useLLM && llmResults.length > 0) {
    parts.push('=== VISUAL NARRATION (Cloud LLM) ===\n' +
      llmResults.map(r => `Beat ${r.beat+1}:\n${r.text}`).join('\n\n'));
  }
  // If user selected gemma/llm but none available, include whatever VISION_RESULTS we have
  if ((useGemma || useLLM) && VISION_RESULTS.length > 0 && gemmaResults.length === 0 && llmResults.length === 0) {
    parts.push('=== VISUAL NARRATION ===\n' +
      VISION_RESULTS.map(r => `Beat ${r.beat+1}:\n${r.text}`).join('\n\n'));
  }

  const narrationToSend = parts.join('\n\n');
  const includePipeline = useMeas;  // include full pipeline narration if measurements selected

  const payload = {
    ecg_id: DATA.ecg_id,
    vision_narration: narrationToSend,
    include_pipeline_narration: includePipeline,
  };

  // Show loading in a new panel or reuse
  const el = document.getElementById('claude-narration');
  el.innerHTML = VISION_RESULTS.map(r =>
    `<div style="border-bottom:2px solid var(--border);margin-bottom:12px;padding-bottom:12px;">
      <div style="color:var(--accent);font-weight:bold;font-size:13px;margin-bottom:6px;">
        BEAT ${r.beat+1} narration (${r.provider})
      </div>
      <pre style="white-space:pre-wrap;font-size:12px;line-height:1.5;">${r.text}</pre>
    </div>`
  ).join('') + '<div class="loading" id="diag-loading"><div class="spinner"></div>Running RAG diagnosis...</div>';

  try {
    const resp = await fetch('/api/diagnose', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(payload),
    });
    const result = await resp.json();

    // Remove loading, append diagnosis
    const loadEl = document.getElementById('diag-loading');
    if (loadEl) loadEl.remove();

    // Persist RAG result
    RAG_RESULT = {
      provider: result.provider || 'deepseek',
      sources: selected.join(' + '),
      diagnosis: result.diagnosis,
      timestamp: new Date().toLocaleTimeString(),
    };

    appendRagResult(el);
    setStatus('RAG diagnosis complete');
    saveCurrentRun();
  } catch (e) {
    const loadEl = document.getElementById('diag-loading');
    if (loadEl) loadEl.innerHTML = `<div style="color:var(--red)">Diagnosis error: ${e.message}</div>`;
    setStatus(`Diagnosis error: ${e.message}`);
  }
}

// ─── Render Measurements ───
function renderMeasurements() {
  const m = DATA.measurements;
  const hp = DATA.heart_position || {};
  const badges = document.getElementById('meas-badges');
  badges.innerHTML = '';

  const items = [
    {label:'HR', value:`${m.hr_bpm || '?'} bpm`, cls: m.hr_bpm && (m.hr_bpm>100||m.hr_bpm<60)?'warn':''},
    {label:'PR', value:`${m.pr_ms || '?'} ms`, cls: m.pr_ms && m.pr_ms>200?'alert':''},
    {label:'QRS', value:`${m.qrs_ms || '?'} ms`, cls: m.qrs_ms && m.qrs_ms>=120?'alert':''},
    {label:'QTc', value:`${m.qtc_ms || '?'} ms`, cls: m.qtc_ms && m.qtc_ms>470?'alert':''},
    {label:'Axis', value:`${m.axis_deg || '?'}°`, cls:''},
    {label:'Rhythm', value:m.rhythm+(m.regular?' (reg)':' (irreg)'), cls: m.rhythm==='afib'?'alert':''},
    {label:'LBBB', value:m.lbbb?'YES':'no', cls: m.lbbb?'warn':''},
    {label:'RBBB', value:m.rbbb?'YES':'no', cls: m.rbbb?'warn':''},
    {label:'WPW', value:m.wpw?'YES':'no', cls: m.wpw?'alert':''},
    {label:'Quality', value:m.quality, cls: m.quality==='POOR'?'alert':''},
    {label:'Beats', value:m.n_beats, cls:''},
  ];

  if (DATA.stat_alerts.length > 0) {
    items.unshift({label:'STAT', value:DATA.stat_alerts.join(', '), cls:'stat'});
  }

  // Heart position badges
  if (hp.axis_category && hp.axis_category !== 'normal') {
    items.push({label:'Axis', value:hp.axis_category.toUpperCase(), cls:'warn'});
  }
  if (hp.rotation && hp.rotation !== 'normal') {
    items.push({label:'Rotation', value:hp.rotation, cls:'warn'});
  }
  if (hp.transition_zone) {
    const tz = hp.transition_zone.toFixed(1);
    const tzCls = hp.transition_zone < 2.5 || hp.transition_zone > 4.5 ? 'warn' : '';
    items.push({label:'Transition', value:`V${tz}`, cls:tzCls});
  }
  if (hp.dextrocardia) {
    items.push({label:'DEXTRO', value:'possible', cls:'alert'});
  }
  if (hp.low_voltage) {
    items.push({label:'Low V', value:'yes', cls:'warn'});
  }

  items.forEach(({label, value, cls}) => {
    const b = document.createElement('span');
    b.className = 'badge ' + cls;
    b.innerHTML = `<span class="label">${label}</span><span class="value">${value}</span>`;
    badges.appendChild(b);
  });

  // Ground truth badge
  if (DATA.ground_truth.length > 0) {
    const gt = document.createElement('span');
    gt.className = 'badge';
    gt.style.borderColor = '#2ecc71';
    gt.innerHTML = `<span class="label">GT</span><span class="value">${DATA.ground_truth.join(', ')}</span>`;
    badges.appendChild(gt);
  }
}

// ─── Render Narration ───
function renderNarration() {
  const el = document.getElementById('pipeline-narration');
  // Highlight section headers
  let html = DATA.narration
    .replace(/^(ECG OVERVIEW:.*)/m, '<span class="section-header">$1</span>')
    .replace(/^(--- Beat.*---)/gm, '<span class="section-header">$1</span>')
    .replace(/^(--- Rhythm.*---)/gm, '<span class="section-header">$1</span>')
    .replace(/^(--- Cross-Lead.*---)/gm, '<span class="section-header">$1</span>')
    .replace(/(ELEVATED|STEMI|PROLONGED|WIDE|HYPERACUTE|DELTA WAVE|WPW)/g, '<span style="color:var(--red);font-weight:700">$1</span>')
    .replace(/(DEPRESSED|SHORT|LOW)/g, '<span style="color:var(--orange);font-weight:700">$1</span>')
    .replace(/(normal|isoelectric|narrow)/gi, '<span style="color:var(--green)">$1</span>');
  el.innerHTML = html;
}

// ─── Render Checklist ───
function renderChecklist() {
  const el = document.getElementById('checklist-items');
  el.innerHTML = '';
  // Sort: FN first, then FP, then TP, then TN
  const order = {FN:0, FP:1, TP:2, TN:3};
  const sorted = [...DATA.checklist].sort((a,b) => (order[a.status]||9) - (order[b.status]||9));

  sorted.forEach(item => {
    if (item.status === 'TN') return; // hide true negatives
    const div = document.createElement('div');
    div.className = `check-item ${item.status}`;
    div.innerHTML = `
      <span class="check-dot ${item.status}"></span>
      <span class="check-label">${item.condition}</span>
      ${item.confidence ? `<span class="check-conf">${item.confidence}</span>` : ''}
      <span class="check-status ${item.status}">${item.status}</span>
    `;
    el.appendChild(div);
  });
}

// ─── Territory presets ───
const TERRITORY_LEADS = {
  all:        ['I','II','III','aVR','aVL','aVF','V1','V2','V3','V4','V5','V6'],
  septal:     ['V1','V2'],
  anterior:   ['V3','V4'],
  lateral:    ['I','aVL','V5','V6'],
  inferior:   ['II','III','aVF'],
  precordial: ['V1','V2','V3','V4','V5','V6'],
  limb:       ['I','II','III','aVR','aVL','aVF'],
  rhythm:     ['II'],
};

function selectTerritory() {
  const val = document.getElementById('territory-select').value;
  const preset = TERRITORY_LEADS[val] || TERRITORY_LEADS.all;
  activeLeads = preset.filter(l => SIGNALS[l]);
  setupLeadToggles();
  drawECG();
}

// ─── Lead Toggles ───
function setupLeadToggles() {
  const container = document.getElementById('lead-toggles');
  container.innerHTML = '';
  const allLeads = Object.keys(SIGNALS);
  allLeads.forEach(lead => {
    const label = document.createElement('label');
    label.textContent = lead;
    label.className = activeLeads.includes(lead) ? 'active' : '';
    label.onclick = () => {
      if (activeLeads.includes(lead)) {
        if (activeLeads.length > 1) activeLeads = activeLeads.filter(l => l !== lead);
      } else {
        activeLeads.push(lead);
      }
      label.className = activeLeads.includes(lead) ? 'active' : '';
      drawECG();
    };
    container.appendChild(label);
  });
}

// ─── ECG Drawing ───
function drawECG() {
  const canvas = document.getElementById('ecg-canvas');
  const wrap = canvas.parentElement;
  canvas.width = wrap.clientWidth * 2;
  canvas.height = wrap.clientHeight * 2;
  canvas.style.width = wrap.clientWidth + 'px';
  canvas.style.height = wrap.clientHeight + 'px';
  const ctx = canvas.getContext('2d');
  ctx.scale(2, 2);

  const W = wrap.clientWidth;
  const H = wrap.clientHeight;
  const nLeads = activeLeads.length;
  const stripH = H / nLeads;
  const margin = {left: 42, right: 10, top: 4, bottom: 4};

  ctx.fillStyle = '#1a1d27';
  ctx.fillRect(0, 0, W, H);

  activeLeads.forEach((lead, li) => {
    const y0 = li * stripH;
    const plotW = W - margin.left - margin.right;
    const plotH = stripH - margin.top - margin.bottom;
    const plotY = y0 + margin.top;

    if (!SIGNALS[lead]) return;
    const {time, amplitude} = SIGNALS[lead];
    const tMax = time[time.length-1];
    const visibleDuration = tMax / zoomLevel;
    const tStart = panOffset;
    const tEnd = tStart + visibleDuration;

    // Grid
    const pxPerSec = plotW / visibleDuration;
    const mvRange = 4; // ±2 mV
    const pxPerMv = plotH / mvRange;

    // Minor grid (1mm = 0.04s, 0.1mV)
    ctx.strokeStyle = 'rgba(244,194,194,0.08)';
    ctx.lineWidth = 0.5;
    for (let t = Math.floor(tStart/0.04)*0.04; t <= tEnd; t += 0.04) {
      const x = margin.left + (t - tStart) * pxPerSec;
      ctx.beginPath(); ctx.moveTo(x, plotY); ctx.lineTo(x, plotY+plotH); ctx.stroke();
    }
    for (let mv = -2; mv <= 2; mv += 0.1) {
      const y = plotY + plotH/2 - mv * pxPerMv;
      ctx.beginPath(); ctx.moveTo(margin.left, y); ctx.lineTo(margin.left+plotW, y); ctx.stroke();
    }
    // Major grid (5mm = 0.2s, 0.5mV)
    ctx.strokeStyle = 'rgba(244,194,194,0.2)';
    ctx.lineWidth = 0.5;
    for (let t = Math.floor(tStart/0.2)*0.2; t <= tEnd; t += 0.2) {
      const x = margin.left + (t - tStart) * pxPerSec;
      ctx.beginPath(); ctx.moveTo(x, plotY); ctx.lineTo(x, plotY+plotH); ctx.stroke();
    }
    for (let mv = -2; mv <= 2; mv += 0.5) {
      const y = plotY + plotH/2 - mv * pxPerMv;
      ctx.beginPath(); ctx.moveTo(margin.left, y); ctx.lineTo(margin.left+plotW, y); ctx.stroke();
    }

    // Baseline
    ctx.strokeStyle = 'rgba(255,255,255,0.1)';
    ctx.lineWidth = 0.5;
    const baseY = plotY + plotH/2;
    ctx.beginPath(); ctx.moveTo(margin.left, baseY); ctx.lineTo(margin.left+plotW, baseY); ctx.stroke();

    // Signal
    ctx.strokeStyle = '#4f8ff7';
    ctx.lineWidth = 1.2;
    ctx.beginPath();
    let started = false;
    for (let i = 0; i < time.length; i++) {
      if (time[i] < tStart || time[i] > tEnd) continue;
      const x = margin.left + (time[i] - tStart) * pxPerSec;
      const y = baseY - amplitude[i] * pxPerMv;
      if (!started) { ctx.moveTo(x, y); started = true; }
      else ctx.lineTo(x, y);
    }
    ctx.stroke();

    // Fiducial markers
    if (showFiducials && FIDUCIALS[lead]) {
      FIDUCIALS[lead].forEach(beat => {
        const points = [
          {key:'r', color:'#e74c3c', label:'R'},
          {key:'qrson', color:'#2ecc71', label:''},
          {key:'qrsoff', color:'#2ecc71', label:''},
          {key:'ppeak', color:'#3498db', label:'P'},
          {key:'tpeak', color:'#f39c12', label:'T'},
        ];
        points.forEach(({key, color, label}) => {
          if (beat[key] === undefined) return;
          const t = beat[key];
          if (t < tStart || t > tEnd) return;
          const x = margin.left + (t - tStart) * pxPerSec;
          ctx.strokeStyle = color;
          ctx.lineWidth = 1;
          ctx.beginPath(); ctx.moveTo(x, plotY); ctx.lineTo(x, plotY+plotH); ctx.stroke();
          if (label) {
            ctx.fillStyle = color;
            ctx.font = '9px monospace';
            ctx.fillText(label, x+2, plotY+10);
          }
        });
      });
    }

    // Lead label
    ctx.fillStyle = '#e1e4eb';
    ctx.font = 'bold 11px monospace';
    ctx.fillText(lead, 4, y0 + stripH/2 + 4);

    // Separator
    if (li < nLeads - 1) {
      ctx.strokeStyle = 'rgba(45,49,64,0.8)';
      ctx.lineWidth = 1;
      ctx.beginPath(); ctx.moveTo(0, y0+stripH); ctx.lineTo(W, y0+stripH); ctx.stroke();
    }
  });
}

// ─── Zoom/Pan ───
function zoomIn() { zoomLevel = Math.min(zoomLevel * 1.5, 20); updateZoom(); }
function zoomOut() { zoomLevel = Math.max(zoomLevel / 1.5, 0.5); updateZoom(); }
function resetZoom() { zoomLevel = 1; panOffset = 0; updateZoom(); }
function updateZoom() {
  document.getElementById('zoom-label').textContent = zoomLevel.toFixed(1) + 'x';
  drawECG();
}
function toggleFiducials() {
  showFiducials = !showFiducials;
  document.getElementById('fid-btn').textContent = 'Fiducials: ' + (showFiducials ? 'ON' : 'OFF');
  drawECG();
}

// Mouse pan
const cvs = document.getElementById('ecg-canvas');
cvs.addEventListener('mousedown', e => { isDragging = true; dragStartX = e.clientX; });
cvs.addEventListener('mousemove', e => {
  if (!isDragging || !DATA) return;
  const dx = e.clientX - dragStartX;
  dragStartX = e.clientX;
  const firstLead = activeLeads[0];
  if (!SIGNALS[firstLead]) return;
  const tMax = SIGNALS[firstLead].time[SIGNALS[firstLead].time.length-1];
  const visDur = tMax / zoomLevel;
  const pxPerSec = (cvs.clientWidth - 52) / visDur;
  panOffset = Math.max(0, Math.min(panOffset - dx/pxPerSec, tMax - visDur));
  drawECG();
});
cvs.addEventListener('mouseup', () => { isDragging = false; });
cvs.addEventListener('mouseleave', () => { isDragging = false; });
cvs.addEventListener('wheel', e => {
  e.preventDefault();
  if (e.deltaY < 0) zoomIn(); else zoomOut();
});

// Resize
window.addEventListener('resize', () => { if (DATA) drawECG(); });

function setStatus(msg) { document.getElementById('status-text').textContent = msg; }

// ─── Disease Tracker ───
let CURRENT_REVIEW = {};

async function loadTracker() {
  const resp = await fetch('/api/disease_tracker');
  const {tracker} = await resp.json();
  const body = document.getElementById('tracker-body');
  body.innerHTML = '';

  tracker.forEach(d => {
    const card = document.createElement('div');
    card.style.cssText = `padding:6px 10px;border-radius:6px;border:1px solid var(--border);
      background:${d.done ? 'rgba(46,204,113,0.1)' : 'var(--surface2)'};
      min-width:180px;font-size:11px;`;

    let pHtml = d.patients.map(p => {
      const icon = p.reviewed ? '✓' : '○';
      const color = p.reviewed ? 'var(--green)' : 'var(--text2)';
      return `<span style="cursor:pointer;color:${color};margin-right:6px;"
                onclick="openReview('${d.condition}',${p.patient_num},${p.ecg_id})"
                title="ECG ${p.ecg_id}">${icon} P${p.patient_num} (${p.ecg_id})</span>`;
    }).join('');

    card.innerHTML = `<div style="font-weight:bold;color:${d.done?'var(--green)':'var(--accent)'};margin-bottom:3px;">
      ${d.condition} ${d.done?'✓':''}
    </div>${pHtml}`;
    body.appendChild(card);
  });
}

async function openReview(condition, patientNum, ecgId) {
  CURRENT_REVIEW = {condition, patientNum, ecgId};
  document.getElementById('review-title').textContent =
    `${condition} — Patient ${patientNum} (ECG ${ecgId})`;

  // Load existing review
  const resp = await fetch(`/api/load_review/${condition}/${patientNum}`);
  const {content, exists} = await resp.json();

  if (exists) {
    document.getElementById('review-content').value = content;
  } else {
    // Pre-fill template
    document.getElementById('review-content').value =
`# ${condition} — Patient ${patientNum} (ECG ${ecgId})
Date: ${new Date().toISOString().split('T')[0]}

## Ground Truth
- Condition: ${condition}

## Pipeline Findings
- (load the record and paste findings here)

## Vision LLM Findings
- (paste GPT-4o narration summary here)

## Discrepancies
-

## Issues Found
-

## Changes Made
-

## Status
- [ ] Pipeline narration matches expert assessment
- [ ] Fiducial points verified
- [ ] Detection correct
`;
  }

  document.getElementById('review-modal').style.display = '';
  document.getElementById('review-save-status').textContent = exists ? 'Loaded existing review' : 'New review';

  // Also load the record in the main dashboard
  document.getElementById('record-picker').value = ecgId;
  loadRecord();
}

async function saveReview() {
  const content = document.getElementById('review-content').value;
  const resp = await fetch('/api/save_review', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      condition: CURRENT_REVIEW.condition,
      patient_num: CURRENT_REVIEW.patientNum,
      ecg_id: CURRENT_REVIEW.ecgId,
      content: content,
    }),
  });
  const {status, path} = await resp.json();
  document.getElementById('review-save-status').textContent = `Saved to ${path}`;
  loadTracker();
}

function closeReviewModal() {
  document.getElementById('review-modal').style.display = 'none';
}

// ─── Shape Template Editor ───
const SHAPE_CODES = {
  P: ['P1','P2','P3','P4','P5','P6','P7'],
  QRS: ['Q1','Q2','Q3','Q4','Q5','Q6','Q7','Q8','Q9','Q10','Q11','Q12'],
  ST: ['ST1','ST2','ST3','ST4','ST5','ST6','ST7','ST8'],
  T: ['T1','T2','T3','T4','T5','T6','T7','T8','T9','T10','T11','T12','T13','T14'],
};

function showShapeEditor() {
  if (!DATA) { alert('Load a record first'); return; }
  document.getElementById('shape-panel').style.display = '';
  loadShapes();
}

async function loadShapes() {
  if (!DATA) return;
  const beatIdx = parseInt(document.getElementById('shape-beat').value) || 0;
  const body = document.getElementById('shape-body');
  body.innerHTML = '<div class="loading"><div class="spinner"></div>Classifying shapes...</div>';

  try {
    const resp = await fetch(`/api/shapes/${DATA.ecg_id}/${beatIdx}`);
    const {shapes, composites, lead_contexts, heart_position} = await resp.json();

    // Build table: rows=leads, columns=P/QRS/ST/T
    const segments = ['P','QRS','ST','T'];
    const leads = Object.keys(shapes).sort((a,b) => {
      const order = ['I','II','III','aVR','aVL','aVF','V1','V2','V3','V4','V5','V6'];
      return order.indexOf(a) - order.indexOf(b);
    });

    // Heart position header
    let hpHtml = '';
    if (heart_position) {
      const tags = [];
      tags.push(`Axis: ${heart_position.axis_category}`);
      tags.push(`Rotation: ${heart_position.rotation}`);
      if (heart_position.transition_zone) tags.push(`Transition: V${heart_position.transition_zone.toFixed(1)}`);
      if (heart_position.dextrocardia) tags.push('⚠ DEXTROCARDIA');
      if (heart_position.low_voltage) tags.push('⚠ LOW VOLTAGE');
      hpHtml = `<div style="margin-bottom:8px;font-size:11px;padding:4px 8px;background:var(--surface2);border-radius:4px;">
        <b>Heart Position:</b> ${tags.join(' | ')}
      </div>`;
    }

    // Composite patterns header
    let compHtml = '';
    if (composites && Object.keys(composites).length > 0) {
      const compItems = [];
      for (const [lead, comps] of Object.entries(composites)) {
        for (const c of comps) {
          compItems.push(`<span style="color:var(--orange);font-weight:bold;">${c.code}:${c.name}</span> in ${lead} (${(c.confidence*100).toFixed(0)}%)`);
        }
      }
      compHtml = `<div style="margin-bottom:8px;font-size:11px;padding:4px 8px;background:rgba(243,156,18,0.1);border:1px solid var(--orange);border-radius:4px;">
        <b>Composite Patterns:</b> ${compItems.join(' | ')}
      </div>`;
    }

    let html = hpHtml + compHtml;
    html += `<table style="width:100%;border-collapse:collapse;font-size:11px;">
      <tr style="background:var(--surface2);">
        <th style="padding:4px 8px;text-align:left;border:1px solid var(--border);">Lead</th>
        <th style="padding:4px 6px;border:1px solid var(--border);font-size:10px;">Context</th>
        ${segments.map(s => `<th style="padding:4px 8px;border:1px solid var(--border);">${s}</th>`).join('')}
      </tr>`;

    for (const lead of leads) {
      const ctx = lead_contexts?.[lead] || {};
      const terrColor = {septal:'#3498DB',anterior:'#E74C3C',lateral:'#2ECC71',inferior:'#F39C12',cavity:'#9B59B6'}[ctx.territory] || 'var(--text2)';

      html += `<tr>`;
      html += `<td style="padding:3px 8px;font-weight:bold;border:1px solid var(--border);">${lead}</td>`;

      // Context column
      let ctxParts = [`<span style="color:${terrColor};font-weight:bold;">${(ctx.territory||'?').toUpperCase()}</span>`];
      if (ctx.j_point_mv !== null && ctx.j_point_mv !== undefined) {
        const jpColor = Math.abs(ctx.j_point_mv) > 0.1 ? 'var(--orange)' : 'var(--text2)';
        ctxParts.push(`<span style="color:${jpColor};">J:${ctx.j_point_mv>0?'+':''}${ctx.j_point_mv.toFixed(2)}</span>`);
      }
      if (ctx.is_avr) ctxParts.push('<span style="color:var(--red);">aVR</span>');
      if (ctx.lbbb) ctxParts.push('<span style="color:var(--orange);">LBBB</span>');
      if (ctx.rbbb) ctxParts.push('<span style="color:var(--orange);">RBBB</span>');
      if (ctx.transition_shifted) ctxParts.push('<span style="color:var(--yellow);">↻</span>');
      html += `<td style="padding:2px 4px;border:1px solid var(--border);font-size:9px;line-height:1.3;">${ctxParts.join('<br>')}</td>`;

      for (const seg of segments) {
        const shape = shapes[lead]?.[seg];
        if (shape) {
          const confColor = shape.confidence > 0.7 ? 'var(--green)' :
                           shape.confidence > 0.4 ? 'var(--orange)' : 'var(--red)';
          html += `<td style="padding:3px 6px;border:1px solid var(--border);">
            <div style="cursor:pointer;" onclick="openShapeDetail('${lead}','${seg}',${beatIdx},'${shape.code}')">
              <span style="font-weight:bold;color:var(--accent);">${shape.code}</span>
              <span style="color:var(--text2);font-size:10px;">${shape.name}</span>
              <span style="color:${confColor};font-size:10px;float:right;">${(shape.confidence*100).toFixed(0)}%</span>
            </div>
            <button onclick="event.stopPropagation();askAgentInline('${lead}','${seg}',${beatIdx})"
              style="margin-top:2px;font-size:9px;padding:1px 6px;background:var(--orange);color:#fff;border:none;border-radius:3px;cursor:pointer;opacity:0.7;">
              🧠 Ask
            </button>
          </td>`;
        } else {
          html += `<td style="padding:3px 6px;border:1px solid var(--border);color:var(--text2);">—</td>`;
        }
      }
      html += `</tr>`;
    }
    html += `</table>`;
    html += `<div style="margin-top:8px;color:var(--text2);font-size:10px;">Click any cell to view details. Use "🧠 Ask Agent" to send the image to Gemma with segment-specific prompt.</div>`;

    // Agent response panel (inline, below table)
    html += `<div id="agent-inline-panel" style="display:none;margin-top:12px;border:1px solid var(--orange);border-radius:6px;overflow:hidden;">
      <div style="padding:6px 10px;background:rgba(243,156,18,0.1);border-bottom:1px solid var(--orange);display:flex;justify-content:space-between;align-items:center;">
        <span style="font-weight:bold;color:var(--orange);font-size:12px;" id="agent-inline-title">Segment Agent</span>
        <button onclick="document.getElementById('agent-inline-panel').style.display='none'" style="font-size:10px;background:none;border:1px solid var(--border);color:var(--text2);padding:2px 8px;border-radius:4px;cursor:pointer;">Close</button>
      </div>
      <div id="agent-inline-body" style="padding:10px;"></div>
    </div>`;

    body.innerHTML = html;
  } catch (e) {
    body.innerHTML = `<div style="color:var(--red);">Error: ${e.message}</div>`;
  }
}

async function openShapeDetail(lead, segment, beatIdx, currentCode) {
  if (!DATA) return;

  // Fetch waveform data
  const resp = await fetch(`/api/shape_waveform/${DATA.ecg_id}/${beatIdx}/${lead}/${segment}`);
  const wfData = await resp.json();

  if (wfData.error) { alert(wfData.error); return; }

  const codes = SHAPE_CODES[segment] || [];
  const codeOptions = codes.map(c =>
    `<option value="${c}" ${c===currentCode?'selected':''}>${c}</option>`
  ).join('');

  const modal = document.getElementById('review-modal');
  document.getElementById('review-title').textContent =
    `Shape: ${lead} ${segment} — Beat ${beatIdx+1} — ${currentCode}`;

  const featHtml = Object.entries(wfData.features).map(([k,v]) =>
    `<span style="margin-right:12px;"><b>${k}:</b> ${typeof v==='number'?v.toFixed(3):v}</span>`
  ).join('');

  document.getElementById('review-content').value = '';
  document.getElementById('review-content').style.display = 'none';

  const contentArea = document.getElementById('review-content').parentElement;
  contentArea.innerHTML = `
    <div style="display:flex;gap:12px;">
      <div style="flex:2;">
        <div style="font-size:11px;font-weight:bold;color:var(--accent);margin-bottom:4px;">
          Full Signal — ${lead} (target beat in blue, others in gray)
        </div>
        <canvas id="shape-canvas-full" width="1200" height="300"
          style="width:100%;background:var(--bg);border:1px solid var(--border);border-radius:4px;"></canvas>
      </div>
      <div style="flex:1;">
        <div style="font-size:11px;font-weight:bold;color:var(--accent);margin-bottom:4px;">
          Normalized Shape (64 samples)
        </div>
        <canvas id="shape-canvas-norm" width="400" height="300"
          style="width:100%;background:var(--bg);border:1px solid var(--border);border-radius:4px;"></canvas>
      </div>
    </div>
    <div style="margin-top:8px;font-size:11px;color:var(--text2);line-height:1.6;">${featHtml}</div>
    <div style="margin-top:12px;display:flex;gap:8px;align-items:center;flex-wrap:wrap;">
      <button onclick="askSegmentAgent('${lead}','${segment}',${beatIdx})"
        style="padding:4px 12px;border-radius:4px;cursor:pointer;background:var(--orange);color:#fff;border:none;font-size:11px;">
        🧠 Ask ${segment} Agent (Gemma)
      </button>
      <label style="font-size:11px;">Assign shape:</label>
      <select id="shape-assign" style="font-size:12px;">${codeOptions}</select>
      <input id="shape-notes" placeholder="Notes..." style="flex:1;font-size:11px;padding:4px 8px;background:var(--bg);border:1px solid var(--border);color:var(--text);border-radius:4px;">
      <button onclick="saveShapeTemplate('${lead}','${segment}',${beatIdx})" class="primary"
        style="padding:4px 12px;border-radius:4px;cursor:pointer;background:var(--accent);color:#fff;border:none;font-size:11px;">
        Save as Template
      </button>
    </div>
    <div id="agent-response" style="margin-top:8px;display:none;padding:8px;background:var(--surface2);border:1px solid var(--border);border-radius:4px;font-size:11px;"></div>
    <div id="shape-save-status" style="margin-top:4px;font-size:10px;color:var(--text2);"></div>
    <textarea id="review-content" style="display:none;"></textarea>
  `;

  window._shapeWaveform = wfData.waveform;
  window._shapeFeatures = wfData.features;
  modal.style.display = '';

  // ── Draw full signal with beat context ──
  const fullCanvas = document.getElementById('shape-canvas-full');
  const fCtx = fullCanvas.getContext('2d');
  const fw = fullCanvas.width, fh = fullCanvas.height;
  fCtx.clearRect(0, 0, fw, fh);

  if (SIGNALS[lead]) {
    const {time, amplitude} = SIGNALS[lead];
    const tMin = 0, tMax = time[time.length-1];
    const aMin = -2, aMax = 2;
    const pad = 10;

    const tx = t => pad + (t - tMin) / (tMax - tMin) * (fw - 2*pad);
    const ty = a => pad + (aMax - a) / (aMax - aMin) * (fh - 2*pad);

    // Grid
    fCtx.strokeStyle = 'rgba(244,194,194,0.15)';
    fCtx.lineWidth = 0.5;
    for (let t = 0; t < tMax; t += 0.2) {
      fCtx.beginPath(); fCtx.moveTo(tx(t), pad); fCtx.lineTo(tx(t), fh-pad); fCtx.stroke();
    }
    for (let a = aMin; a <= aMax; a += 0.5) {
      fCtx.beginPath(); fCtx.moveTo(pad, ty(a)); fCtx.lineTo(fw-pad, ty(a)); fCtx.stroke();
    }

    // Baseline
    fCtx.strokeStyle = 'rgba(255,255,255,0.1)';
    fCtx.beginPath(); fCtx.moveTo(pad, ty(0)); fCtx.lineTo(fw-pad, ty(0)); fCtx.stroke();

    // Full signal in gray
    fCtx.strokeStyle = 'rgba(150,150,150,0.4)';
    fCtx.lineWidth = 1.5;
    fCtx.beginPath();
    for (let i = 0; i < time.length; i++) {
      const x = tx(time[i]), y = ty(amplitude[i]);
      i === 0 ? fCtx.moveTo(x, y) : fCtx.lineTo(x, y);
    }
    fCtx.stroke();

    // Target beat segment in BLUE
    if (FIDUCIALS[lead] && FIDUCIALS[lead][beatIdx]) {
      const fids = FIDUCIALS[lead][beatIdx];
      // Determine segment boundaries
      const segBounds = {
        P: [fids.pon || fids.ppeak, fids.poff || fids.ppeak],
        QRS: [fids.qrson, fids.qrsoff],
        ST: [fids.qrsoff, fids.ton],
        T: [fids.ton, fids.toff],
      };
      const bounds = segBounds[segment];
      if (bounds && bounds[0] && bounds[1]) {
        const tStart = bounds[0], tEnd = bounds[1];

        // Highlight region
        fCtx.fillStyle = 'rgba(79,143,247,0.08)';
        fCtx.fillRect(tx(tStart), pad, tx(tEnd)-tx(tStart), fh-2*pad);

        // Draw segment in blue
        fCtx.strokeStyle = '#4f8ff7';
        fCtx.lineWidth = 3;
        fCtx.beginPath();
        let started = false;
        for (let i = 0; i < time.length; i++) {
          if (time[i] >= tStart && time[i] <= tEnd) {
            const x = tx(time[i]), y = ty(amplitude[i]);
            if (!started) { fCtx.moveTo(x, y); started = true; }
            else fCtx.lineTo(x, y);
          }
        }
        fCtx.stroke();
      }
    }

    // Lead label
    fCtx.fillStyle = '#e1e4eb';
    fCtx.font = 'bold 14px monospace';
    fCtx.fillText(lead + ' — ' + segment, pad + 4, pad + 16);
  }

  // ── Draw normalized waveform ──
  const normCanvas = document.getElementById('shape-canvas-norm');
  const nCtx = normCanvas.getContext('2d');
  const nw = normCanvas.width, nh = normCanvas.height;
  nCtx.clearRect(0, 0, nw, nh);

  const wf = wfData.waveform;
  const nPad = 20;

  // Grid
  nCtx.strokeStyle = 'rgba(255,255,255,0.05)';
  nCtx.lineWidth = 0.5;
  nCtx.beginPath(); nCtx.moveTo(nPad, nh/2); nCtx.lineTo(nw-nPad, nh/2); nCtx.stroke();

  // Normalized waveform in BLUE
  nCtx.strokeStyle = '#4f8ff7';
  nCtx.lineWidth = 2.5;
  nCtx.beginPath();
  for (let i = 0; i < wf.length; i++) {
    const x = nPad + (i / (wf.length-1)) * (nw - 2*nPad);
    const y = nPad + (1 - (wf[i]+1)/2) * (nh - 2*nPad);
    i === 0 ? nCtx.moveTo(x, y) : nCtx.lineTo(x, y);
  }
  nCtx.stroke();

  // Label
  nCtx.fillStyle = '#e1e4eb';
  nCtx.font = 'bold 12px monospace';
  nCtx.fillText(currentCode + ' — normalized', nPad, nPad - 4);
  nCtx.fillStyle = '#8b90a0';
  nCtx.font = '10px monospace';
  nCtx.fillText('+1', 2, nPad + 4);
  nCtx.fillText('-1', 2, nh - nPad + 4);
  nCtx.fillText('0', 2, nh/2 + 4);
}

async function askAgentInline(lead, segment, beatIdx) {
  if (!DATA) return;
  const panel = document.getElementById('agent-inline-panel');
  const body = document.getElementById('agent-inline-body');
  const title = document.getElementById('agent-inline-title');
  panel.style.display = '';
  title.textContent = `🧠 ${segment} Agent — ${lead} Beat ${beatIdx+1}`;
  body.innerHTML = `<div class="loading" style="height:auto;padding:12px;"><div class="spinner"></div>Sending image to ${segment} Agent (Gemma 27B)...</div>`;

  // Scroll to panel
  panel.scrollIntoView({behavior: 'smooth', block: 'nearest'});

  try {
    const resp = await fetch(`/api/segment_agent/${DATA.ecg_id}/${beatIdx}/${lead}/${segment}`);
    const result = await resp.json();

    if (result.error) {
      body.innerHTML = `<div style="color:var(--red);">Error: ${result.error}</div>`;
      return;
    }

    // Build per-lead result cards
    const leads = result.leads || [];
    let leadsHtml = '';
    if (leads.length > 0) {
      leadsHtml = leads.map(l => {
        const confColor = l.confidence === 'HIGH' ? 'var(--green)' : l.confidence === 'MEDIUM' ? 'var(--orange)' : 'var(--red)';
        return `<div style="padding:6px 8px;border:1px solid var(--border);border-radius:4px;margin-bottom:4px;background:var(--bg);">
          <div style="display:flex;justify-content:space-between;align-items:center;">
            <span style="font-weight:bold;color:var(--text);font-size:12px;">${l.lead || '?'}</span>
            <span style="font-size:16px;font-weight:bold;color:var(--accent);">${l.shape || '?'}</span>
            <span style="font-size:10px;color:${confColor};font-weight:bold;">${l.confidence || '?'}</span>
          </div>
          <div style="font-size:11px;color:var(--text2);margin-top:2px;">${l.name || ''}</div>
          ${l.amplitude ? `<div style="font-size:10px;color:var(--text2);">Amp: ${l.amplitude}${l.duration ? ' | Dur: '+l.duration : ''}${l.polarity ? ' | '+l.polarity : ''}</div>` : ''}
          ${l.pattern ? `<div style="font-size:10px;color:var(--text2);">Pattern: ${l.pattern}${l.r_amplitude ? ' | R:'+l.r_amplitude : ''}${l.s_amplitude ? ' S:'+l.s_amplitude : ''}</div>` : ''}
          ${l.j_point ? `<div style="font-size:10px;color:var(--text2);">J-point: ${l.j_point}${l.curvature ? ' | Curv: '+l.curvature : ''}</div>` : ''}
          ${l.symmetry ? `<div style="font-size:10px;color:var(--text2);">Symmetry: ${l.symmetry}</div>` : ''}
          <div style="font-size:10px;color:var(--text);margin-top:2px;">${l.description || ''}</div>
        </div>`;
      }).join('');
    } else {
      leadsHtml = `<div style="padding:8px;color:var(--text2);">(Could not parse per-lead results)</div>`;
    }

    body.innerHTML = `
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
        <!-- Left: Image + Prompt -->
        <div>
          <div style="font-size:11px;font-weight:bold;color:var(--accent);margin-bottom:4px;">IMAGE SENT TO GEMMA:</div>
          ${result.image ? `<img src="data:image/png;base64,${result.image}" style="width:100%;border:1px solid var(--border);border-radius:4px;background:white;">` : '(no image)'}
          <details style="margin-top:8px;">
            <summary style="cursor:pointer;font-size:10px;color:var(--text2);font-weight:bold;">PROMPT SENT (click to expand)</summary>
            <pre style="white-space:pre-wrap;font-size:9px;margin-top:4px;color:var(--text2);background:var(--bg);padding:8px;border-radius:4px;max-height:300px;overflow-y:auto;">${(result.prompt||'').replace(/</g,'&lt;')}</pre>
          </details>
        </div>
        <!-- Right: Per-lead results -->
        <div>
          <div style="font-size:11px;font-weight:bold;color:var(--orange);margin-bottom:4px;">
            GEMMA ${segment} AGENT — PER LEAD:
          </div>
          ${leadsHtml}
          <details style="margin-top:8px;">
            <summary style="cursor:pointer;font-size:10px;color:var(--text2);font-weight:bold;">Full raw response</summary>
            <pre style="white-space:pre-wrap;font-size:10px;margin-top:4px;color:var(--text);line-height:1.5;max-height:300px;overflow-y:auto;">${(result.raw_response||'').replace(/</g,'&lt;')}</pre>
          </details>
        </div>
      </div>
      <div style="margin-top:8px;display:flex;gap:8px;align-items:center;flex-wrap:wrap;">
        <span style="font-size:10px;color:var(--text2);">Save template for each lead:</span>
        ${leads.map(l => `
          <button onclick="saveFromAgentLead('${l.lead||lead}','${segment}',${beatIdx},'${l.shape||''}')"
            style="padding:2px 8px;border-radius:3px;cursor:pointer;background:var(--accent);color:#fff;border:none;font-size:10px;">
            ${l.lead||'?'}: ${l.shape||'?'}
          </button>
        `).join('')}
        <span id="agent-save-status" style="font-size:10px;color:var(--text2);"></span>
      </div>
    `;
  } catch (e) {
    body.innerHTML = `<div style="color:var(--red);">Error: ${e.message}</div>`;
  }
}

async function saveFromAgent(lead, segment, beatIdx) {
  const code = document.getElementById('agent-shape-accept')?.value;
  if (!code) return;
  const resp = await fetch('/api/save_template', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      ecg_id: DATA.ecg_id, lead, beat_idx: beatIdx, segment,
      shape_code: code,
      waveform: window._shapeWaveform || [],
      features: window._shapeFeatures || {},
      notes: 'Classified by segment agent (Gemma)',
    }),
  });
  const {total_templates} = await resp.json();
  document.getElementById('agent-save-status').textContent = `Saved! (${total_templates} total)`;
}

async function saveFromAgentLead(lead, segment, beatIdx, shapeCode) {
  if (!shapeCode || !DATA) return;
  const resp = await fetch('/api/save_template', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      ecg_id: DATA.ecg_id, lead, beat_idx: beatIdx, segment,
      shape_code: shapeCode,
      waveform: [],
      features: {},
      notes: `Classified by ${segment} agent (Gemma) for lead ${lead}`,
    }),
  });
  const {total_templates} = await resp.json();
  document.getElementById('agent-save-status').textContent = `Saved ${lead}:${shapeCode} (${total_templates} total)`;
}

async function askSegmentAgent(lead, segment, beatIdx) {
  if (!DATA) return;
  const agentDiv = document.getElementById('agent-response');
  agentDiv.style.display = '';
  agentDiv.innerHTML = `<div class="loading" style="height:auto;padding:8px;"><div class="spinner"></div>Asking ${segment} Agent (Gemma)...</div>`;

  try {
    const resp = await fetch(`/api/segment_agent/${DATA.ecg_id}/${beatIdx}/${lead}/${segment}`);
    const result = await resp.json();

    if (result.error) {
      agentDiv.innerHTML = `<div style="color:var(--red);">Error: ${result.error}</div>`;
      return;
    }

    // Show the image that was sent
    const imgHtml = result.image
      ? `<img src="data:image/png;base64,${result.image}" style="width:100%;border:1px solid var(--border);border-radius:4px;background:white;margin-bottom:8px;">`
      : '';

    // Update the shape dropdown to match agent's suggestion
    if (result.shape) {
      const select = document.getElementById('shape-assign');
      for (let opt of select.options) {
        if (opt.value === result.shape) { select.value = result.shape; break; }
      }
    }

    agentDiv.innerHTML = `
      <div style="font-weight:bold;color:var(--orange);margin-bottom:4px;">
        🧠 ${segment} Agent Response (Gemma)
      </div>
      ${imgHtml}
      ${result.shape ? `<div><b>Shape:</b> <span style="color:var(--accent);font-size:14px;font-weight:bold;">${result.shape}</span> — ${result.name || ''}</div>` : ''}
      ${result.confidence ? `<div><b>Confidence:</b> ${result.confidence}</div>` : ''}
      ${result.description ? `<div><b>Description:</b> ${result.description}</div>` : ''}
      <details style="margin-top:6px;">
        <summary style="cursor:pointer;color:var(--text2);font-size:10px;">Full response</summary>
        <pre style="white-space:pre-wrap;font-size:10px;margin-top:4px;color:var(--text2);">${result.raw_response || ''}</pre>
      </details>
    `;
  } catch (e) {
    agentDiv.innerHTML = `<div style="color:var(--red);">Error: ${e.message}</div>`;
  }
}

async function saveShapeTemplate(lead, segment, beatIdx) {
  const code = document.getElementById('shape-assign').value;
  const notes = document.getElementById('shape-notes').value;

  const resp = await fetch('/api/save_template', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      ecg_id: DATA.ecg_id,
      lead: lead,
      beat_idx: beatIdx,
      segment: segment,
      shape_code: code,
      waveform: window._shapeWaveform,
      features: window._shapeFeatures,
      notes: notes,
    }),
  });
  const {status, total_templates} = await resp.json();
  document.getElementById('shape-save-status').textContent =
    `Saved! Total templates: ${total_templates}`;
}

// Load tracker on init
setTimeout(loadTracker, 500);

init();
</script>
</body>
</html>
"""


# ─── Main ────────────────────────────────────────────────────────────────

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Narration comparison dashboard")
    parser.add_argument("--port", type=int, default=8050)
    parser.add_argument("--host", default="127.0.0.1")
    args = parser.parse_args()

    print(f"\n  YouOwnECG Narration Lab")
    print(f"  Open: http://{args.host}:{args.port}\n")
    app.run(host=args.host, port=args.port, debug=False)


if __name__ == "__main__":
    main()
