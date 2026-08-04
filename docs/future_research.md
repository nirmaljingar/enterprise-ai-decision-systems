# Future Research

This repository is intentionally designed for extension. Below are natural next steps aligned with the EADS research direction.

## Immediate extensions

- **Full-text paper extraction (Phase 1.5):** parse the four provided PDFs to finalize exact algorithms, evaluation protocols, and numerical claims.
- **Additional domains:** implement healthcare triage, finance compliance, IT incident response, and customer support escalation examples.
- **Real LLM adapters:** validate `FakeLLM` outputs against open and closed LLM backends, measuring `DecisionConsistency` and `TokenEfficiency`.
- **Solver and forecaster adapters:** connect `eads.decision` to `scipy`, `pulp`, `ortools`, and `sktime`.

## Longer-term research questions

- How can this architecture be certified or formally audited for high-stakes enterprise use?
- What is the minimum set of governance layers needed for safe delegation in a given domain?
- How can human-in-the-loop escalation be optimized without losing throughput?

## Contributing

See `CONTRIBUTING.md` and `docs/roadmap.md` for how to add a module, example, or benchmark.
