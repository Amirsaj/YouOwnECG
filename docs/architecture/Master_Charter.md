# Master Charter — YouOwnECG

**Framework:** U-HIEF v4 (Universal Hierarchical Ideal Execution Framework)
**Issued by:** Executive Product Manager (EPM)
**Date:** 2026-03-26
**Version:** 1.0
**Status:** APPROVED (v1.1 — revised per user feedback 2026-03-26)

---

## 1. Root Problem Statement

Build a complete, local (self-hosted, no cloud), clinical-grade web platform for ER clinicians — and later cardiologists — that performs comprehensive, transparent, traceable ECG analysis with the following capabilities:

### 1.1 Input Handling

- PTB-XL dataset formats: `.mat`, `.hea`, `.dat` (WFDB standard)
- Support for 1-lead through 12-lead configurations
- Any standard digital ECG format encountered in clinical practice (WFDB, CSV, EDF)

### 1.2 Output: Interactive General Dashboard

- Plot all leads simultaneously with clinical-standard layout
- Zoom, pan, and beat-selection interactivity
- Annotation overlays (fiducial points, intervals, findings)
- **Natural-language Q&A**: User clicks anywhere on the ECG and asks questions about THAT specific location — the system must have complete contextual knowledge of THIS patient's ECG at that point (which beat, which lead, what morphology, what's normal vs. abnormal)

### 1.3 Output: Per-Disease Dashboards

- For every detected or user-selected disease/condition: a dedicated, clean, color-coded dashboard
- Extremely simple and visually immediate 
- Highlights exactly the relevant ECG segments with arrows, color overlays, and annotations
- Explains in simple clinician language WHY the finding is abnormal
- Every explanation supported by RAG-retrieved sources from 4 ECG textbooks + medical literature
- Disease dashboards include but are not limited to: STEMI (by territory), Wellens syndrome, de Winter T-waves, complete AV block, bundle branch blocks, atrial fibrillation/flutter, LVH/RVH, long QT, Brugada, WPW, hyperkalemia, pericarditis, pulmonary embolism patterns, and more

### 1.4 Beat-by-Beat and Lead-by-Lead Analysis

- ECG is repetitive: every P-wave, every QRS complex, every ST segment, every T-wave across ALL beats and ALL leads must be individually examinable
- When relevant to a finding, the system shows beat-to-beat variation, lead-to-lead comparison, and identifies which specific beats/leads are abnormal
- The system must understand patient-level basics derived from each beat: heart rate, rhythm regularity, beat count, interval consistency, axis per beat — count everything, consider everything
- Every measurable parameter is computed per-beat and aggregated across the full record
- This is not optional — it is fundamental to rigorous ECG interpretation

### 1.5 Medical-Grade Data Pipeline

- Strict medical-grade signal processing only — no ordinary data-science shortcuts
- PTB-XL dataset used for development and validation
- Validated against PTB-XL metadata (`ptbxl_database.csv` — diagnostic descriptions, SCP codes, patient demographics, device info) which serves as clinical ground truth for evaluation
- Every processing step justified from first principles

### 1.6 Fiducial Detection Without Ground-Truth Labels

- P-wave onset/peak/offset, QRS onset/Q/R/S/QRS offset, T-wave onset/peak/offset
- Detection and verification must be achievable using:
  - Signal processing methods (ECGdeli wavelet-based detection)
  - LLM vision verification (DeepSeek-VL2 reading rendered ECG images)
  - Textual cross-validation methods
- **No ground-truth fiducial labels allowed in the final inference system** — the system must detect fiducials independently
- PTB-XL fiducial ground truth exists at `.../fiducial_points/ecgdeli/` and is used ONLY for validation (measuring detection accuracy), never as input to the inference pipeline

### 1.7 Agentic Diagnosis Architecture

- Diagnosis uses a completely novel agentic-model approach, NOT standard ML classifiers 
- 5 specialist agents (rhythm, conduction, ischemia, structural, morphology) running in parallel — **RESEARCH REQUIRED**: whether 5 agents is sufficient and whether these specific specializations are optimal (this is a mandatory FD-FPRE research node under SDA-2)
- **ALL agents (specialists + orchestrator) must use DeepSeek reasoner mode** for maximum reasoning depth and accuracy — no lightweight chat calls for diagnostic reasoning
- Orchestrator synthesizes findings via DeepSeek reasoner
- Each agent has a defined reasoning chain, confidence scoring, and RAG-grounded evidence
- STAT condition detection with immediate surfacing

### 1.8 Knowledge Base from 4 ECG Textbooks

- Books (with figures) must be properly ingested, chunked, embedded, and indexed
- RAG pipeline retrieves relevant textbook content for every finding
- **NO risky free-text narrations** of the ECG trace — all LLM outputs grounded in computed features + retrieved evidence
- Every citation links to specific book, chapter, page, and figure where applicable

### 1.9 ER-Optimized UI (Primary), Cardiologist Extension (Secondary)

- **ER mode**: Minimalist, glanceable, one-glance disease insights
  - Color-safe for color-blind users (deuteranopia, protanopia, tritanopia)
  - Low cognitive load under high-stress conditions
  - Critical findings front-and-center with no scrolling required
  - Large touch targets for gloved hands
- **Cardiologist mode**: Extended analysis views, beat-by-beat deep dives, morphology comparisons, full reasoning chains visible

### 1.10 Hybrid Methods

- Every possible complex technique is investigated and justified:
  - Signal processing (wavelets, adaptive filtering, morphological analysis)
  - Computer vision (DeepSeek-VL2 reading ECG images/strips)
  - Agentic LLM reasoning (multi-agent architecture)
  - RAG (textbook-grounded evidence retrieval)
  - Hybrid combinations of all the above
- Every choice justified with 2-4 Publication-Grade Module Reports (PGMRs)

---

## 2. Success Metrics

### 2.1 Clinical Accuracy


| Metric                                            | Target                       | Validation Method                             |
| ------------------------------------------------- | ---------------------------- | --------------------------------------------- |
| STEMI detection sensitivity                       | ≥ 99%                        | PTB-XL STEMI subset + DEC cardiologist review |
| STEMI detection specificity                       | ≥ 95%                        | PTB-XL non-STEMI subset                       |
| STAT condition detection (all 8+)                 | ≥ 98% sensitivity            | PTB-XL labeled subset + synthetic edge cases  |
| Fiducial point accuracy (vs. PTB-XL ground truth) | ≤ 10ms mean error per marker | PTB-XL fiducial annotations (eval only)       |
| Multi-label diagnosis F1 (all conditions)         | ≥ 0.85 macro-F1              | PTB-XL full diagnostic label set              |
| False narration rate (LLM hallucination)          | 0% unsupported claims        | Manual audit of 500 random reports            |


### 2.2 Signal Processing Quality


| Metric                              | Target                     |
| ----------------------------------- | -------------------------- |
| SNR improvement after preprocessing | ≥ 10 dB on noisy records   |
| Baseline wander residual            | < 0.05 mV peak-to-peak     |
| QRS detection sensitivity           | ≥ 99.5% (MIT-BIH standard) |
| Processing latency (12-lead, 10s)   | < 2 seconds end-to-end     |


### 2.3 UI/UX (ER Context)


| Metric                    | Target                                      | Validation Method                       |
| ------------------------- | ------------------------------------------- | --------------------------------------- |
| Time-to-critical-finding  | ≤ 3 seconds from page load                  | Usability testing with ER nurse persona |
| Color-blind accessibility | WCAG 2.1 AAA                                | Automated + manual audit                |
| Cognitive load score      | SUS ≥ 80                                    | System Usability Scale evaluation       |
| Touch target size         | ≥ 44px minimum                              | Design audit                            |
| One-glance comprehension  | Critical findings visible without scrolling | Layout validation                       |


### 2.4 RAG & Knowledge Base


| Metric                      | Target                                          |
| --------------------------- | ----------------------------------------------- |
| Retrieval relevance (top-5) | ≥ 90% relevant chunks                           |
| Citation accuracy           | 100% — every citation verifiable in source book |
| Figure retrieval accuracy   | ≥ 85% correct figure for finding                |
| Hallucination rate          | 0% — every claim grounded                       |


### 2.5 Publication Quality


| Metric                         | Target                               |
| ------------------------------ | ------------------------------------ |
| Total PGMRs produced           | ≥ 30 across all nodes                |
| PGMRs with ≥ 15 citations      | 100%                                 |
| ADRs with full decision matrix | 100%                                 |
| Traceability coverage          | Every artifact links to root problem |


---

## 3. Stakeholder Registry

### 3.1 Primary Stakeholders


| Stakeholder      | Role                    | Needs                                                                          | Priority |
| ---------------- | ----------------------- | ------------------------------------------------------------------------------ | -------- |
| **ER Nurse**     | Primary end user        | Instant, glanceable, stress-proof ECG interpretation with clear STAT alerts    | HIGHEST  |
| **ER Physician** | Clinical decision maker | Reliable findings to act on, transparent reasoning, no false reassurance       | HIGHEST  |
| **Cardiologist** | Advanced user (Phase 2) | Deep beat-by-beat analysis, morphology comparison, full agent reasoning chains | HIGH     |


### 3.2 Secondary Stakeholders


| Stakeholder           | Role                     | Needs                                                            |
| --------------------- | ------------------------ | ---------------------------------------------------------------- |
| **Patient**           | Subject of analysis      | Safe, accurate interpretation; data privacy; no cloud exposure   |
| **Hospital IT**       | Deployment & maintenance | Self-hosted, minimal infrastructure, standard web stack          |
| **Medical Director**  | Oversight                | Regulatory compliance, audit trail, explainability               |
| **Quality Assurance** | Validation               | Reproducible results, test coverage, known-failure documentation |


### 3.3 Domain Expert Council (DEC) Composition


| Expert Role           | Perspective            | Key Validation Areas                                       |
| --------------------- | ---------------------- | ---------------------------------------------------------- |
| **Cardiologist**      | Clinical correctness   | Diagnostic criteria, edge cases, STAT conditions           |
| **ECG Signal Expert** | Signal integrity       | Filter design, artifact handling, fiducial accuracy        |
| **ER Nurse**          | Usability under stress | Dashboard layout, alert priority, cognitive load           |
| **AI/XAI Architect**  | Model behavior         | Agent reasoning, confidence calibration, failure modes     |
| **UI/UX Expert**      | Interface design       | Information hierarchy, accessibility, interaction patterns |


---

## 4. Technical Environment

### 4.1 Stack


| Layer                  | Technology                                            | Justification                                              |
| ---------------------- | ----------------------------------------------------- | ---------------------------------------------------------- |
| **Backend**            | Python 3.9, FastAPI                                   | Medical signal processing ecosystem; async API             |
| **Signal Processing**  | ECGdeli (local port), NumPy, SciPy, PyWavelets        | Wavelet-based fiducial detection; clinical-grade filtering |
| **Quality Assessment** | NeuroKit2 0.2.7 (pinned for 3.9)                      | Signal quality metrics                                     |
| **Fiducial Detection** | ECGdeli mastermind + DeepSeek-VL2 vision verification | Hybrid signal + vision approach                            |
| **Feature Extraction** | Custom (intervals, axis, voltage, ST, morphology)     | Medical-grade computed features                            |
| **Agentic Diagnosis**  | 5 specialist agents + orchestrator via DeepSeek API   | Novel agentic approach, not standard ML                    |
| **RAG**                | ChromaDB, sentence-transformers, PyMuPDF              | Textbook-grounded evidence                                 |
| **Frontend**           | Next.js 14, TypeScript, Tailwind CSS, D3.js           | Interactive visualization; ER-optimized UI                 |
| **Hosting**            | Local (self-hosted)                                   | No cloud — patient data never leaves the machine           |


### 4.2 Data Sources


| Source                | Path                                                                                                         | Purpose                                                |
| --------------------- | ------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------ |
| **PTB-XL Dataset**    | `/Users/amirsadjadtaleban/Documents/PTBXL/ptb-xl-a-comprehensive-electrocardiographic-feature-dataset-1.0.1` | 42,708 12-lead ECG records; development and validation |
| **ECG Textbooks (4)** | `/Users/amirsadjadtaleban/Documents/NewECG_Agentic/ecg-platform/books`                                       | RAG knowledge base                                     |
| **ECGdeli Engine**    | `ecgdeli/` (project root)                                                                                    | Python port of KIT-IBT MATLAB toolbox                  |
| **PTB-XL Fiducials**  | `.../ptb-xl.../fiducial_points/ecgdeli/`                                                                     | Ground-truth fiducials — VALIDATION ONLY, never inference |
| **PTB-XL Metadata**   | `.../ptb-xl.../ptbxl_database.csv`                                                                           | Diagnostic labels, SCP codes, demographics — evaluation ground truth |
| **RAG Vector Store**  | `data/rag_store/`                                                                                            | ChromaDB persistent storage                            |


### 4.3 External APIs


| API          | Endpoint           | Purpose                                              |
| ------------ | ------------------ | ---------------------------------------------------- |
| **DeepSeek** | `api.deepseek.com` | Agentic reasoning (chat) + vision verification (VL2) |


### 4.4 ECGdeli FPT Column Mapping

```
Index  Column    Description
0      Pon       P-wave onset
1      Ppeak     P-wave peak
2      Poff      P-wave offset
3      QRSon     QRS complex onset
4      Q         Q-wave nadir
5      R         R-wave peak
6      S         S-wave nadir
7      QRSoff    QRS complex offset (J-point)
8      L         L-point (early ST segment)
9      Ton       T-wave onset
10     Tpeak     T-wave peak
11     Toff      T-wave offset
12     class     Beat classification
```

---

## 5. Sacred Pipeline Order (Inviolable)

No step may be skipped. No step may begin before its predecessor completes and passes quality checks.

```
┌──────────────────────────────────────────────────────────────────┐
│  1. INGEST        │ Read ECG from any supported format           │
│  (ingestion.py)   │ Output: raw digital signal array (leads×samples) │
├──────────────────────────────────────────────────────────────────┤
│  2. PREPROCESS    │ Notch filter (50/60 Hz), baseline wander     │
│  (preprocessing.py)│ removal, bandpass filter (0.05–150 Hz)      │
├──────────────────────────────────────────────────────────────────┤
│  3. QUALITY       │ SNR estimation, clipping detection, flatline │
│  (quality.py)     │ detection → FAIL LOUD on poor quality        │
├──────────────────────────────────────────────────────────────────┤
│  4. FIDUCIALS     │ ECGdeli mastermind: P, QRS, T detection      │
│  (fiducial_det.py)│ + DeepSeek-VL2 vision verification           │
├──────────────────────────────────────────────────────────────────┤
│  5. FEATURES      │ Intervals (PR, QRS, QT, QTc), axis,         │
│  (extractor.py)   │ voltages, ST analysis, morphology            │
├──────────────────────────────────────────────────────────────────┤
│  6. AGENTS        │ 5 specialists in parallel via ThreadPool:    │
│  (orchestrator.py)│ rhythm, conduction, ischemia, structural,    │
│                   │ morphology → orchestrator synthesizes         │
├──────────────────────────────────────────────────────────────────┤
│  7. REPORT        │ Narrative generation with safety hedging,    │
│  (report_gen.py)  │ RAG citations, confidence scores             │
│                   │ ALWAYS labeled as AI-generated                │
└──────────────────────────────────────────────────────────────────┘

CRITICAL RULES:
- Morphology analysis uses RAW signal (pre-baseline-correction)
- No PTB-XL labels at inference — training/eval only
- Every finding has confidence score + RAG citation
- Narration always labeled AI-generated, never stated as diagnosis
- Fail loudly on poor quality — no silent degradation
```

---

## 6. The Four SDA Branches

The project decomposes into four parallel Strategic Decomposition Architect branches:

### SDA-1: Signal & Vision Core

**Scope**: Everything from raw electrical signal to verified, computed features.

- ECG ingestion (digital formats: WFDB, CSV, EDF — no PDF/image input)
- Signal preprocessing (filtering, baseline, artifacts)
- Quality assessment (fail-loud gate)
- Fiducial detection (ECGdeli + vision hybrid)
- Feature extraction (all clinical intervals, axes, voltages, morphology)
- Vision verification pipeline (DeepSeek-VL2 reading rendered ECG images)
- Per-beat comprehensive parameter computation (count everything, aggregate everything)

### SDA-2: Diagnosis & Agentic Core

**Scope**: Everything from computed features to clinical findings and reasoning.

- Agent architecture design — **mandatory research node**: are 5 specialists (rhythm, conduction, ischemia, structural, morphology) sufficient? Are these the right specializations?
- All agents use DeepSeek reasoner mode (no lightweight chat) — individual reasoning chains
- Orchestrator synthesis strategy (also reasoner mode)
- Confidence scoring framework
- STAT condition detection pipeline
- Conflict resolution (when agents disagree)
- Beat-by-beat and lead-by-lead analysis strategy
- DeepSeek API integration for reasoning

### SDA-3: UI/UX & ER Workflow

**Scope**: Everything the clinician sees, touches, and interacts with.

- General dashboard (all leads, zoom, pan, annotations, NLP Q&A)
- Per-disease dashboards (color-coded, highlighted, arrows, explanations)
- ER optimization (glanceability, cognitive load, color-blind safety, touch targets)
- Cardiologist extension views
- Information architecture and hierarchy
- Real-time feedback and loading states
- Accessibility compliance (WCAG 2.1 AAA)

### SDA-4: Knowledge Base & RAG & Safety

**Scope**: Everything about grounding AI outputs in verifiable evidence.

- Book ingestion pipeline (4 textbooks, text + figures)
- Figure extraction, classification, and indexing
- Chunking strategy (semantic, overlap, metadata)
- Embedding and vector store (ChromaDB + sentence-transformers)
- Retrieval pipeline (query formulation, re-ranking, citation generation)
- Safety layer (no unsupported narration, mandatory hedging, AI-generated labels)
- Source attribution (book → chapter → page → figure)
- Regulatory awareness (SaMD framework considerations)

---

## 7. U-HIEF v4 Governance Rules (Constitution)

These rules are absolute and override all other considerations:

1. **Research-First**: 100% of FD-FPRE + RES work must complete, be drafted into PGMRs, reviewed by RRC, validated by QASVS, and receive written EPM "Research-First Gate Passed" approval BEFORE any IEC implementation for that node.
2. **Dynamic Branching**: Any node may spawn unlimited child branches the instant a knowledge gap appears. Depth capped at 4 unless EPM approves extension.
3. **Leisurely Execution**: Time, speed, and cost are irrelevant. Only ideal, publication-grade completeness matters.
4. **One Node at a Time**: Full concentration on the active node. Complete its deliverables, then explicitly stop and await approval.
5. **Contract Governance**: Sub-teams receive only the formal Team Contract from their direct lead. No external instructions.
6. **Publication Mandate**: Every major node produces 2-4 PGMRs in full journal style.
7. **Traceability**: Every artifact links back to the root problem via the Traceability Dashboard.
8. **No PTB-XL Labels at Inference**: Training and evaluation only.
9. **Fail Loud**: Poor quality input is rejected, not silently degraded.
10. **AI-Generated Label**: Every narrative output is explicitly labeled as AI-generated and never stated as a clinical diagnosis.

---

## 8. Traceability Dashboard (Stub)

This dashboard will be maintained as a living document throughout the project:

```markdown
| Node ID | Node Name | SDA Branch | Status | FD-FPRE | PGMRs | RRC | QASVS | DEC | Gate | IEC |
|---------|-----------|------------|--------|---------|-------|-----|-------|-----|------|-----|
| 1.0     | Signal & Vision Core | SDA-1 | Pending | - | - | - | - | - | - | - |
| 2.0     | Diagnosis & Agentic Core | SDA-2 | Pending | - | - | - | - | - | - | - |
| 3.0     | UI/UX & ER Workflow | SDA-3 | Pending | - | - | - | - | - | - | - |
| 4.0     | Knowledge Base & RAG & Safety | SDA-4 | Pending | - | - | - | - | - | - | - |
```

Status progression: `Pending` → `Research` → `Draft` → `Review` → `Validated` → `Gate Passed` → `Implementing` → `Verified` → `Complete`

---

## 9. Risk Registry


| Risk                                                                  | Severity | Mitigation                                                                         |
| --------------------------------------------------------------------- | -------- | ---------------------------------------------------------------------------------- |
| DeepSeek-VL2 cannot reliably read ECG morphology from images          | Critical | FD-FPRE research node (SDA-1); fallback to signal-only with documented limitation  |
| RAG retrieves irrelevant textbook content leading to wrong citations  | Critical | Chunking + retrieval research node (SDA-4); multi-stage re-ranking; DEC validation |
| LLM hallucinates clinical findings not supported by computed features | STAT     | Safety layer (SDA-4); mandatory grounding check; zero-tolerance policy             |
| ECGdeli fiducial detection fails on noisy records                     | High     | Quality gate (SDA-1); multi-method consensus; vision cross-validation              |
| ER UI too complex under stress                                        | High     | ER nurse DEC validation (SDA-3); iterative usability testing                       |
| PTB-XL label leakage into inference pipeline                          | Critical | Architectural separation enforced in SDA-1 and SDA-2; code audit gate              |
| Color-blind users miss critical findings                              | High     | WCAG AAA compliance (SDA-3); redundant encoding (color + shape + text)             |
| Beat-by-beat analysis computational cost too high for real-time       | Medium   | Optimization research (SDA-1/SDA-2); progressive loading strategy (SDA-3)          |


---

## 10. Approval Chain

```
Master Charter.md (this document)
        │
        ▼
  EPM/User Approval
        │
        ▼
  Master Contract → 4 SDA Leads
        │
        ▼
  SDA Depth-4 Trees + Child Contracts
        │
        ▼
  Research-First Gates (per node)
        │
        ▼
  IEC Implementation (per node)
        │
        ▼
  Final Integration & Validation
        │
        ▼
  FPHL Handoff
```

---

*End of Master Charter v1.1*
*Prepared by: EPM (Claude, U-HIEF v4)*
*Date: 2026-03-26*
*Revised: 2026-03-26 — incorporated user feedback (removed PDF/image input, added per-beat computation mandate, clarified PTB-XL CSV for validation, fiducial ground truth path for validation only, all agents use reasoner mode, mandatory research on agent count/specialization)*
*Status: APPROVED*