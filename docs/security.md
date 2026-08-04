# Security

The EADS research companion is designed for synthetic, offline research. Follow these guidelines when running, extending, or deploying any of the code.

## No proprietary data

Never add real enterprise data, credentials, schemas, prompts, or benchmark artifacts to the repository. All demonstrations must use synthetic data.

## API keys and third-party services

- API keys for optional LLM adapters must not be hard-coded or committed.
- Use environment variables or a local secrets manager if running real backends.
- The default examples run with the `FakeLLM` backend and do not make external network calls.

## Dependency hygiene

- Core dependencies are intentionally minimal.
- Optional adapters are isolated under `[project.optional-dependencies]` in `pyproject.toml`.
- Review dependency updates quarterly; pin major versions.

## Auditing and reproducibility

- Every decision cycle produces an `AuditRecord`.
- Re-running with the same input, seed, and policy snapshot must produce the same observable trace.
- Any remaining non-determinism is captured as a `DecisionConsistency` metric.
