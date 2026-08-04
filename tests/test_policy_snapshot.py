from eads.core.clock import FixedClock
from eads.core.pipeline import DecisionPipeline
from eads.core.types import DecisionRequest, Signal
from eads.governance import policy_snapshot_id


def _request(policy: dict[str, object]) -> DecisionRequest:
    return DecisionRequest(
        request_id="req-1",
        goal="order replacement stock",
        signals=[Signal(id="sig-1", source="email", content="supplier delay", timestamp="t0")],
        policy_snapshot=policy,
    )


def test_id_ignores_key_order_but_not_values() -> None:
    assert policy_snapshot_id({"max_quantity": 10, "region": "eu"}) == policy_snapshot_id(
        {"region": "eu", "max_quantity": 10}
    )
    assert policy_snapshot_id({"max_quantity": 10}) != policy_snapshot_id({"max_quantity": 11})


def test_audit_record_identifies_the_policy_it_was_judged_under() -> None:
    policy = {"max_quantity": 10, "allowed_regions": ["eu"]}
    pipeline = DecisionPipeline(clock=FixedClock())
    record = pipeline.run(_request(policy))
    assert record.policy_snapshot_id == policy_snapshot_id(policy)
    verdict_step = next(step for step in record.trace if step["step"] == "verdict")
    assert verdict_step["policy_snapshot_id"] == record.policy_snapshot_id


def test_a_changed_limit_changes_the_recorded_snapshot_id() -> None:
    pipeline = DecisionPipeline(clock=FixedClock())
    lenient = pipeline.run(_request({"max_quantity": 10_000}))
    strict = pipeline.run(_request({"max_quantity": 1}))
    assert lenient.policy_snapshot_id != strict.policy_snapshot_id
