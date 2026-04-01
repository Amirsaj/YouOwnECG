/** TypeScript mirror of DiagnosticResult schema from agents/schemas.py */

export type Confidence = "HIGH" | "MODERATE" | "LOW" | "INSUFFICIENT_EVIDENCE";
export type OverallQuality = "GOOD" | "ACCEPTABLE" | "POOR" | "UNINTERPRETABLE";

export interface Citation {
  chunk_id: string;
  book: string;
  book_short: string;
  chapter: string;
  section: string;
  page_number: number;
  similarity_score: number;
  retrieved_text: string;
  context_expanded: boolean;
}

export interface DiagnosticFinding {
  finding_type: string;
  confidence: Confidence;
  clinical_summary: string;
  clinical_summary_fa?: string | null;
  technical_detail: string;
  citations: Citation[];
  rag_invoked: boolean;
}

export interface StatAlert {
  finding_type: string;
  confidence: Confidence;
  message: string;
}

export interface Measurements {
  heart_rate_ventricular_bpm: number | null;
  heart_rate_atrial_bpm?: number | null;
  pr_interval_ms: number | null;
  qrs_duration_global_ms: number | null;
  qt_interval_ms?: number | null;
  qtc_bazett_ms: number | null;
  qrs_axis_deg: number | null;
  p_axis_deg?: number | null;
  t_axis_deg?: number | null;
  rhythm: string | null;
  rhythm_regular?: boolean | null;
  beat_class_counts?: Record<string, number> | null;
  lbbb: boolean;
  rbbb: boolean;
  lvh_criteria_met?: boolean | null;
}

export interface DiagnosticResult {
  ecg_id: string;
  findings: DiagnosticFinding[];
  stat_alerts: StatAlert[];
  measurements: Measurements;
  overall_quality: OverallQuality;
  pipeline_version: string;
  model_version: string;
}

/* ---- Signal data for disease dashboard ECG rendering ---- */

export interface BeatFiducials {
  pon: number | null;
  ppeak: number | null;
  poff: number | null;
  qrson: number | null;
  q: number | null;
  r: number | null;
  s: number | null;
  qrsoff: number | null;
  ton: number | null;
  tpeak: number | null;
  toff: number | null;
}

export interface LeadSignal {
  filtered: number[];
  raw: number[];
}

export interface PerLeadFeatures {
  st_elevation_mv?: number | null;
  st_depression_mv?: number | null;
  t_amplitude_mv?: number | null;
  t_morphology?: string | null;
  r_amplitude_mv?: number | null;
  s_amplitude_mv?: number | null;
  st_morphology?: string | null;
}

export interface GlobalFeatures {
  heart_rate_bpm: number | null;
  pr_interval_ms: number | null;
  qrs_duration_ms: number | null;
  qt_interval_ms: number | null;
  qtc_bazett_ms: number | null;
  qrs_axis_deg: number | null;
  dominant_rhythm: string | null;
  rhythm_regular: boolean | null;
  lbbb: boolean;
  rbbb: boolean;
  wpw_pattern: boolean;
}

export interface SignalData {
  ecg_id: string;
  leads: string[];
  fs: number;
  n_samples: number;
  safe_window_duration_sec: number;
  signal: Record<string, LeadSignal>;
  fiducials: Record<string, BeatFiducials[]>;
  per_lead_features: Record<string, PerLeadFeatures>;
  global_features: GlobalFeatures;
  patient_age?: number | null;
  patient_sex?: string | null;
}
