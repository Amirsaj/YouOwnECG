# [Disease/Condition Name] — ECG Manifestation from First Principles

**Node:** 2.7.X
**SDA:** SDA-2 (Diagnosis & Agentic Core) — shared resource for SDA-1, SDA-3, SDA-4
**Status:** Pending
**PGMR:** Required
**Date:** YYYY-MM-DD

---

## 1. Pathophysiology Root Cause

### 1.1 What Goes Wrong (Anatomy/Physiology)
- The underlying structural, electrical, or metabolic defect
- Which part of the heart is affected (atria, AV node, His-Purkinje, ventricles, pericardium)
- The mechanism at cellular level (ion channel, ischemia, pressure overload, etc.)

### 1.2 Electrical Consequence
- How the defect alters the cardiac action potential
- How it changes depolarization and/or repolarization vectors
- Which phase of the cardiac cycle is affected (P-wave, PR, QRS, ST, T, QT)

### 1.3 Why It Appears on ECG
- The altered electrical vector → how it projects onto each lead
- Why specific leads show specific changes (dipole theory + lead orientation)

---

## 2. ECG Presentation — Lead by Lead

### 2.1 Diagnostic Criteria (2025 AHA/ESC Guidelines)

| Criterion | Threshold | Source |
|-----------|-----------|--------|
| ... | ... | ... |

### 2.2 Lead-by-Lead Manifestation

| Lead | Expected Finding | Why (Vector Explanation) | Sensitivity |
|------|-----------------|------------------------|-------------|
| I | ... | ... | ... |
| II | ... | ... | ... |
| III | ... | ... | ... |
| aVR | ... | ... | ... |
| aVL | ... | ... | ... |
| aVF | ... | ... | ... |
| V1 | ... | ... | ... |
| V2 | ... | ... | ... |
| V3 | ... | ... | ... |
| V4 | ... | ... | ... |
| V5 | ... | ... | ... |
| V6 | ... | ... | ... |

### 2.3 Key Leads (Most Diagnostic)
- Which leads are most sensitive/specific for this condition
- Which leads show the earliest changes
- Which leads show reciprocal changes (if applicable)

### 2.4 Beat-by-Beat Considerations
- Is this condition constant across all beats or intermittent?
- Beat-to-beat variability expected?
- Which beats are most diagnostic? (e.g., after a pause, during tachycardia)

---

## 3. Morphology Details (What the Agent Must See)

### 3.1 P-wave Changes
- Morphology: normal / peaked / notched / biphasic / absent / flutter waves / fibrillatory
- Duration change: prolonged / shortened / normal
- Axis change: normal / abnormal / variable

### 3.2 PR Interval Changes
- Duration: prolonged / shortened / variable / absent
- Pattern: constant / progressive / dropped beats

### 3.3 QRS Complex Changes
- Duration: narrow / wide / borderline
- Morphology: rSR' / QS / delta wave / notching / slurring
- Amplitude: increased / decreased / normal
- Axis: normal / LAD / RAD / extreme

### 3.4 ST Segment Changes
- Direction: elevation / depression / normal
- Morphology: concave / convex / horizontal / downsloping / upsloping
- Measurement point: J-point / J+60ms / J+80ms
- Gender/lead-specific thresholds (if applicable)

### 3.5 T-wave Changes
- Direction: upright / inverted / biphasic / flattened
- Amplitude: tall/peaked / normal / low
- Symmetry: symmetric / asymmetric
- Specific patterns: Wellens Type A/B, hyperacute, strain pattern

### 3.6 QT/QTc Changes
- Prolonged / shortened / normal
- Clinical significance threshold
- Torsades de Pointes risk

### 3.7 Other Features
- U-waves, Osborn waves, epsilon waves, delta waves
- Any condition-specific morphological markers

---

## 4. Differential Diagnosis

### 4.1 Mimics (What Looks Like This But Isn't)

| Mimic Condition | Shared Features | Distinguishing Features |
|----------------|-----------------|----------------------|
| ... | ... | ... |

### 4.2 Coexisting Conditions
- What other conditions commonly coexist and may confuse the picture
- How to identify this condition DESPITE confounders (e.g., STEMI + LBBB → Sgarbossa)

---

## 5. STAT Classification

| Priority | Criteria |
|----------|----------|
| **STAT** | [Is this a STAT condition? Why?] |
| **Time-sensitive** | [How quickly must this be identified?] |
| **Clinical action** | [What does the ER team do when this is found?] |

---

## 6. Reasoning Complexity Analysis (Feeds Into Node 2.1 — Agent Architecture Research)

> **NOTE**: This section does NOT pre-assign agents. It documents the reasoning
> complexity of this condition so that Node 2.1 can determine the BEST agent
> architecture to handle ALL conditions. The actual agent assignment is filled
> in AFTER Node 2.1 research completes.

### 6.1 Reasoning Domains Required to Detect This Condition
- Which types of reasoning are needed? (rate analysis, rhythm regularity, interval measurement, morphology comparison, voltage criteria, axis calculation, lead-group correlation, temporal pattern, metabolic context, etc.)
- Does detection require cross-domain reasoning? (e.g., Wellens needs BOTH morphology + ischemia context)
- Does it require sequential reasoning? (e.g., "IF LBBB THEN apply Sgarbossa criteria")

### 6.2 Feature Dependencies
- What computed features (from SDA-1) are ESSENTIAL to detect this condition?
- What features are SUPPORTING (increase confidence but not required)?
- What features, if abnormal, should EXCLUDE this condition?
- What features require per-beat analysis vs aggregate analysis?

### 6.3 Cross-Condition Interactions
- Does this condition affect how OTHER conditions present? (e.g., LBBB masks STEMI)
- Does detecting this condition require ruling out others first? (differential)
- Are there condition combinations that change the interpretation? (e.g., AFib + WPW = danger)

### 6.4 Reasoning Chain Sketch
- Step-by-step: what observations lead to this diagnosis?
- What is the minimum reasoning chain? (fewest steps to high confidence)
- What is the full reasoning chain? (complete evidence assembly)

### 6.5 Confidence Anchors
- What features, if present, give HIGH confidence?
- What features, if absent, should LOWER confidence?
- What combination is pathognomonic (near-100% specific)?
- What is the minimum evidence for a "possible" vs "probable" vs "definite" classification?

### 6.6 Difficulty Score
| Dimension | Score (1-5) | Notes |
|-----------|-------------|-------|
| Signal clarity needed | ... | How clean must the signal be? |
| Number of leads required | ... | Can it be detected from subset of leads? |
| Cross-domain reasoning | ... | How many reasoning domains involved? |
| Temporal pattern complexity | ... | Beat-to-beat vs constant vs progressive? |
| Differential complexity | ... | How many mimics must be excluded? |
| Rarity in PTB-XL | ... | How many examples available for validation? |
| **Overall difficulty** | **...** | **Average — informs agent workload balancing** |

---

## 6A. Agent Assignment (FILLED AFTER Node 2.1 Research Completes)

> **STATUS**: Pending — awaiting Node 2.1 "Agent Architecture Research" gate passage.
> The architecture (number of agents, specializations, communication patterns)
> must be determined by research, not assumed.

| Agent (TBD) | Role for This Condition | Key Features Used |
|-------------|------------------------|-------------------|
| *To be determined by Node 2.1 research* | ... | ... |

### Which Agent is Primary?
*Pending Node 2.1 completion*

### Multi-Agent Collaboration Required?
*Pending — does this condition need multiple agents working together?*

---

## 7. RAG Knowledge Requirements

### 7.1 Textbook References
- Which of the 4 books covers this condition best?
- Key chapters/pages/figures for RAG retrieval

### 7.2 Key Figures
- Reference ECG figures from textbooks for this condition
- What should the per-disease dashboard show as "textbook example"?

---

## 8. Dashboard Visualization Specification

### 8.1 Highlighted Leads
- Which leads to emphasize on the per-disease dashboard
- Color coding for abnormal segments

### 8.2 Arrows and Annotations
- Where do arrows point? (specific morphological features)
- What labels appear on the highlighted segments?

### 8.3 Clinician Explanation (Plain Language)
- The 2-3 sentence explanation for ER nurse
- The expanded explanation for cardiologist

---

## 9. Edge Cases and Pitfalls

- Atypical presentations
- Age/sex/demographic variations
- Technical artifacts that mimic this condition
- When this condition is masked by another (e.g., STEMI masked by LBBB)

---

## 10. References
- AHA/ESC guideline citations
- Key papers (2024–2026)
- Textbook chapter references
