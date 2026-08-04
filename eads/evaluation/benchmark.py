import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ..core.pipeline import DecisionPipeline
from .metrics import decision_consistency, policy_compliance


class Benchmark:
    """Reproducible benchmark harness for EADS pipelines."""

    def __init__(
        self,
        pipeline: DecisionPipeline,
        scenarios: list[dict[str, Any]],
        output_dir: str | None = None,
        metadata: dict[str, Any] | None = None,
    ):
        self.pipeline = pipeline
        self.scenarios = scenarios
        self.output_dir = output_dir or "benchmarks/results"
        self.metadata = metadata or {}

    def run(self) -> dict[str, Any]:
        results = []
        for scenario in self.scenarios:
            request = scenario["request"]
            record = self.pipeline.run(request)
            results.append(
                {
                    "scenario_id": scenario["id"],
                    "approved": record.verdict.approved if record.verdict else False,
                    "execution_status": record.execution.status if record.execution else "unknown",
                    "reason": record.verdict.reason if record.verdict else "",
                }
            )
        report = {
            "metadata": {
                "timestamp": datetime.now(UTC).isoformat(),
                "scenarios": len(self.scenarios),
                **self.metadata,
            },
            "policy_compliance": policy_compliance(results),
            "decision_consistency": decision_consistency(results),
            "results": results,
        }
        if self.output_dir:
            self._write(report)
        return report

    def _write(self, report: dict[str, Any]) -> Path:
        out_dir = Path(self.output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / "results.json"
        path.write_text(json.dumps(report, indent=2, default=str))
        return path
