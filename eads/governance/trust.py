from typing import Any

from ..core.types import DecisionCandidate

UNPARSED_PENALTY = 0.5
"""Multiplier applied when any proposed action could not be parsed."""


class TrustScorer:
    """Heuristic trust score for a decision candidate.

    Stub: this is not a calibrated hallucination measure. It reports the candidate's
    self-declared confidence, clamped to [0, 1], and halves it when any action could not be
    parsed -- output the checks could not understand should never carry full trust. It does
    not compare claims against evidence; a real scorer would.
    """

    def score(
        self, candidate: DecisionCandidate, context: dict[str, Any] | None = None
    ) -> float:
        score = max(0.0, min(1.0, candidate.confidence))
        if not candidate.actions or any(not action.parsed for action in candidate.actions):
            score *= UNPARSED_PENALTY
        return score
