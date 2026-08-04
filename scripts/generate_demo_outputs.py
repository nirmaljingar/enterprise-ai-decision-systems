#!/usr/bin/env python3
"""Capture example stdout to docs/assets/ for the README and demo docs."""

import subprocess
from pathlib import Path


def main() -> None:
    base = Path("docs/assets")
    base.mkdir(parents=True, exist_ok=True)

    for example in ["quickstart.py", "supply_chain.py"]:
        out_path = base / f"{Path(example).stem}_output.txt"
        result = subprocess.run(
            f"PYTHONPATH=. python3 examples/{example}",
            shell=True,
            text=True,
            capture_output=True,
            check=True,
        )
        out_path.write_text(result.stdout)
        print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
