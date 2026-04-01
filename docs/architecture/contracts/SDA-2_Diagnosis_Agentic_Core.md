# SDA-2: Diagnosis & Agentic Core — Decomposition Tree + Contracts

**TEAM CONTRACT — U-HIEF v4**
**Issuer:** EPM
**Recipient:** SDA-2 Lead Architect
**Date:** 2026-03-26
**Scope:** Everything from computed features to clinical findings and reasoning
**Charter:** [Master_Charter.md](../Master_Charter.md) v1.1

---

## Depth-4 Decomposition Tree

```
2.0 Diagnosis & Agentic Core
├── 2.1 Agent Architecture Research (**MANDATORY FD-FPRE — THE architecture must emerge from research**)
│   │
│   │   *** CRITICAL DEPENDENCY ***
│   │   Node 2.7 (Disease Knowledge Base) Phase 1 (STAT conditions) feeds INTO this node.
│   │   The 95 disease .md files document the reasoning complexity of each condition.
│   │   This node reads those complexity analyses and determines the BEST architecture
│   │   to cover ALL conditions. The architecture is NOT predetermined — it must be
│   │   DISCOVERED through research. 5 agents is a starting hypothesis, not a decision.
│   │
│   ├── 2.1.1 FD-FPRE: What Does "Fully Understanding an ECG" Actually Require?
│   │   ├── 2.1.1.1 Map every reasoning domain by analyzing all 95 disease .md files
│   │   │   ├── Rate & rhythm analysis (is it regular? what's the rate? what drives it?)
│   │   │   ├── Conduction pathway analysis (how does the impulse travel? where is it blocked?)
│   │   │   ├── Ischemia/infarction detection (is there acute injury? where? which artery?)
│   │   │   ├── Structural remodeling detection (is the heart enlarged? which chambers?)
│   │   │   ├── Repolarization/morphology analysis (is the shape normal? what pattern?)
│   │   │   ├── Metabolic/electrolyte effects (is there a systemic cause?)
│   │   │   ├── Cross-domain reasoning (conditions that span multiple domains)
│   │   │   └── Temporal reasoning (beat-to-beat changes, progressive patterns)
│   │   ├── 2.1.1.2 Cluster conditions by reasoning similarity — which conditions share reasoning patterns?
│   │   ├── 2.1.1.3 Identify cross-domain dependencies (e.g., LBBB changes how ischemia is detected)
│   │   ├── 2.1.1.4 Map the "difficulty scores" from disease .md files → workload per domain
│   │   └── 2.1.1.5 PGAM: PGMR on ECG reasoning domain taxonomy
│   │
│   ├── 2.1.2 FD-FPRE: Agent Architecture Alternatives (Research ALL Options)
│   │   ├── 2.1.2.1 **Option A**: Domain-specialist agents (current hypothesis: 5–7 parallel specialists)
│   │   │   ├── Pros: clear ownership, parallel execution, focused expertise
│   │   │   └── Cons: cross-domain conditions need multi-agent coordination
│   │   ├── 2.1.2.2 **Option B**: Pipeline/sequential agents (each adds to a growing assessment)
│   │   │   ├── Pros: each agent builds on previous findings, natural reasoning flow
│   │   │   └── Cons: slower, ordering bias, single point of failure
│   │   ├── 2.1.2.3 **Option C**: Hierarchical agents (specialist layer → supervisor layer → orchestrator)
│   │   │   ├── Pros: handles cross-domain naturally at supervisor level
│   │   │   └── Cons: more LLM calls, latency, complexity
│   │   ├── 2.1.2.4 **Option D**: Single comprehensive agent with structured reasoning steps
│   │   │   ├── Pros: simplest, no coordination overhead, full context
│   │   │   └── Cons: context window limits, no parallelism, less explainable
│   │   ├── 2.1.2.5 **Option E**: Hybrid (parallel specialists + sequential cross-domain reviewers)
│   │   │   ├── Pros: best of parallel and sequential
│   │   │   └── Cons: complexity, more LLM calls
│   │   ├── 2.1.2.6 **Option F**: Condition-triggered agents (only activate agents relevant to initial findings)
│   │   │   ├── Pros: efficient, focused
│   │   │   └── Cons: misses unexpected findings, chicken-and-egg (need findings to choose agents)
│   │   ├── 2.1.2.7 Decision matrix: ALL options scored on accuracy, explainability, latency,
│   │   │   robustness, cross-domain handling, scalability, DeepSeek reasoner compatibility
│   │   └── 2.1.2.8 PGAM: PGMR on agent architecture comparison for medical ECG interpretation
│   │
│   ├── 2.1.3 FD-FPRE: Agent Communication & Information Flow
│   │   ├── 2.1.3.1 What does each agent SEE? (all features? only its domain? other agents' findings?)
│   │   ├── 2.1.3.2 How do agents SHARE information? (shared state? message passing? blackboard?)
│   │   ├── 2.1.3.3 Cross-domain handoff protocol (Agent A detects LBBB → Agent B must apply Sgarbossa)
│   │   ├── 2.1.3.4 Conflict resolution: when agents disagree, who decides? (orchestrator? voting? evidence weight?)
│   │   └── 2.1.3.5 Literature: Multi-agent orchestration patterns (LangGraph, CrewAI, AutoGen — learn patterns, don't adopt frameworks)
│   │
│   ├── 2.1.4 FD-FPRE: DeepSeek Reasoner for Medical Diagnosis
│   │   ├── 2.1.4.1 DeepSeek reasoner capabilities and chain-of-thought behavior
│   │   ├── 2.1.4.2 Prompt engineering for medical reasoning (2024–2026 SOTA)
│   │   ├── 2.1.4.3 ALL agents use reasoner mode — justification and cost/latency analysis
│   │   ├── 2.1.4.4 Context window budget per agent (features + RAG + system prompt + reasoning space)
│   │   └── 2.1.4.5 PGAM: PGMR on LLM reasoning for clinical ECG interpretation
│   │
│   ├── 2.1.5 FD-FPRE: Agentic Diagnosis vs Traditional ML vs Hybrid
│   │   ├── 2.1.5.1 Why NOT standard ML classifiers alone? (interpretability, flexibility, rare conditions)
│   │   ├── 2.1.5.2 Why NOT agentic alone? (hallucination risk, computational cost)
│   │   ├── 2.1.5.3 Hybrid possibility: ML pre-screening + agentic deep analysis for flagged findings
│   │   ├── 2.1.5.4 Advantages and risks of each approach — evidence-based comparison
│   │   └── 2.1.5.5 PGAM: PGMR comparing agentic vs ML vs hybrid for ECG diagnosis
│   │
│   └── 2.1.6 Architecture Validation Plan
│       ├── 2.1.6.1 How to TEST the chosen architecture before full implementation
│       ├── 2.1.6.2 Pilot: run architecture on 10 representative ECGs (2 STAT, 4 common, 4 complex)
│       ├── 2.1.6.3 Metrics: accuracy, reasoning quality, latency, cross-domain handling
│       └── 2.1.6.4 Go/no-go criteria: what results would make us change the architecture?
│
├── 2.2 Individual Agent Design
│   ├── 2.2.1 Rhythm Agent
│   │   ├── 2.2.1.1 FD-FPRE: All rhythm disorders from first principles
│   │   │   ├── Sinus rhythms (normal, tachycardia, bradycardia, arrhythmia)
│   │   │   ├── Atrial arrhythmias (AFib, AFlutter, MAT, PACs, SVT)
│   │   │   ├── Junctional rhythms
│   │   │   ├── Ventricular arrhythmias (PVCs, VT, VF, AIVR)
│   │   │   └── Pacemaker rhythms
│   │   ├── 2.2.1.2 Input features this agent needs (RR intervals, P-wave presence, regularity metrics)
│   │   ├── 2.2.1.3 Reasoning chain template (structured thought → finding → confidence → evidence)
│   │   └── 2.2.1.4 PGAM: PGMR on agentic rhythm analysis
│   ├── 2.2.2 Conduction Agent
│   │   ├── 2.2.2.1 FD-FPRE: All conduction disorders from first principles
│   │   │   ├── AV blocks (1st, 2nd Mobitz I/II, 3rd degree, high-grade)
│   │   │   ├── Bundle branch blocks (RBBB, LBBB, incomplete, rate-dependent)
│   │   │   ├── Fascicular blocks (LAFB, LPFB, bifascicular, trifascicular)
│   │   │   ├── Accessory pathways (WPW, LGL)
│   │   │   └── Intraventricular conduction delay (IVCD)
│   │   ├── 2.2.2.2 Input features (PR interval, QRS duration, QRS morphology per lead, delta wave)
│   │   ├── 2.2.2.3 Reasoning chain template
│   │   └── 2.2.2.4 PGAM: PGMR on agentic conduction analysis
│   ├── 2.2.3 Ischemia Agent
│   │   ├── 2.2.3.1 FD-FPRE: All ischemic/infarction patterns from first principles
│   │   │   ├── STEMI by territory (anterior, inferior, lateral, posterior, RV)
│   │   │   ├── NSTEMI patterns (ST depression, T-wave inversion)
│   │   │   ├── Wellens syndrome (Type A biphasic, Type B deep symmetric inversion)
│   │   │   ├── de Winter T-waves (upsloping ST depression + tall T in precordial)
│   │   │   ├── STEMI equivalents (sgarbossa criteria for LBBB/paced)
│   │   │   ├── Old MI (pathological Q waves, poor R-wave progression)
│   │   │   └── Reciprocal changes
│   │   ├── 2.2.3.2 **STAT PROTOCOL**: This agent triggers immediate alerts for STEMI/equivalents
│   │   ├── 2.2.3.3 Input features (ST deviation per lead, T morphology, Q waves, age/sex for thresholds)
│   │   ├── 2.2.3.4 Reasoning chain template
│   │   └── 2.2.3.5 PGAM: PGMR on agentic ischemia detection
│   ├── 2.2.4 Structural Agent
│   │   ├── 2.2.4.1 FD-FPRE: All structural abnormalities from first principles
│   │   │   ├── LVH (voltage criteria, strain pattern, multiple scoring systems)
│   │   │   ├── RVH (R-wave V1, RAD, strain)
│   │   │   ├── LAE (P-wave duration, P-mitrale, terminal force V1)
│   │   │   ├── RAE (P-wave amplitude, P-pulmonale)
│   │   │   ├── Dilated cardiomyopathy patterns
│   │   │   └── Hypertrophic cardiomyopathy patterns
│   │   ├── 2.2.4.2 Input features (voltage measurements, axis, P-wave morphology)
│   │   ├── 2.2.4.3 Reasoning chain template
│   │   └── 2.2.4.4 PGAM: PGMR on agentic structural analysis
│   ├── 2.2.5 Morphology Agent
│   │   ├── 2.2.5.1 FD-FPRE: All morphology abnormalities from first principles
│   │   │   ├── Long QT syndrome (congenital vs acquired, TdP risk)
│   │   │   ├── Short QT syndrome
│   │   │   ├── Brugada pattern (Type 1 coved, Type 2 saddle-back)
│   │   │   ├── Early repolarization (benign vs malignant)
│   │   │   ├── Pericarditis (diffuse ST elevation, PR depression)
│   │   │   ├── Pulmonary embolism patterns (S1Q3T3, RV strain, sinus tach)
│   │   │   ├── Hypothermia (Osborn/J waves)
│   │   │   └── Drug effects (digoxin, antiarrhythmics, TCAs)
│   │   ├── 2.2.5.2 **CRITICAL**: Uses RAW signal morphology (pre-baseline-correction)
│   │   ├── 2.2.5.3 Input features (raw waveform segments, T morphology, QT, J-point)
│   │   ├── 2.2.5.4 Reasoning chain template
│   │   └── 2.2.5.5 PGAM: PGMR on agentic morphology analysis
│   └── 2.2.6 **DYNAMIC NODE**: Metabolic/Electrolyte Agent (pending 2.1.1 research)
│       ├── 2.2.6.1 FD-FPRE: Electrolyte effects on ECG (hyperK, hypoK, hyperCa, hypoCa)
│       ├── 2.2.6.2 Drug effect patterns on ECG
│       ├── 2.2.6.3 Decision: standalone agent vs sub-role of morphology agent
│       └── 2.2.6.4 PGAM: PGMR on metabolic ECG patterns
│
├── 2.3 Orchestrator Design
│   ├── 2.3.1 Synthesis Strategy
│   │   ├── 2.3.1.1 FD-FPRE: How to combine findings from parallel agents into a unified assessment
│   │   ├── 2.3.1.2 Conflict resolution: when agents disagree (e.g., rhythm says SVT, conduction says WPW)
│   │   ├── 2.3.1.3 Confidence aggregation: individual agent confidence → overall confidence
│   │   └── 2.3.1.4 Priority ordering: STAT conditions surface first, then critical, then standard
│   ├── 2.3.2 Orchestrator Prompt Engineering
│   │   ├── 2.3.2.1 Orchestrator system prompt design (DeepSeek reasoner mode)
│   │   ├── 2.3.2.2 How to present agent findings to orchestrator (structured JSON vs narrative)
│   │   ├── 2.3.2.3 Orchestrator reasoning chain: synthesis → differential → final assessment
│   │   └── 2.3.2.4 PGAM: PGMR on multi-agent orchestration for clinical diagnosis
│   ├── 2.3.3 STAT Condition Pipeline
│   │   ├── 2.3.3.1 STAT conditions list (STEMI, Wellens A, de Winter, complete AVB, sustained VT/VF, hyperK sine wave, Brugada Type 1, long QT with TdP)
│   │   ├── 2.3.3.2 Fast-path detection: can we detect STAT conditions BEFORE full agent pipeline completes?
│   │   ├── 2.3.3.3 Alert protocol: immediate UI surfacing, confidence threshold for alerts
│   │   └── 2.3.3.4 False positive management: STAT false alarm rate target
│   └── 2.3.4 FD-FPRE: Clinical Decision Support from First Principles
│       ├── 2.3.4.1 How cardiologists actually read ECGs (systematic approach — rate, rhythm, axis, intervals, morphology)
│       ├── 2.3.4.2 Cognitive process modeling: agent architecture mirrors clinical thinking
│       └── 2.3.4.3 PGAM: PGMR on clinical reasoning process → agentic architecture mapping
│
├── 2.4 Confidence Scoring Framework
│   ├── 2.4.1 FD-FPRE: Confidence Calibration in Medical AI
│   │   ├── 2.4.1.1 Literature: Calibration methods for clinical AI (2024–2026)
│   │   ├── 2.4.1.2 What does "80% confidence" mean clinically? (calibration curves)
│   │   ├── 2.4.1.3 LLM confidence estimation methods (verbalized, logprob-based, consistency-based)
│   │   └── 2.4.1.4 PGAM: PGMR on confidence calibration for agentic ECG diagnosis
│   ├── 2.4.2 Per-Finding Confidence
│   │   ├── 2.4.2.1 Signal-derived confidence (how clear are the features?)
│   │   ├── 2.4.2.2 Agent-derived confidence (how certain is the reasoning?)
│   │   ├── 2.4.2.3 RAG-derived confidence (how strong is the textbook support?)
│   │   └── 2.4.2.4 Combined confidence score formula
│   ├── 2.4.3 Uncertainty Communication
│   │   ├── 2.4.3.1 How to display confidence to ER nurse (simple: high/medium/low vs numeric)
│   │   ├── 2.4.3.2 How to display to cardiologist (full detail, calibration curves)
│   │   └── 2.4.3.3 When to say "I don't know" (uncertainty threshold)
│   └── 2.4.4 Validation Against PTB-XL Labels
│       ├── 2.4.4.1 Compare agent diagnoses vs PTB-XL ptbxl_database.csv SCP codes
│       ├── 2.4.4.2 Per-condition accuracy metrics (sensitivity, specificity, PPV, NPV)
│       ├── 2.4.4.3 Calibration plot: predicted confidence vs actual accuracy
│       └── 2.4.4.4 PGAM: PGMR on validation methodology and results
│
├── 2.5 Beat-by-Beat & Lead-by-Lead Analysis Strategy
│   ├── 2.5.1 FD-FPRE: When Does Beat-by-Beat Matter?
│   │   ├── 2.5.1.1 Conditions that require individual beat analysis (intermittent arrhythmias, alternans, Wenckebach)
│   │   ├── 2.5.1.2 Conditions that require lead-by-lead comparison (STEMI territory, axis, reciprocal changes)
│   │   └── 2.5.1.3 When aggregate analysis is sufficient vs when individual beats are mandatory
│   ├── 2.5.2 Agent Interaction with Beat Data
│   │   ├── 2.5.2.1 How agents receive beat-level features (all beats at once? exemplar beats? flagged beats only?)
│   │   ├── 2.5.2.2 Token/context window management (10-second 12-lead = many beats × many leads × many features)
│   │   ├── 2.5.2.3 Summarization strategy: per-beat features → agent-digestible summary
│   │   └── 2.5.2.4 PGAM: PGMR on beat-level data presentation to LLM agents
│   ├── 2.5.3 Lead Comparison Framework
│   │   ├── 2.5.3.1 Contiguous lead groups (anterior V1-V4, lateral I/aVL/V5-V6, inferior II/III/aVF)
│   │   ├── 2.5.3.2 Reciprocal change detection across lead groups
│   │   └── 2.5.3.3 Single-lead anomaly detection (one lead abnormal, rest normal)
│   └── 2.5.4 Comprehensive Counting
│       ├── 2.5.4.1 Heart rate (instantaneous, average, variability)
│       ├── 2.5.4.2 Beat count (total, normal, PVC, PAC, other)
│       ├── 2.5.4.3 P:QRS ratio (conduction assessment)
│       └── 2.5.4.4 Interval trends across beats (progressive PR prolongation = Wenckebach)
│
└── 2.6 DeepSeek API Integration
    ├── 2.6.1 API Architecture
    │   ├── 2.6.1.1 Reasoner mode API usage (system prompt, temperature, max tokens)
    │   ├── 2.6.1.2 Parallel agent execution via ThreadPoolExecutor
    │   ├── 2.6.1.3 Rate limiting, retry logic, error handling
    │   └── 2.6.1.4 Latency budget: how long can the full pipeline take?
    ├── 2.6.2 Prompt Architecture
    │   ├── 2.6.2.1 System prompt per agent (role, expertise, output format)
    │   ├── 2.6.2.2 Feature presentation format (structured JSON with units and normal ranges)
    │   ├── 2.6.2.3 RAG context injection (how to include textbook evidence in prompts)
    │   └── 2.6.2.4 Output parsing and structured extraction
    ├── 2.6.3 Safety Guardrails
    │   ├── 2.6.3.1 Input validation: never send raw patient identifiers to API
    │   ├── 2.6.3.2 Output validation: check for unsupported claims (grounding check)
    │   ├── 2.6.3.3 Fallback: what if API is down or returns garbage?
    │   └── 2.6.3.4 PGAM: PGMR on safe LLM API usage for clinical applications
    └── 2.6.4 FD-FPRE: LLM API Best Practices for Medical Applications
        ├── 2.6.4.1 Literature: Medical LLM deployment (2024–2026 FDA guidance, safety papers)
        ├── 2.6.4.2 Prompt injection risks and mitigations
        └── 2.6.4.3 Reproducibility: same input → same output? (temperature=0, seed control)
```

---

## First-Level Child Contracts

### Contract SDA-2.1: Agent Architecture Research — THE Architecture Must Be Discovered

```
TEAM CONTRACT — U-HIEF v4
Issuer: SDA-2 Lead Architect – Branch Diagnosis & Agentic Core
Recipient: RES + FD-FPRE Swarm — Agent Architecture Team + DEC (AI Architect, Cardiologist)
Scope: MANDATORY FOUNDATIONAL RESEARCH — Determine through rigorous first-principles
research the OPTIMAL agent architecture for fully understanding an ECG record.

THE ARCHITECTURE IS NOT PREDETERMINED. "5 specialist agents" is a starting
hypothesis, NOT a decision. The research must:

1. FIRST understand what "fully understanding an ECG" requires — analyze the
   reasoning complexity of ALL 95 conditions (from Node 2.7 disease .md files)
2. THEN determine what architecture best handles that complexity — research
   at least 6 fundamentally different architecture options (specialist parallel,
   sequential pipeline, hierarchical, single comprehensive, hybrid, condition-triggered)
3. THEN validate the choice against representative ECGs before committing

KEY INPUT: Node 2.7 Phase 1 disease .md files provide "Reasoning Complexity
Analysis" (Section 6) for each condition — difficulty scores, cross-domain
dependencies, reasoning chains. This data drives the architecture decision.

KEY OUTPUT: A formally justified architecture design that determines:
- How many agents (could be 3, could be 10, could be a 2-layer hierarchy)
- What each agent is responsible for
- How agents communicate (what they see, how they share findings)
- How cross-domain conditions are handled (LBBB+STEMI, AFib+WPW, etc.)
- How the orchestrator synthesizes
- How the architecture scales to rare/novel conditions

ALL agents must use DeepSeek reasoner mode. No lightweight chat for diagnosis.

You are an AI Systems Architect, Clinical Decision Support Expert, and
Computational Cardiologist. Your sole mission is ideal, zero-miss,
publication-grade outcomes for this exact node. Ignore all time, computation,
and cost constraints. Proceed leisurely and thoroughly. Do everything.
Explore every edge case.

Mandatory Rules:
- Research-First: Complete 100% of FD-FPRE + RES work and obtain RRC/QASVS
  approval *before* any implementation.
- Dynamic Branching: If any new gap appears, instantly create a new child node.
- FD-FPRE: Start from how EXPERT CARDIOLOGISTS actually reason about ECGs
  (their cognitive process, their systematic approach: rate → rhythm → axis →
  intervals → morphology → synthesis). Map the human reasoning process FIRST,
  then determine how agents should mirror or improve on it.
- Survey 2024–2026 multi-agent medical AI literature exhaustively.
- PGAM: Produce minimum 4 PGMRs for this node.

Deliverables (in order):
1. FD-FPRE: How cardiologists read ECGs — cognitive process analysis
2. FD-FPRE: Reasoning domain taxonomy from 95 disease complexity analyses
3. FD-FPRE: 6+ architecture alternatives with full pros/cons/evidence
4. FD-FPRE: Multi-agent medical AI literature survey (2024–2026)
5. FD-FPRE: DeepSeek reasoner capabilities for medical reasoning
6. Decision matrix: ALL architecture options scored on ≥7 criteria
7. Cross-domain dependency map (which conditions require multi-agent coordination)
8. Information flow design (what each agent sees, shared state, handoff protocols)
9. Pilot validation plan (10 representative ECGs to test before committing)
10. Agentic vs ML vs hybrid comparison with evidence
11. Draft 4 PGMRs:
    - PGMR-2.1a: ECG Reasoning Domain Taxonomy
    - PGMR-2.1b: Agent Architecture Comparison for Clinical ECG
    - PGMR-2.1c: Cross-Domain Reasoning in Multi-Agent Medical Systems
    - PGMR-2.1d: DeepSeek Reasoner for Medical Decision Support
12. Submit to RRC + DEC (Cardiologist + AI Architect must both sign off)

AFTER this gate passes:
- Fill in "Agent Assignment" (Section 6A) in all 95 disease .md files
- Node 2.2 (Individual Agent Design) can begin
- Node 2.3 (Orchestrator Design) can begin

Proceed leisurely. Research everything broadly and in depth. Spawn new nodes
for any emerging gap. Produce 2–4 PGMRs per major deliverable. Never rush.
```

### Contract SDA-2.2: Individual Agent Design

```
TEAM CONTRACT — U-HIEF v4
Issuer: SDA-2 Lead Architect – Branch Diagnosis & Agentic Core
Recipient: RES + FD-FPRE Swarm — Agent Design Team
Scope: Design each specialist agent in full detail: what it knows, what features
it receives, its reasoning chain template, its output format, its STAT triggers.
DEPENDS ON 2.1 completion (agent count/specialization must be finalized first).

You are a Clinical Cardiology and AI Agent Design Expert. Your sole mission is
ideal, zero-miss, publication-grade outcomes for this exact node.

Begin work on this node only after SDA-2.1 Research-First Gate is passed.

Deliverables per agent:
1. FD-FPRE: Complete first-principles review of the agent's diagnostic domain
2. Input feature specification (exactly which features from SDA-1.5 this agent needs)
3. Reasoning chain template (structured: observation → interpretation → finding → confidence → evidence)
4. STAT condition triggers (if applicable)
5. Edge cases and failure modes
6. Draft PGMR per agent (or grouped)
7. Submit to RRC

Proceed leisurely. Research everything broadly and in depth. Spawn new nodes
for any emerging gap. Produce 2–4 PGMRs per major deliverable. Never rush.
```

### Contract SDA-2.3: Orchestrator Design

```
TEAM CONTRACT — U-HIEF v4
Issuer: SDA-2 Lead Architect – Branch Diagnosis & Agentic Core
Recipient: RES + FD-FPRE Swarm — Orchestrator Team
Scope: Design the orchestrator that synthesizes findings from all specialist
agents into a unified clinical assessment. Includes conflict resolution,
confidence aggregation, STAT fast-path, and priority ordering.
Uses DeepSeek reasoner mode.

You are a Clinical Decision Support and Multi-Agent Systems Expert.

Deliverables:
1. FD-FPRE: Multi-agent synthesis patterns (voting, weighted, hierarchical)
2. Conflict resolution protocol (when agents disagree — which wins? escalate?)
3. STAT fast-path design (immediate detection before full pipeline completes)
4. Confidence aggregation formula
5. Orchestrator prompt architecture (DeepSeek reasoner mode)
6. Draft 2–4 PGMRs
7. Submit to RRC

Proceed leisurely. Research everything broadly and in depth. Spawn new nodes
for any emerging gap. Produce 2–4 PGMRs per major deliverable. Never rush.
```

### Contract SDA-2.4: Confidence Scoring Framework

```
TEAM CONTRACT — U-HIEF v4
Issuer: SDA-2 Lead Architect
Recipient: RES + FD-FPRE Swarm — Confidence Team
Scope: Design the confidence scoring framework: per-finding confidence
from signal, agent reasoning, and RAG evidence. Calibration methodology.
Uncertainty communication strategy for ER nurses vs cardiologists.

Deliverables:
1. FD-FPRE: Confidence calibration in medical AI (literature)
2. Three-source confidence model (signal + agent + RAG)
3. Calibration methodology (validation against PTB-XL)
4. Uncertainty communication design (ER: simple; cardiology: detailed)
5. "I don't know" threshold
6. Draft 2–4 PGMRs
7. Submit to RRC

Proceed leisurely. Research everything broadly and in depth. Spawn new nodes
for any emerging gap. Produce 2–4 PGMRs per major deliverable. Never rush.
```

### Contract SDA-2.5: Beat-by-Beat & Lead-by-Lead Strategy

```
TEAM CONTRACT — U-HIEF v4
Issuer: SDA-2 Lead Architect
Recipient: RES + FD-FPRE Swarm — Beat Analysis Team
Scope: Research when individual beat/lead analysis is necessary, how agents
consume beat-level data within LLM context windows, and comprehensive
counting (heart rate, beat count, P:QRS ratio, interval trends).

Deliverables:
1. FD-FPRE: Conditions requiring individual beat analysis
2. Token/context window management strategy for beat-level features
3. Summarization vs full-detail decision framework
4. Comprehensive counting specification
5. Lead comparison framework (contiguous groups, reciprocal changes)
6. Draft 2–4 PGMRs
7. Submit to RRC

Proceed leisurely. Research everything broadly and in depth. Spawn new nodes
for any emerging gap. Produce 2–4 PGMRs per major deliverable. Never rush.
```

### Contract SDA-2.6: DeepSeek API Integration

```
TEAM CONTRACT — U-HIEF v4
Issuer: SDA-2 Lead Architect
Recipient: RES + FD-FPRE Swarm — API Integration Team
Scope: Design the DeepSeek API integration: reasoner mode configuration,
parallel execution architecture, prompt templates, safety guardrails,
rate limiting, and fallback strategies.

Deliverables:
1. FD-FPRE: Medical LLM deployment best practices (FDA guidance, safety)
2. API architecture design (parallel ThreadPoolExecutor, latency budget)
3. Prompt architecture per agent (system prompt, feature format, RAG injection)
4. Safety guardrails (no PII to API, output grounding check, fallback)
5. Reproducibility strategy (temperature=0, seed control)
6. Draft 2–4 PGMRs
7. Submit to RRC

Proceed leisurely. Research everything broadly and in depth. Spawn new nodes
for any emerging gap. Produce 2–4 PGMRs per major deliverable. Never rush.
```

### Contract SDA-2.7: Disease-to-ECG Manifestation Knowledge Base (**NEW — per user directive**)

```
TEAM CONTRACT — U-HIEF v4
Issuer: SDA-2 Lead Architect – Branch Diagnosis & Agentic Core
Recipient: RES + FD-FPRE Swarm — Disease Knowledge Team + DEC (Cardiologist mandatory)
Scope: Create a standalone .md file for EVERY disease/condition the system must
detect. Each .md documents the COMPLETE chain from first principles:

    Root cause (pathophysiology)
    → Electrical mechanism (what changes in the cardiac action potential)
    → Lead-by-lead ECG presentation (what each of the 12 leads shows and WHY)
    → Diagnostic criteria (2025 AHA/ESC thresholds)
    → Beat-by-beat considerations (constant vs intermittent)
    → Differential diagnosis (mimics and coexisting conditions)
    → Agent assignment (which agent owns it, what features anchor confidence)
    → Dashboard visualization spec (what to highlight, where arrows go)
    → RAG references (which textbook chapters/figures to retrieve)

This is the SINGLE SOURCE OF TRUTH consumed by:
- SDA-1 (what features to extract for each condition)
- SDA-2 (what each agent looks for and how to reason)
- SDA-3 (what each per-disease dashboard shows)
- SDA-4 (which textbook content to retrieve)

Total: 95 disease .md files organized by category.
Priority: STAT conditions FIRST (13 files), then common ER conditions, then full coverage.

Template: docs/architecture/nodes/diseases/_TEMPLATE.md
Index: docs/architecture/nodes/diseases/_INDEX.md

You are a Clinical Cardiology Expert with deep ECG interpretation knowledge.
Your sole mission is ideal, zero-miss, publication-grade outcomes for every
disease .md file. Each file must be detailed enough that a cardiology fellow
could learn the ECG pattern from reading it alone.

Mandatory Rules:
- Research-First: Complete FD-FPRE for each disease before finalizing its .md
- Dynamic Branching: If a disease has subtypes or special presentations, spawn
  child .md files (e.g., STEMI splits into 5 territory files)
- Lead-by-lead table is MANDATORY in every file — never skip a lead
- Differential diagnosis section is MANDATORY — what mimics this?
- STAT classification is MANDATORY — is this immediately life-threatening?
- Every claim must cite a guideline or textbook reference

Deliverables (phased):
Phase 1: 13 STAT condition .md files + Normal ECG reference + Lead anatomy reference
Phase 2: Common ER conditions (AFib, RBBB, LBBB, LVH, pericarditis, PE)
Phase 3: All remaining conditions
Phase 4: Cross-cutting references and edge-case files

PGMRs: Minimum 4 PGMRs for this node:
- PGMR-2.7a: STAT Conditions — ECG Manifestation Compendium
- PGMR-2.7b: Conduction and Rhythm Disorders — First-Principles ECG Analysis
- PGMR-2.7c: Structural and Morphological Abnormalities — ECG Presentation
- PGMR-2.7d: Metabolic and Special Patterns — ECG Recognition Framework

Proceed leisurely. Research everything broadly and in depth. Spawn new nodes
for any emerging gap. Produce 2–4 PGMRs per major deliverable. Never rush.
```

---

**SDA-2 Tree: 7 first-level nodes, 25+ second-level nodes, ~170 leaf nodes (including 95 disease files). Expected PGMRs: 16–20.**
**Known dynamic nodes: Metabolic/Electrolyte Agent (2.2.6), STAT fast-path timing (2.3.3), disease subtypes as needed.**
