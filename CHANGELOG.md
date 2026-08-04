# Changelog

All notable changes to the EADS Research Companion are documented in this file.

## [2.0.0] - 2026-08-04

A major version because the interfaces a caller depends on changed, and because every module that
traces to a paper now implements a method rather than a placeholder.

### Changed -- breaking

- `DecisionCandidate.actions` is `list[ProposedAction]` rather than `list[dict]`. Governance checks
  typed fields; it no longer regex-scans raw model text, which is what made it fail open.
- `AuditRecord.signatures` is removed. It was a security-shaped field with no signing mechanism.
- Governance fails closed: an action that is missing, unparseable, of an unknown type, or missing a
  required field is rejected rather than approved.
- `Verdict.outcome` distinguishes `approved`, `rejected`, and `escalated`; escalation is not
  authorization and requires a second party.
- `Plan.evidence_refs` contains only the evidence the plan used, not everything ingested.
- `TrustScorer` grades a candidate against the evidence it cites instead of reporting the
  candidate's own confidence. `Verdict.trust_reasons` names every deduction.
- `ModernizationPipeline.analyze` returns service objects, units, cycles, cut edges, and a `parsed`
  flag; unparseable source yields no decomposition.
- `Agent.act` returns a vote, and `Agent.swarm` reports the outcome it measured rather than a fixed
  "consensus reached" string.

### Added

- `eads.knowledge_ingestion`: claim segmentation with exact source spans, cross-source corroboration,
  and confidence derived from checkable detail. Untrusted and instruction-shaped claims are marked
  on the record.
- `eads.reasoning`: multi-hop selection over a typed evidence graph, with contradictions surfaced for
  verification rather than resolved.
- `eads.modernization`: `ast`-based dependency analysis and connected-component service boundaries.
- `eads.agents`: typed-proposal voting with quorum, recorded dissent, and role-scoped tools.
- Reproducibility: injectable clocks (`eads.core.clock`), and the audit record states whether the
  backend honoured the seed.
- `policy_snapshot_id`, actor identity, and typed approver roles on the audit record.
- Benchmark manifests, `eads/evaluation/runner.py`, and a generated `docs/benchmarks/index.md` gated
  against staleness.
- Metrics: `policy_compliance`, `evidence_grounding_rate`, `fallback_recovery_rate`,
  `audit_completeness`, and `injection_resistance`.
- `docs/threat_model.md`, and `tests/test_claims.py`, which fails the suite when a stub label or a
  safety metric drifts from the documentation.
- `tests/test_citations.py`, which resolves every declared DOI against Crossref and asserts the title
  matches.
- `docs/releasing.md`, and `tests/test_release.py`, which fails when version metadata disagrees with
  itself.

### Fixed

- The four paper DOIs. The values shipped in 1.0.0 resolved through Crossref to unrelated papers by
  other authors; the verified identifiers are in `data/papers/papers.json` and checked by a test.
- `mkdocs build --strict` passes; the 1.0.0 navigation pointed at files that did not exist, so the
  documentation badge had never been green.
- Removed the claim that the design was grounded in full-text PDF extraction into
  `data/papers/extracted/`. That extraction was never run and the directory does not exist.
- `approval_rate` is no longer presented as a correctness metric. Approving everything scores 1.0.
- `decision_consistency` compares repeats of the *same* scenario.

### Notes

Every implementation in this release is lexical, rule-based, and calls no language model. That is a
deliberate tradeoff for determinism -- a benchmark run replays to the same answer -- and its cost is
listed per module in `docs/limitations.md`. The published benchmark numbers are runs of this
implementation against synthetic manifests; they are not results from the papers.

## [1.0.0] - 2026-08-02

### Added
- Full paper-to-module traceability for the four IEEE EADS papers.
- Phase 1.5 PDF extraction *tooling* (`eads.paper_extraction`) using PyMuPDF. Tooling only: it has
  never been run against the four papers here, and no extracted corpus ships.
- End-to-end `DecisionPipeline` covering ingestion, modernization, reasoning, decision, governance, execution, and audit.
- Real LLM adapters for OpenAI, Anthropic, and Ollama with lazy imports.
- Solver adapters (SciPy, PuLP, OR-Tools) and forecaster adapters (Naive, sktime).
- Domain-agnostic synthetic data generators for supply chain, healthcare, finance, IT operations, and customer support.
- Reproducible `Benchmark` harness with versioned `results.json` output.
- Validation scripts for optional extras (`scripts/validate_extras.py`) and live LLM adapters (`scripts/validate_llms.py`).
- Comprehensive per-module README files, design docs, and GitHub Actions workflows for tests, lint, type-check, and documentation.
- 27 passing tests covering core, modules, evaluation, paper extraction, and conditional extras.
