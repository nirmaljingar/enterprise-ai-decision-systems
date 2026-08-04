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
- The four paper DOIs resolve through Crossref to the titles claimed here, checked by
  `tests/test_citations.py`; the papers themselves are not open access.
- Approvals are routed to a role, and separation of duties is enforced, but no approval is ever
  *granted*: there is no approver interface, credential, or grant record. Escalation is a terminal
  state here.

### Implemented, but lexically and deterministically

Every paper-traced module now implements a method rather than a placeholder, and none of them calls a
language model. The implementations are lexical and rule-based, which buys determinism -- the benchmark
harness replays a run and gets the same answer -- at a cost each module README states in full:

| Module | What it does not do |
|--------|---------------------|
| `eads.knowledge_ingestion` | No coreference, negation scope, temporal normalisation, or entity linking; term overlap is not synonymy |
| `eads.reasoning` | Edges are shared entities and matching figures; no embedding similarity, causal, or temporal inference; cycle detection finds mutually referencing pairs only |
| `eads.modernization` | No refactoring or code generation; the call graph does not resolve aliases or dynamic dispatch; Python only |
| `eads.agents` | Agents do not call a model, negotiate over rounds, or revise a position in response to an argument |
| `eads.governance.trust` | Multipliers are chosen, not fitted, so the score is not a calibrated hallucination probability -- and it authorizes nothing |
| `DecisionEngine` confidence | A fixed constant (`STUB_CONFIDENCE`), not a calibrated probability |

### Capabilities that are documented but absent

- Prompt, completion, and token-usage logging (and therefore token-efficiency metrics).
- Tool-invocation precision and decision-latency metrics.
- Signed or externally persisted audit logs; the `AuditLogger` is in-memory only, and `AuditRecord`
  carries no `signatures` field because no signing mechanism exists to back one.
- A PyPI release. The Zenodo archive exists (concept DOI `10.5281/zenodo.21797859`); see
  [`CITING.md`](https://github.com/nirmaljingar/enterprise-ai-decision-systems/blob/main/CITING.md).

## What this is not

- A drop-in enterprise platform.
- A vendor-specific or closed-source SDK replacement.
- A repository containing proprietary code, APIs, schemas, prompts, datasets, or benchmark artifacts.
