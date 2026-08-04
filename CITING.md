# Citing this work

This repository is an open research companion to the following four EADS papers:

1. N. K. Jingar, "Modernizing Legacy Enterprise Platforms Using LLM-Driven Refactoring and
   AI-Assisted Architecture Transformation," in *2026 3rd International Conference on Research
   Methodologies in Knowledge Management, Artificial Intelligence and Telecommunication
   Engineering (RMKMATE)*, IEEE, 2026, pp. 1-6, doi: 10.1109/rmkmate69073.2026.11518954.
2. N. K. Jingar, "Leveraging Large Language Models and Autonomous Agents for Unstructured Supply
   Chain Intelligence," in *2026 ASU International Conference in Emerging Technologies for
   Sustainability and Intelligent Systems (ICETSIS)*, IEEE, 2026, pp. 1467-1472,
   doi: 10.1109/icetsis68266.2026.11548779.
3. N. K. Jingar, "Reliable LLM-Powered Decision Engines for Large-Scale Supply Chain Operations:
   Architecture, Safety, and Performance Guarantees," in *2026 IEEE International Conference on
   Advanced Systems and Emergent Technologies (IC_ASET)*, IEEE, 2026, pp. 1-6,
   doi: 10.1109/IC_ASET69920.2026.11502212.
4. N. K. Jingar, "Operationalizing Generative and Agentic AI Across Complex Logistics Networks:
   Architecture, Governance, and Trust Models," in *2026 ASU International Conference in Emerging
   Technologies for Sustainability and Intelligent Systems (ICETSIS)*, IEEE, 2026, pp. 1460-1466,
   doi: 10.1109/icetsis68266.2026.11549394.

## Publication status

All four DOIs above are verified: each resolves through Crossref to the title and venue listed
here. `data/papers/papers.json` is the single source of truth, and
`tests/test_citations.py::test_every_doi_resolves_to_its_title` re-checks every entry against
`https://api.crossref.org/works/<doi>` so a wrong identifier fails the test suite rather than
reaching a reader.

An earlier revision of this repository listed four DOIs that resolved to unrelated papers by other
authors. That is why the check exists, and why the test also asserts that no DOI appears in prose
without appearing in `papers.json`: add or change an identifier there, never in prose alone.

## Citing the software

The v2.0.0 release is archived on Zenodo, so a specific state of this code is citable on its own:

- **Concept DOI — [10.5281/zenodo.21797859](https://doi.org/10.5281/zenodo.21797859).** Resolves to
  the latest version. Cite this when you mean "this software".
- **Version DOI — [10.5281/zenodo.21797860](https://doi.org/10.5281/zenodo.21797860).** Resolves to
  v2.0.0 exactly. Cite this when a result depends on the code that produced it -- a benchmark number
  reported against a moving target cannot be reproduced.

Both are declared in `CITATION.cff`, which GitHub's *Cite this repository* reads.
