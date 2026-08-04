"""Enforce the two claims this repository has broken before, as tests rather than review notes.

The research design forbade unlabelled stub modules on the default branch and required the safety
metrics to be assertions rather than observations. Both rules were violated silently, because both
were prose. Here they fail the suite.
"""

import importlib
import inspect
import json
from pathlib import Path
from typing import Any

import pytest

from eads.core.clock import FixedClock
from eads.core.pipeline import DecisionPipeline
from eads.core.types import DecisionRequest
from eads.decision.decision import DecisionEngine
from eads.evaluation import Benchmark
from eads.governance import GovernanceLayer
from eads.synthetic_data import SupplyChainGenerator

ROOT = Path(__file__).resolve().parent.parent
PAPERS = ROOT / "data" / "papers" / "papers.json"
LIMITATIONS = ROOT / "docs" / "limitations.md"
STUB_MARKER = "Stub:"


def _paper_modules() -> list[str]:
    with PAPERS.open() as handle:
        papers: list[dict[str, Any]] = json.load(handle)
    modules: set[str] = set()
    for paper in papers:
        modules.update(str(module) for module in paper["modules"])
    return sorted(modules)


def _documented_stubs() -> set[str]:
    """Names in the first column of the stub table in ``docs/limitations.md``."""
    names: set[str] = set()
    for line in LIMITATIONS.read_text().splitlines():
        if not line.startswith("|") or line.startswith("|--"):
            continue
        first = line.split("|")[1].strip()
        names.update(part.strip("` ") for part in first.split() if "`" in part)
    return names


def _public_classes(module_name: str) -> list[type]:
    module = importlib.import_module(module_name)
    return [
        obj
        for name, obj in vars(module).items()
        if inspect.isclass(obj) and not name.startswith("_") and obj.__module__.startswith("eads")
    ]


@pytest.mark.parametrize("module_name", _paper_modules())
def test_paper_traced_module_is_importable(module_name: str) -> None:
    """A module a paper claims cannot be missing from the package."""
    importlib.import_module(module_name)


@pytest.mark.parametrize("module_name", _paper_modules())
def test_stub_behavior_is_declared_in_the_docstring_and_documented(module_name: str) -> None:
    """A class that does not implement its paper's method must say so, and be listed as a stub.

    The rule is symmetric on purpose: a docstring that declares ``Stub:`` must appear in the stub
    table in ``docs/limitations.md``, so the label cannot be added in code and hidden from readers.
    """
    documented = _documented_stubs()
    declared_stubs = [
        cls for cls in _public_classes(module_name) if STUB_MARKER in (cls.__doc__ or "")
    ]
    for cls in declared_stubs:
        names = {cls.__module__, cls.__module__.rsplit(".", 1)[0], cls.__name__}
        assert names & documented, (
            f"{cls.__module__}.{cls.__name__} declares '{STUB_MARKER}' but no row of the stub "
            "table in docs/limitations.md names it"
        )


@pytest.mark.parametrize("module_name", _paper_modules())
def test_every_paper_traced_class_has_a_docstring(module_name: str) -> None:
    """No paper-traced class may be silent about what it does or does not implement."""
    for cls in _public_classes(module_name):
        assert (cls.__doc__ or "").strip(), f"{cls.__module__}.{cls.__name__} has no docstring"


def _scenarios() -> list[dict[str, Any]]:
    gen = SupplyChainGenerator(seed=3, clock=FixedClock())
    return [
        {
            "id": "gate-escalated",
            "expected_outcome": "escalated",
            "request": DecisionRequest(
                request_id="gate-escalated",
                goal="place replenishment order for SKU-1001",
                signals=gen.generate(3),
                policy_snapshot={
                    "max_order_quantity": 1000,
                    "unit_price": 10.0,
                    "region": "US",
                },
            ),
        },
        {
            "id": "gate-rejected",
            "expected_outcome": "rejected",
            "request": DecisionRequest(
                request_id="gate-rejected",
                goal="place replenishment order for SKU-1001",
                signals=gen.generate(3),
                policy_snapshot={"max_order_quantity": 5, "unit_price": 10.0, "region": "US"},
            ),
        },
    ]


def test_safety_metrics_are_assertions_not_observations(tmp_path: Path) -> None:
    """The metrics that mean "governance worked" gate every change, at their exact values.

    ``fallback_recovery_rate < 1.0`` means a decision that should have been withheld executed
    anyway; ``policy_compliance < 1.0`` means an outcome disagreed with its scenario's expectation;
    ``audit_completeness < 1.0`` means a decision happened without a full, attributable record.
    None of the three is allowed to drift.
    """
    report = Benchmark(
        DecisionPipeline(
            governance=GovernanceLayer(), decision_engine=DecisionEngine(), clock=FixedClock()
        ),
        _scenarios(),
        output_dir=str(tmp_path),
        repeats=2,
        clock=FixedClock(),
    ).run()
    assert report["fallback_recovery_rate"] == 1.0
    assert report["policy_compliance"] == 1.0
    assert report["audit_completeness"] == 1.0
    assert report["decision_consistency"] == 1.0
    assert report["evidence_grounding_rate"] == 1.0
