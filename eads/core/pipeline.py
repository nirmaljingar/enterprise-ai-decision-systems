from typing import Any

from ..decision.decision import DecisionEngine
from ..governance.governance import GovernanceLayer
from ..knowledge_ingestion.ingestion import IngestionPipeline
from ..modernization.modernization import ModernizationPipeline
from ..reasoning.reasoning import ReasoningEngine
from .adapters import FakeLLM, LLMBackend
from .types import (
    AuditRecord,
    DecisionCandidate,
    DecisionRequest,
    Evidence,
    ExecutionResult,
    Plan,
    Signal,
    Verdict,
)


class DecisionPipeline:
    """Deterministic orchestration over the EADS decision lifecycle."""

    def __init__(
        self,
        llm: LLMBackend | None = None,
        ingestion: IngestionPipeline | None = None,
        modernization: ModernizationPipeline | None = None,
        reasoning: ReasoningEngine | None = None,
        decision_engine: DecisionEngine | None = None,
        governance: GovernanceLayer | None = None,
    ):
        self.llm = llm or FakeLLM()
        self.ingestion = ingestion or IngestionPipeline()
        self.modernization = modernization
        self.reasoning = reasoning or ReasoningEngine()
        self.decision_engine = decision_engine or DecisionEngine(llm=self.llm)
        self.governance = governance or GovernanceLayer()

    def run(self, request: DecisionRequest) -> AuditRecord:
        record = AuditRecord(request_id=request.request_id)
        legacy_signals = [
            s for s in request.signals if s.metadata.get("source_type") == "legacy_code"
        ]
        legacy_ids = {s.id for s in legacy_signals}
        non_legacy_signals = [s for s in request.signals if s.id not in legacy_ids]
        modernization_evidence = self._modernize(legacy_signals)
        evidence = self.ingestion.ingest(non_legacy_signals) + modernization_evidence
        plan = self.reasoning.plan(evidence, request.goal)
        candidate = self.decision_engine.generate(request, plan=plan)
        verdict = self._review(candidate, request)
        execution = self._execute(candidate, verdict)
        record.decision = candidate
        record.verdict = verdict
        record.execution = execution
        record.trace = self._build_trace(
            request,
            modernization_evidence,
            evidence,
            plan,
            candidate,
            verdict,
            execution,
        )
        return record

    def _modernize(self, legacy_signals: list[Signal]) -> list[Evidence]:
        if not self.modernization or not legacy_signals:
            return []
        evidence = []
        for signal in legacy_signals:
            result = self.modernization.analyze(signal.content)
            evidence.append(
                Evidence(
                    id=f"modernization_{signal.id}",
                    signal_ids=[signal.id],
                    claim=f"Modernization analysis: {result}",
                    confidence=1.0,
                    source_refs=[signal.id],
                    extracted_by="eads.modernization",
                )
            )
        return evidence

    def _review(self, candidate: DecisionCandidate, request: DecisionRequest) -> Verdict:
        if self.governance is not None:
            return self.governance.review(candidate, request.policy_snapshot)
        return Verdict(approved=True, reason="no governance configured")

    def _execute(self, candidate: DecisionCandidate, verdict: Verdict) -> ExecutionResult:
        if not verdict.approved:
            return ExecutionResult(
                action_id="fallback",
                status="blocked",
                output={"reason": verdict.reason},
                latency_ms=0.0,
            )
        action_id = candidate.actions[0].get("type", "action") if candidate.actions else "none"
        return ExecutionResult(
            action_id=action_id,
            status="success",
            output={"executed": True, "actions": candidate.actions},
            latency_ms=1.0,
        )

    def _build_trace(
        self,
        request: DecisionRequest,
        modernization_evidence: list[Evidence],
        evidence: list[Evidence],
        plan: Plan,
        candidate: DecisionCandidate,
        verdict: Verdict,
        execution: ExecutionResult,
    ) -> list[dict[str, Any]]:
        trace = []
        if modernization_evidence:
            trace.append({"step": "modernize", "evidence": len(modernization_evidence)})
        trace.extend(
            [
                {"step": "ingest", "signals": len(request.signals), "evidence": len(evidence)},
                {
                    "step": "reason",
                    "plan_id": plan.plan_id,
                    "evidence_refs": plan.evidence_refs,
                },
                {
                    "step": "generate",
                    "actions": candidate.actions,
                    "evidence_refs": candidate.evidence_refs,
                },
                {"step": "verdict", "approved": verdict.approved, "reason": verdict.reason},
                {"step": "execute", "status": execution.status},
            ]
        )
        return trace
