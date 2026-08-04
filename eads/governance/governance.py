from typing import Any

from ..core.types import (
    APPROVED,
    ESCALATED,
    REJECTED,
    Actor,
    DecisionCandidate,
    Verdict,
)
from .audit import AuditLogger
from .fallback import FallbackHandler
from .permissions import PermissionGate
from .policy import PolicyEngine
from .safety import SafetyFilter
from .trust import TrustScorer


class GovernanceLayer:
    """Cross-cutting policy, safety, permissions, fallback, audit, and trust."""

    def __init__(
        self,
        policy_engine: PolicyEngine | None = None,
        safety_filter: SafetyFilter | None = None,
        permission_gate: PermissionGate | None = None,
        fallback: FallbackHandler | None = None,
        trust_scorer: TrustScorer | None = None,
        audit_logger: AuditLogger | None = None,
    ) -> None:
        self.policy = policy_engine or PolicyEngine()
        self.safety = safety_filter or SafetyFilter()
        self.permissions = permission_gate or PermissionGate()
        self.fallback = fallback or FallbackHandler()
        self.trust = trust_scorer or TrustScorer()
        self.audit = audit_logger or AuditLogger()

    def review(
        self,
        candidate: DecisionCandidate,
        context: dict[str, Any] | None = None,
        actor: Actor | None = None,
    ) -> Verdict:
        context = context or {}
        policy_violations = self.policy.evaluate(candidate, context)
        safety_violations = self.safety.check(candidate, context)
        all_violations = policy_violations + safety_violations
        approvals = self.permissions.approvals(candidate, context, actor)
        trust = self.trust.score(candidate, context)
        if all_violations:
            # A violation is terminal: no approval can authorize an unsafe action.
            outcome = REJECTED
            reason = "; ".join(all_violations)
        elif approvals:
            outcome = ESCALATED
            reason = "; ".join(
                f"{approval.approver_role}: {approval.reason}" for approval in approvals
            )
        else:
            outcome = APPROVED
            reason = "passed"
        return Verdict(
            approved=outcome == APPROVED,
            reason=reason,
            violated_policies=all_violations,
            required_approvals=approvals,
            trust_score=trust,
            outcome=outcome,
        )
