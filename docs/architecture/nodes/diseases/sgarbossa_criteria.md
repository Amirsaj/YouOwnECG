# Sgarbossa / Smith-Modified Sgarbossa Criteria — ECG Manifestation from First Principles

**Node:** 2.7.66
**SDA:** SDA-2 (Diagnosis & Agentic Core) — shared resource for SDA-1, SDA-3, SDA-4
**Status:** Research Complete
**PGMR:** Required
**Date:** 2026-03-27

---

## 1. Pathophysiology Root Cause

### 1.1 What Goes Wrong (Anatomy/Physiology)

- Left bundle branch block (LBBB) disrupts normal ventricular depolarization: the right ventricle activates first via the intact right bundle, then activation spreads slowly across the septum and into the left ventricle via cell-to-cell conduction rather than the fast conduction system
- This abnormal depolarization sequence generates a repolarization response that is the mirror image of the abnormal depolarization: wherever the QRS terminal forces are positive (toward a lead), the ST segment and T-wave will be negative — and vice versa. This is called "secondary" or "appropriate discordance"
- The fundamental principle: in LBBB, the ST-T vector is always discordant (opposite) to the terminal QRS vector. This is a passive electrical consequence of the abnormal activation front, not ischemia
- When acute MI superimposes an additional injury current on top of the LBBB baseline, the ST segment is pushed further in the direction of the injury — either making a discordant change "more discordant than expected" or, critically, reversing the direction entirely to become concordant with the QRS
- This is the core diagnostic challenge: the normal LBBB pattern includes ST changes that would meet STEMI criteria in a normal QRS — you cannot simply look for ST elevation. You must ask whether the ST change is appropriate to the LBBB or excessive/discordant in the wrong direction

### 1.2 Electrical Consequence

- In LBBB with a predominantly positive QRS (e.g., I, aVL, V5, V6 — the leads that see the delayed leftward final activation), the terminal QRS forces are positive → secondary ST segment will be negative (ST depression + T-wave inversion)
- In LBBB with a predominantly negative QRS (e.g., V1, V2 — leads that see the initial rightward forces but not the delayed left), the terminal QRS forces are negative → secondary ST segment will be positive (ST elevation)
- This means V1 and V2 naturally have ST elevation in LBBB — this elevation is expected and is NOT a sign of STEMI
- STEMI superimposed on LBBB creates an additional injury current (the current of injury) that disturbs this expected pattern in one of two ways:
  1. **Concordant changes**: The injury current is strong enough to flip the ST direction so it is now in the SAME direction as the QRS — concordant elevation in a positive QRS lead, or concordant depression in a negative QRS lead. Because the secondary ST-T would naturally oppose the QRS, any concordant change means the injury current has completely overpowered the LBBB baseline — this is extremely specific for infarction
  2. **Excessively discordant changes**: The injury current ADDS to the natural discordant ST elevation (in leads with negative QRS like V1-V2), making it disproportionately large. The expected discordant ST elevation in V1-V2 may be 1-2mm — if it reaches 5mm or represents >25% of the preceding S-wave, the excess is attributed to the superimposed injury current

### 1.3 Why It Appears on ECG

- Elena Sgarbossa published the criteria in 1996 using data from the GUSTO-I trial (17,000 patients with acute MI, subset with LBBB — n=131 with LBBB and confirmed acute MI matched against controls)
- She identified three independent predictors of acute MI in the presence of LBBB, each assigned a weighted score
- The Smith-Modified criteria (2012, Stephen Smith MD) replaced the absolute 5mm threshold for criterion 3 with a ratio-based approach (ST/S ratio), recognizing that a 5mm elevation is excessively discordant in a patient with a small S-wave (3mm S-wave + 5mm elevation = 167% ratio, clearly excessive) but may be within normal variation for a patient with a very deep S-wave (20mm S-wave + 5mm elevation = 25% ratio, marginally excessive)
- The ratio approach normalizes criterion 3 to QRS amplitude and substantially improves sensitivity (36% → 91%) with comparable specificity

---

## 2. ECG Presentation — Lead by Lead

### 2.1 Diagnostic Criteria (2025 AHA/ESC Guidelines)

#### Original Sgarbossa Criteria (1996) — Scoring System

| Criterion | Threshold | Score | Specificity | Sensitivity |
|-----------|-----------|-------|-------------|-------------|
| **Criterion 1**: Concordant ST elevation | ≥1mm in ≥1 lead where QRS is predominantly positive | 5 points | ~98% | ~18% |
| **Criterion 2**: Concordant ST depression | ≥1mm in V1, V2, or V3 | 3 points | ~94% | ~23% |
| **Criterion 3 (original)**: Excessively discordant ST elevation | ≥5mm absolute in leads where QRS is predominantly negative | 2 points | ~82% | ~53% |
| **Total score ≥3** | Any combination reaching threshold | — | ~96% | ~36% |

**Criterion 1 is the most powerful single finding**: Concordant ST elevation ≥1mm in a lead with a predominantly positive QRS is virtually diagnostic of STEMI (~98% specific). No scoring needed — treat as STEMI.

#### Smith-Modified Criterion 3 (2012) — Replaces Absolute 5mm Threshold

| Parameter | Formula | Threshold | Interpretation |
|-----------|---------|-----------|----------------|
| ST/S ratio | \|ST deviation (mm)\| ÷ \|S-wave depth (mm)\| in same lead | ≥ 0.25 | Excessively discordant → STEMI |
| Alternative expression | \|ST elevation\| / \|preceding S-wave\| | ≥ 25% | Same criterion, percentage form |
| Example A | S-wave = 8mm, ST elevation = 3mm → ratio = 0.375 | Positive | Excessive discordance |
| Example B | S-wave = 20mm, ST elevation = 4mm → ratio = 0.20 | Negative | Within acceptable discordance |
| Example C | S-wave = 4mm, ST elevation = 2mm → ratio = 0.50 | Positive | Excessive discordance despite small absolute value |

**Smith-Modified performance**: Sensitivity ~91%, Specificity ~90% for criterion 3 alone. Overall Smith-Modified criteria (1+2+3-modified): sensitivity ~91%, specificity ~90%.

#### Application to Pacemaker Rhythms

The same three criteria apply identically to ventricular paced rhythms. Paced beats generate secondary ST-T discordance identical in principle to LBBB. The pacing spike precedes the wide QRS. Concordant changes or excessive discordance in paced rhythms should trigger the same cath lab activation pathway.

### 2.2 Lead-by-Lead Manifestation

**For each lead, the analysis requires two steps: (1) determine QRS predominance (positive vs. negative), then (2) assess ST direction and magnitude relative to that QRS.**

| Lead | Expected LBBB Baseline ST | What Concordance Means Here | Criterion 1 Applicable? | Criterion 3 Applicable? | Sensitivity for STEMI |
|------|--------------------------|----------------------------|------------------------|------------------------|----------------------|
| I | ST depression, T inversion (secondary to positive QRS) | ST elevation = concordant → STEMI | Yes | No | High (80%) |
| II | Variable — QRS usually positive; mild ST depression | ST elevation ≥1mm = concordant | Yes | No | Moderate (55%) |
| III | Variable — QRS often positive; mild ST depression | ST elevation ≥1mm = concordant | Yes | No | Moderate (45%) |
| aVR | ST elevation (QRS negative) — expected | ST depression = concordant → STEMI; ST elevation >5mm or ratio ≥0.25 = excessive discordance | No | Yes | Low (20%) |
| aVL | ST depression (QRS usually positive) | ST elevation = concordant → STEMI | Yes | No | Moderate (50%) |
| aVF | Variable; usually positive QRS with mild ST depression | ST elevation = concordant if QRS positive | Yes | No | Moderate (45%) |
| V1 | ST elevation expected (QRS predominantly negative — rS or QS) | ST depression = concordant → criterion 2 | No (criterion 2) | Yes (if elevation excessive) | Moderate (60%) |
| V2 | ST elevation expected (QRS predominantly negative) | ST depression = concordant → criterion 2 | No (criterion 2) | Yes (if elevation excessive) | High (75%) |
| V3 | ST elevation expected (QRS usually negative in LBBB) | ST depression = concordant → criterion 2; ST elevation excessive → criterion 3 | Borderline | Yes | High (70%) |
| V4 | Transition — may be positive or negative | If QRS positive: ST elevation = concordant | Yes (if QRS positive) | Yes (if QRS negative) | Moderate (50%) |
| V5 | ST depression, T inversion (QRS positive) | ST elevation = concordant → STEMI | Yes | No | High (65%) |
| V6 | ST depression, T inversion (QRS positive — broad R wave) | ST elevation = concordant → STEMI | Yes | No | High (70%) |

### 2.3 Key Leads

- **V1-V3**: Primary territory for Criterion 2 (concordant depression) and Criterion 3 (excessive discordant elevation). In LBBB, these leads have negative QRS and therefore ST elevation is expected — depression here is a strongly concordant signal
- **I, V5, V6, aVL**: Predominantly positive QRS in LBBB — these leads form the most important targets for Criterion 1 (concordant elevation). Any ST elevation in these leads is abnormal by definition in LBBB
- **V5 and V6** are the highest-yield leads for criterion 1 detection because the QRS is most reliably positive (broad, tall R-wave from left ventricular lateral activation)

### 2.4 Beat-by-Beat Considerations

- Sgarbossa analysis requires a consistent beat: avoid assessing criteria on aberrantly conducted beats, fusion beats, or beats with rate-dependent bundle branch aberrancy
- In LBBB with rapid ventricular rates, ST analysis is more reliable at slower rates where the QRS and ST segments are better separated
- In pacemaker rhythms: use paced beats only (P-wave-triggered paced QRS). Spontaneous narrow beats, if present, provide a window for direct STEMI assessment without Sgarbossa overlay
- If intermittent LBBB: assess ST during the LBBB beats using Sgarbossa; assess ST during narrow QRS beats using standard STEMI criteria

---

## 3. Morphology Details

### 3.1 QRS Morphology Prerequisites

- Confirm LBBB is present before applying Sgarbossa: QRS ≥120ms, broad notched R in I/V5/V6, absent septal q waves in I/V5/V6, delayed intrinsicoid deflection in V5-V6 (>60ms), rS or QS in V1
- If QRS is <120ms, criteria do not apply — use standard STEMI criteria
- Distinguish LBBB from LBBB-like patterns: WPW with left-sided accessory pathway can mimic LBBB. Confirm delta wave absence

### 3.2 ST Measurement Technique

- Measure ST deviation at the J-point (junction of QRS end and ST segment onset)
- In LBBB, the J-point may be slurred — measure at the point of inflection from the QRS slope into the ST segment
- Reference isoelectric line: the TP segment (end of T-wave to beginning of next P-wave) is most reliable; PR segment is acceptable if TP is obscured

### 3.3 S-Wave Measurement (for Criterion 3 / Smith-Modified)

- Measure from the isoelectric baseline to the nadir of the S-wave (deepest negative deflection in the QRS)
- Use the same lead in which you are measuring ST deviation
- If no S-wave is present (QS pattern): the ratio is not applicable for that lead; use the absolute criterion with caution, or default to criterion 1/2 evaluation
- The S-wave in V1-V2 is typically the deepest in LBBB (the initial septal forces are directed rightward, creating deep S-waves before the delayed left lateral activation)

### 3.4 Concordance vs. Discordance — Practical Determination

- Step 1: Identify the terminal QRS deflection in the lead of interest (the last portion of the QRS before the J-point)
- Step 2: Is the terminal QRS force positive (upward) or negative (downward)?
  - Positive terminal QRS → discordant ST is depression/T-inversion; concordant ST is elevation
  - Negative terminal QRS → discordant ST is elevation/positive T; concordant ST is depression
- Step 3: Apply the criterion based on direction and magnitude

### 3.5 T-Wave Morphology

- In LBBB, T-waves should be discordant with the terminal QRS — tall upright T in V1-V2 (negative QRS) and inverted T in V5-V6 (positive QRS)
- Concordant T-waves (e.g., upright T in V5-V6 or inverted T in V1-V2) should raise suspicion for ischemia even in the absence of clear ST elevation
- Terminal T-wave concordance without meeting formal ST criteria can be a soft sign — document and correlate with troponin and clinical context

### 3.6 PR Segment and P-Wave

- AV block may coexist with LBBB in anterior STEMI (septal involvement may damage AV node or His bundle)
- First-degree AV block with LBBB + chest pain has higher pre-test probability of LAD involvement
- New LBBB with chest pain is no longer per se a STEMI criterion (2013 ACC/AHA guideline update) — Sgarbossa criteria are required

### 3.7 Comparison to Prior ECG

- This is the highest-yield intervention: if a prior ECG exists showing the same LBBB without Sgarbossa criteria, any new concordant change or new excessive discordance is the most powerful signal available
- "New or presumably new LBBB" with chest pain in the pre-Sgarbossa era was a STEMI criterion — abandoned because it produced too many false cath lab activations (~50% false positive rate)
- The comparison requirement underscores the importance of rapid ECG retrieval from prior visits

---

## 4. Differential Diagnosis

### 4.1 Mimics

| Condition | How It Mimics Sgarbossa | Distinguishing Feature |
|-----------|------------------------|----------------------|
| Normal LBBB secondary changes | ST elevation in V1-V2, ST depression in V5-V6 | Expected magnitude; ratio <0.25; no concordant changes |
| LVH with strain | ST depression + T inversion in lateral leads | QRS not ≥120ms; strain pattern in context of LVH voltage; no LBBB morphology |
| Acute pericarditis with LBBB | Diffuse ST elevation | Saddle-shape; PR depression; no reciprocal changes; responds to NSAIDs |
| Hyperkalemia with LBBB-like QRS widening | Wide QRS, ST changes | Peaked T-waves; sine wave QRS at extreme levels; potassium context; no specific LBBB morphology |
| LBBB + demand ischemia (type 2 MI) | ST changes in LBBB | Clinical context: tachycardia, hypotension, anemia; ST changes may meet Sgarbossa but no culprit occlusion |
| Ventricular paced rhythm (non-ischemic) | Wide QRS, discordant ST | Expected discordant pattern; ratio <0.25; no concordant changes unless STEMI superimposed |
| Rate-related LBBB aberrancy | LBBB morphology at fast rate | Disappears at slower rates; no ischemic history; Sgarbossa still applies if chest pain present |
| Takotsubo cardiomyopathy with LBBB | Concordant ST changes possible | Echocardiographic apical ballooning; female, post-stress trigger; may not respond to heparin |

### 4.2 Coexisting Conditions

- **LBBB + RV STEMI**: Right-sided leads (V3R, V4R) should be obtained in all inferior STEMIs. LBBB does not prevent assessment of right-sided leads; same Sgarbossa logic applies
- **LBBB + posterior STEMI**: The posterior STEMI signal (ST depression V1-V3) may be masked by expected discordant ST elevation in LBBB. This is a critical pitfall — posterior STEMI in LBBB is the hardest combination to detect
- **LBBB + complete AV block**: The wide QRS with AV block may represent Mobitz II or complete block from septal infarction; urgent pacing consideration alongside cath lab activation
- **Intermittent LBBB**: Rate-related LBBB that appears at faster rates — look for Sgarbossa criteria in the LBBB beats and standard STEMI criteria in the narrow beats

---

## 5. STAT Classification

| Feature | Status |
|---------|--------|
| **STAT alert trigger** | YES — Sgarbossa-positive LBBB requires immediate cath lab activation |
| **Criterion 1 alone (concordant ST elevation ≥1mm)** | STAT — no scoring needed; treat as STEMI |
| **Criterion 2 alone (concordant ST depression V1-V3 ≥1mm)** | STAT — high specificity; treat as STEMI |
| **Criterion 3-modified alone (ratio ≥0.25)** | STAT — treat as STEMI |
| **Score ≥3 (original criteria)** | STAT — cath lab activation |
| **Score <3 but clinical suspicion high** | Urgent cardiology consultation; serial ECGs; troponin; do not dismiss |
| **New LBBB with chest pain, no Sgarbossa criteria** | NOT automatic STEMI equivalent; requires Sgarbossa evaluation; clinical judgment |
| **Pacemaker rhythm with Sgarbossa-positive changes** | STAT — same cath lab activation threshold |
| **Time to intervention target** | Door-to-balloon ≤90 minutes (ESC 2023) |

---

## 6. Reasoning Complexity Analysis

### 6.1 Reasoning Domains Required

1. **Conduction system anatomy**: Must understand LBBB — why the QRS is wide, why secondary ST-T changes occur, and what "expected" discordance looks like for each lead
2. **Lead orientation geometry**: Must know which leads have positive vs. negative QRS in LBBB and why this varies by patient (the LBBB QRS axis and morphology varies — not all leads are uniformly positive or negative)
3. **Quantitative ratio analysis**: Must measure S-wave depth and ST deviation accurately, then compute and threshold the ratio — this is a numerical reasoning step embedded within pattern recognition
4. **Concordance logic**: A two-step conditional — first determine QRS direction, then determine whether ST follows or opposes. Error in step 1 (misidentifying QRS direction) invalidates step 2
5. **Score aggregation**: Original Sgarbossa is a weighted scoring system — requires identifying all three criteria independently and summing
6. **Differential reasoning**: Must distinguish pathological concordance from normal LBBB secondary changes AND from LVH/strain/pericarditis/hyperkalemia in the same ECG
7. **Temporal context**: New vs. old LBBB changes the prior probability substantially; comparison ECG interpretation is a prerequisite for maximum accuracy
8. **Clinical correlation**: Sgarbossa criteria have a false negative rate (9% for Smith-Modified). Clinical pretest probability must enter the final decision

### 6.2 Feature Dependencies

- Sgarbossa analysis is impossible without first confirming LBBB — the entire framework is conditional on a prerequisite diagnosis
- Criterion 3 (Smith-Modified) is mathematically impossible to apply without valid S-wave measurement — if no S-wave is present or the S-wave is ambiguous, this criterion must be flagged as unevaluable
- Concordance determination requires per-lead QRS polarity classification — this must be done for all 12 leads independently before ST assessment, generating a 12-element vector of QRS polarities
- The ratio calculation requires clean fiducial detection: ECGdeli must accurately identify QRS offset (J-point) and S-wave nadir — noise or pacemaker artifacts can corrupt both measurements

### 6.3 Cross-Condition Interactions

- **[[stemi_anterior.md]]**: Sgarbossa-positive LBBB from LAD occlusion overlaps heavily with anterior STEMI territory. Concordant changes in I, V5, V6 indicate lateral LAD distribution; concordant changes in V1-V3 (criterion 2) indicate proximal LAD
- **[[stemi_equivalent_patterns.md]]**: Sgarbossa criteria are listed as STEMI equivalent pattern #7 in the master reference. This file is a direct input into that cross-cutting document
- **[[stemi_inferior.md]]**: LBBB + inferior STEMI may produce concordant changes in II, III, aVF. Sgarbossa applies with the same logic
- **[[reciprocal_changes.md]]**: Reciprocal changes in LBBB are difficult to identify because the expected discordant pattern already resembles reciprocal depression. Sgarbossa-positive LBBB may or may not show classic reciprocal patterns — their absence does not exclude STEMI in this context
- **[[complete_av_block.md]]**: Complete AV block with LBBB escape rhythm — same Sgarbossa principles apply to the escape rhythm QRS morphology
- **[[stemi_right_ventricular.md]]**: All inferior STEMIs with LBBB must prompt right-sided lead acquisition; Sgarbossa logic applies to right-sided leads as well

### 6.4 Reasoning Chain Sketch

```
INPUT: Wide QRS ECG + chest pain clinical context
  │
  ▼
STEP 1: QRS WIDTH ≥120ms?
  ├── No → LBBB not present → use standard STEMI criteria → EXIT Sgarbossa pathway
  └── Yes → Continue
  │
  ▼
STEP 2: Confirm LBBB morphology
  ├── Broad notched R in I, V5, V6
  ├── rS or QS in V1
  ├── Absent septal q in I, V5, V6
  └── If WPW delta wave suspected → FLAG and consult
  │
  ▼
STEP 3: For each of the 12 leads → classify QRS polarity
  └── Build polarity vector: [I: +, II: +, III: +/-, aVR: -, aVL: +/-, aVF: +/-,
      V1: -, V2: -, V3: +/-, V4: +/-, V5: +, V6: +]
  │
  ▼
STEP 4: CRITERION 1 — For each POSITIVE-QRS lead
  └── Is ST elevation ≥1mm? → YES → CONCORDANT → SCORE 5 → STEMI POSITIVE → STAT
  │
  ▼
STEP 5: CRITERION 2 — In V1, V2, V3 (negative QRS)
  └── Is ST depression ≥1mm? → YES → CONCORDANT → SCORE 3 → Add to total
  │
  ▼
STEP 6: CRITERION 3 (Smith-Modified) — For each NEGATIVE-QRS lead
  ├── Measure ST elevation magnitude (mm)
  ├── Measure S-wave depth (mm)
  ├── Compute ratio = |ST elevation| / |S-wave depth|
  └── Ratio ≥0.25? → YES → EXCESSIVE DISCORDANCE → SCORE 2 → Add to total
  │
  ▼
STEP 7: Evaluate total score
  ├── Score ≥3 → STEMI POSITIVE → STAT → Cath lab activation
  ├── Score 1-2 → Soft positive → Urgent cardiology; serial ECGs; troponin
  └── Score 0 → Sgarbossa negative → Clinical context; do not exclude MI on ECG alone
  │
  ▼
STEP 8: Compare to prior ECG
  └── Any NEW concordant changes vs. prior → Upgrade confidence regardless of absolute score
```

### 6.5 Confidence Anchors

- **Concordant ST elevation ≥1mm in any positive-QRS lead**: Near-certain STEMI (positive predictive value ~95%). This single finding overrides all uncertainty
- **ST/S ratio ≥0.50 in V1-V3**: High confidence excessive discordance; ratio this large is rarely within LBBB baseline variation
- **Two or more independent criteria positive simultaneously**: Confidence approaches certainty; probability of false positive <3%
- **Sgarbossa negative but patient has typical STEMI symptoms, new LBBB, and hemodynamic compromise**: Clinical override — activate cath lab. Sgarbossa sensitivity is not 100%
- **Sgarbossa negative with no prior ECG available**: Cannot confidently distinguish new from chronic LBBB; clinical context drives decision

### 6.6 Difficulty Score

| Dimension | Score (1–5) | Rationale |
|-----------|-------------|-----------|
| Signal clarity needed | 5 | Requires clean J-point identification, precise S-wave nadir measurement, and correct QRS polarity classification — all prone to noise corruption |
| Number of leads required | 5 | All 12 leads must be individually classified for QRS polarity before ST assessment; lead-specific analysis mandatory |
| Cross-domain reasoning | 5 | Requires simultaneous conduction anatomy, vector geometry, quantitative ratio math, differential diagnosis, and clinical context integration |
| Temporal pattern complexity | 4 | Prior ECG comparison is critical; new vs. chronic LBBB distinction substantially changes interpretation |
| Differential complexity | 4 | Multiple mimics (LVH strain, pericarditis, hyperkalemia, paced rhythm) can overlap; all require systematic exclusion |
| Rarity in PTB-XL | 3 | LBBB is common in PTB-XL; confirmed STEMI + LBBB cases exist but are less frequent than isolated LBBB |
| **Overall difficulty** | **4.5** | **Highest-complexity ischemia interpretation task — requires multi-step conditional logic, quantitative computation, and prior-ECG integration** |

---

## 6A. Agent Assignment

**Architecture:** Option E — 3 Parallel Phase 1 Specialists + 1 Sequential CDS (Node 2.1 Gate Passed 2026-03-27)

**Note:** Sgarbossa criteria is a reference/tool file, not a diagnostic entity. This section documents which agent APPLIES Sgarbossa criteria and under what trigger conditions, not which agent detects it as a standalone diagnosis.

| Agent | Role for Sgarbossa Criteria Application | Key Features Used |
|-------|--------------------------|-------------------|
| **RRC** (Rhythm/Rate/Conduction) | Trigger agent | Detects LBBB (QRS ≥120 ms, broad monophasic R in I/aVL/V5–V6, broad S in V1, QS pattern in V1–V3, discordant ST-T); emits cross_domain_hint to CDS when LBBB is confirmed; provides QRS morphology for concordance/discordance assessment |
| **IT** (Ischemia/Territory) | Detection agent | Detects ischemic ST changes in the context of LBBB; measures: concordant ST elevation ≥1 mm (ST elevation in same direction as QRS), concordant ST depression ≥1 mm in V1–V3, discordant ST elevation in leads with negative QRS deflection; flags all three Sgarbossa criteria features |
| **MR** (Morphology/Repolarization) | Supporting | QRS morphology in LBBB context (confirms LBBB pattern is complete); measures S-wave depth in leads with discordant ST elevation (for Smith-modified Sgarbossa: STE/S-wave ratio ≥0.25); assesses whether ST changes exceed expected LBBB repolarization abnormality |
| **CDS** (Cross-Domain Synthesis) | Application agent — APPLIES Sgarbossa criteria | Sgarbossa criteria are applied exclusively by CDS after RRC confirms LBBB AND IT detects ischemic-pattern ST changes; CDS calculates the original Sgarbossa score (concordant STE: 5 pts; concordant STD V1–V3: 3 pts; discordant STE >5 mm: 2 pts; ≥3 pts = positive) AND the Smith-modified criterion (STE/S-wave ratio ≥0.25 in any lead) |

### Primary Agent
**CDS** is the agent that applies Sgarbossa criteria — it is a cross-domain tool that requires RRC's LBBB confirmation AND IT's ischemic ST findings. Neither RRC nor IT can apply Sgarbossa alone.

### Cross-Domain Hints
- RRC emits `cross_domain_hint: "LBBB confirmed (QRS ≥120 ms with LBBB morphology) — Sgarbossa criteria application required if ischemic ST changes are present; forward LBBB confirmation to CDS"` when LBBB is detected.
- IT emits `cross_domain_hint: "Ischemic ST changes detected in the context of LBBB — concordant/discordant ST measurements forwarded to CDS for Sgarbossa scoring"` when ST changes are found alongside LBBB pattern.

### CDS Specific Role
CDS is the exclusive executor of Sgarbossa criteria. The trigger is: RRC confirms LBBB + IT reports any ischemic ST pattern. CDS then applies both scoring systems: (1) original Sgarbossa point score (≥3 points = positive for ischemia superimposed on LBBB, specificity ~90%); (2) Smith-modified Sgarbossa (any lead with STE/S-wave ratio ≥0.25 = positive, higher sensitivity). CDS generates a final LBBB+ischemia determination with the specific criteria met, the score, and the confidence level. A positive Sgarbossa result from CDS triggers the same urgency escalation as a confirmed STEMI.

---

## 7. RAG Knowledge Requirements

### 7.1 Required Textbook Sections

| Source | Section | Why Required |
|--------|---------|-------------|
| Chou's Electrocardiography in Clinical Practice (6th ed.) | Chapter on bundle branch blocks and STEMI recognition | Foundational LBBB physiology and secondary ST-T changes |
| Marriott's Practical Electrocardiography (12th ed.) | LBBB chapter; STEMI in conduction defects | Sgarbossa criteria explanation and clinical application |
| Goldberger's Clinical Electrocardiography (9th ed.) | Chapter 8 (LBBB); Chapter 9 (MI patterns) | Vector analysis of concordance; graphical examples |
| ECG Made Easy (5th ed.) | Bundle branch block chapter | Accessible concordance/discordance explanation for bedside teaching |

### 7.2 Guideline and Literature Requirements

| Reference | Content Needed | Priority |
|-----------|---------------|----------|
| Sgarbossa EB et al. NEJM 1996;334:481-7 | Original criteria derivation, scoring weights, sensitivity/specificity data | CRITICAL |
| Smith SW et al. Ann Emerg Med 2012;60:766-776 | Smith-Modified criterion 3 derivation; ratio threshold validation | CRITICAL |
| ESC 2023 Acute Coronary Syndromes Guidelines | Updated recommendations on LBBB + chest pain; cath lab activation criteria | CRITICAL |
| ACC/AHA 2013 STEMI Guideline update | Removal of "new LBBB" as automatic STEMI criterion; rationale | HIGH |
| Cai Q et al. Heart Rhythm 2013 | External validation of Smith-Modified criteria | HIGH |
| Meyers HP et al. J Electrocardiol 2015 | BARCELONA criteria comparison; proportionality approach variants | MODERATE |

---

## 8. Dashboard Visualization Specification

### 8.1 Primary Display

- **Lead group panel**: Display all 12 leads simultaneously with color-coded QRS polarity overlay: green highlight on leads with positive QRS (criterion 1 candidates), red highlight on V1-V3 (criterion 2 candidates), yellow highlight on negative-QRS leads (criterion 3 candidates)
- **Concordance indicator**: Per-lead badge showing "CONCORDANT / DISCORDANT / EXCESSIVE DISCORDANT" with numerical ST deviation measurement annotated on the ST segment
- **Score accumulator**: Running Sgarbossa score displayed as criteria are identified (0 → 3 → 5 → 8 maximum), with color progression: gray (0) → yellow (1-2) → orange (3-4) → red (≥5)
- **Ratio display**: For all negative-QRS leads, show ST/S ratio as a numerical overlay: "ST: 3.2mm / S: 8.1mm = ratio 0.39 ✓ POSITIVE"

### 8.2 Secondary Display

- **QRS polarity summary table**: 12-row table populated automatically from ECGdeli QRS analysis, showing lead, dominant direction, QRS amplitude, and applicable criterion
- **Smith-Modified formula box**: Persistent display of the ratio formula with the current lead's values plugged in, updating as the clinician scrolls between leads
- **Prior ECG comparison panel** (if available): Side-by-side display of current vs. prior ECG for the highest-yield leads (V1-V3, V5-V6, I), with ST deviation delta calculated automatically
- **Pacemaker flag**: If pacing spikes detected, display "PACED RHYTHM — Sgarbossa criteria applied to paced QRS" banner

### 8.3 Alert Logic

- **Criterion 1 alone**: Immediate STAT alert regardless of score — banner: "CONCORDANT ST ELEVATION IN LBBB — STEMI UNTIL PROVEN OTHERWISE"
- **Score ≥3**: STAT alert with cath lab activation recommendation
- **Score 1-2**: Elevated alert — "Sgarbossa indeterminate — urgent cardiology consultation required"
- **Ratio 0.20-0.24** (near threshold): Soft alert — "ST/S ratio approaching threshold — obtain serial ECG in 15 minutes"

---

## 9. Edge Cases and Pitfalls

- **The most dangerous pitfall**: Dismissing ST elevation in V1-V2 in LBBB as "just LBBB changes" — this is correct for DISCORDANT elevation, but must be examined for excessive discordance (criterion 3). Many false negatives arise from this error
- **Posterior STEMI in LBBB**: Posterior STEMI produces ST depression in V1-V3. In LBBB, this depression may be misidentified as concordant (criterion 2 positive) OR may be masked because the expected discordant ST elevation already "fills in" the posterior injury signal — this combination is extremely difficult to detect and requires V7-V9 leads
- **Septal Q-wave confusion**: LBBB eliminates septal Q-waves in I/V5/V6. If Q-waves ARE present in these leads despite LBBB morphology, consider anteroseptal infarction with LBBB — the absence of septal Q-waves is so reliable that their presence is a red flag
- **Variable QRS morphology in LBBB**: The QRS polarity in V3-V4 and aVL is not always predictable — some patients have a negative QRS in aVL despite LBBB. Per-lead polarity classification is mandatory; never assume polarity without examining the actual waveform
- **Rate-related LBBB (phase 3 aberrancy)**: Appears at faster rates, disappears at slower rates. Sgarbossa criteria can still be applied to the LBBB beats. If applying criteria: look for rate-independent persistence of the ST changes (changes that persist at normal rates suggest pathology)
- **Hyperkalemia masquerading as LBBB**: Wide QRS from hyperkalemia may be mistaken for LBBB. The peaked T-waves of hyperkalemia in conjunction with widened QRS can superficially meet some ST criteria. Always check electrolytes in wide QRS with ST changes
- **Sensitivity ceiling of Smith-Modified**: Even Smith-Modified criteria miss ~9% of STEMI in LBBB. A Sgarbossa-negative ECG does not exclude MI — clinical pretest probability, troponin kinetics, and serial ECGs are mandatory complements
- **The "concordant T-wave" phenomenon**: Even without formal ST criteria, a concordant T-wave (upright T in V5-V6 or inverted T in V1-V2) that is clearly out of proportion to the expected LBBB pattern represents a soft Sgarbossa signal — escalate accordingly

---

## 10. References

1. Sgarbossa EB, Pinski SL, Barbagelata A, et al. Electrocardiographic diagnosis of evolving acute myocardial infarction in the presence of left bundle-branch block. *N Engl J Med.* 1996;334(8):481–487.
2. Smith SW, Dodd KW, Henry TD, Dvorak DM, Pearce LA. Diagnosis of ST-elevation myocardial infarction in the presence of left bundle branch block with the ST-elevation to S-wave ratio in a modified Sgarbossa rule. *Ann Emerg Med.* 2012;60(6):766–776.
3. Ibanez B, James S, Agewall S, et al. 2017 ESC Guidelines for the management of acute myocardial infarction in patients presenting with ST-segment elevation. *Eur Heart J.* 2018;39(2):119–177.
4. O'Gara PT, Kushner FG, Ascheim DD, et al. 2013 ACCF/AHA guideline for the management of ST-elevation myocardial infarction. *J Am Coll Cardiol.* 2013;61(4):e78–e140.
5. Cai Q, Mehta N, Sgarbossa EB, et al. The left bundle-branch block puzzle in the 2013 ST-elevation myocardial infarction guideline. *Am Heart J.* 2013;166(3):409–413.
6. Meyers HP, Limkakeng AT Jr, Jaffa EJ, et al. Validation of the modified Sgarbossa criteria for acute coronary occlusion in the setting of left bundle branch block: a retrospective case-control study. *J Electrocardiol.* 2015;48(6):929–934.
7. Goldberger AL, Goldberger ZD, Shvilkin A. *Goldberger's Clinical Electrocardiography: A Simplified Approach.* 9th ed. Philadelphia: Elsevier; 2018.
8. Surawicz B, Knilans TK. *Chou's Electrocardiography in Clinical Practice.* 6th ed. Philadelphia: Saunders; 2008.
9. Wagner GS, Marriott HJL. *Marriott's Practical Electrocardiography.* 12th ed. Philadelphia: Lippincott Williams & Wilkins; 2013.
