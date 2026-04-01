"use client";

import { useState } from "react";

export type UserRole = "NURSE" | "TECHNICIAN" | "PHYSICIAN" | "CARDIOLOGIST";

interface Props {
  ecgId: string;
  findingType: string;
  userRole: UserRole;
  onOverride?: (ecgId: string, findingType: string, reason: string) => Promise<void>;
}

const PERMITTED_ROLES: UserRole[] = ["CARDIOLOGIST", "PHYSICIAN"];

export default function OverrideModal({ ecgId, findingType, userRole, onOverride }: Props) {
  const [open, setOpen] = useState(false);
  const [reason, setReason] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [done, setDone] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // VT-3.4: override button absent for non-permitted roles
  if (!PERMITTED_ROLES.includes(userRole)) return null;

  async function handleConfirm() {
    if (!reason.trim()) { setError("Override reason is required."); return; }
    setError(null);
    setSubmitting(true);
    try {
      await onOverride?.(ecgId, findingType, reason.trim());
      setDone(true);
      setOpen(false);
      setReason("");
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setSubmitting(false);
    }
  }

  if (done) {
    return <span style={{ fontSize: 12, color: "#9ca3af" }}>Override recorded</span>;
  }

  return (
    <>
      <button
        onClick={() => setOpen(true)}
        style={{
          fontSize: 12,
          padding: "3px 10px",
          background: "transparent",
          border: "1px solid #d97706",
          color: "#d97706",
          borderRadius: 6,
          cursor: "pointer",
          fontWeight: 600,
        }}
      >
        Override
      </button>

      {open && (
        <div
          style={{
            position: "fixed",
            inset: 0,
            background: "rgba(0,0,0,0.4)",
            zIndex: 200,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
          onClick={(e) => { if (e.target === e.currentTarget) setOpen(false); }}
        >
          <div
            style={{
              background: "#fff",
              borderRadius: 12,
              padding: "24px",
              width: 420,
              boxShadow: "0 20px 60px rgba(0,0,0,0.3)",
            }}
          >
            <h3 style={{ margin: "0 0 8px 0", fontSize: 16, fontWeight: 700 }}>Override Finding</h3>
            <p style={{ margin: "0 0 16px 0", fontSize: 13, color: "#6b7280" }}>
              Overriding: <strong>{findingType.replace(/_/g, " ").toUpperCase()}</strong>
              <br />
              This action is logged in the audit trail with your user ID.
            </p>

            <label style={{ display: "block", fontSize: 13, fontWeight: 600, marginBottom: 6 }}>
              Clinical reason <span style={{ color: "#dc2626" }}>*</span>
            </label>
            <textarea
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              placeholder="Enter clinical justification for override..."
              rows={3}
              style={{
                width: "100%",
                padding: "8px 12px",
                border: "1px solid #d1d5db",
                borderRadius: 8,
                fontSize: 13,
                resize: "vertical",
                boxSizing: "border-box",
              }}
            />

            {error && (
              <div style={{ marginTop: 8, fontSize: 12, color: "#dc2626" }}>{error}</div>
            )}

            <div style={{ marginTop: 16, padding: "10px 12px", background: "#fffbeb", border: "1px solid #fcd34d", borderRadius: 8, fontSize: 12, color: "#92400e" }}>
              ⚠ Override does not modify the AI analysis. It records your clinical assessment alongside the AI finding.
            </div>

            <div style={{ marginTop: 16, display: "flex", gap: 8, justifyContent: "flex-end" }}>
              <button
                onClick={() => { setOpen(false); setReason(""); setError(null); }}
                disabled={submitting}
                style={{ padding: "8px 16px", background: "#f9fafb", border: "1px solid #d1d5db", borderRadius: 8, cursor: "pointer", fontSize: 13 }}
              >
                Cancel
              </button>
              <button
                onClick={handleConfirm}
                disabled={submitting || !reason.trim()}
                style={{
                  padding: "8px 16px",
                  background: submitting ? "#9ca3af" : "#d97706",
                  color: "#fff",
                  border: "none",
                  borderRadius: 8,
                  cursor: submitting ? "not-allowed" : "pointer",
                  fontWeight: 600,
                  fontSize: 13,
                }}
              >
                {submitting ? "Recording..." : "Confirm Override"}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
