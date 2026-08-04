# EADS in 60 Seconds — Live Demo

Turn unstructured enterprise signals into an **auditable, explainable decision** in one command.

## Run the live demo

```bash
pip install git+https://github.com/nirmaljingar/enterprise-ai-decision-systems.git
python examples/wow_demo.py
```

## What just happened?

1. **Ingested** 3 synthetic supply-chain signals.
2. **Reasoned** over them to build a replenishment plan.
3. **Generated** a decision (`order_quantity=181`).
4. **Governed** it — blocked because *manager approval* is required.
5. **Audited** the full trace end-to-end.

## Quickstart output

```text
Request: demo-1
Approved: False
Reason: manager_approval_required
Trust score: 0.9
Execution: blocked
Trace: [{'step': 'ingest', 'signals': 3, 'evidence': 3}, {'step': 'reason', 'plan_id': 'plan_1', 'evidence_refs': ['ev_0', 'ev_1', 'ev_2']}, {'step': 'generate', 'actions': [{'type': 'decision', 'value': 'order_quantity=181'}], 'evidence_refs': ['ev_0', 'ev_1', 'ev_2']}, {'step': 'verdict', 'approved': False, 'reason': 'manager_approval_required'}, {'step': 'execute', 'status': 'blocked'}]
```

## Benchmark output

The wow demo also runs a full reproducible supply-chain benchmark:

```text
Benchmark report: {'metadata': {'timestamp': '2026-08-02T20:53:12.043225', 'scenarios': 2, 'example': 'supply_chain', 'version': '1.0.0'}, 'policy_compliance': 1.0, 'decision_consistency': 1.0, 'results': [{'scenario_id': 'sc-1', 'approved': True, 'execution_status': 'success', 'reason': 'passed'}, {'scenario_id': 'sc-2', 'approved': True, 'execution_status': 'success', 'reason': 'passed'}]}
Saved to benchmarks/results/supply_chain/results.json
```

## Try it yourself

- **Notebook:** `notebooks/eads_killer_demo.ipynb` — an end-to-end Colab-ready walkthrough with a single decision + full benchmark.
- **Colab:** [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nirmaljingar/enterprise-ai-decision-systems/blob/main/notebooks/eads_killer_demo.ipynb)
- **Getting started:** [`docs/getting_started.md`](./getting_started.md)
- **Examples:** `examples/healthcare.py`, `examples/finance.py`, `examples/it_operations.py`, `examples/customer_support.py`
