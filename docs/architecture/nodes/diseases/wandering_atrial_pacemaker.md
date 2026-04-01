# Wandering Atrial Pacemaker — ECG Manifestation from First Principles

**Node:** 2.7.33
**SDA:** SDA-2 (Diagnosis & Agentic Core) — shared resource for SDA-1, SDA-3, SDA-4
**Status:** Research Complete
**PGMR:** Required
**Date:** 2026-03-27

---

## 1. Pathophysiology Root Cause

### 1.1 What Goes Wrong

- In Wandering Atrial Pacemaker (WAP), the dominant cardiac pacemaker shifts — gradually and repeatedly — among the SA node, other atrial foci, and sometimes the AV junction. At any given moment, one focus is dominant; the shift from one focus to another occurs gradually over several beats rather than abruptly.
- The underlying mechanism is a competition between the SA node and subsidiary atrial or junctional pacemakers, driven by changes in **autonomic tone** — particularly increased vagal (parasympathetic) tone suppressing the SA node while allowing lower subsidiary foci to emerge.
- **Physiological WAP (most common)**: In athletes, young healthy individuals, and during sleep — high vagal tone chronically suppresses the SA node. The SA node rate slows, allowing nearby atrial foci (spontaneously slightly faster than the SA node at that moment) to capture the rhythm. The dominance shifts back as vagal tone fluctuates. This is a normal variant and requires no treatment.
- **Pathological WAP**: Structural atrial disease (COPD with right atrial enlargement, rheumatic heart disease, atrial fibrosis) alters the automaticity landscape of the atria. Multiple foci compete, not just due to autonomic variation but due to intrinsic pathological enhanced automaticity. This type may be a precursor to MAT or AFib.
- The key feature distinguishing WAP from MAT is rate: if the rate exceeds 100 bpm, the condition is by definition MAT (same mechanism, same morphological features, just faster).
- The key feature distinguishing WAP from AFib or PVCs: in WAP, the shift from one pacemaker to another is **gradual** — the P-wave morphology transitions beat-by-beat (not a sudden jump), and the PR interval shortens progressively as the pacemaker moves closer to the AV node.

### 1.2 Electrical Consequence

- Each pacemaker focus that gains dominance generates a distinct depolarization wavefront spreading across the atria from its own anatomical origin. The vector of atrial depolarization thus changes with each dominant focus.
- As the pacemaker migrates from the SA node (high right atrium) downward toward the AV junction:
  - The atrial depolarization wavefront shifts from superior-to-inferior (sinus direction) to inferior-to-superior (junctional/low atrial direction).
  - The P-wave axis changes: from the normal +60° (upright in II, III, aVF; negative in aVR) toward a more rightward, superior, or inverted axis.
  - The PR interval shortens: the closer the focus is to the AV node, the shorter the path for the impulse to travel before reaching the AV node → shorter atrial conduction time → shorter PR.
  - When the pacemaker is junctional (AV node itself): P-waves may be retrograde (inverted in II, III, aVF) and may appear just before, during, or just after the QRS. Alternatively, P-waves may be absent (hidden within QRS).
- The QRS is not affected — ventricular activation proceeds via normal His-Purkinje conduction regardless of where in the atria the impulse originates.

### 1.3 Why It Appears on ECG

- **Multiple P-wave morphologies**: Each dominant pacemaker focus generates its own unique atrial depolarization vector → different P-wave axis, amplitude, and shape in every lead. Over a sequence of beats, the P-wave changes morphology gradually as the pacemaker wanders.
- **Gradual morphological transition**: Unlike PACs (sudden single ectopic beat) or MAT (multiple foci firing independently at irregular intervals), WAP transitions smoothly — the P-wave on beat 4 looks intermediate between beat 3 and beat 5. This gradual shift is visible and expected.
- **PR interval changes in parallel**: As the pacemaker moves toward the AV node, PR shortens. As it moves back toward the SA node, PR lengthens. The PR change tracks the P-wave morphology change.
- **Rate <100 bpm**: The combined effect of all foci is a rate within the normal or low-normal range. If rate exceeds 100 bpm, the diagnosis changes to MAT.
- **Irregular rhythm**: The shift between foci produces beat-to-beat variation in the atrial cycle length → irregular PP and RR intervals, similar to sinus arrhythmia but with morphological variation.

---

## 2. ECG Presentation — Lead by Lead

### 2.1 Diagnostic Criteria (2025 AHA/ESC Guidelines)

| Criterion | Threshold | Notes |
|-----------|-----------|-------|
| Distinct P-wave morphologies | ≥3 morphologically distinct P-waves in the same lead | Must include gradual morphological transitions (not abrupt jumps) |
| Heart rate | <100 bpm | If rate ≥100 bpm with same morphology criteria = MAT by definition |
| Variable PR intervals | PR interval changes beat-to-beat, tracking P-wave morphology | PR shortens as pacemaker moves toward AV node; lengthens as it moves toward SA node |
| Gradual transition | P-wave morphology shifts gradually over multiple beats | Distinguishes WAP from PACs (abrupt single ectopic) and MAT (random alternation) |
| Irregular rhythm | PP and RR intervals vary | Not perfectly regular; irregular but at a slow overall rate |
| Discrete P-waves | Each P-wave is a well-formed, complete deflection; isoelectric baseline between P-waves | Distinguishes WAP from AFib |

### 2.2 Lead-by-Lead Manifestation

| Lead | Expected Finding | Why | Sensitivity |
|------|-----------------|-----|-------------|
| I | ≥3 P-wave morphologies; variable amplitude; gradual transitions; irregular slow rate | Lateral lead — records horizontal atrial vector; morphology shifts as pacemaker moves left/right atrial dominance | Moderate — lateral projection may show subtle changes |
| II | **Primary diagnostic lead**: ≥3 P-wave morphologies most distinguishable; PR varies in parallel; upright P (SA node) → biphasic → inverted (junctional) | Inferior lead (+60°) — where normal sinus P is largest and most upright; junctional P is most inverted; the full range of morphology is widest here | **High** — best single lead for WAP diagnosis |
| III | P-waves show morphological variation; polarity may invert | Inferior lead (+120°) — inferior pacemaker foci project strongly; morphological transitions visible | Moderate-high |
| aVR | P-waves typically inverted during sinus phases; may become upright as junctional pacemaker emerges (retrograde P upright in aVR) | Rightward-superior lead — inverts sinus P; when pacemaker is junctional (retrograde), P may become less negative or even positive in aVR | Moderate — useful for confirming junctional phase |
| aVL | P-wave morphologies vary; low amplitude changes | Left lateral superior lead — atrial vectors project weakly; changes may be subtle | Low-moderate |
| aVF | P-waves upright with SA node foci; transition toward inverted with junctional foci | Inferior lead (+90°) — mirrors II; good for tracking inferior-superior axis shift | Moderate-high |
| V1 | Biphasic P-waves (positive-then-negative) with SA node foci; shape changes as pacemaker shifts; isoelectric baseline always present | V1 records right-to-left atrial depolarization; morphology changes as origin shifts; critically, baseline remains isoelectric throughout | **High** for confirming discrete P-waves and isoelectric baseline (ruling out AFib) |
| V2 | P-wave morphologies vary; smaller than V1 | Adjacent to V1; similar principles | Moderate |
| V3-V6 | P-waves present but small; morphology differences subtle in precordial leads | Precordial leads farther from atria; ventricular signal dominates | Low for P-wave morphology; useful for confirming narrow QRS |

### 2.3 Key Leads

- **Lead II (long rhythm strip)**: Primary diagnostic lead. The full range of P-wave morphology (upright sinus → inverted junctional) is best seen here. PR interval tracking also most visible.
- **V1**: Essential for confirming the isoelectric baseline between discrete P-waves — the key feature excluding AFib.
- **Lead aVR**: Useful for confirming junctional phase of WAP — when the pacemaker is junctional, retrograde P-waves may become less inverted or even upright in aVR.
- **Long rhythm strip**: WAP requires observing the gradual morphological transition across multiple beats. A single 10-second Lead II strip is usually adequate if the patient is in WAP throughout.

### 2.4 Beat-by-Beat Considerations

- **Gradual morphological shift**: Over a sequence of 4–8 beats, the P-wave morphology will change continuously. If the P-wave jumps abruptly from one morphology to another between consecutive beats, consider PACs (for isolated jumps) or MAT (for sustained random alternation) rather than WAP.
- **PR interval tracks with P-wave morphology**: This parallel relationship is the confirmatory feature. If P-wave morphology changes but PR stays fixed, the morphology change may be artifactual or due to respiratory variation (sinus arrhythmia with axis shift) rather than true pacemaker migration.
- **Junctional phase**: When the pacemaker is junctional (AV node), P-waves may disappear within the QRS (hidden) or appear as retrograde P-waves (inverted in II, III, aVF) very close to the QRS. PR interval is <120 ms or unmeasurable. This phase may last for several beats before the pacemaker migrates back to the atria.
- **QRS is narrow and constant**: All QRS complexes should look the same (unless pre-existing BBB). WAP does not affect ventricular conduction. Uniform narrow QRS throughout = confirms atrial/junctional origin of all beats.
- **Rate variation**: Heart rate in WAP varies cyclically with autonomic tone — slower during junctional phases (more vagal), slightly faster during SA node phases. Overall rate remains <100 bpm.

---

## 3. Morphology Details

### 3.1 P-Wave Morphology Spectrum

- WAP produces a spectrum of P-wave morphologies corresponding to pacemaker location along the craniocaudal atrial axis:
  - **SA node (high right atrium)**: Normal sinus P — upright I, II, aVF; inverted aVR; biphasic V1 (positive-then-negative). PR interval 120–200 ms.
  - **Upper right atrial foci**: P-wave similar to sinus but slightly different amplitude or axis. PR interval 110–200 ms.
  - **Mid-right atrial foci**: P-wave upright in II but smaller; biphasic in III; PR 100–160 ms.
  - **Low right atrial / low septal foci**: P-wave small in II; inverted in III, aVF; short PR <120 ms.
  - **AV junction**: Retrograde P — inverted in II, III, aVF; upright in aVR. PR <120 ms or P within QRS (hidden) or after QRS (retrograde, RP <200 ms). When P is within QRS, it is invisible on surface ECG.
- The transitions between these morphologies are gradual: the P-wave in Lead II on beat N+1 looks intermediate between the morphology on beat N and beat N+2.

### 3.2 PR Interval Spectrum

- As the pacemaker migrates from SA node → AV junction, PR intervals change as follows:
  - SA node: PR 160–200 ms (long conduction distance to AV node)
  - Mid-atrial: PR 120–160 ms
  - Low atrial/junctional: PR <120 ms
  - Junctional (within QRS): no measurable PR
- The PR shortening is gradual and tracks the P-wave morphology change. This parallel change is pathognomonic of WAP and distinguishes it from other causes of variable P-wave morphology.
- Important: PR interval <120 ms in a WAP beat reflects a lower atrial or junctional origin — not pre-excitation (no delta wave, no widened QRS in WAP).

### 3.3 QRS Complex

- Narrow (<120 ms) and uniform throughout. All QRS complexes have the same morphology regardless of which pacemaker is dominant — ventricular activation is always via normal His-Purkinje conduction.
- No fusion beats (distinguishes WAP from AIVR or PVCs).
- No delta wave (distinguishes WAP with short PR from WPW syndrome — WAP short PR has no delta wave, and QRS is narrow).

### 3.4 ST Segment and T-Wave

- ST segment and T-waves are normal. WAP does not produce ST or T-wave abnormalities.
- During the junctional phase: T-waves may appear slightly different due to minor changes in ventricular activation sequence if the junctional impulse reaches the bundle branches at a slightly different timing — but this is a minor effect.
- If ST/T abnormalities are present in WAP, they reflect underlying disease (the cause of the WAP, such as COPD with RVH, or structural heart disease) — not WAP itself.

### 3.5 Rate and Rhythm

- Rate: 60–100 bpm. If rate falls below 60 bpm during junctional phases, this may represent junctional bradycardia rather than WAP. If rate rises above 100 bpm, the diagnosis shifts to MAT.
- Rhythm: irregularly irregular, but at a slower rate than AFib or MAT. The irregularity is mild and fluctuates cyclically with autonomic tone — often showing a relationship to the respiratory cycle in physiological WAP.
- In physiological WAP in athletes: rate may vary between 50–80 bpm with clear respiratory variation (slow on expiration → more vagal → junctional foci take over; faster on inspiration → less vagal → SA node resumes).

### 3.6 Axis

- Mean P-wave axis is not fixed — it cycles through a range (from ~+60° during sinus phase to negative axis during junctional phase). This is the defining feature of WAP.
- Mean QRS axis is normal and stable throughout — confirms ventricular activation is not affected by the pacemaker migration.

### 3.7 Special Features

- **Gradual shift is the sine qua non**: The morphological transition must be gradual. If beat-to-beat P-wave morphology change is abrupt (random), consider MAT (if fast) or multiform PACs (if isolated ectopics on sinus background).
- **PR shortening tracks morphology**: This parallel relationship is the most reliable single confirmatory feature that distinguishes true pacemaker migration from respiratory or artifact-induced P-wave variation.
- **Junctional phase with absent P-waves**: During junctional phases of WAP, P-waves may disappear for several beats (hidden in QRS or before QRS interval falls below ECG resolution). A brief run of "junctional rhythm" embedded within the wandering pattern is a WAP feature, not a separate diagnosis.

---

## 4. Differential Diagnosis

### 4.1 Mimics

| Condition | Key Similarity | Key Difference | Distinguishing Feature |
|-----------|---------------|----------------|----------------------|
| Multifocal Atrial Tachycardia (MAT) | ≥3 P-wave morphologies, variable PR, irregular rhythm | MAT rate ≥100 bpm; WAP rate <100 bpm | **Rate is the sole criterion**: rate ≥100 bpm = MAT; rate <100 bpm = WAP |
| Atrial Fibrillation | Irregular rhythm, variable P-wave appearance | AFib: NO discrete P-waves; fibrillatory undulating baseline | Isoelectric baseline between discrete P-waves = WAP; fibrillatory baseline = AFib |
| Sinus arrhythmia | Irregular rate, normal P-waves | Sinus arrhythmia: single P-wave morphology (sinus only); variation is in rate not morphology | WAP: ≥3 P-wave morphologies; sinus arrhythmia: one consistent P-wave morphology |
| Multiform PACs (isolated) | Multiple P-wave morphologies | PACs: isolated ectopic beats on a background of dominant sinus rhythm; abrupt morphology jump | WAP: ALL beats arise from ectopic foci; no dominant sinus background; gradual morphology transitions |
| Junctional rhythm | PR <120 ms, P-wave inverted or absent | Junctional rhythm: FIXED single morphology; no gradual transition; no SA node beats | WAP includes SA node and multiple atrial foci; junctional rhythm is a fixed single pacemaker |
| WPW syndrome (AVRT) | Short PR interval | WPW: delta wave; wide QRS; short PR is fixed; single P-wave morphology | WAP: no delta wave; narrow normal QRS; variable PR tracks variable P-wave morphology |
| Respiratory P-wave axis variation (sinus arrhythmia) | P-wave amplitude variation with breathing in sinus rhythm | Respiratory variation: single consistent P-wave morphology; axis variation is minor (within sinus range) | WAP: discrete morphological changes exceeding respiratory variation; ≥3 distinct morphologies |

### 4.2 Coexisting Conditions

- **COPD / cor pulmonale**: Pathological WAP is most common in COPD patients with right atrial enlargement. Coexisting P pulmonale (tall peaked P >2.5 mm in II) and RVH features may be present during the SA node phases of WAP.
- **Athlete's heart**: Physiological WAP in athletes coexists with high vagal tone findings: sinus bradycardia, first-degree AV block, early repolarization. All are benign.
- **Rheumatic heart disease / structural atrial disease**: Mitral stenosis → left atrial enlargement (wide notched P in II during SA node phases) may coexist with WAP.
- **Acceleration to MAT**: If the underlying condition (COPD exacerbation, metabolic stress) worsens, WAP can accelerate to MAT. Monitor for rate increase exceeding 100 bpm.
- **Digitalis effect**: Digoxin enhances vagal tone and suppresses SA node → can cause WAP, particularly at higher doses. WAP in a patient on digoxin should prompt checking dig levels.

---

## 5. STAT Classification

| Parameter | Value | Clinical Implication |
|-----------|-------|---------------------|
| STAT Level | **NOT STAT** | WAP is a benign finding in the vast majority of cases. No immediate treatment required. |
| Physiological WAP | Benign normal variant | Athletes, young vagotonic patients, sleep-related — reassurance only. No workup unless symptomatic. |
| Pathological WAP | Evaluate underlying cause | COPD, structural heart disease, digitalis effect — treat the underlying condition. WAP itself is not treated. |
| Monitoring | Only if symptomatic (palpitations, near-syncope) | Holter monitoring to correlate symptoms with rhythm; document absence of MAT or AFib. |
| Treatment | None for WAP itself | If digitalis toxicity suspected: check levels, consider dose reduction or Digibind if severe. |
| Pacemaker | Not indicated | WAP does not require pacing. |
| Anticoagulation | Not indicated for WAP alone | WAP does not carry AFib stroke risk. If WAP is a harbinger of AFib, anticoagulation decision follows AFib guidelines when AFib is documented. |
| Clinical monitoring | Watch for rate increase (WAP → MAT) | If rate increases to ≥100 bpm, reclassify as MAT and increase clinical concern for underlying disease severity. |

---

## 6. Reasoning Complexity Analysis

### 6.1 Signal Quality Requirements

- P-wave morphology discrimination requires a clean, artifact-free baseline. Small P-wave amplitude differences between foci demand a noise floor of <0.1 mV.
- The key analytical step — confirming that P-wave morphology changes are GRADUAL (not abrupt) — requires that consecutive P-waves be clearly resolved with no overlapping artifact.
- Isoelectric baseline between P-waves must be confirmed in V1 to exclude AFib.

### 6.2 Number of Leads Required

- Minimum: Lead II (morphology tracking, PR interval measurement) + V1 (baseline confirmation).
- Optimal: All 12 leads to fully characterize P-wave morphology spectrum and confirm QRS uniformity.
- Single-lead analysis (Lead II only) is often sufficient for a definitive WAP diagnosis if the recording is clean and of adequate duration.

### 6.3 Cross-Domain Reasoning

- Clinical context determines whether WAP is physiological (athlete, sleep) or pathological (COPD, digoxin, structural heart disease). The ECG alone cannot make this distinction.
- Drug history: Digoxin use raises the possibility of drug-induced WAP → dose adjustment may be indicated.
- Age and fitness context: WAP in a 25-year-old endurance athlete is unremarkable; WAP in a 75-year-old with COPD requires evaluation.

### 6.4 Temporal Pattern Complexity

- The gradual morphological transition is the defining temporal feature. Detecting gradual change requires sequential beat-by-beat P-wave morphology analysis, not single-beat assessment.
- The transition pattern should be distinguishable from random variation (MAT) or fixed variation (PACs). This requires morphological clustering combined with sequence analysis — are the morphology changes gradual and continuous, or random and abrupt?
- Rate constancy confirms WAP (<100 bpm throughout). If rate varies across the recording, confirm no transient MAT acceleration episodes.

### 6.5 Differential Complexity

- The MAT differential is resolved by rate threshold alone (simple once rate is measured accurately).
- The AFib differential is resolved by isoelectric baseline confirmation (simple with clean signal).
- The most nuanced differential is WAP vs. sinus arrhythmia with respiratory P-wave axis variation: both produce gradual P-wave changes correlated with breathing. The distinction is degree — WAP produces morphologically distinct P-waves (≥3 categories); sinus arrhythmia produces amplitude variation of a single morphology. In practice, the categories can overlap in mild WAP.

### 6.6 Difficulty Score

| Dimension | Score (1–5) | Notes |
|-----------|-------------|-------|
| Signal clarity needed | 3 | P-wave morphology clustering and gradient tracking requires clean signal; small morphology differences between adjacent beats may be within noise range |
| Number of leads required | 2 | Lead II + V1 minimum; 12-lead preferred for full characterization |
| Cross-domain reasoning | 2 | Clinical context (athlete vs COPD vs digoxin) matters but WAP itself is benign; clinical integration is straightforward |
| Temporal pattern complexity | 3 | Sequential beat-by-beat morphology gradient analysis required; gradual vs abrupt transition discrimination adds complexity |
| Differential complexity | 2 | MAT (rate threshold) and AFib (baseline) differentials are simple; sinus arrhythmia vs WAP borderline cases are the only genuinely nuanced differential |
| Rarity in PTB-XL | 2 | WAP is uncommon but present in PTB-XL; primarily in recordings with sinus arrhythmia variants — may be underrepresented as a discrete label |
| Overall difficulty | **2.0/5** | Low-moderate: conceptually straightforward once P-wave morphology clustering and rate threshold are applied; main challenge is subtle gradual morphology transitions |

---

## 6A. Agent Assignment

**Architecture:** Option E — 3 Parallel Phase 1 Specialists + 1 Sequential CDS (Node 2.1 Gate Passed 2026-03-27)

| Agent | Role for Wandering Atrial Pacemaker | Key Features Used |
|-------|--------------------------|-------------------|
| **RRC** (Rhythm/Rate/Conduction) | Primary | ≥3 distinct P-wave morphologies, irregular RR intervals, rate <100 bpm, gradual morphology transitions beat-to-beat, variable PR interval corresponding to P morphology changes |
| **IT** (Ischemia/Territory) | Not involved | ST/T assessment not relevant to WAP classification |
| **MR** (Morphology/Repolarization) | Not involved | QRS morphology not relevant; P-wave morphology variation is RRC-domain |
| **CDS** (Cross-Domain Synthesis) | Standard integration only | Applies rate threshold to distinguish WAP (<100 bpm) from MAT (≥100 bpm); confirms gradual vs abrupt P-wave morphology changes |

### Primary Agent
**RRC** — WAP diagnosis requires identifying ≥3 P-wave morphologies with gradual transitions and a rate below 100 bpm; all criteria are RRC-domain rhythm and P-wave analysis.

### Cross-Domain Hints
No cross-domain hints required — single-domain condition.

### CDS Specific Role
CDS applies the rate threshold rule: if RRC reports ≥3 P-wave morphologies at rate <100 bpm, WAP is confirmed; if rate ≥100 bpm, CDS reclassifies as MAT. CDS also differentiates WAP from frequent PACs by confirming that the P-wave morphology changes occur gradually across consecutive beats rather than abruptly as isolated premature beats.

---

## 7. RAG Knowledge Requirements

### 7.1 Essential Knowledge Chunks

- WAP diagnostic criteria: ≥3 distinct P-wave morphologies, rate <100 bpm, variable PR intervals tracking P-wave morphology, gradual morphological transition, discrete P-waves with isoelectric baseline
- WAP vs MAT rate threshold: <100 bpm = WAP; ≥100 bpm = MAT (same morphological criteria, rate is the only differentiator)
- WAP vs AFib: discrete P-waves + isoelectric baseline = WAP; fibrillatory baseline = AFib
- P-wave morphology spectrum: SA node → upper RA → mid-RA → low RA → AV junction (with corresponding PR interval changes from 160–200 ms down to <120 ms or retrograde)
- Physiological WAP: normal variant in athletes, young vagotonic patients, during sleep — high vagal tone mechanism; benign; no treatment
- Pathological WAP: associated with COPD, structural atrial disease, digitalis effect — evaluate and treat underlying cause
- WAP does not require treatment; WAP does not require anticoagulation; WAP does not require pacemaker
- Gradual vs abrupt P-wave morphology transitions: gradual = WAP; abrupt = PACs or MAT
- 2025 AHA/ESC rhythm classification: WAP as benign supraventricular rhythm variant

### 7.2 Supporting Reference Material

- Josephson ME. *Clinical Cardiac Electrophysiology: Techniques and Interpretations.* 4th ed. Lippincott Williams & Wilkins; 2008. Chapter on supraventricular arrhythmias.
- Goldberger AL, Goldberger ZD, Shvilkin A. *Goldberger's Clinical Electrocardiography: A Simplified Approach.* 9th ed. Elsevier; 2018. Chapter on wandering pacemaker and related rhythms.
- Wagner GS, Strauss DG. *Marriott's Practical Electrocardiography.* 12th ed. Lippincott Williams & Wilkins; 2014.
- Surawicz B, Knilans TK. *Chou's Electrocardiography in Clinical Practice.* 6th ed. Saunders; 2008. Chapter on sinus node arrhythmias.
- ECGdeli P-wave detection parameters: amplitude threshold for small P-waves; morphology clustering algorithm; PR interval measurement precision

---

## 8. Dashboard Visualization Specification

### 8.1 Primary Display Elements

- **Rhythm strip (Lead II)**: 10-second strip with color-coded P-waves by morphology cluster (cluster 1 = blue, cluster 2 = orange, cluster 3 = green, junctional phase = grey/absent). The gradual color transition across beats is itself a visual confirmation of WAP.
- **P-wave morphology progression panel**: Sequential averaged P-wave templates displayed left-to-right in order of appearance — showing the gradual morphological shift visually as a "spectrum" rather than distinct categories.
- **PR interval plot**: Beat-by-beat PR interval plotted as a line graph — should show gradual PR shortening during pacemaker migration toward AV node and gradual PR lengthening during migration back to SA node. Smooth curve confirms WAP; erratic plot suggests MAT or multiform PACs.
- **Rate display**: Instantaneous rate plot — confirms rate stays <100 bpm throughout. Any beat approaching 100 bpm flagged.

### 8.2 Annotations

- Each P-wave annotated with its cluster assignment (color + label).
- Junctional phase annotated: "Junctional phase — P-wave within or absent" when PR <120 ms or P-wave undetectable.
- PR interval annotated on the rhythm strip for each beat.
- Rate annotation: "WAP — rate range: XX–XX bpm (below MAT threshold)"
- Benign finding banner: "Wandering Atrial Pacemaker — gradual P-wave morphology transition, rate <100 bpm. Benign finding in most contexts."
- Clinical context prompt: "Consider: athlete/vagotonic state, COPD, digitalis effect."

### 8.3 Pitfall Warnings

- If rate approaches 100 bpm (90–99 bpm): "Rate approaching MAT threshold — monitor for rate increase."
- If morphology transitions are abrupt rather than gradual: "Abrupt P-wave morphology changes detected — consider MAT or multiform PACs rather than WAP."
- If baseline is not isoelectric: "Baseline not confirmed isoelectric — AFib vs WAP differentiation requires cleaner signal."
- If fewer than ≥3 morphology clusters confirmed: "Only 2 P-wave morphologies identified — insufficient for WAP diagnosis. May represent sinus arrhythmia with axis variation."

---

## 9. Edge Cases and Pitfalls

- **WAP vs sinus arrhythmia with respiratory axis shift**: Normal respiratory variation can produce mild P-wave amplitude changes in sinus rhythm (axis shifts slightly with inspiration/expiration). If P-wave morphology variation is minor (amplitude changes without axis inversion, PR stays constant), this is sinus arrhythmia — not WAP. True WAP requires ≥3 distinct morphologies with PR interval change tracking the morphology.
- **WAP with rate near 100 bpm**: A patient with WAP at 95–99 bpm is technically WAP, but clinically this is the borderline zone where the underlying cause may be escalating toward MAT. Flag and monitor — single-beat rate counting near this threshold can introduce classification instability.
- **Junctional phase mimicking junctional bradycardia**: During the junctional phase of WAP, several consecutive beats may show no visible P-wave and a rate of 50–60 bpm — this looks identical to a junctional escape rhythm. Distinguish by the surrounding context: if beats before and after show gradual WAP transition, the junctional phase is part of WAP. If the "junctional" beats appear abruptly without preceding WAP context, consider primary junctional rhythm.
- **Digitalis effect WAP**: Digoxin-induced WAP may be difficult to distinguish from digitalis toxicity-related arrhythmias (PAT with block, junctional tachycardia). If WAP is detected in a patient on digoxin, flag for drug level review — particularly if the ventricular rate is irregular or the PR is prolonged.
- **WAP in acutely ill patients**: WAP in a critically ill patient (sepsis, metabolic crisis) may be the early harbinger of MAT — the same metabolic stressors that drive WAP can accelerate it to MAT. Serial ECGs are warranted; a single 10-second ECG showing WAP in a sick patient should not be given a false reassurance label.
- **P-wave detection failure mimicking WAP**: If P-wave detection is inconsistent (sometimes detecting, sometimes missing P-waves in the same patient in sinus rhythm), the resulting variable P-wave presence and apparent morphology change can mimic WAP or MAT. Validate P-wave detection algorithm confidence score before WAP classification.
- **WAP vs low atrial rhythm with exit**: A fixed low atrial ectopic pacemaker can produce a single different P-wave morphology with short PR — this is a single ectopic rhythm, not WAP. WAP requires the pacemaker to MIGRATE (gradual transitions) and requires ≥3 distinct morphologies.

---

## 10. References

1. Goldberger AL, Goldberger ZD, Shvilkin A. *Goldberger's Clinical Electrocardiography: A Simplified Approach.* 9th ed. Elsevier; 2018. Chapter on supraventricular arrhythmias.
2. Josephson ME. *Clinical Cardiac Electrophysiology: Techniques and Interpretations.* 4th ed. Lippincott Williams & Wilkins; 2008. Part III: Supraventricular Tachycardias.
3. Surawicz B, Knilans TK. *Chou's Electrocardiography in Clinical Practice.* 6th ed. Saunders; 2008. Chapter 3: Sinus Node Arrhythmias and Wandering Pacemaker.
4. Wagner GS, Strauss DG. *Marriott's Practical Electrocardiography.* 12th ed. Lippincott Williams & Wilkins; 2014. Chapter on supraventricular arrhythmias.
5. Alpert MA, Flaker GC. Arrhythmias associated with sinus node dysfunction. *JAMA.* 1983;250(16):2160–2166.
6. Kastor JA. Multifocal atrial tachycardia. *N Engl J Med.* 1990;322(24):1713–1717. (WAP described as the low-rate precursor to MAT in this seminal paper.)
7. Mangrum JM, DiMarco JP. The evaluation and management of bradycardia. *N Engl J Med.* 2000;342(10):703–709.
8. Hindricks G, et al. 2020 ESC Guidelines for the diagnosis and management of atrial fibrillation. *Eur Heart J.* 2021;42(5):373–498. (Context for WAP differentiation from AFib spectrum.)
