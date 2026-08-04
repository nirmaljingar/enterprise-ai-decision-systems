from eads.core.pipeline import DecisionPipeline
from eads.core.types import DecisionRequest
from eads.decision.decision import DecisionEngine
from eads.governance import GovernanceLayer
from eads.synthetic_data import SupplyChainGenerator


def main():
    gen = SupplyChainGenerator(seed=42)
    signals = gen.generate(3)
    request = DecisionRequest(
        request_id="demo-1",
        goal="decide replenishment order for SKU-1001",
        signals=signals,
        policy_snapshot={"region": "US"},
    )
    engine = DecisionEngine()
    governance = GovernanceLayer()
    pipeline = DecisionPipeline(
        llm=engine.llm,
        governance=governance,
        decision_engine=engine,
    )
    record = pipeline.run(request)
    print("Request:", record.request_id)
    print("Approved:", record.verdict.approved)
    print("Reason:", record.verdict.reason)
    print("Trust score:", record.verdict.trust_score)
    print("Execution:", record.execution.status)
    print("Trace:", record.trace)


if __name__ == "__main__":
    main()
