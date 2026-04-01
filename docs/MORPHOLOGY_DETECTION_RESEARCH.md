# How to Read ECG Morphology from Raw Signal — Research Notes

## The Core Insight

Every morphological pattern a cardiologist "sees" maps to one of 6 signal properties:

```
Signal Property     | Math Operation              | Clinical Use
--------------------|-----------------------------|---------------------------------
1. AMPLITUDE        | peak value - baseline       | R/S ratio, ST elevation, T depth
2. DURATION         | (fiducial2 - fiducial1)/fs  | QRS width, PR interval, Q duration
3. SLOPE            | 1st derivative (linear fit)  | Upsloping vs downsloping ST
4. CURVATURE        | 2nd derivative (parabolic)   | Concave vs convex ST
5. SYMMETRY         | ascending_time / descending  | Symmetric T = ischemia
6. POLARITY/AREA    | signed integral of segment   | Net QRS direction (LBBB vs RBBB)
```

We already do 1-3. We're missing 4-6. These three additions unlock diagnosis of
LBBB, Brugada, Pericarditis, Wellens, Sgarbossa, and de Winter.

---

## Property 4: CURVATURE (2nd Derivative)

### What it tells us
- **Concave up (positive curvature)** = "smiley face" = pericarditis ST, benign early repol
- **Convex up (negative curvature)** = "frowning" = STEMI, Brugada Type 1 coved

### How to compute
```python
def classify_st_curvature(sig, qrs_off, t_on):
    """Classify ST segment as concave, convex, or linear."""
    segment = sig[qrs_off:t_on]
    if len(segment) < 5:
        return "indeterminate"

    # Fit parabola: y = ax² + bx + c
    x = np.arange(len(segment), dtype=float)
    coeffs = np.polyfit(x, segment.astype(float), 2)
    a = coeffs[0]  # 2nd derivative coefficient

    if a > 0.5:     # concave up (bowl shape)
        return "concave"    # → pericarditis, early repol
    elif a < -0.5:  # convex up (dome shape)
        return "convex"     # → STEMI, Brugada coved
    else:
        return "linear"     # → horizontal ST
```

### Where it matters
| Pattern | Curvature | Currently detected? |
|---------|-----------|-------------------|
| Pericarditis ST | Concave (a > 0) | NO — we only have slope |
| STEMI ST | Convex (a < 0) | NO |
| Brugada Type 1 | Convex dome → descending → T-inv | NO |
| Early repol | Concave with J-point notch | NO |

---

## Property 5: SYMMETRY (Ascending vs Descending Limb)

### What it tells us
- **Symmetric T-wave** (ascending ≈ descending time) = ischemia, Wellens, hyperacute
- **Asymmetric T-wave** (slow ascent, rapid descent) = LVH strain, normal variant

### How to compute
```python
def compute_t_symmetry(sig, t_on, t_peak, t_off):
    """Compute T-wave symmetry index. 1.0 = perfectly symmetric."""
    ascending = t_peak - t_on     # samples from onset to peak
    descending = t_off - t_peak   # samples from peak to offset

    if ascending <= 0 or descending <= 0:
        return None

    # Symmetry index: ratio of shorter to longer limb
    ratio = min(ascending, descending) / max(ascending, descending)
    return ratio  # > 0.7 = symmetric, < 0.5 = asymmetric

def detect_biphasic_t(sig, t_on, t_peak, t_off):
    """Detect biphasic T-wave (Wellens Type A): initial up, terminal down."""
    segment = sig[t_on:t_off]
    if len(segment) < 5:
        return False, None

    # Find zero crossings within T-wave
    signs = np.sign(segment - segment[0])  # relative to onset level
    crossings = np.where(np.diff(signs))[0]

    if len(crossings) >= 1:
        # Check: positive first half, negative second half
        mid = len(segment) // 2
        first_half_positive = np.mean(segment[:mid]) > segment[0]
        second_half_negative = np.mean(segment[mid:]) < segment[0]
        if first_half_positive and second_half_negative:
            return True, "wellens_type_a"

    return False, None
```

### Where it matters
| Pattern | Symmetry Index | Currently detected? |
|---------|---------------|-------------------|
| Wellens Type B | > 0.7 (symmetric deep inversion) | NO |
| LVH strain | < 0.5 (asymmetric) | NO |
| Hyperacute T | > 0.7 (symmetric, tall) | Partial (T/QRS ratio only) |
| Wellens Type A | Biphasic (crosses zero) | NO |
| De Winter | > 0.7 (tall symmetric peaked) | NO |

---

## Property 6: POLARITY/AREA (Signed Integral)

### What it tells us
- **Net positive QRS area in V1** = RBBB pattern (terminal R')
- **Net negative QRS area in V1** = LBBB pattern (QS or rS)
- **Concordant ST** = ST direction SAME as QRS terminal direction → pathological
- **Discordant ST** = ST direction OPPOSITE to QRS terminal direction → expected in BBB

### How to compute (existing + enhancement)
```python
# EXISTING (features.py:_v1_qrs_net_negative):
net_area = segment.sum()  # Positive = RBBB, Negative = LBBB

# NEW: Terminal QRS polarity for any lead (last 40ms)
def terminal_qrs_polarity(sig, qrs_off, fs):
    """Determine if terminal QRS force is positive or negative."""
    terminal_start = max(0, qrs_off - int(0.040 * fs))  # last 40ms
    terminal = sig[terminal_start:qrs_off]
    return "positive" if np.mean(terminal) > 0 else "negative"

# NEW: Concordance assessment
def assess_concordance(terminal_polarity, st_direction):
    """
    terminal_polarity: "positive" or "negative" (from terminal QRS)
    st_direction: "elevation" or "depression" (from ST measurement)

    Concordant = SAME direction → pathological (Sgarbossa positive)
    Discordant = OPPOSITE → expected secondary change in BBB
    """
    if terminal_polarity == "positive" and st_direction == "elevation":
        return "concordant"  # → STEMI in LBBB (Sgarbossa Criterion 1)
    if terminal_polarity == "negative" and st_direction == "depression":
        return "concordant"  # → STEMI in LBBB (Sgarbossa Criterion 2)
    return "discordant"      # → expected secondary change
```

### Where it matters
| Pattern | Polarity/Area Use | Currently detected? |
|---------|------------------|-------------------|
| LBBB detection | V1 net negative area | YES (features.py) |
| RBBB detection | V1 net positive + R' | YES (partial) |
| Sgarbossa | Concordance per lead | NO — critical gap |
| LBBB secondary changes | Discordance = expected | NO |

---

## Property 6b: QRS MORPHOLOGY PATTERN (Zero-Crossing Analysis)

### What it tells us
The number and location of zero-crossings within QRS tells us the pattern:
- **0 crossings** = monophasic (pure R or QS)
- **1 crossing** = biphasic (RS or QR)
- **2 crossings** = triphasic (RSR' or qRs)
- **>2 crossings** = fragmented QRS

### How to compute
```python
def classify_qrs_pattern(sig, qrs_on, qrs_off):
    """Classify QRS morphology pattern from signal."""
    segment = sig[qrs_on:qrs_off].astype(float)
    if len(segment) < 3:
        return "indeterminate"

    # Baseline = signal at QRS onset
    baseline = segment[0]
    centered = segment - baseline

    # Count zero crossings
    signs = np.sign(centered)
    crossings = np.where(np.diff(signs))[0]
    n_cross = len(crossings)

    # Determine dominant polarity
    net = np.sum(centered)

    if n_cross == 0:
        return "R" if net > 0 else "QS"
    elif n_cross == 1:
        if centered[0] > 0:
            return "Rs"  # starts positive, goes negative
        else:
            return "rS" if net < 0 else "qR"
    elif n_cross == 2:
        # Triphasic — check for RSR' vs qRs
        mid = len(centered) // 2
        if centered[mid] < 0 and centered[-3:].mean() > 0:
            return "RSR'"  # RBBB pattern (M-shaped)
        else:
            return "qRs"   # Normal
    else:
        return "fragmented"
```

---

## PR Segment Depression (Pericarditis)

### How to compute
```python
def compute_pr_depression(sig, p_off, qrs_on, p_on, fs):
    """Measure PR segment depression relative to TP baseline."""
    # TP baseline: 10 samples before P onset
    iso_start = max(0, p_on - 10)
    baseline = np.mean(sig[iso_start:p_on]) if p_on > iso_start else 0

    # PR segment: between P offset and QRS onset
    pr_segment = sig[p_off:qrs_on]
    if len(pr_segment) < 2:
        return None

    pr_level = np.mean(pr_segment)
    depression_uv = baseline - pr_level  # positive = depressed
    return depression_uv / 1000.0  # convert to mV
```

---

## AV Dissociation Detection (Complete AVB)

### How to compute
```python
def detect_av_dissociation(fpt, fs):
    """Detect AV dissociation by comparing P-P and R-R independence."""
    p_peaks = fpt[:, COL_PPEAK]
    r_peaks = fpt[:, COL_R]

    valid_p = p_peaks[p_peaks > 0].astype(float)
    valid_r = r_peaks[r_peaks > 0].astype(float)

    if len(valid_p) < 3 or len(valid_r) < 3:
        return None

    pp_intervals = np.diff(valid_p) / fs * 1000  # ms
    rr_intervals = np.diff(valid_r) / fs * 1000

    # P-P should be regular (low CV)
    pp_cv = np.std(pp_intervals) / np.mean(pp_intervals) if np.mean(pp_intervals) > 0 else 1
    rr_cv = np.std(rr_intervals) / np.mean(rr_intervals) if np.mean(rr_intervals) > 0 else 1

    # PR intervals should be VARIABLE (high CV) in complete AVB
    pr_intervals = []
    for beat in fpt:
        if beat[COL_PON] > 0 and beat[COL_QRSON] > 0:
            pr_intervals.append((beat[COL_QRSON] - beat[COL_PON]) / fs * 1000)

    pr_cv = np.std(pr_intervals) / np.mean(pr_intervals) if pr_intervals and np.mean(pr_intervals) > 0 else 0

    atrial_rate = 60000 / np.mean(pp_intervals) if np.mean(pp_intervals) > 0 else None
    ventricular_rate = 60000 / np.mean(rr_intervals) if np.mean(rr_intervals) > 0 else None

    # Complete AVB criteria:
    # 1. Both P-P and R-R are regular (CV < 0.15)
    # 2. PR interval varies widely (CV > 0.3)
    # 3. Atrial rate > ventricular rate
    is_dissociated = (pp_cv < 0.15 and rr_cv < 0.15 and pr_cv > 0.3
                      and atrial_rate and ventricular_rate
                      and atrial_rate > ventricular_rate * 1.2)

    return {
        "dissociated": is_dissociated,
        "atrial_rate": atrial_rate,
        "ventricular_rate": ventricular_rate,
        "pp_cv": pp_cv,
        "rr_cv": rr_cv,
        "pr_cv": pr_cv,
    }
```

---

## Summary: What to Add to the Narrator

| Enhancement | Math Operation | Lines of Code | Diseases Unlocked |
|------------|---------------|---------------|-------------------|
| ST curvature | 2nd derivative (polyfit deg=2) | ~15 | Pericarditis, Brugada, STEMI |
| T-wave symmetry | ascending/descending ratio | ~10 | Wellens, de Winter, LVH strain |
| Biphasic T detection | zero-crossing in T-wave | ~15 | Wellens Type A |
| QRS morphology pattern | zero-crossing + net area | ~20 | LBBB, RBBB, WPW |
| Terminal QRS polarity | mean of last 40ms | ~8 | Sgarbossa concordance |
| Concordance flag | compare terminal QRS to ST | ~10 | Sgarbossa LBBB+STEMI |
| PR depression | PR segment vs TP baseline | ~10 | Pericarditis |
| AV dissociation | P-P vs R-R independence | ~25 | Complete AVB |
| **TOTAL** | | **~113 lines** | **10+ diseases** |
