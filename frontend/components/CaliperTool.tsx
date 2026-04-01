/**
 * Clinical caliper tool for measuring intervals and amplitudes on ECG strips.
 *
 * Renders SVG marker lines (for use inside an SVG parent) and a floating
 * measurement display (HTML overlay). Toggle on/off via the `active` prop.
 */
"use client";

import { useState, useCallback } from "react";

interface CaliperPoint {
  x: number;
  y: number;
  sampleIdx: number;
  amplitudeMv: number;
}

interface CaliperToolProps {
  active: boolean;
  sampleRate: number;
  onMeasurement?: (measurement: CaliperMeasurement) => void;
}

interface CaliperMeasurement {
  intervalMs: number;
  amplitudeDiffMv: number;
  heartRateBpm: number | null;
}

export type { CaliperMeasurement, CaliperToolProps };

export default function CaliperTool({ active, sampleRate, onMeasurement }: CaliperToolProps) {
  const [point1, setPoint1] = useState<CaliperPoint | null>(null);
  const [point2, setPoint2] = useState<CaliperPoint | null>(null);

  const handleClick = useCallback(
    (e: React.MouseEvent<SVGSVGElement>) => {
      if (!active) return;

      const svg = e.currentTarget;
      const rect = svg.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;

      // Placeholder coordinate transforms — the parent component must map
      // pixel coordinates to sample indices and mV values based on its own
      // viewBox / scale configuration.
      const sampleIdx = 0;
      const amplitudeMv = 0;

      const point: CaliperPoint = { x, y, sampleIdx, amplitudeMv };

      if (!point1) {
        setPoint1(point);
        setPoint2(null);
      } else if (!point2) {
        setPoint2(point);
        const intervalMs = (Math.abs(point.sampleIdx - point1.sampleIdx) / sampleRate) * 1000;
        const amplitudeDiffMv = Math.abs(point.amplitudeMv - point1.amplitudeMv);
        const heartRateBpm = intervalMs > 200 ? 60000 / intervalMs : null;
        onMeasurement?.({ intervalMs, amplitudeDiffMv, heartRateBpm });
      } else {
        setPoint1(point);
        setPoint2(null);
      }
    },
    [active, point1, point2, sampleRate, onMeasurement],
  );

  const reset = () => {
    setPoint1(null);
    setPoint2(null);
  };

  if (!active) return null;

  const measurement =
    point1 && point2
      ? {
          intervalMs: (Math.abs(point2.sampleIdx - point1.sampleIdx) / sampleRate) * 1000,
          amplitudeDiffMv: Math.abs(point2.amplitudeMv - point1.amplitudeMv),
          heartRateBpm: null as number | null,
        }
      : null;

  if (measurement && measurement.intervalMs > 200) {
    measurement.heartRateBpm = 60000 / measurement.intervalMs;
  }

  return (
    <>
      {/* Caliper overlay — rendered inside SVG */}
      {point1 && (
        <line
          x1={point1.x}
          y1={0}
          x2={point1.x}
          y2={9999}
          stroke="#dc2626"
          strokeWidth={1.5}
          strokeDasharray="4,4"
        />
      )}
      {point2 && (
        <>
          <line
            x1={point2.x}
            y1={0}
            x2={point2.x}
            y2={9999}
            stroke="#dc2626"
            strokeWidth={1.5}
            strokeDasharray="4,4"
          />
          <line
            x1={point1!.x}
            y1={point1!.y}
            x2={point2.x}
            y2={point2.y}
            stroke="#dc2626"
            strokeWidth={1}
          />
        </>
      )}

      {/* Measurement display — rendered outside SVG */}
      {measurement && (
        <div
          style={{
            position: "absolute",
            top: 8,
            right: 8,
            zIndex: 10,
            background: "rgba(255,255,255,0.95)",
            border: "2px solid #dc2626",
            borderRadius: 8,
            padding: "8px 12px",
            fontSize: 13,
            fontWeight: 500,
            boxShadow: "0 2px 8px rgba(0,0,0,0.15)",
          }}
        >
          <div style={{ fontWeight: 700, marginBottom: 4, color: "#dc2626" }}>Caliper</div>
          <div>
            Interval: <strong>{measurement.intervalMs.toFixed(0)} ms</strong>
          </div>
          <div>
            Amplitude: <strong>{measurement.amplitudeDiffMv.toFixed(2)} mV</strong>
          </div>
          {measurement.heartRateBpm && (
            <div>
              Rate: <strong>{measurement.heartRateBpm.toFixed(0)} bpm</strong>
            </div>
          )}
          <button
            onClick={reset}
            style={{
              marginTop: 4,
              fontSize: 11,
              color: "#6b7280",
              cursor: "pointer",
              background: "none",
              border: "none",
              textDecoration: "underline",
            }}
          >
            Reset
          </button>
        </div>
      )}
    </>
  );
}
