# `eads.core`

**Trace:** Reference implementation.

Shared data model, deterministic pipeline contract, and public plugin interface for the EADS research companion.

- `eads.core.types` — dataclasses for `Signal`, `Evidence`, `Plan`, `DecisionCandidate`, `Verdict`, `ExecutionResult`, `AuditRecord`, and `DecisionRequest`.
- `eads.core.pipeline` — `DecisionPipeline` orchestrating ingest → reason → generate → govern → execute → audit.
- `eads.core.adapters` — `LLMBackend` interface plus deterministic `FakeLLM` and optional real-LLM adapters.

Status: runnable skeleton; deeper deterministic-state guarantees and plugin hooks are still being hardened.
