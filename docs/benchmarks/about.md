# Benchmarks

Benchmark manifests, the runner that executes them, and the results they emit.

- **[Published results](index.md)** — the current numbers, regenerated from the manifests.
- `benchmarks/manifests/*.json` — one manifest per benchmark: scenarios, policy snapshots, expected
  outcomes, injected signals, seed, and backend.
- `benchmarks/results/<domain>/<benchmark_id>/results.json` — emitted results, recording the seed,
  backend, Python version, and a digest of the manifest that produced them.

Each manifest declares a label, and `Manifest.load` rejects any other value:

| Label | Meaning |
|---|---|
| `Published methodology` | Follows an evaluation protocol described in one of the four papers. |
| `Illustrative example` | Demonstrates how a metric is computed. Not evidence about a real model. |

Every manifest currently in the repository is an *Illustrative example*.

## Running them

```bash
pip install -e ".[dev]"
python scripts/run_benchmarks.py          # rerun everything and regenerate the results page
python scripts/run_benchmarks.py --check  # fail if the published page is stale
pytest tests/test_runner.py               # assert every manifest reaches its declared outcome
```

`benchmarks/results/` is gitignored. The generated results page is the committed artifact, so a
reader compares numbers without running anything while the repository does not accumulate a diff of
regenerated JSON on every run; the seed, backend, and manifest digest recorded on the page are what
make a number reproducible.

The results page is generated, never hand-edited: a table typed by hand is a claim, a generated one
is a result. `tests/test_runner.py` also asserts that two runs of a manifest are byte-identical, so
the published numbers are reproducible rather than merely recorded.

## Adding one

1. Add `benchmarks/manifests/<name>.json` with an `id`, `domain`, `label`, `traces_to`, `seed`, and
   `scenarios`. Give every scenario an `expected_outcome`, so it asserts rather than observes.
2. To make it adversarial, set `adversarial: true`, add `injected_signals`, and use the
   `injection_prone` backend — an injection benchmark against a backend that ignores its prompt
   measures nothing.
3. Run `python scripts/run_benchmarks.py` and commit the manifest, the emitted results, and the
   regenerated page.
