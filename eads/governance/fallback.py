from ..core.types import ESCALATED, REJECTED, DecisionCandidate, ExecutionResult

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
    ) -> ExecutionResult:
        return ExecutionResult(
            action_id="fallback",
            status=_STATUS.get(outcome, "blocked"),
            output={
                "reason": reason,
                "outcome": outcome,
                "safe_action": _SAFE_ACTION.get(outcome, "discard_and_notify"),
                "candidate": candidate.plan_id,
            },
            latency_ms=0.0,
        )
