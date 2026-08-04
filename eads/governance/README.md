# `eads.governance`

**Trace:** Papers 1, 3, and 4 — policy, safety, permissions, fallback, audit, and trust.

Cross-cutting governance layer composed of focused sub-packages:

- `eads.governance.policy.PolicyEngine`
- `eads.governance.safety.SafetyFilter`
- `eads.governance.permissions.PermissionGate`
- `eads.governance.fallback.FallbackHandler`
- `eads.governance.audit.AuditLogger`
- `eads.governance.trust.TrustScorer` — grades a candidate against the evidence it cites.
- `eads.governance.governance.GovernanceLayer` — orchestrates all checks into a single `Verdict`.

## Trust

`TrustScorer` checks the candidate against the evidence record, not against its own confidence:
whether its citations resolve, whether the figure it proposes appears in a cited claim, how well
supported those claims are, whether any came from an untrusted source or was phrased as an
instruction, and whether they contradict each other. Every deduction is named on
`Verdict.trust_reasons`, so a low score can be explained rather than merely observed.

Two things it is not. It is not a calibrated hallucination probability — the multipliers are chosen,
not fitted. And it authorizes nothing: `PolicyEngine`, `SafetyFilter`, and `PermissionGate` decide
the outcome and fail closed regardless of the score. Trust that gates execution would be a second,
weaker policy engine.

Status: rich policy DSL, role-based access control, and immutable audit signing are planned
extensions.
