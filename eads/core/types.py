from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass(frozen=True)
class Signal:
    id: str
    source: str
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


@dataclass(frozen=True)
class Evidence:
    id: str
    signal_ids: list[str]
    claim: str
    confidence: float
    source_refs: list[str]
    extracted_by: str


@dataclass(frozen=True)
class AgentMessage:
    sender: str
    role: str
    content: str
    tool_call: dict[str, Any] | None = None
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


@dataclass
class Plan:
    plan_id: str
    goal: str
    steps: list[dict[str, Any]]
    evidence_refs: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ProposedAction:
    """A model proposal after parsing, in the form the governance layer can check.

    ``parsed`` records whether the model output matched a known action grammar. Governance
    rejects actions with ``parsed is False``: an action that cannot be understood cannot be
    proven safe.
    """

    type: str
    raw_value: str
    quantity: int | None = None
    region: str | None = None
    label: str | None = None
    parsed: bool = False


@dataclass
class DecisionCandidate:
    plan_id: str
    actions: list[ProposedAction]
    expected_outcome: dict[str, Any] = field(default_factory=dict)
    evidence_refs: list[str] = field(default_factory=list)
    confidence: float = 0.0


APPROVED = "approved"
REJECTED = "rejected"
ESCALATED = "escalated"


@dataclass
class Verdict:
    """Outcome of policy, safety, and permission review.

    ``outcome`` distinguishes the three terminal states the architecture calls for:
    ``approved`` (execute), ``rejected`` (a policy or safety violation, never executable), and
    ``escalated`` (permissible but requires a human approval that has not been granted).
    ``approved`` is the boolean shorthand for ``outcome == "approved"``.
    """

    approved: bool
    reason: str
    violated_policies: list[str] = field(default_factory=list)
    required_approvals: list[str] = field(default_factory=list)
    trust_score: float = 0.0
    outcome: str = APPROVED


@dataclass
class ExecutionResult:
    action_id: str
    status: str
    output: dict[str, Any] = field(default_factory=dict)
    latency_ms: float = 0.0


@dataclass
class AuditRecord:
    request_id: str
    trace: list[dict[str, Any]] = field(default_factory=list)
    decision: DecisionCandidate | None = None
    verdict: Verdict | None = None
    execution: ExecutionResult | None = None
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    signatures: dict[str, str] = field(default_factory=dict)


@dataclass
class DecisionRequest:
    request_id: str
    goal: str
    signals: list[Signal]
    policy_snapshot: dict[str, Any] = field(default_factory=dict)
    seed: int = 42
