from typing import Any


def decision_consistency(records: list[dict[str, Any]]) -> float:
    """Fraction of repeated runs producing the same execution status."""
    if len(records) < 2:
        return 1.0
    decisions = [str(r.get("execution_status")) for r in records]
    return float(sum(d == decisions[0] for d in decisions)) / float(len(decisions))


def policy_compliance(records: list[dict[str, Any]]) -> float:
    """Fraction of decisions passing policy/safety/permissions."""
    total = len(records)
    if not total:
        return 1.0
    passed = sum(bool(r.get("approved", False)) for r in records)
    return float(passed / total)
