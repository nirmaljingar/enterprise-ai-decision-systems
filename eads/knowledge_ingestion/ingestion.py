
from ..core.types import Evidence, Signal


class IngestionPipeline:
    """Convert unstructured enterprise signals into grounded evidence.

    Stub: this copies each signal verbatim into one :class:`~eads.core.types.Evidence` claim.
    It performs no semantic extraction, entity resolution, or confidence estimation.
    """

    def ingest(self, signals: list[Signal]) -> list[Evidence]:
        evidence = []
        for signal in signals:
            evidence.append(
                Evidence(
                    # Derived from the signal id so evidence ids are stable across batches
                    # and can be resolved back to their source.
                    id=f"ev_{signal.id}",
                    signal_ids=[signal.id],
                    claim=signal.content,
                    confidence=1.0,
                    source_refs=[signal.id],
                    extracted_by="verbatim_copy_stub",
                )
            )
        return evidence
