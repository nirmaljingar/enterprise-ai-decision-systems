# Roadmap

Current state: every module that traces to a paper implements a method rather than a placeholder,
and the repository is released as v2.0.0 and archived on Zenodo. What each implementation cannot do
is stated per module in [Limitations](limitations.md); this page is only about what comes next.

## Done

- Phase 1 research design ([`research_design.md`](research_design.md)) and Phase 2 repository design.
- Typed data model, `DecisionPipeline`, and injectable clocks for reproducible runs.
- Governance: policy, safety, permissions, fallback, audit, and trust, checking typed fields and
  failing closed on anything it cannot parse.
- Knowledge ingestion, reasoning, agents, modernization, and the synthetic generators.
- Benchmark harness, manifests, and a generated results page gated against staleness.
- Per-module `README.md` files, tests, and the four CI workflows (`tests`, `lint`, `typecheck`,
  `docs`).
- Release v2.0.0 with a Zenodo concept DOI (`10.5281/zenodo.21797859`).

## Not done, and why it matters

1. **Full paper text extraction (Phase 1.5).** The design derives from the papers' abstracts.
   `eads.paper_extraction` can parse locally licensed PDFs, but no extracted corpus ships and no
   statement here is traceable to full paper text.
2. **A benchmark other systems can be scored against.** Today the manifests measure this
   implementation. An adapter interface would let a reader score their own guard and report a
   comparable number, which is the difference between a demo and a baseline.
3. **Metrics that need instrumentation the pipeline does not have**: tool-invocation precision,
   decision latency, and token efficiency. Each is listed as *No* in
   [Evaluation](evaluation.md) rather than estimated.
4. **Tamper-evident audit.** `AuditLogger` is in-memory and unsigned; signing needs key management
   and canonical serialization, neither of which exists here.
5. **Model-backed implementations.** Every paper-traced module is lexical and rule-based, which is
   what makes a benchmark run replayable. Anything model-backed would need the determinism contract
   restated first.
