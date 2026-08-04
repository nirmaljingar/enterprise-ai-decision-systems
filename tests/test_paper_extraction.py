import tempfile
from pathlib import Path

from eads.paper_extraction import (
    PaperExtractor,
    extract_papers_from_directory,
    find_paper_by_doi,
)


def test_paper_extractor_default_backend_is_lazy():
    extractor = PaperExtractor()
    assert extractor._backend is None


def test_extract_papers_from_empty_directory():
    with tempfile.TemporaryDirectory() as tmpdir:
        papers = extract_papers_from_directory(Path(tmpdir))
        assert papers == []


def test_find_paper_by_doi_returns_none_for_empty_list():
    assert find_paper_by_doi("10.0/0", []) is None
