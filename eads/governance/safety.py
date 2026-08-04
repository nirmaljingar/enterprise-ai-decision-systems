from typing import Any

from ..core.types import DecisionCandidate
from ._utils import parse_quantity


class SafetyFilter:
    """Hard safety constraints that cannot be violated."""

    def __init__(self, hard_limits: dict[str, Any] | None = None):
        self.hard_limits = hard_limits or {
            "max_order_quantity": 1000,
            "allowed_regions": ["US", "EU"],
        }

    def check(self, candidate: DecisionCandidate, context: dict[str, Any] | None = None) -> list[str]:
        context = context or {}
        violations = []
        for action in candidate.actions:
            value = str(action.get("value", ""))
            qty = parse_quantity(value)
            if qty is None:
                continue
            if qty > self.hard_limits["max_order_quantity"]:
                violations.append("quantity_hard_limit")
        return violations
