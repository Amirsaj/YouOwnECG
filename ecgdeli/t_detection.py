"""
T-wave detection - Python port of T_Detection.m.

Detects T-wave onset, peak, and offset using the reverse-biorthogonal 3.3
wavelet stationary wavelet transform (SWT) on a signal where P and QRS
have been replaced by sigmoid transitions.
"""

import numpy as np
import pywt
from scipy import signal as sp_signal

from .filtering import ecg_high_low_filter, ecg_baseline_removal
from .wave_removal import remove_pqrs


def _swt_rbio33_all_levels(sig_padded, n_levels):
    """Compute all detail levels of rbio3.3 SWT.

    Returns Dx1 array (N_original x n_levels) for forward transform and
    Dx2 for the reversed-signal transform.

    pywt.swt(data, wavelet, level=n) returns
        [(cA_n, cD_n), ..., (cA_1, cD_1)]
    so coeffs[0] = coarsest (level n), coeffs[n-1] = finest (level 1).
    MATLAB swd(lvl, :) for a level-x transform = Python coeffs[x-lvl][1].
    """
    N_pad = len(sig_padded)

    # Forward transform
    coeff_fwd = pywt.swt(sig_padded, 'rbio3.3', level=n_levels)
    # Reversed transform
    coeff_rev = pywt.swt(sig_padded[::-1], 'rbio3.3', level=n_levels)

    return coeff_fwd, coeff_rev, N_pad


def t_detection(signal, samplerate, fpt):
    """Detect T-wave onset, peak, and offset for each beat.

    Parameters
    ----------
    signal     : 1-D numpy array (N,)
    samplerate : sampling frequency in Hz
    fpt        : (n_beats, 13) Fiducial Point Table from QRS detection
                 (0-indexed positions)

    Returns
    -------
    fpt : updated FPT with columns 9 (Ton), 10 (Tpeak), 11 (Toff) filled.
          Column 8 (L point) is also set.
    """
    print('Detecting T Waves...')

    signal = np.asarray(signal, dtype=float).ravel()
    N = len(signal)
    fpt = fpt.copy()
    n_beats = len(fpt)

    if n_beats < 2:
        print('Too few beats for T detection.')
        return fpt

    # -----------------------------------------------------------------
    # 1. Remove P+QRS; bandpass + baseline removal
    # -----------------------------------------------------------------
    signal_pre = signal.copy()
    sig_rep, interval_sigmoid = remove_pqrs(signal, samplerate, fpt)
    sig_rep = ecg_high_low_filter(sig_rep, samplerate, 0.3, 20, 'B')

    w = 750e-3
    _, baseline = ecg_baseline_removal(sig_rep, samplerate, w, 0.75)
    w2 = 2.0
    _, baseline = ecg_baseline_removal(baseline, samplerate, w2, 0.75)
    sig_rep = sig_rep - baseline

    # -----------------------------------------------------------------
    # 2. Wavelet transform: rbio3.3, all levels up to x
    # -----------------------------------------------------------------
    x = max(int(np.floor(np.log2(samplerate / 2 / 7))) + 1, 1)

    # Pad to next power of 2
    npo = int(np.ceil(np.log2(N)))
    l_pad = 2 ** npo
    if l_pad == N:
        l_pad = 2 ** (npo + 1)
    l1_p = int(np.floor((l_pad - N) / 2))  # right pad
    l2_p = l_pad - N - l1_p                 # left pad

    sig_padded = np.concatenate([
        np.full(l2_p, sig_rep[0]),
        sig_rep,
        np.full(l1_p, sig_rep[-1])
    ])

    try:
        cf, cr, _ = _swt_rbio33_all_levels(sig_padded, x)
    except Exception as e:
        print(f'Warning: wavelet transform failed ({e}). Skipping T detection.')
        return fpt

    # Assemble Dx (N x x):  Dx[:, lvl-1] = level lvl coefficients
    # pywt returns coarsest first: cf[0] = level x, cf[x-1] = level 1
    Dx1 = np.full((N, x), np.nan)
    Dx2 = np.full((N, x), np.nan)

    for lvl in range(1, x + 1):
        py_idx = x - lvl  # coeffs index (0 = coarsest = level x)
        d_fwd = np.array(cf[py_idx][1])[l2_p: l2_p + N]
        d_rev = np.array(cr[py_idx][1])[::-1][l2_p: l2_p + N]
        Dx1[:, lvl - 1] = d_fwd
        Dx2[:, lvl - 1] = d_rev

    Dx = -(Dx1 + Dx2)

    # Column index for the coarsest level (MATLAB lvl = x → Python col = x-1)
    lvl_col = x - 1

    # -----------------------------------------------------------------
    # 3. Find TPOS (approximate T peak location using wavelet peaks)
    # -----------------------------------------------------------------
    pks_idx, _ = sp_signal.find_peaks(np.abs(Dx[:, lvl_col]))
    pks_vals = np.abs(Dx[pks_idx, lvl_col])

    RR = np.diff(fpt[:, 5])
    if len(RR) == 0:
        return fpt
    next_thresh = float(np.min(RR)) * 1.9

    TPOS = np.zeros(n_beats, dtype=int)

    for i in range(n_beats):
        qrs_off = int(fpt[i, 7])
        # Guard: if QRSoff is 0 (unmatched beat), approximate it from R peak
        if qrs_off == 0:
            qrs_off = int(fpt[i, 5]) + int(round(50e-3 * samplerate))
        search_lo = qrs_off + int(round(100e-3 * samplerate))

        if i == n_beats - 1 or fpt[i + 1, 5] - fpt[i, 5] >= next_thresh:
            if i == 0 or fpt[i, 5] - fpt[i - 1, 5] >= next_thresh:
                search_hi = qrs_off + int(round(0.4 * samplerate))
            else:
                search_hi = int(round(0.5 * (fpt[i - 1, 5] + fpt[i, 5])))
        else:
            search_hi = int(round(0.5 * (fpt[i, 5] + fpt[i + 1, 5])))

        search_lo = max(0, min(search_lo, N - 1))
        search_hi = max(search_lo + 1, min(search_hi, N - 1))

        I_ext = np.where((pks_idx >= search_lo) & (pks_idx < search_hi))[0]

        if len(I_ext) == 0:
            if i == n_beats - 1 or fpt[i + 1, 5] - fpt[i, 5] >= next_thresh:
                if i == 0 or fpt[i, 5] - fpt[i - 1, 5] >= next_thresh:
                    TPOS[i] = search_lo
                elif i == n_beats - 1 and fpt[i, 5] + abs(fpt[i - 1, 5] - TPOS[i - 1]) >= N:
                    TPOS[i] = N - 4
                else:
                    TPOS[i] = fpt[i, 5] + abs(fpt[i - 1, 5] - TPOS[i - 1])
            else:
                TPOS[i] = int(round(2 / 3 * fpt[i, 5] + 1 / 3 * fpt[i + 1, 5]))
        else:
            best = I_ext[np.argmax(pks_vals[I_ext])]
            TPOS[i] = int(pks_idx[best])

        TPOS[i] = np.clip(TPOS[i], 0, N - 1)

    # -----------------------------------------------------------------
    # 4. Find isoline (zero-crossings of Dx at a coarser level)
    # -----------------------------------------------------------------
    # MATLAB T_Detection.m line 144 re-assigns x = floor(log2(fs/2/7)) - 1
    # for the isoline search (a DIFFERENT x from the SWT level x above).
    # At 500 Hz: x_iso = floor(log2(35.7)) - 1 = 5 - 1 = 4.
    # MATLAB Dx(:, x_iso) is 1-indexed column x_iso = level x_iso.
    # Python (0-indexed): level x_iso is stored in column (x_iso - 1).
    x_iso = int(np.floor(np.log2(samplerate / 2 / 7))) - 1
    x_iso = max(1, x_iso)
    iso_col = x_iso - 1  # 0-indexed column for level x_iso
    iso_col = max(0, min(iso_col, Dx.shape[1] - 1))

    iso_position = np.full(n_beats - 1, np.nan)

    for i in range(1, n_beats):
        r_cur = int(fpt[i, 5])
        qrs_on = int(fpt[i, 3])

        if r_cur - fpt[i - 1, 5] >= next_thresh:
            lo_iso = max(qrs_on - int(round(samplerate)), 0)
        else:
            lo_iso = max(int(fpt[i - 1, 3]), 0)

        hi_iso = max(qrs_on, lo_iso + 1)
        hi_iso = min(hi_iso, N)

        Dx_seg = Dx[lo_iso:hi_iso, iso_col]
        sgn = np.sign(Dx_seg)
        zc = np.where(np.abs(sgn[:-1] + sgn[1:]) == 0)[0] + lo_iso

        if len(zc) > 0:
            closest = zc[np.argmin(np.abs(zc - qrs_on))]
            iso_position[i - 1] = closest

    # Fill NaN isoline positions
    nan_mask = np.isnan(iso_position)
    if nan_mask.any():
        valid = np.where(~nan_mask)[0]
        if len(valid) >= 2:
            d_iso = np.diff(iso_position[valid]).mean()
            for bad in np.where(nan_mask)[0]:
                prev = np.where(~nan_mask[:bad])[0]
                if len(prev) > 0:
                    iso_position[bad] = iso_position[prev[-1]] + (bad - prev[-1]) * d_iso
                else:
                    next_v = np.where(~nan_mask[bad + 1:])[0]
                    if len(next_v) > 0:
                        iso_position[bad] = iso_position[bad + 1 + next_v[0]]
        elif len(valid) == 1:
            iso_position[nan_mask] = iso_position[valid[0]]
        else:
            iso_position[:] = 0

    iso_position = np.clip(iso_position.astype(int), 0, N - 1)

    # -----------------------------------------------------------------
    # 5. Determine T-wave polarity (T_type)
    # -----------------------------------------------------------------
    if len(RR) >= 3:
        X = np.column_stack([RR[:-1], RR[1:]])
        mean_X = X.mean(axis=0)
        rot = (1 / np.sqrt(2)) * np.array([[1, -1], [1, 1]])
        score_T = (X - mean_X) @ rot
        d1 = np.abs(score_T[:, 0])
        thl1 = 2.5 * np.std(d1, ddof=1)
        idx_normal = np.where((score_T[:, 0] >= -thl1) & (score_T[:, 1] <= 0))[0] + 1
        idx_normal = idx_normal[1:-1] if len(idx_normal) > 2 else idx_normal
    else:
        idx_normal = np.arange(n_beats)

    if len(idx_normal) == 0:
        idx_normal = np.arange(n_beats)

    MP = np.zeros((len(idx_normal), 2))
    SP = np.zeros_like(MP)

    for ii, i in enumerate(idx_normal):
        if i >= n_beats:
            continue
        L_w = max(1, int(round(TPOS[i] - fpt[i, 5] - 25e-3 * samplerate)))
        if i == n_beats - 1 or fpt[i + 1, 5] - fpt[i, 5] >= next_thresh:
            if i == 0 or fpt[i, 5] - fpt[i - 1, 5] >= next_thresh:
                R_w = int(round(0.2 * samplerate))
            else:
                R_w = max(1, int(round(0.5 * (fpt[i, 5] - TPOS[i - 1]))))
        else:
            R_w = max(1, int(round(0.5 * (fpt[i + 1, 5] - TPOS[i]))))

        lo_t = max(TPOS[i] - L_w, 0)
        hi_t = min(TPOS[i] + R_w + 1, N)
        if lo_t >= hi_t:
            continue

        seg_Dx = Dx[lo_t:hi_t, lvl_col]
        seg_sig = sig_rep[lo_t:hi_t]
        MP[ii] = [seg_Dx.max(), seg_Dx.min()]
        SP[ii] = [seg_sig.max(), seg_sig.min()]

    # T type from combined WT + signal polarity vote
    def _median_iqr(arr, q1=0.25, q2=0.75):
        lo, hi = np.quantile(arr, [q1, q2])
        sel = arr[(arr >= lo) & (arr <= hi)]
        return np.median(sel) if len(sel) > 0 else 0.0

    T_type = int(np.sign(
        _median_iqr(MP[:, 0]) + _median_iqr(MP[:, 1]) +
        _median_iqr(SP[:, 0]) + _median_iqr(SP[:, 1])
    ))
    if T_type == 0:
        T_type = 1

    # Refine T type
    if T_type == -1:
        combined = (_median_iqr(MP[:, 0]) + _median_iqr(MP[:, 1]) +
                    _median_iqr(SP[:, 0]) + _median_iqr(SP[:, 1]))
        th11 = np.quantile(MP[:, 0], 0.25)
        if abs(combined) < 0.3 * th11:
            if _median_iqr(MP[:, 0]) >= abs(_median_iqr(MP[:, 1])):
                T_type = 1

    # -----------------------------------------------------------------
    # 6. Refine TPEAK using WT peaks near TPOS
    # -----------------------------------------------------------------
    TPEAK = np.zeros(n_beats, dtype=int)

    for i in range(n_beats):
        L_w = max(1, int(round(TPOS[i] - int(fpt[i, 7]) - 75e-3 * samplerate)))
        if i == n_beats - 1 or fpt[i + 1, 5] - fpt[i, 5] >= next_thresh:
            if i == 0 or fpt[i, 5] - fpt[i - 1, 5] >= next_thresh:
                R_w = int(round(0.2 * samplerate))
            else:
                R_w = max(1, int(round(0.5 * (fpt[i, 5] - TPOS[i - 1]))))
        else:
            # Extend R_w to 75% of the remaining RR instead of 50%,
            # so that broad T waves whose peak is past the RR midpoint are found.
            R_w = max(1, int(round(0.75 * (fpt[i + 1, 5] - TPOS[i]))))

        lo_t = max(TPOS[i] - L_w, 0)
        hi_t = min(TPOS[i] + R_w + 1, N)

        if lo_t >= hi_t or lo_t < 0 or hi_t > N:
            TPEAK[i] = TPOS[i]
            continue

        wt_seg = Dx[lo_t:hi_t, lvl_col]

        peaks_pos, _ = sp_signal.find_peaks(wt_seg)
        peaks_neg, _ = sp_signal.find_peaks(-wt_seg)

        # Limit to sigmoid boundary
        if i < n_beats - 1:
            if fpt[i + 1, 5] - fpt[i, 5] > next_thresh:
                max_pos = int(fpt[i, 5] + round(0.8 * np.min(RR)))
            else:
                if interval_sigmoid is not None and i + 1 < len(interval_sigmoid):
                    max_pos = int(interval_sigmoid[i + 1, 0])
                else:
                    max_pos = int(fpt[i + 1, 5])
            peaks_pos = peaks_pos[peaks_pos + lo_t <= max_pos]
            peaks_neg = peaks_neg[peaks_neg + lo_t <= max_pos]

        if len(peaks_pos) == 0 and len(peaks_neg) == 0:
            TPEAK[i] = TPOS[i]
            continue

        # Sort by amplitude
        pos_amps = wt_seg[peaks_pos] if len(peaks_pos) > 0 else np.array([])
        neg_amps = wt_seg[peaks_neg] if len(peaks_neg) > 0 else np.array([])

        iso = float(signal_pre[iso_position[i - 1]] if i > 0 else signal_pre[iso_position[0]])

        if T_type > 0:
            if len(peaks_pos) == 1 and len(peaks_neg) == 0:
                best_loc = peaks_pos[0] + lo_t
                sign_flag = 1
            elif len(peaks_pos) == 0 and len(peaks_neg) > 0:
                best_loc = peaks_neg[np.argmax(np.abs(neg_amps))] + lo_t
                sign_flag = -1
            elif len(peaks_pos) > 0 and len(peaks_neg) > 0:
                if np.abs(neg_amps).max() > 5 * pos_amps.max():
                    best_loc = peaks_neg[np.argmax(np.abs(neg_amps))] + lo_t
                    sign_flag = -1
                else:
                    best_loc = peaks_pos[np.argmax(pos_amps)] + lo_t
                    sign_flag = 1
            else:
                best_loc = peaks_pos[np.argmax(pos_amps)] + lo_t
                sign_flag = 1
        else:
            if len(peaks_neg) == 1 and len(peaks_pos) == 0:
                best_loc = peaks_neg[0] + lo_t
                sign_flag = -1
            elif len(peaks_neg) == 0 and len(peaks_pos) > 0:
                best_loc = peaks_pos[np.argmax(pos_amps)] + lo_t
                sign_flag = 1
            elif len(peaks_neg) > 0 and len(peaks_pos) > 0:
                if pos_amps.max() > 5 * np.abs(neg_amps).max():
                    best_loc = peaks_pos[np.argmax(pos_amps)] + lo_t
                    sign_flag = 1
                else:
                    best_loc = peaks_neg[np.argmax(np.abs(neg_amps))] + lo_t
                    sign_flag = -1
            else:
                best_loc = peaks_neg[np.argmax(np.abs(neg_amps))] + lo_t
                sign_flag = -1

        # Refine in time domain ±40 ms
        fine_w = int(round(0.04 * samplerate))
        lo_fine = max(best_loc - fine_w, 0)
        hi_fine = min(best_loc + fine_w + 1, N)

        if lo_fine < hi_fine:
            seg_fine = signal_pre[lo_fine:hi_fine]
            if sign_flag == 1:
                best_loc = lo_fine + int(np.argmax(seg_fine))
            else:
                best_loc = lo_fine + int(np.argmin(seg_fine))

        TPEAK[i] = int(np.clip(best_loc, 0, N - 1))

    # -----------------------------------------------------------------
    # 7. Delineate T onset and offset
    #    Mirrors MATLAB T_Detection.m lines 392–514:
    #    • Find WT peaks at lvl_col (coarsest) and lvl_col-1 (finer) separately.
    #    • Ton  → last  WT peak in [TPEAK-L_w, TPEAK],  excluding peak ≤60ms from TPEAK.
    #    • Toff → first WT peak in [TPEAK, TPEAK+R_w],  excluding peak ≤80ms from TPEAK.
    #    • Density distribution used only as a fallback reference, not the primary answer.
    #    • Hard fallback: ±75ms when no peaks are found.
    # -----------------------------------------------------------------
    TON = np.full(n_beats, np.nan)
    TOFF = np.full(n_beats, np.nan)
    threshold_dist = 0.3
    fine_col = max(lvl_col - 1, 0)  # level lvl-1 in MATLAB = column lvl_col-1 here

    # Minimum distances (samples) to guard against spurious peaks
    min_dist_on = int(round(0.06 * samplerate))   # 60 ms
    min_dist_off = int(round(0.08 * samplerate))  # 80 ms
    fallback_ms = int(round(0.100 * samplerate))  # 100 ms fallback (was 75 ms)

    for i in range(n_beats):
        tp = int(TPEAK[i])
        qrs_off = int(fpt[i, 7])
        # Guard: if QRSoff is 0 (unmatched beat from sync), derive it from R peak
        if qrs_off == 0:
            qrs_off = int(fpt[i, 5]) + int(round(50e-3 * samplerate))

        # --- window widths (mirrors MATLAB lines 398–413) ---
        L_w = max(1, int(round(tp - int(fpt[i, 5]) - 25e-3 * samplerate)))
        if i == n_beats - 1 or fpt[i + 1, 5] - fpt[i, 5] >= next_thresh:
            if i == 0 or fpt[i, 5] - fpt[i - 1, 5] >= next_thresh:
                R_w = int(round(0.2 * samplerate))
            else:
                R_w = max(1, int(round(0.5 * (fpt[i, 5] - TPEAK[i - 1]))))
        else:
            R_w = max(1, int(round(0.5 * (fpt[i + 1, 5] - TPEAK[i]))))

        # Clip L_w so we don't go before QRSoff
        if tp - L_w < qrs_off:
            L_w = max(0, tp - qrs_off)

        # Clip R_w at sigmoid boundary of next beat
        if (i < n_beats - 1 and interval_sigmoid is not None and
                i + 1 < len(interval_sigmoid) and not np.isnan(interval_sigmoid[i + 1, 0])):
            sig_bound = int(interval_sigmoid[i + 1, 0])
            if tp + R_w > sig_bound:
                R_w = max(0, sig_bound - tp)

        L_w = max(L_w, 2)
        R_w = max(R_w, 2)

        lo_tp = max(tp - L_w, 0)
        hi_tp = min(tp + R_w + 1, N)

        if lo_tp >= hi_tp or hi_tp > Dx.shape[0]:
            TON[i] = qrs_off + fallback_ms
            TOFF[i] = tp + fallback_ms
            continue

        L_w_actual = tp - lo_tp
        R_w_actual = hi_tp - tp  # includes tp itself at index 0

        # --- WT peaks at coarsest level (lvl_col) ---
        seg_on_lvl = Dx[lo_tp: tp + 1, lvl_col]       # left side
        seg_off_lvl = Dx[tp: hi_tp, lvl_col]           # right side

        def _wt_peaks(seg):
            pp, _ = sp_signal.find_peaks(seg)
            pn, _ = sp_signal.find_peaks(-seg)
            return np.sort(np.concatenate([pp, pn]))

        loco_on_lvl = _wt_peaks(seg_on_lvl)
        loco_off_lvl = _wt_peaks(seg_off_lvl)

        # Remove peaks too close to TPEAK
        loco_on_lvl = loco_on_lvl[loco_on_lvl < L_w_actual - min_dist_on]
        loco_off_lvl = loco_off_lvl[loco_off_lvl > min_dist_off]

        # --- WT peaks at finer level (lvl_col - 1) ---
        seg_on_lvl1 = Dx[lo_tp: tp + 1, fine_col]
        seg_off_lvl1 = Dx[tp: hi_tp, fine_col]

        loco_on_lvl1 = _wt_peaks(seg_on_lvl1)
        loco_off_lvl1 = _wt_peaks(seg_off_lvl1)

        loco_on_lvl1 = loco_on_lvl1[loco_on_lvl1 < L_w_actual - int(round(0.04 * samplerate))]
        loco_off_lvl1 = loco_off_lvl1[loco_off_lvl1 > int(round(0.04 * samplerate))]

        # Convert local indices to absolute signal positions
        loco_on_lvl_abs = lo_tp + loco_on_lvl
        loco_on_lvl1_abs = lo_tp + loco_on_lvl1
        loco_off_lvl_abs = tp + loco_off_lvl
        loco_off_lvl1_abs = tp + loco_off_lvl1

        # --- density-based rough estimate (used as reference only) ---
        Dy = np.abs(Dx[lo_tp:hi_tp, fine_col])
        if L_w_actual > 0 and Dy[:L_w_actual].sum() > 0:
            Dy_L = Dy[:L_w_actual]
            dist_L = np.cumsum(Dy_L) / Dy_L.sum()
            ton_ref = lo_tp + int(np.searchsorted(dist_L, threshold_dist))
        else:
            ton_ref = tp - int(round(80e-3 * samplerate))

        if R_w_actual > 0 and Dy[L_w_actual:].sum() > 0:
            Dy_R = Dy[L_w_actual:]
            dist_R = np.cumsum(Dy_R) / Dy_R.sum()
            toff_ref = tp + int(np.searchsorted(dist_R, 1 - threshold_dist))
        else:
            toff_ref = tp + int(round(80e-3 * samplerate))

        # Isoline value for the current beat
        iso = float(signal_pre[iso_position[i - 1]] if i > 0 else signal_pre[iso_position[0]])

        # --- TON selection (mirrors MATLAB lines 463–486) ---
        if len(loco_on_lvl_abs) == 0:
            if len(loco_on_lvl1_abs) > 0:
                # pick nearest lvl1 peak to density estimate
                if (len(loco_on_lvl1_abs) > 1 and
                        (abs(loco_on_lvl1_abs[-2] - ton_ref) < abs(loco_on_lvl1_abs[-1] - ton_ref)
                         or abs(signal_pre[loco_on_lvl1_abs[-1]]) > 0.5 * abs(signal_pre[tp]))):
                    TON[i] = loco_on_lvl1_abs[-2]
                else:
                    TON[i] = loco_on_lvl1_abs[-1]
            else:
                # no WT peaks at all
                if qrs_off + fallback_ms - tp < int(50e-3 * samplerate):
                    TON[i] = lo_tp
                else:
                    TON[i] = qrs_off + fallback_ms
        elif (len(loco_on_lvl_abs) > 1 and signal_pre[tp] < iso and
              (Dx[loco_on_lvl_abs[-2], 4] > iso  # MATLAB uses column 5 (1-idx)=col 4 (0-idx)
               or abs(Dx[loco_on_lvl_abs[-2], 4]) < abs(10 * iso))):
            TON[i] = loco_on_lvl_abs[-2]
        elif (len(loco_on_lvl1_abs) > 1 and len(loco_on_lvl1_abs) < 4 and
              len(loco_on_lvl_abs) == 1 and
              abs(loco_on_lvl1_abs[-1] - ton_ref) < abs(loco_on_lvl_abs[-1] - ton_ref) and
              loco_on_lvl_abs[-1] - qrs_off < int(round(0.06 * samplerate))):
            TON[i] = loco_on_lvl1_abs[-1]
        else:
            TON[i] = loco_on_lvl_abs[-1]

        # --- TOFF selection (mirrors MATLAB lines 494–513) ---
        if len(loco_off_lvl_abs) == 0:
            if len(loco_off_lvl1_abs) > 0:
                if (len(loco_off_lvl1_abs) > 1 and
                        (abs(loco_off_lvl1_abs[1] - toff_ref) < abs(loco_off_lvl1_abs[0] - toff_ref)
                         or abs(signal_pre[loco_off_lvl1_abs[0]]) > 0.5 * abs(signal_pre[tp]))):
                    TOFF[i] = loco_off_lvl1_abs[1]
                else:
                    TOFF[i] = loco_off_lvl1_abs[0]
            else:
                TOFF[i] = tp + fallback_ms
        elif len(loco_off_lvl1_abs) == 0:
            TOFF[i] = loco_off_lvl_abs[0]
        else:
            # Complex MATLAB condition: prefer lvl peak when it's close to density estimate
            # and the signal is smooth there; otherwise use lvl1 peak.
            lo0 = loco_off_lvl_abs[0]
            l10 = loco_off_lvl1_abs[0]
            diff_at_lvl = int(round(0.04 * samplerate))
            cond_slope = False
            if lo0 + diff_at_lvl < N and l10 + diff_at_lvl < N:
                slope_lvl = abs(np.sum(np.diff(signal_pre[lo0: lo0 + diff_at_lvl])))
                slope_lvl1 = abs(np.sum(np.diff(signal_pre[l10: l10 + diff_at_lvl])))
                cond_slope = slope_lvl < 3 * slope_lvl1
            if (abs(lo0 - toff_ref) < int(round(0.02 * samplerate)) and cond_slope):
                TOFF[i] = lo0
            elif (abs(tp - l10) < 0.6 * float(np.nanmean(TOFF - TPEAK) if np.any(TOFF > 0) else R_w) or
                  abs(tp - l10) > 1.4 * float(np.nanmean(TOFF - TPEAK) if np.any(TOFF > 0) else R_w)):
                TOFF[i] = lo0
            else:
                TOFF[i] = l10

        TON[i] = int(np.clip(TON[i], 0, N - 1))
        TOFF[i] = int(np.clip(TOFF[i], 0, N - 1))

    # -----------------------------------------------------------------
    # 8. Write back to FPT
    # -----------------------------------------------------------------
    fpt[:, 9] = np.nan_to_num(TON).astype(int)
    fpt[:, 10] = TPEAK
    fpt[:, 11] = np.nan_to_num(TOFF).astype(int)

    # L point (midpoint of QRS offset and T onset)
    if np.all(fpt[:, 9] != 0) and np.all(fpt[:, 7] != 0):
        fpt[:, 8] = np.round(0.5 * fpt[:, 9] + 0.5 * fpt[:, 7]).astype(int)
    elif np.all(fpt[:, 9] != 0) and np.all(fpt[:, 6] != 0):
        fpt[:, 8] = np.round(0.55 * fpt[:, 9] + 0.45 * fpt[:, 6]).astype(int)
    else:
        fpt[:, 8] = np.round(0.6 * fpt[:, 9] + 0.4 * fpt[:, 5]).astype(int)

    print('Done')
    return fpt
