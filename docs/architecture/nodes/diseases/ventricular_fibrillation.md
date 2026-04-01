# Ventricular Fibrillation — ECG Manifestation from First Principles

**Node:** 2.7.10
**SDA:** SDA-2 (Diagnosis & Agentic Core) — shared resource for SDA-1, SDA-3, SDA-4
**Status:** Complete
**PGMR:** Required
**Date:** 2026-03-26

---

## 1. Pathophysiology Root Cause

### 1.1 What Goes Wrong (Anatomy/Physiology)
- Multiple re-entrant wavelets simultaneously circulate through ventricular myocardium in a chaotic, self-sustaining pattern with no organized depolarization sequence
- The ventricles quiver rather than contract — there is NO effective cardiac output, NO pulse, NO blood pressure. This is clinical death without immediate intervention.
- The substrate requires a combination of trigger and vulnerable myocardium:
  - **Trigger:** A premature ventricular complex (PVC) falling on the vulnerable period of repolarization (R-on-T phenomenon), or degeneration from VT, or Torsades de Pointes degenerating to VF
  - **Vulnerable substrate:** Myocardial heterogeneity in refractoriness and conduction velocity — areas of scar (post-MI), fibrosis (cardiomyopathy), ion channel dysfunction (Brugada, long QT, short QT), or acute ischemia create regions with different electrical properties that sustain chaotic re-entry
- Once initiated, the multiple wavelet re-entry is self-sustaining: each wavelet breaks into daughter wavelets when encountering refractory tissue, and the wavelets continuously find excitable gaps to perpetuate the arrhythmia
- With time, myocardial ATP depletion and acidosis reduce the amplitude of fibrillatory waves (coarse VF → fine VF), eventually leading to asystole if not defibrillated

### 1.2 Electrical Consequence
- There is NO organized ventricular depolarization — no coherent wavefront propagates through the ventricles
- Hundreds of small re-entrant circuits activate simultaneously in different directions, producing chaotic electrical vectors that change continuously in direction, amplitude, and frequency
- The net electrical vector at any moment is the sum of these chaotic individual vectors — it changes from millisecond to millisecond, producing the characteristic irregular, chaotic undulations on ECG
- There are no discrete QRS complexes because there is no organized depolarization sequence — the ECG shows continuous, irregular oscillations
- The frequency and amplitude of the oscillations reflect the metabolic state of the myocardium: recently initiated VF (well-oxygenated myocardium) → high amplitude, higher frequency (coarse VF); prolonged VF (hypoxic, acidotic, ATP-depleted) → low amplitude, lower frequency (fine VF)

### 1.3 Why It Appears on ECG
- The ECG electrodes detect the summation of all chaotic electrical activity in the ventricles
- Because the wavefronts are random and constantly changing, no two consecutive cycles look the same — there is no repeating morphology
- The amplitude of undulations reflects the mass of myocardium participating in each chaotic cycle — more mass activated simultaneously = larger deflection
- Different leads may show different amplitudes simultaneously because the instantaneous vector projects differently onto each lead axis — a lead perpendicular to the dominant instantaneous vector may show low amplitude while an aligned lead shows high amplitude
- Fine VF may appear as a nearly flat line in some leads while still showing fibrillatory activity in others — this is why multiple leads must be checked before diagnosing asystole

---

## 2. ECG Presentation — Lead by Lead

### 2.1 Diagnostic Criteria (2025 AHA/ESC Guidelines)

| Criterion | Threshold | Source |
|-----------|-----------|--------|
| Chaotic, irregular waveform | No identifiable P-waves, QRS complexes, or T-waves | AHA ACLS 2020/2025; universal recognition criterion |
| No organized rhythm | No repeating pattern, no regular intervals between deflections | AHA/ESC consensus |
| Coarse VF | Fibrillatory amplitude >0.2 mV (2 mm at standard calibration) | AHA ACLS classification |
| Fine VF | Fibrillatory amplitude <0.2 mV (may approach isoelectric line) | AHA ACLS classification; must distinguish from asystole |
| Frequency | Typically 150-500 fibrillatory cycles per minute (dominant frequency 3-9 Hz) | Electrophysiology literature |
| Clinical correlation | Pulseless, unresponsive patient | Required — VF is a clinical-electrical diagnosis |

### 2.2 Lead-by-Lead Manifestation

| Lead | Expected Finding | Why (Vector Explanation) | Sensitivity |
|------|-----------------|------------------------|-------------|
| I | Chaotic, irregular undulations with no identifiable complexes; amplitude varies continuously | Lead I captures the horizontal (left-right) component of the chaotic vectors; since vectors are random, the projection onto lead I axis changes chaotically | Moderate — VF may appear lower amplitude in some leads than others |
| II | Chaotic, irregular undulations; often among the leads with larger amplitude fibrillatory waves | Lead II is typically the longest vector axis in normal hearts; may capture more of the chaotic activity depending on the dominant fibrillatory wavefronts | High — frequently used for rhythm monitoring |
| III | Chaotic, irregular undulations | Inferior lead; amplitude depends on instantaneous vector projection; may differ significantly from lead II at any given moment | Moderate |
| aVR | Chaotic, irregular undulations; no organized QRS complexes | aVR sees the same chaotic activity from its rightward-superior vantage; amplitude may differ from limb leads | Moderate |
| aVL | Chaotic, irregular undulations | High lateral lead; amplitude varies moment to moment | Moderate |
| aVF | Chaotic, irregular undulations | Inferior lead; critical to assess — fine VF in aVF may be mistaken for asystole if only this lead is monitored | Moderate — important for fine VF vs asystole |
| V1 | Chaotic, irregular undulations; anterior chest lead may show prominent fibrillatory waves | V1 is close to the RV and septum — if fibrillatory activity has any transient anterior dominance, V1 may show larger waves | High |
| V2 | Chaotic, irregular undulations; often shows larger amplitude fibrillatory waves | V2 overlies the anterior heart; proximity to myocardium may produce larger signals | High |
| V3 | Chaotic, irregular undulations | Anterior lead; variable amplitude | Moderate |
| V4 | Chaotic, irregular undulations | Anterior-apical lead; variable amplitude | Moderate |
| V5 | Chaotic, irregular undulations | Anterolateral lead; variable amplitude | Moderate |
| V6 | Chaotic, irregular undulations; may show lower amplitude than V1-V3 due to greater distance from the heart | V6 is more lateral and further from the myocardial mass; may register lower amplitude fibrillatory activity | Low-Moderate — not the best lead for VF assessment |

### 2.3 Key Leads (Most Diagnostic)
- **Lead II:** Standard monitoring lead; often shows VF clearly; most clinicians will see VF first in lead II on the monitor
- **V1-V3:** Precordial leads closest to the myocardium; often show the largest amplitude fibrillatory waves and may show VF when limb leads appear nearly flat
- **CRITICAL:** Fine VF vs asystole assessment requires checking MULTIPLE leads. VF may appear as a flat line in one lead (lead perpendicular to dominant fibrillatory vector) while showing clear fibrillatory activity in another. The AHA recommends checking at least 2 leads and increasing gain before diagnosing asystole.
- There are no "reciprocal changes" or lead-specific patterns — VF is global chaotic activity visible (to varying degrees) in all leads

### 2.4 Beat-by-Beat Considerations
- There are NO discrete beats in VF — the concept of beat-to-beat analysis does not apply
- The waveform is a continuous, chaotic oscillation with no repeating units
- **Coarse vs fine assessment:** The amplitude and frequency of the fibrillatory waves should be assessed across the entire recording. Coarse VF (larger amplitude, higher frequency) indicates more recent onset and better response to defibrillation. Fine VF (lower amplitude, lower frequency) indicates longer duration and worse prognosis.
- **Transition patterns:** VF may be preceded by VT (VT degenerating to VF — the organized wide complexes become progressively irregular and chaotic), Torsades de Pointes (the twisting morphology breaks down into chaos), or a single PVC on the T-wave (R-on-T triggering VF). The agent should attempt to identify any organized rhythm preceding the VF for etiologic clues.
- **Organized segments within VF:** Occasionally, brief runs of organized rhythm (seconds of apparent VT or even narrow complexes) may appear transiently within VF before degenerating back to fibrillation. These do NOT represent cardioversion and do NOT change the diagnosis.

---

## 3. Morphology Details (What the Agent Must See)

### 3.1 P-wave Changes
- Morphology: ABSENT — no identifiable P-waves. The atria may be fibrillating as well (concurrent AF) or may maintain sinus rhythm (the sinus P-waves are completely obscured by the overwhelming ventricular fibrillatory activity)
- There is no meaningful P-wave analysis in VF
- If apparent P-waves are visible with no ventricular activity, this is NOT VF — consider asystole with P-waves (ventricular standstill, which is a form of complete heart block)

### 3.2 PR Interval Changes
- Not applicable — there are no identifiable P-waves or QRS complexes, so no PR interval exists
- If a PR interval can be measured, the rhythm is NOT VF

### 3.3 QRS Complex Changes
- Morphology: ABSENT — there are no QRS complexes. The waveform consists of irregular, chaotic undulations that do not form discrete complexes.
- If any QRS complexes can be identified, consider: (a) VT rather than VF, (b) brief organized intervals within VF, (c) artifact superimposed on an organized rhythm
- Duration: Not applicable
- Amplitude: The fibrillatory waves have continuously varying amplitude (0.1-10+ mm depending on coarse vs fine VF)
- Axis: Not applicable — no organized QRS to determine axis

### 3.4 ST Segment Changes
- Not applicable — no identifiable ST segments
- There is no organized repolarization sequence in VF
- Cannot assess for ischemia during VF; must wait for restoration of organized rhythm

### 3.5 T-wave Changes
- Not applicable — no identifiable T-waves
- The entire waveform is chaotic undulation without discrete repolarization phases
- After successful defibrillation, T-wave abnormalities on the post-cardioversion ECG are expected (post-resuscitation changes, possibly reflecting underlying ischemia or the cause of VF)

### 3.6 QT/QTc Changes
- Not applicable during VF
- PRE-VF QTc is critically important: prolonged QTc (>500 ms) preceding VF suggests long QT syndrome (LQTS) as the substrate, especially if the VF was preceded by Torsades de Pointes
- POST-VF QTc (after ROSC): must be measured to assess for underlying channelopathy. QTc may be transiently prolonged after resuscitation due to ischemia, hypothermia, or drugs, so serial monitoring is needed.

### 3.7 Other Features
- **Dominant frequency analysis:** The frequency content of VF (typically analyzed via FFT) correlates with myocardial metabolic state and defibrillation success. Dominant frequency >4 Hz is associated with better defibrillation response. This is a potential computational feature for the agent.
- **Amplitude spectrum area (AMSA):** A computed metric combining amplitude and frequency components of VF; AMSA >15.5 mV-Hz predicts successful defibrillation with high sensitivity. This could be a valuable SDA-1 computed feature.
- **Coarse-to-fine transition:** Progressive decrease in amplitude and frequency over time indicates ongoing myocardial ischemia and ATP depletion. The agent should track this if monitoring over time.
- **Post-defibrillation rhythm:** After shock delivery, the rhythm may convert to sinus, asystole, PEA, or recurrent VF. The agent must immediately re-analyze the post-shock rhythm.

---

## 4. Differential Diagnosis

### 4.1 Mimics (What Looks Like This But Isn't)

| Mimic Condition | Shared Features | Distinguishing Features |
|----------------|-----------------|----------------------|
| Fine VF vs Asystole | Both may appear as a nearly flat line on the monitor | Fine VF shows low-amplitude irregular undulations (>0.1 mV); true asystole is a flat line with no electrical activity. Check MULTIPLE leads — VF may appear flat in one lead but clearly fibrillatory in another. Increase gain to 2x. If any doubt, treat as VF (defibrillation). AHA protocol: confirm asystole in at least 2 leads. |
| Artifact (loose lead, patient movement, CPR) | Irregular, chaotic waveform on the monitor | Artifact from CPR shows rhythmic oscillations at the compression rate (~100-120/min, regular); loose lead shows intermittent signal dropout or high-frequency noise; patient movement shows bursts correlated with movement. Check multiple leads — true VF is present in ALL leads simultaneously. |
| Polymorphic VT / Torsades de Pointes | Wide, irregular, chaotic-appearing QRS complexes | Polymorphic VT and Torsades still have identifiable (though varying) QRS complexes with clear isoelectric baseline between complexes. Torsades shows the characteristic sinusoidal rotation of QRS axis. VF has NO identifiable QRS complexes and NO isoelectric baseline. |
| Very fast monomorphic VT (>250 bpm) | Sinusoidal waveform that may look disorganized | Very fast VT is REGULAR (constant cycle length) with a REPEATING morphology, even though individual complexes may be hard to delineate. VF is IRREGULAR with NO repeating morphology. |
| Atrial fibrillation (on monitor) | Irregular baseline | AF has irregular RR intervals but identifiable (narrow) QRS complexes. The irregularity is in the rhythm, not in the QRS morphology. The fibrillatory baseline in AF is between clearly defined QRS complexes. |
| Electromagnetic interference | Chaotic waveform | 50/60 Hz interference has a regular sinusoidal pattern at the line frequency; other electrical interference may be irregular but is typically high-frequency and low-amplitude; not present in all leads; patient has a pulse |

### 4.2 Coexisting Conditions
- **Acute MI → VF:** VF is the leading cause of death in the first hour of acute MI. Primary VF occurs from ischemia-induced electrical instability. After resuscitation, STEMI assessment is mandatory — emergent PCI may be indicated regardless of neurologic status.
- **Brugada syndrome → VF:** VF may be the first presentation of Brugada syndrome, triggered during sleep or rest. Post-resuscitation ECG in sinus rhythm should be evaluated for Brugada pattern (coved ST elevation in V1-V3). Drug challenge (ajmaline/procainamide) may be needed to unmask the pattern.
- **Long QT → Torsades → VF:** Torsades de Pointes may degenerate to VF. Review any pre-arrest ECG for prolonged QT. Post-resuscitation QTc measurement is critical. Avoid QT-prolonging drugs.
- **WPW + rapid AF → VF:** Pre-excited AF (irregular wide-complex tachycardia at rates >250 bpm) can degenerate to VF. Delta waves on post-resuscitation ECG indicate WPW substrate.
- **Hyperkalemia → VF:** Severe hyperkalemia (>7.0 mEq/L) can cause VF. Preceding ECG may show peaked T-waves, wide QRS, loss of P-waves. Treatment includes IV calcium, insulin/glucose, bicarbonate.
- **Hypothermia → VF:** Osborn (J) waves on ECG preceding VF suggest hypothermia. Core temperature must be >30°C for defibrillation to be effective. Rewarm before repeated shocks.
- **Commotio cordis:** Blunt chest impact during the vulnerable period of repolarization (R-on-T) triggering VF in a structurally normal heart. Typically in young athletes. No preceding ECG abnormality.

---

## 5. STAT Classification

| Priority | Criteria |
|----------|----------|
| **STAT** | YES — VF is the MOST emergent cardiac rhythm. It represents cardiac arrest with ZERO cardiac output. Every second of VF is brain death in progress. This is the highest possible priority in all of medicine. |
| **Time-sensitive** | IMMEDIATE DEFIBRILLATION — survival decreases approximately 7-10% with EVERY MINUTE of delay. At 10 minutes without defibrillation, survival approaches zero. Early defibrillation is the single most important determinant of survival. CPR buys time but cannot terminate VF. |
| **Clinical action** | **Immediate:** Confirm pulselessness. Begin CPR. Defibrillate as rapidly as possible (biphasic 120-200J, or maximum available energy if device-specific dose unknown). **ACLS protocol:** CPR 2 min → rhythm check → shock if VF persists → CPR 2 min → epinephrine 1 mg IV q3-5 min → shock → amiodarone 300 mg IV first dose, 150 mg second dose. **Post-ROSC:** 12-lead ECG immediately for STEMI assessment → emergent PCI if indicated. Targeted temperature management (TTM) 32-36°C for 24 hours. Continuous telemetry. Electrolyte correction (K+ >4.0, Mg2+ >2.0). Cardiology/EP consultation for ICD evaluation. Assess for reversible causes (ischemia, electrolytes, toxins, channelopathies). |

---

## 6. Reasoning Complexity Analysis (Feeds Into Node 2.1 — Agent Architecture Research)

> **NOTE**: This section does NOT pre-assign agents. It documents the reasoning
> complexity of this condition so that Node 2.1 can determine the BEST agent
> architecture to handle ALL conditions. The actual agent assignment is filled
> in AFTER Node 2.1 research completes.

### 6.1 Reasoning Domains Required to Detect This Condition
- **Pattern recognition:** The primary reasoning domain — recognizing the absence of organized cardiac complexes and the presence of chaotic undulations. This is fundamentally different from most other conditions that require identifying specific waveform features.
- **Signal analysis:** Distinguishing true VF from artifact (especially CPR artifact, which can mimic VF or obscure underlying VF)
- **Amplitude assessment:** Classifying coarse vs fine VF based on fibrillatory wave amplitude
- **Multi-lead correlation:** Confirming VF is present in all leads (artifact tends to be lead-specific); critical for fine VF vs asystole differentiation
- **Temporal analysis:** Identifying the transition from organized rhythm (VT, Torsades) to VF; tracking coarse-to-fine progression
- **Frequency domain analysis (optional advanced):** Dominant frequency and AMSA computation for prognostication
- Cross-domain reasoning is MINIMAL for VF detection itself (the pattern is unmistakable when coarse), but fine VF vs asystole requires multi-lead correlation and amplitude assessment

### 6.2 Feature Dependencies
- **ESSENTIAL features (from SDA-1):**
  - Absence of identifiable QRS complexes (QRS detection algorithm returns zero or near-zero confidence for all detected peaks)
  - Presence of continuous electrical activity (signal is NOT flat/isoelectric)
  - Irregular amplitude variation (no repeating pattern)
  - Signal present in multiple/all leads simultaneously (not artifact)
- **SUPPORTING features (increase confidence):**
  - Fibrillatory wave amplitude (coarse vs fine classification)
  - Dominant frequency of the fibrillatory waveform
  - AMSA (amplitude spectrum area) for prognostication
  - Identification of preceding organized rhythm (VT, Torsades, R-on-T PVC)
  - Signal coherence across leads (all leads show chaotic activity simultaneously)
- **EXCLUDING features (if present, reconsider VF diagnosis):**
  - Identifiable QRS complexes at regular intervals → this is VT or other organized rhythm, not VF
  - Flat line in ALL leads → asystole, not VF
  - Artifact pattern (regular frequency, single-lead involvement, correlation with external events like CPR)
  - Identifiable P-waves without QRS → ventricular standstill / complete heart block, not VF
- **Per-beat vs aggregate:** Aggregate analysis — there are no individual beats to analyze. The assessment is of the overall waveform character.

### 6.3 Cross-Condition Interactions
- **Affects other conditions:** VF makes ALL other ECG diagnosis impossible. No condition can be assessed during VF. Post-defibrillation rhythm must be immediately analyzed for underlying conditions.
- **Requires ruling out:** Asystole (check multiple leads, increase gain), artifact (check pulse, check all leads), very fast VT (look for regularity and repeating morphology), Torsades (look for twisting QRS pattern)
- **Condition combinations that change interpretation:**
  - Fine VF + asystole uncertainty: must default to treating as VF (defibrillation is harmless in asystole)
  - VF preceded by wide QRS VT: suggests ischemic or structural substrate; post-ROSC assessment for MI is mandatory
  - VF preceded by Torsades: suggests long QT substrate; avoid QT-prolonging drugs including amiodarone in post-resuscitation care; magnesium and pacing preferred
  - Recurrent VF despite defibrillation ("VF storm"): suggests ongoing trigger (acute ischemia, severe electrolyte imbalance, drug effect); the underlying cause must be identified and treated

### 6.4 Reasoning Chain Sketch
- **Minimum reasoning chain (fewest steps to high confidence):**
  1. QRS detection algorithm fails to identify any organized QRS complexes
  2. Continuous irregular electrical activity present (not flat line)
  3. Activity present in multiple leads simultaneously (not artifact)
  4. Diagnosis: VF → IMMEDIATE DEFIBRILLATION ALERT

- **Full reasoning chain (complete evidence assembly):**
  1. Run QRS detection algorithm across all leads; confirm absence of organized complexes (confidence <threshold in all leads)
  2. Confirm continuous electrical activity present (signal amplitude above noise floor)
  3. Confirm irregularity — no repeating pattern or constant cycle length (excludes VT, flutter)
  4. Confirm multi-lead presence — chaotic activity in ≥2 leads simultaneously (excludes single-lead artifact)
  5. Classify amplitude: coarse (>0.2 mV) vs fine (<0.2 mV)
  6. If fine: verify in all 12 leads; check for any lead showing activity >0.2 mV; if ALL leads <0.1 mV → consider asystole, flag uncertainty, recommend treating as VF
  7. Assess for artifact overlay: if CPR in progress, attempt to identify pauses in compressions for rhythm analysis
  8. If preceding rhythm available: identify transition pattern (VT→VF, Torsades→VF, R-on-T→VF) for etiologic classification
  9. Compute dominant frequency (if capable): >4 Hz suggests better defibrillation response
  10. Compute AMSA (if capable): >15.5 mV-Hz predicts successful defibrillation
  11. Final diagnosis: VF — IMMEDIATE DEFIBRILLATION ALERT with classification (coarse/fine) and prognostic features

### 6.5 Confidence Anchors
- **HIGH confidence features:**
  - Complete absence of identifiable QRS complexes + continuous chaotic electrical activity = VF (this combination is essentially pathognomonic)
  - Coarse fibrillatory waves (>0.2 mV) with irregular amplitude and frequency across all leads = unambiguous VF
  - Preceding organized rhythm (VT or Torsades) that abruptly transitions to chaotic activity = VF
- **LOW confidence (if absent or equivocal):**
  - Very low amplitude fibrillatory activity (<0.1 mV) — may be fine VF or asystole; must check multiple leads and increase gain
  - Activity present in only one lead — likely artifact
  - Any identifiable repeating QRS pattern — likely VT, not VF
  - Regular oscillation at a fixed frequency — likely artifact (electrical interference, CPR)
- **Pathognomonic combination:** Chaotic, irregular, continuous electrical activity with no identifiable P/QRS/T in ALL monitored leads in a pulseless patient = 100% VF
- **Classification thresholds:**
  - "Possible" VF: low-amplitude chaotic activity in some leads; equivocal in others (fine VF vs asystole territory — treat as VF)
  - "Probable" VF: clear chaotic activity in multiple leads with no identifiable complexes
  - "Definite" VF: unmistakable chaotic activity across all leads with varying amplitude, no organized complexes, confirmed in ≥2 leads

### 6.6 Difficulty Score
| Dimension | Score (1-5) | Notes |
|-----------|-------------|-------|
| Signal clarity needed | 2 | Coarse VF is obvious even with noise; however, fine VF vs asystole distinction requires clean signal and multiple leads. CPR artifact is a major confounder during resuscitation. |
| Number of leads required | 3 | Coarse VF is identifiable from a single monitoring lead; however, fine VF vs asystole requires multiple leads. Standard practice is ≥2 leads for confirmation. |
| Cross-domain reasoning | 1 | VF detection is primarily pattern recognition (absence of organized complexes + chaotic activity). Minimal cross-domain integration needed compared to VT or STEMI. |
| Temporal pattern complexity | 2 | No beat-to-beat analysis needed (no beats exist). The only temporal assessment is coarse-to-fine progression and identifying the transition from preceding organized rhythm. |
| Differential complexity | 3 | Primary differentials (asystole, artifact, very fast VT) are relatively limited but clinically critical — misclassifying fine VF as asystole means missing the only shockable rhythm. |
| Rarity in PTB-XL | 5 | VF is essentially absent from PTB-XL (patients with VF are in cardiac arrest, not getting diagnostic 12-lead ECGs). Detection algorithms must be validated on other datasets (AHA defibrillator databases, PhysioNet). |
| **Overall difficulty** | **2.7** | **Low-moderate — VF pattern recognition is straightforward for coarse VF, but fine VF vs asystole is a critical edge case, and CPR artifact during resuscitation adds complexity** |

---

## 6A. Agent Assignment

**Architecture:** Option E — 3 Parallel Phase 1 Specialists + 1 Sequential CDS (Node 2.1 Gate Passed 2026-03-27)

| Agent | Role for Ventricular Fibrillation | Key Features Used |
|-------|--------------------------|-------------------|
| **RRC** (Rhythm/Rate/Conduction) | Primary | Absence of organized QRS complexes, chaotic irregular baseline oscillations (1–10 mm amplitude, 150–500 deflections/min), absence of identifiable P-waves, no measurable RR intervals, confirmation of complete disorganization |
| **IT** (Ischemia/Territory) | Not involved | No interpretable ST segments or ischemic morphology — no measurable waveforms exist |
| **MR** (Morphology/Repolarization) | Not involved | No measurable QRS, T-wave, or QT interval — no morphology analysis possible |
| **CDS** (Cross-Domain Synthesis) | Minimal — validates absence confirmation from all agents | Confirms IT and MR report no interpretable waveforms; validates that RRC's chaotic baseline finding is not artifact; generates final VF diagnosis with highest urgency flag |

### Primary Agent
**RRC** — ventricular fibrillation is a rhythm diagnosis defined by the complete absence of organized cardiac complexes, which is entirely within the RRC agent's domain.

### Cross-Domain Hints
No cross-domain hints required — VF is a single-domain condition within RRC's primary domain. No ST segments, QRS morphology, or QTc measurements are available or meaningful during VF.

### CDS Specific Role
CDS performs standard integration with the critical function of absence validation: CDS confirms that IT reports no identifiable ST segments and MR reports no measurable QRS morphology, which is consistent with VF rather than artifact or other causes of disorganized tracing. CDS also applies coarse vs fine VF classification (amplitude threshold) and distinguishes from artifact (CPR compressions produce rhythmic wide deflections) and asystole (flat line vs low-amplitude chaotic). Final output is a VF diagnosis with immediate defibrillation urgency flag.

---

## 7. RAG Knowledge Requirements

### 7.1 Textbook References
- **Goldberger's Clinical Electrocardiography (10th ed.):** Chapter on cardiac arrest rhythms — VF recognition, coarse vs fine distinction, and post-arrest ECG assessment
- **Marriott's Practical Electrocardiography (13th ed.):** Section on ventricular fibrillation — waveform characteristics, transition from VT, artifact differentiation
- **Chou's Electrocardiography in Clinical Practice (7th ed.):** Chapter on sudden cardiac death rhythms — VF mechanisms, recognition, and prognostic features
- **ACLS Provider Manual (AHA 2020/2025):** Cardiac arrest algorithm — VF/pVT pathway, defibrillation protocols, post-ROSC care
- **Issa ZF, Miller JM, Zipes DP. Clinical Arrhythmology and Electrophysiology (3rd ed.):** Chapter on VF mechanisms — detailed electrophysiology of multiple wavelet re-entry

### 7.2 Key Figures
- Coarse VF example: high-amplitude, irregular fibrillatory waves across all leads
- Fine VF example: low-amplitude fibrillatory activity barely distinguishable from baseline
- Fine VF vs asystole comparison: side-by-side tracings at standard and 2x gain
- VT → VF transition: continuous recording showing organized VT degenerating to VF
- Torsades → VF transition: continuous recording showing polymorphic rotation breaking into chaos
- CPR artifact vs VF: tracings during chest compressions showing regular artifact pattern superimposed on/obscuring underlying rhythm
- Dashboard should show: multi-lead rhythm display with amplitude markers, coarse/fine classification indicator, frequency analysis panel, and bold DEFIBRILLATION alert

---

## 8. Dashboard Visualization Specification

### 8.1 Highlighted Leads
- **Primary display (large):** Lead II and V2 — most commonly used monitoring leads, typically show clear fibrillatory activity
- **Multi-lead confirmation panel:** At least 4 leads displayed simultaneously (I, II, V1, V5) to confirm VF is present in multiple leads and exclude artifact
- **Gain control display:** If fine VF is detected, show same lead at 1x and 2x gain side-by-side
- Color coding: Entire waveform in RED (maximum urgency); background of display in red or red-bordered to indicate cardiac arrest rhythm

### 8.2 Arrows and Annotations
- NO arrows pointing to specific complexes (there are none) — instead:
- Amplitude measurement bracket: showing peak-to-peak amplitude of fibrillatory waves; label "Coarse VF (X.X mV)" or "Fine VF (X.X mV)"
- Frequency annotation: label "Dominant frequency: X.X Hz"
- If transition from organized rhythm detected: marker at transition point; label "VT → VF transition" or "Torsades → VF transition" or "R-on-T → VF"
- Multi-lead indicator: checkmarks on each lead showing confirmed chaotic activity; label "VF confirmed in X/12 leads"
- Banner (LARGEST POSSIBLE): "VENTRICULAR FIBRILLATION — DEFIBRILLATE IMMEDIATELY"
- Countdown timer: "Survival decreases ~10% per minute without defibrillation"

### 8.3 Clinician Explanation (Plain Language)
- **ER nurse (2-3 sentences):** "This is ventricular fibrillation — the heart is not pumping blood. The patient has no pulse and will die without immediate defibrillation. Charge the defibrillator and shock now. Begin CPR between shocks."
- **Cardiologist (expanded):** "[Coarse/Fine] ventricular fibrillation identified across [X] leads. Dominant frequency [X.X Hz]; [AMSA X.X mV-Hz if computed]. [Preceding rhythm: VT/Torsades/R-on-T PVC/unknown]. Immediate defibrillation per ACLS VF/pVT algorithm. Post-ROSC priorities: 12-lead ECG for STEMI assessment (emergent PCI if indicated regardless of neurologic status), targeted temperature management, electrolyte correction, continuous telemetry. Assess for reversible substrate: acute ischemia, channelopathy (Brugada, LQTS), cardiomyopathy, electrolyte derangement, drug effect. EP consultation for ICD evaluation in survivors."

---

## 9. Edge Cases and Pitfalls

- **Fine VF vs asystole — the most critical edge case in emergency medicine:** Fine VF is treatable with defibrillation; asystole is not shockable. If there is ANY doubt, treat as VF. Check multiple leads, increase gain to 2x, and rotate lead axis (if paddle monitoring, rotate paddles 90°). The consequences of shocking asystole are minimal; the consequences of NOT shocking fine VF are death.
- **CPR artifact during resuscitation:** Chest compressions create regular-frequency artifact (1.5-2 Hz) that can obscure underlying VF or mimic organized rhythm. During rhythm checks, compressions MUST be paused. Emerging filtering algorithms can attempt to remove CPR artifact without pausing, but these are not yet standard. The agent should flag if rhythm analysis is attempted during ongoing CPR.
- **Recurrent VF (electrical storm):** Multiple VF episodes despite defibrillation. This is a distinct clinical scenario requiring identification of the underlying trigger (ongoing ischemia, proarrhythmic drug, electrolyte imbalance). The agent should track the number of VF episodes and alert if recurrent.
- **Post-shock artifact:** Defibrillation itself produces artifact on the ECG (saturation of amplifier). There may be 5-15 seconds of unreliable signal after a shock. The agent should not attempt rhythm classification during this window.
- **Hypothermic VF:** VF in hypothermic patients (<30°C) may not respond to defibrillation until core temperature is raised. The fibrillatory waves may be very coarse due to slower metabolic rate. The agent should correlate with temperature data if available.
- **Pediatric VF:** Less common in children but occurs. Fibrillatory wave amplitude may be smaller due to smaller cardiac mass. The agent should use age-adjusted amplitude thresholds if patient demographics are available.
- **ICD-recorded VF:** Implantable defibrillators record intracardiac electrograms during VF that look different from surface ECG VF. The agent should be aware that intracardiac signals have different morphology and amplitude characteristics.
- **Agonal rhythm transitioning through fine VF to asystole:** A dying heart may pass through a brief fine VF phase between organized rhythm and asystole. This represents a narrow window where defibrillation could be effective. The agent should flag even brief periods of possible fine VF.
- **Simulated VF (lead disconnection during monitoring):** A lead falling off during monitoring can produce a chaotic signal in that lead. The key: VF is present in ALL leads, while lead disconnection affects only the disconnected lead(s). Multi-lead confirmation is essential.

---

## 10. References
- Panchal AR, Bartos JA, Cabañas JG, et al. Part 3: Adult Basic and Advanced Life Support: 2020 American Heart Association Guidelines for Cardiopulmonary Resuscitation and Emergency Cardiovascular Care. Circulation. 2020;142(16_suppl_2):S366-S468.
- Zeppenfeld K, Tfelt-Hansen J, de Riva M, et al. 2022 ESC Guidelines for the management of patients with ventricular arrhythmias and the prevention of sudden cardiac death. Eur Heart J. 2022;43(40):3997-4126.
- Weisfeldt ML, Becker LB. Resuscitation after cardiac arrest: a 3-phase time-sensitive model. JAMA. 2002;288(23):3035-3038.
- Endoh H, Hida S, Oohashi S, Hayashi Y, Kinoshita H, Honda T. Prompt prediction of successful defibrillation from 1-s segments of ventricular fibrillation waveform in patients with out-of-hospital cardiac arrest. J Anesth. 2011;25(1):34-41.
- Ristagno G, Li Y, Fumagalli F, Finzi A, Bhatt S. Amplitude spectrum area to guide defibrillation: a validation on 1617 patients with ventricular fibrillation. Circulation. 2015;131(5):478-487.
- Goldberger AL, Goldberger ZD, Shvilkin A. Goldberger's Clinical Electrocardiography: A Simplified Approach. 10th ed. Elsevier; 2024.
- Surawicz B, Knilans TK. Chou's Electrocardiography in Clinical Practice. 7th ed. Saunders; 2020.
- Wagner GS, Strauss DG. Marriott's Practical Electrocardiography. 13th ed. Wolters Kluwer; 2022.
- Issa ZF, Miller JM, Zipes DP. Clinical Arrhythmology and Electrophysiology: A Companion to Braunwald's Heart Disease. 3rd ed. Elsevier; 2019.
- Li Y, Ristagno G, Guan J, et al. Wandering wavefronts underlying ventricular fibrillation waveform modulations. Heart Rhythm. 2016;13(7):1571-1580.
