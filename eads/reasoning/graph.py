"""The evidence graph the planner reasons over.

Evidence arrives as a flat list, but a decision needs the relationships between claims: which claims
concern the entity in the goal, which corroborate each other, and which cannot both be true. Those
relationships are what make a chain of reasoning inspectable, so they are computed explicitly here
rather than left implicit in a prompt.

Edges are lexical and deterministic. That is a limitation with a purpose: a reader can verify every
edge by looking at the two claims, and the benchmark harness can run the planner offline with a fixed
seed. Nothing here calls a model.
"""

import re
from dataclasses import dataclass, field

from ..core.types import Evidence

_TOKEN = re.compile(r"[A-Za-z][\w-]{2,}")
_STOPWORDS = frozenset(
    {
        "and", "are", "for", "from", "has", "have", "its", "that", "the", "this", "was", "were",
        "with", "will", "into", "over", "per", "than", "then", "they", "them", "there", "been",
        "not", "all", "any", "our", "out", "now", "place", "order",
    }
)
CONTRADICTION_TOLERANCE = 0.0


@dataclass(frozen=True)
class Edge:
    """A relationship between two claims, named so a reader can check it.

    ``kind`` is one of ``shares_entity``, ``corroborates``, or ``contradicts``. A contradiction is
    not a resolution: the planner surfaces it for verification rather than choosing a winner, because
    picking the larger number is how a decision quietly adopts an attacker's figure.
    """

    source: str
    target: str
    kind: str
    detail: str = ""


@dataclass
class EvidenceGraph:
    """Evidence indexed by entity, with typed edges between related claims."""

    evidence: list[Evidence]
    edges: list[Edge] = field(default_factory=list)
    by_entity: dict[str, list[str]] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.by_entity = {}
        for item in self.evidence:
            for entity in _entities(item):
                self.by_entity.setdefault(entity, []).append(item.id)
        self.edges = self._edges()

    def _edges(self) -> list[Edge]:
        edges: list[Edge] = []
        for index, left in enumerate(self.evidence):
            for right in self.evidence[index + 1 :]:
                shared = _entities(left) & _entities(right)
                if not shared:
                    continue
                conflict = _conflict(left, right)
                if conflict:
                    edges.append(Edge(left.id, right.id, "contradicts", conflict))
                elif _corroborates(left, right):
                    edges.append(
                        Edge(left.id, right.id, "corroborates", ",".join(sorted(shared)))
                    )
                else:
                    edges.append(
                        Edge(left.id, right.id, "shares_entity", ",".join(sorted(shared)))
                    )
        return edges

    def neighbours(self, evidence_id: str) -> set[str]:
        related = set()
        for edge in self.edges:
            if edge.source == evidence_id:
                related.add(edge.target)
            elif edge.target == evidence_id:
                related.add(edge.source)
        return related

    def contradictions(self) -> list[Edge]:
        return [edge for edge in self.edges if edge.kind == "contradicts"]

    def matching(self, terms: set[str]) -> list[str]:
        """Evidence ids whose entities or claim terms intersect *terms*, best match first."""
        scored = []
        for item in self.evidence:
            overlap = len(_terms(item.claim) & terms) + 2 * len(_entities(item) & terms)
            if overlap:
                scored.append((overlap, item.confidence, item.id))
        return [identifier for _, _, identifier in sorted(scored, reverse=True)]

    def get(self, evidence_id: str) -> Evidence | None:
        for item in self.evidence:
            if item.id == evidence_id:
                return item
        return None


def goal_terms(goal: str) -> set[str]:
    """Content words and identifiers of the goal, upper-cased for identifier matching."""
    terms = _terms(goal)
    return terms | {term.upper() for term in terms}


def _entities(item: Evidence) -> set[str]:
    return {entity.upper() for entity in item.entities}


def _terms(text: str) -> set[str]:
    return {
        word.lower() for word in _TOKEN.findall(text) if word.lower() not in _STOPWORDS
    }


def _corroborates(left: Evidence, right: Evidence) -> bool:
    """Two claims corroborate when they concern the same entity and agree on the numbers."""
    if not (left.quantities and right.quantities):
        return False
    return set(left.quantities) == set(right.quantities)


def _conflict(left: Evidence, right: Evidence) -> str:
    """Report the incompatible figures two claims give for the same entity, if any.

    Only claims with exactly one quantity each are compared. Multi-quantity claims are left alone
    rather than guessed at: a false contradiction sends a sound decision to verification, which is
    wasteful, while a missed one is merely undetected -- but a *wrong* pairing would be reported as
    fact, which is worse than either.
    """
    if len(left.quantities) != 1 or len(right.quantities) != 1:
        return ""
    difference = abs(left.quantities[0] - right.quantities[0])
    if difference <= CONTRADICTION_TOLERANCE:
        return ""
    return f"{left.quantities[0]} vs {right.quantities[0]}"


__all__ = ["CONTRADICTION_TOLERANCE", "Edge", "EvidenceGraph", "goal_terms"]
