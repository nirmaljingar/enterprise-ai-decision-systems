from eads.agents.agents import Agent
from eads.core.types import (
    DecisionCandidate,
    DecisionRequest,
    Evidence,
    ProposedAction,
    Signal,
)
from eads.decision.decision import DecisionEngine
from eads.governance import GovernanceLayer
from eads.knowledge_ingestion.ingestion import IngestionPipeline
from eads.modernization.modernization import ModernizationPipeline
from eads.reasoning.reasoning import ReasoningEngine
from eads.synthetic_data import SupplyChainGenerator


def test_modernization_analyzes_code():
    code = "import os\nimport sys\nprint('hello')"
    pipeline = ModernizationPipeline()
    result = pipeline.analyze(code)
    assert "os" in result["dependencies"]
    assert "sys" in result["dependencies"]
    assert len(result["proposed_services"]) > 0


def test_knowledge_ingestion_extracts_evidence():
    signals = [Signal(id="s1", source="email", content="Demand up 10%")]
    pipeline = IngestionPipeline()
    evidence = pipeline.ingest(signals)
    assert len(evidence) == 1
    assert evidence[0].claim == "Demand up 10%"


def test_reasoning_produces_plan():
    evidence = [
        Evidence(
            id="e1",
            signal_ids=["s1"],
            claim="Demand up",
            confidence=0.9,
            source_refs=["s1"],
            extracted_by="test",
        )
    ]
    plan = ReasoningEngine().plan(evidence, "replenish SKU-1001")
    assert plan.goal == "replenish SKU-1001"
    assert "e1" in plan.evidence_refs


def test_agent_act_and_swarm():
    agent = Agent(name="a1", role="planner")
    msg = agent.act([])
    assert msg.sender == "a1"
    assert msg.role == "planner"
    swarm = Agent.swarm([], ["tool1"])
    assert any(m.sender == "swarm" for m in swarm)


def test_decision_engine_generates_candidate():
    request = DecisionRequest(
        request_id="d1",
        goal="order SKU-1001",
        signals=[Signal(id="s1", source="test", content="stock low")],
    )
    engine = DecisionEngine()
    candidate = engine.generate(request)
    assert candidate.actions[0].type == "order"
    assert candidate.actions[0].parsed
    assert candidate.confidence > 0


def test_governance_blocks_high_value_order():
    g = GovernanceLayer()
    candidate = DecisionCandidate(
        plan_id="p1",
        actions=[
            ProposedAction(
                type="order",
                raw_value="order_quantity=600",
                quantity=600,
                region="US",
                parsed=True,
            )
        ],
        confidence=0.5,
    )
    verdict = g.review(candidate, {"unit_price": 10.0})
    assert not verdict.approved
    assert "manager_approval_required" in verdict.required_approvals


def _signal_key(signal):
    return (signal.id, signal.source, signal.content, signal.metadata)


def test_synthetic_data_is_deterministic():
    g1 = SupplyChainGenerator(seed=7)
    g2 = SupplyChainGenerator(seed=7)
    assert [_signal_key(s) for s in g1.generate(3)] == [_signal_key(s) for s in g2.generate(3)]
