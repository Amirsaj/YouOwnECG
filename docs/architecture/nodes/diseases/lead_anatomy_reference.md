# Lead Anatomy Reference — Which Lead Sees What and Why

**Node:** 2.7.201
**Status:** Research Complete
**Date:** 2026-03-26

---

## 1. Lead Theory from First Principles

### 1.1 The Cardiac Dipole

The heart generates electrical activity through sequential depolarization and repolarization of myocardial cells. At any instant during this process, a boundary exists between depolarized (negatively charged on the outside) and resting (positively charged on the outside) tissue. This boundary constitutes the **wavefront**, and it creates an electrical dipole.

**Core principles:**

- The wavefront of depolarization creates a dipole with a positive charge ahead (in the direction of propagation) and a negative charge behind (already depolarized tissue).
- The **net instantaneous cardiac vector** is the sum of all individual cellular dipoles active at that moment. It points in the direction of the dominant depolarization wavefront.
- Each ECG lead measures the **projection** of this net vector onto the lead's axis — this is Einthoven's "lead field" concept.
- If the net vector points **toward** the positive electrode of a lead, that lead records an **upward (positive) deflection**.
- If the net vector points **away** from the positive electrode, the lead records a **downward (negative) deflection**.
- If the net vector is **perpendicular** to the lead axis, the lead records an **isoelectric (flat) deflection** — this is called the transition point and is exploited in axis determination.
- The **amplitude** of the deflection is proportional to the magnitude of the vector's projection onto the lead axis: `V_lead = |D| * cos(theta)` where theta is the angle between the dipole vector and the lead axis.

**Why this matters for ECG interpretation:** A lead only "sees" the component of electrical activity that is parallel to its axis. This means the same cardiac event (e.g., a myocardial infarction) will produce different patterns in different leads depending on each lead's spatial orientation relative to the injury.

### 1.2 Lead Vectors and Angles

Each ECG lead has a defined axis in either the frontal plane (limb leads) or the horizontal/transverse plane (precordial leads). The axis is defined by the angle between the lead vector and the standard reference (Lead I direction = 0 degrees).

**Frontal Plane Lead Axes (Exact Angles):**

| Lead | Axis Angle | Direction |
|------|-----------|-----------|
| I | 0° | Leftward (horizontal) |
| II | +60° | Left-inferior |
| III | +120° | Right-inferior |
| aVR | -150° (equivalent to +210°) | Right-superior |
| aVL | -30° (equivalent to +330°) | Left-superior |
| aVF | +90° | Directly inferior |

**Horizontal Plane Lead Axes (Approximate Angles):**

The precordial leads sweep around the chest from right to left in the transverse plane. Their axes in the horizontal plane are approximately:

| Lead | Horizontal Plane Angle (from posterior, clockwise) | Approximate Direction |
|------|-----------------------------------------------------|----------------------|
| V1 | ~115° | Rightward-anterior, facing septum from front-right |
| V2 | ~105° | Anterior, facing septum from front |
| V3 | ~80° | Left-anterior, facing anterior wall |
| V4 | ~60° | Left-anterior, facing anterior wall |
| V5 | ~30° | Leftward, facing lateral wall |
| V6 | ~0° | Directly leftward, facing lateral wall |

Note: Horizontal plane angles for precordial leads are approximations because they depend on individual chest anatomy. The important concept is the progressive leftward sweep from V1 to V6.

### 1.3 The Three Planes of the Heart

The 12-lead ECG provides views in two orthogonal planes:

- **Frontal plane** (coronal): Covered by the 6 limb leads (I, II, III, aVR, aVL, aVF). Views the heart as if looking at the patient from the front. Captures superior-inferior and left-right electrical activity.
- **Horizontal plane** (transverse): Covered by the 6 precordial leads (V1-V6). Views the heart as if looking down from above. Captures anterior-posterior and left-right electrical activity.
- **Sagittal plane**: Not directly represented by standard leads. Some information can be inferred from the combination of frontal and horizontal plane data. Modified leads (e.g., XYZ orthogonal leads in vectorcardiography) capture this directly.

---

## 2. Limb Leads — Frontal Plane

### 2.1 Einthoven's Bipolar Leads

Bipolar leads measure the potential difference between two electrodes. Neither electrode is "neutral" — both contribute to the signal.

#### Lead I

- **Positive electrode:** Left arm (LA)
- **Negative electrode:** Right arm (RA)
- **Lead axis:** 0° (purely leftward in the frontal plane)
- **What it sees:** The lateral wall of the left ventricle, looking from right to left across the heart. Any electrical vector moving leftward produces a positive deflection.
- **Cardiac structures:** High lateral LV wall, left atrial appendage
- **Coronary territory:** Left circumflex artery (LCx) marginal branches, diagonal branches of the LAD
- **Normal QRS:** Predominantly positive (upright), because the dominant vector of ventricular depolarization is directed leftward and inferiorly, and the leftward component projects positively onto Lead I
- **Clinical significance:** Essential for axis determination. A negative QRS in Lead I indicates right axis deviation. ST-T changes here suggest high lateral injury.

#### Lead II

- **Positive electrode:** Left leg (LL)
- **Negative electrode:** Right arm (RA)
- **Lead axis:** +60° (left-inferior direction)
- **What it sees:** The inferior and slightly lateral LV wall. Its axis closely parallels the normal cardiac axis (which averages about +60°), making it the lead that best "aligns with" normal cardiac electrical activity.
- **Cardiac structures:** Inferior LV wall, interatrial septum (P-wave is best seen here because atrial depolarization travels inferiorly and leftward — nearly parallel to Lead II)
- **Coronary territory:** Right coronary artery (RCA) in right-dominant circulation (85%), left circumflex (LCx) in left-dominant circulation (15%)
- **Normal QRS:** Tallest of all limb leads in normal hearts (because the normal mean QRS axis ~+60° aligns with Lead II's axis)
- **Clinical significance:** Best lead for rhythm analysis (P-waves most prominent), inferior STEMI detection, axis calculation. Continuous monitoring lead of choice in many ICU settings.

#### Lead III

- **Positive electrode:** Left leg (LL)
- **Negative electrode:** Left arm (LA)
- **Lead axis:** +120° (right-inferior direction)
- **What it sees:** The inferior wall, with a more rightward perspective than Lead II.
- **Cardiac structures:** Inferior LV wall, right ventricle (partial)
- **Coronary territory:** RCA (right-dominant) or LCx (left-dominant)
- **Normal QRS:** Variable — can be positive, negative, or biphasic depending on the cardiac axis. In a normal axis of +60°, the vector is 60° away from Lead III's axis, giving a relatively small positive deflection.
- **Clinical significance:** Inferior STEMI detection. Lead III > Lead II ST elevation suggests RCA as culprit (because the RCA territory is more rightward, aligning better with Lead III's rightward-pointing axis). Lead II > Lead III suggests LCx.

#### Einthoven's Equation

The three bipolar limb leads are mathematically related:

**Lead II = Lead I + Lead III**

This is Einthoven's Law, derived from Kirchhoff's voltage law. At every instant:

`V_II = V_I + V_III`

Practical implications:
- If any two limb leads are known, the third can be calculated.
- This provides a built-in quality check: if the equation doesn't hold, there is a technical error (lead misplacement, poor contact).
- The augmented leads can also be derived from the bipolar leads (see below).

### 2.2 Goldberger's Augmented Leads

Augmented leads are **unipolar** — they measure the potential at one electrode relative to a modified reference (the average of the other two limb electrodes, called the Goldberger central terminal). The "augmented" refers to Goldberger's modification of Wilson's original unipolar limb leads: by disconnecting the exploring electrode from the central terminal, the signal amplitude is increased by 50% (multiplied by 3/2), hence "augmented."

**Derivation:**
- `aVR = V_RA - (V_LA + V_LL) / 2`
- `aVL = V_LA - (V_RA + V_LL) / 2`
- `aVF = V_LL - (V_RA + V_LA) / 2`

Or equivalently from the bipolar leads:
- `aVR = -(Lead I + Lead II) / 2`
- `aVL = (Lead I - Lead III) / 2`
- `aVF = (Lead II + Lead III) / 2`

#### aVR — The Cavity Lead

- **Exploring electrode:** Right arm (RA)
- **Lead axis:** -150° (right-superior direction)
- **What it sees:** Looks into the heart from the right shoulder. Its axis points away from all normal depolarization vectors, so it normally records predominantly **negative** deflections. It is effectively a "cavity lead" — it peers into the ventricular cavities from a distant, rightward-superior vantage point.
- **Cardiac structures:** Right upper heart, endocardial surface of the left ventricle (viewed from inside-out), basal septum
- **Coronary territory:** Left main coronary artery, proximal LAD, proximal RCA (the aVR lead is uniquely sensitive to global subendocardial ischemia)
- **Normal QRS:** Predominantly negative (deep QS or rS pattern), because the mean QRS vector points away from aVR. P-wave is negative. T-wave is usually positive (since repolarization vector also points away from aVR, and T-wave inversion of the negative QRS produces an upright T).
- **Clinical significance:**
  - **ST elevation in aVR** suggests left main occlusion, severe proximal LAD disease, or severe 3-vessel disease causing global subendocardial ischemia
  - **Tall R-wave in aVR** (terminal R >3mm) suggests sodium channel blockade (tricyclic antidepressant overdose, class IC antiarrhythmics)
  - **aVR is the most frequently ignored lead** but contains critical diagnostic information
  - ST elevation in aVR with diffuse ST depression elsewhere = left main equivalent until proven otherwise

#### aVL — The High Lateral Lead

- **Exploring electrode:** Left arm (LA)
- **Lead axis:** -30° (left-superior direction)
- **What it sees:** The high lateral wall of the left ventricle, looking from the left shoulder.
- **Cardiac structures:** High lateral LV wall, lateral free wall
- **Coronary territory:** First diagonal branch of LAD, obtuse marginal branches of LCx
- **Normal QRS:** Variable depending on axis. With normal axis (+60°), the vector is 90° away from aVL, producing a small or biphasic QRS. With leftward axis, QRS becomes more positive in aVL.
- **Clinical significance:**
  - Reciprocal lead for inferior MI (ST depression in aVL is often the **earliest sign** of an inferior STEMI — it may appear before ST elevation in inferior leads)
  - High lateral STEMI (isolated ST elevation in I and aVL suggests diagonal branch or obtuse marginal occlusion)
  - Lead aVL is the most sensitive reciprocal lead for inferior injury

#### aVF — The Inferior Lead

- **Exploring electrode:** Left leg (LL)
- **Lead axis:** +90° (directly inferior)
- **What it sees:** The inferior wall of the left ventricle, looking straight up from below.
- **Cardiac structures:** Inferior (diaphragmatic) LV wall, inferior portion of the interventricular septum
- **Coronary territory:** RCA (right-dominant, 85%) or LCx (left-dominant, 15%)
- **Normal QRS:** Usually positive, since the mean QRS vector has a significant inferior component.
- **Clinical significance:** Inferior STEMI detection. Essential for axis determination — if QRS is negative in aVF, the axis has a superior component (left axis deviation if Lead I is positive).

### 2.3 Hexaxial Reference System

The six frontal plane leads create a hexaxial reference system when their axes are all drawn through a common center point. This divides the frontal plane into 12 sectors of 30° each.

**Arrangement (clockwise from 0°):**

```
             -90° (aVL is at -30°, aVR is at -150°)
              |
              |
  -150° aVR --+-- -30° aVL
             /|\
            / | \
  +/-180° /  |  \ 0° Lead I
          /   |   \
         /    |    \
  +150° /     |     \ +30°
       /      |      \
  +120° III --+-- +60° Lead II
              |
           +90° aVF
```

**Quick Axis Determination (2-Lead Method):**

1. Look at Lead I:
   - QRS predominantly positive → axis is somewhere between -90° and +90° (left half of circle)
   - QRS predominantly negative → axis is between +90° and +270° (right half)
2. Look at aVF:
   - QRS predominantly positive → axis is between 0° and +180° (inferior half)
   - QRS predominantly negative → axis is between 0° and -180° (superior half)
3. Combine:
   - Lead I positive + aVF positive → **Normal axis** (0° to +90°)
   - Lead I positive + aVF negative → **Left axis deviation** (-1° to -90°)
   - Lead I negative + aVF positive → **Right axis deviation** (+91° to +180°)
   - Lead I negative + aVF negative → **Extreme axis deviation** (-91° to -180° / +181° to +270°), also called "northwest axis"

**Precise Axis Determination (6-Lead Method):**

1. Find the lead with the **most isoelectric** (smallest amplitude, most biphasic) QRS complex.
2. The mean QRS axis is **perpendicular** to that lead's axis.
3. Determine direction (of the two perpendicular options) by checking which leads have positive QRS deflections.
4. For fine-tuning: find the lead with the **tallest** positive QRS — the axis points approximately toward that lead's positive pole.

**Normal Axis Ranges:**

| Axis Range | Classification | Common Causes |
|-----------|----------------|---------------|
| -30° to +90° | Normal axis | Healthy hearts |
| +90° to +180° | Right axis deviation | RV hypertrophy, PE, lateral MI, LPFB |
| -30° to -90° | Left axis deviation | LAFB, inferior MI, LVH, LBBB |
| -90° to -180° | Extreme axis deviation | Ventricular rhythms, severe conduction disease |

---

## 3. Precordial (Chest) Leads — Horizontal Plane

### 3.1 Electrode Positions

The precordial leads are **unipolar** leads. Each measures the potential at a specific chest wall location relative to the Wilson Central Terminal (WCT), which is the average of all three limb electrodes and approximates zero potential.

#### V1 — Fourth Intercostal Space, Right Sternal Border

- **Exact position:** 4th intercostal space (ICS), immediately to the right of the sternum
- **Landmark method:** Palpate the sternal angle (Angle of Louis), which is at the level of the 2nd rib. The space below the 2nd rib is the 2nd ICS. Count down two more spaces to reach the 4th ICS. Place the electrode at the right sternal border.
- **Faces:** Rightward and anterior — directly faces the interventricular septum and the right ventricle

#### V2 — Fourth Intercostal Space, Left Sternal Border

- **Exact position:** 4th ICS, immediately to the left of the sternum
- **Landmark method:** Same ICS level as V1, but on the left side of the sternum
- **Faces:** Anterior — faces the interventricular septum from the left parasternal position

#### V3 — Midway Between V2 and V4

- **Exact position:** Midpoint of a straight line between V2 and V4 (no independent bony landmark)
- **Landmark method:** Place V2 and V4 first, then position V3 equidistant between them
- **Faces:** Anterior — transitional lead between septal and anterior territory

#### V4 — Fifth Intercostal Space, Left Midclavicular Line

- **Exact position:** 5th ICS at the intersection with the midclavicular line (a vertical line dropped from the midpoint of the left clavicle)
- **Landmark method:** From the 4th ICS (V1/V2 level), count down one more space. Follow this space laterally to the midclavicular line.
- **Faces:** Anterior — directly over the cardiac apex in most individuals
- **Note:** V4 is the anchor for V5 and V6 — those leads are placed at the same horizontal level as V4, NOT by counting ribs at their respective lateral positions

#### V5 — Left Anterior Axillary Line, Same Horizontal Level as V4

- **Exact position:** Intersection of the anterior axillary line (the fold of skin at the front of the armpit) with the horizontal plane of V4
- **Landmark method:** Draw a horizontal line from V4 laterally. Place V5 where this line meets the anterior axillary line.
- **Faces:** Leftward — faces the lateral wall of the LV

#### V6 — Left Midaxillary Line, Same Horizontal Level as V4

- **Exact position:** Intersection of the midaxillary line (midpoint of the axilla, roughly the center of the armpit) with the horizontal plane of V4
- **Landmark method:** Continue the horizontal line from V4/V5 to the midaxillary line.
- **Faces:** Directly leftward — faces the lateral wall of the LV

#### Additional Leads (Not Standard 12-Lead)

| Lead | Position | When to Use |
|------|----------|-------------|
| V3R | Mirror of V3 on right chest | Right ventricular MI |
| V4R | 5th ICS, right midclavicular line (mirror of V4) | Right ventricular MI — MOST diagnostic |
| V7 | Left posterior axillary line, same horizontal as V4 | Posterior MI |
| V8 | Left midscapular line (tip of scapula), same horizontal as V4 | Posterior MI |
| V9 | Left paraspinal border, same horizontal as V4 | Posterior MI |

### 3.2 What Each Precordial Lead Sees

The precordial leads create a sweep around the chest wall from right (V1) to left (V6), progressively moving the viewpoint from the septum and right ventricle to the lateral left ventricle. This creates the characteristic **R-wave progression** — the R-wave grows and the S-wave shrinks from V1 to V6, reflecting the increasing alignment of the lead axis with the dominant leftward depolarization vector.

#### Detailed Lead-by-Lead Analysis

**V1 — The Septal-RV Lead**

- **Faces:** Interventricular septum (from the right side), right ventricular free wall
- **Cardiac structures:** RV anterior wall, interventricular septum (right side), right atrium (partially)
- **Coronary territory:** LAD (septal perforators), RCA (RV branches)
- **Normal QRS morphology:** rS pattern — small r wave followed by a deep S wave
  - **Why:** Septal depolarization (left-to-right, toward V1) produces the small initial r-wave. Then the massive LV free wall depolarization (directed leftward, away from V1) produces the dominant S-wave. The small RV depolarization occurring simultaneously is overwhelmed by the LV vector.
- **Normal R:S ratio:** <1 (r < S), typically R:S approximately 0.1-0.5
- **R-wave amplitude:** Small, usually <6mm
- **Transition significance:** V1 is normally the lead with the smallest R-wave

**V2 — The Septal Lead**

- **Faces:** Interventricular septum (from the left parasternal position)
- **Cardiac structures:** Interventricular septum, anterior RV-LV junction
- **Coronary territory:** LAD (septal perforators), proximal LAD
- **Normal QRS morphology:** rS pattern — slightly larger r-wave than V1, still dominant S-wave
  - **Why:** Similar to V1 but slightly more leftward position means the septal vector still projects toward V2 (r-wave) and the LV vector still projects away (S-wave). The r-wave may be marginally taller because V2 is slightly closer to the septum.
- **Normal R:S ratio:** <1, but R:S is larger than in V1
- **Clinical note:** V1-V2 are the most important leads for detecting RBBB (rsR' pattern), Brugada pattern, and posterior MI (tall R-waves as reciprocal change)

**V3 — The Anterior Transitional Lead**

- **Faces:** Anterior LV wall, transitional zone between septum and anterior wall
- **Cardiac structures:** Anterior interventricular groove, anterior LV wall
- **Coronary territory:** LAD (mid-segment)
- **Normal QRS morphology:** RS pattern — R and S waves of roughly equal amplitude (the "transition zone" often occurs here)
  - **Why:** V3 sits at the crossover point where the leftward LV depolarization vector is roughly perpendicular to the lead axis. The septal (toward) and LV free wall (away) vectors cancel to varying degrees.
- **Normal R:S ratio:** Approximately 1 (this is where the R/S transition typically occurs)
- **Clinical note:** The normal transition zone is between V2 and V4. Early transition (R > S in V1 or V2) or late transition (R < S beyond V4) are abnormal and clinically significant.

**V4 — The Anterior-Apical Lead**

- **Faces:** Anterior LV wall, cardiac apex
- **Cardiac structures:** LV apex, anterior LV wall, anterolateral papillary muscle region
- **Coronary territory:** LAD (mid-to-distal), sometimes the "wrap-around" LAD supplies the inferior apex
- **Normal QRS morphology:** Rs or RS pattern — R-wave is now dominant or at least equal to S-wave
  - **Why:** V4 is directly over the apex. The initial septal vector still produces a small q-wave or initial r-wave deflection, but the dominant LV depolarization now has a significant component toward V4 (the apex is part of the LV), producing a tall R-wave. The terminal LV base depolarization moving away may produce a small s-wave.
- **Normal R:S ratio:** >=1 (R should equal or exceed S by V4)
- **Clinical note:** V4 typically has the tallest R-wave of all precordial leads. Loss of R-wave height in V4 is very sensitive for anterior wall pathology.

**V5 — The Low Lateral Lead**

- **Faces:** Lateral LV wall (anterolateral)
- **Cardiac structures:** Lateral LV free wall, anterolateral papillary muscle
- **Coronary territory:** LCx (obtuse marginal branches), LAD (diagonal branches)
- **Normal QRS morphology:** qRs pattern — small initial q-wave (septal depolarization moving away from V5), tall R-wave (LV depolarization moving toward V5), small terminal s-wave
  - **Why:** Septal depolarization is left-to-right, moving away from the laterally-placed V5, producing a small q-wave. The massive LV free wall vector points toward V5, producing a tall R. Terminal depolarization of the basal portions may move slightly away.
- **Normal R:S ratio:** >1, typically R >> S
- **Clinical note:** A normal q-wave in V5-V6 reflects normal septal depolarization and should NOT be confused with pathological Q-waves of infarction. Pathological Qs are >40ms wide and/or >25% of R-wave amplitude.

**V6 — The Lateral Lead**

- **Faces:** Lateral LV wall (directly lateral)
- **Cardiac structures:** Lateral LV free wall
- **Coronary territory:** LCx (obtuse marginals), distal LAD diagonal branches
- **Normal QRS morphology:** qRs pattern — similar to V5 but with a smaller R-wave (because V6 is further from the heart)
  - **Why:** Same mechanism as V5. The R-wave is slightly smaller because V6 is at the midaxillary line, further from the myocardium than V5.
- **Normal R:S ratio:** >1, R dominant
- **Clinical note:** R-wave in V6 should be smaller than V5. If R in V6 > R in V5, consider LVH or lateral wall pathology.

#### Comprehensive Precordial Lead Summary Table

| Lead | Faces | Cardiac Structure | Coronary Territory | Normal R:S | Normal Morphology | Expected R-Wave (mm) | Key Pathological Findings |
|------|-------|-------------------|-------------------|-----------|-------------------|---------------------|--------------------------|
| V1 | Right-anterior | RV free wall, right side of septum | LAD septals, RCA (RV) | <1 | rS | 1-4 | rsR' (RBBB), tall R (posterior MI, RVH, WPW), Brugada ST pattern |
| V2 | Anterior | Septum, anterior RV-LV junction | LAD septals, proximal LAD | <1 | rS | 2-6 | rsR' (RBBB), tall R (posterior MI), ST elevation (anterior STEMI, Brugada) |
| V3 | Anterior | Anterior LV wall, transition zone | LAD (mid) | ~1 | RS | 4-12 | Poor R progression (anterior MI), ST elevation (anterior STEMI) |
| V4 | Anterior-apical | LV apex, anterior wall | LAD (mid-distal) | >=1 | Rs or qRs | 8-18 | Q-waves (anterior MI), tallest R normally, ST elevation (anterior STEMI) |
| V5 | Anterolateral | Lateral LV free wall | LCx (OM), LAD (diag) | >1 | qRs | 8-18 | Q-waves (lateral MI), ST changes (lateral ischemia), tall R (LVH) |
| V6 | Lateral | Lateral LV free wall | LCx (OM), LAD (diag) | >1 | qRs | 6-16 | Q-waves (lateral MI), ST changes (lateral ischemia), deep S loss |

#### R-Wave Progression

Normal R-wave progression: the R-wave amplitude progressively increases from V1 to V4 (or V5), then may slightly decrease in V6.

| Condition | R-Wave Pattern | Mechanism |
|-----------|---------------|-----------|
| Normal | R grows V1 → V4/V5, slight decrease V6 | Normal leftward LV dominance |
| Poor R-wave progression | R fails to grow or grows slowly V1-V4 | Anterior MI, LVH, LBBB, COPD, lead misplacement |
| Reverse R-wave progression | R decreases V1 → V4 | Anterior MI, dextrocardia, lead reversal |
| Early transition | R/S > 1 by V2 | Posterior MI, RVH, WPW (posterior pathway), normal variant |
| Late transition | R/S < 1 at V5 | Anterior MI, LBBB, LVH (occasionally), COPD |

---

## 4. Lead Groups by Cardiac Region

This section defines the anatomical territories and their corresponding ECG lead groups. This is the foundation for MI localization, ischemia detection, and understanding which artery is likely involved.

### 4.1 Septal Leads: V1, V2

**Anatomic Basis:** V1 and V2 are positioned directly over the interventricular septum. The septum is the muscular wall dividing the right and left ventricles. It depolarizes from left to right (first structure activated via the left bundle branch), which is why these leads show an initial small r-wave.

- **What they see:** Interventricular septum (anterior two-thirds depolarized by septal perforators from the LAD; posterior one-third by septal perforators from the PDA)
- **Coronary artery:** Left anterior descending artery (LAD) — specifically the septal perforator branches
- **Clinical significance:**
  - **Septal STEMI:** ST elevation in V1-V2 (usually extending to V3-V4 as well, since isolated septal MI is uncommon with current-era criteria)
  - **RBBB morphology:** The terminal conduction delay of RBBB (right bundle depolarizing late) is directed rightward/anterior toward V1-V2, producing the characteristic rsR' pattern
  - **LBBB morphology:** Loss of normal septal depolarization (left-to-right) means loss of the normal r-wave in V1-V2, producing a QS pattern with broad, slurred complexes
  - **Posterior MI:** V1-V2 show the **reciprocal** changes of posterior injury — tall R-waves (mirror of Q-waves), ST depression (mirror of ST elevation), upright tall T-waves (mirror of T-wave inversion)
  - **RV hypertrophy:** Tall R-wave in V1 (R > S) because the RV contributes more to the anterior/rightward vector
  - **Brugada syndrome:** Characteristic coved or saddleback ST elevation in V1-V2

### 4.2 Anterior Leads: V3, V4

**Anatomic Basis:** V3 and V4 overlie the anterior wall of the left ventricle. V4, positioned at the 5th ICS midclavicular line, sits approximately over the cardiac apex.

- **What they see:** Anterior wall of the left ventricle, cardiac apex
- **Coronary artery:** LAD — mid-to-distal segments
- **Clinical significance:**
  - **Anterior STEMI:** ST elevation in V3-V4 (often extending to V1-V2 and/or V5-V6 depending on the extent of the LAD territory involved)
  - **Anterior MI Q-waves:** Pathological Q-waves in V3-V4 indicate anterior wall necrosis
  - **Poor R-wave progression:** Failure of R-wave to grow normally from V1 to V4 — most commonly caused by prior anterior MI (loss of anterior electrical forces), but also seen with LBBB, LVH, COPD, and lead misplacement
  - **LAD wrap-around:** In some patients, the LAD extends beyond the apex to supply the inferior wall. Occlusion of a "wrap-around" LAD can cause ST elevation in V3-V4 AND II, III, aVF simultaneously — this anteroinferior pattern can be confusing but is clinically important
  - **Early repolarization:** V3-V4 are common leads for benign early repolarization ST elevation (J-point elevation with concave-upward morphology)

### 4.3 Lateral Leads: I, aVL, V5, V6

**Anatomic Basis:** These leads face the lateral wall of the left ventricle from two different planes. Leads I and aVL view the lateral wall from the frontal plane (high lateral), while V5 and V6 view it from the horizontal plane (low lateral or anterolateral). They are grouped together because they share the LCx/diagonal coronary territory, but recognizing the high vs. low distinction is important for culprit artery identification.

- **What they see:** Lateral wall of the left ventricle
- **Coronary artery:** LCx (obtuse marginal branches) for the lateral free wall; diagonal branches of the LAD for the anterolateral wall
- **Subdivisions:**
  - **High lateral:** I, aVL — supplied by the first diagonal branch of LAD or first obtuse marginal of LCx
  - **Low lateral (anterolateral):** V5, V6 — supplied by obtuse marginal branches of LCx, distal diagonal branches of LAD
- **Clinical significance:**
  - **Lateral STEMI:** ST elevation in I, aVL, V5, V6 — the extent of involvement helps determine the culprit:
    - Isolated I, aVL = first diagonal or high obtuse marginal
    - V5, V6 with or without I, aVL = obtuse marginal or LCx main
    - V1-V6 with I, aVL = proximal LAD (extensive anterior-lateral)
  - **LVH voltage criteria:** V5 and V6 often show the tallest R-waves in LVH (Sokolow-Lyon: S in V1 + R in V5 or V6 >= 35mm)
  - **Reciprocal changes for inferior MI:** I and aVL are the most important reciprocal leads for inferior STEMI. ST depression in aVL may precede overt inferior ST elevation.

### 4.4 Inferior Leads: II, III, aVF

**Anatomic Basis:** These three leads all have axes with significant inferior components (+60°, +120°, +90° respectively), meaning they view the inferior (diaphragmatic) surface of the heart from below.

- **What they see:** Inferior wall of the left ventricle (the surface resting on the diaphragm)
- **Coronary artery:**
  - **Right coronary artery (RCA):** In approximately 85% of the population (right-dominant circulation), the RCA gives rise to the posterior descending artery (PDA), which supplies the inferior wall
  - **Left circumflex (LCx):** In approximately 10-15% (left-dominant circulation), the LCx gives rise to the PDA and supplies the inferior wall
  - **Co-dominant:** In approximately 5%, both arteries contribute
- **Clinical significance:**
  - **Inferior STEMI:** ST elevation in II, III, aVF
  - **Culprit artery determination:**
    - ST elevation in Lead III > Lead II → favors **RCA** (because Lead III at +120° is more rightward, and RCA territory extends more rightward/posteriorly)
    - ST elevation in Lead II > Lead III → favors **LCx** (because Lead II at +60° is more leftward, and LCx territory is more leftward)
    - Reciprocal ST depression in Lead I and aVL → strongly favors **RCA**
    - Concomitant lateral ST elevation (V5, V6) → favors **LCx**
  - **Always check V4R** when inferior STEMI is present — RV infarction accompanies 30-50% of inferior STEMIs from proximal RCA occlusion and requires specific management (volume loading, avoid nitrates/diuretics)
  - **Always check V7-V9** — posterior extension is common with inferior STEMIs

### 4.5 Right Ventricular Leads: V1, V3R, V4R

**Anatomic Basis:** The right ventricle sits anteriorly and to the right. Standard V1 partially overlies the RV, but dedicated right-sided leads (obtained by placing V3-V6 in mirror-image positions on the right chest) are far more sensitive for RV pathology.

- **What they see:** Right ventricular free wall and outflow tract
- **Standard 12-lead RV representation:** Only V1 — and it is heavily influenced by the septum and LV as well
- **Dedicated RV leads:**
  - **V3R:** Mirror of V3 on the right chest — right anterior RV wall
  - **V4R:** 5th ICS, right midclavicular line (mirror of V4) — **the single most diagnostic lead for RV MI** (ST elevation >= 1mm in V4R has >90% sensitivity and specificity for RV infarction)
  - V5R, V6R: Possible but rarely used, as V4R is sufficient
- **Coronary artery:** Proximal RCA (acute marginal branches supply the RV free wall). RV MI occurs with proximal RCA occlusion — the RV branches arise early from the RCA, so occlusion must be proximal to deprive the RV of blood supply.
- **Clinical significance:**
  - **RV STEMI:** ST elevation >= 1mm in V4R in the setting of inferior STEMI → RV infarction
  - **Hemodynamic implications:** RV MI causes RV failure → decreased preload to LV → hypotension. Treatment is **volume** (IV fluids) and avoidance of preload-reducing agents (nitroglycerin, morphine, diuretics)
  - **RV hypertrophy:** Right axis deviation + dominant R in V1 + RV strain pattern (ST depression/T-inversion in V1-V3, sometimes called "RV strain")
  - **Pulmonary embolism:** RV dilation from acute pressure overload can produce S1Q3T3, right axis deviation, RBBB, and T-wave inversions in V1-V4 (RV strain pattern)

### 4.6 Posterior Leads: V7, V8, V9

**Anatomic Basis:** The posterior wall of the left ventricle is not directly faced by any standard 12-lead electrode. V7-V9 are placed on the back to directly "see" the posterior wall. In the standard 12-lead, posterior wall events are detected only through **reciprocal changes** in the anterior leads V1-V3.

- **What they see:** Posterior (inferobasal) wall of the left ventricle
- **Electrode positions:**
  - **V7:** Left posterior axillary line, same horizontal level as V4-V6
  - **V8:** Left midscapular line (tip of left scapula), same horizontal level
  - **V9:** Left paraspinal border, same horizontal level
- **Coronary artery:**
  - **Posterior descending artery (PDA):** Arising from the RCA in right-dominant (85%) or from the LCx in left-dominant (15%) circulation
  - **LCx posterolateral branches** in many patients
- **Standard 12-lead reciprocal clues for posterior MI (seen in V1-V3):**
  - ST depression (reciprocal of posterior ST elevation)
  - Tall, broad R-waves (reciprocal of posterior Q-waves)
  - Upright, tall T-waves (reciprocal of posterior T-wave inversions)
  - R/S ratio > 1 in V1-V2 with the above features
- **When V7-V9 are diagnostic:**
  - ST elevation >= 0.5mm in V7-V9 (note: the threshold is lower than standard 1mm because these leads are further from the heart, attenuating the signal)
  - This confirms posterior STEMI and is a catheterization lab activation criterion
- **Clinical significance:**
  - Posterior MI is **frequently missed** because standard 12-lead criteria don't include posterior leads
  - Any patient with ST depression in V1-V3 should be suspected of posterior STEMI and should have posterior leads applied
  - Posterior MI commonly accompanies inferior STEMI (inferoposterior pattern) — up to 40% of inferior STEMIs have posterior extension
  - Isolated posterior MI (without inferior or lateral involvement) is the most commonly missed STEMI diagnosis

### 4.7 aVR — The Forgotten Lead

**Anatomic Basis:** aVR views the heart from the right shoulder at -150 degrees. Its axis points away from the dominant direction of depolarization, making it a unique "reverse mirror" of the rest of the ECG. It looks into the ventricular cavity and sees the endocardial surface and the basal septum.

- **Why it is unique:** aVR is the only standard lead whose axis points toward the right atrium and the outflow tracts. It is diametrically opposite to Lead II (+60° vs. -150°), meaning aVR is approximately the inverse of Lead II.
- **Clinical significance:**

  **1. Left main/severe 3-vessel disease:**
  - ST elevation in aVR >= 1mm with diffuse ST depression in multiple leads (especially V4-V6, I, II) suggests:
    - Left main coronary artery stenosis or occlusion
    - Severe proximal LAD disease
    - Severe 3-vessel disease
  - **Mechanism:** Global subendocardial ischemia causes ST depression pointing away from the endocardium (toward the epicardium) in most leads. In aVR, which looks at the endocardium, this same vector produces ST elevation.
  - ST elevation in aVR > V1 in the setting of STEMI → suggests left main rather than proximal LAD

  **2. Sodium channel blockade / TCA overdose:**
  - Terminal R-wave in aVR > 3mm
  - R-wave duration in aVR > 40ms
  - R/S ratio > 0.7 in aVR
  - **Mechanism:** Sodium channel blockade slows depolarization of the basal interventricular septum. This terminal, slow depolarization vector points rightward and superiorly — toward aVR — producing a prominent terminal R-wave.
  - Agents: tricyclic antidepressants, class IA/IC antiarrhythmics, cocaine, diphenhydramine (in overdose)

  **3. Acute pericarditis differentiation:**
  - In pericarditis: diffuse ST elevation with PR depression in most leads. aVR shows **ST depression with PR elevation** (reciprocal to the diffuse changes).
  - This is opposite to the aVR ST elevation of left main disease, helping differentiate the two.

  **4. SVT differentiation:**
  - In AVNRT, retrograde P-waves may be visible in aVR as pseudo-R' waves
  - The P-wave morphology in aVR during tachycardia can help localize the origin of an atrial tachycardia

  **5. Pulmonary embolism:**
  - ST elevation in aVR may occur with massive PE due to RV strain and global hemodynamic compromise

---

## 5. Reciprocal Changes — The Mirror Theory

### 5.1 What Are Reciprocal Changes?

When myocardial injury occurs (e.g., acute STEMI), the injured region generates an "injury current" — a voltage gradient between injured and healthy tissue. Leads facing the injured region record ST elevation (the injury current points toward the epicardial surface of the injury zone, which faces these leads). Simultaneously, leads facing the **opposite** side of the heart record ST depression, because the same injury current vector points **away** from them.

**Key principles:**
- Reciprocal changes are not artifact — they represent the same electrical event viewed from the opposite direction
- They are a **direct consequence of dipole theory**: if a vector produces a positive deflection in one lead, it MUST produce a negative deflection in a lead oriented in the opposite direction
- Reciprocal changes are often **more prominent** than the primary changes because the reciprocal leads may be closer to the heart or better aligned with the injury vector
- The presence of reciprocal changes **increases specificity** for true STEMI (helps distinguish from pericarditis, early repolarization, and other ST elevation mimics)

### 5.2 Reciprocal Lead Pairs

| Primary Territory | Primary Leads (ST Elevation) | Reciprocal Leads (ST Depression) | Clinical Notes |
|-------------------|------------------------------|----------------------------------|----------------|
| Anterior (LAD) | V1, V2, V3, V4 | II, III, aVF | Inferior reciprocal depression is subtle and less consistent than other patterns |
| Extensive anterior (proximal LAD) | V1-V6, I, aVL | II, III, aVF | More prominent reciprocal changes with larger territory involvement |
| Inferior (RCA) | II, III, aVF | I, aVL | aVL reciprocal depression is often the FIRST and most sensitive sign; may appear before inferior ST elevation is overt |
| Inferior (LCx) | II, III, aVF | I, aVL (less pronounced) | Reciprocal changes in aVL may be less pronounced with LCx-mediated inferior MI because LCx territory extends laterally |
| Lateral (LCx/diagonal) | I, aVL, V5, V6 | III, aVF, sometimes V1-V2 | Reciprocal inferior depression helps distinguish lateral STEMI from pericarditis |
| High lateral (diagonal) | I, aVL | III, aVF | Isolated high lateral STEMI is easy to miss — look for the reciprocal changes in inferior leads |
| Posterior (PDA/LCx) | V7, V8, V9 | V1, V2, V3 | The "reciprocal" changes in V1-V3 (ST depression, tall R, upright T) are often the ONLY sign on standard 12-lead; this is why posterior MI is frequently missed |
| RV (proximal RCA) | V1, V4R | V5, V6 (sometimes) | RV STEMI reciprocal changes are inconsistent on standard 12-lead |
| Left main / 3-vessel | aVR (ST elevation) | V4-V6, I, II (diffuse ST depression) | The "global" pattern: aVR elevation with diffuse depression indicates diffuse subendocardial ischemia |

### 5.3 Why Reciprocal Changes Matter

**Diagnostic:**
- Reciprocal ST depression increases the specificity of STEMI diagnosis from ~50% to >90%
- Pericarditis causes diffuse ST elevation WITHOUT reciprocal changes (except in aVR, which shows ST depression as expected). If reciprocal depression is present in limb or precordial leads, it is STEMI until proven otherwise.
- Early repolarization does NOT produce reciprocal changes

**Prognostic:**
- The presence of reciprocal changes correlates with **larger infarct size**
- More extensive reciprocal changes indicate more myocardium at risk
- Reciprocal changes with inferior STEMI that extend to V1-V3 suggest posterior involvement (worse prognosis)

**Diagnostic primacy:**
- In posterior MI, the reciprocal changes in V1-V3 may be the **only** findings on standard 12-lead ECG
- In high lateral STEMI (small diagonal branch), the primary ST elevation in I and aVL may be subtle, but reciprocal ST depression in III and aVF may be more obvious
- The reciprocal changes can appear **earlier** than the primary changes — aVL depression may precede inferior ST elevation by minutes

**Differentiation of STEMI mimics:**

| Condition | ST Elevation | Reciprocal Depression | Other Features |
|-----------|-------------|----------------------|----------------|
| STEMI | Regional (territory-based) | Present in opposite leads | Hyperacute T-waves, Q-wave evolution |
| Pericarditis | Diffuse (except aVR, V1) | Absent (except aVR) | PR depression, diffuse, concave-up morphology |
| Early repolarization | V2-V5 (sometimes I, II, aVL) | Absent | Notched J-point, concave-up, young patient |
| LVH with strain | V5-V6 (strain pattern) | V1-V2 (tall R) | High voltage, strain = asymmetric T-wave inversion |
| Brugada | V1-V2 (coved or saddleback) | Absent | RBBB-like pattern, characteristic morphology |
| Takotsubo | Anterior (V2-V5), sometimes diffuse | Variable | Apical ballooning, emotional/physical trigger, deep T inversions later |

---

## 6. Coronary Artery Territory Mapping

### 6.1 Complete Artery-to-Lead Mapping

#### Left Anterior Descending (LAD) Artery

The LAD is the largest coronary artery, supplying approximately 40-50% of the LV myocardium. It travels in the anterior interventricular groove from the left main bifurcation toward the cardiac apex.

| Branch | Territory Supplied | ECG Leads | STEMI Pattern | Additional Notes |
|--------|-------------------|-----------|---------------|-----------------|
| **Proximal LAD** (before 1st septal and 1st diagonal) | Anterior wall, septum, lateral, apex, sometimes inferior | V1-V6, I, aVL (sometimes II, III, aVF) | Extensive anterior STEMI | Worst prognosis of all LAD lesions; involves >40% of LV; may present with cardiogenic shock |
| **Mid LAD** (after 1st diagonal, before 2nd) | Anterior wall, apex | V3-V5 (sometimes V2, V6) | Focal anterior STEMI | Typical "anterior STEMI" presentation |
| **Distal LAD** | Apex, sometimes inferior apex | V4-V5, sometimes II, III, aVF | Apical/anteroinferior | "Wrap-around LAD" — extends to inferior surface in ~15% of patients |
| **Septal perforator branches** | Interventricular septum (anterior 2/3) | V1-V2 (sometimes V3) | Septal MI (rare in isolation) | Supplies the His bundle and proximal bundle branches; occlusion can cause fascicular/bundle branch blocks |
| **First diagonal branch (D1)** | High lateral wall | I, aVL | High lateral STEMI | Often presents as isolated ST elevation in I, aVL with reciprocal depression in III, aVF; easy to miss |
| **Second diagonal branch (D2)** | Anterolateral wall | I, aVL, V5, V6 | Anterolateral | Variable territory depending on vessel size |

**LAD occlusion algorithm (proximal vs. mid vs. distal):**

1. **ST elevation in V1-V6 + I, aVL + ST depression in II, III, aVF** → Proximal LAD (before D1 and S1)
2. **ST elevation in V1-V6 but NO ST depression in inferior leads and NO ST elevation in I, aVL** → Proximal LAD after D1 but before S1 (lateral wall spared)
3. **ST elevation in V1-V4 + new RBBB** → Proximal LAD (septal perforator occlusion with extensive anterior injury)
4. **ST elevation in V3-V5 without V1-V2 involvement and without I, aVL** → Mid LAD
5. **ST elevation in V4-V6 + II, III, aVF** → Distal wrap-around LAD
6. **ST elevation isolated to I, aVL** → Diagonal branch

#### Left Circumflex (LCx) Artery

The LCx travels in the left atrioventricular groove, supplying the lateral and (in left-dominant circulation) the posterior and inferior walls. The LCx is the most difficult artery to detect occlusion of on standard 12-lead ECG because its territory is relatively "electrocardiographically silent" — the lateral and posterior walls are poorly represented by standard lead positions.

| Branch | Territory Supplied | ECG Leads | STEMI Pattern | Additional Notes |
|--------|-------------------|-----------|---------------|-----------------|
| **Proximal LCx** | Lateral wall, posterior (if dominant) | I, aVL, V5-V6, possibly V7-V9 | Lateral STEMI | May have minimal changes on standard 12-lead |
| **First obtuse marginal (OM1)** | High lateral wall | I, aVL | High lateral STEMI | Can be indistinguishable from D1 occlusion on ECG alone |
| **Second obtuse marginal (OM2)** | Posterolateral wall | V5-V6, V7-V8 | Posterolateral STEMI | Posterior leads essential |
| **Posterolateral branch** | Posterior and lateral wall | V5-V6, V7-V9 | Posterolateral | Often presents with ST depression V1-V3 (reciprocal) |
| **LCx as dominant artery** (15%) | Inferior + posterior + lateral | II, III, aVF, I, aVL, V5-V6, V7-V9 | Inferolateral STEMI | Lead II > Lead III ST elevation suggests LCx over RCA |

**Key LCx points:**
- LCx occlusion produces the **most commonly missed STEMI** — up to 50% of LCx STEMIs may not meet standard criteria on 12-lead ECG
- If clinical suspicion is high and the ECG shows ST depression in V1-V3 or nonspecific changes, obtain posterior leads (V7-V9)
- Isolated ST elevation in I, aVL may be the only sign of an OM1 occlusion

#### Right Coronary Artery (RCA)

The RCA travels in the right atrioventricular groove, supplying the RV, the SA node (55% of patients), the AV node (85-90% of patients), and the inferior LV wall (in right-dominant circulation). It is the dominant artery in ~85% of patients.

| Branch | Territory Supplied | ECG Leads | STEMI Pattern | Additional Notes |
|--------|-------------------|-----------|---------------|-----------------|
| **Proximal RCA** (before acute marginal) | RV + inferior wall | V1, V4R, II, III, aVF | Inferior + RV STEMI | Includes RV branches; RV MI occurs here; check V4R |
| **SA node artery** (from proximal RCA in 55%) | SA node | No direct ECG lead | No ST changes | Occlusion can cause sinus bradycardia, sinus arrest |
| **Acute marginal branches** | RV free wall | V1, V3R, V4R | RV STEMI | Dedicated right-sided leads needed |
| **Mid RCA** | Inferior wall | II, III, aVF | Inferior STEMI (no RV) | Distal to RV branches, so RV is spared |
| **Distal RCA / PDA** | Inferior wall, posterior septum | II, III, aVF, V7-V9 | Inferoposterior | PDA supplies the posterior septum including the AV node in 85-90% |
| **AV node artery** (from distal RCA/PDA in 85-90%) | AV node | No direct lead | No ST changes | Occlusion can cause AV block (1st, 2nd Mobitz I, 3rd degree with junctional escape) |
| **Posterolateral branch** (in right-dominant) | Posterolateral wall | V5-V6, V7-V9 | Inferoposterolateral | Full RCA occlusion in right-dominant patient |

**RCA occlusion algorithm:**

1. **ST elevation III > II + reciprocal depression in I, aVL** → RCA (not LCx)
2. **ST elevation in V4R >= 1mm** → Proximal RCA with RV involvement
3. **ST elevation II, III, aVF + AV block** → RCA (AV node artery involvement)
4. **ST elevation II, III, aVF + sinus bradycardia** → Proximal RCA (SA node artery involvement)
5. **ST elevation II, III, aVF + ST depression V1-V3** → RCA with posterior extension (PDA involvement)
6. **ST elevation II, III, aVF + ST elevation V5-V6** → Large RCA or LCx territory overlap

### 6.2 Coronary Dominance

Coronary dominance is defined by which artery gives rise to the posterior descending artery (PDA) and posterolateral branches:

| Dominance | Prevalence | PDA Origin | Supplies |
|-----------|-----------|-----------|----------|
| **Right-dominant** | ~85% | RCA | Inferior wall, posterior septum, AV node |
| **Left-dominant** | ~10-15% | LCx | Inferior wall, posterior septum, AV node |
| **Co-dominant** | ~5% | Both RCA and LCx contribute | Shared inferior/posterior supply |

**Clinical implications of dominance:**
- In right-dominant patients, inferior STEMI is usually from RCA occlusion
- In left-dominant patients, the LCx is a larger vessel and its occlusion causes more extensive damage (inferior + lateral + posterior)
- Left-dominant patients who occlude their LCx are at higher risk because a single vessel supplies a larger territory
- AV block with inferior MI suggests RCA in right-dominant patients or LCx in left-dominant patients
- Dominance cannot be determined from the ECG — it requires coronary angiography. However, the patterns above (Lead III > II for RCA, Lead II > III for LCx) provide strong probabilistic guidance.

### 6.3 Clinical Decision: Which Artery Is Occluded?

**Step-by-step algorithm for STEMI culprit artery identification:**

**Step 1: Identify the territory of ST elevation**

| ST Elevation Pattern | Primary Territory |
|---------------------|-------------------|
| V1-V4 | Anterior (LAD) |
| V1-V6, I, aVL | Extensive anterior (proximal LAD) |
| I, aVL only | High lateral (D1 or OM1) |
| II, III, aVF | Inferior (RCA or LCx) |
| V5-V6 with I, aVL | Lateral (LCx) |
| V7-V9 (or V1-V3 depression) | Posterior (PDA or LCx) |

**Step 2: For anterior STEMI — determine LAD level**

| Finding | Culprit |
|---------|---------|
| V1-V6 + I, aVL + inferior depression | Proximal LAD (before D1 and S1) |
| V1-V6 without lateral or inferior changes | LAD between D1 and S1 |
| V3-V5 only | Mid-distal LAD |
| V4-V6 + inferior elevation | Wrap-around LAD |
| New RBBB + anterior STE | Proximal LAD (septal perforator) |

**Step 3: For inferior STEMI — determine RCA vs. LCx**

| Finding | Favors |
|---------|--------|
| Lead III > Lead II ST elevation | RCA |
| Lead II > Lead III ST elevation | LCx |
| Reciprocal depression in I, aVL | RCA (strongly) |
| ST elevation in V4R >= 1mm | RCA (proximal) |
| Concomitant V5-V6 ST elevation | LCx |
| AV block (any degree) | RCA (in right-dominant) |
| Sinus bradycardia | Proximal RCA |
| No reciprocal changes in I, aVL | LCx |

**Step 4: Check for extension**

| Combination | Interpretation |
|-------------|---------------|
| Inferior + V4R elevation | RCA with RV involvement → avoid preload reduction |
| Inferior + V1-V3 depression | Posterior extension → apply V7-V9 |
| Inferior + V5-V6 elevation | Posterolateral extension |
| Anterior + inferior elevation | Wrap-around LAD or very proximal LAD or multivessel |

---

## 7. Summary: The Master Lead Reference Table

### 7.1 Standard 12-Lead ECG — Complete Reference

| Lead | Axis Angle | Plane | Cardiac Structure | Coronary Territory | Reciprocal To | Normal QRS | Key Clinical Uses |
|------|-----------|-------|-------------------|-------------------|---------------|-----------|-------------------|
| **I** | 0° | Frontal | High lateral LV wall | LCx (OM), LAD (D1) | III | Upright (positive R) | Lateral STEMI, axis determination (leftward component), LAFB detection |
| **II** | +60° | Frontal | Inferior LV wall | RCA (right-dom), LCx (left-dom) | aVL | Tallest upright of limb leads | Inferior STEMI, rhythm analysis (best P-waves), axis (inferior component) |
| **III** | +120° | Frontal | Inferior LV wall (rightward) | RCA (right-dom), LCx (left-dom) | aVL, I | Variable (positive, negative, or biphasic) | Inferior STEMI (III > II = RCA), LPFB detection, axis |
| **aVR** | -150° | Frontal | Cavity (endocardial), basal septum | Left main, proximal LAD, proximal RCA | II (approximate) | Predominantly negative (QS or rS) | Left main/3-vessel disease (STE), TCA OD (tall terminal R), pericarditis (STD + PR elevation) |
| **aVL** | -30° | Frontal | High lateral LV wall | LAD (D1), LCx (OM1) | III, aVF | Variable (depends on axis) | High lateral STEMI, reciprocal mirror for inferior STEMI (earliest sign), axis |
| **aVF** | +90° | Frontal | Inferior LV wall (directly below) | RCA (right-dom), LCx (left-dom) | aVL | Usually positive | Inferior STEMI, axis determination (inferior component) |
| **V1** | ~115° (horiz) | Horizontal | RV, right side of septum | LAD (septals), RCA (RV branches) | V5, V6 (partial) | rS (small r, deep S) | RBBB (rsR'), posterior MI (tall R reciprocal), Brugada, RVH, WPW (posterior pathway), P-wave morphology (atrial pathology) |
| **V2** | ~105° (horiz) | Horizontal | Septum, anterior RV-LV junction | LAD (septals), proximal LAD | V5, V6 (partial) | rS (slightly larger r than V1) | RBBB, Brugada, anterior STEMI, posterior MI reciprocal, LBBB (QS pattern) |
| **V3** | ~80° (horiz) | Horizontal | Anterior LV wall (transition zone) | LAD (mid) | — | RS (approximately equal) | Anterior STEMI, R-wave transition point, poor R progression assessment |
| **V4** | ~60° (horiz) | Horizontal | LV apex, anterior wall | LAD (mid-distal) | — | Rs or qRs (R >= S) | Anterior STEMI, apical pathology, tallest R normally, early repolarization |
| **V5** | ~30° (horiz) | Horizontal | Anterolateral LV wall | LCx (OM), LAD (diag) | V1 (partial) | qRs (dominant R) | Lateral STEMI, LVH voltage (Sokolow-Lyon), lateral ischemia |
| **V6** | ~0° (horiz) | Horizontal | Lateral LV free wall | LCx (OM), LAD (diag) | V1 (partial) | qRs (dominant R, smaller than V5) | Lateral STEMI, LBBB vs RBBB morphology, LVH |

### 7.2 Supplementary Leads — Complete Reference

| Lead | Position | Plane | Cardiac Structure | Coronary Territory | Reciprocal To | Key Clinical Uses |
|------|----------|-------|-------------------|-------------------|---------------|-------------------|
| **V3R** | Mirror of V3, right chest | Horizontal | RV anterior wall | RCA (acute marginals) | — | RV MI detection |
| **V4R** | 5th ICS, right midclavicular line | Horizontal | RV free wall (directly over) | Proximal RCA | — | **Gold standard** for RV MI (STE >= 1mm); must obtain in all inferior STEMIs |
| **V5R** | Right anterior axillary line | Horizontal | RV lateral wall | RCA | — | Rarely needed; V4R is sufficient |
| **V6R** | Right midaxillary line | Horizontal | RV lateral wall | RCA | — | Rarely needed |
| **V7** | Left posterior axillary line | Horizontal | Posterior LV wall | PDA (from RCA or LCx), LCx posterolateral | V1-V3 | Posterior STEMI (STE >= 0.5mm); obtain when V1-V3 ST depression present |
| **V8** | Left midscapular line (scapular tip) | Horizontal | Posterior LV wall | PDA, LCx posterolateral | V1-V3 | Posterior STEMI confirmation |
| **V9** | Left paraspinal border | Horizontal | Posterior LV wall (most posterior) | PDA, LCx posterolateral | V1-V3 | Posterior STEMI; lowest amplitude due to distance from heart |

### 7.3 Lead Groups — Quick Reference

| Group Name | Leads | Wall | Primary Artery | Reciprocal Leads |
|-----------|-------|------|---------------|-----------------|
| **Septal** | V1, V2 | Interventricular septum | LAD (septal perforators) | V7-V9 (posterior, partial) |
| **Anterior** | V3, V4 | Anterior LV wall, apex | LAD (mid-distal) | II, III, aVF (mild) |
| **Extensive anterior** | V1-V6, I, aVL | Septum + anterior + lateral | LAD (proximal) | II, III, aVF |
| **High lateral** | I, aVL | High lateral LV wall | D1 (LAD), OM1 (LCx) | III, aVF |
| **Low lateral** | V5, V6 | Anterolateral LV wall | OM (LCx), diagonal (LAD) | III, aVF, V1 (partial) |
| **Lateral (all)** | I, aVL, V5, V6 | Lateral LV wall | LCx, LAD diagonals | III, aVF |
| **Inferior** | II, III, aVF | Inferior (diaphragmatic) LV wall | RCA (85%) or LCx (15%) | I, aVL |
| **Right ventricular** | V1, V4R | RV free wall | Proximal RCA | — |
| **Posterior** | V7, V8, V9 | Posterior (inferobasal) LV wall | PDA, LCx posterolateral | V1, V2, V3 |

### 7.4 The "Dangerous" Patterns — Leads That Must Not Be Ignored

| Pattern | Leads to Check | What It Means | Action |
|---------|---------------|---------------|--------|
| Any inferior STEMI | V4R | RV involvement | Volume resuscitation, avoid nitrates |
| ST depression V1-V3 | V7-V9 | Posterior STEMI | Apply posterior leads, cath lab if confirmed |
| Diffuse ST depression + aVR elevation | aVR | Left main / 3-vessel disease | Emergent cardiology consultation |
| ST elevation I, aVL only | Inferior leads | Missed high lateral STEMI | Reciprocal depression in III, aVF confirms |
| Tall R in V1 (new) | V7-V9, clinical context | Posterior MI vs RVH vs WPW | Correlate clinically, posterior leads if ACS suspected |
| Deep T inversions V1-V4 (Wellens) | V2-V3 (deepest) | Critical proximal LAD stenosis | Cath lab, not stress test (risk of anterior STEMI) |
| Terminal R in aVR >3mm | aVR | Sodium channel blockade | IV sodium bicarbonate |
| New RBBB + anterior STE | V1-V4 | Proximal LAD occlusion with septal infarction | Emergent reperfusion |

---

## 8. Implementation Notes for the AI System

### 8.1 Lead-Territory Mapping as Code Logic

When the AI system analyzes an ECG, it should use the following hierarchy:

1. **Identify leads with ST elevation** — map to primary territory using Section 4 lead groups
2. **Identify leads with ST depression** — determine if these are reciprocal (opposite territory) or primary ischemia (subendocardial)
3. **Determine culprit artery** — use the algorithms in Section 6.3
4. **Check for extension** — posterior leads (V1-V3 depression), RV leads (V4R in inferior STEMI)
5. **Assess severity** — number of leads involved, magnitude of ST deviation, presence of reciprocal changes

### 8.2 Confidence Modifiers Based on Lead Anatomy

| Scenario | Confidence Modifier | Reason |
|----------|-------------------|--------|
| ST elevation in contiguous leads matching a known territory + reciprocal changes | HIGH | Classic territorial pattern with confirmation |
| ST elevation in contiguous leads matching a known territory, no reciprocal changes | MODERATE | Could be STEMI or mimic (pericarditis, early repolarization) |
| ST elevation in non-contiguous leads | LOW | Does not match any single territorial pattern; consider artifact, lead misplacement, or multivessel |
| ST depression V1-V3 only | MODERATE for posterior MI | Requires clinical correlation and ideally posterior leads |
| Isolated aVR ST elevation with diffuse depression | HIGH for left main/3-vessel | Highly specific pattern |
| ST changes in a single lead only | LOW | Requires serial ECGs and clinical correlation |

### 8.3 Common Pitfalls

| Pitfall | Problem | Solution |
|---------|---------|----------|
| Ignoring aVR | Missing left main disease | Always analyze aVR — it is not a "throwaway" lead |
| Not checking V4R in inferior STEMI | Missing RV MI → inappropriate treatment (nitrates, diuretics) | Protocol: every inferior STEMI triggers V4R check recommendation |
| Calling V1-V3 ST depression "anterior ischemia" | Missing posterior STEMI | Consider posterior MI first; recommend posterior leads |
| Normal variant Q-waves in III | Over-calling inferior MI | Q-wave in III alone is common and benign; must see Q-waves in at least 2 inferior leads with ST-T changes |
| Benign early repolarization | False positive STEMI activation | Look for: absence of reciprocal changes, concave-up morphology, notched J-point, young patient, serial ECG stability |
| Lead misplacement | Territory misassignment | Check for: impossible patterns (e.g., P-wave axis not matching expected), sudden morphology shifts between adjacent leads, negative P in I (arm lead reversal) |

---

## 6A. Agent Assignment

**Architecture:** Option E — 3 Parallel Phase 1 Specialists + 1 Sequential CDS (Node 2.1 Gate Passed 2026-03-27)

| Agent | Role for Lead Anatomy Reference | Key Features Used |
|-------|--------------------------|-------------------|
| **RRC** (Rhythm/Rate/Conduction) | Not a direct user for territory mapping | RRC uses lead assignments for axis calculation (frontal plane leads) but does not perform coronary territory mapping |
| **IT** (Ischemia/Territory) | Primary user — queries this reference for all coronary territory mapping | V1-V4 → LAD → anterior wall; II/III/aVF → RCA or LCx → inferior wall; I/aVL/V5-V6 → LCx or diagonal → lateral wall; V7-V9 or reciprocal anterior changes → posterior wall; aVR → cavity/proximal LAD occlusion pattern; right-sided leads (V3R/V4R) → RV wall |
| **MR** (Morphology/Repolarization) | Not a direct user for territory mapping | MR identifies morphology patterns by lead (e.g., Brugada in V1-V2, early repolarization in lateral leads) but does not perform coronary territory mapping; uses lead locations for morphology context only |
| **CDS** (Cross-Domain Synthesis) | Uses territory mapping to validate IT findings and resolve cross-domain conflicts | CDS references lead anatomy when resolving ST elevation territory ambiguity (e.g., ST elevation in V1-V2 only — anterior STEMI vs Brugada); applies mirror-image mapping for dextrocardia when flagged by RRC/MR |

### Primary Agent
**IT** — IT is the sole Phase 1 agent that directly queries this reference for coronary territory mapping. IT uses the lead-to-territory table to assign ST elevation, ST depression, T-wave changes, and Q-waves to specific coronary territories.

### Cross-Domain Hints
No cross_domain_hints are generated from this reference file itself. IT generates territory-related cross_domain_hints to CDS from individual disease files based on the territory mappings defined here.

### CDS Specific Role
CDS uses this reference indirectly, receiving IT's territory-mapped findings and using the reference to validate territory assignments in ambiguous cases (e.g., when ST elevation spans multiple territories or when IT and MR provide competing explanations for the same lead group). CDS also applies the mirror-image territory table from this reference when dextrocardia is confirmed, reversing IT's standard territory mapping to generate a corrected ischemia assessment.

---

## References

1. Goldberger AL, Goldberger ZD, Shvilkin A. *Goldberger's Clinical Electrocardiography: A Simplified Approach*. 9th ed. Elsevier; 2018.
2. Surawicz B, Knilans TK. *Chou's Electrocardiography in Clinical Practice*. 6th ed. Saunders; 2008.
3. Wagner GS, Strauss DG. *Marriott's Practical Electrocardiography*. 12th ed. Lippincott Williams & Wilkins; 2014.
4. Birnbaum Y, et al. "ECG Diagnosis of ST-Elevation Myocardial Infarction." *J Electrocardiol*. 2014;47(4):443-455.
5. de Winter RJ, et al. "A New ECG Sign of Proximal LAD Occlusion." *N Engl J Med*. 2008;359(19):2071-2073.
6. Smith SW. "Updates on the Electrocardiogram in Acute Coronary Syndromes." *Curr Emerg Hosp Med Rep*. 2013;1(1):43-52.
7. Wellens HJ. "The ECG in Emergency Decision Making." 2nd ed. Saunders; 2006.
8. Bayés de Luna A. *Clinical Electrocardiography: A Textbook*. 4th ed. Wiley-Blackwell; 2012.
9. Zimetbaum PJ, Josephson ME. "Use of the Electrocardiogram in Acute Myocardial Infarction." *N Engl J Med*. 2003;348(10):933-940.
10. Thygesen K, et al. "Fourth Universal Definition of Myocardial Infarction." *Eur Heart J*. 2018;39(37):2032-2040.
