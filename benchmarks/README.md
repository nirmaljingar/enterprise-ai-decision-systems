# Benchmarks

- `manifests/*.json` — the benchmark declarations: scenarios, policy snapshots, expected outcomes,
  injected signals, seed, and backend. Each declares a `label` (`Published methodology` or
  `Illustrative example`) and a `traces_to` naming the paper concept it exercises.
- `results/<domain>/<benchmark_id>/results.json` — emitted results, recording the seed, the backend,
  the Python version, and a digest of the manifest that produced them.

Run them and regenerate the published table:

```bash
python scripts/run_benchmarks.py
```

The numbers are published in [`docs/benchmarks/index.md`](../docs/benchmarks/index.md), which is
generated from these manifests and checked for staleness by `tests/test_runner.py`. Runs are seeded
and use a fixed clock, so rerunning a manifest produces a byte-identical result file.

The manifest format is versioned (`schema_version`), unknown fields are refused rather than ignored,
and `manifest_template.json` is a valid starting point checked by the test suite. See
[how to report a number against this baseline](../docs/benchmarks/about.md#reporting-a-number-against-this-baseline).

Every manifest here is an *Illustrative example*: it demonstrates how a metric is computed against
synthetic data and a deterministic backend, and is not evidence about any real model's behaviour.
