"""
Main annotation pipeline - Python port of Annotate_ECG_Multi.m.

annotate_ecg_multi : full PQRST delineation for single or multi-lead ECG.
"""

import numpy as np

from .qrs_detection import qrs_detection
from .t_detection import t_detection
from .p_detection import p_detection
from .sync import sync_beats, check_r_peaks_multi, reorder_fpt_cell
from .mastermind import mastermind_delineate

try:
    import neurokit2 as nk
    _HAS_NK = True
except ImportError:
    _HAS_NK = False


def _neurokit_rescue(signal, samplerate, fpt_multi, lead_names=None):
    """Use NeuroKit2 as a second opinion to rescue R-peaks ECGdeli missed.

    Runs NK's ecg_peaks on Lead II (or first available lead), finds any NK
    R-peak that has no ECGdeli match within ``tol_ms``, and inserts it into
    the synced FPT — provided it satisfies basic amplitude / RR checks.

    ECGdeli stays primary: we only *add* missed beats, never remove.
    """
    if not _HAS_NK:
        return fpt_multi

    signal = np.asarray(signal, dtype=float)
    if signal.ndim == 1:
        signal = signal[:, np.newaxis]
    N, C = signal.shape
    fs = int(round(samplerate))

    preferred = ['II', 'I', 'AVF', 'V5', 'V4']
    ch_idx = 0
    if lead_names is not None:
        names_upper = [str(n).upper().replace(' ', '') for n in lead_names]
        for pref in preferred:
            if pref in names_upper:
                ch_idx = names_upper.index(pref)
                break

    lead_sig = signal[:, ch_idx].ravel()

    try:
        _, info = nk.ecg_peaks(lead_sig, sampling_rate=fs)
        nk_r = np.sort(np.asarray(info['ECG_R_Peaks'], dtype=int))
    except Exception:
        return fpt_multi

    if len(nk_r) == 0:
        return fpt_multi

    ecg_r = fpt_multi[:, 5].astype(float)
    tol_samples = int(0.10 * samplerate)  # 100 ms

    amp_at_ecg = np.abs(lead_sig[ecg_r.astype(int).clip(0, N - 1)])
    amp_med = float(np.median(amp_at_ecg)) if len(amp_at_ecg) > 0 else 0.0
    amp_floor = 0.25 * amp_med

    rr_ecg = np.diff(ecg_r)
    med_rr = float(np.median(rr_ecg)) if len(rr_ecg) > 0 else samplerate
    min_sep = max(int(0.25 * samplerate), int(0.40 * med_rr))

    rescued = []
    for nk_pos in nk_r:
        dists = np.abs(ecg_r - float(nk_pos))
        if dists.min() <= tol_samples:
            continue
        if abs(lead_sig[min(nk_pos, N - 1)]) < amp_floor:
            continue
        all_r = np.concatenate([ecg_r, [float(r) for r in rescued]])
        if len(all_r) > 0 and np.min(np.abs(all_r - float(nk_pos))) < min_sep:
            continue
        rescued.append(float(nk_pos))

    if not rescued:
        return fpt_multi

    new_rows = np.zeros((len(rescued), 13))
    new_rows[:, 5] = rescued
    merged = np.vstack([fpt_multi, new_rows])
    order = np.argsort(merged[:, 5])
    return merged[order]


def annotate_ecg_multi(signal, samplerate, process_flag='all', fpt_given=None,
                       lead_names=None, use_mastermind=True):
    """Full ECG waveform annotation (PQRST delineation).

    Parameters
    ----------
    signal         : (N,) or (N, C) numpy array — single or multi-lead ECG
    samplerate     : sampling frequency in Hz
    process_flag   : which waves to detect (default 'all'):
                     'all' / 'PQRST', 'QRS', 'PQRS', 'QRST', 'P', 'T', 'PT'
    fpt_given      : optional (n_beats, 13) FPT with pre-computed R peaks
    lead_names     : list of lead name strings (same length as channels)
    use_mastermind : if True (default), use the Beat Mastermind pipeline for
                     T/P delineation instead of the legacy independent detectors

    Returns
    -------
    fpt_multi : (n_beats, 13) global synchronised Fiducial Point Table
    fpt_cell  : list of per-channel FPT arrays (each (n_beats, 13))

    FPT column layout (0-indexed positions):
      0  Pon | 1  Ppeak | 2  Poff
      3  QRSon | 4  Q | 5  R | 6  S | 7  QRSoff
      8  L point | 9  Ton | 10 Tpeak | 11 Toff | 12 class
    """
    signal = np.asarray(signal, dtype=float)
    if signal.ndim == 1:
        signal = signal[:, np.newaxis]
    if signal.shape[0] < signal.shape[1]:
        signal = signal.T  # force (N, C)

    N, C = signal.shape
    samplerate = float(samplerate)

    valid_flags = {'all', 'PQRST', 'QRS', 'PQRS', 'QRST', 'P', 'T', 'PT'}
    if process_flag not in valid_flags:
        raise ValueError(f"process_flag must be one of {valid_flags}")

    do_qrs = process_flag in {'all', 'PQRST', 'QRS', 'PQRS', 'QRST'}
    do_t   = process_flag in {'all', 'PQRST', 'QRST', 'T', 'PT'}
    do_p   = process_flag in {'all', 'PQRST', 'PQRS', 'P', 'PT'}

    fpt_given_flag = fpt_given is not None

    fpt_cell = [None] * C
    empty_count = 0

    # Normalise lead_names to a length-C list (or Nones)
    if lead_names is not None and len(lead_names) == C:
        _lead_names = list(lead_names)
    else:
        _lead_names = [None] * C

    # ------------------------------------------------------------------
    # Step 1: QRS detection (or use provided FPT)
    # Preserve the full QRS-delineated FPTs (Q, S, QRSon, QRSoff filled)
    # for use in T/P detection.  sync_beats only keeps the R column, so
    # we hold onto the originals here and re-align them after syncing.
    # ------------------------------------------------------------------
    for ch in range(C):
        if fpt_given_flag:
            fpt_cell[ch] = check_r_peaks_multi(signal[:, ch], samplerate, fpt_given)
        elif do_qrs:
            fpt_cell[ch] = qrs_detection(signal[:, ch], samplerate,
                                         verbose=(ch == 0),
                                         lead_name=_lead_names[ch])
        else:
            print(f'Warning: no QRS detection requested and no FPT provided for ch {ch}.')
            empty_count += 1

        if fpt_cell[ch] is None or len(fpt_cell[ch]) == 0:
            empty_count += 1

    if empty_count == C:
        print('Warning: No QRS complexes detected in any channel. Returning None.')
        return None, fpt_cell

    # Keep original per-channel QRS FPTs (with Q/S/QRSon/QRSoff filled)
    fpt_cell_qrs_orig = [f.copy() if f is not None else None for f in fpt_cell]

    # ------------------------------------------------------------------
    # Step 2: Synchronise beats across channels → global reference
    # ------------------------------------------------------------------
    if not fpt_given_flag:
        fpt_multi, _ = sync_beats(fpt_cell, samplerate)
        if fpt_multi is None or len(fpt_multi) == 0:
            print('Warning: Synchronisation returned empty FPT.')
            return None, fpt_cell
    else:
        fpt_multi = fpt_given.copy()

    # ------------------------------------------------------------------
    # Step 2b: NeuroKit2 rescue — recover R-peaks ECGdeli wavelet missed
    # ------------------------------------------------------------------
    fpt_multi = _neurokit_rescue(signal, samplerate, fpt_multi,
                                 lead_names=_lead_names)

    # Re-align the original QRS-delineated per-channel FPTs to the global
    # reference so that T/P detection gets correct QRSon/QRSoff values.
    fpt_cell = reorder_fpt_cell(fpt_cell_qrs_orig, fpt_multi, samplerate)

    # ------------------------------------------------------------------
    # Step 3: T-wave and P-wave detection per channel
    # ------------------------------------------------------------------
    for ch in range(C):
        if fpt_cell[ch] is None or len(fpt_cell[ch]) == 0:
            continue

        if use_mastermind and (do_t or do_p):
            try:
                fpt_cell[ch] = mastermind_delineate(
                    signal[:, ch], samplerate, fpt_cell[ch],
                    lead_name=_lead_names[ch])
            except Exception as e:
                print(f'Warning: Mastermind failed on ch {ch}, falling back to legacy: {e}')
                if do_t:
                    try:
                        fpt_cell[ch] = t_detection(signal[:, ch], samplerate, fpt_cell[ch])
                    except Exception as e2:
                        print(f'Warning: T detection fallback failed on ch {ch}: {e2}')
                if do_p:
                    try:
                        fpt_cell[ch] = p_detection(signal[:, ch], samplerate, fpt_cell[ch])
                    except Exception as e2:
                        print(f'Warning: P detection fallback failed on ch {ch}: {e2}')
        else:
            if do_t:
                try:
                    fpt_cell[ch] = t_detection(signal[:, ch], samplerate, fpt_cell[ch])
                except Exception as e:
                    print(f'Warning: T detection failed on ch {ch}: {e}')
            if do_p:
                try:
                    fpt_cell[ch] = p_detection(signal[:, ch], samplerate, fpt_cell[ch])
                except Exception as e:
                    print(f'Warning: P detection failed on ch {ch}: {e}')

    # ------------------------------------------------------------------
    # Step 4: Re-align per-channel FPTs (with full P/T data) to the
    #         global R-peak reference without zeroing wave information.
    # ------------------------------------------------------------------
    fpt_cell = reorder_fpt_cell(fpt_cell, fpt_multi, samplerate)

    return fpt_multi, fpt_cell
