# Atrial Fibrillation — ECG Manifestation from First Principles

**Node:** 2.7.24
**SDA:** SDA-2 (Diagnosis & Agentic Core) — shared resource for SDA-1, SDA-3, SDA-4
**Status:** Complete
**PGMR:** Required
**Date:** 2026-03-26

---

## 1. Pathophysiology Root Cause

### 1.1 What Goes Wrong (Anatomy/Physiology)
- Two competing mechanisms drive atrial fibrillation (AFib):
  1. **Multiple re-entrant wavelets**: Structural and electrical remodeling of the atrial myocardium (fibrosis, dilation, heterogeneous refractory periods) creates a substrate where 4–6+ independent wavelet circuits propagate simultaneously across both atria. Each wavelet depolarizes a small region, extinguishes, and re-initiates from another region, sustaining the arrhythmia.
  2. **Focal triggers**: Ectopic foci — most commonly arising from the myocardial sleeves extending into the pulmonary veins (especially the left superior PV) — fire rapidly at 350–600 impulses/min. These foci have short refractory periods and automaticity driven by DADs (delayed afterdepolarizations) or micro-reentry.
- The atria become electrically chaotic: no organized atrial contraction occurs. Atrial transport function is lost (15–25% of cardiac output in normal hearts, more in diastolic dysfunction).
- The AV node acts as a gatekeeper: it cannot conduct at 350–600/min. It conducts impulses variably based on its own refractory period (concealed conduction — some impulses penetrate the AV node partially, resetting its refractory period without producing a QRS). This creates the irregularly irregular ventricular response.

### 1.2 Electrical Consequence
- **No organized atrial depolarization vector**: Instead of a single P-wave vector (SA node → right atrium → left atrium), hundreds of tiny depolarization wavelets fire in random directions simultaneously. These sum to a chaotic, low-amplitude, high-frequency oscillation of the baseline (fibrillatory waves, or f-waves).
- **Variable AV conduction**: Each atrial impulse arrives at the AV node at a different point in its recovery cycle. Some conduct, most are blocked or concealed. The result: unpredictable, variable RR intervals with no pattern.
- **QRS is unaffected** (unless pre-existing BBB or rate-related aberrant conduction): The His-Purkinje system is intact. Once an impulse traverses the AV node, ventricular depolarization proceeds normally.
- **Repolarization (ST/T)**: Baseline may be affected by the fibrillatory waves superimposed on ST segments and T-waves, but the fundamental ventricular repolarization is unchanged unless rate-related ischemia occurs.

### 1.3 Why It Appears on ECG
- **Absent P-waves**: The summation of hundreds of small, randomly directed atrial depolarization vectors cancels most activity. What remains is a chaotic, undulating baseline — f-waves at 350–600/min with amplitudes typically <0.5 mm. No discrete, reproducible P-wave can be identified before any QRS.
- **Best seen in V1**: V1 is positioned directly over the right atrium (anterior chest, right parasternal). It records atrial electrical activity with highest amplitude. Fine vs coarse fibrillatory waves are best assessed here.
- **Irregularly irregular RR intervals**: Because AV nodal conduction is random (influenced by concealed conduction, autonomic tone, medications), the interval between consecutive R-waves has no repeating pattern. This is the single most diagnostic feature and can be detected computationally by analyzing RR interval variance.
- **Each lead "sees" the same chaos** from its own angle — but all leads share the three hallmarks: no P-waves, irregular RR intervals, and (usually) narrow QRS.

---

## 2. ECG Presentation — Lead by Lead

### 2.1 Diagnostic Criteria (2025 AHA/ACC/HRS Guidelines)

| Criterion | Threshold | Source |
|-----------|-----------|--------|
| Absence of discrete P-waves | No reproducible P-wave morphology preceding QRS complexes | 2023 ACC/AHA/ACCP/HRS AFib Guideline; reaffirmed 2025 |
| Fibrillatory baseline | Irregular oscillations, 350–600/min; may be fine (<0.5 mm) or coarse (≥0.5 mm) | ESC 2024 AFib Guidelines |
| Irregularly irregular RR intervals | No repeating RR pattern; coefficient of variation of RR intervals typically >10% | ACC/AHA 2023 |
| Episode duration | ≥30 seconds of continuous AFib on ECG or full 10-second strip showing AFib | ACC/AHA 2023 |
| QRS duration | Typically <120 ms (narrow); wide QRS suggests concurrent BBB or aberrancy | Standard ECG criteria |
| Ventricular rate classification | RVR: >100 bpm; controlled: 60–100 bpm; slow: <60 bpm | ACC/AHA 2023 |

### 2.2 Lead-by-Lead Manifestation

| Lead | Expected Finding | Why (Vector Explanation) | Sensitivity |
|------|-----------------|------------------------|-------------|
| I | Absent P-waves; irregular RR; fibrillatory baseline often subtle | Lateral lead — atrial chaos projects weakly along 0° axis; f-waves low amplitude | Moderate for f-waves; high for RR irregularity |
| II | Absent P-waves; irregular RR; fibrillatory baseline usually visible | Inferior lead at +60° — normally best for P-waves, so their absence is conspicuous here; moderate f-wave amplitude | High — best rhythm assessment lead; absence of P-waves most apparent where they should be largest |
| III | Absent P-waves; irregular RR; f-waves may be visible | Inferior lead at +120° — smaller f-wave amplitude than II | Moderate |
| aVR | Absent P-waves; inverted fibrillatory baseline; irregular RR | Rightward-superior lead (-150°) — records atrial activity in opposite direction; f-waves may appear inverted | Low for f-waves; moderate for rhythm |
| aVL | Absent P-waves; irregular RR; f-waves usually low amplitude | Lateral lead at -30° — atrial vectors project weakly | Low for f-waves; high for RR irregularity |
| aVF | Absent P-waves; irregular RR; fibrillatory baseline visible | Inferior lead at +90° — good for atrial activity detection; f-waves moderate amplitude | High for rhythm; moderate for f-waves |
| V1 | **Best lead for f-waves**; coarse or fine fibrillatory baseline clearly visible; absent discrete P-waves; irregular RR | V1 sits directly over the right atrium (4th ICS, right sternal border). Atrial vectors project maximally here. F-waves often 0.5–1.5 mm amplitude | **Highest** — most sensitive lead for detecting fibrillatory waves and distinguishing fine vs coarse AFib |
| V2 | F-waves visible but lower amplitude than V1; absent P-waves; irregular RR | Adjacent to V1 but slightly more ventricular tissue overlap; atrial signals still reasonably strong | High |
| V3 | F-waves may be visible; absent P-waves; irregular RR | Transitional lead — atrial signal diminishes as ventricular signal increases | Moderate |
| V4 | F-waves often subtle or absent; irregular RR is main finding | Over LV apex — dominated by ventricular depolarization; atrial signals small | Low for f-waves; high for RR irregularity |
| V5 | F-waves rarely visible; irregular RR; absent P-waves inferred | Lateral precordial — atrial vectors project minimally | Low for f-waves; high for RR irregularity |
| V6 | F-waves rarely visible; irregular RR; absent P-waves inferred | Most lateral precordial — similar to V5 | Low for f-waves; high for RR irregularity |

### 2.3 Key Leads (Most Diagnostic)
- **V1**: Most sensitive for fibrillatory wave detection — always examine first for f-wave characterization (fine vs coarse). Fine AFib in V1 can distinguish from atrial flutter.
- **II**: Best rhythm strip lead — irregularly irregular RR intervals most apparent here. The absence of P-waves is most conspicuous in the lead where P-waves are normally tallest.
- **aVF**: Complementary inferior lead for rhythm assessment and f-wave detection.
- **V1 + II combination**: Sufficient for AFib diagnosis in >95% of cases.

### 2.4 Beat-by-Beat Considerations
- **ESSENTIAL for AFib**: Every single beat occurs at a different RR interval. This means:
  - Heart rate must be computed as an average over the full strip, not from a single RR interval
  - Rate-dependent features (QT interval, ST morphology, T-wave amplitude) vary beat to beat
  - Ashman phenomenon: a long-short RR cycle sequence can cause aberrant conduction (RBBB morphology) on the beat following the short cycle — mimics PVCs
  - Long pauses may trigger escape beats (junctional or ventricular)
- **Beat-to-beat variability is diagnostic**: A coefficient of variation (CV) of RR intervals >10–15% strongly suggests AFib. Regular rhythms have CV <5%.
- **Most diagnostic beats**: The fibrillatory baseline is best assessed in the longest RR intervals (more baseline visible between QRS complexes). Short RR intervals may obscure f-waves.
- **Per-beat feature extraction**: For AFib, the system must extract RR intervals for every beat and compute aggregate statistics (mean, SD, CV, histogram shape) rather than relying on any single beat.

---

## 3. Morphology Details (What the Agent Must See)

### 3.1 P-wave Changes
- **Morphology**: Absent — replaced by fibrillatory waves (f-waves). F-waves are chaotic, irregular oscillations of the baseline with no consistent morphology, amplitude, or timing.
  - **Fine AFib**: f-wave amplitude <0.5 mm, baseline appears nearly flat or minimally undulating — can be mistaken for sinus rhythm with absent P-waves
  - **Coarse AFib**: f-wave amplitude ≥0.5 mm, prominent irregular oscillations — can be mistaken for atrial flutter
- **Duration change**: Not applicable — no discrete P-waves to measure
- **Axis change**: No consistent P-wave axis — atrial depolarization is multidirectional and chaotic

### 3.2 PR Interval Changes
- **Duration**: Not measurable — there is no identifiable P-wave onset to define a PR interval
- **Pattern**: No PR interval exists; any apparent "PR" relationship is coincidental

### 3.3 QRS Complex Changes
- **Duration**: Narrow (<120 ms) in uncomplicated AFib. Wide QRS occurs with:
  - Pre-existing BBB (LBBB or RBBB)
  - Rate-related aberrancy (Ashman phenomenon — RBBB pattern after long-short cycles)
  - Pre-excited AFib (WPW — delta waves, very wide QRS, dangerous)
  - Hyperkalemia superimposed on AFib
- **Morphology**: Normal unless aberrancy or pre-excitation. No pathological Q-waves from AFib itself.
- **Amplitude**: Normal — AFib does not intrinsically alter QRS voltage
- **Axis**: Normal — AFib does not shift the QRS axis (axis abnormalities suggest coexisting ventricular pathology)

### 3.4 ST Segment Changes
- **Direction**: Normal at baseline. ST depression may occur with:
  - Rapid ventricular response (demand ischemia)
  - Digitalis effect (downsloping ST "scooping")
  - Underlying CAD unmasked by tachycardia
- **Morphology**: Baseline undulation from f-waves can be superimposed on ST segments, making ST analysis more difficult
- **Measurement point**: Use J-point + 60–80 ms as standard. Average ST measurements across multiple beats due to RR-dependent variation.
- **Critical note**: AFib does NOT invalidate ST elevation analysis — STEMI criteria still apply, though sensitivity may be reduced due to baseline wander and rate-related changes

### 3.5 T-wave Changes
- **Direction**: Normal in uncomplicated AFib; rate-related T-wave inversion may occur with persistent tachycardia (cardiac memory)
- **Amplitude**: May vary beat to beat due to varying RR intervals (shorter RR → smaller T-wave) and superimposed f-waves
- **Symmetry**: Normal unless coexisting ischemia
- **Specific patterns**: No AFib-specific T-wave pattern. T-wave changes should prompt evaluation for other pathology (ischemia, electrolyte abnormality).

### 3.6 QT/QTc Changes
- **QT measurement in AFib is challenging**: Each beat has a different RR interval, so QTc varies beat to beat.
- **Recommended approach**: Measure QT in at least 5–10 consecutive beats, use the Fridericia correction (QTcF = QT / RR^(1/3)) which is more accurate than Bazett at extreme rates, and report the average QTcF.
- **Alternative**: Use beats with RR intervals closest to 1000 ms (HR ~60) where correction formulas are most accurate.
- **Clinical significance**: QTc prolongation in AFib increases torsades risk, especially relevant when starting antiarrhythmics (sotalol, dofetilide, amiodarone).

### 3.7 Other Features
- **Fibrillatory waves (f-waves)**: The signature feature. Continuously varying, irregular oscillations best seen in V1. Frequency 350–600/min. Amplitude correlates roughly with atrial size (coarse f-waves → larger/less fibrotic atria; fine f-waves → smaller or more fibrotic atria).
- **No U-waves specific to AFib**: U-waves, if present, suggest hypokalemia or other cause.
- **Ashman beats**: Aberrantly conducted beats (RBBB morphology) following a long-short RR cycle — a hallmark of AFib physiology, not a separate arrhythmia. Distinguished from PVCs by: RBBB (not LBBB) morphology, preceding long-short cycle, no compensatory pause.

---

## 4. Differential Diagnosis

### 4.1 Mimics (What Looks Like This But Isn't)

| Mimic Condition | Shared Features | Distinguishing Features |
|----------------|-----------------|----------------------|
| Atrial flutter with variable block | Irregular RR intervals; may have obscured P-waves | Flutter waves are organized and regular (300/min sawtooth); RR intervals often cluster around ratios (2:1, 3:1, 4:1) rather than being truly random; V1 and inferior leads show discrete flutter waves |
| Multifocal atrial tachycardia (MAT) | Irregular rhythm; no single dominant P-wave morphology | MAT has ≥3 distinct P-wave morphologies that ARE identifiable; each P-wave precedes a QRS with a PR interval; rate usually 100–150 bpm; seen in COPD/hypoxia |
| Frequent PACs (premature atrial complexes) | May appear irregularly irregular; some P-waves look different | Most beats have normal sinus P-waves; PACs have identifiable (though abnormal) P-waves; the underlying rhythm is regular with premature beats interrupting it |
| Wandering atrial pacemaker | Variable P-wave morphology | P-waves ARE present (≥3 morphologies); rate typically <100; PR intervals vary but are measurable; rhythm is only mildly irregular |
| Motion artifact / tremor | Irregular baseline mimics f-waves; if severe, QRS timing hard to assess | Artifact affects ALL leads simultaneously and correlates with movement; QRS complexes remain regular underneath; artifact has non-physiological frequency (e.g., Parkinsonian tremor at 4–6 Hz) |
| Sinus rhythm with baseline wander | Undulating baseline mimics coarse f-waves | P-waves with consistent morphology are identifiable; RR intervals are regular; baseline wander is slow (respiratory rate, ~12–20/min) vs f-waves (350–600/min) |

### 4.2 Coexisting Conditions
- **AFib + LBBB**: Wide QRS (>120 ms) with LBBB morphology. The irregular rhythm confirms AFib (LBBB alone has regular rhythm). ST/T changes are secondary to LBBB, not ischemia — but Sgarbossa criteria still apply if STEMI is suspected.
- **AFib + RBBB**: Wide QRS with RBBB pattern. Must distinguish from Ashman phenomenon (transient RBBB in AFib). Persistent RBBB across all beats at all rates = true RBBB.
- **AFib + WPW (pre-excited AFib)**: CRITICAL DANGER. The accessory pathway bypasses the AV node's protective rate-limiting. Impulses conduct via the pathway at rates up to 300+/min → extremely rapid (often >200 bpm), wide-complex, irregular tachycardia. QRS varies beat to beat (fusion of pathway and normal conduction). **NEVER give AV nodal blockers (adenosine, verapamil, diltiazem, digoxin, beta-blockers)** — they force all conduction down the pathway, potentially degenerating to VF. Treat with procainamide or electrical cardioversion.
- **AFib + complete heart block (CHB)**: Paradoxically REGULAR ventricular rhythm in the setting of absent P-waves. The ventricular rate is typically slow (30–50 bpm, junctional or ventricular escape). The combination of no P-waves + regular slow rate is diagnostic of AFib + CHB (or AFib + high-grade AV block). This is a critical finding.
- **AFib + STEMI**: The irregular rhythm complicates automated analysis (fiducial point detection, RR normalization), but ST elevation criteria remain valid. Average ST measurements across multiple beats. Irregular rhythm + ST elevation should be flagged as potential STEMI + AFib.
- **AFib + LVH**: High QRS voltages with strain pattern (ST depression, T inversion in lateral leads) can mimic ischemia. The irregular rhythm identifies AFib; LVH voltage criteria identify the hypertrophy.
- **AFib + digitalis therapy**: "Scooped" ST depression (Salvador Dali mustache sign), possible regularization of rate at therapeutic levels, slow ventricular response. Digitalis toxicity can cause regularization of AFib (junctional rhythm taking over) — regularized AFib + digitalis = suspect toxicity.

---

## 5. STAT Classification

| Priority | Criteria |
|----------|----------|
| **STAT** | AFib + WPW (pre-excited AFib with rate >150 bpm) — imminent VF risk. AFib + STEMI — dual emergency. AFib with ventricular rate >150 bpm and hemodynamic instability (hypotension, altered mental status, chest pain, acute HF). New-onset AFib + complete heart block. |
| **Time-sensitive** | New-onset AFib should be identified within minutes. Rate >100 bpm (RVR) requires rate control. Duration <48 hours is the window for cardioversion without prolonged anticoagulation (though TEE-guided approach is acceptable beyond this). |
| **Clinical action** | (1) Rate control: beta-blockers or calcium channel blockers (NOT in pre-excited AFib). (2) Stroke risk: CHA₂DS₂-VASc score → anticoagulation decision. (3) Rhythm control: cardioversion consideration (electrical or pharmacological). (4) Hemodynamically unstable → immediate synchronized cardioversion. (5) Search for reversible causes: thyroid, PE, sepsis, alcohol, post-surgical. |

---

## 6. Reasoning Complexity Analysis (Feeds Into Node 2.1 — Agent Architecture Research)

> **NOTE**: This section does NOT pre-assign agents. It documents the reasoning
> complexity of this condition so that Node 2.1 can determine the BEST agent
> architecture to handle ALL conditions. The actual agent assignment is filled
> in AFTER Node 2.1 research completes.

### 6.1 Reasoning Domains Required to Detect This Condition
- **Rhythm regularity analysis** (PRIMARY): Compute RR interval variability — coefficient of variation, histogram distribution, successive difference analysis. This is the most reliable computational feature.
- **P-wave detection** (PRIMARY): Confirm absence of organized P-waves. Requires template matching or morphological analysis in the baseline segments between QRS complexes, especially in V1 and II.
- **Rate analysis**: Calculate mean ventricular rate from all RR intervals. Classify as RVR (>100), controlled (60–100), or slow (<60).
- **Morphology analysis** (SUPPORTING): Characterize fibrillatory baseline (fine vs coarse). Assess QRS width (narrow vs wide). Detect Ashman beats.
- **Cross-domain reasoning** (for combinations): AFib + WPW requires recognizing irregular wide-complex tachycardia + variable QRS morphology + very rapid rate. AFib + CHB requires recognizing absent P-waves + paradoxically regular rhythm. AFib + STEMI requires combining rhythm diagnosis with ST analysis.
- Does NOT require: axis calculation, voltage criteria, or interval measurement (no PR interval exists) for basic AFib detection.

### 6.2 Feature Dependencies
- **ESSENTIAL computed features (from SDA-1)**:
  - All RR intervals (every beat pair in the strip)
  - RR interval statistics: mean, SD, coefficient of variation, range, successive differences
  - P-wave presence/absence determination per beat (or per segment between QRS complexes)
  - Baseline amplitude and frequency between QRS complexes (f-wave characterization)
  - QRS duration (narrow vs wide classification)
- **SUPPORTING features**:
  - Heart rate (derived from RR intervals)
  - QRS morphology (for detecting aberrancy, WPW, BBB)
  - ST segment measurements (for detecting coexisting STEMI)
  - f-wave amplitude and frequency (fine vs coarse characterization)
- **EXCLUSION features** (if present, AFib less likely):
  - Regular RR intervals (CV <5%) — excludes AFib (unless AFib + CHB)
  - Consistent P-wave morphology preceding each QRS with fixed PR interval — excludes AFib
  - Organized sawtooth flutter waves at 300/min — suggests flutter, not AFib
- **Per-beat vs aggregate**:
  - RR intervals: per-beat extraction, aggregate analysis (statistics)
  - P-wave presence: per-beat assessment, aggregate conclusion
  - QRS width: per-beat (to detect intermittent aberrancy)
  - ST segments: per-beat measurement, averaged for STEMI analysis

### 6.3 Cross-Condition Interactions
- **AFib affects how OTHER conditions present**:
  - STEMI: Irregular rhythm causes baseline wander; fiducial point detection is harder; ST measurements must be averaged across beats
  - QT prolongation: Cannot use single-beat QT/QTc; must average multiple beats with Fridericia correction
  - Bundle branch blocks: Must distinguish true BBB (persistent wide QRS) from Ashman phenomenon (transient aberrancy)
  - Digitalis toxicity: Regularization of AFib is a clue to digitalis toxicity
- **Conditions that must be ruled out first** (differential):
  - Atrial flutter with variable block (organized flutter waves vs chaotic f-waves)
  - MAT (identifiable P-waves with ≥3 morphologies)
  - Frequent PACs (underlying regular rhythm with premature beats)
- **Dangerous combinations**:
  - AFib + WPW = pre-excited AF → VF risk → STAT
  - AFib + CHB = paradoxically regular rhythm → diagnostic clue
  - AFib + hypokalemia = increased AF persistence + increased digoxin toxicity risk

### 6.4 Reasoning Chain Sketch
- **Minimum reasoning chain (high confidence)**:
  1. Extract all RR intervals from the strip
  2. Compute RR variability (CV > 10–15%)
  3. Confirm absence of organized P-waves in V1 and II
  4. Confirm narrow QRS (<120 ms)
  5. → Diagnosis: Atrial Fibrillation (confidence: HIGH)
- **Full reasoning chain (complete evidence assembly)**:
  1. Extract all RR intervals → compute statistics (mean, SD, CV, range)
  2. Assess RR irregularity: irregularly irregular pattern (no repeating grouping)
  3. Scan V1 baseline between QRS complexes for f-waves vs discrete P-waves vs flutter waves
  4. Scan II for P-wave absence confirmation
  5. Characterize f-waves: fine (<0.5 mm) vs coarse (≥0.5 mm)
  6. Measure QRS duration: narrow (<120 ms) vs wide (≥120 ms)
  7. If wide QRS: assess for WPW (variable morphology + delta waves + very rapid rate), BBB (consistent LBBB/RBBB pattern), or Ashman phenomenon (long-short cycle dependent)
  8. Calculate mean ventricular rate → classify RVR / controlled / slow
  9. If regular rhythm despite absent P-waves → consider AFib + CHB
  10. Assess ST segments for coexisting STEMI
  11. Measure QT in multiple beats → average QTcF
  12. → Final diagnosis with subtype and rate classification

### 6.5 Confidence Anchors
- **HIGH confidence features**:
  - RR interval CV >15% + no identifiable P-waves = near-diagnostic
  - Chaotic f-waves clearly visible in V1 = strong positive evidence
  - Narrow QRS + irregular RR + absent P-waves = classic presentation
- **LOWER confidence if**:
  - Very fast rate (>150 bpm): short RR intervals make it hard to assess baseline; may overlap with other SVTs
  - Very slow rate (<50 bpm): few beats on strip, less statistical power for irregularity assessment
  - Fine AFib with minimal f-waves: may appear as sinus rhythm with absent P-waves
  - Significant artifact or baseline wander
- **Pathognomonic combination**: Irregularly irregular RR intervals + absent P-waves + fibrillatory baseline in V1 + narrow QRS = AFib (specificity >99%)
- **Classification thresholds**:
  - "Possible AFib": Irregular rhythm but P-waves uncertain (e.g., artifact, fine AFib)
  - "Probable AFib": Irregular rhythm + absent P-waves, but only a few beats available
  - "Definite AFib": Irregularly irregular RR (CV >12%) + absent P-waves + f-waves in V1, sustained ≥30 seconds

### 6.6 Difficulty Score

| Dimension | Score (1-5) | Notes |
|-----------|-------------|-------|
| Signal clarity needed | 2 | AFib is detectable even in moderate noise; RR irregularity is robust to noise. Fine AFib requires cleaner signal for f-wave detection. |
| Number of leads required | 1 | Can be diagnosed from a single lead (II or V1) based on RR irregularity alone. V1 adds f-wave confirmation. Full 12-lead needed for combination assessment. |
| Cross-domain reasoning | 2 | Basic AFib = rhythm + P-wave analysis only. Increases to 4–5 when assessing AFib + WPW, AFib + STEMI, or AFib + CHB. |
| Temporal pattern complexity | 3 | Every beat is different — requires full-strip analysis, not single-beat. Ashman phenomenon adds temporal complexity. |
| Differential complexity | 3 | Must distinguish from atrial flutter with variable block, MAT, frequent PACs, and artifact. Flutter vs AFib is the hardest differential. |
| Rarity in PTB-XL | 1 | Very common in PTB-XL (~1,500+ records). Large validation set available. One of the most prevalent arrhythmias in the dataset. |
| **Overall difficulty** | **2.0** | **Basic AFib detection is straightforward — one of the easier arrhythmias to detect computationally. Complexity increases substantially with combination conditions.** |

---

## 6A. Agent Assignment

**Architecture:** Option E — 3 Parallel Phase 1 Specialists + 1 Sequential CDS (Node 2.1 Gate Passed 2026-03-27)

| Agent | Role for Atrial Fibrillation | Key Features Used |
|-------|--------------------------|-------------------|
| **RRC** (Rhythm/Rate/Conduction) | Primary | Irregularly irregular RR intervals (no two consecutive RR intervals equal), absence of distinct P-waves, fibrillatory baseline (f-waves at 350–600/min), mean ventricular rate assessment, AV conduction ratio variability, Ashman phenomenon detection (long-short sequence → aberrant conduction) |
| **IT** (Ischemia/Territory) | Not involved | — |
| **MR** (Morphology/Repolarization) | Supporting | QRS morphology during aberrant conduction (Ashman beats — RBBB pattern), detection of delta waves if WPW is coexisting (irregular rhythm + preexcitation = emergent), ventricular rate response pattern |
| **CDS** (Cross-Domain Synthesis) | Required — resolves WPW + AFib if detected | If RRC identifies irregularly irregular rhythm AND MR detects delta waves/preexcitation pattern, CDS escalates to WPW + AFib emergent diagnosis; for standard AFib, CDS performs integration and confirms rate and rhythm classification |

### Primary Agent
**RRC** — atrial fibrillation is a rhythm diagnosis defined by irregularly irregular RR intervals with absent P-waves and fibrillatory baseline, which is entirely in the RRC agent's domain.

### Cross-Domain Hints
- MR emits `cross_domain_hint: "Delta wave morphology detected during irregularly irregular rhythm — WPW + AFib is possible; this is a life-threatening combination; CDS must escalate urgency immediately"` when preexcitation pattern accompanies AFib rhythm.

### CDS Specific Role
CDS performs standard AFib integration for isolated AFib: confirms RRC's rhythm diagnosis, notes ventricular rate category (controlled vs uncontrolled), and generates final classification. The critical CDS function is the WPW + AFib detection: if MR reports delta waves during RRC's irregularly irregular rhythm, CDS applies the emergent escalation — WPW + AFib allows antegrade conduction down the accessory pathway at the atrial rate (potentially 300+ bpm ventricular response), which can degenerate to VF. CDS flags this as the highest urgency tier with specific treatment note (no AV-blocking agents).

---

## 7. RAG Knowledge Requirements

### 7.1 Textbook References
- **Goldberger's Clinical Electrocardiography (10th ed.)**: Chapter on supraventricular arrhythmias — excellent f-wave illustrations and systematic approach to irregular rhythms. Best for foundational understanding.
- **Chou's Electrocardiography in Clinical Practice (7th ed.)**: Chapter 12 — detailed atrial fibrillation section with extensive lead-by-lead examples and electrophysiological correlates. Best for depth.
- **Marriott's Practical Electrocardiography (13th ed.)**: Strong on Ashman phenomenon, aberrant conduction in AFib, and AFib mimics. Best for differential diagnosis.
- **Braunwald's Heart Disease (12th ed.)**: Chapter 66 — clinical context, management algorithms, CHA₂DS₂-VASc scoring. Best for clinical integration.

### 7.2 Key Figures
- Reference ECG: 12-lead showing classic AFib with RVR — prominent f-waves in V1, irregularly irregular RR intervals, narrow QRS
- Comparison figure: Fine AFib (nearly flat baseline) vs coarse AFib (prominent f-waves) side by side
- Danger case: Pre-excited AFib (WPW) — wide, irregular, very rapid
- Diagnostic case: AFib + complete heart block — absent P-waves but paradoxically regular rhythm
- Ashman phenomenon example: Long-short cycle with aberrant beat

---

## 8. Dashboard Visualization Specification

### 8.1 Highlighted Leads
- **Primary display**: V1 (full width, enlarged) — highlight fibrillatory baseline between QRS complexes with a shaded overlay
- **Secondary display**: Lead II rhythm strip (full width) — RR intervals marked with vertical markers showing irregularity
- **Supporting**: All 12 leads in standard format with P-wave search windows highlighted (empty = absent P-waves)

### 8.2 Arrows and Annotations
- **V1**: Arrows pointing to f-waves between QRS complexes, labeled "Fibrillatory waves (f-waves) — no organized P-waves"
- **Lead II**: Brackets between consecutive R-waves with RR interval values (in ms), color-coded: green for similar intervals, red for highly variable — demonstrating irregularly irregular pattern
- **RR interval histogram**: Inset showing distribution of all RR intervals — wide, non-clustered distribution (vs flutter which clusters at 2:1, 3:1 ratios)
- **If RVR**: Rate banner at top: "Rapid ventricular response — mean rate: XXX bpm"
- **If wide QRS**: Alert annotation: "Wide QRS — evaluate for WPW / BBB / aberrancy"

### 8.3 Clinician Explanation (Plain Language)
- **ER nurse**: "This ECG shows atrial fibrillation — the heart's upper chambers are beating chaotically instead of in an organized rhythm. The main clue is that the heartbeat is completely irregular with no pattern, and there are no normal P-waves before each heartbeat."
- **Cardiologist**: "Twelve-lead ECG demonstrating atrial fibrillation with [RVR/controlled/slow ventricular response] at a mean rate of [X] bpm. Fibrillatory baseline is [fine/coarse], best seen in V1. QRS is [narrow/wide — if wide, specify BBB pattern or pre-excitation concern]. No ST elevation to suggest acute coronary syndrome. Recommend CHA₂DS₂-VASc assessment for anticoagulation decision and rate/rhythm control per current guidelines."

---

## 9. Edge Cases and Pitfalls

- **Fine AFib mimicking sinus rhythm**: When f-waves are <0.1 mm (very fine AFib), the baseline appears flat. May be misread as sinus rhythm with "absent P-waves" or sinus bradycardia. Key: check RR irregularity — sinus rhythm is regular; fine AFib is irregularly irregular.
- **Coarse AFib mimicking atrial flutter**: Large f-waves (>1 mm) can appear somewhat organized. Key: true flutter waves are identical and regular (300/min); coarse AFib f-waves vary in morphology and timing.
- **AFib with slow ventricular response mimicking normal sinus rhythm**: Slow AFib (50–60 bpm) with fine f-waves can appear deceptively normal. Key: RR intervals are still irregular (though less obviously so with fewer beats).
- **AFib + complete heart block**: The paradoxically REGULAR rhythm is a trap — it appears to contradict AFib. Key: absent P-waves + slow regular rate = AFib + CHB until proven otherwise.
- **Pre-excited AFib (WPW)**: The wide, bizarre QRS complexes at rapid rates can be misdiagnosed as ventricular tachycardia. Key differences: VT is typically regular or regularly irregular; pre-excited AFib is irregularly irregular with varying QRS morphology.
- **Ashman phenomenon vs PVCs**: Wide beats in AFib are often Ashman beats, not PVCs. Overtreating with antiarrhythmics is a risk. Key: Ashman beats have RBBB morphology, follow long-short cycles, and have no compensatory pause.
- **Rate-controlled AFib vs sinus rhythm on short strips**: A 3-second strip of well-controlled AFib (60–80 bpm) may show only 3–4 beats with minimal RR variation. Key: need longer strips; always examine V1 for f-waves.
- **Post-cardioversion**: Immediately after cardioversion, the atria may be stunned — P-waves may be absent or low-amplitude for hours despite sinus rhythm restoration. Do not diagnose persistent AFib based solely on post-cardioversion ECG.
- **Age/sex variations**: AFib prevalence increases with age (>5% in patients >65). No significant sex-based ECG morphology differences, though women may have faster ventricular rates due to shorter AV nodal refractory periods.
- **Pediatric AFib**: Rare — when seen in children, almost always associated with structural heart disease or WPW. F-waves may be more prominent due to thinner chest wall.
- **Electrode artifact**: Loose electrodes, patient tremor (especially Parkinson's), and shivering can create irregular baseline oscillations mimicking f-waves. Key: artifact typically affects multiple leads simultaneously and does not respect the isoelectric line.

---

## 10. References
- January CT, et al. 2019 AHA/ACC/HRS Focused Update of the 2014 AHA/ACC/HRS Guideline for the Management of Patients With Atrial Fibrillation. Circulation. 2019;140(2):e125-e151.
- Joglar JA, et al. 2023 ACC/AHA/ACCP/HRS Guideline for Diagnosis and Management of Atrial Fibrillation. Circulation. 2024;149(1):e1-e156.
- Hindricks G, et al. 2020 ESC Guidelines for the diagnosis and management of atrial fibrillation. Eur Heart J. 2021;42(5):373-498.
- Van Gelder IC, et al. 2024 ESC Guidelines for the management of atrial fibrillation. Eur Heart J. 2024;45(36):3314-3414.
- Lip GYH, et al. Atrial fibrillation. Nat Rev Dis Primers. 2016;2:16016.
- Ashman R. Aberrant conduction in atrial fibrillation. Am Heart J. 1947;33:685.
- Goldberger AL. Clinical Electrocardiography: A Simplified Approach. 10th ed. Elsevier; 2024.
- Surawicz B, Knilans TK. Chou's Electrocardiography in Clinical Practice. 7th ed. Saunders; 2020.
- Wagner GS, Strauss DG. Marriott's Practical Electrocardiography. 13th ed. Wolters Kluwer; 2022.
- PTB-XL ECG dataset: Wagner P, et al. PTB-XL, a large publicly available electrocardiography dataset. Sci Data. 2020;7(1):154.
