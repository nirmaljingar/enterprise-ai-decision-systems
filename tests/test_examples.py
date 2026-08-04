"""Run every example script, because the research design requires it on every commit.

Section 17.1 asks that every example execute in CI. Linting them is not the same thing: an example
can lint cleanly and still raise on the first line, and examples are the first thing a reader runs.
Each script must exit zero using only synthetic data and no API keys.
"""

import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
EXAMPLES = sorted(path.name for path in (ROOT / "examples").glob("*.py"))


def test_examples_directory_is_not_empty() -> None:
    assert EXAMPLES, "no example scripts found; the example gate would pass vacuously"


@pytest.mark.parametrize("script", EXAMPLES)
def test_example_does_not_hardcode_a_version(script: str) -> None:
    """Results carry the version that produced them, or the provenance is a guess.

    Every domain example stamped ``"version": "1.0.0"`` into ``results.json`` long after the package
    reached 2.0.0, so a published result named code that did not produce it.
    """
    source = (ROOT / "examples" / script).read_text()
    assert not re.search(r'"version":\s*"', source), (
        f"examples/{script} hard-codes a version; stamp eads.__version__ instead"
    )


@pytest.mark.parametrize("script", EXAMPLES)
def test_example_runs_without_credentials(script: str) -> None:
    completed = subprocess.run(
        [sys.executable, str(ROOT / "examples" / script)],
        capture_output=True,
        check=False,
        text=True,
        timeout=300,
        cwd=ROOT,
        env={"PATH": "/usr/bin:/bin", "HOME": str(ROOT)},
    )
    assert completed.returncode == 0, (
        f"examples/{script} exited {completed.returncode}\n{completed.stderr}"
    )
    assert completed.stdout.strip(), f"examples/{script} printed nothing"
