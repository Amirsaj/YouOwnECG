import { getECGResult, getSignalData } from "@/lib/api";
import type { DiagnosticResult, SignalData } from "@/lib/types";
import StatAlertBanner from "@/components/StatAlertBanner";
import MeasurementsTable from "@/components/MeasurementsTable";
import ECGGridView from "@/components/ECGGridView";
import ResultClient from "./ResultClient";
import QAPanel from "./QAPanel";

interface Props {
  params: Promise<{ id: string }>;
}

export default async function ECGResultPage({ params }: Props) {
  const { id } = await params;
  let result: DiagnosticResult;
  let signalData: SignalData | null = null;

  try {
    result = await getECGResult(id);
  } catch (e) {
    return (
      <main style={{ maxWidth: 720, margin: "80px auto", padding: "0 24px" }}>
        <div style={{ padding: 20, background: "#fef2f2", border: "1px solid #fca5a5", borderRadius: 8, color: "#dc2626" }}>
          {(e as Error).message}
        </div>
      </main>
    );
  }

  try {
    signalData = await getSignalData(id);
  } catch {
    // Signal data is optional — page still renders without it
  }

  return (
    <>
      <StatAlertBanner alerts={result.stat_alerts} />

      <main style={{ maxWidth: 720, margin: "24px auto", padding: "0 24px" }}>
        <div style={{ marginBottom: 24 }}>
          <h1 style={{ fontSize: 22, fontWeight: 800, margin: "0 0 4px 0" }}>ECG Analysis</h1>
          <p style={{ fontSize: 12, color: "#6b7280", margin: 0 }}>
            ID: {result.ecg_id} · Pipeline: {result.pipeline_version} · Model: {result.model_version}
          </p>
        </div>

        {signalData && (
          <div style={{ marginBottom: 24, overflowX: "auto" }}>
            <ECGGridView signalData={signalData} />
          </div>
        )}

        <div style={{ marginBottom: 24 }}>
          <MeasurementsTable
            measurements={result.measurements}
            overallQuality={result.overall_quality}
          />
        </div>

        <ResultClient result={result} />

        <div style={{ borderTop: "1px solid #e5e7eb", paddingTop: 24 }}>
          <h2 style={{ fontSize: 16, fontWeight: 700, marginBottom: 12 }}>Ask a Question</h2>
          <QAPanel ecgId={result.ecg_id} />
        </div>

        <div style={{ marginTop: 32, padding: "10px 16px", background: "#fef2f2", borderRadius: 8, fontSize: 11, color: "#dc2626", fontWeight: 600 }}>
          AI-GENERATED — NOT A CLINICAL DIAGNOSIS — CLINICAL CORRELATION REQUIRED
        </div>
      </main>
    </>
  );
}
