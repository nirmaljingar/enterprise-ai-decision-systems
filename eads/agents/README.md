# `eads.agents`

**Trace:** Papers 2 and 4 — autonomous agent collaboration.

Deterministic multi-agent collaboration primitives, tool-calling placeholders, and message passing.

- `eads.agents.agents.Agent` — a single agent that emits typed `AgentMessage` objects.
- `Agent.swarm` — a minimal coordinator that aggregates messages into a consensus placeholder.

Status: runnable skeleton; real consensus protocols and tool registration are suggested extensions.
