import json
from dataclasses import asdict
from pathlib import Path
from statistics import mean
from typing import Any

from ..core.clock import Clock, system_clock
from ..core.pipeline import DecisionPipeline
from .metrics import (
    approval_rate,
    audit_completeness,
    decision_consistency,
    evidence_grounding_rate,
    fallback_recovery_rate,
    injection_resistance,
    policy_compliance,
)


class Benchmark:
    """Reproducible benchmark harness for EADS pipelines.

    Each scenario is a dict with an ``id``, a ``request``, and optionally an
    ``expected_outcome`` label (``approved``, ``rejected``, or ``escalated``) that turns the
    scenario into an assertion instead of an observation. A scenario may also set
    ``adversarial: True`` to declare that its signals carry an injected instruction, which puts it
    in the denominator of :func:`~eads.evaluation.metrics.injection_resistance`. Scenarios are
    executed *repeats* times so decision consistency measures repeated runs of the same input.
    """

    def __init__(
        self,
        pipeline: DecisionPipeline,
        scenarios: list[dict[str, Any]],
        output_dir: str | None = None,
        metadata: dict[str, Any] | None = None,
        repeats: int = 3,
        clock: Clock = system_clock,
    ):
        if repeats < 1:
            raise ValueError("repeats must be at least 1")
        self.pipeline = pipeline
        self.scenarios = scenarios
        self.output_dir = output_dir or "benchmarks/results"
        self.metadata = metadata or {}
        self.repeats = repeats
        self.clock = clock

    def run(self) -> dict[str, Any]:
        runs: list[dict[str, Any]] = []
        consistency_per_scenario = []
        for scenario in self.scenarios:
            scenario_runs = [
                self._run_once(scenario, index) for index in range(self.repeats)
            ]
            consistency_per_scenario.append(decision_consistency(scenario_runs))
            runs.extend(scenario_runs)

        report = {
            "metadata": {
                "timestamp": self.clock(),
                "scenarios": len(self.scenarios),
                "repeats": self.repeats,
                **self.metadata,
            },
            "approval_rate": approval_rate(runs),
            "policy_compliance": policy_compliance(runs),
            "decision_consistency": mean(consistency_per_scenario)
            if consistency_per_scenario
            else 1.0,
            "evidence_grounding_rate": evidence_grounding_rate(runs),
            "fallback_recovery_rate": fallback_recovery_rate(runs),
            "injection_resistance": injection_resistance(runs),
            "audit_completeness": audit_completeness(runs),
            "results": runs,
        }
        if self.output_dir:
            self._write(report)
        return report

    def _run_once(self, scenario: dict[str, Any], index: int) -> dict[str, Any]:
        record = self.pipeline.run(scenario["request"])
        evidence_ids = [
            evidence_id
            for step in record.trace
            if step["step"] == "ingest"
            for evidence_id in step.get("evidence_ids", [])
        ]
        return {
            "scenario_id": scenario["id"],
            "run_index": index,
            "expected_outcome": scenario.get("expected_outcome"),
            "adversarial": bool(scenario.get("adversarial", False)),
            "outcome": record.verdict.outcome if record.verdict else "unknown",
            "approved": record.verdict.approved if record.verdict else False,
            "execution_status": record.execution.status if record.execution else "unknown",
            "reason": record.verdict.reason if record.verdict else "",
            "evidence_refs": record.decision.evidence_refs if record.decision else [],
            "evidence_ids": evidence_ids,
            "audit_record": asdict(record),
        }

    def _write(self, report: dict[str, Any]) -> Path:
        out_dir = Path(self.output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / "results.json"
        path.write_text(json.dumps(report, indent=2, default=str))
        return path
