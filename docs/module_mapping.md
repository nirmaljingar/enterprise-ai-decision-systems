# Module Mapping

Every `eads.*` module either traces to one or more IEEE EADS papers or is explicitly labeled as a *Reference implementation*.

| Module | Traced to | Research concept | Scope |
|--------|-----------|------------------|-------|
| `eads.paper_extraction` | All | Phase 1.5 full-text extraction corpus | PyMuPDF-backed extraction of the four IEEE papers into structured JSON/TXT summaries |
| `eads.modernization` | Paper 1 | LRAATF / LLM-Guided Enterprise Modernization (LGEM): semantic code parsing, dependency extraction, microservice decomposition, governance validation | Synthetic legacy-code parsing, dependency extraction, monolith-to-microservice decomposition, modernization validation |
| `eads.knowledge_ingestion` | Paper 2 | LASCI Step 1 — semantic extraction from unstructured enterprise information | Ingest unstructured text (emails, reports, contracts, news) and produce structured evidence |
| `eads.reasoning` | Papers 2, 3 | LASCI / LLM-SSC context-aware and evidence-backed reasoning | Reason over structured evidence and forecasts |
| `eads.agents` | Papers 2, 4 | LASCI multi-agent verification; AGAF agentic decision layer | Multi-agent collaboration primitives, consensus-seeking, tool-calling, message passing |
| `eads.decision` | Paper 3 | LLM-DE / LLM-SSC: LLM reasoning + optimization + forecasting + safety filter | Generate candidate decisions by combining semantic reasoning with solver/forecaster adapters |
| `eads.governance` | Papers 1, 3, 4 | Governance, Validation and Trust Layer / AGAF trust layer | Policy enforcement, safety filtering, permissions, fallback, audit, and trust scoring |
| `eads.core` | Reference implementation | Shared data model, pipeline contract, and public API surface | Dataclass schemas, deterministic orchestration primitives, public plugin interface |
| `eads.evaluation` | Papers 1–4 | LRAATF/LASCI/LLM-DE/AGAF experimental metrics | Reusable benchmark harness and metric definitions |
| `eads.synthetic_data` | All | Domain-agnostic synthetic datasets | Supply chain, healthcare, finance, customer support, and IT operations examples |
| `examples/` | All | End-to-end educational workflows | Reference implementations that demonstrate the decision lifecycle |
| `docs/`, `diagrams/` | All | Reproducible research artifact and textbook-style documentation | Architecture, tutorials, FAQ, limitations, roadmap |

## Public API surface

| Entry point | Status | Description |
|-------------|--------|-------------|
| `eads.paper_extraction.extract_papers_from_directory` | Implemented | PyMuPDF-backed extraction pipeline |
| `eads.core.pipeline.DecisionPipeline` | Implemented | Deterministic orchestration over the full lifecycle |
| `eads.governance.GovernanceLayer` | Implemented (stub) | Policy, safety, permissions, fallback, audit, and trust checks |
| `eads.decision.DecisionEngine` | Implemented (stub) | LLM reasoning with optional solver/forecaster adapters |
| `eads.evaluation.Benchmark` | Implemented | Reproducible benchmark harness with JSON output |
