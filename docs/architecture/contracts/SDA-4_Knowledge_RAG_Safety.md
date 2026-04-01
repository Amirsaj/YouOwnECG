# SDA-4: Knowledge Base & RAG & Safety — Decomposition Tree + Contracts

**TEAM CONTRACT — U-HIEF v4**
**Issuer:** EPM
**Recipient:** SDA-4 Lead Architect
**Date:** 2026-03-26
**Scope:** Everything about grounding AI outputs in verifiable evidence
**Charter:** [Master_Charter.md](../Master_Charter.md) v1.1

---

## Depth-4 Decomposition Tree

```
4.0 Knowledge Base & RAG & Safety
├── 4.1 Book Ingestion Pipeline
│   ├── 4.1.1 PDF Text Extraction
│   │   ├── 4.1.1.1 FD-FPRE: PDF structure from first principles (text streams, font encoding, layout)
│   │   ├── 4.1.1.2 PyMuPDF extraction: text blocks, paragraphs, headers, page numbers
│   │   ├── 4.1.1.3 Per-book preprocessing (4 books have different layouts, fonts, structures)
│   │   │   ├── Chou's Electrocardiography in Clinical Practice (135 MB)
│   │   │   ├── Marriott's Practical Electrocardiography (134 MB)
│   │   │   ├── Goldberger's Clinical Electrocardiography (19 MB)
│   │   │   └── The ECG Made Easy 8th Edition (26 MB)
│   │   └── 4.1.1.4 Quality validation: spot-check extracted text vs original PDF
│   ├── 4.1.2 Figure Extraction & Classification
│   │   ├── 4.1.2.1 FD-FPRE: Medical figure extraction from PDF (2024–2026 methods)
│   │   ├── 4.1.2.2 Image extraction from PDF pages (PyMuPDF image methods)
│   │   ├── 4.1.2.3 Figure classification: ECG strip, diagram, table, photo, illustration
│   │   ├── 4.1.2.4 Figure-to-text association: which figure belongs to which paragraph/section
│   │   └── 4.1.2.5 PGAM: PGMR on medical textbook figure extraction and classification
│   ├── 4.1.3 Book Structure Parsing
│   │   ├── 4.1.3.1 Table of contents extraction per book
│   │   ├── 4.1.3.2 Chapter/section/subsection hierarchy detection
│   │   ├── 4.1.3.3 Metadata per chunk: book title, chapter, section, page number, figure refs
│   │   └── 4.1.3.4 Cross-reference detection (when one section references another)
│   └── 4.1.4 FD-FPRE: Medical Textbook Knowledge Representation
│       ├── 4.1.4.1 How is ECG knowledge structured in textbooks? (anatomy → physiology → pathology → pattern)
│       ├── 4.1.4.2 Knowledge types: factual (criteria), procedural (how to read), visual (reference images)
│       ├── 4.1.4.3 How to preserve knowledge structure through ingestion
│       └── 4.1.4.4 PGAM: PGMR on medical knowledge representation for RAG systems
│
├── 4.2 Chunking Strategy
│   ├── 4.2.1 FD-FPRE: Chunking Methods from First Principles
│   │   ├── 4.2.1.1 Fixed-size vs semantic vs recursive vs document-structure-based chunking
│   │   ├── 4.2.1.2 Chunk size optimization (too small = no context, too large = diluted retrieval)
│   │   ├── 4.2.1.3 Overlap strategy (sliding window, sentence overlap, paragraph overlap)
│   │   └── 4.2.1.4 PGAM: PGMR on optimal chunking for medical textbook RAG
│   ├── 4.2.2 Medical-Domain-Specific Chunking
│   │   ├── 4.2.2.1 ECG criteria should never be split across chunks (e.g., STEMI criteria = one chunk)
│   │   ├── 4.2.2.2 Diagnostic criteria tables: chunk as complete units
│   │   ├── 4.2.2.3 Figures and their captions: co-located in same chunk or linked
│   │   └── 4.2.2.4 Clinical decision rules: keep complete (e.g., Sgarbossa criteria)
│   ├── 4.2.3 Chunk Metadata Enrichment
│   │   ├── 4.2.3.1 Metadata per chunk: book, chapter, section, page, type (criteria/explanation/figure)
│   │   ├── 4.2.3.2 Medical concept tagging (which conditions does this chunk discuss?)
│   │   ├── 4.2.3.3 Difficulty level (basic → advanced) for ER nurse vs cardiologist retrieval
│   │   └── 4.2.3.4 Lead/region tagging (does this chunk discuss specific leads or territories?)
│   └── 4.2.4 Validation
│       ├── 4.2.4.1 Chunk quality audit: sample 100 chunks, verify no split criteria
│       ├── 4.2.4.2 Coverage audit: are all major ECG conditions represented?
│       └── 4.2.4.3 Deduplication: same information across 4 books — handle or leverage?
│
├── 4.3 Embedding & Vector Store
│   ├── 4.3.1 FD-FPRE: Embedding Models for Medical Text
│   │   ├── 4.3.1.1 sentence-transformers model selection (general vs medical-domain models)
│   │   ├── 4.3.1.2 Embedding dimension and similarity metrics (cosine, dot product)
│   │   ├── 4.3.1.3 Medical terminology handling (do general embeddings capture "J-point elevation"?)
│   │   └── 4.3.1.4 PGAM: PGMR on embedding model selection for clinical ECG RAG
│   ├── 4.3.2 ChromaDB Configuration
│   │   ├── 4.3.2.1 Collection design (one collection vs per-book vs per-condition)
│   │   ├── 4.3.2.2 Metadata filtering (filter by book, chapter, condition, lead)
│   │   ├── 4.3.2.3 Persistence and backup strategy
│   │   └── 4.3.2.4 Performance: query latency targets (< 200ms for top-10 retrieval)
│   ├── 4.3.3 Indexing Pipeline
│   │   ├── 4.3.3.1 Batch embedding of all chunks (4 books worth)
│   │   ├── 4.3.3.2 Figure embedding (embed caption text + classification label)
│   │   ├── 4.3.3.3 Incremental update strategy (add new sources without re-indexing all)
│   │   └── 4.3.3.4 Index validation: sample queries → verify relevant chunks are top-ranked
│   └── 4.3.4 FD-FPRE: Vector Search from First Principles
│       ├── 4.3.4.1 Approximate nearest neighbor algorithms (HNSW, IVF)
│       ├── 4.3.4.2 Embedding space geometry for medical concepts
│       └── 4.3.4.3 When vector similarity fails (semantic gap between query and answer)
│
├── 4.4 Retrieval Pipeline
│   ├── 4.4.1 Query Formulation
│   │   ├── 4.4.1.1 FD-FPRE: Query strategies for medical RAG (2024–2026 literature)
│   │   ├── 4.4.1.2 Finding → query translation (agent finding "ST elevation V1-V4" → retrieval query)
│   │   ├── 4.4.1.3 Multi-query: generate multiple query variants for better recall
│   │   └── 4.4.1.4 Hypothetical document embedding (HyDE) for medical queries
│   ├── 4.4.2 Re-Ranking
│   │   ├── 4.4.2.1 FD-FPRE: Re-ranking methods (cross-encoder, LLM-based, reciprocal rank fusion)
│   │   ├── 4.4.2.2 Medical relevance scoring (is this chunk actually about the query condition?)
│   │   ├── 4.4.2.3 Diversity: avoid returning 5 chunks from the same section
│   │   └── 4.4.2.4 PGAM: PGMR on retrieval and re-ranking for clinical ECG knowledge
│   ├── 4.4.3 Citation Generation
│   │   ├── 4.4.3.1 Citation format: "Chou's Electrocardiography, Ch. 5, p. 142, Fig. 5.3"
│   │   ├── 4.4.3.2 Multiple source citation (same finding supported by 2+ books)
│   │   ├── 4.4.3.3 Citation verification: does the cited page actually say what we claim?
│   │   └── 4.4.3.4 Figure citation: link finding to relevant ECG figure in textbook
│   ├── 4.4.4 Context Window Management
│   │   ├── 4.4.4.1 How many chunks per agent query? (too few = incomplete, too many = diluted)
│   │   ├── 4.4.4.2 Context ordering: most relevant first? chronological? structured?
│   │   ├── 4.4.4.3 Token budget allocation: features + RAG context + system prompt must fit
│   │   └── 4.4.4.4 PGAM: PGMR on context management for RAG-augmented clinical reasoning
│   └── 4.4.5 Retrieval Validation
│       ├── 4.4.5.1 Evaluation dataset: 50+ ECG findings → expected textbook references
│       ├── 4.4.5.2 Relevance metrics: Precision@5, Recall@10, MRR
│       ├── 4.4.5.3 Failure analysis: which conditions have poor retrieval? Why?
│       └── 4.4.5.4 A/B testing: different chunking/embedding strategies on same queries
│
├── 4.5 Safety Layer
│   ├── 4.5.1 FD-FPRE: AI Safety in Clinical Decision Support
│   │   ├── 4.5.1.1 Literature: AI safety frameworks for medical AI (FDA SaMD guidance 2024–2026)
│   │   ├── 4.5.1.2 Failure modes: hallucination, overconfidence, under-confidence, anchoring bias
│   │   ├── 4.5.1.3 Legal and ethical considerations for AI ECG interpretation
│   │   └── 4.5.1.4 PGAM: PGMR on safety framework for AI-assisted ECG interpretation
│   ├── 4.5.2 Grounding Check (Anti-Hallucination)
│   │   ├── 4.5.2.1 Every LLM output must be grounded in BOTH:
│   │   │   ├── (a) Computed signal features (from SDA-1 pipeline)
│   │   │   └── (b) RAG-retrieved textbook evidence
│   │   ├── 4.5.2.2 Grounding verification: automated check before output reaches UI
│   │   ├── 4.5.2.3 Ungrounded claim handling: strip the claim, flag as "insufficient evidence"
│   │   └── 4.5.2.4 PGAM: PGMR on LLM grounding verification for medical applications
│   ├── 4.5.3 Mandatory Safety Hedging
│   │   ├── 4.5.3.1 Language rules:
│   │   │   ├── "Findings suggest..." never "Diagnosis is..."
│   │   │   ├── "Consistent with..." never "This is..."
│   │   │   ├── "Clinical correlation recommended" on every report
│   │   │   └── Confidence scores always displayed
│   │   ├── 4.5.3.2 "AI-GENERATED" label: prominent, non-removable, on every output
│   │   ├── 4.5.3.3 Disclaimer language (reviewed by legal/compliance persona)
│   │   └── 4.5.3.4 What the system explicitly CANNOT do (it is not a diagnosis, not a substitute for clinical judgment)
│   ├── 4.5.4 Narration Risk Prevention
│   │   ├── 4.5.4.1 FD-FPRE: The narration risk (LLM writes fluent, confident, wrong ECG descriptions)
│   │   ├── 4.5.4.2 Template-based output: structured findings, NOT free-text paragraphs
│   │   ├── 4.5.4.3 Each statement must reference its source: [Signal: ST elev 2.3mm V2] [RAG: Chou Ch.5 p.142]
│   │   └── 4.5.4.4 Free-text allowed ONLY in Q&A responses, and ONLY when grounded
│   └── 4.5.5 Audit Trail
│       ├── 4.5.5.1 Log every agent call: input features, RAG context, agent response, confidence
│       ├── 4.5.5.2 Log every grounding check: pass/fail, what was stripped
│       ├── 4.5.5.3 Reproducibility: same ECG input → same output (deterministic pipeline)
│       └── 4.5.5.4 PGAM: PGMR on clinical AI audit trail design
│
└── 4.6 Source Attribution System
    ├── 4.6.1 Attribution Architecture
    │   ├── 4.6.1.1 Every finding → list of supporting sources
    │   ├── 4.6.1.2 Source types: textbook (book, chapter, page, figure), computed feature, agent reasoning
    │   ├── 4.6.1.3 Attribution confidence: how strongly does this source support this finding?
    │   └── 4.6.1.4 PGAM: PGMR on source attribution for AI clinical decision support
    ├── 4.6.2 Figure Reference System
    │   ├── 4.6.2.1 Link findings to relevant ECG figures in textbooks
    │   ├── 4.6.2.2 Display: show textbook figure alongside patient's ECG for comparison
    │   ├── 4.6.2.3 Figure relevance scoring (is this the right reference figure?)
    │   └── 4.6.2.4 Copyright/fair-use considerations for figure display
    ├── 4.6.3 Multi-Source Consensus
    │   ├── 4.6.3.1 Finding supported by multiple books → stronger evidence
    │   ├── 4.6.3.2 Books disagree on criteria → present both, flag discrepancy
    │   └── 4.6.3.3 Medical literature supplement (beyond the 4 books, if needed)
    └── 4.6.4 FD-FPRE: Evidence-Based Medicine Principles for AI
        ├── 4.6.4.1 Levels of evidence (guidelines > RCTs > case series > expert opinion)
        ├── 4.6.4.2 How to rank textbook authority
        └── 4.6.4.3 PGAM: PGMR on evidence hierarchy in AI-assisted clinical interpretation
```

---

## First-Level Child Contracts

### Contract SDA-4.1: Book Ingestion Pipeline

```
TEAM CONTRACT — U-HIEF v4
Issuer: SDA-4 Lead Architect – Branch Knowledge Base & RAG & Safety
Recipient: RES + FD-FPRE Swarm — Book Ingestion Team
Scope: Design and justify the complete book ingestion pipeline for 4 ECG
textbooks: PDF text extraction (PyMuPDF), figure extraction and classification,
book structure parsing (TOC, chapters, sections), and metadata enrichment.
Books located at: /Users/amirsadjadtaleban/Documents/NewECG_Agentic/ecg-platform/books

You are a Document Engineering and Medical Knowledge Extraction Expert. Your
sole mission is ideal, zero-miss, publication-grade outcomes for this exact
node. Ignore all time, computation, and cost constraints. Proceed leisurely
and thoroughly. Do everything. Explore every edge case.

Mandatory Rules:
- Research-First: Complete 100% of FD-FPRE + RES work and obtain RRC/QASVS
  approval *before* any implementation.
- Dynamic Branching: If any new gap appears, instantly create a new child node.
- FD-FPRE: Start from PDF structure first principles, then medical knowledge
  representation, then 2026 SOTA extraction methods.
- PGAM: Produce minimum 2–4 PGMRs for this node.

Deliverables (in order):
1. FD-FPRE: PDF structure and text extraction from first principles
2. FD-FPRE: Medical figure extraction and classification methods
3. Per-book structure analysis (each of the 4 books has different layout)
4. Figure-to-text association algorithm
5. Metadata schema design (book, chapter, section, page, figure, condition tags)
6. Quality validation protocol
7. Draft 2–4 PGMRs
8. Submit to RRC

Proceed leisurely. Research everything broadly and in depth. Spawn new nodes
for any emerging gap. Produce 2–4 PGMRs per major deliverable. Never rush.
```

### Contract SDA-4.2: Chunking Strategy

```
TEAM CONTRACT — U-HIEF v4
Issuer: SDA-4 Lead Architect
Recipient: RES + FD-FPRE Swarm — Chunking Team
Scope: Research and design the optimal chunking strategy for medical ECG
textbooks: chunk method selection, medical-domain-specific rules (never
split criteria across chunks), metadata enrichment per chunk, and validation.

Deliverables:
1. FD-FPRE: Chunking methods comparison (fixed, semantic, recursive, structure-based)
2. Medical domain chunking rules (keep criteria together, co-locate figures, etc.)
3. Chunk size optimization experiments
4. Metadata enrichment schema (book, chapter, section, page, type, conditions, leads)
5. Deduplication strategy (same info in 4 books)
6. Chunk quality audit methodology
7. Draft 2–4 PGMRs
8. Submit to RRC

Proceed leisurely. Research everything broadly and in depth. Spawn new nodes
for any emerging gap. Produce 2–4 PGMRs per major deliverable. Never rush.
```

### Contract SDA-4.3: Embedding & Vector Store

```
TEAM CONTRACT — U-HIEF v4
Issuer: SDA-4 Lead Architect
Recipient: RES + FD-FPRE Swarm — Embedding Team
Scope: Research embedding model selection for medical ECG text, ChromaDB
configuration, indexing pipeline, and retrieval performance validation.

Deliverables:
1. FD-FPRE: Embedding models for medical text (general vs domain-specific)
2. FD-FPRE: Vector search from first principles (ANN algorithms, embedding geometry)
3. Embedding model decision matrix
4. ChromaDB collection and metadata filter design
5. Indexing pipeline (batch embed, figure embed, incremental update)
6. Retrieval validation (sample queries, relevance metrics)
7. Draft 2–4 PGMRs
8. Submit to RRC

Proceed leisurely. Research everything broadly and in depth. Spawn new nodes
for any emerging gap. Produce 2–4 PGMRs per major deliverable. Never rush.
```

### Contract SDA-4.4: Retrieval Pipeline

```
TEAM CONTRACT — U-HIEF v4
Issuer: SDA-4 Lead Architect
Recipient: RES + FD-FPRE Swarm — Retrieval Team
Scope: Design the complete retrieval pipeline: query formulation (finding →
query translation, multi-query, HyDE), re-ranking (cross-encoder, diversity),
citation generation (book/chapter/page/figure format), context window
management for agent prompts, and retrieval validation.

Deliverables:
1. FD-FPRE: Query strategies for medical RAG (2024–2026 SOTA)
2. FD-FPRE: Re-ranking methods (cross-encoder, LLM-based, RRF)
3. Query formulation design (finding → query translation)
4. Re-ranking pipeline design
5. Citation format and verification protocol
6. Context window budget allocation
7. Evaluation dataset (50+ finding → expected reference pairs)
8. Draft 2–4 PGMRs
9. Submit to RRC

Proceed leisurely. Research everything broadly and in depth. Spawn new nodes
for any emerging gap. Produce 2–4 PGMRs per major deliverable. Never rush.
```

### Contract SDA-4.5: Safety Layer

```
TEAM CONTRACT — U-HIEF v4
Issuer: SDA-4 Lead Architect
Recipient: RES + FD-FPRE Swarm — Safety Team
Scope: Design the complete safety layer: grounding check (every LLM output
must be grounded in computed features + RAG evidence), mandatory safety
hedging ("findings suggest", never "diagnosis is"), AI-generated labeling,
narration risk prevention (template-based output, per-statement sourcing),
and audit trail.

THIS IS A PATIENT SAFETY NODE — treat with STAT-level rigor.

Deliverables:
1. FD-FPRE: AI safety in clinical decision support (FDA SaMD guidance, 2024–2026)
2. FD-FPRE: LLM hallucination in medical applications — failure modes and mitigations
3. Grounding verification algorithm (automated check before output reaches UI)
4. Hedging language rules (what phrases are allowed/forbidden)
5. Narration risk prevention protocol (template output, per-statement source references)
6. "AI-GENERATED" label specification
7. Audit trail design (log every agent call, grounding check, output)
8. Draft 2–4 PGMRs
9. Submit to RRC

Proceed leisurely. Research everything broadly and in depth. Spawn new nodes
for any emerging gap. Produce 2–4 PGMRs per major deliverable. Never rush.
```

### Contract SDA-4.6: Source Attribution System

```
TEAM CONTRACT — U-HIEF v4
Issuer: SDA-4 Lead Architect
Recipient: RES + FD-FPRE Swarm — Attribution Team
Scope: Design the source attribution system: every finding links to supporting
sources (textbook citations, computed features, agent reasoning), figure
reference system (show textbook figure alongside patient ECG), multi-source
consensus (multiple books agreeing strengthens evidence), and evidence
hierarchy principles.

Deliverables:
1. FD-FPRE: Evidence-based medicine principles for AI systems
2. Attribution data model (finding → sources with confidence)
3. Figure reference system design
4. Multi-source consensus scoring
5. Discrepancy handling (when books disagree)
6. Draft 2–4 PGMRs
7. Submit to RRC

Proceed leisurely. Research everything broadly and in depth. Spawn new nodes
for any emerging gap. Produce 2–4 PGMRs per major deliverable. Never rush.
```

---

**SDA-4 Tree: 6 first-level nodes, 26 second-level nodes, ~75 leaf nodes. Expected PGMRs: 10–14.**
**Known dynamic nodes: Copyright/fair-use for figure display (4.6.2.4), medical literature supplement beyond 4 books (4.6.3.3).**
