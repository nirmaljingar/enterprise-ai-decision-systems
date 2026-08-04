from typing import Any

from ..core.types import DecisionCandidate


class PermissionGate:
    """Role and value-based approval routing.

    Returns the approvals a candidate still needs. Unparseable actions are not handled here:
    they are rejected by :class:`~eads.governance.safety.SafetyFilter`, since a value that
    cannot be computed cannot be routed to the right approver.
    """

    def __init__(self, threshold: float = 500.0):
        self.threshold = threshold

    def approvals(
        self, candidate: DecisionCandidate, context: dict[str, Any] | None = None
    ) -> list[str]:
        context = context or {}
        total = 0.0
        for action in candidate.actions:
            if not action.parsed or action.quantity is None:
                continue
            price = context.get("unit_price", 10.0)
            total += action.quantity * price
        if total > self.threshold:
            return ["manager_approval_required"]
        return []
