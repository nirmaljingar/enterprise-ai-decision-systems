# Enterprise AI Decision Systems — Research Companion

This site documents the open research implementation accompanying the IEEE EADS papers.

It is alpha research software. Every paper-traced module implements a method rather than a
placeholder, and every one of them is lexical and rule-based rather than model-backed — a deliberate
trade for determinism, so a published benchmark number is reproducible. What each implementation
cannot do is stated per module in [Limitations](limitations.md).

- [Getting Started](getting_started.md) — install and first run.
- [Research Design](research_design.md) — project plan and architecture.
- [Evaluation](evaluation.md) — the metrics that exist and the ones that do not.
- [Tutorials](tutorials/README.md), [Examples](examples/README.md),
  [Benchmarks](benchmarks/index.md).

Run the quickstart:

```bash
pip install -e ".[dev]"
python examples/quickstart.py
pytest
```
