from eads import __version__
from eads.core.pipeline import DecisionPipeline
from eads.core.types import DecisionRequest
from eads.decision.decision import DecisionEngine
from eads.evaluation import Benchmark
from eads.governance import GovernanceLayer
from eads.synthetic_data import ITOperationsGenerator


def main():
    gen = ITOperationsGenerator(seed=42)
    engine = DecisionEngine()
    governance = GovernanceLayer()
    pipeline = DecisionPipeline(governance=governance, decision_engine=engine)

    scenarios = [
        {
            "id": "it-1",
            "request": DecisionRequest(
                request_id="it-1",
                goal="escalate database failover incident",
                signals=gen.generate(3),
                policy_snapshot={"max_latency_ms": 2000, "p1_requires_oncall": True},
            ),
        },
        {
            "id": "it-2",
            "request": DecisionRequest(
                request_id="it-2",
                goal="renew expiring certificate",
                signals=gen.generate(3),
                policy_snapshot={"max_latency_ms": 3000, "p1_requires_oncall": False},
            ),
        },
    ]
    benchmark = Benchmark(
        pipeline,
        scenarios,
        output_dir="benchmarks/results/it_operations",
        metadata={"example": "it_operations", "version": __version__},
    )
    report = benchmark.run()
    print("Benchmark report:", report)
    print("Saved to benchmarks/results/it_operations/results.json")


if __name__ == "__main__":
    main()
