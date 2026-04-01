# Disease Knowledge Base — Index

**Node:** 2.7 (Disease-to-ECG Manifestation Knowledge Base)
**SDA:** Cross-cutting — owned by SDA-2, consumed by SDA-1 (features), SDA-3 (dashboards), SDA-4 (RAG)
**Date:** 2026-03-26
**Status:** Phase 3 Complete — all 94 disease/reference files written (2026-03-27)
**Template:** [_TEMPLATE.md](_TEMPLATE.md)

---

## Purpose

Each disease/condition gets a standalone .md that documents the COMPLETE chain:
**Root cause (pathophysiology) → Electrical mechanism → Lead-by-lead ECG presentation → Diagnostic criteria → Reasoning complexity analysis → Dashboard spec**

### Bidirectional Dependency with Node 2.1 (Agent Architecture Research)

```
Disease .md files (Node 2.7)                 Agent Architecture (Node 2.1)
┌─────────────────────────┐                  ┌─────────────────────────┐
│ Section 6: Reasoning     │ ──── FEEDS ───→ │ Analyze all 95 disease  │
│ Complexity Analysis      │                  │ reasoning complexities  │
│ - reasoning domains      │                  │ to DISCOVER the best    │
│ - cross-domain deps      │                  │ agent architecture      │
│ - difficulty scores      │                  │                         │
├─────────────────────────┤                  ├─────────────────────────┤
│ Section 6A: Agent        │ ←── FILLS IN ── │ Output: architecture    │
│ Assignment               │                  │ definition (# agents,   │
│ (BLANK until 2.1 done)   │                  │ specializations, comms) │
└─────────────────────────┘                  └─────────────────────────┘
```

**Phase 1** disease files (STAT conditions) are completed FIRST with Sections 1–6 + 7–10.
Section 6A (Agent Assignment) remains blank until Node 2.1 research determines the architecture.
After Node 2.1 gate passes, Section 6A is filled in for ALL disease files.

### All Downstream Consumers
- **SDA-1** (Feature Extraction): Section 6.2 (Feature Dependencies) tells what to compute
- **SDA-2** (Agents): Section 6 (Reasoning Complexity) drives architecture; Section 6A (Agent Assignment) drives agent design
- **SDA-3** (Dashboards): Section 8 (Dashboard Visualization Spec) drives per-disease UI
- **SDA-4** (RAG): Section 7 (RAG Knowledge Requirements) drives retrieval targeting

---

## STAT Conditions (Immediate Life Threat)

These are researched and documented FIRST — they are the highest priority.

| # | File | Condition | Primary Agent | Status |
|---|------|-----------|---------------|--------|
| 2.7.1 | `stemi_anterior.md` | Anterior STEMI (LAD occlusion) | Ischemia | **Complete** |
| 2.7.2 | `stemi_inferior.md` | Inferior STEMI (RCA/LCx occlusion) | Ischemia | **Complete** |
| 2.7.3 | `stemi_lateral.md` | Lateral STEMI (LCx/diagonal occlusion) | Ischemia | **Complete** |
| 2.7.4 | `stemi_posterior.md` | Posterior STEMI (posterior descending) | Ischemia | **Complete** |
| 2.7.5 | `stemi_right_ventricular.md` | Right Ventricular STEMI (proximal RCA) | Ischemia | **Complete** |
| 2.7.6 | `wellens_syndrome.md` | Wellens Syndrome (Type A & B — critical LAD stenosis) | Ischemia | **Complete** |
| 2.7.7 | `de_winter_t_waves.md` | de Winter T-waves (LAD occlusion equivalent) | Ischemia | **Complete** |
| 2.7.8 | `complete_av_block.md` | Complete (3rd Degree) AV Block | Conduction | **Complete** |
| 2.7.9 | `ventricular_tachycardia.md` | Sustained Ventricular Tachycardia | Rhythm | **Complete** |
| 2.7.10 | `ventricular_fibrillation.md` | Ventricular Fibrillation | Rhythm | **Complete** |
| 2.7.11 | `hyperkalemia.md` | Severe Hyperkalemia (peaked T → wide QRS → sine wave) | Morphology | **Complete** |
| 2.7.12 | `brugada_type1.md` | Brugada Syndrome Type 1 (coved pattern) | Morphology | **Complete** |
| 2.7.13 | `long_qt_tdp.md` | Long QT with Torsades de Pointes Risk | Morphology | **Complete** |

---

## Rhythm Disorders

| # | File | Condition | Status |
|---|------|-----------|--------|
| 2.7.20 | `sinus_normal.md` | Normal Sinus Rhythm (baseline reference) | **Research Complete** |
| 2.7.21 | `sinus_tachycardia.md` | Sinus Tachycardia | **Research Complete** |
| 2.7.22 | `sinus_bradycardia.md` | Sinus Bradycardia | **Research Complete** |
| 2.7.23 | `sinus_arrhythmia.md` | Sinus Arrhythmia | **Research Complete** |
| 2.7.24 | `atrial_fibrillation.md` | Atrial Fibrillation | **Research Complete** |
| 2.7.25 | `atrial_flutter.md` | Atrial Flutter (typical & atypical) | **Research Complete** |
| 2.7.26 | `svt.md` | Supraventricular Tachycardia (AVNRT, AVRT) | **Research Complete** |
| 2.7.27 | `multifocal_atrial_tachycardia.md` | Multifocal Atrial Tachycardia (MAT) | **Research Complete** |
| 2.7.28 | `pac.md` | Premature Atrial Complexes (PACs) | **Research Complete** |
| 2.7.29 | `pvc.md` | Premature Ventricular Complexes (PVCs) | **Research Complete** |
| 2.7.30 | `junctional_rhythm.md` | Junctional Rhythm / Junctional Tachycardia | **Research Complete** |
| 2.7.31 | `aivr.md` | Accelerated Idioventricular Rhythm (AIVR) | **Research Complete** |
| 2.7.32 | `sick_sinus_syndrome.md` | Sick Sinus Syndrome (tachy-brady) | **Research Complete** |
| 2.7.33 | `wandering_atrial_pacemaker.md` | Wandering Atrial Pacemaker | **Research Complete** |

---

## Conduction Disorders

| # | File | Condition | Status |
|---|------|-----------|--------|
| 2.7.40 | `first_degree_av_block.md` | First Degree AV Block | **Research Complete** |
| 2.7.41 | `second_degree_av_block_type1.md` | Second Degree AV Block — Mobitz Type I (Wenckebach) | **Research Complete** |
| 2.7.42 | `second_degree_av_block_type2.md` | Second Degree AV Block — Mobitz Type II | **Research Complete** |
| 2.7.43 | `high_grade_av_block.md` | High-Grade AV Block (2:1 and advanced) | **Research Complete** |
| 2.7.44 | `rbbb.md` | Right Bundle Branch Block (RBBB) | **Research Complete** |
| 2.7.45 | `lbbb.md` | Left Bundle Branch Block (LBBB) | **Research Complete** |
| 2.7.46 | `incomplete_rbbb.md` | Incomplete RBBB | **Research Complete** |
| 2.7.47 | `incomplete_lbbb.md` | Incomplete LBBB | **Research Complete** |
| 2.7.48 | `lafb.md` | Left Anterior Fascicular Block (LAFB) | **Research Complete** |
| 2.7.49 | `lpfb.md` | Left Posterior Fascicular Block (LPFB) | **Research Complete** |
| 2.7.50 | `bifascicular_block.md` | Bifascicular Block (RBBB + LAFB or LPFB) | **Research Complete** |
| 2.7.51 | `trifascicular_block.md` | Trifascicular Block | **Research Complete** |
| 2.7.52 | `wpw.md` | Wolff-Parkinson-White (WPW) / Pre-excitation | **Research Complete** |
| 2.7.53 | `ivcd.md` | Intraventricular Conduction Delay (IVCD) | **Research Complete** |
| 2.7.54 | `rate_dependent_bbb.md` | Rate-Dependent Bundle Branch Block | **Research Complete** |

---

## Ischemic / Infarction Patterns

| # | File | Condition | Status |
|---|------|-----------|--------|
| 2.7.60 | `nstemi.md` | Non-ST Elevation MI (NSTEMI) | **Research Complete** |
| 2.7.61 | `unstable_angina_ecg.md` | Unstable Angina — ECG Patterns | **Research Complete** |
| 2.7.62 | `old_mi_anterior.md` | Old/Prior MI — Anterior (pathological Q waves V1-V4) | **Research Complete** |
| 2.7.63 | `old_mi_inferior.md` | Old/Prior MI — Inferior (pathological Q waves II, III, aVF) | **Research Complete** |
| 2.7.64 | `old_mi_lateral.md` | Old/Prior MI — Lateral | **Research Complete** |
| 2.7.65 | `poor_r_wave_progression.md` | Poor R-Wave Progression | **Research Complete** |
| 2.7.66 | `sgarbossa_criteria.md` | Sgarbossa / Smith-Modified Sgarbossa (STEMI + LBBB) | **Research Complete** |
| 2.7.67 | `stemi_equivalent_patterns.md` | STEMI Equivalents Overview | **Research Complete** |
| 2.7.68 | `reciprocal_changes.md` | Reciprocal Changes — Anatomy and Significance | **Research Complete** |
| 2.7.69 | `subendocardial_ischemia.md` | Subendocardial Ischemia (diffuse ST depression) | **Research Complete** |

---

## Structural Abnormalities

| # | File | Condition | Status |
|---|------|-----------|--------|
| 2.7.70 | `lvh.md` | Left Ventricular Hypertrophy (all scoring systems) | **Research Complete** |
| 2.7.71 | `rvh.md` | Right Ventricular Hypertrophy | **Research Complete** |
| 2.7.72 | `lae.md` | Left Atrial Enlargement (P-mitrale) | **Research Complete** |
| 2.7.73 | `rae.md` | Right Atrial Enlargement (P-pulmonale) | **Research Complete** |
| 2.7.74 | `biatrial_enlargement.md` | Biatrial Enlargement | **Research Complete** |
| 2.7.75 | `biventricular_hypertrophy.md` | Biventricular Hypertrophy | **Research Complete** |
| 2.7.76 | `hcm.md` | Hypertrophic Cardiomyopathy (HCM) | **Research Complete** |
| 2.7.77 | `dcm.md` | Dilated Cardiomyopathy (DCM) | **Research Complete** |
| 2.7.78 | `arvc.md` | Arrhythmogenic RV Cardiomyopathy (ARVC) — epsilon waves | **Research Complete** |

---

## Morphology / Repolarization Abnormalities

| # | File | Condition | Status |
|---|------|-----------|--------|
| 2.7.80 | `long_qt.md` | Long QT Syndrome (congenital & acquired) | **Research Complete** |
| 2.7.81 | `short_qt.md` | Short QT Syndrome | **Research Complete** |
| 2.7.82 | `brugada_all_types.md` | Brugada Pattern — All Types (Type 1 coved, Type 2 saddle-back) | **Research Complete** |
| 2.7.83 | `early_repolarization.md` | Early Repolarization (benign vs malignant) | **Research Complete** |
| 2.7.84 | `t_wave_inversion_patterns.md` | T-Wave Inversion — All Patterns and Causes | **Research Complete** |
| 2.7.85 | `st_elevation_differential.md` | ST Elevation Differential (STEMI vs pericarditis vs early repol vs BER) | **Research Complete** |
| 2.7.86 | `u_wave.md` | U-Wave — When Present and Clinical Significance | **Research Complete** |
| 2.7.87 | `electrical_alternans.md` | Electrical Alternans (pericardial effusion/tamponade) | **Research Complete** |
| 2.7.88 | `low_voltage.md` | Low Voltage QRS — Causes and Significance | **Research Complete** |
| 2.7.89 | `strain_pattern.md` | Strain Pattern (LV strain, RV strain) | **Research Complete** |

---

## Metabolic / Electrolyte / Drug Effects

| # | File | Condition | Status |
|---|------|-----------|--------|
| 2.7.90 | `hyperkalemia.md` | Hyperkalemia (full spectrum: mild → severe → sine wave) | **Research Complete** |
| 2.7.91 | `hypokalemia.md` | Hypokalemia (ST depression, U-waves, T flattening) | **Research Complete** |
| 2.7.92 | `hypercalcemia.md` | Hypercalcemia (short QT, Osborn waves) | **Research Complete** |
| 2.7.93 | `hypocalcemia.md` | Hypocalcemia (prolonged QT) | **Research Complete** |
| 2.7.94 | `hypomagnesemia.md` | Hypomagnesemia (TdP risk, U-waves) | **Research Complete** |
| 2.7.95 | `digoxin_effect.md` | Digoxin Effect / Toxicity (Salvador Dali mustache, bigeminy) | **Research Complete** |
| 2.7.96 | `antiarrhythmic_effects.md` | Antiarrhythmic Drug Effects (Class I-IV) | **Research Complete** |
| 2.7.97 | `tca_overdose.md` | Tricyclic Antidepressant Overdose (wide QRS, RAD, R aVR) | **Research Complete** |
| 2.7.98 | `hypothermia.md` | Hypothermia (Osborn/J waves, bradycardia) | **Research Complete** |

---

## Special Patterns / Multi-System

| # | File | Condition | Status |
|---|------|-----------|--------|
| 2.7.100 | `pericarditis.md` | Acute Pericarditis (diffuse ST elevation, PR depression, Spodick's sign) | **Research Complete** |
| 2.7.101 | `myocarditis.md` | Myocarditis — ECG Patterns | **Research Complete** |
| 2.7.102 | `pulmonary_embolism.md` | Pulmonary Embolism (S1Q3T3, RV strain, sinus tach, RBBB) | **Research Complete** |
| 2.7.103 | `pericardial_effusion.md` | Pericardial Effusion / Tamponade (low voltage, electrical alternans) | **Research Complete** |
| 2.7.104 | `takotsubo.md` | Takotsubo Cardiomyopathy (stress cardiomyopathy) | **Research Complete** |
| 2.7.105 | `athlete_heart.md` | Athletic Heart — Normal Variants in Athletes | **Research Complete** |
| 2.7.106 | `pacemaker_rhythms.md` | Pacemaker Rhythms (AAI, VVI, DDD, BiV) | **Research Complete** |
| 2.7.107 | `dextrocardia.md` | Dextrocardia / Lead Reversal Patterns | **Research Complete** |
| 2.7.108 | `pediatric_ecg_normals.md` | Pediatric ECG Normal Variants (RVH normal in neonates, etc.) | **Research Complete** |
| 2.7.109 | `pregnancy_ecg.md` | Pregnancy — ECG Changes | **Research Complete** |

---

## Cross-Cutting References (Not Per-Disease)

| # | File | Topic | Status |
|---|------|-------|--------|
| 2.7.200 | `normal_ecg_reference.md` | Complete Normal ECG — All Parameters, All Leads, All Demographics | **Research Complete** |
| 2.7.201 | `lead_anatomy_reference.md` | Which Lead Sees What — Cardiac Anatomy to Lead Mapping | **Research Complete** |
| 2.7.202 | `ecg_axes_reference.md` | Cardiac Axes — P, QRS, T — Normal Ranges by Age/Sex | **Research Complete** |
| 2.7.203 | `interval_normals_reference.md` | All Interval Normal Ranges (PR, QRS, QT/QTc) by Demographics | **Research Complete** |
| 2.7.204 | `voltage_criteria_reference.md` | All Voltage Criteria Systems (Sokolow-Lyon, Cornell, Romhilt-Estes, etc.) | **Research Complete** |

---

## Statistics

| Category | Count |
|----------|-------|
| STAT conditions | 13 |
| Rhythm disorders | 14 |
| Conduction disorders | 15 |
| Ischemic patterns | 10 |
| Structural abnormalities | 9 |
| Morphology abnormalities | 10 |
| Metabolic/electrolyte/drug | 9 |
| Special patterns | 10 |
| Cross-cutting references | 5 |
| **Total disease .md files** | **95** |

---

## Research Order (Priority)

### Phase 1 — STAT Conditions + References (do FIRST — feeds into Node 2.1)
All 13 STAT files (2.7.1 – 2.7.13) + Normal ECG reference (2.7.200) + Lead anatomy reference (2.7.201)
**Output**: 15 complete .md files with Sections 1–6 + 7–10. Section 6A left blank.
**Then**: Node 2.1 reads all Phase 1 reasoning complexity analyses to begin architecture research.

### Phase 2 — Common ER Conditions (parallel with Node 2.1 research)
AFib (2.7.24), AFlutter (2.7.25), RBBB (2.7.44), LBBB (2.7.45), LVH (2.7.70), Pericarditis (2.7.100), PE (2.7.102)
**Additional reasoning complexity data refines Node 2.1 architecture decision.**

### Phase 3 — Complete Coverage (can proceed while Node 2.1 finalizes)
All remaining conditions — full Section 1–6 + 7–10, Section 6A still blank.

### Phase 4 — Agent Assignment + Edge Cases (AFTER Node 2.1 Gate Passes)
- Fill in Section 6A (Agent Assignment) for ALL 95 disease files
- Sgarbossa (2.7.66), STEMI equivalents (2.7.67), ST elevation differential (2.7.85)
- Cross-condition interaction files
