from eads.core.pipeline import DecisionPipeline
from eads.core.types import DecisionCandidate, DecisionRequest
from eads.decision.decision import DecisionEngine
from eads.governance import GovernanceLayer
from eads.synthetic_data import SupplyChainGenerator


def test_governance_blocks_excessive_order():
    g = GovernanceLayer()
    candidate = DecisionCandidate(
        plan_id="t",
        actions=[{"type": "order", "value": "order_quantity=1500"}],
        expected_outcome={},
        confidence=0.5,
    )
    verdict = g.review(candidate, {"unit_price": 10.0})
    assert not verdict.approved
    assert "quantity_hard_limit" in verdict.violated_policies


def test_end_to_end_pipeline():
    gen = SupplyChainGenerator(seed=1)
    signals = gen.generate(2)
    request = DecisionRequest(
        request_id="e2e-1",
        goal="replenish SKU-1001",
        signals=signals,
    )
    engine = DecisionEngine()
    governance = GovernanceLayer()
    pipeline = DecisionPipeline(governance=governance, decision_engine=engine)
    record = pipeline.run(request)
    assert record.request_id == "e2e-1"
    assert record.verdict is not None
    assert record.execution is not None
    assert record.trace[0]["step"] == "ingest"


def test_decision_consistency():
    gen = SupplyChainGenerator(seed=2)
    engine = DecisionEngine()
    governance = GovernanceLayer()
    pipeline = DecisionPipeline(governance=governance, decision_engine=engine)
    records = []
    for _ in range(5):
        request = DecisionRequest(
            request_id="c-1",
            goal="replenish SKU-1001",
            signals=gen.generate(3),
        )
        records.append(pipeline.run(request))
    statuses = {r.execution.status for r in records}
    assert len(statuses) == 1
