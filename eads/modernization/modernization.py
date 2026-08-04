from typing import Any


class ModernizationPipeline:
    """Legacy-code analysis and decomposition.

    Stub: collects text after each ``import`` keyword and names one service per dependency,
    up to three. It does not build a dependency graph, resolve modules, or analyze coupling,
    so its output is illustrative only.
    """

    def analyze(self, code: str) -> dict[str, Any]:
        deps = [
            line.split("import")[-1].strip()
            for line in code.splitlines()
            if "import" in line
        ]
        return {
            "dependencies": deps,
            "proposed_services": [f"service_{i}" for i in range(min(len(deps), 3))],
            "entry_points": ["main"],
        }
