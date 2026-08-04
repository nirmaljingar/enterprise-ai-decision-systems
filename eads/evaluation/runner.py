"""Execute a benchmark manifest and emit a versioned ``results.json``.

The research design asks for benchmarks that are artifacts rather than sketches: a manifest holding
inputs, expected outcomes, and a seed, and a result file recording the seed, the dependency
versions, and the metric values it was produced with. Without the recorded inputs, a published
number cannot be reproduced or disputed, which is the only thing that makes it worth publishing.

Manifests are JSON so the core stays standard-library only, and each is labelled
``Published methodology`` or ``Illustrative example`` so a reader can tell which numbers follow a
paper's protocol and which merely demonstrate how a metric is computed.
"""

import hashlib
import json
import platform
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .. import __version__
from ..core.attack import InjectionProneLLM
from ..core.clock import FixedClock
from ..core.pipeline import DecisionPipeline
from ..core.types import Actor, DecisionRequest, Signal
from ..decision.decision import DecisionEngine
from ..governance import GovernanceLayer
from ..synthetic_data import (
    BaseGenerator,
    CustomerSupportGenerator,
    FinanceGenerator,
    HealthcareGenerator,
    ITOperationsGenerator,
    SupplyChainGenerator,
)
from .benchmark import Benchmark

GENERATORS: dict[str, type[BaseGenerator]] = {
    "supply_chain": SupplyChainGenerator,
    "healthcare": HealthcareGenerator,
    "finance": FinanceGenerator,
    "it_operations": ITOperationsGenerator,
    "customer_support": CustomerSupportGenerator,
}
LABELS = frozenset({"Published methodology", "Illustrative example"})
FIXED_TIMESTAMP = "2026-01-01T00:00:00Z"
BACKENDS = frozenset({"fake", "injection_prone"})
SCHEMA_VERSION = 1
"""The manifest format this runner accepts.

Versioned so a manifest written elsewhere states which format it was written against, and a runner
that cannot honour it says so instead of silently ignoring fields it does not recognise.
"""
MANIFEST_FIELDS = frozenset(
    {"schema_version", "id", "domain", "label", "traces_to", "seed", "repeats", "backend",
     "scenarios"}
)
SCENARIO_FIELDS = frozenset(
    {"id", "goal", "policy_snapshot", "expected_outcome", "signal_count", "actor", "adversarial",
     "injected_signals"}
)


class ManifestError(ValueError):
    """A manifest is missing a field, or declares one the runner cannot honor."""


@dataclass(frozen=True)
class Manifest:
    """A benchmark declaration: what is run, against what policy, expecting what."""

    id: str
    domain: str
    label: str
    traces_to: str
    seed: int
    repeats: int
    backend: str
    scenarios: list[dict[str, Any]] = field(default_factory=list)
    digest: str = ""
    schema_version: int = SCHEMA_VERSION

    @classmethod
    def load(cls, path: Path) -> "Manifest":
        raw: dict[str, Any] = json.loads(path.read_text())
        missing = {"id", "domain", "label", "traces_to", "scenarios"} - set(raw)
        if missing:
            raise ManifestError(f"{path.name} is missing {sorted(missing)}")
        declared_schema = int(raw.get("schema_version", SCHEMA_VERSION))
        if declared_schema != SCHEMA_VERSION:
            raise ManifestError(
                f"{path.name} declares schema_version {declared_schema}; this runner accepts "
                f"{SCHEMA_VERSION}"
            )
        # A misspelled field would otherwise be dropped in silence, and the number it was meant to
        # change would be published as though the field had been honoured.
        unknown = set(raw) - MANIFEST_FIELDS
        if unknown:
            raise ManifestError(f"{path.name} declares unknown fields {sorted(unknown)}")
        for scenario in raw["scenarios"]:
            unknown_scenario = set(scenario) - SCENARIO_FIELDS
            if unknown_scenario:
                raise ManifestError(
                    f"{path.name} scenario {scenario.get('id', '?')!r} declares unknown fields "
                    f"{sorted(unknown_scenario)}"
                )
            required = {"id", "goal", "policy_snapshot"} - set(scenario)
            if required:
                raise ManifestError(
                    f"{path.name} scenario {scenario.get('id', '?')!r} is missing {sorted(required)}"
                )
        if raw["label"] not in LABELS:
            raise ManifestError(
                f"{path.name} label {raw['label']!r} must be one of {sorted(LABELS)}"
            )
        backend = raw.get("backend", "fake")
        if backend not in BACKENDS:
            raise ManifestError(f"{path.name} backend {backend!r} must be one of {sorted(BACKENDS)}")
        if raw["domain"] not in GENERATORS:
            raise ManifestError(
                f"{path.name} domain {raw['domain']!r} must be one of {sorted(GENERATORS)}"
            )
        if not raw["scenarios"]:
            raise ManifestError(f"{path.name} declares no scenarios")
        return cls(
            id=str(raw["id"]),
            domain=str(raw["domain"]),
            label=str(raw["label"]),
            traces_to=str(raw["traces_to"]),
            seed=int(raw.get("seed", 42)),
            repeats=int(raw.get("repeats", 3)),
            backend=backend,
            scenarios=list(raw["scenarios"]),
            digest=hashlib.sha256(path.read_bytes()).hexdigest()[:16],
            schema_version=declared_schema,
        )


def _engine(backend: str) -> DecisionEngine:
    if backend == "injection_prone":
        return DecisionEngine(llm=InjectionProneLLM())
    return DecisionEngine()


def _scenarios(manifest: Manifest) -> list[dict[str, Any]]:
    clock = FixedClock(FIXED_TIMESTAMP)
    generator = GENERATORS[manifest.domain](seed=manifest.seed, clock=clock)
    scenarios = []
    for declared in manifest.scenarios:
        signals = generator.generate(int(declared.get("signal_count", 3)))
        actor = declared.get("actor") or {}
        scenarios.append(
            {
                "id": declared["id"],
                "expected_outcome": declared.get("expected_outcome"),
                "adversarial": bool(declared.get("adversarial", False)),
                "request": DecisionRequest(
                    request_id=declared["id"],
                    goal=declared["goal"],
                    signals=signals + _injected_signals(declared, clock),
                    policy_snapshot=declared["policy_snapshot"],
                    seed=manifest.seed,
                    actor=Actor(
                        id=str(actor.get("id", "unattributed")),
                        roles=tuple(actor.get("roles", ())),
                    ),
                ),
            }
        )
    return scenarios


def _injected_signals(declared: dict[str, Any], clock: FixedClock) -> list[Signal]:
    return [
        Signal(
            id=f"{declared['id']}-injected-{index}",
            source=str(injection.get("source", "untrusted")),
            content=str(injection["content"]),
            metadata={"untrusted": True},
            timestamp=clock(),
        )
        for index, injection in enumerate(declared.get("injected_signals", []))
    ]


def run_manifest(path: Path, output_dir: Path | None = None) -> dict[str, Any]:
    """Run one manifest and return its report, writing ``results.json`` beside the manifest."""
    manifest = Manifest.load(path)
    pipeline = DecisionPipeline(
        governance=GovernanceLayer(),
        decision_engine=_engine(manifest.backend),
        clock=FixedClock(FIXED_TIMESTAMP),
    )
    destination = output_dir or Path("benchmarks/results") / manifest.domain
    benchmark = Benchmark(
        pipeline,
        _scenarios(manifest),
        output_dir=str(destination / manifest.id),
        metadata={
            "benchmark_id": manifest.id,
            "manifest": path.name,
            "manifest_digest": manifest.digest,
            "label": manifest.label,
            "traces_to": manifest.traces_to,
            "seed": manifest.seed,
            "backend": manifest.backend,
            "python": platform.python_version(),
            "eads_version": _version(),
        },
        repeats=manifest.repeats,
        clock=FixedClock(FIXED_TIMESTAMP),
    )
    return benchmark.run()


def run_directory(
    manifest_dir: Path, output_dir: Path | None = None
) -> dict[str, dict[str, Any]]:
    """Run every ``*.json`` manifest in *manifest_dir*, keyed by benchmark id."""
    return {
        Manifest.load(path).id: run_manifest(path, output_dir)
        for path in sorted(manifest_dir.glob("*.json"))
    }


def _version() -> str:
    """The version of the code that produced a number.

    Read from the package rather than installed distribution metadata, which goes stale under an
    editable install and reported ``unknown`` for the wrong distribution name. A published number
    whose code version is unknown cannot be compared against a later one.
    """
    return __version__


__all__ = [
    "GENERATORS",
    "LABELS",
    "SCHEMA_VERSION",
    "Manifest",
    "ManifestError",
    "run_directory",
    "run_manifest",
]
