"""
QRS Detection - Python port of QRS_Detection.m.

Wavelet-based R-peak detector (Haar SWT) with adaptive thresholding
followed by Q/R/S localisation using zero-crossings of the derivative.
"""

import numpy as np
import pywt
from scipy import signal as sp_signal

from .filtering import ecg_high_low_filter
from .sync import sync_r_peaks, check_small_rr


def _pad_to_pow2(sig):
    """Pad signal to next power of 2 using edge (sp0) padding.

    Returns (padded, l2, l1) where l2 samples are added on the left,
    l1 samples on the right.
    """
    N = len(sig)
    npo = int(np.ceil(np.log2(N)))
    l_target = 2 ** npo
    if l_target == N:
        l_target = 2 ** (npo + 1)

    l1 = int(np.floor((l_target - N) / 2))  # right pad
    l2 = l_target - N - l1                   # left pad

    left = np.full(l2, sig[0])
    right = np.full(l1, sig[-1])
    padded = np.concatenate([left, sig, right])
    return padded, l2, l1


def _haar_swt_detail(sig, level):
    """Return the Haar SWT detail coefficients at the given level.

    pywt.swt returns [(cA_n, cD_n), ..., (cA_1, cD_1)] for level=n,
    so index 0 is the coarsest (level n).  We always request exactly
    `level` levels and take index 0.
    """
    coeffs = pywt.swt(sig, 'haar', level=level)
    # coeffs[0] = (cA_level, cD_level)  ← coarsest = what we want
    return np.array(coeffs[0][1])


def _find_qrs_regions(Dx, rms_Dx_base, threshold_vec, samplerate):
    """Adaptive threshold search for QRS candidate regions.

    Returns (Bound_A, Bound_B) as 0-indexed arrays.
    """
    NR_vec = np.zeros(len(threshold_vec))
    Bound_A = np.array([], dtype=int)
    Bound_B = np.array([], dtype=int)

    for H, th in enumerate(threshold_vec):
        if H == len(threshold_vec) - 1 and np.any(NR_vec[:H] > 0):
            mt = np.argmin(np.diff(NR_vec[:H]))
            rms_Dx = threshold_vec[mt] * rms_Dx_base
        else:
            rms_Dx = th * rms_Dx_base

        can = (Dx > rms_Dx).astype(float)
        can[0] = 0
        can[-1] = 0

        i = np.arange(len(can) - 1)
        bA = np.where((can[i] == 0) & (can[i + 1] > 0))[0] + 1
        bB = np.where((can[i] > 0) & (can[i + 1] == 0))[0]

        if len(bA) == 0 or len(bB) == 0:
            NR_vec[H] = 0
            continue

        # Merge close regions (< 100 ms apart)
        while len(bA) > 1 and len(bB) > 0:
            gaps = (bA[1:] - bB[:-1]) / samplerate
            if gaps.min() >= 0.1:
                break
            idx = int(np.argmin(gaps))
            bB = np.delete(bB, idx)
            bA = np.delete(bA, idx + 1)

        # Discard implausibly short (< 5 ms) or long (> 250 ms) regions
        if len(bA) == 0 or len(bB) == 0:
            continue
        n = min(len(bA), len(bB))
        bA, bB = bA[:n], bB[:n]
        widths = (bB - bA) / samplerate
        keep = (widths >= 5e-3) & (widths <= 0.25)
        bA, bB = bA[keep], bB[keep]

        NR_vec[H] = len(bA)
        if H > 0:
            dNR = NR_vec[H] - NR_vec[H - 1]
            if dNR <= 0 or H == len(threshold_vec) - 1:
                if len(bA) > 1 and len(bB) > 1:
                    Bound_A = bA
                    Bound_B = bB
                    break

    if len(Bound_A) == 0:
        Bound_A = bA if 'bA' in dir() and len(bA) > 0 else np.array([], dtype=int)
        Bound_B = bB if 'bB' in dir() and len(bB) > 0 else np.array([], dtype=int)

    return Bound_A, Bound_B


def _qrs_energy_envelope(sig, samplerate):
    """Smoothed squared-derivative energy — QRS >> T for candidate scoring."""
    x = np.asarray(sig, dtype=float)
    d = np.diff(x, prepend=x[0])
    w = max(3, int(0.022 * samplerate))
    e = d * d
    box = np.ones(w, dtype=float) / float(w)
    return np.convolve(e, box, mode='same')


def _append_terminal_r_peaks(work_sig, samplerate, r_peaks, N):
    """Recover QRS complexes missed by wavelet detection in the strip tail.

    Handles (a) **long sinus pauses** with several undetected beats in the middle
    of the tail, and (b) the **last** beat near EOF.  Uses sequential
    ~1×median-RR windows with **derivative-energy** argmax (not raw amplitude) so
    T-waves are less often mistaken for QRS than in the previous single-window
    |V| search.
    """
    r_peaks = np.asarray(r_peaks, dtype=int)
    if len(r_peaks) < 2 or N < int(0.5 * samplerate):
        return r_peaks
    rr = np.diff(r_peaks).astype(float)
    med_rr = float(np.median(rr))
    if med_rr <= 0:
        return r_peaks
    min_sep = int(max(0.28 * samplerate, 0.45 * med_rr))
    margin_end = int(max(0.08 * samplerate, 40))
    amps = np.abs(work_sig[r_peaks])
    amp_med = float(np.median(amps))
    amp_floor = max(0.16 * amp_med, float(np.quantile(np.abs(work_sig), 0.88) * 0.12))

    E = _qrs_energy_envelope(work_sig, samplerate)
    e_at_r = E[r_peaks]
    e_med = float(np.median(e_at_r))
    e_thresh = max(0.20 * e_med, float(np.quantile(E, 0.75) * 0.35))

    rp = sorted(int(x) for x in r_peaks.tolist())
    last = rp[-1]
    if (N - margin_end) - last < int(0.48 * med_rr):
        return np.array(r_peaks, dtype=int)

    win_w = int(min(max(0.92 * med_rr, 0.35 * samplerate), 1.15 * med_rr))
    max_add = 8

    for _ in range(max_add):
        if (N - margin_end) - last < int(0.48 * med_rr):
            break

        lo = last + min_sep
        hi = min(lo + win_w, N - margin_end)

        # Last beat hugging EOF: align window to recording end
        if hi <= lo or (N - margin_end - lo) < int(0.55 * med_rr):
            lo = max(last + min_sep, N - int(1.18 * med_rr) - margin_end)
            hi = N - margin_end

        if lo >= hi:
            break

        seg = E[lo:hi]
        if len(seg) < max(5, int(0.04 * samplerate)):
            break

        # Top few local maxima of E — pick best by E*|V| so T-waves lose to QRS
        flat = seg.ravel()
        cand_rel = [int(np.argmax(flat))]
        for _ in range(2):
            tmp = flat.copy()
            for j in cand_rel:
                a0 = max(0, j - int(0.05 * samplerate))
                b0 = min(len(tmp), j + int(0.05 * samplerate))
                tmp[a0:b0] = 0.0
            if tmp.max() <= 0:
                break
            cand_rel.append(int(np.argmax(tmp)))

        best_k, best_sc = -1, -1.0
        wref = max(1, int(0.022 * samplerate))
        for rel in cand_rel:
            kk = lo + rel
            a = max(0, kk - wref)
            b = min(N, kk + wref + 1)
            kk = a + int(np.argmax(E[a:b]))
            sc = float(E[kk]) * max(abs(work_sig[kk]), amp_floor * 0.5)
            if sc > best_sc:
                best_sc, best_k = sc, kk
        k = best_k

        if E[k] < e_thresh and abs(work_sig[k]) < amp_floor:
            break
        # QRS should exceed typical T in the same lead (loose check)
        if abs(work_sig[k]) < 0.38 * amp_med:
            break
        if min(abs(k - x) for x in rp) < min_sep // 2:
            break

        rp.append(k)
        last = k
        rp.sort()

    return np.array(sorted(set(rp)), dtype=int)


# Lead polarity map: True = R wave must be positive (first positive deflection).
# Medical basis: R is the FIRST positive deflection regardless of amplitude.
# In LAD/LAFB lead II shows rS (small r, deep S); the algorithm must NOT call S the "R".
EXPECTED_R_POSITIVE = {
    'I': True, 'II': True, 'III': None,
    'AVR': False, 'AVL': None, 'AVF': True,
    'V1': False, 'V2': None, 'V3': None,
    'V4': True,  'V5': True,  'V6': True,
}


def qrs_detection(signal, samplerate, mode='auto', verbose=True, lead_name=None):
    """Detect QRS complexes in a single-lead ECG.

    Parameters
    ----------
    signal     : 1-D numpy array (N,)
    samplerate : sampling frequency in Hz
    mode       : 'auto'      – use dominant-type template (default)
                 'peaksQRS'  – simply take max/min in QRS window
    verbose    : print progress messages (default True)
    lead_name  : optional string (e.g. 'II', 'AVR') — when supplied, the
                 EXPECTED_R_POSITIVE map enforces the medical definition
                 that R is the FIRST POSITIVE deflection.  For example in
                 LAD/LAFB, lead II shows rS (small r, deep S) but the
                 amplitude heuristic mistakenly picks the deep S as R.
                 Supplying lead_name='II' overrides R_type to +1.

    Returns
    -------
    fpt : (n_beats, 13) Fiducial Point Table with columns:
          0=Pon, 1=Ppeak, 2=Poff, 3=QRSon, 4=Q, 5=R, 6=S, 7=QRSoff,
          8-12 zero.
          All positions are 0-indexed sample indices.
          Returns None if no QRS complexes found.
    """
    flag_peaks_qrs = (mode == 'peaksQRS')

    if verbose:
        print('Detecting R Peaks...')

    signal = np.asarray(signal, dtype=float).ravel()
    N = len(signal)

    if np.all(np.abs(signal) < np.finfo(float).eps):
        print('Warning: signal values too small. Returning None.')
        return None

    # -----------------------------------------------------------------------
    # 1. Bandpass filter: 0.5 – 30 Hz
    # -----------------------------------------------------------------------
    sig_filt = ecg_high_low_filter(signal, samplerate, 0.5, 30, 'B')

    # -----------------------------------------------------------------------
    # 2. Downsampling to 400 Hz (if needed)
    # Only actually decimate when r_ds >= 2; for r_ds=1 (e.g. fs=500 Hz)
    # decimate would just apply an unnecessary anti-alias filter.
    # -----------------------------------------------------------------------
    f_ds = 400
    r_ds = int(np.floor(samplerate / f_ds))
    flag_ds = samplerate > f_ds and r_ds >= 2
    if flag_ds:
        sig_ds = sp_signal.decimate(sig_filt, r_ds, zero_phase=True)
        fs_ds = samplerate / r_ds
    else:
        sig_ds = sig_filt.copy()
        fs_ds = samplerate
        r_ds = 1

    # -----------------------------------------------------------------------
    # 3. Haar SWT at level x
    # -----------------------------------------------------------------------
    x = max(1, int(np.ceil(np.log2(fs_ds / 2 / 30))))

    ecg_pad, l2, l1 = _pad_to_pow2(sig_ds)

    Dx = _haar_swt_detail(ecg_pad, x)[l2: l2 + len(sig_ds)]

    # Mirrored transform for symmetry
    ecg_pad_rev, l2r, l1r = _pad_to_pow2(sig_ds[::-1])
    Dx2 = _haar_swt_detail(ecg_pad_rev, x)[l2r: l2r + len(sig_ds)][::-1]

    Dx = np.abs(Dx + Dx2)
    std_Dx = np.std(Dx)
    if std_Dx > 0:
        Dx /= std_Dx
    saturation = np.quantile(Dx, 0.99)
    Dx = np.minimum(Dx, saturation)

    # -----------------------------------------------------------------------
    # 4. Adaptive threshold, 3 iterations (nrep=3)
    # -----------------------------------------------------------------------
    Tl = 4.0
    nrep = 3
    r_cell = []

    for _j in range(nrep):
        n1 = int(np.floor(fs_ds * Tl))
        n_segs = int(np.floor(len(sig_ds) / n1)) - 1
        rms_base = np.zeros(len(sig_ds))

        for seg_i in range(n_segs + 1):
            lo = max(seg_i * n1, 0)
            hi = min((seg_i + 1) * n1, len(sig_ds))
            margin = int(round(0.1 * fs_ds))
            lo_q = max(lo, margin) if seg_i == 0 else lo
            hi_q = min(hi, len(sig_ds) - margin) if seg_i == n_segs else hi
            rms_base[lo:hi] = np.quantile(Dx[lo_q:hi_q], 0.95)

        th_begin = 1.0
        th_end = np.quantile(Dx, 0.95) / (saturation + 1e-12)
        threshold_vec = np.linspace(th_begin, th_end, 20)

        bA, bB = _find_qrs_regions(Dx, rms_base, threshold_vec, fs_ds)

        if len(bA) > 1 and len(bB) > 1:
            n_bA = min(len(bA), len(bB))
            qrs_pos = 0.5 * (bA[:n_bA] + bB[:n_bA])
            r_arr = np.round(qrs_pos).astype(int)
            r_cell.append(r_arr)
            # Update Tl for next iteration
            Tl = np.quantile(np.diff(bA[:n_bA]) / fs_ds, 0.98) * 4
        else:
            if len(r_cell) == 0:
                if verbose:
                    print('Warning: No QRS complexes found. Returning None.')
                return None

    if len(r_cell) == 0:
        if verbose:
            print('Warning: No QRS complexes found. Returning None.')
        return None

    # -----------------------------------------------------------------------
    # 5. Sync across nrep detection results
    # -----------------------------------------------------------------------
    fpt_list = []
    for r_arr in r_cell:
        tmp = np.zeros((len(r_arr), 13))
        tmp[:, 5] = r_arr
        fpt_list.append(tmp)

    fpt_synced, _ = sync_r_peaks(fpt_list, fs_ds)
    if fpt_synced is None or len(fpt_synced) == 0:
        if verbose:
            print('Warning: Sync failed. Returning None.')
        return None

    r_synced = fpt_synced[:, 5].astype(int)

    # -----------------------------------------------------------------------
    # 6. Undo downsampling (scale back positions)
    # -----------------------------------------------------------------------
    if flag_ds:
        r_synced = (r_synced * r_ds).astype(int)
    # Work with the full-rate filtered signal from here
    work_sig = sig_filt
    fs_work = samplerate

    # -----------------------------------------------------------------------
    # 7. Build FPT – find Q, R, S peaks
    # -----------------------------------------------------------------------
    WB = int(round(0.05 * fs_work))  # ±50 ms search window

    # Boundary handling (was: drop if r + WB >= N — that removed the terminal beat
    # whenever the last QRS sat in the final ~50 ms of the strip).
    # Keep any peak with room for a QRS window on the left; allow a *partial*
    # window on the right up to N-1 (downstream code already uses min(..., N)).
    mask = (r_synced - WB >= 0) & (r_synced < N)
    r_synced = r_synced[mask]

    # Recover terminal QRS missed by wavelet regions (common on 10 s clips)
    r_synced = _append_terminal_r_peaks(work_sig, fs_work, r_synced, N)

    if len(r_synced) < 3:
        if verbose:
            print('Warning: Too few QRS complexes detected. Returning None.')
        return None

    fpt = np.zeros((len(r_synced), 13), dtype=int)

    if flag_peaks_qrs:
        # Simple max/min mode
        for i, rp in enumerate(r_synced):
            lo = max(rp - WB, 0)
            hi = min(rp + WB + 1, N)
            seg = work_sig[lo:hi]
            r_rel = int(np.argmax(seg))
            fpt[i, 5] = lo + r_rel

            s_seg = work_sig[fpt[i, 5]: hi]
            fpt[i, 6] = fpt[i, 5] + int(np.argmin(s_seg))

            q_seg = work_sig[lo: fpt[i, 5] + 1]
            fpt[i, 4] = lo + int(np.argmin(q_seg))

        donoff = int(round(25e-3 * fs_work))
        fpt[:, 3] = np.maximum(0, fpt[:, 4] - donoff)
        fpt[:, 7] = np.minimum(N - 1, fpt[:, 6] + donoff)

    else:
        # Zero-crossing of derivative mode
        dsig = np.diff(work_sig)
        i_arr = np.arange(len(dsig) - 1)
        I_ext = np.where(
            ((dsig[i_arr] >= 0) & (dsig[i_arr + 1] < 0)) |
            ((dsig[i_arr] < 0) & (dsig[i_arr + 1] >= 0))
        )[0] + 1  # 0-indexed positions of extrema in work_sig

        # Build QRS template to determine R-wave polarity
        rr = np.diff(r_synced)
        if len(rr) >= 3:
            X = np.column_stack([rr[:-1], rr[1:]])
            mean_X = X.mean(axis=0)
            rot = (1 / np.sqrt(2)) * np.array([[1, -1], [1, 1]])
            score = (X - mean_X) @ rot
            d1 = np.abs(score[:, 0])
            thl1 = 2.5 * np.std(d1, ddof=1)
            idx_normal = np.where((score[:, 0] >= -thl1) & (score[:, 1] <= 0))[0] + 1
            idx_normal = idx_normal[1:-1] if len(idx_normal) > 2 else idx_normal
        else:
            idx_normal = np.arange(len(r_synced))

        if len(idx_normal) == 0:
            idx_normal = np.arange(len(r_synced))

        # Build template
        QRS_mats = []
        mp_vals = []
        for k in idx_normal:
            if k >= len(r_synced):
                continue
            lo = max(r_synced[k] - WB, 0)
            hi = min(r_synced[k] + WB + 1, N)
            if hi - lo == 2 * WB + 1:
                seg = work_sig[lo:hi]
                QRS_mats.append(seg)
                mp_vals.append([seg.max(), seg.min()])

        if len(QRS_mats) == 0:
            Template = np.zeros(2 * WB + 1)
            R_type = 1
        else:
            QRS_matrix = np.column_stack(QRS_mats).T  # (n_beats, 2*WB+1)
            MP = np.array(mp_vals)
            th11, th12 = np.quantile(MP[:, 0], [0.25, 0.75])
            th21, th22 = np.quantile(MP[:, 1], [0.25, 0.75])
            sel = (MP[:, 0] >= th11) & (MP[:, 0] <= th12) & (MP[:, 1] >= th21) & (MP[:, 1] <= th22)
            sel_mat = QRS_matrix[sel] if sel.any() else QRS_matrix
            Template = sel_mat.mean(axis=0)
            R_type = int(np.sign(Template.max() + Template.min()))
            if R_type == 0:
                R_type = 1

        # -----------------------------------------------------------------------
        # Medical override: enforce first-positive-deflection rule.
        # In LAD/LAFB, lead II shows an rS pattern (small r, deep S).
        # The amplitude-based heuristic above gives R_type=-1 (S dominant),
        # but medically R is always the FIRST positive deflection.
        # If the lead is known to require a positive R, override R_type.
        # -----------------------------------------------------------------------
        lead_key = lead_name.upper().replace(' ', '') if lead_name else None
        expected_positive = EXPECTED_R_POSITIVE.get(lead_key, None) if lead_key else None
        if expected_positive is True and R_type < 0:
            R_type = 1   # force first-positive-deflection search
        elif expected_positive is False and R_type > 0:
            R_type = -1  # e.g. aVR should always be negative dominant

        biph_crit = 2 / 5
        w_crit = 9 / 10

        # Clamp QRS search interval to valid sample range (critical for last beat)
        lo_r_arr = np.maximum(r_synced - WB, 0)
        hi_r_arr = np.minimum(r_synced + WB, N - 1)

        for i in range(len(r_synced)):
            lo_r = int(lo_r_arr[i])
            hi_r = int(hi_r_arr[i])
            tmp_zc = I_ext[(I_ext >= lo_r - WB) & (I_ext <= hi_r + WB)]

            if len(tmp_zc) == 0:
                fpt[i, 5] = int(round((lo_r + hi_r) / 2))
                fpt[i, 4] = lo_r
                fpt[i, 6] = hi_r
            elif len(tmp_zc) == 1:
                fpt[i, 5] = tmp_zc[0]
                fpt[i, 4] = lo_r
                fpt[i, 6] = hi_r
            else:
                amps = work_sig[tmp_zc]
                order = np.argsort(amps)

                ratio_biph = min(abs(amps[order[0]] / (amps[order[-1]] + 1e-12)),
                                 abs(amps[order[-1]] / (amps[order[0]] + 1e-12)))

                if ratio_biph > biph_crit:  # biphasic
                    if R_type >= 0:
                        if len(order) >= 2 and abs(amps[order[-2]] / (amps[order[-1]] + 1e-12)) < w_crit:
                            r_idx = order[-1]
                        else:
                            r_idx = min(order[-1], order[-2])
                    else:
                        if len(order) >= 2 and abs(amps[order[1]] / (amps[order[0]] + 1e-12)) < w_crit:
                            r_idx = order[0]
                        else:
                            r_idx = min(order[0], order[1])
                elif abs(amps[order[-1]]) > abs(amps[order[0]]):  # positive dominant
                    if len(order) >= 2 and abs(amps[order[-2]] / (amps[order[-1]] + 1e-12)) < w_crit:
                        r_idx = order[-1]
                    else:
                        r_idx = min(order[-1], order[-2]) if len(order) >= 2 else order[-1]
                else:
                    # Negative dominant (e.g. rS pattern: tiny r, deep S).
                    # If lead polarity requires positive R (R_type > 0), always
                    # pick the positive maximum even when the negative amplitude
                    # is larger.  This implements the medical first-positive-
                    # deflection rule for ALL QRS morphologies, not just biphasic.
                    if R_type > 0:
                        if len(order) >= 2 and abs(amps[order[-2]] / (amps[order[-1]] + 1e-12)) < w_crit:
                            r_idx = order[-1]
                        else:
                            r_idx = min(order[-1], order[-2]) if len(order) >= 2 else order[-1]
                    else:
                        if len(order) >= 2 and abs(amps[order[1]] / (amps[order[0]] + 1e-12)) < w_crit:
                            r_idx = order[0]
                        else:
                            r_idx = min(order[0], order[1]) if len(order) >= 2 else order[0]

                fpt[i, 5] = tmp_zc[r_idx]

                q_idx = r_idx - 1
                s_idx = r_idx + 1
                fpt[i, 4] = tmp_zc[q_idx] if q_idx >= 0 else lo_r
                fpt[i, 6] = tmp_zc[s_idx] if s_idx < len(tmp_zc) else hi_r

        donoff = int(round(25e-3 * fs_work))
        fpt[:, 3] = np.maximum(0, fpt[:, 4] - donoff)
        fpt[:, 7] = np.minimum(N - 1, fpt[:, 6] + donoff)

        # Clamp first/last
        fpt[0, 3] = max(0, fpt[0, 3])
        fpt[-1, 7] = min(N - 1, fpt[-1, 7])
        fpt[0, 4] = max(1, fpt[0, 4])
        fpt[-1, 6] = min(N - 2, fpt[-1, 6])

    # -----------------------------------------------------------------------
    # 8. Remove unphysiological beats (RR < 250 ms)
    # -----------------------------------------------------------------------
    fpt, _ = check_small_rr(fpt, fs_work)

    if verbose:
        print(f'Done – {len(fpt)} beats detected.')

    return fpt
