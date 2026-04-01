"""
Beat Mastermind: Condition-Aware Consensus Fiducial Detection
=============================================================

Instead of running T and P detectors independently with hardcoded windows,
the mastermind:

1. Segments the ECG into beats using reliable R-peak anchors
2. Catalogs ALL local extrema in each beat
3. Detects the rhythm / condition (AFIB, BBB, normal, etc.)
4. Builds a consensus template across beats
5. Assigns fiducial points jointly using the template + physiological rules

This produces robust delineation across normal sinus rhythm, AFIB, LBBB/RBBB,
MI, LVH, STTC, and other conditions.
"""

import numpy as np
from scipy.signal import find_peaks, butter, filtfilt

# =====================================================================
# Physiological timing windows (ms relative to R peak)
# =====================================================================
# Each fiducial has an expected timing range relative to R.
# Negative = before R; positive = after R.
TIMING_WINDOWS = {
    'Q':      (-80, -2),
    'S':      (2, 100),
    'Ton':    (60, 400),
    'Tpeak':  (120, 550),
    'Toff':   (180, 650),
}

# P-wave windows are relative to the NEXT R peak (expressed as offset
# from current R, so they depend on RR interval).
P_WINDOWS_FROM_NEXT_R = {
    'Pon':   (-300, -60),
    'Ppeak': (-250, -80),
    'Poff':  (-200, -20),
}


# =====================================================================
# Phase 1: Condition detection
# =====================================================================

def detect_condition(signal, fs, fpt):
    """Analyze signal and FPT to classify rhythm and QRS morphology.

    Returns
    -------
    dict with keys:
        rhythm     : 'sinus' | 'afib' | 'tachy' | 'brady'
        qrs_wide   : bool (median QRS > 120 ms)
        has_p_waves: bool
        pvc_beats  : list[int] — indices of suspected PVC beats
        hr_bpm     : float — heart rate
    """
    n = len(fpt)
    result = {
        'rhythm': 'sinus',
        'qrs_wide': False,
        'has_p_waves': True,
        'pvc_beats': [],
        'hr_bpm': 75.0,
    }
    if n < 3:
        return result

    r_peaks = fpt[:, 5].astype(float)
    rr = np.diff(r_peaks) / fs  # seconds

    # Heart rate
    median_rr = float(np.median(rr))
    if median_rr > 0:
        result['hr_bpm'] = 60.0 / median_rr

    # Rhythm classification based on RR variability
    if len(rr) >= 4:
        rr_cv = float(np.std(rr) / (np.mean(rr) + 1e-9))
        # AFIB: irregularly irregular (high CV) — threshold tuned from
        # PTB-XL validation: sinus patients have CV < 0.10 typically,
        # AFIB patients have CV > 0.15.
        if rr_cv > 0.15:
            result['rhythm'] = 'afib'
            result['has_p_waves'] = False

    # Heart rate classification
    if result['hr_bpm'] > 100:
        if result['rhythm'] == 'sinus':
            result['rhythm'] = 'tachy'
    elif result['hr_bpm'] < 60:
        if result['rhythm'] == 'sinus':
            result['rhythm'] = 'brady'

    # QRS width
    qrs_on = fpt[:, 3].astype(float)
    qrs_off = fpt[:, 7].astype(float)
    valid_qrs = (qrs_on > 0) & (qrs_off > qrs_on)
    if valid_qrs.any():
        qrs_dur_ms = (qrs_off[valid_qrs] - qrs_on[valid_qrs]) / fs * 1000
        result['qrs_wide'] = bool(np.median(qrs_dur_ms) > 120)

    # PVC detection: beats with unusually wide QRS and short preceding RR
    pvc_list = []
    for i in range(1, n):
        if not valid_qrs[i]:
            continue
        dur_ms = (qrs_off[i] - qrs_on[i]) / fs * 1000
        rr_before = (r_peaks[i] - r_peaks[i - 1]) / fs
        if dur_ms > 160 and rr_before < 0.85 * median_rr:
            pvc_list.append(i)
    result['pvc_beats'] = pvc_list

    return result


# =====================================================================
# Phase 2: Extrema catalog
# =====================================================================

def _bandpass_for_extrema(signal, fs, lo=0.5, hi=40.0):
    """Light bandpass to reduce noise before extrema detection."""
    nyq = fs / 2
    lo_n = max(lo / nyq, 0.001)
    hi_n = min(hi / nyq, 0.999)
    b, a = butter(2, [lo_n, hi_n], btype='band')
    return filtfilt(b, a, signal, padtype='even')


def catalog_extrema(signal, fs, fpt):
    """Find all local extrema within each beat's RR segment.

    Returns
    -------
    list of dicts, one per beat:
        {'beat_idx', 'r_peak', 'rr_before_ms', 'rr_after_ms',
         'extrema': list of (sample, rel_ms, amplitude, prominence, is_peak)}
    """
    sig = _bandpass_for_extrema(signal, fs)
    n_beats = len(fpt)
    r_peaks = fpt[:, 5].astype(int)
    N = len(signal)

    # Compute segment boundaries: mid-RR on each side
    seg_starts = np.zeros(n_beats, dtype=int)
    seg_ends = np.zeros(n_beats, dtype=int)
    for i in range(n_beats):
        if i == 0:
            seg_starts[i] = max(0, r_peaks[i] - int(0.4 * fs))
        else:
            seg_starts[i] = (r_peaks[i - 1] + r_peaks[i]) // 2
        if i == n_beats - 1:
            seg_ends[i] = min(N, r_peaks[i] + int(0.6 * fs))
        else:
            seg_ends[i] = (r_peaks[i] + r_peaks[i + 1]) // 2

    beats = []
    for i in range(n_beats):
        lo = seg_starts[i]
        hi = seg_ends[i]
        r = r_peaks[i]

        rr_before = (r_peaks[i] - r_peaks[i - 1]) / fs * 1000 if i > 0 else 0.0
        rr_after = (r_peaks[i + 1] - r_peaks[i]) / fs * 1000 if i < n_beats - 1 else 0.0

        seg = sig[lo:hi]
        if len(seg) < 10:
            beats.append({
                'beat_idx': i, 'r_peak': r,
                'rr_before_ms': rr_before, 'rr_after_ms': rr_after,
                'extrema': [],
            })
            continue

        # Find peaks (maxima) — use low prominence to capture small P waves
        pks_idx, pks_props = find_peaks(seg, distance=max(1, int(0.02 * fs)),
                                        prominence=0.002)
        # Find troughs (minima)
        troughs_idx, tr_props = find_peaks(-seg, distance=max(1, int(0.02 * fs)),
                                           prominence=0.002)

        extrema = []
        for j, pk in enumerate(pks_idx):
            abs_s = lo + pk
            rel_ms = (abs_s - r) / fs * 1000
            prom = float(pks_props['prominences'][j]) if 'prominences' in pks_props else 0.0
            extrema.append((int(abs_s), float(rel_ms), float(signal[abs_s]),
                            prom, True))
        for j, tr in enumerate(troughs_idx):
            abs_s = lo + tr
            rel_ms = (abs_s - r) / fs * 1000
            prom = float(tr_props['prominences'][j]) if 'prominences' in tr_props else 0.0
            extrema.append((int(abs_s), float(rel_ms), float(signal[abs_s]),
                            prom, False))

        extrema.sort(key=lambda x: x[0])

        beats.append({
            'beat_idx': i, 'r_peak': r,
            'rr_before_ms': rr_before, 'rr_after_ms': rr_after,
            'extrema': extrema,
        })

    return beats


# =====================================================================
# Phase 3: Consensus template
# =====================================================================

def build_consensus_template(beat_features, condition, fs):
    """Build a median-position template for each fiducial from extrema clusters.

    For each fiducial slot (Q, S, Ton, Tpeak, Toff, Pon, Ppeak, Poff),
    collects the best-matching extremum from each beat, then computes
    the median position and amplitude.

    Returns
    -------
    dict: slot_name -> {'median_rel_ms', 'std_ms', 'median_amp',
                        'is_peak', 'presence_rate'}
    """
    pvc_set = set(condition.get('pvc_beats', []))
    n_beats = len(beat_features)

    # Collect candidates per slot
    slot_candidates = {}
    for name, (lo_ms, hi_ms) in TIMING_WINDOWS.items():
        slot_candidates[name] = []

    if condition.get('has_p_waves', True):
        for name in P_WINDOWS_FROM_NEXT_R:
            slot_candidates[name] = []

    for bf in beat_features:
        idx = bf['beat_idx']
        if idx in pvc_set:
            continue

        rr_after = bf['rr_after_ms']

        for name, (lo_ms, hi_ms) in TIMING_WINDOWS.items():
            # Expected polarity for this slot
            expect_peak = name in ('Tpeak',)
            expect_trough = name in ('Q', 'S')

            candidates = []
            for (samp, rel_ms, amp, prom, is_peak) in bf['extrema']:
                if lo_ms <= rel_ms <= hi_ms:
                    candidates.append((samp, rel_ms, amp, prom, is_peak))

            if not candidates:
                continue

            # Pick the best candidate by prominence
            if name == 'Q':
                # Q = most prominent trough before R
                troughs = [c for c in candidates if not c[4]]
                if troughs:
                    best = max(troughs, key=lambda c: c[3])
                    slot_candidates[name].append(best)
            elif name == 'S':
                # S = most prominent trough after R
                troughs = [c for c in candidates if not c[4]]
                if troughs:
                    best = max(troughs, key=lambda c: c[3])
                    slot_candidates[name].append(best)
            elif name == 'Tpeak':
                # Tpeak = most prominent extremum in the T-wave window
                best = max(candidates, key=lambda c: c[3])
                slot_candidates[name].append(best)
            elif name == 'Ton':
                # Ton = closest qualifying extremum to QRS offset side
                # (the one nearest to lo_ms boundary)
                best = min(candidates, key=lambda c: abs(c[1] - lo_ms))
                slot_candidates[name].append(best)
            elif name == 'Toff':
                # Toff = closest qualifying extremum past Tpeak
                best = max(candidates, key=lambda c: c[1])
                slot_candidates[name].append(best)

        # P-wave: timing relative to NEXT R
        if condition.get('has_p_waves', True) and rr_after > 200:
            for name, (lo_ms, hi_ms) in P_WINDOWS_FROM_NEXT_R.items():
                # Convert to relative-to-current-R
                adj_lo = rr_after + lo_ms
                adj_hi = rr_after + hi_ms

                candidates = []
                for (samp, rel_ms, amp, prom, is_peak) in bf['extrema']:
                    if adj_lo <= rel_ms <= adj_hi:
                        candidates.append((samp, rel_ms, amp, prom, is_peak))

                if not candidates:
                    continue

                if name == 'Ppeak':
                    peaks = [c for c in candidates if c[4]]
                    if peaks:
                        best = max(peaks, key=lambda c: c[3])
                    else:
                        best = max(candidates, key=lambda c: c[3])
                    slot_candidates[name].append(best)
                elif name == 'Pon':
                    best = min(candidates, key=lambda c: c[1])
                    slot_candidates[name].append(best)
                elif name == 'Poff':
                    best = max(candidates, key=lambda c: c[1])
                    slot_candidates[name].append(best)

    # Build template from collected candidates
    template = {}
    usable_beats = max(1, n_beats - len(pvc_set))
    for name, cands in slot_candidates.items():
        if len(cands) < 2:
            continue
        rels = np.array([c[1] for c in cands])
        amps = np.array([c[2] for c in cands])
        is_peaks = [c[4] for c in cands]
        template[name] = {
            'median_rel_ms': float(np.median(rels)),
            'std_ms': float(np.std(rels)),
            'median_amp': float(np.median(amps)),
            'is_peak': sum(is_peaks) > len(is_peaks) / 2,
            'presence_rate': len(cands) / usable_beats,
        }

    return template


# =====================================================================
# Phase 4: Per-beat fiducial assignment
# =====================================================================

def assign_fiducials(signal, fs, fpt, beat_features, template, condition):
    """Assign fiducial points to each beat using the consensus template.

    Updates columns 0-2 (P), 8-11 (L, T) of fpt in place.
    QRS columns (3-7) are kept from the existing QRS detection.

    Returns
    -------
    fpt : updated (n_beats, 13) array
    """
    N = len(signal)
    n_beats = len(fpt)
    pvc_set = set(condition.get('pvc_beats', []))

    for i in range(n_beats):
        r = int(fpt[i, 5])
        if r <= 0:
            continue

        bf = beat_features[i] if i < len(beat_features) else None
        if bf is None or len(bf['extrema']) == 0:
            continue

        is_pvc = i in pvc_set
        extrema = bf['extrema']

        # --- Assign T-wave fiducials ---
        if 'Tpeak' in template and not is_pvc:
            tp_tmpl = template['Tpeak']
            target_ms = tp_tmpl['median_rel_ms']
            target_amp = tp_tmpl['median_amp']
            expect_is_peak = tp_tmpl['is_peak']

            # QRSoff guard: T peak must be >= 100ms after QRSoff
            qrs_off = int(fpt[i, 7])
            if qrs_off <= 0:
                qrs_off = r + int(round(50e-3 * fs))
            min_tpeak_sample = qrs_off + int(round(0.10 * fs))

            best_tp = None
            best_cost = float('inf')
            for (samp, rel_ms, amp, prom, is_peak) in extrema:
                if samp < min_tpeak_sample:
                    continue
                lo_ms, hi_ms = TIMING_WINDOWS['Tpeak']
                if not (lo_ms - 50 <= rel_ms <= hi_ms + 50):
                    continue

                cost = (abs(rel_ms - target_ms) / 50.0 +
                        2.0 * (0 if is_peak == expect_is_peak else 1) +
                        1.0 / (prom + 0.01))
                if cost < best_cost:
                    best_cost = cost
                    best_tp = samp

            if best_tp is not None:
                # Refine: snap to actual signal max/min in +-20ms window
                w = int(round(0.02 * fs))
                lo_f = max(0, best_tp - w)
                hi_f = min(N, best_tp + w + 1)
                seg = signal[lo_f:hi_f]
                if len(seg) > 0:
                    if expect_is_peak:
                        best_tp = lo_f + int(np.argmax(seg))
                    else:
                        best_tp = lo_f + int(np.argmin(seg))
                fpt[i, 10] = best_tp

        # T onset
        tpeak = int(fpt[i, 10])
        qrs_off = int(fpt[i, 7])
        if qrs_off <= 0:
            qrs_off = r + int(round(50e-3 * fs))

        if tpeak > 0 and 'Ton' in template:
            # Ton: find the inflection point between QRSoff and Tpeak
            ton_search_lo = qrs_off + int(round(0.02 * fs))
            ton_search_hi = tpeak - int(round(0.02 * fs))
            if ton_search_lo < ton_search_hi:
                seg = signal[ton_search_lo:ton_search_hi]
                if len(seg) > 2:
                    # Find the point of minimum absolute amplitude (closest
                    # to isoelectric) — this is where the T wave begins
                    abs_seg = np.abs(seg - np.median(signal[max(0,qrs_off-int(0.05*fs)):qrs_off]))
                    ton_local = int(np.argmin(abs_seg))
                    fpt[i, 9] = ton_search_lo + ton_local
                else:
                    fpt[i, 9] = ton_search_lo
            else:
                fpt[i, 9] = qrs_off + int(round(0.06 * fs))

        # T offset — find where the T wave returns to isoelectric line
        if tpeak > 0:
            min_toff_dist = int(round(0.08 * fs))   # 80 ms minimum
            # Adaptive max: longer for bradycardia (big RR), shorter for tachy
            rr_ms = bf['rr_after_ms'] if (bf and bf['rr_after_ms'] > 0) else 800
            if rr_ms > 1000:
                max_toff_dist = int(round(0.30 * fs))   # 300 ms for brady
            elif rr_ms > 700:
                max_toff_dist = int(round(0.25 * fs))   # 250 ms normal
            else:
                max_toff_dist = int(round(0.20 * fs))   # 200 ms for tachy
            toff_search_lo = tpeak + min_toff_dist

            if i < n_beats - 1:
                next_qrs_on = int(fpt[i + 1, 3])
                if next_qrs_on <= 0:
                    next_qrs_on = int(fpt[i + 1, 5]) - int(round(0.05 * fs))
                toff_search_hi = next_qrs_on - int(round(0.02 * fs))
            else:
                toff_search_hi = min(N - 1, tpeak + int(round(0.35 * fs)))
            # Hard cap: never search beyond 300ms from Tpeak
            toff_search_hi = min(toff_search_hi, tpeak + max_toff_dist, N - 1)

            if toff_search_lo < toff_search_hi:
                seg = signal[toff_search_lo:toff_search_hi]
                if len(seg) > 3:
                    qrs_on_i = int(fpt[i, 3])
                    if qrs_on_i > 0:
                        bl_lo = max(0, qrs_on_i - int(0.04 * fs))
                        bl_hi = qrs_on_i
                    else:
                        bl_lo = max(0, r - int(0.12 * fs))
                        bl_hi = max(bl_lo + 1, r - int(0.06 * fs))
                    baseline = float(np.median(signal[bl_lo:bl_hi])) if bl_hi > bl_lo else 0.0

                    t_amp = signal[tpeak] - baseline
                    # Toff: where signal drops to within 30% of peak amplitude
                    thresh_amp = baseline + 0.30 * t_amp
                    if abs(t_amp) > 0.01:
                        if t_amp > 0:
                            crosses = np.where(seg <= thresh_amp)[0]
                        else:
                            crosses = np.where(seg >= thresh_amp)[0]
                        if len(crosses) > 0:
                            fpt[i, 11] = toff_search_lo + int(crosses[0])
                        else:
                            # Fallback: 60% between Tpeak and search boundary
                            fpt[i, 11] = tpeak + int(0.6 * (toff_search_hi - tpeak))
                    else:
                        fpt[i, 11] = tpeak + int(round(0.12 * fs))
                else:
                    fpt[i, 11] = tpeak + int(round(0.12 * fs))
            else:
                fpt[i, 11] = tpeak + int(round(0.12 * fs))

            fpt[i, 11] = max(tpeak + min_toff_dist,
                             min(int(fpt[i, 11]), tpeak + max_toff_dist, N - 1))

        # L point (ST midpoint)
        ton = int(fpt[i, 9])
        if qrs_off > 0 and ton > qrs_off:
            fpt[i, 8] = (qrs_off + ton) // 2
        elif qrs_off > 0:
            s_pos = int(fpt[i, 6])
            if s_pos > 0:
                fpt[i, 8] = int(round(0.55 * qrs_off + 0.45 * s_pos))
            else:
                fpt[i, 8] = qrs_off + int(round(0.02 * fs))

        # --- Assign P-wave fiducials ---
        if condition.get('has_p_waves', True) and not is_pvc and i > 0:
            qrs_on = int(fpt[i, 3])
            if qrs_on <= 0:
                qrs_on = r - int(round(0.05 * fs))

            prev_r = int(fpt[i - 1, 5])
            prev_toff = int(fpt[i - 1, 11])
            if prev_toff <= 0 or prev_toff <= prev_r:
                prev_toff = prev_r + int(0.35 * fs)

            # P-wave search: between previous Toff+40ms and current QRSon-10ms
            # Also cap: P search window shouldn't start more than 300ms before QRSon
            p_search_lo = max(prev_toff + int(round(0.04 * fs)),
                              qrs_on - int(round(0.30 * fs)))
            p_search_hi = qrs_on - int(round(0.01 * fs))

            # Sanity: at least 60ms window for meaningful P detection
            if p_search_hi - p_search_lo >= int(0.06 * fs) and p_search_hi > 0:
                seg = signal[p_search_lo:p_search_hi]
                if len(seg) > 5:
                    pks_i, pks_p = find_peaks(seg, prominence=0.002,
                                               distance=max(1, int(0.03 * fs)))
                    if len(pks_i) > 0:
                        best = pks_i[np.argmax(pks_p['prominences'])]
                        ppeak_abs = p_search_lo + int(best)

                        # Refine to signal max/min within +-15ms
                        w = int(round(0.015 * fs))
                        lo_f = max(p_search_lo, ppeak_abs - w)
                        hi_f = min(p_search_hi, ppeak_abs + w + 1)
                        ppeak_abs = lo_f + int(np.argmax(signal[lo_f:hi_f]))
                        fpt[i, 1] = ppeak_abs

                        # Estimate baseline from start of P search window
                        bl_seg_len = max(1, int(0.02 * fs))
                        baseline = float(np.median(seg[:bl_seg_len]))
                        p_amp = signal[ppeak_abs] - baseline

                        # P onset: where signal departs from baseline toward peak
                        pon_seg = signal[p_search_lo:ppeak_abs]
                        if len(pon_seg) > 2 and abs(p_amp) > 0.005:
                            thresh = baseline + 0.15 * p_amp
                            if p_amp > 0:
                                above = np.where(pon_seg >= thresh)[0]
                            else:
                                above = np.where(pon_seg <= thresh)[0]
                            if len(above) > 0:
                                fpt[i, 0] = p_search_lo + int(above[0])
                            else:
                                fpt[i, 0] = max(p_search_lo, ppeak_abs - int(0.04 * fs))
                        else:
                            fpt[i, 0] = max(p_search_lo, ppeak_abs - int(0.04 * fs))

                        # P offset: where signal returns toward baseline after peak
                        poff_lo = ppeak_abs + 1
                        poff_hi = min(qrs_on, ppeak_abs + int(0.08 * fs))
                        if poff_lo < poff_hi:
                            poff_seg = signal[poff_lo:poff_hi]
                            if len(poff_seg) > 2 and abs(p_amp) > 0.005:
                                thresh = baseline + 0.15 * p_amp
                                if p_amp > 0:
                                    below = np.where(poff_seg <= thresh)[0]
                                else:
                                    below = np.where(poff_seg >= thresh)[0]
                                if len(below) > 0:
                                    fpt[i, 2] = poff_lo + int(below[0])
                                else:
                                    fpt[i, 2] = min(poff_hi, qrs_on - int(0.01 * fs))
                            else:
                                fpt[i, 2] = min(poff_hi, qrs_on - int(0.01 * fs))
                        else:
                            fpt[i, 2] = max(ppeak_abs + 1, min(qrs_on - int(0.01 * fs), N - 1))

        # Clamp all values
        for col in [0, 1, 2, 8, 9, 10, 11]:
            fpt[i, col] = max(0, min(int(fpt[i, col]), N - 1))

    return fpt


# =====================================================================
# Main entry point
# =====================================================================

def mastermind_delineate(signal, fs, fpt, lead_name=None):
    """Full beat-mastermind fiducial detection for a single lead.

    Parameters
    ----------
    signal    : 1-D numpy array
    fs        : sampling frequency (Hz)
    fpt       : (n_beats, 13) FPT with QRS columns (3-7) already filled
    lead_name : optional lead name string (e.g. 'II', 'V1')

    Returns
    -------
    fpt : updated FPT with all 13 columns filled
    """
    signal = np.asarray(signal, dtype=float).ravel()
    fpt = np.asarray(fpt, dtype=int).copy()
    N = len(signal)

    if len(fpt) < 2:
        return fpt

    # Phase 1: Condition detection
    condition = detect_condition(signal, fs, fpt)

    # Phase 2: Catalog extrema
    beat_features = catalog_extrema(signal, fs, fpt)

    # Phase 3: Build consensus template
    template = build_consensus_template(beat_features, condition, fs)

    # Phase 4: Assign fiducials
    fpt = assign_fiducials(signal, fs, fpt, beat_features, template, condition)

    return fpt
