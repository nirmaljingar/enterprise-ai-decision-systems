"""Multi-agent deliberation with explicit votes, quorum, and tool scoping.

The stub acknowledged without reading its messages, and `swarm` appended the string "consensus
reached" regardless of what the agents said. Announcing agreement that was never measured is the
failure mode this module exists to avoid: a coordinator that always agrees is indistinguishable from
one agent acting alone, and it makes disagreement invisible at exactly the moment it matters.

Deliberation here is a vote over *typed* proposals. Agents that propose the same action with the same
fields count as agreeing; anything else is dissent, and dissent is reported rather than averaged --
averaging two proposals produces a third that no agent argued for and nobody is accountable for.
Consensus requires a quorum; short of it the outcome is `no_consensus`, which is a result and not a
failure to produce one.

Tools are scoped per role. An agent cannot call a tool its role does not hold, and a tool request
arriving inside a message never grants one: capability comes from the registry the caller configured,
never from the content of the conversation. That is the same rule the governance layer applies to
model output, for the same reason.
"""

from collections import Counter
from dataclasses import dataclass, field
from typing import Any

from ..core.types import AgentMessage

CONSENSUS = "consensus"
NO_CONSENSUS = "no_consensus"
DEFAULT_QUORUM = 0.5


@dataclass(frozen=True)
class Proposal:
    """A typed proposal an agent can vote on.

    Votes compare fields, not prose. Two agents phrasing the same order differently should count as
    agreement, and two agents proposing different quantities must not.
    """

    action_type: str
    quantity: int | None = None
    region: str | None = None

    @property
    def key(self) -> tuple[str, int | None, str | None]:
        return (self.action_type, self.quantity, self.region)


@dataclass(frozen=True)
class Vote:
    """One agent's position on one proposal, with the reason it took that position."""

    agent: str
    role: str
    proposal: Proposal | None
    reason: str

    @property
    def abstained(self) -> bool:
        return self.proposal is None


@dataclass(frozen=True)
class Consensus:
    """The outcome of a deliberation, including every dissenting vote."""

    outcome: str
    proposal: Proposal | None
    votes: tuple[Vote, ...] = ()
    dissent: tuple[Vote, ...] = ()
    support: float = 0.0

    @property
    def reached(self) -> bool:
        return self.outcome == CONSENSUS


@dataclass
class Agent:
    """An agent that votes on proposals within the limits of its role.

    ``act`` reads the messages it is given -- the stub did not -- and returns its vote as a message.
    An agent abstains when no proposal is on the table, and abstention is recorded as a position
    rather than silently dropped, because a decision supported by two of five agents is not the same
    as one supported by two of two.

    ``tools`` is the set of tools the role holds. A tool named in a message is not thereby granted:
    capability comes from this set only.
    """

    name: str
    role: str
    tools: frozenset[str] = field(default_factory=frozenset)
    accepts: frozenset[str] = field(default_factory=frozenset)
    """Action types this role will vote for. Empty means the role votes for any action type."""

    def vote(self, proposals: list[Proposal]) -> Vote:
        if not proposals:
            return Vote(self.name, self.role, None, "no_proposal_on_the_table")
        acceptable = [
            proposal
            for proposal in proposals
            if not self.accepts or proposal.action_type in self.accepts
        ]
        if not acceptable:
            return Vote(self.name, self.role, None, f"outside_role:{self.role}")
        # Deterministic tie-break: the smallest proposal. A role with no reason to prefer the larger
        # of two figures should not be the thing that raises a quantity.
        chosen = min(acceptable, key=lambda proposal: (proposal.quantity or 0, proposal.key))
        return Vote(self.name, self.role, chosen, "within_role")

    def act(self, messages: list[AgentMessage]) -> AgentMessage:
        proposals = [
            proposal
            for message in messages
            for proposal in _proposals_of(message)
        ]
        cast = self.vote(proposals)
        return AgentMessage(
            sender=self.name,
            role=self.role,
            content=cast.reason if cast.abstained else f"votes_for:{cast.proposal}",
            tool_call=None,
        )

    def request_tool(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        """Return a tool call, or a refusal when the role does not hold the tool."""
        if name not in self.tools:
            return {"tool": name, "granted": False, "reason": "tool_not_held_by_role"}
        return {"tool": name, "granted": True, "arguments": arguments}

    @staticmethod
    def swarm(messages: list[AgentMessage], tools: list[str]) -> list[AgentMessage]:
        """Deliberate over the proposals in *messages* and append the coordinator's finding.

        A convenience shim over three identically configured reviewers. Identical agents agreeing
        measures nothing, so the outcome here is only ever a statement about the proposals on the
        table; `Coordinator` with differently scoped agents is the interface that carries meaning.
        """
        agents = [Agent(name=f"agent_{index}", role="reviewer", tools=frozenset(tools))
                  for index in range(3)]
        result = Coordinator(agents=agents).deliberate(
            [proposal for message in messages for proposal in _proposals_of(message)]
        )
        return messages + [
            AgentMessage(
                sender="swarm",
                role="coordinator",
                content=f"{result.outcome}:{result.proposal}"
                if result.reached
                else f"{result.outcome}:support={result.support:.2f}",
            )
        ]


@dataclass
class Coordinator:
    """Collects votes and declares consensus only when a quorum agrees on the same proposal."""

    agents: list[Agent]
    quorum: float = DEFAULT_QUORUM

    def deliberate(self, proposals: list[Proposal]) -> Consensus:
        votes = tuple(agent.vote(proposals) for agent in self.agents)
        counted = Counter(
            vote.proposal.key for vote in votes if vote.proposal is not None
        )
        if not counted or not self.agents:
            return Consensus(NO_CONSENSUS, None, votes, votes, 0.0)

        winner, count = counted.most_common(1)[0]
        support = count / len(self.agents)
        # Abstentions count against support. Two of five agents agreeing is not the same as two of
        # two, and treating it as such is how a minority position becomes a decision.
        if support <= self.quorum or _tied(counted):
            return Consensus(
                NO_CONSENSUS,
                None,
                votes,
                tuple(vote for vote in votes if vote.proposal is None or vote.proposal.key != winner),
                support,
            )
        agreed = next(
            vote.proposal
            for vote in votes
            if vote.proposal is not None and vote.proposal.key == winner
        )
        return Consensus(
            CONSENSUS,
            agreed,
            votes,
            tuple(
                vote
                for vote in votes
                if vote.proposal is None or vote.proposal.key != winner
            ),
            support,
        )


def _tied(counted: Counter[tuple[str, int | None, str | None]]) -> bool:
    ranked = counted.most_common(2)
    return len(ranked) > 1 and ranked[0][1] == ranked[1][1]


def _proposals_of(message: AgentMessage) -> list[Proposal]:
    """Read the proposal a message carries, if it carries one in the typed field.

    Proposals travel in ``tool_call``, which is structured. Prose in ``content`` is never parsed into
    a proposal: text that can vote is text that can be injected.
    """
    payload = message.tool_call
    if not payload or payload.get("proposal") is None:
        return []
    fields = payload["proposal"]
    if not isinstance(fields, dict) or "action_type" not in fields:
        return []
    quantity = fields.get("quantity")
    region = fields.get("region")
    return [
        Proposal(
            action_type=str(fields["action_type"]),
            quantity=int(quantity) if isinstance(quantity, int | float) else None,
            region=str(region) if isinstance(region, str) else None,
        )
    ]


__all__ = [
    "CONSENSUS",
    "DEFAULT_QUORUM",
    "NO_CONSENSUS",
    "Agent",
    "Consensus",
    "Coordinator",
    "Proposal",
    "Vote",
]
