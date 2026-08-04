# Contributing to EADS

Thank you for helping make the EADS research companion more useful. This repository is an open research artifact, so contributions should preserve its vendor-neutral, reproducible, and citable character.

## Before you start

- Read `docs/research_design.md` and `docs/roadmap.md` to understand the current phase.
- Every module, metric, or example must cite the originating IEEE paper(s) or be labeled as a *Suggested extension*.
- Do not include proprietary code, datasets, schemas, API keys, prompts, or benchmark artifacts.
- All examples must use synthetic data and deterministic seeds.

## Adding a module

1. Create `eads/<module>/` with a `README.md` explaining research traceability and usage.
2. Add `tests/<module>/` with unit tests covering deterministic behavior and paper-aligned claims.
3. Add or update `docs/module_mapping.md` with the paper trace.
4. Open a PR; ensure `pytest`, `ruff check`, and `mypy` pass in CI.

## Adding a domain example

1. Add `examples/<domain>_<scenario>.py` with a header identifying the paper(s) and scenario.
2. Include the problem statement, architecture, execution flow, expected output, and the exact command to reproduce it.
3. Use only `SyntheticDataGenerator` output or other generated data.
4. Add a test under `tests/examples/` that runs the example without external API keys.

## Adding a benchmark

1. Add `benchmarks/synthetic_<domain>_<scenario>.yaml` with inputs, expected outputs, and seed.
2. Label the manifest as `Published methodology` or `Illustrative example` and cite the paper concept.
3. Add the corresponding runner support in `eads/evaluation/runner.py` if a new metric is involved.
4. Commit the generated `docs/benchmarks/archive/<release>.json` after a reproducibility audit.

## Code style

- `ruff` enforces formatting and import order.
- `mypy --strict` is required; prefer `typing` annotations.
- Keep the core free of vendor-specific SDKs; put optional adapters in `eads/core/adapters.py`.
