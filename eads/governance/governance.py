from typing import Any

from ..core.types import DecisionCandidate, Verdict
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
        self, candidate: DecisionCandidate, context: dict[str, Any] | None = None
    ) -> Verdict:
        context = context or {}
        policy_violations = self.policy.evaluate(candidate, context)
        safety_violations = self.safety.check(candidate, context)
        all_violations = policy_violations + safety_violations
        approvals = self.permissions.approvals(candidate, context)
        trust = self.trust.score(candidate, context)
        approved = not all_violations and not approvals
        reason = "passed" if approved else "; ".join(all_violations + approvals)
        return Verdict(
            approved=approved,
            reason=reason,
            violated_policies=all_violations,
            required_approvals=approvals,
            trust_score=trust,
        )
