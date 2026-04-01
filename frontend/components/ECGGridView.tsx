"use client";

/**
 * Standard clinical 12-lead ECG grid layout (4x3 + rhythm strip).
 *
 * Layout:
 *   Row 1: I    aVR    V1    V4
 *   Row 2: II   aVL    V2    V5
 *   Row 3: III  aVF    V3    V6
 *   Row 4: -------- Lead II rhythm strip (full width) --------
 *
 * Each grid cell shows 2.5s of signal at 25 mm/s.
 * The bottom rhythm strip shows the full recording duration.
 */

import { useRef } from "react";
import LeadStrip from "./LeadStrip";
import type { SignalData, PerLeadFeatures, BeatFiducials } from "@/lib/types";
import type { HighlightRule } from "@/lib/disease-config";

const GRID_LAYOUT = [
  ["I", "aVR", "V1", "V4"],
  ["II", "aVL", "V2", "V5"],
  ["III", "aVF", "V3", "V6"],
];

const RHYTHM_LEAD = "II";

interface ECGGridViewProps {
  signalData: SignalData;
  highlights?: HighlightRule[];
  showFiducials?: boolean;
  selectedLeads?: string[];
  onLeadClick?: (lead: string) => void;
}

const EMPTY_FEATURES: PerLeadFeatures = {};
const EMPTY_BEATS: BeatFiducials[] = [];

export default function ECGGridView({
  signalData,
  highlights = [],
  showFiducials = true,
  selectedLeads,
  onLeadClick,
}: ECGGridViewProps) {
  const containerRef = useRef<HTMLDivElement>(null);

  const isVisible = (lead: string) =>
    !selectedLeads || selectedLeads.includes(lead);

  const getLeadSamples = (lead: string): number[] | undefined =>
    signalData.signal[lead]?.filtered;

  const getLeadBeats = (lead: string): BeatFiducials[] =>
    showFiducials ? (signalData.fiducials[lead] ?? EMPTY_BEATS) : EMPTY_BEATS;

  const getLeadFeatures = (lead: string): PerLeadFeatures =>
    signalData.per_lead_features[lead] ?? EMPTY_FEATURES;

  const cellDurationSec = 2.5;
  const cellSampleCount = Math.floor(cellDurationSec * signalData.fs);

  return (
    <div ref={containerRef} style={{ width: "100%", background: "#fff", borderRadius: 8, overflow: "hidden", border: "1px solid #e5e7eb" }}>
      {/* Header */}
      <div style={{
        display: "flex", justifyContent: "space-between", alignItems: "center",
        padding: "8px 16px", borderBottom: "1px solid #e5e7eb", background: "#f9fafb",
      }}>
        <span style={{ fontWeight: 600, fontSize: 14 }}>12-Lead ECG</span>
        <div style={{ display: "flex", gap: 16, fontSize: 12, color: "#6b7280" }}>
          <span>25 mm/s</span>
          <span>10 mm/mV</span>
        </div>
      </div>

      {/* 4x3 Grid */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 0 }}>
        {GRID_LAYOUT.map((row) =>
          row.map((lead) => {
            const samples = getLeadSamples(lead);
            const visible = isVisible(lead);

            return (
              <div
                key={lead}
                onClick={() => onLeadClick?.(lead)}
                style={{
                  borderRight: "1px solid #d1d5db",
                  borderBottom: "1px solid #d1d5db",
                  cursor: onLeadClick ? "pointer" : "default",
                  opacity: visible ? 1 : 0.3,
                  position: "relative",
                  overflow: "hidden",
                }}
              >
                {samples && visible ? (
                  <LeadStrip
                    leadName={lead}
                    samples={samples.slice(0, cellSampleCount)}
                    fs={signalData.fs}
                    beats={getLeadBeats(lead)}
                    features={getLeadFeatures(lead)}
                    highlights={highlights}
                    pxPerMm={2.5}
                  />
                ) : (
                  <div style={{ height: 100, display: "flex", alignItems: "center", justifyContent: "center", color: "#9ca3af", fontSize: 12 }}>
                    {visible ? "No data" : "Hidden"}
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>

      {/* Rhythm strip - full width lead II */}
      <div style={{ borderTop: "2px solid #374151", position: "relative", overflow: "hidden" }}>
        <div style={{
          position: "absolute", top: 4, left: 8, zIndex: 2,
          fontSize: 12, fontWeight: 700, color: "#1f2937",
          background: "rgba(255,255,255,0.85)", padding: "1px 4px", borderRadius: 2,
        }}>
          {RHYTHM_LEAD} — Rhythm Strip
        </div>
        {(() => {
          const samples = getLeadSamples(RHYTHM_LEAD);
          if (!samples) {
            return (
              <div style={{ height: 100, display: "flex", alignItems: "center", justifyContent: "center", color: "#9ca3af" }}>
                No rhythm data
              </div>
            );
          }
          return (
            <LeadStrip
              leadName={RHYTHM_LEAD}
              samples={samples}
              fs={signalData.fs}
              beats={getLeadBeats(RHYTHM_LEAD)}
              features={getLeadFeatures(RHYTHM_LEAD)}
              highlights={highlights}
              pxPerMm={2.5}
              interactive
            />
          );
        })()}
      </div>
    </div>
  );
}
