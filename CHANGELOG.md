# Changelog

All notable changes to the EADS Research Companion are documented in this file.

## [1.0.0] - 2026-08-02

### Added
- Full paper-to-module traceability for the four IEEE EADS papers.
- Phase 1.5 PDF extraction pipeline (`eads.paper_extraction`) using PyMuPDF.
- End-to-end `DecisionPipeline` covering ingestion, modernization, reasoning, decision, governance, execution, and audit.
- Real LLM adapters for OpenAI, Anthropic, and Ollama with lazy imports.
- Solver adapters (SciPy, PuLP, OR-Tools) and forecaster adapters (Naive, sktime).
- Domain-agnostic synthetic data generators for supply chain, healthcare, finance, IT operations, and customer support.
- Reproducible `Benchmark` harness with versioned `results.json` output.
- Validation scripts for optional extras (`scripts/validate_extras.py`) and live LLM adapters (`scripts/validate_llms.py`).
- Comprehensive per-module README files, design docs, and GitHub Actions workflows for tests, lint, type-check, and documentation.
- 27 passing tests covering core, modules, evaluation, paper extraction, and conditional extras.
