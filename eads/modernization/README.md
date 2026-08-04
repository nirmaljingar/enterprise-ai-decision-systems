# `eads.modernization`

**Trace:** Paper 1 — LLM-driven refactoring and architecture transformation.

Static analysis of legacy Python source and monolith-to-service decomposition.

- `eads.modernization.analysis.analyze_source` — source → units, imports, unit-to-unit edges,
  entry points.
- `eads.modernization.modernization.ModernizationPipeline` — the dependency graph plus the service
  boundaries it supports.

## What it does

Parses with `ast`. The submitted source is never imported, `eval`-ed, or executed — that is the
control behind T5 in the [threat model](../../docs/threat_model.md), and it is why the module can be
handed attacker-supplied text.

The unit of analysis is a top-level function or class, plus a synthetic `<module>` unit for statements
at module level. Edges come from the names a unit references. Services are the connected components of
that graph, named after their largest unit, so a proposed boundary is one the graph actually supports.
Reported alongside them: the edges that would be cut, and the cycles that would have to be untangled
first — a cycle is what makes a decomposition hard and hiding it would make the output useless.

Source that does not parse yields `parsed: False` and no decomposition. A decomposition of source that
could not be read would be an invented answer, and a caller cannot tell an invented one from a real
one.

## What it does not do

It does not refactor, generate code, or claim a decomposition is correct. The call graph is an
approximation: edges follow direct name references and attribute roots, and it does not resolve
aliases, dynamic dispatch, or calls reached through a variable. Cycle detection finds mutually
referencing pairs, not longer cycles. Python only — no other language is parsed. Boundaries are
candidates for a human to weigh, which is why the cost of each cut is reported rather than scored.
