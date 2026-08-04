# `eads.reasoning`

**Trace:** Papers 2 and 3 — evidence-backed, context-aware reasoning.

Plans over the evidence graph produced by `eads.knowledge_ingestion`.

- `eads.reasoning.graph.EvidenceGraph` — evidence indexed by entity, with typed edges
  (`shares_entity`, `corroborates`, `contradicts`).
- `eads.reasoning.reasoning.ReasoningEngine` — `List[Evidence]` + goal → `Plan`.

## What it does

1. **Selects** evidence by walking outward from the goal: hop 1 matches the goal's entities and
   terms, hop 2 follows typed edges, so a claim about a SKU reaches the carrier delay that affects
   it. The plan cites only what it used, with the hop depth and the reason for each selection.
2. **Reports contradictions** rather than resolving them. Two claims giving different figures for one
   entity become an explicit `verify` step; picking the larger number is how a decision quietly
   adopts an attacker's figure.
3. **Records untrusted instructions** as a `review_untrusted_instruction` step. The text is data, it
   is never followed here, and governance is what actually stops the action it asks for.
4. **Abstains** when there is no evidence, and says so when nothing matched the goal instead of
   implying a link it did not establish.

Planning is deterministic and calls no model: plan ids are content digests rather than salted string
hashes, so a replayed run produces an identical plan and the reproducibility contract on the audit
record holds.

## What it does not do

Edges are lexical — shared entities and matching figures. There is no embedding similarity, no
coreference resolution, and no temporal or causal inference, so two claims about the same thing in
different words are not connected, and "stock fell" and "stock rose" are not recognised as opposites.
Contradiction detection compares only claims carrying exactly one quantity each; a wrong pairing
would be reported as fact, which is worse than a missed one.
