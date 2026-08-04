from eads.core.pipeline import DecisionPipeline
from eads.core.types import DecisionRequest
from eads.decision.decision import DecisionEngine
from eads.evaluation import Benchmark
from eads.governance import GovernanceLayer
from eads.synthetic_data import SupplyChainGenerator


def main():
    gen = SupplyChainGenerator(seed=42)
    engine = DecisionEngine()
    governance = GovernanceLayer()
    pipeline = DecisionPipeline(governance=governance, decision_engine=engine)

    scenarios = [
        {
            "id": "sc-1",
            "request": DecisionRequest(
                request_id="sc-1",
                goal="replenish SKU-1001",
                signals=gen.generate(3),
                policy_snapshot={"max_order_quantity": 1000, "unit_price": 10.0, "region": "US"},
            ),
        },
        {
            "id": "sc-2",
            "request": DecisionRequest(
                request_id="sc-2",
                goal="emergency purchase for SKU-1001",
                signals=gen.generate(3),
                policy_snapshot={"max_order_quantity": 50, "unit_price": 10.0, "region": "US"},
            ),
        },
    ]
    benchmark = Benchmark(
        pipeline,
        scenarios,
        output_dir="benchmarks/results/supply_chain",
        metadata={"example": "supply_chain", "version": "1.0.0"},
    )
    report = benchmark.run()
    print("Benchmark report:", report)
    print("Saved to benchmarks/results/supply_chain/results.json")


if __name__ == "__main__":
    main()
