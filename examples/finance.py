from eads.core.pipeline import DecisionPipeline
from eads.core.types import DecisionRequest
from eads.decision.decision import DecisionEngine
from eads.evaluation import Benchmark
from eads.governance import GovernanceLayer
from eads.synthetic_data import FinanceGenerator


def main():
    gen = FinanceGenerator(seed=42)
    engine = DecisionEngine()
    governance = GovernanceLayer()
    pipeline = DecisionPipeline(governance=governance, decision_engine=engine)

    scenarios = [
        {
            "id": "fin-1",
            "request": DecisionRequest(
                request_id="fin-1",
                goal="flag transaction for AML review",
                signals=gen.generate(3),
                policy_snapshot={"aml_threshold": 0.7, "max_exposure_tech": 0.2},
            ),
        },
        {
            "id": "fin-2",
            "request": DecisionRequest(
                request_id="fin-2",
                goal="rebalance portfolio",
                signals=gen.generate(3),
                policy_snapshot={"aml_threshold": 0.9, "max_exposure_tech": 0.15},
            ),
        },
    ]
    benchmark = Benchmark(
        pipeline,
        scenarios,
        output_dir="benchmarks/results/finance",
        metadata={"example": "finance", "version": "1.0.0"},
    )
    report = benchmark.run()
    print("Benchmark report:", report)
    print("Saved to benchmarks/results/finance/results.json")


if __name__ == "__main__":
    main()
