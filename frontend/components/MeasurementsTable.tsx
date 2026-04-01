/**
 * Measurements table with traffic-light color coding for clinical normal ranges.
 */
"use client";

import type { Measurements, OverallQuality } from "@/lib/types";

interface Props {
  measurements: Measurements;
  overallQuality: OverallQuality;
}

const QUALITY_COLOR: Record<OverallQuality, string> = {
  GOOD: "#22c55e",
  ACCEPTABLE: "#f59e0b",
  POOR: "#ef4444",
  UNINTERPRETABLE: "#9ca3af",
};

type MeasurementStatus = "normal" | "borderline" | "abnormal" | "unknown";

function classifyMeasurement(name: string, value: number | null | undefined): MeasurementStatus {
  if (value === null || value === undefined) return "unknown";

  const ranges: Record<string, [number, number, number, number]> = {
    // [abnormal_low, borderline_low, borderline_high, abnormal_high]
    heart_rate: [50, 60, 100, 110],
    pr_interval: [100, 120, 200, 220],
    qrs_duration: [0, 0, 120, 140],
    qtc: [0, 0, 440, 470],
    qrs_axis: [-45, -30, 90, 110],
  };

  const range = ranges[name];
  if (!range) return "unknown";

  if (value < range[0] || value > range[3]) return "abnormal";
  if (value < range[1] || value > range[2]) return "borderline";
  return "normal";
}

const STATUS_COLORS: Record<MeasurementStatus, string> = {
  normal: "#16a34a",
  borderline: "#d97706",
  abnormal: "#dc2626",
  unknown: "#9ca3af",
};

const STATUS_BG: Record<MeasurementStatus, string> = {
  normal: "#f0fdf4",
  borderline: "#fffbeb",
  abnormal: "#fef2f2",
  unknown: "#f9fafb",
};

function row(
  label: string,
  value: string | number | null | undefined,
  unit?: string,
  measurementKey?: string,
) {
  if (value === null || value === undefined) return null;

  const numericValue = typeof value === "number" ? value : undefined;
  const status = measurementKey ? classifyMeasurement(measurementKey, numericValue) : "unknown";
  const dotColor = STATUS_COLORS[status];
  const bgColor = STATUS_BG[status];

  return (
    <tr key={label} style={{ borderBottom: "1px solid #e5e7eb", background: bgColor }}>
      <td style={{ padding: "6px 12px", color: "#6b7280", fontWeight: 500 }}>{label}</td>
      <td style={{ padding: "6px 12px", display: "flex", alignItems: "center", gap: 8 }}>
        {measurementKey && status !== "unknown" && (
          <span
            style={{
              display: "inline-block",
              width: 8,
              height: 8,
              borderRadius: "50%",
              background: dotColor,
              flexShrink: 0,
            }}
          />
        )}
        <span style={{ color: status === "abnormal" ? "#dc2626" : status === "borderline" ? "#92400e" : undefined, fontWeight: status === "abnormal" ? 600 : undefined }}>
          {typeof value === "number" ? value.toFixed(1) : value}
          {unit && <span style={{ color: "#9ca3af", marginLeft: 4 }}>{unit}</span>}
        </span>
      </td>
    </tr>
  );
}

export default function MeasurementsTable({ measurements: m, overallQuality }: Props) {
  const color = QUALITY_COLOR[overallQuality] ?? "#9ca3af";
  return (
    <div style={{ border: "1px solid #e5e7eb", borderRadius: 8, overflow: "hidden" }}>
      <div style={{ background: "#f9fafb", padding: "8px 12px", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <span style={{ fontWeight: 600 }}>Measurements</span>
        <span style={{ color, fontWeight: 600, fontSize: 13 }}>Quality: {overallQuality}</span>
      </div>
      <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 14 }}>
        <tbody>
          {row("Heart Rate", m.heart_rate_ventricular_bpm, "bpm", "heart_rate")}
          {row("PR Interval", m.pr_interval_ms, "ms", "pr_interval")}
          {row("QRS Duration", m.qrs_duration_global_ms, "ms", "qrs_duration")}
          {row("QTc (Bazett)", m.qtc_bazett_ms, "ms", "qtc")}
          {row("QRS Axis", m.qrs_axis_deg, "°", "qrs_axis")}
          {m.rhythm && row("Rhythm", m.rhythm)}
          {m.lbbb && row("LBBB", "Present")}
          {m.rbbb && row("RBBB", "Present")}
          {m.lvh_criteria_met && row("LVH", "Criteria met")}
        </tbody>
      </table>
    </div>
  );
}
