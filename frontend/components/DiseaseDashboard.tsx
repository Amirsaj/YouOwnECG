"use client";

/**
 * Per-disease dashboard (Node 3.2) — cardiologist-oriented layout:
 *
 * ┌──────────────────────────────────────────────────┐
 * │ STAT │  Disease Name              │  Confidence  │
 * ├──────────────────────────────────────────────────┤
 * │  ECG STRIPS (grid paper, annotated, scrollable)  │
 * ├───────────────────────┬──────────────────────────┤
 * │  CRITERIA CHECKLIST   │  PER-LEAD MEASUREMENTS   │
 * │  ✓ QRS >= 120 ms     │  Lead  ST   R    T       │
 * │  ✗ Sgarbossa >= 3    │  V1   +0.5  2.7  upright │
 * ├───────────────────────┴──────────────────────────┤
 * │  EXPLANATION (deterministic, template-based)      │
 * ├──────────────────────────────────────────────────┤
 * │  TEXTBOOK EVIDENCE (RAG citations)               │
 * ├──────────────────────────────────────────────────┤
 * │  ⚠ ACTION (STAT only)                           │
 * └──────────────────────────────────────────────────┘
 */

import { useEffect, useState } from "react";
import type { DiagnosticFinding, SignalData, Confidence, PerLeadFeatures } from "@/lib/types";
import type { DiseaseConfig, DiagnosticCriterion, LeadColumn, HighlightRule } from "@/lib/disease-config";
import { getDiseaseConfig } from "@/lib/disease-config";
import { getSignalData } from "@/lib/api";
import LeadStrip from "./LeadStrip";

interface Props {
  finding: DiagnosticFinding;
  ecgId: string;
}

const CONF_COLOR: Record<Confidence, string> = {
  HIGH: "#dc2626",
  MODERATE: "#d97706",
  LOW: "#2563eb",
  INSUFFICIENT_EVIDENCE: "#9ca3af",
};

export default function DiseaseDashboard({ finding, ecgId }: Props) {
  const config = getDiseaseConfig(finding.finding_type);
  const [signal, setSignal] = useState<SignalData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!config) return;
    setLoading(true);
    getSignalData(ecgId, config.leads)
      .then(setSignal)
      .catch((e) => setError((e as Error).message))
      .finally(() => setLoading(false));
  }, [ecgId, config]);

  if (!config) return null;

  const confColor = CONF_COLOR[finding.confidence] ?? "#9ca3af";
  const explanation = fillTemplate(config.explanation, signal, finding);

  return (
    <div style={{
      border: "1px solid #e5e7eb",
      borderRadius: 12,
      overflow: "hidden",
      marginBottom: 16,
      background: "#fff",
      boxShadow: "0 1px 3px rgba(0,0,0,0.06)",
    }}>
      {/* ---- HEADER ---- */}
      <div style={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        padding: "10px 16px",
        background: config.stat ? "#fef2f2" : "#f9fafb",
        borderBottom: `2px solid ${config.stat ? "#fca5a5" : "#e5e7eb"}`,
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          {config.stat && (
            <span style={{
              background: "#dc2626", color: "#fff", fontSize: 10, fontWeight: 800,
              padding: "2px 8px", borderRadius: 4, letterSpacing: "0.1em",
            }}>STAT</span>
          )}
          <span style={{ fontSize: 16, fontWeight: 700 }}>{config.label}</span>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          {/* Global measurements badges */}
          {signal && <GlobalBadges signal={signal} />}
          <span style={{
            fontSize: 11, fontWeight: 700, color: confColor,
            background: `${confColor}18`, padding: "3px 10px", borderRadius: 12,
          }}>
            {finding.confidence.replace("_", " ")}
          </span>
        </div>
      </div>

      {/* ---- PATIENT METADATA ---- */}
      {signal && (signal.patient_age != null || signal.patient_sex != null) && (
        <div style={{
          padding: "6px 16px",
          borderBottom: "1px solid #e5e7eb",
          background: "#f9fafb",
          display: "flex",
          gap: 16,
          fontSize: 12,
          color: "#4b5563",
        }}>
          {signal.patient_age != null && (
            <span><span style={{ fontWeight: 600, color: "#374151" }}>Age:</span> {signal.patient_age} yr</span>
          )}
          {signal.patient_sex != null && (
            <span><span style={{ fontWeight: 600, color: "#374151" }}>Sex:</span> {signal.patient_sex}</span>
          )}
        </div>
      )}

      {/* ---- ECG STRIPS ---- */}
      <div style={{
        padding: "4px 0",
        overflowX: "auto",
        background: "#fff5f5",
        borderBottom: "1px solid #e5e7eb",
      }}>
        {loading && <div style={{ color: "#9ca3af", fontSize: 13, padding: 16 }}>Loading ECG...</div>}
        {error && <div style={{ color: "#dc2626", fontSize: 13, padding: 16 }}>{error}</div>}
        {signal && config.leads.map((lead) => {
          const leadSig = signal.signal[lead];
          if (!leadSig) return null;
          return (
            <LeadStrip
              key={lead}
              leadName={lead}
              samples={leadSig.filtered}
              fs={signal.fs}
              beats={signal.fiducials[lead] ?? []}
              features={signal.per_lead_features[lead] ?? {}}
              highlights={config.highlights}
              pxPerMm={4}
            />
          );
        })}
      </div>

      {/* ---- HIGHLIGHT LEGEND ---- */}
      {config.highlights.length > 0 && (
        <HighlightLegend highlights={config.highlights} />
      )}

      {/* ---- CRITERIA + MEASUREMENTS side by side ---- */}
      {signal && (
        <div style={{ display: "flex", borderBottom: "1px solid #e5e7eb" }}>
          {/* Criteria checklist */}
          <div style={{ flex: 1, padding: "12px 16px", borderRight: "1px solid #e5e7eb" }}>
            <h4 style={{ fontSize: 11, fontWeight: 700, color: "#6b7280", margin: "0 0 8px 0", textTransform: "uppercase", letterSpacing: "0.05em" }}>
              Diagnostic Criteria
            </h4>
            <CriteriaChecklist criteria={config.criteria} signal={signal} />
          </div>

          {/* Per-lead measurement table */}
          {config.leadColumns.length > 0 && (
            <div style={{ flex: 1, padding: "12px 16px", overflowX: "auto" }}>
              <h4 style={{ fontSize: 11, fontWeight: 700, color: "#6b7280", margin: "0 0 8px 0", textTransform: "uppercase", letterSpacing: "0.05em" }}>
                Per-Lead Measurements
              </h4>
              <LeadTable
                leads={config.leads}
                columns={config.leadColumns}
                features={signal.per_lead_features}
              />
            </div>
          )}
        </div>
      )}

      {/* ---- EXPLANATION ---- */}
      <div style={{ padding: "12px 16px", borderBottom: "1px solid #e5e7eb" }}>
        <p style={{ fontSize: 13, color: "#4b5563", lineHeight: 1.6, margin: 0 }}>
          {explanation}
        </p>
      </div>

      {/* ---- EVIDENCE ---- */}
      {finding.citations && finding.citations.length > 0 && (
        <div style={{ padding: "10px 16px", borderBottom: "1px solid #e5e7eb", background: "#f9fafb" }}>
          <h4 style={{ fontSize: 11, fontWeight: 700, color: "#6b7280", margin: "0 0 6px 0", textTransform: "uppercase", letterSpacing: "0.05em" }}>
            Textbook Evidence
          </h4>
          {finding.citations.map((c, i) => (
            <div key={i} style={{ fontSize: 12, color: "#4b5563", marginBottom: 4 }}>
              <span style={{ fontWeight: 600 }}>[{i + 1}]</span> {c.book} | {c.chapter} | p.{c.page_number}
              {c.retrieved_text && (
                <span style={{ color: "#6b7280" }}> — &quot;{c.retrieved_text.slice(0, 120)}...&quot;</span>
              )}
            </div>
          ))}
        </div>
      )}

      {/* ---- ACTION (STAT only) ---- */}
      {config.stat && config.action && (
        <div style={{
          padding: "10px 16px",
          background: "#fef2f2",
          display: "flex", alignItems: "center", gap: 8,
        }}>
          <span style={{ fontSize: 18, lineHeight: 1 }}>!</span>
          <span style={{ fontSize: 13, fontWeight: 600, color: "#dc2626" }}>{config.action}</span>
        </div>
      )}
    </div>
  );
}


/* ============================================================
 * SUB-COMPONENTS
 * ============================================================ */

function GlobalBadges({ signal }: { signal: SignalData }) {
  const g = signal.global_features;
  const items: [string, string][] = [];
  if (g.heart_rate_bpm != null) items.push(["HR", `${Math.round(g.heart_rate_bpm)}`]);
  if (g.qrs_duration_ms != null) items.push(["QRS", `${Math.round(g.qrs_duration_ms)}`]);
  if (g.pr_interval_ms != null) items.push(["PR", `${Math.round(g.pr_interval_ms)}`]);
  if (g.qtc_bazett_ms != null) items.push(["QTc", `${Math.round(g.qtc_bazett_ms)}`]);

  return (
    <div style={{ display: "flex", gap: 4 }}>
      {items.map(([label, value]) => (
        <span key={label} style={{
          fontSize: 10, fontWeight: 600, color: "#6b7280",
          background: "#f3f4f6", borderRadius: 4, padding: "2px 6px",
        }}>
          {label} {value}
        </span>
      ))}
    </div>
  );
}


function highlightLabel(hl: HighlightRule): string {
  switch (hl.region) {
    case "st":
      if (hl.condition === "elevation") return "ST elevation";
      if (hl.condition === "depression") return "ST depression";
      return "ST segment";
    case "qrs":
      if (hl.condition === "wide") return "Wide QRS";
      return "QRS complex";
    case "t":
      if (hl.condition === "inversion") return "T-wave inversion";
      return "T wave";
    case "p":
      if (hl.condition === "absent") return "Absent P wave";
      return "P wave";
    case "pr":
      if (hl.condition === "short") return "Short PR interval";
      return "PR interval";
    case "rr":
      return "RR interval";
    default:
      return String(hl.region);
  }
}


function HighlightLegend({ highlights }: { highlights: HighlightRule[] }) {
  const seen = new Set<string>();
  const items: { color: string; label: string }[] = [];
  for (const hl of highlights) {
    const key = `${hl.color}-${hl.region}-${hl.condition}`;
    if (seen.has(key)) continue;
    seen.add(key);
    items.push({ color: hl.color, label: highlightLabel(hl) });
  }
  if (items.length === 0) return null;

  return (
    <div style={{
      display: "flex",
      flexWrap: "wrap",
      gap: 12,
      padding: "6px 16px",
      borderBottom: "1px solid #e5e7eb",
      background: "#fafafa",
    }}>
      <span style={{
        fontSize: 10,
        fontWeight: 700,
        color: "#6b7280",
        textTransform: "uppercase",
        letterSpacing: "0.05em",
        lineHeight: "20px",
      }}>
        Overlays
      </span>
      {items.map((item) => (
        <span key={item.label} style={{ display: "flex", alignItems: "center", gap: 4 }}>
          <span style={{
            display: "inline-block",
            width: 14,
            height: 10,
            borderRadius: 2,
            background: item.color,
            opacity: 0.35,
            border: `1px solid ${item.color}`,
          }} />
          <span style={{ fontSize: 11, color: "#4b5563" }}>{item.label}</span>
        </span>
      ))}
    </div>
  );
}


function CriteriaChecklist({ criteria, signal }: { criteria: DiagnosticCriterion[]; signal: SignalData }) {
  return (
    <div>
      {criteria.map((c, i) => {
        const result = c.check(signal);
        const icon = result === true ? "\u2713" : result === false ? "\u2717" : "?";
        const color = result === true ? "#16a34a" : result === false ? "#dc2626" : "#9ca3af";
        const bg = result === true ? "#f0fdf4" : result === false ? "#fef2f2" : "#f9fafb";
        return (
          <div key={i} style={{
            display: "flex", alignItems: "flex-start", gap: 8,
            padding: "4px 8px", borderRadius: 6, background: bg, marginBottom: 4,
          }}>
            <span style={{
              fontWeight: 800, fontSize: 13, color, minWidth: 16, textAlign: "center",
              fontFamily: "monospace",
            }}>
              {icon}
            </span>
            <span style={{ fontSize: 12, color: "#374151", lineHeight: 1.4 }}>
              {c.label}
              {c.weight === "supportive" && (
                <span style={{ fontSize: 10, color: "#9ca3af", marginLeft: 4 }}>(supportive)</span>
              )}
            </span>
          </div>
        );
      })}
    </div>
  );
}


function LeadTable({
  leads, columns, features,
}: {
  leads: string[];
  columns: LeadColumn[];
  features: Record<string, PerLeadFeatures>;
}) {
  return (
    <table style={{ fontSize: 12, borderCollapse: "collapse", width: "100%" }}>
      <thead>
        <tr>
          <th style={thStyle}>Lead</th>
          {columns.map((col) => (
            <th key={col.key} style={thStyle}>{col.label}</th>
          ))}
        </tr>
      </thead>
      <tbody>
        {leads.map((lead) => {
          const f = features[lead];
          if (!f) return null;
          return (
            <tr key={lead}>
              <td style={{ ...tdStyle, fontWeight: 700 }}>{lead}</td>
              {columns.map((col) => {
                const raw = f[col.key];
                const val = typeof raw === "number" ? raw : null;
                const strVal = typeof raw === "string" ? raw : null;
                const isAbnormal = col.threshold != null && val != null && (
                  col.thresholdDir === "above" ? val > col.threshold : val < col.threshold
                );
                const display = val != null
                  ? (col.format ? col.format(val) : val.toFixed(2))
                  : strVal ?? "\u2014";
                return (
                  <td key={col.key} style={{
                    ...tdStyle,
                    color: isAbnormal ? "#dc2626" : "#374151",
                    fontWeight: isAbnormal ? 700 : 400,
                    background: isAbnormal ? "#fef2f2" : "transparent",
                  }}>
                    {display}
                    {isAbnormal && <span style={{ fontSize: 9, marginLeft: 2 }}>!</span>}
                  </td>
                );
              })}
            </tr>
          );
        })}
      </tbody>
    </table>
  );
}

const thStyle: React.CSSProperties = {
  textAlign: "left", padding: "3px 6px", borderBottom: "1px solid #e5e7eb",
  fontSize: 10, fontWeight: 700, color: "#6b7280", textTransform: "uppercase",
};
const tdStyle: React.CSSProperties = {
  padding: "3px 6px", borderBottom: "1px solid #f3f4f6", fontSize: 12,
};


/* ============================================================
 * TEMPLATE FILL
 * ============================================================ */

function fillTemplate(template: string, signal: SignalData | null, finding: DiagnosticFinding): string {
  if (!signal) return finding.clinical_summary;

  const g = signal.global_features;
  const plf = signal.per_lead_features;

  const elevLeads = Object.entries(plf)
    .filter(([, f]) => (f.st_elevation_mv ?? 0) > 0.05)
    .map(([l]) => l);
  const depLeads = Object.entries(plf)
    .filter(([, f]) => (f.st_depression_mv ?? 0) > 0.05)
    .map(([l]) => l);
  const invLeads = Object.entries(plf)
    .filter(([, f]) => f.t_morphology === "inverted")
    .map(([l]) => l);
  const maxSt = elevLeads.length > 0
    ? Math.max(...elevLeads.map((l) => plf[l]?.st_elevation_mv ?? 0)).toFixed(2)
    : "N/A";

  const fmt = (v: number | null | undefined, precision = 0) =>
    v != null ? (precision > 0 ? v.toFixed(precision) : String(Math.round(v))) : "N/A";

  return template
    .replace("{elev_leads}", elevLeads.join(", ") || "none")
    .replace("{dep_leads}", depLeads.join(", ") || "none")
    .replace("{inv_leads}", invLeads.join(", ") || "none")
    .replace("{max_st}", maxSt)
    .replace("{hr}", fmt(g.heart_rate_bpm))
    .replace("{pr_ms}", fmt(g.pr_interval_ms))
    .replace("{qrs_ms}", fmt(g.qrs_duration_ms))
    .replace("{qtc_ms}", fmt(g.qtc_bazett_ms))
    .replace("{axis_deg}", fmt(g.qrs_axis_deg));
}
