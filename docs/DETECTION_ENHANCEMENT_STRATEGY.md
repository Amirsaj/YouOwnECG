# Detection Enhancement Strategy — Agent-Assisted Fiducial Improvement

## Why This Matters

Fiducial detection is the **backbone** of the entire system. Every measurement (PR, QRS, QT, ST elevation, axis) depends on accurate P/QRS/T boundary detection. Current ECGdeli port achieves:
- R-peak: MAE 5.1 ms (good)
- QRS onset/offset: MAE 4-9 ms (good)
- P-wave onset: MAE 26 ms (needs improvement — propagates to PR interval error)
- T-wave onset: MAE 26 ms (affects QT measurement)

The safe-window limitation (only ~40% of beats analyzed) is a design constraint, not a bug. But the accuracy of detected fiducials CAN be improved.

## Enhancement Approaches

### Approach 1: Multi-Lead Consensus Refinement
**Idea:** Use cross-lead agreement to refine ambiguous fiducials.
- R-peak is detected in all leads; use the most confident lead's timing as reference
- P-wave detected in lead II but uncertain → check V1 (biphasic P in V1 is diagnostic)
- T-wave end ambiguous → use V2/V3 where T is tallest

**Implementation:**
1. After ecgdeli detection, compute per-lead fiducial confidence
2. For each beat, if a fiducial's confidence < threshold in one lead, borrow timing from highest-confidence lead
3. Weight by SNR (from quality assessment)

**Test on:** 3 patients — 1 normal sinus, 1 AFib, 1 with wide QRS (BBB)

### Approach 2: Agent-Assisted ECG Plot Analysis
**Idea:** Render ECG segments as images and use vision LLM to verify/correct fiducial positions.
- Generate zoomed-in plots of each beat showing detected fiducials
- Ask vision model: "Are the P-wave onset/offset markers correctly placed?"
- If vision disagrees, flag for re-detection with adjusted search windows

**Implementation:**
1. For each beat, render 500ms window as matplotlib plot with fiducial markers
2. Send to DeepSeek-VL2 or GPT-4V with structured prompt
3. Parse response for corrections (shift onset left/right by N ms)
4. Apply corrections and recompute intervals

**Test on:** 3 patients — focus on cases where PR interval is miscalculated

### Approach 3: Derivative-Based Refinement
**Idea:** Use signal derivatives to sharpen fiducial boundaries.
- P-wave onset: where second derivative crosses zero before P-peak
- QRS onset: maximum negative slope before Q-wave
- T-wave offset: where first derivative returns to zero after T-peak
- These are classical signal processing refinements on top of ecgdeli

**Implementation:**
1. After ecgdeli detection, re-examine each fiducial using derivative analysis
2. If derivative-based estimate differs > 10ms from ecgdeli, use the derivative estimate
3. Compute confidence as agreement between methods (0-1)

**Test on:** 3 patients — compare interval accuracy before/after refinement

### Approach 4: Template Matching with LUDB Ground Truth
**Idea:** Use LUDB's 200 expert-annotated records as templates.
- For each new beat, find most similar beat morphology in LUDB
- Transfer fiducial positions from the expert-annotated template
- Weight by morphological similarity

**Implementation:**
1. Build beat template database from LUDB (200 records × ~10 beats × 12 leads)
2. For each new beat, compute DTW distance to templates
3. Use top-3 template matches to estimate fiducial positions
4. Blend with ecgdeli detection (weighted average)

**Test on:** 3 patients — compare against LUDB ground truth directly

### Approach 5: LLM Brainstorming with ECG Plots
**Idea:** Show the LLM the actual ECG waveform plot with current fiducial annotations and ask it to identify errors.
- Render full 12-lead ECG with all fiducial markers overlaid
- Ask: "Review these fiducial point annotations. Identify any that appear misplaced."
- Use the LLM's visual reasoning to catch systematic errors

**Implementation:**
1. Generate annotated 12-lead plot (each fiducial color-coded: P=blue, QRS=red, T=green)
2. Send to vision-capable LLM with structured prompt
3. Parse corrections and apply

**Test on:** 3 patients per scenario (normal, AFib, LBBB)

## Testing Protocol

For each approach:
1. Select 3 diverse patients from PTB-XL (normal sinus, AFib, BBB)
2. Run current pipeline → record all interval measurements
3. Apply enhancement → record updated measurements
4. Compare against PTB-XL ground truth (ecgdeli_features.csv)
5. Compute: delta_MAE for PR, QRS, QT, QTc, HR
6. If MAE improves by > 5ms on average, integrate the enhancement

## Priority Order

1. **Approach 3** (derivative refinement) — pure signal processing, no API cost, fastest to implement
2. **Approach 1** (multi-lead consensus) — improves P-wave detection significantly
3. **Approach 4** (LUDB templates) — highest accuracy potential but most complex
4. **Approach 2/5** (vision LLM) — most novel for the paper but has API cost

## Integration Point

All enhancements modify `pipeline/fiducials.py` by adding a post-processing step after ecgdeli detection. The FPT array is refined in-place before feature extraction begins.
