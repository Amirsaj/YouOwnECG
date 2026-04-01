# SDA-3: UI/UX & ER Workflow — Decomposition Tree + Contracts

**TEAM CONTRACT — U-HIEF v4**
**Issuer:** EPM
**Recipient:** SDA-3 Lead Architect
**Date:** 2026-03-26
**Scope:** Everything the clinician sees, touches, and interacts with
**Charter:** [Master_Charter.md](../Master_Charter.md) v1.1

---

## Depth-4 Decomposition Tree

```
3.0 UI/UX & ER Workflow
├── 3.1 General Dashboard
│   ├── 3.1.1 12-Lead ECG Visualization
│   │   ├── 3.1.1.1 FD-FPRE: Standard clinical ECG display formats (3×4+rhythm, Cabrera, custom)
│   │   ├── 3.1.1.2 D3.js implementation: SVG rendering, grid, calibration marks (25mm/s, 10mm/mV)
│   │   ├── 3.1.1.3 Lead labeling, color coding per lead group (limb vs precordial)
│   │   └── 3.1.1.4 PGAM: PGMR on clinical ECG display standards and digital implementation
│   ├── 3.1.2 Interactive Controls
│   │   ├── 3.1.2.1 Zoom (time axis, amplitude axis, both) — scroll wheel, pinch, button
│   │   ├── 3.1.2.2 Pan (horizontal scrolling through longer recordings)
│   │   ├── 3.1.2.3 Beat selection (click a beat → highlight, show fiducials, show features)
│   │   ├── 3.1.2.4 Lead isolation (click a lead → expand to full-width detail view)
│   │   └── 3.1.2.5 Measurement tools (calipers — click two points → show interval in ms)
│   ├── 3.1.3 Annotation Overlays
│   │   ├── 3.1.3.1 FD-FPRE: Best practices for ECG annotation display (2024–2026 digital ECG UI research)
│   │   ├── 3.1.3.2 Fiducial point markers (P, QRS, T onset/peak/offset — toggleable)
│   │   ├── 3.1.3.3 Interval labels (PR, QRS, QT displayed on trace)
│   │   ├── 3.1.3.4 Finding highlights (color overlays on abnormal segments)
│   │   └── 3.1.3.5 Toggle layers: user controls what annotations are visible
│   ├── 3.1.4 Natural-Language Q&A Interface
│   │   ├── 3.1.4.1 FD-FPRE: Click-to-ask UX patterns (2024–2026 interactive medical tools)
│   │   ├── 3.1.4.2 Click anywhere → system knows: which beat, which lead, which segment, what features
│   │   ├── 3.1.4.3 Context assembly: when user asks "Is this ST elevated?", system provides
│   │   │   the exact location, computed ST deviation, threshold, and RAG context to DeepSeek
│   │   ├── 3.1.4.4 Response display: inline answer near click point, with citations
│   │   └── 3.1.4.5 PGAM: PGMR on contextual NLP Q&A for ECG analysis
│   └── 3.1.5 Patient Record Summary
│       ├── 3.1.5.1 Heart rate (instantaneous + average), rhythm classification
│       ├── 3.1.5.2 All computed intervals and axes (table format)
│       ├── 3.1.5.3 Beat count summary (total, normal, PVC, PAC, other)
│       ├── 3.1.5.4 Quality assessment summary per lead
│       └── 3.1.5.5 Findings summary (list with confidence + STAT flags)
│
├── 3.2 Per-Disease Dashboards
│   ├── 3.2.1 Dashboard Template System
│   │   ├── 3.2.1.1 FD-FPRE: Color-coded medical dashboard design principles
│   │   ├── 3.2.1.2 Reusable template: header (disease name, confidence, STAT badge)
│   │   ├── 3.2.1.3 Reusable template: highlighted ECG (only relevant leads, arrows pointing to abnormality)
│   │   ├── 3.2.1.4 Reusable template: explanation panel (WHY this is abnormal, in clinician language)
│   │   ├── 3.2.1.5 Reusable template: evidence panel (RAG-retrieved textbook excerpt, page/figure reference)
│   │   └── 3.2.1.6 PGAM: PGMR on per-disease ECG dashboard architecture
│   ├── 3.2.2 STEMI Dashboard(s)
│   │   ├── 3.2.2.1 Territory-specific: anterior, inferior, lateral, posterior, RV
│   │   ├── 3.2.2.2 Highlight: affected leads with ST deviation values, reciprocal changes
│   │   ├── 3.2.2.3 Arrows: point to J-point elevation, reciprocal depression
│   │   ├── 3.2.2.4 Explanation: "ST elevation in V1-V4 suggests anterior STEMI involving LAD territory"
│   │   └── 3.2.2.5 Textbook reference: AHA/ESC STEMI criteria with page/figure
│   ├── 3.2.3 Arrhythmia Dashboards
│   │   ├── 3.2.3.1 AFib: highlight irregular RR, absent P-waves, fibrillatory baseline
│   │   ├── 3.2.3.2 AV Block: highlight P-waves vs QRS, show PR intervals, dropped beats
│   │   ├── 3.2.3.3 VT/VF: wide complex tachycardia display, STAT alert
│   │   └── 3.2.3.4 Bundle Branch Blocks: highlight QRS morphology in relevant leads
│   ├── 3.2.4 Structural Dashboards
│   │   ├── 3.2.4.1 LVH: voltage criteria visualization, strain pattern highlight
│   │   ├── 3.2.4.2 RVH: R-wave V1, RAD display
│   │   └── 3.2.4.3 Atrial enlargement: P-wave morphology across leads
│   ├── 3.2.5 Special Pattern Dashboards
│   │   ├── 3.2.5.1 Wellens: highlight T-wave morphology in V2-V3 (Type A vs B)
│   │   ├── 3.2.5.2 de Winter: highlight upsloping ST depression + tall T precordial
│   │   ├── 3.2.5.3 Brugada: highlight V1-V3 coved/saddle-back morphology
│   │   ├── 3.2.5.4 Long QT: highlight QT interval with correction, overlay normal range
│   │   └── 3.2.5.5 Hyperkalemia: progressive changes (peaked T → widened QRS → sine wave)
│   └── 3.2.6 PGAM: PGMR on Disease-Specific ECG Visualization
│       ├── 3.2.6.1 Literature review: medical data visualization (2024–2026)
│       ├── 3.2.6.2 Before/after usability comparison
│       └── 3.2.6.3 Clinician feedback integration methodology
│
├── 3.3 ER Optimization
│   ├── 3.3.1 FD-FPRE: ER Clinical Workflow and Cognitive Science
│   │   ├── 3.3.1.1 Literature: Cognitive load theory applied to medical dashboards
│   │   ├── 3.3.1.2 ER nurse workflow: when do they look at ECG? How long? What do they need first?
│   │   ├── 3.3.1.3 Time-critical decision making: what information in ≤3 seconds?
│   │   └── 3.3.1.4 PGAM: PGMR on ER-optimized clinical dashboard design
│   ├── 3.3.2 Glanceability Design
│   │   ├── 3.3.2.1 One-glance summary: STAT/CRITICAL/NORMAL badge (largest element on page)
│   │   ├── 3.3.2.2 Traffic-light system: red (STAT), yellow (abnormal), green (normal)
│   │   ├── 3.3.2.3 Information hierarchy: what's visible without scrolling (above the fold)
│   │   └── 3.3.2.4 Progressive disclosure: overview → click for detail → click for deep analysis
│   ├── 3.3.3 Color-Blind Accessibility
│   │   ├── 3.3.3.1 FD-FPRE: Color vision deficiency types and prevalence in medical professionals
│   │   ├── 3.3.3.2 WCAG 2.1 AAA color contrast requirements
│   │   ├── 3.3.3.3 Redundant encoding: color + shape + text (never color alone for critical info)
│   │   ├── 3.3.3.4 Palette design: safe for deuteranopia, protanopia, tritanopia simultaneously
│   │   └── 3.3.3.5 PGAM: PGMR on accessible medical dashboard color design
│   ├── 3.3.4 Touch & Motor Accessibility
│   │   ├── 3.3.4.1 Touch target minimum: 44px (WCAG), ideally 48px for gloved hands
│   │   ├── 3.3.4.2 No hover-only interactions (ER nurses may use touch screens)
│   │   ├── 3.3.4.3 Keyboard navigation for all critical actions
│   │   └── 3.3.4.4 Screen reader compatibility for non-visual access
│   └── 3.3.5 Alert Design
│       ├── 3.3.5.1 STAT alert: visual (red flash/banner) + position (top of screen, unmissable)
│       ├── 3.3.5.2 Alert fatigue prevention: only STAT conditions trigger highest alert
│       ├── 3.3.5.3 Alert acknowledgment workflow (nurse must acknowledge to dismiss)
│       └── 3.3.5.4 PGAM: PGMR on clinical alert design for ER settings
│
├── 3.4 Cardiologist Extension
│   ├── 3.4.1 Deep Analysis Views
│   │   ├── 3.4.1.1 Beat-by-beat comparison view (overlay multiple beats, spot differences)
│   │   ├── 3.4.1.2 Lead-by-lead detail view (single lead expanded, all features displayed)
│   │   ├── 3.4.1.3 Morphology comparison (current beat vs textbook reference)
│   │   └── 3.4.1.4 Trend view (how features change across the recording)
│   ├── 3.4.2 Reasoning Chain Viewer
│   │   ├── 3.4.2.1 Full agent reasoning display (each agent's chain of thought)
│   │   ├── 3.4.2.2 Confidence breakdown (signal confidence, agent confidence, RAG confidence)
│   │   ├── 3.4.2.3 Evidence trail (click finding → see reasoning → see textbook source)
│   │   └── 3.4.2.4 PGAM: PGMR on XAI interfaces for clinical ECG analysis
│   ├── 3.4.3 Comparison Mode
│   │   ├── 3.4.3.1 Compare current ECG with previous ECG (same patient, if available)
│   │   ├── 3.4.3.2 Compare with textbook reference ECG for a condition
│   │   └── 3.4.3.3 Side-by-side lead comparison
│   └── 3.4.4 Report Generation UI
│       ├── 3.4.4.1 Structured report view (findings, evidence, confidence)
│       ├── 3.4.4.2 "AI-GENERATED" label prominently displayed
│       ├── 3.4.4.3 Editable: cardiologist can annotate/override findings
│       └── 3.4.4.4 Export (PDF report with all citations)
│
├── 3.5 Frontend Architecture
│   ├── 3.5.1 Next.js 14 Application Structure
│   │   ├── 3.5.1.1 App router structure (pages, layouts, loading states)
│   │   ├── 3.5.1.2 Component architecture (atomic design: atoms, molecules, organisms)
│   │   ├── 3.5.1.3 State management (React context vs Zustand for ECG data)
│   │   └── 3.5.1.4 API integration layer (FastAPI backend communication)
│   ├── 3.5.2 D3.js ECG Rendering Engine
│   │   ├── 3.5.2.1 SVG vs Canvas performance for 12-lead ECG
│   │   ├── 3.5.2.2 Real-time zoom/pan performance optimization
│   │   ├── 3.5.2.3 Annotation layer architecture (separate SVG layer for overlays)
│   │   └── 3.5.2.4 PGAM: PGMR on high-performance ECG visualization with D3.js
│   ├── 3.5.3 Responsive Design
│   │   ├── 3.5.3.1 Desktop primary (ER workstation), tablet secondary (bedside)
│   │   ├── 3.5.3.2 Breakpoint strategy for medical dashboards
│   │   └── 3.5.3.3 ECG readability at different screen sizes
│   └── 3.5.4 Performance
│       ├── 3.5.4.1 Initial load time target: < 2 seconds to first meaningful paint
│       ├── 3.5.4.2 ECG render time: < 500ms for 12-lead display
│       ├── 3.5.4.3 Interaction latency: < 100ms for zoom/pan
│       └── 3.5.4.4 Lazy loading for per-disease dashboards (load on demand)
│
└── 3.6 FD-FPRE: Medical Dashboard Design from First Principles
    ├── 3.6.1 Human visual perception for data comprehension
    ├── 3.6.2 Pre-attentive visual processing (what the eye catches in <200ms)
    ├── 3.6.3 Medical informatics: clinical decision support interface design (2024–2026 SOTA)
    └── 3.6.4 PGAM: PGMR on evidence-based medical dashboard design
```

---

## First-Level Child Contracts

### Contract SDA-3.1: General Dashboard

```
TEAM CONTRACT — U-HIEF v4
Issuer: SDA-3 Lead Architect – Branch UI/UX & ER Workflow
Recipient: RES + FD-FPRE Swarm — Dashboard Team
Scope: Design the interactive general ECG dashboard: 12-lead visualization
(D3.js), zoom/pan/beat-selection, annotation overlays (fiducials, intervals,
findings), natural-language Q&A (click-to-ask), and patient record summary
(heart rate, rhythm, intervals, axes, beat counts, quality, findings).

You are a Medical Data Visualization and UX Expert. Your sole mission is
ideal, zero-miss, publication-grade outcomes for this exact node.

Deliverables:
1. FD-FPRE: Clinical ECG display standards and digital implementation best practices
2. FD-FPRE: Click-to-ask NLP UX patterns for medical tools
3. Wireframes and interaction design (zoom, pan, beat selection, lead isolation, calipers)
4. Annotation layer architecture (toggleable overlays)
5. NLP Q&A context assembly design (click → location → features → RAG → DeepSeek → response)
6. Patient summary layout
7. Draft 2–4 PGMRs
8. Submit to RRC

Proceed leisurely. Research everything broadly and in depth. Spawn new nodes
for any emerging gap. Produce 2–4 PGMRs per major deliverable. Never rush.
```

### Contract SDA-3.2: Per-Disease Dashboards

```
TEAM CONTRACT — U-HIEF v4
Issuer: SDA-3 Lead Architect
Recipient: RES + FD-FPRE Swarm — Disease Dashboard Team
Scope: Design the per-disease dashboard system: reusable template (header,
highlighted ECG, explanation panel, evidence panel), specific dashboards for
STEMI (by territory), arrhythmias, conduction disorders, structural
abnormalities, and special patterns (Wellens, de Winter, Brugada, long QT,
hyperkalemia). Each dashboard uses arrows, highlights, and color-coded
overlays with simple clinician-language explanations.

Deliverables:
1. FD-FPRE: Color-coded medical dashboard design principles
2. Reusable dashboard template design (5 components)
3. Specific dashboard designs for each condition category
4. Clinician-language explanation templates
5. Evidence panel design (RAG citation display)
6. Draft 2–4 PGMRs
7. Submit to RRC

Proceed leisurely. Research everything broadly and in depth. Spawn new nodes
for any emerging gap. Produce 2–4 PGMRs per major deliverable. Never rush.
```

### Contract SDA-3.3: ER Optimization

```
TEAM CONTRACT — U-HIEF v4
Issuer: SDA-3 Lead Architect
Recipient: RES + FD-FPRE Swarm — ER Optimization Team
Scope: ER-specific UI optimization: glanceability (one-glance STAT/CRITICAL/
NORMAL), cognitive load reduction, color-blind accessibility (WCAG 2.1 AAA),
touch/motor accessibility (44px+ targets, no hover-only), alert design
(STAT alerts, fatigue prevention, acknowledgment workflow).

Deliverables:
1. FD-FPRE: Cognitive load theory for medical dashboards
2. FD-FPRE: Color vision deficiency — accessible palette design
3. Glanceability specification (what's visible in ≤3 seconds)
4. Traffic-light system design with redundant encoding
5. STAT alert protocol (visual, position, acknowledgment)
6. Accessibility audit checklist
7. Draft 2–4 PGMRs
8. Submit to RRC

Proceed leisurely. Research everything broadly and in depth. Spawn new nodes
for any emerging gap. Produce 2–4 PGMRs per major deliverable. Never rush.
```

### Contract SDA-3.4: Cardiologist Extension

```
TEAM CONTRACT — U-HIEF v4
Issuer: SDA-3 Lead Architect
Recipient: RES + FD-FPRE Swarm — Cardiology UI Team
Scope: Design extended views for cardiologists: beat-by-beat comparison,
lead-by-lead detail, morphology comparison with textbook, trend views,
full agent reasoning chain viewer, confidence breakdown, evidence trail,
comparison mode, and report generation with "AI-GENERATED" label.

Deliverables:
1. FD-FPRE: Cardiologist ECG reading workflow and information needs
2. Deep analysis view designs (beat, lead, morphology, trend)
3. Reasoning chain viewer (XAI interface)
4. Comparison mode design
5. Report generation and export
6. Draft 2–4 PGMRs
7. Submit to RRC

Proceed leisurely. Research everything broadly and in depth. Spawn new nodes
for any emerging gap. Produce 2–4 PGMRs per major deliverable. Never rush.
```

### Contract SDA-3.5: Frontend Architecture

```
TEAM CONTRACT — U-HIEF v4
Issuer: SDA-3 Lead Architect
Recipient: RES + FD-FPRE Swarm — Frontend Architecture Team
Scope: Design the Next.js 14 application architecture: routing, component
structure, state management, API layer, D3.js rendering engine (SVG vs
Canvas), responsive design, and performance targets.

Deliverables:
1. FD-FPRE: Next.js 14 app router best practices for data-heavy medical UIs
2. Component architecture design (atomic design)
3. D3.js rendering engine design (performance for 12-lead ECG)
4. State management strategy
5. Performance budget and optimization plan
6. Draft 2–4 PGMRs
7. Submit to RRC

Proceed leisurely. Research everything broadly and in depth. Spawn new nodes
for any emerging gap. Produce 2–4 PGMRs per major deliverable. Never rush.
```

### Contract SDA-3.6: Medical Dashboard Design FD-FPRE

```
TEAM CONTRACT — U-HIEF v4
Issuer: SDA-3 Lead Architect
Recipient: RES + FD-FPRE Swarm — Design Research Team
Scope: Foundational research on medical dashboard design from first principles:
human visual perception, pre-attentive processing, medical informatics,
clinical decision support interface design (2024–2026 SOTA).

Deliverables:
1. FD-FPRE: Human visual perception for data comprehension
2. FD-FPRE: Pre-attentive visual processing (<200ms perception)
3. FD-FPRE: Medical informatics CDS interface design literature survey
4. Design principles document derived from research
5. Draft 2–4 PGMRs
6. Submit to RRC

Proceed leisurely. Research everything broadly and in depth. Spawn new nodes
for any emerging gap. Produce 2–4 PGMRs per major deliverable. Never rush.
```

---

**SDA-3 Tree: 6 first-level nodes, 26 second-level nodes, ~80 leaf nodes. Expected PGMRs: 10–14.**
