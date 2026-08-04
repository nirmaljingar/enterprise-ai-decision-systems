import pytest

from eads.core.clock import FixedClock
from eads.core.pipeline import DecisionPipeline
from eads.core.types import DecisionRequest
from eads.decision.decision import DecisionEngine
from eads.evaluation import Benchmark
from eads.evaluation.metrics import (
    approval_rate,
    audit_completeness,
    decision_consistency,
    evidence_grounding_rate,
    fallback_recovery_rate,
    policy_compliance,
)
from eads.governance import GovernanceLayer
from eads.synthetic_data import SupplyChainGenerator


def _pipeline() -> DecisionPipeline:
    return DecisionPipeline(
        governance=GovernanceLayer(),
        decision_engine=DecisionEngine(),
        clock=FixedClock(),
    )


def _scenarios() -> list[dict[str, object]]:
    gen = SupplyChainGenerator(seed=3, clock=FixedClock())
    return [
        {
            "id": "b-1",
            "expected_outcome": "escalated",
            "request": DecisionRequest(
                request_id="b-1",
                goal="place replenishment order for SKU-1001",
                signals=gen.generate(3),
                policy_snapshot={
                    "max_order_quantity": 1000,
                    "unit_price": 10.0,
                    "region": "US",
                },
            ),
        },
        {
            "id": "b-2",
            "expected_outcome": "rejected",
            "request": DecisionRequest(
                request_id="b-2",
                goal="place replenishment order for SKU-1001",
                signals=gen.generate(3),
                policy_snapshot={"max_order_quantity": 5, "unit_price": 10.0, "region": "US"},
            ),
        },
    ]


def test_benchmark_reports_every_metric(tmp_path):
    report = Benchmark(
        _pipeline(),
        _scenarios(),
        output_dir=str(tmp_path),
        repeats=2,
        clock=FixedClock(),
    ).run()
    assert report["metadata"]["repeats"] == 2
    assert len(report["results"]) == 4
    for metric in (
        "approval_rate",
        "policy_compliance",
        "decision_consistency",
        "evidence_grounding_rate",
        "fallback_recovery_rate",
        "audit_completeness",
    ):
        assert 0.0 <= report[metric] <= 1.0
    assert report["decision_consistency"] == 1.0
    assert report["policy_compliance"] == 1.0
    assert report["fallback_recovery_rate"] == 1.0
    assert report["audit_completeness"] == 1.0
    assert report["evidence_grounding_rate"] == 1.0


def test_benchmark_rejects_zero_repeats():
    with pytest.raises(ValueError, match="repeats"):
        Benchmark(_pipeline(), _scenarios(), repeats=0)


def test_decision_consistency_requires_a_single_scenario():
    runs = [
        {"scenario_id": "a", "outcome": "approved", "execution_status": "success"},
        {"scenario_id": "b", "outcome": "approved", "execution_status": "success"},
    ]
    with pytest.raises(ValueError, match="single scenario"):
        decision_consistency(runs)


def test_decision_consistency_detects_divergence():
    runs = [
        {"scenario_id": "a", "outcome": "approved", "execution_status": "success"},
        {"scenario_id": "a", "outcome": "rejected", "execution_status": "blocked"},
    ]
    assert decision_consistency(runs) == 0.5


def test_policy_compliance_credits_a_correct_block():
    runs = [{"scenario_id": "a", "outcome": "rejected", "expected_outcome": "rejected"}]
    assert policy_compliance(runs) == 1.0
    assert approval_rate(runs) == 0.0


def test_policy_compliance_ignores_unlabelled_runs():
    assert policy_compliance([{"scenario_id": "a", "outcome": "approved"}]) == 1.0


def test_evidence_grounding_rate_penalizes_unsupported_decisions():
    grounded = [{"evidence_refs": ["ev_1", "ev_2"], "evidence_ids": ["ev_1", "ev_2"]}]
    partial = [{"evidence_refs": ["ev_1", "ev_9"], "evidence_ids": ["ev_1"]}]
    assert evidence_grounding_rate(grounded) == 1.0
    assert evidence_grounding_rate(partial) == 0.5
    assert evidence_grounding_rate([{"evidence_refs": [], "evidence_ids": ["ev_1"]}]) == 0.0


def test_fallback_recovery_rate_only_counts_injected_violations():
    runs = [
        {"expected_outcome": "rejected", "execution_status": "blocked"},
        {"expected_outcome": "rejected", "execution_status": "success"},
        {"expected_outcome": "approved", "execution_status": "success"},
    ]
    assert fallback_recovery_rate(runs) == 0.5


def test_audit_completeness_detects_missing_fields():
    complete = {
        "request_id": "r",
        "trace": [{}],
        "decision": {},
        "verdict": {},
        "execution": {},
        "timestamp": "t",
        "policy_snapshot_id": "pol_0",
        "actor": {"id": "planner-7", "roles": ()},
    }
    assert audit_completeness([{"audit_record": complete}]) == 1.0
    incomplete = dict(complete, verdict=None)
    assert audit_completeness([{"audit_record": incomplete}]) == 0.0
