from typing import Any

from ..core.types import DecisionCandidate

UNPARSEABLE_ACTION = "unparseable_action"
REGION_SCOPED_ACTIONS = frozenset({"order", "route"})


class SafetyFilter:
    """Hard safety constraints that cannot be violated.

    Every action must be checkable. An action that could not be parsed into typed fields, or
    that omits a field a hard limit applies to, is reported as a violation: the filter fails
    closed rather than approving output it does not understand.
    """

    def __init__(self, hard_limits: dict[str, Any] | None = None):
        self.hard_limits = hard_limits or {
            "max_order_quantity": 1000,
            "allowed_regions": ["US", "EU"],
        }

    def check(
        self, candidate: DecisionCandidate, context: dict[str, Any] | None = None
    ) -> list[str]:
        context = context or {}
        violations: list[str] = []
        if not candidate.actions:
            return ["no_action_proposed"]
        allowed_regions = self.hard_limits.get("allowed_regions")
        max_quantity = self.hard_limits["max_order_quantity"]
        for action in candidate.actions:
            if not action.parsed:
                violations.append(UNPARSEABLE_ACTION)
                continue
            if action.type == "order":
                if action.quantity is None:
                    violations.append("order_missing_quantity")
                elif action.quantity > max_quantity:
                    violations.append("quantity_hard_limit")
            if allowed_regions is not None and action.type in REGION_SCOPED_ACTIONS:
                # A physical action with no region cannot be checked against the region
                # allow-list, so it is rejected rather than assumed to be domestic.
                if action.region is None:
                    violations.append("region_unspecified")
                elif action.region not in allowed_regions:
                    violations.append("region_not_allowed")
        return violations
