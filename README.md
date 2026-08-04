# Enterprise AI Decision Systems (EADS) — Research Companion

[![Tests](https://github.com/nirmaljingar/enterprise-ai-decision-systems/actions/workflows/tests.yml/badge.svg)](https://github.com/nirmaljingar/enterprise-ai-decision-systems/actions/workflows/tests.yml)
[![Docs](https://github.com/nirmaljingar/enterprise-ai-decision-systems/actions/workflows/docs.yml/badge.svg)](https://github.com/nirmaljingar/enterprise-ai-decision-systems/actions/workflows/docs.yml)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](./LICENSE)
[![PyPI](https://img.shields.io/badge/PyPI-v1.0.0-blue.svg)](https://pypi.org/project/enterprise-ai-decision-systems/)
[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nirmaljingar/enterprise-ai-decision-systems/blob/main/notebooks/eads_quickstart.ipynb)

A reproducible, modular Python toolkit for building **reliable, safe, and auditable enterprise AI decisions** with large language models, safety filters, and governance.

**Install and run in 60 seconds:**

```bash
pip install git+https://github.com/nirmaljingar/enterprise-ai-decision-systems.git
python -c "
from eads.core.pipeline import DecisionPipeline
from eads.core.types import DecisionRequest
from eads.decision.decision import DecisionEngine
from eads.governance import GovernanceLayer
from eads.synthetic_data import SupplyChainGenerator

request = DecisionRequest(
    request_id='demo',
    goal='decide replenishment order for SKU-1001',
    signals=SupplyChainGenerator(seed=42).generate(3),
)
record = DecisionPipeline(governance=GovernanceLayer(), decision_engine=DecisionEngine()).run(request)
print('Approved:', record.verdict.approved)
print('Reason:', record.verdict.reason)
print('Trace:', [t['step'] for t in record.trace])
"
```

## Live demo

- **60-second walkthrough:** [`docs/wow_demo.md`](./docs/wow_demo.md)
- **Killer Colab notebook:** [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nirmaljingar/enterprise-ai-decision-systems/blob/main/notebooks/eads_killer_demo.ipynb)
- **Quickstart notebook:** [`notebooks/eads_quickstart.ipynb`](./notebooks/eads_quickstart.ipynb)

## Mission

The central research question this repository addresses is:

> How can enterprise AI systems remain **reliable, safe, and auditable** while delegating decision authority to autonomous LLM agents?

Enterprise AI is moving from deterministic rule engines to autonomous, language-model-powered agents. This transition creates a tension: the same models that can reason over unstructured data, modernize legacy systems, and coordinate multi-agent workflows are also probabilistic, opaque, and error-prone. The four IEEE EADS papers argue that the solution is not raw performance, but the disciplined integration of:

- **Probabilistic language models** for reasoning and planning.
- **Deterministic safety, policy, and optimization layers** for guarantees.
- **Human-visible audit and governance** for trust.

This repository becomes the official open companion to that research: it supplies the code, data, benchmarks, diagrams, and documentation necessary to study, clone, modify, and cite the work.

## The four IEEE papers

| Paper | Identifier | Publication status | Contribution in this repo |
|-------|------------|--------------------|---------------------------|
| Modernizing Legacy Enterprise Platforms Using LLM-Driven Refactoring and AI-Assisted Architecture Transformation | Paper 1 | Unpublished — no verified DOI | `eads.modernization` — legacy parsing, dependency extraction, monolith-to-microservice decomposition |
| Leveraging Large Language Models and Autonomous Agents for Unstructured Supply Chain Intelligence | Paper 2 | Unpublished — no verified DOI | `eads.knowledge_ingestion`, `eads.reasoning`, `eads.agents` — semantic extraction, evidence grounding, multi-agent collaboration |
| Reliable LLM-Powered Decision Engines for Large-Scale Supply Chain Operations: Architecture, Safety, and Performance Guarantees | Paper 3 | Unpublished — no verified DOI | `eads.decision`, `eads.governance.safety` — LLM decision engine, mathematical optimization, safety filtering |
| Operationalizing Generative and Agentic AI Across Complex Logistics Networks: Architecture, Governance, and Trust Models | Paper 4 | Unpublished — no verified DOI | `eads.governance` — policy, permissions, fallback, audit, and trust scoring |

DOIs are deliberately absent: no DOI is listed until it has been checked against the publisher's
record. See [`CITING.md`](./CITING.md) for full citation guidance and [`docs/research_design.md`](./docs/research_design.md) for the complete research design.

## Why this repository matters

- **Open and citable.** Released as a public research artifact under Apache-2.0 with `CITATION.cff`, `CITING.md`, and `LICENSE`.
- **Domain-agnostic.** Supply chain is the primary worked example, but the architecture is reusable for healthcare, finance, IT operations, customer support, and other domains.
- **Reproducible.** All examples use synthetic data, deterministic seeds, and pinned dependencies. The same input, seed, and policy snapshot must produce the same observable trace.
- **Transparent.** Every module, metric, and example either traces to an IEEE paper or is explicitly labeled as a *Reference implementation*, *Educational example*, or *Suggested extension*.
- **Vendor-neutral.** The core implementation uses the Python standard library and `pydantic`. Optional adapters for LLM backends, solvers, and forecasters are isolated so the architecture stays portable.

## Reference architecture

```mermaid
graph LR
    A[Signals / Unstructured Input] --> B[Knowledge Ingestion]
    B --> C[Evidence Graph]
    C --> D[Reasoning & Agents]
    D --> E[Decision Engine]
    E --> F[Governance Layer]
    F -->|Approved| G[Execution]
    F -->|Unsafe / Unauthorized| H[Human Escalation]
    G --> I[Audit Record]
    H --> I
    A --> J[Modernization]
    J --> C
```

The decision lifecycle is: **Sense / Ingest → Modernize / Extract → Reason / Plan → Generate → Govern / Validate → Escalate or Execute → Audit.**

## Module map

| Module | Traced to | Responsibility |
|--------|-----------|--------------|
| `eads.core` | Reference implementation | Shared data model, pipeline contract, and plugin interface |
| `eads.modernization` | Paper 1 | Synthetic legacy-code parsing and modernization |
| `eads.knowledge_ingestion` | Paper 2 | Semantic extraction from unstructured enterprise signals |
| `eads.reasoning` | Papers 2, 3 | Evidence-backed, context-aware reasoning |
| `eads.agents` | Papers 2, 4 | Deterministic multi-agent collaboration primitives |
| `eads.decision` | Paper 3 | LLM + optimization + forecasting + safety filter |
| `eads.governance` | Papers 1, 3, 4 | Policy, safety, permissions, fallback, audit, and trust |
| `eads.evaluation` | Papers 1–4 | Reproducible benchmark harness and metrics |
| `eads.synthetic_data` | All | Domain-agnostic synthetic data generators |
| `examples/` | All | End-to-end educational workflows |
| `docs/` | All | Research design, architecture, tutorials, and limitations |

## Quick start

```bash
# Install the core package and development dependencies
pip install -e ".[dev]"

# Run the end-to-end quickstart with synthetic data (no API key required)
python examples/quickstart.py

# Run the test suite and reproducibility checks
pytest
```

## Installation

```bash
pip install -e .
```

Optional adapters are available as extras and remain isolated from the core:

```bash
pip install -e ".[openai]"     # OpenAI LLM backend
pip install -e ".[anthropic]"  # Anthropic LLM backend
pip install -e ".[solvers]"    # scipy, pulp, ortools, sktime adapters
pip install -e ".[pdf]"       # PyMuPDF paper extraction backend
pip install -e ".[docs]"       # mkdocs-material for building the documentation site
```

## Examples

```bash
python examples/quickstart.py                  # 60-second pipeline demo
python examples/supply_chain.py                # supply-chain replenishment benchmark
python examples/healthcare.py                   # healthcare triage/capacity benchmark
python examples/finance.py                      # finance compliance benchmark
python examples/it_operations.py                # IT incident response benchmark
python examples/customer_support.py             # support ticket prioritization benchmark
```

## Core data objects

The `eads.core.types` module defines the shared data model:

- `Signal` — a raw enterprise input.
- `Evidence` — a structured, source-annotated fact.
- `AgentMessage` — typed agent-to-agent messages.
- `DecisionCandidate` — a proposed action.
- `Verdict` — the result of policy, safety, and permission checks.
- `ExecutionResult` — deterministic tool invocation output.
- `AuditRecord` — an immutable trace of a complete decision cycle.

## Evaluation metrics

The `eads.evaluation` module implements the reproducible metrics from the research design:

| Metric | Paper trace | Status |
|--------|-------------|--------|
| Decision Consistency | Paper 3 | Published methodology |
| Policy Compliance | Papers 3, 4 | Published methodology |
| Evidence Grounding Rate | Paper 2 | Published methodology |
| Fallback Recovery Rate | Papers 3, 4 | Published methodology |
| Audit Completeness | Paper 4 | Published methodology |
| Tool Invocation Precision | Paper 3 | Suggested extension |
| Decision Latency | Paper 3 | Suggested extension |
| Token Efficiency | Papers 1–3 | Suggested extension |

No numerical results or experimental claims are fabricated. Benchmarks live in `benchmarks/` and produce versioned `results.json` files.

## Determinism contract

- The `DecisionPipeline` records a `PipelineState` at every step.
- Re-running with the same `input`, `seed`, `policy_snapshot`, and `tool_versions` produces the same `PipelineState` trace.
- LLM calls are wrapped in a seedable `LLMBackend` adapter that logs prompts, completions, and token usage.
- Any remaining non-determinism is captured as a `DecisionConsistency` metric rather than ignored.

## Citation

Please cite both the originating IEEE papers and this repository. See [`CITATION.cff`](./CITATION.cff) for repository metadata and [`CITING.md`](./CITING.md) for the paper list and BibTeX guidance.

## License

This project is released under the [Apache-2.0 license](./LICENSE).

## Status

This repository is a **v1.0.0 release candidate**. The four IEEE EADS papers are extracted, modules trace to paper concepts, and the full pipeline is implemented and tested (27 passing tests). Remaining work — optional solver/forecaster/live-LLM execution, Zenodo DOI, PyPI release, and deeper numerical reproductions — is documented in [`docs/roadmap.md`](./docs/roadmap.md) and [`docs/limitations.md`](./docs/limitations.md). See [`PUBLICATION.md`](./PUBLICATION.md) for release and citation instructions.
