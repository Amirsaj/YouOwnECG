"use client";

import { useState } from "react";
import FindingCard from "@/components/FindingCard";
import DiseaseDashboard from "@/components/DiseaseDashboard";
import ECGViewer from "@/components/ECGViewer";
import type { DiagnosticResult } from "@/lib/types";
import type { UserRole } from "@/components/OverrideModal";
import { recordOverride } from "@/lib/api";
import { getDiseaseConfig } from "@/lib/disease-config";

interface Props {
  result: DiagnosticResult;
  ecgImageBase64?: string | null;
}

// In a real deployment this would come from the auth session.
// For development, default to PHYSICIAN so override is visible.
const DEV_USER_ROLE: UserRole = "PHYSICIAN";
const DEV_USER_ID = "dev-user-001";

export default function ResultClient({ result, ecgImageBase64 }: Props) {
  const [activeTab, setActiveTab] = useState<string | null>(null);

  async function handleOverride(ecgId: string, findingType: string, reason: string) {
    await recordOverride(ecgId, findingType, reason, DEV_USER_ROLE, DEV_USER_ID);
  }

  // Split findings into those with disease dashboards and those without
  const dashboardFindings = result.findings.filter((f) => getDiseaseConfig(f.finding_type) != null);
  const otherFindings = result.findings.filter((f) => getDiseaseConfig(f.finding_type) == null);

  return (
    <>
      {ecgImageBase64 && (
        <div style={{ marginBottom: 24 }}>
          <ECGViewer imageBase64={ecgImageBase64} ecgId={result.ecg_id} />
        </div>
      )}

      {/* Disease Dashboard Tabs */}
      {dashboardFindings.length > 0 && (
        <div style={{ marginBottom: 32 }}>
          <h2 style={{ fontSize: 16, fontWeight: 700, marginBottom: 12 }}>
            Disease Dashboards ({dashboardFindings.length})
          </h2>

          {/* Tab bar */}
          <div style={{
            display: "flex",
            gap: 4,
            marginBottom: 12,
            overflowX: "auto",
            paddingBottom: 4,
          }}>
            {dashboardFindings.map((f) => {
              const cfg = getDiseaseConfig(f.finding_type);
              const isActive = activeTab === f.finding_type;
              return (
                <button
                  key={f.finding_type}
                  onClick={() => setActiveTab(isActive ? null : f.finding_type)}
                  style={{
                    padding: "6px 14px",
                    borderRadius: 8,
                    border: isActive ? "2px solid #2563eb" : "1px solid #d1d5db",
                    background: isActive ? "#eff6ff" : "#fff",
                    fontSize: 13,
                    fontWeight: isActive ? 700 : 500,
                    cursor: "pointer",
                    whiteSpace: "nowrap",
                    color: isActive ? "#1d4ed8" : "#374151",
                    display: "flex",
                    alignItems: "center",
                    gap: 6,
                  }}
                >
                  {cfg?.stat && (
                    <span style={{
                      width: 6, height: 6,
                      borderRadius: "50%",
                      background: "#dc2626",
                      display: "inline-block",
                    }} />
                  )}
                  {cfg?.label ?? f.finding_type}
                </button>
              );
            })}
          </div>

          {/* Active dashboard or all collapsed */}
          {activeTab ? (
            dashboardFindings
              .filter((f) => f.finding_type === activeTab)
              .map((f) => (
                <DiseaseDashboard key={f.finding_type} finding={f} ecgId={result.ecg_id} />
              ))
          ) : (
            dashboardFindings.map((f) => (
              <DiseaseDashboard key={f.finding_type} finding={f} ecgId={result.ecg_id} />
            ))
          )}
        </div>
      )}

      {/* Other findings (no disease dashboard available) */}
      {otherFindings.length > 0 && (
        <div style={{ marginBottom: 32 }}>
          <h2 style={{ fontSize: 16, fontWeight: 700, marginBottom: 12 }}>
            Other Findings ({otherFindings.length})
          </h2>
          {otherFindings.map((f, i) => (
            <FindingCard
              key={f.finding_type}
              finding={f}
              index={i}
              ecgId={result.ecg_id}
              userRole={DEV_USER_ROLE}
              onOverride={handleOverride}
            />
          ))}
        </div>
      )}

      {/* No findings at all */}
      {result.findings.length === 0 && (
        <div style={{ marginBottom: 32 }}>
          <h2 style={{ fontSize: 16, fontWeight: 700, marginBottom: 12 }}>Findings</h2>
          <p style={{ color: "#6b7280", fontSize: 14 }}>No significant findings detected.</p>
        </div>
      )}
    </>
  );
}
