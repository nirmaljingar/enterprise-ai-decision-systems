"""Extract individual claims, with their source spans, from unstructured signal text.

The point of extraction is not to restate a signal — it is to make a decision *auditable*. A claim
that cannot be pointed back at the characters it came from is unverifiable, so every claim carries
the span it was cut from, and every span indexes the original signal content unmodified.

The extractors are deliberately lexical and dependency-free. That is a real limitation, stated
plainly in the module README: they recognise quantities, percentages, currency, dates, identifiers,
and regions, and they do not do coreference, negation scope, or entity linking against a knowledge
base. A lexical extractor that says so is more useful than a model-shaped one that cannot be run.
"""

import re
from dataclasses import dataclass, field

SENTENCE_BOUNDARY = re.compile(r"(?<=[.!?;])\s+|\n+")
MINIMUM_CLAIM_WORDS = 3

_QUANTITY = re.compile(
    r"(?<![\w.])(\d+(?:,\d{3})*(?:\.\d+)?)\s*"
    r"(units?|pcs|items?|beds?|tickets?|days?|hours?|minutes?|seconds?|%|percent)",
    re.IGNORECASE,
)
_CURRENCY = re.compile(r"([$£€])\s?(\d+(?:,\d{3})*(?:\.\d+)?)\s*([kmb]|million|billion)?", re.IGNORECASE)
_IDENTIFIER = re.compile(r"\b(?:SKU|PO|ORD|TCK|INC|CVE|ID)[-#]?\d[\w-]*\b", re.IGNORECASE)
_REGION = re.compile(
    r"\b(?:region\s+)?(US|USA|EU|UK|CN|IN|APAC|EMEA|LATAM|"
    r"us-(?:east|west|central)|eu-(?:west|central)|North|South|East|West)\b"
)
_ORGANISATION = re.compile(r"\b(?:Supplier|Warehouse|Vendor|Customer|Carrier|Service)\s+[\w-]+\b")

# Instruction-shaped text is the shape prompt injection takes when it arrives inside ingested
# content. Extraction does not decide what to do about it; it records that the text was imperative
# so the trust boundary is visible downstream instead of being inferred from prose later.
_IMPERATIVE = re.compile(
    r"\b(?:ignore (?:all |your )?(?:previous|prior) instructions?|disregard|"
    r"you must|you should now|immediately (?:place|order|ship|approve|release)|"
    r"approve (?:this|the) (?:order|request)|no (?:further )?(?:review|approval) (?:is )?needed|"
    r"already (?:been )?(?:granted|approved)|as (?:your )?system|new instructions?)\b",
    re.IGNORECASE,
)

MULTIPLIERS = {"k": 1_000.0, "m": 1_000_000.0, "b": 1_000_000_000.0,
               "million": 1_000_000.0, "billion": 1_000_000_000.0}


@dataclass(frozen=True)
class Claim:
    """One extracted assertion, and the characters of the signal it came from.

    ``start`` and ``end`` index the *original* signal content, so a reviewer can quote the source.
    ``specificity`` counts the checkable details found — quantities, identifiers, regions,
    organisations — and is what confidence is derived from, rather than a number the extractor
    asserts about itself.
    """

    text: str
    start: int
    end: int
    quantities: tuple[float, ...] = ()
    percentages: tuple[float, ...] = ()
    amounts: tuple[float, ...] = ()
    identifiers: tuple[str, ...] = ()
    regions: tuple[str, ...] = ()
    organisations: tuple[str, ...] = ()
    imperative: bool = False
    terms: frozenset[str] = field(default_factory=frozenset)

    @property
    def specificity(self) -> int:
        return len(
            self.quantities
            + self.percentages
            + self.amounts
            + self.identifiers
            + self.regions
            + self.organisations
        )


def sentences(content: str) -> list[tuple[str, int, int]]:
    """Split *content* into sentence-like fragments with their character offsets.

    Offsets are what make a claim checkable, so splitting is done by scanning rather than by
    ``str.split``: a fragment that has lost its position cannot be quoted back to a reviewer.
    """
    found: list[tuple[str, int, int]] = []
    cursor = 0
    for match in SENTENCE_BOUNDARY.finditer(content):
        found.append((content[cursor : match.start()], cursor, match.start()))
        cursor = match.end()
    found.append((content[cursor:], cursor, len(content)))

    result = []
    for text, start, end in found:
        stripped = text.strip()
        if not stripped:
            continue
        offset = text.index(stripped)
        result.append((stripped, start + offset, start + offset + len(stripped)))
    return result


def extract_claims(content: str) -> list[Claim]:
    """Extract every claim-like fragment of *content*, in order.

    Fragments shorter than :data:`MINIMUM_CLAIM_WORDS` words are dropped: a bare identifier or a
    salutation is not a claim, and admitting it as one inflates evidence counts without adding
    anything a decision can be grounded in.
    """
    claims = []
    for text, start, end in sentences(content):
        if len(text.split()) < MINIMUM_CLAIM_WORDS:
            continue
        claims.append(
            Claim(
                text=text,
                start=start,
                end=end,
                quantities=_quantities(text),
                percentages=_percentages(text),
                amounts=_amounts(text),
                identifiers=tuple(dict.fromkeys(_IDENTIFIER.findall(text))),
                regions=tuple(dict.fromkeys(_REGION.findall(text))),
                organisations=tuple(dict.fromkeys(_ORGANISATION.findall(text))),
                imperative=bool(_IMPERATIVE.search(text)),
                terms=_terms(text),
            )
        )
    return claims


def _quantities(text: str) -> tuple[float, ...]:
    return tuple(
        float(number.replace(",", ""))
        for number, unit in _QUANTITY.findall(text)
        if unit not in {"%", "percent"}
    )


def _percentages(text: str) -> tuple[float, ...]:
    return tuple(
        float(number.replace(",", ""))
        for number, unit in _QUANTITY.findall(text)
        if unit in {"%", "percent"}
    )


def _amounts(text: str) -> tuple[float, ...]:
    amounts = []
    for _symbol, number, multiplier in _CURRENCY.findall(text):
        value = float(number.replace(",", ""))
        amounts.append(value * MULTIPLIERS.get(multiplier.lower(), 1.0))
    return tuple(amounts)


def _terms(text: str) -> frozenset[str]:
    """Content words, used to recognise that two signals say the same thing.

    Deliberately crude: lowercased word forms with short function words dropped. It resolves
    duplicates and near-duplicates across sources, and it is not synonymy.
    """
    return frozenset(
        word
        for word in re.findall(r"[a-z][\w-]{2,}", text.lower())
        if word not in _STOPWORDS
    )


_STOPWORDS = frozenset(
    {
        "and", "are", "for", "from", "has", "have", "its", "that", "the", "this", "was", "were",
        "with", "will", "into", "over", "per", "than", "then", "they", "them", "there", "been",
        "not", "all", "any", "our", "out", "now",
    }
)


__all__ = ["MINIMUM_CLAIM_WORDS", "Claim", "extract_claims", "sentences"]
