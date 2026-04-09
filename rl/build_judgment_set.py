"""
Build judgment dataset for comparing Gemma+RAG vs LLM+RAG.

For 3 patients from different diseases:
  1. Renders all territory beat strip images
  2. Runs Visual Narrate (Gemma local) for each beat
  3. Runs Vision LLM (OpenAI GPT-4o) for each beat
  4. Runs RAG diagnosis with Gemma narration only
  5. Runs RAG diagnosis with LLM narration only
  6. Saves everything to rl/judgment/{disease}_patient_{ecgid}/

Output structure (one directory per patient):
  judgment/
    lbbb_patient_6174/
      00_README.md           ← summary + ground truth + measurements
      01_full_ecg.png        ← 12-lead overview
      images/
        beat1_septal.png
        beat1_anterior.png
        beat1_lateral.png
        beat1_inferior.png
        beat2_*.png (etc)
      gemma_narration.md     ← per-beat visual descriptions
      llm_narration.md       ← per-beat cloud LLM descriptions
      rag_with_gemma.md      ← RAG diagnosis using Gemma narration
      rag_with_llm.md        ← RAG diagnosis using LLM narration
      pipeline_narration.md  ← our signal-processing narration
"""

from __future__ import annotations
import asyncio
import csv
import json
import os
import sys
import time
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from validation.ptbxl_mapping import PTBXL_DIR, get_positive_findings
from agents.signal_findings import generate_signal_findings
from pipeline.ingestion import load_ecg
from pipeline.preprocessing import preprocess
from pipeline.quality import assess_quality
from pipeline.fiducials import detect_fiducials
from pipeline.features import extract_features
from pipeline.narrator import narrate_ecg
from pipeline.vision import render_ecg_image
from rl.vision_reward import (
    render_territory_beat_strip, TERRITORIES, assess_single_beat,
)
from pipeline.visual_narrator import describe_beat_visually


JUDGMENT_DIR = Path(__file__).parent / "judgment"
JUDGMENT_DIR.mkdir(exist_ok=True)

# Pick 3 patients from different diseases — one each
SELECTED = [
    {"disease": "imi",   "ecg_id": 210,  "label": "Inferior MI (IMI) — QS pattern III/aVF, LAD"},
    {"disease": "afib",  "ecg_id": 351,  "label": "Atrial Fibrillation (AFIB) — irregular, no P waves"},
    {"disease": "lvh",   "ecg_id": 96,   "label": "Left Ventricular Hypertrophy (LVH) — voltage criteria, no BBB"},
]

N_BEATS = 3


def run_for_patient(spec: dict):
    eid = spec["ecg_id"]
    disease = spec["disease"]
    label = spec["label"]

    out_dir = JUDGMENT_DIR / f"{disease}_patient_{eid}"
    images_dir = out_dir / "images"
    out_dir.mkdir(exist_ok=True)
    images_dir.mkdir(exist_ok=True)

    print(f"\n{'='*60}\n{label} — ECG {eid}\n{'='*60}")

    # ── Load and process ──
    subfolder = f"{(eid - 1) // 1000 * 1000:05d}"
    hea = str(PTBXL_DIR / f"records500/{subfolder}/{eid:05d}_hr.hea")
    print("Loading and processing ECG...")
    raw = load_ecg(hea, ecg_id=str(eid))
    prep = preprocess(raw)
    qual = assess_quality(prep)
    fid = detect_fiducials(prep, qual)
    feats = extract_features(prep, qual, fid)
    pipeline_narration = narrate_ecg(prep, fid, feats, max_beats=N_BEATS)

    # Get ground truth from PTB-XL
    import ast
    df = None
    try:
        import pandas as pd
        ptbxl_db = PTBXL_DIR / "ptbxl_database.csv"
        df = pd.read_csv(ptbxl_db)
        row = df[df.ecg_id == eid].iloc[0]
        scp = ast.literal_eval(row["scp_codes"])
        gt = sorted(get_positive_findings(scp, min_likelihood=50.0))
    except Exception as e:
        scp = {}
        gt = []
        print(f"  GT lookup failed: {e}")

    # ── Save full 12-lead image ──
    print("Rendering full ECG...")
    full_png = render_ecg_image(prep)
    (out_dir / "01_full_ecg.png").write_bytes(full_png)

    # ── Save per-beat territory strip images ──
    print(f"Rendering {N_BEATS} beats × 4 territories = {N_BEATS * 4} strips...")
    for beat_idx in range(N_BEATS):
        for territory, info in TERRITORIES.items():
            result = render_territory_beat_strip(
                prep, fid, beat_idx, territory, info["leads"], features=feats
            )
            if result:
                img, _ = result
                (images_dir / f"beat{beat_idx + 1}_{territory}.png").write_bytes(img)

    # ── Pipeline narration ──
    (out_dir / "pipeline_narration.md").write_text(
        f"# Pipeline Narration — {label}\n\n"
        f"ECG ID: {eid}\n"
        f"Ground Truth: {gt}\n\n"
        f"```\n{pipeline_narration}\n```\n"
    )

    # ── Visual Narrate (Gemma) ──
    print("Running Visual Narrate (Gemma local)...")
    gemma_narrations = {}
    for beat_idx in range(N_BEATS):
        print(f"  Beat {beat_idx + 1}/{N_BEATS}...")
        try:
            t0 = time.time()
            descriptions = describe_beat_visually(prep, fid, feats, beat_idx)
            elapsed = time.time() - t0
            gemma_narrations[beat_idx] = {"descriptions": descriptions, "elapsed_sec": elapsed}
            print(f"    done in {elapsed:.0f}s")
        except Exception as e:
            print(f"    ERROR: {e}")
            gemma_narrations[beat_idx] = {"error": str(e)}

    # Format Gemma narration as markdown
    gemma_md = [f"# Visual Narration (Gemma local) — {label}\n", f"ECG ID: {eid}\n"]
    for beat_idx, data in sorted(gemma_narrations.items()):
        gemma_md.append(f"\n## Beat {beat_idx + 1}\n")
        if "error" in data:
            gemma_md.append(f"Error: {data['error']}\n")
            continue
        for territory, desc in data.get("descriptions", {}).items():
            gemma_md.append(f"\n### {territory.upper()}\n")
            gemma_md.append(desc.strip() + "\n")
    (out_dir / "gemma_narration.md").write_text("\n".join(gemma_md))

    # ── Vision LLM (OpenAI) ──
    print("Running Vision LLM (OpenAI GPT-4o)...")
    llm_narrations = {}
    for beat_idx in range(N_BEATS):
        print(f"  Beat {beat_idx + 1}/{N_BEATS}...")
        try:
            t0 = time.time()
            text, provider = assess_single_beat(prep, fid, feats, beat_idx, provider="openai")
            elapsed = time.time() - t0
            llm_narrations[beat_idx] = {"text": text, "provider": provider, "elapsed_sec": elapsed}
            print(f"    done in {elapsed:.0f}s ({provider})")
        except Exception as e:
            print(f"    ERROR: {e}")
            llm_narrations[beat_idx] = {"error": str(e)}

    llm_md = [f"# Vision LLM Narration (OpenAI GPT-4o) — {label}\n", f"ECG ID: {eid}\n"]
    for beat_idx, data in sorted(llm_narrations.items()):
        llm_md.append(f"\n## Beat {beat_idx + 1}\n")
        if "error" in data:
            llm_md.append(f"Error: {data['error']}\n")
            continue
        llm_md.append(data.get("text", "") + "\n")
    (out_dir / "llm_narration.md").write_text("\n".join(llm_md))

    # ── Signal findings (deterministic) ──
    signal_findings = generate_signal_findings(feats)
    if signal_findings:
        findings_text = "\n=== PIPELINE SIGNAL FINDINGS (deterministic, high-confidence) ===\n"
        for sf in signal_findings:
            conf = getattr(sf, "confidence", "")
            findings_text += (
                f"  [{sf.finding_type.upper()}] {sf.clinical_summary}"
                f" | {sf.technical_detail} | confidence={conf}\n"
            )
        findings_text += "\n"
    else:
        findings_text = ""

    # ── RAG with Gemma narration ──
    print("Running RAG diagnosis with Gemma narration...")
    gemma_text = findings_text
    for beat_idx, data in sorted(gemma_narrations.items()):
        if "descriptions" in data:
            gemma_text += f"\n=== Beat {beat_idx + 1} ===\n"
            for t, d in data["descriptions"].items():
                gemma_text += f"\n{t.upper()}:\n{d}\n"

    try:
        from pipeline.diagnostic_rag import run_two_stage_diagnosis
        loop = asyncio.new_event_loop()
        rag_gemma = loop.run_until_complete(
            run_two_stage_diagnosis(gemma_text, feats)
        )
        loop.close()
    except Exception as e:
        rag_gemma = {"error": str(e)}

    (out_dir / "rag_with_gemma.md").write_text(
        f"# RAG Diagnosis (Gemma narration) — {label}\n\n"
        f"ECG ID: {eid}\nGround Truth: {gt}\n\n"
        "## Stage 1 — Observations\n```json\n"
        f"{json.dumps(rag_gemma.get('stage1_observations', rag_gemma), indent=2)}\n```\n\n"
        "## Stage 2 — Validated Findings\n```json\n"
        f"{json.dumps(rag_gemma.get('stage2_validated', {}), indent=2)}\n```\n"
    )

    # ── RAG with LLM narration ──
    print("Running RAG diagnosis with LLM narration...")
    llm_text = findings_text
    for beat_idx, data in sorted(llm_narrations.items()):
        if "text" in data:
            llm_text += f"\n=== Beat {beat_idx + 1} ===\n{data['text']}\n"

    try:
        loop = asyncio.new_event_loop()
        rag_llm = loop.run_until_complete(
            run_two_stage_diagnosis(llm_text, feats)
        )
        loop.close()
    except Exception as e:
        rag_llm = {"error": str(e)}

    (out_dir / "rag_with_llm.md").write_text(
        f"# RAG Diagnosis (LLM narration) — {label}\n\n"
        f"ECG ID: {eid}\nGround Truth: {gt}\n\n"
        "## Stage 1 — Observations\n```json\n"
        f"{json.dumps(rag_llm.get('stage1_observations', rag_llm), indent=2)}\n```\n\n"
        "## Stage 2 — Validated Findings\n```json\n"
        f"{json.dumps(rag_llm.get('stage2_validated', {}), indent=2)}\n```\n"
    )

    # ── README ──
    readme = f"""# Judgment Comparison — {label}

## Patient
- **ECG ID:** {eid}
- **Disease:** {disease}
- **Ground Truth:** {gt}
- **SCP Codes:** {scp}
- **Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Pipeline Measurements
- HR: {feats.heart_rate_ventricular_bpm:.0f} bpm
- Rhythm: {feats.dominant_rhythm}
- PR interval: {feats.pr_interval_ms} ms
- QRS duration: {feats.qrs_duration_global_ms} ms
- QTc (Bazett): {feats.qtc_bazett_ms:.0f} ms
- QRS axis: {feats.qrs_axis_deg:.0f}°
- LBBB: {feats.lbbb} | RBBB: {feats.rbbb} | WPW: {feats.wpw_pattern}

## Files in This Directory

| File | Description |
|------|-------------|
| `01_full_ecg.png` | Standard 12-lead ECG view |
| `images/beat{{N}}_{{territory}}.png` | Per-beat territory strips ({N_BEATS} beats × 4 territories = {N_BEATS * 4} images) |
| `pipeline_narration.md` | Our signal-processing narration |
| `gemma_narration.md` | Visual narration from Gemma 27B (local, free) |
| `llm_narration.md` | Vision narration from OpenAI GPT-4o |
| `rag_with_gemma.md` | RAG diagnosis using Gemma narration |
| `rag_with_llm.md` | RAG diagnosis using OpenAI narration |

## How to Compare in Claude

Open Claude.ai chat and:
1. Upload `01_full_ecg.png` + a few `images/beat{{N}}_*.png` files
2. Paste the contents of `gemma_narration.md` and `rag_with_gemma.md`
3. Paste the contents of `llm_narration.md` and `rag_with_llm.md`
4. Ask Claude to compare which approach better matches the ground truth

## Key Question to Ask Claude

> Given the ground truth is **{gt}**, which approach (Gemma+RAG vs OpenAI+RAG)
> better captured the morphology and produced a more accurate diagnosis?
> What are the strengths and weaknesses of each?
"""
    (out_dir / "00_README.md").write_text(readme)

    print(f"  ✓ Saved to {out_dir}")
    return out_dir


def main():
    print(f"\nBuilding judgment dataset in: {JUDGMENT_DIR}\n")
    print(f"Selected {len(SELECTED)} patients:")
    for s in SELECTED:
        print(f"  - {s['label']} (ECG {s['ecg_id']})")

    for spec in SELECTED:
        run_for_patient(spec)

    print(f"\n{'='*60}\nDone. All outputs in {JUDGMENT_DIR}\n{'='*60}")
    print("\nDirectories:")
    for d in sorted(JUDGMENT_DIR.iterdir()):
        if d.is_dir():
            print(f"  {d.name}")


if __name__ == "__main__":
    main()
