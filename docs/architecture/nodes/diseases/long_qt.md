# Long QT Syndrome — ECG Manifestation from First Principles

**Node:** 2.7.80
**SDA:** SDA-2 (Diagnosis & Agentic Core) — shared resource for SDA-1, SDA-3, SDA-4
**Status:** Research Complete
**PGMR:** Required
**Date:** 2026-03-27

---

## 1. Pathophysiology Root Cause

### 1.1 What Goes Wrong
- Long QT Syndrome (LQTS) is defined by abnormally prolonged ventricular repolarization. The action potential duration (APD) is extended beyond normal limits, delaying return of ventricular myocytes to their resting state
- **Congenital LQTS** arises from inherited mutations in genes encoding cardiac ion channels. The three major subtypes account for ~90% of genotype-positive cases:
  - **LQT1 (KCNQ1 — IKs channel)**: Loss-of-function in the slow delayed rectifier potassium channel. IKs normally activates during sympathetic stimulation to accelerate repolarization at faster heart rates. Loss of IKs → APD fails to shorten appropriately with exercise → QT does not shorten with tachycardia → arrhythmic events triggered by exercise, particularly swimming, and emotional stress
  - **LQT2 (KCNH2/hERG — IKr channel)**: Loss-of-function in the rapid delayed rectifier potassium channel. IKr is the dominant repolarizing current during phase 3. Loss of IKr → prolonged phase 3 → markedly prolonged APD. Arrhythmic events triggered by sudden auditory stimuli (alarm clock, phone ringing) and emotional arousal; acute sympathetic surges create transmural dispersion of repolarization (TDR) in already-vulnerable myocardium
  - **LQT3 (SCN5A — INa channel)**: Gain-of-function in the cardiac sodium channel (same gene as Brugada, but opposite functional effect). Persistent late inward sodium current (late INa) during the plateau phase → prolonged phase 2 → prolonged APD. Bradycardia-dependent: events occur predominantly at rest and during sleep, because the late INa has more time to prolong the plateau at slower rates
- **Acquired LQTS** is far more prevalent in clinical practice than congenital LQTS:
  - **Drug-induced (most common cause of QT prolongation globally)**: Most QT-prolonging drugs block the hERG/IKr channel, mimicking LQT2 at the channel level. Complete reference at www.crediblemeds.org
  - **Electrolyte imbalances**: Hypokalemia (reduces IKr conductance), hypomagnesemia (impairs Na+/K+-ATPase and multiple repolarizing currents), hypocalcemia (prolongs phase 2 plateau by delaying ICa-L inactivation)
  - **Bradycardia**: Slow heart rates independently prolong APD and amplify the QT-prolonging effect of drugs or electrolyte abnormalities
  - **Structural heart disease**: Heart failure, LVH, myocardial ischemia — all cause ion channel remodeling that prolongs repolarization

### 1.2 Electrical Consequence
- **Prolonged phase 3 repolarization**: Regardless of the specific channel mutation or drug effect, the net result is delayed completion of repolarization → prolonged QT interval
- **Early afterdepolarizations (EADs)**: During the abnormally extended plateau and phase 3, L-type calcium channels (ICa-L) recover from inactivation before repolarization completes → spontaneous late inward calcium current → secondary depolarizations (EADs) that appear as oscillations in membrane voltage → if an EAD reaches threshold, a triggered action potential fires
- **Transmural dispersion of repolarization (TDR)**: Mid-myocardial M-cells have the longest intrinsic APD due to weaker IKs expression. QT-prolonging conditions disproportionately affect M-cells, creating large TDR. Large TDR = substrate for re-entry when an EAD-triggered PVC fires as the trigger
- **Torsades de Pointes (TdP) risk**: TdP — the arrhythmia of LQTS — is a polymorphic VT initiated by the trigger (EAD-triggered PVC) meeting the substrate (heterogeneous TDR). QTc ≥500 ms marks the clinically recognized threshold for substantially elevated TdP risk

### 1.3 Why It Appears on ECG
- **QT interval prolongation**: The QT interval spans from the start of QRS to the end of the T-wave, representing all of ventricular depolarization + repolarization. Prolonged APD pushes the T-wave end rightward → measurably longer QT in all leads
- **Subtype-specific T-wave morphology**: The phase of the action potential that is primarily prolonged determines the visible T-wave shape on ECG:
  - LQT1 (IKs loss): Prolongation of the late repolarization phase → **broad-based, smooth, rounded T-wave**. The T-wave is wide at the base but retains normal amplitude. Looks like a normal T-wave stretched horizontally
  - LQT2 (IKr loss): Loss of the dominant phase 3 current unmasks transmural repolarization gradient discontinuities → **notched or bifid T-wave** with low amplitude. The notch creates two distinct humps separated by a trough. Most visible in V2-V5
  - LQT3 (late INa gain): Prolongation of the plateau phase 2 → **long isoelectric ST segment** followed by a relatively narrow, late-appearing T-wave. The flat ST segment is the hallmark; the T-wave itself may look nearly normal but starts late
- **QTc prolongation is global**: Unlike Brugada (V1-V3 only), QT prolongation is present in ALL leads — the entire ventricular myocardium has prolonged repolarization. Morphological changes are most evident in V2-V5 where T-wave amplitude is largest

---

## 2. ECG Presentation — Lead by Lead

### 2.1 Diagnostic Criteria (2025 AHA/ESC Guidelines)

| Criterion | Threshold / Detail | Source |
|-----------|-------------------|--------|
| QTc upper normal — male | 440 ms (borderline 441–460; prolonged 461–480; markedly prolonged >480 ms) | 2025 AHA/ACC/HRS; Bazett 1920 |
| QTc upper normal — female | 450 ms (borderline 451–470; prolonged 471–500; markedly prolonged >500 ms) | 2025 AHA; Moss 1991 |
| High TdP risk threshold | QTc ≥500 ms in any patient, any sex | 2025 AHA; 2025 ESC; Priori 2003 |
| Critical danger zone | QTc ≥600 ms — very high TdP risk | Expert consensus |
| Bazett correction | QTc = QT / √RR (seconds). Standard clinical use; overestimates at fast HR, underestimates at slow HR | Bazett 1920; AHA standard |
| Fridericia correction | QTc = QT / RR^(1/3) (seconds). More accurate at HR <60 or >100 bpm | Fridericia 1920; 2025 ESC preferred |
| Hodges correction | QTc = QT + 1.75 × (HR − 60). Linear correction; less common | Hodges 1983 |
| LQT1 T-wave | Broad-based, smooth, rounded T-wave; wide base; normal or near-normal amplitude | Zhang 2000; Moss 1995 |
| LQT2 T-wave | Notched or bifid T-wave; two humps; low amplitude; most prominent V2-V5 | Zhang 2000; Moss 1995 |
| LQT3 T-wave | Long isoelectric ST segment; late-onset narrow T-wave; flat plateau phase visible | Zhang 2000; Moss 1995 |
| Schwartz score for congenital LQTS | ≥3.5 points = high probability; 1.5–3.0 = intermediate; ≤1.0 = low | Schwartz 2011; 2025 ESC |
| Drug-induced LQTS screen | Check www.crediblemeds.org for all medications; hypoK, hypoMg, hypoCa as cofactors | AHA 2025; CredibleMeds |

### 2.2 Lead-by-Lead Manifestation

| Lead | Expected Finding | Why | Sensitivity |
|------|-----------------|-----|-------------|
| I | Prolonged QTc; T-wave broad (LQT1), notched (LQT2), or late-onset (LQT3) | Leftward horizontal lead sees global repolarization; T-wave amplitude moderate | Moderate |
| II | Prolonged QTc (primary measurement lead); subtype T-wave morphology visible | Aligned with mean repolarization vector (+60°); clearest T-wave delineation; standard for QT measurement | Very High |
| III | Prolonged QTc; T-wave morphology visible but variable amplitude | Inferior axis (+120°); secondary QT measurement lead | Moderate |
| aVR | Prolonged QTc; T-wave normally inverted — inversion is broader/deeper with LQTS | Opposite direction (-150°); inverted T makes morphological subtyping difficult | Low |
| aVL | Prolonged QTc; T-wave morphology changes visible | Superior leftward view (-30°); useful confirmation lead | Moderate |
| aVF | Prolonged QTc; T-wave morphology changes visible | Inferior (+90°); reliable QT measurement, good for confirmation | Moderate-High |
| V1 | Prolonged QTc; T-wave normally biphasic or inverted; LQT2 bifid pattern may appear | Anterior septal; T-wave end may be ambiguous due to biphasic morphology | Moderate |
| V2 | Prolonged QTc; LQT2 notched/bifid T-wave first apparent here; LQT3 long ST segment visible | Anterior septal transitional; T-wave amplitude increases; morphological changes emerging | High |
| V3 | Prolonged QTc; all three subtype T-waves clearly visible; T-wave alternans detectable | Anterior LV; large T-wave amplitude makes subtle changes (notching, broadening, delayed onset) most visible | Very High |
| V4 | Prolonged QTc; T-wave morphology highly visible; often the lead with maximum T-wave amplitude | LV apex; largest T-wave amplitude; best for morphological detail but end-point identification can be difficult when T is very tall | Very High |
| V5 | Prolonged QTc; broad T (LQT1), notched T (LQT2) clearly identifiable; good secondary QTc measurement | Lateral LV; T-wave moderate-to-large; excellent confirmation lead | High |
| V6 | Prolonged QTc; T-wave smaller; morphological changes less prominent | Far lateral LV; smaller T-wave; less useful for subtyping but QT measurement reliable | Moderate |

### 2.3 Key Leads
- **Lead II**: Primary lead for QTc measurement; standard T-wave end-point determination; best for identifying RR sequences (short-long-short pattern)
- **V3-V4**: Best leads for T-wave morphology subtyping (LQT1 vs LQT2 vs LQT3) and T-wave alternans detection
- **V5**: Excellent supplementary QTc measurement when lead II T-wave end is ambiguous
- **Longest QT lead**: Per guidelines, QTc should be measured in the lead showing the longest unambiguous QT interval; exclude leads where T-wave end cannot be confidently determined
- **Avoid V1**: T-wave end is often ambiguous; tends to underestimate QT

### 2.4 Beat-by-Beat Considerations
- **Beat-to-beat QT variability**: LQTS displays increased QT variability between beats; a quantitative risk marker beyond the mean QTc
- **Rate-dependent QT shortening**: LQT1 — QT fails to shorten appropriately with increasing heart rate (IKs cannot activate to accelerate repolarization). LQT3 — QT may shorten more than expected at faster rates (late INa has less time to act). This rate-dependent behavior can suggest subtype during exercise testing
- **T-wave alternans (TWA)**: Beat-to-beat alternation in T-wave amplitude or polarity = STAT finding. TWA indicates imminent TdP risk; may precede TdP by seconds to minutes. Scan all 12 leads for alternating tall/short T-waves or inverted/upright T-waves
- **Short-long-short (SLS) sequence**: PVC (short RR) → compensatory pause (long RR) → post-pause sinus beat with maximally prolonged QT → second PVC during vulnerable window → TdP. Present in >80% of TdP initiations; must be recognized in real-time monitoring
- **Post-pause QT prolongation**: Any pause (PVC, sinus pause, AV block) causes exaggerated QT prolongation in the following beat in LQTS patients. A PVC followed by a pause in a patient with long QT = high-risk observation

---

## 3. Morphology Details

### 3.1 P-wave Changes
- **Morphology**: Normal sinus P-waves — LQTS does not affect atrial depolarization
- **Duration**: Normal (<120 ms)
- **Axis**: Normal (0° to +75°)
- **During TdP**: P-waves are not visible; overwhelmed by the polymorphic VT complex. After TdP terminates, sinus P-waves resume — typically preceded by a long post-tachycardia pause
- **Clinical note**: Normal P-waves before each QRS confirm sinus origin and help distinguish LQTS from ischemia with non-sinus rhythm or junctional rhythms

### 3.2 PR Interval Changes
- **Duration**: Normal (120–200 ms) — LQTS does not affect AV conduction velocity
- **Pattern**: Constant, no Wenckebach, no dropped beats
- **Exception**: Iatrogenic PR prolongation if patient is on beta-blockers (the primary treatment for LQT1/LQT2) or other AV-nodal-slowing drugs
- **Key point**: Normal PR distinguishes LQTS from conditions that prolong both conduction and repolarization simultaneously (hyperkalemia prolongs PR + QRS + QT)

### 3.3 QRS Complex Changes
- **Duration**: Normal (<120 ms) during sinus rhythm. QRS widening is NOT a feature of LQTS; if QRS is wide, consider BBB, hyperkalemia, TCA overdose, or antiarrhythmic toxicity as alternative or coexisting diagnosis
- **Morphology**: Normal during sinus rhythm — no rSR', no delta wave, no fragmentation, no notching
- **Amplitude**: Normal
- **Axis**: Normal
- **During TdP**: Wide, polymorphic, continuously changing axis. The defining sinusoidal waxing-waning amplitude pattern reflects the QRS axis rotating progressively around the isoelectric baseline. Rate typically 150–300 bpm

### 3.4 ST Segment Changes
- **LQT1**: ST segment is of normal duration; prolongation is in the T-wave itself. The ST-T transition is smooth and gradual
- **LQT2**: Short or normal ST segment followed by the notched/bifid T. The ST segment itself may appear shortened or absent as it merges with the early T-wave hump
- **LQT3**: Long, flat (isoelectric) ST segment — this is the pathognomonic feature of LQT3. The plateau phase is prolonged and visible as a flat segment between QRS and T-wave that is clearly longer than normal
- **Drug-induced / electrolyte LQTS**: ST changes depend on the underlying cause; no single ST pattern is universal. Hypokalemia may produce ST depression with prominent U-waves

### 3.5 T-wave Changes
- **LQT1**: Broad-based, smooth, rounded T-wave. The T-wave base is wider than normal but the peak amplitude is relatively preserved. The T-wave appears to occupy more of the ST-T interval than normal. This is the most subtle morphological change of the three subtypes
- **LQT2**: Notched or bifid T-wave with two distinct humps separated by a notch or trough. Often low amplitude overall. The first hump may be smaller; the second hump is typically larger. The notch in V2-V5 is the diagnostic clue. This is the most easily recognized subtype on ECG
- **LQT3**: Late-onset T-wave following the long isoelectric ST segment. Once it begins, the T-wave may have relatively normal morphology (not particularly notched or broadened), but its onset is markedly delayed. The T-wave appears "stuck to the right" on the ECG
- **Acquired/drug-induced**: T-wave morphology resembles LQT2 (IKr blockade) — notched T-waves and low amplitude are common. U-waves may be prominent, particularly with hypokalemia
- **U-waves**: Large U-waves (especially if U-wave amplitude exceeds T-wave amplitude) must not be mistaken for the T-wave end — QT should be measured to the true T-wave end, not U-wave end

### 3.6 QT/QTc Changes
- **QTc**: The primary diagnostic measurement. Calculate using Bazett (standard) or Fridericia (preferred at extreme heart rates). Measure in lead II and the lead with the longest visible QT
- **Upper normal**: 440 ms (men), 450 ms (women)
- **Clinically prolonged**: >460 ms men, >470 ms women
- **High TdP risk threshold**: ≥500 ms regardless of sex
- **Critical danger zone**: ≥600 ms — treat as emergency
- **Pitfall**: U-waves incorporated into QT measurement falsely elevate QTc. T-wave end is the tangent method endpoint (draw tangent to descending T-wave limb; endpoint is where it crosses the baseline)

### 3.7 Other Features
- **T-wave alternans**: Beat-to-beat T-wave amplitude or polarity alternation = imminent TdP. A STAT finding on any monitoring
- **Prominent U-waves**: Particularly with hypokalemia and hypomagnesemia. U-waves are separate from the T-wave (occur after T-wave ends) but may fuse with a prolonged T-wave, creating a "TU fusion" that falsely extends measured QT
- **QT dispersion**: The difference in QT across 12 leads. Elevated QT dispersion (>60 ms) reflects regional repolarization heterogeneity and is associated with increased TdP risk, though this measurement has fallen out of routine clinical use

---

## 4. Differential Diagnosis

### 4.1 Mimics

| Mimic | Key Distinguishing Feature | How to Differentiate |
|-------|---------------------------|---------------------|
| Hyperkalemia | Prolongs QRS + QT; peaked T-waves; wide QRS | Wide QRS; peaked T-waves; peaked T ≠ broad T; potassium level |
| Hypocalcemia | Prolongs ST segment specifically; QTc may exceed 500 ms | Long ST segment (LQT3-like) but no T-wave notching; corrected calcium level |
| Hypothyroidism | Bradycardia + low voltage + prolonged QTc | Low voltage; slow HR; TSH; no T-wave subtype morphology |
| Hypokalemia | Prolonged QTc + prominent U-waves + flat T-waves | U-waves may be mistaken for T-wave; potassium level; TU fusion |
| RBBB | May alter T-wave morphology in V1-V3 and QT appearance | Wide QRS with rSR' in V1; secondary T-wave changes are discordant to QRS |
| Cerebral T-waves (CNS events) | Deep, symmetric T inversions + prolonged QTc post-subarachnoid hemorrhage | Clinical context; sudden onset; history of SAH, intracerebral hemorrhage |
| Normal variant | Slightly long QTc (441–460 ms male; 451–470 ms female) | No T-wave morphology abnormality; no symptoms; no medications; no family history |
| TCA overdose | Prolonged QRS + QT + sinus tachycardia + right axis deviation | Wide QRS; tachycardia; clinical toxicology context |

### 4.2 Coexisting Conditions
- **Bradycardia + long QT**: Bradycardia independently prolongs QT; when combined with congenital LQTS or QT-prolonging drug, risk is multiplicative. Calculate QTc to account for rate
- **LQT + hypokalemia**: Very high-risk combination. Hypokalemia blocks IKr by altering channel kinetics; when added to baseline LQTS, QTc can become critically prolonged
- **LQT + QT-prolonging drug**: Acquired-on-congenital LQTS = very high risk. Patients with congenital LQTS are exquisitely sensitive to even low doses of QT-prolonging drugs
- **LQT + structural heart disease**: Heart failure prolongs repolarization intrinsically; adding QT-prolonging drugs (e.g., antiarrhythmics) in this context is particularly dangerous

---

## 5. STAT Classification

| Priority | Criteria |
|----------|---------|
| STAT (Immediate) | QTc ≥500 ms with symptoms (syncope, near-syncope, palpitations) |
| STAT (Immediate) | T-wave alternans visible on ECG |
| STAT (Immediate) | TdP identified on rhythm strip |
| STAT (Immediate) | Short-long-short RR sequence with PVCs in setting of long QT |
| Urgent (15 min) | QTc ≥500 ms, asymptomatic, on QT-prolonging drug |
| Urgent (15 min) | QTc 470–499 ms with hypokalemia, hypomagnesemia, or bradycardia |
| Non-urgent | QTc 440–469 ms (men) or 450–469 ms (women), asymptomatic, no risk factors |
| Informational | QTc borderline (441–460 ms men, 451–470 ms women) — flag for clinical review |

---

## 6. Reasoning Complexity Analysis (Feeds Into Node 2.1)

### 6.1 Reasoning Domains Required
- Interval measurement (QT, RR, QTc calculation with multiple formulas)
- T-wave morphology classification (broad vs notched/bifid vs late-onset)
- Arrhythmia recognition (TdP vs other polymorphic VT, T-wave alternans)
- Pharmacological knowledge (which drugs prolong QT, additive risk)
- Electrolyte pathophysiology (hypoK, hypoMg, hypoCa effects on QT)
- Risk stratification (QTc thresholds, symptom integration, trigger pattern)
- Subtype pattern recognition (LQT1/2/3 morphological distinctions)

### 6.2 Feature Dependencies
- QTc calculation requires: accurate QT measurement (requires reliable T-wave end identification), accurate RR interval measurement, selection of correct formula for current heart rate
- T-wave morphology subtyping requires: clear T-wave visible in V2-V5, no overlapping U-waves, adequate ECG quality
- TdP recognition requires: beat-by-beat rhythm analysis across the full strip, not just a single beat
- Drug-induced LQTS requires: medication reconciliation external to the ECG (crediblemeds.org cross-reference)

### 6.3 Cross-Condition Interactions
- Hypokalemia + long QT: additive and synergistic; hypokalemia blocks IKr independently
- Bradycardia + long QT: rate-dependent APD prolongation amplifies baseline QT prolongation
- RBBB + long QT: RBBB alters T-wave morphology in V1-V3 and makes QT measurement difficult in those leads; measure QTc in leads II, V5-V6
- LVH + long QT: LVH itself can mildly prolong QTc; combined with drug-induced QT prolongation = risk compounding
- Ischemia + long QT: Regional repolarization abnormalities from ischemia add to global QT prolongation

### 6.4 Reasoning Chain Sketch
1. Measure QT in lead II and in the lead with the longest clearly visible QT
2. Measure RR interval (average of 3–5 beats if rhythm is regular)
3. Calculate QTc using Bazett (and Fridericia if HR <60 or >100)
4. Classify QTc: normal / borderline / prolonged / markedly prolonged / critical
5. If QTc ≥440/450 ms: examine T-wave morphology in V2-V5 for LQT1/LQT2/LQT3 pattern
6. Scan all leads for T-wave alternans (beat-to-beat amplitude or polarity change)
7. Examine rhythm strip for SLS sequence (PVC → pause → PVC → polymorphic VT)
8. If QTc ≥500 ms or TWA or TdP: trigger STAT alert
9. Cross-reference medications (IKr-blocking drugs) and electrolytes (K, Mg, Ca)
10. Assign congenital vs acquired probability based on morphology, medications, context

### 6.5 Confidence Anchors
- QTc ≥500 ms in absence of wide QRS = high-confidence QT prolongation (not QRS widening artifact)
- Notched/bifid T in V2-V5 with QTc >450 ms = LQT2 pattern (congenital or acquired IKr blockade)
- Long flat ST segment + late T in V2-V5 with QTc >450 ms = LQT3 pattern
- Broad smooth T in V2-V5 with QTc >450 ms = LQT1 pattern
- Prominent U-waves fusing with T-wave = hypokalemia-associated QT prolongation until proven otherwise

### 6.6 Difficulty Score

| Dimension | Score (1–5) | Rationale |
|-----------|-------------|-----------|
| Feature detection | 2.5 | QT measurement is objective but T-wave end identification has ambiguity |
| Pattern recognition | 3.0 | Three subtypes require morphological discrimination (LQT1 vs LQT2 vs LQT3) |
| Differential breadth | 3.0 | Multiple mimics; overlap with normal variants, U-waves, RBBB |
| Clinical integration | 3.5 | Medication reconciliation, electrolytes, symptom triggers needed |
| Risk stratification | 3.0 | QTc thresholds are explicit, but TdP risk is multifactorial |
| **Overall** | **3.2/5** | Moderate complexity — interval measurement is learnable; subtype morphology and acquired risk factors require synthesis |

---

## 6A. Agent Assignment

**Architecture:** Option E — 3 Parallel Phase 1 Specialists + 1 Sequential CDS (Node 2.1 Gate Passed 2026-03-27)

| Agent | Role for Long QT Syndrome | Key Features Used |
|-------|--------------------------|-------------------|
| **RRC** (Rhythm/Rate/Conduction) | Supporting | QT/QTc measurement from RR intervals (QTc >440ms men / ≥460ms women); rate measurement for Bazett correction; arrhythmia detection (TdP — short-long-short initiation pattern) |
| **IT** (Ischemia/Territory) | Not involved | No ischemic ST or territorial changes associated with long QT syndrome |
| **MR** (Morphology/Repolarization) | Primary | Prolonged QTc with prolonged T-wave morphology; subtype-specific T-wave patterns: LQT1 (broad, smooth, high amplitude T); LQT2 (notched or bifid T, low amplitude); LQT3 (long isoelectric ST segment followed by late-onset T-wave); QTc >500ms STAT threshold |
| **CDS** (Cross-Domain Synthesis) | Standard integration only | Integrates RRC QTc measurement + MR T-wave subtype morphology; distinguishes congenital LQT subtypes (LQT1/2/3 by T-wave pattern) from acquired (drug-induced QTc prolongation, electrolyte abnormalities); flags TdP risk when QTc >500ms |

### Primary Agent
**MR** — Long QT syndrome is defined by prolonged T-wave morphology and subtype-specific T-wave patterns (LQT1/2/3), which are repolarization morphology determinations within MR's domain.

### Cross-Domain Hints
- MR → RRC: `cross_domain_hint: "Prolonged T-wave detected — confirm RRC QTc measurement includes full T-wave duration; QTc >500ms requires STAT flag for TdP risk"`
- RRC → CDS: `cross_domain_hint: "QTc >440ms (men) or >460ms (women) measured — CDS should integrate MR T-wave morphology for LQT subtype classification and distinguish congenital vs acquired cause"`

### CDS Specific Role
CDS performs standard integration for long QT syndrome, combining RRC's QTc measurement with MR's T-wave morphology characterization to achieve subtype classification and risk stratification. LQT1 (IKs mutation): broad smooth T-wave, exercise-triggered; LQT2 (IKr mutation): notched/bifid T-wave, emotion/auditory-triggered; LQT3 (SCN5A mutation): long flat ST segment with late narrow T-wave, sleep/rest events. For acquired QT prolongation, CDS applies the clinical context (drug list, electrolytes) to identify the cause. CDS flags QTc >500ms as a STAT finding requiring immediate notification due to markedly elevated TdP risk, and identifies the short-long-short initiation pattern if TdP runs are present in the rhythm.

---

## 7. RAG Knowledge Requirements

### 7.1 Textbook References
- Goldberger AL, Goldberger ZD, Shvilkin A. *Goldberger's Clinical Electrocardiography: A Simplified Approach.* 9th ed. Elsevier; 2018. Chapter 16 (QT prolongation and TdP)
- Priori SG et al. 2015 ESC Guidelines for the management of patients with ventricular arrhythmias and the prevention of sudden cardiac death. *Eur Heart J.* 2015;36(41):2793–2867
- Schwartz PJ et al. Diagnostic criteria for the long QT syndrome: An update. *Circulation.* 1993;88:782–784 (Schwartz scoring system)
- Zhang L et al. Spectrum of ST-T-wave patterns and repolarization parameters in congenital long-QT syndrome: ECG findings identify genotypes. *Circulation.* 2000;102:2849–2855 (definitive subtype morphology paper)
- CredibleMeds / AZCERT QTDrugs List. www.crediblemeds.org (authoritative drug-QT risk database)
- 2025 AHA/ACC/HRS Guideline for Diagnosis and Management of Ventricular Arrhythmias

### 7.2 Key Figures
- T-wave morphology comparison panel: LQT1 (broad, smooth), LQT2 (notched, bifid), LQT3 (long ST + late T) — side-by-side in V3
- QTc calculation diagram: QT and RR interval measurement, Bazett formula illustration
- T-wave alternans strip: beat-to-beat T-wave amplitude alternation preceding TdP
- Short-long-short sequence leading to TdP onset on rhythm strip

---

## 8. Dashboard Visualization Specification

### 8.1 Highlighted Leads
- **Primary**: Lead II (QT measurement), V3 (T-wave morphology), V4 (T-wave amplitude)
- **Secondary**: V2, V5 (morphology confirmation), aVF (QT confirmation)
- **Alert**: All leads if T-wave alternans detected

### 8.2 Arrows and Annotations
- Bidirectional bracket over QT interval in lead II with label: "QT = XXX ms | QTc = XXX ms (Bazett)"
- Color-coded QTc badge: green (<440/450), yellow (440/450–499), red (≥500), critical red (≥600)
- T-wave annotation in V3: "Broad (LQT1)" / "Notched/Bifid (LQT2)" / "Late-onset (LQT3)"
- If T-wave alternans: flashing annotation "T-wave Alternans — STAT Risk"
- If SLS sequence: annotate PVC → pause → PVC sequence on rhythm strip with arrows

### 8.3 Clinician Explanation
- **ER Nurse**: "The QT interval — the time for the heart to recharge after each beat — is abnormally long. This raises risk of a dangerous rhythm called Torsades de Pointes. Key actions: check potassium, magnesium, and all medications. Avoid giving any additional QT-prolonging drugs. Alert physician immediately if QTc ≥500 ms."
- **Cardiologist**: "QTc is [value] ms ([formula] correction) — [subtype pattern] T-wave morphology in V3-V5 is consistent with [LQT1 IKs / LQT2 IKr / LQT3 late-INa / drug-induced IKr blockade]. [If TWA present: T-wave alternans identified — imminent TdP risk. Crash cart, continuous monitoring, IV magnesium, consider overdrive pacing.] Risk stratification: [list active triggers, medications, electrolyte status]."

---

## 9. Edge Cases and Pitfalls

- **U-wave mistaken for T-wave end**: The most common measurement error in LQTS. Hypokalemia produces large U-waves that fuse with prolonged T-waves. Always use the tangent method to the descending T-wave limb to identify the true T-wave end. If T and U are fused and inseparable, report QTU interval and flag for clinical interpretation
- **Normal QTc with morphological LQTS**: Some congenital LQTS patients have QTc in the borderline range at rest but demonstrate the characteristic T-wave morphology. LQT2 notched T-waves in V2-V5 with QTc 440–460 ms should still flag for clinical review
- **Bradycardia overcorrection with Bazett**: Bazett formula overcorrects at slow heart rates — a patient with HR 40 bpm may show QTc 500 ms by Bazett but only 460 ms by Fridericia. Use Fridericia for HR <60
- **Tachycardia undercorrection with Bazett**: Conversely, at fast rates (HR >100), Bazett overestimates QTc. A patient with sinus tachycardia at HR 130 may have an apparently short QTc by Fridericia that Bazett inflates. Always state which formula was used
- **RBBB masking QT**: RBBB prolongs QRS (which contributes to measured QT) without prolonging ventricular repolarization. In RBBB, the JT interval (QT minus QRS duration) may be more informative than raw QT
- **LQT3 underdiagnosis**: The long flat ST segment of LQT3 may be interpreted as normal ST segment variation or missed when scanning quickly. Look for the disproportionate length of the ST segment relative to the T-wave
- **Drug-induced LQTS with "normal" QTc at rest**: Some drugs cause QTc prolongation that is not always present at rest and becomes apparent only with drug level peaks. A normal QTc on a single ECG does not exclude drug-induced LQTS risk

---

## 10. References

1. Bazett HC. An analysis of the time-relations of electrocardiograms. *Heart.* 1920;7:353–370
2. Fridericia LS. Die Systolendauer im Elektrokardiogramm bei normalen Menschen und bei Herzkranken. *Acta Med Scand.* 1920;53:469–486
3. Zhang L et al. Spectrum of ST-T-wave patterns and repolarization parameters in congenital long-QT syndrome. *Circulation.* 2000;102:2849–2855
4. Moss AJ et al. The long QT syndrome: prospective longitudinal study of 328 families. *Circulation.* 1991;84:1136–1144
5. Schwartz PJ et al. Diagnostic criteria for the long QT syndrome: An update. *Circulation.* 1993;88:782–784
6. Priori SG et al. Risk stratification in the long-QT syndrome. *N Engl J Med.* 2003;348:1866–1874
7. Dessertenne F. La tachycardie ventriculaire à deux foyers opposés variables. *Arch Mal Coeur Vaiss.* 1966;59:263–272
8. Al-Khatib SM et al. 2017 AHA/ACC/HRS Guideline for Management of Patients with Ventricular Arrhythmias. *Circulation.* 2018;138:e272–e391
9. CredibleMeds / AZCERT. QT Drugs List. www.crediblemeds.org. Accessed 2026-03-27
10. Rautaharju PM et al. AHA/ACCF/HRS recommendations for the standardization and interpretation of the electrocardiogram: Part IV. *J Am Coll Cardiol.* 2009;53:982–991
