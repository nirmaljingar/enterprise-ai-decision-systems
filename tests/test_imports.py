"""Every public subpackage must import on its own, in a fresh interpreter.

``eads.core`` imports the pipeline, which imports the decision, governance, reasoning, and ingestion
packages, each of which imports back into ``eads.core``. Entering through ``eads.core`` warms that
cycle in an order that happens to work, so the whole suite passed while
``from eads.governance import GovernanceLayer`` raised ``ImportError`` in a new process.

A test in this suite cannot see that: the first import wins for the rest of the session. Hence the
subprocess.
"""

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent

PUBLIC_SUBPACKAGES = [
    "eads",
    "eads.agents",
    "eads.core",
    "eads.decision",
    "eads.evaluation",
    "eads.governance",
    "eads.knowledge_ingestion",
    "eads.modernization",
    "eads.reasoning",
    "eads.synthetic_data",
]


@pytest.mark.parametrize("module", PUBLIC_SUBPACKAGES)
def test_the_subpackage_imports_without_importing_anything_else_first(module: str) -> None:
    completed = subprocess.run(
        [sys.executable, "-c", f"import {module}"],
        capture_output=True,
        check=False,
        cwd=ROOT,
        text=True,
    )
    assert completed.returncode == 0, completed.stderr


def test_the_pipeline_is_still_reachable_from_the_core_namespace() -> None:
    """Deferring the import must not quietly remove the export it defers."""
    import eads.core

    assert eads.core.DecisionPipeline.__name__ == "DecisionPipeline"
    assert "DecisionPipeline" in eads.core.__all__


def test_an_unknown_core_attribute_still_raises_attribute_error() -> None:
    """A module ``__getattr__`` that returns None for typos is worse than no export at all."""
    import eads.core

    with pytest.raises(AttributeError):
        getattr(eads.core, "NoSuchThing")  # noqa: B009  -- the lookup is the assertion
