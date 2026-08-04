# Evaluation

This page defines the metrics, benchmark harness, and measurement methodology for the EADS research companion.

## Metrics

| Metric | Definition | Measurement methodology | Paper link | Status |
|--------|------------|------------------------|------------|--------|
| **Decision Consistency** | Variance of the same decision under repeated execution with fixed inputs | Re-run decision workflow `n` times on an identical synthetic scenario with a fixed seed | Paper 3 | Published methodology |
| **Policy Compliance** | Fraction of decisions passing the policy/safety filter | Automated rule evaluation on synthetic cases | Papers 3, 4 | Published methodology |
| **Evidence Grounding Rate** | Fraction of claims supported by extracted evidence with a retrievable source | Compare reasoning output to the evidence graph | Paper 2 | Published methodology |
| **Fallback Recovery Rate** | Fraction of unsafe or unauthorized decisions correctly caught and recovered | Inject known constraint violations and measure recovery | Papers 3, 4 | Published methodology |
| **Audit Completeness** | Fraction of decision events containing all required trace fields | Schema validation of audit records | Paper 4 | Published methodology |
| **Tool Invocation Precision** | Correct tool selected divided by total tool invocations | Manual or programmatic schema matching against the planned workflow | Paper 3 | Suggested extension |
| **Decision Latency** | End-to-end time from input to executable decision | Instrument the pipeline | Paper 3 | Suggested extension |
| **Token Efficiency** | Tokens consumed per unit of useful output | Count prompt and completion tokens | Papers 1–3 | Suggested extension |

> No numerical results or experimental claims are fabricated. Metrics are labeled either as `Published methodology` (derived from a paper concept) or `Suggested extension` (reference implementation demonstrating how the metric could be measured).

## Running benchmarks

```bash
pip install -e ".[dev]"
pytest tests/evaluation
python examples/supply_chain.py
```

Benchmark manifests live in `benchmarks/` and each is labeled `Published methodology` or `Illustrative example`. Results are emitted to `benchmarks/results/` and archived under `docs/benchmarks/archive/` for each release.
