"use client";

import { useRef, useState } from "react";
import { qaStream } from "@/lib/api";

interface Props {
  ecgId: string;
}

const ABORT_TIMEOUT_MS = 15_000;
const SLOW_WARN_MS = 5_000;

export default function QAPanel({ ecgId }: Props) {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(false);
  const [slowWarning, setSlowWarning] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);
  const slowTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const abortTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  function clearTimers() {
    if (slowTimerRef.current) clearTimeout(slowTimerRef.current);
    if (abortTimerRef.current) clearTimeout(abortTimerRef.current);
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!question.trim() || loading) return;

    setAnswer("");
    setError(null);
    setSlowWarning(false);
    setLoading(true);

    const controller = new AbortController();
    abortRef.current = controller;

    // Slow warning at 5s (Node 3.5)
    slowTimerRef.current = setTimeout(() => setSlowWarning(true), SLOW_WARN_MS);
    // Hard abort at 15s (Node 3.5)
    abortTimerRef.current = setTimeout(() => {
      controller.abort();
      setError("Response timed out (15s). Please try again.");
      setLoading(false);
      setSlowWarning(false);
    }, ABORT_TIMEOUT_MS);

    try {
      for await (const token of qaStream(ecgId, question, controller.signal)) {
        clearTimers();
        setSlowWarning(false);
        setAnswer((prev) => prev + token);
        // Reset abort timer on each token received
        if (abortTimerRef.current) clearTimeout(abortTimerRef.current);
        abortTimerRef.current = setTimeout(() => {
          controller.abort();
          setError("No response received for 15s. Please try again.");
          setLoading(false);
        }, ABORT_TIMEOUT_MS);
      }
    } catch (e) {
      if ((e as Error).name !== "AbortError") {
        setError((e as Error).message);
      }
    } finally {
      clearTimers();
      setLoading(false);
      setSlowWarning(false);
    }
  }

  return (
    <div>
      <form onSubmit={handleSubmit} style={{ display: "flex", gap: 8, marginBottom: 16 }}>
        <input
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Ask about this ECG (e.g. 'What does the ST elevation mean?')"
          disabled={loading}
          style={{
            flex: 1,
            padding: "8px 12px",
            border: "1px solid #d1d5db",
            borderRadius: 8,
            fontSize: 14,
          }}
        />
        <button
          type="submit"
          disabled={loading || !question.trim()}
          style={{
            padding: "8px 16px",
            background: loading ? "#9ca3af" : "#2563eb",
            color: "#fff",
            border: "none",
            borderRadius: 8,
            cursor: loading ? "not-allowed" : "pointer",
            fontWeight: 600,
            fontSize: 14,
          }}
        >
          {loading ? "..." : "Ask"}
        </button>
        {loading && (
          <button
            type="button"
            onClick={() => { abortRef.current?.abort(); clearTimers(); setLoading(false); setSlowWarning(false); }}
            style={{
              padding: "8px 12px",
              background: "#dc2626",
              color: "#fff",
              border: "none",
              borderRadius: 8,
              cursor: "pointer",
              fontSize: 13,
            }}
          >
            Stop
          </button>
        )}
      </form>

      {slowWarning && (
        <div style={{ marginBottom: 8, padding: "6px 12px", background: "#fffbeb", border: "1px solid #fcd34d", borderRadius: 6, fontSize: 13, color: "#92400e" }}>
          Response is taking longer than expected...
        </div>
      )}

      {error && (
        <div style={{ marginBottom: 12, padding: "8px 12px", background: "#fef2f2", border: "1px solid #fca5a5", borderRadius: 6, fontSize: 13, color: "#dc2626" }}>
          {error}
        </div>
      )}

      {answer && (
        <div style={{ padding: "12px 16px", background: "#f9fafb", border: "1px solid #e5e7eb", borderRadius: 8, fontSize: 14, whiteSpace: "pre-wrap", lineHeight: 1.6 }}>
          {answer}
        </div>
      )}
    </div>
  );
}
