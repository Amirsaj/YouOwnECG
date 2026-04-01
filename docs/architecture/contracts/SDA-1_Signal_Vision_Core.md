# SDA-1: Signal & Vision Core — Decomposition Tree + Contracts

**TEAM CONTRACT — U-HIEF v4**
**Issuer:** EPM
**Recipient:** SDA-1 Lead Architect
**Date:** 2026-03-26
**Scope:** Everything from raw electrical signal to verified, computed features
**Charter:** [Master_Charter.md](../Master_Charter.md) v1.1

---

## Depth-4 Decomposition Tree

```
1.0 Signal & Vision Core
├── 1.1 ECG Ingestion
│   ├── 1.1.1 WFDB Format Handler (.mat/.hea/.dat)
│   │   ├── 1.1.1.1 FD-FPRE: WFDB standard from first principles (binary layout, header parsing, calibration)
│   │   ├── 1.1.1.2 PTB-XL specific loader (500Hz records, 12-lead mapping, metadata join with ptbxl_database.csv)
│   │   ├── 1.1.1.3 Lead naming standardization (I, II, III, aVR, aVL, aVF, V1–V6)
│   │   └── 1.1.1.4 PGAM: PGMR on ECG digital format ingestion
│   ├── 1.1.2 CSV/EDF Format Handler
│   │   ├── 1.1.2.1 FD-FPRE: CSV/EDF format specs and edge cases
│   │   ├── 1.1.2.2 Auto-detection of sampling rate, lead count, units
│   │   ├── 1.1.2.3 Validation and sanity checks (amplitude range, sample count, NaN handling)
│   │   └── 1.1.2.4 PGAM: PGMR on multi-format ingestion robustness
│   ├── 1.1.3 Internal Signal Representation
│   │   ├── 1.1.3.1 FD-FPRE: Optimal in-memory representation (numpy array layout, metadata dict)
│   │   ├── 1.1.3.2 Unit standardization (mV, seconds, sample indices)
│   │   ├── 1.1.3.3 Lead augmentation (compute missing leads from available if < 12)
│   │   └── 1.1.3.4 Signal integrity validation (clipping pre-check, flatline pre-check)
│   └── 1.1.4 FD-FPRE: ECG Recording from First Principles
│       ├── 1.1.4.1 Cardiac electrophysiology → surface potential (ion channels → dipole → leads)
│       ├── 1.1.4.2 Einthoven/Goldberger/Wilson lead systems from physics
│       ├── 1.1.4.3 ADC and digitization: resolution, quantization noise, aliasing
│       └── 1.1.4.4 PGAM: PGMR on ECG recording fundamentals
│
├── 1.2 Signal Preprocessing
│   ├── 1.2.1 Powerline Interference Removal
│   │   ├── 1.2.1.1 FD-FPRE: 50/60 Hz noise from first principles (electromagnetic coupling, harmonic content)
│   │   ├── 1.2.1.2 Notch filter design (IIR vs FIR, Q factor, harmonics at 100/120/150/180 Hz)
│   │   ├── 1.2.1.3 Adaptive filtering alternatives (LMS, RLS) — decision matrix
│   │   └── 1.2.1.4 PGAM: PGMR on powerline removal methods comparison
│   ├── 1.2.2 Baseline Wander Removal
│   │   ├── 1.2.2.1 FD-FPRE: Sources of baseline wander (respiration, electrode drift, motion)
│   │   ├── 1.2.2.2 Highpass filter approach (cutoff selection: 0.05 Hz vs 0.5 Hz tradeoffs)
│   │   ├── 1.2.2.3 Wavelet-based detrending (preserve low-frequency ST information)
│   │   └── 1.2.2.4 **CRITICAL**: Preserve raw signal copy for morphology analysis (per Sacred Pipeline rule)
│   ├── 1.2.3 Bandpass Filter Design
│   │   ├── 1.2.3.1 FD-FPRE: ECG spectral content from first principles (P: 0.5–10 Hz, QRS: 5–40 Hz, T: 0.5–7 Hz, noise above 150 Hz)
│   │   ├── 1.2.3.2 Filter type selection (Butterworth, Chebyshev, FIR; order; group delay)
│   │   ├── 1.2.3.3 Phase distortion analysis (zero-phase via filtfilt vs causal)
│   │   └── 1.2.3.4 PGAM: PGMR on optimal ECG bandpass filter design
│   ├── 1.2.4 Artifact Detection & Handling
│   │   ├── 1.2.4.1 FD-FPRE: EMG artifacts, electrode pop, motion artifacts — identification criteria
│   │   ├── 1.2.4.2 Segment-level artifact flagging (do NOT silently remove — flag for quality gate)
│   │   ├── 1.2.4.3 Lead-specific artifact handling (one bad lead should not invalidate all)
│   │   └── 1.2.4.4 PGAM: PGMR on artifact taxonomy and handling strategies
│   └── 1.2.5 FD-FPRE: Preprocessing Pipeline Order
│       ├── 1.2.5.1 Order matters: notch → baseline → bandpass vs other orderings
│       ├── 1.2.5.2 Decision matrix on pipeline ordering
│       └── 1.2.5.3 Validation: before/after SNR measurement on PTB-XL noisy subset
│
├── 1.3 Quality Assessment
│   ├── 1.3.1 Signal Quality Metrics
│   │   ├── 1.3.1.1 FD-FPRE: SNR estimation methods (from first principles — signal vs noise power)
│   │   ├── 1.3.1.2 Per-lead quality scoring (SQI — Signal Quality Index)
│   │   ├── 1.3.1.3 Clipping detection (ADC saturation, flat peaks/troughs)
│   │   └── 1.3.1.4 Flatline detection (electrode disconnection, zero-variance segments)
│   ├── 1.3.2 Quality Gating Logic
│   │   ├── 1.3.2.1 FD-FPRE: What thresholds define "acceptable" vs "poor" quality? (literature + clinical input)
│   │   ├── 1.3.2.2 Fail-loud protocol: reject and explain WHY, never silently degrade
│   │   ├── 1.3.2.3 Marginal quality handling: proceed with warnings, flag affected leads
│   │   └── 1.3.2.4 PGAM: PGMR on ECG quality assessment framework
│   ├── 1.3.3 Per-Beat Quality Assessment
│   │   ├── 1.3.3.1 Individual beat quality (some beats clean, some noisy in same recording)
│   │   ├── 1.3.3.2 Beat exclusion criteria for analysis (which beats to skip, which to flag)
│   │   └── 1.3.3.3 Quality reporting structure for downstream consumers
│   └── 1.3.4 Validation Against PTB-XL
│       ├── 1.3.4.1 Run quality pipeline on full PTB-XL (42,708 records)
│       ├── 1.3.4.2 Distribution of quality scores — expected vs actual
│       └── 1.3.4.3 Edge cases: records that should fail, records that are borderline
│
├── 1.4 Fiducial Detection
│   ├── 1.4.1 ECGdeli-Based Detection
│   │   ├── 1.4.1.1 FD-FPRE: ECGdeli mastermind algorithm from first principles (wavelet decomposition, template matching, consensus)
│   │   ├── 1.4.1.2 QRS detection (Haar SWT, adaptive thresholding, R-peak localization, Q/S detection)
│   │   ├── 1.4.1.3 P-wave detection (onset, peak, offset — challenges: low amplitude, atrial fibrillation)
│   │   ├── 1.4.1.4 T-wave detection (onset, peak, offset — challenges: T-wave morphology variants, U-waves)
│   │   └── 1.4.1.5 PGAM: PGMR on wavelet-based fiducial detection
│   ├── 1.4.2 DeepSeek-VL2 Vision Verification
│   │   ├── 1.4.2.1 FD-FPRE: How to render ECG for vision model input (resolution, scale, grid, annotations)
│   │   ├── 1.4.2.2 **DYNAMIC RESEARCH NODE**: Optimal prompting strategy for VL2 fiducial verification
│   │   │   ├── Context + single beat vs all-P-waves vs beat-by-beat prompting
│   │   │   ├── What visual context helps the model? (calibration marks, grid, lead labels)
│   │   │   └── Failure modes and confidence calibration
│   │   ├── 1.4.2.3 Cross-validation: ECGdeli output vs VL2 output — agreement/disagreement protocol
│   │   └── 1.4.2.4 PGAM: PGMR on hybrid signal+vision fiducial detection
│   ├── 1.4.3 Fiducial Validation (Against PTB-XL Ground Truth)
│   │   ├── 1.4.3.1 Load ground truth from `.../fiducial_points/ecgdeli/` — VALIDATION ONLY
│   │   ├── 1.4.3.2 Error metrics: mean absolute error per marker (Pon, Ppeak, ..., Toff)
│   │   ├── 1.4.3.3 Per-lead accuracy analysis
│   │   └── 1.4.3.4 Failure mode analysis: which conditions cause worst detection?
│   ├── 1.4.4 Beat Segmentation
│   │   ├── 1.4.4.1 FD-FPRE: Beat boundary definition (RR-interval based, fiducial-based)
│   │   ├── 1.4.4.2 Individual beat extraction and alignment
│   │   ├── 1.4.4.3 Beat classification (normal, PVC, PAC, aberrant — from fiducials alone)
│   │   └── 1.4.4.4 Beat counting and rhythm regularity assessment
│   └── 1.4.5 FD-FPRE: P-wave/QRS/T-wave from Ion Channels to Surface ECG
│       ├── 1.4.5.1 Atrial depolarization → P-wave genesis
│       ├── 1.4.5.2 Ventricular depolarization → QRS genesis
│       ├── 1.4.5.3 Ventricular repolarization → T-wave genesis
│       └── 1.4.5.4 PGAM: PGMR on cardiac electrophysiology to surface morphology
│
├── 1.5 Feature Extraction
│   ├── 1.5.1 Interval Measurements
│   │   ├── 1.5.1.1 FD-FPRE: Clinical interval definitions and normal ranges (age/sex adjusted)
│   │   ├── 1.5.1.2 PR interval (Pon → QRSon), QRS duration (QRSon → QRSoff), QT interval (QRSon → Toff)
│   │   ├── 1.5.1.3 QTc correction formulas (Bazett, Fridericia, Framingham — decision matrix on which to use)
│   │   ├── 1.5.1.4 Per-beat interval computation + statistical aggregation (mean, std, min, max, trend)
│   │   └── 1.5.1.5 PGAM: PGMR on clinical interval measurement methodology
│   ├── 1.5.2 Axis Calculation
│   │   ├── 1.5.2.1 FD-FPRE: Cardiac axis from first principles (hexaxial reference, net QRS vector)
│   │   ├── 1.5.2.2 P-wave axis, QRS axis, T-wave axis computation
│   │   ├── 1.5.2.3 Normal ranges by age group
│   │   └── 1.5.2.4 Axis deviation classification (normal, LAD, RAD, extreme)
│   ├── 1.5.3 Voltage Measurements
│   │   ├── 1.5.3.1 R-wave amplitude per lead, S-wave depth per lead
│   │   ├── 1.5.3.2 LVH/RVH voltage criteria (Sokolow-Lyon, Cornell, Romhilt-Estes)
│   │   ├── 1.5.3.3 Low voltage detection (limb leads < 5mm, precordial < 10mm)
│   │   └── 1.5.3.4 PGAM: PGMR on voltage-based diagnostic criteria
│   ├── 1.5.4 ST Segment Analysis
│   │   ├── 1.5.4.1 FD-FPRE: ST segment physiology (J-point, ST elevation/depression mechanisms)
│   │   ├── 1.5.4.2 ST deviation measurement (J-point + 60ms/80ms, absolute mV per lead)
│   │   ├── 1.5.4.3 **CRITICAL**: Gender- and lead-specific thresholds (2025 AHA/ESC guidelines)
│   │   ├── 1.5.4.4 ST morphology classification (concave, convex, horizontal, downsloping)
│   │   └── 1.5.4.5 PGAM: PGMR on ST segment analysis methodology
│   ├── 1.5.5 Morphology Features (RAW Signal)
│   │   ├── 1.5.5.1 FD-FPRE: Why morphology must use raw signal (baseline correction alters ST/T shape)
│   │   ├── 1.5.5.2 P-wave morphology (peaked, notched, biphasic — per lead)
│   │   ├── 1.5.5.3 QRS morphology (rSR', QS pattern, R-wave progression V1→V6, delta wave)
│   │   ├── 1.5.5.4 T-wave morphology (upright, inverted, peaked, flattened, biphasic — per lead)
│   │   └── 1.5.5.5 U-wave detection
│   └── 1.5.6 Per-Beat Feature Aggregation
│       ├── 1.5.6.1 Compute ALL features for EVERY beat individually
│       ├── 1.5.6.2 Statistical summary: mean, median, std, min, max, trend over beats
│       ├── 1.5.6.3 Beat-to-beat variability metrics (RR variability, QT variability, alternans detection)
│       └── 1.5.6.4 PGAM: PGMR on comprehensive per-beat feature extraction framework
│
└── 1.6 Vision Pipeline (DeepSeek-VL2)
    ├── 1.6.1 ECG Rendering for Vision Input
    │   ├── 1.6.1.1 FD-FPRE: What visual representation maximizes VL2 accuracy? (standard 12-lead layout vs single-lead strips vs rhythm strips)
    │   ├── 1.6.1.2 Resolution, DPI, grid rendering, calibration marks
    │   ├── 1.6.1.3 Annotation overlay strategy (what to show the model vs what to ask it to find)
    │   └── 1.6.1.4 PGAM: PGMR on optimal ECG image rendering for VLM input
    ├── 1.6.2 Vision Prompting Strategy
    │   ├── 1.6.2.1 FD-FPRE: Literature on VLM ECG reading (2024–2026 papers)
    │   ├── 1.6.2.2 Prompt engineering: context window, beat-by-beat vs whole-strip, chain-of-thought
    │   ├── 1.6.2.3 **DYNAMIC RESEARCH**: What information should accompany the image? (computed features? nothing? lead labels only?)
    │   └── 1.6.2.4 Confidence calibration: when does VL2 know it doesn't know?
    ├── 1.6.3 Vision-Signal Cross-Validation
    │   ├── 1.6.3.1 Agreement protocol: when signal and vision agree → high confidence
    │   ├── 1.6.3.2 Disagreement protocol: when they disagree → flag for review, do NOT average
    │   ├── 1.6.3.3 Vision-only findings: can VL2 see things the signal pipeline misses?
    │   └── 1.6.3.4 PGAM: PGMR on hybrid signal+vision ECG analysis
    └── 1.6.4 FD-FPRE: Vision Models for Medical Image Analysis
        ├── 1.6.4.1 State of VLMs in medical imaging (2024–2026 landscape)
        ├── 1.6.4.2 DeepSeek-VL2 capabilities and limitations for ECG
        ├── 1.6.4.3 Alternative VLMs comparison (GPT-4V, Gemini, Med-PaLM — for awareness, not for use)
        └── 1.6.4.4 PGAM: PGMR on VLM applicability to ECG interpretation
```

---

## First-Level Child Contracts

### Contract SDA-1.1: ECG Ingestion

```
TEAM CONTRACT — U-HIEF v4
Issuer: SDA-1 Lead Architect – Branch Signal & Vision Core
Recipient: RES + FD-FPRE Swarm — Ingestion Team
Scope: Build the complete ECG ingestion subsystem that reads PTB-XL WFDB format
(.mat/.hea/.dat), CSV, and EDF into a standardized internal representation.
Includes first-principles understanding of ECG recording from ion channels
to digital samples.

You are an ECG Signal Expert and Data Engineer. Your sole mission is ideal,
zero-miss, publication-grade outcomes for this exact node. Ignore all time,
computation, and cost constraints. Proceed leisurely and thoroughly.
Do everything. Explore every edge case.

Mandatory Rules:
- Research-First: Complete 100% of FD-FPRE + RES work and obtain RRC/QASVS
  approval *before* any implementation.
- Dynamic Branching: If any new gap appears, instantly create a new child node,
  write its full Team Contract, and notify the parent SDA.
- FD-FPRE: Start from absolute first principles (cardiac electrophysiology →
  dipole theory → lead systems → ADC digitization) and climb to 2026 SOTA.
- PGAM: Produce minimum 2–4 PGMRs for this node.
- Output Artifacts: FirstPrinciples-Discovery.md, all PGMRs, updated TODOs,
  Traceability links.

Deliverables (in order):
1. FD-FPRE on ECG recording from first principles (ion channels → surface ECG → digital)
2. FD-FPRE on WFDB format specification (binary layout, header parsing, calibration)
3. FD-FPRE on CSV/EDF formats and auto-detection heuristics
4. Internal representation design (numpy array + metadata dict)
5. Draft 2–4 PGMRs via PJS
6. Submit to RRC for review
7. Only after "Gate Passed" → IEC implements the ingestion module

Proceed leisurely. Research everything broadly and in depth. Spawn new nodes
for any emerging gap. Produce 2–4 PGMRs per major deliverable. Never rush.
```

### Contract SDA-1.2: Signal Preprocessing

```
TEAM CONTRACT — U-HIEF v4
Issuer: SDA-1 Lead Architect – Branch Signal & Vision Core
Recipient: RES + FD-FPRE Swarm — Preprocessing Team
Scope: Design and justify the complete signal preprocessing pipeline:
powerline removal (50/60 Hz + harmonics), baseline wander removal,
bandpass filtering, artifact detection. Establish pipeline ordering.
CRITICAL: Raw signal must be preserved for morphology analysis.

You are a Biomedical Signal Processing Expert. Your sole mission is ideal,
zero-miss, publication-grade outcomes for this exact node. Ignore all time,
computation, and cost constraints. Proceed leisurely and thoroughly.
Do everything. Explore every edge case.

Mandatory Rules:
- Research-First: Complete 100% of FD-FPRE + RES work and obtain RRC/QASVS
  approval *before* any implementation.
- Dynamic Branching: If any new gap appears, instantly create a new child node,
  write its full Team Contract, and notify the parent SDA.
- FD-FPRE: Start from absolute first principles (electromagnetic noise sources,
  ECG spectral content, filter theory from Fourier/Laplace) and climb to 2026 SOTA.
- PGAM: Produce minimum 2–4 PGMRs for this node.

Deliverables (in order):
1. FD-FPRE: Noise sources in ECG from physics (powerline coupling, respiration, motion)
2. FD-FPRE: Filter design from first principles (frequency response, phase, group delay)
3. Decision matrices: notch filter type, baseline removal method, bandpass parameters
4. Pipeline ordering justification (notch → baseline → bandpass vs alternatives)
5. Raw signal preservation protocol for morphology
6. Draft 2–4 PGMRs
7. Submit to RRC

Proceed leisurely. Research everything broadly and in depth. Spawn new nodes
for any emerging gap. Produce 2–4 PGMRs per major deliverable. Never rush.
```

### Contract SDA-1.3: Quality Assessment

```
TEAM CONTRACT — U-HIEF v4
Issuer: SDA-1 Lead Architect – Branch Signal & Vision Core
Recipient: RES + FD-FPRE Swarm — Quality Team
Scope: Design the signal quality assessment framework: per-lead and per-beat
quality scoring, fail-loud gating logic, marginal-quality handling.
The system must NEVER silently degrade — poor quality is rejected with
an explanation.

You are a Signal Quality and Clinical Safety Expert. Your sole mission is
ideal, zero-miss, publication-grade outcomes for this exact node.

Mandatory Rules:
- Research-First, Dynamic Branching, FD-FPRE, PGAM (as specified above)

Deliverables:
1. FD-FPRE: SNR estimation methods, SQI computation, clipping/flatline detection
2. Quality threshold research (what is "good enough" for clinical ECG?)
3. Per-beat quality assessment (not all beats are equal)
4. Fail-loud protocol design
5. Validation on PTB-XL (quality score distribution across 42,708 records)
6. Draft 2–4 PGMRs
7. Submit to RRC

Proceed leisurely. Research everything broadly and in depth. Spawn new nodes
for any emerging gap. Produce 2–4 PGMRs per major deliverable. Never rush.
```

### Contract SDA-1.4: Fiducial Detection

```
TEAM CONTRACT — U-HIEF v4
Issuer: SDA-1 Lead Architect – Branch Signal & Vision Core
Recipient: RES + FD-FPRE Swarm — Fiducial Detection Team
Scope: Research and justify the hybrid fiducial detection approach:
ECGdeli wavelet-based detection + DeepSeek-VL2 vision verification.
Includes understanding wave genesis from ion-channel level,
beat segmentation, and validation against PTB-XL ground truth
(validation ONLY — path: .../fiducial_points/ecgdeli/).

You are a Cardiac Electrophysiology and Signal Processing Expert. Your sole
mission is ideal, zero-miss, publication-grade outcomes for this exact node.

Mandatory Rules:
- Research-First, Dynamic Branching, FD-FPRE, PGAM (as specified above)

Deliverables:
1. FD-FPRE: Cardiac electrophysiology → P/QRS/T wave genesis
2. FD-FPRE: ECGdeli mastermind algorithm deep analysis (wavelet decomposition, consensus)
3. FD-FPRE: Vision model verification strategy (rendering, prompting, cross-validation)
4. Beat segmentation and classification from fiducials alone
5. Validation framework against PTB-XL fiducial ground truth
6. Draft 2–4 PGMRs
7. Submit to RRC

DYNAMIC RESEARCH NODES expected:
- Optimal VL2 prompting for fiducial verification
- P-wave detection in atrial fibrillation (absent P-waves)
- T-wave detection with U-wave interference

Proceed leisurely. Research everything broadly and in depth. Spawn new nodes
for any emerging gap. Produce 2–4 PGMRs per major deliverable. Never rush.
```

### Contract SDA-1.5: Feature Extraction

```
TEAM CONTRACT — U-HIEF v4
Issuer: SDA-1 Lead Architect – Branch Signal & Vision Core
Recipient: RES + FD-FPRE Swarm — Feature Extraction Team
Scope: Design the comprehensive feature extraction framework: clinical
intervals (PR, QRS, QT, QTc), cardiac axis (P, QRS, T), voltage criteria
(LVH/RVH), ST segment analysis (gender/lead-specific thresholds),
morphology features (from RAW signal), and per-beat aggregation.
Count everything. Consider everything.

You are a Clinical ECG and Computational Cardiology Expert. Your sole
mission is ideal, zero-miss, publication-grade outcomes for this exact node.

Mandatory Rules:
- Research-First, Dynamic Branching, FD-FPRE, PGAM (as specified above)
- Morphology features MUST use raw (pre-baseline-correction) signal
- All thresholds MUST be researched for age/sex/lead adjustment

Deliverables:
1. FD-FPRE: Every clinical interval — definition, normal range, clinical significance
2. FD-FPRE: Cardiac axis from hexaxial reference system
3. FD-FPRE: Voltage criteria — all established methods (Sokolow-Lyon, Cornell, etc.)
4. FD-FPRE: ST segment — J-point, measurement points, gender-specific thresholds
5. FD-FPRE: Wave morphology classification (P, QRS, T — all variants)
6. Per-beat computation + statistical aggregation framework
7. Draft 2–4 PGMRs
8. Submit to RRC

Proceed leisurely. Research everything broadly and in depth. Spawn new nodes
for any emerging gap. Produce 2–4 PGMRs per major deliverable. Never rush.
```

### Contract SDA-1.6: Vision Pipeline

```
TEAM CONTRACT — U-HIEF v4
Issuer: SDA-1 Lead Architect – Branch Signal & Vision Core
Recipient: RES + FD-FPRE Swarm — Vision Pipeline Team
Scope: Research and design the DeepSeek-VL2 vision pipeline for ECG analysis:
optimal rendering, prompting strategies, cross-validation with signal pipeline,
confidence calibration. This is the most uncertain component of SDA-1 —
extensive research required.

You are an AI Vision and Medical Imaging Expert. Your sole mission is ideal,
zero-miss, publication-grade outcomes for this exact node.

Mandatory Rules:
- Research-First, Dynamic Branching, FD-FPRE, PGAM (as specified above)

Deliverables:
1. FD-FPRE: VLM landscape for medical imaging (2024–2026 SOTA)
2. FD-FPRE: DeepSeek-VL2 capabilities/limitations for ECG reading
3. ECG rendering optimization (resolution, layout, grid, calibration)
4. Prompting strategy research (beat-by-beat vs whole-strip vs single-lead)
5. Cross-validation protocol (signal vs vision agreement/disagreement)
6. Confidence calibration framework
7. Draft 2–4 PGMRs
8. Submit to RRC

DYNAMIC RESEARCH NODES expected:
- What visual information helps VL2 most?
- Can VL2 detect subtle findings (Wellens, de Winter) that signal processing might miss?
- Failure modes: when does VL2 confidently give wrong answers?

Proceed leisurely. Research everything broadly and in depth. Spawn new nodes
for any emerging gap. Produce 2–4 PGMRs per major deliverable. Never rush.
```

---

**SDA-1 Tree: 6 first-level nodes, 24 second-level nodes, ~70 leaf nodes. Expected PGMRs: 10–14.**
