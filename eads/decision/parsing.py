"""Parse free-form model output into a typed, checkable action.

The governance layer evaluates :class:`~eads.core.types.ProposedAction` fields, never raw
model text. Parsing therefore happens exactly once, here, at the boundary between the
probabilistic model and the deterministic checks.
"""

import re
from collections.abc import Callable

from ..core.types import ProposedAction

_QUANTITY = re.compile(r"(?:order_)?quantity\s*[=:]\s*(\d+)", re.IGNORECASE)
_REGION = re.compile(r"region\s*[=:]\s*([A-Za-z][\w-]*)", re.IGNORECASE)
_LABELLED = {
    "route": re.compile(r"route\s*[=:]\s*([\w-]+)", re.IGNORECASE),
    "mitigation": re.compile(r"mitigation\s*[=:]\s*([\w-]+)", re.IGNORECASE),
    "decision": re.compile(r"decision\s*[=:]\s*([\w-]+)", re.IGNORECASE),
}


def _sole_value(
    pattern: re.Pattern[str],
    raw_value: str,
    normalize: Callable[[str], str] = str,
) -> str | None:
    """The one value ``pattern`` matches, or ``None`` if it matches several that disagree.

    A completion stating a field twice with two different values has not been parsed: it has been
    disambiguated, and taking the first match picks a winner by position. The adversary here writes
    the text being summarised, so position is something an attacker chooses. Repeats that agree --
    under ``normalize``, so ``region=US`` and ``region=us`` are one value -- are harmless and stay
    allowed.
    """
    values = {normalize(match.group(1)) for match in pattern.finditer(raw_value)}
    if len(values) != 1:
        return None
    return values.pop()


def parse_action(raw_value: str, region_default: str | None = None) -> ProposedAction:
    """Parse one model completion into a :class:`ProposedAction`.

    ``parsed`` is ``True`` only when the completion matched a known action grammar exactly once.
    Callers must treat ``parsed is False`` as "not checkable", and the governance layer rejects such
    actions rather than letting them through unchecked.
    """
    region_matched = _REGION.search(raw_value) is not None
    region = _sole_value(_REGION, raw_value, str.upper)
    if region_matched and region is None:
        return ProposedAction(type="unknown", raw_value=raw_value, parsed=False)
    region = region or region_default

    if _QUANTITY.search(raw_value):
        quantity = _sole_value(_QUANTITY, raw_value, lambda value: str(int(value)))
        if quantity is None:
            return ProposedAction(type="unknown", raw_value=raw_value, region=region, parsed=False)
        return ProposedAction(
            type="order",
            raw_value=raw_value,
            quantity=int(quantity),
            region=region,
            parsed=True,
        )

    for action_type, pattern in _LABELLED.items():
        if pattern.search(raw_value):
            label = _sole_value(pattern, raw_value)
            if label is None:
                return ProposedAction(
                    type="unknown", raw_value=raw_value, region=region, parsed=False
                )
            return ProposedAction(
                type=action_type,
                raw_value=raw_value,
                region=region,
                label=label,
                parsed=True,
            )

    return ProposedAction(type="unknown", raw_value=raw_value, region=region, parsed=False)


__all__ = ["parse_action"]
