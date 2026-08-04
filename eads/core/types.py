from dataclasses import dataclass, field
from typing import Any

from .clock import system_clock


@dataclass(frozen=True)
class Signal:
    id: str
    source: str
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=system_clock)


@dataclass(frozen=True)
class SourceSpan:
    """The characters of a signal an evidence claim was extracted from.

    Evidence without a span is unverifiable: a reviewer cannot quote it, and a changed source cannot
    be detected. The span indexes ``Signal.content`` unmodified.
    """

    signal_id: str
    start: int
    end: int
    text: str = ""


@dataclass(frozen=True)
class Evidence:
    """One extracted claim, with everything needed to check it.

    ``confidence`` is derived from how much checkable detail the extractor found, never asserted by
    the extractor or by a model. ``imperative`` marks claims phrased as instructions, which is the
    shape prompt injection takes when it arrives inside ingested content; ``trusted`` records
    whether the source was on the caller's trusted list. Neither is used to authorize anything --
    they exist so the trust boundary is visible on the record rather than inferred from prose.
    """

    id: str
    signal_ids: list[str]
    claim: str
    confidence: float
    source_refs: list[str]
    extracted_by: str
    provenance: tuple[SourceSpan, ...] = ()
    entities: tuple[str, ...] = ()
    quantities: tuple[float, ...] = ()
    imperative: bool = False
    trusted: bool = True


@dataclass(frozen=True)
class AgentMessage:
    sender: str
    role: str
    content: str
    tool_call: dict[str, Any] | None = None
    timestamp: str = field(default_factory=system_clock)


@dataclass
class Plan:
    plan_id: str
    goal: str
    steps: list[dict[str, Any]]
    evidence_refs: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class Actor:
    """The principal a decision is requested on behalf of.

    Approvals are meaningless without one: ``manager_approval_required`` names a role, not a
    person, so an escalation that does not record who asked cannot be audited or routed.
    """

    id: str
    roles: tuple[str, ...] = ()


@dataclass(frozen=True)
class ApprovalRequirement:
    """An approval a candidate still needs before it may execute.

    ``approver_role`` is the role that can grant it. The requesting actor never satisfies its own
    requirement, even when it holds the role: separation of duties is the point of the gate.
    """

    approver_role: str
    reason: str
    threshold: float | None = None
    value: float | None = None


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
    required_approvals: list[ApprovalRequirement] = field(default_factory=list)
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
    timestamp: str = field(default_factory=system_clock)
    policy_snapshot_id: str = ""
    actor: Actor | None = None


@dataclass
class DecisionRequest:
    request_id: str
    goal: str
    signals: list[Signal]
    policy_snapshot: dict[str, Any] = field(default_factory=dict)
    seed: int = 42
    actor: Actor = field(default_factory=lambda: Actor(id="unattributed"))
