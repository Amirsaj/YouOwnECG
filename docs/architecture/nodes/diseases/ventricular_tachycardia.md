# Ventricular Tachycardia — ECG Manifestation from First Principles

**Node:** 2.7.9
**SDA:** SDA-2 (Diagnosis & Agentic Core) — shared resource for SDA-1, SDA-3, SDA-4
**Status:** Complete
**PGMR:** Required
**Date:** 2026-03-26

---

## 1. Pathophysiology Root Cause

### 1.1 What Goes Wrong (Anatomy/Physiology)
- A re-entrant circuit, abnormal automaticity, or triggered activity originates within ventricular myocardium or the His-Purkinje system BELOW the bundle of His
- **Re-entry (most common, ~80%):** A fixed or functional circuit exists within scarred ventricular myocardium (post-MI scar, cardiomyopathy fibrosis, arrhythmogenic right ventricular cardiomyopathy). The circuit has a slow conduction zone (through scar) and a fast zone (normal tissue), creating the substrate for sustained re-entry.
- **Abnormal automaticity:** Enhanced phase-4 depolarization in damaged ventricular Purkinje fibers or myocytes (ischemia, electrolyte derangement, catecholamine excess). The cells fire spontaneously at rates exceeding the sinus node.
- **Triggered activity:** Early afterdepolarizations (EADs, seen in long QT) or delayed afterdepolarizations (DADs, seen in digoxin toxicity, catecholaminergic polymorphic VT) reach threshold and initiate repetitive ventricular firing.
- Structural heart disease is present in the majority of cases: ischemic cardiomyopathy (post-MI scar), dilated cardiomyopathy, hypertrophic cardiomyopathy, ARVC, or cardiac sarcoidosis. A minority occur in structurally normal hearts (idiopathic VT from RVOT or fascicular regions).

### 1.2 Electrical Consequence
- Ventricular depolarization occurs via cell-to-cell (myocyte-to-myocyte) conduction rather than the rapid His-Purkinje system, resulting in SLOW propagation across the ventricles
- Slow conduction → wide QRS complex (>120 ms, typically >140 ms)
- The depolarization wavefront originates eccentrically (from one ventricular focus) rather than simultaneously from both bundle branches, creating an abnormal QRS axis and morphology
- The atria and ventricles depolarize independently — the sinus node continues to fire but AV conduction to the ventricles is interrupted by the ventricular tachycardia (AV dissociation)
- Rate is typically 150-250 bpm for monomorphic VT; polymorphic VT may be faster and more irregular
- Ventricular repolarization is also abnormal, producing discordant ST-T changes (ST/T opposite in direction to the QRS)

### 1.3 Why It Appears on ECG
- Wide QRS: because ventricular activation bypasses the His-Purkinje system and spreads slowly through myocardium; the wider the QRS, the more myocardial (non-Purkinje) conduction is involved
- The QRS morphology reflects the origin: LBBB-pattern QRS suggests right ventricular or septal origin; RBBB-pattern suggests left ventricular origin
- AV dissociation: P-waves march through at sinus rate, independent of QRS complexes — visible as P-waves at a slower rate "buried" within or between QRS-T complexes
- Concordance (all precordial leads positive or all negative) occurs when the depolarization vector uniformly points toward or away from the precordial leads — this is nearly pathognomonic for VT
- The superior axis ("northwest axis") occurs when the origin is in the inferior wall, sending the depolarization vector upward and rightward — away from normal

---

## 2. ECG Presentation — Lead by Lead

### 2.1 Diagnostic Criteria (2025 AHA/ESC Guidelines)

| Criterion | Threshold | Source |
|-----------|-----------|--------|
| QRS duration | >120 ms (typically >140 ms); if LBBB morphology >160 ms strongly favors VT | AHA/ACC/HRS 2024 VT/VF Guidelines |
| Ventricular rate | Typically 150-250 bpm, regular (monomorphic) or irregular (polymorphic) | ESC 2022 Ventricular Arrhythmia Guidelines |
| AV dissociation | P-waves at independent (slower) rate from QRS; diagnostic when present | AHA/ESC consensus — pathognomonic |
| Capture beats | Narrow QRS complex during wide-complex tachycardia (sinus impulse captures ventricles briefly) | Pathognomonic for VT |
| Fusion beats | Intermediate morphology QRS (partial sinus + partial VT activation) | Pathognomonic for VT |
| Sustained VT definition | Duration >30 seconds OR requires termination due to hemodynamic compromise | AHA/ACC/HRS 2024 |
| Concordance | All precordial QRS complexes positive or all negative | Strongly favors VT (positive predictive value >90%) |

### 2.2 Lead-by-Lead Manifestation

| Lead | Expected Finding | Why (Vector Explanation) | Sensitivity |
|------|-----------------|------------------------|-------------|
| I | Wide QRS; morphology depends on VT origin. LBBB-type VT: negative or isoelectric. RBBB-type VT: may be positive or negative depending on axis. | Lead I views the heart from the left; origin in RV produces leftward vector (positive in I), origin in lateral LV produces rightward vector (negative in I) | Moderate — axis determination |
| II | Wide QRS; typically dominant in determining axis. Superior axis (negative in II) strongly suggests VT. | Lead II is the primary axis reference; VT from inferior wall sends vector superiorly → negative deflection in II | High — axis assessment |
| III | Wide QRS; helps confirm axis. Usually concordant with aVF for axis determination. | Inferior lead; inferior-origin VT → negative in III; superior-origin VT → positive in III | Moderate |
| aVR | Wide QRS; positive (dominant R wave) in aVR strongly favors VT. Vereckei aVR algorithm applied here. | aVR faces rightward-superior; VT origin from apex/inferior wall directs vector toward aVR. Vereckei: initial R >40 ms, or initial r or q >40 ms, or notch on descending limb, or Vi/Vt ratio ≤1 all favor VT | Very High — Vereckei algorithm is a primary VT vs SVT discriminator |
| aVL | Wide QRS; morphology aids axis determination. | High lateral lead; used to confirm left axis deviation or northwest axis in VT | Moderate |
| aVF | Wide QRS; negative QRS (superior axis) strongly favors VT over SVT with aberrancy. | aVF faces inferiorly; superior axis VT produces negative deflection; combined with negative II → northwest axis → VT | High — axis assessment |
| V1 | Wide QRS; RBBB-pattern (dominant R or Rs or qR) or LBBB-pattern (rS or QS). Morphology details distinguish VT from SVT+aberrancy. For RBBB-type: monophasic R, qR, or broad R (>40 ms) favors VT. For LBBB-type: R >30 ms, notched S downstroke, RS >60 ms favors VT. | V1 is the key lead for bundle-branch pattern classification; VT produces atypical BBB morphology because conduction is not through the fascicles | Very High — primary morphology analysis lead |
| V2 | Wide QRS; concordance assessment. RS interval measurement — RS >100 ms in ANY precordial lead favors VT. | V2 is critical for RS interval measurement in Brugada criteria; slow initial R-wave upstroke or delayed S-wave nadir indicates myocardial (non-Purkinje) conduction | Very High — Brugada criterion |
| V3 | Wide QRS; concordance assessment. Transition point — absence of RS complex (all positive or all negative) in V3 supports concordance and VT. | V3 is the usual transition zone; if QRS remains entirely positive or entirely negative here (no transition), concordance is established | High |
| V4 | Wide QRS; concordance assessment. | Anterior lead; continuation of concordance pattern or transition assessment | High |
| V5 | Wide QRS; concordance assessment. | Anterolateral lead; concordance pattern continuation | Moderate |
| V6 | Wide QRS; specific morphology. RBBB-type VT: R/S ratio <1 (deep S wave) favors VT. LBBB-type VT: QS or qR pattern favors VT (normal LBBB has no Q in V6). | V6 faces the lateral wall; VT from RV produces delayed lateral activation with atypical morphology that differs from true RBBB or LBBB patterns | High — key morphology distinction lead |

### 2.3 Key Leads (Most Diagnostic)
- **V1:** Primary lead for QRS morphology classification (RBBB vs LBBB pattern) and specific VT morphology criteria
- **V2:** RS interval measurement (Brugada criteria — RS >100 ms favors VT)
- **aVR:** Vereckei algorithm for VT vs SVT discrimination; initial R >40 ms or Vi/Vt ≤1 = VT
- **V6:** Morphology assessment — atypical BBB patterns favor VT
- **II, aVF:** Axis determination — superior/northwest axis strongly favors VT
- **All precordial leads (V1-V6):** Concordance assessment — all positive or all negative = VT
- **Any lead showing P-waves independent of QRS:** AV dissociation = pathognomonic for VT

### 2.4 Beat-by-Beat Considerations
- **Monomorphic VT:** All QRS complexes are identical beat-to-beat (same morphology, same axis). The regularity is constant or near-constant (cycle length variation <40 ms).
- **Polymorphic VT:** QRS morphology continuously changes beat-to-beat (varying axis, amplitude, and shape). Rate may be faster and more irregular. If the QRS appears to rotate around the baseline → Torsades de Pointes (a specific subset of polymorphic VT).
- **Capture beats:** Intermittent narrow QRS complexes appearing during wide-complex tachycardia — these are sinus impulses that "capture" the ventricles through normal conduction during a gap in the VT cycle. Pathognomonic for VT. May occur every 10-50 beats or not at all.
- **Fusion beats:** QRS complexes with intermediate morphology between the wide VT complex and the narrow sinus complex — simultaneous partial ventricular activation from both the VT focus and the sinus node. Pathognomonic for VT.
- **Warmup phenomenon:** The initial few beats of VT may show gradual acceleration (slightly longer initial cycle lengths); this favors automatic VT mechanism.
- **Most diagnostic beats:** Capture and fusion beats are the most diagnostic individual beats — the agent must scan the entire recording for these rare but pathognomonic findings.

---

## 3. Morphology Details (What the Agent Must See)

### 3.1 P-wave Changes
- Morphology: Normal sinus P-waves continue independently (AV dissociation); P-waves are often buried within the wide QRS-T complexes and difficult to identify
- P-wave rate is slower than QRS rate (sinus rate ~60-100 bpm vs VT rate 150-250 bpm)
- P-waves may be visible in the ST segment or T-wave as subtle distortions — the agent must look for regular deformations at the sinus rate superimposed on the VT rhythm
- In some VTs, 1:1 retrograde VA conduction occurs (each QRS is followed by a retrograde P-wave) — this eliminates AV dissociation as a diagnostic criterion and makes VT harder to distinguish from SVT

### 3.2 PR Interval Changes
- PR interval is not applicable in the traditional sense — there is no consistent temporal relationship between P-waves and QRS complexes (AV dissociation)
- When capture beats occur, the preceding P-wave has a normal PR interval (120-200 ms), and the resulting QRS is narrow
- Variable PP and RR intervals with no consistent PR relationship = AV dissociation = VT

### 3.3 QRS Complex Changes
- Duration: Wide — >120 ms (usually >140 ms). If QRS >160 ms with LBBB morphology, VT is very likely. QRS >200 ms suggests hyperkalemia or antiarrhythmic drug effect superimposed on VT.
- Morphology:
  - **RBBB-pattern VT (origin in LV):** Monophasic R or qR in V1 (NOT the typical rSR' of true RBBB). In V6: R/S <1, deep S wave, or QS pattern (NOT the typical tall R of true RBBB).
  - **LBBB-pattern VT (origin in RV or septum):** R-wave duration >30 ms in V1, notched downstroke of S-wave in V1-V2, RS interval >60 ms in V1. In V6: QS or qR pattern (true LBBB shows NO Q-waves in V5-V6).
- Amplitude: Variable; may be large or diminished depending on VT origin and underlying myocardial substrate
- Axis: Often extreme ("northwest axis" = negative in both I and aVF, between -90° and ±180°). This axis does not occur with SVT+aberrancy. Superior axis (left axis deviation beyond -30°) is also common and favors VT.
- Notching/slurring: Josephson sign = notching on the downstroke of the S-wave in V1-V2 (indicates slow myocardial conduction)

### 3.4 ST Segment Changes
- Direction: Discordant with QRS — ST segment and T-wave point in the OPPOSITE direction from the dominant QRS deflection (appropriate discordance)
- Morphology: The discordance is expected and is NOT independently diagnostic of ischemia during VT
- Concordant ST changes (ST in SAME direction as QRS) during VT are abnormal and may suggest acute ischemia as the cause of VT
- Measurement during VT is unreliable for ischemia diagnosis due to altered depolarization-repolarization sequence

### 3.5 T-wave Changes
- Direction: Discordant with QRS (opposite polarity) — this is the expected finding during VT and reflects altered repolarization sequence
- After VT terminates: T-wave inversions may persist for hours to days in the leads corresponding to the VT origin ("T-wave memory" or "cardiac memory") — this is NOT ischemia
- T-wave amplitude and morphology during VT are not independently diagnostic

### 3.6 QT/QTc Changes
- QT interval during VT is not meaningful as a standalone measurement because the QRS itself is wide and repolarization is discordant
- Pre-VT QTc is important: prolonged QTc (>500 ms) preceding polymorphic VT suggests long QT syndrome as the substrate; the VT may be Torsades de Pointes
- Post-VT QTc should be measured once sinus rhythm is restored to assess for underlying channelopathy

### 3.7 Other Features
- **Ventriculoatrial (VA) dissociation:** In some VTs, retrograde conduction produces inverted P-waves after each QRS — this is 1:1 VA conduction and does NOT exclude VT (it eliminates AV dissociation as a criterion but VT is still present)
- **Brugada criteria (sequential algorithm):**
  1. Absence of RS complex in ALL precordial leads (concordance) → VT
  2. RS interval >100 ms in any precordial lead → VT
  3. AV dissociation → VT
  4. Morphology criteria in V1-V2 and V6 → VT vs SVT
  - If all four steps are negative → SVT with aberrancy (sensitivity ~99% for VT)
- **Vereckei aVR algorithm:**
  1. Dominant initial R-wave in aVR → VT
  2. Initial r or q >40 ms in aVR → VT
  3. Notch on descending limb of negative QRS in aVR → VT
  4. Vi/Vt ratio ≤1 (initial vs terminal velocity) → VT
- **Josephson sign:** Notching near the nadir of the QRS S-wave, indicating slow conduction through scar tissue

---

## 4. Differential Diagnosis

### 4.1 Mimics (What Looks Like This But Isn't)

| Mimic Condition | Shared Features | Distinguishing Features |
|----------------|-----------------|----------------------|
| SVT with aberrancy (RBBB or LBBB) | Wide QRS tachycardia, regular rhythm | Typical BBB morphology (rSR' in V1 for RBBB, no Q in V6 for LBBB); QRS usually <140 ms; NO AV dissociation (1:1 AV relationship); preceding atrial activity visible; Brugada and Vereckei criteria negative for VT; history of prior SVT |
| SVT with pre-excitation (WPW + antidromic) | Wide QRS tachycardia, can be very wide | Delta waves may be visible; irregularity if AF with WPW; very young patient; extremely fast rate (>250 bpm with AF+WPW); prior ECGs show delta waves in sinus rhythm |
| Hyperkalemia with sinus tachycardia | Wide QRS, bizarre morphology | Sine-wave pattern; peaked T-waves; loss of P-waves; responds to calcium/insulin/glucose; check potassium level; QRS widening is progressive with worsening K+ |
| Ventricular paced rhythm | Wide QRS, regular rhythm | Pacing spikes visible before each QRS; LBBB morphology (RV pacing); left axis; pacer on chest X-ray; device history |
| Artifact (tremor, movement) | Apparent wide-complex tachycardia on one or more leads | QRS complexes visible at normal rate "marching through" the artifact; not present in all leads simultaneously; irregular amplitude and frequency inconsistent with cardiac rhythm |
| Polymorphic VT (Torsades de Pointes) vs polymorphic SVT | Wide QRS, changing morphology | True polymorphic VT: QRS rotates around baseline ("twisting of the points"), preceded by long QT, pause-dependent initiation. SVT with alternating aberrancy is extremely rare and should not be assumed. |

### 4.2 Coexisting Conditions
- **Acute MI + VT:** VT is a common complication of acute MI (both early ischemic VT and late scar-related VT). ST changes of MI may be impossible to assess during VT. After cardioversion, immediately re-assess for STEMI.
- **Heart failure + VT:** Reduced EF is the single strongest predictor of VT. VT may cause acute hemodynamic decompensation in already-compromised hearts. Post-cardioversion assessment of LV function is critical.
- **Electrolyte abnormalities + VT:** Hypokalemia, hypomagnesemia, and hypocalcemia lower the VT threshold. Must be corrected to prevent recurrence after cardioversion.
- **Drug-induced VT:** Antiarrhythmics (especially class Ia and III) can paradoxically cause VT (proarrhythmia). QT-prolonging drugs can trigger Torsades. Digoxin toxicity causes bidirectional VT (alternating RBBB and LBBB morphology — pathognomonic for dig toxicity).
- **LBBB at baseline + VT:** Pre-existing LBBB means the patient already has wide QRS at baseline. VT superimposed on LBBB produces even wider QRS (>200 ms possible) and more bizarre morphology.

---

## 5. STAT Classification

| Priority | Criteria |
|----------|----------|
| **STAT** | YES — Sustained VT is a life-threatening arrhythmia. It can degenerate to ventricular fibrillation and cardiac arrest at any moment. Even hemodynamically tolerated VT requires urgent intervention because decompensation is unpredictable. |
| **Time-sensitive** | IMMEDIATELY — Hemodynamically unstable VT (hypotension, altered consciousness, chest pain, heart failure) requires cardioversion within SECONDS to MINUTES. Stable VT should be treated within minutes, not hours. Pulseless VT is managed identically to VF with immediate defibrillation. |
| **Clinical action** | **Pulseless VT:** Immediate defibrillation (biphasic 120-200J), CPR, epinephrine, amiodarone per ACLS protocol. **Unstable VT (pulse present but hemodynamically compromised):** Immediate synchronized cardioversion (100-200J biphasic). **Stable VT (pulse present, hemodynamically stable):** IV amiodarone 150 mg over 10 min (preferred) or IV procainamide 20-50 mg/min (alternative); elective synchronized cardioversion if drugs fail. **Polymorphic VT / Torsades:** IV magnesium 2g; isoproterenol or overdrive pacing to increase heart rate and shorten QT; avoid amiodarone if long QT is the cause. **All VT:** correct electrolytes (K+ >4.0, Mg2+ >2.0), assess for acute ischemia, cardiology consultation, consider ICD evaluation. |

---

## 6. Reasoning Complexity Analysis (Feeds Into Node 2.1 — Agent Architecture Research)

> **NOTE**: This section does NOT pre-assign agents. It documents the reasoning
> complexity of this condition so that Node 2.1 can determine the BEST agent
> architecture to handle ALL conditions. The actual agent assignment is filled
> in AFTER Node 2.1 research completes.

### 6.1 Reasoning Domains Required to Detect This Condition
- **Rate analysis:** Ventricular rate measurement (150-250 bpm)
- **Rhythm regularity:** Regular (monomorphic) vs irregular (polymorphic) assessment
- **QRS duration measurement:** Wide complex identification (>120 ms, typically >140 ms)
- **QRS morphology analysis:** Atypical vs typical BBB morphology in V1, V2, V6 — this requires detailed shape analysis
- **Axis calculation:** Northwest axis detection, superior axis
- **Lead-group correlation:** Concordance detection across V1-V6
- **Interval measurement:** RS interval in precordial leads (>100 ms = VT per Brugada)
- **AV relationship analysis:** Detection of AV dissociation — P-waves independent of QRS (requires identifying low-amplitude P-waves within large QRS-T complexes)
- **Beat-specific analysis:** Capture beat and fusion beat detection — requires comparing individual beat morphologies across the recording
- **Algorithmic reasoning:** Sequential application of Brugada criteria and/or Vereckei aVR algorithm
- Cross-domain reasoning IS heavily required: rate + rhythm + morphology + axis + AV relationship + algorithmic criteria must be integrated

### 6.2 Feature Dependencies
- **ESSENTIAL features (from SDA-1):**
  - QRS duration (each beat)
  - Ventricular rate / RR interval regularity
  - QRS morphology classification per lead (V1, V2, V6, aVR especially)
  - QRS axis
  - RS interval in each precordial lead
  - P-wave detection (even within QRS-T complexes)
  - AV relationship (P:QRS ratio, PR relationship)
- **SUPPORTING features (increase confidence):**
  - Concordance across V1-V6
  - Capture beat detection (narrow QRS amid wide-complex tachycardia)
  - Fusion beat detection (intermediate morphology QRS)
  - Josephson sign (notching in S-wave nadir)
  - Vi/Vt ratio in aVR (Vereckei criterion)
  - Initial R-wave duration in aVR
  - QRS onset morphology (sharp vs slurred initial deflection)
- **EXCLUDING features (if abnormal, reconsider VT diagnosis):**
  - Typical rSR' in V1 with narrow S-wave → suggests true RBBB (SVT with aberrancy)
  - Tall R-wave in V6 without S-wave → suggests true LBBB (SVT with aberrancy)
  - Clear 1:1 AV relationship with P-waves preceding QRS → favors SVT (but does not exclude VT with 1:1 retrograde conduction)
  - QRS <120 ms → this is a narrow complex tachycardia, not VT (with rare exception of fascicular VT which can have QRS 100-120 ms)
- **Per-beat analysis REQUIRED:** Capture beats, fusion beats, and beat-to-beat morphology changes (polymorphic VT) require per-beat analysis, not just aggregate

### 6.3 Cross-Condition Interactions
- **Affects other conditions:** VT makes it impossible to reliably assess for STEMI, LVH, or other conditions until sinus rhythm is restored. Post-cardioversion ECG must be immediately reassessed for underlying pathology.
- **Requires ruling out:** SVT with aberrancy (the primary differential — Brugada/Vereckei criteria), hyperkalemia (check potassium), ventricular pacing (check for pacing spikes), artifact (check all leads for QRS marching through)
- **Condition combinations that change interpretation:**
  - VT + WPW: Pre-excited AF can mimic VT; irregularity and varying QRS morphology favor AF+WPW; procainamide is safe for both, but verapamil/digoxin can be lethal if WPW
  - VT + acute MI: VT may be the presenting rhythm of acute MI; post-cardioversion STEMI assessment is mandatory
  - Polymorphic VT + long QT: This is Torsades de Pointes — treatment is different (magnesium, pacing, isoproterenol; NOT amiodarone)
  - Bidirectional VT + digoxin: Beat-to-beat alternation of RBBB and LBBB morphology is pathognomonic for digoxin toxicity

### 6.4 Reasoning Chain Sketch
- **Minimum reasoning chain (fewest steps to high confidence):**
  1. Detect wide QRS tachycardia (QRS >120 ms, rate >100 bpm)
  2. Identify AV dissociation OR capture beats OR fusion beats → VT (pathognomonic)
  3. If pathognomonic signs absent → apply Brugada criteria sequentially
  4. VT confirmed → STAT alert

- **Full reasoning chain (complete evidence assembly):**
  1. Measure QRS duration in multiple leads; confirm >120 ms (>140 ms strengthens diagnosis)
  2. Measure ventricular rate; confirm tachycardia (>100 bpm, typically 150-250)
  3. Assess regularity: regular → monomorphic VT; irregular → polymorphic VT or AF with aberrancy/pre-excitation
  4. Search for P-waves independent of QRS → AV dissociation (if found → VT, stop)
  5. Search for capture beats (narrow QRS amid wide) → pathognomonic for VT (if found → VT, stop)
  6. Search for fusion beats (intermediate morphology) → pathognomonic for VT (if found → VT, stop)
  7. Apply Brugada Step 1: Check for concordance in V1-V6 → if positive concordance → VT
  8. Apply Brugada Step 2: Measure RS interval in precordial leads → if >100 ms in any → VT
  9. Apply Brugada Step 3: AV dissociation (already checked in step 4)
  10. Apply Brugada Step 4: Morphology criteria in V1/V2 and V6 → assess for typical vs atypical BBB pattern
  11. Apply Vereckei aVR algorithm as confirmatory
  12. Assess axis: northwest axis → VT
  13. Assess for Torsades (polymorphic + long preceding QT + pause-dependent)
  14. Assess for bidirectional VT (alternating axis → digoxin toxicity)
  15. Classify: sustained VT → STAT alert

### 6.5 Confidence Anchors
- **HIGH confidence features:**
  - AV dissociation (independent P-wave rate) — virtually 100% specific for VT
  - Capture beats — pathognomonic
  - Fusion beats — pathognomonic
  - Positive concordance in V1-V6 — >95% specific for VT
  - Northwest axis (negative in I and aVF) — does not occur with SVT+aberrancy
- **LOW confidence (if absent, consider alternatives):**
  - Absence of AV dissociation does NOT exclude VT (30% of VT has 1:1 retrograde VA conduction)
  - Typical BBB morphology → favors SVT with aberrancy
  - QRS 120-140 ms → borderline; could be VT with fascicular origin or SVT with aberrancy
  - Regular rhythm with clear P:QRS relationship → favors SVT
- **Pathognomonic combination:** AV dissociation + capture beats + fusion beats + wide QRS >140 ms = 100% VT
- **Classification thresholds:**
  - "Possible" VT: wide QRS tachycardia without pathognomonic features; Brugada/Vereckei equivocal
  - "Probable" VT: wide QRS tachycardia with ≥2 Brugada criteria positive OR northwest axis OR concordance
  - "Definite" VT: pathognomonic features (AV dissociation, capture beats, or fusion beats) OR all Brugada criteria positive

### 6.6 Difficulty Score
| Dimension | Score (1-5) | Notes |
|-----------|-------------|-------|
| Signal clarity needed | 4 | P-wave detection within wide QRS-T complexes requires high signal quality; capture/fusion beats are subtle and may be obscured by noise; RS interval measurement needs clean signal |
| Number of leads required | 5 | Full 12-lead required: V1-V6 for concordance and morphology, aVR for Vereckei, II/aVF for axis, all leads for AV dissociation assessment |
| Cross-domain reasoning | 5 | Requires simultaneous integration of rate, rhythm, QRS duration, morphology, axis, AV relationship, concordance, RS interval, and algorithmic criteria — the most cross-domain-intensive condition |
| Temporal pattern complexity | 4 | Per-beat analysis needed for capture/fusion beats, polymorphic morphology changes, and AV dissociation; monomorphic VT is constant but detecting the rare capture/fusion beat requires scanning all beats |
| Differential complexity | 5 | SVT with aberrancy is the primary mimic and requires systematic algorithmic exclusion (Brugada, Vereckei); multiple other mimics (hyperkalemia, paced rhythm, artifact, pre-excitation); polymorphic VT vs Torsades adds another layer |
| Rarity in PTB-XL | 3 | VT is present in PTB-XL but sustained VT recordings are limited; short VT runs (NSVT) are more common; polymorphic VT and Torsades are rare in the dataset |
| **Overall difficulty** | **4.3** | **High — VT detection requires the most comprehensive cross-domain reasoning of any arrhythmia, with multiple algorithmic criteria and per-beat analysis** |

---

## 6A. Agent Assignment

**Architecture:** Option E — 3 Parallel Phase 1 Specialists + 1 Sequential CDS (Node 2.1 Gate Passed 2026-03-27)

| Agent | Role for Ventricular Tachycardia | Key Features Used |
|-------|--------------------------|-------------------|
| **RRC** (Rhythm/Rate/Conduction) | Primary | Wide QRS tachycardia (QRS ≥120 ms) at 150–250 bpm, AV dissociation (independent P-wave rate slower than QRS rate), fusion beats (intermediate morphology QRS), capture beats (narrow conducted QRS during tachycardia), regular or slightly irregular RR intervals, concordance in V1 identification |
| **IT** (Ischemia/Territory) | Supporting | ST changes during VT are not interpretable as primary ischemia; flags if baseline ischemic pattern was present before tachycardia onset; suppresses territorial STEMI calls during active wide-QRS tachycardia |
| **MR** (Morphology/Repolarization) | Supporting | QRS morphology in V1 (LBBB vs RBBB pattern of VT), axis in frontal plane (extreme right or northwest axis supports VT), QRS width (>160 ms strongly favors VT), R-wave in aVR (initial broad R favors VT), Brugada VT criteria morphology (V1: broad monophasic R or qR; V6: rS), concordance pattern (all precordial leads same polarity) |
| **CDS** (Cross-Domain Synthesis) | Required — CRITICAL: VT vs SVT+aberrancy differentiation | Integrates RRC's rhythm analysis (AV dissociation, fusion/capture beats) with MR's morphology analysis (Brugada algorithm, aVR criteria, axis, QRS width); applies Brugada 4-step algorithm and Vereckei aVR criteria; generates final VT vs SVT+aberrancy determination with confidence score |

### Primary Agent
**RRC** — ventricular tachycardia is a rhythm diagnosis defined by wide QRS tachycardia with AV dissociation, which is primarily in the RRC domain; however, MR morphology analysis is essential for the VT vs SVT+aberrancy differentiation.

### Cross-Domain Hints
- RRC emits `cross_domain_hint: "Wide QRS tachycardia detected (QRS ≥120 ms, rate 150–250 bpm) — MR QRS morphology analysis required for Brugada algorithm application and VT vs SVT differentiation"` when wide-QRS tachycardia is identified.
- MR emits `cross_domain_hint: "Extreme axis deviation (northwest axis) or concordance pattern detected during wide-QRS tachycardia — strongly supports VT; forward to CDS for algorithmic confirmation"` when these morphology features are present.

### CDS Specific Role
CDS performs the definitive VT vs SVT+aberrancy differentiation by applying the Brugada 4-step algorithm: (1) absence of RS in precordial leads → VT; (2) RS interval >100 ms in any precordial lead → VT; (3) AV dissociation from RRC → VT; (4) LBBB/RBBB morphology criteria from MR → VT or SVT. CDS also applies the Vereckei aVR criterion (initial R-wave ≥40 ms or notched downstroke favors VT). Final output is a VT confidence score with the specific algorithm step that clinched the diagnosis, enabling downstream explanation generation.

---

## 7. RAG Knowledge Requirements

### 7.1 Textbook References
- **Marriott's Practical Electrocardiography (13th ed.):** Chapter on ventricular arrhythmias — comprehensive coverage of VT morphology criteria, Brugada algorithm, and Vereckei algorithm with illustrated examples
- **Goldberger's Clinical Electrocardiography (10th ed.):** Chapter on wide-complex tachycardias — practical approach to VT vs SVT differential
- **Chou's Electrocardiography in Clinical Practice (7th ed.):** Chapter on ventricular tachycardia — detailed morphology criteria with sensitivity/specificity data for each criterion
- **Brugada P et al.** "A new approach to the differential diagnosis of a regular tachycardia with a wide QRS complex." Circulation. 1991;83(5):1649-1659 — the original Brugada criteria paper
- **Vereckei A et al.** "New algorithm using only lead aVR for differential diagnosis of wide QRS complex tachycardia." Heart Rhythm. 2008;5(1):89-98

### 7.2 Key Figures
- Brugada criteria flowchart: step-by-step decision algorithm with example ECGs at each branch
- VT vs SVT morphology comparison: side-by-side V1 and V6 tracings showing typical RBBB/LBBB vs atypical morphology in VT
- AV dissociation, capture beat, and fusion beat examples: annotated rhythm strips with arrows
- Concordance examples: positive and negative concordance across V1-V6
- Dashboard should show: full 12-lead display with QRS duration measurement, rhythm strip (lead II or V1) highlighting AV dissociation/capture/fusion beats, Brugada criteria checklist, Vereckei aVR analysis panel

---

## 8. Dashboard Visualization Specification

### 8.1 Highlighted Leads
- **Primary display (large):** V1, V6, aVR — the three key morphology analysis leads
- **Secondary display:** Lead II rhythm strip (continuous) — for AV dissociation, capture, and fusion beat visualization
- **Full 12-lead display:** Required for concordance and axis assessment
- Color coding: Wide QRS complexes in red; P-waves (if identified) in blue with marker arrows; capture beats in green; fusion beats in yellow; RS interval measurement zone in orange

### 8.2 Arrows and Annotations
- Arrow at V1 QRS: label "Wide QRS >140 ms — [RBBB/LBBB] pattern"
- Caliper marking on QRS: label "QRS duration: XXX ms"
- If AV dissociation detected: P-wave markers (blue arrows) on rhythm strip; label "AV dissociation — P-wave rate XX bpm, QRS rate YYY bpm"
- If capture beat detected: green arrow; label "CAPTURE BEAT — pathognomonic for VT"
- If fusion beat detected: yellow arrow; label "FUSION BEAT — pathognomonic for VT"
- Concordance indicator: V1-V6 QRS polarity summary bar; label "Positive/Negative concordance"
- Brugada criteria sidebar: checkboxes for each step with pass/fail
- Vereckei aVR sidebar: stepwise analysis with result
- Banner: "VENTRICULAR TACHYCARDIA — STAT" with hemodynamic assessment prompt

### 8.3 Clinician Explanation (Plain Language)
- **ER nurse (2-3 sentences):** "This ECG shows ventricular tachycardia — a dangerously fast heart rhythm starting in the lower chambers. The heart rate is approximately XXX and the wide QRS pattern confirms the rhythm is coming from the ventricles, not the normal conduction system. Check the patient's blood pressure and consciousness immediately — if unstable, prepare for cardioversion."
- **Cardiologist (expanded):** "Wide-complex tachycardia at XXX bpm with [monomorphic/polymorphic] morphology. QRS duration XXX ms with [RBBB/LBBB] pattern. [AV dissociation identified / Concordance present / Brugada criteria positive at step X / Vereckei positive at step X]. [Capture/fusion beats identified — pathognomonic]. Axis: [superior/northwest/normal]. Diagnosis: sustained ventricular tachycardia. Recommend: [hemodynamic assessment → cardioversion if unstable; IV amiodarone if stable]. Post-conversion: assess for underlying substrate (ischemia, cardiomyopathy, channelopathy), check electrolytes, cardiology consultation for ICD evaluation."

---

## 9. Edge Cases and Pitfalls

- **THE cardinal rule:** Wide complex tachycardia = VT until proven otherwise. Treating VT as SVT (giving verapamil or adenosine) can cause cardiovascular collapse and death. The reverse (treating SVT as VT with cardioversion) is safe. When in doubt, treat as VT.
- **Fascicular VT (idiopathic LV VT):** QRS may be relatively narrow (100-140 ms) with RBBB + left axis pattern. This is VT from the left posterior fascicle. The narrow QRS can mislead the agent into calling it SVT. The RBBB+left axis combination at a fast rate in a young patient should raise suspicion.
- **RVOT VT (idiopathic outflow tract VT):** LBBB morphology + inferior axis. This occurs in structurally normal hearts and can mimic SVT with LBBB aberrancy. The inferior axis (positive in II, III, aVF) helps distinguish from most scar-related VTs but does not distinguish from SVT.
- **Bundle branch re-entry VT:** Uses the His-Purkinje system, so QRS may look like typical LBBB (because the LBB is the antegrade limb). This VT can fool Brugada criteria because the morphology IS typical BBB. AV dissociation or clinical context (dilated cardiomyopathy) is key.
- **Artifact mimicking VT:** Tremor artifact (especially Parkinson's) can simulate wide-complex tachycardia. The key: sinus QRS complexes can be seen "marching through" the artifact at a normal rate, and the artifact is usually not present in all leads simultaneously.
- **Rate-dependent BBB:** Sinus tachycardia that reaches a critical rate and develops rate-dependent LBBB or RBBB. The wide QRS develops abruptly when a critical rate is reached. Regular narrow complexes precede the wide complexes; there is a clear rate threshold.
- **Very fast VT (>250 bpm):** At very high rates, QRS complexes may merge with T-waves creating a sinusoidal pattern ("pre-VF VT"). This may be difficult to distinguish from VF. Regular periodicity favors VT; chaotic irregularity favors VF.
- **Antidromic AVRT (WPW):** Wide QRS tachycardia using an accessory pathway antegradely. Young patient, very fast rate, delta waves may be visible. History of WPW is key. Procainamide is safe; AV nodal blockers are contraindicated.
- **Post-cardioversion assessment:** Always obtain a 12-lead ECG immediately after restoring sinus rhythm. Assess for STEMI, Brugada pattern, long QT, pre-excitation, or structural heart disease clues that indicate the VT substrate.

---

## 10. References
- Al-Khatib SM, Stevenson WG, Ackerman MJ, et al. 2017 AHA/ACC/HRS Guideline for Management of Patients With Ventricular Arrhythmias and the Prevention of Sudden Cardiac Death. J Am Coll Cardiol. 2018;72(14):e91-e220.
- Zeppenfeld K, Tfelt-Hansen J, de Riva M, et al. 2022 ESC Guidelines for the management of patients with ventricular arrhythmias and the prevention of sudden cardiac death. Eur Heart J. 2022;43(40):3997-4126.
- Brugada P, Brugada J, Mont L, Smeets J, Andries EW. A new approach to the differential diagnosis of a regular tachycardia with a wide QRS complex. Circulation. 1991;83(5):1649-1659.
- Vereckei A, Duray G, Szénási G, Altemose GT, Miller JM. New algorithm using only lead aVR for differential diagnosis of wide QRS complex tachycardia. Heart Rhythm. 2008;5(1):89-98.
- Wellens HJJ. Electrophysiology: Ventricular tachycardia — diagnosis of broad QRS complex tachycardia. Heart. 2001;86(5):579-585.
- Goldberger AL, Goldberger ZD, Shvilkin A. Goldberger's Clinical Electrocardiography: A Simplified Approach. 10th ed. Elsevier; 2024.
- Surawicz B, Knilans TK. Chou's Electrocardiography in Clinical Practice. 7th ed. Saunders; 2020.
- Wagner GS, Strauss DG. Marriott's Practical Electrocardiography. 13th ed. Wolters Kluwer; 2022.
- Jastrzebski M, Kukla P, Czarnecka D, Kawecka-Jaszcz K. Comparison of five electrocardiographic methods for differentiation of wide QRS-complex tachycardias. Europace. 2012;14(8):1165-1171.
- Issa ZF, Miller JM, Zipes DP. Clinical Arrhythmology and Electrophysiology: A Companion to Braunwald's Heart Disease. 3rd ed. Elsevier; 2019.
