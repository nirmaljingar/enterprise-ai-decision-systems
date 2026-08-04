from dataclasses import asdict

from eads.core.clock import FixedClock
from eads.core.pipeline import DecisionPipeline
from eads.core.types import DecisionRequest
from eads.governance import GovernanceLayer
from eads.synthetic_data import SupplyChainGenerator


def _request() -> DecisionRequest:
    generator = SupplyChainGenerator(seed=42, clock=FixedClock())
    return DecisionRequest(
        request_id="repro-1",
        goal="decide replenishment order for SKU-1001",
        signals=generator.generate(3),
        policy_snapshot={"region": "US", "max_order_quantity": 1000, "unit_price": 10.0},
    )


def test_identical_request_produces_identical_audit_record():
    clock = FixedClock()
    first = DecisionPipeline(governance=GovernanceLayer(), clock=clock).run(_request())
    second = DecisionPipeline(governance=GovernanceLayer(), clock=clock).run(_request())
    assert asdict(first) == asdict(second)


def test_backend_seed_support_is_recorded_on_the_trace():
    record = DecisionPipeline(clock=FixedClock()).run(_request())
    generate_step = next(step for step in record.trace if step["step"] == "generate")
    assert generate_step["seed_honored"] is True
