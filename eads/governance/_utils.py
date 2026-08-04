"""Shared parsing helpers for the governance layer."""

import re


def parse_quantity(value: str) -> int | None:
    """Extract an integer quantity from a decision action value if present.

    Supports strings of the form ``order_quantity=123`` or ``order_quantity=123-...``.
    Returns ``None`` when no quantity can be parsed.
    """
    match = re.search(r"order_quantity=(\d+)", value)
    if match:
        return int(match.group(1))
    return None
