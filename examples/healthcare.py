from eads.core.pipeline import DecisionPipeline
from eads.core.types import DecisionRequest
from eads.decision.decision import DecisionEngine
from eads.evaluation import Benchmark
from eads.governance import GovernanceLayer
from eads.synthetic_data import HealthcareGenerator


def main():
    gen = HealthcareGenerator(seed=42)
    engine = DecisionEngine()
    governance = GovernanceLayer()
    pipeline = DecisionPipeline(governance=governance, decision_engine=engine)

    scenarios = [
        {
            "id": "hc-1",
            "request": DecisionRequest(
                request_id="hc-1",
                goal="triage patient in Region North",
                signals=gen.generate(3),
                policy_snapshot={"max_icu_occupancy": 0.95, "urgency_threshold": 0.8},
            ),
        },
        {
            "id": "hc-2",
            "request": DecisionRequest(
                request_id="hc-2",
                goal="defer routine cardiology appointment",
                signals=gen.generate(3),
                policy_snapshot={"max_icu_occupancy": 0.90, "urgency_threshold": 0.9},
            ),
        },
    ]
    benchmark = Benchmark(
        pipeline,
        scenarios,
        output_dir="benchmarks/results/healthcare",
        metadata={"example": "healthcare", "version": "1.0.0"},
    )
    report = benchmark.run()
    print("Benchmark report:", report)
    print("Saved to benchmarks/results/healthcare/results.json")


if __name__ == "__main__":
    main()
