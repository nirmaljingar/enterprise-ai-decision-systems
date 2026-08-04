# Limitations

This is an open **research artifact**, not a production enterprise framework. The following limitations are acknowledged from the start.

## Design limitations

- **Abstract-based design.** The current module and metric mapping are derived from public abstracts and the project brief. Final paper-aligned details require Phase 1.5 full-text extraction.
- **Reference implementation.** Code shapes, schemas, and method signatures are *Suggested extension* until the full paper text is parsed.
- **Synthetic data only.** All examples use generated data; no real enterprise data is included.
- **No production hardening.** The repository prioritizes clarity, reproducibility, and traceability over performance, scalability, or security hardening.

## Known gaps

- Most `eads.*` modules are reference scaffolding; the full paper-aligned implementations are a work in progress.
- Real LLM backend adapters are optional; the default `FakeLLM` is deterministic but not a real model.
- Numerical benchmarks are illustrative; rigorous evaluation against the IEEE corpus is ongoing.

## What this is not

- A drop-in enterprise platform.
- A vendor-specific or closed-source SDK replacement.
- A repository containing proprietary code, APIs, schemas, prompts, datasets, or benchmark artifacts.
