# Pacemaker Rhythms (AAI, VVI, DDD, CRT) — ECG Manifestation from First Principles

**Node:** 2.7.106
**SDA:** SDA-2 (Diagnosis & Agentic Core) — shared resource for SDA-1, SDA-3, SDA-4
**Status:** Research Complete
**PGMR:** Required
**Date:** 2026-03-27

---

## 1. Pathophysiology Root Cause

### 1.1 Why Pacemakers Are Implanted
Pacemakers substitute for failed intrinsic cardiac pacing and conduction:
- **Sick sinus syndrome (SSS):** Sinus node fails to fire reliably → pauses, bradycardia, tachy-brady syndrome. AAI or DDD pacing.
- **AV block (2° Mobitz II or 3°):** AV node or His-Purkinje fails to conduct. VVI or DDD pacing.
- **LBBB with dilated cardiomyopathy (CRT indication):** Dyssynchronous LV contraction due to delayed lateral wall activation. Biventricular (CRT) pacing to resynchronize.
- **Long QT / channelopathies:** Rate support pacing to suppress bradycardia-dependent arrhythmias (pacing floor 70–80 bpm to shorten QT).

### 1.2 NBG Code Explained
The NBG (North American Society of Pacing and Electrophysiology / British Pacing Group) pacemaker code describes pacemaker function:
- **Position 1:** Chamber Paced — A (Atrium), V (Ventricle), D (Dual = both)
- **Position 2:** Chamber Sensed — A, V, D, O (None)
- **Position 3:** Response to sensing — I (Inhibit), T (Trigger), D (Dual = Inhibit + Trigger), O (None)
- **Position 4:** Rate modulation — R (rate-responsive) or O
- **Position 5:** Multisite pacing — A (atrial), V (ventricular), D (dual), O (none)

### 1.3 Electrophysiological Consequence of Ventricular Pacing
When a pacemaker stimulates the right ventricular apex, depolarization spreads via slow cell-to-cell conduction (not the fast His-Purkinje system). This produces a wide, bizarre QRS — identical in appearance to LBBB because the LV is activated late via myocardial (not Purkinje) conduction. This is the most important ECG consequence of ventricular pacing. The secondary ST/T changes of LBBB (discordant ST-T changes) are also present — and this is why the modified Sgarbossa criteria are required to detect ischemia in a paced rhythm.

---

## 2. ECG Presentation — Lead by Lead

### 2.1 Diagnostic Criteria by Pacing Mode

| Pacing Mode | Pacing Spike Location | QRS Morphology | Notes |
|---|---|---|---|
| AAI | Before P wave | Normal (narrow) QRS | AV conduction intact; ventricular conduction via native His-Purkinje |
| VVI | Before QRS (no preceding spike-P) | Wide LBBB-morphology QRS | P waves may be dissociated (AV dissociation) |
| DDD — A-paced, V-paced | Spike before P; spike before QRS | Wide paced QRS | Full dual-chamber pacing |
| DDD — A-sensed, V-paced | No atrial spike; spike before QRS | Wide paced QRS (sensed P conducts to paced V) | Sensed sinus P triggers ventricular pacing |
| DDD — A-paced, V-sensed | Spike before P; no ventricular spike | Narrow intrinsic QRS | Atrial paced, ventricle conducts natively (intact AV node) |
| DDD — A-sensed, V-sensed | No spikes (both inhibited) | Fully intrinsic P and QRS | Adequate intrinsic rate inhibits both channels |
| CRT/BiV | Before QRS (may see 2 spikes or single fused) | Narrowed QRS (vs. single-site VVI) | Both RV and LV paced; LBBB correction |

### 2.2 Lead-by-Lead Manifestation (RV Apical Pacing — VVI/DDD Ventricular Channel)

| Lead | Expected Finding | Notes |
|---|---|---|
| I | Negative QRS (broad) | RV apex pacing → vector points rightward-superior; lead I records leftward → negative |
| II | Positive or biphasic wide QRS | Variable |
| III | Positive wide QRS | |
| aVR | Positive QRS (tall broad R) | Diagnostic of RV apical pacing — positive aVR QRS in LBBB morphology |
| aVL | Negative QRS | |
| aVF | Positive QRS | Inferior direction of activation from apical pacing |
| V1 | QS or rS (LBBB-like) | Small r or absent; broad S |
| V2 | QS or rS | Deep S, no R |
| V3 | QS or rS transitioning | |
| V4 | Broad R beginning | Transition zone |
| V5 | Broad monophasic R | LBBB morphology |
| V6 | Broad monophasic R, no S | Classic LBBB appearance; pacing spike precedes it |
| ST-T | Discordant (opposite to QRS) in all leads | Expected secondary change; baseline for Sgarbossa |

### 2.3 Key Leads
- **V1:** QS or rS pattern confirms LBBB morphology (RV apical pacing expected pattern)
- **aVR:** Positive QRS (broad R) confirms ventricular pacing from RV apex
- **I:** Negative broad QRS confirms RV apical pacing axis
- **Any lead:** Concordant ST changes = ischemia (Sgarbossa criterion 1)

### 2.4 Beat-by-Beat Considerations
In DDD mode, each beat must be categorized: A-paced or A-sensed? V-paced or V-sensed? The combination determines what the QRS will look like. In a single rhythm strip, multiple combinations may appear (e.g., patient transitions from intrinsic sinus rhythm to paced rhythm as HR drops below lower rate limit). The system must classify each beat's pacing state individually.

---

## 3. Morphology Details

### 3.1 Pacing Spike Detection
Pacing spikes are vertical artifact deflections. Unipolar pacing leads produce large spikes (1–2 mV, visible in all leads). Bipolar pacing leads produce tiny spikes (often <0.2 mV, may be invisible in many leads and visible only in one or two leads). The system must not require visible spikes to diagnose paced rhythm — if QRS morphology is consistent with paced rhythm (LBBB + clinical context), flag as possible paced rhythm even without visible spikes.

### 3.2 CRT (Biventricular) Pacing Morphology
CRT uses two ventricular leads (RV apex and LV lateral wall via coronary sinus). Simultaneous or near-simultaneous activation of both ventricles produces a NARROWER QRS than single-site RV pacing. The QRS may approach normal width (120–130 ms). A dominant R in V5/V6 with an rS in V1 is common in CRT. If the CRT QRS is wide (>150 ms), this may indicate loss of LV capture (only RV pacing) or RV lead failure.

### 3.3 Fusion and Pseudofusion Beats
- **Fusion beat:** Intrinsic depolarization and paced depolarization occur simultaneously; QRS is intermediate morphology between native and paced — narrower and more "normal-looking" than fully paced beat. Normal behavior in VVI.
- **Pseudofusion beat:** Pacing spike falls during intrinsic depolarization but does not contribute; QRS looks like intrinsic beat with a spike artifact superimposed. Normal behavior; not oversensing.

### 3.4 Sgarbossa Criteria Applied to Paced Rhythm
Original Sgarbossa criteria were developed for LBBB but apply directly to paced rhythms because the electrical substrate (wide complex with discordant ST-T) is identical:
1. **Concordant ST elevation ≥1 mm** (ST elevates in same direction as QRS) in any lead → 5 points → highly specific for ischemia
2. **Concordant ST depression ≥1 mm** in V1–V3 → 3 points → ischemia
3. **Excessively discordant ST elevation ≥5 mm** (ST elevates opposite to QRS by ≥5 mm) → 2 points → less specific

Modified Sgarbossa (Smith modification): use a ratio — if ST/S ratio (discordant ST elevation divided by preceding S-wave depth) ≥ 0.25, consider ischemia. This replaces the 5 mm absolute threshold with a proportional criterion and is more sensitive.

### 3.5 Pacemaker Malfunction Types

| Malfunction | ECG Finding | Cause |
|---|---|---|
| Failure to capture | Pacing spike without subsequent QRS (or P wave in AAI) | Lead dislodgement, elevated threshold, battery depletion |
| Failure to sense (undersensing) | Pacing spike during intrinsic beat (spike falls inside QRS or T wave) | Sensing threshold too high; lead issue |
| Oversensing | Pacemaker pauses (long RR); no spike when expected | Pacemaker sensing T waves, myopotentials, or EMI as QRS → inhibits output |
| Pacemaker-mediated tachycardia (PMT) | Regular tachycardia at upper rate limit in DDD pacemaker | Retrograde P wave sensed by atrial channel → triggers ventricular pacing → loop |
| Runaway pacemaker | Very fast pacing rate (>180 bpm) | Battery failure; rare |
| Exit block | Prolonged spike-to-capture latency; intermittent capture | Elevated threshold at lead tip |

### 3.6 Rate-Responsive Pacing (VVIR, DDDR)
The "R" modifier means the pacemaker increases its pacing rate with activity (accelerometer or minute ventilation sensor). On ECG: pacing rate increases with ambulation/exercise. If the pacemaker paces at 110 bpm during activity, this is not pathological tachycardia — it is rate-response behavior. Clinical context (patient ambulatory vs. sedentary) required.

### 3.7 AAI Mode ECG
Atrial pacing: spike before P wave; normal narrow QRS (AV conduction intact). The QRS morphology is the patient's native QRS. If QRS is wide in AAI pacing, this indicates aberrant conduction or underlying bundle branch block — not a pacing effect.

---

## 4. Differential Diagnosis

### 4.1 Mimics

| Condition | ECG Overlap | Key Differentiator |
|---|---|---|
| LBBB (intrinsic) | Wide QRS, LBBB morphology, discordant ST-T | No pacing spikes; no pacemaker history; QRS initiation without spike artifact |
| Accelerated idioventricular rhythm (AIVR) | Wide QRS, similar to paced | No pacing spikes; rate typically 60–80 bpm; pattern different from pacing |
| WPW (Type B) | Wide QRS, delta wave, LBBB-like | Delta wave (slurred QRS onset); short PR; no spike; irregular when AF coexists |
| Ventricular tachycardia (VT) | Wide QRS, rapid | Rate >100 bpm; AV dissociation; different morphological criteria; no pacing spike |
| Hyperkalemia | Wide QRS | Peaked T waves; sine wave progression; clinical context; potassium level |

### 4.2 Coexisting Conditions
Ischemia in paced patients: the most dangerous diagnostic trap. ST elevation ≥1 mm concordant in any lead is STEMI until proven otherwise regardless of pacing. The system must apply Sgarbossa/modified Sgarbossa to every paced ECG where ischemia is on the clinical differential. Paced rhythm does not protect against STEMI — it hides it.

---

## 5. STAT Classification

| Presentation | Classification | Rationale |
|---|---|---|
| Stable paced rhythm, expected morphology | **Routine** | Normal pacemaker function |
| Failure to capture (spike without QRS) | **URGENT** | Pacemaker malfunction; patient may be pacemaker-dependent |
| Failure to capture + bradycardia | **STAT** | Patient may be pacemaker-dependent; bradycardia → hemodynamic compromise |
| Runaway pacemaker (>180 bpm paced) | **STAT** | Rare; magnet application needed |
| Pacemaker-mediated tachycardia | **Urgent** | Apply magnet to interrupt loop |
| Concordant ST elevation ≥1 mm in paced rhythm | **STAT — STEMI equivalent** | Sgarbossa criterion met; activate cath team |
| Concordant ST depression V1–V3 in paced rhythm | **STAT** | Posterior or anterior ischemia; evaluate urgently |
| Oversensing with pauses | **Urgent** | Risk of asystole if pacemaker-dependent |

---

## 6. Reasoning Complexity Analysis

### 6.1 Pattern Recognition Challenge
Recognizing paced rhythm is straightforward when spikes are visible. The challenge arises when bipolar spikes are invisible — the system must recognize paced morphology (LBBB + right axis in limb leads + aVR positive) without relying on spike detection.

### 6.2 Per-Beat Classification in DDD Mode
DDD can produce four different combinations of paced/sensed in a single rhythm strip. The system must classify each beat individually and explain the composite rhythm (e.g., "Beats 1–3: A-sensed, V-paced; Beat 4: A-sensed, V-sensed [intrinsic conduction]; Beats 5–8: A-paced, V-paced").

### 6.3 Sgarbossa Application
Every ventricular-paced or LBBB ECG where ischemia is possible must have Sgarbossa criteria applied. The modified Sgarbossa (Smith modification, ST/S ratio ≥0.25) requires measuring ST elevation amplitude and S-wave depth in each lead. This is a quantitative measurement task — computable from ECGdeli waveform data.

### 6.4 Malfunction Detection
Malfunction patterns (failure to capture, failure to sense, oversensing, PMT) require beat-by-beat spike-QRS relationship analysis. The system must measure spike-to-capture latency, spike-to-R interval consistency, and expected vs. actual spike timing relative to lower rate limit.

### 6.5 CRT Optimization Context
CRT optimization questions (is the QRS narrow enough? Is there LV capture?) are device-specific and require device interrogation data. The system can flag "QRS width >140 ms in CRT patient may indicate loss of LV capture" but cannot definitively diagnose — recommend device interrogation.

### 6.6 Difficulty Score

| Dimension | Score (1–5) | Rationale |
|---|---|---|
| Pattern recognition (stable paced) | 2 | LBBB morphology + spikes is distinctive |
| Spike detection (bipolar leads) | 4 | Invisible spikes require morphology inference |
| DDD per-beat classification | 4 | Requires beat-by-beat sensing/pacing state analysis |
| Sgarbossa/ischemia detection | 5 | Quantitative; most critical; ST changes in paced rhythm are commonly missed |
| Malfunction detection | 4 | Requires precise spike timing and capture assessment |
| CRT optimization | 3 | Qualitative QRS width assessment; device interrogation required |
| Clinical urgency (malfunction) | 4 | Pacemaker-dependent patients at risk of asystole |
| **Overall** | **3.5** | **Moderate-high; Sgarbossa application is hardest component** |

---

## 6A. Agent Assignment

**Architecture:** Option E — 3 Parallel Phase 1 Specialists + 1 Sequential CDS (Node 2.1 Gate Passed 2026-03-27)

| Agent | Role for Pacemaker Rhythms | Key Features Used |
|-------|--------------------------|-------------------|
| **RRC** (Rhythm/Rate/Conduction) | Primary | Pacing spikes (atrial and/or ventricular), sensing behavior (inhibited vs triggered), pacing rate, intrinsic rate when sensed, failure to pace (missing spikes), failure to sense (spikes during intrinsic rhythm) |
| **IT** (Ischemia/Territory) | Not involved | ST-segment analysis is invalid in ventricular paced rhythm (LBBB-like morphology masks ischemia); Sgarbossa/modified Sgarbossa criteria apply if needed but not standard IT analysis |
| **MR** (Morphology/Repolarization) | Supporting | Paced QRS morphology: RV pacing produces LBBB pattern; biventricular pacing produces narrowed QRS; failure to capture (spike not followed by P or QRS); pacer spike amplitude and morphology |
| **CDS** (Cross-Domain Synthesis) | Required — pacemaker function assessment and ischemia caveat | Identifies pacing failures (failure to pace, sense, or capture); integrates RRC spike timing with MR capture confirmation; explicitly flags that ischemia assessment via standard ST criteria is unreliable in paced rhythm |

### Primary Agent
**RRC** — Pacemaker rhythm analysis is fundamentally a timing and conduction task: detecting spikes, measuring sensing and pacing rates, identifying pauses and failures; all are RRC-domain measurements.

### Cross-Domain Hints
- RRC → MR: `cross_domain_hint: "pacing_spike_detected — confirm ventricular capture by QRS morphology following each spike"`
- RRC → CDS: `cross_domain_hint: "ventricular_paced_rhythm — flag standard ischemia criteria as unreliable; apply modified Sgarbossa only if clinically indicated"`

### CDS Specific Role
CDS synthesizes pacing spike timing (RRC) with capture confirmation (MR) to identify the three primary pacemaker failures: failure to pace (no spike when expected), failure to sense (spike delivered during intrinsic activity), and failure to capture (spike present but no P-wave or QRS follows). CDS also prominently notes in the final report that ventricular pacing renders standard ST-segment ischemia interpretation unreliable, and that modified Sgarbossa criteria must be applied if ischemia is clinically suspected.

---

## 7. RAG Knowledge Requirements

### 7.1 Core Knowledge Documents Required
- Sgarbossa EB et al. (1996): Electrocardiographic diagnosis of evolving acute MI in the presence of LBBB (*N Engl J Med*) — original Sgarbossa paper
- Smith SW et al. (2012): Diagnosis of ST-elevation myocardial infarction in the presence of LBBB with the ST-elevation to S-wave ratio (*Ann Emerg Med*) — modified Sgarbossa
- Barold SS, Herweg B (2012): Usefulness of the 12-lead ECG in the follow-up of patients with cardiac resynchronization devices — CRT ECG patterns
- Ellenbogen KA, Kay GN: *Clinical Cardiac Pacing, Defibrillation, and Resynchronization Therapy* — ECG chapter
- Brignole M et al. (2021): 2021 ESC Guidelines on cardiac pacing and cardiac resynchronization therapy

### 7.2 Structured Reference Tables Required
- NBG code complete lookup table (all positions and values)
- Pacing mode to expected ECG morphology mapping table
- Sgarbossa original criteria (3 criteria, point scores)
- Modified Sgarbossa (Smith) ST/S ratio criterion
- Pacemaker malfunction ECG pattern table
- CRT response assessment criteria (QRS width targets)

---

## 8. Dashboard Visualization Specification

### 8.1 Pacing Mode Identification Panel
- Automatic mode detection: "Pacing mode detected: [VVI / DDD / AAI / CRT / Unknown — spikes not visible]"
- Per-beat classification strip: each QRS annotated with "AS/AP + VS/VP" coding (A-Sensed/A-Paced + V-Sensed/V-Paced)
- Spike detection overlay: marker on each detected pacing spike with amplitude measurement

### 8.2 Sgarbossa Analysis Panel
- Activated automatically when paced ventricular rhythm detected
- Per-lead ST measurement with concordance assessment
- Criterion 1: "Concordant ST elevation: [lead] = [value] mm — THRESHOLD MET / NOT MET"
- Criterion 2: "Concordant ST depression V1–V3: [value] mm — THRESHOLD MET / NOT MET"
- Modified Sgarbossa ST/S ratio: "[lead]: ST = [x] mm, S = [y] mm, ratio = [z] — ≥0.25: YES/NO"
- Summary: "Sgarbossa Score: [0–10] — Ischemia: UNLIKELY / POSSIBLE / HIGHLY PROBABLE"

### 8.3 Malfunction Alert Panel
- Beat-by-beat expected vs. actual capture assessment
- "Failure to capture detected: Beat [N] — spike present, no following QRS within 80 ms"
- "Undersensing detected: Spike at [time] falls within intrinsic QRS (within [X] ms of prior R wave)"
- Pause detector: flags RR intervals >2 × lower rate limit interval as potential oversensing

---

## 9. Edge Cases and Pitfalls

- **Never assume normal ST-T in paced rhythm without Sgarbossa analysis.** The most dangerous error in pacemaker ECG interpretation is dismissing ST/T changes as "just the normal paced pattern" without formally checking concordance.
- **Invisible bipolar spikes with LBBB morphology:** If the clinical record indicates an implanted device and the ECG shows LBBB, assume paced rhythm and apply Sgarbossa — do not require visible spikes.
- **Fusion beats during Sgarbossa analysis:** Fusion beats have intermediate morphology and may show ST changes that reflect either intrinsic or paced components. Sgarbossa analysis is unreliable on fusion beats — identify and exclude them.
- **PMT (pacemaker-mediated tachycardia):** Regular tachycardia at exactly the upper rate limit in a DDD patient = PMT until proven otherwise. Applying a magnet over the device breaks the loop immediately.
- **T-wave oversensing:** Tall T waves (as in hyperkalemia or LQTS) may be sensed as a second QRS → pacemaker is inhibited → dangerous if pacemaker-dependent. ECG shows inappropriate pauses.
- **CRT non-responder:** Some patients with CRT still have wide paced QRS (>140 ms). On ECG, this should be flagged for device interrogation — LV lead may have dislodged or captured threshold elevated.
- **Pacing in the setting of AF:** In AF, atrial pacing is not possible (atria are fibrillating). VVI is the typical backup mode. DDD in AF switches to DDI or VVI mode automatically (mode-switch). ECG shows no atrial spikes, irregular R-R (driven by AF ventricular rate), with ventricular pacing when rate drops below lower rate limit.

---

## 10. References

1. Sgarbossa EB, Pinski SL, Barbagelata A, et al. Electrocardiographic diagnosis of evolving acute myocardial infarction in the presence of left bundle-branch block. *N Engl J Med.* 1996;334(8):481–487.
2. Smith SW, Dodd KW, Henry TD, et al. Diagnosis of ST-elevation myocardial infarction in the presence of left bundle branch block with the ST-elevation to S-wave ratio in a modified Sgarbossa rule. *Ann Emerg Med.* 2012;60(6):766–776.
3. Brignole M, Auricchio A, Baron-Esquivias G, et al. 2021 ESC Guidelines on cardiac pacing and cardiac resynchronization therapy. *Eur Heart J.* 2021;42(35):3427–3520.
4. Barold SS, Herweg B. Usefulness of the 12-lead electrocardiogram in the follow-up of patients with cardiac resynchronization devices. Part I. *Cardiol J.* 2011;18(5):476–486.
5. Ellenbogen KA, Kay GN, Lau CP, Wilkoff BL. *Clinical Cardiac Pacing, Defibrillation, and Resynchronization Therapy.* 4th ed. Philadelphia: Elsevier Saunders; 2011.
6. Harrigan RA, Chan TC, Brady WJ. Electrocardiographic electrode misplacement, misconnection, and artifact. *J Emerg Med.* 2012;43(6):1038–1044.
