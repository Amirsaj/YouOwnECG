"use client";

interface Props {
  /** Base64-encoded PNG returned by the vision pipeline. */
  imageBase64: string | null | undefined;
  ecgId: string;
}

export default function ECGViewer({ imageBase64, ecgId }: Props) {
  if (!imageBase64) {
    return (
      <div
        style={{
          border: "1px dashed #d1d5db",
          borderRadius: 8,
          padding: "24px",
          textAlign: "center",
          color: "#9ca3af",
          fontSize: 13,
        }}
      >
        ECG render unavailable
      </div>
    );
  }

  const src = imageBase64.startsWith("data:")
    ? imageBase64
    : `data:image/png;base64,${imageBase64}`;

  return (
    <div style={{ border: "1px solid #e5e7eb", borderRadius: 8, overflow: "hidden" }}>
      <div style={{ background: "#f9fafb", padding: "6px 12px", fontSize: 12, color: "#6b7280", fontWeight: 500 }}>
        ECG Render — {ecgId}
      </div>
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img
        src={src}
        alt={`Rendered ECG for ${ecgId}`}
        style={{ width: "100%", display: "block", background: "#fff" }}
      />
    </div>
  );
}
