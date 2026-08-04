# Enterprise AI Decision Systems — Research Companion

This site documents the open research implementation accompanying the IEEE EADS papers.

It is alpha research software: the pipeline, governance layer, and benchmark harness are
implemented, while several paper-traced modules are documented stubs. See
[Limitations](limitations.md).

- [Getting Started](getting_started.md) — install and first run.
- [Research Design](research_design.md) — project plan and architecture.
- [Evaluation](evaluation.md) — the metrics that exist and the ones that do not.
- [Tutorials](tutorials/README.md), [Examples](examples/README.md),
  [Benchmarks](benchmarks/README.md).

Run the quickstart:

```bash
pip install -e ".[dev]"
python examples/quickstart.py
pytest
```
