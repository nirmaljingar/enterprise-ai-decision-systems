# Examples

Documentation for the runnable examples in the top-level `examples/` directory.

- `examples/quickstart.py` — single end-to-end decision cycle with synthetic data.
- `examples/injection_demo.py` — a prompt-injected supplier email against a model that obeys it, and
  what a first-match parser would have approved. The output is checked against a live run by
  `tests/test_docs.py`.
- `examples/wow_demo.py` — the same scenario as a narrated walkthrough.
- `examples/supply_chain.py` — small benchmark scenario over two replenishment cases.
- `examples/healthcare.py`, `examples/finance.py`, `examples/it_operations.py`,
  `examples/customer_support.py` — the same harness over each domain generator, writing
  `benchmarks/results/<domain>/results.json`.

Every script here runs without credentials or network access, and `tests/test_examples.py` executes
all of them on each commit.
