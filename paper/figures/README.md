# Figure Generation Prompts

Each figure below has a generation prompt. Use these with a diagram/plotting tool
or image generation model to produce the actual figures.

## Fig 1: system_architecture.pdf
**Prompt:** Full system architecture diagram with data flow arrows.
Left-to-right: ECG file → Ingestion → Preprocessing → Quality Assessment →
Fiducial Detection → Feature Extraction → Vision Description → Agent Orchestrator
(3 parallel domain-specialist agents: Rhythm/Rate/Conduction, Ischemia/Territory,
Morphology/Repolarization → sequential Clinical Decision Synthesis) →
DiagnosticResult → Frontend (upload → results → per-disease dashboards).
RAG knowledge base (textbook chunks) feeds into each agent.
Emphasize signal grounding: agents receive structured measurements, not raw signals.
Use clinical blue/white color scheme. Professional vector diagram style.

## Fig 2: fiducial_annotation.pdf
**Prompt:** Annotated single-lead ECG beat showing all 13 fiducial points from
the FPT table. Label each: P-onset, P-peak, P-offset, QRS-onset, Q-nadir,
R-peak, S-nadir, QRS-offset, J-point, T-onset, T-peak, T-offset. Use a clean
normal sinus rhythm beat from Lead II. Color-code: P-wave region blue, QRS red,
T-wave green. Show measurement intervals (PR, QRS, QT) as brackets below.

## Fig 3: agent_architecture.pdf
**Prompt:** Agent orchestration diagram modeled after a cardiology department.
3 parallel domain-specialist agents (like subspecialty fellows):
Rhythm/Rate/Conduction, Ischemia/Territory, Morphology/Repolarization.
Each receives structured FeatureObject + RAG-retrieved textbook citations.
Their findings feed into a sequential Clinical Decision Synthesis agent
(like the attending cardiologist) that resolves conflicts and applies
clinical suppression rules. Show: input = FeatureObject + RAG context,
output = list of DiagnosticFinding with confidence levels.
Blue = deterministic signal data, orange = LLM clinical reasoning.

## Fig 4: disease_dashboard.pdf
**Prompt:** Screenshot mockup of per-disease dashboard for Anterior STEMI.
Top: red STAT badge + global measurement badges. Left: 4 ECG lead strips
(V1-V4) on pink clinical grid paper with ST elevation arrows. Right top:
criteria checklist. Right middle: per-lead measurement table. Bottom:
explanation and STAT action panel. Clinical white/blue/red scheme.

## Fig 5: fiducial_bland_altman.pdf
**Script:** Generate from validation/results/fiducial_accuracy.csv
2x4 Bland-Altman plots for each fiducial point. Mean bias + 95% LoA.

## Fig 6: measurement_correlation.pdf
**Script:** Generate from validation/results/measurement_accuracy.csv
2x3 scatter plots: HR, PR, QRS, QT, QTc, axis. Identity + regression lines.

## Fig 7: disease_confusion_matrix.pdf
**Script:** Generate from validation/results/disease_detection.csv
4x4 grid of 2x2 confusion matrices, one per condition.

## Fig 8: disease_sensitivity_specificity.pdf
**Script:** Generate from validation/results/disease_summary.csv
ROC-space scatter: (1-spec, sens) per condition. Color by category.

## Fig 9: multimodel_radar.pdf
**Script:** Generate after multi-model validation runs.
Radar chart: 5 models × 6 axes (F1, Sens, Spec, Cost, Latency, Reasoning).

## Fig 10: multimodel_agreement.pdf
**Script:** Generate after multi-model validation runs.
5x5 Cohen's kappa heatmap.

## Fig 11: crossdataset_f1.pdf
**Script:** Generate after multi-dataset validation runs.
Grouped bar chart: per-condition F1 across datasets.
