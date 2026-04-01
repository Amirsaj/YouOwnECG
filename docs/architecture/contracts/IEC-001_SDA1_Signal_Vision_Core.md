# IEC-001 — Implementation Execution Contract: SDA-1 Signal & Vision Core

**Contract Type:** IEC (Implementation Execution Contract)
**SDA:** SDA-1 (Signal & Vision Core)
**Date:** 2026-03-29
**Research Gate Status:** All nodes 1.1–1.6 PASSED
**Prerequisite:** All FD-FPREs, RRC reviews, EPM responses complete

---

## 1. Scope

Implement the sacred pipeline stages 1–5:

```
Ingest (1.1) → Preprocess (1.2) → Quality (1.3) → Fiducials (1.4) → Features (1.5) → VisionPipeline (1.6)
```

Output: a fully-populated `FeatureObject` + `VisionVerificationResult` ready for SDA-2 agent dispatch.

---

## 2. Implementation Order (strict)

| Step | Module | Node | Output |
|------|--------|------|--------|
| 1 | `pipeline/ingestion.py` | 1.1 | `RawECGRecord` |
| 2 | `pipeline/preprocessing.py` | 1.2 | `PreprocessedECGRecord` |
| 3 | `pipeline/quality.py` | 1.3 | `QualityReport` |
| 4 | `pipeline/fiducials.py` | 1.4 | `FiducialTable` |
| 5 | `pipeline/features.py` | 1.5 | `FeatureObject` |
| 6 | `pipeline/vision.py` | 1.6 | `VisionVerificationResult` |
| 7 | `pipeline/runner.py` | All | Orchestrates 1–6 |

---

## 3. Verification Tasks (must pass before SDA-2 IEC)

| VT ID | Source | Task |
|-------|--------|------|
| VT-1.1-01 | Node 1.1 | Load PTB-XL WFDB + SCP + EDF; verify 12-lead shape, 500 Hz, Float32 |
| VT-1.2-01 | Node 1.2 | Verify safe analysis window excludes 3s edges; filtfilt on full record only |
| VT-1.3-01 | Node 1.3 | Bootstrap R-peaks internal to quality; REQUIRED_LEADS ischemia = 11 leads |
| VT-1.4-01 | Node 1.4 | FiducialTable total_recording_beats ≥ safe-window n_beats; AFib zeroing applied |
| VT-1.5-01 | Node 1.5 | Q_duration uses Q_idx; fQRS sign-change counter; P terminal force in mV·s |
| VT-1.6-01 | Node 1.6 | VL2 runs concurrently with Phase 1 agents; times out at 15s; result is advisory only |

---

## 4. File Structure

```
pipeline/
  __init__.py
  ingestion.py      ← Node 1.1
  preprocessing.py  ← Node 1.2
  quality.py        ← Node 1.3
  fiducials.py      ← Node 1.4
  features.py       ← Node 1.5
  vision.py         ← Node 1.6
  runner.py         ← orchestrates full SDA-1 pipeline
  schemas.py        ← all dataclasses: RawECGRecord, PreprocessedECGRecord, QualityReport, FiducialTable, FeatureObject, VisionVerificationResult
```

---

## 5. Dependencies

```
wfdb          ← WFDB/SCP/EDF ingestion
pyEDFlib      ← EDF ingestion
mne           ← EDF alternative
scipy         ← signal processing (butter, filtfilt, find_peaks)
numpy         ← all signal math
openai        ← VL2 vision API (DeepSeek-VL2 via compatible endpoint)
Pillow        ← ECG image rendering for VL2
matplotlib    ← ECG rendering (headless)
```

The `ecgdeli/` directory at the project root provides the fiducial detection engine. It is imported as `from ecgdeli.mastermind import mastermind_delineate`.

---

## 6. Done Criteria

- All 6 VTs pass on at least 3 PTB-XL records (1 normal sinus, 1 STEMI, 1 AFib)
- `runner.py` produces a valid `FeatureObject` JSON serializable with no None crashes
- `VisionVerificationResult` is returned (or a TIMEOUT result) for every pipeline run
- No debugging print statements in committed code
