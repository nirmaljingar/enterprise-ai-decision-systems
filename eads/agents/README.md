# `eads.agents`

**Trace:** Papers 2 and 4 — autonomous agent collaboration.

Deliberation over typed proposals, with explicit votes, quorum, and role-scoped tools.

- `eads.agents.agents.Proposal` — a typed proposal: action type, quantity, region.
- `eads.agents.agents.Agent` — votes within the limits of its role; `request_tool` refuses tools the
  role does not hold.
- `eads.agents.agents.Coordinator` — collects votes and declares consensus only when a quorum agrees
  on the same proposal.
- `Agent.swarm` — convenience shim over three identically configured reviewers.

## What it does

Votes compare fields, not prose, so two agents phrasing one order differently count as agreeing and
two agents proposing different quantities do not. Dissent is reported rather than averaged: averaging
two proposals produces a third that no agent argued for and nobody is accountable for. Abstentions
count against support, because two of five agents agreeing is not two of two.

Short of quorum the outcome is `no_consensus` — a result, not a failure to produce one. A tie is never
consensus.

Proposals travel in the structured `tool_call` field and are never parsed out of message prose: text
that can vote is text that can be injected. Likewise, a tool named in a message is not thereby
granted; capability comes only from the role's configured tool set. That is the same rule the
governance layer applies to model output, for the same reason.

## What it does not do

Agents do not call a language model, plan, negotiate over multiple rounds, or revise a position in
response to an argument — a vote is a function of the proposals and the role, so deliberation is
deterministic and replayable. There is no shared memory between rounds and no tool execution: a
granted request is returned to the caller, which decides whether to run it. `Agent.swarm` configures
three identical reviewers, and identical agents agreeing measures nothing; `Coordinator` with
differently scoped agents is the interface that carries meaning.
