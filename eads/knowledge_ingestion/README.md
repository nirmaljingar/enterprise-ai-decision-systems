# `eads.knowledge_ingestion`

**Trace:** Paper 2 — unstructured supply-chain intelligence (LASCI Step 1).

Converts unstructured enterprise signals into structured, span-attributed evidence.

- `eads.knowledge_ingestion.extraction.extract_claims` — text → `List[Claim]` with character offsets.
- `eads.knowledge_ingestion.ingestion.IngestionPipeline` — `Signal` → `List[Evidence]`.

## What it does

1. **Segments** each signal into individual claims, so a decision cites the sentence that supports it
   rather than a whole email.
2. **Attributes** every claim to the characters it came from (`Evidence.provenance`), so a reviewer
   can quote the source and a changed source is detectable.
3. **Extracts** quantities, percentages, currency amounts, identifiers, regions, and organisations.
4. **Corroborates**: near-identical claims from different sources collapse into one piece of
   evidence listing every source.
5. **Derives** confidence from the checkable detail found and the number of independent sources,
   capped below 1.0. Certainty is not something an extractor can claim.
6. **Marks** instruction-shaped content and untrusted sources on the record, so the trust boundary is
   visible rather than inferred from prose later.

## What it does not do

The extractors are lexical and dependency-free. They do not do coreference resolution, negation
scope, temporal normalization, or entity linking against a knowledge base, and term overlap is not
synonymy — two sources wording the same fact differently enough will be recorded as two claims. A
lexical extractor that states its limits is more useful than a model-shaped one that cannot be run
offline and deterministically, which is what the benchmark harness requires.

Untrusted content is never dropped. Suppressing it would hide an attack rather than contain it;
containment belongs to `eads.governance`, which reads typed actions rather than evidence prose.
