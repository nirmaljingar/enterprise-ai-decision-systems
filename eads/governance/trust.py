from typing import Any

from ..core.types import DecisionCandidate


class TrustScorer:
    """Aggregate trust and hallucination-mitigation score."""

    def score(
        self, candidate: DecisionCandidate, context: dict[str, Any] | None = None
    ) -> float:
        return max(0.0, min(1.0, candidate.confidence))
