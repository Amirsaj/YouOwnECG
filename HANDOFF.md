# YouOwnECG — Complete Handoff Document for New Chat Session

**Date:** 2026-03-30
**Purpose:** Enable another Claude Code session to fully understand and continue this project

---

## 1. What This Project Is

YouOwnECG is a **local (self-hosted, no cloud) clinical-grade ECG analysis platform** for ER clinicians. It ingests raw 12-lead ECG signals, runs them through a "sacred pipeline" (signal processing + fiducial detection + feature extraction), sends computed features to AI agents (DeepSeek reasoner mode), and produces clinical diagnostic reports grounded in textbook evidence via RAG.

**Key principle:** No patient data ever leaves the machine. All processing is local.

---

## 2. The Framework: U-HIEF v4

The project follows **Universal Hierarchical Ideal Execution Framework v4** — a rigorous research-first methodology where:

1. **Research comes before code.** Every node in the project tree goes through: FD-FPRE (First-Principles Discovery) → PGMRs (Publication-Grade Module Reports) → RRC (adversarial peer review) → EPM gate approval → ONLY THEN implementation.

2. **The project is decomposed into 4 parallel departments (SDAs):**
   - **SDA-1: Signal & Vision Core** — raw signal → verified computed features
   - **SDA-2: Diagnosis & Agentic Core** — features → clinical findings via AI agents
   - **SDA-3: UI/UX & ER Workflow** — everything the clinician sees (Next.js frontend)
   - **SDA-4: Knowledge Base & RAG & Safety** — textbook ingestion → evidence grounding

3. **Each SDA has 4-7 research nodes**, each with a depth-4 decomposition tree. Every node produces:
   - `{N.N}_*.md` — FD-FPRE research document
   - `{N.N}_RRC_review.md` — adversarial review (GATE CONDITIONAL verdict)
   - `{N.N}_EPM_gate_response.md` — EPM adjudication (GATE PASSED)

4. **After ALL research gates pass**, an IEC (Implementation Execution Contract) is written specifying exact file structure, implementation order, and verification tasks (VTs).

5. **Document hierarchy:**
   ```
   Master_Charter.md (root problem, success metrics, 4 SDAs)
       → MC-001_Master_Contract.md (team contract for all 4 SDA leads)
           → SDA-1_Signal_Vision_Core.md (depth-4 tree + sub-contracts)
           → SDA-2_Diagnosis_Agentic_Core.md
           → SDA-3_UI_UX_ER_Workflow.md
           → SDA-4_Knowledge_RAG_Safety.md
               → IEC-001 through IEC-004 (implementation contracts)
   ```

---

## 3. The Sacred Pipeline (Inviolable Order)

```
1. INGEST       → RawECGRecord           (pipeline/ingestion.py)
2. PREPROCESS   → PreprocessedECGRecord   (pipeline/preprocessing.py)
3. QUALITY      → QualityReport           (pipeline/quality.py)
4. FIDUCIALS    → FiducialTable           (pipeline/fiducials.py)
5. FEATURES     → FeatureObject           (pipeline/features.py)
6. VISION       → VisionVerificationResult (pipeline/vision.py)
7. AGENTS       → DiagnosticResult        (agents/orchestrator.py)
```

No step may be skipped. No step may begin before its predecessor completes.

**Runner:** `pipeline/runner.py` orchestrates steps 1-6.

---

## 4. Agent Architecture (ADR-001: Option E — 3+1 Hybrid)

```
Phase 1 (parallel, async):
  ├── RRC Agent  — Rhythm / Rate / Conduction
  ├── IT Agent   — Ischemia / Territory
  └── MR Agent   — Morphology / Repolarization

Phase 2 (sequential, after Phase 1 completes):
  └── CDS Agent  — Cross-Domain Synthesis (resolves conflicts, applies cross-domain rules)
```

All agents use **DeepSeek reasoner mode** (deep reasoning, not lightweight chat).

Implemented in:
- `agents/deepseek.py` — DeepSeek API client with `_RoundedFloatEncoder`, retry, PHI stripping
- `agents/orchestrator.py` — `run_diagnostic()` dispatches Phase 1 async, then CDS
- `agents/schemas.py` — `DiagnosticResult`, `DiagnosticFinding`, `StatAlert` dataclasses
- `agents/context_builder.py` — builds feature context strings for each agent
- `agents/prompts.py` — agent system/user prompts

---

## 5. ECGdeli Integration

`ecgdeli/` at project root is a Python port of the KIT-IBT MATLAB fiducial detection toolbox.

**Key interface:**
```python
from ecgdeli.mastermind import annotate_ecg_multi
consensus_fpt, per_lead_fpt_list = annotate_ecg_multi(
    signal_multi, samplerate, lead_names, use_mastermind=True
)
```

**FPT columns (13):**
```
0=Pon  1=Ppeak  2=Poff  3=QRSon  4=Q  5=R  6=S  7=QRSoff  8=L  9=Ton  10=Tpeak  11=Toff  12=class
```

**Critical:** FPT indices are 0-based within the **safe analysis window** (not the full recording). The safe window excludes 3-second edge margins from the 10-second PTB-XL recordings. All feature extraction must slice signals to `[safe_window_start:safe_window_end]` before indexing with FPT values.

**Sentinel value:** `-1` for undetected fiducials (originally `0` from ecgdeli, converted to `-1` in `fiducials.py`).

---

## 6. Current Codebase Structure

```
YouOwnECG/
├── pipeline/                    # SDA-1: Sacred pipeline
│   ├── schemas.py               # All dataclasses
│   ├── ingestion.py             # Node 1.1: WFDB/EDF/CSV → RawECGRecord
│   ├── preprocessing.py         # Node 1.2: filtering, safe window
│   ├── quality.py               # Node 1.3: SNR, clipping, flatline
│   ├── fiducials.py             # Node 1.4: ECGdeli wrapper
│   ├── features.py              # Node 1.5: intervals, axis, voltage, ST, patterns
│   ├── vision.py                # Node 1.6: DeepSeek-VL2 verification
│   └── runner.py                # Orchestrates full SDA-1 pipeline
│
├── agents/                      # SDA-2: Diagnostic agents
│   ├── schemas.py               # DiagnosticResult, Finding, StatAlert
│   ├── deepseek.py              # DeepSeek API client
│   ├── orchestrator.py          # Phase 1 async + Phase 2 CDS
│   ├── context_builder.py       # Feature → agent prompt context
│   └── prompts.py               # System/user prompts per agent
│
├── api/                         # FastAPI backend
│   ├── main.py                  # App factory, CORS, routers
│   ├── db.py                    # SQLite persistence + audit trail
│   └── routes/
│       ├── ecg.py               # POST /ecg/analyze, GET /ecg/{id}, POST /ecg/{id}/override
│       └── qa.py                # POST /ecg/{id}/qa (SSE streaming)
│
├── rag/                         # SDA-4: RAG pipeline
│   ├── schemas.py               # Section, Chunk, ChunkMetadata, RetrievalResult
│   ├── ingestion.py             # Node 4.1: PDF → Section list (PyMuPDF)
│   ├── chunking.py              # Node 4.2: Section → Chunk list (tiktoken)
│   ├── embedding.py             # Node 4.3: Chunk → FAISS IndexFlatIP
│   ├── retrieval.py             # Node 4.4: query → RetrievalResult list
│   ├── safety.py                # Node 4.5: grounding check, numeric contradiction
│   ├── attribution.py           # Node 4.6: [REF:N] citation parsing
│   └── ingest_books.py          # CLI entry point
│
├── frontend/                    # SDA-3: Next.js 14 App Router
│   ├── app/
│   │   ├── page.tsx             # Landing page (upload)
│   │   ├── layout.tsx           # Root layout
│   │   └── ecg/[id]/
│   │       ├── page.tsx         # Server Component — fetches result
│   │       ├── ResultClient.tsx # Client Component — findings + override
│   │       └── QAPanel.tsx      # Client Component — streaming Q&A
│   ├── components/
│   │   ├── UploadForm.tsx       # Multi-file drag-drop (.hea + .dat pair)
│   │   ├── StatAlertBanner.tsx  # STAT alert (10s auto-minimise)
│   │   ├── FindingCard.tsx      # Finding display with citations
│   │   ├── MeasurementsTable.tsx
│   │   ├── ECGViewer.tsx        # Base64 ECG image
│   │   └── OverrideModal.tsx    # Role-gated clinical override
│   └── lib/
│       ├── api.ts               # Typed fetch wrappers
│       └── types.ts             # TypeScript DiagnosticResult schema
│
├── ecgdeli/                     # Python port of KIT-IBT fiducial detector
│
├── docs/architecture/           # All U-HIEF v4 documentation
│   ├── Master_Charter.md        # Root problem statement (v1.1 APPROVED)
│   ├── problems_first.md        # U-HIEF v4 methodology guide
│   ├── Traceability_Dashboard.md
│   ├── SDA-{1,2,3,4}_*.md      # SDA decomposition trees
│   ├── contracts/               # MC-001 + IEC-001 through IEC-004
│   └── nodes/                   # 72 research artifacts (FD-FPRE + RRC + EPM per node)
│       └── diseases/            # 94 disease knowledge base files + _INDEX.md
│
├── data/                        # Runtime data (gitignored)
│   ├── uploads/                 # Uploaded ECG files
│   ├── rag/                     # FAISS index + chunks (after ingestion)
│   └── youownecg.db             # SQLite (results + audit trail)
│
└── requirements.txt
```

---

## 7. Research Status — ALL 24 GATES PASSED

| SDA | Nodes | Status |
|-----|-------|--------|
| SDA-1 | 1.1-1.6 (Ingestion through Vision) | All gates passed 2026-03-29 |
| SDA-2 | 2.1-2.6 (Architecture through API Integration) | All gates passed 2026-03-27/28/29 |
| SDA-3 | 3.1-3.6 (Dashboard through Design Principles) | All gates passed 2026-03-29 |
| SDA-4 | 4.1-4.6 (Ingestion through Attribution) | All gates passed 2026-03-29 |

Node 2.7 (Disease Knowledge Base): 94/94 files complete with Section 6A agent assignments.

---

## 8. Implementation Status

| Component | Status | Notes |
|-----------|--------|-------|
| `pipeline/*` (SDA-1) | **COMPLETE + VT-TESTED** | All clinical VTs passing (normal sinus, AFib, STEMI, 1AVB, LBBB, WPW, LVH) |
| `agents/*` (SDA-2) | **CODE COMPLETE** | Not tested with live DeepSeek API (needs `DEEPSEEK_API_KEY`) |
| `api/*` | **WORKING** | End-to-end signal-only mode confirmed (POST + GET round-trip) |
| `rag/*` (SDA-4) | **CODE COMPLETE** | VT-4.1/4.2/4.5/4.6 pass. Books NOT yet ingested (needs embedding API key) |
| `frontend/*` (SDA-3) | **CODE COMPLETE** | TypeScript builds clean. Not browser-tested yet |

---

## 9. Critical Bugs Fixed (for reference)

1. **Safe-window offset** — FPT indices are 0-based within safe window; features.py must slice `morph = signal[:, s0:s1]` before indexing
2. **PR interval** — was `COL_PPEAK, sign=-1`; fixed to `COL_PON, sign=1` (P-onset → QRS-onset, clinical standard)
3. **LBBB/RBBB mutual exclusivity** — `if lbbb: rbbb = False`
4. **WPW detection** — needs `pr_ms < 120 AND qrs_ms >= 110`
5. **Hyperacute T threshold** — `t_amp` is in mV, threshold should be `0.6` not `600`
6. **AFib detection** — dual-path: `(rr_cv > 0.08 AND p_frac < 0.5) OR (p_frac == 0 AND rr_cv > 0.05)`
7. **np.bool_ serialization** — handled in `_RoundedFloatEncoder` and `_coerce()`
8. **Lead name normalization** — PTB-XL uses `AVF`; ingestion.py normalizes to `aVF`
9. **API multi-file upload** — WFDB needs both .hea + .dat; route accepts `files: List[UploadFile]`

---

## 10. What Remains (Priority Order)

### 10.1 CRITICAL PATH
1. **Switch RAG embeddings to local model** — `rag/embedding.py` currently uses OpenAI `text-embedding-3-small`. DeepSeek has no embedding model. Swap to `sentence-transformers/all-MiniLM-L6-v2` (384-dim, local, free). This unblocks book ingestion.
2. **Run book ingestion** — `python -m rag.ingest_books --books-dir ~/Documents/NewECG_Agentic/ecg-platform/books --output-dir data/rag`
3. **Extract and store textbook figures** — Currently only figure captions are extracted as text (`[Figure caption: ...]`). The actual images (ECG tracings, morphology diagrams) should be extracted as PNGs and stored alongside chunk metadata for future vision model comparison.
4. **Agent integration test** — Set `DEEPSEEK_API_KEY`, submit real ECG, verify full DiagnosticResult with findings + citations
5. **Wire RAG into agent context** — `agents/context_builder.py` has optional `rag_store` parameter; needs to call `retrieve()` and append `rag_block` to agent prompts

### 10.2 IMPORTANT
6. **Browser end-to-end test** — Copy `frontend/.env.local.example` → `.env.local`, run `npm run dev` + `uvicorn api.main:app --port 8000`
7. **Q&A route** — `api/routes/qa.py` exists but may need implementation; frontend `qaStream()` is already wired

### 10.3 ENHANCEMENTS
8. **Auth session** — Replace hardcoded `DEV_USER_ROLE=PHYSICIAN` with real auth
9. **Persian dual-language** — `clinical_summary_fa` field exists in schema; agent prompts need to generate it
10. **General ECG dashboard** — Interactive lead viewer with zoom/pan/annotations (D3.js)
11. **Per-disease dashboards** — Color-coded highlighting of relevant ECG segments

---

## 11. External Data Paths

| Resource | Path |
|----------|------|
| PTB-XL dataset | `/Users/amirsadjadtaleban/Documents/PTBXL/ptb-xl-a-comprehensive-electrocardiographic-feature-dataset-1.0.1` |
| ECG textbooks (4 PDFs) | `/Users/amirsadjadtaleban/Documents/NewECG_Agentic/ecg-platform/books` |
| Vault project memory | `/Users/amirsadjadtaleban/Documents/_vault/projects/YouOwnECG.md` |

---

## 12. How to Run

```bash
# Backend (signal-only, no API keys needed)
cd ~/Documents/YouOwnECG
uvicorn api.main:app --port 8000

# Frontend
cd ~/Documents/YouOwnECG/frontend
cp .env.local.example .env.local   # set NEXT_PUBLIC_API_URL=http://localhost:8000
npm run dev

# Full pipeline test (Python)
from pipeline.runner import run_pipeline
features, vision = await run_pipeline("/path/to/ecg.hea", ecg_id="test-001")

# Submit via API (WFDB pair)
curl -X POST http://localhost:8000/ecg/analyze -F "files=@record.hea" -F "files=@record.dat"
```

---

## 13. Key Design Decisions (ADRs)

- **ADR-001:** Agent architecture is Option E (3 parallel + 1 CDS), not 5 separate specialists
- **ADR-002:** Wellens syndrome is exclusively IT Agent's domain (not MR)
- **FPT sentinel:** `-1` for undetected fiducials (converted from ecgdeli's `0`)
- **Safe window:** 3-second margins excluded from 10-second recordings; FPT indices are relative to this window
- **No PTB-XL labels at inference:** Dataset used for validation only, never as input
- **Fail loud:** Poor quality input is rejected, not silently degraded
- **AI-generated label:** Every output explicitly labeled as AI-generated, never stated as diagnosis

---

## 14. Reading Order for Full Understanding

1. `docs/architecture/problems_first.md` — U-HIEF v4 methodology (how research nodes work)
2. `docs/architecture/Master_Charter.md` — Root problem, success metrics, 4 SDAs
3. `docs/architecture/contracts/MC-001_Master_Contract.md` — Team contract template
4. `docs/architecture/Traceability_Dashboard.md` — Status of all 24+ nodes
5. Any specific `docs/architecture/nodes/{N.N}_*.md` for deep research on a node
6. `docs/architecture/contracts/IEC-{001-004}_*.md` — Implementation specs
7. This file (`HANDOFF.md`) — Current state and what remains
