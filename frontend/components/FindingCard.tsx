"use client";

import type { DiagnosticFinding, Confidence } from "@/lib/types";
import OverrideModal, { type UserRole } from "./OverrideModal";

interface Props {
  finding: DiagnosticFinding;
  index: number;
  ecgId?: string;
  userRole?: UserRole;
  onOverride?: (ecgId: string, findingType: string, reason: string) => Promise<void>;
}

const CONF_COLOR: Record<Confidence, string> = {
  HIGH: "#dc2626",
  MODERATE: "#d97706",
  LOW: "#2563eb",
  INSUFFICIENT_EVIDENCE: "#9ca3af",
};

const CONF_BG: Record<Confidence, string> = {
  HIGH: "#fef2f2",
  MODERATE: "#fffbeb",
  LOW: "#eff6ff",
  INSUFFICIENT_EVIDENCE: "#f9fafb",
};

export default function FindingCard({ finding, index, ecgId, userRole, onOverride }: Props) {
  const color = CONF_COLOR[finding.confidence];
  const bg = CONF_BG[finding.confidence];

  return (
    <div
      style={{
        border: `1px solid ${color}40`,
        borderLeft: `4px solid ${color}`,
        borderRadius: 8,
        padding: "12px 16px",
        background: bg,
        marginBottom: 12,
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 6 }}>
        <span style={{ fontWeight: 700, fontSize: 15 }}>
          {index + 1}. {finding.finding_type.replace(/_/g, " ").toUpperCase()}
        </span>
        <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
          {ecgId && userRole && onOverride && (
            <OverrideModal
              ecgId={ecgId}
              findingType={finding.finding_type}
              userRole={userRole}
              onOverride={onOverride}
            />
          )}
          <span
          style={{
            fontSize: 11,
            fontWeight: 700,
            color,
            background: `${color}20`,
            padding: "2px 8px",
            borderRadius: 12,
            letterSpacing: "0.05em",
          }}
        >
          {finding.confidence.replace("_", " ")}
        </span>
        </div>
      </div>

      <p style={{ margin: "0 0 6px 0", fontSize: 14 }}>{finding.clinical_summary}</p>

      {finding.clinical_summary_fa && (
        <p style={{ margin: "0 0 6px 0", fontSize: 14, direction: "rtl", color: "#374151" }}>
          {finding.clinical_summary_fa}
        </p>
      )}

      {finding.technical_detail && (
        <p style={{ margin: "0 0 6px 0", fontSize: 12, color: "#6b7280", fontFamily: "monospace" }}>
          {finding.technical_detail}
        </p>
      )}

      {finding.citations && finding.citations.length > 0 && (
        <div style={{ marginTop: 8, fontSize: 12, color: "#6b7280" }}>
          {finding.citations.map((c, i) => (
            <div key={i}>
              [{i + 1}] {c.book.toUpperCase()} | {c.chapter} | p.{c.page_number}
            </div>
          ))}
        </div>
      )}

      {finding.rag_invoked && finding.citations.length === 0 && (
        <div style={{ fontSize: 12, color: "#9ca3af", marginTop: 6 }}>
          No textbook source retrieved for this finding.
        </div>
      )}
    </div>
  );
}
