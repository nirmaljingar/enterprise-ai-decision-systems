# Getting Started with EADS

This tutorial walks through the EADS Research Companion in five minutes.

## 1. Install

```bash
git clone https://github.com/nirmaljingar/enterprise-ai-decision-systems.git
cd enterprise-ai-decision-systems
pip install -e ".[dev]"
```

Optional extras let you plug in real LLMs, solvers, forecasters, and the PDF extractor:

```bash
pip install -e ".[openai,anthropic,solvers,forecasters,pdf]"
```

## 2. Run your first decision

```python
from eads.core.pipeline import DecisionPipeline
from eads.core.types import DecisionRequest
from eads.decision.decision import DecisionEngine
from eads.governance import GovernanceLayer
from eads.synthetic_data import SupplyChainGenerator

request = DecisionRequest(
    request_id="demo",
    goal="decide replenishment order for SKU-1001",
    signals=SupplyChainGenerator(seed=42).generate(3),
)

pipeline = DecisionPipeline(governance=GovernanceLayer(), decision_engine=DecisionEngine())
record = pipeline.run(request)

print("Approved:", record.verdict.approved)
print("Reason:", record.verdict.reason)
print("Trace:", [t["step"] for t in record.trace])
```

## 3. Run domain benchmarks

```bash
python examples/supply_chain.py
python examples/healthcare.py
python examples/finance.py
python examples/it_operations.py
python examples/customer_support.py
```

Each example uses synthetic data and writes results to `benchmarks/results/`.

## 4. Run tests

```bash
python3 -m pytest -q
```

## 5. Reproducibility

See `reproducibility/README.md` for the full reproduction suite and [Releasing](releasing.md)
for how a citable release and its DOI are produced.
