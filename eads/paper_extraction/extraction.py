"""IEEE paper PDF text extraction for Phase 1.5 of the EADS research design."""

import json
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class ExtractedPaper:
    """Container for text extracted from one IEEE PDF."""

    path: str
    title: str = ""
    authors: list[str] = field(default_factory=list)
    doi: str = ""
    abstract: str = ""
    full_text: str = ""
    sections: dict[str, str] = field(default_factory=dict)
    references: list[str] = field(default_factory=list)
    algorithms: list[str] = field(default_factory=list)
    metrics: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "title": self.title,
            "authors": self.authors,
            "doi": self.doi,
            "abstract": self.abstract,
            "sections": self.sections,
            "references": self.references,
            "algorithms": self.algorithms,
            "metrics": self.metrics,
        }


class PDFBackend(ABC):
    """Pluggable backend for extracting text from a PDF file."""

    @abstractmethod
    def extract(self, path: Path) -> str:
        ...


class PyMuPDFBackend(PDFBackend):
    """PyMuPDF / fitz extraction backend."""

    def __init__(self) -> None:
        try:
            import fitz
        except ImportError as exc:
            raise ImportError(
                "PDF extra not installed. Run `pip install -e '.[pdf]'`."
            ) from exc
        self._fitz = fitz

    def extract(self, path: Path) -> str:
        doc = self._fitz.open(path)
        pages = [page.get_text() for page in doc]
        return "\n".join(pages)


class PaperExtractor:
    """Extract and lightly structure text from IEEE EADS PDFs."""

    def __init__(self, backend: PDFBackend | None = None) -> None:
        self._backend = backend

    def extract(self, pdf_path: Path) -> ExtractedPaper:
        backend = self._backend or PyMuPDFBackend()
        raw_text = backend.extract(pdf_path)
        return self._structure(pdf_path, raw_text)

    def _structure(self, pdf_path: Path, text: str) -> ExtractedPaper:
        paper = ExtractedPaper(path=str(pdf_path), full_text=text)
        paper.doi = self._extract_doi(text)
        paper.title = self._extract_title(text)
        paper.authors = self._extract_authors(text)
        paper.abstract = self._extract_abstract(text)
        paper.sections = self._extract_sections(text)
        paper.references = self._extract_references(text)
        paper.algorithms = self._extract_algorithm_mentions(text)
        paper.metrics = self._extract_metric_mentions(text)
        return paper

    @staticmethod
    def _extract_doi(text: str) -> str:
        match = re.search(r"10\.\d{4,}/[\w.\-/]+", text)
        return match.group(0) if match else ""

    @staticmethod
    def _extract_title(text: str) -> str:
        # First non-empty, non-header line is a reasonable heuristic for the title.
        for line in text.splitlines():
            stripped = line.strip()
            if stripped and len(stripped) > 10:
                return stripped
        return ""

    @staticmethod
    def _extract_authors(text: str) -> list[str]:
        # Very crude heuristic: look for blocks containing e-mail addresses or institution markers.
        authors = []
        for line in text.splitlines():
            if "@" in line and any(domain in line.lower() for domain in [".edu", ".org", ".com"]):
                # Treat preceding token as a name if it looks like a name (no numbers).
                possible = line.split("@")[0].strip().split(",")[-1].strip()
                if possible and not re.search(r"\d", possible):
                    authors.append(possible)
        return authors

    @staticmethod
    def _extract_abstract(text: str) -> str:
        match = re.search(
            r"Abstract[\s:—-]+(.*?)(?:\n\s*I\.\s+[A-Z]|\n\s*1\s+[A-Z]|\n\s*Introduction|\n\s*Keywords)",
            text,
            re.DOTALL | re.IGNORECASE,
        )
        return match.group(1).strip() if match else ""

    @staticmethod
    def _extract_sections(text: str) -> dict[str, str]:
        sections = {}
        # Match numbered or titled section headers (I. INTRO, 1. Introduction, etc.).
        pattern = re.compile(r"(?:^|\n)\s*(?:I{1,3}V?|\d+)\s*[.\s]+([A-Z][A-Z\s\-]{3,})\s*\n", re.IGNORECASE)
        matches = list(pattern.finditer(text))
        for i, match in enumerate(matches):
            start = match.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            title = match.group(1).strip()
            body = text[start:end].strip()
            sections[title] = body
        return sections

    @staticmethod
    def _extract_references(text: str) -> list[str]:
        refs = []
        match = re.search(r"References\s*\n(.*?)(?:\n\s*\n|$)", text, re.DOTALL | re.IGNORECASE)
        if match:
            refs = [r.strip() for r in re.split(r"\[\d+\]", match.group(1)) if r.strip()]
        return refs

    @staticmethod
    def _extract_algorithm_mentions(text: str) -> list[str]:
        return re.findall(r"Algorithm\s*\d+[.:]?\s*([A-Z][A-Za-z\s\-]{2,})", text)

    @staticmethod
    def _extract_metric_mentions(text: str) -> list[str]:
        candidates = [
            "accuracy",
            "precision",
            "recall",
            "f1",
            "latency",
            "throughput",
            "consistency",
            "compliance",
            "grounding",
            "recovery",
        ]
        found = []
        lower = text.lower()
        for term in candidates:
            if term in lower:
                found.append(term)
        return found


def extract_papers_from_directory(
    input_dir: Path,
    output_dir: Path | None = None,
) -> list[ExtractedPaper]:
    """Extract every PDF in *input_dir* and optionally write JSON/TXT outputs."""
    input_dir = Path(input_dir)
    output_dir = Path(output_dir) if output_dir else None
    if output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)

    extractor = PaperExtractor()
    papers: list[ExtractedPaper] = []
    for pdf_path in sorted(input_dir.glob("*.pdf")):
        paper = extractor.extract(pdf_path)
        papers.append(paper)
        if output_dir:
            base = output_dir / pdf_path.stem
            base.with_suffix(".txt").write_text(paper.full_text, encoding="utf-8")
            base.with_suffix(".json").write_text(
                json.dumps(paper.to_dict(), indent=2, default=str),
                encoding="utf-8",
            )
    return papers


def find_paper_by_doi(doi: str, papers: list[ExtractedPaper]) -> ExtractedPaper | None:
    """Return the extracted paper whose DOI matches the requested string."""
    target = doi.lower().strip()
    for paper in papers:
        if paper.doi.lower().strip() == target:
            return paper
    return None
