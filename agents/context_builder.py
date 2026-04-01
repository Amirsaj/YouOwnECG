"""
Context assembly for agent prompts.

Builds the user-prompt context block from FeatureObject + VisionVerificationResult.
Keeps token budget tight: BeatSummary (~600 tokens) + selected feature values.
The full FeatureObject is NOT forwarded — only the fields relevant to each agent.
"""

from __future__ import annotations
from typing import Optional
from pipeline.schemas import FeatureObject, VisionVerificationResult
from agents.deepseek import serialize_for_prompt, _strip_phi


def build_rrc_context(features: FeatureObject, vision: VisionVerificationResult) -> str:
    """Build context block for the RRC agent."""
    bs = features.beat_summary
    ctx = {
        "beat_summary": {
            "n_beats": bs.n_beats,
            "beat_class_counts": bs.beat_class_counts,
            "dominant_rhythm": bs.dominant_rhythm,
            "rhythm_regular": bs.rhythm_regular,
            "rr_mean_ms": round(bs.rr_mean_ms, 1) if bs.rr_mean_ms else None,
            "rr_cv": round(bs.rr_cv, 4) if bs.rr_cv else None,
            "rr_intervals_ms": [round(v, 1) for v in bs.rr_intervals_ms] if bs.rr_intervals_ms else [],
            "beat_pattern": bs.beat_pattern,
            "dropped_beat_context": bs.dropped_beat_context,
            "per_beat_detail": bs.per_beat_detail,
        },
        "intervals": {
            "heart_rate_ventricular_bpm": features.heart_rate_ventricular_bpm,
            "heart_rate_atrial_bpm": features.heart_rate_atrial_bpm,
            "av_ratio": features.av_ratio,
            "pr_interval_ms": features.pr_interval_ms,
            "qrs_duration_global_ms": features.qrs_duration_global_ms,
            "qtc_bazett_ms": features.qtc_bazett_ms,
            "qtc_fridericia_ms": features.qtc_fridericia_ms,
        },
        "conduction": {
            "lbbb": features.lbbb,
            "rbbb": features.rbbb,
            "lafb": features.lafb,
            "lpfb": features.lpfb,
            "wpw_pattern": features.wpw_pattern,
            "electrical_alternans": features.electrical_alternans,
        },
        "p_wave": {
            "p_wave_present": features.p_wave_present,
            "p_duration_ms": features.p_duration_ms,
            "p_amplitude_mv": features.p_amplitude_mv,
        },
    }
    return serialize_for_prompt(_strip_phi(ctx))


def build_it_context(features: FeatureObject, vision: VisionVerificationResult) -> str:
    """Build context block for the IT (Ischemia/Territory) agent."""
    ctx = {
        "st_elevation_mv": {k: v for k, v in features.st_elevation_mv.items() if v is not None},
        "st_depression_mv": {k: v for k, v in features.st_depression_mv.items() if v is not None},
        "st_morphology": {k: v for k, v in features.st_morphology.items() if v is not None},
        "j_point_mv": {k: v for k, v in features.j_point_mv.items() if v is not None},
        "t_amplitude_mv": {k: v for k, v in features.t_amplitude_mv.items() if v is not None},
        "t_morphology": {k: v for k, v in features.t_morphology.items() if v is not None},
        "t_qrs_ratio": {k: v for k, v in features.t_qrs_ratio.items() if v is not None},
        "symmetric_t_inversion": {k: v for k, v in features.symmetric_t_inversion.items() if v},
        "hyperacute_t_pattern": features.hyperacute_t_pattern,
        "de_winter_pattern": features.de_winter_pattern,
        "early_repolarization_pattern": features.early_repolarization_pattern,
        "lead_quality_cap": features.lead_quality_cap,
        "lbbb": features.lbbb,  # IT needs to know about LBBB for Sgarbossa
        "vision_st_elevation_leads": vision.st_elevation_leads if vision.available else [],
        "vision_conflicts": [
            {"lead": c.lead, "type": c.conflict_type, "signal": c.signal_value, "vision": c.vision_value}
            for c in vision.signal_vision_conflicts
        ],
    }
    return serialize_for_prompt(ctx)


def build_mr_context(features: FeatureObject, vision: VisionVerificationResult) -> str:
    """Build context block for the MR (Morphology/Repolarization) agent."""
    ctx = {
        "p_wave": {
            "p_duration_ms": features.p_duration_ms,
            "p_amplitude_mv": features.p_amplitude_mv,
            "p_terminal_force_v1_mv_s": features.p_terminal_force_v1_mv_s,
            "p_wave_present": features.p_wave_present,
            "p_morphology_notes": features.p_morphology_notes,
        },
        "qrs_morphology": {
            "qrs_duration_global_ms": features.qrs_duration_global_ms,
            "qrs_axis_deg": features.qrs_axis_deg,
            "r_amplitude_mv": {k: v for k, v in features.r_amplitude_mv.items() if v is not None},
            "s_amplitude_mv": {k: v for k, v in features.s_amplitude_mv.items() if v is not None},
            "q_duration_ms": {k: v for k, v in features.q_duration_ms.items() if v is not None},
            "q_amplitude_mv": {k: v for k, v in features.q_amplitude_mv.items() if v is not None},
            "qrs_fragmented": {k: v for k, v in features.qrs_fragmented.items() if v},
            "r_progression": features.r_progression,
            "intrinsicoid_deflection_ms": {k: v for k, v in features.intrinsicoid_deflection_ms.items() if v is not None},
        },
        "lvh_rvh": {
            "lvh_sokolow_lyon_mv": features.lvh_sokolow_lyon_mv,
            "lvh_cornell_mv": features.lvh_cornell_mv,
            "lvh_cornell_product_mv_ms": features.lvh_cornell_product_mv_ms,
            "lvh_romhilt_estes_score": features.lvh_romhilt_estes_score,
            "lvh_lewis_index_mv": features.lvh_lewis_index_mv,
            "lvh_criteria_met": features.lvh_criteria_met,
            "rvh_criteria_met": features.rvh_criteria_met,
            "low_voltage_limb": features.low_voltage_limb,
            "low_voltage_precordial": features.low_voltage_precordial,
        },
        "repolarization": {
            "qtc_bazett_ms": features.qtc_bazett_ms,
            "qtc_fridericia_ms": features.qtc_fridericia_ms,
            "qtc_framingham_ms": features.qtc_framingham_ms,
            "qtc_hodges_ms": features.qtc_hodges_ms,
            "t_amplitude_mv": {k: v for k, v in features.t_amplitude_mv.items() if v is not None},
            "t_morphology": {k: v for k, v in features.t_morphology.items() if v is not None},
            "symmetric_t_inversion": {k: v for k, v in features.symmetric_t_inversion.items() if v},
            "u_wave_prominent": features.u_wave_prominent,
            "osborn_wave": features.osborn_wave,
        },
        "special_patterns": {
            "brugada_type1_pattern": features.brugada_type1_pattern,
            "brugada_type2or3_pattern": features.brugada_type2or3_pattern,
            "pericarditis_pattern": features.pericarditis_pattern,
            "epsilon_wave_suspected": features.epsilon_wave_suspected,
        },
    }
    return serialize_for_prompt(ctx)


def build_cds_context(
    features: FeatureObject,
    vision: VisionVerificationResult,
    rrc_output: dict,
    it_output: dict,
    mr_output: dict,
) -> str:
    """Build context block for the CDS agent (receives Phase 1 outputs)."""
    measurements = {
        "heart_rate_ventricular_bpm": features.heart_rate_ventricular_bpm,
        "pr_interval_ms": features.pr_interval_ms,
        "qrs_duration_global_ms": features.qrs_duration_global_ms,
        "qtc_bazett_ms": features.qtc_bazett_ms,
        "qtc_fridericia_ms": features.qtc_fridericia_ms,
        "qrs_axis_deg": features.qrs_axis_deg,
        "p_axis_deg": features.p_axis_deg,
        "beat_summary": {
            "n_beats": features.beat_summary.n_beats,
            "beat_class_counts": features.beat_summary.beat_class_counts,
            "dominant_rhythm": features.beat_summary.dominant_rhythm,
            "beat_pattern": features.beat_summary.beat_pattern,
        },
    }

    ctx = {
        "measurements": measurements,
        "overall_quality": features.lead_quality_cap,
        "phase1_outputs": {
            "RRC": {
                "findings": rrc_output.get("findings", []),
                "no_significant_findings": rrc_output.get("no_significant_findings", False),
            },
            "IT": {
                "findings": it_output.get("findings", []),
                "no_significant_findings": it_output.get("no_significant_findings", False),
            },
            "MR": {
                "findings": mr_output.get("findings", []),
                "t_wave_raw": mr_output.get("t_wave_raw", {}),
                "no_significant_findings": mr_output.get("no_significant_findings", False),
            },
        },
        "vision_available": vision.available,
        "vision_conflicts": len(vision.signal_vision_conflicts),
    }
    return serialize_for_prompt(ctx)


def build_measurements_block(features: FeatureObject) -> dict:
    """
    Build the deterministic measurements block for the DiagnosticResult.
    These values come from signal computation only — never from LLM.
    """
    return {
        "heart_rate_ventricular_bpm": features.heart_rate_ventricular_bpm,
        "heart_rate_atrial_bpm": features.heart_rate_atrial_bpm,
        "pr_interval_ms": features.pr_interval_ms,
        "qrs_duration_global_ms": features.qrs_duration_global_ms,
        "qt_interval_ms": features.qt_interval_ms,
        "qtc_bazett_ms": features.qtc_bazett_ms,
        "qtc_fridericia_ms": features.qtc_fridericia_ms,
        "qtc_framingham_ms": features.qtc_framingham_ms,
        "qtc_hodges_ms": features.qtc_hodges_ms,
        "qrs_axis_deg": features.qrs_axis_deg,
        "p_axis_deg": features.p_axis_deg,
        "t_axis_deg": features.t_axis_deg,
        "rhythm": features.dominant_rhythm,
        "rhythm_regular": features.rhythm_regular,
        "n_beats": features.beat_summary.n_beats,
        "beat_class_counts": features.beat_summary.beat_class_counts,
        "lbbb": features.lbbb,
        "rbbb": features.rbbb,
        "lvh_criteria_met": features.lvh_criteria_met,
    }
