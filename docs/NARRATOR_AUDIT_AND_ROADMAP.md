# ECG Narrator Audit & Enhancement Roadmap

## The Core Problem

The narrator describes what it **measures** (amplitudes, durations, intervals) but not what a cardiologist **sees** (patterns, shapes, relationships). Disease diagnosis requires pattern recognition that our narrator doesn't yet provide.

## Critical Gaps by Disease

### TIER 1 — Life-Threatening Misses

| Disease | What's Missing | Why It's Critical |
|---------|---------------|-------------------|
| **LBBB vs RBBB** | QRS polarity pattern (QS/rS vs RSR'), concordance/discordance analysis | System calls LBBB as RBBB; can't apply Sgarbossa for STEMI |
| **Sgarbossa (LBBB+STEMI)** | Concordant vs discordant ST per lead, ST/S ratio | Misses 50% of STEMI in LBBB |
| **Brugada Type 1** | Coved vs saddle-back ST morphology, continuous ST-T curve | Can't distinguish Type 1 (lethal) from Type 2 (benign alone) |
| **Complete AVB** | AV dissociation (independent P and QRS), P-P vs R-R comparison | Calls it "bradycardia" instead of "imminent asystole risk" |
| **Pre-excited AFib** | Delta waves + irregular rhythm + shortest RR interval | VF risk if missed; contraindicated drugs given |
| **De Winter** | Upsloping ST depression + tall symmetric T + aVR elevation as a pattern | STEMI-equivalent missed because no ST elevation |

### TIER 2 — High-Consequence Misses

| Disease | What's Missing | Why It's Critical |
|---------|---------------|-------------------|
| **Wellens** | Symmetric vs asymmetric T inversion, biphasic T detection | Can't distinguish from LVH strain; 75% progress to MI |
| **Pericarditis vs STEMI** | Concave vs convex ST, PR depression, diffuse vs territorial | 50% false positive rate for STEMI without these |
| **Long QT subtypes** | Notched/bifid T (LQT2), long isoelectric ST (LQT3), T-wave alternans | Can't subtype or detect imminent TdP |

### TIER 3 — Accuracy Improvers

| Disease | What's Missing |
|---------|---------------|
| **AFib** | Fibrillatory baseline (f-wave) characterization |
| **RVH** | Explicit axis computation, strain pattern naming |
| **LAE** | Morris criterion (PTF calculation), notch characterization |
| **Inferior STEMI** | III vs II magnitude (RCA vs LCx), RV involvement |
| **WPW** | Delta wave polarity for pathway localization |

---

## What the Narrator Currently Describes Well

- P-wave: presence, amplitude, duration, polarity
- PR interval: measurement with normal/prolonged annotation
- QRS: width, R/S amplitudes per lead
- ST segment: elevation/depression in mV, morphology (up/down/horizontal)
- T-wave: amplitude, direction (upright/inverted/flat)
- T/QRS ratio: hyperacute T flagging
- RR intervals: per-beat, mean, SD, CV
- Cross-lead: territorial ST comparison (LAD/RCA/LCx)
- LVH criteria: voltage criteria met list

---

## Enhancement Plan

### Phase 1: QRS Pattern Recognition (fixes LBBB/RBBB/Sgarbossa)

Add to narrator per beat per lead:
1. **QRS net polarity** — "predominantly positive" vs "predominantly negative" (signed area)
2. **QRS morphology pattern** — "QS" / "rS" / "Rs" / "RSR'" / "qRs" / "delta+wide"
3. **Concordance flag** — "ST is CONCORDANT with QRS" vs "ST is DISCORDANT" (expected in BBB)
4. **S-wave depth** — explicit measurement for Sgarbossa Smith ratio (ST/S ≤ -0.25)

### Phase 2: ST Morphology Enhancement (fixes Pericarditis/Brugada/De Winter)

Add to narrator:
1. **ST curvature** — "concave up (smiley)" vs "convex (frowning)" vs "coved (dome→descent→T-inv)"
2. **PR segment depression** — measure PR-to-baseline difference (pericarditis marker)
3. **ST-T continuity** — "ST merges into T without isoelectric segment" (Brugada Type 1)
4. **Diffuse vs territorial pattern** — count how many territories have ST elevation

### Phase 3: T-Wave Morphology (fixes Wellens/Long QT)

Add to narrator:
1. **T-wave symmetry** — "symmetric" vs "asymmetric" (compute ascending vs descending limb ratio)
2. **Biphasic T detection** — "initial positive + terminal negative" (Wellens Type A)
3. **Notched T detection** — "two-humped T-wave" (LQT2)
4. **T-wave alternans** — beat-to-beat T amplitude variation

### Phase 4: AV Relationship (fixes Complete AVB/Wenckebach)

Add to narrator:
1. **P-to-QRS relationship** — "1:1 fixed PR" vs "varying PR" vs "independent P and QRS"
2. **P-P regularity** — separate from R-R (sinus P-P should be constant in AVB)
3. **Progressive PR** — detect Wenckebach pattern (increasing PR → dropped QRS)
4. **Escape rhythm type** — "junctional (narrow, 40-60)" vs "ventricular (wide, 20-40)"

### Phase 5: Safety Patterns

Add to narrator:
1. **Pre-excited AFib flag** — delta waves + irregular + fast = DANGER
2. **Shortest RR in irregular rhythm** — for pre-excited AFib risk
3. **De Winter triad** — upsloping depression + tall T + aVR elevation = STEMI-equivalent
4. **Sgarbossa score** — compute when LBBB is detected

---

## Token Budget Impact

Current narrator: ~300-450 tokens per record (3-4 beats × 3 leads)

With all enhancements: estimated ~600-800 tokens per record
- Phase 1 adds ~50 tokens (QRS pattern + concordance per beat)
- Phase 2 adds ~40 tokens (ST curvature + PR depression)
- Phase 3 adds ~30 tokens (T symmetry + biphasic)
- Phase 4 adds ~40 tokens (AV relationship analysis)
- Phase 5 adds ~30 tokens (safety pattern flags)

This is within the ~1000 token budget for agent context.
