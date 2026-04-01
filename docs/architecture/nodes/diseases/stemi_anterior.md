# Anterior STEMI (LAD Occlusion) — ECG Manifestation from First Principles

**Node:** 2.7.1
**SDA:** SDA-2 (Diagnosis & Agentic Core) — shared resource for SDA-1, SDA-3, SDA-4
**Status:** Complete
**PGMR:** Required
**Date:** 2026-03-26

---

## 1. Pathophysiology Root Cause

### 1.1 What Goes Wrong (Anatomy/Physiology)

The left anterior descending artery (LAD) is acutely occluded, most commonly by atherosclerotic plaque rupture with superimposed thrombosis. The LAD supplies the anterior wall of the left ventricle, the anterior two-thirds of the interventricular septum, and the apex. In proximal LAD occlusion, the diagonal branches are also compromised, extending ischemia to the anterolateral wall. In very proximal ("wraparound") LAD occlusion, the apex and even the apical inferior wall may be affected.

The territory at risk is large — the LAD supplies approximately 40-50% of the left ventricular myocardium, making anterior STEMI the highest-risk STEMI territory for hemodynamic compromise and mortality.

Within seconds of occlusion, the affected myocardium becomes ischemic. The ischemic cascade proceeds:

1. **Cessation of aerobic metabolism** (seconds) — ATP depletion begins
2. **Anaerobic glycolysis** (1-2 minutes) — lactate accumulates, intracellular pH drops
3. **Ion pump failure** (2-5 minutes) — Na+/K+-ATPase fails, intracellular K+ leaks out, Na+ and Ca2+ accumulate intracellularly
4. **Resting membrane potential depolarization** — ischemic cells cannot maintain -90mV; resting potential drifts toward -60 to -70mV
5. **Action potential shortening** — ischemic cells have abbreviated phase 2 (plateau), reducing action potential duration
6. **Irreversible injury** (20-40 minutes without reperfusion) — cell membrane rupture, contraction band necrosis

The injury is transmural in STEMI: it extends from the endocardium (most vulnerable due to highest oxygen demand and lowest perfusion pressure) through the full thickness of the myocardial wall to the epicardium. This full-thickness injury is what distinguishes STEMI from NSTEMI, where ischemia is limited to the subendocardium.

### 1.2 Electrical Consequence

The electrical consequences arise from the voltage gradient between injured and healthy myocardium:

**During diastole (TQ segment baseline shift):**
- Ischemic cells have a depolarized resting potential (-60 to -70mV vs normal -90mV)
- This creates a diastolic injury current flowing FROM ischemic tissue TO normal tissue (intracellularly) and FROM normal tissue TO ischemic tissue (extracellularly)
- The extracellular diastolic current flows AWAY from the exploring electrode overlying the injury zone
- This depresses the TQ baseline in leads facing the injury

**During systole (true ST elevation):**
- Normal myocardium fully depolarizes to approximately +20mV; ischemic myocardium reaches only 0 to -10mV
- This creates a systolic injury current with an intracellular flow FROM normal TO ischemic tissue
- The extracellular systolic current flows TOWARD the exploring electrode overlying the injury zone
- Combined with the depressed TQ baseline, the ST segment appears elevated relative to the depressed baseline

**Net effect on the ECG:** The combination of TQ depression and true ST elevation produces the observed ST elevation in leads facing the transmural injury. Conventional ECG machines use the TQ segment as the baseline, so the apparent ST elevation is the sum of both mechanisms. The injury current vector points FROM the center of the heart TOWARD the anterior wall — i.e., anteriorly and slightly leftward.

**Repolarization changes:**
- The shortened action potential in ischemic tissue alters the repolarization sequence
- Normally, repolarization proceeds from epicardium to endocardium (opposite to depolarization)
- In acute ischemia, the gradient reversal produces tall, peaked, hyperacute T-waves — these PRECEDE ST elevation

### 1.3 Why It Appears on ECG

The injury current vector for anterior STEMI points anteriorly and slightly leftward, directed from the posterior base toward the anterior wall and apex. This vector projects onto the 12-lead system as follows:

- **V1-V4** face the anterior wall directly. These leads have their positive poles oriented anteriorly, aligned with the injury vector. Result: maximal ST elevation.
- **V5-V6** face the anterolateral wall. They see the injury vector at an oblique angle. Result: variable ST elevation, often less prominent unless the LAD wraps laterally.
- **I, aVL** face the high lateral wall (supplied by diagonal branches of LAD). In proximal LAD occlusion with diagonal involvement, these leads show ST elevation. In mid or distal LAD occlusion, these leads may be uninvolved.
- **II, III, aVF** face the inferior wall, which is opposite to the anterior wall. The injury vector points AWAY from these leads. Result: reciprocal ST depression (the mirror image of the anterior ST elevation).
- **aVR** is oriented toward the right shoulder, roughly opposite to the global injury vector. ST elevation in aVR in the context of anterior STEMI suggests very proximal LAD or left main occlusion, because the injury vector is large enough that even aVR sees a component of it, OR more commonly, the aVR elevation is a reciprocal reflection of widespread ST depression in the opposite leads.

---

## 2. ECG Presentation — Lead by Lead

### 2.1 Diagnostic Criteria (2025 AHA/ACC/ESC Guidelines)

| Criterion | Threshold | Source |
|-----------|-----------|--------|
| ST elevation in V2-V3, men <40 years | >=2.5 mm at J-point | 2025 AHA/ACC STEMI Guideline; ESC 2023 ACS Guidelines |
| ST elevation in V2-V3, men >=40 years | >=2.0 mm at J-point | 2025 AHA/ACC STEMI Guideline; ESC 2023 ACS Guidelines |
| ST elevation in V2-V3, women (any age) | >=1.5 mm at J-point | 2025 AHA/ACC STEMI Guideline; ESC 2023 ACS Guidelines |
| ST elevation in all other leads | >=1.0 mm at J-point | 2025 AHA/ACC STEMI Guideline; ESC 2023 ACS Guidelines |
| New ST elevation at J-point required | In >=2 contiguous leads | 2025 AHA/ACC STEMI Guideline |
| New or presumably new LBBB with ischemic symptoms | Apply modified Sgarbossa criteria | 2025 AHA/ACC; Smith 2012 |
| Hyperacute T-wave amplitude | No formal threshold; must exceed baseline for lead/sex | Expert consensus; de Winter 2008 |
| Pathological Q-wave | >=40 ms duration OR >=25% of R-wave amplitude in >=2 contiguous leads | 2025 AHA/ACC; Thygesen 2018 (4th Universal Definition of MI) |
| Reciprocal ST depression | Present in >=1 non-contiguous lead group | Supports STEMI diagnosis; increases specificity from ~85% to >95% |

### 2.2 Lead-by-Lead Manifestation

| Lead | Expected Finding | Why (Vector Explanation) | Sensitivity |
|------|-----------------|------------------------|-------------|
| I | ST elevation 0.5-1.5 mm if proximal LAD; may be normal in mid/distal | Lead I axis is 0 degrees (leftward). Proximal LAD injury vector has a leftward component from diagonal territory involvement. Mid/distal LAD injury is more purely anterior, perpendicular to lead I. | Low for mid-LAD; moderate for proximal LAD |
| II | Reciprocal ST depression 0.5-1.5 mm | Lead II axis is +60 degrees (inferior-leftward). Anterior injury vector has a component pointing AWAY from this direction. The further anterior the vector, the greater the reciprocal depression. | Moderate (70-80% of anterior STEMI) |
| III | Reciprocal ST depression 0.5-2.0 mm (often most prominent inferior reciprocal lead) | Lead III axis is +120 degrees (inferior-rightward). This is nearly opposite to the anterolateral injury vector, producing maximal reciprocal depression among inferior leads. | High (80-90% of anterior STEMI) |
| aVR | ST elevation >=1 mm suggests proximal LAD or left main | aVR axis is -150 degrees (rightward-superior). In very proximal LAD or left main occlusion, the large injury territory creates vectors that project partially onto aVR. Also, widespread ST depression in lateral and inferior leads produces reciprocal elevation in aVR. | Variable; high specificity for proximal/left main when >1.5 mm |
| aVL | ST elevation 0.5-1.5 mm with proximal LAD (diagonal branch territory) | aVL axis is -30 degrees (leftward-superior). Diagonal branch territory injury projects superiorly and leftward, aligning with aVL. | Moderate for proximal LAD; low for distal |
| aVF | Reciprocal ST depression 0.5-1.5 mm | aVF axis is +90 degrees (directly inferior). Anterior injury vector is perpendicular or directed away. Reciprocal depression correlates with the magnitude of anterior ST elevation. | Moderate (60-75%) |
| V1 | ST elevation >=1 mm; often with QS complex in established infarction | V1 faces the septum anteriorly. Septal ischemia from LAD septal perforators projects directly onto V1. Early: tall hyperacute T-wave. Later: ST elevation with loss of r-wave. | High (85-95%) |
| V2 | ST elevation >=2.0-2.5 mm (sex/age dependent); hyperacute T-waves earliest here | V2 faces the anterior septum and anterior wall. This is the lead most directly aligned with the anterior injury vector. Hyperacute T-waves in V2 are often the earliest sign, appearing within minutes. | Very high (90-98%) |
| V3 | ST elevation >=2.0-2.5 mm (sex/age dependent); prominent STE with tombstone morphology in massive anterior STEMI | V3 faces the anterior wall at the transition zone. The full-thickness anterior injury vector projects maximally here. In large infarcts, the ST segment merges with the T-wave ("tombstone" pattern). | Very high (90-98%) |
| V4 | ST elevation >=1 mm; may be the lead of maximal STE in mid-LAD occlusion | V4 faces the anteroapical wall. Mid-LAD occlusion beyond the septal perforators but proximal to the apex produces maximal injury current here. Loss of R-wave amplitude is an early sign. | High (85-95%) |
| V5 | ST elevation >=1 mm with proximal LAD (lateral extension via diagonals); may be isoelectric or mildly depressed in distal LAD | V5 faces the low anterolateral wall. Only involved when diagonal branches or a large LAD territory are affected. The injury vector must have a sufficient leftward component. | Moderate (50-70% overall; higher with proximal LAD) |
| V6 | ST elevation >=1 mm in extensive anterior STEMI; often isoelectric or minimally affected | V6 faces the lateral wall. Only shows ST elevation in extensive anterior STEMI involving diagonal/obtuse marginal watershed territory. May actually show reciprocal depression if the injury is purely septal. | Low-moderate (40-60%) |

### 2.3 Key Leads (Most Diagnostic)

**Most sensitive:** V2, V3 — these leads are most directly aligned with the anterior wall injury vector. ST elevation is largest and appears earliest in V2-V3.

**Earliest changes:** V2 — hyperacute T-waves appear in V2 within 1-5 minutes of LAD occlusion, often before formal ST elevation criteria are met.

**Reciprocal changes:** III > II > aVF — reciprocal ST depression is most prominent in lead III because its axis (+120 degrees) is most opposite to the anterior injury vector. The presence of reciprocal changes increases specificity for true STEMI from approximately 85% to >95%.

**Localizing leads:**
- V1-V3 elevation = septal involvement (septal perforators from LAD)
- V3-V5 elevation = anterior wall (LAD proper)
- V4-V6, I, aVL elevation = anterolateral extension (diagonal branches)
- aVR elevation >1 mm = proximal LAD or left main involvement (high-risk marker)

### 2.4 Beat-by-Beat Considerations

- Anterior STEMI produces **constant** ST elevation across all beats in established occlusion. Unlike intermittent arrhythmias, acute STEMI does not fluctuate beat-to-beat.
- **Exception — stuttering STEMI:** intermittent occlusion/reperfusion can produce beat-to-beat variation in ST elevation amplitude. This occurs when a thrombus is labile and intermittently occludes and re-canalizes. The agent should flag beat-to-beat ST amplitude variation >50% as possible stuttering occlusion.
- **PVC beats** should be excluded from ST analysis — their altered depolarization produces secondary ST-T changes unrelated to ischemia.
- **Post-PVC beats** may transiently show augmented ST elevation due to post-extrasystolic potentiation and altered repolarization; do not use these beats for threshold measurement.
- If the patient is in atrial fibrillation, ST analysis should average across multiple beats (minimum 3-5 consecutive beats) to account for rate-dependent ST variation.

---

## 3. Morphology Details (What the Agent Must See)

### 3.1 P-wave Changes

- **Morphology:** Normal in uncomplicated anterior STEMI. P-waves are not directly affected by ventricular ischemia.
- **Exception — acute heart failure:** Large anterior STEMI with acute LV failure may produce elevated left atrial pressure within hours, leading to P-mitrale pattern (notched P in lead II, biphasic P with dominant terminal negative deflection in V1). This is a secondary finding, not a diagnostic criterion for STEMI itself.
- **Exception — sinus tachycardia:** Sympathetic activation from pain and hemodynamic compromise often increases heart rate to 90-120 bpm. P-waves may be buried in the preceding T-wave at higher rates.
- **Duration change:** Normal (unless pre-existing atrial abnormality).
- **Axis change:** Normal.

### 3.2 PR Interval Changes

- **Duration:** Normal (120-200 ms) unless pre-existing conduction disease. The AV node is supplied by the AV nodal branch (usually from RCA), not the LAD, so PR prolongation is not expected in anterior STEMI.
- **Exception — massive septal infarction:** Very proximal LAD occlusion can compromise the His bundle blood supply (supplied by the first septal perforator), producing infranodal AV block (Mobitz Type II or complete heart block with wide escape rhythm). This occurs in 5-8% of anterior STEMI and is an ominous sign.
- **Pattern:** Constant (not progressive).

### 3.3 QRS Complex Changes

- **Duration:** Initially narrow (< 120 ms). May widen acutely if:
  - Right bundle branch block develops (the right bundle traverses the septum — septal infarction can disrupt it). New RBBB in anterior STEMI occurs in ~5-10% and indicates large infarct territory.
  - Left anterior fascicular block develops (septally located). New LAFB produces left axis deviation.
  - Bifascicular block (RBBB + LAFB) = very proximal LAD, near-complete septal necrosis. Extremely high risk for progression to complete heart block.
- **Morphology:**
  - **Early (minutes to hours):** Diminishing R-wave amplitude in V1-V4. The R-wave represents septal and anterior wall depolarization; as myocardium becomes electrically inert, the R-wave shrinks.
  - **Established (hours to days):** Pathological Q-waves in V1-V4 appear as dead myocardium no longer generates depolarization vectors. The initial QRS vector shifts AWAY from the infarcted area (posteriorly), recorded as Q-waves (or QS complexes) in leads V1-V4.
  - **QS complexes:** Complete loss of R-wave in V1-V3 (sometimes V4) — indicates full-thickness anterior and septal necrosis.
  - **Poor R-wave progression:** R-wave amplitude fails to increase from V1 to V4 as expected. Defined as R-wave <3 mm in V3 or R in V3 < R in V2.
- **Amplitude:** Decreasing R-wave amplitude in V1-V4 is an evolving sign. Loss of >50% of initial R-wave amplitude within 6 hours correlates with large infarct size.
- **Axis:** Normal unless fascicular block develops. LAFB produces left axis deviation beyond -45 degrees. Combined RBBB + LAFB produces right axis deviation of the terminal QRS with left axis of the initial forces.

### 3.4 ST Segment Changes

- **Direction:** Elevation in V1-V4 (primary); V5-V6, I, aVL (with proximal LAD); depression in II, III, aVF (reciprocal).
- **Morphology evolution (temporal progression):**
  1. **Hyperacute phase (0-30 minutes):** Straightening of the ST segment — loss of the normal concavity between the S-wave nadir and the T-wave peak. The ST-T junction becomes indistinct.
  2. **Early elevation (30 minutes - 2 hours):** Concave-upward (scooped) ST elevation. This morphology can initially resemble benign early repolarization but is distinguished by the clinical context and reciprocal changes.
  3. **Established elevation (2-12 hours):** Convex-upward (dome-shaped) ST elevation. The concavity is replaced by a bulging outward contour. This is the classic STEMI morphology and is highly specific for transmural injury.
  4. **Tombstone pattern (massive STEMI):** The ST segment and T-wave fuse into a single monophasic waveform rising directly from the R-wave (or QS complex) with no isoelectric ST segment. This indicates a very large territory of transmural injury and carries the worst prognosis.
- **Measurement point:** J-point (junction of QRS termination and ST segment onset). The 2025 AHA/ACC guidelines specify J-point measurement. Some older criteria used J+60 ms or J+80 ms; the current standard is J-point.
- **Gender/lead-specific thresholds:**
  - V2-V3, men <40 years: >=2.5 mm
  - V2-V3, men >=40 years: >=2.0 mm
  - V2-V3, women (any age): >=1.5 mm
  - All other leads: >=1.0 mm
  - Measured from the preceding TP baseline (or TQ segment if P-wave is identifiable)
  - 1 mm = 0.1 mV at standard calibration (10 mm/mV)

### 3.5 T-wave Changes

- **Hyperacute T-waves (earliest ECG sign — minutes):**
  - **Direction:** Upright (same polarity as normal T-waves in precordial leads, but exaggerated)
  - **Amplitude:** Abnormally tall — significantly exceeds the normal T-wave amplitude for the lead. In V2-V3, normal T-wave amplitude is 3-8 mm in men; hyperacute T-waves reach 10-15+ mm. In women, normal V2-V3 T-wave amplitude is 1.5-6 mm; hyperacute exceeds 8-10 mm.
  - **Width:** Broad-based — the T-wave base is widened compared to normal. The normal T-wave base in V2-V3 is approximately 150-200 ms; hyperacute T-waves have bases of 200-300+ ms.
  - **Symmetry:** Symmetric — both the ascending and descending limbs have similar slope. This contrasts with normal T-waves (asymmetric: gradual upstroke, steeper downstroke) and LVH strain T-waves (asymmetric: steep downstroke, gradual return).
  - **Clinical significance:** Hyperacute T-waves represent the earliest ECG change, often appearing 1-5 minutes after LAD occlusion. They may precede formal ST elevation criteria by 15-60 minutes. Missing this sign delays reperfusion therapy.

- **T-wave inversion (subacute phase — days 1-3):**
  - As ST elevation begins to resolve, T-waves become biphasic (terminal inversion) and then fully inverted in V1-V4.
  - Inversions are symmetric and often deep (5-15 mm).
  - T-wave inversions that appear BEFORE reperfusion ("pre-reperfusion inversions") indicate spontaneous reperfusion and are a favorable sign.
  - Post-reperfusion (PCI or thrombolysis) T-wave inversions typically appear within 12-24 hours and are expected.

- **Persistent T-wave inversion (weeks to months):**
  - T-wave inversions in V1-V4 may persist indefinitely after anterior STEMI, especially with large infarcts.
  - Progressive normalization (pseudo-normalization) of previously inverted T-waves may indicate re-ischemia and warrants urgent evaluation.

### 3.6 QT/QTc Changes

- **Acute phase:** QTc is often prolonged (>450 ms in men, >460 ms in women) due to delayed repolarization in the ischemic zone. The ischemic cells have shortened action potentials, but the peri-infarction zone has heterogeneous repolarization that prolongs the overall QT.
- **Clinical significance:** Prolonged QTc in acute anterior STEMI increases the risk of polymorphic ventricular tachycardia and ventricular fibrillation. QTc >500 ms in the acute phase is a high-risk marker.
- **Post-reperfusion:** QTc may paradoxically prolong further in the first 24-48 hours as reperfusion injury creates additional repolarization heterogeneity. This is transient.
- **Torsades de Pointes risk:** Elevated in the acute phase, particularly if hypokalemia or hypomagnesemia coexist (common in acute MI patients who are stressed and catecholamine-surging). Maintain K+ >4.0 mEq/L and Mg2+ >2.0 mEq/L.

### 3.7 Other Features

- **Loss of R-wave amplitude:** Progressive R-wave loss in V1-V4 is a sensitive early marker, sometimes detectable before formal ST elevation criteria are met. Serial comparison of R-wave amplitude (if prior ECG available) increases sensitivity.
- **ST/T ratio:** In the early phase, the ratio of ST elevation to T-wave amplitude changes — initial hyperacute T-waves have a low ST/T ratio (< 0.5), which increases as the ST segment elevates and the T-wave begins to flatten or invert.
- **Terminal QRS distortion (a high-risk marker):** Defined as absence of both S-wave in V1-V3 AND absence of J-point in V1-V3 (the ST segment takes off directly from the R-wave without returning to baseline). This indicates massive transmural injury and large infarct size. Present in approximately 30% of anterior STEMI; associated with lower ejection fraction and higher mortality. (Birnbaum et al., JACC 1996; validated in subsequent studies through 2024.)
- **Cabrera sign:** Notching of the ascending limb of the S-wave (or the R-wave descending limb) in V3-V5, lasting >=40 ms. This indicates established (rather than hyperacute) myocardial necrosis. Specificity ~90% for MI, but low sensitivity.
- **Chapman sign:** Notching of the R-wave upstroke in I, aVL, V5, V6 — indicates lateral extension of infarction.

### 3.8 Temporal Evolution Summary

| Phase | Timing | ECG Feature | Clinical Implication |
|-------|--------|-------------|---------------------|
| Hyperacute | 0-30 min | Tall, broad, symmetric T-waves in V2-V4; ST straightening | Window for emergent reperfusion; most commonly missed |
| Acute | 30 min - 12 hr | Convex ST elevation V1-V4; reciprocal depression III, aVF; R-wave loss begins | STEMI activation; door-to-balloon <90 min |
| Evolving | 12-72 hr | Q-waves develop V1-V4; ST elevation begins to resolve; T-wave inversion begins | Assess reperfusion success; watch for re-occlusion |
| Subacute | 3-14 days | Deep symmetric T-wave inversions V1-V4; Q-waves established; ST normalizing | Risk of ventricular remodeling; start ACE/ARB |
| Chronic | Weeks-months | Persistent Q-waves V1-V4; T-waves may remain inverted or normalize; ST should be isoelectric | If ST remains elevated: suspect LV aneurysm |

---

## 4. Differential Diagnosis

### 4.1 Mimics (What Looks Like This But Isn't)

| Mimic Condition | Shared Features | Distinguishing Features |
|----------------|-----------------|----------------------|
| **Benign Early Repolarization (BER)** | ST elevation in V2-V4 (often 1-3 mm), prominent T-waves | Concave (scooped) ST morphology with a notch or slur at the J-point; no reciprocal ST depression; no Q-waves; no R-wave loss; stable on serial ECGs; age typically <40; ST/T ratio <0.25 (Smith's rule: ST elevation at 60 ms after J-point / T-wave amplitude in V3 < 0.25 favors BER over STEMI; Smith SW et al., Ann Emerg Med 2012) |
| **Left Ventricular Hypertrophy (LVH) with repolarization abnormality** | ST elevation in V1-V3 (sometimes up to 5 mm); tall T-waves | Preceded by deep S-waves in V1-V3 with tall R-waves in V5-V6 meeting voltage criteria (Sokolow-Lyon: S in V1 + R in V5 or V6 >=35 mm); ST elevation is concave and proportional to preceding S-wave depth; asymmetric T-wave inversion (strain) in V5-V6, I, aVL; no reciprocal depression in inferior leads; no dynamic evolution |
| **Acute Pericarditis** | Diffuse ST elevation; tall T-waves | ST elevation is diffuse (present in most leads, not confined to a single coronary territory); PR segment depression (most specific finding — 85% specificity); Spodick's sign (downsloping TP segment); NO reciprocal ST depression (except in aVR and V1); concave morphology in ALL leads; PR elevation in aVR |
| **Takotsubo (Stress) Cardiomyopathy** | ST elevation in V2-V5, deep T-wave inversions; troponin elevation | ST elevation extends beyond a single coronary territory (often V2-V6 + I + II); deep, symmetric T-wave inversions develop within 24-48 hr (often deeper than typical STEMI — can exceed 15-20 mm); QTc markedly prolonged (often >500 ms); regional wall motion abnormality on echo extends beyond single coronary territory (apical ballooning with basal hyperkinesis); coronary angiography shows no culprit lesion; predominantly post-menopausal women after emotional or physical stress |
| **Left Bundle Branch Block (LBBB)** | ST elevation in V1-V3; wide QRS | QRS >=120 ms with typical LBBB morphology (broad notched R in I, aVL, V5-V6; QS or rS in V1-V3); ST-T changes are expected secondary repolarization changes (discordant to QRS); apply modified Sgarbossa criteria to detect superimposed STEMI: (1) concordant STE >=1 mm in any lead (5 points); (2) concordant ST depression >=1 mm in V1-V3 (3 points); (3) discordant STE with ST/S ratio >=0.25 (Smith-modified, 2 points; replaces original Sgarbossa criterion 3) |
| **LV Aneurysm** | Persistent ST elevation in V1-V4 with Q-waves | History of prior anterior MI; ST elevation is chronic and stable (no acute evolution on serial ECGs); convex morphology but T-waves are typically upright (not inverted as in acute resolution phase); no reciprocal changes; no troponin elevation; echocardiography confirms dyskinetic or aneurysmal segment |
| **Myocarditis** | ST elevation (focal or diffuse); troponin elevation; chest pain | Young patient; preceded by viral illness; ST elevation pattern does not conform to single coronary territory; PR depression may be present; cardiac MRI shows patchy mid-wall or epicardial late gadolinium enhancement (not subendocardial); coronary angiography is normal |
| **Hyperkalemia** | Tall peaked T-waves in V2-V4 | T-waves are narrow-based and tented (tent-like apex) rather than broad-based; T-wave changes are diffuse across ALL leads (not confined to a coronary territory); PR prolongation and widened QRS at higher K+ levels; no ST elevation; no reciprocal changes; check serum K+ |
| **Pulmonary Embolism** | ST elevation in V1 (occasionally V2-V3); T-wave inversions in V1-V4 | Right heart strain pattern: S1Q3T3; T-wave inversions in V1-V4 from RV strain (not LAD ischemia); sinus tachycardia; new incomplete or complete RBBB; right axis deviation; ST elevation limited to V1 (rarely V2); no ST elevation in V3-V4; clinical context of dyspnea > chest pain |

### 4.2 Coexisting Conditions

- **Anterior STEMI + pre-existing LBBB:** LBBB masks STEMI criteria. Use modified Sgarbossa criteria (Smith modification): concordant ST elevation >=1 mm (score 5), concordant ST depression >=1 mm in V1-V3 (score 3), or excessively discordant STE with ST/S ratio >=0.25 (score 2). Score >=3 is diagnostic. Sensitivity ~80%, specificity ~99%. If suspicion is high and criteria are not met, proceed to emergent catheterization based on clinical presentation.
- **Anterior STEMI + ventricular paced rhythm:** Paced QRS produces secondary ST-T changes similar to LBBB. Apply Sgarbossa criteria as for LBBB. Smith-modified Sgarbossa has been validated for ventricular paced rhythms (Dodd et al., Ann Emerg Med 2021).
- **Anterior STEMI + atrial fibrillation:** AF occurs in 5-10% of acute anterior STEMI. Irregular R-R intervals cause beat-to-beat ST variation. Average ST measurements across >=5 consecutive beats. New AF in the setting of anterior STEMI indicates large infarct territory and worse prognosis.
- **Anterior STEMI + right ventricular involvement:** Proximal LAD occlusion above the first RV branch can produce simultaneous anterior and RV infarction. Look for ST elevation in right-sided leads (V3R, V4R). RV involvement compounds hemodynamic compromise. Avoid nitrates and volume depletion — the failing RV is preload-dependent.
- **Anterior STEMI + posterior extension:** If LCx territory is also involved (especially with left-dominant circulation), look for ST depression in V1-V3 that PARTIALLY OFFSETS the expected anterior ST elevation, leading to underestimation of infarct size. Obtain posterior leads (V7-V9): ST elevation >=0.5 mm confirms posterior involvement.

---

## 5. STAT Classification

| Priority | Criteria |
|----------|----------|
| **STAT** | **YES** — Anterior STEMI is a STAT condition. It represents acute total occlusion of the LAD, threatening the largest single myocardial territory. Mortality without reperfusion: 25-30% at 30 days. Mortality with timely PCI: 3-5% at 30 days. Every 30-minute delay in reperfusion increases 1-year mortality by approximately 7.5% (De Luca et al., Heart 2004; reaffirmed in 2025 AHA/ACC STEMI guidelines). |
| **Time-sensitive** | **CRITICAL** — ECG must be acquired within 10 minutes of first medical contact (Class I, Level of Evidence A). STEMI activation must occur within 10 minutes of ECG acquisition. Door-to-balloon time target: <=90 minutes. First-medical-contact-to-device time: <=120 minutes for transfer cases. If PCI is not available within 120 minutes, thrombolytic therapy must be administered within 30 minutes of hospital arrival (door-to-needle <=30 min). "Time is muscle" — approximately 1.6 billion myocytes die per hour of total occlusion. |
| **Clinical action** | **Immediate:** (1) STEMI activation / Code STEMI (notify cath lab team); (2) Aspirin 325 mg chewed; (3) P2Y12 inhibitor loading (ticagrelor 180 mg or prasugrel 60 mg preferred over clopidogrel 600 mg); (4) Heparin bolus (unfractionated 60 U/kg, max 4000 U); (5) Sublingual nitroglycerin x3 (if SBP >90 and no RV involvement); (6) Morphine for refractory pain (use cautiously — may reduce P2Y12 absorption); (7) Emergent PCI with drug-eluting stent; (8) Consider GP IIb/IIIa inhibitor if high thrombus burden. **Post-PCI:** Dual antiplatelet therapy for 12 months minimum; high-dose statin; beta-blocker; ACE inhibitor/ARB (especially if EF <40%); echocardiography within 24-48 hours. |

---

## 6. Reasoning Complexity Analysis (Feeds Into Node 2.1 — Agent Architecture Research)

> **NOTE**: This section does NOT pre-assign agents. It documents the reasoning
> complexity of this condition so that Node 2.1 can determine the BEST agent
> architecture to handle ALL conditions. The actual agent assignment is filled
> in AFTER Node 2.1 research completes.

### 6.1 Reasoning Domains Required to Detect This Condition

**Primary reasoning domains:**
1. **ST-segment morphology analysis** — must detect elevation, classify morphology (concave vs convex), and measure amplitude at the J-point in every lead
2. **Lead-group correlation** — must identify that ST elevation is localized to a contiguous anterior lead group (V1-V4/V5) conforming to a single coronary territory
3. **Reciprocal change detection** — must identify ST depression in the non-contiguous inferior leads (II, III, aVF) as the mirror image of the primary injury
4. **Threshold application with demographic adjustment** — must apply different J-point thresholds based on patient sex and age
5. **T-wave morphology analysis** — must detect hyperacute T-waves (tall, broad, symmetric) as the earliest sign, even before ST elevation thresholds are formally met
6. **QRS morphology analysis** — must detect pathological Q-waves, R-wave amplitude loss, and new bundle branch blocks

**Cross-domain reasoning required:** YES
- Must integrate ischemia domain (ST/T changes) with conduction domain (new RBBB or LAFB) to recognize complicated anterior STEMI
- Must apply conditional logic: IF LBBB is present, THEN switch to Sgarbossa criteria rather than standard STEMI criteria
- Must integrate morphology domain (T-wave symmetry, ST concavity) with ischemia domain to distinguish hyperacute T-waves from LVH/BER/hyperkalemia

**Sequential reasoning required:** YES
- Step 1: Exclude artifact and ensure signal quality in V1-V4
- Step 2: Check for LBBB or paced rhythm (if present, branch to Sgarbossa pathway)
- Step 3: Measure ST elevation at J-point in V1-V4 with appropriate thresholds
- Step 4: Assess ST morphology (concave vs convex)
- Step 5: Check for reciprocal changes in inferior leads
- Step 6: Assess T-wave morphology for hyperacute pattern
- Step 7: Evaluate Q-waves and R-wave progression
- Step 8: Check aVR for proximal LAD/left main markers
- Step 9: Synthesize — confirm diagnosis, estimate territory, and assign confidence

### 6.2 Feature Dependencies

**ESSENTIAL computed features (from SDA-1):**
- `st_elevation_j_point[lead]` — ST amplitude at J-point for all 12 leads (mm)
- `st_morphology[lead]` — concave / straight / convex / tombstone classification
- `t_wave_amplitude[lead]` — peak T-wave amplitude (mm)
- `t_wave_symmetry[lead]` — ratio of ascending to descending limb slopes
- `t_wave_width[lead]` — duration of T-wave base (ms)
- `q_wave_present[lead]` — boolean
- `q_wave_duration[lead]` — duration in ms (pathological if >=40 ms)
- `q_wave_depth_ratio[lead]` — Q amplitude / R amplitude (pathological if >=0.25)
- `r_wave_amplitude[lead]` — R-wave amplitude in V1-V6 (for R-wave progression)
- `qrs_duration` — total QRS duration (ms)
- `patient_sex` — required for threshold selection
- `patient_age` — required for threshold selection (men <40 vs >=40)

**SUPPORTING features (increase confidence but not strictly required):**
- `st_depression_max_inferior` — maximum reciprocal ST depression in II/III/aVF (presence strongly supports diagnosis)
- `r_wave_progression` — computed R-wave progression score across V1-V6
- `terminal_qrs_distortion[lead]` — absence of S-wave and J-point in V1-V3 (high-risk marker)
- `heart_rate` — sinus tachycardia supports acute MI; extreme bradycardia suggests high-grade AV block
- `qrs_axis` — new LAD suggests LAFB (septum involvement); new RAD suggests LPFB
- `qtc` — prolonged QTc increases arrhythmia risk stratification
- `avr_st_elevation` — ST elevation in aVR suggests proximal LAD / left main

**EXCLUSION features (if present, reconsider diagnosis):**
- `diffuse_st_elevation` — ST elevation in >2 non-contiguous territories suggests pericarditis, not STEMI
- `pr_depression` — PR depression in multiple leads suggests pericarditis
- `lbbb_present` — if LBBB is present, standard STEMI criteria are invalid; switch to Sgarbossa
- `paced_rhythm` — if paced, standard criteria invalid; switch to Sgarbossa
- `t_wave_narrow_peaked_diffuse` — narrow-based peaked T-waves in ALL leads suggest hyperkalemia, not ischemia

**Per-beat vs aggregate:**
- ST elevation, T-wave morphology, Q-waves: aggregate analysis (median of sinus beats, excluding PVCs and post-PVC beats)
- QRS duration: per-beat (to detect intermittent bundle branch block)
- R-wave amplitude: aggregate (trend across V1-V6)

### 6.3 Cross-Condition Interactions

**This condition affects how OTHER conditions present:**
- Anterior STEMI can CAUSE new RBBB (10%), new LAFB (5%), or complete heart block (5-8%) — these conduction abnormalities are consequences, not confounders
- Large anterior STEMI can cause secondary AF (5-10%), which complicates ST measurement but does not invalidate the STEMI diagnosis
- Anterior STEMI reperfusion (post-PCI) commonly produces accelerated idioventricular rhythm (AIVR) — this is a reperfusion marker, not a new arrhythmia diagnosis

**Detecting this condition requires ruling out:**
1. BER (check: reciprocal changes, morphology, Smith's ST/T ratio)
2. LVH with repolarization abnormality (check: voltage criteria, proportionality of ST to QRS)
3. Pericarditis (check: diffuse vs territorial, PR depression, Spodick's sign)
4. LBBB (check: QRS duration and morphology first; if LBBB, branch to Sgarbossa)
5. LV aneurysm (check: acute evolution on serial ECG, troponin, clinical history)

**Condition combinations that change interpretation:**
- Anterior STEMI + LBBB = requires Sgarbossa criteria (standard criteria invalid)
- Anterior STEMI + RV extension = avoid nitrates, aggressive fluids
- Anterior STEMI + posterior extension = ST elevation in V1-V3 may be partially cancelled by posterior ST depression vector; true infarct size is underestimated. Check V7-V9.
- Anterior STEMI + hyperkalemia = peaked T-waves from hyperkalemia superimposed on hyperacute T-waves from ischemia; very difficult to distinguish. Treat both empirically (calcium, insulin/glucose AND cath lab activation).

### 6.4 Reasoning Chain Sketch

**Minimum reasoning chain (fewest steps to high confidence):**
1. ST elevation >=2.0 mm (men >=40) or >=2.5 mm (men <40) or >=1.5 mm (women) in >=2 of V2-V4 with convex morphology
2. Reciprocal ST depression in >=1 of II, III, aVF
3. No LBBB, no paced rhythm, no diffuse ST elevation
4. **Confidence: HIGH (>=0.90)** — this 3-step chain is sufficient for STEMI activation

**Full reasoning chain (complete evidence assembly):**
1. Confirm signal quality in V1-V4 (SNR adequate, no baseline wander, no lead reversal)
2. Verify no LBBB or paced rhythm (if present, branch to Sgarbossa)
3. Measure J-point ST elevation in V1-V6, I, aVL, II, III, aVF, aVR
4. Apply sex/age-appropriate thresholds to V2-V3; >=1 mm threshold to all other leads
5. Confirm >=2 contiguous leads with ST elevation above threshold
6. Classify ST morphology: concave (early/equivocal) vs convex/tombstone (established/definite)
7. Detect reciprocal ST depression in II, III, aVF (strengthens diagnosis)
8. Assess T-wave morphology: hyperacute (tall, broad, symmetric) vs normal vs peaked-narrow (hyperkalemia)
9. Assess Q-waves in V1-V4: pathological Q (>=40 ms or >=25% of R) indicates evolving infarction
10. Assess R-wave progression across V1-V6: poor progression or R-wave loss supports infarction
11. Check aVR: ST elevation >1 mm suggests proximal LAD or left main
12. Check for terminal QRS distortion in V1-V3 (prognostic marker)
13. Check for new RBBB or LAFB (indicates large septal territory)
14. Integrate all findings → assign confidence level and territory estimate
15. Flag as STAT with time-to-treatment urgency

### 6.5 Confidence Anchors

**HIGH confidence (>=0.90) — any single criterion sufficient:**
- Convex (dome-shaped) ST elevation meeting sex/age thresholds in >=2 of V1-V4 WITH reciprocal ST depression in >=1 inferior lead
- Tombstone ST pattern in V2-V4
- Terminal QRS distortion with ST elevation in V1-V4

**MODERATE confidence (0.70-0.89):**
- ST elevation meeting thresholds in V1-V4 but WITHOUT reciprocal changes (possible early STEMI, or differential includes pericarditis/BER)
- Hyperacute T-waves in V2-V4 (tall, broad, symmetric) without yet meeting formal ST elevation thresholds (possible hyperacute STEMI — recommend serial ECGs at 15-minute intervals)
- Concave (scooped) ST elevation meeting thresholds with reciprocal changes (probable STEMI in early evolution)

**LOW confidence (0.50-0.69) — warrants further evaluation:**
- Borderline ST elevation (just meeting threshold) with concave morphology and no reciprocal changes (could be BER, LVH, or early STEMI)
- ST elevation in presence of LVH voltage criteria (could be repolarization abnormality)

**Confidence DECREASE triggers:**
- Absence of reciprocal changes: -0.10 to -0.15
- Concave ST morphology: -0.05 to -0.10 (can still be early STEMI; do not exclude)
- ST elevation in >2 non-contiguous territories: -0.20 (suggests pericarditis or non-ischemic cause)
- PR depression in multiple leads: -0.15 (suggests pericarditis)
- Smith's ST/T ratio <0.25 in V3: -0.10 (favors BER)
- Normal R-wave progression: -0.05

**Pathognomonic (near-100% specific):**
- Convex ST elevation V1-V4 + reciprocal depression III/aVF + new Q-waves V1-V3 + troponin rise = definite anterior STEMI. (The ECG agent does not have troponin data — but the ECG pattern alone with the first three features reaches ~98% specificity.)

**Classification tiers:**
- **Possible anterior STEMI (confidence 0.50-0.69):** Borderline ST elevation or hyperacute T-waves without other supporting features. Recommend: serial ECG at 15-minute intervals, urgent troponin, clinical correlation.
- **Probable anterior STEMI (confidence 0.70-0.89):** ST elevation meeting criteria but with equivocal morphology or absent reciprocal changes. Recommend: immediate cardiology consultation, prepare for possible cath lab activation.
- **Definite anterior STEMI (confidence >=0.90):** Classic pattern with convex STE + reciprocal changes. Recommend: immediate STEMI activation (Code STEMI), cath lab mobilization, do NOT wait for troponin.

### 6.6 Difficulty Score

| Dimension | Score (1-5) | Notes |
|-----------|-------------|-------|
| Signal clarity needed | 2 | ST elevation in STEMI is a large signal (2-10+ mm) — detectable even in moderately noisy tracings. V1-V3 are less prone to motion artifact than limb leads. Baseline wander is the main threat — must be corrected before measurement. |
| Number of leads required | 2 | Can be definitively diagnosed from V2-V3 alone (2 contiguous leads). Reciprocal changes in III/aVF increase confidence but are not strictly required for diagnosis. |
| Cross-domain reasoning | 3 | Requires integration of ST analysis + T-wave morphology + QRS analysis + lead-group correlation. Must branch to Sgarbossa pathway if LBBB detected. Moderate cross-domain complexity. |
| Temporal pattern complexity | 2 | STEMI is a constant (non-intermittent) pattern within a single ECG. Does not require beat-to-beat analysis (exception: stuttering STEMI, which is rare). Temporal evolution across serial ECGs is important clinically but not needed for single-ECG diagnosis. |
| Differential complexity | 4 | Multiple mimics must be excluded: BER, LVH strain, pericarditis, Takotsubo, LBBB, LV aneurysm, hyperkalemia. Each mimic has a distinct exclusion criterion, requiring systematic differential reasoning. In practice, BER vs STEMI in young patients is the hardest differentiation. |
| Rarity in PTB-XL | 2 | Anterior STEMI (or anterior MI pattern) is well-represented in PTB-XL. The diagnostic_superclass "MI" contains 5486 records; anterior MI is the largest subset. Sufficient examples for validation and threshold tuning. |
| **Overall difficulty** | **2.5** | **Anterior STEMI is a HIGH-AMPLITUDE, TERRITORIAL pattern with CLEAR criteria — one of the easier acute conditions to detect algorithmically. The difficulty lies entirely in the differential diagnosis (particularly BER vs STEMI) and the Sgarbossa branch. The low overall difficulty reflects the large electrical signal and well-defined diagnostic criteria, offset by the moderate complexity of differentials.** |

---

## 6A. Agent Assignment

**Architecture:** Option E — 3 Parallel Phase 1 Specialists + 1 Sequential CDS (Node 2.1 Gate Passed 2026-03-27)

| Agent | Role for Anterior STEMI | Key Features Used |
|-------|--------------------------|-------------------|
| **RRC** (Rhythm/Rate/Conduction) | Supporting | Ventricular rate, rhythm regularity, QRS duration (detect LBBB — triggers Sgarbossa branch), axis deviation, presence of AV conduction abnormalities |
| **IT** (Ischemia/Territory) | Primary | ST elevation ≥1–2.5 mm (sex/age-adjusted) in ≥2 contiguous leads V1–V6/I/aVL, hyperacute T-waves in anterior leads, reciprocal ST depression in II/III/aVF, coronary territory assignment (LAD/diagonal/left main), pathological Q-waves V1–V4 |
| **MR** (Morphology/Repolarization) | Supporting | LVH voltage criteria (affects ST baseline), R-wave progression V1–V4, QRS morphology assessment in context of LBBB pattern if detected |
| **CDS** (Cross-Domain Synthesis) | Required — resolves LBBB+STEMI via Sgarbossa criteria | Receives RRC LBBB flag + IT ischemic ST findings; applies modified Sgarbossa criteria (concordant STE ≥1 mm, concordant STD ≥1 mm in V1–V3, discordant STE ≥25% of S-wave) when LBBB is present; integrates MR voltage findings to contextualize ST baseline; generates final confidence-scored diagnosis |

### Primary Agent
**IT** — anterior STEMI is defined by ischemic ST elevation in the LAD territory, which is the IT agent's core domain.

### Cross-Domain Hints
- RRC emits `cross_domain_hint: "LBBB detected — Sgarbossa criteria required for ischemia interpretation (forward to CDS)"` when QRS duration ≥120 ms with LBBB morphology is identified.
- IT emits `cross_domain_hint: "ST elevation present with wide QRS — confirm LBBB vs RBBB with RRC before territory assignment"` when ST elevation accompanies QRS duration ≥120 ms.

### CDS Specific Role
CDS receives the LBBB flag from RRC and the ischemic ST findings from IT, then applies the modified Sgarbossa criteria to determine whether the ST changes exceed what is expected from the LBBB alone. CDS also integrates MR's LVH voltage findings to contextualize whether elevated baseline ST is pre-existing strain pattern versus acute injury. Final output is a confidence-scored anterior STEMI call with explicit notation of whether Sgarbossa criteria were invoked.

---

## 7. RAG Knowledge Requirements

### 7.1 Textbook References

| Book | Relevance | Key Chapters/Sections |
|------|-----------|----------------------|
| **Goldberger — Clinical Electrocardiography: A Simplified Approach (10th ed.)** | High — best for foundational pathophysiology of ST elevation and injury current | Chapter 8: ST Elevations and Q Waves (Myocardial Infarction); Chapter 9: STEMI — Clinical and ECG Correlations; Figures 8-1 through 8-12 (injury current vectors) |
| **Chou's Electrocardiography in Clinical Practice (7th ed.)** | Very High — the most comprehensive reference for lead-by-lead presentation and differential diagnosis | Chapter 5: Myocardial Ischemia and Infarction; Section 5.3: Anterior Wall MI; Section 5.7: Differential Diagnosis of ST Elevation; Tables 5-2, 5-3 (sex-specific thresholds) |
| **Marriott's Practical Electrocardiography (13th ed.)** | High — excellent morphology atlas with annotated tracings | Chapter 5: Myocardial Infarction; Section on hyperacute T-waves (pp. 96-103); Figure series 5.1-5.15; Chapter 17: ST Segment Elevation — Differential Diagnosis |
| **Braunwald's Heart Disease (12th ed.)** | Moderate — comprehensive clinical context but less ECG-focused | Chapter 35: ST-Elevation Myocardial Infarction; Chapter 13: Electrocardiography (ECG sections on acute MI); Tables on reperfusion criteria and prognostic ECG markers |

### 7.2 Key Figures

- **Goldberger Fig 8-3:** Injury current vector diagram showing anterior wall projection onto V1-V4 — ideal for the "Why It Appears on ECG" explanation
- **Chou's Fig 5-12:** Complete temporal evolution of anterior STEMI (hyperacute → acute → subacute → chronic) in a 12-lead montage
- **Marriott's Fig 5.8:** Hyperacute T-wave morphology comparison (hyperacute vs normal vs hyperkalemia vs BER)
- **Chou's Fig 5-18:** Tombstone ST elevation vs convex vs concave morphology atlas
- **Goldberger Fig 8-7:** Reciprocal change mechanism — anterior STE producing inferior STD by mirror projection

---

## 8. Dashboard Visualization Specification

### 8.1 Highlighted Leads

**Primary highlight (red/critical):** V1, V2, V3, V4 — these contain the diagnostic ST elevation

**Secondary highlight (blue/reciprocal):** III, aVF, (II if reciprocal depression present) — reciprocal changes

**Tertiary highlight (orange/warning):** aVR if ST elevation >1 mm (proximal LAD / left main marker); I, aVL if ST elevation present (lateral extension)

**Lead arrangement on dashboard:** Display leads in anatomical grouping, not standard format:
- Top row: aVL, I (high lateral)
- Middle row: V1, V2, V3, V4, V5, V6 (precordial, left to right)
- Bottom row: II, III, aVF (inferior)
- Corner: aVR (with separate annotation if elevated)

### 8.2 Arrows and Annotations

| Location | Arrow/Annotation | Label |
|----------|-----------------|-------|
| V2-V3: J-point | Horizontal line at J-point with vertical measurement arrow from baseline to J-point | "STE: X.X mm (threshold: Y.Y mm for [sex/age])" |
| V2-V3: ST segment contour | Curved annotation tracing the ST morphology | "Convex (dome)" or "Concave (early)" or "Tombstone" |
| V2-V3: T-wave peak (if hyperacute) | Arrow pointing to T-wave peak | "Hyperacute T: XX mm, broad-based, symmetric" |
| V1-V3: Q-wave (if present) | Arrow to Q-wave onset and offset | "Pathological Q: XX ms" |
| V1-V4: R-wave | Small amplitude markers | "R-wave loss" (if < expected) |
| III, aVF: ST depression | Downward arrow from baseline to ST nadir | "Reciprocal STD: X.X mm" |
| aVR: ST elevation (if >1 mm) | Warning badge | "aVR STE >1 mm: proximal LAD / left main?" |
| Global | Animated STAT badge, red pulsing border | "STAT — Anterior STEMI — Activate Cath Lab" |
| Timeline bar | Colored bar showing estimated phase | "Phase: [Hyperacute / Acute / Evolving]" based on morphology |

### 8.3 Clinician Explanation (Plain Language)

**For ER Nurse / Triage (2-3 sentences):**
> This ECG shows ST elevation in the anterior chest leads (V1-V4) consistent with an acute anterior heart attack. The main artery supplying the front wall of the heart (LAD) is blocked. This is a STAT finding — notify the attending and activate the cath lab immediately. Time is critical: every minute of delay causes permanent heart muscle damage.

**For Cardiologist (expanded):**
> Acute anterior STEMI pattern with [convex/tombstone] ST elevation in V1-V[3/4/5] (maximal in V[2/3]: [X.X] mm), meeting [sex/age-appropriate] thresholds. Reciprocal ST depression present in leads [III/aVF/II] (maximal in III: [X.X] mm). [If applicable: Hyperacute T-wave morphology in V2-V3 suggests early/hyperacute phase.] [If applicable: Pathological Q-waves in V[1-3] indicate evolving infarction.] [If applicable: New RBBB/LAFB suggests large septal territory at risk.] [If applicable: aVR ST elevation [X.X] mm raises concern for proximal LAD or left main involvement.] R-wave progression: [normal/poor/absent in V1-V4]. QTc: [XXX] ms. Territory estimate: [septal/anterior/anterolateral/extensive anterior]. Recommend emergent PCI. Door-to-balloon target: <=90 minutes.

---

## 9. Edge Cases and Pitfalls

### 9.1 Female Patients — Lower Thresholds

Women have lower baseline ST elevation and lower normal T-wave amplitude than men due to hormonal effects on repolarization and smaller cardiac mass. The sex-specific V2-V3 threshold (>=1.5 mm for women vs >=2.0-2.5 mm for men) was introduced in the 2012 Third Universal Definition of MI (Thygesen et al., Circulation 2012) and retained in the 2018 Fourth Universal Definition and 2025 guidelines.

**Pitfall:** Anterior STEMI in women is underdiagnosed when male thresholds are applied. A woman with 1.5 mm ST elevation in V2-V3 with reciprocal inferior depression meets STEMI criteria but would be missed at the male threshold of 2.0 mm. The agent MUST apply sex-specific thresholds. If sex is unknown, use the lower female threshold to avoid false negatives in a STAT condition.

### 9.2 Elderly Patients — Atypical Presentation

Patients >75 years frequently present with atypical symptoms (dyspnea, confusion, syncope rather than chest pain). ECG changes may be blunted:
- Baseline LVH may produce pre-existing ST elevation in V1-V3, masking acute changes
- Pre-existing Q-waves from prior MI reduce the diagnostic value of new Q-waves
- Baseline conduction abnormalities (RBBB, LBBB, LAFB) are more common, complicating interpretation

**Pitfall:** Serial ECG comparison is critical in the elderly. A "normal-looking" ECG in an elderly patient with dyspnea may show subtle dynamic ST changes on serial tracings. The agent should lower its confidence threshold for recommending serial ECGs in patients >75.

### 9.3 Posterior Extension (LAD + LCx Territory)

In patients with a wraparound LAD or concurrent LCx disease, posterior wall involvement can occur alongside anterior STEMI. The posterior injury vector (pointing posteriorly) partially cancels the anterior injury vector (pointing anteriorly) in leads V1-V3, resulting in UNDERESTIMATION of total infarct size.

**Pitfall:** V1-V3 ST elevation may appear smaller than expected for the actual infarct size. If clinical severity (cardiogenic shock, hemodynamic instability) seems disproportionate to the modest V1-V3 ST elevation, suspect posterior extension. Posterior leads V7-V9 showing ST elevation >=0.5 mm confirm this.

**Agent action:** If anterior STE is present but the magnitude in V1-V2 seems attenuated relative to V3-V4 (an unusual gradient), flag possible posterior extension and recommend V7-V9.

### 9.4 Right Ventricular Extension

Proximal LAD occlusion (above the origin of the first RV branch) can produce concurrent RV ischemia. This is more common when the LAD wraps around the apex to supply the inferior wall.

**Pitfall:** RV involvement causes preload-dependent hemodynamic compromise. Standard treatment (nitroglycerin, diuretics) can be catastrophic. Right-sided leads (V3R, V4R) are not part of the standard 12-lead ECG. The agent should flag proximal LAD occlusion markers (aVR elevation, extensive V1-V6 territory) and recommend right-sided leads.

### 9.5 De Winter Pattern (STEMI Equivalent in LAD Occlusion)

1-2% of acute LAD occlusions present NOT with ST elevation but with the de Winter pattern: upsloping ST depression >1 mm at the J-point in V1-V6 with tall, symmetric, peaked T-waves. ST elevation in aVR is typically present.

**Pitfall:** This pattern does NOT meet STEMI criteria but represents an acute LAD occlusion requiring emergent reperfusion. The agent must recognize the de Winter pattern as a STEMI equivalent (covered in detail in Node 2.7.7 — `de_winter_t_waves.md`). The link between this file and the de Winter file must be bidirectional.

### 9.6 Wellens Syndrome (Critical LAD Stenosis — Pre-Infarction)

Wellens syndrome represents critical LAD stenosis with spontaneous reperfusion. ECG shows deep symmetric T-wave inversions (Type A: biphasic T in V2-V3; Type B: deeply inverted symmetric T in V2-V4) with minimal or no troponin elevation and no ST elevation.

**Pitfall:** Wellens is a WARNING of imminent anterior STEMI. If a patient with Wellens pattern undergoes stress testing, it may provoke complete occlusion. The agent should recognize Wellens morphology (covered in Node 2.7.6 — `wellens_syndrome.md`) and flag it with appropriate urgency.

### 9.7 Lead Misplacement

V1-V2 lead placement one intercostal space too high (a common error) can produce ST elevation mimicking anterior STEMI. This is because electrodes placed over the outflow tract record the Brugada-zone repolarization pattern.

**Pitfall:** If ST elevation is present in V1-V2 but NOT in V3-V4, and the ST morphology has a saddle-back or coved appearance (Brugada-like), consider lead misplacement. The agent should flag isolated V1-V2 ST elevation without V3-V4 involvement as potentially artifactual and recommend lead position verification.

### 9.8 Early Repolarization vs Hyperacute STEMI in Young Men

Young men (<40) have the highest prevalence of BER (up to 15-25% in some populations) and the highest ST elevation thresholds (>=2.5 mm). This creates a diagnostic dilemma: is this ST elevation BER or hyperacute STEMI?

**Key discriminators the agent should use:**
1. **Smith's rule (ST60V3 / T-wave amplitude V3):** Ratio >=0.25 favors STEMI; <0.25 favors BER (sensitivity 86%, specificity 91%; Smith SW et al., Ann Emerg Med 2012)
2. **Reciprocal changes:** Present in STEMI, absent in BER
3. **Morphology:** BER has a J-point notch or slur; STEMI has a smooth J-point transition
4. **Dynamic evolution:** STEMI evolves over minutes; BER is stable. Serial ECGs at 15-minute intervals are definitive.
5. **T-wave symmetry:** Hyperacute T-waves are symmetric; BER T-waves maintain normal asymmetry

### 9.9 Massive Anterior STEMI with Cardiogenic Shock

Extensive anterior STEMI (V1-V6 + I + aVL) may present with diffuse ST elevation that can be confused with pericarditis. However:
- Territorial contiguity (all precordial + high lateral) follows LAD + diagonal distribution
- Reciprocal depression is present in III, aVF
- Patient is in cardiogenic shock (hypotension, tachycardia, pulmonary edema)
- No PR depression or Spodick's sign

**Pitfall:** Massive anterior STEMI mimicking pericarditis can delay cath lab activation. Reciprocal changes are the key differentiator.

---

## 10. References

### Guidelines
1. Writing Committee, 2025 AHA/ACC/ACEP/NAEMSP/SCAI Guideline for the Management of Patients With Acute Myocardial Infarction. *Circulation*. 2025;151:eXXX. (2025 STEMI Guideline — primary reference for diagnostic criteria and treatment algorithms)
2. Byrne RA, Rossello X, Coughlan JJ, et al. 2023 ESC Guidelines for the management of acute coronary syndromes. *Eur Heart J*. 2023;44(38):3720-3826. (ESC 2023 ACS — sex-specific thresholds, contiguous lead definition)
3. Thygesen K, Alpert JS, Jaffe AS, et al. Fourth Universal Definition of Myocardial Infarction (2018). *Circulation*. 2018;138(20):e618-e651. (Pathological Q-wave criteria, MI classification system)

### Key Papers
4. Smith SW, Dodd KW, Henry TD, et al. Diagnosis of ST-elevation myocardial infarction in the presence of left bundle branch block with the ST-elevation to S-wave ratio in a modified Sgarbossa rule. *Ann Emerg Med*. 2012;60(6):766-776. (Modified Sgarbossa criteria — ST/S ratio >=0.25)
5. De Luca G, Suryapranata H, Ottervanger JP, Antman EM. Time delay to treatment and mortality in primary angioplasty for acute myocardial infarction: every minute of delay counts. *Circulation*. 2004;109(10):1223-1225. (Time-to-treatment mortality data — 7.5% increase per 30-minute delay)
6. de Winter RJ, Verouden NJ, Wellens HJ, Wilde AA. A new ECG sign of proximal LAD occlusion. *N Engl J Med*. 2008;359(19):2071-2073. (de Winter T-wave pattern description)
7. Birnbaum Y, Sclarovsky S, Mager A, et al. ST segment depression in aVL: a sensitive marker for acute inferior myocardial infarction. *Eur Heart J*. 1993;14(1):4-7. (Reciprocal change significance)
8. Birnbaum Y, Herz I, Sclarovsky S, et al. Prognostic significance of the admission electrocardiogram in acute myocardial infarction. *J Am Coll Cardiol*. 1996;27(5):1128-1132. (Terminal QRS distortion as prognostic marker)
9. Smith SW, Khalil A, Henry TD, et al. Electrocardiographic differentiation of early repolarization from subtle anterior ST-segment elevation myocardial infarction. *Ann Emerg Med*. 2012;60(1):45-56. (Smith's rule — ST60V3/T ratio for BER vs STEMI differentiation)
10. Dodd KW, Zvosec DL, Hart MA, et al. Electrocardiographic diagnosis of acute coronary occlusion myocardial infarction in ventricular paced rhythm using the modified Sgarbossa criteria. *Ann Emerg Med*. 2021;78(4):517-529. (Sgarbossa validation for paced rhythms)

### Textbook References
11. Goldberger AL, Goldberger ZD, Shvilkin A. *Clinical Electrocardiography: A Simplified Approach*. 10th ed. Elsevier; 2024. Chapters 8-9.
12. Surawicz B, Knilans TK. *Chou's Electrocardiography in Clinical Practice*. 7th ed. Saunders; 2020. Chapter 5.
13. Wagner GS, Strauss DG. *Marriott's Practical Electrocardiography*. 13th ed. Wolters Kluwer; 2022. Chapter 5.
14. Libby P, Bonow RO, Mann DL, et al. *Braunwald's Heart Disease: A Textbook of Cardiovascular Medicine*. 12th ed. Elsevier; 2022. Chapters 13, 35.
