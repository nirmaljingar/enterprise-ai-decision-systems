"""Notebooks are the first thing a reader runs, and nothing was checking that they still work.

Both notebooks were written against the pre-2.0 API and had been broken since typed actions landed:
they printed ``record.verdict.approved``, a field that no longer exists. A broken notebook behind a
Colab badge is worse than no notebook, because the reader concludes the project does not run.

These tests execute every code cell in order, in one namespace, exactly as a reader would -- without
nbclient or a Jupyter kernel, so the check costs nothing and runs in the default suite.
"""

import json
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parent.parent
NOTEBOOKS = sorted((ROOT / "notebooks").glob("*.ipynb"))


def _code_cells(path: Path) -> list[str]:
    cells = json.loads(path.read_text())["cells"]
    return [
        "".join(cell["source"])
        for cell in cells
        if cell["cell_type"] == "code"
    ]


def _is_magic(source: str) -> bool:
    """Install cells are for Colab; the test environment already has the package."""
    return all(
        not line.strip() or line.lstrip().startswith(("%", "!"))
        for line in source.splitlines()
    )


def test_notebooks_exist() -> None:
    assert NOTEBOOKS, "no notebooks found; the Colab badges point at nothing"


@pytest.mark.parametrize("path", NOTEBOOKS, ids=lambda path: path.stem)
def test_notebook_runs(path: Path, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.chdir(ROOT)  # cells reference repository-relative paths
    namespace: dict[str, Any] = {"__name__": "__notebook__"}
    for index, source in enumerate(_code_cells(path)):
        if _is_magic(source):
            continue
        try:
            # S102: running the cell is the assertion. The source is committed to this repository.
            exec(compile(source, f"{path.name}#cell{index}", "exec"), namespace)  # noqa: S102
        except Exception as error:  # noqa: BLE001 - the failure is the result being reported
            pytest.fail(f"{path.name} cell {index} raised {type(error).__name__}: {error}")


@pytest.mark.parametrize("path", NOTEBOOKS, ids=lambda path: path.stem)
def test_notebook_installs_from_the_public_url(path: Path) -> None:
    """The install cell is the one line a Colab reader cannot fix for themselves."""
    sources = _code_cells(path)
    assert any(
        "pip install" in source and "enterprise-ai-decision-systems" in source
        for source in sources
    ), f"{path.name} has no install cell, so it cannot run in Colab"


@pytest.mark.parametrize("path", NOTEBOOKS, ids=lambda path: path.stem)
def test_notebook_has_no_stored_output(path: Path) -> None:
    """Stored output is a claim about behaviour that nothing regenerates."""
    for cell in json.loads(path.read_text())["cells"]:
        if cell["cell_type"] == "code":
            assert not cell.get("outputs"), f"{path.name} ships stored output"
