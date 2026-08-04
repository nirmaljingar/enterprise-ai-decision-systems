from typing import Any

from ..core.types import DecisionCandidate
from ._utils import parse_quantity


class PermissionGate:
    """Role and value-based approval routing."""

    def __init__(self, threshold: float = 500.0):
        self.threshold = threshold

    def approvals(self, candidate: DecisionCandidate, context: dict[str, Any] | None = None) -> list[str]:
        context = context or {}
        total = 0.0
        for action in candidate.actions:
            value = str(action.get("value", ""))
            qty = parse_quantity(value)
            if qty is None:
                continue
            price = context.get("unit_price", 10.0)
            total += qty * price
        if total > self.threshold:
            return ["manager_approval_required"]
        return []
