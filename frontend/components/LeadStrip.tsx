"use client";

/**
 * SVG-based single-lead ECG strip renderer (Node 3.2).
 *
 * Clinical-standard display:
 * - ECG grid paper background (small 1mm boxes, large 5mm boxes)
 * - Fixed speed: 25 mm/s
 * - Fixed gain: 10 mm/mV (1 mV = 10 mm on paper)
 * - 1 mV calibration pulse at strip start
 * - Arrow annotations pointing to highlighted features
 * - ST/PR/QRS measurement labels
 */

import { useState, useCallback, type ReactElement } from "react";
import type { BeatFiducials, PerLeadFeatures } from "@/lib/types";
import type { HighlightRule } from "@/lib/disease-config";

interface Props {
  leadName: string;
  /** Filtered signal samples (safe window, in uV from preprocessed signal) */
  samples: number[];
  /** Sample rate in Hz (after downsampling) */
  fs: number;
  /** Per-beat fiducial indices (already scaled for downsampling) */
  beats: BeatFiducials[];
  /** Per-lead computed features */
  features: PerLeadFeatures;
  /** Highlight rules from disease config */
  highlights: HighlightRule[];
  /** Pixels per millimeter of ECG paper (controls zoom level) */
  pxPerMm?: number;
  /** Enable mouse-wheel zoom and click-drag pan */
  interactive?: boolean;
}

/* ---- Clinical constants ---- */
const SPEED_MM_PER_S = 25;       // 25 mm/s — standard paper speed
const GAIN_MM_PER_MV = 10;       // 10 mm/mV — standard gain
const CAL_PULSE_MV = 1.0;        // 1 mV calibration pulse
const CAL_PULSE_MS = 200;        // 200 ms wide calibration pulse
const LEAD_LABEL_W_MM = 12;      // space for lead label + cal pulse
const STRIP_HEIGHT_MV = 4;       // ±2 mV vertical range (4 mV total)

/* ---- Grid colours (standard ECG paper) ---- */
const GRID_SMALL = "#f4c2c2";    // light pink — 1mm boxes
const GRID_LARGE = "#e8a0a0";    // darker pink — 5mm boxes
const GRID_BG    = "#fff5f5";    // very light pink background

export default function LeadStrip({
  leadName,
  samples,
  fs,
  beats,
  features,
  highlights,
  pxPerMm = 4,
  interactive = false,
}: Props) {
  const [zoomLevel, setZoomLevel] = useState(1);
  const [panOffset, setPanOffset] = useState(0);
  const [isDragging, setIsDragging] = useState(false);
  const [dragStartX, setDragStartX] = useState(0);
  const [tooltip, setTooltip] = useState<{ x: number; y: number; text: string } | null>(null);

  const handleWheel = useCallback((e: React.WheelEvent) => {
    if (!interactive) return;
    e.preventDefault();
    setZoomLevel((prev) => {
      const next = e.deltaY > 0 ? prev * 0.8 : prev * 1.25;
      return Math.max(0.5, Math.min(4, next));
    });
  }, [interactive]);

  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    if (!interactive) return;
    setIsDragging(true);
    setDragStartX(e.clientX);
    setTooltip(null);
  }, [interactive]);

  const handleMouseMove = useCallback((e: React.MouseEvent) => {
    if (!isDragging) return;
    const dx = e.clientX - dragStartX;
    const samplesPerPx = fs / (SPEED_MM_PER_S * pxPerMm * zoomLevel);
    setPanOffset((prev) => Math.max(0, Math.min(samples.length - 1, prev - dx * samplesPerPx)));
    setDragStartX(e.clientX);
  }, [isDragging, dragStartX, fs, pxPerMm, zoomLevel, samples.length]);

  const handleMouseUp = useCallback(() => {
    setIsDragging(false);
  }, []);

  if (!samples || samples.length === 0) return null;

  // When interactive, apply zoom and pan to select a visible window
  const effectiveSpeed = SPEED_MM_PER_S * zoomLevel;
  const startSample = interactive ? Math.floor(panOffset) : 0;
  const visibleCount = interactive
    ? Math.min(samples.length - startSample, Math.ceil(samples.length / zoomLevel))
    : samples.length;
  const visibleSamples = interactive
    ? samples.slice(startSample, startSample + visibleCount)
    : samples;

  const durationS = visibleSamples.length / fs;
  const durationMm = durationS * effectiveSpeed;
  const totalWidthMm = LEAD_LABEL_W_MM + durationMm;
  const heightMm = STRIP_HEIGHT_MV * GAIN_MM_PER_MV;

  const W = totalWidthMm * pxPerMm;
  const H = heightMm * pxPerMm;
  const labelW = LEAD_LABEL_W_MM * pxPerMm;
  const plotW = durationMm * pxPerMm;

  const uvPerMm = 1000 / GAIN_MM_PER_MV;
  const midY = H / 2;

  const toX = (sampleIdx: number) => labelW + (sampleIdx / visibleSamples.length) * plotW;
  const toY = (uv: number) => midY - (uv / uvPerMm) * pxPerMm;

  /* ---- Grid lines ---- */
  const gridLines: ReactElement[] = [];
  const smallBoxPx = 1 * pxPerMm;
  const largeBoxPx = 5 * pxPerMm;

  // Vertical grid lines (time axis)
  for (let x = labelW; x <= W; x += smallBoxPx) {
    const isLarge = Math.abs((x - labelW) % largeBoxPx) < 0.5;
    gridLines.push(
      <line key={`gv-${x}`} x1={x} y1={0} x2={x} y2={H}
        stroke={isLarge ? GRID_LARGE : GRID_SMALL} strokeWidth={isLarge ? 0.8 : 0.4} />
    );
  }
  // Horizontal grid lines (amplitude axis)
  for (let y = 0; y <= H; y += smallBoxPx) {
    const isLarge = Math.abs(y % largeBoxPx) < 0.5;
    gridLines.push(
      <line key={`gh-${y}`} x1={labelW} y1={y} x2={W} y2={y}
        stroke={isLarge ? GRID_LARGE : GRID_SMALL} strokeWidth={isLarge ? 0.8 : 0.4} />
    );
  }

  /* ---- Calibration pulse (1 mV square wave in label area) ---- */
  const calStartX = 4 * pxPerMm;
  const calEndX = calStartX + (CAL_PULSE_MS / 1000) * SPEED_MM_PER_S * pxPerMm;
  const calTopY = toY(CAL_PULSE_MV * 1000); // 1 mV = 1000 µV
  const calBaseY = toY(0);
  const calPath = `M${calStartX},${calBaseY} L${calStartX},${calTopY} L${calEndX},${calTopY} L${calEndX},${calBaseY}`;

  /* ---- Signal trace ---- */
  const signalPath = visibleSamples
    .map((v, i) => `${i === 0 ? "M" : "L"}${toX(i).toFixed(1)},${toY(v).toFixed(1)}`)
    .join(" ");

  /* ---- Highlight overlays ---- */
  const highlightElems: ReactElement[] = [];
  for (const beat of beats) {
    for (const hl of highlights) {
      const bounds = getRegionBounds(beat, hl.region);
      if (!bounds) continue;
      if (!shouldHighlight(hl, features)) continue;
      const [si, ei] = bounds;
      // Adjust indices for the visible window
      const adjSi = si - startSample;
      const adjEi = ei - startSample;
      if (adjEi < 0 || adjSi >= visibleSamples.length) continue;
      const clampSi = Math.max(0, adjSi);
      const clampEi = Math.min(visibleSamples.length - 1, adjEi);

      const x1 = toX(clampSi);
      const x2 = toX(clampEi);
      highlightElems.push(
        <rect key={`hl-${beat.r ?? si}-${hl.region}`}
          x={x1} y={0} width={Math.max(x2 - x1, 2)} height={H}
          fill={hl.color} opacity={0.12} />
      );

      const midIdx = Math.floor((clampSi + clampEi) / 2);
      if (midIdx >= 0 && midIdx < visibleSamples.length) {
        const ax = toX(midIdx);
        const ay = toY(visibleSamples[midIdx]);
        const arrowY = ay < H / 2 ? ay + 14 : ay - 14;
        const arrowDir = ay < H / 2 ? -1 : 1;
        highlightElems.push(
          <g key={`arr-${beat.r ?? si}-${hl.region}`}>
            <line x1={ax} y1={arrowY} x2={ax} y2={ay + arrowDir * 2}
              stroke={hl.color} strokeWidth={1.2} markerEnd="none" />
            <polygon
              points={`${ax},${ay + arrowDir * 2} ${ax - 3},${arrowY} ${ax + 3},${arrowY}`}
              fill={hl.color} opacity={0.7} />
            <text x={ax + 5} y={arrowY + (arrowDir > 0 ? -3 : 10)}
              fontSize={8} fontWeight={600} fill={hl.color} opacity={0.9}>
              {regionLabel(hl)}
            </text>
          </g>
        );
      }
    }
  }

  /* ---- Fiducial markers on first beat only (to avoid clutter) ---- */
  const fiducialElems: ReactElement[] = [];
  const firstBeat = beats[0];
  if (firstBeat) {
    const adjR = firstBeat.r != null ? firstBeat.r - startSample : null;
    if (adjR != null && adjR >= 0 && adjR < visibleSamples.length) {
      const rx = toX(adjR);
      const ry = toY(visibleSamples[adjR]);
      fiducialElems.push(
        <polygon key="r-mark"
          points={`${rx},${ry - 6} ${rx - 3},${ry - 11} ${rx + 3},${ry - 11}`}
          fill="#dc2626" opacity={0.5}
          style={{ cursor: interactive ? "pointer" : "default" }}
          onClick={(e) => {
            if (!interactive) return;
            e.stopPropagation();
            setTooltip({ x: rx, y: ry - 16, text: `R-peak: ${visibleSamples[adjR].toFixed(0)} uV` });
          }}
        />
      );
    }
    const brackets: [number | null, number | null, string, string][] = [
      [firstBeat.pon, firstBeat.poff, "#7c3aed", "P"],
      [firstBeat.qrson, firstBeat.qrsoff, "#dc2626", "QRS"],
      [firstBeat.ton, firstBeat.toff, "#2563eb", "T"],
    ];
    for (const [s, e, color, label] of brackets) {
      if (s == null || e == null) continue;
      const adjS = s - startSample;
      const adjE = e - startSample;
      if (adjS >= visibleSamples.length || adjE < 0) continue;
      const clampS = Math.max(0, adjS);
      const clampE = Math.min(visibleSamples.length - 1, adjE);
      const bx1 = toX(clampS);
      const bx2 = toX(clampE);
      const by = H - 3 * pxPerMm;
      const durationMs = ((e - s) / fs * 1000).toFixed(0);
      fiducialElems.push(
        <g key={`br-${label}`}
          style={{ cursor: interactive ? "pointer" : "default" }}
          onClick={(e_) => {
            if (!interactive) return;
            e_.stopPropagation();
            setTooltip({ x: (bx1 + bx2) / 2, y: by - 14, text: `${label}: ${durationMs} ms` });
          }}
        >
          <line x1={bx1} y1={by} x2={bx2} y2={by} stroke={color} strokeWidth={1.5} opacity={0.5} />
          <line x1={bx1} y1={by - 2} x2={bx1} y2={by + 2} stroke={color} strokeWidth={1} opacity={0.5} />
          <line x1={bx2} y1={by - 2} x2={bx2} y2={by + 2} stroke={color} strokeWidth={1} opacity={0.5} />
          <text x={(bx1 + bx2) / 2} y={by - 3} fontSize={7} fontWeight={600}
            fill={color} textAnchor="middle" opacity={0.6}>{label}</text>
        </g>
      );
    }
  }

  /* ---- ST / PR measurement annotation (first beat) ---- */
  const measureLabels: ReactElement[] = [];
  const adjQrsoff = firstBeat?.qrsoff != null ? firstBeat.qrsoff - startSample : null;
  if (firstBeat && adjQrsoff != null && adjQrsoff >= 0 && adjQrsoff < visibleSamples.length) {
    const jx = toX(adjQrsoff);
    const jy = toY(visibleSamples[adjQrsoff]);
    const baseY = toY(0);
    if (Math.abs(jy - baseY) > 3) {
      measureLabels.push(
        <g key="st-measure">
          <line x1={jx + 2} y1={baseY} x2={jx + 2} y2={jy}
            stroke="#ea580c" strokeWidth={1} strokeDasharray="2,2" />
          <text x={jx + 6} y={(baseY + jy) / 2 + 3} fontSize={8} fontWeight={700} fill="#ea580c">
            {features.st_elevation_mv != null && features.st_elevation_mv > 0.03
              ? `+${features.st_elevation_mv.toFixed(1)}mV`
              : features.st_depression_mv != null && features.st_depression_mv > 0.03
              ? `\u2212${features.st_depression_mv.toFixed(1)}mV`
              : ""}
          </text>
        </g>
      );
    }
  }

  const speedLabel = interactive
    ? `${(SPEED_MM_PER_S * zoomLevel).toFixed(0)}mm/s 10mm/mV`
    : "25mm/s 10mm/mV";

  return (
    <div
      style={{
        overflow: "hidden",
        position: "relative",
        cursor: interactive ? (isDragging ? "grabbing" : "grab") : "default",
        userSelect: "none",
      }}
      onWheel={handleWheel}
      onMouseDown={handleMouseDown}
      onMouseMove={handleMouseMove}
      onMouseUp={handleMouseUp}
      onMouseLeave={handleMouseUp}
    >
      <svg width={W} height={H} style={{ display: "block" }} viewBox={`0 0 ${W} ${H}`}>
        {/* Grid paper background */}
        <rect x={0} y={0} width={W} height={H} fill={GRID_BG} />
        <rect x={0} y={0} width={labelW} height={H} fill="#fff" />
        {gridLines}

        {/* Highlight overlays (behind signal) */}
        {highlightElems}

        {/* Baseline */}
        <line x1={labelW} y1={midY} x2={W} y2={midY} stroke={GRID_LARGE} strokeWidth={1} />

        {/* Calibration pulse */}
        <path d={calPath} fill="none" stroke="#111827" strokeWidth={1.5} />

        {/* Signal trace */}
        <path d={signalPath} fill="none" stroke="#111827" strokeWidth={1.3} />

        {/* Fiducial brackets */}
        {fiducialElems}

        {/* ST / measurement annotations */}
        {measureLabels}

        {/* Lead label */}
        <text x={3} y={14} fontSize={11} fontWeight={800} fill="#111827">{leadName}</text>

        {/* Speed / gain label */}
        <text x={3} y={H - 4} fontSize={7} fill="#9ca3af">{speedLabel}</text>
      </svg>

      {/* Tooltip overlay for fiducial clicks */}
      {tooltip && (
        <div
          style={{
            position: "absolute",
            left: tooltip.x,
            top: tooltip.y,
            transform: "translate(-50%, -100%)",
            background: "#1f2937",
            color: "#fff",
            fontSize: 11,
            fontWeight: 600,
            padding: "3px 8px",
            borderRadius: 4,
            whiteSpace: "nowrap",
            pointerEvents: "none",
            zIndex: 10,
          }}
        >
          {tooltip.text}
        </div>
      )}
    </div>
  );
}


function regionLabel(hl: HighlightRule): string {
  switch (hl.region) {
    case "st": return hl.condition === "elevation" ? "ST\u2191" : hl.condition === "depression" ? "ST\u2193" : "ST";
    case "qrs": return "QRS";
    case "t": return hl.condition === "inversion" ? "T inv" : "T";
    case "p": return hl.condition === "absent" ? "no P" : "P";
    case "pr": return hl.condition === "short" ? "short PR" : "PR";
    case "rr": return "RR";
    default: return "";
  }
}


function getRegionBounds(beat: BeatFiducials, region: string): [number, number] | null {
  switch (region) {
    case "st":
      if (beat.qrsoff != null && beat.ton != null) return [beat.qrsoff, beat.ton];
      if (beat.qrsoff != null && beat.tpeak != null) return [beat.qrsoff, beat.tpeak];
      return null;
    case "qrs":
      if (beat.qrson != null && beat.qrsoff != null) return [beat.qrson, beat.qrsoff];
      return null;
    case "t":
      if (beat.ton != null && beat.toff != null) return [beat.ton, beat.toff];
      if (beat.tpeak != null && beat.toff != null) return [beat.tpeak - 10, beat.toff];
      return null;
    case "p":
      if (beat.pon != null && beat.poff != null) return [beat.pon, beat.poff];
      return null;
    case "pr":
      if (beat.pon != null && beat.qrson != null) return [beat.pon, beat.qrson];
      return null;
    case "rr":
      if (beat.pon != null && beat.toff != null) return [beat.pon, beat.toff];
      if (beat.qrson != null && beat.toff != null) return [beat.qrson, beat.toff];
      return null;
    default:
      return null;
  }
}


function shouldHighlight(hl: HighlightRule, features: PerLeadFeatures): boolean {
  switch (hl.condition) {
    case "elevation":
      return (features.st_elevation_mv ?? 0) > 0.05;
    case "depression":
      return (features.st_depression_mv ?? 0) > 0.05;
    case "inversion":
      return features.t_morphology === "inverted";
    case "wide":
    case "short":
    case "absent":
    case "always":
      return true;
    default:
      return false;
  }
}
