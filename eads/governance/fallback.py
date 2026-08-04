from ..core.types import DecisionCandidate, ExecutionResult


class FallbackHandler:
    """Governed fallback and human escalation."""

    def handle(self, candidate: DecisionCandidate, reason: str) -> ExecutionResult:
        return ExecutionResult(
            action_id="fallback",
            status="blocked",
            output={
                "reason": reason,
                "safe_action": "request_human_review",
                "candidate": candidate.plan_id,
            },
            latency_ms=0.0,
        )
