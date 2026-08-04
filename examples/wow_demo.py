"""Single-command EADS wow demo: one decision + one benchmark."""

import subprocess
import sys
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parent.parent

    print("=" * 60)
    print("EADS in 60 Seconds — Live Wow Demo")
    print("=" * 60)

    print("\n--- 1. One auditable decision in <1 second ---\n")
    subprocess.run([sys.executable, str(root / "examples" / "quickstart.py")], check=True)

    print("\n--- 2. Reproducible supply-chain benchmark ---\n")
    subprocess.run([sys.executable, str(root / "examples" / "supply_chain.py")], check=True)

    print("\n" + "=" * 60)
    print("Demo complete. Explore examples/ and notebooks/ for more.")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
