"""Trust scoring by checking a candidate against the evidence it cites.

The stub reported the candidate's *self-declared* confidence. Asking a model how much to trust it is
circular, and it is exactly the number an injected instruction would inflate.

What replaces it grades the candidate against the evidence record: whether its citations resolve,
whether the figure it proposes appears in a claim, how well supported and how trustworthy those
claims are, and whether they contradict each other. Each deduction is named, so a low score can be
explained rather than merely observed.

This is still not a calibrated hallucination probability, and no part of the system treats it as one:
trust does not gate execution. `PolicyEngine`, `SafetyFilter`, and `PermissionGate` decide that, and
they fail closed regardless of the score. Trust is a signal on the audit record and for triage.
"""

from dataclasses import dataclass, field
from typing import Any

from ..core.types import DecisionCandidate, Evidence

UNPARSED_PENALTY = 0.5
"""Multiplier applied when any proposed action could not be parsed."""

UNVERIFIABLE_CEILING = 0.5
"""Cap when no evidence was supplied: nothing was checked, so nothing is trusted much."""

UNCITED_PENALTY = 0.6
"""Multiplier when a candidate cites no evidence at all."""

UNSUPPORTED_QUANTITY_PENALTY = 0.7
"""Multiplier when the proposed figure appears in none of the cited claims."""

UNTRUSTED_SOURCE_PENALTY = 0.8
"""Multiplier when a cited claim came from an untrusted source."""

INSTRUCTION_PENALTY = 0.7
"""Multiplier when a cited claim is instruction-shaped, the shape prompt injection takes."""

CONTRADICTION_PENALTY = 0.6
"""Multiplier when two cited claims give incompatible figures."""


@dataclass(frozen=True)
class TrustAssessment:
    """A trust score with the reason for every deduction."""

    score: float
    reasons: tuple[str, ...] = ()


@dataclass
class TrustScorer:
    """Evidence-grounded trust score for a decision candidate.

    Scores what can be checked: citation resolution, whether the proposed quantity appears in a cited
    claim, the mean confidence of those claims, whether any came from an untrusted source or was
    phrased as an instruction, and whether they contradict each other. Unparseable actions are
    penalised because output the checks could not understand should never carry full trust.

    The candidate's self-declared confidence is *not* an input. It is the number an injected
    instruction would inflate, and asking a model how much to trust it is circular.

    With no evidence to check against, the score is capped at :data:`UNVERIFIABLE_CEILING` rather than
    defaulting high: an unverifiable decision is not a trustworthy one. The score never authorizes
    anything -- governance decides that, and it fails closed regardless of the score.
    """

    evidence: list[Evidence] = field(default_factory=list)

    def assess(
        self,
        candidate: DecisionCandidate,
        context: dict[str, Any] | None = None,
        evidence: list[Evidence] | None = None,
    ) -> TrustAssessment:
        available = list(evidence if evidence is not None else self.evidence)
        score = 1.0
        reasons: list[str] = []

        if not candidate.actions or any(not action.parsed for action in candidate.actions):
            score *= UNPARSED_PENALTY
            reasons.append("action_not_parsed")

        if not available:
            reasons.append("no_evidence_supplied")
            return TrustAssessment(round(min(score, UNVERIFIABLE_CEILING), 4), tuple(reasons))

        by_id = {item.id: item for item in available}
        cited = [by_id[ref] for ref in candidate.evidence_refs if ref in by_id]

        if not candidate.evidence_refs:
            score *= UNCITED_PENALTY
            reasons.append("no_evidence_cited")
        else:
            resolved = len(cited) / len(candidate.evidence_refs)
            if resolved < 1.0:
                # A citation that does not resolve is a fabricated reference, which is the most
                # direct hallucination the record can catch.
                score *= resolved
                reasons.append("citations_do_not_resolve")

        if cited:
            score *= sum(item.confidence for item in cited) / len(cited)
            if not self._quantities_supported(candidate, cited):
                score *= UNSUPPORTED_QUANTITY_PENALTY
                reasons.append("proposed_quantity_absent_from_cited_evidence")
            if any(not item.trusted for item in cited):
                score *= UNTRUSTED_SOURCE_PENALTY
                reasons.append("cited_untrusted_source")
            if any(item.imperative for item in cited):
                score *= INSTRUCTION_PENALTY
                reasons.append("cited_instruction_shaped_claim")
            if self._contradictory(cited):
                score *= CONTRADICTION_PENALTY
                reasons.append("cited_evidence_contradicts_itself")

        return TrustAssessment(round(max(0.0, min(1.0, score)), 4), tuple(reasons))

    def score(
        self,
        candidate: DecisionCandidate,
        context: dict[str, Any] | None = None,
        evidence: list[Evidence] | None = None,
    ) -> float:
        return self.assess(candidate, context, evidence).score

    @staticmethod
    def _quantities_supported(
        candidate: DecisionCandidate, cited: list[Evidence]
    ) -> bool:
        """True when every proposed figure appears in a cited claim.

        A quantity nobody reported is the signature of a number the model invented -- or was talked
        into. Candidates proposing no quantity are vacuously supported.
        """
        proposed = [
            float(action.quantity)
            for action in candidate.actions
            if action.parsed and action.quantity is not None
        ]
        if not proposed:
            return True
        reported = {value for item in cited for value in item.quantities}
        return all(value in reported for value in proposed)

    @staticmethod
    def _contradictory(cited: list[Evidence]) -> bool:
        single = [item.quantities[0] for item in cited if len(item.quantities) == 1]
        return len(set(single)) > 1


__all__ = [
    "CONTRADICTION_PENALTY",
    "INSTRUCTION_PENALTY",
    "UNCITED_PENALTY",
    "UNPARSED_PENALTY",
    "UNSUPPORTED_QUANTITY_PENALTY",
    "UNTRUSTED_SOURCE_PENALTY",
    "UNVERIFIABLE_CEILING",
    "TrustAssessment",
    "TrustScorer",
]
