# Cardiac Axes: P, QRS, T — Normal Ranges by Age/Sex — ECG Reference

**Node:** 2.7.202
**SDA:** SDA-2 (Diagnosis & Agentic Core) — shared resource for SDA-1, SDA-3, SDA-4
**Status:** Research Complete
**PGMR:** Required
**Date:** 2026-03-27

---

## Purpose

This reference consolidates all axis-related knowledge needed for ECG interpretation: P-wave axis, QRS axis, and T-wave axis across the frontal and horizontal planes. It serves as the authoritative source consumed by any downstream disease node that requires axis determination — including LAFB (2.7.51), LPFB (2.7.52), RVH (2.7.53), WPW (2.7.58), PE (2.7.60), and the general QRS axis evaluation step embedded in nearly every diagnosis chain. The axis calculation methods documented here are the computational methods used by the SDA-1 feature extraction pipeline.

---

## 1. The Hexaxial Reference System (Frontal Plane)

The six limb leads are arranged at 30° intervals around the frontal plane, forming the **hexaxial reference system**. All frontal-plane axis values are expressed in degrees measured clockwise from Lead I (0°), with counterclockwise values expressed as negative.

| Lead | Axis Angle | Direction |
|------|-----------|-----------|
| I | 0° | Leftward (horizontal) |
| II | +60° | Left-inferior |
| III | +120° | Right-inferior |
| aVR | −150° | Right-superior |
| aVL | −30° | Left-superior |
| aVF | +90° | Directly inferior |

**Key principle:** A vector parallel to a lead axis produces maximum deflection in that lead. A vector perpendicular to a lead axis produces an isoelectric deflection — this is the basis of the isoelectric method for axis calculation.

---

## 2. QRS Axis

### 2.1 Normal Ranges by Age

| Age Group | Normal QRS Axis | Notes |
|-----------|----------------|-------|
| Neonates (0–1 month) | +90° to +180° | Right-dominant ventricle at birth; RAD is physiologic |
| Infants (1–12 months) | +30° to +180° | Gradual shift leftward as LV grows |
| Children (1–8 years) | +10° to +120° | Wider range than adults; mild RAD still normal |
| Adolescents (8–16 years) | −15° to +110° | Approaching adult norms |
| Adults | −30° to +90° | Standard adult normal range |
| Elderly (>65 years) | −30° to +90° | Same range; mild LAD more common with age and LVH |

### 2.2 QRS Axis Deviation Definitions

| Classification | Axis Range | Clinical Significance |
|---------------|-----------|----------------------|
| Normal | −30° to +90° | No pathological axis deviation |
| Left Axis Deviation (LAD) | −30° to −90° | LAFB, inferior MI, LBBB, congenital heart disease |
| Extreme LAD (required for LAFB) | −45° to −90° | Required criterion for left anterior fascicular block |
| Right Axis Deviation (RAD) | +90° to +180° | RVH, LPFB, PE, lateral MI, normal in children |
| Extreme (northwest) Axis | ±180° to −90° (>+180° or <−90°) | Ventricular tachycardia, severe LPFB, lead reversal, hyperkalemia |

**Note on LAFB threshold:** Some guidelines require ≤−45° (not just ≤−30°) for a confident LAFB diagnosis to avoid overcalling LAD from inferior MI or normal variation. Node 2.7.51 specifies −45° as the required threshold.

### 2.3 Sex-Based Considerations

Adult women have a slightly more leftward mean QRS axis than adult men (mean ~+50° vs ~+60° in large population studies). This does not change the clinical cutoffs but means that a woman at −25° is closer to pathological LAD than a man at −25°. The YouOwnECG agent should flag axes between −20° and −30° as "borderline LAD — correlate clinically" rather than normal or abnormal.

### 2.4 QRS Axis Calculation Methods

**Method 1 — Lead I + aVF Quadrant Screen (fastest, least precise)**

| Lead I | aVF | Quadrant |
|--------|-----|---------|
| Positive | Positive | Normal (0° to +90°) |
| Negative | Positive | RAD (+90° to +180°) |
| Positive | Negative | LAD (−30° to −90°); confirm with Lead II |
| Negative | Negative | Extreme/northwest axis |

If Lead I is positive and aVF is negative: check Lead II. If Lead II is positive → axis is 0° to −30° (normal or borderline). If Lead II is negative → axis is ≤−30° (true LAD).

**Method 2 — Isoelectric Lead Method (most accurate, used for precise axis)**

1. Find the limb lead with the most isoelectric QRS (net deflection closest to zero — positive and negative deflections are equal).
2. The axis is perpendicular to that lead. There are two perpendicular directions — choose the one toward which the majority of the QRS deflection is positive in the adjacent leads.
3. Example: If aVL (−30°) is isoelectric, the axis is either +60° or −120°. If Lead II (+60°) is predominantly positive, the axis is +60°.

**Method 3 — Net Deflection Estimation (numerical, used in automated systems)**

For each limb lead, compute the net QRS amplitude (R amplitude minus S amplitude in mm). Map these values onto the hexaxial system to triangulate the axis. The YouOwnECG SDA-1 pipeline should compute this numerically from the measured R and S peak amplitudes.

**Automated agent instruction:** Use Method 3 as the primary computation. Use Method 1 as a sanity check. Report axis to the nearest 15° for clinical decision-making — false precision beyond this is not warranted given measurement variability.

---

## 3. P-Wave Axis

### 3.1 Normal P-Wave Axis

| Parameter | Normal Value | Notes |
|-----------|-------------|-------|
| Normal range | 0° to +75° | Typically approximately +60° |
| Typical sinus origin | ~+60° | Reflects superior-to-inferior, right-to-left atrial depolarization |
| Sinus confirmation | Negative P in aVR | If P is negative in aVR (pointing away from −150°), origin is upper right atrium — sinus node |
| Abnormal range | <0° or >90° | Suggests ectopic atrial pacemaker |

### 3.2 Abnormal P-Wave Axis Patterns

| Axis | Interpretation |
|------|---------------|
| Negative in Lead II (axis <−30°) | Retrograde atrial activation — junctional rhythm, ectopic low atrial pacemaker, retrograde conduction in SVT |
| Inverted in I and aVL (axis >+90°) | Right atrial ectopic pacemaker, dextrocardia, limb lead reversal |
| Positive in aVR | Ectopic atrial pacemaker (most sinus P waves are negative in aVR) |
| Markedly superior (<−45°) | Low atrial or coronary sinus rhythm |
| Variable axis, beat to beat | Multifocal atrial tachycardia — multiple ectopic foci, changing axis per beat |

### 3.3 Clinical Use of P-Wave Axis

- **Sinus rhythm confirmation:** P-wave axis of 0° to +75° + negative P in aVR = high confidence sinus origin.
- **Junctional rhythm detection:** If P waves are present but inverted in II, III, aVF (retrograde), the origin is junctional or low atrial.
- **MAT vs AFib:** MAT has clearly distinct P waves with at least 3 different morphologies and varying P-P axis. AFib has no discrete P waves.

---

## 4. T-Wave Axis

### 4.1 Normal T-Wave Axis

| Parameter | Value |
|-----------|-------|
| Normal T-wave axis | Approximately +45° to +60° (near the QRS axis) |
| QRS-T angle (normal) | ≤45° |
| QRS-T angle (abnormal) | >45° — indicates repolarization abnormality |
| QRS-T angle (markedly abnormal) | >90° — indicates significant repolarization abnormality (strain, ischemia, LVH with strain) |

### 4.2 T-Wave/QRS Axis Concordance Rule

The T-wave axis should be **within 45° of the QRS axis** in both the frontal and horizontal planes. Significant T-QRS discordance indicates abnormal repolarization regardless of whether T waves appear overtly inverted in any single lead.

**Why this matters for the agent:** A patient can have "normal" T waves in each individual lead (all upright, none obviously inverted) yet still have a pathological T-QRS angle if the QRS axis is itself abnormal. The agent must compute the angle, not just scan leads individually.

### 4.3 T-Wave Axis in Specific Conditions

| Condition | T-Wave Axis Pattern |
|-----------|-------------------|
| Normal | Concordant with QRS, typically +45° to +75° |
| LVH with strain | T-axis shifted opposite to QRS axis in lateral leads (discordant in V5/V6, I, aVL) |
| LBBB | T-wave always discordant (opposite to QRS) — this is expected and does NOT indicate additional ischemia |
| RBBB | T-wave discordant in V1-V2 (expected); discordance in V4-V6 is abnormal |
| Anterior ischemia | T-axis shifts posteriorly — deep T inversions in V1-V4 |
| Inferior ischemia | T-axis shifts superiorly — T inversions in II, III, aVF |
| PE (S1Q3T3 pattern) | Rightward T-axis shift with T inversions in V1-V4 and III |

---

## 5. Horizontal Plane Axis (Precordial Leads)

### 5.1 Normal R-Wave Progression (Horizontal Axis)

The horizontal plane electrical axis rotates from approximately +120° (rightward-anterior) at V1 to 0° (leftward) at V6. The **transition zone** is where R and S amplitudes are equal (R/S = 1), normally occurring at V3 or V4.

| Lead | Normal R/S Pattern | Interpretation |
|------|--------------------|---------------|
| V1 | Small r, large S (rS pattern) | Septal depolarization moving leftward away from V1 |
| V2 | Slightly larger r, still S dominant | Transition beginning |
| V3 | r and S approximately equal | Normal transition zone |
| V4 | R dominant (R/S >1) | Lateral LV forces now dominant |
| V5 | Tall R, small S | Peak R-wave amplitude |
| V6 | Tall R, minimal S | Lateral wall; slight decrease from V5 due to increased distance |

### 5.2 Abnormal Horizontal Plane Rotation

| Pattern | Axis Shift | Causes |
|---------|-----------|--------|
| Clockwise rotation (late transition — R/S transition at V5 or V6) | Rightward horizontal axis | COPD, RVH, posterior MI, normal variant |
| Counterclockwise rotation (early transition — R/S at V1 or V2) | Leftward horizontal axis | LVH, posterior MI presenting as tall R in V1, WPW (Type A) |
| No transition (persistent S dominance to V6) | Far rightward horizontal axis | Severe RVH, LBBB (reversed septal activation), PRWP from anterior MI |

---

## 6. Age/Sex Normal Ranges — Summary Table

| Group | P-Wave Axis | QRS Axis | T-Wave Axis (frontal) |
|-------|------------|---------|----------------------|
| Neonates | +30° to +90° | +90° to +180° | +90° to +180° (mirrors QRS) |
| Infants | +30° to +90° | +30° to +180° | Concordant with QRS ±45° |
| Children 1–8 | +30° to +75° | +10° to +120° | Concordant with QRS ±45° |
| Adolescents | +30° to +75° | −15° to +110° | Concordant with QRS ±45° |
| Adult men | +30° to +75° | −30° to +90° (mean ~+60°) | +15° to +75° |
| Adult women | +30° to +75° | −30° to +90° (mean ~+50°) | +15° to +75° |
| Elderly >65 | +30° to +75° | −30° to +90° | +15° to +75° (may shift leftward) |

---

## 7. Clinical Application

**How agents use this reference in reasoning chains:**

1. **LAFB detection (Node 2.7.51):** Compute QRS axis from limb leads. If axis ≤−45°, this is a required criterion. Agent then checks for additional LAFB criteria (small q in I/aVL, small r in II/III/aVF, QRS <120 ms).

2. **LPFB detection (Node 2.7.52):** If QRS axis ≥+90° (RAD), after exclusion of RVH and PE, LPFB is considered. Agent must rule out RAD from other causes first.

3. **RVH detection (Node 2.7.53):** RAD ≥+90° is one of several criteria. Agent combines with voltage criteria from Node 2.7.204.

4. **PE (S1Q3T3):** Acute rightward axis shift + T inversions in V1-V4 + S in I, Q and T inversion in III. The axis calculation confirms the rightward shift.

5. **WPW pathway localization:** The delta wave axis (which is the initial QRS vector from ventricular pre-excitation) approximates the location of the accessory pathway. A delta wave axis of −60° to −90° suggests a left lateral pathway; +60° to +90° suggests a posterior septal pathway.

6. **Sinus rhythm confirmation:** Every rhythm analysis begins with P-wave axis check. P-axis 0° to +75° + negative P in aVR = sinus rhythm.

7. **Lead reversal detection:** Right arm/left arm reversal produces: negative P and QRS in Lead I, positive aVR, and apparent extreme axis — these flag a technical artifact rather than pathology.

---

## 8. Common Errors / Pitfalls

**1. Using Lead I + aVF quadrant method as final axis determination**
This only gets to ±90° accuracy. The isoelectric lead method or numerical computation must be used for precise axis values, especially for LAFB (requires ≤−45°, not just "LAD present").

**2. Ignoring the −30° vs −45° LAFB threshold**
Axis of −35° qualifies as LAD but should NOT be called LAFB without additional criteria. The threshold for LAFB is −45°.

**3. Applying adult axis norms to children**
A QRS axis of +120° is normal in a 3-year-old and abnormal in a 40-year-old. Age-specific tables must be applied.

**4. Treating T-wave concordance as binary (inverted vs upright) per lead**
T-QRS angle must be computed as an angle, not just checking if T waves are upright. An upright T wave at +120° with a QRS axis at +30° represents a 90° T-QRS angle — abnormal despite no T inversions.

**5. Computing axis from precordial leads**
Precordial leads are in the horizontal plane, not the frontal plane. QRS axis (by convention, and as used in all clinical criteria) refers to the **frontal plane axis** computed from limb leads. Horizontal plane rotation is a separate concept.

**6. LBBB and T-wave discordance**
In LBBB, T-wave discordance (T opposite to QRS terminal force) is expected and normal. Do NOT flag LBBB T-wave discordance as a repolarization abnormality — it is a primary consequence of the conduction defect.

**7. Neonatal axis misread as pathological RAD**
Neonates have physiological RV dominance. An axis of +150° in a neonate is normal. The same axis in an adult is extreme RAD requiring immediate investigation.

---

## 6A. Agent Assignment

**Architecture:** Option E — 3 Parallel Phase 1 Specialists + 1 Sequential CDS (Node 2.1 Gate Passed 2026-03-27)

| Agent | Role for ECG Axes Reference | Key Features Used |
|-------|--------------------------|-------------------|
| **RRC** (Rhythm/Rate/Conduction) | Primary user — queries this reference for all axis calculations | Normal axis range (-30° to +90°); LAD criteria (-30° to -90°); RAD criteria (+90° to +180°); northwest axis (-90° to ±180°); P-wave axis for sinus rhythm confirmation; QRS axis for conduction and hypertrophy assessment |
| **IT** (Ischemia/Territory) | Not a direct user of this reference | IT uses lead-anatomy reference for territory mapping; axis information is supplied by RRC if relevant |
| **MR** (Morphology/Repolarization) | Not a direct user of this reference | MR uses axis information from RRC output (e.g., right axis deviation as context for RVH, left axis for LVH/fascicular block) but does not directly query axis reference |
| **CDS** (Cross-Domain Synthesis) | Receives axis output from RRC | CDS integrates RRC axis findings with MR morphology (e.g., LAD + morphological LVH = probable LVH; RAD + RV strain pattern = RVH) for final interpretation |

### Primary Agent
**RRC** — Axis calculation and classification (QRS axis, P-wave axis, T-wave axis) are conduction and rate-related determinations within RRC's domain. RRC is the sole Phase 1 agent that queries this reference.

### Cross-Domain Hints
No cross_domain_hints are generated from this reference file. RRC generates axis-related cross_domain_hints to CDS from individual disease files (e.g., RAD in RVH file, LAD in LAFB file) based on the thresholds defined in this reference.

### CDS Specific Role
CDS receives axis findings from RRC (which has queried this reference) and integrates them with morphology findings from MR. CDS uses axis deviations in the context of the full cross-domain picture: left axis deviation combined with MR's morphological LVH criteria strengthens the LVH diagnosis; right axis deviation combined with MR's right precordial dominant R-wave and right ventricular strain pattern confirms RVH; northwest axis with wide QRS and MR's morphology characterization suggests ventricular tachycardia or hyperkalemia. CDS does not directly query this reference — it receives axis output from RRC.

---

## References

- Goldberger AL, Goldberger ZD, Shvilkin A. *Goldberger's Clinical Electrocardiography: A Simplified Approach*. 9th ed. Philadelphia: Elsevier; 2018. Chapter 4 (Electrical Axis).
- Surawicz B, Knilans TK. *Chou's Electrocardiography in Clinical Practice*. 6th ed. Philadelphia: Saunders; 2008. Chapter 2.
- Macfarlane PW, van Oosterom A, Pahlm O, et al. *Comprehensive Electrocardiology*. 2nd ed. London: Springer; 2011.
- Mason JW, Hancock EW, Gettes LS, et al. Recommendations for the standardization and interpretation of the electrocardiogram. Part II: Electrocardiography diagnostic statement list. *J Am Coll Cardiol*. 2007;49(10):1128–1135.
- Rijnbeek PR, van Herpen G, Bots ML, et al. Normal values of the electrocardiogram for ages 16–90 years. *J Electrocardiol*. 2014;47(6):914–921.
- Harrigan RA, Jones K. ABC of clinical electrocardiography: Conditions affecting the right side of the heart. *BMJ*. 2002;324(7347):1201–1204.
