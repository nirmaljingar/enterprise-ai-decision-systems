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
            "expected_outcome": "escalated",
            "request": DecisionRequest(
                request_id="sc-1",
                goal="place replenishment order for SKU-1001",
                signals=gen.generate(3),
                policy_snapshot={"max_order_quantity": 1000, "unit_price": 10.0, "region": "US"},
            ),
        },
        {
            "id": "sc-2",
            "expected_outcome": "rejected",
            "request": DecisionRequest(
                request_id="sc-2",
                goal="place emergency purchase order for SKU-1001",
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
    for metric in (
        "approval_rate",
        "policy_compliance",
        "decision_consistency",
        "evidence_grounding_rate",
        "fallback_recovery_rate",
        "audit_completeness",
    ):
        print(f"{metric}: {report[metric]:.2f}")
    for run in report["results"]:
        print(
            f"  {run['scenario_id']} run {run['run_index']}: "
            f"{run['outcome']} (expected {run['expected_outcome']}) — {run['reason']}"
        )
    print("Saved to benchmarks/results/supply_chain/results.json")


if __name__ == "__main__":
    main()
