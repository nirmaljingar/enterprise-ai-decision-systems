from eads.core.pipeline import DecisionPipeline
from eads.core.types import DecisionRequest
from eads.decision.decision import DecisionEngine
from eads.evaluation import Benchmark
from eads.governance import GovernanceLayer
from eads.synthetic_data import SupplyChainGenerator


def test_benchmark():
    gen = SupplyChainGenerator(seed=3)
    engine = DecisionEngine()
    governance = GovernanceLayer()
    pipeline = DecisionPipeline(governance=governance, decision_engine=engine)
    scenarios = [
        {
            "id": "b-1",
            "request": DecisionRequest(
                request_id="b-1",
                goal="replenish SKU-1001",
                signals=gen.generate(3),
                policy_snapshot={"max_order_quantity": 1000, "unit_price": 10.0},
            ),
        }
    ]
    report = Benchmark(pipeline, scenarios).run()
    assert 0.0 <= report["policy_compliance"] <= 1.0
    assert "results" in report
