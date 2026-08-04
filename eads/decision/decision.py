
from ..core.adapters import FakeLLM, LLMBackend
from ..core.types import DecisionCandidate, DecisionRequest, Plan
from .adapters import ForecasterBackend, SolverBackend
from .parsing import parse_action

STUB_CONFIDENCE = 0.9
"""Placeholder self-reported confidence.

This is a fixed constant, not a calibrated probability. It exists so the data model has a
confidence field to carry; do not read it as an accuracy estimate.
"""


class DecisionEngine:
    """Combine semantic reasoning with optional solver/forecaster adapters."""

    def __init__(
        self,
        llm: LLMBackend | None = None,
        solver: SolverBackend | None = None,
        forecaster: ForecasterBackend | None = None,
    ):
        self.llm = llm or FakeLLM()
        self.solver = solver
        self.forecaster = forecaster

    def generate(
        self, request: DecisionRequest, plan: Plan | None = None
    ) -> DecisionCandidate:
        evidence_summary = ""
        evidence_refs: list[str] = []
        if plan is not None:
            evidence_summary = f"\nPlan: {plan.goal}\nSteps: {plan.steps}"
            evidence_refs = plan.evidence_refs
        prompt = (
            f"Goal: {request.goal}\n"
            f"Signals: {[s.content for s in request.signals]}"
            f"{evidence_summary}"
        )
        response = self.llm.generate(prompt, seed=request.seed)

        expected_outcome = {}
        if self.solver is not None:
            expected_outcome.update(self.solver.optimize(request, plan))
        if self.forecaster is not None:
            expected_outcome.update(self.forecaster.forecast(request, plan))

        region_default = request.policy_snapshot.get("region")
        actions = [parse_action(response, region_default=region_default)]
        return DecisionCandidate(
            plan_id=request.request_id,
            actions=actions,
            expected_outcome=expected_outcome,
            evidence_refs=evidence_refs,
            confidence=STUB_CONFIDENCE,
        )
