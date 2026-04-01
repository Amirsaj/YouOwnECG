# Normal ECG — Complete Reference from First Principles

**Node:** 2.7.200
**Status:** Research Complete
**Date:** 2026-03-26

---

## 1. The Normal Cardiac Cycle — From Ion Channels to Surface ECG

### 1.1 Resting Membrane Potential

The resting membrane potential of a ventricular myocyte is approximately **-90 mV**, maintained by:

- **K+ equilibrium potential**: The cell membrane at rest is predominantly permeable to K+ through inward rectifier channels (I_K1). The Nernst equation gives the K+ equilibrium potential:

$$E_K = \frac{RT}{zF} \ln \frac{[K^+]_o}{[K^+]_i} \approx -96 \text{ mV}$$

where $[K^+]_o \approx 4 \text{ mM}$ and $[K^+]_i \approx 150 \text{ mM}$.

- **Na+/K+ ATPase pump**: Actively transports 3 Na+ out and 2 K+ in per cycle, generating a net outward (hyperpolarizing) current of approximately -4 mV contribution. This maintains the ionic gradients against passive leak.

- **Goldman-Hodgkin-Katz equation** governs the actual resting potential, incorporating the small but non-zero Na+ permeability:

$$V_m = \frac{RT}{F} \ln \frac{P_K[K^+]_o + P_{Na}[Na^+]_o + P_{Cl}[Cl^-]_i}{P_K[K^+]_i + P_{Na}[Na^+]_i + P_{Cl}[Cl^-]_o}$$

At rest, $P_K : P_{Na} : P_{Cl} \approx 1 : 0.04 : 0.45$, yielding $V_m \approx -90 \text{ mV}$.

**Working myocardium vs pacemaker cells:**
- Working myocardium (atrial and ventricular cardiomyocytes): Stable Phase 4. High I_K1 density keeps the membrane clamped near $E_K$. These cells do NOT depolarize spontaneously — they require an external stimulus.
- Pacemaker cells (SA node, AV node): Low I_K1 density. Phase 4 is NOT stable — there is a slow, spontaneous diastolic depolarization driven by the "funny current" ($I_f$), T-type Ca2+ current ($I_{Ca,T}$), and the Na+/Ca2+ exchanger (NCX). This is the basis of cardiac automaticity.

### 1.2 Action Potential Phases

#### Working Myocardium (Atrial and Ventricular Cardiomyocytes)

**Phase 0 — Rapid Depolarization**
- Trigger: membrane potential reaches threshold (~-70 mV from a propagating wavefront)
- Mechanism: voltage-gated Na+ channels (Nav1.5, encoded by SCN5A) open rapidly
- Na+ rushes into the cell down its electrochemical gradient ($E_{Na} \approx +67 \text{ mV}$)
- Upstroke velocity ($dV/dt_{max}$): **200-400 V/s** in Purkinje fibers, **150-300 V/s** in ventricular myocytes, **100-200 V/s** in atrial myocytes
- Membrane potential overshoots to approximately **+20 to +30 mV**
- Na+ channels inactivate within 1-2 ms (fast inactivation gate closes)

**Phase 1 — Early Rapid Repolarization**
- Mechanism: transient outward K+ current ($I_{to}$) activates rapidly then inactivates
- $I_{to}$ has two components: $I_{to,fast}$ (4-AP sensitive, Kv4.3) and $I_{to,slow}$ (Kv1.4)
- Creates the characteristic "notch" between Phase 0 peak and Phase 2 plateau
- $I_{to}$ density is heterogeneous: highest in epicardium, lowest in endocardium — this creates the transmural voltage gradient responsible for the J-wave
- Membrane potential drops to approximately **+10 to 0 mV**

**Phase 2 — Plateau**
- Unique to cardiac myocytes (not seen in skeletal muscle or neurons)
- Duration: **200-300 ms** (the long plateau is why cardiac muscle has a long refractory period, preventing tetanic contraction)
- Balance of inward and outward currents:
  - Inward: L-type Ca2+ current ($I_{Ca,L}$, Cav1.2) — slow inactivation, provides Ca2+ for excitation-contraction coupling
  - Outward: delayed rectifier K+ currents — $I_{Kr}$ (hERG/KCNH2, rapid component) and $I_{Ks}$ (KvLQT1/KCNQ1 + minK, slow component)
- The Ca2+ entering triggers Ca2+-induced Ca2+ release (CICR) from the sarcoplasmic reticulum via ryanodine receptors (RyR2) — this is the coupling between electrical excitation and mechanical contraction
- Membrane potential hovers near **0 to +10 mV**, gradually declining as $I_{Ca,L}$ inactivates and $I_K$ increases

**Phase 3 — Rapid Repolarization**
- $I_{Ca,L}$ fully inactivates, removing inward current
- $I_{Kr}$ and $I_{Ks}$ continue to increase, creating net outward current
- As membrane repolarizes past approximately -40 mV, I_K1 reactivates (inward rectifier), accelerating repolarization
- Rapid return to resting potential (~-90 mV)
- $I_{Kr}$ is the dominant repolarizing current during Phase 3 — this is why hERG channel blockade (many drugs) prolongs the QT interval

**Phase 4 — Resting Potential**
- Membrane potential stable at approximately -90 mV
- Dominated by I_K1 conductance
- Na+/K+ ATPase and NCX restore ionic homeostasis
- Cell awaits next depolarizing stimulus

#### SA Node and AV Node Pacemaker Cells

**Phase 0 — Slow Depolarization**
- No functional fast Na+ channels (hyperpolarization-dependent Na+ channels are absent or scarce)
- Upstroke driven by L-type Ca2+ current ($I_{Ca,L}$)
- Upstroke velocity: **1-10 V/s** (much slower than working myocardium)
- Peak potential: approximately **+10 to +20 mV**
- Slow conduction velocity results from the slow upstroke — this is critical for the AV nodal delay

**Phase 1-2 — Absent or minimal**
- No distinct plateau or notch

**Phase 3 — Repolarization**
- Delayed rectifier K+ currents ($I_{Kr}$, $I_{Ks}$) repolarize the cell
- Maximum diastolic potential: approximately **-60 to -65 mV** (never reaches -90 mV — no significant I_K1)

**Phase 4 — Spontaneous Diastolic Depolarization**
- The "pacemaker potential" — the basis of all cardiac automaticity
- Three overlapping mechanisms drive the slow depolarization from ~-65 mV to the threshold of ~-40 mV:
  1. **$I_f$ ("funny current")**: Hyperpolarization-activated, cyclic nucleotide-gated (HCN4) channels. Mixed Na+/K+ current that activates upon hyperpolarization. Called "funny" because it activates on hyperpolarization (opposite of most voltage-gated channels). cAMP-sensitive — this is how sympathetic/parasympathetic tone modulates heart rate.
  2. **T-type Ca2+ current ($I_{Ca,T}$)**: Activates at more negative potentials than L-type, contributes to late Phase 4 depolarization.
  3. **Na+/Ca2+ exchanger (NCX)**: Rhythmic Ca2+ release from SR ("calcium clock") drives NCX in forward mode (3 Na+ in, 1 Ca2+ out), generating net inward current.
- Rate of Phase 4 depolarization determines heart rate:
  - Sympathetic stimulation (norepinephrine → beta-1 → cAMP) increases $I_f$ → steeper slope → faster rate
  - Parasympathetic stimulation (ACh → muscarinic M2 → reduces cAMP, activates $I_{K,ACh}$) decreases $I_f$ and hyperpolarizes → slower rate

### 1.3 Normal Conduction Pathway

| Structure | Inherent Rate | Conduction Velocity | Time from SA Node |
|-----------|--------------|--------------------|--------------------|
| **SA node** | 60-100 bpm | 0.05 m/s (within node) | 0 ms |
| **Atrial myocardium** | — (not automatic) | 0.8-1.0 m/s | 0-80 ms |
| Internodal pathways (anterior/middle/posterior) | — | 1.0-1.2 m/s | Facilitate preferential conduction |
| **AV node** (compact node) | 40-60 bpm (escape) | **0.02-0.05 m/s** (slowest) | 80-120 ms |
| **Bundle of His** | 40-60 bpm (escape) | 1.0-1.5 m/s | 120-160 ms |
| **Left bundle branch** (splits into anterior and posterior fascicles) | 25-40 bpm (escape) | 1.5-2.0 m/s | 140-170 ms |
| **Right bundle branch** | 25-40 bpm (escape) | 1.5-2.0 m/s | 140-170 ms |
| **Purkinje fibers** | 20-40 bpm (escape) | **2.0-4.0 m/s** (fastest) | 160-190 ms |
| **Ventricular myocardium** | — (not automatic) | 0.3-0.4 m/s | 190-210 ms |

**The AV delay (120-200 ms total PR interval):**
- AV node conduction is intentionally slow due to: small cell size, fewer gap junctions, L-type Ca2+ dependent Phase 0 (slow upstroke), fewer Na+ channels
- Physiologic purpose: allows atrial systole to complete before ventricular systole begins. The "atrial kick" contributes 15-25% of ventricular filling (more in diastolic dysfunction, stiff ventricle)
- The AV node is the electrical "gatekeeper" — protects the ventricles from excessively rapid atrial rates (critical in atrial fibrillation/flutter)
- AV node is richly innervated by both sympathetic and parasympathetic fibers — conduction speed is autonomically modulated

**Ventricular activation sequence:**
1. Left septal surface (first 10-20 ms) — via left bundle branch posterior fascicle
2. Right septal surface and RV apex (20-40 ms)
3. Both free walls from endocardium to epicardium (40-80 ms)
4. Posterobasal LV and upper septum (last to depolarize, 80-100 ms)

### 1.4 From Cellular Depolarization to Surface ECG

**Dipole theory:**
- A wavefront of depolarization creates an electrical dipole: the boundary between depolarized (negative intracellular charge has reversed to positive) and resting (still negative) tissue
- The dipole vector points from negative (already depolarized) toward positive (about to be depolarized) — i.e., in the direction of propagation
- The net cardiac vector at any instant is the vector sum of all simultaneously active dipoles throughout the heart
- This net vector changes direction continuously throughout the cardiac cycle

**Lead theory — projecting the cardiac vector:**
- Each ECG lead defines an axis in space
- The voltage recorded by a lead equals the projection of the net cardiac vector onto that lead's axis:

$$V_{lead} = \vec{H} \cdot \hat{L} = |\vec{H}| \cos\theta$$

where $\vec{H}$ is the net heart vector, $\hat{L}$ is the unit vector of the lead axis, and $\theta$ is the angle between them.

- A lead records a **positive** deflection when the net vector points toward its positive electrode
- A lead records a **negative** deflection when the net vector points away from its positive electrode
- A lead records an **isoelectric** or biphasic deflection when the net vector is perpendicular to its axis

**The 12-lead system:**

*Limb leads (frontal plane):*

| Lead | Positive Electrode | Angle (Hexaxial) | Orientation |
|------|--------------------|-------------------|-------------|
| I | Left arm | 0° | Rightward to leftward |
| II | Left leg | +60° | Right shoulder to left leg |
| III | Left leg | +120° | Left shoulder to left leg |
| aVR | Right arm | -150° | Toward right shoulder |
| aVL | Left arm | -30° | Toward left shoulder |
| aVF | Left leg | +90° | Superior to inferior |

*Einthoven's triangle* — Leads I, II, III form a triangle around the heart. Einthoven's law: Lead II = Lead I + Lead III.

*Goldberger augmented leads* — aVR, aVL, aVF are augmented unipolar leads that use Wilson's central terminal (modified) as the reference. They bisect the angles of Einthoven's triangle.

*Precordial leads (transverse/horizontal plane):*

| Lead | Electrode Position | Primary View |
|------|--------------------|-------------|
| V1 | 4th ICS, right sternal border | RV, septum (anterior) |
| V2 | 4th ICS, left sternal border | Septum (anterior) |
| V3 | Midway between V2 and V4 | Anterior wall |
| V4 | 5th ICS, midclavicular line | Anterior wall, apex |
| V5 | 5th ICS, anterior axillary line | Lateral wall |
| V6 | 5th ICS, midaxillary line | Lateral wall |

*Wilson's central terminal (WCT):* The reference for unipolar leads. Average potential of RA + LA + LL through 5 kOhm resistors. Ideally zero throughout the cycle, in practice varies slightly.

Precordial leads essentially create a "sweep" around the chest from right anterior (V1) to left lateral (V6). Because V1 faces the RV and V6 faces the LV free wall, the QRS morphology undergoes a systematic transition (R-wave progression).

---

## 2. Normal P-wave

### 2.1 Genesis

The P-wave represents **atrial depolarization**.

- The SA node fires (no surface ECG correlate — SA node is too small to generate detectable voltage)
- Depolarization spreads through the **right atrium** first (the SA node is in the high right atrium at the junction of the SVC and the crista terminalis)
- Approximate timing:
  - First 40 ms: right atrial depolarization (contributes to the initial upstroke of the P-wave)
  - 40-80 ms: simultaneous right and left atrial depolarization (peak of P-wave)
  - 80-120 ms: terminal left atrial depolarization (downslope and terminal portion)
- In V1, the P-wave is characteristically **biphasic** (+/-): the initial positive component is right atrial (vector directed anteriorly toward V1), and the terminal negative component is left atrial (vector directed posteriorly away from V1)
- **Net P-wave vector**: directed leftward (+), inferior (+), and slightly anterior — approximately +50° to +60° in the frontal plane

### 2.2 Normal Parameters (All 12 Leads)

| Lead | Morphology | Amplitude | Duration | Notes |
|------|-----------|-----------|----------|-------|
| **I** | Upright | 0.05-0.20 mV | 60-120 ms | Always upright in normal sinus rhythm. If inverted in Lead I, consider: ectopic atrial rhythm, limb lead reversal, dextrocardia |
| **II** | Upright | 0.05-0.25 mV | 60-120 ms | Best lead for P-wave analysis. Tallest P-wave (Lead II axis closely parallels the normal P-wave axis). The P-wave must be upright in II for sinus rhythm diagnosis |
| **III** | Variable (upright / flat / inverted) | 0-0.20 mV | 60-120 ms | May be upright, flat, or slightly inverted depending on P-wave axis. A slightly inverted P in III alone is a normal variant if P is upright in I and II |
| **aVR** | Inverted | 0.05-0.20 mV | 60-120 ms | Always inverted in sinus rhythm. If upright → wrong rhythm or lead reversal |
| **aVL** | Variable (upright / flat / inverted) | 0-0.15 mV | 60-120 ms | Depends on P-wave axis. Often low amplitude. May be biphasic or isoelectric if P-axis is near +60° (perpendicular to aVL at -30°) |
| **aVF** | Upright | 0.05-0.20 mV | 60-120 ms | Upright in sinus rhythm (P-axis is inferior). If inverted → consider ectopic atrial or junctional rhythm with retrograde P |
| **V1** | Biphasic (+/-) | Positive component ≤0.15 mV; negative component ≤0.10 mV | 60-120 ms | Critical lead for atrial abnormality. The terminal negative force (P-terminal force in V1, PTF_V1) should have area ≤0.04 mm·s (1 small box wide x 1 small box deep). PTF_V1 exceeding this suggests LAE |
| **V2** | Upright or biphasic (+/-) | 0.05-0.15 mV | 60-120 ms | Transition from V1 biphasic to upright. May still have small terminal negativity |
| **V3** | Upright | 0.05-0.15 mV | 60-120 ms | Usually upright by V3 |
| **V4** | Upright | 0.05-0.15 mV | 60-120 ms | Upright |
| **V5** | Upright | 0.05-0.15 mV | 60-120 ms | Upright, morphology similar to Lead I |
| **V6** | Upright | 0.05-0.15 mV | 60-120 ms | Upright, morphology similar to Lead I |

**Global P-wave normals:**
- **Duration**: 60-120 ms (3 small boxes at 25 mm/s). ≥120 ms suggests left atrial abnormality (delayed left atrial depolarization).
- **Amplitude**: ≤0.25 mV (2.5 mm at 10 mm/mV standard calibration) in any lead. Amplitude >0.25 mV in II, III, or aVF suggests right atrial abnormality (P-pulmonale).
- **Morphology**: Should be smooth and rounded. Notching with interpeak distance ≥40 ms suggests left atrial abnormality (P-mitrale).

### 2.3 P-wave Axis

- **Normal range**: **0° to +75°**
- This guarantees: P upright in I (axis between -90° and +90°) and P upright in II (axis between -30° and +150°)
- The most common normal P-wave axis is approximately **+50° to +60°**
- If P-axis is between +75° and +90°: P may be isoelectric in Lead I — borderline, may be normal in tall/thin individuals
- If P-axis is negative: consider ectopic atrial rhythm (focus is low in atrium, depolarization proceeds superiorly → inverted P in II, III, aVF)

---

## 3. Normal PR Interval

### 3.1 Definition
- Measured from the **onset of the P-wave** to the **onset of the QRS complex** (whether Q or R)
- Includes: P-wave duration (atrial depolarization) + PR segment (primarily AV nodal delay + His-Purkinje conduction)
- The **PR segment** (end of P to onset of QRS) is the true isoelectric baseline for ST segment measurement when the TP segment is obscured by tachycardia

### 3.2 Normal Range
- **120-200 ms** (3-5 small boxes at 25 mm/s)
- <120 ms: short PR — consider pre-excitation (WPW, LGL), ectopic atrial rhythm near AV node, enhanced AV conduction
- \>200 ms: first-degree AV block (delay in AV node or His-Purkinje system)

### 3.3 Variation with Heart Rate
- PR interval shortens at higher heart rates due to sympathetic enhancement of AV nodal conduction:
  - HR 60 bpm: PR typically 160-200 ms
  - HR 80 bpm: PR typically 140-180 ms
  - HR 100 bpm: PR typically 120-160 ms
- This is a normal physiologic adaptation — not disease

### 3.4 Age Variations
- Neonates/infants: PR 80-120 ms (shorter due to smaller heart and faster conduction)
- Children (1-12 years): PR 100-180 ms
- Adolescents: PR 120-200 ms (adult range)
- Elderly (>65 years): PR may extend to 200-220 ms due to fibrosis; mild prolongation is often benign but should be noted

### 3.5 Sex Variations
- No clinically significant sex-based difference in PR interval at matched heart rates

### 3.6 Athletic Heart
- Athletes may have PR intervals up to **220 ms** at rest as a normal variant due to high vagal tone
- Should shorten normally with exercise
- If PR >220 ms or fails to shorten with exercise → pathologic until proven otherwise

---

## 4. Normal QRS Complex

### 4.1 Genesis

The QRS complex represents **ventricular depolarization**. The three sequential phases create the characteristic morphology:

**Phase 1 — Septal Depolarization (first 10-20 ms):**
- The septum depolarizes **left-to-right** (the left bundle branch activates the left septal surface first, via septal perforator branches from the posterior fascicle)
- This produces a small vector directed **rightward and anteriorly**
- Surface ECG correlate: small **q wave** in left-facing leads (I, aVL, V5, V6) and small **r wave** in right-facing leads (V1, V2)
- These are "septal q waves" and "septal r waves" — both normal

**Phase 2 — Free Wall Depolarization (20-60 ms):**
- Both ventricular free walls depolarize simultaneously (endocardium to epicardium)
- The LV is ~3x the mass of the RV, so the LV vector dominates
- Net vector: directed **leftward, inferiorly, and posteriorly**
- Surface ECG: large **R wave** in left-facing leads (I, V5, V6), large **S wave** in right-facing leads (V1, V2)
- The RV contribution is largely "cancelled" by the larger opposing LV vector

**Phase 3 — Terminal/Basal Depolarization (60-100 ms):**
- The posterobasal LV and upper septum depolarize last (these regions are farthest from Purkinje endings)
- Net vector: directed **rightward, superiorly, and posteriorly** (small)
- Surface ECG: terminal **s wave** in left-facing leads, terminal **r'** or return toward baseline in V1

### 4.2 Normal Parameters — Lead by Lead

| Lead | Typical Morphology | R Amplitude | S Depth | Q Wave | Notes |
|------|-------------------|-------------|---------|--------|-------|
| **I** | qRs or Rs | 0.2-1.0 mV | 0-0.3 mV | Septal q: <0.04 s, <25% R height, <0.3 mV | R is dominant. Small q is normal (septal). Small terminal s is normal. |
| **II** | qRs, Rs, or R | 0.3-1.5 mV | 0-0.5 mV | Small q possible: <0.04 s, <25% R | Often the tallest R among limb leads. Morphology varies with QRS axis. |
| **III** | rS, Rs, qRs, QS, or Qr | 0.1-1.0 mV | 0-1.0 mV | Q wave can be normal and relatively large (up to 0.04 s) | Highly axis-dependent. QS or deep Q in III alone is a normal variant if no Q in II or aVF. Q in III may diminish or disappear with deep inspiration. |
| **aVR** | QS or rS | 0-0.3 mV (small r possible) | 0.3-1.5 mV | Predominantly negative complex is normal | aVR faces the "cavity" of the heart. All major vectors point away from aVR. R in aVR >0.3 mV or dominant R → abnormal (consider RVH, TCA toxicity, acute RV strain). |
| **aVL** | qRs, Rs, R, or rS | 0.1-1.0 mV | 0-0.6 mV | Septal q possible: <0.04 s, <25% R, <0.3 mV | Morphology depends on QRS axis. If axis is vertical (+60° to +90°), aVL may show rS. If axis is horizontal (-30° to 0°), aVL shows qR or R. |
| **aVF** | qRs, Rs, or R | 0.2-1.5 mV | 0-0.5 mV | Small q possible: <0.04 s, <25% R, <0.3 mV | If axis is horizontal, aVF may have small r and large S. Small q in aVF alone is not pathologic if no Q in II. |
| **V1** | rS | **r: 0.1-0.6 mV** (≤6 mm) | **S: 0.3-1.8 mV** | No Q wave normally | R:S ratio <1 (S must be deeper than R is tall). R in V1 >0.6 mV: consider RVH, posterior MI, WPW, RBBB. The small r = septal depolarization (left→right). |
| **V2** | rS | **r: 0.2-1.0 mV** | **S: 0.5-2.5 mV** | No Q wave normally | R growing compared to V1, S still dominant. Q in V2 is always pathologic (suggest anterior MI, septal MI). |
| **V3** | RS (transition) | **R: 0.3-1.5 mV** | **S: 0.3-1.5 mV** | Tiny q possible but uncommon | Transition zone: R ≈ S. The equiphasic (R=S) complex usually occurs in V3 or V4. |
| **V4** | Rs or qRs | **R: 0.5-2.5 mV** | **s: 0.1-0.8 mV** | Small septal q possible | R now dominant. V4 often has the tallest R wave among all 12 leads. |
| **V5** | qRs | **R: 0.5-2.5 mV** | **s: 0.1-0.5 mV** | Septal q: <0.04 s, <25% R, <0.3 mV | Septal q is normal and expected. R amplitude high but usually ≤V4. |
| **V6** | qRs | **R: 0.3-2.0 mV** (usually < V5) | **s: 0-0.3 mV** | Septal q: <0.04 s, <25% R, <0.3 mV | R in V6 < R in V5 (R decreases from V5 to V6 due to increasing distance from LV). Absent q in V5-V6 may suggest LBBB or LV pathology (loss of septal forces). |

**Absolute voltage limits (Sokolow-Lyon reference values):**
- R in V5 or V6 ≤2.6 mV (>2.6 mV: consider LVH)
- S in V1 + R in V5 or V6 ≤3.5 mV (Sokolow-Lyon criterion; >3.5 mV suggests LVH)
- R in V1 ≤0.6 mV (>0.6 mV: consider RVH, posterior MI, WPW)
- R in aVL ≤1.1 mV (>1.1 mV in isolation: consider LVH by Cornell)

### 4.3 R-Wave Progression

The systematic transition of QRS morphology from V1 (predominantly S) to V6 (predominantly R) is called **normal R-wave progression**.

| Zone | Leads | Expected R:S Ratio | QRS Morphology |
|------|-------|---------------------|----------------|
| Right precordial | V1-V2 | R:S < 1 | rS pattern — small r, deep S |
| Transition | V3-V4 | R:S ≈ 1 | RS pattern — R and S approximately equal |
| Left precordial | V5-V6 | R:S > 1 | qRs pattern — dominant R, small s |

- **Normal transition zone**: V3 or V4 (the lead where R first equals or exceeds S)
- **Early transition** (V1-V2): R:S ≥1 in V1 or V2. Causes: posterior MI (loss of posterior forces), RVH (increased anterior forces), WPW (Type A pre-excitation), normal variant (especially in young women), chest lead misplacement
- **Late transition** (V5-V6): R remains < S through V4 or later. Causes: LVH (delayed intrinsicoid deflection), anterior MI (loss of anterior forces), LBBB, COPD (hyperinflated lungs, vertically displaced heart), normal variant (especially in obese or short individuals)
- **Poor R-wave progression** (PRWP): R wave in V3 ≤0.3 mV. Nonspecific finding; differential includes anterior MI, LVH, cardiomyopathy, COPD, lead placement error

### 4.4 Normal QRS Duration

- **Normal**: **80-100 ms** (2-2.5 small boxes)
- **Upper limit of normal (borderline)**: 100-110 ms
- **Borderline/nonspecific**: 110-120 ms (intraventricular conduction delay if no BBB pattern)
- **Wide QRS**: ≥120 ms — always abnormal. Causes: RBBB, LBBB, IVCD, pre-excitation (WPW), hyperkalemia, ventricular rhythm, drug effect (Na+ channel blockers)

**Intrinsicoid deflection** (R-wave peak time):
- Time from QRS onset to R-wave peak, measured in V1 and V6
- V1: ≤35 ms (prolonged in RBBB)
- V6: ≤45 ms (prolonged in LBBB or LVH)

### 4.5 QRS Axis

**Normal**: **-30° to +90°**

| Axis Range | Classification | Lead I | Lead aVF | Quick Determination |
|-----------|---------------|--------|----------|---------------------|
| -30° to +90° | **Normal axis** | Positive | Positive (or slightly negative near -30°) | R upright in I and II |
| -30° to -90° | **Left axis deviation (LAD)** | Positive | Negative | Upright in I, inverted in aVF |
| +90° to +180° | **Right axis deviation (RAD)** | Negative | Positive | Inverted in I, upright in aVF |
| -90° to ±180° | **Extreme axis / northwest axis** | Negative | Negative | Inverted in both I and aVF |

**Rapid axis estimation method:**
1. Find the most isoelectric (equiphasic) limb lead
2. The QRS axis is perpendicular to that lead
3. Determine which of the two perpendicular directions by checking if the R-wave is positive in the lead 90° away

**Common causes of axis deviation:**
- LAD: LAFB (most common), LVH, inferior MI, ostium primum ASD
- RAD: RVH, LPFB (rare), PE, lateral MI, normal in children/young adults, tall/thin habitus

---

## 5. Normal ST Segment

### 5.1 Genesis

The ST segment represents the **early phase of ventricular repolarization** (Phase 2 plateau of the ventricular action potential).

- During the plateau, all ventricular myocytes are at approximately the same potential (~0 mV)
- Since there is no significant potential gradient across the myocardium during this phase, the ST segment is normally **isoelectric** (at the same level as the TP baseline)
- Any departure from isoelectric implies a transmural or regional difference in the plateau potential — this can be caused by ischemia, injury, pericardial inflammation, or (importantly) normal variants

### 5.2 Normal Ranges and Variants

**J-point (junction point):**
- The point where the QRS ends and the ST segment begins
- Defined as the first point of inflection (slope change) after the S-wave nadir (or after the R-wave if no S)

**Normal ST segment elevation thresholds:**

| Lead | Males <40 y | Males ≥40 y | Females (all ages) |
|------|------------|------------|-------------------|
| **V1** | ≤0.25 mV | ≤0.20 mV | ≤0.15 mV |
| **V2** | ≤0.25 mV | ≤0.20 mV | ≤0.15 mV |
| **V3** | ≤0.25 mV | ≤0.20 mV | ≤0.15 mV |
| **V4** | ≤0.10 mV | ≤0.10 mV | ≤0.10 mV |
| **V5** | ≤0.10 mV | ≤0.10 mV | ≤0.10 mV |
| **V6** | ≤0.10 mV | ≤0.10 mV | ≤0.10 mV |
| **Limb leads (I, II, III, aVF, aVL)** | ≤0.10 mV | ≤0.10 mV | ≤0.10 mV |
| **aVR** | ST depression ≤0.05 mV normal | Same | Same |

*Source: 2018 Fourth Universal Definition of MI (ESC/AHA/ACC/WHF)*

**Normal ST segment depression:**
- ≤0.05 mV (0.5 mm) in any lead is generally accepted as normal
- ≤0.10 mV in V2-V3 may be seen as a normal variant in some references
- ST depression >0.05 mV in other leads warrants clinical correlation

**Normal ST segment morphology:**
- **Concave upward** ("smiling"): Normal. The ST segment gently curves upward from the J-point into the T-wave upstroke
- **Flat/horizontal**: Can be normal if within amplitude limits, but less reassuring
- **Convex upward** ("frowning"): NOT normal morphology — raises concern for ischemia or injury even if amplitude is borderline

### 5.3 Early Repolarization Pattern (Benign)

- Seen in up to 2-5% of the general population, higher in young men, athletes, and individuals of African descent
- Characteristics:
  - J-point elevation with concave-upward ST elevation, typically 0.1-0.3 mV
  - Most prominent in V2-V5 (anterior distribution) or inferolateral leads
  - Notching or slurring at the J-point ("J-wave" or "Osborn-like wave")
  - Tall, concordant T-waves
  - Reciprocal ST depression in aVR
  - Stable on serial ECGs (does not evolve like STEMI)
- Note: recent data suggest that early repolarization with >0.2 mV J-point elevation in inferior leads may carry a small increase in sudden cardiac death risk ("malignant early repolarization") — but this remains controversial and the absolute risk is very low

### 5.4 Measurement Standards

- ST deviation is measured at the **J-point** or **J+60 ms** (for routine analysis) or **J+80 ms** (at slow heart rates)
- Reference baseline: **TP segment** (preferred) or **PR segment** (if TP is obscured by tachycardia)
- Measure in at least two contiguous leads showing the same deviation for clinical significance

---

## 6. Normal T-wave

### 6.1 Genesis

The T-wave represents **ventricular repolarization** (Phase 3 of the ventricular action potential).

**Why the T-wave is concordant with the QRS (upright where QRS is upright):**
- Depolarization proceeds from endocardium to epicardium (via Purkinje fibers inserted into the subendocardium)
- If repolarization followed the same direction, the T-wave would be inverted relative to QRS (opposite polarity of phase 3 vs phase 0)
- However, repolarization proceeds from **epicardium to endocardium** — the reverse direction. This is because:
  - Epicardial action potentials are shorter than endocardial action potentials
  - The epicardium repolarizes first despite depolarizing last
  - This difference is due to the higher density of $I_{to}$ in the epicardium (shorter plateau)
- Since both the direction and the polarity are reversed, they cancel out:
  - Depolarization: endo→epi, creating a positive wave toward leads facing the epicardium
  - Repolarization: epi→endo (reverse direction), with phase 3 being a negative-going potential (reverse polarity)
  - Net effect: T-wave is in the same direction as the major QRS deflection

**T-wave amplitude reflects the transmural gradient of repolarization:**
- The steeper the gradient between epicardial and endocardial APD, the taller the T-wave
- Factors that affect this gradient (sympathetic tone, heart rate, ischemia, drugs) alter T-wave morphology

### 6.2 Normal Parameters — Lead by Lead

| Lead | Expected Polarity | Amplitude Range | Morphology | Notes |
|------|------------------|-----------------|------------|-------|
| **I** | **Upright** | 0.10-0.60 mV | Asymmetric (gradual upstroke, steeper downstroke) | Always upright. Inverted T in I is always abnormal. |
| **II** | **Upright** | 0.10-0.70 mV | Asymmetric | Usually the tallest T in limb leads. Always upright in normal. |
| **III** | **Variable** (upright / flat / inverted) | 0-0.40 mV | Variable | Isolated T-wave inversion in III is a normal variant, especially in the setting of a vertical heart. T-III inversion may resolve with deep inspiration. |
| **aVR** | **Inverted** | 0.10-0.50 mV | Inverted | Always inverted. Upright T in aVR is abnormal (consider ischemia, especially LAD territory). |
| **aVL** | **Variable** (upright / flat / inverted) | 0-0.40 mV | Variable | Depends on QRS axis. Flat or inverted T in aVL is common and normal when QRS axis is vertical (+60° to +90°). Inverted T in aVL with upright QRS is abnormal. |
| **aVF** | **Upright** | 0.10-0.50 mV | Asymmetric | Usually upright. Flat or mildly inverted T in aVF with inverted T in III and normal T in II is generally benign. |
| **V1** | **Variable** (inverted / flat / upright) | 0-0.30 mV | Variable | T-wave inversion in V1 is normal in adults. Upright T in V1 is also normal, but a new upright T in V1 in the context of prior TWI may indicate posterior ischemia. |
| **V2** | **Upright** (adults), **inverted** (juvenile pattern) | 0.10-0.80 mV | Asymmetric | Normally upright by late adolescence. Persistent juvenile T-wave inversion pattern (V1-V3) is normal in females up to 30% of young adults. |
| **V3** | **Upright** | 0.10-1.00 mV | Asymmetric | Must be upright in adults (>18 years). Inverted T in V3 in adults is abnormal unless persistent juvenile pattern in young women. |
| **V4** | **Upright** | 0.20-1.20 mV | Asymmetric | Tallest T-wave in the precordial leads is usually in V4 (or V3). Must be upright. |
| **V5** | **Upright** | 0.15-0.80 mV | Asymmetric | Must be upright. T amplitude decreases from V4 to V6. |
| **V6** | **Upright** | 0.10-0.60 mV | Asymmetric | Must be upright. Inverted T in V5-V6 is always abnormal (consider ischemia, LVH with strain). |

**Normal T-wave morphology:**
- **Asymmetric**: Gradual upstroke (ascending limb), steeper downstroke (descending limb)
- The asymmetry reflects the different rates of repolarization in epicardial vs endocardial layers
- **Symmetric T-waves** (equal upstroke and downstroke) suggest abnormality: hyperacute T-waves (early STEMI), hyperkalemia, or LV hypovolemia
- T-wave amplitude should generally be at least **10% of the R-wave amplitude** in leads with dominant R (the "1/10th rule" is a rough guide, not a strict threshold)

### 6.3 T-wave Axis

- **Normal T-wave axis**: generally concordant with the QRS axis (within approximately 45° of the QRS axis in the frontal plane)
- **QRS-T angle**:
  - Frontal plane: normally <45° in men, <60° in women
  - Spatial QRS-T angle (3D): normally <105°. Widened spatial QRS-T angle is an independent predictor of cardiac events
- Discordant T-waves (T-axis far from QRS axis) suggest abnormal repolarization: ischemia, strain, electrolyte abnormalities, or primary repolarization disease (LQTS, Brugada)

---

## 7. Normal QT Interval

### 7.1 Definition and Measurement

- **Definition**: From the **onset of the QRS complex** to the **end of the T-wave** (return to baseline)
- Encompasses the total duration of ventricular depolarization AND repolarization
- **Measurement lead**: Measure in the lead with the longest QT and a clearly defined T-wave offset (usually **V2 or V3**). If uncertain, measure in multiple leads and use the longest.
- **T-wave offset determination**: Draw a tangent to the steepest part of the T-wave downslope. The intersection of this tangent with the baseline is the T-wave offset ("tangent method"). If a U-wave is present, do NOT include the U-wave in the QT measurement — measure to the nadir between T and U.

### 7.2 Rate Dependence

The QT interval shortens with increasing heart rate (shorter diastole → shorter action potential duration due to incomplete recovery of K+ channels). This mandates rate correction.

**Correction formulas** (all assume RR interval in seconds, QT in seconds, result in seconds):

**Bazett (1920):**

$$QTc_B = \frac{QT}{\sqrt{RR}}$$

- Most widely used; standard in clinical practice
- Overcorrects at high HR (>100 bpm) and undercorrects at low HR (<60 bpm)
- Despite limitations, remains the de facto clinical standard

**Fridericia (1920):**

$$QTc_F = \frac{QT}{\sqrt[3]{RR}} = \frac{QT}{RR^{1/3}}$$

- More accurate than Bazett at heart rates >90 bpm and <60 bpm
- Recommended by AHA/ACC as a preferred alternative
- Preferred in drug safety studies (ICH E14 guideline)

**Framingham / Sagie (1992):**

$$QTc_{Fram} = QT + 0.154 \times (1 - RR)$$

- Linear correction; derived from Framingham Heart Study population
- Performs well across a wide range of heart rates
- Less affected by extreme rates than Bazett

**Hodges (1983):**

$$QTc_H = QT + 1.75 \times (HR - 60)$$

where HR is in bpm and QTc is in ms.

- Linear correction using heart rate directly
- Good performance at extreme heart rates

**Recommendation for this platform:**
- Use **Fridericia** as primary (best accuracy at extreme rates, recommended by regulatory bodies)
- Report **Bazett** alongside for clinical familiarity
- Flag discrepancies between Bazett and Fridericia when HR is <50 or >100 bpm

### 7.3 Normal QTc Ranges

| Category | Normal | Borderline | Prolonged | Short |
|----------|--------|------------|-----------|-------|
| **Males** | ≤430 ms | 431-450 ms | >450 ms | <360 ms |
| **Females** | ≤450 ms | 451-470 ms | >470 ms | <370 ms |

*Note: Thresholds vary slightly across guidelines. The above follows the 2022 AHA/ACC/HRS Guideline for Ventricular Arrhythmia Management. Some references use 440/460 ms as the upper normal for males/females respectively — the system should flag values approaching any threshold.*

**Key clinical thresholds:**
- QTc >500 ms: high risk for Torsades de Pointes (TdP) — STAT alert
- QTc >600 ms: very high risk, often drug-induced or congenital LQTS — emergent
- QTc <340 ms: suggests Short QT Syndrome — flag for further evaluation

### 7.4 Factors Affecting QT/QTc (Not Disease)

| Factor | Effect on QT | Mechanism |
|--------|-------------|-----------|
| Heart rate (↑) | QT shortens | Shorter diastole → shorter APD |
| Female sex | QT longer by ~10-20 ms | Lower testosterone, different ion channel expression |
| Age (↑) | QT slightly longer | Fibrosis, reduced repolarization reserve |
| Sleep / circadian | QT longer at night | Vagal predominance |
| Postprandial | QT may shorten | Sympathetic response |
| Autonomic tone | Variable | Sympathetic shortens, parasympathetic may lengthen |

---

## 8. Normal U-wave

### 8.1 Definition
- A small, low-amplitude deflection occurring **after the T-wave** and **before the next P-wave**
- Same polarity as the preceding T-wave (upright in leads where T is upright, inverted where T is inverted)
- Best seen in **V2-V3** at slow heart rates (merged with T at faster rates)

### 8.2 Genesis (Debated)
Multiple proposed mechanisms:
- Repolarization of the Purkinje fiber network (longer APD than ventricular myocytes)
- Repolarization of the papillary muscles
- Mechanical-electrical coupling ("afterpotentials" from ventricular relaxation)
- M-cell (midmyocardial cell) repolarization
- Current consensus favors a combination of Purkinje fiber and M-cell repolarization

### 8.3 Normal Parameters
- **Amplitude**: typically 0.05-0.15 mV (0.5-1.5 mm), should be <33% of T-wave amplitude in the same lead
- **Duration**: 160-200 ms
- **Prominent U-waves (>0.15 mV)** can be normal in:
  - Sinus bradycardia (<60 bpm) — more time for U-wave to manifest
  - Athletes (high vagal tone, slow rates)
  - Young adults
- **Inverted U-waves**: always abnormal — strongly associated with myocardial ischemia (especially LAD territory), LVH, or hypertension
- **Giant U-waves** (>0.2 mV): consider hypokalemia, hypomagnesemia, drug effect (Class IA/III antiarrhythmics, digoxin)

---

## 9. Normal Variants by Demographics

### 9.1 Age-Related Normal Variants

#### Neonates (0-1 month)
| Parameter | Normal in Neonate | Reasoning |
|-----------|-------------------|-----------|
| Heart rate | 110-160 bpm | High metabolic demand, immature vagal tone |
| QRS axis | +60° to +180° (RAD) | RV dominance in utero (RV and LV equal pressure in fetal circulation) |
| R in V1 | Dominant R (R > S) | RV dominance — V1 faces the dominant chamber |
| S in V6 | Deep S | RV dominance — LV is relatively small |
| T in V1 | Upright (first 48 hrs), then inverted | T inverts in V1 by day 3-7 as pulmonary resistance drops |
| PR interval | 80-120 ms | Smaller heart, faster conduction |
| QRS duration | 50-80 ms | Smaller ventricles |
| R in V1 | Up to 2.5 mV | Normal with RV dominance |

#### Infants (1-12 months)
| Parameter | Normal |
|-----------|--------|
| Heart rate | 100-150 bpm |
| QRS axis | +10° to +125° (still rightward of adult) |
| T in V1-V3 | Inverted (normal by 1 week of age) |
| R in V1 | Decreasing over months as LV takes over dominance |
| QRS duration | 50-80 ms |

#### Children (1-12 years)
| Parameter | Normal |
|-----------|--------|
| Heart rate | 60-120 bpm (decreasing with age) |
| QRS axis | Transitions toward adult normal by age 8-12 |
| T in V1-V3 | Remains inverted until puberty — "juvenile T-wave pattern" |
| Voltages | Higher than adults (thin chest wall, heart closer to electrodes) |
| PR interval | 100-180 ms (increases with age) |
| QRS duration | 60-90 ms |
| Sinus arrhythmia | Very common, normal — RR varies >10% with respiration |

#### Adolescents (12-18 years)
| Parameter | Normal |
|-----------|--------|
| T in V1-V3 | Should become upright by mid-adolescence in males. In females, T-wave inversion in V1-V3 may persist into adulthood as a normal variant ("persistent juvenile pattern," seen in up to 3% of adult women) |
| Voltages | May be higher than adults (thin chest wall) |
| Early repolarization | Common, normal |

#### Elderly (>65 years)
| Parameter | Normal Variant |
|-----------|---------------|
| QRS axis | Shifts leftward (up to -30° may be normal) due to LV hypertrophy, fibrosis, or diaphragm elevation |
| PR interval | May extend to 200-220 ms (increased fibrosis in conduction system) |
| QRS duration | May extend to 100-110 ms |
| Voltage | May decrease (increased chest wall impedance, lung hyperinflation) |
| ST/T changes | Nonspecific ST-T changes more common; interpret with caution |
| QTc | May increase by 10-20 ms |

### 9.2 Sex-Related Normal Variants

| Parameter | Males | Females | Clinical Significance |
|-----------|-------|---------|----------------------|
| Heart rate | Slightly lower at rest | Slightly higher at rest | ~3-5 bpm difference |
| QTc | ≤430 ms normal | ≤450 ms normal | Testosterone shortens QT (higher I_Kr density). Post-menopausal women: QTc may decrease toward male range |
| ST elevation V2-V3 | ≤0.25 mV (<40y), ≤0.20 mV (≥40y) | ≤0.15 mV | Higher thresholds in men because benign ST elevation is more common |
| LVH voltage criteria | Standard Sokolow-Lyon (≤3.5 mV) | Lower thresholds used (Sokolow ≤3.2 mV, or sex-specific Cornell: R_aVL + S_V3 ≤2.0 mV in women vs ≤2.8 mV in men) | Women have lower normal voltages; using male criteria misses LVH in women |
| T-wave inversion V1-V3 | Abnormal after puberty (unless athlete) | Persistent juvenile pattern normal in up to 3% of adult women | Avoid overcalling anterior ischemia in young women |
| Early repolarization | More common (5-10% of young men) | Less common (1-2%) | Higher ST thresholds in V2-V3 for men reflect this |

### 9.3 Athletic Heart (Trained Athletes, >6 hrs/week)

Regular, intensive endurance or mixed endurance-strength training produces structural and electrical cardiac adaptations:

| ECG Finding | Prevalence in Athletes | Mechanism | Normal If... |
|------------|----------------------|-----------|-------------|
| **Sinus bradycardia** (40-60 bpm, may be as low as 30 bpm in sleep) | 50-85% | Increased vagal tone, intrinsic SA node remodeling | Asymptomatic, HR rises appropriately with exercise |
| **Sinus arrhythmia** | 50-70% | Enhanced vagal tone | Resolves with exercise |
| **1st degree AV block** (PR 200-300 ms) | 10-35% | Enhanced vagal tone at AV node | PR shortens with exercise. If PR >300 ms → further evaluation |
| **Mobitz Type I** (Wenckebach) | 2-10% (especially at night/rest) | Vagal tone | Resolves with exercise or atropine |
| **Junctional escape rhythm** | 1-2% | Vagal suppression of SA node below junctional rate | Sinus rhythm resumes with activity |
| **Incomplete RBBB** (QRS 100-120 ms, rSR' in V1) | 15-40% | RV volume loading → RV enlargement → mildly delayed RV conduction | QRS <120 ms, no strain pattern |
| **Early repolarization** (J-point elevation V2-V5 or inferolateral) | 20-50% | Vagal tone, transmural repolarization gradient | Concave-up ST, tall concordant T-waves. Not convex, not evolving |
| **LVH voltage criteria met** | 30-60% | True LV enlargement (physiologic, eccentric hypertrophy from volume loading) | No strain pattern (no ST depression/T inversion in lateral leads). If strain pattern present → investigate HCM |
| **Tall T-waves** (>1.0 mV in V2-V4) | 15-30% | Increased transmural repolarization gradient, vagal tone | Concordant with QRS, normal morphology (asymmetric), no symptoms |
| **T-wave inversion V1-V4** (anterior) | 3-5% (more common in African/Caribbean descent athletes) | Repolarization variant, RV adaptation | Concerning — must exclude ARVC, HCM. Requires further evaluation (echo, CMR) |

**What is NOT a normal athletic variant (always investigate):**
- T-wave inversion in lateral leads (V5-V6, I, aVL) unless of African/Caribbean descent
- ST depression
- Pathological Q-waves
- Complete LBBB or RBBB
- QTc >470 ms (males) or >480 ms (females)
- Epsilon waves
- Ventricular pre-excitation (delta waves)

### 9.4 Body Habitus

| Habitus | ECG Effects | Mechanism |
|---------|-------------|-----------|
| **Tall/thin (asthenic)** | Higher precordial voltages (may meet LVH voltage criteria without LVH), vertical QRS axis (+60° to +90°), P-wave may be upright and peaked in II (P-pulmonale pattern without RAE), clockwise rotation | Heart is more vertical, chest wall thin → electrodes closer to heart |
| **Obese** | Low voltage (all limb leads <0.5 mV and/or all precordial leads <1.0 mV), left axis deviation (-10° to -30°), P-wave may appear notched (mimicking LAE), poor R-wave progression, T-wave flattening in inferior leads, sinus tachycardia | Increased distance from heart to electrodes (adipose tissue), elevated diaphragm pushing heart leftward and horizontally |
| **Pregnancy** | Sinus tachycardia (HR 80-100 bpm normal), LAD (axis shifts leftward by 15-20° as uterus elevates diaphragm), small Q in III and aVF (positional), low-amplitude T-wave changes (flattened/inverted in III, V1-V2), frequent PACs/PVCs | Diaphragm elevation, increased blood volume, hyperdynamic circulation, hormonal changes |
| **Pectus excavatum** | Rightward QRS axis shift, incomplete RBBB pattern, poor R-wave progression, T-wave inversion V1-V3 | Anatomical compression of the heart, displacement of the heart leftward and posteriorly |

### 9.5 Racial/Ethnic Variants

| Population | Common Normal ECG Variants | Notes |
|------------|---------------------------|-------|
| **African descent** | Early repolarization with J-point elevation (up to 0.4 mV in V2-V4), T-wave inversion V1-V4 (especially young males), higher voltages (may meet LVH criteria without true LVH), Brugada-like pattern in V1-V2 | Consider higher voltage thresholds for LVH diagnosis. T-wave inversion in V1-V4 in young athletes of African descent is common and usually benign but must exclude HCM/ARVC |
| **Asian descent** | Slightly lower voltages on average, higher prevalence of early repolarization | Population-specific voltage criteria may be needed |

---

## 10. The Normal 12-Lead Master Reference Table

This is the comprehensive ground truth table that every disease node compares against. All values represent typical adults (18-65 years), standard calibration (10 mm/mV, 25 mm/s).

### 10.1 Lead I

| Parameter | Normal Value | Alert Threshold |
|-----------|-------------|-----------------|
| **P-wave** polarity | Upright | Inverted → ectopic atrial rhythm or lead reversal |
| **P-wave** amplitude | 0.05-0.20 mV | >0.25 mV |
| **P-wave** duration | 60-120 ms | >120 ms |
| **PR interval** | 120-200 ms | <120 ms or >200 ms |
| **Q wave** | Septal q: <40 ms, <0.3 mV, <25% of R | Pathologic Q: ≥40 ms or ≥25% of R |
| **R wave** amplitude | 0.2-1.0 mV | >1.3 mV (consider LVH, lateral) |
| **S wave** depth | 0-0.3 mV | >0.5 mV (consider RVH, RAD) |
| **QRS** duration | 80-100 ms | >120 ms |
| **QRS** morphology | qRs or Rs | QS pattern, wide/notched |
| **ST segment** | Isoelectric (±0.1 mV) | Elevation >0.1 mV, depression >0.05 mV |
| **T-wave** polarity | Upright | Inverted → always abnormal |
| **T-wave** amplitude | 0.10-0.60 mV | Flat (<0.05 mV) or >0.80 mV |

### 10.2 Lead II

| Parameter | Normal Value | Alert Threshold |
|-----------|-------------|-----------------|
| **P-wave** polarity | Upright | Inverted → not sinus rhythm |
| **P-wave** amplitude | 0.05-0.25 mV | >0.25 mV (RAE/P-pulmonale) |
| **P-wave** duration | 60-120 ms | >120 ms (LAE) |
| **PR interval** | 120-200 ms | <120 ms or >200 ms |
| **Q wave** | Small q possible: <40 ms, <0.3 mV | ≥40 ms or >0.3 mV (inferior MI) |
| **R wave** amplitude | 0.3-1.5 mV | >2.0 mV |
| **S wave** depth | 0-0.5 mV | >0.8 mV |
| **QRS** duration | 80-100 ms | >120 ms |
| **QRS** morphology | qRs, Rs, or R | QS pattern |
| **ST segment** | Isoelectric (±0.1 mV) | Elevation >0.1 mV, depression >0.05 mV |
| **T-wave** polarity | Upright | Inverted → always abnormal |
| **T-wave** amplitude | 0.10-0.70 mV | Flat (<0.05 mV) or peaked (>1.0 mV, consider hyperkalemia) |

### 10.3 Lead III

| Parameter | Normal Value | Alert Threshold |
|-----------|-------------|-----------------|
| **P-wave** polarity | Variable (upright / flat / inverted) | Isolated inversion may be normal |
| **P-wave** amplitude | 0-0.20 mV | >0.25 mV |
| **P-wave** duration | 60-120 ms | >120 ms |
| **PR interval** | 120-200 ms | <120 ms or >200 ms |
| **Q wave** | Q can be normal: <40 ms; may appear deeper with expiration. Q-III that diminishes with inspiration is benign | Pathologic Q: ≥40 ms AND present in aVF and/or II |
| **R wave** amplitude | 0.1-1.0 mV | Highly variable with axis |
| **S wave** depth | 0-1.0 mV | Deep S with LAD is normal variant |
| **QRS** duration | 80-100 ms | >120 ms |
| **QRS** morphology | rS, Rs, qRs, QS, or Qr | All can be normal variants |
| **ST segment** | Isoelectric (±0.1 mV) | Elevation >0.1 mV (especially if also in II and aVF) |
| **T-wave** polarity | Variable (upright / flat / inverted) | Isolated T inversion in III is normal |
| **T-wave** amplitude | 0-0.40 mV | Deeply inverted (>0.5 mV) with associated inferior changes |

### 10.4 Lead aVR

| Parameter | Normal Value | Alert Threshold |
|-----------|-------------|-----------------|
| **P-wave** polarity | Inverted | Upright → not sinus or lead reversal |
| **P-wave** amplitude | 0.05-0.20 mV (inverted) | >0.25 mV |
| **PR interval** | 120-200 ms | <120 or >200 ms |
| **Q wave / QRS** | Predominantly negative: QS or rS | Dominant R (R >0.3 mV or R:S >1) → abnormal (TCA toxicity, acute RV strain, ventricular origin) |
| **R wave** amplitude | 0-0.3 mV | >0.3 mV |
| **S wave / QS** depth | 0.3-1.5 mV | — |
| **QRS** duration | 80-100 ms | >120 ms |
| **ST segment** | May have ST depression up to 0.1 mV (reciprocal to normal inferior ST) | ST elevation >0.1 mV (especially >0.15 mV) → suggests diffuse subendocardial ischemia, LMCA occlusion, or severe 3-vessel disease |
| **T-wave** polarity | Inverted | Upright → abnormal (consider acute ischemia) |
| **T-wave** amplitude | 0.10-0.50 mV (inverted) | Upright T or large amplitude |

### 10.5 Lead aVL

| Parameter | Normal Value | Alert Threshold |
|-----------|-------------|-----------------|
| **P-wave** polarity | Variable (upright / flat / inverted) | Depends on P-axis |
| **P-wave** amplitude | 0-0.15 mV | >0.25 mV |
| **PR interval** | 120-200 ms | <120 ms or >200 ms |
| **Q wave** | Septal q possible: <40 ms, <0.3 mV | Pathologic Q: ≥40 ms or ≥25% of R (consider high lateral MI) |
| **R wave** amplitude | 0.1-1.0 mV | >1.1 mV (Cornell LVH criterion) |
| **S wave** depth | 0-0.6 mV | — |
| **QRS** duration | 80-100 ms | >120 ms |
| **QRS** morphology | qRs (horizontal axis) or rS (vertical axis) | Axis-dependent |
| **ST segment** | Isoelectric (±0.1 mV) | Elevation >0.1 mV (high lateral STEMI), depression >0.05 mV |
| **T-wave** polarity | Variable: upright if QRS is upright, may be flat/inverted if rS | Inverted with upright QRS → abnormal (ischemia, LVH strain) |
| **T-wave** amplitude | 0-0.40 mV | Deeply inverted with upright QRS |

### 10.6 Lead aVF

| Parameter | Normal Value | Alert Threshold |
|-----------|-------------|-----------------|
| **P-wave** polarity | Upright | Inverted → ectopic atrial/junctional |
| **P-wave** amplitude | 0.05-0.20 mV | >0.25 mV (RAE) |
| **PR interval** | 120-200 ms | <120 ms or >200 ms |
| **Q wave** | Small q possible: <40 ms, <0.3 mV | Pathologic Q: ≥40 ms or ≥25% of R (especially if Q also in II and III → inferior MI) |
| **R wave** amplitude | 0.2-1.5 mV | >2.0 mV |
| **S wave** depth | 0-0.5 mV | — |
| **QRS** duration | 80-100 ms | >120 ms |
| **QRS** morphology | qRs, Rs, or R | QS pattern (with Q in II and III → inferior MI) |
| **ST segment** | Isoelectric (±0.1 mV) | Elevation >0.1 mV (inferior STEMI), depression >0.05 mV |
| **T-wave** polarity | Upright | Inverted (with TWI in II/III → always abnormal) |
| **T-wave** amplitude | 0.10-0.50 mV | Flat or deeply inverted |

### 10.7 Lead V1

| Parameter | Normal Value | Alert Threshold |
|-----------|-------------|-----------------|
| **P-wave** polarity | Biphasic (+/-) | Deeply negative terminal force: depth >0.1 mV AND duration >40 ms → LAE |
| **P-wave** amplitude | Positive: ≤0.15 mV; Negative: ≤0.10 mV | Positive >0.15 mV (RAE); Negative PTF >0.04 mm·s (LAE) |
| **PR interval** | 120-200 ms | <120 ms (check for delta wave → WPW) |
| **Q wave** | Absent (no Q normally in V1) | Any Q wave in V1 → consider septal MI, LBBB |
| **R wave** amplitude | 0.1-0.6 mV (small r) | R >0.6 mV or R:S >1 → consider RVH, posterior MI, WPW Type A |
| **S wave** depth | 0.3-1.8 mV (deep S dominant) | S <0.2 mV (lost S → check for RBBB or RVH) |
| **R:S ratio** | <1 (S > R) | R:S ≥1 → abnormal |
| **QRS** duration | 80-100 ms | >120 ms (check for rSR' → RBBB; wide QS → LBBB) |
| **QRS** morphology | rS | rSR' → RBBB; QS → may be normal variant or LBBB; rsR' with QRS <120 ms → incomplete RBBB |
| **ST segment** | Isoelectric or slightly depressed (≤0.05 mV) | Elevation >0.15-0.25 mV (age/sex dependent), depression >0.1 mV |
| **T-wave** polarity | Variable: inverted, flat, or upright (all normal) | Newly upright if previously inverted (posterior ischemia) |
| **T-wave** amplitude | 0-0.30 mV | Deeply inverted (>0.5 mV) with rSR' pattern → RV strain |

### 10.8 Lead V2

| Parameter | Normal Value | Alert Threshold |
|-----------|-------------|-----------------|
| **P-wave** polarity | Upright or biphasic | Deeply negative → LAE |
| **P-wave** amplitude | 0.05-0.15 mV | >0.25 mV |
| **PR interval** | 120-200 ms | <120 ms or >200 ms |
| **Q wave** | Absent normally | Any Q wave in V2 → always pathologic (anterior/septal MI) |
| **R wave** amplitude | 0.2-1.0 mV (growing r) | R > S (early transition → RVH, posterior MI, WPW) |
| **S wave** depth | 0.5-2.5 mV | — |
| **R:S ratio** | <1 (S still dominant, but R larger than V1) | R:S ≥1 in V2 → early transition |
| **QRS** duration | 80-100 ms | >120 ms |
| **QRS** morphology | rS (r growing) | RS or Rs → early transition |
| **ST segment** | Isoelectric; may have up to 0.25 mV elevation (males <40y) | Elevation exceeding age/sex thresholds |
| **T-wave** polarity | Upright (adults) | Inverted → abnormal in adult males; may be normal in young females (persistent juvenile pattern) |
| **T-wave** amplitude | 0.10-0.80 mV | Peaked (>1.0 mV) → hyperkalemia; flat/inverted → ischemia |

### 10.9 Lead V3

| Parameter | Normal Value | Alert Threshold |
|-----------|-------------|-----------------|
| **P-wave** polarity | Upright | — |
| **P-wave** amplitude | 0.05-0.15 mV | >0.25 mV |
| **PR interval** | 120-200 ms | <120 ms or >200 ms |
| **Q wave** | Tiny q possible, uncommon | Q ≥40 ms or deep Q → anterior MI |
| **R wave** amplitude | 0.3-1.5 mV | — |
| **S wave** depth | 0.3-1.5 mV | — |
| **R:S ratio** | ≈1 (transition zone) | — |
| **QRS** duration | 80-100 ms | >120 ms |
| **QRS** morphology | RS (R ≈ S, equiphasic) | PRWP if R <0.3 mV |
| **ST segment** | Isoelectric; mild elevation acceptable (same thresholds as V2) | Exceeding age/sex thresholds |
| **T-wave** polarity | Upright | Inverted → abnormal in adults (Wellens if deep and symmetric) |
| **T-wave** amplitude | 0.10-1.00 mV | Peaked (>1.0 mV) → hyperacute T or hyperkalemia |

### 10.10 Lead V4

| Parameter | Normal Value | Alert Threshold |
|-----------|-------------|-----------------|
| **P-wave** polarity | Upright | — |
| **P-wave** amplitude | 0.05-0.15 mV | >0.25 mV |
| **PR interval** | 120-200 ms | <120 ms or >200 ms |
| **Q wave** | Small septal q possible | Pathologic Q ≥40 ms |
| **R wave** amplitude | 0.5-2.5 mV (often tallest R of all leads) | >2.6 mV (LVH) |
| **S wave** depth | 0.1-0.8 mV (small s) | — |
| **R:S ratio** | >1 (R now dominant) | — |
| **QRS** duration | 80-100 ms | >120 ms |
| **QRS** morphology | Rs or qRs | QS → anterior MI |
| **ST segment** | Isoelectric (±0.1 mV) | Elevation >0.1 mV, depression >0.05 mV |
| **T-wave** polarity | Upright | Inverted → abnormal (anterior ischemia, LVH strain) |
| **T-wave** amplitude | 0.20-1.20 mV (tallest T often in V4) | Peaked (>1.5 mV); deeply inverted |

### 10.11 Lead V5

| Parameter | Normal Value | Alert Threshold |
|-----------|-------------|-----------------|
| **P-wave** polarity | Upright | — |
| **P-wave** amplitude | 0.05-0.15 mV | >0.25 mV |
| **PR interval** | 120-200 ms | <120 ms or >200 ms |
| **Q wave** | Septal q: <40 ms, <0.3 mV, <25% of R | Pathologic Q (absent q also notable → LBBB) |
| **R wave** amplitude | 0.5-2.5 mV | >2.6 mV (Sokolow LVH: S_V1 + R_V5 >3.5 mV) |
| **S wave** depth | 0.1-0.5 mV (small s) | — |
| **R:S ratio** | >1 (R dominant) | — |
| **QRS** duration | 80-100 ms | >120 ms |
| **QRS** morphology | qRs | Absent septal q with wide QRS → LBBB |
| **ST segment** | Isoelectric (±0.1 mV) | Elevation >0.1 mV (lateral STEMI), depression with TWI → LVH strain |
| **T-wave** polarity | Upright | Inverted → always abnormal (ischemia or strain) |
| **T-wave** amplitude | 0.15-0.80 mV | Flat or inverted |

### 10.12 Lead V6

| Parameter | Normal Value | Alert Threshold |
|-----------|-------------|-----------------|
| **P-wave** polarity | Upright | — |
| **P-wave** amplitude | 0.05-0.15 mV | >0.25 mV |
| **PR interval** | 120-200 ms | <120 ms or >200 ms |
| **Q wave** | Septal q: <40 ms, <0.3 mV, <25% of R | Pathologic Q; absent septal q → consider LBBB |
| **R wave** amplitude | 0.3-2.0 mV (usually < R in V5) | >2.6 mV |
| **S wave** depth | 0-0.3 mV | — |
| **R:S ratio** | >1 (R dominant) | — |
| **QRS** duration | 80-100 ms | >120 ms |
| **QRS** morphology | qRs | Absent q, wide QRS → LBBB |
| **ST segment** | Isoelectric (±0.1 mV) | Elevation >0.1 mV, depression >0.05 mV |
| **T-wave** polarity | Upright | Inverted → always abnormal |
| **T-wave** amplitude | 0.10-0.60 mV | Flat or inverted |

---

## 11. Sinus Rhythm Diagnostic Criteria

To confirm the rhythm is **Normal Sinus Rhythm (NSR)**, ALL of the following must be met:

| Criterion | Requirement | How to Verify |
|-----------|-------------|---------------|
| **1. P-wave present before every QRS** | Each QRS is preceded by a P-wave | Visual inspection; P:QRS ratio = 1:1 |
| **2. QRS present after every P-wave** | Each P-wave is followed by a QRS | No dropped beats |
| **3. P-wave upright in II, inverted in aVR** | Confirms atrial depolarization originates from SA node region | P-wave polarity in leads II and aVR |
| **4. P-wave axis 0° to +75°** | Sinus origin confirmed | Upright in I and II |
| **5. Constant P-wave morphology** | Same focus for each beat | All P-waves identical in each lead |
| **6. Constant PR interval** | Normal AV conduction | PR interval same (±10%) for each beat |
| **7. PR interval 120-200 ms** | Normal range | Direct measurement |
| **8. Heart rate 60-100 bpm** | Normal sinus rate | 60/RR interval (in seconds) |
| **9. Regular R-R intervals** | Sinus regularity | R-R variation <10% (except sinus arrhythmia — see below) |

**Sinus arrhythmia** (R-R variation >10%, typically respiratory) is a normal variant — the rhythm is still sinus origin. Identified by: phasic RR variation correlating with respiration (RR shortens with inspiration, lengthens with expiration). More common in young adults, athletes, and during sleep.

---

## 12. Signal Processing Reference Values for Algorithm Validation

These values guide the ECG signal processing pipeline (Node 2.7.200 → SDA-1 feature extraction).

### 12.1 Normal ECG Signal Characteristics

| Parameter | Normal Range | Notes |
|-----------|-------------|-------|
| **Signal bandwidth** | 0.05-150 Hz (diagnostic), 0.5-40 Hz (monitoring) | Diagnostic mode must preserve low-frequency ST and high-frequency QRS notching |
| **Sampling rate** | ≥500 Hz (recommended 1000 Hz) | PTB-XL: 500 Hz; adequate for standard analysis |
| **Amplitude resolution** | ≤5 µV (12-bit ADC minimum) | PTB-XL: sufficient resolution |
| **Baseline wander frequency** | <0.5 Hz | Remove with high-pass filter or polynomial fitting |
| **Powerline interference** | 50 Hz (Europe) or 60 Hz (Americas) | Remove with notch filter |
| **Normal QRS amplitude** | 0.5-3.0 mV (largest deflection in any lead) | <0.5 mV in all limb leads → low voltage |
| **Normal peak-to-peak noise** | <0.05 mV (after filtering) | SNR >20 dB for reliable analysis |

### 12.2 Fiducial Point Normal Intervals (for ECGdeli Validation)

These intervals between fiducial points (FPT columns) should be validated against these ranges:

| Interval | FPT Columns | Normal Range | Notes |
|----------|-------------|-------------|-------|
| P-wave onset to P-peak | Pon(0) → Ppeak(1) | 30-60 ms | First half of P-wave |
| P-peak to P-wave offset | Ppeak(1) → Poff(2) | 30-60 ms | Second half of P-wave |
| P-wave total duration | Pon(0) → Poff(2) | 60-120 ms | Entire P-wave |
| PR interval | Pon(0) → QRSon(3) | 120-200 ms | Atrial + AV delay |
| PR segment | Poff(2) → QRSon(3) | 50-120 ms | AV nodal delay only |
| QRS duration | QRSon(3) → QRSoff(7) | 80-100 ms | Ventricular depolarization |
| Q-wave duration | QRSon(3) → Q(4) offset | <40 ms | Normal septal Q |
| R-wave peak time (V6) | QRSon(3) → R(5) | ≤45 ms | Intrinsicoid deflection |
| ST segment | QRSoff(7) → Ton(9) | 80-120 ms | Early repolarization plateau |
| QT interval | QRSon(3) → Toff(11) | 350-440 ms (rate dependent) | Total ventricular electrical activity |
| T-wave onset to T-peak | Ton(9) → Tpeak(10) | 100-180 ms | Ascending T limb |
| T-peak to T-offset | Tpeak(10) → Toff(11) | 60-120 ms | Descending T limb |
| T-peak to T-end (Tpe) | Tpeak(10) → Toff(11) | 60-100 ms | Transmural dispersion of repolarization; >100 ms increases arrhythmic risk |

---

## 6A. Agent Assignment

**Architecture:** Option E — 3 Parallel Phase 1 Specialists + 1 Sequential CDS (Node 2.1 Gate Passed 2026-03-27)

| Agent | Role for Normal ECG Reference | Key Features Used |
|-------|--------------------------|-------------------|
| **RRC** (Rhythm/Rate/Conduction) | Queries this reference for normal rate, rhythm, and conduction baselines | Normal sinus rhythm criteria (rate 60-100bpm, P-wave axis 0-75°, PR 120-200ms, QRS <120ms); normal axis ranges; normal P-wave morphology parameters |
| **IT** (Ischemia/Territory) | Queries this reference for normal ST segment and T-wave baselines by lead | Normal ST segment (isoelectric ±0.5mm in limb leads; ±1mm in precordial leads); normal T-wave polarity by lead; lead-specific normal variant ST elevation values |
| **MR** (Morphology/Repolarization) | Queries this reference for normal morphology thresholds | Normal QRS morphology by lead (R/S ratios, Q-wave limits, R-wave progression); normal T-wave amplitude and polarity; normal QTc ranges; normal U-wave criteria; normal variant patterns (early repolarization, juvenile T-wave inversions) |
| **CDS** (Cross-Domain Synthesis) | Uses this reference to determine "Normal ECG" output | When all three Phase 1 agents report findings within normal ranges as defined by this reference, CDS generates a "Normal ECG" interpretation; uses normal variant section to distinguish pathological from normal variant findings |

### Primary Agent
All three Phase 1 agents use this reference equally as the baseline for abnormality determination. This is the foundational reference for all agent comparisons — every finding is assessed as normal or abnormal relative to the parameters in this file.

### Cross-Domain Hints
No cross_domain_hints are generated from this reference file. Each Phase 1 agent queries it internally as the baseline normal standard. When all Phase 1 outputs fall within normal ranges defined here, CDS generates a "Normal ECG" conclusion without cross-domain conflict resolution.

### CDS Specific Role
CDS uses the normal ECG reference as the final arbiter for "Normal ECG" output generation. When RRC, IT, and MR all return findings within normal ranges as defined in this reference, CDS generates a normal ECG interpretation. CDS also uses the normal variant section of this reference to reclassify findings initially flagged by Phase 1 agents (e.g., early repolarization, juvenile T-wave inversions in young patients, sinus arrhythmia) as expected variants rather than pathology. CDS applies demographic-adjusted normal ranges (age, sex) from this reference to ensure that borderline findings are interpreted with appropriate context.

---

## 13. References

### Guidelines
- Thygesen K, et al. Fourth Universal Definition of Myocardial Infarction (2018). *Circulation*. 2018;138:e618-e651.
- Al-Khatib SM, et al. 2017 AHA/ACC/HRS Guideline for Management of Patients With Ventricular Arrhythmias. *Circulation*. 2018;138:e272-e391.
- Rautaharju PM, et al. AHA/ACCF/HRS Recommendations for the Standardization and Interpretation of the Electrocardiogram: Part IV. *Circulation*. 2009;119:e241-e250.
- Sharma S, et al. International Recommendations for Electrocardiographic Interpretation in Athletes. *JACC*. 2017;69:1057-1075.
- Macfarlane PW, et al. The Normal Electrocardiogram and Vectorcardiogram. In: *Comprehensive Electrocardiology*, 2nd ed. Springer; 2010.

### Textbooks (RAG Source Priority)
- Wagner GS, Strauss DG. *Marriott's Practical Electrocardiography*, 13th ed. Wolters Kluwer; 2021.
- Goldberger AL, et al. *Goldberger's Clinical Electrocardiography: A Simplified Approach*, 10th ed. Elsevier; 2024.
- Surawicz B, Knilans TK. *Chou's Electrocardiography in Clinical Practice*, 6th ed. Saunders; 2008.
- Hampton JR. *The ECG Made Easy*, 9th ed. Elsevier; 2019.

### Key Papers
- Surawicz B, et al. AHA/ACCF/HRS Recommendations for the Standardization and Interpretation of the Electrocardiogram: Part III: Intraventricular Conduction Disturbances. *JACC*. 2009;53:976-981.
- Rautaharju PM, et al. Normal Standards for QT and QTc Intervals Derived from a Large Ethnically Diverse Population. *Heart Rhythm*. 2014;11:2027-2034.
- Postema PG, Wilde AA. The Measurement of the QT Interval. *Curr Cardiol Rev*. 2014;10:287-294.
- Mason JW, et al. Electrocardiographic Reference Ranges Derived from 79,743 Ambulatory Subjects. *J Electrocardiol*. 2007;40:228-234.
