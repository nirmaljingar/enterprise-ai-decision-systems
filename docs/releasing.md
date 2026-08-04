# Releasing

A release exists so a reader can cite a specific state of this software and get the same behaviour
back. Everything below is manual and requires credentials the repository does not hold.

## 1. Check the version is consistent

`tests/test_release.py` asserts that `pyproject.toml`, `eads/__init__.py`, `CITATION.cff`, and the
newest `CHANGELOG.md` heading all state the same version, and that the changelog entry is not empty.
A release whose metadata disagrees with itself cannot be cited reliably.

```bash
pytest tests/test_release.py
```

## 2. Verify the working tree

```bash
ruff check eads tests examples
mypy eads
pytest
mkdocs build --strict
python scripts/run_benchmarks.py --check
```

The last command matters for a release specifically: it fails if `docs/benchmarks/index.md` no longer
matches what the harness produces, so published numbers cannot drift from the tagged code.

## 3. Tag

```bash
git tag -a v2.0.0 -m "EADS Research Companion v2.0.0"
git push origin v2.0.0
```

Tag from `main` after CI is green. Do not move a tag once pushed: a moved tag silently changes what a
citation refers to.

## 4. Archive on Zenodo for a citable DOI

Zenodo mints a DOI per release and a concept DOI covering all of them — cite the concept DOI for "this
software", and a version DOI to point at exactly what was run.

1. Sign in to <https://zenodo.org> with GitHub.
2. Under **Account → GitHub**, enable the toggle for `nirmaljingar/enterprise-ai-decision-systems`.
   Zenodo archives every *subsequent* release, so enable it before tagging.
3. Publish a GitHub release from the tag. Zenodo reads `CITATION.cff` for authors, title, and license.
4. Add the DOI badge and the `identifiers:` entry to `CITATION.cff`, then commit that.

Until step 4 lands, no document in this repository should claim a Zenodo DOI exists.

## 5. Publish to PyPI

```bash
python -m build
python -m twine check dist/*
python -m twine upload dist/*
```

Prefer a scoped project API token over an account password, and prefer a Trusted Publisher workflow
over a long-lived token. Verify the install in a clean environment before announcing it:

```bash
pip install enterprise-ai-decision-systems
python -c "import eads; print(eads.__version__)"
```

## What a release does not assert

A tag says the code in it behaves as documented. It does not assert that the benchmark numbers
reproduce results from the four papers — they are runs of this implementation against synthetic
manifests, which [`docs/benchmarks/about.md`](benchmarks/about.md) states in full.
