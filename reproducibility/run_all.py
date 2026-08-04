#!/usr/bin/env python3
"""Run the full reproducibility suite and write a summary JSON."""

import json
import subprocess
from pathlib import Path


def run(cmd: str) -> str:
    print(f"$ {cmd}")
    result = subprocess.run(
        cmd,
        shell=True,
        check=True,
        text=True,
        capture_output=True,
    )
    return result.stdout.strip()


def main() -> None:
    out = Path("reproducibility/results.json")
    out.parent.mkdir(exist_ok=True)

    summary = {
        "tests": run("python3 -m pytest -q"),
        "examples": run("PYTHONPATH=. python3 examples/supply_chain.py"),
        "extras": run("PYTHONPATH=. python3 scripts/validate_extras.py"),
        "llms": run("PYTHONPATH=. python3 scripts/validate_llms.py"),
    }

    out.write_text(json.dumps(summary, indent=2))
    print(f"\nReproducibility summary written to {out}")


if __name__ == "__main__":
    main()
