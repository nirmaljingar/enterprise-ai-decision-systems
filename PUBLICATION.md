# Publishing and Citing the EADS Research Companion

This repository is designed as a **citable, reproducible research artifact**. This guide explains how to assign a DOI, publish to PyPI, and present the companion as a publication.

## 1. DOI via Zenodo

1. Link the GitHub repository to [Zenodo](https://zenodo.org/).
2. Create a GitHub release tagged `v1.0.0`.
3. Zenodo will mint a DOI and update `CITATION.cff` automatically.
4. Replace the placeholder DOI in `CITATION.cff` with the Zenodo DOI and commit the change.

## 2. PyPI package

The package can be published to PyPI once a stable release is ready:

```bash
python -m build
python -m twine upload dist/*
```

After publication, users can install with:

```bash
pip install enterprise-ai-decision-systems
```

## 3. GitHub release

1. Tag the commit: `git tag -a v1.0.0 -m "EADS Research Companion v1.0.0"`
2. Push the tag: `git push origin v1.0.0`
3. Create a release with the changelog from `CHANGELOG.md`.

## 4. Citation

Please cite both the originating IEEE papers and the repository. See [`CITATION.cff`](../CITATION.cff) for repository metadata and [`CITING.md`](../CITING.md) for the paper list.

## 5. Publication options

- Submit a software paper to venues such as the *Journal of Open Source Software*, *SoftwareX*, or an ACM/IEEE software-track venue.
- Use the draft in `docs/technical_report.md` as the basis for an arXiv preprint or a conference submission.
- Include the DOI, GitHub URL, and PyPI link in an EB-1A or academic portfolio.
