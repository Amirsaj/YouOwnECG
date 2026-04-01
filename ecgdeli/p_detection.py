"""
P-wave detection - Python port of P_Detection.m.

Detects P-wave onset, peak, and offset using a quadratic-spline wavelet SWT
on a signal where QRS and T waves have been replaced by sigmoid transitions.
"""

import warnings
import numpy as np
import pywt
from scipy import signal as sp_signal

from .filtering import _gaussian_hp_kernel, _gaussian_lp_kernel
from .wave_removal import remove_qrst


def _gaussian_filter_signal(sig, samplerate, hp_freq, lp_freq):
    """Gaussian bandpass: highpass then lowpass convolution."""
    # Highpass
    sigma_hp = samplerate / (2 * np.pi * hp_freq)
    n_hp = 2 * int(round(4 * sigma_hp)) + 1
    h_hp = _gaussian_hp_kernel(sigma_hp, n_hp)
    out = np.convolve(sig, h_hp, mode='same')

    # Lowpass
    sigma_lp = samplerate / (2 * np.pi * lp_freq)
    n_lp = int(round(8 * sigma_lp))
    if n_lp < 3:
        n_lp = 3
    h_lp = _gaussian_lp_kernel(sigma_lp, n_lp)
    out = np.convolve(out, h_lp, mode='same')
    return out


def _custom_spline_wavelet():
    """Return PyWavelets Wavelet object for the quadratic spline wavelet
    used in P_Detection.m:
        h = [1/8, 3/8, 3/8, 1/8]   lowpass
        g = [0,  -2,   2,   0]     highpass
    """
    h = np.array([1 / 8, 3 / 8, 3 / 8, 1 / 8])
    g = np.array([0.0, -2.0, 2.0, 0.0])
    return pywt.Wavelet(filter_bank=(h, g, h[::-1], g[::-1]))


def _swt_spline_level(sig_padded, level_total, target_level, wavelet):
    """SWT with custom wavelet; returns detail at *target_level*.

    pywt returns [(cA_n, cD_n), ..., (cA_1, cD_1)] for level=n
    so coeffs[0] = coarsest = level n.
    MATLAB swd(x,:) for a level-(x+1) transform = coeffs[1][1].
    """
    coeffs = pywt.swt(sig_padded, wavelet, level=level_total)
    # MATLAB swd(target_level,:) = Python coeffs[level_total - target_level][1]
    py_idx = level_total - target_level
    py_idx = max(0, min(py_idx, len(coeffs) - 1))
    return np.array(coeffs[py_idx][1])


def p_detection(signal, samplerate, fpt, use_wt_max=True, condition=None):
    """Detect P-wave onset, peak, and offset for each beat.

    Parameters
    ----------
    signal      : 1-D numpy array (N,)
    samplerate  : sampling frequency in Hz
    fpt         : (n_beats, 13) FPT with QRS and T columns already filled
    use_wt_max  : if True, use the wavelet-transform maximum as P peak
                  (vs. ECG signal maximum near the WT peak)
    condition   : optional dict from detect_condition(); when
                  condition['has_p_waves'] is False (e.g. AFIB), P columns
                  are zeroed and detection is skipped.

    Returns
    -------
    fpt : updated FPT with columns 0 (Pon), 1 (Ppeak), 2 (Poff) filled.
    """
    if condition is not None and not condition.get('has_p_waves', True):
        fpt = fpt.copy()
        fpt[:, 0:3] = 0
        return fpt

    print('Detecting P Waves...')

    signal = np.asarray(signal, dtype=float).ravel()
    N = len(signal)
    fpt = fpt.copy()
    n_beats = len(fpt)

    if n_beats < 3:
        print('Too few beats for P detection.')
        return fpt

    # -----------------------------------------------------------------
    # 1. Gaussian bandpass (1–15 Hz) on original signal
    # -----------------------------------------------------------------
    fsig = _gaussian_filter_signal(signal, samplerate, 1.0, 15.0)

    # -----------------------------------------------------------------
    # 2. Replace QRS+T with sigmoid; compute sum SWT (forward + reversed)
    # -----------------------------------------------------------------
    rep_sig, ant = remove_qrst(fsig, samplerate, fpt)

    x = max(1, int(np.floor(np.log2(samplerate / 2 / 7))))

    npo = int(np.ceil(np.log2(N)))
    l_pad = 2 ** npo
    if l_pad == N:
        l_pad = 2 ** (npo + 1)
    l1_p = int(np.floor((l_pad - N) / 2))
    l2_p = l_pad - N - l1_p

    sig_padded = np.concatenate([
        np.full(l2_p, rep_sig[0]),
        rep_sig,
        np.full(l1_p, rep_sig[-1])
    ])

    try:
        wav = _custom_spline_wavelet()
        # Forward
        Dx_full = _swt_spline_level(sig_padded, x + 1, x, wav)
        Dx = Dx_full[l2_p: l2_p + N]
        # Reversed
        sig_rev = sig_padded[::-1]
        Dx2_full = _swt_spline_level(sig_rev, x + 1, x, wav)
        Dx2 = Dx2_full[::-1][l2_p: l2_p + N]
    except Exception as e:
        print(f'Warning: custom wavelet failed ({e}), falling back to db2.')
        try:
            cf = pywt.swt(sig_padded, 'db2', level=x + 1)
            Dx = np.array(cf[1][1])[l2_p: l2_p + N]
            cr = pywt.swt(sig_padded[::-1], 'db2', level=x + 1)
            Dx2 = np.array(cr[1][1])[::-1][l2_p: l2_p + N]
        except Exception as e2:
            print(f'Warning: fallback wavelet failed ({e2}). Skipping P detection.')
            return fpt

    sum_sig = Dx + Dx2

    d_sum_sig = np.diff(sum_sig)
    d_fsig = np.diff(fsig)

    # -----------------------------------------------------------------
    # 3. Set search intervals per beat
    # -----------------------------------------------------------------
    r_peaks = fpt[:, 5].astype(int)
    rr = np.diff(r_peaks)

    on_arr = r_peaks[:-1] + np.round(rr * ant).astype(int) - int(round(35e-3 * samplerate))
    off_arr = fpt[1:, 4].astype(int) - int(round(35e-3 * samplerate))
    off_arr = np.maximum(off_arr, 0)

    # Ensure on < off
    for k in range(len(on_arr)):
        while on_arr[k] >= off_arr[k]:
            off_arr[k] += int(round(10e-3 * samplerate))

    # -----------------------------------------------------------------
    # 4. Find P peak for each beat using WT extrema
    # -----------------------------------------------------------------
    n_inter = len(off_arr)
    p_peaks = np.zeros(n_inter, dtype=int)
    p_ons = np.zeros(n_inter, dtype=int)
    p_offs = np.zeros(n_inter, dtype=int)

    p_width = int(round(0.1 * samplerate / 4))

    for i in range(n_inter):
        # WT extrema in [r_peaks[i], r_peaks[i+1]]
        seg_d = d_sum_sig[r_peaks[i]: r_peaks[i + 1]]
        idx_offset = r_peaks[i]

        t = np.arange(len(seg_d) - 1)
        pos_max = np.where((seg_d[t] >= 0) & (seg_d[t + 1] < 0))[0]
        neg_max = np.where((seg_d[t] < 0) & (seg_d[t + 1] >= 0))[0]

        all_ext = np.concatenate([pos_max, neg_max])
        if len(all_ext) == 0:
            # No extremum – place P at midpoint of search interval
            p_peaks[i] = int(round((off_arr[i] - on_arr[i]) / 2)) + on_arr[i]
            p_ons[i] = on_arr[i]
            p_offs[i] = off_arr[i]
            continue

        ext_type = np.concatenate([np.ones(len(pos_max)), -np.ones(len(neg_max))])
        ext_global = all_ext + idx_offset
        ext_amp = np.abs(sum_sig[ext_global])

        # Sort descending by absolute amplitude, prefer later extrema on ties
        order = np.argsort(-ext_amp)
        all_ext = all_ext[order]
        ext_type = ext_type[order]
        ext_global = ext_global[order]

        # Attempt to find the P peak
        found = False
        for k_try in range(len(all_ext)):
            wt_pos = int(ext_global[k_try])
            wt_type = int(ext_type[k_try])

            if use_wt_max:
                p_pk = wt_pos
            else:
                lo_f = max(wt_pos - p_width, 0)
                hi_f = min(wt_pos + p_width + 1, N)
                if wt_type == 1:
                    p_pk = lo_f + int(np.argmax(rep_sig[lo_f:hi_f]))
                else:
                    p_pk = lo_f + int(np.argmin(rep_sig[lo_f:hi_f]))

            p_pk = int(np.clip(p_pk, 0, N - 1))

            # Check that the peak has a zero-crossing in its derivative
            if p_pk > 0 and p_pk < N - 1:
                valid = ((d_fsig[p_pk - 1] < 0 and d_fsig[p_pk] >= 0) or
                         (d_fsig[p_pk - 1] > 0 and d_fsig[p_pk] <= 0))
                if valid and p_pk > on_arr[i]:
                    p_peaks[i] = p_pk
                    found = True
                    break

        if not found:
            p_peaks[i] = int(round((off_arr[i] - on_arr[i]) / 2)) + on_arr[i]

        p_ons[i] = on_arr[i]
        p_offs[i] = off_arr[i]

    # -----------------------------------------------------------------
    # 5. Template-based delineation (every 50 beats)
    # -----------------------------------------------------------------
    n_waves_block = 50
    n_blocks = int(np.ceil(n_inter / n_waves_block))
    seg_int = int(round(0.1 * samplerate / 2 * 3))  # template half-width

    fpt_p = np.zeros((n_inter, 3), dtype=int)
    fpt_p[:, 1] = p_peaks

    for blk in range(n_blocks):
        lo_blk = blk * n_waves_block
        hi_blk = min((blk + 1) * n_waves_block, n_inter)
        p_pos_blk = p_peaks[lo_blk:hi_blk]
        n_blk = len(p_pos_blk)

        if n_blk < 2:
            for k in range(n_blk):
                idx_b = lo_blk + k
                fpt_p[idx_b, 0] = max(0, p_peaks[idx_b] - int(round(50e-3 * samplerate)))
                fpt_p[idx_b, 2] = min(N - 1, p_peaks[idx_b] + int(round(50e-3 * samplerate)))
            continue

        # Build segment matrix
        segs = np.zeros((n_blk, 2 * seg_int + 1))
        for k in range(n_blk):
            pk = p_pos_blk[k]
            lo_s = pk - seg_int
            hi_s = pk + seg_int + 1
            if lo_s < 0:
                d = -lo_s
                segs[k, d:] = sum_sig[0: min(hi_s, N)]
                if d > 0:
                    segs[k, :d] = sum_sig[0]
            elif hi_s > N:
                avail = N - lo_s
                segs[k, :avail] = sum_sig[lo_s:N]
                segs[k, avail:] = sum_sig[-1]
            else:
                segs[k, :] = sum_sig[lo_s:hi_s]

        # PCA + Mahalanobis outlier removal
        abs_segs = np.abs(segs)
        try:
            from sklearn.decomposition import PCA as _PCA
            pca_model = _PCA(n_components=1)
            pca_score = pca_model.fit_transform(abs_segs)[:, 0]
            std_s = np.std(pca_score, ddof=1) + 1e-12
            tsq = ((pca_score - np.mean(pca_score)) / std_s) ** 2
            acc = tsq <= (np.mean(tsq) + np.std(tsq, ddof=1))
        except Exception:
            acc = np.ones(n_blk, dtype=bool)

        segs_filt = abs_segs[acc]
        mean_seg = segs_filt.mean(axis=0) if len(segs_filt) > 0 else abs_segs.mean(axis=0)

        # Template distribution -> pon/poff offsets from peak
        cumsum_temp = np.cumsum(np.abs(mean_seg)) / (np.sum(np.abs(mean_seg)) + 1e-12)
        pon_tpl = int(np.searchsorted(cumsum_temp, 0.05))
        poff_tpl = int(np.searchsorted(cumsum_temp, 0.85))

        pon_tpl = min(pon_tpl, seg_int - 1)
        poff_tpl = max(poff_tpl, seg_int + 1)

        area_plus = np.cumsum(np.abs(mean_seg[seg_int + 1: poff_tpl + 1]))
        area_plus_full = np.cumsum(np.abs(mean_seg[seg_int + 1:]))
        area_minus = np.cumsum(np.abs(mean_seg[pon_tpl: seg_int]))
        area_minus_full = np.cumsum(np.abs(mean_seg[:seg_int]))

        thresh_plus = (area_plus[-1] / (area_plus_full[-1] + 1e-12)
                       if len(area_plus) > 0 and len(area_plus_full) > 0 else 0.5)
        thresh_minus = (area_minus[-1] / (area_minus_full[-1] + 1e-12)
                        if len(area_minus) > 0 and len(area_minus_full) > 0 else 0.5)

        for k in range(n_blk):
            idx_b = lo_blk + k
            pk = p_pos_blk[k]

            seg_abs = np.abs(segs[k])

            # Pon from "minus area"
            area_w_m = np.cumsum(np.abs(seg_abs[:seg_int]))
            if area_w_m[-1] > 0:
                pon_est = int(np.searchsorted(
                    area_w_m,
                    area_w_m[-1] - thresh_minus * area_w_m[-1]
                ))
                d_temp_m = np.diff(np.abs(seg_abs[:seg_int]))
                infl_m = np.where(
                    (d_temp_m[:-1] >= 0) & (d_temp_m[1:] < 0)
                )[0] if len(d_temp_m) > 1 else np.array([])
                if len(infl_m) > 0:
                    best_m = infl_m[np.argmin(np.abs(infl_m - pon_est))]
                    pon_global = pk - seg_int + best_m
                else:
                    pon_global = pk - seg_int + pon_est
            else:
                pon_global = pk - int(round(50e-3 * samplerate))

            # Poff from "plus area"
            area_w_p = np.cumsum(np.abs(seg_abs[seg_int + 1:]))
            if len(area_w_p) > 0 and area_w_p[-1] > 0:
                poff_est = int(np.searchsorted(
                    area_w_p,
                    thresh_plus * area_w_p[-1]
                ))
                d_temp_p = np.diff(np.abs(seg_abs[seg_int + 1:]))
                infl_p = np.where(
                    (d_temp_p[:-1] >= 0) & (d_temp_p[1:] < 0)
                )[0] if len(d_temp_p) > 1 else np.array([])
                if len(infl_p) > 0:
                    best_p = infl_p[np.argmin(np.abs(infl_p - poff_est))]
                    poff_global = pk + best_p
                else:
                    poff_global = pk + poff_est
            else:
                poff_global = pk + int(round(50e-3 * samplerate))

            # Clamp
            pon_global = max(0, pon_global)
            if poff_global >= N:
                pon_global = N - 2
            # Poff must be before Q wave
            q_pos = int(fpt[idx_b + 1, 4]) if idx_b + 1 < n_beats else N - 1
            if poff_global > q_pos:
                poff_global = q_pos - int(round(30e-3 * samplerate))

            fpt_p[idx_b, 0] = int(np.clip(pon_global, 0, N - 1))
            fpt_p[idx_b, 2] = int(np.clip(poff_global, 0, N - 1))

    # -----------------------------------------------------------------
    # 6. Write back to FPT (beats 1..n-2 in 0-indexed = indices 1..n-2)
    # -----------------------------------------------------------------
    fpt[1:-1, 0] = fpt_p[:-1, 0]
    fpt[1:-1, 1] = fpt_p[:-1, 1]
    fpt[1:-1, 2] = fpt_p[:-1, 2]

    # Propagate first and last beats from median RR offsets
    med_pr = int(round(np.median(fpt[1:-1, 6] - fpt[1:-1, 1])))
    med_pron = int(round(np.median(fpt[1:-1, 6] - fpt[1:-1, 0])))
    med_proff = int(round(np.median(fpt[1:-1, 6] - fpt[1:-1, 2])))

    s0 = int(fpt[0, 6])
    fpt[0, 0] = max(0, s0 - med_pron)
    fpt[0, 1] = max(0, s0 - med_pr)
    fpt[0, 2] = max(0, s0 - med_proff)

    sL = int(fpt[-1, 6])
    fpt[-1, 0] = max(0, sL - med_pron)
    fpt[-1, 1] = max(0, sL - med_pr)
    fpt[-1, 2] = max(0, sL - med_proff)

    print('Done')
    return fpt
