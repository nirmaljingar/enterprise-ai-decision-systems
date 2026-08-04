# EADS Research Companion: A Reproducible Reference Implementation for IEEE EADS Papers

**Abstract.** The Enterprise AI Decision Systems (EADS) research companion is an open-source, modular, and deterministic reference implementation that operationalizes the concepts in four related IEEE papers on legacy-system modernization, unstructured supply-chain intelligence, reliable LLM-powered decision engines, and agentic generative-AI logistics. It provides a typed pipeline (ingest → modernize → reason → decide → govern → execute → audit), pluggable LLM/solver/forecaster adapters, domain-agnostic synthetic data generators, and a reproducible benchmark harness. This report describes the architecture, the mapping from paper claims to code, the determinism contract, and the artifacts available for citation and extension.

## 1. Introduction

Enterprise AI systems increasingly combine large language models with deterministic safety, optimization, and governance layers. The four IEEE EADS papers propose complementary frameworks: LRAATF/LGEM for legacy modernization, LASCI for supply-chain intelligence, LLM-DE/LLM-SSC for safe decision engines, and AGAF/AGLO for agentic logistics. The EADS Research Companion translates these high-level proposals into runnable modules with explicit paper traceability.

## 2. Architecture

The companion uses a shared data model (`eads.core.types`) and a deterministic `DecisionPipeline` that orchestrates:

1. **Knowledge ingestion** — convert unstructured signals into typed evidence.
2. **Modernization** (optional) — analyze legacy code signals using `eads.modernization`.
3. **Reasoning and agent collaboration** — `eads.reasoning` and `eads.agents`.
4. **Decision generation** — `eads.decision` combining LLM reasoning with solver/forecaster adapters.
5. **Governance** — policy, safety, permissions, fallback, audit, and trust scoring in `eads.governance`.
6. **Execution and audit** — deterministic tool invocation and an immutable `AuditRecord`.

## 3. Paper-to-module mapping

| Paper | Module(s) | Key concept |
|-------|-----------|-------------|
| Modernizing Legacy Enterprise Platforms Using LLM-Driven Refactoring and AI-Assisted Architecture Transformation | `eads.modernization` | LRAATF / LGEM |
| Leveraging Large Language Models and Autonomous Agents for Unstructured Supply Chain Intelligence | `eads.knowledge_ingestion`, `eads.reasoning`, `eads.agents` | LASCI |
| Reliable LLM-Powered Decision Engines for Large-Scale Supply Chain Operations | `eads.decision`, `eads.governance` | LLM-DE / LLM-SSC |
| Operationalizing Generative and Agentic AI Across Complex Logistics Networks | `eads.agents`, `eads.governance` | AGAF / AGLO |

## 4. Reproducibility

All examples use synthetic data and deterministic seeds. The `Benchmark` harness writes versioned `results.json` files. Optional adapters (OpenAI, Anthropic, Ollama, SciPy, PuLP, OR-Tools, sktime) are isolated behind lazy-import adapters and are not required for the core tests.

## 5. Artifacts for citation

- Source code: `https://github.com/nirmaljingar/enterprise-ai-decision-systems`
- Citation metadata: `CITATION.cff`
- Paper DOIs: see `CITING.md`
- Reproducibility suite: `reproducibility/`
