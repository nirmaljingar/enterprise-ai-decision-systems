"""Multi-hop planning over the evidence graph.

The stub returned one step referencing *every* piece of evidence. That is not a plan, and worse, it
made grounding meaningless: a decision that cites everything cites nothing, since no reviewer can
tell which claim supported which conclusion, and `evidence_grounding_rate` is satisfied by
construction.

What replaces it walks the graph from the goal:

1. **Hop 1** -- claims whose entities or terms match the goal.
2. **Hop 2..n** -- claims connected to those by a typed edge, so a claim about a supplier reaches a
   claim about the warehouse that supplier ships to.
3. **Verification** -- every contradiction found among the selected claims becomes an explicit step,
   because two claims giving different figures for one entity is a fact about the evidence, and
   resolving it by taking the larger number is how a decision quietly adopts an attacker's figure.
4. **Review** -- instruction-shaped claims from untrusted sources become a step of their own, so the
   plan shows that the text was seen and treated as data.

The plan references only the claims it used, at a recorded hop depth, with the reason each was
selected. Nothing here calls a model: planning is deterministic so it can be replayed and audited.
"""

import hashlib
from dataclasses import dataclass
from typing import Any

from ..core.types import Evidence, Plan
from .graph import EvidenceGraph, goal_terms

MAXIMUM_HOPS = 2
MAXIMUM_EVIDENCE = 12


@dataclass
class ReasoningEngine:
    """Evidence-backed planning for decision support.

    Selects the evidence that bears on the goal by walking the evidence graph outward from it,
    surfaces contradictions and untrusted instructions as explicit steps, and emits an ordered plan
    citing only the claims it used.

    Reasoning is lexical and deterministic: edges come from shared entities and matching figures, not
    from a model or an embedding. Two claims that concern the same thing in different words are not
    connected, which is stated in the module README rather than glossed over.
    """

    maximum_hops: int = MAXIMUM_HOPS
    maximum_evidence: int = MAXIMUM_EVIDENCE

    def plan(self, evidence: list[Evidence], goal: str) -> Plan:
        graph = EvidenceGraph(list(evidence))
        selected = self._select(graph, goal)
        steps = self._steps(graph, goal, selected)
        return Plan(
            # Digest rather than hash(): str.__hash__ is salted per process, and a plan id that
            # changes between runs would break the reproducibility contract on the audit record.
            plan_id=f"plan_{hashlib.sha256(goal.encode()).hexdigest()[:12]}",
            goal=goal,
            steps=steps,
            evidence_refs=[identifier for identifier, _ in selected],
        )

    def _select(self, graph: EvidenceGraph, goal: str) -> list[tuple[str, int]]:
        """Return ``(evidence_id, hop)`` pairs, nearest to the goal first."""
        frontier = graph.matching(goal_terms(goal))
        selected: dict[str, int] = {identifier: 1 for identifier in frontier}

        hop = 1
        while frontier and hop < self.maximum_hops:
            hop += 1
            next_frontier = []
            for identifier in frontier:
                for neighbour in sorted(graph.neighbours(identifier)):
                    if neighbour not in selected:
                        selected[neighbour] = hop
                        next_frontier.append(neighbour)
            frontier = next_frontier

        if not selected and graph.evidence:
            # No claim mentions anything in the goal. Falling back to the best-supported claims keeps
            # the decision attributable to something a reviewer can read, and the plan says outright
            # that the link to the goal was not established rather than implying one.
            ranked = sorted(graph.evidence, key=lambda item: -item.confidence)
            selected = {item.id: 0 for item in ranked[: self.maximum_evidence]}

        return sorted(selected.items(), key=lambda pair: (pair[1], pair[0]))[
            : self.maximum_evidence
        ]

    def _steps(
        self, graph: EvidenceGraph, goal: str, selected: list[tuple[str, int]]
    ) -> list[dict[str, Any]]:
        chosen = {identifier for identifier, _ in selected}
        steps: list[dict[str, Any]] = []

        if not chosen:
            return [
                {
                    "action": "abstain",
                    "reason": "no_evidence_available",
                    "evidence_ids": [],
                }
            ]

        direct = [identifier for identifier, hop in selected if hop == 1]
        indirect = [identifier for identifier, hop in selected if hop > 1]
        unlinked = [identifier for identifier, hop in selected if hop == 0]

        if unlinked:
            steps.append(
                {
                    "action": "gather",
                    "reason": "no_evidence_matched_the_goal; using best-supported claims",
                    "hop": 0,
                    "evidence_ids": unlinked,
                }
            )
        if direct:
            steps.append(
                {
                    "action": "gather",
                    "reason": "matches_goal_entities_or_terms",
                    "hop": 1,
                    "evidence_ids": direct,
                }
            )
        if indirect:
            steps.append(
                {
                    "action": "gather",
                    "reason": "connected_to_goal_evidence",
                    "hop": 2,
                    "evidence_ids": indirect,
                }
            )

        conflicts = [
            edge
            for edge in graph.contradictions()
            if edge.source in chosen and edge.target in chosen
        ]
        for edge in conflicts:
            steps.append(
                {
                    "action": "verify",
                    "reason": f"contradictory_quantities:{edge.detail}",
                    "evidence_ids": [edge.source, edge.target],
                }
            )

        untrusted_instructions = [
            identifier
            for identifier in sorted(chosen)
            if _is_untrusted_instruction(graph.get(identifier))
        ]
        if untrusted_instructions:
            steps.append(
                {
                    # The instruction is recorded as data and never followed. Governance is what
                    # actually stops it; this step exists so the plan shows the text was seen.
                    "action": "review_untrusted_instruction",
                    "reason": "instruction_shaped_claim_from_untrusted_source",
                    "evidence_ids": untrusted_instructions,
                }
            )

        steps.append(
            {
                "action": "propose",
                "reason": "goal_pursued_on_the_gathered_evidence",
                "goal": goal,
                # A proposal blocked behind unresolved contradictions is still proposed, because
                # withholding is governance's decision and not the planner's. Flagging it here keeps
                # the reason visible on the audit trail.
                "unresolved_contradictions": len(conflicts),
                "evidence_ids": [identifier for identifier, _ in selected],
            }
        )
        return steps


def _is_untrusted_instruction(item: Evidence | None) -> bool:
    return item is not None and item.imperative and not item.trusted


__all__ = ["MAXIMUM_EVIDENCE", "MAXIMUM_HOPS", "ReasoningEngine"]
