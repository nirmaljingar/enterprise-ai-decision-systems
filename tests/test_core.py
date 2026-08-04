from eads.core.pipeline import DecisionPipeline
from eads.core.types import DecisionCandidate, DecisionRequest, ProposedAction
from eads.decision.decision import DecisionEngine
from eads.governance import GovernanceLayer
from eads.governance.safety import UNPARSEABLE_ACTION, SafetyFilter
from eads.governance.trust import TrustScorer
from eads.synthetic_data import SupplyChainGenerator


def _order(quantity: int, region: str | None = "US") -> DecisionCandidate:
    return DecisionCandidate(
        plan_id="t",
        actions=[
            ProposedAction(
                type="order",
                raw_value=f"order_quantity={quantity}",
                quantity=quantity,
                region=region,
                parsed=True,
            )
        ],
        expected_outcome={},
        confidence=0.5,
    )


def test_governance_blocks_excessive_order():
    verdict = GovernanceLayer().review(_order(1500), {"unit_price": 10.0})
    assert not verdict.approved
    assert "quantity_hard_limit" in verdict.violated_policies


def test_governance_rejects_unparseable_action():
    candidate = DecisionCandidate(
        plan_id="t",
        actions=[ProposedAction(type="unknown", raw_value="ship 999999 units to RU")],
        confidence=1.0,
    )
    verdict = GovernanceLayer().review(candidate, {"max_order_quantity": 10})
    assert not verdict.approved
    assert UNPARSEABLE_ACTION in verdict.violated_policies


def test_governance_rejects_action_without_region():
    verdict = GovernanceLayer().review(_order(10, region=None), {"unit_price": 1.0})
    assert not verdict.approved
    assert "region_unspecified" in verdict.violated_policies


def test_governance_enforces_allowed_regions():
    verdict = GovernanceLayer().review(_order(10, region="RU"), {"unit_price": 1.0})
    assert not verdict.approved
    assert "region_not_allowed" in verdict.violated_policies


def test_governance_rejects_empty_candidate():
    verdict = GovernanceLayer().review(DecisionCandidate(plan_id="t", actions=[]))
    assert not verdict.approved
    assert "no_action_proposed" in verdict.violated_policies


def test_end_to_end_pipeline():
    gen = SupplyChainGenerator(seed=1)
    signals = gen.generate(2)
    request = DecisionRequest(
        request_id="e2e-1",
        goal="replenish SKU-1001",
        signals=signals,
        policy_snapshot={"region": "US"},
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
            policy_snapshot={"region": "US"},
        )
        records.append(pipeline.run(request))
    statuses = {r.execution.status for r in records}
    assert len(statuses) == 1


def test_high_value_order_is_escalated_not_rejected():
    verdict = GovernanceLayer().review(_order(600), {"unit_price": 10.0})
    assert verdict.outcome == "escalated"
    assert not verdict.approved
    assert verdict.violated_policies == []
    assert [a.approver_role for a in verdict.required_approvals] == ["manager"]
    assert verdict.required_approvals[0].value == 6000.0


def test_violation_outranks_pending_approval():
    verdict = GovernanceLayer().review(_order(1500), {"unit_price": 10.0})
    assert verdict.outcome == "rejected"


def test_clean_order_is_approved():
    verdict = GovernanceLayer().review(_order(10), {"unit_price": 1.0})
    assert verdict.outcome == "approved"
    assert verdict.approved


def test_pipeline_audits_every_decision():
    governance = GovernanceLayer()
    pipeline = DecisionPipeline(governance=governance)
    request = DecisionRequest(
        request_id="audit-1",
        goal="replenish SKU-1001",
        signals=SupplyChainGenerator(seed=4).generate(2),
        policy_snapshot={"region": "US"},
    )
    pipeline.run(request)
    pipeline.run(request)
    assert len(governance.audit.records) == 2
    assert governance.audit.records[0]["request_id"] == "audit-1"


def test_blocked_decision_uses_fallback_handler():
    governance = GovernanceLayer(safety_filter=SafetyFilter(hard_limits={"max_order_quantity": 1}))
    pipeline = DecisionPipeline(governance=governance)
    record = pipeline.run(
        DecisionRequest(
            request_id="fb-1",
            goal="place order for SKU-1001",
            signals=SupplyChainGenerator(seed=4).generate(2),
            policy_snapshot={"region": "US"},
        )
    )
    assert record.execution.status == "blocked"
    assert record.execution.output["safe_action"] == "discard_and_notify"


def test_escalated_decision_is_not_reported_as_blocked():
    pipeline = DecisionPipeline()
    record = pipeline.run(
        DecisionRequest(
            request_id="esc-1",
            goal="place order for SKU-1001",
            signals=SupplyChainGenerator(seed=4).generate(2),
            policy_snapshot={"region": "US", "unit_price": 10.0},
        )
    )
    assert record.verdict.outcome == "escalated"
    assert record.execution.status == "escalated"
    assert record.execution.output["safe_action"] == "request_human_review"


def test_trust_score_is_capped_when_there_is_no_evidence_to_check_against():
    """With nothing to verify, a high self-declared confidence buys nothing."""
    unparsed = DecisionCandidate(
        plan_id="t",
        actions=[ProposedAction(type="unknown", raw_value="ship it", parsed=False)],
        expected_outcome={},
        confidence=1.0,
    )
    assert TrustScorer().score(unparsed) == 0.5
    assert TrustScorer().score(_order(10)) == 0.5
    assert "no_evidence_supplied" in TrustScorer().assess(_order(10)).reasons
