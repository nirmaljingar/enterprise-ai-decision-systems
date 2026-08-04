from eads.core.clock import FixedClock
from eads.core.pipeline import DecisionPipeline
from eads.core.types import Actor, DecisionCandidate, DecisionRequest, ProposedAction, Signal
from eads.governance import GovernanceLayer


def _order(quantity: int) -> DecisionCandidate:
    return DecisionCandidate(
        plan_id="plan-1",
        actions=[
            ProposedAction(
                type="order",
                raw_value=f"order_quantity={quantity}",
                quantity=quantity,
                region="EU",
                parsed=True,
            )
        ],
        confidence=0.9,
    )


def _request(actor: Actor) -> DecisionRequest:
    return DecisionRequest(
        request_id="req-1",
        goal="order replacement stock",
        signals=[Signal(id="sig-1", source="email", content="supplier delay", timestamp="t0")],
        policy_snapshot={"unit_price": 10.0, "allowed_regions": ["EU", "US"]},
        actor=actor,
    )


def test_escalation_names_the_requester_and_the_approving_role() -> None:
    verdict = GovernanceLayer().review(
        _order(600), {"unit_price": 10.0}, Actor(id="planner-7", roles=("planner",))
    )
    assert verdict.outcome == "escalated"
    requirement = verdict.required_approvals[0]
    assert requirement.approver_role == "manager"
    assert requirement.threshold == 500.0
    assert requirement.value == 6000.0
    assert "planner-7" in requirement.reason


def test_holding_the_approver_role_does_not_self_approve() -> None:
    """Separation of duties: the requester cannot satisfy its own requirement."""
    manager = Actor(id="manager-1", roles=("manager",))
    verdict = GovernanceLayer().review(_order(600), {"unit_price": 10.0}, manager)
    assert verdict.outcome == "escalated"
    assert not verdict.approved
    assert [a.approver_role for a in verdict.required_approvals] == ["manager"]


def test_audit_record_attributes_the_request_and_the_awaiting_role() -> None:
    actor = Actor(id="planner-7", roles=("planner",))
    record = DecisionPipeline(clock=FixedClock()).run(_request(actor))
    assert record.actor == actor
    verdict_step = next(step for step in record.trace if step["step"] == "verdict")
    assert verdict_step["actor"] == "planner-7"
    if record.verdict is not None and record.verdict.outcome == "escalated":
        assert record.execution is not None
        assert record.execution.output["requested_by"] == "planner-7"
        assert record.execution.output["awaiting_roles"] == verdict_step["awaiting_roles"]


def test_an_unattributed_request_is_still_recorded_explicitly() -> None:
    record = DecisionPipeline(clock=FixedClock()).run(
        DecisionRequest(request_id="req-2", goal="order stock", signals=[])
    )
    assert record.actor is not None
    assert record.actor.id == "unattributed"
