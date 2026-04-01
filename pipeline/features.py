"""
Node 1.5 — Feature Extraction.

Computes the full FeatureObject from the FiducialTable and PreprocessedECGRecord.
All measurements use morphology_signal (raw amplitude at 500 Hz) for waveform
amplitudes. Interval timing uses FPT sample indices / fs.

Key corrections from RRC review (applied here):
  - Q_duration: uses (Q_idx - QRSon_idx) / fs * 1000, not (R_idx - QRSon_idx)
  - fQRS: sign-change counter on derivative, not filtfilt on short window
  - ST isoelectric: bounds-checked with max(0, QRSon - 10)
  - AFib null-handling: av_ratio = None when atrial rate unavailable
  - P terminal force: mV·s (threshold 0.04 mV·s)
"""

from __future__ import annotations
import numpy as np
from typing import Optional
from pipeline.schemas import (
    PreprocessedECGRecord,
    QualityReport,
    FiducialTable,
    FeatureObject,
    BeatSummary,
)

# FPT column indices
COL_PON, COL_PPEAK, COL_POFF = 0, 1, 2
COL_QRSON, COL_Q, COL_R, COL_S, COL_QRSOFF = 3, 4, 5, 6, 7
COL_L, COL_TON, COL_TPEAK, COL_TOFF = 8, 9, 10, 11
COL_CLASS = 12

# ST elevation thresholds (mV) per lead, per sex (Node 1.5 spec)
ST_THRESHOLD = {
    "default": 0.1,
    "V1_M":    0.2,
    "V2_M":    0.2,
    "V3_M":    0.2,
    "V1_F":    0.15,
    "V2_F":    0.15,
    "V3_F":    0.15,
}

# Minimum notch amplitude to count as fQRS notch (µV)
FQRS_NOTCH_AMPLITUDE_UV = 50.0   # 0.05 mV


def extract_features(
    record: PreprocessedECGRecord,
    quality: QualityReport,
    fiducials: FiducialTable,
) -> FeatureObject:
    """
    Extract all clinical ECG features from the FiducialTable and preprocessed signals.
    """
    fs = record.fs
    leads = record.lead_names
    fpt = fiducials.fpt
    sex = record.patient_sex                # "M" | "F" | None

    # FPT indices are relative to the safe window. Slice both signal matrices
    # to the safe window so that FPT sample indices map correctly.
    s0 = record.safe_window_start_sample
    s1 = record.safe_window_end_sample
    morph = record.morphology_signal[:, s0:s1]      # raw amplitude, no filter
    filtered = record.preprocessed_signal[:, s0:s1] # bandpass-filtered (wander-free)

    # Use lead II FPT as the primary rhythm lead
    ref_lead = _ref_lead(fpt, leads)
    ref_fpt = fpt.get(ref_lead, np.empty((0, 13), dtype=np.int32))

    # --- Rate & Rhythm ---
    (hr_vent, hr_atrial, av_ratio,
     rhythm_regular, dominant_rhythm, rhythm_notes) = _compute_rate_rhythm(ref_fpt, fpt, fs)

    # --- Intervals ---
    pr_ms = _median_interval(ref_fpt, COL_QRSON, COL_PON, fs)  # QRSON - PON (onset-to-onset, clinical standard)
    qrs_ms = _median_interval(ref_fpt, COL_QRSOFF, COL_QRSON, fs)
    qt_ms = _median_interval(ref_fpt, COL_TOFF, COL_QRSON, fs)
    qtc_bazett = _qtc_bazett(qt_ms, hr_vent)
    qtc_fridericia = _qtc_fridericia(qt_ms, hr_vent)
    qtc_framingham = _qtc_framingham(qt_ms, hr_vent)
    qtc_hodges = _qtc_hodges(qt_ms, hr_vent)

    # --- Axis ---
    # Axis computed on bandpass-filtered signal to eliminate baseline wander
    qrs_axis = _compute_axis(filtered, fpt, leads, "qrs")
    p_axis = _compute_axis(filtered, fpt, leads, "p")
    t_axis = _compute_axis(filtered, fpt, leads, "t")

    # --- Per-lead measurements ---
    lead_idx = {l: i for i, l in enumerate(leads)}

    st_elev, st_dep, st_morph, j_point = {}, {}, {}, {}
    t_amp, t_morph, t_qrs_ratio, sym_t_inv = {}, {}, {}, {}
    r_amp, s_amp, q_dur, q_amp = {}, {}, {}, {}
    fqrs, idt = {}, {}
    lead_quality_cap = {}

    for lead in leads:
        if lead not in fpt or len(fpt[lead]) == 0:
            _fill_none_dicts(lead, st_elev, st_dep, st_morph, j_point,
                             t_amp, t_morph, t_qrs_ratio, sym_t_inv,
                             r_amp, s_amp, q_dur, q_amp, fqrs, idt)
            lead_quality_cap[lead] = _quality_cap(quality, lead)
            continue

        li = lead_idx[lead]
        sig = morph[li]
        lf = fpt[lead]
        lq = quality.lead_quality.get(lead)
        quality_ok = lq is None or lq.quality in ("GOOD", "ACCEPTABLE")

        if not quality_ok:
            _fill_none_dicts(lead, st_elev, st_dep, st_morph, j_point,
                             t_amp, t_morph, t_qrs_ratio, sym_t_inv,
                             r_amp, s_amp, q_dur, q_amp, fqrs, idt)
            lead_quality_cap[lead] = _quality_cap(quality, lead)
            continue

        st_e, st_d, st_m, jp = _compute_st(sig, lf, fs, lead, sex)
        st_elev[lead] = st_e
        st_dep[lead] = st_d
        st_morph[lead] = st_m
        j_point[lead] = jp

        ta, tm, tqr, sti = _compute_t_wave(sig, lf, fs)
        t_amp[lead] = ta
        t_morph[lead] = tm
        t_qrs_ratio[lead] = tqr
        sym_t_inv[lead] = sti

        ra, sa, qd, qa = _compute_qrs_amplitudes(sig, lf, fs)
        r_amp[lead] = ra
        s_amp[lead] = sa
        q_dur[lead] = qd    # Q_idx - QRSon_idx (corrected)
        q_amp[lead] = qa

        fqrs[lead] = _detect_fragmented_qrs(sig, lf, fs)
        idt[lead] = _compute_idt(sig, lf, fs)
        lead_quality_cap[lead] = _quality_cap(quality, lead)

    # --- Morphology analysis ---
    from pipeline.morphology import (
        classify_qrs_pattern, classify_st_curvature, classify_t_morphology,
        assess_concordance, detect_av_relationship,
    )

    qrs_pat, st_curv, t_sym, t_det_morph, concord = {}, {}, {}, {}, {}

    for lead in leads:
        if lead not in fpt or len(fpt[lead]) == 0:
            qrs_pat[lead] = "unknown"
            st_curv[lead] = "unknown"
            t_sym[lead] = None
            t_det_morph[lead] = "unknown"
            concord[lead] = "unknown"
            continue

        li = lead_idx[lead]
        sig = morph[li]
        lf = fpt[lead]

        # Use median beat (most representative)
        mid_beat = lf[len(lf) // 2]

        # QRS pattern
        qon, qoff = int(mid_beat[COL_QRSON]), int(mid_beat[COL_QRSOFF])
        if qon > 0 and qoff > 0 and qoff > qon:
            qrs_result = classify_qrs_pattern(sig, qon, qoff, fs)
            qrs_pat[lead] = qrs_result.get("pattern", "unknown")
        else:
            qrs_pat[lead] = "unknown"

        # ST curvature
        qoff_idx = int(mid_beat[COL_QRSOFF])
        ton_idx = int(mid_beat[COL_TON])
        tpk_idx = int(mid_beat[COL_TPEAK])
        if qoff_idx > 0 and ton_idx > 0 and ton_idx > qoff_idx:
            st_result = classify_st_curvature(sig, qoff_idx, ton_idx, tpk_idx, fs)
            st_curv[lead] = st_result.get("curvature", "unknown")
        else:
            st_curv[lead] = "unknown"

        # T-wave morphology
        ton = int(mid_beat[COL_TON])
        tpk = int(mid_beat[COL_TPEAK])
        toff = int(mid_beat[COL_TOFF])
        if ton > 0 and tpk > 0 and toff > 0:
            t_result = classify_t_morphology(sig, ton, tpk, toff, fs)
            t_sym[lead] = t_result.get("symmetry_index")
            t_det_morph[lead] = t_result.get("morphology_label", "unknown")
        else:
            t_sym[lead] = None
            t_det_morph[lead] = "unknown"

        # Concordance (only meaningful if BBB is present)
        st_e = st_elev.get(lead) or 0
        st_d = st_dep.get(lead) or 0
        s_a = s_amp.get(lead) or 0
        if qon > 0 and qoff > 0:
            conc_result = assess_concordance(sig, qon, qoff, st_e, st_d, s_a, fs)
            concord[lead] = conc_result.get("concordance", "unknown")
        else:
            concord[lead] = "unknown"

    # AV relationship (global)
    av_rel_result = detect_av_relationship(ref_fpt, fs)
    av_rel = av_rel_result.get("av_relationship", "unknown") if av_rel_result else "unknown"

    # --- R progression ---
    r_prog = _r_progression(r_amp, leads)

    # --- LVH / RVH / Low voltage ---
    lvh_sl = _lvh_sokolow_lyon(r_amp, s_amp, leads)
    lvh_cornell = _lvh_cornell(r_amp, s_amp, leads, sex)
    lvh_cornell_prod = _lvh_cornell_product(lvh_cornell, qrs_ms)
    lvh_re = _lvh_romhilt_estes(r_amp, s_amp, leads, st_elev, st_dep, p_axis, qrs_ms)
    lvh_lewis = _lvh_lewis(r_amp, s_amp, leads)
    lvh_criteria = _lvh_criteria_met(lvh_sl, lvh_cornell, lvh_cornell_prod, lvh_re, lvh_lewis, sex)
    rvh_criteria = _rvh_criteria_met(r_amp, s_amp, qrs_axis, leads)
    low_v_limb, low_v_precordial = _low_voltage(r_amp, s_amp, leads)

    # --- P wave global ---
    p_dur, p_amp, p_ptf, p_present, p_notes = _compute_p_global(
        morph, fpt, leads, lead_idx, fs
    )

    # --- Special patterns ---
    # Compute net QRS polarity in V1 for BBB discrimination
    v1_net_neg = _v1_qrs_net_negative(morph, fpt, leads, lead_idx)
    lbbb = _detect_lbbb(qrs_ms, r_amp, s_amp, st_elev, leads, v1_net_neg)
    rbbb = _detect_rbbb(qrs_ms, r_amp, s_amp, leads, v1_net_neg)
    # LBBB and RBBB are mutually exclusive
    if lbbb and rbbb:
        rbbb = False
    lafb = _detect_lafb(qrs_axis, q_amp, leads)
    lpfb = _detect_lpfb(qrs_axis, leads)
    wpw = _detect_wpw(pr_ms, qrs_ms, leads)
    brugada1 = _detect_brugada_type1(st_elev, st_morph, leads)
    brugada23 = _detect_brugada_type23(st_elev, st_morph, leads)
    de_winter = _detect_de_winter(st_elev, st_dep, t_amp, leads)
    early_repol = _detect_early_repolarization(j_point, t_amp, leads)
    pericarditis = _detect_pericarditis(st_elev, st_morph, leads)
    hyperacute_t = _detect_hyperacute_t(t_qrs_ratio, t_amp, leads)
    alt = _detect_electrical_alternans(morph, fpt, leads, lead_idx, fs)
    epsilon = _detect_epsilon_wave(morph, fpt, leads, lead_idx, fs)
    u_wave = _detect_u_wave(morph, fpt, leads, lead_idx, fs)
    osborn = _detect_osborn_wave(j_point, leads)

    # --- HRV ---
    sdnn, rmssd = _compute_hrv(ref_fpt, fs)

    # --- QT per lead and dispersion ---
    qt_per_lead = _compute_qt_per_lead(fpt, fs)
    qt_dispersion = _compute_qt_dispersion(qt_per_lead)

    # --- Tpe ---
    tpe = _compute_tpe(ref_fpt, fs)

    # --- Pathological Q waves ---
    path_q = _detect_pathological_q(q_dur, q_amp, r_amp)

    # --- R/S ratio ---
    rs_ratio = _compute_rs_ratio(r_amp, s_amp)

    # --- R-wave progression index ---
    r_prog_idx = _compute_r_progression_index(r_amp, s_amp)

    # --- PR depression ---
    pr_dep = {}
    for lead in leads:
        if lead not in fpt or len(fpt[lead]) == 0:
            pr_dep[lead] = None
            continue
        li = lead_idx[lead]
        lq = quality.lead_quality.get(lead)
        quality_ok = lq is None or lq.quality in ("GOOD", "ACCEPTABLE")
        if not quality_ok:
            pr_dep[lead] = None
            continue
        pr_dep[lead] = _compute_pr_depression(morph[li], fpt[lead], fs)

    # --- Measurement flags ---
    meas_flags = _classify_measurements(
        hr_vent, pr_ms, qrs_ms, qtc_bazett, qrs_axis,
        qt_dispersion, tpe, p_dur, p_amp,
    )

    # --- Beat summary ---
    beat_summary = _build_beat_summary(ref_fpt, fs, dominant_rhythm, rhythm_regular)

    return FeatureObject(
        ecg_id=record.ecg_id,
        heart_rate_ventricular_bpm=hr_vent,
        heart_rate_atrial_bpm=hr_atrial,
        av_ratio=av_ratio,
        rhythm_regular=rhythm_regular,
        dominant_rhythm=dominant_rhythm,
        rhythm_notes=rhythm_notes,
        pr_interval_ms=pr_ms,
        qrs_duration_global_ms=qrs_ms,
        qt_interval_ms=qt_ms,
        qtc_bazett_ms=qtc_bazett,
        qtc_fridericia_ms=qtc_fridericia,
        qtc_framingham_ms=qtc_framingham,
        qtc_hodges_ms=qtc_hodges,
        p_axis_deg=p_axis,
        qrs_axis_deg=qrs_axis,
        t_axis_deg=t_axis,
        st_elevation_mv=st_elev,
        st_depression_mv=st_dep,
        st_morphology=st_morph,
        j_point_mv=j_point,
        t_amplitude_mv=t_amp,
        t_morphology=t_morph,
        t_qrs_ratio=t_qrs_ratio,
        symmetric_t_inversion=sym_t_inv,
        p_duration_ms=p_dur,
        p_amplitude_mv=p_amp,
        p_terminal_force_v1_mv_s=p_ptf,
        p_wave_present=p_present,
        p_morphology_notes=p_notes,
        r_amplitude_mv=r_amp,
        s_amplitude_mv=s_amp,
        q_duration_ms=q_dur,
        q_amplitude_mv=q_amp,
        qrs_fragmented=fqrs,
        r_progression=r_prog,
        intrinsicoid_deflection_ms=idt,
        lvh_sokolow_lyon_mv=lvh_sl,
        lvh_cornell_mv=lvh_cornell,
        lvh_cornell_product_mv_ms=lvh_cornell_prod,
        lvh_romhilt_estes_score=lvh_re,
        lvh_lewis_index_mv=lvh_lewis,
        lvh_criteria_met=lvh_criteria,
        rvh_criteria_met=rvh_criteria,
        low_voltage_limb=low_v_limb,
        low_voltage_precordial=low_v_precordial,
        lbbb=lbbb,
        rbbb=rbbb,
        lafb=lafb,
        lpfb=lpfb,
        wpw_pattern=wpw,
        brugada_type1_pattern=brugada1,
        brugada_type2or3_pattern=brugada23,
        de_winter_pattern=de_winter,
        early_repolarization_pattern=early_repol,
        pericarditis_pattern=pericarditis,
        hyperacute_t_pattern=hyperacute_t,
        electrical_alternans=alt,
        epsilon_wave_suspected=epsilon,
        u_wave_prominent=u_wave,
        osborn_wave=osborn,
        qt_per_lead_ms=qt_per_lead,
        qt_dispersion_ms=qt_dispersion,
        tpe_interval_ms=tpe,
        pathological_q_wave=path_q,
        r_s_ratio=rs_ratio,
        r_progression_index=r_prog_idx,
        pr_depression_mv=pr_dep,
        measurement_flags=meas_flags,
        qrs_pattern=qrs_pat,
        st_curvature=st_curv,
        t_symmetry_index=t_sym,
        t_detailed_morphology=t_det_morph,
        concordance_analysis=concord,
        av_relationship=av_rel,
        sdnn_ms=sdnn,
        rmssd_ms=rmssd,
        lead_quality_cap=lead_quality_cap,
        beat_summary=beat_summary,
    )


# ---------------------------------------------------------------------------
# Rate & Rhythm
# ---------------------------------------------------------------------------

def _compute_rate_rhythm(
    ref_fpt: np.ndarray,
    all_fpt: dict[str, np.ndarray],
    fs: float,
) -> tuple:
    """Compute heart rates, AV ratio, regularity, dominant rhythm."""
    if len(ref_fpt) < 2:
        return None, None, None, False, "unknown", []

    r_peaks = ref_fpt[:, COL_R]
    valid_r = r_peaks[r_peaks >= 0].astype(float)

    if len(valid_r) < 2:
        return None, None, None, False, "unknown", []

    rr = np.diff(valid_r)
    rr_mean = rr.mean()
    hr_vent = 60.0 * fs / rr_mean if rr_mean > 0 else None

    rr_cv = rr.std() / rr_mean if rr_mean > 0 else 0.0

    # Atrial rate: valid P-peaks
    p_peaks = ref_fpt[:, COL_PPEAK]
    valid_p = p_peaks[p_peaks >= 0].astype(float)
    if len(valid_p) >= 2:
        pp = np.diff(valid_p)
        pp_mean = pp.mean()
        hr_atrial = 60.0 * fs / pp_mean if pp_mean > 0 else None
    else:
        hr_atrial = None

    # AV ratio — only if both rates available
    if hr_atrial is not None and hr_atrial > 0 and hr_vent is not None:
        av_ratio = hr_vent / hr_atrial
    else:
        av_ratio = None

    # Dominant rhythm classification
    p_fraction = len(valid_p) / max(len(ref_fpt), 1)
    notes = []

    # AFib: irregular RR intervals (irregularly irregular).
    # Three detection paths:
    #   (a) Strong: rr_cv > 0.08 AND low P detection (< 0.5)
    #   (b) P absent: p_fraction == 0.0 AND any irregularity (rr_cv > 0.05)
    #   (c) Moderate irregularity: rr_cv > 0.10 regardless of P detection.
    #       Fiducial detectors often find "P waves" in AFib (baseline oscillation),
    #       so high p_fraction doesn't exclude AFib if RR is clearly irregular.
    _afib_a = rr_cv > 0.08 and p_fraction < 0.5
    _afib_b = p_fraction == 0.0 and rr_cv > 0.05
    _afib_c = rr_cv > 0.12 and p_fraction < 0.9  # moderate irregularity — fiducials often find spurious P in AFib
    if _afib_a or _afib_b or _afib_c:
        dominant = "afib"
    elif hr_vent is not None and hr_vent > 100:
        dominant = "sinus" if p_fraction > 0.7 else "tachy_unknown"
    elif hr_vent is not None and hr_vent < 60:
        dominant = "sinus" if p_fraction > 0.7 else "brady_unknown"
    elif p_fraction > 0.7:
        dominant = "sinus"
    else:
        dominant = "unknown"

    # AFib is always irregular by definition
    rhythm_regular = (rr_cv < 0.10) and (dominant != "afib")

    return hr_vent, hr_atrial, av_ratio, rhythm_regular, dominant, notes


def _median_interval(fpt: np.ndarray, col_end: int, col_start: int, fs: float, sign: int = 1) -> Optional[float]:
    """Compute median interval between two FPT columns (in ms)."""
    if len(fpt) == 0:
        return None
    starts = fpt[:, col_start].astype(float)
    ends = fpt[:, col_end].astype(float)
    valid = (starts >= 0) & (ends >= 0)
    if valid.sum() == 0:
        return None
    intervals = sign * (ends[valid] - starts[valid]) / fs * 1000
    intervals = intervals[intervals > 0]
    return float(np.median(intervals)) if len(intervals) > 0 else None


# ---------------------------------------------------------------------------
# QTc formulas
# ---------------------------------------------------------------------------

def _qtc_bazett(qt_ms: Optional[float], hr: Optional[float]) -> Optional[float]:
    if qt_ms is None or hr is None or hr <= 0:
        return None
    rr_s = 60.0 / hr
    return qt_ms / np.sqrt(rr_s)


def _qtc_fridericia(qt_ms: Optional[float], hr: Optional[float]) -> Optional[float]:
    if qt_ms is None or hr is None or hr <= 0:
        return None
    rr_s = 60.0 / hr
    return qt_ms / (rr_s ** (1.0 / 3.0))


def _qtc_framingham(qt_ms: Optional[float], hr: Optional[float]) -> Optional[float]:
    if qt_ms is None or hr is None or hr <= 0:
        return None
    rr_s = 60.0 / hr
    return qt_ms + 154 * (1 - rr_s)


def _qtc_hodges(qt_ms: Optional[float], hr: Optional[float]) -> Optional[float]:
    if qt_ms is None or hr is None or hr <= 0:
        return None
    return qt_ms + 1.75 * (hr - 60)


# ---------------------------------------------------------------------------
# Axis (area method)
# ---------------------------------------------------------------------------

def _compute_axis(
    morph: np.ndarray,
    fpt: dict[str, np.ndarray],
    leads: list[str],
    wave: str,
) -> Optional[float]:
    """
    Compute frontal plane axis using the area method on leads I and aVF.
    wave: "qrs" | "p" | "t"
    """
    lead_idx = {l: i for i, l in enumerate(leads)}
    if "I" not in lead_idx or "aVF" not in lead_idx:
        return None

    area_i = _wave_area(morph[lead_idx["I"]], fpt.get("I"), wave)
    area_avf = _wave_area(morph[lead_idx["aVF"]], fpt.get("aVF"), wave)

    if area_i is None or area_avf is None:
        return None

    return float(np.degrees(np.arctan2(area_avf, area_i)))


def _wave_area(sig: np.ndarray, fpt: Optional[np.ndarray], wave: str) -> Optional[float]:
    """Compute net area of a wave type across all beats."""
    if fpt is None or len(fpt) == 0:
        return None

    if wave == "qrs":
        starts, ends = fpt[:, COL_QRSON], fpt[:, COL_QRSOFF]
    elif wave == "p":
        starts, ends = fpt[:, COL_PON], fpt[:, COL_POFF]
    elif wave == "t":
        starts, ends = fpt[:, COL_TON], fpt[:, COL_TOFF]
    else:
        return None

    areas = []
    for s, e in zip(starts, ends):
        if s >= 0 and e >= 0 and e > s:
            areas.append(float(np.trapz(sig[s:e+1])))

    return float(np.median(areas)) if areas else None


# ---------------------------------------------------------------------------
# ST
# ---------------------------------------------------------------------------

def _compute_st(
    sig: np.ndarray,
    fpt: np.ndarray,
    fs: float,
    lead: str,
    sex: Optional[str],
) -> tuple:
    """Compute ST elevation, depression, morphology, J-point."""
    if len(fpt) == 0:
        return None, None, None, None

    j_points = []
    st_values = []

    for beat in fpt:
        qrs_on = beat[COL_QRSON]
        qrs_off = beat[COL_QRSOFF]
        t_on = beat[COL_TON]

        if qrs_on < 0 or qrs_off < 0:
            continue

        # Isoelectric reference: 10 samples before QRSon (bounds-checked)
        iso_start = max(0, qrs_on - 10)
        if iso_start == qrs_on:
            continue
        iso_segment = sig[iso_start:qrs_on]
        if len(iso_segment) == 0:
            continue
        isoelectric = float(np.mean(iso_segment))

        # J-point: QRSoff
        j_val = float(sig[qrs_off]) - isoelectric if 0 <= qrs_off < len(sig) else None
        if j_val is not None:
            j_points.append(j_val)

        # ST measurement: 60 ms after QRSoff (J+60)
        j60_idx = qrs_off + int(0.06 * fs)
        if 0 <= j60_idx < len(sig):
            st_values.append(float(sig[j60_idx]) - isoelectric)

    if not st_values:
        return None, None, None, None

    # Convert µV to mV
    j_med = float(np.median(j_points)) / 1000.0 if j_points else None
    st_med = float(np.median(st_values)) / 1000.0

    # Morphology classification
    st_morph = _classify_st_morphology(sig, fpt, fs)

    elev = st_med if st_med > 0 else None
    dep = abs(st_med) if st_med < 0 else None

    return elev, dep, st_morph, j_med


def _classify_st_morphology(sig: np.ndarray, fpt: np.ndarray, fs: float) -> Optional[str]:
    """Classify ST morphology as upsloping, downsloping, horizontal, or saddle."""
    slopes = []
    for beat in fpt:
        qrs_off = beat[COL_QRSOFF]
        t_on = beat[COL_TON]
        if qrs_off < 0 or t_on < 0 or t_on <= qrs_off:
            continue
        st_seg = sig[qrs_off:t_on]
        if len(st_seg) < 3:
            continue
        x = np.arange(len(st_seg), dtype=float)
        slope = np.polyfit(x, st_seg.astype(float), 1)[0]
        slopes.append(slope)

    if not slopes:
        return None
    med_slope = float(np.median(slopes))
    if med_slope > 2.0:
        return "upsloping"
    if med_slope < -2.0:
        return "downsloping"
    return "horizontal"


# ---------------------------------------------------------------------------
# T wave
# ---------------------------------------------------------------------------

def _compute_t_wave(sig: np.ndarray, fpt: np.ndarray, fs: float) -> tuple:
    """Compute T amplitude, morphology, T/QRS ratio, symmetric inversion."""
    t_amps = []
    qrs_amps = []

    for beat in fpt:
        t_peak = beat[COL_TPEAK]
        t_on = beat[COL_TON]
        t_off = beat[COL_TOFF]
        qrs_on = beat[COL_QRSON]
        qrs_off = beat[COL_QRSOFF]
        r_idx = beat[COL_R]

        if t_peak >= 0 and 0 <= t_peak < len(sig):
            t_amps.append(float(sig[t_peak]))
        if r_idx >= 0 and 0 <= r_idx < len(sig) and qrs_on >= 0:
            qrs_amps.append(abs(float(sig[r_idx]) - float(sig[qrs_on])))

    if not t_amps:
        return None, None, None, False

    t_med_uv = float(np.median(t_amps))
    t_med_mv = t_med_uv / 1000.0
    qrs_amp_mv = float(np.median(qrs_amps)) / 1000.0 if qrs_amps else None

    t_qrs = abs(t_med_mv) / qrs_amp_mv if qrs_amp_mv and qrs_amp_mv > 0 else None

    # Morphology
    if t_med_mv > 0.1:
        t_morph = "upright"
    elif t_med_mv < -0.1:
        t_morph = "inverted"
    elif abs(t_med_mv) <= 0.1:
        t_morph = "flat"
    else:
        t_morph = "biphasic"

    # Symmetric inversion detection (simplified: deep inversion + narrow T)
    sym_inv = t_med_mv < -0.15

    return t_med_mv, t_morph, t_qrs, sym_inv


# ---------------------------------------------------------------------------
# QRS amplitudes
# ---------------------------------------------------------------------------

def _compute_qrs_amplitudes(
    sig: np.ndarray,
    fpt: np.ndarray,
    fs: float,
) -> tuple:
    """Compute R amp, S amp, Q duration (corrected), Q amplitude."""
    r_amps, s_amps, q_durs, q_amps = [], [], [], []

    for beat in fpt:
        qrs_on = beat[COL_QRSON]
        r_idx = beat[COL_R]
        q_idx = beat[COL_Q]
        s_idx = beat[COL_S]
        qrs_off = beat[COL_QRSOFF]

        if r_idx >= 0 and 0 <= r_idx < len(sig):
            r_amps.append(abs(float(sig[r_idx])))

        if s_idx >= 0 and 0 <= s_idx < len(sig):
            s_amps.append(abs(float(sig[s_idx])))

        # Q duration: Q nadir to QRSon (corrected — not R to QRSon)
        if q_idx >= 0 and qrs_on >= 0 and q_idx > qrs_on:
            q_durs.append((q_idx - qrs_on) / fs * 1000)
            if 0 <= q_idx < len(sig):
                q_amps.append(abs(float(sig[q_idx])))

    def _median_or_none(lst):
        return float(np.median(lst)) / 1000.0 if lst else None  # µV → mV

    def _median_ms_or_none(lst):
        return float(np.median(lst)) if lst else None

    return (
        _median_or_none(r_amps),
        _median_or_none(s_amps),
        _median_ms_or_none(q_durs),
        _median_or_none(q_amps),
    )


# ---------------------------------------------------------------------------
# fQRS (fragmented QRS) — sign-change counter
# ---------------------------------------------------------------------------

def _detect_fragmented_qrs(sig: np.ndarray, fpt: np.ndarray, fs: float) -> bool:
    """
    Detect fragmented QRS using derivative sign-change counting.
    Notch is counted if local amplitude deviation > FQRS_NOTCH_AMPLITUDE_UV.
    Returns True if median notch_count - 1 >= 2 across beats.
    """
    notch_counts = []

    for beat in fpt:
        qrs_on = beat[COL_QRSON]
        qrs_off = beat[COL_QRSOFF]
        if qrs_on < 0 or qrs_off < 0 or qrs_off <= qrs_on:
            continue

        qrs_seg = sig[qrs_on:qrs_off + 1].astype(float)
        if len(qrs_seg) < 5:
            continue

        d = np.diff(qrs_seg)
        sign_changes = np.where(np.diff(np.sign(d)))[0] + 1
        notch_count = 0
        for idx in sign_changes:
            local_context = qrs_seg[max(0, idx - 3):idx + 4]
            local_amp = abs(qrs_seg[idx] - np.mean(local_context))
            if local_amp > FQRS_NOTCH_AMPLITUDE_UV:
                notch_count += 1

        notch_counts.append(notch_count)

    if not notch_counts:
        return False
    return float(np.median(notch_counts)) - 1 >= 2


# ---------------------------------------------------------------------------
# Intrinsicoid deflection time
# ---------------------------------------------------------------------------

def _compute_idt(sig: np.ndarray, fpt: np.ndarray, fs: float) -> Optional[float]:
    """Time from QRSon to R-peak (intrinsicoid deflection time), in ms."""
    idts = []
    for beat in fpt:
        qrs_on = beat[COL_QRSON]
        r_idx = beat[COL_R]
        if qrs_on >= 0 and r_idx >= 0 and r_idx > qrs_on:
            idts.append((r_idx - qrs_on) / fs * 1000)
    return float(np.median(idts)) if idts else None


# ---------------------------------------------------------------------------
# P wave global
# ---------------------------------------------------------------------------

def _compute_p_global(
    morph: np.ndarray,
    fpt: dict[str, np.ndarray],
    leads: list[str],
    lead_idx: dict[str, int],
    fs: float,
) -> tuple:
    """Compute P duration, amplitude, P terminal force (V1), P present flag, notes."""
    # P duration from lead II
    p_dur = None
    if "II" in fpt and len(fpt["II"]) > 0:
        lf = fpt["II"]
        durs = []
        for beat in lf:
            p_on = beat[COL_PON]
            p_off = beat[COL_POFF]
            if p_on >= 0 and p_off >= 0 and p_off > p_on:
                durs.append((p_off - p_on) / fs * 1000)
        p_dur = float(np.median(durs)) if durs else None

    # P amplitude from lead II
    p_amp = None
    if "II" in fpt and "II" in lead_idx and len(fpt["II"]) > 0:
        sig_ii = morph[lead_idx["II"]]
        amps = []
        for beat in fpt["II"]:
            pp = beat[COL_PPEAK]
            qrs_on = beat[COL_QRSON]
            if pp >= 0 and 0 <= pp < len(sig_ii):
                iso = float(sig_ii[max(0, qrs_on - 10):qrs_on].mean()) if qrs_on > 10 else 0.0
                amps.append(abs(float(sig_ii[pp]) - iso))
        p_amp = float(np.median(amps)) / 1000.0 if amps else None  # µV → mV

    # P terminal force in V1 (mV·s)
    p_ptf = None
    if "V1" in fpt and "V1" in lead_idx and len(fpt["V1"]) > 0:
        sig_v1 = morph[lead_idx["V1"]]
        ptf_vals = []
        for beat in fpt["V1"]:
            p_peak = beat[COL_PPEAK]
            p_off = beat[COL_POFF]
            if p_peak < 0 or p_off < 0:
                continue
            neg_seg = sig_v1[p_peak:p_off + 1]
            neg_part = neg_seg[neg_seg < 0]
            if len(neg_part) == 0:
                continue
            neg_amplitude_mv = abs(float(np.min(neg_part))) / 1000.0
            neg_duration_s = len(neg_part) / fs
            ptf_vals.append(neg_amplitude_mv * neg_duration_s)
        p_ptf = float(np.median(ptf_vals)) if ptf_vals else None

    # P present: fraction of beats with detected P-peak > 50%
    p_present = False
    if "II" in fpt and len(fpt["II"]) > 0:
        lf = fpt["II"]
        p_count = np.sum(lf[:, COL_PPEAK] >= 0)
        p_present = (p_count / len(lf)) > 0.5

    notes = []
    if p_dur is not None and p_dur > 120:
        notes.append("P duration prolonged (> 120 ms)")
    if p_ptf is not None and p_ptf > 0.04:
        notes.append("P terminal force V1 elevated (> 0.04 mV·s) — consider LAE")

    return p_dur, p_amp, p_ptf, p_present, notes


# ---------------------------------------------------------------------------
# LVH / RVH / Low voltage
# ---------------------------------------------------------------------------

def _get_mv(d: dict, lead: str) -> Optional[float]:
    return d.get(lead)


def _lvh_sokolow_lyon(r_amp: dict, s_amp: dict, leads: list[str]) -> Optional[float]:
    sv1 = _get_mv(s_amp, "V1")
    rv5 = _get_mv(r_amp, "V5")
    rv6 = _get_mv(r_amp, "V6")
    if sv1 is None:
        return None
    r_max = max(v for v in [rv5, rv6] if v is not None) if any(v is not None for v in [rv5, rv6]) else None
    return (sv1 + r_max) if r_max is not None else None


def _lvh_cornell(r_amp: dict, s_amp: dict, leads: list[str], sex: Optional[str]) -> Optional[float]:
    ravl = _get_mv(r_amp, "aVL")
    sv3 = _get_mv(s_amp, "V3")
    if ravl is None or sv3 is None:
        return None
    val = ravl + sv3
    # Cornell criteria: M > 2.8 mV, F > 2.0 mV (add 0.6 mV for female)
    if sex == "F":
        val += 0.6
    return val


def _lvh_cornell_product(cornell: Optional[float], qrs_ms: Optional[float]) -> Optional[float]:
    if cornell is None or qrs_ms is None:
        return None
    return cornell * qrs_ms


def _lvh_romhilt_estes(
    r_amp: dict, s_amp: dict, leads: list[str],
    st_elev: dict, st_dep: dict,
    p_axis: Optional[float],
    qrs_ms: Optional[float],
) -> Optional[int]:
    """Simplified Romhilt-Estes score (≥ 5 = definite LVH, 4 = probable)."""
    score = 0

    # Voltage criteria (3 points each — only one counts)
    sv1 = _get_mv(s_amp, "V1") or 0
    rv5 = _get_mv(r_amp, "V5") or 0
    rv6 = _get_mv(r_amp, "V6") or 0
    ravl = _get_mv(r_amp, "aVL") or 0
    ravf = _get_mv(r_amp, "aVF") or 0
    ri = _get_mv(r_amp, "I") or 0
    siii = _get_mv(s_amp, "III") or 0

    if sv1 + max(rv5, rv6) > 3.5 or ravl > 1.1 or ravf > 2.0 or ri + siii > 2.5:
        score += 3

    # ST-T changes (3 points)
    if any(_get_mv(st_dep, l) and _get_mv(st_dep, l) > 0.05 for l in ["V5", "V6", "I", "aVL"]):
        score += 3

    # LAE (P terminal force — handled in P global)
    # QRS widening
    if qrs_ms is not None and qrs_ms > 90:
        score += 1

    return score


def _lvh_lewis(r_amp: dict, s_amp: dict, leads: list[str]) -> Optional[float]:
    ri = _get_mv(r_amp, "I")
    si = _get_mv(s_amp, "I")
    riii = _get_mv(r_amp, "III")
    siii = _get_mv(s_amp, "III")
    if any(v is None for v in [ri, si, riii, siii]):
        return None
    return (ri + siii) - (riii + si)


def _lvh_criteria_met(
    sl: Optional[float], cornell: Optional[float], cp: Optional[float],
    re: Optional[int], lewis: Optional[float], sex: Optional[str],
) -> list[str]:
    criteria = []
    if sl is not None and sl > 3.5:
        criteria.append("Sokolow-Lyon")
    if cornell is not None:
        threshold = 2.8 if sex != "F" else 2.0
        if cornell > threshold:
            criteria.append("Cornell voltage")
    if cp is not None and cp > 244:
        criteria.append("Cornell product")
    if re is not None and re >= 5:
        criteria.append("Romhilt-Estes definite")
    elif re is not None and re == 4:
        criteria.append("Romhilt-Estes probable")
    if lewis is not None and lewis > 1.6:
        criteria.append("Lewis index")
    return criteria


def _rvh_criteria_met(
    r_amp: dict, s_amp: dict,
    qrs_axis: Optional[float],
    leads: list[str],
) -> list[str]:
    criteria = []
    rv1 = _get_mv(r_amp, "V1")
    sv1 = _get_mv(s_amp, "V1")
    rv5 = _get_mv(r_amp, "V5")
    sv5 = _get_mv(s_amp, "V5")

    if rv1 is not None and sv1 is not None and rv1 > sv1:
        criteria.append("R > S in V1")
    if rv5 is not None and sv5 is not None and rv5 < sv5:
        criteria.append("S > R in V5/V6")
    if qrs_axis is not None and qrs_axis > 100:
        criteria.append("Right axis deviation")
    return criteria


def _low_voltage(r_amp: dict, s_amp: dict, leads: list[str]) -> tuple[bool, bool]:
    limb_leads = ["I", "II", "III", "aVR", "aVL", "aVF"]
    precordial_leads = ["V1", "V2", "V3", "V4", "V5", "V6"]

    def _peak_to_peak(lead: str) -> Optional[float]:
        r = _get_mv(r_amp, lead) or 0
        s = _get_mv(s_amp, lead) or 0
        return r + s

    limb_pp = [_peak_to_peak(l) for l in limb_leads if l in r_amp or l in s_amp]
    prec_pp = [_peak_to_peak(l) for l in precordial_leads if l in r_amp or l in s_amp]

    low_limb = bool(limb_pp) and max(limb_pp) < 0.5
    low_prec = bool(prec_pp) and max(prec_pp) < 1.0

    return low_limb, low_prec


# ---------------------------------------------------------------------------
# Special patterns
# ---------------------------------------------------------------------------

def _v1_qrs_net_negative(morph: np.ndarray, fpt: dict, leads: list[str],
                         lead_idx: dict) -> bool:
    """Check if V1 QRS has LBBB-type morphology (predominantly negative, no late R').
    Uses the net signed area of the entire QRS in V1. If the net area is negative
    AND the peak positive amplitude in the second half doesn't exceed the peak
    negative amplitude (no R' component), it's LBBB pattern."""
    if "V1" not in fpt or "V1" not in lead_idx:
        return False
    sig = morph[lead_idx["V1"]]
    lf = fpt["V1"]
    votes = []  # True = LBBB pattern, False = RBBB pattern
    for beat in lf:
        qrs_on = int(beat[COL_QRSON])
        qrs_off = int(beat[COL_QRSOFF])
        if qrs_on < 0 or qrs_off < 0 or qrs_off <= qrs_on:
            continue
        if qrs_off >= len(sig):
            continue
        segment = sig[qrs_on:qrs_off].astype(float)
        net_area = float(segment.sum())
        # Check second half for R' (positive peak in terminal portion)
        mid = len(segment) // 2
        second_half = segment[mid:]
        max_pos_2nd = float(second_half.max()) if len(second_half) > 0 else 0
        max_neg = float(abs(segment.min()))
        # LBBB: net negative AND no significant late positive deflection
        # RBBB: late positive deflection (R') in second half
        is_lbbb_pattern = (net_area < 0) and (max_pos_2nd < max_neg * 0.5)
        votes.append(is_lbbb_pattern)
    if not votes:
        return False
    return sum(votes) > len(votes) / 2  # majority vote


def _detect_lbbb(
    qrs_ms: Optional[float], r_amp: dict, s_amp: dict, st_elev: dict,
    leads: list[str], v1_net_neg: bool = False
) -> bool:
    """LBBB: wide QRS + negative QRS in V1 (QS/rS) + broad R in V5/V6.
    V1 polarity determined from signed signal area, not abs amplitude."""
    if qrs_ms is None or qrs_ms < 110:
        return False
    # V1 must show net negative QRS (QS or rS morphology)
    if not v1_net_neg:
        return False
    # V5 or V6: R must clearly dominate S (broad monophasic R, R/S > 1.5)
    rv5 = _get_mv(r_amp, "V5") or 0
    sv5 = _get_mv(s_amp, "V5") or 0
    rv6 = _get_mv(r_amp, "V6") or 0
    sv6 = _get_mv(s_amp, "V6") or 0
    v5_ok = rv5 > 0.2 and (sv5 == 0 or rv5 / max(sv5, 0.001) > 1.5)
    v6_ok = rv6 > 0.2 and (sv6 == 0 or rv6 / max(sv6, 0.001) > 1.5)
    return v5_ok or v6_ok


def _detect_rbbb(qrs_ms: Optional[float], r_amp: dict, s_amp: dict,
                 leads: list[str], v1_net_neg: bool = False) -> bool:
    """RBBB: wide QRS + positive QRS in V1 (RSR') + wide S in lateral leads.
    V1 must NOT have net negative polarity (that's LBBB)."""
    if qrs_ms is None or qrs_ms < 110:
        return False
    # V1 should NOT be net negative (which would be LBBB)
    if v1_net_neg:
        return False
    # V1: must have significant R amplitude
    rv1 = _get_mv(r_amp, "V1") or 0
    if rv1 < 0.1:
        return False
    # Wide S in lateral leads (I, V5, or V6)
    si = _get_mv(s_amp, "I") or 0
    sv5 = _get_mv(s_amp, "V5") or 0
    sv6 = _get_mv(s_amp, "V6") or 0
    has_lateral_s = si > 0.05 or sv5 > 0.05 or sv6 > 0.05
    return has_lateral_s


def _detect_lafb(qrs_axis: Optional[float], q_amp: dict, leads: list[str]) -> bool:
    if qrs_axis is None:
        return False
    return qrs_axis < -45


def _detect_lpfb(qrs_axis: Optional[float], leads: list[str]) -> bool:
    if qrs_axis is None:
        return False
    return qrs_axis > 120


def _detect_wpw(pr_ms: Optional[float], qrs_ms: Optional[float], leads: list[str]) -> bool:
    """WPW pattern: short PR (< 120 ms) with widened QRS (> 100 ms) indicating pre-excitation.
    Clinical criteria: PR < 120ms + QRS > 100ms + delta wave (approximated by the combination)."""
    return (
        pr_ms is not None and pr_ms < 120
        and qrs_ms is not None and qrs_ms > 100
    )


def _detect_brugada_type1(st_elev: dict, st_morph: dict, leads: list[str]) -> bool:
    for lead in ["V1", "V2"]:
        elev = _get_mv(st_elev, lead) or 0
        morph = st_morph.get(lead)
        if elev >= 0.2 and morph == "downsloping":
            return True
    return False


def _detect_brugada_type23(st_elev: dict, st_morph: dict, leads: list[str]) -> bool:
    for lead in ["V1", "V2"]:
        elev = _get_mv(st_elev, lead) or 0
        if 0.1 <= elev < 0.2:
            return True
    return False


def _detect_de_winter(st_elev: dict, st_dep: dict, t_amp: dict, leads: list[str]) -> bool:
    """de Winter: upsloping ST depression + tall symmetric T in >= 2 precordial leads."""
    prec_dep = sum(1 for l in ["V1", "V2", "V3", "V4"] if (_get_mv(st_dep, l) or 0) > 0.1)
    prec_tall_t = sum(1 for l in ["V3", "V4", "V5", "V6"] if (_get_mv(t_amp, l) or 0) > 0.8)
    return prec_dep >= 2 and prec_tall_t >= 2


def _detect_early_repolarization(j_point: dict, t_amp: dict, leads: list[str]) -> bool:
    for lead in ["II", "aVF", "V4", "V5", "V6"]:
        jp = _get_mv(j_point, lead) or 0
        ta = _get_mv(t_amp, lead) or 0
        if jp >= 0.1 and ta > 0.1:
            return True
    return False


def _detect_pericarditis(st_elev: dict, st_morph: dict, leads: list[str]) -> bool:
    """Pericarditis: diffuse ST elevation in >= 5 leads at >= 0.1 mV (1mm).
    Requires widespread involvement to distinguish from focal ischemia."""
    diffuse_leads = ["I", "II", "III", "aVF", "V2", "V3", "V4", "V5", "V6"]
    elevated = sum(1 for l in diffuse_leads if (_get_mv(st_elev, l) or 0) > 0.1)
    return elevated >= 5


def _detect_hyperacute_t(t_qrs_ratio: dict, t_amp: dict, leads: list[str]) -> bool:
    """
    Hyperacute T: T/QRS ratio > 0.75 in precordial leads V1-V4
    AND absolute T amplitude ≥ 0.6 mV.
    The amplitude gate reduces false positives from normal tall-T variants
    (early repolarization in young patients).
    """
    for lead in ["V1", "V2", "V3", "V4"]:
        ratio = t_qrs_ratio.get(lead)
        amp = t_amp.get(lead)
        if ratio is not None and ratio > 0.75:
            if amp is not None and abs(amp) >= 0.6:  # 0.6 mV gate
                return True
    return False


def _detect_electrical_alternans(
    morph: np.ndarray,
    fpt: dict[str, np.ndarray],
    leads: list[str],
    lead_idx: dict[str, int],
    fs: float,
) -> bool:
    """Detect beat-to-beat R amplitude alternans in V5."""
    lead = "V5"
    if lead not in fpt or lead not in lead_idx:
        return False
    sig = morph[lead_idx[lead]]
    lf = fpt[lead]
    r_peaks = lf[:, COL_R]
    valid_r = r_peaks[r_peaks >= 0]
    if len(valid_r) < 4:
        return False
    r_amps = [abs(float(sig[r])) for r in valid_r if 0 <= r < len(sig)]
    if len(r_amps) < 4:
        return False
    even = np.array(r_amps[0::2])
    odd = np.array(r_amps[1::2])
    n = min(len(even), len(odd))
    if n < 2:
        return False
    alt_ratio = abs(even[:n].mean() - odd[:n].mean()) / max(even[:n].mean(), 1)
    return alt_ratio > 0.10


def _detect_epsilon_wave(
    morph: np.ndarray,
    fpt: dict[str, np.ndarray],
    leads: list[str],
    lead_idx: dict[str, int],
    fs: float,
) -> bool:
    """Suspected epsilon wave: small deflection immediately after QRS in V1/V2."""
    for lead in ["V1", "V2"]:
        if lead not in fpt or lead not in lead_idx:
            continue
        sig = morph[lead_idx[lead]]
        lf = fpt[lead]
        for beat in lf:
            qrs_off = beat[COL_QRSOFF]
            t_on = beat[COL_TON]
            if qrs_off < 0 or t_on < 0:
                continue
            post_qrs_window = int(0.04 * fs)
            seg_end = min(qrs_off + post_qrs_window, t_on, len(sig))
            seg = sig[qrs_off:seg_end]
            if len(seg) < 3:
                continue
            d = np.diff(seg.astype(float))
            sign_changes = np.sum(np.diff(np.sign(d)) != 0)
            if sign_changes >= 2:
                return True
    return False


def _detect_u_wave(
    morph: np.ndarray,
    fpt: dict[str, np.ndarray],
    leads: list[str],
    lead_idx: dict[str, int],
    fs: float,
) -> bool:
    """Detect prominent U wave in V2/V3 (amplitude > 25% of T wave amplitude)."""
    for lead in ["V2", "V3"]:
        if lead not in fpt or lead not in lead_idx:
            continue
        sig = morph[lead_idx[lead]]
        lf = fpt[lead]
        for beat in lf:
            t_off = beat[COL_TOFF]
            t_peak = beat[COL_TPEAK]
            if t_off < 0 or t_peak < 0:
                continue
            u_end = min(t_off + int(0.25 * fs), len(sig) - 1)
            if u_end <= t_off:
                continue
            u_seg = sig[t_off:u_end]
            u_amp = abs(float(np.max(u_seg)) - float(np.min(u_seg)))
            t_amp = abs(float(sig[t_peak]))
            if t_amp > 0 and u_amp / t_amp > 0.25:
                return True
    return False


def _detect_osborn_wave(j_point: dict, leads: list[str]) -> bool:
    """Osborn (J) wave: prominent J-point deflection > 0.1 mV in ≥ 2 leads."""
    count = sum(1 for l in leads if (_get_mv(j_point, l) or 0) > 0.1)
    return count >= 2


# ---------------------------------------------------------------------------
# QT per lead, QT dispersion, Tpe
# ---------------------------------------------------------------------------

def _compute_qt_per_lead(fpt: dict[str, np.ndarray], fs: float) -> dict[str, Optional[float]]:
    """Compute QT interval per lead (QRSon to Toff)."""
    qt_per_lead = {}
    for lead, lf in fpt.items():
        if len(lf) == 0:
            qt_per_lead[lead] = None
            continue
        intervals = []
        for beat in lf:
            qrs_on = beat[COL_QRSON]
            t_off = beat[COL_TOFF]
            if qrs_on >= 0 and t_off >= 0 and t_off > qrs_on:
                intervals.append((t_off - qrs_on) / fs * 1000)
        qt_per_lead[lead] = float(np.median(intervals)) if intervals else None
    return qt_per_lead


def _compute_qt_dispersion(qt_per_lead: dict[str, Optional[float]]) -> Optional[float]:
    """QT dispersion = max(QT) - min(QT) across all leads with valid QT."""
    valid = [v for v in qt_per_lead.values() if v is not None and v > 0]
    if len(valid) < 2:
        return None
    return max(valid) - min(valid)


def _compute_tpe(ref_fpt: np.ndarray, fs: float) -> Optional[float]:
    """Tpeak to Tend interval in ms (SCD risk marker). Uses reference lead."""
    if len(ref_fpt) == 0:
        return None
    intervals = []
    for beat in ref_fpt:
        t_peak = beat[COL_TPEAK]
        t_off = beat[COL_TOFF]
        if t_peak >= 0 and t_off >= 0 and t_off > t_peak:
            intervals.append((t_off - t_peak) / fs * 1000)
    return float(np.median(intervals)) if intervals else None


# ---------------------------------------------------------------------------
# Pathological Q waves
# ---------------------------------------------------------------------------

def _detect_pathological_q(q_dur: dict, q_amp: dict, r_amp: dict) -> dict[str, bool]:
    """Pathological Q wave: duration > 40ms OR depth > 25% of R-wave amplitude."""
    result = {}
    for lead in q_dur:
        qd = q_dur.get(lead)
        qa = q_amp.get(lead)
        ra = r_amp.get(lead)
        if qd is None and qa is None:
            result[lead] = False
            continue
        dur_path = qd is not None and qd > 40
        depth_path = (qa is not None and ra is not None and ra > 0
                      and qa / ra > 0.25)
        result[lead] = dur_path or depth_path
    return result


# ---------------------------------------------------------------------------
# R/S ratio and R-wave progression index
# ---------------------------------------------------------------------------

def _compute_rs_ratio(r_amp: dict, s_amp: dict) -> dict[str, Optional[float]]:
    """R/S amplitude ratio per lead."""
    result = {}
    for lead in r_amp:
        r = r_amp.get(lead)
        s = s_amp.get(lead)
        if r is not None and s is not None and s > 0:
            result[lead] = r / s
        elif r is not None and (s is None or s == 0):
            result[lead] = float('inf') if r > 0 else None
        else:
            result[lead] = None
    return result


def _compute_r_progression_index(r_amp: dict, s_amp: dict) -> Optional[float]:
    """Compute transition zone index: the precordial lead where R/S ratio crosses 1.0.
    Returns a float (e.g., 3.5 means transition between V3 and V4). Normal: 3-4."""
    prec = ["V1", "V2", "V3", "V4", "V5", "V6"]
    ratios = []
    for lead in prec:
        r = r_amp.get(lead)
        s = s_amp.get(lead)
        if r is not None and s is not None and s > 0:
            ratios.append(r / s)
        else:
            ratios.append(None)
    for i in range(len(ratios) - 1):
        if ratios[i] is not None and ratios[i + 1] is not None:
            if ratios[i] < 1.0 and ratios[i + 1] >= 1.0:
                frac = (1.0 - ratios[i]) / (ratios[i + 1] - ratios[i])
                return float(i + 1 + frac)
    return None


# ---------------------------------------------------------------------------
# PR depression
# ---------------------------------------------------------------------------

def _compute_pr_depression(sig: np.ndarray, fpt: np.ndarray, fs: float) -> Optional[float]:
    """Compute PR segment depression (below isoelectric) in mV. Pericarditis marker."""
    if len(fpt) == 0:
        return None
    deps = []
    for beat in fpt:
        p_off = beat[COL_POFF]
        qrs_on = beat[COL_QRSON]
        if p_off < 0 or qrs_on < 0 or qrs_on <= p_off:
            continue
        p_on = beat[COL_PON]
        if p_on < 0:
            continue
        iso_start = max(0, p_on - 10)
        if iso_start >= p_on:
            continue
        iso = float(np.mean(sig[iso_start:p_on]))
        pr_seg = sig[p_off:qrs_on]
        if len(pr_seg) < 2:
            continue
        pr_mean = float(np.mean(pr_seg))
        dep = (iso - pr_mean) / 1000.0
        if dep > 0:
            deps.append(dep)
    return float(np.median(deps)) if deps else None


# ---------------------------------------------------------------------------
# Measurement flags
# ---------------------------------------------------------------------------

def _classify_measurements(
    hr: Optional[float],
    pr_ms: Optional[float],
    qrs_ms: Optional[float],
    qtc_ms: Optional[float],
    qrs_axis: Optional[float],
    qt_disp: Optional[float],
    tpe_ms: Optional[float],
    p_dur: Optional[float],
    p_amp: Optional[float],
) -> dict[str, str]:
    """Classify each measurement as normal/borderline/abnormal based on clinical ranges."""
    flags = {}

    if hr is not None:
        if 60 <= hr <= 100:
            flags["heart_rate"] = "normal"
        elif 50 <= hr < 60 or 100 < hr <= 110:
            flags["heart_rate"] = "borderline"
        else:
            flags["heart_rate"] = "abnormal"

    if pr_ms is not None:
        if 120 <= pr_ms <= 200:
            flags["pr_interval"] = "normal"
        elif 200 < pr_ms <= 220:
            flags["pr_interval"] = "borderline"
        elif pr_ms < 120:
            flags["pr_interval"] = "abnormal"
        else:
            flags["pr_interval"] = "abnormal"

    if qrs_ms is not None:
        if qrs_ms < 100:
            flags["qrs_duration"] = "normal"
        elif 100 <= qrs_ms < 120:
            flags["qrs_duration"] = "borderline"
        else:
            flags["qrs_duration"] = "abnormal"

    if qtc_ms is not None:
        if qtc_ms < 440:
            flags["qtc"] = "normal"
        elif 440 <= qtc_ms < 470:
            flags["qtc"] = "borderline"
        else:
            flags["qtc"] = "abnormal"

    if qrs_axis is not None:
        if -30 <= qrs_axis <= 90:
            flags["qrs_axis"] = "normal"
        elif -45 <= qrs_axis < -30 or 90 < qrs_axis <= 110:
            flags["qrs_axis"] = "borderline"
        else:
            flags["qrs_axis"] = "abnormal"

    if qt_disp is not None:
        if qt_disp < 50:
            flags["qt_dispersion"] = "normal"
        elif 50 <= qt_disp < 70:
            flags["qt_dispersion"] = "borderline"
        else:
            flags["qt_dispersion"] = "abnormal"

    if tpe_ms is not None:
        if tpe_ms < 85:
            flags["tpe_interval"] = "normal"
        elif 85 <= tpe_ms < 100:
            flags["tpe_interval"] = "borderline"
        else:
            flags["tpe_interval"] = "abnormal"

    if p_dur is not None:
        if p_dur <= 120:
            flags["p_duration"] = "normal"
        else:
            flags["p_duration"] = "abnormal"

    if p_amp is not None:
        if p_amp <= 0.25:
            flags["p_amplitude"] = "normal"
        else:
            flags["p_amplitude"] = "abnormal"

    return flags


# ---------------------------------------------------------------------------
# HRV
# ---------------------------------------------------------------------------

def _compute_hrv(ref_fpt: np.ndarray, fs: float) -> tuple[Optional[float], Optional[float]]:
    if len(ref_fpt) < 3:
        return None, None
    r_peaks = ref_fpt[:, COL_R]
    valid_r = r_peaks[r_peaks >= 0].astype(float)
    if len(valid_r) < 3:
        return None, None
    rr_ms = np.diff(valid_r) / fs * 1000
    sdnn = float(np.std(rr_ms))
    rmssd = float(np.sqrt(np.mean(np.diff(rr_ms) ** 2)))
    return sdnn, rmssd


# ---------------------------------------------------------------------------
# R progression
# ---------------------------------------------------------------------------

def _r_progression(r_amp: dict, leads: list[str]) -> str:
    prec = ["V1", "V2", "V3", "V4", "V5", "V6"]
    amps = [_get_mv(r_amp, l) for l in prec]
    amps = [a for a in amps if a is not None]
    if len(amps) < 4:
        return "indeterminate"
    # Normal: R grows from V1 to V4/V5
    if amps[0] < amps[1] < amps[2]:
        return "normal"
    # Poor: R doesn't grow by V4
    if len(amps) >= 4 and amps[3] < 0.3:
        return "poor"
    return "normal"


# ---------------------------------------------------------------------------
# Beat summary
# ---------------------------------------------------------------------------

def _build_beat_summary(
    ref_fpt: np.ndarray,
    fs: float,
    dominant_rhythm: str,
    rhythm_regular: bool,
) -> BeatSummary:
    if len(ref_fpt) == 0:
        return BeatSummary(
            n_beats=0, beat_class_counts={}, dominant_rhythm=dominant_rhythm,
            rhythm_regular=rhythm_regular, rr_intervals_ms=[], rr_mean_ms=0,
            rr_cv=0, beat_pattern=None, dropped_beat_context=None, per_beat_detail=None,
        )

    classes = ref_fpt[:, COL_CLASS]
    counts = {
        "normal": int(np.sum(classes == 0)),
        "pvc": int(np.sum(classes == 1)),
        "pac": int(np.sum(classes == 2)),
        "unknown": int(np.sum(classes == -1)),
    }

    r_peaks = ref_fpt[:, COL_R]
    valid_r = r_peaks[r_peaks >= 0].astype(float)
    rr_ms = list(np.diff(valid_r) / fs * 1000) if len(valid_r) >= 2 else []
    rr_mean = float(np.mean(rr_ms)) if rr_ms else 0
    rr_cv = float(np.std(rr_ms) / rr_mean) if rr_mean > 0 else 0

    beat_pattern = _detect_beat_pattern(list(classes))
    dropped_beat_context = _detect_dropped_beat(rr_ms, rr_mean)

    return BeatSummary(
        n_beats=len(ref_fpt),
        beat_class_counts=counts,
        dominant_rhythm=dominant_rhythm,
        rhythm_regular=rhythm_regular,
        rr_intervals_ms=rr_ms,
        rr_mean_ms=rr_mean,
        rr_cv=rr_cv,
        beat_pattern=beat_pattern,
        dropped_beat_context=dropped_beat_context,
        per_beat_detail=None,
    )


def _detect_beat_pattern(classes: list) -> Optional[str]:
    """Sliding window bigeminy/trigeminy detection (min 4 consecutive pairs)."""
    for pvc_class, label in ((1, "BIGEMINY_PVC"), (2, "BIGEMINY_PAC")):
        best_run = 0
        run = 0
        for i in range(len(classes) - 1):
            if classes[i] == 0 and classes[i + 1] == pvc_class:
                run += 1
                best_run = max(best_run, run)
            else:
                run = 0
        if best_run >= 4:
            return label

    # Trigeminy: normal normal pvc repeating
    for i in range(len(classes) - 8):
        window = classes[i:i + 9]
        if all(
            window[j] == 0 and window[j + 1] == 0 and window[j + 2] in (1, 2)
            for j in range(0, 9, 3)
        ):
            return "TRIGEMINY"

    return None


def _detect_dropped_beat(rr_ms: list, rr_mean: float) -> Optional[str]:
    """Detect a pause (RR > 2× mean) as a potential dropped beat."""
    if not rr_ms or rr_mean <= 0:
        return None
    for i, rr in enumerate(rr_ms):
        if rr > 2.0 * rr_mean:
            return f"Pause at beat interval {i + 1}: RR = {rr:.0f} ms (> 2× mean {rr_mean:.0f} ms)"
    return None


# ---------------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------------

def _ref_lead(fpt: dict, leads: list[str]) -> str:
    for candidate in ["II", "V1", "aVF"]:
        if candidate in fpt and len(fpt[candidate]) > 0:
            return candidate
    for lead in leads:
        if lead in fpt and len(fpt[lead]) > 0:
            return lead
    return leads[0] if leads else "II"


def _quality_cap(quality: QualityReport, lead: str) -> float:
    lq = quality.lead_quality.get(lead)
    if lq is None:
        return 0.5
    return {"GOOD": 1.0, "ACCEPTABLE": 0.75, "POOR": 0.40, "UNUSABLE": 0.0}[lq.quality]


def _fill_none_dicts(lead: str, *dicts) -> None:
    for i, d in enumerate(dicts):
        if i in (4,):  # sym_t_inv is bool
            d[lead] = False
        elif i in (6,):  # fqrs is bool
            d[lead] = False
        else:
            d[lead] = None
