# EADS Source Papers

This directory contains a **public, shareable bibliographic index** for the four EADS source papers in `papers.json`. The repository does **not** redistribute the full-text PDFs or extracted full-text copies.

## Public index

- `papers.json` — title, authors, DOI, public URL, venue, year, and module alignment for each paper.

## Local full-text extraction (optional)

If you have your own licensed copies of the PDFs, place them here for local Phase 1.5 extraction:

1. `paper1_lraatf_modernizing_legacy.pdf` — *Modernizing Legacy Enterprise Platforms Using LLM-Driven Refactoring and AI-Assisted Architecture Transformation* (DOI `10.1109/TTS.2024.3403681`)
2. `paper2_lasci_leveraging_llm_agents.pdf` — *Leveraging Large Language Models and Autonomous Agents for Unstructured Supply Chain Intelligence* (DOI `10.1109/ACCESS.2025.3605837`)
3. `paper3_llm_de_reliable_decision_engines.pdf` — *Reliable LLM-Powered Decision Engines for Large-Scale Supply Chain Operations: Architecture, Safety, and Performance Guarantees* (DOI `10.1109/TEM.2025.3567302`)
4. `paper4_agaf_operationalizing_generative_ai.pdf` — *Operationalizing Generative and Agentic AI Across Complex Logistics Networks: Architecture, Governance, and Trust Models* (DOI `10.1109/ACCESS.2025.3585783`)

Install the optional PDF dependency and run extraction:

```bash
pip install -e ".[pdf]"
python scripts/extract_papers.py --input-dir data/papers --output-dir data/papers/extracted
```

Generated `.txt` and `.json` extractions are written to `data/papers/extracted/` and are **gitignored** so they are never committed to the public repository.

