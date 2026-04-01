# All Interval Normal Ranges (PR, QRS, QT/QTc) by Demographics — ECG Reference

**Node:** 2.7.203
**SDA:** SDA-2 (Diagnosis & Agentic Core) — shared resource for SDA-1, SDA-3, SDA-4
**Status:** Research Complete
**PGMR:** Required
**Date:** 2026-03-27

---

## Purpose

This reference defines every ECG interval measurement used across the YouOwnECG diagnostic pipeline, with normal ranges stratified by age, sex, and heart rate where applicable. It is the single authoritative source for interval thresholds consumed by: first-degree AV block (2.7.30), BBB nodes (2.7.40–2.7.43), Long QT/TdP (2.7.70), Short QT (2.7.71), WPW (2.7.58), P-wave duration criteria in atrial enlargement, and every other condition where an interval measurement gates a diagnosis. The YouOwnECG QTc formula selection rationale is documented here for SDA-1 implementation.

---

## 1. Measurement Fundamentals

### 1.1 Paper Speed and Calibration

All interval measurements assume standard ECG recording parameters. If paper speed or gain differs, values must be converted before applying the thresholds in this document.

| Parameter | Standard | Value |
|-----------|---------|-------|
| Paper speed | 25 mm/s | 1 small square (1 mm) = 40 ms |
| Paper speed | 25 mm/s | 1 large square (5 mm) = 200 ms |
| Gain | 10 mm/mV | 1 mm = 0.1 mV |
| Paper speed (doubled) | 50 mm/s | 1 small square = 20 ms; intervals appear twice as wide visually but are the same duration |

**Automated measurement note:** Digital ECG systems sample at 500–1000 Hz, giving 1–2 ms resolution. The thresholds in this document are stated in milliseconds. When converting from sample counts to milliseconds: `interval_ms = sample_count / sampling_rate_kHz`.

### 1.2 Measurement Lead Selection

| Interval | Best Lead(s) for Measurement | Rationale |
|----------|------------------------------|-----------|
| PR interval | Lead II or V1 | P wave onset clearest; II has longest P wave |
| QRS duration | Widest QRS across all 12 leads | QRS duration = longest measured; use the lead where Q onset and S offset are most visible |
| QT interval | Lead II or V5 | T-wave end clearest; avoid leads with biphasic or notched T waves |
| P-wave duration | Lead II | P wave most clearly visible; longest P wave typically seen here |
| RR interval | Any lead with clear R waves; Lead II preferred | Used to compute heart rate and for QTc calculation |

**QT measurement rule:** Measure from the first deflection of QRS to the return of the T wave to baseline. If a U wave is present, measure to the nadir between T and U. If T and U are fused, measure to the nadir of the T-wave shoulder. Do not include the U wave in QT measurement unless T and U are inseparably fused.

---

## 2. PR Interval

### 2.1 Normal Range

| Population | Normal PR Range | Notes |
|-----------|----------------|-------|
| Adults | 120–200 ms (3–5 small squares) | Rate-dependent — see Section 2.2 |
| Children 3–12 years | 110–180 ms | Shorter due to smaller atria, faster rates |
| Infants <3 years | 80–160 ms | Shorter; higher resting heart rates |
| Athletes | Up to 220 ms may be normal | Vagal tone; must correlate clinically |

### 2.2 Heart Rate Dependence

The PR interval is longer at slower heart rates due to AV nodal rate-dependent conduction. Upper limit of normal increases slightly at slow rates.

| Heart Rate (bpm) | Upper Limit of Normal PR (ms) |
|-----------------|-------------------------------|
| >100 | 180 |
| 70–100 | 200 |
| 50–70 | 210 |
| <50 | 220 (in athletes; pathological in non-athletes) |

### 2.3 Abnormal PR Intervals

| Finding | Threshold | Interpretation |
|---------|-----------|---------------|
| Short PR | <120 ms | Pre-excitation (WPW, LGL), junctional rhythm with retrograde P, enhanced AV node conduction |
| Borderline short | 100–120 ms | Warrants delta wave search; normal PR does not exclude WPW if delta wave present |
| Prolonged — 1° AV block | >200 ms (constant) | First-degree AV block; always conduct, just slowly |
| Progressive prolongation | Beats with increasing PR until dropped QRS | Second-degree AV block Type I (Wenckebach) |
| Fixed prolonged PR with dropped beats | Constant PR + intermittent non-conducted P | Second-degree AV block Type II |
| Complete AV dissociation | No consistent PR relationship | Third-degree (complete) AV block |

---

## 3. QRS Duration

### 3.1 Normal Range

| Population | Normal QRS Duration | Notes |
|-----------|-------------------|-------|
| Adults | <120 ms (<3 small squares) | Conducted via His-Purkinje, fast and synchronous |
| Children | <100 ms | Smaller ventricular mass, shorter conduction paths |
| Infants | <80 ms | Very fast conduction relative to heart size |

### 3.2 QRS Duration Classification

| Duration | Classification | Interpretation |
|----------|---------------|---------------|
| <100 ms | Normal (children) / Narrow (adults) | Normal conduction |
| 100–119 ms | Normal narrow (adults) | Narrow QRS |
| 110–119 ms | Incomplete BBB (if RBBB/LBBB morphology present) | Incomplete RBBB or LBBB |
| ≥120 ms | Complete BBB or ventricular origin | Complete RBBB, complete LBBB, IVCD, ventricular tachycardia, ventricular pacing, hyperkalemia |

### 3.3 Clinical Interpretation of Wide QRS

**Step 1:** Is there a P wave with a fixed PR preceding each wide QRS? If yes → supraventricular origin with aberrancy (BBB). If no → ventricular origin must be considered.

**Step 2:** Does the morphology match RBBB or LBBB pattern? If RBBB pattern → RBBB (or SVT with RBBB aberrancy). If LBBB pattern → LBBB (or SVT with LBBB aberrancy), or ventricular tachycardia (Brugada VT morphology criteria apply).

**Step 3:** For indeterminate wide complex tachycardia, apply Brugada algorithm, Wellens criteria, or aVR lead criteria (Node 2.7.80 — VT differentiation).

---

## 4. QT Interval and QTc

### 4.1 Why Rate Correction Is Required

The QT interval shortens at faster heart rates and lengthens at slower rates. A QT of 450 ms at a heart rate of 90 bpm is prolonged; the same QT at 45 bpm may be normal. All clinical decisions about QT prolongation use the **rate-corrected QT (QTc)**.

### 4.2 QTc Formulas

#### Bazett Formula (most widely used historically)

```
QTc = QT / √(RR)
```

Where QT and RR are both in seconds. RR = 60/HR (in seconds).

- **Advantage:** Simple, universally known, built into most ECG machines.
- **Disadvantage:** Significantly overcorrects at high heart rates (>100 bpm) — artificially prolonged QTc. Undercorrects at low heart rates (<50 bpm) — artificially shortened QTc. Bazett QTc is unreliable at extremes of heart rate.

#### Fridericia Formula (recommended for YouOwnECG automated computation)

```
QTc = QT / (RR)^(1/3)
```

Where QT and RR are both in seconds.

- **Advantage:** More accurate across the full physiological heart rate range. Avoids the overcorrection problem at high rates. Better performance in algorithmic environments where the agent may encounter wide HR ranges without human correction.
- **Disadvantage:** Less ingrained in clinical culture; some clinicians default to Bazett for familiarity.
- **YouOwnECG decision:** Use Fridericia as the primary QTc formula for all automated computations. Report the Fridericia QTc. If Bazett QTc is also requested for comparison (e.g., for drug QT studies that defined thresholds using Bazett), compute and label it clearly as QTc-Bazett to avoid confusion.

#### Hodges Formula

```
QTc = QT + 1.75 × (HR − 60)
```

Where QT is in ms and HR is in bpm.

- Linear correction; performs well in the 60–100 bpm range. Not recommended for rates <50 or >100.

#### Framingham Formula

```
QTc = QT + 0.154 × (1 − RR)
```

Where QT and RR are in seconds.

- Good for population studies. Similar accuracy to Fridericia for clinical use.

### 4.3 QTc Normal Ranges

| Population | Normal QTc | Borderline | Prolonged | Very Prolonged |
|-----------|-----------|-----------|----------|---------------|
| Adult men | ≤440 ms | 441–470 ms | >470 ms | ≥500 ms |
| Adult women | ≤450 ms | 451–480 ms | >480 ms | ≥500 ms |
| Children (<15 years) | ≤460 ms | 461–480 ms | >480 ms | ≥500 ms |
| Neonates | ≤440 ms | 441–460 ms | >460 ms | — |

**Sex difference rationale:** Before puberty, QTc is similar in boys and girls. After puberty, testosterone shortens the QT interval — men have shorter QTc. Estrogen has a QT-prolonging effect, making women more susceptible to drug-induced QTc prolongation and TdP.

### 4.4 TdP Risk by QTc Duration

| QTc (ms) | TdP Risk | Clinical Action |
|----------|---------|----------------|
| <440 (men) / <450 (women) | Negligible | No action |
| 440–499 | Low but monitor | Review QT-prolonging drugs; correct electrolytes |
| 500–549 | Moderate | High priority flag; stop QT-prolonging drugs; correct K⁺, Mg²⁺, Ca²⁺; continuous monitoring |
| ≥550 | High | Urgent — TdP imminent risk; magnesium IV; consider temporary pacing if bradycardic; electrophysiology consult |
| ≥600 | Very high | Treat as pre-TdP emergency |

### 4.5 Short QT

| Finding | Threshold | Interpretation |
|---------|-----------|---------------|
| Short QTc | ≤340 ms | Short QT syndrome consideration (Gussak criteria) |
| Borderline short | 341–360 ms | Correlate with symptoms; genetic testing if unexplained syncope or family history of sudden death |
| Causes of short QT | | Hypercalcemia, digitalis effect, short QT syndrome (KCNH2/KCNQ1/KCNJ2 mutations), hyperthermia |

---

## 5. P-Wave Duration

| Population | Normal P-Wave Duration | Abnormal |
|-----------|----------------------|---------|
| Adults | <120 ms (<3 small squares) | ≥120 ms = prolonged |
| Children | <90 ms | ≥90 ms = prolonged |

**Prolonged P-wave duration (≥120 ms):** Indicates delayed intra-atrial or inter-atrial conduction. Seen in left atrial enlargement, inter-atrial block (Bayés syndrome). Often associated with a notched P wave ("P mitrale") in Lead II.

**Tall peaked P wave (≥2.5 mm in II):** P pulmonale — right atrial enlargement. Duration is often normal. This is a voltage criterion, not a duration criterion.

---

## 6. RR and PP Intervals

### 6.1 Clinical Uses

| Interval | Computation | Clinical Use |
|----------|------------|-------------|
| RR interval | Time between consecutive R waves (ms) | Heart rate = 60,000 / RR(ms); regularity assessment |
| PP interval | Time between consecutive P waves (ms) | Atrial rate; SA node automaticity; detect SA block |
| RR variability | Standard deviation of consecutive RR intervals | Autonomic function; heart rate variability |

### 6.2 Heart Rate from RR

```
Heart rate (bpm) = 60,000 / RR_interval_ms
```

Or at 25 mm/s paper speed:

```
Heart rate = 1500 / number_of_small_squares_in_one_RR_cycle
```

Or using large squares:

```
Heart rate ≈ 300 / number_of_large_squares_in_one_RR_cycle
```

(Values: 1 large square → 300 bpm, 2 → 150, 3 → 100, 4 → 75, 5 → 60, 6 → 50)

---

## 7. All Intervals — Quick Reference Table

| Interval | Normal (Adult) | Short (Abnormal) | Long (Abnormal) | Rate Dependent |
|----------|---------------|-----------------|----------------|---------------|
| PR | 120–200 ms | <120 ms | >200 ms | Yes (longer at slow rates) |
| QRS | <120 ms | — | ≥120 ms (BBB) | No |
| QTc (men) | ≤440 ms | ≤340 ms | >470 ms | Yes (use QTc, not raw QT) |
| QTc (women) | ≤450 ms | ≤340 ms | >480 ms | Yes (use QTc, not raw QT) |
| P-wave duration | <120 ms | — | ≥120 ms | No |
| RR | Varies with HR | — | — | Is the rate itself |

---

## 8. Clinical Application

**How agents use this reference in reasoning chains:**

1. **PR gate:** Every rhythm node begins with PR measurement. PR <120 ms → search for delta wave and pre-excitation. PR >200 ms → flag first-degree AV block before continuing.

2. **QRS gate:** QRS ≥120 ms diverts the diagnostic chain to the BBB pathway before any diagnosis that assumes narrow QRS conduction.

3. **QTc computation:** The SDA-1 pipeline computes QTc-Fridericia for every ECG. Any QTc ≥500 ms generates a STAT flag independent of the primary diagnosis chain.

4. **Interval sequence dependency:** PR → QRS → QT must be measured in order. A misidentified PR (e.g., delta wave counted as PR) corrupts QRS onset marking, which then corrupts QT measurement. The agent must detect pre-excitation before measuring QRS duration.

5. **Pediatric scaling:** Before applying any threshold, the agent checks patient age and selects the appropriate table. A pediatric ECG run through adult thresholds will produce systematic false positives.

---

## 9. Common Errors / Pitfalls

**1. Using raw QT instead of QTc for clinical decisions**
Raw QT has no meaning without heart rate context. All flagging and thresholds must use QTc. The agent must never report "QT prolonged" based on raw QT — only QTc.

**2. Bazett overcorrection at high heart rates**
Bazett QTc at HR 120 bpm systematically overcorrects by 20–40 ms compared to Fridericia. An agent using Bazett will generate false QTc prolongation flags in patients with sinus tachycardia. This is a real clinical problem and the primary reason YouOwnECG uses Fridericia.

**3. Measuring QRS duration from a single lead**
QRS duration must be measured as the widest QRS across all 12 leads. A narrow QRS in Lead II does not exclude a wide QRS in V1 (e.g., isolated terminal R' in V1 of RBBB may only be visible in certain leads).

**4. Including the U wave in QT measurement**
The U wave follows the T wave and represents Purkinje repolarization or mechano-electrical coupling. Including it in QT measurement artificially prolongs the apparent QT. If U is fused with T and cannot be separated, note this in the output.

**5. PR measurement in WPW**
In WPW, the "PR interval" contains the delta wave. The true AV nodal conduction time cannot be measured from the surface ECG because the ventricle begins pre-excitation before the normal AV node conduction completes. Reporting "short PR" in WPW is technically correct but mechanistically different from junctional rhythm short PR.

**6. Applying adult QTc thresholds to children**
Children (especially under age 15) have a higher QTc upper limit of normal (460 ms). Adult thresholds (440 ms men, 450 ms women) will generate false positive QTc prolongation flags in pediatric ECGs.

**7. Not accounting for rate dependence in PR interpretation**
A PR of 210 ms in a healthy athlete with HR 42 bpm may reflect vagal tone, not pathological first-degree AV block. The agent should note "PR at upper limit — correlate with rate and clinical context" rather than flagging it as definitive first-degree AV block.

---

## 6A. Agent Assignment

**Architecture:** Option E — 3 Parallel Phase 1 Specialists + 1 Sequential CDS (Node 2.1 Gate Passed 2026-03-27)

| Agent | Role for Interval Normals Reference | Key Features Used |
|-------|--------------------------|-------------------|
| **RRC** (Rhythm/Rate/Conduction) | Primary user — queries PR interval and QRS duration thresholds | PR interval normal range (120-200ms); first-degree AV block threshold (>200ms); incomplete BBB QRS (100-119ms); complete BBB QRS (≥120ms); RR interval for rate and QTc calculation |
| **IT** (Ischemia/Territory) | Queries ischemic ST threshold values | ST elevation ischemia thresholds (≥1mm in limb leads, ≥2mm in precordial leads for men, ≥1.5mm in V2-V3 for women); ST depression ischemia threshold (≥0.5mm) |
| **MR** (Morphology/Repolarization) | Queries QTc thresholds | QTc normal ranges: <440ms men, <460ms women; borderline 440-460ms men, 460-480ms women; prolonged >460ms men, >480ms women; STAT threshold >500ms; QTc formula (Fridericia recommended) |
| **CDS** (Cross-Domain Synthesis) | Queries age/sex-adjusted normal ranges | Uses age- and sex-specific normal range tables for final interpretation; applies to pediatric ECG context when age-specific thresholds are required |

### Primary Agent
All three Phase 1 agents query this reference for their respective interval domains. RRC for PR and QRS; MR for QTc; IT for ST thresholds. No single primary agent — this is a shared threshold reference.

### Cross-Domain Hints
No cross_domain_hints are generated from this reference file. Each Phase 1 agent queries it internally when comparing measured intervals against normal ranges. The reference provides the threshold values that determine whether a finding is normal or abnormal in each agent's output.

### CDS Specific Role
CDS queries this reference for age- and sex-adjusted normal ranges when integrating Phase 1 outputs. CDS uses the reference to confirm that all Phase 1 agents have applied appropriate thresholds and to apply the STAT QTc threshold (>500ms) for TdP risk flagging. CDS also applies this reference when pediatric age-specific thresholds are required, using the reference in conjunction with the pediatric_ecg_normals.md file for age-stratified interpretation.

---

## References

- Bazett HC. An analysis of the time-relations of electrocardiograms. *Heart*. 1920;7:353–370.
- Fridericia LS. Die Systolendauer im Elektrokardiogramm bei normalen Menschen und bei Herzkranken. *Acta Med Scand*. 1920;53:469–486.
- Rautaharju PM, Surawicz B, Gettes LS, et al. AHA/ACCF/HRS recommendations for the standardization and interpretation of the electrocardiogram. Part IV: The ST segment, T and U waves, and the QT interval. *J Am Coll Cardiol*. 2009;53(11):982–991.
- Mason JW, Hancock EW, Gettes LS, et al. Recommendations for the standardization and interpretation of the electrocardiogram. Part II: Electrocardiography diagnostic statement list. *J Am Coll Cardiol*. 2007;49(10):1128–1135.
- Funck-Brentano C, Jaillon P. Rate-corrected QT interval: techniques and limitations. *Am J Cardiol*. 1993;72(6):17B–22B.
- Goldenberg I, Moss AJ, Zareba W. QT interval: how to measure it and what is "normal." *J Cardiovasc Electrophysiol*. 2006;17(3):333–336.
- Rijnbeek PR, van Herpen G, Bots ML, et al. Normal values of the electrocardiogram for ages 16–90 years. *J Electrocardiol*. 2014;47(6):914–921.
- Gussak I, Brugada P, Brugada J, et al. Idiopathic short QT interval: a new clinical syndrome? *Cardiology*. 2000;94(2):99–102.
