"""Injectable clocks so decision traces can be byte-reproducible."""

from collections.abc import Callable
from datetime import UTC, datetime

Clock = Callable[[], str]


def system_clock() -> str:
    """Return the current UTC time as an ISO-8601 string."""
    return datetime.now(UTC).isoformat()


class FixedClock:
    """Clock that always returns the same timestamp.

    Use in tests and benchmarks so that two runs of an identical request
    produce identical :class:`~eads.core.types.AuditRecord` values.
    """

    def __init__(self, timestamp: str = "1970-01-01T00:00:00+00:00") -> None:
        self.timestamp = timestamp

    def __call__(self) -> str:
        return self.timestamp


__all__ = ["Clock", "FixedClock", "system_clock"]
