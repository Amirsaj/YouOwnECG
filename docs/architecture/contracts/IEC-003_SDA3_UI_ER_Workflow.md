"""
IEC-003 — SDA-3 Implementation Contract: UI / ER Workflow (Next.js)

Issuer: EPM
Recipient: SDA-3 Implementation Lead
Date: 2026-03-29
Status: OPEN
Prerequisite gates: SDA-3 Nodes 3.1–3.6 ALL GATE PASSED ✓
"""

# IEC-003: SDA-3 UI / ER Workflow — Implementation Contract

## Scope

Build the Next.js 14 App Router frontend that lets ER clinicians:
1. Upload an ECG file and receive a streaming DiagnosticResult
2. View findings, STAT alerts, measurements, and citations
3. Ask follow-up Q&A questions with streaming responses
4. Override a finding (cardiologist/physician role-gated)

## Directory Layout

```
frontend/
├── app/
│   ├── layout.tsx              # Root layout — AI-GENERATED banner, global styles
│   ├── page.tsx                # Landing: upload form
│   ├── ecg/[id]/
│   │   ├── page.tsx            # ECG result page (Server Component — fetches result)
│   │   └── QAPanel.tsx         # Client Component — Q&A streaming
│   └── api/
│       └── proxy/              # Optional: proxy to FastAPI (avoids CORS in prod)
├── components/
│   ├── UploadForm.tsx          # Drag-drop + file validation
│   ├── StatAlertBanner.tsx     # Red top-of-page banner for STAT conditions
│   ├── FindingCard.tsx         # One card per DiagnosticFinding
│   ├── MeasurementsTable.tsx   # HR / PR / QRS / QTc / axis table
│   ├── ECGViewer.tsx           # Rendered ECG image (base64 via Server Component)
│   └── OverrideModal.tsx       # Role-gated override UI
├── lib/
│   ├── api.ts                  # Typed wrappers for FastAPI endpoints
│   └── types.ts                # TypeScript mirror of DiagnosticResult schema
├── public/
└── package.json
```

## Critical Constraints (from SDA-3 RRC reviews)

### Node 3.1 — Context assembly
- Q&A panel forwards only `BeatSummary + findings` to backend (not full FeatureObject)
- If R-peak list is empty, QAPanel shows "Insufficient beat data" and disables input

### Node 3.2 — STAT alerts
- `StatAlertBanner` renders for every `stat_alerts` entry regardless of confidence
- Banner persists until clinician explicitly dismisses
- After 10s auto-minimise to mini-strip (not full dismiss)

### Node 3.3 — STAT suppression
- Suppression is server-side only — UI sends POST to backend suppression endpoint
- Client never stores suppression state locally

### Node 3.4 — Override
- Override button only shown when `user.role` ∈ {CARDIOLOGIST, PHYSICIAN}
- Requires explicit confirmation modal before submission
- Override recorded via backend audit endpoint (never client-only)

### Node 3.5 — Streaming
- ECG image transfered as base64 string in JSON (not `Float32Array`) through Server Component boundary
- Q&A EventSource wrapped in AbortController; abort after 15s of no tokens
- Show "Response is taking longer than expected..." warning at 5s

### Node 3.6 — Bilingual
- `DiagnosticFinding.clinical_summary_fa` and `clinical_summary_en` rendered in separate `<p>` tags
- No client-side translation — both fields come from API

## TypeScript Schema (lib/types.ts)

```typescript
export interface DiagnosticFinding {
  finding_type: string;
  confidence: "HIGH" | "MODERATE" | "LOW" | "INSUFFICIENT_EVIDENCE";
  clinical_summary_en: string;
  clinical_summary_fa: string;
  technical_detail: string;
  citations: Citation[];
  rag_invoked: boolean;
}

export interface Citation {
  book_title: string;
  chapter: string;
  page: number;
  figure_ref: string | null;
  quote_snippet: string | null;
}

export interface StatAlert {
  condition: string;
  confidence: string;
  triggered_at: string;
}

export interface Measurements {
  heart_rate_ventricular_bpm: number | null;
  pr_interval_ms: number | null;
  qrs_duration_global_ms: number | null;
  qtc_bazett_ms: number | null;
  qrs_axis_deg: number | null;
  rhythm: string | null;
  lbbb: boolean;
  rbbb: boolean;
}

export interface DiagnosticResult {
  ecg_id: string;
  findings: DiagnosticFinding[];
  stat_alerts: StatAlert[];
  measurements: Measurements;
  overall_quality: "GOOD" | "ACCEPTABLE" | "POOR" | "UNINTERPRETABLE";
  pipeline_version: string;
  model_version: string;
}
```

## Implementation Order

1. `lib/types.ts` + `lib/api.ts` — typed fetch wrappers
2. `components/MeasurementsTable.tsx` + `components/FindingCard.tsx` — pure display
3. `components/StatAlertBanner.tsx` — STAT logic (10s timer, mini-strip)
4. `components/UploadForm.tsx` — file drag-drop, extension validation
5. `app/page.tsx` — landing + upload flow
6. `app/ecg/[id]/page.tsx` — Server Component result page
7. `app/ecg/[id]/QAPanel.tsx` — Client Component streaming Q&A
8. `components/ECGViewer.tsx` — base64 image display
9. `components/OverrideModal.tsx` — role-gated override

## Done Criteria (VTs)

| VT | Test |
|----|------|
| VT-3.1 | Upload `00083_hr.dat` → result page renders findings |
| VT-3.2 | Mock STEMI result → red STAT banner renders; auto-minimises at 10s |
| VT-3.3 | Q&A question → streaming tokens appear in panel; aborts at 15s no-token |
| VT-3.4 | Non-physician user → override button absent |
| VT-3.5 | Physician user → override modal → confirmation → audit POST fires |
| VT-3.6 | Result with Persian clinical_summary_fa → both languages render |
