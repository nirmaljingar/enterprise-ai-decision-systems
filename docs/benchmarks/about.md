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

## Reporting a number against this baseline

If you compare your system against these numbers, three things make the comparison checkable, and a
comparison that is not checkable is not worth publishing:

1. **The manifest and its digest**, both printed on the [results page](index.md). A manifest can be
   edited; the digest says which version you ran.
2. **The code version.** Each benchmark records the EADS and Python version it was produced by. State
   yours, since a metric's definition can change between releases.
3. **The label.** Every manifest here is an *Illustrative example*, so a comparison against it is a
   comparison of implementations against a deterministic backend -- not a claim about model
   behaviour.

A citable form:

```
Compared against the EADS reference implementation (v2.0.0, manifest
supply_chain_prompt_injection.json, digest <digest>, label "Illustrative example"),
which reports injection_resistance = 1.00 against an obedient attack simulator.
```

The `injection_resistance` number deserves that last clause every time it is quoted. It is measured
against `InjectionProneLLM`, a backend that *always* obeys an injected instruction, so it bounds what
the governance layer blocks when the model is maximally compromised. It says nothing about how often a
real model complies -- and quoting it as a model's resistance would be a misreading this repository
does not want to enable.

## Contributing a scenario

The interesting contribution is an attack the governance layer *fails* to block.

1. Copy `benchmarks/manifest_template.json` into `benchmarks/manifests/<name>.json`.
2. Set `expected_outcome` per scenario. A scenario that observes rather than asserts cannot fail, so
   it adds nothing.
3. For an attack, set `adversarial: true`, add `injected_signals`, and use the `injection_prone`
   backend -- an injection benchmark against a backend that ignores its prompt measures nothing.
4. Run `python scripts/run_benchmarks.py`, then commit the manifest and the regenerated page.
5. If your scenario is blocked, the table gains a row. If it is *not* blocked, open the PR anyway with
   the failing expectation: that is a finding, and it is worth more than a passing row.

`python -c "from eads.evaluation.runner import Manifest; Manifest.load('path')"` validates a manifest
without running it. Unknown fields are refused rather than ignored, so a typo fails loudly instead of
producing a number for a manifest that was misread.
