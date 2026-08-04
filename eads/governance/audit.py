from dataclasses import asdict
from typing import Any

from ..core.types import AuditRecord


class AuditLogger:
    """Append-only decision trace log.

    Each record is stored as a detached ``dict`` snapshot, so later mutation of the
    :class:`~eads.core.types.AuditRecord` cannot rewrite history. The log is in-memory and
    append-only by construction; it is not tamper-proof and does not sign entries.
    """

    def __init__(self) -> None:
        self._records: list[dict[str, Any]] = []

    @property
    def records(self) -> list[dict[str, Any]]:
        """Logged entries, oldest first (a shallow copy of the internal list)."""
        return list(self._records)

    def log(self, record: AuditRecord) -> dict[str, Any]:
        entry = asdict(record)
        self._records.append(entry)
        return entry
