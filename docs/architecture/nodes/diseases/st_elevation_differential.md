# ST Elevation Differential — ECG Manifestation from First Principles
**Node:** 2.7.85
**SDA:** SDA-2 (Diagnosis & Agentic Core) — shared resource for SDA-1, SDA-3, SDA-4
**Status:** Research Complete
**PGMR:** Required
**Date:** 2026-03-27

---

## 1. Pathophysiology Root Cause

### 1.1 Mechanisms of ST Elevation
ST elevation (STE) reflects a shift in the ST segment above the isoelectric baseline. Multiple distinct mechanisms produce this finding:

- **Transmural ischemia (STEMI)**: Total or near-total occlusion of an epicardial coronary artery generates a current of injury. The ischemic zone cannot repolarize normally; the voltage difference between ischemic and non-ischemic myocardium during diastole (TQ depression) and systole (STE) produces the characteristic monophasic ST elevation. Reciprocal changes appear in opposite leads because the injury current vector points away from those leads.
- **Pericardial inflammation**: Diffuse myopericardial irritation elevates the ST segment across all ventricular surfaces. The PR segment is characteristically depressed because the atria are primarily affected first (pericardium-atrial proximity). No single coronary territory is preferentially affected.
- **Phase 2 loss of dome (Brugada, ER)**: Ito-mediated early repolarization creates voltage gradients between epicardium and endocardium without ischemia. Localized to RVOT (Brugada) or inferior/lateral (ER) territories.
- **Secondary ST elevation in LBBB**: Abnormal depolarization sequence forces repolarization in discordant direction; ST elevation appears in leads with predominantly negative QRS (V1–V3) as a secondary — expected — finding.
- **Mechanical/structural causes**: LV aneurysm, Takotsubo, myocarditis — each with distinct mechanisms.

### 1.2 Why This Is the Most Critical ECG Differential
The STEMI diagnosis mandates emergent cath lab activation within 90 minutes. A false positive activation (non-STEMI cause of STE) carries risks of unnecessary catheterization with contrast, procedure complications, and delays to appropriate treatment. A false negative (missed STEMI) carries mortality risk. The clinician — and AI — must integrate morphology, distribution, context, and evolution to make this distinction rapidly.

### 1.3 The Four Primary Causes
Emergency medicine prioritizes four causes: STEMI, pericarditis, benign early repolarization (BER), and LBBB. All other causes are secondary considerations that arise after these are evaluated.

---

## 2. ECG Presentation — Lead by Lead

### 2.1 Diagnostic Criteria (2025 AHA/ESC Guidelines)

| Cause | ST Morphology | Distribution | Reciprocal Changes | PR Depression | Evolution |
|---|---|---|---|---|---|
| STEMI | Convex (tombstone) or flat-top | Regional (coronary territory) | Present (contralateral leads) | Absent | Rapid evolution; Q waves develop |
| Pericarditis (Stage 1) | Concave (saddle-shaped) | Diffuse (all territories) | Absent | Present in multiple leads | Slow evolution through 4 stages |
| Benign Early Repolarization | Concave with J-point notch/slur | V2–V6 and/or inferior | Absent | Absent | Stable; no evolution |
| LBBB | Discordant STE (leads with neg QRS) | V1–V3 (negative QRS leads) | Concordant STE = abnormal (Sgarbossa) | Absent | Stable unless Sgarbossa criteria met |
| Brugada Type 1 | Coved (convex-down, downsloping) | V1–V3 only | Absent | Absent | Dynamic; may disappear |
| Takotsubo | Anterior > diffuse, evolving | V3–V6 initially; global later | May be present early | Absent | Rapidly evolving; followed by deep TWI |
| LV Aneurysm | Persistent convex STE | Anterior (V1–V4) post-infarct | Fixed Q waves present | Absent | Chronic, no evolution; stable for months |
| Hyperkalemia | Peaked STE V1–V2 with wide QRS | V1–V2 ± diffuse | Wide QRS, P-wave loss | Absent | Evolves with K+ level |

### 2.2 Lead-by-Lead Manifestation

| Lead | STEMI Territory | Pericarditis | BER | LBBB (secondary) |
|---|---|---|---|---|
| I | Lateral STEMI | Yes | Possible | Possible (discordant) |
| II | Inferior STEMI | Yes | Possible inferior | Discordant if neg QRS |
| III | Inferior STEMI | Yes | Possible inferior | Discordant if neg QRS |
| aVR | Upward in LMCA/LAD occlusion | Yes (inverted) | No | Secondary |
| aVL | High lateral STEMI; reciprocal inferior | Yes | Possible | Secondary |
| aVF | Inferior STEMI | Yes | Possible inferior | Secondary |
| V1 | Septal/anterior STEMI; RV infarction | Yes | No | Expected STE (neg QRS) |
| V2 | Anterior/septal STEMI | Yes | Possible | Expected STE (neg QRS) |
| V3 | Anterior STEMI | Yes | Yes (classic BER territory) | Expected STE |
| V4 | Anterior STEMI | Yes | Yes (classic BER territory) | Transition |
| V5 | Lateral STEMI | Yes | Yes (classic BER territory) | Discordant if neg QRS |
| V6 | Lateral STEMI | Yes | Yes | Discordant if neg QRS |

### 2.3 Key Leads
- **V1–V3 coved ST elevation**: Brugada — evaluate independently
- **V1–V4 discordant STE + wide QRS**: LBBB secondary change — apply Sgarbossa
- **II/III/aVF + reciprocal I/aVL**: Inferior STEMI
- **I/aVL/V1–V6 diffuse + PR depression**: Pericarditis
- **V2–V5 concave + J notch + young patient**: BER
- **aVR ST elevation**: Significant sign — global ischemia (LMCA/proximal LAD occlusion)

### 2.4 Beat-by-Beat Considerations
- STEMI evolves rapidly: ST elevation reaches maximum within minutes to hours; Q waves develop within 1–2 hours; T waves invert as reperfusion occurs
- Pericarditis progresses slowly through 4 stages over days to weeks
- BER is stable — no evolution on serial ECGs
- LBBB is stable (unless caused by acute ischemia — new LBBB + chest pain = STEMI equivalent)

---

## 3. Morphology Details

### 3.1 STEMI — Convex/Tombstone Morphology
The ST segment is elevated with a convex upper border (arching upward). In hyperacute STEMI the T wave is tall and symmetric before the ST elevation peaks. As injury progresses, the ST fuses with the T wave creating the "tombstone" pattern — a monophasic deflection without distinct ST-T separation. Q waves develop as the infarct progresses and necrosis causes loss of R wave.

### 3.2 Pericarditis — Concave/Saddle-Shaped Morphology
The ST segment elevation is concave upward — bowing downward toward the baseline before rising again into an upright T wave. The classic "saddle-shape" is the hallmark. PR depression is the most specific finding for pericarditis: atrial inflammation causes the PR segment (corresponding to atrial repolarization, the Ta wave) to shift, producing PR depression in leads where STE is present and PR elevation in aVR. All four stages: Stage 1 (STE + PR depression), Stage 2 (normalization), Stage 3 (T inversion), Stage 4 (normal or persistent changes).

### 3.3 Benign Early Repolarization — J-Point with Concave ST
J-point elevation with upsloping (ascending) ST segment. The "fish-hook" appearance in V4–V5. No reciprocal changes. No PR depression. No evolution. The ST segment is concave (upward bowing like a smile). T waves are usually tall and symmetric.

### 3.4 LBBB — Discordant ST Changes
Sgarbossa criteria for identifying STEMI in LBBB:
- Concordant STE ≥1 mm in any lead: 5 points (highly specific for STEMI)
- Concordant ST depression ≥1 mm in V1–V3: 3 points
- Discordant STE ≥5 mm: 2 points (less specific)
Score ≥3 = STEMI (modified Sgarbossa: concordant STE/STD criteria same; discordant STE/QRS ratio >0.25 replaces the 5 mm criterion)
New LBBB in a patient with chest pain = STEMI equivalent by ESC/ACC guidelines regardless of Sgarbossa.

### 3.5 Takotsubo — Evolving Anterior Pattern
Initial presentation may mimic anterior STEMI (STE V3–V6). The STE resolves within hours to days, followed by progressive deep, global T-wave inversions that reach maximum depth at 2–5 days. The STE in Takotsubo is less regional than LAD STEMI and often spares V1 (because the most basal anterior segments are not affected by apical ballooning). Echo showing apical ballooning with basal hypercontractility is diagnostic.

### 3.6 LV Aneurysm
Chronic convex ST elevation in anterior leads (V1–V4) persisting months after anterior MI. Fixed Q waves are always present. The absence of evolution distinguishes it from acute STEMI. Clinically important: LV aneurysm after anterior MI may be confused with re-infarction on ECG alone; troponin rise is the key differentiator.

### 3.7 Hyperkalemia
At very high K+ levels (>7.0 mEq/L), the sinusoidal wide QRS pattern may show ST elevation in V1–V2 (Brugada phenocopy). The context: P-wave loss, widened QRS, peaked T waves, serum K+ level all confirm.

---

## 4. Differential Diagnosis

### 4.1 Mimics

| Condition | Key Discriminator vs STEMI |
|---|---|
| Pericarditis | Concave morphology; PR depression; diffuse (not regional); no reciprocal changes |
| BER | Concave; J-point notch; young athlete; stable; no symptoms |
| LBBB | Wide QRS; discordant STE expected; Sgarbossa criteria to detect superimposed STEMI |
| Brugada Type 1 | V1–V3 coved only; no inferior/lateral involvement; known channelopathy context |
| Takotsubo | Apical ballooning on echo; female post-stress; STE less regional; rapid TWI evolution |
| LV aneurysm | Chronic stable; prior MI history; Q waves present; no acute evolution; troponin flat |
| Hyperkalemia | Wide QRS; peaked T; P-wave loss; metabolic context; K+ level |
| Myocarditis | May mimic STEMI perfectly; young patient; viral prodrome; troponin elevated; echo may show diffuse wall motion abnormality |
| Vasospastic angina | Transient STE that resolves spontaneously or with nitroglycerin; no fixed occlusion on cath |
| PE (right heart strain) | RV strain V1–V4; S1Q3T3; sinus tachycardia; different clinical presentation |

### 4.2 Coexisting Conditions
- STEMI + LBBB: New LBBB + chest pain = STEMI regardless; Sgarbossa identifies STEMI in known LBBB
- Pericarditis + myocarditis (myopericarditis): Diffuse STE + troponin rise; echo may show wall motion abnormality
- STEMI + Brugada: Documented in some SCN5A patients; STE V1–V3 during STEMI due to catecholamine surge

---

## 5. STAT Classification

| Finding | STAT Level | Action |
|---|---|---|
| Convex STE + regional + reciprocal changes | STAT — Critical | STEMI protocol: cath lab activation <90 min |
| STE V1–V3 new, in chest pain, unknown LBBB status | STAT — Critical | Treat as STEMI until proven otherwise |
| Known LBBB + chest pain + Sgarbossa positive | STAT — Critical | STEMI protocol |
| Diffuse concave STE + PR depression, stable | Urgent | Pericarditis workup; rule out STEMI |
| Anterior STE + young female + stress trigger | Urgent | Echo urgent; Takotsubo vs STEMI |
| Coved STE V1–V3 without chest pain | Urgent | Brugada evaluation |
| Chronic anterior STE + Q waves + known MI | Non-urgent | Document LV aneurysm; troponin to exclude re-infarction |
| Concave STE V4–V6 young athlete, asymptomatic | Normal variant | Document BER; no action |
| aVR STE ≥1 mm + diffuse STD | STAT — Critical | LMCA/proximal LAD occlusion; emergent cath |

---

## 6. Reasoning Complexity Analysis

### 6.1 Reasoning Domains Required
- ST morphology classification: convex vs concave vs coved — the primary sorting step
- Territorial distribution mapping: regional (coronary) vs diffuse (pericardial) vs focal (Brugada/ER)
- Reciprocal change detection: presence → supports STEMI; absence does not exclude
- PR depression detection: specific for pericarditis
- QRS width assessment: LBBB/RBBB context
- Evolution assessment: serial ECG comparison
- Clinical context: symptoms, age, sex, stress trigger, prior MI

### 6.2 Feature Dependencies
- Convex vs concave distinction: the single most important morphologic feature. Requires accurate waveform measurement; automated classifiers prone to error at borderline morphologies
- Reciprocal changes: must identify ALL 12 leads to confirm absence (pericarditis) or presence (STEMI) — partial ECG views insufficient
- Sgarbossa in LBBB: requires baseline wide QRS identification first
- STEMI in paced rhythm: Sgarbossa-equivalent criteria exist but are less validated
- aVR evaluation: systematically underused; aVR STE = global ischemia signal

### 6.3 Cross-Condition Interactions
- STEMI + pericarditis: myopericarditis can present with regional STE + troponin; echo and cath needed to distinguish
- STEMI + LBBB: the most dangerous diagnostic overlap; LBBB masks STEMI features
- BER + ischemia: BER is a stable baseline; acute ischemia superimposed on BER requires serial comparison — new convexity or reciprocal changes on a BER background = STEMI
- Brugada + ischemia: V1–V3 involvement shared; independent evaluation required

### 6.4 Reasoning Chain Sketch
1. Detect ST elevation in any lead (threshold: ≥1 mm limb leads, ≥2 mm precordial leads by ESC criteria)
2. Classify ST morphology per lead: convex / concave / coved / discordant
3. Map distribution: regional (coronary territory) / diffuse / right precordial only / anterior only
4. Check for reciprocal ST depression in contralateral leads → supports STEMI
5. Check for PR depression → supports pericarditis
6. Assess QRS width → if ≥120 ms, apply LBBB/RBBB pathway with Sgarbossa
7. Assess for J-wave notch/slur → supports BER if present with concave morphology
8. Check for coved morphology V1–V3 → Brugada pathway
9. Apply clinical context: symptoms, prior MI, age/sex, stress trigger, drugs
10. Output: primary diagnosis + top differential + STAT level + confidence score
11. Flag any clinical actions: cath lab activation, pericarditis workup, echo, Brugada evaluation

### 6.5 Confidence Anchors
- Convex STE + regional + reciprocal changes + chest pain: very high confidence STEMI
- Diffuse concave STE + PR depression + no reciprocal changes: high confidence pericarditis
- Concave J-notch STE V4–V6 + young male athlete + no symptoms: high confidence BER
- Wide QRS + discordant STE only: high confidence LBBB secondary change (normal)
- Wide QRS + concordant STE (Sgarbossa positive): high confidence STEMI in LBBB
- Any borderline morphology + symptoms: low confidence any single diagnosis → STEMI protocol default

### 6.6 Difficulty Score

| Dimension | Score (1–5) | Rationale |
|---|---|---|
| Morphology Recognition | 4 | Convex/concave/coved distinction; borderline cases common |
| Interval Measurement | 3 | ST amplitude and slope measurement; Sgarbossa thresholds |
| Differential Diagnosis | 5 | Broadest and most consequential DDx in emergency medicine |
| Clinical Integration | 5 | Symptom-dependent diagnosis; BER and STEMI can be identical without context |
| Rarity / Prior Probability | 3 | STEMI common enough; rare causes (Brugada, LV aneurysm) require specific features |
| Arrhythmia Risk Stratification | 4 | STEMI = immediate mortality risk; others lower but non-trivial |
| **Overall** | **4.5** | Highest overall difficulty — the definitive emergency ECG challenge |

---

## 6A. Agent Assignment

**Architecture:** Option E — 3 Parallel Phase 1 Specialists + 1 Sequential CDS (Node 2.1 Gate Passed 2026-03-27)

| Agent | Role for ST Elevation Differential (Reference) | Key Features Used |
|-------|--------------------------|-------------------|
| **RRC** (Rhythm/Rate/Conduction) | Not involved | Rate and conduction findings are not part of the ST elevation differential reference |
| **IT** (Ischemia/Territory) | Contributing — supplies ST elevation detection and territory mapping to CDS | Detects ST elevation, maps to coronary territory (LAD anterior, RCA/LCx inferior, LCx lateral), identifies reciprocal changes; supplies these findings to CDS for differential application |
| **MR** (Morphology/Repolarization) | Contributing — supplies ST morphology characterization to CDS | Characterizes ST elevation morphology: convex/tombstone (STEMI), concave/saddle-back (pericarditis/early repolarization), coved (Brugada V1-V2), J-point elevation with notching (early repolarization); supplies to CDS |
| **CDS** (Cross-Domain Synthesis) | Sole agent applying this reference — uses ST elevation differential decision tree | CDS is the only agent that applies this reference. Triggered when: (a) IT detects ST elevation not clearly matching a single coronary territory, (b) MR flags concave morphology suggesting non-STEMI etiology, or (c) multiple agents flag competing ST elevation explanations. CDS applies: territory + morphology + reciprocal changes + distribution → STEMI vs pericarditis vs Brugada vs early repolarization vs Takotsubo |

### Primary Agent
**CDS** — This is a reference file. CDS is the sole agent that applies this differential reference; Phase 1 agents supply their findings to CDS, which then uses this reference to generate the final ST elevation classification.

### Cross-Domain Hints
No Phase 1 agent generates cross_domain_hints directly from this reference. Cross-domain hints that trigger CDS to apply this reference are generated by IT and MR from their respective disease files (e.g., early_repolarization.md, pericarditis.md, brugada_all_types.md, stemi_anterior.md).

### CDS Specific Role
CDS applies the ST elevation differential reference as the decision engine whenever the three-agent Phase 1 outputs produce ambiguous or competing ST elevation explanations. The reference provides CDS with a structured decision tree: (1) assess coronary territory — single territory with reciprocal changes favors STEMI; non-territorial or diffuse disfavors STEMI; (2) assess morphology — convex/flat = STEMI; concave/saddle-back = pericarditis or early repolarization; coved V1-V2 = Brugada; J-point notching inferior/lateral = early repolarization; apical ballooning pattern = Takotsubo; (3) assess PR segment — PR depression in multiple leads = pericarditis; (4) integrate rate/age/sex context for Takotsubo. CDS uses this reference to generate a definitive ST elevation classification rather than leaving the differential open.

---

## 7. RAG Knowledge Requirements

### 7.1 Required Reference Documents
- 2023 ESC Guidelines on Acute Coronary Syndromes (ACS with STE)
- Sgarbossa EB et al. Electrocardiographic diagnosis of evolving myocardial infarction in LBBB. NEJM. 1996.
- Smith SW et al. — Modified Sgarbossa criteria (STE/QRS ratio)
- Spodick DH — Pericarditis ECG stages (definitive reference)
- Smith SW, Dodd KW et al. — Diagnosis of ST-elevation myocardial infarction in the presence of LBBB. Ann Emerg Med. 2012.
- Sharkey SW et al. — Takotsubo cardiomyopathy ECG criteria
- 2022 ESC Guidelines on Pericardial Diseases
- Antzelevitch C et al. — Brugada vs STEMI V1–V3 differential

### 7.2 PTB-XL Representation
PTB-XL contains labeled STEMI, LBBB, pericarditis, and early repolarization cases. STEMI representation covers inferior, anterior, lateral, and posterior territories. Training strategy: (1) train ST morphology classifier (convex/concave/coved) on labeled ECGs; (2) regional distribution detector; (3) reciprocal change detector; (4) Sgarbossa criteria extractor. PTB-XL Brugada and Takotsubo cases are limited — supplement with published datasets.

---

## 8. Dashboard Visualization Specification

### 8.1 Primary Display
- 12-lead ECG with ST elevation highlighted in all affected leads
- Distribution map: coronary territory overlay showing which territory affected
- Primary diagnosis with confidence; top 3 differentials with confidence scores
- STEMI protocol recommendation visible prominently

### 8.2 Annotation Overlays
- ST amplitude measurement (mm) per affected lead
- ST morphology label per lead: convex / concave / coved / discordant
- Reciprocal change indicators in contralateral leads
- PR depression measurement in limb leads
- Sgarbossa score display if QRS ≥120 ms (concordance/discordance per lead)
- aVR ST elevation callout

### 8.3 Risk Panel
- STEMI probability score with confidence interval
- Cath lab activation decision support (threshold-based alert)
- Pericarditis differentiation checklist
- Serial ECG comparison if prior available (delta STE, morphology change)
- Clinical context input: symptom onset time, chest pain character, prior MI

---

## 9. Edge Cases and Pitfalls

1. **Subtle posterior STEMI (no STE visible)**: Posterior STEMI (circumflex or RCA wraparound) shows ST depression in V1–V3 (reciprocal to posterior STE), not STE. Posterior leads (V7–V9) show STE. A standard 12-lead showing only anterior ST depression in V1–V3 may represent posterior STEMI — posterior leads must be added.
2. **De Winter T waves**: LAD occlusion variant without STE. Instead shows upsloping ST depression ≥1 mm at the J point with tall, symmetric peaked T waves in precordial leads. No STE present. This STEMI equivalent is frequently missed on automated interpretation and by inexperienced readers.
3. **Pericarditis with aVR elevation**: In pericarditis, aVR shows ST elevation (the opposite direction of the diffuse STE in other leads). This can be confused with the aVR STE pattern of LMCA occlusion. Differentiation: diffuse concave STE everywhere else = pericarditis; diffuse ST depression everywhere else = LMCA.
4. **New LBBB without symptoms**: The old guideline that new LBBB = STEMI is no longer endorsed without clinical context. New LBBB in the absence of chest pain does not mandate cath lab activation. Only new LBBB + typical ischemic symptoms warrants STEMI protocol.
5. **Takotsubo in young male post-cocaine**: Cocaine can trigger Takotsubo in males (less common than in post-menopausal females). The ECG shows anterior STE that evolves rapidly to deep TWI. Coronary vasospasm can coexist — cath may be needed to distinguish.
6. **Hyperkalemia Brugada phenocopy**: Severe hyperkalemia in V1–V2 can produce a pattern identical to Brugada Type 1 (coved STE V1–V2). Context: wide QRS, peaked T waves everywhere, P-wave loss, metabolic status. This is NOT true Brugada — it resolves with K+ correction.
7. **Right ventricular infarction with inferior STEMI**: RV infarction accompanies ~30-50% of inferior STEMIs (RCA). The ECG sign: STE in right-sided leads (V3R, V4R). Clinical significance: these patients must NOT receive nitrates (RV preload dependent) and require IV fluids. Right-sided leads must be performed in any inferior STEMI.

---

## 10. References

1. Thygesen K, Alpert JS, Jaffe AS, et al. Fourth Universal Definition of Myocardial Infarction. Eur Heart J. 2019;40(3):237-269.
2. Sgarbossa EB, Pinski SL, Barbagelata A, et al. Electrocardiographic diagnosis of evolving acute myocardial infarction in the presence of LBBB. N Engl J Med. 1996;334(8):481-487.
3. Smith SW, Dodd KW, Henry TD, et al. Diagnosis of ST-elevation myocardial infarction in the presence of LBBB with the ST-elevation to S-wave ratio in a modified Sgarbossa rule. Ann Emerg Med. 2012;60(6):766-776.
4. Spodick DH. Acute pericarditis: current concepts and practice. JAMA. 2003;289(9):1150-1153.
5. Ibanez B, James S, Agewall S, et al. 2017 ESC Guidelines for the management of acute myocardial infarction in patients presenting with ST-segment elevation. Eur Heart J. 2018;39(2):119-177.
6. Sclarovsky S, Birnbaum Y, Solodky A, et al. Isolated right ventricular infarction. J Electrocardiol. 1994;27(3):193-199.
7. Nikus K, Pahlm O, Wagner G, et al. Electrocardiographic classification of acute coronary syndromes. Ann Noninvasive Electrocardiol. 2010;15(1):75-84.
