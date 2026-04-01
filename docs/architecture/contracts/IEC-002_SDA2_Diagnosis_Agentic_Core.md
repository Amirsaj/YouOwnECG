# IEC-002 — Implementation Execution Contract: SDA-2 Diagnosis & Agentic Core

**Contract Type:** IEC (Implementation Execution Contract)
**SDA:** SDA-2 (Diagnosis & Agentic Core)
**Date:** 2026-03-29
**Research Gate Status:** All nodes 2.1–2.6 PASSED (Node 2.7 disease KB complete)
**Prerequisite:** IEC-001 complete — FeatureObject available from pipeline/

---

## 1. Scope

Implement the agent orchestrator and the FastAPI backend:

```
FeatureObject + VisionResult
        ↓
  agents/orchestrator.py   ← Node 2.3 — Phase 1 async + Phase 2 CDS
  agents/rrc_agent.py      ← Rhythm/Rate/Conduction
  agents/it_agent.py       ← Ischemia/Territory
  agents/mr_agent.py       ← Morphology/Repolarization
  agents/cds_agent.py      ← Cross-Domain Synthesis
  agents/deepseek.py       ← Node 2.6 — DeepSeek API client
        ↓
  DiagnosticResult (findings + confidence + citations)
        ↓
  api/main.py              ← FastAPI app
  api/routes/ecg.py        ← POST /ecg/analyze, GET /ecg/{id}
  api/routes/qa.py         ← POST /ecg/{id}/qa (streaming)
  api/db.py                ← SQLite audit trail
```

---

## 2. Implementation Order

| Step | Module | Node |
|------|--------|------|
| 1 | `agents/deepseek.py` | 2.6 |
| 2 | `agents/schemas.py` | 2.2/2.3 |
| 3 | `agents/rrc_agent.py` | 2.2 |
| 4 | `agents/it_agent.py` | 2.2 |
| 5 | `agents/mr_agent.py` | 2.2 |
| 6 | `agents/cds_agent.py` | 2.2 |
| 7 | `agents/orchestrator.py` | 2.3 |
| 8 | `api/db.py` | 2.6 |
| 9 | `api/main.py` + routes | 3.5 |

---

## 3. Done Criteria

- `POST /ecg/analyze` accepts a file upload, runs full pipeline, returns DiagnosticResult JSON
- All 4 agents called; CDS receives Phase 1 outputs
- STAT findings produce `stat_alert_fires=True` regardless of confidence level
- Audit log written to SQLite for every agent call
- Server starts with `uvicorn api.main:app`
