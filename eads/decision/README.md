# `eads.decision`

**Trace:** Paper 3 — reliable LLM-powered decision engines.

Combines semantic reasoning with optional solver and forecaster adapters to generate `DecisionCandidate` objects.

- `eads.decision.decision.DecisionEngine` — wraps an `LLMBackend` and accepts an optional `Plan` to carry evidence references through the pipeline.

Status: runnable skeleton; solver/forecaster adapters and safety-filter integration are planned extensions.
