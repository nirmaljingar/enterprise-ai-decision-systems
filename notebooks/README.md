# EADS Notebooks

This directory contains interactive examples for Google Colab and local Jupyter environments.

## Quickstart

Open the quickstart notebook in Colab:

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nirmaljingar/enterprise-ai-decision-systems/blob/main/notebooks/eads_quickstart.ipynb)

## Notebooks

- `eads_killer_demo.ipynb` — full end-to-end pipeline + benchmark (best Colab demo).
- `eads_quickstart.ipynb` — one-minute decision pipeline demo using synthetic supply-chain signals.

## Running locally

```bash
pip install -e ".[dev]"
jupyter notebook notebooks/eads_quickstart.ipynb
```
