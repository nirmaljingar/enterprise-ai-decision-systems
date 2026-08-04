"""Behavioral tests for evidence-grounded trust scoring.

The stub reported the candidate's own confidence, so it could not fail any test that mattered: a
hallucinated citation, an invented quantity, and a claim lifted from an injected email all scored
identically to a fully supported decision. Each of those is a separate assertion here.

One property is asserted deliberately in the negative: a low trust score must not block anything.
Trust that gates execution is a second, weaker policy engine, and the fail-closed checks are what
decide outcomes.
"""

from eads.core.types import DecisionCandidate, Evidence, ProposedAction
from eads.governance.governance import GovernanceLayer
from eads.governance.trust import UNVERIFIABLE_CEILING, TrustScorer

POLICY = {"max_order_quantity": 1000, "unit_price": 1.0, "region": "US"}


def evidence(
    identifier: str,
    quantities: tuple[float, ...] = (),
    confidence: float = 1.0,
    imperative: bool = False,
    trusted: bool = True,
) -> Evidence:
    return Evidence(
        id=identifier,
        signal_ids=[f"sig_{identifier}"],
        claim=f"claim {identifier}",
        confidence=confidence,
        source_refs=[f"sig_{identifier}"],
        extracted_by="test",
        quantities=quantities,
        imperative=imperative,
        trusted=trusted,
    )


def candidate(quantity: int | None = 100, refs: tuple[str, ...] = ("ev1",)) -> DecisionCandidate:
    return DecisionCandidate(
        plan_id="p",
        actions=[
            ProposedAction(
                type="order", raw_value="order_quantity=100", quantity=quantity,
                region="US", parsed=True,
            )
        ],
        evidence_refs=list(refs),
        confidence=1.0,
    )


def test_a_fully_supported_decision_scores_highest() -> None:
    assessment = TrustScorer().assess(candidate(), evidence=[evidence("ev1", (100.0,))])
    assert assessment.score == 1.0
    assert assessment.reasons == ()


def test_the_candidates_self_declared_confidence_is_not_an_input() -> None:
    """Asking a model how much to trust it is circular, and injection inflates that number."""
    supported = candidate()
    supported.confidence = 0.01
    high = TrustScorer().assess(supported, evidence=[evidence("ev1", (100.0,))])
    supported.confidence = 1.0
    same = TrustScorer().assess(supported, evidence=[evidence("ev1", (100.0,))])
    assert high.score == same.score == 1.0


def test_a_citation_that_does_not_resolve_is_penalized() -> None:
    """A reference to evidence that does not exist is the most direct hallucination on record."""
    assessment = TrustScorer().assess(
        candidate(refs=("ev1", "ev-invented")), evidence=[evidence("ev1", (100.0,))]
    )
    assert assessment.score == 0.5
    assert "citations_do_not_resolve" in assessment.reasons


def test_a_quantity_no_cited_claim_reports_is_penalized() -> None:
    """A figure nobody reported is the signature of a number the model invented."""
    assessment = TrustScorer().assess(candidate(), evidence=[evidence("ev1", (7.0,))])
    assert assessment.score < 1.0
    assert "proposed_quantity_absent_from_cited_evidence" in assessment.reasons


def test_citing_nothing_is_penalized() -> None:
    assessment = TrustScorer().assess(candidate(refs=()), evidence=[evidence("ev1", (100.0,))])
    assert "no_evidence_cited" in assessment.reasons
    assert assessment.score < 1.0


def test_citing_an_untrusted_or_instruction_shaped_claim_lowers_trust() -> None:
    injected = evidence("ev1", (100.0,), imperative=True, trusted=False)
    assessment = TrustScorer().assess(candidate(), evidence=[injected])
    assert set(assessment.reasons) == {
        "cited_untrusted_source",
        "cited_instruction_shaped_claim",
    }
    assert assessment.score < TrustScorer().assess(
        candidate(), evidence=[evidence("ev1", (100.0,))]
    ).score


def test_contradictory_cited_evidence_lowers_trust() -> None:
    assessment = TrustScorer().assess(
        candidate(refs=("ev1", "ev2")),
        evidence=[evidence("ev1", (100.0,)), evidence("ev2", (900.0,))],
    )
    assert "cited_evidence_contradicts_itself" in assessment.reasons


def test_weak_evidence_lowers_trust_proportionally() -> None:
    strong = TrustScorer().assess(candidate(), evidence=[evidence("ev1", (100.0,), 1.0)])
    weak = TrustScorer().assess(candidate(), evidence=[evidence("ev1", (100.0,), 0.4)])
    assert weak.score < strong.score


def test_an_unparseable_action_is_penalized_even_when_supported() -> None:
    unparsed = DecisionCandidate(
        plan_id="p",
        actions=[ProposedAction(type="unknown", raw_value="ship it", parsed=False)],
        evidence_refs=["ev1"],
        confidence=1.0,
    )
    assessment = TrustScorer().assess(unparsed, evidence=[evidence("ev1", (100.0,))])
    assert "action_not_parsed" in assessment.reasons
    assert assessment.score == 0.5


def test_no_evidence_at_all_is_unverifiable_rather_than_trusted() -> None:
    assessment = TrustScorer().assess(candidate())
    assert assessment.score == UNVERIFIABLE_CEILING
    assert "no_evidence_supplied" in assessment.reasons


def test_a_candidate_proposing_no_quantity_is_not_penalized_for_one() -> None:
    assessment = TrustScorer().assess(candidate(quantity=None), evidence=[evidence("ev1")])
    assert "proposed_quantity_absent_from_cited_evidence" not in assessment.reasons


def test_low_trust_does_not_block_a_policy_compliant_action() -> None:
    """Trust that gates execution is a second, weaker policy engine."""
    verdict = GovernanceLayer().review(
        candidate(), POLICY, evidence=[evidence("ev1", (7.0,), confidence=0.1)]
    )
    assert verdict.outcome == "approved"
    assert verdict.trust_score < 0.5
    assert verdict.trust_reasons


def test_the_verdict_carries_the_reason_for_every_deduction() -> None:
    verdict = GovernanceLayer().review(
        candidate(refs=("ev-invented",)), POLICY, evidence=[evidence("ev1", (100.0,))]
    )
    assert "citations_do_not_resolve" in verdict.trust_reasons
