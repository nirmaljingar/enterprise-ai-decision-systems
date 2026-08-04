"""Turn unstructured signals into grounded, deduplicated, span-attributed evidence.

The previous implementation copied each signal verbatim into one claim with ``confidence=1.0``. That
is worse than doing nothing: it produced an evidence graph whose every node asserted certainty about
text nobody had examined, and it made the downstream `evidence_grounding_rate` meaningless, since a
citation always resolved.

What replaces it does three things the copy could not:

* **Segments** each signal into individual claims, so a decision cites the sentence that supports it
  rather than a whole email.
* **Attributes** every claim to the characters it came from, so a reviewer can quote the source and a
  changed source is detectable.
* **Corroborates**: identical or near-identical claims from different sources collapse into one
  piece of evidence listing every source, which is the only honest way to represent two suppliers
  reporting the same disruption.

Confidence is *derived* — from how much checkable detail a claim contains and how many independent
sources assert it — and is capped below 1.0. Certainty is not something an extractor is in a
position to claim.
"""

from dataclasses import dataclass, field

from ..core.types import Evidence, Signal, SourceSpan
from .extraction import Claim, extract_claims

EXTRACTOR = "lexical_claim_extractor_v1"

BASE_CONFIDENCE = 0.4
DETAIL_WEIGHT = 0.1
MAXIMUM_DETAIL_BONUS = 0.3
CORROBORATION_WEIGHT = 0.1
MAXIMUM_CORROBORATION_BONUS = 0.2
TRUST_BONUS = 0.05
CONFIDENCE_CEILING = 0.95
SIMILARITY_THRESHOLD = 0.8


@dataclass
class IngestionPipeline:
    """Convert unstructured enterprise signals into grounded evidence.

    Segments each signal into claims, attributes each claim to its source span, merges claims that
    corroborate each other, and derives a confidence from the checkable detail found rather than
    asserting one.

    ``trusted_sources`` names the sources whose content the *caller* vouches for. It affects only the
    recorded ``trusted`` flag and a small confidence bonus — it never grants authority. Untrusted
    content is ingested normally: suppressing it would hide the attack rather than contain it, and
    containment is the governance layer's job, which reads typed actions and not evidence prose.
    """

    trusted_sources: frozenset[str] = field(default_factory=frozenset)
    similarity_threshold: float = SIMILARITY_THRESHOLD

    def ingest(self, signals: list[Signal]) -> list[Evidence]:
        groups: list[_Group] = []
        for signal in signals:
            trusted = self._is_trusted(signal)
            for claim in extract_claims(signal.content):
                match = self._match(groups, claim)
                if match is None:
                    groups.append(_Group(claim=claim, signals=[signal], trusted=trusted))
                else:
                    match.add(claim, signal, trusted)
        return [group.to_evidence(index) for index, group in enumerate(groups)]

    def _is_trusted(self, signal: Signal) -> bool:
        if signal.metadata.get("untrusted"):
            # An explicit marking on the signal wins over the source allow-list: a caller that has
            # already identified content as untrusted should not have that overridden by a source
            # name that happens to be on the list.
            return False
        return signal.source in self.trusted_sources

    def _match(self, groups: list["_Group"], claim: Claim) -> "_Group | None":
        for group in groups:
            if _similarity(group.claim.terms, claim.terms) >= self.similarity_threshold:
                return group
        return None


@dataclass
class _Group:
    """One claim and every signal found to assert it."""

    claim: Claim
    signals: list[Signal]
    trusted: bool
    spans: list[SourceSpan] = field(default_factory=list)
    imperative: bool = False

    def __post_init__(self) -> None:
        self.imperative = self.claim.imperative
        self.spans = [_span(self.signals[0], self.claim)]

    def add(self, claim: Claim, signal: Signal, trusted: bool) -> None:
        self.signals.append(signal)
        self.spans.append(_span(signal, claim))
        # Corroboration must not launder an instruction: if any source phrased the claim as a
        # command, the merged evidence stays marked, and trust is the weakest of the sources.
        self.imperative = self.imperative or claim.imperative
        self.trusted = self.trusted and trusted

    def to_evidence(self, index: int) -> Evidence:
        signal_ids = list(dict.fromkeys(signal.id for signal in self.signals))
        return Evidence(
            # Keyed on the first source signal so an id stays resolvable to a source, with the claim
            # index appended because a signal now yields several claims rather than exactly one.
            id=f"ev_{signal_ids[0]}_{index}",
            signal_ids=signal_ids,
            claim=self.claim.text,
            confidence=self._confidence(len(signal_ids)),
            source_refs=signal_ids,
            extracted_by=EXTRACTOR,
            provenance=tuple(self.spans),
            entities=self.claim.identifiers
            + self.claim.regions
            + tuple(self.claim.organisations),
            quantities=self.claim.quantities + self.claim.percentages + self.claim.amounts,
            imperative=self.imperative,
            trusted=self.trusted,
        )

    def _confidence(self, sources: int) -> float:
        detail = min(self.claim.specificity * DETAIL_WEIGHT, MAXIMUM_DETAIL_BONUS)
        corroboration = min(
            (sources - 1) * CORROBORATION_WEIGHT, MAXIMUM_CORROBORATION_BONUS
        )
        trust = TRUST_BONUS if self.trusted else 0.0
        return round(
            min(BASE_CONFIDENCE + detail + corroboration + trust, CONFIDENCE_CEILING), 4
        )


def _span(signal: Signal, claim: Claim) -> SourceSpan:
    return SourceSpan(
        signal_id=signal.id, start=claim.start, end=claim.end, text=claim.text
    )


def _similarity(left: frozenset[str], right: frozenset[str]) -> float:
    """Jaccard overlap of content words. Zero when either side has no content words."""
    if not left or not right:
        return 0.0
    return len(left & right) / len(left | right)


__all__ = ["EXTRACTOR", "IngestionPipeline"]
