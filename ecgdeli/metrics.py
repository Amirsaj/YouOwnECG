"""
Clinical ECG interval computation and fiducial marker validation.

compute_intervals  : PR, QRS duration, QT, QTc, RR per beat from an FPT.
validate_markers   : sanity checks for out-of-range intervals and T-wave
                     concordance rule violations.
summarise_patient  : aggregate per-lead metrics into a single patient summary dict.
"""

import numpy as np

# ---------------------------------------------------------------------------
# Leads that are EXPECTED to show a negative/inverted T wave relative to R
# (normal anatomy — these leads are exempt from the T-concordance check).
#
# Medical basis:
#   V1, AVR : T inversion is ALWAYS normal (negative R expected too)
#   III, AVL: T can be negative in normal sinus rhythm when the QRS axis
#             creates a negative QRS in those leads; T follows QRS polarity
#             so T inversion in III/AVL with negative QRS is concordant.
# ---------------------------------------------------------------------------
T_INVERSION_OK_LEADS = {'V1', 'AVR', 'III', 'AVL'}

# Leads where T inversion is an EXPECTED secondary finding in BBB
# LBBB: discordant T in I, AVL, V5, V6 (lateral) and V1-V3 (septal)
# RBBB: discordant T in V1-V3 and sometimes III, AVF
T_SECONDARY_CHANGE_LEADS_BBB = {
    'V1', 'V2', 'V3', 'V4', 'V5', 'V6',
    'I', 'II', 'III', 'AVR', 'AVL', 'AVF',
}

# ---------------------------------------------------------------------------
# Normal interval ranges (ms)
# ---------------------------------------------------------------------------
PR_MIN_MS   = 80    # below = pre-excitation (WPW) territory
PR_NORM_MIN = 120
PR_NORM_MAX = 200
PR_MAX_MS   = 300   # above = high-degree AV block

QRS_MIN_MS  = 40
QRS_NORM_MAX = 120  # above = bundle branch block / intraventricular delay
QRS_MAX_MS  = 200

QT_MIN_MS   = 200
QT_MAX_MS   = 600

QTC_WARN_MEN   = 450   # ms, Fridericia
QTC_WARN_WOMEN = 460
QTC_CRITICAL   = 500   # high arrhythmia risk regardless of sex

RR_MIN_MS   = 300   # > 200 bpm
RR_MAX_MS   = 2000  # < 30 bpm

TPEAK_TOFF_MIN_MS = 50   # too short = likely detection error
TPEAK_TOFF_MAX_MS = 300

PR_FROM_P_ONSET = True  # use Pon (col 0) when available; else Ppeak (col 1)


def compute_intervals(fpt, fs):
    """Compute clinical ECG intervals per beat.

    Parameters
    ----------
    fpt : (n_beats, 13) numpy int array — FPT from annotate_ecg_multi
    fs  : sampling frequency (Hz)

    Returns
    -------
    dict with keys (each is a 1-D float array of length n_beats):
        RR_ms, PR_ms, QRS_ms, QT_ms, QTc_ms, Tpeak_Toff_ms
    Missing values are represented as NaN.
    """
    fpt = np.asarray(fpt, dtype=float)
    n = len(fpt)
    ms = 1000.0 / fs

    def _valid(col):
        v = fpt[:, col]
        return np.where(v > 0, v, np.nan)

    R      = _valid(5)
    Pon    = _valid(0)
    Ppeak  = _valid(1)
    QRSon  = _valid(3)
    QRSoff = _valid(7)
    Tpeak  = _valid(10)
    Toff   = _valid(11)

    # RR interval
    RR = np.full(n, np.nan)
    if n >= 2:
        rr_vals = np.diff(R) * ms
        RR[1:] = rr_vals

    # PR interval: P onset (col 0) → QRS onset (col 3)
    P_anchor = np.where(~np.isnan(Pon), Pon, Ppeak)
    PR = (QRSon - P_anchor) * ms

    # QRS duration
    QRS = (QRSoff - QRSon) * ms

    # QT interval: QRS onset → T offset
    QT = (Toff - QRSon) * ms

    # QTc by Fridericia: QTc = QT / RR^(1/3)
    RR_s = RR / 1000.0
    with np.errstate(invalid='ignore', divide='ignore'):
        QTc = QT / np.cbrt(RR_s)
    QTc = np.where(RR_s > 0, QTc, np.nan)

    # T peak → T offset
    Tpk_Toff = (Toff - Tpeak) * ms

    # Clamp physiologically impossible values to NaN
    def _clamp(arr, lo, hi):
        return np.where((arr > lo) & (arr < hi), arr, np.nan)

    return {
        'RR_ms':           _clamp(RR,       RR_MIN_MS,  RR_MAX_MS),
        'PR_ms':           _clamp(PR,        PR_MIN_MS,  PR_MAX_MS),
        'QRS_ms':          _clamp(QRS,       QRS_MIN_MS, QRS_MAX_MS),
        'QT_ms':           _clamp(QT,        QT_MIN_MS,  QT_MAX_MS),
        'QTc_ms':          _clamp(QTc,       QT_MIN_MS,  QTC_CRITICAL + 200),
        'Tpeak_Toff_ms':   _clamp(Tpk_Toff, 10,         TPEAK_TOFF_MAX_MS),
    }


def validate_markers(fpt, lead_name, fs, signal=None):
    """Run clinical sanity checks on a single-lead FPT.

    Parameters
    ----------
    fpt       : (n_beats, 13) FPT array
    lead_name : string (e.g. 'II', 'V1') — used for lead-specific rules
    fs        : sampling frequency (Hz)
    signal    : optional 1-D signal array for amplitude-based checks

    Returns
    -------
    warnings : list of dict, each with keys:
               'beat' (int or 'all'), 'rule', 'value', 'expected', 'severity'
               severity: 'INFO' | 'WARN' | 'ERROR'
    stats    : dict summary (median intervals, pass/fail counts)
    """
    fpt = np.asarray(fpt, dtype=float)
    n = len(fpt)
    lead_key = lead_name.upper().replace(' ', '') if lead_name else ''
    warnings = []
    ivl = compute_intervals(fpt, fs)

    def _warn(beat, rule, value, expected, severity='WARN'):
        warnings.append({
            'beat': beat, 'rule': rule,
            'value': round(float(value), 1) if not np.isnan(value) else None,
            'expected': expected, 'severity': severity
        })

    # ---- PR interval -------------------------------------------------------
    for i, pr in enumerate(ivl['PR_ms']):
        if np.isnan(pr):
            continue
        if pr < PR_MIN_MS:
            _warn(i, 'PR_too_short', pr, f'>={PR_MIN_MS} ms', 'ERROR')
        elif pr < PR_NORM_MIN:
            _warn(i, 'PR_short', pr, f'{PR_NORM_MIN}–{PR_NORM_MAX} ms', 'WARN')
        elif pr > PR_MAX_MS:
            _warn(i, 'PR_too_long', pr, f'<={PR_MAX_MS} ms', 'ERROR')
        elif pr > PR_NORM_MAX:
            _warn(i, 'PR_long', pr, f'{PR_NORM_MIN}–{PR_NORM_MAX} ms', 'WARN')

    # ---- QRS duration ------------------------------------------------------
    for i, qrs in enumerate(ivl['QRS_ms']):
        if np.isnan(qrs):
            continue
        if qrs > QRS_NORM_MAX:
            sev = 'WARN' if qrs <= 160 else 'ERROR'
            _warn(i, 'QRS_wide', qrs, f'<={QRS_NORM_MAX} ms', sev)

    # ---- QTc ---------------------------------------------------------------
    for i, qtc in enumerate(ivl['QTc_ms']):
        if np.isnan(qtc):
            continue
        if qtc >= QTC_CRITICAL:
            _warn(i, 'QTc_critical', qtc, f'<{QTC_CRITICAL} ms', 'ERROR')
        elif qtc >= QTC_WARN_WOMEN:
            _warn(i, 'QTc_prolonged', qtc, f'<{QTC_WARN_WOMEN} ms', 'WARN')

    # ---- T–peak → T–offset too short (detection error indicator) ----------
    for i, dt in enumerate(ivl['Tpeak_Toff_ms']):
        if np.isnan(dt):
            continue
        if dt < TPEAK_TOFF_MIN_MS:
            _warn(i, 'Toff_too_close_to_Tpeak', dt,
                  f'>={TPEAK_TOFF_MIN_MS} ms', 'ERROR')

    # ---- T-wave concordance ------------------------------------------------
    # T wave should have same sign as R wave (T concordance rule).
    # Exceptions:
    #   1. Some leads always have inverted T (V1, AVR, III, AVL).
    #   2. In bundle branch block (QRS > 120 ms), T inversion in V1-V3 and
    #      some limb leads is a SECONDARY change — expected, not pathological.
    qrs_wide = bool(np.nanmedian(ivl['QRS_ms']) > 120) if any(~np.isnan(ivl['QRS_ms'])) else False

    if lead_key not in T_INVERSION_OK_LEADS and signal is not None:
        # In BBB, secondary T-wave changes in V1-V3 are expected
        bbb_exempt = qrs_wide and lead_key in T_SECONDARY_CHANGE_LEADS_BBB
        if not bbb_exempt:
            sig = np.asarray(signal, dtype=float).ravel()
            for i in range(n):
                r_idx = int(fpt[i, 5])
                t_idx = int(fpt[i, 10])
                if r_idx <= 0 or t_idx <= 0:
                    continue
                if r_idx >= len(sig) or t_idx >= len(sig):
                    continue
                r_amp = sig[r_idx]
                t_amp = sig[t_idx]
                # Only flag when both are clearly non-zero
                if abs(r_amp) < 0.05 or abs(t_amp) < 0.03:
                    continue
                if np.sign(r_amp) != np.sign(t_amp):
                    _warn(i, 'T_discordant',
                          round(t_amp, 3),
                          f'same sign as R ({round(r_amp, 3):+.3f})',
                          'WARN')

    # ---- R amplitude polarity in constrained leads -------------------------
    # Medical rule: R = first positive deflection.
    # QS complex exception: if the QRS region has NO positive deflection
    # (e.g. pathological Q waves from inferior/anterior MI, or LBBB in some
    # leads), the detected R may fall near zero or slightly negative.
    # Only flag as ERROR when r_amp < -0.15 mV (clearly wrong, not QS).
    from .qrs_detection import EXPECTED_R_POSITIVE
    expected_pos = EXPECTED_R_POSITIVE.get(lead_key, None)
    if signal is not None and expected_pos is not None:
        sig = np.asarray(signal, dtype=float).ravel()
        for i in range(n):
            r_idx = int(fpt[i, 5])
            if r_idx <= 0 or r_idx >= len(sig):
                continue
            r_amp = sig[r_idx]
            qrs_on = int(fpt[i, 3])
            qrs_off = int(fpt[i, 7])
            # Detect true QS complex: entire QRS region stays negative
            if qrs_on > 0 and qrs_off > qrs_on and qrs_off < len(sig):
                qrs_seg = sig[qrs_on:qrs_off + 1]
                is_qs = bool(qrs_seg.max() < 0.05)  # no positive deflection
            else:
                is_qs = False
            if expected_pos and r_amp < -0.15 and not is_qs:
                _warn(i, 'R_wrong_polarity',
                      round(r_amp, 3),
                      'positive (first positive deflection rule)',
                      'ERROR')
            elif expected_pos and is_qs:
                _warn(i, 'QS_complex_detected',
                      round(r_amp, 3),
                      'pathological Q wave / QS complex (e.g. MI, LBBB)',
                      'INFO')
            elif not expected_pos and r_amp > 0.05:
                _warn(i, 'R_wrong_polarity',
                      round(r_amp, 3),
                      'negative (aVR should be negative)',
                      'WARN')

    # ---- Summary stats -----------------------------------------------------
    def _med(arr):
        v = arr[~np.isnan(arr)]
        return round(float(np.median(v)), 1) if len(v) else None

    stats = {
        'n_beats':       n,
        'PR_ms_median':  _med(ivl['PR_ms']),
        'QRS_ms_median': _med(ivl['QRS_ms']),
        'QT_ms_median':  _med(ivl['QT_ms']),
        'QTc_ms_median': _med(ivl['QTc_ms']),
        'RR_ms_median':  _med(ivl['RR_ms']),
        'Tpk_Toff_ms_median': _med(ivl['Tpeak_Toff_ms']),
        'n_warnings':    sum(1 for w in warnings if w['severity'] == 'WARN'),
        'n_errors':      sum(1 for w in warnings if w['severity'] == 'ERROR'),
    }

    return warnings, stats


def summarise_patient(fpt_cell, lead_names, fs, signal=None):
    """Compute per-lead stats + aggregate patient-level summary.

    Parameters
    ----------
    fpt_cell   : list of (n_beats, 13) FPT arrays (one per lead)
    lead_names : list of lead name strings
    fs         : sampling frequency (Hz)
    signal     : optional (N, C) signal array for amplitude checks

    Returns
    -------
    per_lead : list of dicts — one per lead with lead_name, stats, n_warnings, n_errors
    patient  : dict — aggregate summary across all leads
    """
    per_lead = []
    total_warnings = 0
    total_errors = 0
    all_pr, all_qrs, all_qtc = [], [], []

    for ch, (fpt, ln) in enumerate(zip(fpt_cell, lead_names)):
        if fpt is None or len(fpt) == 0:
            per_lead.append({'lead': ln, 'status': 'no_detection',
                             'stats': {}, 'warnings': []})
            continue
        sig_ch = signal[:, ch] if signal is not None else None
        warns, stats = validate_markers(fpt, ln, fs, signal=sig_ch)
        per_lead.append({
            'lead':     ln,
            'status':   'ok' if stats['n_errors'] == 0 else 'errors',
            'stats':    stats,
            'warnings': warns,
        })
        total_warnings += stats['n_warnings']
        total_errors   += stats['n_errors']

        ivl = compute_intervals(fpt, fs)
        for arr, store in [(ivl['PR_ms'], all_pr),
                           (ivl['QRS_ms'], all_qrs),
                           (ivl['QTc_ms'], all_qtc)]:
            v = arr[~np.isnan(arr)]
            store.extend(v.tolist())

    def _med(lst):
        return round(float(np.median(lst)), 1) if lst else None

    patient = {
        'n_leads_ok':       sum(1 for r in per_lead if r.get('status') == 'ok'),
        'n_leads_errors':   sum(1 for r in per_lead if r.get('status') == 'errors'),
        'total_warnings':   total_warnings,
        'total_errors':     total_errors,
        'PR_ms_median':     _med(all_pr),
        'QRS_ms_median':    _med(all_qrs),
        'QTc_ms_median':    _med(all_qtc),
    }

    return per_lead, patient
