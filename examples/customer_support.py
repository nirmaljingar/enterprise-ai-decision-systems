from eads.core.pipeline import DecisionPipeline
from eads.core.types import DecisionRequest
from eads.decision.decision import DecisionEngine
from eads.evaluation import Benchmark
from eads.governance import GovernanceLayer
from eads.synthetic_data import CustomerSupportGenerator


def main():
    gen = CustomerSupportGenerator(seed=42)
    engine = DecisionEngine()
    governance = GovernanceLayer()
    pipeline = DecisionPipeline(governance=governance, decision_engine=engine)

    scenarios = [
        {
            "id": "cs-1",
            "request": DecisionRequest(
                request_id="cs-1",
                goal="prioritize VIP escalation",
                signals=gen.generate(3),
                policy_snapshot={"vip_priority": True, "refund_limit_usd": 1000},
            ),
        },
        {
            "id": "cs-2",
            "request": DecisionRequest(
                request_id="cs-2",
                goal="process standard refund",
                signals=gen.generate(3),
                policy_snapshot={"vip_priority": False, "refund_limit_usd": 500},
            ),
        },
    ]
    benchmark = Benchmark(
        pipeline,
        scenarios,
        output_dir="benchmarks/results/customer_support",
        metadata={"example": "customer_support", "version": "1.0.0"},
    )
    report = benchmark.run()
    print("Benchmark report:", report)
    print("Saved to benchmarks/results/customer_support/results.json")


if __name__ == "__main__":
    main()
