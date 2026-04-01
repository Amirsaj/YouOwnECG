# U-HIEF v4 — Problems-First: The Complete Guide to Dealing with Problems Before Implementation

**Version:** 4.0
**Date:** 2026-03-26
**Project:** YouOwnECG — Clinical-Grade Agentic ECG Analysis Platform
**Governing Framework:** Universal Hierarchical Ideal Execution Framework v4 (U-HIEF v4)

---

## 1. Core Philosophy: Research-First, Always

Every problem in this project — from a single ambiguous UI label to a fundamental signal-processing question — is governed by one absolute rule:

> **100% of research, first-principles discovery, and peer review must be completed, drafted into publication-grade reports, and approved BEFORE any line of implementation code is written for that problem.**

This is not a suggestion. It is the constitution of this project. The rationale:

- **Medical domain**: A wrong assumption in ECG analysis can propagate silently through the pipeline and produce clinically dangerous outputs. There is no "move fast and break things" in clinical software.
- **Complexity budget**: The system spans signal processing, computer vision, LLM reasoning, agentic orchestration, RAG, and high-stress ER UI. Skipping research on any layer compounds errors across all layers.
- **Publication mandate**: Every major decision must be defensible at journal level. If you cannot write a rigorous paper about your approach, you do not understand the problem well enough to implement it.

---

## 2. Problem Classification Taxonomy

Before doing anything with a problem, classify it:

### 2.1 By Origin

| Type | Description | Example |
|------|-------------|---------|
| **Foundational Gap** | Missing knowledge that blocks an entire subtree | "How does a P-wave actually form from ion-channel dynamics to the surface ECG?" |
| **Architectural Gap** | Unclear how components connect or interact | "Should fiducial detection feed into the agentic pipeline synchronously or asynchronously?" |
| **Domain Gap** | Medical or clinical knowledge needed | "What ST-elevation thresholds are gender- and age-adjusted per 2025 AHA guidelines?" |
| **Technical Gap** | Engineering unknowns | "Can DeepSeek-VL2 reliably detect J-point elevation on a paper-strip photo at 300 DPI?" |
| **Integration Gap** | Problems that emerge only when subsystems meet | "RAG retrieval returns textbook content that contradicts the signal-derived finding — who wins?" |
| **Edge-Case Gap** | Discovered mid-work, often the most dangerous | "What happens when Lead aVR is the only lead with ST-elevation? (posterior MI)" |

### 2.2 By Severity

| Level | Meaning | Action |
|-------|---------|--------|
| **STAT** | Patient safety implication | Immediate research node, DEC (Domain Expert Council) review mandatory |
| **Critical** | Blocks multiple downstream nodes | Priority research, RRC review before proceeding |
| **Standard** | Blocks one node | Normal FD-FPRE cycle |
| **Enhancement** | Improves quality but doesn't block | Queue for after gate passage |

### 2.3 By Scope

| Scope | Meaning |
|-------|---------|
| **Local** | Contained within one node (e.g., bandpass filter cutoff frequency) |
| **Cross-Node** | Affects 2+ nodes in the same SDA branch (e.g., fiducial format affects features AND agents) |
| **Cross-Branch** | Affects nodes in different SDA branches (e.g., signal quality threshold affects both Signal Core and Diagnosis Core) |
| **Global** | Affects the entire system (e.g., data format standardization, API key management) |

---

## 3. The FD-FPRE Methodology (First-Principles Discovery)

FD-FPRE is the engine that powers research-first. For every identified problem:

### 3.1 Start from Absolute First Principles

Do not start from "how does library X do it." Start from physics, chemistry, biology, or mathematics.

**Example for P-wave analysis:**
1. **Ion channels**: Na+/K+/Ca2+ dynamics in atrial myocytes
2. **Cellular depolarization**: How a single cell generates an action potential
3. **Tissue propagation**: How depolarization spreads through atrial tissue (conduction velocity, anisotropy)
4. **Surface projection**: How the dipole vector projects onto each lead (Einthoven's triangle, hexaxial system)
5. **Recording mechanics**: ADC resolution, sampling rate, electrode impedance, filtering
6. **Signal representation**: Digital samples → morphology → clinical interpretation
7. **2025-2026 SOTA**: What do the best current systems do? Where do they fail?

### 3.2 Broad-Then-Deep Literature Search

| Phase | Sources | Goal |
|-------|---------|------|
| **Broad sweep** | PubMed, arXiv, IEEE Xplore, Google Scholar, FDA guidance docs | Map the landscape — what exists, what's contested, what's missing |
| **Deep dive** | Top 15-25 papers from broad sweep, textbook chapters, AHA/ESC guidelines | Extract methods, equations, validation results, limitations |
| **Edge scan** | Conference proceedings (CinC, EMBC), preprints, GitHub repos, clinical case reports | Find what the mainstream missed — rare conditions, failed approaches, novel techniques |

**Minimum citation requirement:** 15 high-quality 2024-2026 sources per research node.

### 3.3 Required Outputs

Every FD-FPRE cycle produces:

```
FirstPrinciples-Discovery.md
├── Search Log (exact queries, databases, date, result counts)
├── First-Principles Derivation (KaTeX equations where applicable)
├── Literature Synthesis (not summaries — synthesis with critical analysis)
├── Decision Matrix (approaches ranked on ≥5 criteria with weighted scores)
├── Gap Analysis (what the literature does NOT answer)
├── Recommended Approach (with full justification)
└── Traceability Links (back to root problem + forward to implementation)
```

### 3.4 Decision Matrix Template

For every non-trivial choice, construct a formal decision matrix:

| Criterion (weight) | Approach A | Approach B | Approach C |
|---------------------|-----------|-----------|-----------|
| Clinical accuracy (0.30) | Score + evidence | Score + evidence | Score + evidence |
| Robustness to noise (0.20) | ... | ... | ... |
| Computational cost (0.10) | ... | ... | ... |
| Interpretability (0.20) | ... | ... | ... |
| Integration complexity (0.10) | ... | ... | ... |
| 2026 SOTA alignment (0.10) | ... | ... | ... |
| **Weighted Total** | **X.XX** | **X.XX** | **X.XX** |

Every score must cite its evidence. No gut feelings.

---

## 4. Dynamic Branching Protocol

Problems do not arrive neatly at the start. They emerge mid-work. U-HIEF v4 handles this with dynamic branching:

### 4.1 Trigger Conditions

A new child node MUST be spawned immediately when:

1. **During research**: A question arises that the current node's scope cannot answer
2. **During review**: RRC or QASVS identifies a gap not covered by existing nodes
3. **During implementation**: An assumption turns out to be wrong (halt implementation, spawn research node)
4. **Cross-node discovery**: Work in Node A reveals that Node B's approach needs revisiting
5. **Clinical edge case**: A DEC member identifies a scenario not covered

### 4.2 Spawn Procedure

```
1. STOP current work immediately (do not "quickly fix it")
2. Write a Problem Statement: What is the gap? Why can't the current node handle it?
3. Classify the problem (Section 2 above)
4. Create a new child node with:
   - Unique node ID (parent.child notation, e.g., 2.3.1.NEW-1)
   - Full Team Contract (using the SDA Child Contract Template)
   - Assigned team (usually RES + FD-FPRE Swarm)
   - Explicit scope boundary (what this node WILL and WILL NOT address)
5. Notify the parent SDA lead
6. Add to Traceability Dashboard
7. Resume current work ONLY on the parts that are not affected by this gap
```

### 4.3 Anti-Pattern: The "Quick Fix"

**NEVER** do this:
- "I'll just hardcode this for now and research it later"
- "This edge case probably won't happen in practice"
- "The library handles this, I don't need to understand it"
- "We can always change it later"

In clinical software, every "quick fix" is technical debt that can kill.

---

## 5. Quality Gates: The Three-Lock System

No problem is considered "solved" until it passes three independent gates:

### 5.1 Gate 1: RRC (Revision & Reflection Council)

**Role**: Honest, adversarial peer review.

The RRC asks:
- Is the first-principles derivation correct and complete?
- Does the literature review miss any major work?
- Is the decision matrix fairly weighted?
- Are there unstated assumptions?
- Would this survive peer review at a top journal?
- Are the edge cases addressed?

**Output**: Written review with "Pass", "Revise" (with specific requirements), or "Fail" (with fundamental objections).

### 5.2 Gate 2: QASVS (Quality Assurance & Stakeholder Validation)

**Role**: Validate against stakeholder needs and real-world conditions.

The QASVS checks:
- Does this solution actually serve the ER nurse in a high-stress scenario?
- Does it meet the cardiologist's diagnostic rigor expectations?
- Does it comply with FDA software guidance (SaMD framework)?
- Is it accessible (color-blind safe, screen-reader compatible)?
- Does it degrade gracefully under poor-quality input?

**Output**: Stakeholder validation report with sign-off or rejection.

### 5.3 Gate 3: DEC (Domain Expert Council)

**Role**: Domain-specific validation.

For this project, the DEC includes perspectives from:
- **Cardiologist**: Clinical accuracy, diagnostic validity
- **ECG Signal Expert**: Signal processing correctness, artifact handling
- **ER Nurse**: Usability under stress, cognitive load, glanceability
- **AI/XAI Architect**: Model behavior, explainability, failure modes
- **UI/UX Expert**: Interface design, information hierarchy

**Output**: Domain sign-off or specific clinical/technical objections.

### 5.4 The Gate Sequence

```
Research Complete
       │
       ▼
   RRC Review ──── Fail? ──→ Revise and resubmit
       │
      Pass
       │
       ▼
  QASVS Validation ── Fail? ──→ Revise and resubmit
       │
      Pass
       │
       ▼
  DEC Sign-off ──── Fail? ──→ Revise and resubmit
       │
      Pass
       │
       ▼
  "Research-First Gate Passed"
  (EPM written approval)
       │
       ▼
  IEC Contract Activated
  (Implementation may begin)
```

---

## 6. Publication-Grade Module Reports (PGMRs)

Every major problem resolution produces 2-4 PGMRs. These are not documentation — they are journal-style papers.

### 6.1 PGMR Structure (IEEE/NEJM/AHA Template)

```markdown
# [Title]: [Descriptive subtitle]

## Abstract
- Problem statement (1-2 sentences)
- Methods used (1-2 sentences)
- Key findings (1-2 sentences)
- Significance (1 sentence)

## 1. Introduction
- Clinical context and motivation
- Gap in current approaches
- Contribution of this work

## 2. Background & Related Work
- First-principles foundation
- Literature review with critical analysis
- How this work differs

## 3. Methods
- Complete methodology with KaTeX equations
- Decision matrix and justification
- Implementation approach (if post-gate)

## 4. Results
- Quantitative findings
- Comparison against alternatives
- Edge-case analysis

## 5. Discussion
- Interpretation of results
- Limitations
- Clinical implications
- Future directions

## 6. Conclusion

## References
- ≥15 high-quality citations (2024-2026 preferred)

## Appendix
- Supplementary data, extended derivations, raw search logs
```

### 6.2 What Counts as "Publication-Grade"

- A domain expert should be able to read it and understand every decision
- Every claim is backed by evidence (citation, derivation, or empirical result)
- No hand-waving ("this is probably fine", "standard practice")
- Equations are typeset in KaTeX, not described in prose
- Figures and diagrams are included where they aid understanding
- Limitations are stated honestly, not buried

---

## 7. Problem Resolution Workflow — Complete Sequence

Here is the exact sequence for dealing with ANY problem in this project:

```
┌─────────────────────────────────────────────────┐
│  1. IDENTIFY                                     │
│     - What is the problem?                       │
│     - Classify: Origin, Severity, Scope          │
│     - Write Problem Statement                    │
├─────────────────────────────────────────────────┤
│  2. SCOPE                                        │
│     - What does this node WILL address?           │
│     - What does it WILL NOT address?              │
│     - What are the inputs and outputs?            │
│     - What nodes depend on this?                  │
├─────────────────────────────────────────────────┤
│  3. RESEARCH (FD-FPRE)                           │
│     - First principles derivation                │
│     - Broad literature sweep                     │
│     - Deep dive on top sources                   │
│     - Edge-case scan                             │
│     - Decision matrix construction               │
│     - Gap analysis                               │
│     - Output: FirstPrinciples-Discovery.md       │
├─────────────────────────────────────────────────┤
│  4. DRAFT (PJS)                                  │
│     - Write 2-4 PGMRs from research artifacts    │
│     - Full journal template                      │
│     - KaTeX equations, figures, citations         │
├─────────────────────────────────────────────────┤
│  5. REVIEW (RRC)                                 │
│     - Adversarial peer review                    │
│     - Pass / Revise / Fail                       │
│     - If Revise or Fail → back to Step 3 or 4   │
├─────────────────────────────────────────────────┤
│  6. VALIDATE (QASVS + DEC)                       │
│     - Stakeholder validation                     │
│     - Domain expert sign-off                     │
│     - If Fail → back to Step 3                   │
├─────────────────────────────────────────────────┤
│  7. GATE APPROVAL (EPM)                          │
│     - EPM reviews all artifacts                  │
│     - Written "Research-First Gate Passed"       │
│     - IEC Contract issued                        │
├─────────────────────────────────────────────────┤
│  8. IMPLEMENT (IEC)                              │
│     - Use ONLY approved research artifacts       │
│     - ImplementationLog.md for traceability      │
│     - If new gap found → STOP → back to Step 1  │
├─────────────────────────────────────────────────┤
│  9. VERIFY                                       │
│     - Does implementation match research?        │
│     - Clinical validation against known cases    │
│     - Update PGMRs with empirical results        │
├─────────────────────────────────────────────────┤
│  10. LINK                                        │
│      - Update Traceability Dashboard             │
│      - Cross-link to related nodes               │
│      - Update project notes and daily logs       │
└─────────────────────────────────────────────────┘
```

---

## 8. Traceability: Every Problem Links to the Root

Every problem, research output, decision, and implementation artifact must trace back to the root problem:

```
Root Problem: Build ideal local ECG analysis platform for ER clinicians
    │
    ├── SDA-1: Signal & Vision Core
    │   ├── Node 1.1: ECG Ingestion
    │   │   ├── Problem: "How to handle 12-lead .mat format from PTB-XL?"
    │   │   ├── FD-FPRE: FirstPrinciples-Discovery-1.1.md
    │   │   ├── PGMRs: PGMR-1.1a.md, PGMR-1.1b.md
    │   │   ├── Decision: ADR-001-ecg-ingestion-format.md
    │   │   └── Traces to: Root → "Input: ECG in multiple formats"
    │   └── ...
    ├── SDA-2: Diagnosis & Agentic Core
    │   └── ...
    ├── SDA-3: UI/UX & ER Workflow
    │   └── ...
    └── SDA-4: Knowledge Base & RAG & Safety
        └── ...
```

### 8.1 Traceability Dashboard

A living document (`Traceability_Dashboard.md`) maintained at the project root:

```markdown
| Node ID | Problem | Status | FD-FPRE | PGMRs | Gate | IEC | Owner |
|---------|---------|--------|---------|-------|------|-----|-------|
| 1.1     | ECG ingestion formats | Research | Done | 2/2 | Pending | - | SDA-1 |
| 1.2     | Signal preprocessing | Research | In Progress | 0/2 | - | - | SDA-1 |
| ...     | ...     | ...    | ...     | ...   | ...  | ... | ...   |
```

Status values: `Identified` → `Research` → `Draft` → `Review` → `Validated` → `Gate Passed` → `Implementing` → `Verified` → `Complete`

---

## 9. Cross-Project Problem Patterns

Problems in this project often mirror patterns from the broader ECG analysis domain. Watch for:

### 9.1 The "Ground Truth" Trap
**Problem**: Using PTB-XL labels as ground truth during inference.
**Rule**: PTB-XL labels are for training/evaluation ONLY. The final system must derive its own findings from signal + vision + agentic reasoning.

### 9.2 The "Library Black Box" Trap
**Problem**: Trusting a library's output without understanding its internals.
**Rule**: Every library (ECGdeli, NeuroKit2, SciPy filters) must have its algorithm understood from first principles. If you cannot derive what the library does, you cannot validate its output.

### 9.3 The "Narration Risk" Trap
**Problem**: LLM generates free-text ECG interpretations that sound confident but are factually wrong.
**Rule**: All LLM outputs must be grounded in (a) computed signal features and (b) RAG-retrieved textbook citations. No unsupported narration.

### 9.4 The "One-Size-Fits-All" Trap
**Problem**: Same thresholds/criteria for all patients regardless of age, sex, or clinical context.
**Rule**: Every threshold must be researched for demographic variation. ST-elevation criteria differ by sex and lead. QTc correction differs by heart rate formula. Axis interpretation differs by age.

### 9.5 The "Happy Path" Trap
**Problem**: System works on clean PTB-XL records but fails on real-world noisy inputs.
**Rule**: Quality assessment (Node 1.3) must fail loudly. Every downstream node must handle the "what if quality is marginal?" case explicitly.

---

## 10. The Four SDA Branches and Their Problem Domains

Understanding where problems live helps route them correctly:

### SDA-1: Signal & Vision Core
**Problem domain**: Everything from raw electrical signal to computed features.
- Ingestion format handling
- Preprocessing (filtering, baseline, artifact removal)
- Quality assessment
- Fiducial detection (P, QRS, T onset/peak/offset)
- Feature extraction (intervals, axes, voltages, morphology)
- Vision-based verification (DeepSeek-VL2 reading ECG images)

### SDA-2: Diagnosis & Agentic Core
**Problem domain**: Everything from features to clinical findings.
- Agent architecture (5 specialists + orchestrator)
- Reasoning chains (how each agent derives findings)
- Confidence scoring
- STAT condition detection (STEMI, Wellens, de Winter, AVB, VT/VF)
- Conflict resolution (when agents disagree)
- Beat-by-beat and lead-by-lead analysis strategy

### SDA-3: UI/UX & ER Workflow
**Problem domain**: Everything the clinician sees and interacts with.
- General dashboard (all leads, zoom, pan, annotations)
- Per-disease dashboards (color-coded, highlighted, arrows)
- ER optimization (glanceability, cognitive load, color-blind safety)
- Natural-language Q&A ("click anywhere and ask")
- Information hierarchy (what shows first, what's expandable)
- Cardiologist extension (deeper analysis views)

### SDA-4: Knowledge Base & RAG & Safety
**Problem domain**: Everything about grounding AI outputs in evidence.
- Book ingestion (4 ECG textbooks with figures)
- Figure extraction and indexing
- RAG pipeline (chunking, embedding, retrieval, citation)
- Safety layer (no unsupported narration, hedging language)
- Source attribution (every finding links to book/page/figure)
- Regulatory compliance (SaMD considerations, AI labeling)

---

## 11. Emergency Problem Protocol (STAT Conditions)

For problems classified as STAT (patient safety implication):

1. **Immediate halt** on all related implementation
2. **DEC emergency review** — cardiologist perspective mandatory
3. **Dedicated research node** spawned with highest priority
4. **No workarounds** — the problem must be solved correctly, not patched
5. **Regression test** — after resolution, test against all known STAT conditions:
   - STEMI (anterior, inferior, lateral, posterior, right ventricular)
   - Wellens syndrome (Type A and B)
   - de Winter T-waves
   - Complete AV block (third-degree)
   - Sustained VT/VF
   - Hyperkalemia (peaked T, widened QRS, sine wave)
   - Brugada pattern (Type 1)
   - Long QT with TdP risk

---

## 12. Problem Documentation Standards

Every problem, at minimum, gets recorded in:

1. **The node's FD-FPRE output** (if it spawned a research cycle)
2. **The Traceability Dashboard** (status tracked)
3. **The relevant PGMR** (if it led to a significant finding)
4. **An ADR** (if it involved a non-trivial decision between alternatives)
5. **A bug postmortem** (if it was discovered after implementation)

### 12.1 ADR Template (Architecture Decision Record)

```markdown
---
adr: NNN
project: YouOwnECG
date: YYYY-MM-DD
status: proposed | accepted | deprecated | superseded
tags: [decision, signal | diagnosis | ui | rag]
---

# ADR-NNN: [Title]

## Context
What is the problem? Why does it need a decision now?

## Decision
What did we decide? Be specific.

## Alternatives Considered
| Alternative | Pros | Cons | Why rejected |
|------------|------|------|-------------|
| A | ... | ... | ... |
| B | ... | ... | ... |

## Consequences
- What changes as a result of this decision?
- What new constraints does this introduce?
- What becomes easier? What becomes harder?

## Related
- [[node-id]] — the node that spawned this decision
- [[pgmr-id]] — the PGMR that justified it
```

---

## Summary: The Ten Commandments of Problem-Handling

1. **Research first, implement never (until gate passes)**
2. **Start from first principles, not from Stack Overflow**
3. **Classify every problem before touching it**
4. **Spawn a new node for every new gap — never "quick fix"**
5. **Every decision needs a matrix, not a gut feeling**
6. **Three independent gates must pass before implementation**
7. **Every artifact traces back to the root problem**
8. **STAT problems halt everything until resolved**
9. **Publication-grade or it didn't happen**
10. **Cross-link everything — problems in isolation are problems missed**

---

*This document is the foundational reference for all problem-handling in the YouOwnECG project. Every team member, every contract, every node operates under these rules. No exceptions.*
