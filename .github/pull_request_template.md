## Summary

<!-- What changes and why. Prefer the "why": the diff already shows the "what". -->

## Type of change

- [ ] Bug fix
- [ ] New capability
- [ ] Breaking change to a public type or signature
- [ ] Documentation only
- [ ] Build, CI, or tooling

## Verification

```bash
pip install -e ".[dev]"
ruff check eads tests examples
mypy eads
pytest
```

<!-- Paste the relevant output, or state which of these you ran. -->

- [ ] Lint, typecheck, and tests pass locally
- [ ] `mkdocs build --strict` passes (if docs changed)

## Claims check

This repository has a history of documentation describing capabilities that do not exist.

- [ ] Every capability this PR documents is implemented, or is explicitly labelled as a stub
- [ ] No DOI, metric, or numerical result is stated without a verifiable source
- [ ] Governance changes cannot approve an action that could not be checked (fail closed)
