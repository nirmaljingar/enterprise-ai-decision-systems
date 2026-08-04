import importlib.util
import json
import tempfile
from pathlib import Path

from eads.core.pipeline import DecisionPipeline
from eads.core.types import DecisionRequest, Signal
from eads.decision.adapters import NaiveForecaster
from eads.decision.decision import DecisionEngine
from eads.evaluation import Benchmark
from eads.modernization.modernization import ModernizationPipeline
from eads.synthetic_data import (
    CustomerSupportGenerator,
    FinanceGenerator,
    HealthcareGenerator,
    ITOperationsGenerator,
    SupplyChainGenerator,
)


def _stable_signal_key(signal):
    return (signal.id, signal.source, signal.content, signal.metadata)


def test_supply_chain_generator_deterministic():
    g1 = SupplyChainGenerator(seed=5)
    g2 = SupplyChainGenerator(seed=5)
    assert [_stable_signal_key(s) for s in g1.generate(3)] == [
        _stable_signal_key(s) for s in g2.generate(3)
    ]


def test_domain_generators_produce_typed_signals():
    generators = [
        ("synthetic_healthcare", HealthcareGenerator),
        ("synthetic_finance", FinanceGenerator),
        ("synthetic_it_operations", ITOperationsGenerator),
        ("synthetic_customer_support", CustomerSupportGenerator),
    ]
    for expected_source, cls in generators:
        gen = cls(seed=1)
        signals = gen.generate(2)
        assert len(signals) == 2
        assert all(s.source == expected_source for s in signals)


def test_naive_forecaster_extracts_last_integer():
    request = DecisionRequest(
        request_id="f1",
        goal="forecast demand",
        signals=[
            Signal(id="s1", source="test", content="Demand was 100"),
            Signal(id="s2", source="test", content="Demand is 250"),
        ],
    )
    result = NaiveForecaster().forecast(request)
    assert result["predicted_demand"] == 250
    assert result["method"] == "naive_last_value"


def test_decision_engine_uses_forecaster():
    request = DecisionRequest(
        request_id="d2",
        goal="order SKU-1001",
        signals=[Signal(id="s1", source="test", content="Demand is 300")],
    )
    engine = DecisionEngine(forecaster=NaiveForecaster())
    candidate = engine.generate(request)
    assert candidate.expected_outcome.get("predicted_demand") == 300


def test_benchmark_writes_results_json():
    gen = SupplyChainGenerator(seed=3)
    engine = DecisionEngine()
    pipeline = DecisionPipeline(decision_engine=engine)
    scenarios = [
        {
            "id": "b-1",
            "request": DecisionRequest(
                request_id="b-1",
                goal="replenish SKU-1001",
                signals=gen.generate(2),
            ),
        }
    ]
    with tempfile.TemporaryDirectory() as tmpdir:
        benchmark = Benchmark(
            pipeline,
            scenarios,
            output_dir=tmpdir,
            metadata={"test": True},
        )
        report = benchmark.run()
        assert "results" in report
        result_file = Path(tmpdir) / "results.json"
        assert result_file.exists()
        saved = json.loads(result_file.read_text())
        assert saved["metadata"]["test"] is True
        assert "policy_compliance" in saved


def test_modernization_integration_in_pipeline():
    legacy_signal = Signal(
        id="legacy-1",
        source="monolith",
        content="import os\nimport sys",
        metadata={"source_type": "legacy_code"},
    )
    regular_signal = Signal(id="s1", source="test", content="stock low")
    pipeline = DecisionPipeline(modernization=ModernizationPipeline())
    request = DecisionRequest(
        request_id="m1",
        goal="modernize and decide",
        signals=[legacy_signal, regular_signal],
    )
    record = pipeline.run(request)
    step_names = [step["step"] for step in record.trace]
    assert "modernize" in step_names
    assert any("modernization_" in (ref or "") for ref in record.decision.evidence_refs)


def _solver_available(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def test_scipy_solver_when_installed():
    if not _solver_available("scipy"):
        return
    from eads.decision.adapters import SciPySolver

    request = DecisionRequest(
        request_id="sol-1",
        goal="order",
        signals=[],
        policy_snapshot={"max_order_quantity": 500},
    )
    result = SciPySolver().optimize(request)
    assert result["solver_status"] == "success"
    assert result["order_quantity"] <= 500


def test_pulp_solver_when_installed():
    if not _solver_available("pulp"):
        return
    from eads.decision.adapters import PulpSolver

    request = DecisionRequest(
        request_id="sol-2",
        goal="order",
        signals=[],
        policy_snapshot={"max_order_quantity": 400},
    )
    result = PulpSolver().optimize(request)
    assert result["order_quantity"] <= 400


def test_ortools_solver_when_installed():
    if not _solver_available("ortools"):
        return
    from eads.decision.adapters import OrtoolsSolver

    request = DecisionRequest(
        request_id="sol-3",
        goal="order",
        signals=[],
        policy_snapshot={"max_order_quantity": 300},
    )
    result = OrtoolsSolver().optimize(request)
    assert result["order_quantity"] <= 300


def test_sktime_forecaster_when_installed():
    if not _solver_available("sktime"):
        return
    from eads.decision.adapters import SKTimeForecaster

    request = DecisionRequest(
        request_id="fc-1",
        goal="forecast",
        signals=[
            Signal(id="s1", source="test", content="100"),
            Signal(id="s2", source="test", content="120"),
        ],
    )
    result = SKTimeForecaster().forecast(request)
    assert "predicted_demand" in result
