# YouOwnECG — Systematic Validation Framework

**Purpose:** Produce publication-grade CSV results measuring the accuracy of every pipeline stage against PTB-XL ground truth.

---

## 1. Overview

The validation framework runs the full YouOwnECG pipeline on PTB-XL records and compares outputs at four levels:

| Level | What we measure | Ground truth source | Output CSV |
|-------|----------------|--------------------|-----------|
| **A. Fiducial Detection** | Per-lead, per-beat fiducial point positions (PON, PPEAK, POFF, QRSON, R, S, QRSOFF, TON, TPEAK, TOFF) | PTB-XL `fiducial_points/ecgdeli/` .atr annotation files | `results/fiducial_accuracy.csv` |
| **B. Interval & Measurement** | PR, QRS, QT, QTc, heart rate, R/S/T amplitudes, ST elevation, axis | PTB-XL `features/ecgdeli_features.csv` (532 columns) + `ptbxl_database.csv` (heart_axis) | `results/measurement_accuracy.csv` |
| **C. Disease Detection** | Per-condition sensitivity, specificity, PPV, NPV, F1 | PTB-XL `scp_codes` with likelihood >= 50% | `results/disease_detection.csv` + `results/disease_summary.csv` |
| **D. Pipeline Timing** | Per-stage latency (ingest, preprocess, quality, fiducials, features, findings) | Wall-clock timing | `results/pipeline_timing.csv` |

---

## 2. PTB-XL Ground Truth

### 2.1 Dataset
- **Location:** `/Users/amirsadjadtaleban/Documents/PTBXL/ptb-xl-a-comprehensive-electrocardiographic-feature-dataset-1.0.1`
- **Records:** 21,837 twelve-lead ECGs (10 s, 500 Hz)
- **Diagnostic codes:** 71 SCP-ECG codes across 5 categories (NORM, MI, STTC, CD, HYP)
- **Fiducial ground truth:** Per-lead WFDB .atr annotation files from the original ecgdeli MATLAB toolbox

### 2.2 Fiducial Annotation Format
Each record has 12 lead-specific annotation files + 1 global file:
```
fiducial_points/ecgdeli/00000/00001_points_lead_II.atr
```
Annotations are WFDB format with `aux_note` labels:
```
"p-wave onset", "p-wave peak", "p-wave offset",
"QRS onset", "Q peak", "R peak", "S peak", "QRS offset",
"L point (for STEMI)", "t-wave onset", "t-wave peak", "t-wave offset"
```
12 fiducials per beat, repeating for each detected beat.

### 2.3 Feature Ground Truth
```
features/ecgdeli_features.csv   — 532 columns, 21,799 records
```
Columns per lead (12 leads + Global):
- `PQ_Int_{lead}` / `PR_Int_{lead}` — PQ and PR interval (ms)
- `QRS_Dur_{lead}` / `QRS_Dur_Global` — QRS duration (ms)
- `QT_Int_{lead}` / `QT_IntCorr_{lead}` — QT and QTc (ms)
- `R_Amp_{lead}` / `S_Amp_{lead}` / `Q_Amp_{lead}` — Amplitudes (mV)
- `P_Amp_{lead}` / `T_Amp_{lead}` — P and T amplitudes (mV)
- `ST_Elev_{lead}` — ST elevation (mV)
- `RR_Mean_Global` — Mean RR interval (ms)

### 2.4 Diagnostic Labels
```
ptbxl_database.csv → scp_codes column (JSON dict: code → likelihood 0-100%)
```
Only codes with **likelihood >= 50%** are treated as positive labels.

### 2.5 SCP Code → YouOwnECG Finding Mapping

| SCP Code | Description | YouOwnECG finding_type | Category |
|----------|-------------|----------------------|----------|
| NORM | Normal ECG | _(absence of findings)_ | Normal |
| SR | Sinus rhythm | _(rhythm="sinus")_ | Rhythm |
| SBRAD | Sinus bradycardia | sinus_bradycardia | Rhythm |
| STACH | Sinus tachycardia | sinus_tachycardia | Rhythm |
| AFIB | Atrial fibrillation | afib | Rhythm |
| AFLT | Atrial flutter | aflutter | Rhythm |
| SARRH | Sinus arrhythmia | _(not a finding)_ | Rhythm |
| SVTAC | Supraventricular tachycardia | svt | Rhythm |
| PSVT | Paroxysmal SVT | svt | Rhythm |
| PAC | Premature atrial complex | _(beat-level, not finding)_ | Rhythm |
| PVC | Premature ventricular complex | _(beat-level, not finding)_ | Rhythm |
| BIGU | Bigeminy | bigeminy | Rhythm |
| TRIGU | Trigeminy | trigeminy | Rhythm |
| 1AVB | First degree AV block | first_degree_avb | Conduction |
| 2AVB | Second degree AV block | second_degree_avb | Conduction |
| 3AVB | Complete AV block | complete_avb | Conduction |
| CLBBB | Complete LBBB | lbbb | Conduction |
| ILBBB | Incomplete LBBB | _(not detected at QRS < 120)_ | Conduction |
| CRBBB | Complete RBBB | rbbb | Conduction |
| IRBBB | Incomplete RBBB | _(not detected at QRS < 120)_ | Conduction |
| LAFB | Left anterior fascicular block | lafb | Conduction |
| LPFB | Left posterior fascicular block | lpfb | Conduction |
| IVCD | Non-specific IVCD | _(not mapped)_ | Conduction |
| WPW | Wolff-Parkinson-White | wpw_pattern | Conduction |
| PACE | Pacemaker | _(not detected)_ | Conduction |
| LVH | Left ventricular hypertrophy | lvh | Hypertrophy |
| RVH | Right ventricular hypertrophy | rvh | Hypertrophy |
| SEHYP | Septal hypertrophy | _(not mapped)_ | Hypertrophy |
| LAO/LAE | Left atrial enlargement | lae | Hypertrophy |
| RAO/RAE | Right atrial enlargement | rae | Hypertrophy |
| HVOLT | High voltage | _(not a finding)_ | Hypertrophy |
| LVOLT | Low voltage | low_voltage | Hypertrophy |
| AMI | Anterior MI | anterior_stemi | MI |
| ASMI | Anteroseptal MI | anterior_stemi | MI |
| ALMI | Anterolateral MI | lateral_stemi | MI |
| IMI | Inferior MI | inferior_stemi | MI |
| ILMI | Inferolateral MI | inferior_stemi | MI |
| IPLMI | Inferoposterolateral MI | inferior_stemi | MI |
| IPMI | Inferoposterior MI | inferior_stemi | MI |
| LMI | Lateral MI | lateral_stemi | MI |
| PMI | Posterior MI | _(not mapped)_ | MI |
| INJAL | Subendocardial injury anterolateral | possible_stemi | MI |
| INJAS | Subendocardial injury anteroseptal | possible_stemi | MI |
| INJIL | Subendocardial injury inferolateral | possible_stemi | MI |
| INJIN | Subendocardial injury inferior | possible_stemi | MI |
| INJLA | Subendocardial injury lateral | possible_stemi | MI |
| ISC_ | Non-specific ischemic | _(not mapped — too vague)_ | STTC |
| ISCAN | Ischemic anterior | _(ST changes — may trigger)_ | STTC |
| ISCAS | Ischemic anteroseptal | _(ST changes — may trigger)_ | STTC |
| ISCAL | Ischemic anterolateral | _(ST changes — may trigger)_ | STTC |
| ISCIL | Ischemic inferolateral | _(ST changes — may trigger)_ | STTC |
| ISCIN | Ischemic inferior | _(ST changes — may trigger)_ | STTC |
| ISCLA | Ischemic lateral | _(ST changes — may trigger)_ | STTC |
| NDT | Non-diagnostic T abnormalities | _(not mapped)_ | STTC |
| NST_ | Non-specific ST changes | _(not mapped)_ | STTC |
| LNGQT | Long QT interval | long_qt | STTC |
| INVT | T-wave inversion | _(morphology, not finding)_ | STTC |
| LOWT | Low T-wave amplitude | _(morphology, not finding)_ | STTC |
| NT_ | Non-specific T changes | _(not mapped)_ | STTC |
| STD_ | ST depression | _(morphology, not finding)_ | STTC |
| STE_ | ST elevation | _(triggers STEMI detectors)_ | STTC |
| DIG | Digitalis effect | _(not detected)_ | STTC |
| ANEUR | Aneurysm | _(not detected)_ | STTC |
| EL | Electrolyte imbalance | _(not detected)_ | STTC |
| QWAVE | Pathological Q wave | _(morphology, not finding)_ | STTC |
| TAB_ | T-wave abnormality | _(not mapped)_ | STTC |
| PRC(S) | Pericarditis | pericarditis | STTC |

---

## 3. Validation Modules

### 3.1 Module A: Fiducial Detection Accuracy (`validate_fiducials.py`)

**What it does:**
1. For each PTB-XL record, load the ground-truth .atr annotations
2. Run our pipeline: `preprocess() → quality() → detect_fiducials()`
3. Match each ground-truth fiducial to the nearest predicted fiducial (within ±50ms tolerance)
4. Compute per-fiducial-type errors

**Output: `results/fiducial_accuracy.csv`**

| Column | Description |
|--------|-------------|
| ecg_id | PTB-XL record ID |
| lead | Lead name |
| beat_idx | Beat number (0-based) |
| fiducial | Fiducial type (pon, ppeak, poff, qrson, r, s, qrsoff, ton, tpeak, toff) |
| gt_sample | Ground truth sample position |
| pred_sample | Our predicted sample position (null if not detected) |
| error_ms | Signed error in ms (pred - gt) |
| abs_error_ms | Absolute error in ms |
| detected | Boolean — did we detect this fiducial? |

**Summary statistics (computed in analysis notebook):**
- Per-fiducial MAE, RMSE, median error
- Detection rate per fiducial type
- Per-lead breakdown
- Error distribution histograms

### 3.2 Module B: Interval & Measurement Accuracy (`validate_measurements.py`)

**What it does:**
1. For each record, load PTB-XL `ecgdeli_features.csv` ground truth values
2. Run our pipeline to get `FeatureObject`
3. Compare: PR, QRS, QT, QTc, R/S/Q/P/T amplitudes, ST elevation, RR interval

**Output: `results/measurement_accuracy.csv`**

| Column | Description |
|--------|-------------|
| ecg_id | PTB-XL record ID |
| measurement | Measurement name (pr_ms, qrs_ms, qt_ms, qtc_ms, r_amp_V1, st_elev_V2, ...) |
| lead | Lead name (or "global") |
| gt_value | Ground truth value from ecgdeli_features.csv |
| pred_value | Our computed value |
| error | Signed error (pred - gt) |
| abs_error | Absolute error |
| pct_error | Percentage error |

**Key comparisons:**

| Our feature | PTB-XL ground truth column | Unit |
|------------|---------------------------|------|
| `pr_interval_ms` | `PR_Int_Global` | ms |
| `qrs_duration_global_ms` | `QRS_Dur_Global` | ms |
| `qt_interval_ms` | `QT_Int_Global` | ms |
| `qtc_bazett_ms` | `QT_IntCorr_Global` (approx) | ms |
| `heart_rate_ventricular_bpm` | `60000 / RR_Mean_Global` | bpm |
| `r_amplitude_mv[lead]` | `R_Amp_{lead}` | mV |
| `s_amplitude_mv[lead]` | `S_Amp_{lead}` | mV |
| `t_amplitude_mv[lead]` | `T_Amp_{lead}` | mV |
| `st_elevation_mv[lead]` | `ST_Elev_{lead}` | mV |
| `qrs_axis_deg` | `heart_axis` (ptbxl_database.csv) | degrees |

### 3.3 Module C: Disease Detection Accuracy (`validate_diseases.py`)

**What it does:**
1. For each record, map PTB-XL `scp_codes` to our `finding_type` names (using Section 2.5 mapping)
2. Run our pipeline + `generate_signal_findings()`
3. Compute TP/FP/TN/FN per condition

**Output: `results/disease_detection.csv`** (per-record)

| Column | Description |
|--------|-------------|
| ecg_id | PTB-XL record ID |
| condition | Our finding_type |
| scp_codes | PTB-XL SCP codes on this record |
| gt_positive | Boolean — PTB-XL says this condition is present |
| pred_positive | Boolean — our pipeline detected this condition |
| pred_confidence | Our confidence level (HIGH/MODERATE/LOW/INSUFFICIENT) |
| true_positive | gt=True, pred=True |
| false_positive | gt=False, pred=True |
| false_negative | gt=True, pred=False |
| true_negative | gt=False, pred=False |

**Output: `results/disease_summary.csv`** (per-condition aggregate)

| Column | Description |
|--------|-------------|
| condition | Our finding_type |
| n_gt_positive | Total records with this condition in PTB-XL |
| n_pred_positive | Total records where we detected it |
| TP | True positives |
| FP | False positives |
| FN | False negatives |
| TN | True negatives |
| sensitivity | TP / (TP + FN) |
| specificity | TN / (TN + FP) |
| PPV | TP / (TP + FP) |
| NPV | TN / (TN + FN) |
| F1 | 2 * (PPV * sensitivity) / (PPV + sensitivity) |
| accuracy | (TP + TN) / total |

**Conditions evaluated:**

| Condition | PTB-XL code(s) | Expected N (>= 50%) |
|-----------|----------------|---------------------|
| lbbb | CLBBB | 536 |
| rbbb | CRBBB | 541 |
| first_degree_avb | 1AVB | 794 |
| lafb | LAFB | 1,625 |
| wpw_pattern | WPW | ~30 |
| afib | AFIB | ~150 |
| lvh | LVH | 1,756 |
| anterior_stemi | AMI, ASMI | ~2,200 |
| inferior_stemi | IMI, ILMI, IPLMI, IPMI | ~2,200 |
| lateral_stemi | ALMI, LMI | ~370 |
| long_qt | LNGQT | 117 |
| pericarditis | PRC(S) | ~10 |
| low_voltage | LVOLT | ~200 |

### 3.4 Module D: Pipeline Timing (`validate_timing.py`)

**Output: `results/pipeline_timing.csv`**

| Column | Description |
|--------|-------------|
| ecg_id | PTB-XL record ID |
| stage | Pipeline stage name |
| latency_ms | Wall-clock time in milliseconds |

Stages: `ingest`, `preprocess`, `quality`, `fiducials`, `features`, `signal_findings`, `total`

---

## 4. How to Run

### Full validation (all modules, all available records)
```bash
cd ~/Documents/YouOwnECG
python -m validation.run --all --output-dir validation/results
```

### Individual modules
```bash
python -m validation.run --fiducials --n-records 500
python -m validation.run --measurements --n-records 500
python -m validation.run --diseases --n-records 0    # 0 = all records
python -m validation.run --timing --n-records 100
```

### Quick smoke test (10 records)
```bash
python -m validation.run --all --n-records 10
```

### Options
| Flag | Description |
|------|-------------|
| `--all` | Run all 4 modules |
| `--fiducials` | Module A only |
| `--measurements` | Module B only |
| `--diseases` | Module C only |
| `--timing` | Module D only |
| `--n-records N` | Limit to first N records (0 = all, default 0) |
| `--output-dir DIR` | Output directory (default: `validation/results`) |
| `--ptbxl-dir DIR` | PTB-XL dataset path (auto-detected) |
| `--strat-fold N` | Run only on PTB-XL stratification fold N (1-10) |
| `--skip-existing` | Skip records already in output CSVs (resume support) |

---

## 5. Output Structure

```
validation/
├── README.md                    ← this file
├── run.py                       ← CLI entry point
├── validate_fiducials.py        ← Module A
├── validate_measurements.py     ← Module B
├── validate_diseases.py         ← Module C
├── validate_timing.py           ← Module D
├── ptbxl_mapping.py             ← SCP code → finding_type mapping
├── results/                     ← gitignored output
│   ├── fiducial_accuracy.csv
│   ├── measurement_accuracy.csv
│   ├── disease_detection.csv
│   ├── disease_summary.csv
│   └── pipeline_timing.csv
└── analysis/                    ← Jupyter notebooks for paper figures
    ├── fiducial_plots.ipynb
    ├── measurement_bland_altman.ipynb
    ├── disease_roc_curves.ipynb
    └── timing_distribution.ipynb
```

---

## 6. Known Limitations

### PTB-XL ground truth caveats
1. **SCP codes are not always accurate** — some records have questionable labels (user confirmed). Use likelihood >= 50% as baseline; consider >= 80% for stricter analysis.
2. **MI labels include chronic/old MI** — PTB-XL `infarction_stadium1`/`infarction_stadium2` columns distinguish acute vs old, but many MI codes cover resolved infarcts with residual Q-waves (no active ST elevation). This will cause **false negatives** for our STEMI detector on old MI records — expected and correct behavior.
3. **No labels for:** Wellens, de Winter, Brugada, hyperkalemia, electrical alternans, epsilon waves. These conditions cannot be validated against PTB-XL.
4. **Fiducial ground truth is from ecgdeli MATLAB** — our Python port may differ slightly from the MATLAB original. Differences here measure our port fidelity, not clinical accuracy.
5. **Incomplete LBBB/RBBB (ILBBB/IRBBB)** — our detector requires QRS >= 120ms; incomplete BBB has QRS 100-120ms and will correctly be missed.

### Our pipeline caveats
1. **QRS duration** may be extended by ecgdeli detecting onset/offset differently in the safe window vs full record. Known issue from session debugging.
2. **LBBB detection criteria** (R in V5 + S in V1) are intentionally simple — may over-detect on some wide QRS patterns. WPW suppression helps.
3. **STEMI detection** is suppressed when LBBB/RBBB is present — this correctly avoids false positives from expected discordant ST changes, but may miss true STEMI+LBBB (Sgarbossa criteria not yet in signal-only mode).

---

## 7. Paper-Ready Metrics

The validation CSVs are designed to directly produce these tables/figures:

### Table 1: Fiducial Detection Accuracy
| Fiducial | MAE (ms) | RMSE (ms) | Detection Rate | N beats |
|----------|----------|-----------|----------------|---------|
| P onset | | | | |
| P peak | | | | |
| QRS onset | | | | |
| R peak | | | | |
| ... | | | | |

### Table 2: Interval Measurement Accuracy
| Interval | MAE | RMSE | Pearson r | Bland-Altman bias | 95% LoA |
|----------|-----|------|-----------|-------------------|---------|
| PR (ms) | | | | | |
| QRS (ms) | | | | | |
| QT (ms) | | | | | |
| QTc (ms) | | | | | |
| HR (bpm) | | | | | |

### Table 3: Disease Detection Performance
| Condition | N | Sens | Spec | PPV | NPV | F1 | Accuracy |
|-----------|---|------|------|-----|-----|----|----------|
| LBBB | 536 | | | | | | |
| RBBB | 541 | | | | | | |
| 1st AVB | 794 | | | | | | |
| ... | | | | | | | |

### Figure 1: Bland-Altman plots for PR, QRS, QT, QTc
### Figure 2: ROC curves per condition
### Figure 3: Fiducial error distribution histograms
### Figure 4: Pipeline latency box plots per stage

---

## 8. Reproducibility

- **Random seed:** None needed — validation is deterministic (same input → same output)
- **PTB-XL version:** ptb-xl-a-comprehensive-electrocardiographic-feature-dataset-1.0.1
- **Pipeline version:** Recorded in each CSV row from `FeatureObject.ecg_id`
- **Hardware:** Apple Silicon (M-series), Python 3.9.6
- **Stratification:** Use `strat_fold` column from ptbxl_database.csv for train/test split consistency with other benchmarks
