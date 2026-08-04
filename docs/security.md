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

- Every decision cycle produces an `AuditRecord`, appended to the governance `AuditLogger`. The log
  is in-memory and append-only by construction; it is **not** signed or tamper-proof, and
  `AuditRecord` deliberately carries no `signatures` field: a security-shaped field with no key
  management, canonical serialization, or verification step is worse than its absence, because
  readers assume the property it implies. Tamper-evidence is listed as an open item in
  [`docs/limitations.md`](limitations.md).
- Each record carries the `policy_snapshot_id` it was judged under and the `actor` it was requested
  for, so a past decision can be attributed and replayed against the same policy.
- Re-running with the same input, seed, policy snapshot, and a fixed clock
  (`eads.core.clock.FixedClock`) produces an identical record. Backends that cannot honor a seed
  report `supports_seed = False`, and the pipeline records that on the trace.
- Any remaining non-determinism is measured by `decision_consistency` over repeated runs.
- Governance fails closed: model output that cannot be parsed into a checkable action is rejected,
  never approved by default.
