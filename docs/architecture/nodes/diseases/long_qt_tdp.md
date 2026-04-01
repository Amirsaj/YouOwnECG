# Long QT Syndrome with Torsades de Pointes Risk — ECG Manifestation from First Principles

**Node:** 2.7.13
**SDA:** SDA-2 (Diagnosis & Agentic Core) — shared resource for SDA-1, SDA-3, SDA-4
**Status:** Complete (Sections 1–6, 7–10; Section 6A pending Node 2.1)
**PGMR:** Required
**Date:** 2026-03-26

---

## 1. Pathophysiology Root Cause

### 1.1 What Goes Wrong (Anatomy/Physiology)
- Long QT Syndrome (LQTS) results from prolonged ventricular repolarization — the action potential duration (APD) is abnormally extended, delaying the return of ventricular myocytes to their resting state
- **Congenital LQTS** arises from inherited mutations in genes encoding cardiac ion channels or their regulatory subunits. The three most common forms account for ~90% of genotype-positive cases:
  - **LQT1 (KCNQ1 — IKs channel)**: Loss-of-function mutation in the slow delayed rectifier potassium channel. IKs normally activates during sympathetic stimulation to shorten APD at faster rates. Loss of IKs → APD fails to shorten appropriately with exercise or adrenergic stress → QT fails to shorten with tachycardia → arrhythmic events characteristically triggered by exercise (especially swimming) and emotional stress
  - **LQT2 (KCNH2/hERG — IKr channel)**: Loss-of-function mutation in the rapid delayed rectifier potassium channel. IKr is the dominant repolarizing current during phase 3. Loss of IKr → prolonged phase 3 → markedly prolonged APD. Arrhythmic events characteristically triggered by sudden auditory stimuli (alarm clocks, phone ringing) and emotional stress, likely because the sudden sympathetic surge creates transmural dispersion in the setting of already-prolonged repolarization
  - **LQT3 (SCN5A — INa channel)**: Gain-of-function mutation in the cardiac sodium channel (same gene as Brugada, but opposite functional effect). Persistent late INa during the plateau phase → prolonged phase 2 → prolonged APD. Arrhythmic events characteristically occur during rest and sleep (bradycardia-dependent), because the prolonged plateau is most prominent at slower heart rates
- **Acquired LQTS** is far more common than congenital and results from:
  - **Drug-induced (most common)**: QT-prolonging drugs block IKr (hERG channel), the same current affected in LQT2. Common culprits: Class III antiarrhythmics (sotalol, dofetilide, amiodarone), antibiotics (erythromycin, fluoroquinolones, azithromycin), antipsychotics (haloperidol, ziprasidone, droperidol), antiemetics (ondansetron, metoclopramide), antifungals (fluconazole, ketoconazole), methadone
  - **Electrolyte imbalances**: Hypokalemia (reduces IKr conductance by altering channel kinetics), hypomagnesemia (impairs Na+/K+-ATPase and multiple repolarizing currents), hypocalcemia (prolongs phase 2 plateau by reducing ICa-L inactivation rate)
  - **Bradycardia**: Slow heart rates prolong APD independently, compounding the effect of QT-prolonging drugs or electrolyte abnormalities
  - **Structural heart disease**: Heart failure, LVH, and myocardial ischemia can prolong repolarization through remodeling of ion channel expression
- The entire ventricular myocardium is affected, but the degree of APD prolongation is NOT uniform — mid-myocardial cells (M-cells) have the longest intrinsic APD due to their weaker IKs expression. This creates transmural dispersion of repolarization (TDR), the substrate for re-entrant arrhythmias

### 1.2 Electrical Consequence
- **Prolonged phase 3 repolarization**: Regardless of the specific channel affected, the net result is delayed completion of repolarization → prolonged QT interval on surface ECG
- **Early afterdepolarizations (EADs)**: During the abnormally prolonged plateau and phase 3, the L-type calcium channels (ICa-L) may recover from inactivation before repolarization completes. This creates spontaneous inward calcium current during late phase 2 or phase 3 → secondary depolarizations (EADs) that appear as oscillations in membrane voltage. If an EAD reaches threshold, it triggers a premature action potential
- **Transmural dispersion of repolarization (TDR)**: The M-cells (mid-myocardium) are disproportionately affected by QT-prolonging conditions. When TDR is large (epicardium repolarized, M-cells still depolarized, endocardium intermediate), the voltage gradients create a substrate for re-entrant circuits. An EAD-triggered PVC (the trigger) encounters this heterogeneous repolarization substrate (the substrate) → re-entry → polymorphic VT
- **Torsades de Pointes (TdP)**: The specific arrhythmia of LQTS. TdP is a polymorphic ventricular tachycardia where the QRS axis appears to rotate around the isoelectric baseline, creating the characteristic "twisting of the points" spindle pattern. The rotating axis results from the re-entrant wavefront interacting with the heterogeneous repolarization substrate, causing the activation vector to precess through 360°
- **Short-long-short (SLS) sequence**: TdP is classically initiated by a short-long-short RR interval sequence. A PVC (short RR) → compensatory pause (long RR) → the post-pause beat has an even longer APD (rate-dependent APD prolongation) → this maximizes TDR → a second PVC during the vulnerable window of the post-pause beat initiates TdP. This SLS sequence is present in >80% of TdP initiations
- **T-wave alternans (TWA)**: Beat-to-beat alternation of T-wave amplitude or polarity reflects APD alternans in the myocardium — one beat has a long APD, the next has a short APD. This creates macroscopic electrical instability and is a harbinger of IMMINENT TdP. When TWA is visible on the surface ECG, TdP may occur within seconds to minutes

### 1.3 Why It Appears on ECG
- **Prolonged QT interval**: The QT interval represents total ventricular depolarization + repolarization time. Prolonged APD → the T-wave ends later → QT is measured from QRS onset to the end of the T-wave, and both boundaries shift when repolarization is delayed
- **T-wave morphology changes by subtype**: The specific phase of the action potential that is prolonged determines T-wave shape:
  - LQT1 (IKs loss): Broad-based, prolonged T-wave with relatively preserved amplitude. The prolongation is mostly in the terminal portion of the T-wave, stretching it out
  - LQT2 (IKr loss): Notched or bifid T-wave (two humps), often with low amplitude. The notch reflects the uncovering of transmural repolarization gradient discontinuities that are normally smoothed by IKr. The bifid T is most prominent in V2-V5
  - LQT3 (late INa gain): Long isoelectric ST segment (flat plateau) followed by a relatively narrow, late-appearing T-wave. The prolonged plateau phase creates the long ST segment; the T-wave onset is delayed but the T-wave itself may have near-normal morphology
- **QTc prolongation is global**: Unlike Brugada (localized to V1-V3), QT prolongation is visible in ALL leads because the entire ventricular myocardium has prolonged repolarization. However, the T-wave morphology changes (notching, bifidity) are most apparent in the precordial leads (V2-V5) where the T-wave amplitude is largest
- **T-wave alternans**: When APD alternans develops, each beat produces a different T-wave vector. The beat-to-beat alternation in T-wave amplitude or polarity is visible across all leads but most obvious in the leads with the largest T-wave amplitude

---

## 2. ECG Presentation — Lead by Lead

### 2.1 Diagnostic Criteria (2025 AHA/ESC Guidelines)

| Criterion | Threshold | Source |
|-----------|-----------|--------|
| Prolonged QTc — male | >440 ms (borderline 441-460; prolonged 461-480; markedly prolonged >480) | 2025 AHA/ACC/HRS Guideline on Ventricular Arrhythmia; Schwartz 1993 |
| Prolonged QTc — female | >460 ms (borderline 461-480; prolonged 481-500; markedly prolonged >500) | 2025 AHA; Moss 1991 |
| HIGH TdP risk threshold | QTc >500 ms in any patient (regardless of sex) | 2025 AHA; 2025 ESC; Priori 2003 |
| VERY HIGH TdP risk threshold | QTc >600 ms — critical danger zone | Expert consensus; Priori 2003 |
| Bazett correction formula | QTc = QT / √RR (in seconds). Most widely used; overestimates QTc at fast rates, underestimates at slow rates | Bazett 1920; endorsed by AHA for standard clinical use |
| Fridericia correction formula | QTc = QT / RR^(1/3) (in seconds). More accurate than Bazett at heart rates outside 60-100 bpm | Fridericia 1920; recommended by 2025 ESC for HR <60 or >100 |
| Schwartz diagnostic score for congenital LQTS | ≥3.5 points = high probability; 1.5-3.0 = intermediate; ≤1.0 = low probability | Schwartz 2011; endorsed 2025 ESC |
| T-wave morphology for subtype | LQT1: broad T; LQT2: notched/bifid T; LQT3: long ST + late T | Zhang 2000; Moss 1995 |
| T-wave alternans | Beat-to-beat alternation of T-wave amplitude or polarity — harbinger of IMMINENT TdP | 2025 AHA; Zareba 1994 |
| Short-long-short (SLS) initiation | PVC → compensatory pause → post-pause beat → second PVC → TdP | 2025 AHA; Viskin 1995 |
| TdP pattern on rhythm strip | Polymorphic VT with sinusoidal modulation of QRS amplitude (spindle pattern), QRS axis rotating around the isoelectric baseline | 2025 AHA; Dessertenne 1966 |
| U-wave prominence | Large U-waves (especially if U-wave amplitude exceeds T-wave amplitude) may cause QT overestimation — measure QT to end of T-wave, NOT U-wave | 2025 AHA; Lepeschkin 1952 |

### 2.2 Lead-by-Lead Manifestation

| Lead | Expected Finding | Why (Vector Explanation) | Sensitivity |
|------|-----------------|------------------------|-------------|
| I | Prolonged QT interval; T-wave may appear broad (LQT1), low/notched (LQT2), or late-onset (LQT3); T-wave alternans visible when present | Lead I (0° leftward) sees the horizontal component of the repolarization vector. QT prolongation is global and measurable here. T-wave morphology changes are visible but may be less dramatic than precordial leads due to smaller T-wave amplitude | Moderate for QTc measurement; Low-moderate for morphology |
| II | Prolonged QT interval (MOST COMMONLY USED lead for QT measurement); T-wave morphology changes visible; SLS sequence identifiable on rhythm strip | Lead II (+60°) is the traditional lead for QT interval measurement because the T-wave is typically most clearly delineated here (aligned with the mean repolarization vector). QT prolongation is easily measured. RR intervals for SLS identification are clearly visible | Very High — standard lead for QTc measurement; best for identifying SLS sequence |
| III | Prolonged QT interval; T-wave morphology changes visible but variable | Lead III (+120°) provides additional QT measurement. T-wave amplitude may be smaller depending on axis. Less commonly used for primary QT measurement than lead II | Moderate |
| aVR | Prolonged QT interval measurable; T-wave is normally inverted in aVR — prolonged QT manifests as delayed return to baseline after the inverted T | aVR (-150°) sees the heart from the opposite direction. QT prolongation is present but the inverted T-wave polarity makes morphological subtyping difficult. Not a primary diagnostic lead | Low — used for confirmation, not primary diagnosis |
| aVL | Prolonged QT interval; T-wave morphology changes visible in some patients; may show more obvious T-wave alternans than limb leads in some cases | aVL (-30° leftward-superior) sees the repolarization vector from a leftward-superior perspective. QT is measurable. T-wave changes are visible but variable depending on axis | Moderate |
| aVF | Prolonged QT interval; T-wave morphology changes visible; similar utility to lead III | aVF (+90° inferior) is aligned with the inferior component of the repolarization vector. QT measurement is reliable here. T-wave is typically upright and measurable | Moderate-High |
| V1 | Prolonged QT interval; T-wave may be normally inverted or biphasic in V1 — QT prolongation makes the T-wave inversion broader or deeper; in LQT2, bifid T-wave may be particularly prominent with two distinct humps | V1 faces the septum anteriorly. The T-wave has variable polarity at baseline (often inverted or biphasic). QT is measurable but T-wave end-point may be ambiguous due to biphasic morphology. LQT2 notching is visible here | Moderate for QTc; Moderate for LQT2 morphology |
| V2 | Prolonged QT interval; T-wave morphology changes are becoming more visible; LQT2 bifid/notched T-wave is prominent; LQT3 long isoelectric ST segment visible | V2 overlies the septum/anterior LV transition. T-wave amplitude increases from V1 to V2, making morphological changes more apparent. The notched T of LQT2 is often first appreciated in V2-V3 | High for QTc; High for T-wave morphology |
| V3 | Prolonged QT interval; T-wave morphology changes highly visible; LQT1 broad-based T clearly seen; LQT2 bifid T most prominent; LQT3 long ST segment with late T-wave onset clearly visible; T-wave alternans most easily detected here | V3 overlies the anterior LV where T-wave amplitude is large. The large T-wave makes subtle morphological changes (notching, broadening, delayed onset) most visible. This is one of the best leads for T-wave morphology assessment and TWA detection | Very High for T-wave morphology and TWA detection |
| V4 | Prolonged QT interval; T-wave morphology changes highly visible; similar utility to V3 for morphology assessment; T-wave amplitude is typically maximal in V4 | V4 faces the LV apex. T-wave amplitude is often the largest of any lead, making V4 excellent for morphological assessment. QT measurement is reliable but T-wave end-point determination can be challenging when T-wave is tall and broad | Very High for morphology; High for QTc measurement |
| V5 | Prolonged QT interval; T-wave morphology changes visible; broad T (LQT1) and notched T (LQT2) still identifiable but less prominent than V3-V4 | V5 faces the lateral LV. T-wave is upright and moderate-to-large. QT prolongation is clearly measurable. Useful as a second measurement point to confirm QTc | High for QTc; Moderate-High for morphology |
| V6 | Prolonged QT interval; T-wave is smaller than V4-V5, making morphological changes less obvious; QT measurement is reliable | V6 faces the far lateral LV. T-wave amplitude is smaller than mid-precordial leads. QT prolongation is present and measurable. Less useful for subtle morphological subtyping | Moderate for QTc; Moderate for morphology |

### 2.3 Key Leads (Most Diagnostic)
- **Lead II**: The standard lead for QT interval measurement. The T-wave is typically well-delineated and upright, with a clear termination point. QTc calculation should primarily use lead II. Also the best lead for identifying the short-long-short RR sequence preceding TdP
- **V3-V4**: Best leads for T-wave morphology assessment (LQT1 broad T, LQT2 notched/bifid T, LQT3 late-onset T) and for detecting T-wave alternans. The large T-wave amplitude in these leads makes subtle morphological changes most apparent
- **V5**: Excellent supplementary lead for QTc measurement when lead II is ambiguous. Often provides the clearest T-wave termination point
- **The lead with the LONGEST QT**: Per guidelines, QTc should be measured in the lead showing the longest QT interval (usually lead II or V5-V6), excluding leads where the T-wave end is ambiguous. If leads show discrepant QT values, use the longest clearly measurable QT
- **All leads for T-wave alternans**: TWA may be most prominent in different leads in different patients — scan all 12 leads for beat-to-beat T-wave amplitude or polarity changes

### 2.4 Beat-by-Beat Considerations
- **Beat-to-beat QT variability**: In LQTS, the QT interval may show increased beat-to-beat variability (QT variability index is elevated). This reflects the underlying repolarization instability and is itself a risk marker
- **Rate-dependent QT behavior**: In LQT1, the QT fails to shorten appropriately with exercise (maladaptive QT response). In LQT3, the QT may paradoxically shorten at faster rates (because the late INa has less time to influence the plateau). Measuring QTc at multiple heart rates can suggest the subtype
- **T-wave alternans (TWA)**: Macroscopic TWA (visible on standard ECG) is a STAT finding — it indicates imminent TdP risk. The alternation may be in amplitude only (tall T / short T alternating), polarity (upright / inverted alternating), or morphology (normal / notched alternating). TWA may appear minutes before TdP onset
- **Short-long-short (SLS) sequence**: The classic initiation of TdP: (1) PVC with short coupling interval → (2) compensatory pause (long RR) → (3) post-pause sinus beat with VERY long QT → (4) PVC during the vulnerable window of this post-pause beat → TdP. The agent must recognize this RR interval pattern as a TdP precursor even before the TdP initiates
- **Post-pause QT prolongation**: After any pause (PVC, sinus pause, AV block), the subsequent beat has a longer APD and therefore a longer QT interval. In LQTS patients, this post-pause QT prolongation is exaggerated, creating the substrate for TdP. PVCs followed by pauses in a patient with long QT should trigger a STAT alert
- **TdP morphology on continuous rhythm**: TdP appears as polymorphic wide complex tachycardia with characteristic sinusoidal oscillation of QRS amplitude — the QRS axis rotates progressively, creating a "spindle" pattern where the QRS amplitude waxes and wanes. Rate is typically 150-300 bpm. Episodes may be self-terminating (lasting seconds to minutes) or may degenerate into VF

---

## 3. Morphology Details (What the Agent Must See)

### 3.1 P-wave Changes
- **Morphology**: Normal — LQTS does not affect atrial depolarization. P-waves are sinus with normal morphology
- **Duration**: Normal (<120 ms)
- **Axis**: Normal (0° to +75°)
- **During TdP**: P-waves are not visible (overwhelmed by the polymorphic ventricular tachycardia). After TdP self-terminates, sinus P-waves return — typically preceded by a long pause
- **Key observation**: Normal P-waves before each QRS in the pre-TdP rhythm confirms sinus rhythm and helps distinguish LQTS from other causes of abnormal repolarization (e.g., ischemia with non-sinus rhythm)

### 3.2 PR Interval Changes
- **Duration**: Normal (120-200 ms) — LQTS does not affect AV conduction
- **Pattern**: Constant; no Wenckebach or dropped beats
- **Exception**: If the patient is on AV-nodal blocking drugs (beta-blockers, which are actually the treatment for LQT1 and LQT2), PR may be prolonged iatrogenically
- **Key point**: Normal PR interval helps distinguish LQTS from conditions that prolong both conduction and repolarization (e.g., hyperkalemia prolongs PR AND QT)

### 3.3 QRS Complex Changes
- **Duration**: Normal (<120 ms) during sinus rhythm. QRS widening is NOT a feature of LQTS. If QRS is wide, consider alternative or coexisting diagnosis (BBB, hyperkalemia, TCA overdose)
- **Morphology**: Normal — no rSR', no delta wave, no fragmentation
- **Amplitude**: Normal
- **Axis**: Normal
- **During TdP**: QRS is wide and polymorphic, with continuously changing axis (the defining feature of TdP). QRS duration during TdP is typically 120-200 ms. The QRS axis rotates progressively, creating the sinusoidal waxing-waning amplitude pattern

### 3.4 ST Segment Changes
- **Direction**: Typically isoelectric (normal) in most LQTS subtypes
- **LQT3 exception**: Long isoelectric ST segment — the ST segment is flat and prolonged before the T-wave begins. This is because the persistent late INa maintains the plateau phase for an extended period. The ST segment may measure 200-400 ms from J-point to T-wave onset (normally ~80-120 ms)
- **Morphology**: Horizontal and isoelectric (normal) in LQT1 and LQT2; prolonged horizontal segment in LQT3
- **Key distinction from STEMI**: LQTS does NOT produce ST elevation or depression. If ST changes are present, consider concurrent ischemia, drug effect, or alternative diagnosis

### 3.5 T-wave Changes
- **LQT1 (broad-based T-wave)**:
  - Direction: Upright
  - Amplitude: Normal to slightly reduced
  - Shape: Broad-based, smooth, prolonged. The T-wave starts normally but its descending limb is stretched out, creating a wider-than-normal T-wave. No notching or bifidity
  - Best seen in: V3-V5, lead II
- **LQT2 (notched/bifid T-wave)**:
  - Direction: Upright with a notch, or biphasic
  - Amplitude: Often low, sometimes with the second component taller than the first
  - Shape: Two distinct humps separated by a notch in the mid-portion of the T-wave. This "bifid T" or "double-humped T" is the hallmark of LQT2. The notch reflects the uncovered transmural repolarization discontinuity when IKr is absent
  - Best seen in: V2-V4 (most prominent), also visible in V5 and limb leads
- **LQT3 (late-onset peaked T-wave)**:
  - Direction: Upright, often peaked
  - Amplitude: Normal to tall
  - Shape: The T-wave appears relatively normal in shape but is LATE — separated from the QRS by a long isoelectric ST segment. The T-wave onset is delayed, and the T-wave itself may be narrow and peaked
  - Best seen in: V3-V5, lead II
- **Acquired LQTS (drug-induced)**:
  - Morphology most closely resembles LQT2 (because most drugs block IKr) — notched or bifid T-waves, low amplitude, prolonged QT
  - May show prominent U-waves that merge with the T-wave, making QT end-point determination difficult
- **T-wave alternans**: Beat-to-beat alternation in T-wave amplitude, polarity, or morphology. When macroscopically visible (without signal averaging), it indicates extreme repolarization instability and IMMINENT TdP. May manifest as every-other-beat T-wave amplitude change (tall-short-tall-short) or polarity change (upright-inverted-upright-inverted)

### 3.6 QT/QTc Changes
- **Prolonged** — this is THE defining feature of the condition
- **Normal values**: Males ≤440 ms, Females ≤460 ms
- **Borderline prolonged**: Males 441-460 ms, Females 461-480 ms
- **Prolonged**: Males 461-480 ms, Females 481-500 ms
- **Markedly prolonged / HIGH TdP risk**: >500 ms (either sex)
- **VERY HIGH TdP risk**: >600 ms — this is a medical emergency
- **QTc correction formulas**:
  - **Bazett**: QTc = QT / √RR. Most widely used. Overestimates at HR >100, underestimates at HR <60. Acceptable for HR 60-100 bpm
  - **Fridericia**: QTc = QT / RR^(1/3). More accurate outside 60-100 bpm range. Recommended by ESC when HR is abnormal
  - **Hodges**: QTc = QT + 1.75 × (HR - 60). Linear correction, simple but less commonly used
  - **Framingham**: QTc = QT + 0.154 × (1 - RR). Population-derived, increasingly recommended
- **Measurement technique**: Measure from QRS onset to the point where the tangent line drawn on the steepest descending limb of the T-wave intersects the baseline (tangent method — reduces interobserver variability). Measure in the lead with the longest QT (usually II or V5). Average over 3-5 beats. In AFib, average over 10+ beats or use the longest RR interval for the most conservative estimate
- **Clinical significance thresholds for TdP risk**:
  - QTc 460-500 ms: Low but present risk — remove QT-prolonging drugs, correct electrolytes, monitor
  - QTc 500-550 ms: Moderate risk — continuous telemetry, active intervention
  - QTc >550 ms: High risk — consider IV magnesium prophylaxis, pacing on standby
  - QTc >600 ms: Very high risk — IV magnesium, consider temporary pacing at 80-100 bpm to prevent pauses

### 3.7 Other Features
- **U-waves**: Prominent U-waves may be present, particularly in hypokalemia-associated QT prolongation. U-waves are low-amplitude deflections following the T-wave, best seen in V2-V3. When large, U-waves can merge with the T-wave, creating a "T-U fusion" pattern that artificially lengthens the measured QT. The agent must distinguish the T-wave endpoint from the U-wave onset — measure QT to the end of the T-wave, NOT the U-wave
- **T-U fusion**: When the T-wave and U-wave merge into a single broad deflection, the true QT becomes difficult to measure. In this case, measure to the nadir between T and U if visible, or report "QT indeterminate due to T-U fusion" and flag for clinical correlation
- **T-wave alternans (TWA)**: As described above — the most critical "other feature." Macroscopic TWA on a standard ECG = STAT finding. Microscopic TWA (detectable only with signal processing/microvolt TWA testing) is a risk marker but not visible on standard ECG
- **Short-long-short RR sequence**: Not a morphological feature per se, but a temporal pattern the agent must detect: a premature beat (short RR) followed by a pause (long RR) followed by another premature beat. This sequence is the typical TdP initiator

---

## 4. Differential Diagnosis

### 4.1 Mimics (What Looks Like This But Isn't)

| Mimic Condition | Shared Features | Distinguishing Features |
|----------------|-----------------|----------------------|
| Hypocalcemia | Prolonged QT interval | Hypocalcemia prolongs the ST segment specifically (long flat ST segment before T-wave) — may mimic LQT3 morphology. However, the T-wave itself is usually normal in shape and duration. Ca2+ level confirms. Hypocalcemia typically prolongs QTc to 480-540 ms range, rarely >600 ms unless extreme |
| Hypothermia | Prolonged QT interval, bradycardia | Hypothermia prolongs ALL intervals (PR, QRS, QT). Osborn/J-waves (positive deflection at the J-point) are pathognomonic for hypothermia and absent in LQTS. Shivering artifact may be present. Core temperature measurement is definitive |
| Raised intracranial pressure (ICP) | Prolonged QT, deep T-wave inversions (cerebral T-waves) | Raised ICP produces deeply inverted, wide, symmetric T-waves ("cerebral T-waves") across multiple leads — these are dramatic and differ from the notched/bifid T of LQT2 or the broad T of LQT1. Clinical context (acute neurological event) is key. QTc may be prolonged but rarely >550 ms |
| Left ventricular hypertrophy (LVH) with strain | Prolonged QT, T-wave inversion in lateral leads | LVH strain pattern: ST depression with asymmetric T-wave inversion in V5-V6, I, aVL (lateral leads) + tall R-waves meeting voltage criteria. LQTS: GLOBAL QT prolongation without voltage criteria or asymmetric ST-T changes. LVH does not produce notched T-waves or T-wave alternans |
| Myocardial ischemia (NSTEMI) | ST-T changes, possibly prolonged QT | Ischemia produces regional ST-T changes in a coronary territory distribution. LQTS produces GLOBAL QT prolongation without regional ST depression or elevation. Troponin, clinical history, and evolution of ECG changes differentiate |
| Normal variant (long QT at baseline) | QTc 440-460 ms | Borderline QTc in otherwise normal individuals (especially young women) is common and does not carry TdP risk if <460 ms (females) or <440 ms (males). No T-wave morphology abnormalities, no family history, no symptoms. Serial ECGs confirm stability |
| U-wave prominence mimicking long QT | Apparent "long QT" due to measuring TU complex instead of T alone | Large U-waves (common in hypokalemia, bradycardia, LVH) can make the QT appear longer than it truly is. Careful identification of the T-wave endpoint using the tangent method, ignoring the U-wave, gives the true QT. If T and U waves merge completely, report as indeterminate |
| Drug-induced QT prolongation (without TdP risk) | Prolonged QTc | Amiodarone prolongs QTc significantly but has a paradoxically LOW TdP risk because it blocks multiple channels homogeneously (reducing TDR). Verapamil prolongs QT but also blocks ICa-L, reducing EAD risk. Not all QT-prolonging drugs carry equal TdP risk — context matters |

### 4.2 Coexisting Conditions
- **LQTS + Atrial Fibrillation**: QTc measurement in AFib is unreliable due to variable RR intervals. Bazett correction is particularly inaccurate in AFib. Best approach: average QTc over ≥10 beats, or measure the QT during the longest RR interval and apply the correction. If QTc is prolonged in AFib, the TdP risk is real but harder to quantify
- **LQTS + Bundle Branch Block (BBB)**: BBB intrinsically prolongs QRS and therefore QT. To assess whether QT is prolonged BEYOND the conduction delay: subtract the excess QRS duration from the QT interval. If QRS is 160 ms (40 ms excess over 120 ms), subtract 40 ms from the measured QT, then calculate QTc. Alternative: use the JTc interval (QTc minus QRS) — JTc >340 ms suggests true repolarization prolongation independent of conduction delay
- **LQTS + Hypokalemia**: Hypokalemia potentiates QT-prolonging drug effects by reducing IKr conductance. A patient on a QT-prolonging drug may have an acceptable QTc with normal K+, but develop markedly prolonged QTc and TdP when K+ drops (e.g., from diuretics, vomiting, diarrhea). Always check electrolytes in new QT prolongation
- **LQTS + Bradycardia**: Bradycardia prolongs APD and QT. A patient with borderline QTc at HR 80 may have dangerously prolonged QTc at HR 50. Beta-blockers, calcium channel blockers, and AV nodal disease can unmask latent LQTS. Bradycardia also creates the pauses that enable the short-long-short TdP initiation sequence
- **Concealed LQTS**: Some genotype-positive LQTS patients have normal resting QTc. The diagnosis is "concealed" until a trigger (drug, electrolyte, bradycardia, exercise) unmasks QT prolongation. The agent cannot detect concealed LQTS from a normal ECG — clinical suspicion and genetic testing are required

---

## 5. STAT Classification

| Priority | Criteria |
|----------|----------|
| **STAT** | Yes — Long QT with QTc >500 ms carries significant TdP risk (annual event rate ~5% in congenital LQTS with QTc >500). T-wave alternans indicates IMMINENT arrhythmic risk — TdP may occur within minutes. TdP itself can degenerate to VF and cardiac arrest |
| **Time-sensitive** | QTc >500 ms requires immediate intervention (drug removal, electrolyte correction, telemetry). T-wave alternans requires IMMEDIATE intervention (IV magnesium, pacing standby, defibrillator at bedside). QTc 460-500 ms requires prompt evaluation but is less emergent |
| **Clinical action** | (1) QTc >500 ms: Discontinue ALL QT-prolonging drugs immediately; check K+, Mg2+, Ca2+ — correct aggressively (target K+ >4.0, Mg2+ >2.0); continuous telemetry; IV magnesium sulfate 2g bolus then infusion (first-line treatment to suppress EADs, effective even with normal Mg2+ levels); (2) T-wave alternans or TdP: All the above PLUS defibrillator at bedside; if TdP occurs: unsynchronized cardioversion if unstable, IV magnesium 2g bolus if hemodynamically tolerated; isoproterenol infusion (increases heart rate → shortens APD → suppresses EADs and pauses); temporary transvenous pacing at 80-100 bpm (overdrive suppression — prevents pauses that enable SLS initiation); (3) Congenital LQTS: Beta-blockers (nadolol preferred) for LQT1 and LQT2; mexiletine (late INa blocker) for LQT3; ICD for survivors of cardiac arrest, syncope despite beta-blockers, or QTc >500 ms with risk factors; (4) Remove offending drug — maintain telemetry until QTc normalizes (may take 3-5 half-lives of the drug) |

---

## 6. Reasoning Complexity Analysis (Feeds Into Node 2.1 — Agent Architecture Research)

> **NOTE**: This section does NOT pre-assign agents. It documents the reasoning
> complexity of this condition so that Node 2.1 can determine the BEST agent
> architecture to handle ALL conditions. The actual agent assignment is filled
> in AFTER Node 2.1 research completes.

### 6.1 Reasoning Domains Required to Detect This Condition
- **Interval measurement (primary)**: QT interval measurement is the core diagnostic task. This requires identifying QRS onset, T-wave offset (using the tangent method), and RR interval for rate correction. Accurate QT measurement is more computationally demanding than most interval measurements because T-wave offset is often ambiguous
- **Rate correction calculation (primary)**: Applying Bazett, Fridericia, or other correction formulas to convert QT to QTc. The agent must select the appropriate formula based on heart rate and rhythm (Bazett for HR 60-100 sinus; Fridericia for HR outside this range; averaging for AFib)
- **Morphology analysis (primary)**: T-wave morphology assessment is critical for subtype identification (LQT1 broad, LQT2 notched/bifid, LQT3 long ST + late T) and for detecting T-wave alternans
- **Temporal pattern analysis (primary)**: Beat-to-beat analysis is essential for detecting T-wave alternans and short-long-short RR sequences. This requires per-beat analysis, not just single-beat or average analysis
- **Lead-group correlation (supporting)**: QT prolongation should be GLOBAL (all leads). If QT appears prolonged in some leads but not others, consider measurement artifact or U-wave inclusion. Confirming global prolongation adds confidence
- **Metabolic context (supporting)**: Clinical context (medication list, electrolytes) profoundly affects interpretation. A QTc of 500 ms on sotalol + hypokalemia has a different risk profile than a QTc of 500 ms in a genetically confirmed LQT1 patient on nadolol
- **Cross-domain reasoning required**: Yes — the agent must combine interval measurement + rate correction + morphology analysis + temporal pattern detection + lead correlation. This is a multi-domain task

### 6.2 Feature Dependencies
- **ESSENTIAL features from SDA-1**:
  - QT interval measurement (QRS onset to T-wave offset, tangent method) in all 12 leads
  - RR interval measurement for rate correction
  - QTc calculation (Bazett and Fridericia) — report both
  - T-wave morphology classification per lead: normal, broad-based, notched/bifid, late-onset, low-amplitude, inverted
  - T-wave alternans detection: beat-to-beat T-wave amplitude comparison across ≥10 consecutive beats
  - Heart rate
- **SUPPORTING features from SDA-1**:
  - U-wave detection and amplitude (to flag T-U fusion risk and avoid QT overestimation)
  - QRS duration (to identify BBB and apply JTc correction if needed)
  - RR interval variability (to detect AFib or frequent ectopy, which affect QTc reliability)
  - ST segment duration (J-point to T-wave onset) — prolonged ST segment suggests LQT3
  - PVC detection and coupling interval (to identify short-long-short sequences)
  - T-wave amplitude per lead per beat (for alternans calculation)
- **EXCLUSION features**:
  - ST elevation or depression in a coronary territory → suggests ischemia, not primary LQTS (though QT may be secondarily prolonged)
  - Osborn/J-waves → suggests hypothermia, not LQTS
  - Peaked T-waves (tall, narrow, symmetric) in V2-V4 → suggests hyperkalemia, not LQTS (QT in hyperK may be shortened early or prolonged late, but the peaked T morphology is distinct from LQTS T-wave patterns)
  - Wide QRS (>120 ms) without BBB morphology → suggests hyperkalemia or TCA overdose, not primary LQTS
- **Per-beat vs aggregate analysis**: BOTH are required. QTc measurement can use aggregate (average of 3-5 beats). T-wave alternans detection REQUIRES per-beat analysis. SLS sequence detection REQUIRES per-beat RR interval analysis

### 6.3 Cross-Condition Interactions
- **LQTS affects other conditions**: A patient with long QT who develops new PVCs is at higher risk than a patient with normal QT and PVCs — the PVCs can initiate TdP via the SLS mechanism. The agent must flag PVCs in the setting of long QT as HIGH RISK even if the PVCs themselves would otherwise be benign
- **Other conditions affect LQTS interpretation**:
  - AFib → QTc measurement is unreliable; averaging required
  - BBB → QRS prolongation confounds QT measurement; use JTc correction
  - Bradycardia → augments QT prolongation; QTc may underestimate risk if Bazett is used at low HR
  - LVH → may prolong QT slightly; voltage criteria + prolonged QT suggests LVH with strain, not primary LQTS
- **Detecting LQTS requires considering**: Whether QT prolongation is primary (congenital) or secondary (drug, electrolyte). The ECG pattern alone cannot definitively distinguish, but T-wave morphology (LQT1/2/3 subtypes) and clinical context help
- **TdP vs polymorphic VT from other causes**: TdP has the characteristic spindle pattern with rotating QRS axis and occurs in the setting of prolonged QT. Polymorphic VT with NORMAL QT (e.g., from ischemia, catecholaminergic VT) has a different mechanism and different treatment (TdP: magnesium + pacing; ischemic PMVT: beta-blockers + revascularization). The agent must check the baseline QT to distinguish

### 6.4 Reasoning Chain Sketch
- **Minimum reasoning chain (fewest steps to high confidence)**:
  1. Measure QT interval in lead II (or lead with longest QT)
  2. Measure RR interval
  3. Calculate QTc using Bazett (and Fridericia if HR outside 60-100)
  4. Compare QTc to sex-specific threshold: males >440 ms, females >460 ms
  5. If QTc >500 ms → flag STAT: HIGH TdP risk
  → High confidence QT prolongation detected

- **Full reasoning chain (complete evidence assembly)**:
  1. Measure QT interval in leads II, V5, V3 (multiple leads for verification)
  2. Use tangent method for T-wave endpoint; flag if U-waves present
  3. Measure RR interval; assess rhythm (sinus vs AFib vs frequent PVCs)
  4. Calculate QTc using Bazett and Fridericia; report both
  5. If BBB present, calculate JTc (QTc - QRS) and report
  6. Compare QTc to sex-specific thresholds; classify as borderline/prolonged/markedly prolonged
  7. Assess T-wave morphology in V2-V5: broad (LQT1), notched/bifid (LQT2), late-onset after long ST (LQT3), or nonspecific (acquired)
  8. Check for T-wave alternans: compare T-wave amplitude beat-to-beat across ≥10 beats in V3-V4
  9. Check for short-long-short RR sequences: scan for PVC → pause → PVC pattern
  10. If QTc >500 ms: flag STAT with TdP risk level
  11. If T-wave alternans present: flag STAT IMMINENT TdP
  12. If SLS sequences present: flag STAT — TdP initiation pattern
  13. Assess for concurrent conditions: AFib (QTc unreliable), BBB (use JTc), bradycardia (augments risk), PVCs (SLS trigger risk)

### 6.5 Confidence Anchors
- **HIGH confidence features**:
  - QTc >500 ms measured consistently across multiple leads with clear T-wave endpoint → definite QT prolongation with HIGH TdP risk
  - Notched/bifid T-wave in V2-V5 + QTc >480 ms → probable LQT2 or acquired (IKr-block)
  - Macroscopic T-wave alternans visible on standard ECG → IMMINENT TdP risk regardless of QTc value
  - TdP on rhythm strip: polymorphic wide complex tachycardia with spindle pattern + preceding QTc prolongation → definite TdP
- **LOWER confidence if absent or ambiguous**:
  - T-wave endpoint is ambiguous (T-U fusion) → QTc measurement may be inaccurate; flag as "indeterminate" and request clinical review
  - QTc 440-480 ms → borderline; may be normal variant; T-wave morphology and clinical context needed
  - Heart rate >100 or <50 → Bazett correction is unreliable; Fridericia needed; confidence in QTc value reduced
  - AFib → QTc from single beat is unreliable; need ≥10-beat average; lower confidence
- **PATHOGNOMONIC combination**: QTc >500 ms + notched/bifid T-waves + T-wave alternans + short-long-short RR sequences = TdP about to occur; specificity near 100%
- **Classification thresholds**:
  - **Possible**: QTc 440-480 ms (sex-adjusted) with normal T-wave morphology → clinical correlation recommended
  - **Probable**: QTc 480-500 ms with abnormal T-wave morphology (broad, notched, or late-onset) → QT-prolonging drugs and electrolytes should be reviewed
  - **Definite**: QTc >500 ms measured consistently → STAT flag; OR any QTc prolongation + T-wave alternans → STAT IMMINENT flag

### 6.6 Difficulty Score
| Dimension | Score (1-5) | Notes |
|-----------|-------------|-------|
| Signal clarity needed | 5 | QT measurement requires precise identification of QRS onset AND T-wave offset. T-wave offset is one of the most challenging measurements in electrocardiography — baseline noise, U-waves, T-wave flattening, and T-U fusion all confound it. T-wave alternans detection requires very clean signal to distinguish real alternans from noise |
| Number of leads required | 2 | QTc should be measured in the lead with the longest QT (typically II or V5), but morphological subtyping requires V2-V5, and confirming global prolongation requires all 12 leads. TWA detection benefits from all leads. In practice, full 12-lead is needed for complete assessment |
| Cross-domain reasoning | 4 | Requires interval measurement + rate correction calculation + morphology analysis + temporal (beat-to-beat) pattern analysis + lead-group correlation + metabolic context. More cross-domain than most conditions. The interaction between QT, rate, morphology, and temporal patterns is complex |
| Temporal pattern complexity | 5 | T-wave alternans requires per-beat analysis across ≥10 consecutive beats. Short-long-short sequence detection requires RR interval analysis across 3-4 consecutive beats. Rate-dependent QT behavior requires multi-rate comparison. This is the highest temporal complexity of any condition |
| Differential complexity | 3 | The differential for QT prolongation is moderate — hypocalcemia, hypothermia, raised ICP, LVH, drugs, ischemia. Most can be distinguished by morphology and clinical context. Less differential complexity than Brugada or STEMI |
| Rarity in PTB-XL | 3 | Long QT is present in PTB-XL at a moderate frequency (drug-induced and congenital). However, T-wave alternans and actual TdP episodes are very rare in the dataset. Validation of QTc measurement is feasible; validation of TWA and TdP detection may require supplementary data |
| **Overall difficulty** | **3.7** | **QT measurement accuracy is the fundamental challenge — it requires high signal quality, precise endpoint detection, and appropriate rate correction. T-wave alternans and SLS detection add significant temporal complexity. The combination of measurement precision, multi-formula correction, morphological subtyping, and beat-to-beat analysis makes this one of the more technically demanding conditions for automated detection.** |

---

## 6A. Agent Assignment

**Architecture:** Option E — 3 Parallel Phase 1 Specialists + 1 Sequential CDS (Node 2.1 Gate Passed 2026-03-27)

| Agent | Role for Long QT / TdP | Key Features Used |
|-------|--------------------------|-------------------|
| **RRC** (Rhythm/Rate/Conduction) | Primary (co-primary) | TdP rhythm identification (sinusoidal twisting morphology at 160–250 bpm, polymorphic QRS axis), short-long-short initiating sequence (RR interval analysis), heart rate for QTc correction formula selection, RR interval variability, pause-dependent QT prolongation |
| **IT** (Ischemia/Territory) | Not involved | — |
| **MR** (Morphology/Repolarization) | Primary (co-primary) | QTc measurement (Bazett, Fridericia, Framingham formulas), T-wave morphology subtyping (LQT1: broad-based; LQT2: notched/bifid; LQT3: late-peaked narrow), T-wave alternans detection (beat-to-beat amplitude variation ≥1 mm), U-wave prominence, QT interval measurement across multiple leads (longest QTc used) |
| **CDS** (Cross-Domain Synthesis) | Required — integrates QTc measurement with rhythm identification | Combines MR's QTc measurement with RRC's TdP rhythm identification; resolves QTc measurement accuracy at elevated rates (Bazett overcorrects >100 bpm — CDS applies Fridericia or Framingham correction); integrates T-wave alternans (MR) with short-long-short sequence (RRC) for TdP risk scoring |

### Primary Agent
Both **MR** and **RRC** are co-primary: MR owns QTc measurement and T-wave morphology subtyping, while RRC owns TdP rhythm identification and the initiating beat patterns. Neither can function independently for the complete Long QT/TdP diagnosis.

### Cross-Domain Hints
- MR emits `cross_domain_hint: "QTc prolonged and T-wave alternans detected — RRC must evaluate for short-long-short initiating sequence and TdP morphology"` when QTc ≥500 ms with T-wave alternans is identified.
- RRC emits `cross_domain_hint: "TdP morphology or short-long-short sequence detected — MR QTc measurement and T-wave subtyping required to confirm substrate"` when polymorphic wide-QRS tachycardia with twisting pattern is identified.

### CDS Specific Role
CDS integrates MR's QTc measurement with RRC's rhythm findings to generate the complete Long QT/TdP assessment. A key CDS function is correcting QTc measurement accuracy at elevated rates: when heart rate exceeds 100 bpm, Bazett's formula overcorrects and CDS applies Fridericia (QTc = QT/RR^0.333) or Framingham correction instead. CDS combines T-wave alternans signal (MR) with short-long-short detection (RRC) to produce a TdP risk score, and generates LQT subtype classification based on T-wave morphology pattern.

---

## 7. RAG Knowledge Requirements

### 7.1 Textbook References
- **Goldberger's Clinical Electrocardiography** (10th ed): Excellent chapter on QT prolongation with clear measurement technique illustrations and TdP recognition. Best single reference for the tangent method of QT measurement and U-wave vs T-wave distinction
- **Chou's Electrocardiography in Clinical Practice** (7th ed): Comprehensive coverage of congenital LQTS subtypes with annotated ECG examples of LQT1, LQT2, and LQT3 T-wave morphologies. Detailed drug-induced QT prolongation section with risk stratification
- **Marriott's Practical Electrocardiography** (13th ed): Practical approach to QT measurement in difficult cases (AFib, BBB, U-waves). Excellent differential diagnosis section for QT prolongation
- **Braunwald's Heart Disease** (12th ed): Genetics of congenital LQTS; genotype-phenotype correlations; risk stratification algorithms; ICD indications; comprehensive drug list. The authoritative reference for clinical management

### 7.2 Key Figures
- 12-lead ECG comparison of LQT1, LQT2, and LQT3 with annotations showing the characteristic T-wave morphology of each subtype
- Tangent method illustration for QT measurement — step-by-step visual guide
- T-wave alternans ECG strip showing beat-to-beat amplitude alternation before TdP onset
- TdP rhythm strip with short-long-short initiation sequence annotated, followed by the characteristic spindle-pattern polymorphic VT
- Action potential diagrams comparing normal APD vs LQT1 (prolonged phase 3) vs LQT2 (prolonged phase 3, different mechanism) vs LQT3 (prolonged phase 2 plateau)
- QTc nomogram: heart rate vs QT interval with normal, borderline, and prolonged zones marked for males and females
- Comparison figure: TdP vs ischemic polymorphic VT — demonstrating the morphological similarity but different baseline QT

---

## 8. Dashboard Visualization Specification

### 8.1 Highlighted Leads
- **Primary highlight**: Lead II — large panel with QT interval measurement markers, RR interval, and calculated QTc (both Bazett and Fridericia) displayed as a numerical overlay
- **Secondary highlight**: V3 and V4 — zoomed panels showing T-wave morphology detail for subtype identification (broad, notched/bifid, or late-onset)
- **T-wave alternans panel**: If TWA is detected, a dedicated multi-beat strip (≥10 beats) in the lead with most prominent alternans, with alternating beats color-coded (e.g., odd beats in blue, even beats in red) to visually highlight the alternation
- **Rhythm strip**: Continuous lead II strip at the bottom showing ≥10 seconds for SLS sequence identification
- **Color coding**: QTc value displayed in GREEN (<440 ms male / <460 ms female), YELLOW (borderline), ORANGE (prolonged 460-500 ms), RED (>500 ms), FLASHING RED (>600 ms). T-wave abnormalities highlighted in ORANGE. T-wave alternans beats highlighted in alternating BLUE/RED

### 8.2 Arrows and Annotations
- Arrow marking QRS onset in lead II with label: "QRS onset"
- Arrow marking T-wave offset in lead II (tangent line drawn) with label: "T-wave end (tangent method)"
- Bracket spanning QRS onset to T-wave offset with label: "QT = XXX ms"
- Numerical display: "QTc (Bazett) = XXX ms | QTc (Fridericia) = XXX ms"
- In V3/V4: arrows pointing to T-wave morphology features:
  - LQT1: arrow spanning the broad T-wave base with label: "Broad-based T (LQT1 pattern)"
  - LQT2: arrows pointing to each notch/hump with label: "Bifid/notched T (LQT2 pattern)"
  - LQT3: bracket spanning the long ST segment with label: "Prolonged ST segment"; arrow to late T-wave with label: "Late-onset T (LQT3 pattern)"
- If U-wave present: arrow to U-wave with label: "U-wave — excluded from QT measurement"
- If TWA present: alternating beat markers with label: "T-wave alternans — IMMINENT TdP risk"
- If SLS present: bracket over the short-long-short sequence with label: "Short-Long-Short sequence — TdP initiation pattern"

### 8.3 Clinician Explanation (Plain Language)
- **ER nurse**: "This ECG shows a dangerously long QT interval (QTc = XXX ms, normal is under 440-460 ms). A long QT puts the patient at risk for a life-threatening heart rhythm called Torsades de Pointes. Stop any medications that prolong the QT, check potassium and magnesium levels, start continuous monitoring, and notify the physician immediately. If the T-waves are alternating in size from beat to beat, call a code — the dangerous rhythm may start any moment."
- **Cardiologist**: "QTc is prolonged at XXX ms (Bazett) / XXX ms (Fridericia), exceeding the TdP risk threshold of 500 ms. T-wave morphology in V2-V5 shows [broad-based / notched-bifid / long ST with late T-wave] pattern, consistent with [LQT1 (IKs) / LQT2 (IKr) / LQT3 (late INa) / acquired IKr block]. [If TWA present: Macroscopic T-wave alternans is detected, indicating extreme repolarization instability with imminent TdP risk — recommend IV magnesium 2g, isoproterenol or temporary pacing at 80-100 bpm, and defibrillator at bedside.] [If SLS present: Short-long-short RR sequences are present, consistent with TdP initiation substrate — recommend overdrive pacing to eliminate pauses.] Evaluate and discontinue QT-prolonging medications. Correct K+ to >4.0 mEq/L, Mg2+ to >2.0 mg/dL. For congenital LQTS: genotype-guided therapy (beta-blockers for LQT1/2, mexiletine for LQT3); ICD evaluation per guideline risk stratification."

---

## 9. Edge Cases and Pitfalls

- **QT measurement in AFib**: RR intervals are irregularly irregular, making single-beat QTc correction unreliable. Bazett overcorrects after long RR and undercorrects after short RR. Best practice: average QTc over ≥10 beats using Fridericia. Alternative: measure QT during the longest available RR interval for the most conservative estimate. The agent should flag "QTc in AFib — reduced reliability" and provide the averaged value
- **QT measurement with prominent U-waves**: U-waves in V2-V3 can merge with the T-wave, creating an apparent QT that is artificially long. The tangent method helps: draw a tangent on the steepest descending limb of the T-wave; the intersection with the baseline marks the T-wave end, even if a U-wave follows. If T-U fusion is complete (no trough between T and U), QT measurement becomes unreliable — flag as "QT indeterminate: T-U fusion"
- **QT in BBB**: LBBB and RBBB prolong QRS, which mechanically prolongs QT. The JTc interval (QTc minus QRS) isolates repolarization time from conduction time. JTc >340 ms in BBB suggests true repolarization prolongation. Alternative: use the Bogossian formula for QT correction in BBB (QTc-BBB = QTc - 48.5% × [QRS - 100])
- **Concealed LQTS**: Genotype-positive patients with normal resting QTc. The resting ECG is normal — the agent will not detect the condition. Triggers (exercise for LQT1, auditory stimulus for LQT2, rest/sleep for LQT3, drugs for acquired) are needed to unmask the phenotype. The agent should not false-positive, but also cannot detect concealed cases
- **QT paradox in LQT3**: LQT3 patients may show QT SHORTENING at faster heart rates (because the late INa has less time during the shorter cycle to influence the plateau). This means LQT3 may have a normal QTc during tachycardia but a very long QTc at rest. Resting ECGs may miss LQT3 in active/tachycardic patients — measure QTc at the lowest available heart rate
- **Drug-drug QT interactions**: Patients on multiple QT-prolonging drugs have synergistic risk. The ECG may show only modestly prolonged QTc (480-500 ms) but the combination creates high TdP risk due to reduced repolarization reserve. Risk calculators (e.g., Tisdale score) supplement ECG-based assessment
- **Electrolyte correction masks LQTS**: A patient with acquired long QT from hypokalemia will normalize QTc after K+ correction. If the underlying cause (diuretics, vomiting) recurs, QT prolongs again. The agent should flag the current QTc but cannot predict future recurrence
- **TdP vs catecholaminergic polymorphic VT (CPVT)**: CPVT produces bidirectional VT or polymorphic VT triggered by exercise/catecholamines, but the baseline QT is NORMAL. If the agent detects polymorphic VT on a rhythm strip, it must check the baseline QTc: prolonged QTc + PMVT = TdP; normal QTc + exercise-triggered PMVT = CPVT. Treatment differs fundamentally (TdP: magnesium + pacing; CPVT: beta-blockers, avoid isoproterenol)
- **Post-TdP ECG**: After a self-terminating TdP episode, the ECG typically shows sinus rhythm with very prolonged QTc and may show post-tachycardia T-wave memory (T-wave changes from the electrical memory of the VT). The QTc after TdP may be even longer than before due to ischemia and catecholamine surge
- **Age and sex considerations**: QTc norms differ: prepubertal children have similar QTc regardless of sex; post-puberty females have longer QTc than males (estrogen effect on IKr). Elderly patients have longer QTc due to age-related ion channel remodeling. The agent must apply age- and sex-appropriate thresholds
- **Athlete QT**: Athletes may have physiologically longer QTc (up to 460-470 ms in males) due to vagal tone and training-related ventricular remodeling. This is usually benign but overlaps with borderline congenital LQTS. T-wave morphology and family history are needed to distinguish

---

## 10. References
- Schwartz PJ, Stramba-Badiale M, Crotti L, et al. "Prevalence of the congenital long-QT syndrome." Circulation. 2009;120(18):1761-1767
- Priori SG, Wilde AA, Horie M, et al. "HRS/EHRA/APHRS Expert Consensus Statement on the Diagnosis and Management of Patients with Inherited Primary Arrhythmia Syndromes." Heart Rhythm. 2013;10(12):1932-1963
- Schwartz PJ, Crotti L. "QTc behavior during exercise and genetic testing for the long-QT syndrome." Circulation. 2011;124(20):2181-2184
- Moss AJ, Schwartz PJ, Crampton RS, et al. "The long QT syndrome: prospective longitudinal study of 328 families." Circulation. 1991;84(3):1136-1144
- Zhang L, Timothy KW, Vincent GM, et al. "Spectrum of ST-T-wave patterns and repolarization parameters in congenital long-QT syndrome: ECG findings identify genotypes." Circulation. 2000;102(23):2849-2855
- Viskin S. "Long QT syndromes and torsade de pointes." Lancet. 1999;354(9190):1625-1633
- Roden DM. "Drug-induced prolongation of the QT interval." N Engl J Med. 2004;350(10):1013-1022
- Drew BJ, Ackerman MJ, Funk M, et al. "Prevention of torsade de pointes in hospital settings: a scientific statement from the AHA and the ACCP." Circulation. 2010;121(8):1047-1060
- 2025 ESC Guidelines for the Management of Patients with Ventricular Arrhythmias and the Prevention of Sudden Cardiac Death
- 2025 AHA/ACC/HRS Guideline for Management of Patients with Ventricular Arrhythmias and the Prevention of Sudden Cardiac Death
- Dessertenne F. "La tachycardie ventriculaire à deux foyers opposés variables." Arch Mal Coeur Vaiss. 1966;59:263-272
- Bazett HC. "An analysis of the time-relations of electrocardiograms." Heart. 1920;7:353-370
- Fridericia LS. "Die Systolendauer im Elektrokardiogramm bei normalen Menschen und bei Herzkranken." Acta Med Scand. 1920;53:469-486
- Tisdale JE, Jaynes HA, Kingery JR, et al. "Development and validation of a risk score to predict QT interval prolongation in hospitalized patients." Circ Cardiovasc Qual Outcomes. 2013;6(4):479-487
- Zareba W, Moss AJ, le Cessie S, et al. "Risk of cardiac events in family members of patients with long QT syndrome." J Am Coll Cardiol. 1995;26(7):1685-1691
