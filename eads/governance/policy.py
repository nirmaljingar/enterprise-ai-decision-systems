from typing import Any

from ..core.types import DecisionCandidate
from ._utils import parse_quantity


class PolicyEngine:
    """Declarative policy evaluation for candidate decisions."""

    def __init__(self, rules: list[Any] | None = None):
        self.rules = rules or []

    def evaluate(self, candidate: DecisionCandidate, context: dict[str, Any] | None = None) -> list[str]:
        context = context or {}
        violations = []
        for action in candidate.actions:
            value = str(action.get("value", ""))
            qty = parse_quantity(value)
            if qty is None:
                continue
            max_qty = context.get("max_order_quantity", 1000)
            if qty > max_qty:
                violations.append("order_quantity_exceeds_policy_max")
        return violations
