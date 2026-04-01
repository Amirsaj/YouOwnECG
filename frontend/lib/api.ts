/** Typed wrappers for the YouOwnECG FastAPI backend. */

import type { DiagnosticResult, SignalData } from "./types";
import type { UserRole } from "@/components/OverrideModal";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export async function analyzeECG(files: File | File[]): Promise<DiagnosticResult> {
  const form = new FormData();
  const fileList = Array.isArray(files) ? files : [files];
  for (const f of fileList) {
    form.append("files", f);
  }
  const res = await fetch(`${API_BASE}/ecg/analyze`, { method: "POST", body: form });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail ?? "Upload failed");
  }
  return res.json();
}

export async function getECGResult(ecgId: string): Promise<DiagnosticResult> {
  const res = await fetch(`${API_BASE}/ecg/${ecgId}`, { cache: "no-store" });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail ?? "Not found");
  }
  return res.json();
}

export async function getSignalData(ecgId: string, leads?: string[]): Promise<SignalData> {
  const params = leads?.length ? `?leads=${leads.join(",")}` : "";
  const res = await fetch(`${API_BASE}/ecg/${ecgId}/signal${params}`, { cache: "no-store" });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail ?? "Signal data not found");
  }
  return res.json();
}

export async function recordOverride(
  ecgId: string,
  findingType: string,
  reason: string,
  userRole: UserRole,
  userId: string
): Promise<void> {
  const res = await fetch(`${API_BASE}/ecg/${ecgId}/override`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      finding_type: findingType,
      reason,
      user_role: userRole,
      user_id: userId,
    }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail ?? "Override failed");
  }
}

/**
 * Open a Q&A SSE stream for a given ECG.
 * Returns an EventSource that emits {text?: string} | {error?: string} JSON objects,
 * followed by a [DONE] sentinel.
 *
 * Caller is responsible for calling .close() on abort.
 */
export function openQAStream(ecgId: string, question: string): EventSource {
  const url = new URL(`${API_BASE}/ecg/${ecgId}/qa`);
  // EventSource only supports GET — use a hidden form POST via fetch + ReadableStream instead
  // Returned as an opaque handle; consumer uses qaStream() below for the async generator.
  throw new Error("Use qaStream() instead");
}

/**
 * Async generator that streams Q&A tokens from the backend.
 * Yields string tokens. Throws on network error or on [DONE].
 */
export async function* qaStream(
  ecgId: string,
  question: string,
  signal?: AbortSignal
): AsyncGenerator<string> {
  const res = await fetch(`${API_BASE}/ecg/${ecgId}/qa`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
    signal,
  });
  if (!res.ok || !res.body) throw new Error("Q&A stream failed");

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() ?? "";
    for (const line of lines) {
      if (!line.startsWith("data: ")) continue;
      const data = line.slice(6).trim();
      if (data === "[DONE]") return;
      try {
        const chunk = JSON.parse(data) as { text?: string; error?: string };
        if (chunk.error) throw new Error(chunk.error);
        if (chunk.text) yield chunk.text;
      } catch {
        // malformed SSE line — skip
      }
    }
  }
}
