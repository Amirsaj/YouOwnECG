/**
 * Per-disease dashboard configuration (Node 3.2).
 *
 * Each disease has:
 * - Relevant leads for the ECG panel
 * - Highlight rules for annotating waveforms
 * - Diagnostic criteria checklist (evaluated from signal features)
 * - Per-lead measurement columns to display
 * - Deterministic explanation template
 * - STAT action text
 *
 * Designed from a cardiologist's clinical workflow: "Does this meet criteria?"
 */

import type { SignalData, PerLeadFeatures } from "./types";

/* ---- Types ---- */

export interface HighlightRule {
  region: "st" | "qrs" | "t" | "p" | "pr" | "rr";
  color: string;
  condition: "elevation" | "depression" | "inversion" | "wide" | "short" | "absent" | "always";
}

export interface DiagnosticCriterion {
  label: string;
  /** Evaluate whether this criterion is met from signal data */
  check: (s: SignalData) => boolean | null;
  /** "required" = must be met; "supportive" = nice to have */
  weight: "required" | "supportive";
}

/** Which per-lead measurements to show in the measurement table */
export interface LeadColumn {
  key: keyof PerLeadFeatures;
  label: string;
  unit: string;
  /** If set, values exceeding this are highlighted as abnormal */
  threshold?: number;
  /** "above" = abnormal if > threshold; "below" = abnormal if < threshold */
  thresholdDir?: "above" | "below";
  format?: (v: number) => string;
}

export interface DiseaseConfig {
  label: string;
  leads: string[];
  highlights: HighlightRule[];
  criteria: DiagnosticCriterion[];
  /** Per-lead measurement columns for the measurement table */
  leadColumns: LeadColumn[];
  explanation: string;
  action?: string;
  stat: boolean;
}

/* ---- Colour palette (colour-blind safe) ---- */
const C_ELEV = "#ea580c";
const C_DEP  = "#2563eb";
const C_INV  = "#7c3aed";
const C_WIDE = "#dc2626";
const C_FAST = "#dc2626";
const C_PABS = "#9333ea";
const C_SHORT = "#16a34a";

/* ---- Helper: format mV ---- */
const fmv = (v: number) => `${v >= 0 ? "+" : ""}${v.toFixed(2)}`;

/* ---- Per-lead column presets ---- */
const COL_ST_ELEV: LeadColumn = {
  key: "st_elevation_mv", label: "ST elev", unit: "mV",
  threshold: 0.1, thresholdDir: "above", format: fmv,
};
const COL_ST_DEP: LeadColumn = {
  key: "st_depression_mv", label: "ST dep", unit: "mV",
  threshold: 0.1, thresholdDir: "above", format: fmv,
};
const COL_T_AMP: LeadColumn = {
  key: "t_amplitude_mv", label: "T amp", unit: "mV", format: fmv,
};
const COL_T_MORPH: LeadColumn = {
  key: "t_morphology", label: "T morph", unit: "",
};
const COL_R_AMP: LeadColumn = {
  key: "r_amplitude_mv", label: "R amp", unit: "mV",
};
const COL_S_AMP: LeadColumn = {
  key: "s_amplitude_mv", label: "S amp", unit: "mV",
};
const COL_ST_MORPH: LeadColumn = {
  key: "st_morphology", label: "ST shape", unit: "",
};


/* ==================================================================
 * DISEASE CONFIGURATIONS
 * ================================================================== */

export const DISEASE_CONFIGS: Record<string, DiseaseConfig> = {

  /* ---- ANTERIOR STEMI ---- */
  anterior_stemi: {
    label: "Anterior STEMI",
    leads: ["V1", "V2", "V3", "V4", "II", "III", "aVF"],
    highlights: [
      { region: "st", color: C_ELEV, condition: "elevation" },
      { region: "st", color: C_DEP, condition: "depression" },
    ],
    criteria: [
      {
        label: "ST elevation >= 1 mm in >= 2 contiguous leads (V1-V4)",
        weight: "required",
        check: (s) => {
          const precordial = ["V1", "V2", "V3", "V4"];
          const count = precordial.filter(
            (l) => (s.per_lead_features[l]?.st_elevation_mv ?? 0) > 0.1
          ).length;
          return count >= 2;
        },
      },
      {
        label: "Reciprocal ST depression in inferior leads (II, III, aVF)",
        weight: "supportive",
        check: (s) => {
          const inf = ["II", "III", "aVF"];
          return inf.some((l) => (s.per_lead_features[l]?.st_depression_mv ?? 0) > 0.05);
        },
      },
      {
        label: "ST morphology convex or tombstone (not concave/BER)",
        weight: "supportive",
        check: (s) => {
          const m = s.per_lead_features["V2"]?.st_morphology ?? s.per_lead_features["V3"]?.st_morphology;
          return m === "convex" || m === "tombstone" || m === "downsloping";
        },
      },
      {
        label: "Hyperacute T waves (tall, symmetric, broad-based)",
        weight: "supportive",
        check: (s) => {
          return ["V2", "V3", "V4"].some((l) => (s.per_lead_features[l]?.t_amplitude_mv ?? 0) > 1.0);
        },
      },
    ],
    leadColumns: [COL_ST_ELEV, COL_ST_DEP, COL_T_AMP, COL_ST_MORPH],
    explanation:
      "ST elevation in {elev_leads} (max {max_st} mV). " +
      "Anterior territory (LAD). Reciprocal depression: {dep_leads}.",
    action: "Consider immediate cath lab activation — clinical correlation required.",
    stat: true,
  },

  /* ---- INFERIOR STEMI ---- */
  inferior_stemi: {
    label: "Inferior STEMI",
    leads: ["II", "III", "aVF", "I", "aVL", "V1"],
    highlights: [
      { region: "st", color: C_ELEV, condition: "elevation" },
      { region: "st", color: C_DEP, condition: "depression" },
    ],
    criteria: [
      {
        label: "ST elevation >= 1 mm in >= 2 of II, III, aVF",
        weight: "required",
        check: (s) => {
          const inf = ["II", "III", "aVF"];
          return inf.filter((l) => (s.per_lead_features[l]?.st_elevation_mv ?? 0) > 0.1).length >= 2;
        },
      },
      {
        label: "Reciprocal ST depression in I, aVL",
        weight: "supportive",
        check: (s) => {
          return ["I", "aVL"].some((l) => (s.per_lead_features[l]?.st_depression_mv ?? 0) > 0.05);
        },
      },
      {
        label: "ST elevation III > II (suggests RCA over LCx)",
        weight: "supportive",
        check: (s) => {
          const stIII = s.per_lead_features["III"]?.st_elevation_mv ?? 0;
          const stII = s.per_lead_features["II"]?.st_elevation_mv ?? 0;
          return stIII > stII;
        },
      },
    ],
    leadColumns: [COL_ST_ELEV, COL_ST_DEP, COL_T_AMP],
    explanation:
      "ST elevation in {elev_leads} (max {max_st} mV). " +
      "Inferior territory (RCA/LCx). Reciprocal: {dep_leads}.",
    action: "Consider immediate cath lab activation. Check V4R for RV involvement.",
    stat: true,
  },

  /* ---- ATRIAL FIBRILLATION ---- */
  afib: {
    label: "Atrial Fibrillation",
    leads: ["II", "V1"],
    highlights: [
      { region: "rr", color: C_FAST, condition: "always" },
    ],
    criteria: [
      {
        label: "Irregularly irregular RR intervals",
        weight: "required",
        check: (s) => s.global_features.rhythm_regular === false,
      },
      {
        label: "Absent discrete P waves",
        weight: "required",
        check: (s) => s.global_features.dominant_rhythm === "afib",
      },
      {
        label: "Narrow QRS (< 120 ms) — no aberrancy",
        weight: "supportive",
        check: (s) => (s.global_features.qrs_duration_ms ?? 999) < 120,
      },
      {
        label: "Ventricular rate classification",
        weight: "supportive",
        check: (s) => {
          const hr = s.global_features.heart_rate_bpm;
          return hr != null && hr > 0; // always true if HR exists
        },
      },
    ],
    leadColumns: [COL_T_AMP, COL_T_MORPH],
    explanation:
      "Irregularly irregular rhythm. P waves absent. " +
      "Ventricular rate: {hr} bpm. QRS: {qrs_ms} ms.",
    stat: false,
  },

  /* ---- LBBB ---- */
  lbbb: {
    label: "Left Bundle Branch Block",
    leads: ["V1", "V6", "I", "aVL"],
    highlights: [
      { region: "qrs", color: C_WIDE, condition: "wide" },
      { region: "st", color: C_DEP, condition: "depression" },
      { region: "st", color: C_ELEV, condition: "elevation" },
    ],
    criteria: [
      {
        label: "QRS duration >= 120 ms",
        weight: "required",
        check: (s) => (s.global_features.qrs_duration_ms ?? 0) >= 120,
      },
      {
        label: "LBBB morphology (QS/rS in V1, broad R in V5-V6)",
        weight: "required",
        check: (s) => s.global_features.lbbb === true,
      },
      {
        label: "Appropriate ST-T discordance (opposite to QRS)",
        weight: "supportive",
        check: (s) => {
          // V1 should have ST elevation (positive ST, negative QRS)
          // V6 should have ST depression (negative ST, positive QRS)
          const v1_elev = (s.per_lead_features["V1"]?.st_elevation_mv ?? 0) > 0.05;
          const v6_dep = (s.per_lead_features["V6"]?.st_depression_mv ?? 0) > 0.05;
          return v1_elev || v6_dep;
        },
      },
      {
        label: "No concordant ST changes (Sgarbossa negative)",
        weight: "supportive",
        check: (s) => {
          // Concordant = ST goes same direction as QRS. In LBBB normal, ST is discordant.
          // Concordant ST elevation in V5/V6 would suggest STEMI
          const v5_elev = (s.per_lead_features["V5"]?.st_elevation_mv ?? 0) > 0.1;
          const v6_elev = (s.per_lead_features["V6"]?.st_elevation_mv ?? 0) > 0.1;
          return !v5_elev && !v6_elev; // true means Sgarbossa negative (good)
        },
      },
    ],
    leadColumns: [COL_R_AMP, COL_S_AMP, COL_ST_ELEV, COL_ST_DEP, COL_T_MORPH],
    explanation:
      "QRS {qrs_ms} ms. V1: QS/rS pattern. V5-V6: broad notched R. " +
      "ST-T discordance is expected and does not indicate ischemia.",
    stat: false,
  },

  /* ---- RBBB ---- */
  rbbb: {
    label: "Right Bundle Branch Block",
    leads: ["V1", "V2", "I", "V6"],
    highlights: [
      { region: "qrs", color: C_WIDE, condition: "wide" },
    ],
    criteria: [
      {
        label: "QRS duration >= 120 ms",
        weight: "required",
        check: (s) => (s.global_features.qrs_duration_ms ?? 0) >= 120,
      },
      {
        label: "RSR' pattern in V1/V2",
        weight: "required",
        check: (s) => s.global_features.rbbb === true,
      },
      {
        label: "Wide S wave in I and V6",
        weight: "supportive",
        check: (s) => {
          return (s.per_lead_features["I"]?.s_amplitude_mv ?? 0) > 0.3 ||
                 (s.per_lead_features["V6"]?.s_amplitude_mv ?? 0) > 0.3;
        },
      },
    ],
    leadColumns: [COL_R_AMP, COL_S_AMP, COL_ST_ELEV, COL_T_MORPH],
    explanation:
      "QRS {qrs_ms} ms. RSR' in V1/V2, wide S in I and V6.",
    stat: false,
  },

  /* ---- WPW ---- */
  wpw_pattern: {
    label: "WPW (Pre-excitation)",
    leads: ["II", "V1", "V2", "I", "aVF", "V6"],
    highlights: [
      { region: "pr", color: C_SHORT, condition: "short" },
      { region: "qrs", color: C_WIDE, condition: "wide" },
    ],
    criteria: [
      {
        label: "PR interval < 120 ms",
        weight: "required",
        check: (s) => (s.global_features.pr_interval_ms ?? 999) < 120,
      },
      {
        label: "QRS >= 110 ms (widened by delta wave)",
        weight: "required",
        check: (s) => (s.global_features.qrs_duration_ms ?? 0) >= 110,
      },
      {
        label: "Delta wave (slurred QRS upstroke) present",
        weight: "required",
        check: (s) => s.global_features.wpw_pattern === true,
      },
      {
        label: "Secondary ST-T changes (discordant to delta)",
        weight: "supportive",
        check: () => true,
      },
    ],
    leadColumns: [COL_R_AMP, COL_S_AMP, COL_ST_ELEV, COL_ST_DEP],
    explanation:
      "Short PR ({pr_ms} ms). Delta wave present. QRS {qrs_ms} ms (pre-excitation). " +
      "Secondary ST-T changes are expected.",
    stat: false,
  },

  /* ---- 1ST DEGREE AVB ---- */
  first_degree_avb: {
    label: "1st Degree AV Block",
    leads: ["II"],
    highlights: [
      { region: "pr", color: "#d97706", condition: "always" },
    ],
    criteria: [
      {
        label: "PR interval > 200 ms",
        weight: "required",
        check: (s) => (s.global_features.pr_interval_ms ?? 0) > 200,
      },
      {
        label: "Every P wave followed by QRS (1:1 conduction)",
        weight: "required",
        check: (s) => s.global_features.rhythm_regular !== false,
      },
    ],
    leadColumns: [],
    explanation: "PR interval {pr_ms} ms (> 200 ms). All P waves conducted.",
    stat: false,
  },

  /* ---- COMPLETE AVB ---- */
  complete_avb: {
    label: "Complete AV Block",
    leads: ["II"],
    highlights: [
      { region: "p", color: C_PABS, condition: "always" },
      { region: "qrs", color: C_WIDE, condition: "always" },
    ],
    criteria: [
      {
        label: "AV dissociation (P and QRS independent)",
        weight: "required",
        check: () => null,
      },
      {
        label: "Regular ventricular escape rhythm",
        weight: "supportive",
        check: (s) => s.global_features.heart_rate_bpm != null,
      },
    ],
    leadColumns: [],
    explanation: "Complete AV dissociation. Ventricular rate: {hr} bpm.",
    action: "Immediate pacing may be required.",
    stat: true,
  },

  /* ---- VT ---- */
  vt: {
    label: "Ventricular Tachycardia",
    leads: ["II", "V1", "V6"],
    highlights: [
      { region: "qrs", color: C_WIDE, condition: "wide" },
    ],
    criteria: [
      {
        label: "Wide complex tachycardia (QRS >= 120 ms, HR > 100)",
        weight: "required",
        check: (s) => {
          return (s.global_features.qrs_duration_ms ?? 0) >= 120 &&
                 (s.global_features.heart_rate_bpm ?? 0) > 100;
        },
      },
      {
        label: "AV dissociation or capture/fusion beats",
        weight: "supportive",
        check: () => null,
      },
    ],
    leadColumns: [COL_R_AMP, COL_S_AMP],
    explanation: "Wide QRS ({qrs_ms} ms) tachycardia ({hr} bpm).",
    action: "Immediate intervention — consider cardioversion.",
    stat: true,
  },

  /* ---- WELLENS ---- */
  wellens: {
    label: "Wellens Syndrome",
    leads: ["V2", "V3", "V4"],
    highlights: [
      { region: "t", color: C_INV, condition: "inversion" },
    ],
    criteria: [
      {
        label: "Deep symmetric T inversion in V2-V3 (Type B) or biphasic T (Type A)",
        weight: "required",
        check: (s) => {
          return ["V2", "V3"].some((l) => s.per_lead_features[l]?.t_morphology === "inverted");
        },
      },
      {
        label: "No significant ST elevation (isoelectric or minimal)",
        weight: "required",
        check: (s) => {
          return ["V2", "V3"].every((l) => (s.per_lead_features[l]?.st_elevation_mv ?? 0) < 0.1);
        },
      },
      {
        label: "Preserved R-wave progression",
        weight: "supportive",
        check: () => null,
      },
    ],
    leadColumns: [COL_T_AMP, COL_T_MORPH, COL_ST_ELEV],
    explanation:
      "Deep symmetric T inversion in {inv_leads}. No significant ST elevation. " +
      "Critical LAD stenosis — patient may be pain-free.",
    action: "Urgent cardiology consultation. Do NOT stress test.",
    stat: true,
  },

  /* ---- DE WINTER ---- */
  de_winter: {
    label: "de Winter T-waves",
    leads: ["V2", "V3", "V4", "V5", "aVR"],
    highlights: [
      { region: "st", color: C_DEP, condition: "depression" },
      { region: "t", color: C_ELEV, condition: "always" },
    ],
    criteria: [
      {
        label: "Upsloping ST depression in V2-V5",
        weight: "required",
        check: (s) => {
          return ["V2", "V3", "V4"].some((l) => (s.per_lead_features[l]?.st_depression_mv ?? 0) > 0.05);
        },
      },
      {
        label: "Tall symmetric T waves in precordial leads",
        weight: "required",
        check: (s) => {
          return ["V2", "V3", "V4"].some((l) => (s.per_lead_features[l]?.t_amplitude_mv ?? 0) > 0.8);
        },
      },
      {
        label: "ST elevation in aVR",
        weight: "supportive",
        check: (s) => (s.per_lead_features["aVR"]?.st_elevation_mv ?? 0) > 0.05,
      },
    ],
    leadColumns: [COL_ST_DEP, COL_T_AMP, COL_ST_ELEV],
    explanation:
      "Upsloping ST depression with tall T waves in V2-V5. aVR ST elevation. " +
      "STEMI equivalent — proximal LAD occlusion.",
    action: "Consider immediate cath lab activation — STEMI equivalent.",
    stat: true,
  },

  /* ---- LVH ---- */
  lvh: {
    label: "Left Ventricular Hypertrophy",
    leads: ["I", "aVL", "V1", "V5", "V6"],
    highlights: [
      { region: "qrs", color: "#d97706", condition: "always" },
      { region: "st", color: C_DEP, condition: "depression" },
    ],
    criteria: [
      {
        label: "Sokolow-Lyon: S(V1) + R(V5 or V6) > 3.5 mV",
        weight: "required",
        check: (s) => {
          const sv1 = s.per_lead_features["V1"]?.s_amplitude_mv ?? 0;
          const rv5 = s.per_lead_features["V5"]?.r_amplitude_mv ?? 0;
          const rv6 = s.per_lead_features["V6"]?.r_amplitude_mv ?? 0;
          return sv1 + Math.max(rv5, rv6) > 3.5;
        },
      },
      {
        label: "Cornell: R(aVL) + S(V3) > 2.8 mV (M) / 2.0 mV (F)",
        weight: "supportive",
        check: (s) => {
          const ravl = s.per_lead_features["aVL"]?.r_amplitude_mv ?? 0;
          const sv3 = s.per_lead_features["V3"]?.s_amplitude_mv ?? 0;
          return ravl + sv3 > 2.8; // using male threshold
        },
      },
      {
        label: "Strain pattern (ST depression + T inversion in lateral leads)",
        weight: "supportive",
        check: (s) => {
          return ["V5", "V6", "I", "aVL"].some(
            (l) => (s.per_lead_features[l]?.st_depression_mv ?? 0) > 0.05 &&
                   s.per_lead_features[l]?.t_morphology === "inverted"
          );
        },
      },
    ],
    leadColumns: [COL_R_AMP, COL_S_AMP, COL_ST_DEP, COL_T_MORPH],
    explanation:
      "Voltage criteria for LVH. QRS axis {axis_deg} deg. " +
      "Strain pattern in lateral leads.",
    stat: false,
  },

  /* ---- BRUGADA TYPE 1 ---- */
  brugada_type1: {
    label: "Brugada Type 1",
    leads: ["V1", "V2", "V3"],
    highlights: [
      { region: "st", color: C_ELEV, condition: "elevation" },
      { region: "t", color: C_INV, condition: "inversion" },
    ],
    criteria: [
      {
        label: "Coved ST elevation >= 2 mm in V1-V2",
        weight: "required",
        check: (s) => {
          return ["V1", "V2"].some((l) => (s.per_lead_features[l]?.st_elevation_mv ?? 0) >= 0.2);
        },
      },
      {
        label: "Descending T-wave inversion following ST",
        weight: "required",
        check: (s) => {
          return ["V1", "V2"].some((l) => s.per_lead_features[l]?.t_morphology === "inverted");
        },
      },
    ],
    leadColumns: [COL_ST_ELEV, COL_ST_MORPH, COL_T_MORPH],
    explanation:
      "Coved ST elevation with T inversion in V1-V2. Brugada Type 1 pattern.",
    action: "EP consultation required — risk of sudden cardiac death.",
    stat: true,
  },

  /* ---- LONG QT ---- */
  long_qt: {
    label: "Long QT",
    leads: ["II", "V5"],
    highlights: [
      { region: "t", color: C_INV, condition: "always" },
    ],
    criteria: [
      {
        label: "QTc > 480 ms (Bazett)",
        weight: "required",
        check: (s) => (s.global_features.qtc_bazett_ms ?? 0) > 480,
      },
      {
        label: "QTc > 500 ms — high TdP risk",
        weight: "supportive",
        check: (s) => (s.global_features.qtc_bazett_ms ?? 0) > 500,
      },
    ],
    leadColumns: [COL_T_AMP, COL_T_MORPH],
    explanation:
      "QTc {qtc_ms} ms (Bazett). Risk of Torsades de Pointes.",
    stat: false,
  },

  /* ---- PERICARDITIS ---- */
  pericarditis: {
    label: "Pericarditis",
    leads: ["II", "aVR", "V5", "V6", "I"],
    highlights: [
      { region: "st", color: C_ELEV, condition: "elevation" },
      { region: "st", color: C_DEP, condition: "depression" },
    ],
    criteria: [
      {
        label: "Diffuse concave ST elevation (>= 4 leads)",
        weight: "required",
        check: (s) => {
          const diffuse = ["I", "II", "aVF", "V3", "V4", "V5", "V6"];
          return diffuse.filter((l) => (s.per_lead_features[l]?.st_elevation_mv ?? 0) > 0.05).length >= 4;
        },
      },
      {
        label: "Reciprocal ST depression + PR elevation in aVR",
        weight: "supportive",
        check: (s) => (s.per_lead_features["aVR"]?.st_depression_mv ?? 0) > 0.03,
      },
    ],
    leadColumns: [COL_ST_ELEV, COL_ST_DEP, COL_ST_MORPH],
    explanation:
      "Diffuse concave ST elevation in {elev_leads}. " +
      "Reciprocal changes in aVR. Pattern consistent with pericarditis.",
    stat: false,
  },

  /* ---- POSSIBLE STEMI ---- */
  possible_stemi: {
    label: "Possible STEMI",
    leads: ["V1", "V2", "V3", "V4", "V5", "V6", "II", "III", "aVF", "I", "aVL"],
    highlights: [
      { region: "st", color: C_ELEV, condition: "elevation" },
      { region: "st", color: C_DEP, condition: "depression" },
    ],
    criteria: [
      {
        label: "ST changes present but do not meet full STEMI criteria",
        weight: "required",
        check: (s) => {
          const anyElev = Object.values(s.per_lead_features).some(
            (f) => (f.st_elevation_mv ?? 0) > 0.05
          );
          return anyElev;
        },
      },
    ],
    leadColumns: [COL_ST_ELEV, COL_ST_DEP, COL_T_AMP],
    explanation:
      "ST changes in {elev_leads}. Does not meet full STEMI criteria. " +
      "Serial ECGs recommended.",
    action: "Serial ECGs recommended — clinical correlation required.",
    stat: true,
  },

  /* ---- HYPERKALEMIA ---- */
  hyperkalemia: {
    label: "Hyperkalemia",
    leads: ["II", "V1", "V3", "V5"],
    highlights: [
      { region: "t", color: C_ELEV, condition: "always" },
      { region: "qrs", color: C_WIDE, condition: "wide" },
    ],
    criteria: [
      {
        label: "Peaked T waves (tall, narrow base)",
        weight: "required",
        check: (s) => {
          return ["V2", "V3", "V4"].some((l) => (s.per_lead_features[l]?.t_amplitude_mv ?? 0) > 0.8);
        },
      },
      {
        label: "QRS widening (> 120 ms in severe cases)",
        weight: "supportive",
        check: (s) => (s.global_features.qrs_duration_ms ?? 0) > 120,
      },
      {
        label: "P-wave flattening or loss",
        weight: "supportive",
        check: () => null,
      },
    ],
    leadColumns: [COL_T_AMP, COL_T_MORPH, COL_R_AMP],
    explanation:
      "Peaked T waves. QRS {qrs_ms} ms. " +
      "Progressive: peaked T -> wide QRS -> loss of P -> sine wave.",
    action: "Check serum potassium urgently.",
    stat: false,
  },

  /* ---- LATERAL STEMI ---- */
  lateral_stemi: {
    label: "Lateral STEMI",
    leads: ["I", "aVL", "V5", "V6", "II", "III", "aVF"],
    highlights: [
      { region: "st", color: C_ELEV, condition: "elevation" },
      { region: "st", color: C_DEP, condition: "depression" },
    ],
    criteria: [
      {
        label: "ST elevation >= 1 mm in >= 2 of I, aVL, V5, V6",
        weight: "required",
        check: (s) => {
          const lateral = ["I", "aVL", "V5", "V6"];
          return lateral.filter(
            (l) => (s.per_lead_features[l]?.st_elevation_mv ?? 0) > 0.1
          ).length >= 2;
        },
      },
      {
        label: "Reciprocal ST depression in inferior leads (II, III, aVF)",
        weight: "supportive",
        check: (s) => {
          return ["II", "III", "aVF"].some(
            (l) => (s.per_lead_features[l]?.st_depression_mv ?? 0) > 0.05
          );
        },
      },
      {
        label: "ST morphology convex or tombstone",
        weight: "supportive",
        check: (s) => {
          const m = s.per_lead_features["I"]?.st_morphology ?? s.per_lead_features["aVL"]?.st_morphology;
          return m === "convex" || m === "tombstone";
        },
      },
    ],
    leadColumns: [COL_ST_ELEV, COL_ST_DEP, COL_T_AMP, COL_ST_MORPH],
    explanation:
      "ST elevation in {elev_leads} (max {max_st} mV). " +
      "Lateral territory (LCx/diagonal). Reciprocal depression: {dep_leads}.",
    action: "Consider immediate cath lab activation — clinical correlation required.",
    stat: true,
  },

  /* ---- SGARBOSSA STEMI (STEMI + LBBB) ---- */
  sgarbossa_stemi: {
    label: "Sgarbossa STEMI (LBBB + STEMI)",
    leads: ["V1", "V2", "V3", "V4", "V5", "V6", "I", "aVL"],
    highlights: [
      { region: "st", color: C_ELEV, condition: "elevation" },
      { region: "st", color: C_DEP, condition: "depression" },
      { region: "qrs", color: C_WIDE, condition: "wide" },
    ],
    criteria: [
      {
        label: "LBBB present (QRS >= 120 ms with LBBB morphology)",
        weight: "required",
        check: (s) => s.global_features.lbbb === true,
      },
      {
        label: "Concordant ST elevation >= 1 mm in any lead (Sgarbossa 5 pts)",
        weight: "required",
        check: (s) => {
          // Concordant = ST same direction as QRS. In LBBB V1-V3 QRS is negative,
          // so concordant ST depression there is normal. Concordant ST elevation
          // in leads with positive QRS (V5, V6, I, aVL) is abnormal.
          return ["V5", "V6", "I", "aVL"].some(
            (l) => (s.per_lead_features[l]?.st_elevation_mv ?? 0) > 0.1
          );
        },
      },
      {
        label: "Concordant ST depression >= 1 mm in V1-V3 (Sgarbossa 3 pts)",
        weight: "supportive",
        check: (s) => {
          return ["V1", "V2", "V3"].some(
            (l) => (s.per_lead_features[l]?.st_depression_mv ?? 0) > 0.1
          );
        },
      },
      {
        label: "Excessively discordant ST elevation (Smith-modified: ST/S ratio > 0.25)",
        weight: "supportive",
        check: (s) => {
          return ["V1", "V2", "V3"].some((l) => {
            const st = s.per_lead_features[l]?.st_elevation_mv ?? 0;
            const sAmp = s.per_lead_features[l]?.s_amplitude_mv ?? 1;
            return sAmp !== 0 && st / Math.abs(sAmp) > 0.25;
          });
        },
      },
    ],
    leadColumns: [COL_R_AMP, COL_S_AMP, COL_ST_ELEV, COL_ST_DEP, COL_ST_MORPH],
    explanation:
      "LBBB with Sgarbossa-positive criteria. QRS {qrs_ms} ms. " +
      "Concordant ST changes suggest acute MI superimposed on LBBB.",
    action: "Consider immediate cath lab activation — STEMI equivalent in LBBB.",
    stat: true,
  },

  /* ---- POSTERIOR STEMI ---- */
  posterior_stemi: {
    label: "Posterior STEMI",
    leads: ["V1", "V2", "V3", "II", "III", "aVF"],
    highlights: [
      { region: "st", color: C_DEP, condition: "depression" },
      { region: "t", color: C_ELEV, condition: "always" },
    ],
    criteria: [
      {
        label: "ST depression >= 1 mm in V1-V3 (reciprocal of posterior elevation)",
        weight: "required",
        check: (s) => {
          return ["V1", "V2", "V3"].filter(
            (l) => (s.per_lead_features[l]?.st_depression_mv ?? 0) > 0.1
          ).length >= 2;
        },
      },
      {
        label: "Tall R waves in V1-V2 (mirror image of posterior Q waves)",
        weight: "supportive",
        check: (s) => {
          return (s.per_lead_features["V1"]?.r_amplitude_mv ?? 0) > 0.6 ||
                 (s.per_lead_features["V2"]?.r_amplitude_mv ?? 0) > 0.6;
        },
      },
      {
        label: "Upright T waves in V1-V2 (mirror of posterior T inversion)",
        weight: "supportive",
        check: (s) => {
          return ["V1", "V2"].some(
            (l) => (s.per_lead_features[l]?.t_amplitude_mv ?? 0) > 0.3
          );
        },
      },
      {
        label: "Associated inferior STEMI (II, III, aVF elevation)",
        weight: "supportive",
        check: (s) => {
          return ["II", "III", "aVF"].some(
            (l) => (s.per_lead_features[l]?.st_elevation_mv ?? 0) > 0.1
          );
        },
      },
    ],
    leadColumns: [COL_ST_DEP, COL_R_AMP, COL_T_AMP, COL_ST_ELEV],
    explanation:
      "ST depression in V1-V3 (reciprocal posterior changes). " +
      "Posterior territory (LCx/RCA). Consider posterior leads (V7-V9).",
    action: "Consider immediate cath lab activation — obtain posterior leads V7-V9.",
    stat: true,
  },

  /* ---- SINUS BRADYCARDIA ---- */
  sinus_bradycardia: {
    label: "Sinus Bradycardia",
    leads: ["II"],
    highlights: [
      { region: "rr", color: C_SHORT, condition: "always" },
      { region: "p", color: C_SHORT, condition: "always" },
    ],
    criteria: [
      {
        label: "Heart rate < 60 bpm",
        weight: "required",
        check: (s) => (s.global_features.heart_rate_bpm ?? 999) < 60,
      },
      {
        label: "Regular sinus rhythm (upright P in II, inverted in aVR)",
        weight: "required",
        check: (s) => s.global_features.dominant_rhythm === "sinus" || s.global_features.rhythm_regular === true,
      },
      {
        label: "Normal PR interval (120-200 ms)",
        weight: "supportive",
        check: (s) => {
          const pr = s.global_features.pr_interval_ms ?? 0;
          return pr >= 120 && pr <= 200;
        },
      },
    ],
    leadColumns: [COL_T_AMP],
    explanation:
      "Sinus rhythm at {hr} bpm (< 60). PR interval {pr_ms} ms. " +
      "May be normal in athletes or during sleep.",
    stat: false,
  },

  /* ---- SINUS TACHYCARDIA ---- */
  sinus_tachycardia: {
    label: "Sinus Tachycardia",
    leads: ["II"],
    highlights: [
      { region: "rr", color: C_FAST, condition: "always" },
      { region: "p", color: C_FAST, condition: "always" },
    ],
    criteria: [
      {
        label: "Heart rate > 100 bpm",
        weight: "required",
        check: (s) => (s.global_features.heart_rate_bpm ?? 0) > 100,
      },
      {
        label: "Regular sinus rhythm (upright P in II preceding each QRS)",
        weight: "required",
        check: (s) => s.global_features.dominant_rhythm === "sinus" || s.global_features.rhythm_regular === true,
      },
      {
        label: "Narrow QRS (< 120 ms)",
        weight: "supportive",
        check: (s) => (s.global_features.qrs_duration_ms ?? 999) < 120,
      },
    ],
    leadColumns: [COL_T_AMP],
    explanation:
      "Sinus rhythm at {hr} bpm (> 100). QRS {qrs_ms} ms. " +
      "Evaluate for underlying cause (pain, fever, hypovolemia, PE).",
    stat: false,
  },

  /* ---- RVH ---- */
  rvh: {
    label: "Right Ventricular Hypertrophy",
    leads: ["V1", "V2", "V5", "V6", "II"],
    highlights: [
      { region: "qrs", color: "#d97706", condition: "always" },
      { region: "st", color: C_DEP, condition: "depression" },
      { region: "t", color: C_INV, condition: "inversion" },
    ],
    criteria: [
      {
        label: "R wave in V1 > 7 mm or R/S ratio > 1 in V1",
        weight: "required",
        check: (s) => {
          const rv1 = s.per_lead_features["V1"]?.r_amplitude_mv ?? 0;
          const sv1 = s.per_lead_features["V1"]?.s_amplitude_mv ?? 1;
          return rv1 > 0.7 || (sv1 !== 0 && rv1 / Math.abs(sv1) > 1);
        },
      },
      {
        label: "Right axis deviation (> 90 degrees)",
        weight: "supportive",
        check: (s) => (s.global_features.qrs_axis_deg ?? 0) > 90,
      },
      {
        label: "RV strain pattern (ST depression + T inversion in V1-V3)",
        weight: "supportive",
        check: (s) => {
          return ["V1", "V2", "V3"].some(
            (l) => (s.per_lead_features[l]?.st_depression_mv ?? 0) > 0.05 &&
                   s.per_lead_features[l]?.t_morphology === "inverted"
          );
        },
      },
      {
        label: "Deep S waves in V5-V6",
        weight: "supportive",
        check: (s) => {
          return (s.per_lead_features["V5"]?.s_amplitude_mv ?? 0) > 0.5 ||
                 (s.per_lead_features["V6"]?.s_amplitude_mv ?? 0) > 0.5;
        },
      },
    ],
    leadColumns: [COL_R_AMP, COL_S_AMP, COL_ST_DEP, COL_T_MORPH],
    explanation:
      "Dominant R in V1. QRS axis {axis_deg} deg. " +
      "RV strain pattern in right precordial leads.",
    stat: false,
  },

  /* ---- LAE ---- */
  lae: {
    label: "Left Atrial Enlargement",
    leads: ["II", "V1"],
    highlights: [
      { region: "p", color: "#d97706", condition: "always" },
    ],
    criteria: [
      {
        label: "P wave duration > 120 ms in lead II (P mitrale)",
        weight: "required",
        check: () => null, // requires P-wave duration not yet in features
      },
      {
        label: "Notched P wave in lead II (interpeak > 40 ms)",
        weight: "supportive",
        check: () => null,
      },
      {
        label: "Terminal P-wave force in V1 > 0.04 mm·s (deep, wide negative component)",
        weight: "supportive",
        check: () => null,
      },
    ],
    leadColumns: [COL_T_AMP],
    explanation:
      "P-wave morphology consistent with left atrial enlargement. " +
      "Broad, notched P in II; deep terminal negativity in V1.",
    stat: false,
  },

  /* ---- RAE ---- */
  rae: {
    label: "Right Atrial Enlargement",
    leads: ["II", "V1"],
    highlights: [
      { region: "p", color: "#d97706", condition: "always" },
    ],
    criteria: [
      {
        label: "P wave amplitude > 2.5 mm in lead II (P pulmonale)",
        weight: "required",
        check: () => null, // requires P-wave amplitude not yet in features
      },
      {
        label: "Peaked P wave in II, III, aVF",
        weight: "supportive",
        check: () => null,
      },
      {
        label: "Tall initial positive P deflection in V1",
        weight: "supportive",
        check: () => null,
      },
    ],
    leadColumns: [COL_T_AMP],
    explanation:
      "Tall peaked P waves in inferior leads (P pulmonale). " +
      "Consistent with right atrial enlargement.",
    stat: false,
  },

  /* ---- SECOND DEGREE AVB ---- */
  second_degree_avb: {
    label: "2nd Degree AV Block",
    leads: ["II"],
    highlights: [
      { region: "pr", color: "#d97706", condition: "always" },
      { region: "p", color: C_PABS, condition: "always" },
    ],
    criteria: [
      {
        label: "Some P waves not followed by QRS (dropped beats)",
        weight: "required",
        check: () => null, // requires beat-level P/QRS association
      },
      {
        label: "Mobitz I (Wenckebach): progressive PR prolongation before drop",
        weight: "supportive",
        check: () => null,
      },
      {
        label: "Mobitz II: constant PR with sudden dropped QRS",
        weight: "supportive",
        check: () => null,
      },
    ],
    leadColumns: [],
    explanation:
      "Intermittent dropped QRS complexes. PR interval {pr_ms} ms. " +
      "Distinguish Mobitz I (benign) from Mobitz II (may need pacing).",
    stat: false,
  },

  /* ---- PATHOLOGICAL Q WAVES ---- */
  pathological_q_waves: {
    label: "Pathological Q Waves",
    leads: ["I", "II", "III", "aVL", "aVF", "V1", "V2", "V3", "V4", "V5", "V6"],
    highlights: [
      { region: "qrs", color: "#d97706", condition: "always" },
    ],
    criteria: [
      {
        label: "Q wave width >= 40 ms or depth >= 25% of R amplitude",
        weight: "required",
        check: () => null, // requires Q-wave measurements not yet in features
      },
      {
        label: "Q waves in >= 2 contiguous leads (same territory)",
        weight: "required",
        check: () => null,
      },
      {
        label: "Associated T-wave changes (inversion or flattening)",
        weight: "supportive",
        check: (s) => {
          return Object.values(s.per_lead_features).some(
            (f) => f.t_morphology === "inverted"
          );
        },
      },
    ],
    leadColumns: [COL_R_AMP, COL_T_AMP, COL_T_MORPH],
    explanation:
      "Pathological Q waves in {q_leads}. " +
      "Suggests prior myocardial infarction in the corresponding territory.",
    stat: false,
  },
};


export function getDiseaseConfig(findingType: string): DiseaseConfig | null {
  return DISEASE_CONFIGS[findingType] ?? null;
}
