# Promotion and Launch Checklist

Use this checklist when the repository is ready for a public launch.

## Pre-launch

- [ ] Repository is public.
- [ ] `CITATION.cff` is filled with the correct author, ORCID, and affiliation.
- [ ] `README.md` includes problem-first pitch, 60-second quickstart, badges, and examples.
- [ ] `CHANGELOG.md` is updated for the release.
- [ ] `CONTRIBUTING.md` and `CODE_OF_CONDUCT.md` are in place.
- [x] GitHub release `v2.0.0` is tagged (see [Releasing](releasing.md)).
- [ ] PyPI package is uploaded and the badge is verified. Deliberately not done: the governance
      boundary is installable as [typedguard](https://pypi.org/project/typedguard/), and this
      repository stays install-from-git as the reference implementation.
- [x] Zenodo DOI is minted and added to `CITATION.cff` (`10.5281/zenodo.21797859`).
- [ ] Docs site is live at `https://nirmaljingar.github.io/enterprise-ai-decision-systems`.
- [ ] Colab notebook opens without errors.

## Announcements

- [ ] Post a launch thread on Hacker News (`Show HN:`).
- [ ] Write a LinkedIn post summarizing the problem, demo, and links.
- [ ] Share on Twitter/X with a short GIF or screenshot of the quickstart output.
- [ ] Submit to relevant subreddits (r/MachineLearning, r/SupplyChain, r/DataScience).
- [ ] Announce on specialized communities (MLOps Discord, LLM/LangChain Slack, etc.).
- [ ] Email relevant academic collaborators and ask for stars/feedback.

## Publications

- [ ] Upload the companion paper/preprint to arXiv.
- [ ] Add the arXiv DOI to `README.md` and `CITATION.cff`.
- [ ] Submit a short software paper to *Journal of Open Source Software* or *SoftwareX*.

## Post-launch

- [ ] Respond to issues and PRs within 48 hours for the first two weeks.
- [ ] Collect testimonials and use cases for an EB-1A or grant portfolio.
- [ ] Track stars and forks with GitHub insights, and citations through the Zenodo DOI.
