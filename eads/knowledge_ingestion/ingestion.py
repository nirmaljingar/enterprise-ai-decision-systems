
from ..core.types import Evidence, Signal


class IngestionPipeline:
    """Convert unstructured enterprise signals into grounded evidence."""

    def ingest(self, signals: list[Signal]) -> list[Evidence]:
        evidence = []
        for i, signal in enumerate(signals):
            evidence.append(
                Evidence(
                    id=f"ev_{i}",
                    signal_ids=[signal.id],
                    claim=signal.content,
                    confidence=1.0,
                    source_refs=[signal.id],
                    extracted_by="synthetic_regex_stub",
                )
            )
        return evidence
