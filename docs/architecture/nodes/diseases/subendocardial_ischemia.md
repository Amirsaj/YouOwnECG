# Subendocardial Ischemia — ECG Manifestation

**Status:** Stub — file was empty at time of Node 2.1 gate passage.

---

## 6A. Agent Assignment

**Architecture:** Option E — 3 Parallel Phase 1 Specialists + 1 Sequential CDS (Node 2.1 Gate Passed 2026-03-27)

| Agent | Role for Subendocardial Ischemia | Key Features Used |
|-------|--------------------------|-------------------|
| **RRC** (Rhythm/Rate/Conduction) | Supporting | Heart rate (demand ischemia at elevated rates), rhythm |
| **IT** (Ischemia/Territory) | Primary | Diffuse horizontal ST depression (not confined to single coronary territory), ST depression ≥0.5 mm in ≥2 contiguous leads, horizontal or downsloping morphology, absence of reciprocal ST elevation (distinguishes from STEMI), ST depression distribution assessment (diffuse vs territorial); horizontal ST depression in V1–V4 flagged for posterior STEMI differentiation |
| **MR** (Morphology/Repolarization) | Supporting | T-wave direction and morphology; R/S ratio in V1 (if V1–V4 depression prominent — CDS uses this to check for posterior STEMI mirror image) |
| **CDS** (Cross-Domain Synthesis) | Required — resolves subendocardial vs territorial vs posterior STEMI | Integrates IT's diffuse ST depression distribution with MR's R/S ratio in V1; if horizontal ST depression is prominent in V1–V4 AND MR reports dominant R in V1, CDS reclassifies as posterior STEMI mirror image rather than subendocardial ischemia |

### Primary Agent
**IT** — subendocardial ischemia is defined by diffuse, non-territorial horizontal ST depression representing circumferential subendocardial injury, which is the IT agent's ischemia/territory domain.

### Cross-Domain Hints
- IT emits `cross_domain_hint: "Horizontal ST depression prominent in V1–V4 — posterior STEMI mirror image must be excluded; MR R/S ratio in V1 required before subendocardial ischemia classification"` when anterior precordial depression is dominant.

### CDS Specific Role
CDS resolves the critical differential between subendocardial ischemia and posterior STEMI mirror image: horizontal ST depression in V1–V4 can represent either diffuse subendocardial ischemia or the reciprocal image of posterior wall STEMI. CDS applies the posterior STEMI check: if IT reports depression is most prominent in V1–V3 (horizontal, ≥0.5 mm) AND MR reports dominant R-wave in V1 (R/S ≥1), CDS reclassifies as posterior STEMI equivalent. If ST depression is equally distributed across multiple territories without dominant V1–V3 involvement and MR shows no dominant R in V1, CDS confirms the subendocardial ischemia pattern.

---
