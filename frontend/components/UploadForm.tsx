"use client";

import { useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { analyzeECG } from "@/lib/api";

const ALLOWED_EXTENSIONS = [".hea", ".dat", ".edf", ".scp", ".csv"];

export default function UploadForm() {
  const [dragging, setDragging] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const router = useRouter();

  function validateFiles(files: File[]): string | null {
    for (const file of files) {
      const ext = "." + file.name.split(".").pop()?.toLowerCase();
      if (!ALLOWED_EXTENSIONS.includes(ext)) {
        return `Unsupported file type "${ext}". Accepted: ${ALLOWED_EXTENSIONS.join(", ")}`;
      }
    }
    const hasHea = files.some(f => f.name.toLowerCase().endsWith(".hea"));
    const hasDat = files.some(f => f.name.toLowerCase().endsWith(".dat"));
    if ((hasHea && !hasDat) || (!hasHea && hasDat)) {
      return "WFDB format requires both .hea and .dat files — please select both.";
    }
    return null;
  }

  async function handleFiles(files: File[]) {
    if (files.length === 0) return;
    const err = validateFiles(files);
    if (err) { setError(err); return; }
    setError(null);
    setLoading(true);
    try {
      const result = await analyzeECG(files.length === 1 ? files[0] : files);
      router.push(`/ecg/${result.ecg_id}`);
    } catch (e) {
      setError((e as Error).message);
      setLoading(false);
    }
  }

  return (
    <div>
      <div
        onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDragging(false);
          handleFiles(Array.from(e.dataTransfer.files));
        }}
        onClick={() => inputRef.current?.click()}
        style={{
          border: `2px dashed ${dragging ? "#2563eb" : "#d1d5db"}`,
          borderRadius: 12,
          padding: "48px 32px",
          textAlign: "center",
          cursor: loading ? "not-allowed" : "pointer",
          background: dragging ? "#eff6ff" : "#f9fafb",
          transition: "all 0.15s",
        }}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".hea,.dat,.edf,.scp,.csv"
          multiple
          style={{ display: "none" }}
          onChange={(e) => handleFiles(Array.from(e.target.files ?? []))}
          disabled={loading}
        />
        {loading ? (
          <div>
            <div style={{ fontSize: 32, marginBottom: 12 }}>⏳</div>
            <p style={{ fontWeight: 600 }}>Analysing ECG — please wait...</p>
          </div>
        ) : (
          <div>
            <div style={{ fontSize: 48, marginBottom: 12 }}>📋</div>
            <p style={{ fontWeight: 600, marginBottom: 4 }}>Drop ECG file(s) here or click to browse</p>
            <p style={{ fontSize: 13, color: "#6b7280" }}>
              WFDB: select both .hea + .dat &nbsp;|&nbsp; Single-file: {[".edf", ".scp", ".csv"].join(", ")}
            </p>
          </div>
        )}
      </div>

      {error && (
        <div style={{ marginTop: 12, padding: "10px 16px", background: "#fef2f2", border: "1px solid #fca5a5", borderRadius: 8, color: "#dc2626", fontSize: 14 }}>
          {error}
        </div>
      )}
    </div>
  );
}
