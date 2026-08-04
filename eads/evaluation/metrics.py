"""Metrics over benchmark run summaries.

Every function takes the list of run dictionaries emitted by
:class:`eads.evaluation.benchmark.Benchmark`. A run has at least ``scenario_id``,
``outcome``, ``execution_status``, ``approved``, ``evidence_refs``, ``evidence_ids``, and
``audit_record``; scenarios may additionally declare an ``expected_outcome`` label
(``approved``, ``rejected``, or ``escalated``) so correctness, not just approval, can be
measured.
"""

from typing import Any

REQUIRED_AUDIT_FIELDS = (
    "request_id",
    "trace",
    "decision",
    "verdict",
    "execution",
    "timestamp",
    "policy_snapshot_id",
    "actor",
)
RECOVERED_STATUSES = frozenset({"blocked", "escalated"})
WITHHELD_OUTCOMES = frozenset({"rejected", "escalated"})


def approval_rate(runs: list[dict[str, Any]]) -> float:
    """Fraction of runs whose decision was approved for execution.

    This is a throughput measure, not a correctness measure: a pipeline that approves
    everything scores 1.0. Use :func:`policy_compliance` to measure correctness.
    """
    if not runs:
        return 0.0
    approved = sum(bool(run.get("approved", False)) for run in runs)
    return approved / len(runs)


def policy_compliance(runs: list[dict[str, Any]]) -> float:
    """Fraction of labelled runs whose outcome matched the expected outcome.

    Only runs carrying an ``expected_outcome`` label count towards the denominator, so
    correctly *blocking* an unsafe decision raises compliance instead of lowering it.
    Returns 1.0 when no run is labelled (nothing was asserted).
    """
    labelled = [run for run in runs if run.get("expected_outcome")]
    if not labelled:
        return 1.0
    matched = sum(1 for run in labelled if run["outcome"] == run["expected_outcome"])
    return matched / len(labelled)


def decision_consistency(runs: list[dict[str, Any]]) -> float:
    """Fraction of repeated runs of one scenario that reached the same outcome.

    Raises ``ValueError`` if the runs come from more than one scenario: agreement across
    different scenarios says nothing about determinism.
    """
    if len(runs) < 2:
        return 1.0
    scenarios = {run.get("scenario_id") for run in runs}
    if len(scenarios) > 1:
        raise ValueError(
            "decision_consistency compares repeated runs of a single scenario, "
            f"but got {len(scenarios)}: {sorted(map(str, scenarios))}"
        )
    outcomes = [(run.get("outcome"), run.get("execution_status")) for run in runs]
    return sum(outcome == outcomes[0] for outcome in outcomes) / len(outcomes)


def evidence_grounding_rate(runs: list[dict[str, Any]]) -> float:
    """Fraction of evidence references that resolve to evidence produced by the run.

    A run whose decision cites no evidence at all counts as ungrounded (0.0) rather than
    being skipped, so an unsupported decision cannot inflate the score.
    """
    if not runs:
        return 1.0
    scores = []
    for run in runs:
        refs = list(run.get("evidence_refs") or [])
        available = set(run.get("evidence_ids") or [])
        if not refs:
            scores.append(0.0)
            continue
        scores.append(sum(ref in available for ref in refs) / len(refs))
    return sum(scores) / len(scores)


def fallback_recovery_rate(runs: list[dict[str, Any]]) -> float:
    """Fraction of runs expected to be withheld that were in fact withheld.

    Only runs labelled ``rejected`` or ``escalated`` count; "recovered" means execution was
    blocked or escalated rather than performed. Returns 1.0 when no violation was injected.
    """
    withheld = [run for run in runs if run.get("expected_outcome") in WITHHELD_OUTCOMES]
    if not withheld:
        return 1.0
    recovered = sum(run.get("execution_status") in RECOVERED_STATUSES for run in withheld)
    return recovered / len(withheld)


def audit_completeness(runs: list[dict[str, Any]]) -> float:
    """Fraction of runs whose audit record carries every required trace field."""
    if not runs:
        return 1.0
    complete = 0
    for run in runs:
        record = run.get("audit_record") or {}
        if all(record.get(field) is not None for field in REQUIRED_AUDIT_FIELDS):
            complete += 1
    return complete / len(runs)


__all__ = [
    "approval_rate",
    "audit_completeness",
    "decision_consistency",
    "evidence_grounding_rate",
    "fallback_recovery_rate",
    "policy_compliance",
]
