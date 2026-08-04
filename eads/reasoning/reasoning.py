
from ..core.types import Evidence, Plan


class ReasoningEngine:
    """Evidence-backed planning for decision support."""

    def plan(self, evidence: list[Evidence], goal: str) -> Plan:
        return Plan(
            plan_id="plan_1",
            goal=goal,
            steps=[{"action": "process", "evidence_ids": [e.id for e in evidence]}],
            evidence_refs=[e.id for e in evidence],
        )
