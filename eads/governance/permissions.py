from typing import Any

from ..core.types import Actor, ApprovalRequirement, DecisionCandidate

DEFAULT_APPROVER_ROLE = "manager"


class PermissionGate:
    """Role and value-based approval routing.

    Returns the approvals a candidate still needs, as
    :class:`~eads.core.types.ApprovalRequirement` records naming the role that can grant them.
    The requesting actor never satisfies its own requirement, even when it holds the approver
    role: separation of duties is the point of the gate.

    Unparseable actions are not handled here: they are rejected by
    :class:`~eads.governance.safety.SafetyFilter`, since a value that cannot be computed cannot be
    routed to the right approver.
    """

    def __init__(self, threshold: float = 500.0, approver_role: str = DEFAULT_APPROVER_ROLE):
        self.threshold = threshold
        self.approver_role = approver_role

    def approvals(
        self,
        candidate: DecisionCandidate,
        context: dict[str, Any] | None = None,
        actor: Actor | None = None,
    ) -> list[ApprovalRequirement]:
        context = context or {}
        total = 0.0
        for action in candidate.actions:
            if not action.parsed or action.quantity is None:
                continue
            price = context.get("unit_price", 10.0)
            total += action.quantity * price
        if total <= self.threshold:
            return []
        requester = actor.id if actor else "unattributed"
        return [
            ApprovalRequirement(
                approver_role=self.approver_role,
                reason=(
                    f"value {total:.2f} exceeds the {self.threshold:.2f} approval threshold; "
                    f"requested by {requester}"
                ),
                threshold=self.threshold,
                value=total,
            )
        ]
