# `eads.governance`

**Trace:** Papers 1, 3, and 4 — policy, safety, permissions, fallback, audit, and trust.

Cross-cutting governance layer composed of focused sub-packages:

- `eads.governance.policy.PolicyEngine`
- `eads.governance.safety.SafetyFilter`
- `eads.governance.permissions.PermissionGate`
- `eads.governance.fallback.FallbackHandler`
- `eads.governance.audit.AuditLogger`
- `eads.governance.trust.TrustScorer`
- `eads.governance.governance.GovernanceLayer` — orchestrates all checks into a single `Verdict`.

Status: runnable skeleton; rich policy DSL, role-based access control, and immutable audit signing are planned extensions.
