# Voltage Criteria Systems for Ventricular Hypertrophy — ECG Reference

**Node:** 2.7.204
**SDA:** SDA-2 (Diagnosis & Agentic Core) — shared resource for SDA-1, SDA-3, SDA-4
**Status:** Research Complete
**Date:** 2026-03-27

---

## Purpose

This is a shared reference node. It contains all validated voltage criteria for left ventricular hypertrophy (LVH) and right ventricular hypertrophy (RVH), with sensitivity/specificity data, measurement instructions, and the YouOwnECG recommended implementation strategy. All disease nodes that require voltage assessment (LVH, HCM, RVH, biventricular hypertrophy, hypertension ECG, athlete heart) link to this reference rather than duplicating criteria.

ECGdeli provides waveform amplitude measurements in millivolts per lead. This reference defines which amplitudes to compute, which criteria to evaluate, and how to combine them into a hypertrophy assessment.

---

## LVH Voltage Criteria

### Criteria 1: Sokolow-Lyon

**Formula:** SV1 + RV5 (or RV6, whichever is larger) ≥ 35 mm

**Sex adjustment:** None in original; same threshold for men and women.

**Sensitivity:** 22–38% | **Specificity:** 84–100%

**Measurement:** S-wave depth in V1 (measured from baseline to nadir of S wave) + R-wave height in V5 or V6 (measured from baseline to peak of R wave). Use the larger of RV5 and RV6.

**Context:** The original criterion (Sokolow & Lyon, 1949). Low sensitivity — approximately 1 in 3 patients with echocardiographic LVH will meet this criterion. High specificity means a positive result is meaningful but a negative result does not exclude LVH.

**Age note:** The 35 mm threshold was derived in a general adult population. In younger adults (<35 years) and in athletes, higher voltage is expected — apply with caution; do not diagnose LVH on Sokolow-Lyon alone in young patients or athletes.

---

### Criteria 2: Cornell Voltage

**Formula (men):** RaVL + SV3 > 28 mm

**Formula (women):** RaVL + SV3 > 20 mm

**Sensitivity:** 42% | **Specificity:** 90%

**Measurement:** R-wave height in aVL + S-wave depth in V3.

**Context:** Casale et al. (1985, 1987). Sex-specific thresholds are important — the female threshold is lower because women have smaller body surface area and lower LV mass thresholds for LVH. Using the male threshold for women misses LVH in women.

**Key advantage over Sokolow-Lyon:** Less affected by lead placement variability in precordial leads V5/V6. aVL and V3 are more reproducibly placed.

---

### Criteria 3: Cornell Voltage-Duration Product

**Formula:** Cornell voltage (mm) × QRS duration (ms) ≥ 2440 mm·ms

**Sensitivity:** 51% | **Specificity:** 90–96%

**Measurement:** Cornell voltage (as above, sex-adjusted) × QRS duration in milliseconds (not seconds).

**Context:** Okin et al. (1995). This is the most validated LVH criterion for cardiovascular event prediction. The addition of QRS duration accounts for the fact that increased LV mass slows ventricular conduction as well as increasing voltage. A patient with high voltage AND a wide QRS (even subclinical IVCD at 110 ms) is more likely to have true hypertrophy than one with the same voltage and narrow QRS.

**YouOwnECG primary criterion:** Use Cornell voltage-duration product as the primary LVH criterion because:
1. QRS duration is automatically computed by ECGdeli
2. Higher sensitivity than voltage-only criteria
3. Best validated for cardiovascular outcomes (Framingham, LIFE trial data)

---

### Criteria 4: Romhilt-Estes Point System

**System:** Points assigned for multiple criteria; ≥5 points = definite LVH; 4 points = probable LVH

| Criterion | Points |
|---|---|
| Voltage: any of: R or S in limb leads ≥20 mm; SV1 or SV2 ≥30 mm; RV5 or RV6 ≥30 mm | 3 |
| ST-T abnormality (strain pattern, no digoxin) | 3 |
| ST-T abnormality (on digoxin) | 1 |
| Left atrial enlargement (terminal P in V1 >1 mm deep and >0.04 s wide) | 3 |
| Left axis deviation ≥−30° | 2 |
| QRS duration ≥0.09 s (90 ms) | 1 |
| Intrinsicoid deflection in V5/V6 ≥0.05 s (50 ms) | 1 |

**Sensitivity:** 54% | **Specificity:** 97% (at ≥5 points threshold)

**Context:** Romhilt & Estes (1968). Highest specificity of all LVH criteria — a score ≥5 is very reliable when present. However, the system is rarely used in contemporary practice because of complexity. It is included here for completeness and for cases where a second confirmatory criterion is needed.

---

### Criteria 5: Peguero-Lo Presti

**Formula (men):** SV4 + deepest S wave in any lead ≥ 28 mm

**Formula (women):** SV4 + deepest S wave in any lead ≥ 23 mm

**Sensitivity:** 62% | **Specificity:** 90%

**Measurement:** S-wave depth in V4 + the deepest S wave found across all 12 leads (often V2 or V3).

**Context:** Peguero et al. (2017). The most recently validated criterion. Currently the most sensitive single voltage criterion for LVH while maintaining high specificity. Outperforms both Sokolow-Lyon and Cornell voltage in head-to-head comparison against echocardiographic LVH. Sex-specific thresholds required.

**YouOwnECG secondary criterion:** Apply Peguero-Lo Presti as secondary LVH screen. A patient negative by Cornell voltage-duration product but positive by Peguero-Lo Presti should be flagged as "possible LVH — borderline criteria."

---

### Criteria 6: R in aVL

**Formula:** R-wave amplitude in aVL ≥ 11 mm

**Sensitivity:** 11–22% | **Specificity:** 95–99%

**Context:** Casale et al. (1985). Very low sensitivity — misses >75% of LVH — but very high specificity. An R in aVL ≥11 mm is a strong positive signal but absence does not exclude LVH. Useful as a quick screening criterion in a busy ER setting: if R in aVL ≥11 mm, LVH is highly likely.

**Additional context:** R in aVL is also used for LAFB diagnosis (left anterior fascicular block). These are related: LAFB is more common in the presence of LVH because the hypertrophied LV distorts fascicular anatomy.

---

### Criteria 7: Lewis Index

**Formula:** (R in I + S in III) − (S in I + R in III) > 1.6 mV (= 16 mm)

**Sensitivity:** 17–30% | **Specificity:** 89–95%

**Context:** Lewis (1914). Historical criterion; rarely used clinically. Included for completeness. Measures the net leftward QRS vector in the frontal plane.

---

## LVH Criteria Comparison Table

| Criterion | Threshold | Sensitivity | Specificity | Sex-Specific | QRS Duration Used | YouOwnECG Role |
|---|---|---|---|---|---|---|
| Sokolow-Lyon | SV1 + RV5/6 ≥ 35 mm | 22–38% | 84–100% | No | No | Tertiary |
| Cornell voltage | RaVL + SV3 >28 (M) / >20 (F) | 42% | 90% | Yes | No | Secondary component |
| Cornell voltage-duration | Cornell × QRS ≥ 2440 mm·ms | 51% | 90–96% | Yes | Yes | **Primary** |
| Romhilt-Estes | ≥5 points | 54% | 97% | No (partial) | Yes (1 point) | Confirmatory |
| Peguero-Lo Presti | SV4 + max S ≥28 (M) / ≥23 (F) | 62% | 90% | Yes | No | **Secondary** |
| R in aVL | ≥11 mm | 11–22% | 95–99% | No | No | Quick screen |
| Lewis index | >16 mm | 17–30% | 89–95% | No | No | Historical |

---

## LVH Repolarization (Strain) Pattern

Voltage criteria alone do not fully characterize LVH. The strain pattern accompanies established LVH and indicates secondary repolarization abnormality from pressure/volume overload:
- Asymmetric ST depression and T-wave inversion in leads with dominant R waves (I, aVL, V5, V6)
- ST segment downslopes from J-point (concave downward or horizontal depression)
- T-wave inversion in the same leads
- ST elevation in V1–V2 (mirror/reciprocal to lateral strain)

The strain pattern is a marker of more advanced hypertrophy and carries additional adverse prognostic significance beyond voltage alone. The system should report "LVH with strain pattern" when voltage criteria are met AND strain pattern is present.

---

## RVH Voltage Criteria

### Primary RVH Criteria

| Criterion | Threshold | Sensitivity | Specificity | Notes |
|---|---|---|---|---|
| R in V1 | ≥7 mm | 30–40% | 95% | Most specific single criterion |
| R/S ratio V1 | >1 with R ≥5 mm | 25–35% | 95% | Both conditions must be met |
| R in V1 + S in V5 or V6 | ≥10 mm | 35% | 96% | Sum criterion |
| S in V5 or V6 | ≥7 mm | 20–25% | 90% | RV vector persisting laterally |
| QRS axis | ≥+90° | Moderate | Moderate | Right axis deviation accompanies RVH |
| S1S2S3 pattern | Deep S in I, II, III | Moderate | Moderate | RV volume overload pattern |
| qR pattern in V1 | q followed by tall R | High specificity | — | Indicates severe RVH (RV systolic overload) |
| rSR' in V1 with R' >10 mm | Tall secondary R | Moderate | — | Volume overload; may overlap incomplete RBBB |

### Supportive RVH Features (Not Diagnostic Alone)

- Right atrial enlargement (P pulmonale: peaked P ≥2.5 mm in II)
- ST depression and T-wave inversion V1–V3 (RV strain pattern)
- Decreased R/S ratio in V5/V6 (R/S <1 in V6 = dominant RV pattern persisting laterally)
- QRS axis ≥+110° in adults (marked right axis deviation)

### Causes of RVH by Pattern

| Cause | ECG Pattern |
|---|---|
| Pulmonary arterial hypertension | qR in V1; right axis; RA enlargement; RV strain |
| Pulmonary stenosis | Tall R in V1; right axis; RA enlargement |
| RV volume overload (ASD, TR) | rSR' or RBBB morphology; moderate right axis |
| COPD/Emphysema | Right axis; low voltage limb leads; S1S2S3; clockwise rotation |
| Tetralogy of Fallot (repaired) | RBBB; varying R in V1 depending on repair |

---

## Pediatric Voltage Criteria Note

Adult LVH and RVH voltage thresholds do NOT apply to children. Age-specific R in V1 upper limits are required. In neonates, R in V1 ≥20 mm is NORMAL (RV dominant fetal circulation). R in V1 >20 mm is pathological RVH in an older child. See pediatric_ecg_normals.md (Node 2.7.108) for complete pediatric reference table.

---

## Clinical Application

### YouOwnECG Implementation Algorithm

```
Step 1: Measure required amplitudes (ECGdeli outputs)
  - S in V1 (mm)
  - R in V5, R in V6 (mm) → use larger
  - R in aVL (mm)
  - S in V3 (mm)
  - S in V4 (mm)
  - Deepest S across all leads (mm)
  - QRS duration (ms)
  - R in V1 (mm)
  - S in V5, S in V6 (mm)
  - Frontal QRS axis (degrees)

Step 2: Apply LVH criteria
  a) Cornell voltage (sex-adjusted): RaVL + SV3 → compute
  b) Cornell voltage-duration product: Cornell voltage × QRS duration
     → if ≥2440 mm·ms: LVH CRITERION MET (primary)
  c) Peguero-Lo Presti (sex-adjusted): SV4 + max(S any lead)
     → if ≥threshold: LVH CRITERION MET (secondary)
  d) Sokolow-Lyon: SV1 + max(RV5, RV6)
     → if ≥35 mm: LVH CRITERION MET (supporting)
  e) R in aVL quick screen:
     → if ≥11 mm: LVH highly likely

Step 3: Apply RVH criteria
  a) R in V1 ≥7 mm
  b) R/S V1 >1 (with R ≥5 mm)
  c) QRS axis ≥+90°
  d) S in V5 or V6 ≥7 mm
  → 2+ criteria met: RVH likely; 1 criterion: possible RVH

Step 4: Check for strain pattern
  → ST/T changes in dominant-R leads → "with strain"
  → ST/T changes in V1–V3 (RVH context) → "RV strain"

Step 5: Report
  → Primary criterion met (Cornell V-D) → "LVH" (with confidence)
  → Secondary only (Peguero) → "Possible LVH"
  → Supporting only (Sokolow/aVL) → "Voltage criterion met — LVH possible"
  → All negative → "No voltage criteria for LVH met — LVH not excluded"
```

### Sex Input Requirement
Cornell voltage and Peguero-Lo Presti require patient sex for threshold selection. If sex is not provided:
- Apply male thresholds (more conservative — fewer false positives but more false negatives in women)
- Flag: "Sex not provided — female-specific thresholds not applied; may underdetect LVH in women"

---

## Common Errors / Pitfalls

- **Using the same threshold for men and women.** Cornell voltage threshold is 28 mm for men and 20 mm for women. A woman with RaVL + SV3 = 22 mm meets LVH criteria for women but not men. The sex-agnostic application (using 28 mm for everyone) misses LVH in women — a well-documented sex disparity.

- **Applying adult LVH criteria to children and adolescents.** High voltage in young people is expected (thinner chest wall, larger cardiac-to-chest ratio). A 16-year-old male athlete with Sokolow ≥35 mm has a 50% chance of this being a normal variant. Always apply age context.

- **Concluding "no LVH" from a normal ECG.** The best available criterion (Peguero-Lo Presti) has only 62% sensitivity. Over one-third of patients with echocardiographic LVH will have a normal ECG by all voltage criteria. Normal ECG voltage does NOT exclude LVH. Echo is required for definitive LVH assessment.

- **Measuring S in V1 from the wrong baseline.** In patients with poor baseline wander, S-wave depth measurement must be from the TP segment baseline (preceding P-wave to QRS), not from the PR segment. ECGdeli baseline correction must be verified before voltage measurements.

- **Counting J-point elevation as ST elevation in LVH.** LVH strain pattern in V5–V6 is ST depression. The corresponding finding in V1–V2 is ST elevation (reciprocal) — this is normal secondary ST elevation in LVH, not STEMI. The system must not trigger STEMI alert for V1–V2 ST elevation that is symmetric and in the context of LVH with lateral strain.

- **Romhilt-Estes strain criterion double-counting.** The strain criterion (3 points) and voltage criterion (3 points) are the two highest-point items. In most patients with LVH, both are present, easily producing ≥5 points. The system should compute the score but also display the breakdown of which components contributed.

- **Peguero-Lo Presti: "deepest S in any lead" requires scanning all 12 leads.** The deepest S is most often in V2 or V3 but can be in any precordial or even a limb lead (in cases of RVH or left axis deviation). The algorithm must scan all 12 leads, not just anterior precordials.

---

## 6A. Agent Assignment

**Architecture:** Option E — 3 Parallel Phase 1 Specialists + 1 Sequential CDS (Node 2.1 Gate Passed 2026-03-27)

| Agent | Role for Voltage Criteria Reference | Key Features Used |
|-------|--------------------------|-------------------|
| **RRC** (Rhythm/Rate/Conduction) | Not involved | Voltage thresholds are not conduction interval measurements; RRC does not use this reference file |
| **IT** (Ischemia/Territory) | Not involved | Voltage amplitude criteria are not ischemia territory features; IT does not use this reference file |
| **MR** (Morphology/Repolarization) | Primary — this reference file is the MR Agent's voltage lookup table | Sokolow-Lyon: SV1 + RV5 or RV6 ≥35mm; Cornell voltage: RaVL + SV3 >28mm (men) or >20mm (women); Cornell product: Cornell voltage × QRS duration >2440mm·ms; Romhilt-Estes: point-score system (≥5 = definite LVH, 4 = probable); Peguero-Lo Presti: deepest S in any lead + SV4 ≥23mm (men) or ≥21mm (women); RVH criteria: R in V1 ≥7mm, R/S ratio >1 in V1; low voltage thresholds: <5mm all limb leads, <10mm all precordial leads |
| **CDS** (Cross-Domain Synthesis) | Not involved directly — uses MR output, not this file directly | CDS receives computed voltage scores from MR Agent; it does not independently query this reference file |

### Primary Agent
**MR** — this file is a reference lookup table used exclusively by the MR Agent during voltage amplitude assessment; it provides the threshold values MR applies when computing LVH criteria (Sokolow-Lyon, Cornell, Romhilt-Estes, Peguero-Lo Presti), RVH criteria, and low voltage thresholds.

### Cross-Domain Hints
No cross-domain hints required — this is a reference file, not a diagnostic entity. The MR Agent queries these thresholds internally during its processing pass; no inter-agent hints originate from reference files.

### CDS Specific Role
CDS does not directly interact with this reference file. It receives already-computed voltage scores from the MR Agent (e.g., "Sokolow-Lyon 38mm — LVH positive", "Cornell voltage 25mm — LVH positive in women") and uses those scored outputs for cross-domain adjudication (strain vs ischemia, LVH context for Q-wave interpretation, etc.). The thresholds in this file are operationalized entirely within the MR Agent's processing layer.

---

## References

1. Sokolow M, Lyon TP. The ventricular complex in left ventricular hypertrophy as obtained by unipolar precordial and limb leads. *Am Heart J.* 1949;37(2):161–186.
2. Casale PN, Devereux RB, Alonso DR, Campo E, Kligfield P. Improved sex-specific criteria of left ventricular hypertrophy for clinical and computer interpretation of electrocardiograms: validation with autopsy findings. *Circulation.* 1987;75(3):565–572.
3. Okin PM, Roman MJ, Devereux RB, Kligfield P. Electrocardiographic identification of increased left ventricular mass by simple voltage-duration products. *J Am Coll Cardiol.* 1995;25(2):417–423.
4. Romhilt DW, Estes EH. A point-score system for the ECG diagnosis of left ventricular hypertrophy. *Am Heart J.* 1968;75(6):752–758.
5. Peguero JG, Lo Presti S, Perez J, Issa O, Brenes JC, Carrillo A. Electrocardiographic criteria for the diagnosis of left ventricular hypertrophy. *J Am Coll Cardiol.* 2017;69(13):1694–1703.
6. Pewsner D, Jüni P, Egger M, Battaglia M, Sundström J, Bachmann LM. Accuracy of electrocardiography in diagnosis of left ventricular hypertrophy in arterial hypertension: systematic review. *BMJ.* 2007;335(7622):711.
7. Devereux RB, Wachtell K, Gerdts E, et al. Prognostic significance of left ventricular mass change during treatment of hypertension. *JAMA.* 2004;292(19):2350–2356.
8. Lewis T. Observations upon ventricular hypertrophy, with especial reference to preponderance of one or other chamber. *Heart.* 1914;5:367–402.
