# Roadmap

Current phase: **Phase 2 / early Phase 3** — repository design is largely complete; per-module implementation is in progress.

## Completed

- Phase 1 Research Design Document (`docs/research_design.md`)
- Core `eads.core.types` data model and `DecisionPipeline` skeleton
- Governance layer scaffolding (`eads.governance.*` sub-packages)
- Basic evaluation metrics and benchmark harness skeleton
- Supply-chain synthetic data generator
- `README.md`, `CITATION.cff`, `CITING.md`, `LICENSE`
- CI workflows: `tests.yml`, `lint.yml`, `typecheck.yml`, `docs.yml`

## In progress

- Full-text paper extraction (Phase 1.5)
- Filling module stubs with runnable implementations
- Per-module `README.md` files and tests
- Domain-agnostic synthetic data generators

## Planned

1. `eads.core` — finalize pipeline contract and deterministic state tracking.
2. `eads.governance.audit` — immutable trace records every module must write.
3. `eads.knowledge_ingestion` — produce the evidence graph.
4. `eads.reasoning` — build plans on top of evidence.
5. `eads.decision` — combine plans with solver/forecaster adapters.
6. `eads.governance` — integrate policy, safety, permissions, fallback, audit, and trust.
7. `eads.agents` — add multi-agent collaboration.
8. `eads.modernization` — legacy modernization end-to-end example.
9. `eads.evaluation` + `benchmarks/` — reproducible metrics.
10. `examples/` and `docs/` — tutorials, final diagrams, publication-ready docs.
