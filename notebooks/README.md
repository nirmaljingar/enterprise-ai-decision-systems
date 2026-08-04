# EADS Notebooks

This directory contains interactive examples for Google Colab and local Jupyter environments.

## Quickstart

Open the quickstart notebook in Colab:

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nirmaljingar/enterprise-ai-decision-systems/blob/main/notebooks/eads_quickstart.ipynb)

## Notebooks

- `eads_killer_demo.ipynb` — an agent is talked into a 50,000-unit order; the naive guard approves
  it and this one rejects it, on the same compromised model. Ends on the measured number and what it
  does not mean.
- `eads_quickstart.ipynb` — one decision end to end, from synthetic signals to an audited verdict.

`tests/test_notebooks.py` executes every code cell, so a notebook cannot silently rot against an API
change — which is what had happened to both of these.

## Running locally

```bash
pip install -e ".[dev]"
jupyter notebook notebooks/eads_quickstart.ipynb
```
