from ..core.types import (
    ESCALATED,
    REJECTED,
    Actor,
    ApprovalRequirement,
    DecisionCandidate,
    ExecutionResult,
)

_STATUS = {REJECTED: "blocked", ESCALATED: "escalated"}
_SAFE_ACTION = {
    REJECTED: "discard_and_notify",
    ESCALATED: "request_human_review",
}


class FallbackHandler:
    """Governed fallback and human escalation for decisions that must not execute."""

    def handle(
        self,
        candidate: DecisionCandidate,
        reason: str,
        outcome: str = REJECTED,
        actor: Actor | None = None,
        required_approvals: list[ApprovalRequirement] | None = None,
    ) -> ExecutionResult:
        return ExecutionResult(
            action_id="fallback",
            status=_STATUS.get(outcome, "blocked"),
            output={
                "reason": reason,
                "outcome": outcome,
                "safe_action": _SAFE_ACTION.get(outcome, "discard_and_notify"),
                "candidate": candidate.plan_id,
                "requested_by": actor.id if actor else "unattributed",
                "awaiting_roles": [
                    approval.approver_role for approval in (required_approvals or [])
                ],
            },
            latency_ms=0.0,
        )
