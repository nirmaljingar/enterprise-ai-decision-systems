from typing import Any

from ..core.types import DecisionCandidate
from .safety import UNPARSEABLE_ACTION


class PolicyEngine:
    """Declarative policy evaluation for candidate decisions.

    Fails closed: an action that cannot be parsed into typed fields is a violation, because
    no policy can be shown to hold over text the engine does not understand.
    """

    def __init__(self, rules: list[Any] | None = None):
        self.rules = rules or []

    def evaluate(
        self, candidate: DecisionCandidate, context: dict[str, Any] | None = None
    ) -> list[str]:
        context = context or {}
        violations: list[str] = []
        if not candidate.actions:
            return ["no_action_proposed"]
        max_qty = context.get("max_order_quantity", 1000)
        for action in candidate.actions:
            if not action.parsed:
                violations.append(UNPARSEABLE_ACTION)
                continue
            if action.type != "order":
                continue
            if action.quantity is None:
                violations.append("order_missing_quantity")
            elif action.quantity > max_qty:
                violations.append("order_quantity_exceeds_policy_max")
        return violations
