# Security Policy

## Status of this project

This repository is **alpha research software**. It is not hardened for production use, and its
governance layer is a reference arrangement rather than a certified control. Do not place it on a
path that authorizes real-world actions without your own review.

## Supported versions

Only the `main` branch receives fixes. There is no release channel and no backport policy.

## Reporting a vulnerability

Report suspected vulnerabilities privately via GitHub's
[private vulnerability reporting](https://github.com/nirmaljingar/enterprise-ai-decision-systems/security/advisories/new).
Please do not open a public issue for anything exploitable.

Include, where possible:

- affected file, module, or workflow;
- reproduction steps or a proof-of-concept input;
- the impact you believe it has.

Expect an acknowledgement within 10 working days. Because this is a research artifact maintained on
a best-effort basis, fixes are not on a guaranteed timeline.

## Scope

In scope: the `eads` package, the GitHub Actions workflows, and the packaging metadata.

Out of scope: the optional third-party adapters themselves (report those upstream), and findings
that depend on running the project with credentials or permissions it advises against granting.

Design-level notes relevant to safe use — the fail-closed governance boundary, audit log
properties, and reproducibility limits — are documented in
[`docs/security.md`](./docs/security.md) and [`docs/limitations.md`](./docs/limitations.md).
