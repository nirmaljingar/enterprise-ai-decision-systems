# Limitations

This is an open **research artifact**, not a production enterprise framework. The following limitations are acknowledged from the start.

## Design limitations

- **Abstract-based design.** The current module and metric mapping are derived from public abstracts and the project brief. Final paper-aligned details require Phase 1.5 full-text extraction.
- **Reference implementation.** Code shapes, schemas, and method signatures are *Suggested extension* until the full paper text is parsed.
- **Synthetic data only.** All examples use generated data; no real enterprise data is included.
- **No production hardening.** The repository prioritizes clarity, reproducibility, and traceability over performance, scalability, or security hardening.

## Known gaps

- Real LLM backend adapters are optional; the default `FakeLLM` is deterministic but not a real model.
- Numerical benchmarks are illustrative; rigorous evaluation against the IEEE corpus is ongoing.
- Approvals are routed to a role, and separation of duties is enforced, but no approval is ever
  *granted*: there is no approver interface, credential, or grant record. Escalation is a terminal
  state here.

### Modules that are stubs

These trace to a paper but do not implement the paper's method. Each says so in its docstring:

| Module | What it actually does |
|--------|-----------------------|
| `eads.modernization` | Counts imports and lines to suggest a decomposition; no refactoring or dependency analysis |
| `eads.knowledge_ingestion` | Copies each signal verbatim into one evidence claim with confidence 1.0; no extraction |
| `eads.reasoning` | Emits a fixed plan skeleton over whatever evidence exists |
| `eads.agents` | Message-passing primitives only; no autonomous collaboration or negotiation |
| `eads.governance.trust` | Clamped self-reported confidence, halved for unparseable actions; not a calibrated hallucination measure |
| `DecisionEngine` confidence | A fixed constant (`STUB_CONFIDENCE`), not a calibrated probability |

### Capabilities that are documented but absent

- Prompt, completion, and token-usage logging (and therefore token-efficiency metrics).
- Tool-invocation precision and decision-latency metrics.
- Signed or externally persisted audit logs; the `AuditLogger` is in-memory only, and `AuditRecord`
  carries no `signatures` field because no signing mechanism exists to back one.
- A PyPI release and a Zenodo DOI.

## What this is not

- A drop-in enterprise platform.
- A vendor-specific or closed-source SDK replacement.
- A repository containing proprietary code, APIs, schemas, prompts, datasets, or benchmark artifacts.
