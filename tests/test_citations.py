"""Guard the citation metadata: a DOI that resolves to the wrong paper must fail the suite.

An earlier revision of this repository shipped four DOIs that resolved, through Crossref, to
unrelated papers by other authors. Prose review did not catch it; a resolution check does.
"""

import json
import os
import re
import urllib.error
import urllib.request
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parent.parent
PAPERS = ROOT / "data" / "papers" / "papers.json"
SKIPPED_DIRECTORIES = {".git", ".venv", "site", "__pycache__"}
CROSSREF = "https://api.crossref.org/works/{doi}"
NETWORK_TESTS_ENABLED = os.getenv("EADS_NETWORK_TESTS") == "1"


def _papers() -> list[dict[str, object]]:
    with PAPERS.open() as handle:
        papers: list[dict[str, object]] = json.load(handle)
    return papers


def _normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def _crossref_title(doi: str) -> str:
    request = urllib.request.Request(
        CROSSREF.format(doi=doi),
        headers={"User-Agent": "eads-research-companion (citation verification test)"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        message = json.load(response)["message"]
    titles: list[str] = message["title"]
    return titles[0]


def test_every_paper_declares_a_doi() -> None:
    for paper in _papers():
        assert paper["doi"], f"{paper['id']} has no DOI"
        assert paper["url"] == f"https://doi.org/{paper['doi']}"
        assert paper["status"] == "published"


def _markdown_documents() -> list[Path]:
    return [
        path
        for path in ROOT.rglob("*.md")
        if not SKIPPED_DIRECTORIES & set(path.relative_to(ROOT).parts)
    ]


def _software_dois() -> set[str]:
    """The archive identifiers for this software, declared in CITATION.cff.

    A Zenodo DOI names the code, not a paper, so it has no place in ``papers.json`` -- but it still
    needs a single declared source, or the rule below degrades into "except the ones we allow".
    """
    with (ROOT / "CITATION.cff").open() as handle:
        citation = yaml.safe_load(handle)
    return {
        str(identifier["value"]).lower()
        for identifier in citation.get("identifiers", [])
        if identifier.get("type") == "doi"
    }


def test_papers_json_is_the_only_source_of_dois() -> None:
    """Every DOI written in any prose file must exist in papers.json or CITATION.cff.

    Scoped to two files, this check passed while ``data/papers/README.md`` still listed the four
    superseded DOIs, so it scans every tracked Markdown document instead.
    """
    declared = {str(paper["doi"]).lower() for paper in _papers()} | _software_dois()
    pattern = re.compile(r"10\.\d{4,9}/[\w.()/-]*\w")
    for document in _markdown_documents():
        for found in pattern.findall(document.read_text()):
            assert found.lower() in declared, (
                f"{document.relative_to(ROOT)} cites unknown DOI {found}"
            )


@pytest.mark.skipif(
    not NETWORK_TESTS_ENABLED,
    reason="reaches api.crossref.org; set EADS_NETWORK_TESTS=1 to enable",
)
def test_every_doi_resolves_to_its_title() -> None:
    for paper in _papers():
        doi = str(paper["doi"])
        try:
            resolved = _crossref_title(doi)
        except urllib.error.URLError as error:  # pragma: no cover - network dependent
            pytest.skip(f"Crossref unreachable: {error}")
        assert _normalize(resolved) == _normalize(str(paper["title"])), (
            f"{doi} resolves to {resolved!r}, not {paper['title']!r}"
        )
