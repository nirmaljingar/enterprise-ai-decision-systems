# Frequently Asked Questions

## Why is this repository important?

It is the open, reproducible research companion to four IEEE EADS papers. It provides code, data, benchmarks, diagrams, and documentation for studying how enterprise AI can remain reliable and auditable when delegating decisions to LLM agents.

## Is this production-ready software?

No. It is a research artifact designed for study, cloning, modification, benchmarking, extension, and citation.

## Can I use this for my own domain?

Yes. The architecture is domain-agnostic. Supply chain is the primary example, but the same lifecycle applies to healthcare, finance, IT operations, and customer support. See `examples/` for planned domain walkthroughs.

## Where are the real algorithms from the papers?

The current design is based on public abstracts. Phase 1.5 requires full-text PDF extraction to finalize exact algorithms and numerical claims. See `docs/research_design.md` and `docs/limitations.md`.

## Do I need an LLM API key?

No. The default `FakeLLM` and synthetic data let every example run without API keys. Optional adapters for OpenAI, Anthropic, Ollama, and local transformers are available as package extras.

## How do I cite this work?

See `CITING.md` and `CITATION.cff`.
