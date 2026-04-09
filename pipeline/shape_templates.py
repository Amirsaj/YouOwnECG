"""
ECG Morphology Shape Template Database.

Defines the "alphabet" of 41 ECG waveform shapes across 4 segment types.
Each shape has scale-invariant geometric feature bounds and a reference
waveform for template matching.

Shape codes:
  P1-P7   : P-wave shapes (7)
  Q1-Q12  : QRS shapes (12)
  ST1-ST8 : ST segment shapes (8)
  T1-T14  : T-wave shapes (14)
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
import numpy as np


@dataclass
class ShapeTemplate:
    code: str                          # "T3"
    name: str                          # "Peaked Tented"
    segment: str                       # "P" | "QRS" | "ST" | "T"
    clinical_name: str                 # "Hyperkalemia peaked T"

    # Scale-invariant feature acceptance ranges (min, max)
    symmetry_range: tuple = (0.0, 1.0)
    base_width_ratio_range: tuple = (0.0, 1.0)
    peak_sharpness_range: tuple = (0.0, float('inf'))
    n_peaks: tuple = (1, 1)            # (min, max) number of peaks
    polarity: str = "any"              # "positive" | "negative" | "any" | "biphasic"
    curvature_range: tuple = (-float('inf'), float('inf'))
    slope_ratio_range: tuple = (0.0, 1.0)  # for QRS delta wave

    # J-point context: where the segment STARTS relative to baseline
    # "above" = J-point above baseline (after tall R)
    # "below" = J-point below baseline (after deep S)
    # "any" = doesn't matter
    j_point_position: str = "any"      # "above" | "below" | "any"

    # Lead-specific behavior: some shapes look different in certain leads
    # e.g., de Winter shows ST elevation in aVR but depression in V1-V6
    lead_context: dict = field(default_factory=dict)
    # Example: {"aVR": "reciprocal_elevation", "V1-V6": "depression"}

    # Diseases this shape is associated with
    associated_conditions: list = field(default_factory=list)

    # Shapes easily confused with this one
    confusable_with: list = field(default_factory=list)
    distinguishing_feature: str = ""

    # 64-sample normalized reference waveform (populated during curation)
    template: Optional[np.ndarray] = None

    # Curated examples (list of dicts with ecg_id, lead, beat_idx, features)
    examples: list = field(default_factory=list)


# ── P-WAVE SHAPES ─────────────────────────────────────────────────────────

P_SHAPES = [
    ShapeTemplate(
        code="P1", name="Normal Upright", segment="P",
        clinical_name="Normal sinus P-wave",
        symmetry_range=(0.3, 0.8),
        base_width_ratio_range=(0.3, 0.7),
        peak_sharpness_range=(0.0, 2.0),
        n_peaks=(1, 1),
        polarity="positive",
        associated_conditions=["normal_sinus_rhythm"],
        confusable_with=["P2"],
        distinguishing_feature="amplitude < 0.25mV, duration 80-120ms",
    ),
    ShapeTemplate(
        code="P2", name="P-Pulmonale (Peaked)", segment="P",
        clinical_name="Right atrial enlargement peaked P",
        symmetry_range=(0.5, 1.0),
        base_width_ratio_range=(0.2, 0.5),
        peak_sharpness_range=(1.5, float('inf')),
        n_peaks=(1, 1),
        polarity="positive",
        associated_conditions=["rae", "cor_pulmonale", "copd"],
        confusable_with=["P1"],
        distinguishing_feature="amplitude > 0.25mV, narrow base, sharp apex",
    ),
    ShapeTemplate(
        code="P3", name="P-Mitrale (Notched)", segment="P",
        clinical_name="Left atrial enlargement bifid P",
        symmetry_range=(0.3, 0.8),
        base_width_ratio_range=(0.5, 0.9),
        peak_sharpness_range=(0.0, 1.5),
        n_peaks=(2, 2),
        polarity="positive",
        associated_conditions=["lae", "mitral_stenosis"],
        confusable_with=["P1"],
        distinguishing_feature="two peaks (M-shaped), duration > 120ms, notch > 30µV",
    ),
    ShapeTemplate(
        code="P4", name="Inverted", segment="P",
        clinical_name="Inverted P-wave",
        symmetry_range=(0.2, 1.0),
        n_peaks=(1, 1),
        polarity="negative",
        associated_conditions=["ectopic_atrial", "junctional_rhythm"],
        confusable_with=["P6"],
        distinguishing_feature="single negative peak > 0.05mV",
    ),
    ShapeTemplate(
        code="P5", name="Biphasic (Terminal Negative)", segment="P",
        clinical_name="Biphasic P with terminal negative force",
        polarity="biphasic",
        n_peaks=(2, 2),
        associated_conditions=["lae"],
        confusable_with=["P3"],
        distinguishing_feature="initial positive + terminal negative, V1 specific",
    ),
    ShapeTemplate(
        code="P6", name="Flat/Absent", segment="P",
        clinical_name="Absent or flat P-wave",
        peak_sharpness_range=(0.0, 0.3),
        polarity="any",
        associated_conditions=["afib", "hyperkalemia_severe", "junctional"],
        confusable_with=["P4"],
        distinguishing_feature="amplitude < 0.05mV across full window",
    ),
    ShapeTemplate(
        code="P7", name="Buried in T", segment="P",
        clinical_name="P-wave hidden in preceding T-wave",
        polarity="any",
        associated_conditions=["svt", "atrial_flutter", "atrial_tachycardia"],
        confusable_with=["P6"],
        distinguishing_feature="T-wave asymmetry from hidden P superposition",
    ),
]


# ── QRS SHAPES ────────────────────────────────────────────────────────────

QRS_SHAPES = [
    ShapeTemplate(
        code="Q1", name="qRs (Normal)", segment="QRS",
        clinical_name="Normal septal q + dominant R + small s",
        polarity="positive",
        n_peaks=(2, 3),
        associated_conditions=["normal"],
        distinguishing_feature="small q (<40ms, <25% R), dominant R, small s",
    ),
    ShapeTemplate(
        code="Q2", name="Rs (Normal Variant)", segment="QRS",
        clinical_name="Dominant R with small s, no q",
        polarity="positive",
        n_peaks=(1, 2),
        associated_conditions=["normal"],
        distinguishing_feature="R dominant, no initial q-wave",
    ),
    ShapeTemplate(
        code="Q3", name="rS", segment="QRS",
        clinical_name="Small r with dominant S",
        polarity="negative",
        n_peaks=(1, 2),
        associated_conditions=["normal_v1v2", "lbbb"],
        confusable_with=["Q4"],
        distinguishing_feature="small initial positive r, deep S dominant",
    ),
    ShapeTemplate(
        code="Q4", name="QS (Pathological)", segment="QRS",
        clinical_name="Entirely negative QRS — no R-wave",
        polarity="negative",
        n_peaks=(1, 1),
        associated_conditions=["old_mi_transmural", "lbbb_v1"],
        confusable_with=["Q3"],
        distinguishing_feature="NO positive deflection at all",
    ),
    ShapeTemplate(
        code="Q5", name="RSR' (RBBB)", segment="QRS",
        clinical_name="M-shaped QRS — RBBB pattern",
        polarity="positive",
        n_peaks=(2, 3),
        associated_conditions=["rbbb", "brugada"],
        confusable_with=["Q6"],
        distinguishing_feature="two positive peaks (R + R') with S valley between, V1-V2",
    ),
    ShapeTemplate(
        code="Q6", name="Monophasic R (LBBB)", segment="QRS",
        clinical_name="Broad single R — LBBB lateral pattern",
        polarity="positive",
        n_peaks=(1, 2),
        base_width_ratio_range=(0.6, 1.0),
        associated_conditions=["lbbb"],
        confusable_with=["Q5"],
        distinguishing_feature="single broad positive, no S, often notched at peak, V5-V6",
    ),
    ShapeTemplate(
        code="Q7", name="Delta Wave (WPW)", segment="QRS",
        clinical_name="Slurred initial upstroke — pre-excitation",
        slope_ratio_range=(0.0, 0.10),
        associated_conditions=["wpw_pattern"],
        confusable_with=["Q1"],
        distinguishing_feature="initial 20ms slope < 10% of max slope, QRS > 110ms",
    ),
    ShapeTemplate(
        code="Q8", name="Fragmented QRS", segment="QRS",
        clinical_name="Multiple deflections within QRS",
        n_peaks=(8, 20),
        associated_conditions=["prior_mi_scar", "cardiomyopathy"],
        distinguishing_feature="> 8 amplitude-gated peaks within QRS envelope",
    ),
    ShapeTemplate(
        code="Q9", name="Pathological Q", segment="QRS",
        clinical_name="Deep/wide initial negative deflection",
        polarity="negative",
        associated_conditions=["old_mi", "septal_infarction"],
        distinguishing_feature="q duration >= 40ms OR q amplitude >= 25% of R",
    ),
    ShapeTemplate(
        code="Q10", name="Wide QRS (Non-specific)", segment="QRS",
        clinical_name="Diffuse QRS widening without BBB morphology",
        base_width_ratio_range=(0.7, 1.0),
        associated_conditions=["hyperkalemia", "drug_toxicity"],
        confusable_with=["Q5", "Q6"],
        distinguishing_feature="QRS >= 120ms, no RSR' and no monophasic R",
    ),
    ShapeTemplate(
        code="Q11", name="Low Voltage", segment="QRS",
        clinical_name="Low amplitude QRS complex",
        peak_sharpness_range=(0.0, 0.5),
        associated_conditions=["pericardial_effusion", "obesity", "copd"],
        distinguishing_feature="limb < 0.5mV, precordial < 1.0mV",
    ),
    ShapeTemplate(
        code="Q12", name="Epsilon Wave", segment="QRS",
        clinical_name="Small terminal deflection after QRS — ARVC",
        associated_conditions=["arvc"],
        distinguishing_feature="small positive notch after J-point, before T-onset, V1-V3",
    ),
]


# ── ST SEGMENT SHAPES ─────────────────────────────────────────────────────

ST_SHAPES = [
    ShapeTemplate(
        code="ST1", name="Isoelectric", segment="ST",
        clinical_name="Normal isoelectric ST segment",
        curvature_range=(-0.3, 0.3),
        associated_conditions=["normal"],
        distinguishing_feature="|elevation| < 0.1mV, flat/linear",
    ),
    ShapeTemplate(
        code="ST2", name="Concave-Up Elevation (Smiley)", segment="ST",
        clinical_name="Upward concavity — early repolarization/pericarditis",
        curvature_range=(0.3, float('inf')),
        polarity="positive",
        associated_conditions=["early_repolarization", "pericarditis"],
        confusable_with=["ST3"],
        distinguishing_feature="positive curvature (smiley), ST > 0.1mV",
    ),
    ShapeTemplate(
        code="ST3", name="Convex Elevation (Frowning)", segment="ST",
        clinical_name="Downward convexity — acute STEMI",
        curvature_range=(-float('inf'), -0.3),
        polarity="positive",
        associated_conditions=["stemi"],
        confusable_with=["ST2", "ST4"],
        distinguishing_feature="negative curvature (frowning/tombstone), ST > 0.1mV",
    ),
    ShapeTemplate(
        code="ST4", name="Coved (Brugada)", segment="ST",
        clinical_name="Convex dome with descending slope — Brugada Type 1",
        curvature_range=(-float('inf'), -0.3),
        associated_conditions=["brugada_type1"],
        confusable_with=["ST3"],
        distinguishing_feature="convex dome + monotonic descent + inverted T, V1-V2, ST-T continuous",
    ),
    ShapeTemplate(
        code="ST5", name="Horizontal Depression", segment="ST",
        clinical_name="Flat ST depression — demand ischemia",
        curvature_range=(-0.3, 0.3),
        polarity="negative",
        associated_conditions=["demand_ischemia", "nstemi"],
        confusable_with=["ST6"],
        distinguishing_feature="flat below baseline > 0.1mV, near-zero slope",
    ),
    ShapeTemplate(
        code="ST6", name="Downsloping Depression", segment="ST",
        clinical_name="Descending ST depression — LVH strain",
        curvature_range=(-float('inf'), 0.0),
        polarity="negative",
        associated_conditions=["lvh_strain", "digitalis_effect"],
        confusable_with=["ST5"],
        distinguishing_feature="negative slope throughout, depression > 0.1mV",
    ),
    ShapeTemplate(
        code="ST7", name="Upsloping Depression (de Winter)", segment="ST",
        clinical_name="J-point depressed with upsloping ST — de Winter",
        polarity="negative",
        associated_conditions=["de_winter"],
        confusable_with=["ST5"],
        distinguishing_feature="J-point depressed > 0.1mV, positive slope into tall T",
    ),
    ShapeTemplate(
        code="ST8", name="Scooped Depression (Digitalis)", segment="ST",
        clinical_name="Reverse checkmark — digitalis effect",
        curvature_range=(-float('inf'), -0.2),
        polarity="negative",
        associated_conditions=["digitalis_effect"],
        confusable_with=["ST6"],
        distinguishing_feature="concave-down scooped shape into inverted T",
    ),
]


# ── T-WAVE SHAPES ─────────────────────────────────────────────────────────

T_SHAPES = [
    ShapeTemplate(
        code="T1", name="Normal Upright", segment="T",
        clinical_name="Normal asymmetric upright T-wave",
        symmetry_range=(0.3, 0.65),
        base_width_ratio_range=(0.4, 0.7),
        peak_sharpness_range=(0.0, 1.5),
        n_peaks=(1, 1),
        polarity="positive",
        associated_conditions=["normal"],
        confusable_with=["T2"],
        distinguishing_feature="asymmetric (slow rise, quick fall), moderate amplitude",
    ),
    ShapeTemplate(
        code="T2", name="Hyperacute (STEMI)", segment="T",
        clinical_name="Tall broad symmetric T — early STEMI",
        symmetry_range=(0.65, 1.0),
        base_width_ratio_range=(0.5, 0.9),
        peak_sharpness_range=(0.0, 1.5),
        n_peaks=(1, 1),
        polarity="positive",
        associated_conditions=["stemi_early", "de_winter"],
        confusable_with=["T3", "T1"],
        distinguishing_feature="BROAD base (BWR > 0.5), symmetric, tall, T/QRS > 0.75",
    ),
    ShapeTemplate(
        code="T3", name="Peaked Tented (Hyperkalemia)", segment="T",
        clinical_name="Narrow-based peaked tented T-wave",
        symmetry_range=(0.6, 1.0),
        base_width_ratio_range=(0.0, 0.4),
        peak_sharpness_range=(1.5, float('inf')),
        n_peaks=(1, 1),
        polarity="positive",
        associated_conditions=["hyperkalemia"],
        confusable_with=["T2"],
        distinguishing_feature="NARROW base (BWR < 0.4), SHARP apex (high curvature)",
    ),
    ShapeTemplate(
        code="T4", name="Deep Symmetric Inversion", segment="T",
        clinical_name="Deep symmetric T-wave inversion — Wellens B / ischemia",
        symmetry_range=(0.65, 1.0),
        n_peaks=(1, 1),
        polarity="negative",
        associated_conditions=["wellens_type_b", "nstemi", "post_stemi"],
        confusable_with=["T5"],
        distinguishing_feature="symmetric limbs (sym > 0.65), inverted > 0.2mV",
    ),
    ShapeTemplate(
        code="T5", name="Asymmetric Inversion (Strain)", segment="T",
        clinical_name="Asymmetric T inversion — LVH/RVH strain",
        symmetry_range=(0.0, 0.5),
        n_peaks=(1, 1),
        polarity="negative",
        associated_conditions=["lvh_strain", "rvh_strain"],
        confusable_with=["T4"],
        distinguishing_feature="asymmetric (sym < 0.5): slow descent + rapid return",
    ),
    ShapeTemplate(
        code="T6", name="Biphasic Wellens A (Pos-Neg)", segment="T",
        clinical_name="Biphasic positive-then-negative — Wellens Type A",
        polarity="biphasic",
        n_peaks=(1, 2),
        associated_conditions=["wellens_type_a"],
        confusable_with=["T7"],
        distinguishing_feature="initial positive > 50µV, terminal negative > 50µV, V2-V3",
    ),
    ShapeTemplate(
        code="T7", name="Biphasic Neg-Pos", segment="T",
        clinical_name="Biphasic negative-then-positive T-wave",
        polarity="biphasic",
        n_peaks=(1, 2),
        confusable_with=["T6"],
        distinguishing_feature="initial negative, terminal positive",
    ),
    ShapeTemplate(
        code="T8", name="Notched/Bifid (LQT2)", segment="T",
        clinical_name="Double-peaked T-wave — LQT2",
        n_peaks=(2, 2),
        polarity="positive",
        associated_conditions=["long_qt_type2"],
        confusable_with=["T1"],
        distinguishing_feature="two peaks same polarity, notch depth > 50µV between",
    ),
    ShapeTemplate(
        code="T9", name="Flat", segment="T",
        clinical_name="Flat/isoelectric T-wave",
        peak_sharpness_range=(0.0, 0.3),
        polarity="any",
        associated_conditions=["ischemia_early", "hypokalemia", "hypothyroidism"],
        confusable_with=["P6"],
        distinguishing_feature="|amplitude| < 0.05mV",
    ),
    ShapeTemplate(
        code="T10", name="Giant Inversion (HCM)", segment="T",
        clinical_name="Giant symmetric T inversion — apical HCM",
        symmetry_range=(0.6, 1.0),
        polarity="negative",
        associated_conditions=["apical_hcm"],
        confusable_with=["T4"],
        distinguishing_feature="depth > 1.0mV, widespread V2-V5 non-territorial",
    ),
    ShapeTemplate(
        code="T11", name="T-wave Alternans", segment="T",
        clinical_name="Beat-to-beat T morphology alternation — TdP precursor",
        associated_conditions=["long_qt_tdp_imminent"],
        distinguishing_feature="alternating amplitude or polarity between consecutive beats",
    ),
    ShapeTemplate(
        code="T12", name="Juvenile Pattern", segment="T",
        clinical_name="Age-appropriate T inversion V1-V3",
        polarity="negative",
        associated_conditions=["normal_juvenile"],
        confusable_with=["T4"],
        distinguishing_feature="inverted V1-V3, age < 25, no territorial pattern",
    ),
    ShapeTemplate(
        code="T13", name="De Winter T", segment="T",
        clinical_name="Tall symmetric T with upsloping ST depression",
        symmetry_range=(0.65, 1.0),
        polarity="positive",
        associated_conditions=["de_winter"],
        confusable_with=["T2"],
        distinguishing_feature="tall symmetric peaked BUT with J-point ST depression > 0.1mV",
    ),
    ShapeTemplate(
        code="T14", name="Concordant/Discordant (BBB)", segment="T",
        clinical_name="T direction relative to terminal QRS in BBB",
        associated_conditions=["lbbb_secondary", "rbbb_secondary", "sgarbossa"],
        distinguishing_feature="concordant (same as terminal QRS) = concerning; discordant = expected",
    ),
]


# ── Complete alphabet ──────────────────────────────────────────────────────

ALL_SHAPES = P_SHAPES + QRS_SHAPES + ST_SHAPES + T_SHAPES

SHAPE_BY_CODE = {s.code: s for s in ALL_SHAPES}
SHAPES_BY_SEGMENT = {
    "P":   P_SHAPES,
    "QRS": QRS_SHAPES,
    "ST":  ST_SHAPES,
    "T":   T_SHAPES,
}


def get_shape(code: str) -> ShapeTemplate:
    """Look up a shape by its code (e.g., 'T3')."""
    return SHAPE_BY_CODE[code]


def get_shapes_for_segment(segment: str) -> list[ShapeTemplate]:
    """Get all shape templates for a segment type."""
    return SHAPES_BY_SEGMENT.get(segment, [])


# ── COMPOSITE SHAPES (multi-segment patterns) ─────────────────────────────

@dataclass
class CompositePattern:
    code: str                     # "C1"
    name: str                     # "de Winter"
    clinical_name: str
    segments_involved: list       # ["ST", "T"]

    # Required individual shape codes (any of these combinations)
    required_shapes: dict = field(default_factory=dict)

    # Lead territory requirements: which territory must this composite appear in?
    # None = any territory. "anterior" = must be in V1-V4 leads.
    required_territory: Optional[str] = None  # "septal" | "anterior" | "lateral" | "inferior" | None

    # Reciprocal pattern: what should the OPPOSITE territory show?
    reciprocal_shapes: dict = field(default_factory=dict)  # {"ST": ["ST2","ST3"]} for reciprocal leads

    # Additional geometric criteria across segments
    cross_segment_criteria: str = ""

    associated_conditions: list = field(default_factory=list)
    confusable_with: list = field(default_factory=list)
    distinguishing_feature: str = ""


COMPOSITE_PATTERNS = [
    CompositePattern(
        code="C1", name="de Winter", segments_involved=["ST", "T"],
        clinical_name="de Winter ST-T pattern — upsloping ST depression + tall symmetric peaked T (STEMI equivalent, proximal LAD)",
        required_shapes={"ST": ["ST7"], "T": ["T2", "T3", "T13"]},
        required_territory=None,  # must appear in septal/anterior (V1-V4), checked manually
        reciprocal_shapes={"ST": ["ST2", "ST3"]},  # aVR shows ST elevation (reciprocal)
        cross_segment_criteria=(
            "Must appear in V1-V4 (septal/anterior territory). "
            "ST is upsloping depression (>0.1mV at J-point) AND T is tall symmetric peaked. "
            "aVR must show reciprocal ST elevation. "
            "The ST-T complex is ONE continuous pattern. "
            "STATIC pattern — does NOT evolve through STEMI stages."
        ),
        associated_conditions=["de_winter", "stemi_equivalent"],
        confusable_with=["hyperkalemia"],
        distinguishing_feature=(
            "de Winter: upsloping ST depression + tall T in V1-V4 + aVR ST elevation. "
            "Hyperkalemia: peaked T WITHOUT ST depression, diffuse (all territories). "
            "de Winter is STATIC; STEMI evolves."
        ),
    ),
    CompositePattern(
        code="C2", name="Brugada Type 1", segments_involved=["ST", "T"],
        clinical_name="Brugada Type 1 — coved ST continuous into T inversion, V1-V2 ONLY",
        required_shapes={"ST": ["ST4"], "T": ["T4", "T5"]},
        required_territory="septal",  # V1-V2 only
        cross_segment_criteria=(
            "MUST appear in V1 and/or V2 ONLY (not V3-V6). "
            "Coved ST dome flows continuously into inverted T with NO isoelectric gap. "
            "V4-V6 should be normal. "
            "QRS may show pseudo-RBBB (rSR' in V1) but NOT true RBBB."
        ),
        associated_conditions=["brugada_type1"],
        confusable_with=["rbbb_secondary"],
        distinguishing_feature="Coved dome + continuous ST-T in V1-V2 only. RBBB has RSR' + ST-T changes in V1-V3.",
    ),
    CompositePattern(
        code="C3", name="LVH Strain", segments_involved=["ST", "T"],
        clinical_name="LVH strain — downsloping ST into asymmetric T inversion, LATERAL leads",
        required_shapes={"ST": ["ST6"], "T": ["T5"]},
        required_territory="lateral",  # I, aVL, V5, V6
        reciprocal_shapes={"ST": ["ST2"]},  # V1-V2 may show reciprocal ST elevation
        cross_segment_criteria=(
            "Must appear in LATERAL leads (I, aVL, V5, V6). "
            "ST downsloping depression flows into asymmetric T inversion (slow down, fast up). "
            "V1-V2 may show reciprocal tall R waves + ST elevation. "
            "Requires voltage criteria for LVH (Sokolow-Lyon or Cornell)."
        ),
        associated_conditions=["lvh_strain"],
        confusable_with=["nstemi"],
        distinguishing_feature="Asymmetric T (sym < 0.5) + LATERAL leads + voltage criteria = strain. Symmetric T (sym > 0.7) = ischemia.",
    ),
    CompositePattern(
        code="C4", name="Digitalis Effect", segments_involved=["ST", "T"],
        clinical_name="Digitalis effect — scooped ST into flat/inverted T",
        required_shapes={"ST": ["ST8"], "T": ["T5", "T9"]},
        required_territory=None,  # can appear in any territory
        cross_segment_criteria="Reverse-checkmark (Salvador Dali mustache). Can appear in any leads but most prominent in lateral leads with tall R-waves.",
        associated_conditions=["digitalis_effect"],
        distinguishing_feature="Scooped ST morphology unique to digoxin. Not territorial like ischemia.",
    ),
    CompositePattern(
        code="C5", name="Sgarbossa Concordant", segments_involved=["QRS", "ST"],
        clinical_name="Sgarbossa concordant ST in BBB — STEMI in LBBB",
        required_shapes={"QRS": ["Q3", "Q4", "Q6"], "ST": ["ST2", "ST3"]},
        required_territory=None,  # can be any territory
        cross_segment_criteria=(
            "ST elevation CONCORDANT with terminal QRS (same direction). "
            "In LBBB V1-V3: terminal QRS is negative, so concordant ST elevation = pathological. "
            "In LBBB V5-V6: terminal QRS is positive, so concordant ST depression would be pathological. "
            "DISCORDANT ST changes are expected secondary BBB changes — NOT this pattern."
        ),
        associated_conditions=["sgarbossa_stemi", "stemi_in_lbbb"],
        confusable_with=["lbbb_secondary"],
        distinguishing_feature="Concordant = acute MI. Discordant = expected. Smith ratio ≥0.25 also diagnostic.",
    ),
    CompositePattern(
        code="C6", name="Anterior STEMI", segments_involved=["ST", "T"],
        clinical_name="Anterior STEMI — convex ST elevation + hyperacute T, V1-V4 with inferior reciprocal",
        required_shapes={"ST": ["ST3"], "T": ["T2"]},
        required_territory="anterior",  # V1-V4
        reciprocal_shapes={"ST": ["ST5", "ST6"]},  # inferior leads show ST depression
        cross_segment_criteria=(
            "Convex (frowning) ST elevation in V1-V4 + broad symmetric hyperacute T. "
            "MUST have reciprocal ST depression in II, III, aVF. "
            "Absence of reciprocal changes → consider pericarditis or benign variant. "
            "Evolves: hyperacute T → ST elevation → T inversion → Q-waves."
        ),
        associated_conditions=["stemi_anterior"],
        confusable_with=["early_repolarization", "pericarditis"],
        distinguishing_feature="Convex ST + territorial + reciprocal changes = STEMI. Concave + diffuse + no reciprocal = pericarditis.",
    ),
    CompositePattern(
        code="C7", name="Inferior STEMI", segments_involved=["ST", "T"],
        clinical_name="Inferior STEMI — ST elevation II/III/aVF with lateral reciprocal depression",
        required_shapes={"ST": ["ST2", "ST3"], "T": ["T1", "T2"]},
        required_territory="inferior",  # II, III, aVF
        reciprocal_shapes={"ST": ["ST5", "ST6"]},  # I, aVL show reciprocal depression
        cross_segment_criteria=(
            "ST elevation in II, III, aVF. "
            "MUST have reciprocal ST depression in I and especially aVL (most sensitive). "
            "III > II suggests RCA. II ≥ III suggests LCx. "
            "Check V1 for ST elevation (RV involvement) and V4R if available."
        ),
        associated_conditions=["stemi_inferior"],
        confusable_with=["early_repolarization"],
        distinguishing_feature="Territorial inferior + aVL reciprocal depression confirms STEMI.",
    ),
    CompositePattern(
        code="C8", name="Pericarditis", segments_involved=["ST", "T"],
        clinical_name="Pericarditis — diffuse concave ST elevation + PR depression, aVR reciprocal",
        required_shapes={"ST": ["ST2"], "T": ["T1"]},
        required_territory=None,  # DIFFUSE — must appear in multiple territories
        reciprocal_shapes={"ST": ["ST5"]},  # aVR shows ST depression + PR elevation
        cross_segment_criteria=(
            "DIFFUSE concave-up (smiley) ST elevation in ≥5 leads across multiple territories. "
            "NOT territorial (not just anterior or just inferior). "
            "PR segment DEPRESSION in most leads (pathognomonic). "
            "aVR shows reciprocal ST depression + PR elevation. "
            "NO reciprocal ST depression in other leads (unlike STEMI)."
        ),
        associated_conditions=["pericarditis"],
        confusable_with=["stemi", "early_repolarization"],
        distinguishing_feature="Diffuse + concave + PR depression + aVR reciprocal + NO territorial reciprocal depression.",
    ),
]

COMPOSITE_BY_CODE = {p.code: p for p in COMPOSITE_PATTERNS}


def get_composite_patterns() -> list[CompositePattern]:
    return COMPOSITE_PATTERNS
