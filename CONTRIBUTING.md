# Contributing to EADS

Thank you for helping make the EADS research companion more useful. This repository is an open research artifact, so contributions should preserve its vendor-neutral, reproducible, and citable character.

## Local setup

```bash
pip install -e ".[dev]"
pre-commit install     # ruff and mypy run on every commit
ruff check eads tests examples
mypy eads
pytest
```

## Before you start

- Read `docs/research_design.md` and `docs/roadmap.md` to understand the current phase.
- Every module, metric, or example must cite the originating IEEE paper(s) or be labeled as a *Suggested extension*.
- Do not include proprietary code, datasets, schemas, API keys, prompts, or benchmark artifacts.
- All examples must use synthetic data and deterministic seeds.

## Adding a module

1. Create `eads/<module>/` with a `README.md` explaining research traceability and usage.
2. Add tests under `tests/` covering deterministic behavior and paper-aligned claims.
3. Add or update `docs/module_mapping.md` with the paper trace.
4. If the module is not a full implementation of the paper's method, say so in its docstring and
   list it in `docs/limitations.md`. Documenting a stub as an implementation is the one defect this
   repository has repeatedly shipped.
5. Open a PR; ensure `pytest`, `ruff check`, `mypy`, and `mkdocs build --strict` pass in CI.

## Adding a domain example

1. Add `examples/<domain>_<scenario>.py` with a header identifying the paper(s) and scenario.
2. Include the problem statement, architecture, execution flow, expected output, and the exact command to reproduce it.
3. Use only `SyntheticDataGenerator` output or other generated data.
4. Add a test under `tests/examples/` that runs the example without external API keys.

## Adding a benchmark

1. Add `benchmarks/synthetic_<domain>_<scenario>.yaml` with inputs, expected outputs, and seed.
2. Label the manifest as `Published methodology` or `Illustrative example` and cite the paper concept.
3. Give each scenario an `expected_outcome` (`approved`, `rejected`, or `escalated`) so the
   correctness metrics have ground truth to compare against.
4. Add any new metric to `eads/evaluation/metrics.py` with a test that shows it can fail, and update
   the tables in `README.md` and `docs/evaluation.md`.

## Code style

- `ruff` enforces lint rules and import order.
- `mypy --strict` is required; prefer `typing` annotations.
- Keep the core free of vendor-specific SDKs; put optional adapters in `eads/core/adapters.py`.
- Governance must fail closed. Model output is parsed once, at the boundary, into a
  `ProposedAction`; checks read its typed fields. An action that cannot be parsed, or that omits a
  field a limit applies to, is a violation — never a pass.
- Tests for optional dependencies use `pytest.mark.skipif`, never an early `return`: a test that
  silently does nothing reports as passing.
