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
4. **Governed** it — escalated to a `manager`, because the order value exceeds the approval threshold. The decision is withheld, not executed.
5. **Audited** the full trace end-to-end.

## Quickstart output

```text
Request: demo-1
Approved: False
Reason: manager: value 1810.00 exceeds the 500.00 approval threshold; requested by planner-7
Trust score: 0.9
Execution: escalated
Policy snapshot: pol_ffdf694df3a25ed2
Trace: [{'step': 'ingest', 'signals': 3, 'evidence': 3, 'evidence_ids': ['ev_synthetic_supply_chain_0', 'ev_synthetic_supply_chain_1', 'ev_synthetic_supply_chain_2']}, {'step': 'reason', 'plan_id': 'plan_1', 'evidence_refs': ['ev_synthetic_supply_chain_0', 'ev_synthetic_supply_chain_1', 'ev_synthetic_supply_chain_2']}, {'step': 'generate', 'actions': [{'type': 'order', 'raw_value': 'order_quantity=181', 'quantity': 181, 'region': 'US', 'label': None, 'parsed': True}], 'evidence_refs': ['ev_synthetic_supply_chain_0', 'ev_synthetic_supply_chain_1', 'ev_synthetic_supply_chain_2'], 'seed_honored': True}, {'step': 'verdict', 'outcome': 'escalated', 'approved': False, 'reason': 'manager: value 1810.00 exceeds the 500.00 approval threshold; requested by planner-7', 'policy_snapshot_id': 'pol_ffdf694df3a25ed2', 'actor': 'planner-7', 'awaiting_roles': ['manager']}, {'step': 'execute', 'status': 'escalated'}]
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
