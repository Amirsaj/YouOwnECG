"use client";

import { useEffect, useRef, useState } from "react";
import type { StatAlert } from "@/lib/types";

interface Props {
  alerts: StatAlert[];
}

export default function StatAlertBanner({ alerts }: Props) {
  const [minimised, setMinimised] = useState(false);
  const [dismissed, setDismissed] = useState(false);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    if (alerts.length === 0) return;
    // Auto-minimise to mini-strip after 10s (Node 3.3: not full dismiss)
    timerRef.current = setTimeout(() => setMinimised(true), 10_000);
    return () => {
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, [alerts.length]);

  if (alerts.length === 0 || dismissed) return null;

  if (minimised) {
    return (
      <div
        role="alert"
        onClick={() => setMinimised(false)}
        style={{
          position: "sticky",
          top: 0,
          zIndex: 100,
          background: "#dc2626",
          color: "#fff",
          padding: "4px 16px",
          fontSize: 13,
          fontWeight: 700,
          cursor: "pointer",
          display: "flex",
          alignItems: "center",
          gap: 8,
        }}
      >
        ⚠ STAT ALERT: {alerts.map((a) => a.finding_type).join(", ")} — click to expand
      </div>
    );
  }

  return (
    <div
      role="alert"
      style={{
        position: "sticky",
        top: 0,
        zIndex: 100,
        background: "#dc2626",
        color: "#fff",
        padding: "12px 16px",
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
        <div style={{ fontWeight: 800, fontSize: 16, marginBottom: 8 }}>
          ⚠ STAT ALERT — IMMEDIATE CLINICAL ATTENTION REQUIRED
        </div>
        <div style={{ display: "flex", gap: 12 }}>
          <button
            onClick={() => setMinimised(true)}
            style={{ background: "rgba(255,255,255,0.2)", border: "none", color: "#fff", padding: "2px 10px", borderRadius: 4, cursor: "pointer", fontSize: 12 }}
          >
            Minimise
          </button>
          <button
            onClick={() => setDismissed(true)}
            style={{ background: "rgba(255,255,255,0.2)", border: "none", color: "#fff", padding: "2px 10px", borderRadius: 4, cursor: "pointer", fontSize: 12 }}
          >
            Acknowledge
          </button>
        </div>
      </div>
      {alerts.map((a, i) => (
        <div key={i} style={{ marginBottom: 4, fontSize: 14 }}>
          <strong>{a.finding_type.toUpperCase().replace(/_/g, " ")}</strong>
          {" — "}{a.message}
        </div>
      ))}
      <div style={{ marginTop: 8, fontSize: 11, opacity: 0.9 }}>
        AI-GENERATED — NOT A CLINICAL DIAGNOSIS — CLINICAL CORRELATION REQUIRED
      </div>
    </div>
  );
}
