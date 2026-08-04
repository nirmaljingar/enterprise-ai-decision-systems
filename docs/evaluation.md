# Evaluation

This page defines the metrics, benchmark harness, and measurement methodology for the EADS research companion.

## Metrics

Every metric below is a function in `eads.evaluation.metrics` taking the run summaries emitted by
`Benchmark`. Scenarios may carry an `expected_outcome` label (`approved`, `rejected`, or
`escalated`); metrics that need ground truth use only labelled runs.

| Metric | Definition | Measurement methodology | Paper link | Implemented |
|--------|------------|------------------------|------------|-------------|
| `approval_rate` | Fraction of runs approved for execution | Count approved verdicts | — | Yes. Throughput only — a pipeline that approves everything scores 1.0 |
| `policy_compliance` | Fraction of labelled runs whose outcome matched the expected outcome | Compare verdict outcome against the scenario label | Papers 3, 4 | Yes. Correctly blocking an unsafe decision *raises* this score |
| `decision_consistency` | Agreement of outcome across repeated runs of one scenario | Run each scenario `repeats` times with fixed seed and clock; compare | Paper 3 | Yes. Raises `ValueError` if handed more than one scenario |
| `evidence_grounding_rate` | Fraction of evidence references that resolve to evidence the run produced | Resolve `decision.evidence_refs` against ingested evidence ids | Paper 2 | Yes. A decision citing nothing scores 0.0 |
| `fallback_recovery_rate` | Fraction of runs expected to be withheld that were withheld | Label violating scenarios; check execution was blocked or escalated | Papers 3, 4 | Yes |
| `audit_completeness` | Fraction of runs whose audit record carries every required trace field | Field presence check over `AuditRecord` | Paper 4 | Yes |
| `injection_resistance` | Fraction of adversarial runs whose injected action did not execute | Run scenarios whose signals carry an injected instruction against a backend that obeys it | Paper 4 | Yes. Bounds the *governance layer* under a fully compromised model, not any real backend's resistance |
| Tool Invocation Precision | Correct tool selected divided by total tool invocations | Schema matching against the planned workflow | Paper 3 | No — suggested extension |
| Decision Latency | End-to-end time from input to executable decision | Instrument the pipeline | Paper 3 | No — suggested extension |
| Token Efficiency | Tokens consumed per unit of useful output | Count prompt and completion tokens | Papers 1–3 | No — token accounting is not implemented |

> No numerical results or experimental claims are fabricated. Metrics marked "No" are documented
> targets, not code.

## Running benchmarks

```bash
pip install -e ".[dev]"
pytest tests/test_evaluation.py
python examples/supply_chain.py
```

Benchmark manifests live in `benchmarks/manifests/` and each is labeled `Published methodology` or
`Illustrative example`; `Manifest.load` rejects any other label. Manifest runs are emitted to
`benchmarks/results/<domain>/<benchmark_id>/results.json`, and the current numbers are published in
[Benchmarks](benchmarks/index.md). The domain example scripts use the same harness directly and
write to `benchmarks/results/<domain>/results.json`; those runs are illustrative and are not
published.

```bash
python scripts/run_benchmarks.py
```
