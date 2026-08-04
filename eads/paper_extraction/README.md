# `eads.paper_extraction`

**Trace:** Reference implementation (Phase 1.5 tooling).

Extracts title, authors, DOI, abstract, sections, references, algorithm blocks, and metric mentions
from a locally licensed IEEE PDF, so a reader who owns the papers can align this repository's module
and metric mapping against their full text.

- `eads.paper_extraction.extraction.PaperExtractor` — parses one PDF into an `ExtractedPaper`.
- `eads.paper_extraction.extraction.PDFBackend` — pluggable text backend; `PyMuPDFBackend` is the
  default and imports `fitz` lazily, so the module is importable without the `[pdf]` extra.
- `extract_papers_from_directory` / `find_paper_by_doi` — batch helpers over a directory of PDFs.

## Status

**Tooling only. It has never been run against the four EADS papers in this repository.** No extracted
corpus ships here, `data/papers/extracted/` is gitignored, and no claim anywhere in this repository
is traceable to full paper text — the module and metric mapping derive from the public abstracts and
the project brief. `data/papers/papers.json` is a bibliographic index, not an extraction output.

The repository does not redistribute the PDFs. To run it against your own licensed copies:

```bash
pip install -e ".[pdf]"
python scripts/extract_papers.py --input-dir data/papers --output-dir data/papers/extracted
```

Section, algorithm, and metric detection is heuristic (heading and keyword patterns), so treat its
output as a reading aid rather than a faithful structural parse.
