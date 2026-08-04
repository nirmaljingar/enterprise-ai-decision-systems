"""Enforce that release metadata agrees with itself.

Version numbers here live in four places, and the 1.0.0 release drifted: the changelog described a
state the code was not in. A citation is only useful if the version it names means one thing, so the
agreement is a test rather than a checklist item.
"""

import re
import tomllib
from pathlib import Path

import eads

ROOT = Path(__file__).resolve().parent.parent
CHANGELOG = ROOT / "CHANGELOG.md"
CITATION = ROOT / "CITATION.cff"
PYPROJECT = ROOT / "pyproject.toml"
SEMANTIC_VERSION = re.compile(r"^\d+\.\d+\.\d+$")


def packaged_version() -> str:
    with PYPROJECT.open("rb") as handle:
        project: dict[str, dict[str, str]] = tomllib.load(handle)
    return project["project"]["version"]


def changelog_versions() -> list[str]:
    return re.findall(r"^## \[(\d+\.\d+\.\d+)\]", CHANGELOG.read_text(), re.MULTILINE)


def test_the_declared_version_is_semantic() -> None:
    assert SEMANTIC_VERSION.match(packaged_version())


def test_every_file_that_states_a_version_states_the_same_one() -> None:
    version = packaged_version()
    assert eads.__version__ == version
    assert f"version: {version}" in CITATION.read_text()
    assert changelog_versions()[0] == version


def test_the_newest_changelog_entry_describes_something() -> None:
    """An empty entry is worse than none: it implies the release was reviewed."""
    body = CHANGELOG.read_text().split("## [", 2)[1]
    assert len(body.strip().splitlines()) > 3


def test_changelog_versions_descend() -> None:
    parsed = [tuple(int(part) for part in entry.split(".")) for entry in changelog_versions()]
    assert parsed == sorted(parsed, reverse=True)


def test_no_zenodo_doi_is_claimed_before_one_exists() -> None:
    """The repository has claimed identifiers it did not have. Not again, and not for the software."""
    citation = CITATION.read_text()
    if "zenodo" in citation.lower():
        assert "identifiers:" in citation, (
            "CITATION.cff mentions Zenodo without declaring the DOI it refers to"
        )
