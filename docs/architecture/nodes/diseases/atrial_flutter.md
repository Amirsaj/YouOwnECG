# Atrial Flutter — ECG Manifestation from First Principles

**Node:** 2.7.25
**SDA:** SDA-2 (Diagnosis & Agentic Core) — shared resource for SDA-1, SDA-3, SDA-4
**Status:** Complete
**PGMR:** Required
**Date:** 2026-03-26

---

## 1. Pathophysiology Root Cause

### 1.1 What Goes Wrong (Anatomy/Physiology)
- **Typical (type I) atrial flutter**: A single macro-reentrant circuit in the right atrium, traveling counterclockwise (when viewed from below) around the tricuspid annulus. The circuit uses:
  - The cavotricuspid isthmus (CTI) as the critical slow-conduction zone (between the tricuspid valve annulus and the inferior vena cava)
  - The crista terminalis as the lateral barrier
  - The interatrial septum as the medial limb
  - The circuit completes one full loop in ~200 ms, generating an atrial rate of ~300/min (range 250–350/min)
- **Reverse typical (clockwise) flutter**: Same circuit, opposite direction — clockwise around the tricuspid annulus. Still uses the CTI as the critical isthmus.
- **Atypical (type II) atrial flutter**: Macro-reentrant circuits NOT dependent on the CTI. Can occur in:
  - Left atrium (especially post-ablation or post-cardiac surgery — circuits around scar tissue or pulmonary veins)
  - Right atrium around non-CTI barriers (crista terminalis, surgical scars)
  - Rates may be faster (300–350/min) or slower (200–250/min) depending on circuit size and conduction velocity
- **AV node conduction**: The AV node cannot conduct at 300/min. It typically conducts every 2nd flutter wave (2:1 block → ventricular rate ~150 bpm). Higher degrees of block (3:1, 4:1) occur with drugs, vagal tone, or AV nodal disease. Variable block (alternating 2:1 and 4:1) is common.
- **Atrial flutter requires a macro-reentrant circuit with a defined anatomical boundary** — this distinguishes it from AFib (which has multiple random wavelets) and focal atrial tachycardia (which has a point source).

### 1.2 Electrical Consequence
- **Organized atrial depolarization at ~300/min**: Unlike AFib's chaotic activity, flutter produces identical, regularly spaced atrial depolarization waves (F-waves or flutter waves). Each circuit loop generates one complete F-wave.
- **Continuous atrial depolarization**: There is no isoelectric baseline between flutter waves — the atria are continuously depolarizing (one part is being activated while another is recovering). This creates the characteristic "sawtooth" pattern without a flat baseline.
- **AV conduction is typically fixed-ratio**: 2:1 (most common), 3:1, 4:1, or variable. With 2:1 block, the ventricular rate locks at ~150 bpm (half of 300). This fixed-ratio conduction creates a regular or regularly irregular ventricular rhythm.
- **QRS is unaffected**: Ventricular depolarization via the His-Purkinje system is normal — narrow QRS (unless pre-existing BBB or rate-related aberrancy).
- **F-wave vector in typical flutter**: The counterclockwise circuit creates a wavefront that descends the right atrial free wall (anterior) and ascends the septum (posterior). The net atrial vector during the downward limb points superiorly and rightward → negative deflection in inferior leads (II, III, aVF). In V1, the vector is directed anteriorly → upright F-waves.

### 1.3 Why It Appears on ECG
- **Sawtooth pattern in inferior leads**: The counterclockwise circuit's descending limb creates a dominant superior vector → negative (downward) F-wave deflection in leads II, III, aVF. The ascending septal limb then creates an inferior vector → upward return. Because the circuit is continuous, these deflections merge into a smooth sawtooth without return to baseline.
- **V1 shows upright F-waves**: The anterior vector from the right atrial free wall points toward V1 → upright, often sharper flutter waves. V1 is the best precordial lead for identifying flutter waves, especially when they are hidden within the QRS or T-wave.
- **2:1 conduction hides every other F-wave**: At 2:1 block, one F-wave falls between QRS complexes (visible) and one F-wave is buried within or near the QRS/T-wave (hidden). Only one "bump" is visible between QRS complexes, which may be mistaken for a P-wave or T-wave. This is the classic trap of 2:1 flutter at ~150 bpm.
- **Higher degrees of block reveal more F-waves**: At 4:1, three F-waves are visible between QRS complexes, making the diagnosis obvious. Adenosine or carotid sinus massage transiently increases AV block, revealing hidden flutter waves — a key diagnostic maneuver.

---

## 2. ECG Presentation — Lead by Lead

### 2.1 Diagnostic Criteria (2025 AHA/ESC Guidelines)

| Criterion | Threshold | Source |
|-----------|-----------|--------|
| Flutter waves (F-waves) | Regular, organized atrial activity at 250–350/min (typically ~300/min) | ESC 2024; ACC/AHA 2023 |
| Sawtooth pattern | Continuous undulating baseline without isoelectric line between F-waves, best seen in II, III, aVF | ESC 2024 |
| AV conduction ratio | Fixed or variable; commonly 2:1, 3:1, 4:1 | ACC/AHA 2023 |
| Typical flutter: F-wave polarity | Negative (inverted) in II, III, aVF; upright in V1 | ESC 2024 Electrophysiology supplement |
| Atypical flutter: F-wave polarity | Variable — may be upright in inferior leads; morphology depends on circuit location | ESC 2024 |
| Ventricular rhythm | Regular (fixed conduction ratio) or regularly irregular (variable block ratio) | Standard criteria |

### 2.2 Lead-by-Lead Manifestation

| Lead | Expected Finding | Why (Vector Explanation) | Sensitivity |
|------|-----------------|------------------------|-------------|
| I | F-waves low amplitude; may be difficult to see; rhythm regular or regularly irregular | Lead I (0° axis) is nearly perpendicular to the dominant superior-inferior flutter vector; F-waves project minimally | Low for F-waves; moderate for rhythm |
| II | **Classic sawtooth pattern** — negative (inverted) F-waves in typical flutter; continuous undulation without isoelectric baseline | Lead II (+60°) is well-aligned with the dominant superior-inferior atrial vector; the descending wavefront along the RA free wall creates a prominent negative deflection | **Highest** — most diagnostic lead for typical flutter |
| III | Sawtooth pattern — negative F-waves; slightly different morphology from II; often sharper | Lead III (+120°) also aligned with the inferior vector; records more right-sided atrial activity | High |
| aVR | Upright (positive) F-waves — mirror image of inferior lead pattern | aVR (-150°) records the opposite direction of II/III/aVF; flutter waves appear inverted relative to inferior leads | Moderate — useful for confirmation |
| aVL | F-waves low amplitude; may be flat or slightly positive | aVL (-30°) is relatively perpendicular to the flutter circuit vector; minimal projection | Low |
| aVF | **Prominent sawtooth pattern** — negative F-waves in typical flutter; continuous undulation | aVF (+90°) perfectly captures the superior-inferior atrial vector; alongside II, the best inferior lead for flutter | **Highest** — co-equal with II for diagnostic sensitivity |
| V1 | **Upright, discrete F-waves** — often sharper and more distinct than the sawtooth in inferior leads; may appear as rapid, regular upright deflections at ~300/min | V1 overlies the right atrium; the anterior vector of the flutter circuit projects directly toward V1. The F-waves in V1 often look different from the sawtooth (more peaked, less undulating) | **High** — best precordial lead; often reveals flutter waves hidden in other leads. Critical when 2:1 block obscures the pattern in inferior leads |
| V2 | F-waves visible but lower amplitude than V1; upright or biphasic | Slightly further from RA; still good atrial activity recording | Moderate-High |
| V3 | F-waves diminishing; may be subtle | Transitional zone — ventricular signals dominate | Moderate |
| V4 | F-waves usually subtle or hidden within larger QRS/T-wave complexes | Over LV apex — atrial signals overwhelmed by ventricular | Low |
| V5 | F-waves rarely discernible; rhythm regularity is the main clue | Lateral precordial — far from atrial structures | Low |
| V6 | F-waves rarely discernible | Most lateral — minimal atrial signal | Low |

### 2.3 Key Leads (Most Diagnostic)
- **II and aVF**: Best leads for the classic sawtooth pattern of typical flutter. The negative, continuous undulating F-waves without return to baseline are pathognomonic.
- **V1**: Best precordial lead — upright, discrete F-waves often visible even when the sawtooth is obscured in inferior leads. Critical for confirming the diagnosis when 2:1 conduction hides flutter waves.
- **III**: Complementary to II — sometimes shows cleaner F-waves due to slightly different axis.
- **Diagnostic combination**: II + aVF + V1 is sufficient for flutter diagnosis in >95% of cases.

### 2.4 Beat-by-Beat Considerations
- **Variable conduction ratios**: The most diagnostically important beat-by-beat feature. Alternating 2:1 and 4:1 conduction (or 2:1 and 3:1) creates a "regularly irregular" rhythm with clustered RR intervals. Unlike AFib (random variation), flutter RR intervals cluster at multiples of the flutter cycle length (~200 ms: 400 ms for 2:1, 600 ms for 3:1, 800 ms for 4:1).
- **Fixed 2:1 conduction**: All beats are identical — regular rhythm at ~150 bpm. This is the "trap" pattern where flutter waves are hardest to see. Each RR interval is ~400 ms.
- **Concealed F-waves during 2:1 block**: One F-wave falls in the T-wave of the preceding beat, distorting T-wave morphology. Look for a "notch" or "bump" in the T-wave — this may be the hidden F-wave.
- **After adenosine**: Transient increase to 4:1 or higher block reveals 3+ F-waves between QRS complexes, making the sawtooth pattern unmistakable. This is a one-time diagnostic view — document/print the strip during the adenosine effect.
- **Aberrant beats**: Less common than in AFib (because the rhythm is more regular), but can occur with sudden changes in conduction ratio.

---

## 3. Morphology Details (What the Agent Must See)

### 3.1 P-wave Changes
- **Morphology**: Absent — replaced by flutter waves (F-waves). F-waves are regular, identical, organized atrial depolarization waves at ~300/min. They are NOT P-waves.
  - **Typical (counterclockwise) flutter**: F-waves are negative (inverted) in II, III, aVF with a gradual downslope and sharp upstroke (sawtooth); upright in V1
  - **Reverse typical (clockwise) flutter**: F-waves are positive (upright) in II, III, aVF with a gradual upslope and sharp downstroke; often negative in V1
  - **Atypical flutter**: F-wave morphology varies based on the circuit — may be positive, negative, or biphasic in any lead. Rate may differ from 300/min.
- **Duration change**: Not applicable — continuous depolarization, no discrete atrial wave
- **Axis change**: Fixed (determined by circuit direction). Typical = superior axis (negative inferior leads). Reverse typical = inferior axis (positive inferior leads).

### 3.2 PR Interval Changes
- **Duration**: Not a true PR interval — the interval from the onset of an F-wave to the subsequent QRS depends on which F-wave conducts and the AV nodal conduction time
- **Pattern**: The F-wave to QRS relationship is fixed at a given conduction ratio (e.g., every 2nd F-wave conducts with a constant F-R interval)

### 3.3 QRS Complex Changes
- **Duration**: Narrow (<120 ms) in uncomplicated flutter. Wide QRS with:
  - Pre-existing BBB
  - Rate-related aberrancy (less common than in AFib due to more regular rhythm)
  - Pre-excited flutter (WPW) — wide, regular, very rapid; dangerous
  - 1:1 conduction (rate ~300 bpm, usually drug-induced): may cause QRS widening from sodium channel blockade
- **Morphology**: Normal unless aberrancy or pre-excitation. F-waves may distort the initial or terminal portion of the QRS, mimicking small q-waves or S-wave changes.
- **Amplitude**: Normal — flutter does not intrinsically alter QRS voltage
- **Axis**: Normal — flutter does not shift the QRS axis

### 3.4 ST Segment Changes
- **Direction**: F-waves are continuously superimposed on the ST segment. This creates pseudo-ST depression (the descending limb of the F-wave) that can mimic ischemic ST depression — a critical pitfall.
- **Morphology**: The "ST depression" in flutter is actually the downsloping limb of the F-wave. It follows the flutter wave periodicity, not the cardiac cycle.
- **Measurement point**: True ST segment analysis in flutter requires mentally "subtracting" the flutter wave from the baseline. This is extremely difficult. If STEMI is suspected with flutter, treat based on clinical picture and serial troponins.
- **Critical note**: Flutter waves can create apparent ST depression of 1–3 mm, especially in inferior leads, that is entirely artifact of the flutter wave superimposition. Do NOT diagnose ischemia based on ST depression during flutter.

### 3.5 T-wave Changes
- **Direction**: T-waves are deformed by superimposed F-waves. In 2:1 flutter, one F-wave is embedded in the T-wave, changing its morphology (often creating a notch or bump).
- **Amplitude**: T-wave amplitude assessment is unreliable during flutter — the F-wave contamination alters apparent T-wave height.
- **Symmetry**: Not assessable due to F-wave superimposition.
- **Specific patterns**: The "notched T-wave" in 2:1 flutter is a hidden F-wave, not a primary T-wave abnormality. Comparing T-wave morphology at different conduction ratios (if available) can help distinguish F-wave contamination from true T-wave changes.

### 3.6 QT/QTc Changes
- **QT measurement in flutter**: Extremely difficult due to F-wave superimposition on the ST-T complex. The end of the T-wave is obscured by the beginning of the next F-wave.
- **Recommended approach**: If QT measurement is clinically necessary, assess after conversion to sinus rhythm, or during transient higher-degree block (after adenosine) when more baseline is visible.
- **Clinical significance**: QT assessment is a secondary concern in flutter — rate control or rhythm control is the immediate priority.

### 3.7 Other Features
- **Flutter-fibrillation (flutter-fib)**: Transitional rhythm where organized flutter degenerates into fibrillation or vice versa — segments of regular F-waves interspersed with chaotic f-waves. Common, as flutter and AFib often coexist.
- **1:1 conduction**: Extremely dangerous — ventricular rate of ~300 bpm. Occurs with sympathetic activation, class IC antiarrhythmics (flecainide, propafenone) that slow the atrial rate to ~200/min without blocking AV conduction, or in WPW. QRS may be wide due to rate-dependent aberrancy. Can degenerate to VF.
- **Concealed flutter waves**: In 2:1 conduction, half the F-waves are hidden. The only visible clue may be a subtle distortion of the ST segment or T-wave.

---

## 4. Differential Diagnosis

### 4.1 Mimics (What Looks Like This But Isn't)

| Mimic Condition | Shared Features | Distinguishing Features |
|----------------|-----------------|----------------------|
| Sinus tachycardia at 150 bpm | Regular rate at ~150 bpm; P-waves may be hard to see in the T-wave at this rate | Sinus P-waves are upright in II and have consistent morphology; carotid massage or adenosine will gradually slow sinus tach (no sudden "unmasking"). Flutter at 2:1 will suddenly reveal 300/min F-waves with adenosine. **Rule: any regular narrow-complex tachycardia at ~150 bpm is flutter until proven otherwise.** |
| Atrial fibrillation | Both are atrial arrhythmias; coarse AFib can mimic flutter | AFib: irregularly irregular RR intervals, no repeating F-wave morphology. Flutter: regular or regularly irregular RR, identical F-waves at ~300/min. The key difference is organization and regularity of atrial activity. |
| Multifocal atrial tachycardia (MAT) | May have variable rate; multiple atrial deflections visible | MAT: ≥3 distinct P-wave morphologies, each preceding a QRS with a PR interval; rate usually 100–150 bpm; rhythm is irregularly irregular. Flutter: single F-wave morphology at ~300/min. |
| Atrial tachycardia with 2:1 block | Regular rhythm with organized atrial activity faster than ventricular rate | Atrial tachycardia: discrete P-waves with isoelectric baseline between them; atrial rate usually 150–250/min (slower than flutter). Flutter: continuous sawtooth without isoelectric baseline; rate ~300/min. |
| SVT (AVNRT/AVRT) | Regular narrow-complex tachycardia at 150–180 bpm | SVT: no visible atrial activity between QRS (retrograde P-waves buried in QRS or just after). Flutter: F-waves are visible (at least in V1) if you look carefully. Adenosine terminates SVT but only transiently increases AV block in flutter. |
| Sinus rhythm with artifact | Baseline oscillations from tremor can mimic flutter waves | Artifact: affects all leads, non-physiological frequency, QRS complexes remain undistorted. Flutter: F-waves are lead-specific (negative inferior, positive V1) and maintain constant rate/morphology. |

### 4.2 Coexisting Conditions
- **Flutter + LBBB**: Wide QRS with LBBB morphology at regular rate. Must distinguish from ventricular tachycardia (regular wide-complex tachycardia). Key: F-waves visible in V1 or inferior leads confirm flutter; AV dissociation would favor VT.
- **Flutter + WPW (pre-excited flutter)**: The accessory pathway can conduct at near-1:1 ratios → extremely fast, wide-complex, regular tachycardia at 250–300 bpm. Similar danger to pre-excited AFib. **NEVER give AV nodal blockers.** Treat with procainamide or cardioversion.
- **Flutter + STEMI**: F-wave superimposition makes ST elevation assessment very difficult. ST elevation that exceeds the expected F-wave amplitude in the appropriate territory should raise concern. Serial troponins are essential.
- **Flutter + class IC antiarrhythmics**: Flecainide or propafenone can slow the atrial rate from 300 to 200/min. If AV conduction is not simultaneously blocked (with a beta-blocker or calcium channel blocker), 1:1 conduction at 200 bpm can occur — hemodynamic collapse risk. **Always co-prescribe an AV nodal blocker when using class IC drugs for flutter.**
- **Flutter-fibrillation coexistence**: Very common. A tracing may show segments of organized flutter alternating with fibrillatory segments. Report both rhythms. The clinical management implications differ (flutter is curable with CTI ablation; AFib is not).

---

## 5. STAT Classification

| Priority | Criteria |
|----------|----------|
| **STAT** | Flutter with 1:1 conduction (rate ~250–300 bpm) — hemodynamic collapse risk. Pre-excited flutter (WPW) — VF risk. Flutter with hemodynamic instability at any rate. New flutter + STEMI (dual emergency). |
| **Time-sensitive** | Flutter with RVR (2:1 at ~150 bpm) causing symptoms — rate control needed within 30–60 minutes. New-onset flutter — identify within minutes for appropriate management. Duration <48 hours relevant for cardioversion decision. |
| **Clinical action** | (1) Rate control: beta-blockers or calcium channel blockers (NOT in pre-excited flutter; NOT class IC drugs without AV nodal blocker). (2) Anticoagulation: same CHA₂DS₂-VASc criteria as AFib — stroke risk is equivalent. (3) Rhythm control: electrical cardioversion (low energy, 50–100 J, often successful); pharmacological cardioversion (ibutilide). (4) Definitive therapy: CTI ablation for typical flutter (>95% success, low recurrence — discuss referral). (5) Hemodynamically unstable → immediate synchronized cardioversion. |

---

## 6. Reasoning Complexity Analysis (Feeds Into Node 2.1 — Agent Architecture Research)

> **NOTE**: This section does NOT pre-assign agents. It documents the reasoning
> complexity of this condition so that Node 2.1 can determine the BEST agent
> architecture to handle ALL conditions. The actual agent assignment is filled
> in AFTER Node 2.1 research completes.

### 6.1 Reasoning Domains Required to Detect This Condition
- **Atrial activity morphology analysis** (PRIMARY): Detect organized, regular, sawtooth F-waves at ~300/min. Requires frequency analysis of the baseline between QRS complexes and within the T-wave region. Template matching of F-wave morphology is key — all F-waves should be identical.
- **Rhythm regularity analysis** (PRIMARY): Assess ventricular rate regularity. Flutter produces regular or regularly irregular rhythm (RR intervals cluster at multiples of flutter cycle length). This differs from AFib's random irregularity.
- **Rate analysis** (PRIMARY): Calculate ventricular rate. Rate ~150 bpm should trigger specific "consider flutter" logic.
- **Lead-group correlation** (SUPPORTING): Confirm F-wave polarity is consistent across lead groups — negative in inferior leads + positive in V1 = typical flutter. Inconsistent polarity may suggest atypical flutter.
- **Cross-domain reasoning** (for combinations): Flutter + WPW, flutter + class IC drugs, flutter + STEMI all require multi-domain analysis.
- **Sequential reasoning**: "IF regular rate ~150 AND narrow QRS THEN search specifically for flutter waves hidden in ST-T complex."

### 6.2 Feature Dependencies
- **ESSENTIAL computed features (from SDA-1)**:
  - All RR intervals and their statistics (mean, SD, CV)
  - Atrial activity frequency in baseline segments (target: 250–350/min = ~4–6 Hz)
  - F-wave morphology template in V1 and II (shape, amplitude, regularity)
  - F-wave regularity: coefficient of variation of F-F intervals (<5% = organized flutter)
  - QRS duration (narrow vs wide)
  - Ventricular rate
- **SUPPORTING features**:
  - F-wave polarity in inferior leads (negative = typical, positive = reverse typical)
  - AV conduction ratio (2:1, 3:1, 4:1, variable)
  - T-wave morphology assessment (detect concealed F-waves as T-wave notching)
  - ST segment analysis (for coexisting STEMI, with F-wave contamination caveat)
- **EXCLUSION features** (if present, flutter less likely):
  - Irregularly irregular RR intervals with random distribution (favors AFib)
  - Identifiable sinus P-waves with consistent morphology and normal axis (favors sinus rhythm)
  - No organized atrial activity at 250–350/min frequency (excludes flutter)
  - Isoelectric baseline between atrial waves (favors focal atrial tachycardia, not flutter)
- **Per-beat vs aggregate**:
  - RR intervals: per-beat extraction, aggregate for conduction ratio determination
  - F-wave detection: aggregate (frequency analysis of inter-QRS baseline)
  - QRS width: per-beat (to detect aberrancy)
  - Conduction ratio: requires correlating F-waves to QRS timing over multiple beats

### 6.3 Cross-Condition Interactions
- **Flutter affects how OTHER conditions present**:
  - STEMI: F-wave superimposition creates pseudo-ST changes; true ST analysis is very difficult during flutter
  - QT measurement: Nearly impossible during flutter — F-waves obscure the T-wave end
  - LVH: Voltage criteria still valid, but strain-pattern ST-T changes are confounded by F-waves
  - Digitalis effect: ST changes from digitalis are indistinguishable from F-wave effects
- **Conditions that must be ruled out first** (differential):
  - Sinus tachycardia at 150 bpm (the most common misdiagnosis of 2:1 flutter)
  - AFib (irregular vs regular/regularly irregular)
  - SVT — AVNRT/AVRT (no visible atrial activity vs F-waves)
  - Focal atrial tachycardia with block (isoelectric line between P-waves vs no isoelectric in flutter)
- **Dangerous combinations**:
  - Flutter + class IC drugs without AV nodal blocker → 1:1 conduction → hemodynamic collapse
  - Flutter + WPW → pre-excited flutter → VF risk
  - Flutter + AFib (flutter-fib) → management must address both

### 6.4 Reasoning Chain Sketch
- **Minimum reasoning chain (high confidence)**:
  1. Detect regular or regularly irregular ventricular rhythm
  2. Identify ventricular rate at or near 150 bpm (or 75, 100 bpm suggesting 4:1, 3:1)
  3. Identify sawtooth F-waves in II, III, or aVF at ~300/min
  4. Confirm organized, regular atrial activity in V1
  5. → Diagnosis: Atrial Flutter (confidence: HIGH)
- **Full reasoning chain (complete evidence assembly)**:
  1. Calculate ventricular rate and assess rhythm regularity
  2. If rate ~150 bpm, flag: "consider 2:1 flutter"
  3. Analyze baseline between QRS complexes in II, III, aVF for sawtooth pattern
  4. Analyze V1 for upright, regular F-waves
  5. Measure F-wave rate (should be 250–350/min)
  6. Measure F-F interval regularity (CV <5% = organized flutter)
  7. Determine conduction ratio: F-wave count per QRS (2:1, 3:1, 4:1, variable)
  8. Classify flutter type: typical (negative F-waves in inferior leads) vs atypical (positive or variable)
  9. Check for concealed F-waves: look for notching/distortion in T-waves or ST segments
  10. Measure QRS duration: narrow (<120 ms) vs wide (evaluate for WPW, BBB, aberrancy)
  11. If wide QRS + very rapid + regular → consider pre-excited flutter or 1:1 conduction
  12. Assess for coexisting conditions (flutter-fib transitions, ST changes beyond F-wave superimposition)
  13. → Final diagnosis with type classification, conduction ratio, and rate

### 6.5 Confidence Anchors
- **HIGH confidence features**:
  - Regular rate ~150 bpm + sawtooth F-waves in inferior leads at 300/min = classic 2:1 flutter
  - Identical, regular F-waves at 250–350/min visible in V1 and at least one inferior lead
  - Adenosine challenge revealing organized flutter waves with transient higher AV block
- **LOWER confidence if**:
  - Atypical F-wave morphology (positive in inferior leads) — could be atypical flutter, atrial tach, or even sinus tach with unusual P-waves
  - Very fast atrial rate (>350/min) — overlap with AFib or atrial tachycardia
  - Variable conduction making rhythm appear irregularly irregular — overlap with AFib
  - Significant baseline artifact obscuring F-waves
  - Post-ablation or post-surgical patients — scar-related circuits produce atypical morphologies
- **Pathognomonic combination**: Regular rate at ~150 bpm + continuous sawtooth F-waves at ~300/min (negative in II, III, aVF; positive in V1) + narrow QRS = typical atrial flutter with 2:1 conduction (specificity >99%)
- **Classification thresholds**:
  - "Possible flutter": Regular rhythm at ~150 bpm but F-waves not clearly seen (consider adenosine challenge)
  - "Probable flutter": Organized atrial activity at 250–350/min in at least one lead + consistent conduction ratio
  - "Definite flutter": Clear sawtooth F-waves in ≥2 leads (inferior + V1) + regular/regularly irregular ventricular rhythm + defined conduction ratio

### 6.6 Difficulty Score

| Dimension | Score (1-5) | Notes |
|-----------|-------------|-------|
| Signal clarity needed | 3 | F-waves require reasonable signal quality; 2:1 flutter hides half the F-waves, making detection harder in noisy signals. Coarser F-waves are easier; subtle F-waves with 2:1 block are the challenge case. |
| Number of leads required | 2 | Diagnosable from II + V1 in most cases. V1 is especially important when inferior leads are ambiguous. Full 12-lead needed for typical vs atypical classification. |
| Cross-domain reasoning | 2 | Basic flutter = atrial morphology + rhythm analysis. Increases to 4 when assessing flutter + WPW, flutter + drug effects, or flutter + STEMI. |
| Temporal pattern complexity | 3 | Variable conduction ratios create beat-to-beat differences. Must correlate F-wave timing to QRS timing across the full strip. Fixed 2:1 is simpler; variable block is more complex. |
| Differential complexity | 4 | The 2:1 flutter at 150 bpm is one of the most commonly misdiagnosed rhythms in cardiology. Must distinguish from sinus tach, SVT, AFib, and atrial tachycardia. Requires active "search for hidden flutter waves." |
| Rarity in PTB-XL | 2 | Common in PTB-XL, though less prevalent than AFib. Sufficient examples for validation (~500+ records). |
| **Overall difficulty** | **2.7** | **Moderate difficulty overall. The 2:1 flutter at ~150 bpm is the most commonly missed diagnosis, driving the differential complexity score. Once flutter waves are identified, the diagnosis is straightforward.** |

---

## 6A. Agent Assignment

**Architecture:** Option E — 3 Parallel Phase 1 Specialists + 1 Sequential CDS (Node 2.1 Gate Passed 2026-03-27)

| Agent | Role for Atrial Flutter | Key Features Used |
|-------|--------------------------|-------------------|
| **RRC** (Rhythm/Rate/Conduction) | Primary | Sawtooth flutter waves at 250–350/min in II/III/aVF (negative) and V1 (positive), regular or regularly irregular ventricular rhythm, 2:1/3:1/4:1 AV conduction ratio, ventricular rate (~150 bpm for 2:1 block), hidden flutter waves in QRS/ST segments, absence of discrete P-waves |
| **IT** (Ischemia/Territory) | Not involved | — |
| **MR** (Morphology/Repolarization) | Not involved | QRS morphology assessment only if aberrant conduction is detected (wide QRS flutter) — flags for CDS |
| **CDS** (Cross-Domain Synthesis) | Standard integration; cross-domain alert if 1:1 flutter with wide QRS | Confirms flutter wave detection and rate; emits cross-domain alert if RRC identifies very high ventricular rate (≥200 bpm, suggesting 1:1 conduction) AND MR detects wide QRS (aberrancy or preexcitation) — this is an emergent pattern requiring immediate rate control |

### Primary Agent
**RRC** — atrial flutter is a rhythm diagnosis defined by regular atrial flutter waves at 250–350/min with characteristic sawtooth morphology and fixed AV conduction ratio, which is entirely in the RRC agent's domain.

### Cross-Domain Hints
- RRC emits `cross_domain_hint: "Ventricular rate ≥200 bpm during flutter pattern — possible 1:1 AV conduction; MR QRS morphology required to assess for preexcitation or aberrancy"` when very high ventricular rates are detected.

### CDS Specific Role
CDS performs standard integration for typical flutter: confirms sawtooth rate and AV ratio classification, generates flutter diagnosis with conduction ratio notation. For the critical edge case of 1:1 flutter (ventricular rate ~300 bpm), CDS integrates RRC's rate detection with MR's wide QRS finding — if present, this suggests preexcitation (WPW + flutter) or very fast 1:1 conduction with aberrancy, both requiring emergent management. CDS generates an urgency-tiered output accordingly.

---

## 7. RAG Knowledge Requirements

### 7.1 Textbook References
- **Goldberger's Clinical Electrocardiography (10th ed.)**: Chapter on supraventricular arrhythmias — clear illustrations of sawtooth pattern, 2:1 vs 4:1 conduction, and the "150 bpm trap." Best for foundational understanding.
- **Chou's Electrocardiography in Clinical Practice (7th ed.)**: Chapter 13 — extensive atrial flutter section with electrophysiological mechanism, multiple ECG examples of typical and atypical flutter, and detailed discussion of flutter-fibrillation coexistence. Best for depth.
- **Marriott's Practical Electrocardiography (13th ed.)**: Strong on the differential of regular tachycardias at 150 bpm, adenosine challenge interpretation, and concealed flutter wave detection. Best for diagnostic reasoning.
- **Braunwald's Heart Disease (12th ed.)**: Chapter 66 — clinical management of flutter, CTI ablation outcomes, drug interactions (class IC + flutter). Best for clinical context and management integration.

### 7.2 Key Figures
- Reference ECG: 12-lead showing classic typical flutter with 2:1 conduction — sawtooth in inferior leads, upright F-waves in V1, rate ~150 bpm
- Comparison figure: 4:1 flutter (F-waves obvious, rate ~75 bpm) vs 2:1 flutter (F-waves hidden, rate ~150 bpm) — same patient if possible
- Diagnostic maneuver: ECG strip during adenosine administration — transient high-grade block revealing flutter waves
- Danger case: 1:1 conduction (~300 bpm) — wide QRS, hemodynamically unstable
- Atypical flutter: Left atrial flutter post-ablation with positive F-waves in inferior leads
- Flutter-fib transition: Strip showing organized flutter degenerating into fibrillation

---

## 8. Dashboard Visualization Specification

### 8.1 Highlighted Leads
- **Primary display**: Lead II (full width, enlarged) — highlight the sawtooth F-wave pattern with color overlay showing the continuous undulation
- **Secondary display**: V1 (full width, enlarged) — highlight upright F-waves with markers at each F-wave peak
- **Supporting**: aVF as third rhythm strip; all 12 leads in standard format with F-wave markers overlaid

### 8.2 Arrows and Annotations
- **Lead II/aVF**: Arrows pointing to the sawtooth troughs and peaks, labeled "Flutter waves (F-waves) at ~300/min — sawtooth pattern"
- **V1**: Arrows at each upright F-wave peak, labeled "Upright F-waves at ~300/min"
- **Conduction ratio annotation**: Bracket showing 2 (or 3, 4) F-waves per QRS complex, labeled "2:1 (3:1, 4:1) AV conduction"
- **If 2:1 block**: Additional annotation on the T-wave: "Hidden F-wave embedded in T-wave" with dashed arrow
- **Rate banner**: "Atrial rate: ~300/min | Ventricular rate: ~150/min | Conduction: 2:1"
- **F-F interval ladder diagram**: Inset showing constant F-F intervals with every Nth F-wave conducting to the ventricle

### 8.3 Clinician Explanation (Plain Language)
- **ER nurse**: "This ECG shows atrial flutter — the heart's upper chambers are beating in a fast, organized loop pattern at about 300 beats per minute. The lower chambers only respond to every 2nd (or 3rd, 4th) beat, so the heart rate you see is about 150 (or 100, 75). The main clue is the smooth, sawtooth-shaped waves between heartbeats, best seen in the bottom leads (II and aVF)."
- **Cardiologist**: "Twelve-lead ECG demonstrating [typical/atypical] atrial flutter with [2:1/3:1/4:1/variable] AV conduction, ventricular rate [X] bpm. F-waves at ~[X]/min are [negative in II, III, aVF and positive in V1, consistent with typical counterclockwise CTI-dependent flutter / atypical morphology suggesting non-CTI circuit]. QRS is [narrow/wide]. No definitive ST changes beyond F-wave superimposition artifact. Recommend rate control with [beta-blocker/CCB], anticoagulation per CHA₂DS₂-VASc, and referral for CTI ablation given [typical flutter / recurrent episodes]."

---

## 9. Edge Cases and Pitfalls

- **The 150 bpm trap**: The single most common flutter pitfall. A regular narrow-complex tachycardia at exactly ~150 bpm is 2:1 flutter until proven otherwise. Sinus tachycardia at exactly 150 in an adult at rest is unusual — flutter is far more likely. The F-waves are hidden because one falls in the QRS and one in the T-wave. Adenosine challenge or vagal maneuvers can unmask the flutter waves.
- **Class IC drug-induced 1:1 conduction**: Flecainide or propafenone slow the atrial rate from 300 to 200/min. Without concurrent AV nodal blockade, 1:1 conduction at 200 bpm occurs — wide QRS (sodium channel blockade), hemodynamically unstable, often misdiagnosed as VT. Prevention: ALWAYS co-prescribe an AV nodal blocker.
- **Atypical flutter misdiagnosed as sinus tachycardia**: Atypical (clockwise or left atrial) flutter with positive F-waves in inferior leads can closely mimic sinus P-waves. Key differences: flutter F-waves have no isoelectric baseline between them and are regular at 250–350/min; sinus P-waves have an isoelectric baseline and rate <200.
- **Flutter-fibrillation transition**: A strip may begin as organized flutter and degrade to fibrillation (or vice versa). The algorithm must handle rhythms that change mid-strip. Look for the transition point where F-wave regularity breaks down.
- **Post-surgical/post-ablation atypical flutter**: Scar-related circuits in the left or right atrium produce atypical F-wave morphologies at variable rates (sometimes slower, 200–250/min). These can be very difficult to distinguish from focal atrial tachycardia. Electrophysiology study may be needed for definitive classification.
- **Flutter with high-degree AV block**: 4:1 or higher conduction produces slow ventricular rates (50–75 bpm). May be misdiagnosed as sinus bradycardia if F-waves are not recognized. Key: look for regular, rapid, small deflections between QRS complexes.
- **Coarse AFib mimicking flutter**: Coarse fibrillatory waves can appear somewhat organized, mimicking flutter. Key difference: true flutter F-waves are identical and metronomically regular; coarse AFib f-waves vary in morphology, amplitude, and timing from wave to wave.
- **Pediatric flutter**: Rare outside the neonatal period. Neonatal flutter has faster atrial rates (350–500/min) and may conduct at 1:1. In older children, usually associated with congenital heart disease or post-surgical repair.
- **Electrode placement artifact**: Poor limb lead placement can alter F-wave appearance — if leads II, III, aVF show inconsistent F-wave morphology, check electrode positions.
- **Dual tachycardia**: Atrial flutter coexisting with a ventricular tachycardia (extremely rare) — AV dissociation with both chambers beating independently. Flutter waves march through at their own rate while QRS complexes follow the VT rate.

---

## 10. References
- Page RL, et al. 2015 ACC/AHA/HRS Guideline for the Management of Adult Patients With Supraventricular Tachycardia. Circulation. 2016;133(14):e506-e574.
- Joglar JA, et al. 2023 ACC/AHA/ACCP/HRS Guideline for Diagnosis and Management of Atrial Fibrillation (includes flutter management). Circulation. 2024;149(1):e1-e156.
- Hindricks G, et al. 2020 ESC Guidelines for the diagnosis and management of atrial fibrillation (includes flutter). Eur Heart J. 2021;42(5):373-498.
- Van Gelder IC, et al. 2024 ESC Guidelines for the management of atrial fibrillation (flutter sections). Eur Heart J. 2024;45(36):3314-3414.
- Saoudi N, et al. A classification of atrial flutter and regular atrial tachycardia according to electrophysiological mechanisms and anatomical bases. Eur Heart J. 2001;22(14):1162-1182.
- Granada J, et al. Atrial flutter: current concepts on mechanisms and management. Med Clin North Am. 2008;92(1):53-63.
- Waldo AL. Atrial flutter: entrainment, characteristics, and clinical implications. Circ Arrhythm Electrophysiol. 2017;10(1):e004950.
- Goldberger AL. Clinical Electrocardiography: A Simplified Approach. 10th ed. Elsevier; 2024.
- Surawicz B, Knilans TK. Chou's Electrocardiography in Clinical Practice. 7th ed. Saunders; 2020.
- Wagner GS, Strauss DG. Marriott's Practical Electrocardiography. 13th ed. Wolters Kluwer; 2022.
- PTB-XL ECG dataset: Wagner P, et al. PTB-XL, a large publicly available electrocardiography dataset. Sci Data. 2020;7(1):154.
