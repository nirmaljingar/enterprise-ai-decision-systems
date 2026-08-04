# EADS Reproducibility Suite

This directory contains scripts and manifests for reproducing the repository's outputs.

## Quick reproduction

From the repository root:

```bash
# 1. Install the core package and optional extras
pip install -e ".[dev,solvers,forecasters,pdf]"

# 2. Run the full test suite
python3 -m tests.run_tests

# 3. Run the end-to-end examples
PYTHONPATH=. python3 examples/quickstart.py
PYTHONPATH=. python3 examples/supply_chain.py

# 4. Validate optional extras and live LLM adapters
PYTHONPATH=. python3 scripts/validate_extras.py
PYTHONPATH=. python3 scripts/validate_llms.py

# 5. Re-extract the four source papers (optional)
PYTHONPATH=. python3 scripts/extract_papers.py --input-dir data/papers --output-dir data/papers/extracted
```

## Automated runner

`run_all.py` executes the test suite, examples, and validation scripts and writes a combined summary to `reproducibility/results.json`:

```bash
python3 reproducibility/run_all.py
```

## Notes

- All examples use synthetic data and deterministic seeds; no API keys are required for the base test suite.
- Live-LLM and solver/forecaster validation are skipped unless the corresponding extras are installed and environment variables are set.
- The paper-extraction step is for local research use and requires your own licensed PDFs in `data/papers/`. The public repository ships only `data/papers/papers.json` (bibliographic metadata).
