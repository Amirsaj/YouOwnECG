import UploadForm from "@/components/UploadForm";

export default function Home() {
  return (
    <main style={{ maxWidth: 640, margin: "80px auto", padding: "0 24px" }}>
      <div style={{ textAlign: "center", marginBottom: 40 }}>
        <h1 style={{ fontSize: 28, fontWeight: 800, margin: "0 0 8px 0" }}>YouOwnECG</h1>
        <p style={{ color: "#6b7280", fontSize: 15 }}>
          AI-assisted 12-lead ECG analysis for ER clinicians
        </p>
        <div
          style={{
            marginTop: 16,
            padding: "6px 16px",
            background: "#fef2f2",
            border: "1px solid #fca5a5",
            borderRadius: 8,
            fontSize: 12,
            color: "#dc2626",
            fontWeight: 600,
            display: "inline-block",
          }}
        >
          AI-GENERATED — NOT A CLINICAL DIAGNOSIS — CLINICAL CORRELATION REQUIRED
        </div>
      </div>
      <UploadForm />
    </main>
  );
}
