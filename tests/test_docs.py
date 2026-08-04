"""Pasted terminal output in the docs must be what the command actually prints.

``docs/wow_demo.md`` carried output from a run months old: a trust score of 0.9 where the code now
produces 0.392, three evidence items where it now produces two, and a benchmark block from an API
that no longer exists. Nobody had lied -- the page simply was not re-run, which is exactly why a
pasted result needs a test rather than a convention.

A block fenced between ``<!-- BEGIN <script> -->`` and ``<!-- END <script> -->`` is compared against
a live run of that script. Adding a checked block to any page is those two comments.
"""

import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
DOCS = sorted((ROOT / "docs").rglob("*.md"))
BLOCK = re.compile(
    r"<!-- BEGIN (?P<script>[\w/.\-]+) -->\s*```text\n(?P<output>.*?)```\s*<!-- END (?P=script) -->",
    re.DOTALL,
)


def _blocks() -> list[tuple[Path, str, str]]:
    found = []
    for path in DOCS:
        for match in BLOCK.finditer(path.read_text()):
            found.append((path, match.group("script"), match.group("output")))
    return found


BLOCKS = _blocks()


def test_at_least_one_output_block_is_checked() -> None:
    assert BLOCKS, "no doc output is verified against a run; pasted results can drift unnoticed"


@pytest.mark.parametrize(
    "path,script,expected",
    BLOCKS,
    ids=[f"{path.stem}-{script}" for path, script, _ in BLOCKS],
)
def test_pasted_output_matches_a_live_run(path: Path, script: str, expected: str) -> None:
    completed = subprocess.run(
        [sys.executable, str(ROOT / script)],
        capture_output=True,
        check=False,
        cwd=ROOT,
        text=True,
    )
    assert completed.returncode == 0, completed.stderr
    assert completed.stdout.strip() == expected.strip(), (
        f"{path.relative_to(ROOT)} shows output {script} no longer produces; rerun it and paste "
        f"the result.\n\n--- pasted ---\n{expected}\n--- actual ---\n{completed.stdout}"
    )
