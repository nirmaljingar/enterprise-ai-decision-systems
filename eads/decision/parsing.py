"""Parse free-form model output into a typed, checkable action.

The governance layer evaluates :class:`~eads.core.types.ProposedAction` fields, never raw
model text. Parsing therefore happens exactly once, here, at the boundary between the
probabilistic model and the deterministic checks.
"""

import re

from ..core.types import ProposedAction

_QUANTITY = re.compile(r"(?:order_)?quantity\s*[=:]\s*(\d+)", re.IGNORECASE)
_REGION = re.compile(r"region\s*[=:]\s*([A-Za-z][\w-]*)", re.IGNORECASE)
_LABELLED = {
    "route": re.compile(r"route\s*[=:]\s*([\w-]+)", re.IGNORECASE),
    "mitigation": re.compile(r"mitigation\s*[=:]\s*([\w-]+)", re.IGNORECASE),
    "decision": re.compile(r"decision\s*[=:]\s*([\w-]+)", re.IGNORECASE),
}


def parse_action(raw_value: str, region_default: str | None = None) -> ProposedAction:
    """Parse one model completion into a :class:`ProposedAction`.

    ``parsed`` is ``True`` only when the completion matched a known action grammar. Callers
    must treat ``parsed is False`` as "not checkable", and the governance layer rejects such
    actions rather than letting them through unchecked.
    """
    region_match = _REGION.search(raw_value)
    region = region_match.group(1).upper() if region_match else region_default

    quantity_match = _QUANTITY.search(raw_value)
    if quantity_match:
        return ProposedAction(
            type="order",
            raw_value=raw_value,
            quantity=int(quantity_match.group(1)),
            region=region,
            parsed=True,
        )

    for action_type, pattern in _LABELLED.items():
        match = pattern.search(raw_value)
        if match:
            return ProposedAction(
                type=action_type,
                raw_value=raw_value,
                region=region,
                label=match.group(1),
                parsed=True,
            )

    return ProposedAction(type="unknown", raw_value=raw_value, region=region, parsed=False)


__all__ = ["parse_action"]
