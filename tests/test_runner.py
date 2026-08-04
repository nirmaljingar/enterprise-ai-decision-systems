"""Every manifest must run, and must reach the outcome it declares.

A benchmark whose numbers nobody checks is a sketch. These tests execute every manifest in
``benchmarks/manifests/`` and assert the metrics it produces, so a change that quietly starts
approving injected orders fails here rather than being published as a result.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

import eads
from eads.evaluation.runner import (
    LABELS,
    SCHEMA_VERSION,
    Manifest,
    ManifestError,
    run_manifest,
)

ROOT = Path(__file__).resolve().parent.parent
MANIFEST_DIR = ROOT / "benchmarks" / "manifests"
MANIFESTS = sorted(MANIFEST_DIR.glob("*.json"))
PINNED_AT_ONE = (
    "policy_compliance",
    "decision_consistency",
    "evidence_grounding_rate",
    "fallback_recovery_rate",
    "injection_resistance",
    "audit_completeness",
)


def test_manifests_exist() -> None:
    assert MANIFESTS, "no benchmark manifests found; the benchmark gate would pass vacuously"


@pytest.mark.parametrize("path", MANIFESTS, ids=lambda path: path.stem)
def test_manifest_declares_its_provenance(path: Path) -> None:
    manifest = Manifest.load(path)
    assert manifest.label in LABELS
    assert manifest.traces_to, f"{path.name} does not say which paper concept it traces to"
    assert manifest.digest, f"{path.name} produced no digest to record in its results"


@pytest.mark.parametrize("path", MANIFESTS, ids=lambda path: path.stem)
def test_manifest_runs_and_matches_its_expectations(path: Path, tmp_path: Path) -> None:
    report = run_manifest(path, tmp_path)
    for metric in PINNED_AT_ONE:
        assert report[metric] == 1.0, (
            f"{path.name} scored {metric} = {report[metric]}; "
            f"outcomes: {[(run['scenario_id'], run['outcome']) for run in report['results']]}"
        )


@pytest.mark.parametrize("path", MANIFESTS, ids=lambda path: path.stem)
def test_results_record_what_produced_them(path: Path, tmp_path: Path) -> None:
    report = run_manifest(path, tmp_path)
    metadata = report["metadata"]
    for field in ("seed", "manifest_digest", "label", "traces_to", "backend", "python"):
        assert metadata[field] not in (None, ""), f"{path.name} results omit {field}"
    written = json.loads(
        (tmp_path / metadata["benchmark_id"] / "results.json").read_text()
    )
    assert written["metadata"]["manifest_digest"] == metadata["manifest_digest"]


def test_an_adversarial_manifest_exists_and_is_actually_adversarial() -> None:
    adversarial = [
        scenario
        for path in MANIFESTS
        for scenario in json.loads(path.read_text())["scenarios"]
        if scenario.get("adversarial")
    ]
    assert adversarial, "no adversarial scenario; injection_resistance would be vacuous"
    for scenario in adversarial:
        assert scenario.get("injected_signals"), (
            f"{scenario['id']} claims to be adversarial but injects nothing"
        )


def test_a_manifest_with_an_unknown_label_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "bad.json"
    path.write_text(
        json.dumps(
            {
                "id": "bad",
                "domain": "supply_chain",
                "label": "Peer reviewed",
                "traces_to": "nothing",
                "scenarios": [{"id": "x", "goal": "g", "policy_snapshot": {}}],
            }
        )
    )
    with pytest.raises(ManifestError, match="label"):
        Manifest.load(path)


def test_a_manifest_with_no_scenarios_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "empty.json"
    path.write_text(
        json.dumps(
            {
                "id": "empty",
                "domain": "supply_chain",
                "label": "Illustrative example",
                "traces_to": "nothing",
                "scenarios": [],
            }
        )
    )
    with pytest.raises(ManifestError, match="no scenarios"):
        Manifest.load(path)


def test_the_published_results_page_is_not_stale() -> None:
    """The page readers see must match what the manifests currently produce.

    A published number that drifts from the code is worse than no number, so regenerating the page
    is part of changing a metric rather than a step someone remembers.
    """
    completed = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "run_benchmarks.py"), "--check"],
        capture_output=True,
        check=False,
        text=True,
        cwd=ROOT,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr


@pytest.mark.parametrize("path", MANIFESTS, ids=lambda path: path.stem)
def test_results_are_byte_identical_across_runs(path: Path, tmp_path: Path) -> None:
    """The determinism contract, applied to the numbers this repository publishes."""
    first = run_manifest(path, tmp_path / "a")
    second = run_manifest(path, tmp_path / "b")
    assert json.dumps(first, default=str) == json.dumps(second, default=str)


def test_a_future_schema_version_is_refused_rather_than_guessed(tmp_path: Path) -> None:
    """A runner that ignores a format it does not know publishes numbers for a manifest it misread."""
    path = tmp_path / "future.json"
    path.write_text(
        json.dumps(
            {
                "schema_version": SCHEMA_VERSION + 1,
                "id": "future",
                "domain": "supply_chain",
                "label": "Illustrative example",
                "traces_to": "nothing",
                "scenarios": [{"id": "x", "goal": "g", "policy_snapshot": {}}],
            }
        )
    )
    with pytest.raises(ManifestError, match="schema_version"):
        Manifest.load(path)


def test_an_unknown_field_is_refused_rather_than_dropped(tmp_path: Path) -> None:
    """A misspelled field would be ignored in silence, and its number published as if honoured."""
    path = tmp_path / "typo.json"
    path.write_text(
        json.dumps(
            {
                "id": "typo",
                "domain": "supply_chain",
                "label": "Illustrative example",
                "traces_to": "nothing",
                "repeat": 5,
                "scenarios": [{"id": "x", "goal": "g", "policy_snapshot": {}}],
            }
        )
    )
    with pytest.raises(ManifestError, match="unknown fields"):
        Manifest.load(path)


def test_an_unknown_scenario_field_is_refused(tmp_path: Path) -> None:
    path = tmp_path / "scenario_typo.json"
    path.write_text(
        json.dumps(
            {
                "id": "scenario-typo",
                "domain": "supply_chain",
                "label": "Illustrative example",
                "traces_to": "nothing",
                "scenarios": [
                    {
                        "id": "x",
                        "goal": "g",
                        "policy_snapshot": {},
                        "injected_signal": [{"source": "s", "content": "c"}],
                    }
                ],
            }
        )
    )
    with pytest.raises(ManifestError, match="unknown fields"):
        Manifest.load(path)


def test_the_template_is_a_valid_manifest() -> None:
    """A template that does not load is a trap for the first person who copies it."""
    manifest = Manifest.load(ROOT / "benchmarks" / "manifest_template.json")
    assert manifest.schema_version == SCHEMA_VERSION
    assert manifest.label in LABELS


def test_the_template_is_not_run_as_a_benchmark() -> None:
    """It lives outside manifests/ so its placeholder numbers are never published."""
    assert (ROOT / "benchmarks" / "manifest_template.json").exists()
    assert "manifest_template" not in {path.stem for path in MANIFESTS}


def test_every_manifest_declares_the_schema_it_was_written_against() -> None:
    for path in MANIFESTS:
        assert "schema_version" in json.loads(path.read_text()), (
            f"{path.name} does not declare schema_version, so a format change cannot be detected"
        )


def test_results_record_the_code_version_that_produced_them(tmp_path: Path) -> None:
    """Read from the package: distribution metadata went stale and reported "unknown"."""
    report = run_manifest(MANIFESTS[0], tmp_path)
    assert report["metadata"]["eads_version"] == eads.__version__
    assert report["metadata"]["eads_version"] != "unknown"

