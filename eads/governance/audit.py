from dataclasses import asdict
from typing import Any

from ..core.types import AuditRecord


class AuditLogger:
    """Immutable, append-only decision trace log."""

    def __init__(self) -> None:
        self.records: list[dict[str, Any]] = []

    def log(self, record: AuditRecord) -> dict[str, Any]:
        entry = asdict(record)
        self.records.append(entry)
        return entry
