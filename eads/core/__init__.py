"""Core types, adapters, and the decision pipeline.

``DecisionPipeline`` is exported lazily. It imports the decision, governance, reasoning, and
ingestion packages, each of which imports back into this one, so binding it at module scope made
``eads.core`` a required first import: ``from eads.governance import GovernanceLayer`` in a fresh
interpreter raised ``ImportError`` on a partially initialized module. Deferring the import means the
cycle is resolved by whichever package is entered first, in any order.
"""

from typing import TYPE_CHECKING, Any

from .adapters import AnthropicLLM, FakeLLM, LLMBackend, OllamaLLM, OpenAILLM
from .types import (
    AgentMessage,
    AuditRecord,
    DecisionCandidate,
    DecisionRequest,
    Evidence,
    ExecutionResult,
    Plan,
    ProposedAction,
    Signal,
    Verdict,
)

if TYPE_CHECKING:
    from .pipeline import DecisionPipeline


def __getattr__(name: str) -> Any:
    if name == "DecisionPipeline":
        from .pipeline import DecisionPipeline

        return DecisionPipeline
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "AgentMessage",
    "AnthropicLLM",
    "AuditRecord",
    "DecisionCandidate",
    "DecisionPipeline",
    "DecisionRequest",
    "Evidence",
    "ExecutionResult",
    "FakeLLM",
    "LLMBackend",
    "OllamaLLM",
    "OpenAILLM",
    "Plan",
    "ProposedAction",
    "Signal",
    "Verdict",
]
