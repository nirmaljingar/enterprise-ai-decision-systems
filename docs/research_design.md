# Research Design Document

This document is the Phase 1 research foundation and Phase 2 repository design for the Enterprise AI Decision Systems (EADS) research companion.

## 1. Research corpus

- **Paper 1** — *Modernizing Legacy Enterprise Platforms Using LLM-Driven Refactoring and AI-Assisted Architecture Transformation*.
- **Paper 2** — *Leveraging Large Language Models and Autonomous Agents for Unstructured Supply Chain Intelligence*.
- **Paper 3** — *Reliable LLM-Powered Decision Engines for Large-Scale Supply Chain Operations: Architecture, Safety, and Performance Guarantees*.
- **Paper 4** — *Operationalizing Generative and Agentic AI Across Complex Logistics Networks: Architecture, Governance, and Trust Models*.

None of the four papers carries a verified DOI in this repository yet; see [`CITING.md`](https://github.com/nirmaljingar/enterprise-ai-decision-systems/blob/main/CITING.md).

> **Note on status.** This design is now grounded in the full-text PDF extraction. Exact algorithms, evaluation protocols, and numerical claims are present in `data/papers/extracted/`. Implementation details not directly traceable to a published paper are labeled as *Reference implementation*, *Educational example*, or *Suggested extension*.

## 2. Unifying research question

> How can enterprise AI systems remain reliable, safe, and auditable while delegating decision authority to autonomous LLM agents?

Each paper contributes a necessary piece of the answer: modernization and validation governance (Paper 1), knowledge ingestion and evidence grounding (Paper 2), reliable decision engines (Paper 3), and operational governance, trust, and audit (Paper 4). The central challenge is not raw performance but reliability under autonomy.

## 3. Repository mission

The repository is the official, open, original research companion for EADS. It is domain-agnostic, designed for study, cloning, modification, benchmarking, extension, and citation.

## 4. Guiding principles

- **Scientific rigor:** No invented algorithms; every module traces to one or more papers.
- **Reproducibility:** Synthetic data, deterministic seeds, pinned dependencies.
- **Transparency:** All non-published extensions are explicitly labeled.
- **Modularity:** Independent modules allow future papers to extend without redesign.
- **No proprietary IP:** No employer code, APIs, schemas, datasets, or confidential details.
- **Dependency guardrails:** Core uses Python standard-library patterns plus the minimum open packages needed. Optional adapters are isolated.
- **Determinism contract:** Same input, seed, policy snapshot, and tool versions produce the same observable trace.

## 5. Implementation roadmap

| Phase | Deliverable | Status |
|-------|-------------|--------|
| Phase 1 | Research Design Document | Complete |
| Phase 1.5 | Full paper text extraction | Complete — source PDFs processed locally; public index in `data/papers/papers.json` |
| Phase 2 | Complete repository design | Complete |
| Phase 3 | Incremental per-module implementation | In progress (tested, reference implementations in place) |
