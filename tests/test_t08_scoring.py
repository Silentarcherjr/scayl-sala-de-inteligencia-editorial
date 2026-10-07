"""T08: high-priority case exposes components and rule; priority does not authorize publication."""
from datetime import UTC, datetime, timedelta

import pytest

from scayl.contracts import EvidenceStatus, PriorityTier, Topic
from scayl.evidence.scoring import ScoringInput, load_rules, rank, rescore, score
from scayl.evidence.status import NOT_AUTHORIZED, recommended_action

CUTOFF = datetime(2025, 10, 1, tzinfo=UTC)


def _inp(**kw):
    base = {"mentions_panama": True, "is_tvn": False, "topic": Topic.LOGISTICA_CANAL, "topic_confidence": 0.9,
            "has_official_evidence": False, "latest_original_publication": CUTOFF - timedelta(hours=2),
            "cutoff": CUTOFF, "max_prior_similarity": None, "max_possible_independent": 1, "confirmed_independent": 0}
    base.update(kw)
    return ScoringInput(**base)


def test_weights_are_official_and_sum_100():
    assert load_rules()["weights"] == {"R": 30, "I": 25, "U": 20, "N": 15, "E": 10}


def test_score_is_reproducible_weighted_sum_with_rationale():
    p = score(_inp())
    c = p.components
    assert p.score == round(30 * c.R + 25 * c.I + 20 * c.U + 15 * c.N + 10 * c.E, 1)
    assert set(c.rationale) == {"R", "I", "U", "N", "E"}
    assert p.rules_version == "scoring-v1"
    assert score(_inp()) == p  # deterministic


def test_high_priority_with_insufficient_evidence_is_not_publishable():
    p = score(_inp())
    assert p.tier == PriorityTier.ALTO
    action = recommended_action(p.tier, EvidenceStatus.INSUFICIENTE, Topic.LOGISTICA_CANAL)
    assert NOT_AUTHORIZED in action and "Investigar" in action


@pytest.mark.parametrize("value,tier", [(39.9, "bajo"), (40.0, "medio"), (69.9, "medio"), (70.0, "alto")])
def test_official_tier_boundaries(value, tier):
    from scayl.evidence.scoring import tier_for
    assert tier_for(value, load_rules()).value == tier


def test_duplicates_do_not_raise_score():
    """T02 guard: more copies of the same provenance never add evidence or novelty."""
    one = score(_inp(max_possible_independent=1))
    many_copies_same_origin = score(_inp(max_possible_independent=1))  # 7 copies collapse to 1 group upstream
    assert one.score == many_copies_same_origin.score


def test_recirculated_story_uses_original_date_and_loses_urgency():
    """T03 guard: urgency comes from the ORIGINAL publication date."""
    fresh = score(_inp())
    old = score(_inp(latest_original_publication=datetime(2024, 3, 1, tzinfo=UTC)))
    assert old.components.U < 0.01 < fresh.components.U


def test_missing_date_gives_zero_urgency_not_error():
    assert score(_inp(latest_original_publication=None)).components.U == 0.0


def test_rank_tiebreak_urgency_then_id(events):
    ranked = rank(list(events.values()))
    scores = [e.priority.score for e in ranked]
    assert scores == sorted(scores, reverse=True)


def test_rescore_with_official_weights_reproduces_v1(events):
    official = load_rules()["weights"]
    again = rescore(list(events.values()), dict(official))
    assert [e.priority.rules_version for e in again] == ["scoring-v1"] * len(again)
    assert [(e.event_id, e.priority.score) for e in again] == [(e.event_id, e.priority.score)
                                                               for e in rank(list(events.values()))]


def test_rescore_custom_weights_are_versioned_and_validated(events):
    custom = rescore(list(events.values()), {"R": 10, "I": 10, "U": 10, "N": 10, "E": 60})
    assert all(e.priority.rules_version.startswith("scoring-v1+custom:") for e in custom)
    with pytest.raises(ValueError):
        rescore(list(events.values()), {"R": 50, "I": 50, "U": 50, "N": 0, "E": 0})


def test_gdelt_without_publication_date_uses_labelled_detection_proxy():
    """GDELT has seendate (detection) only: urgency must not collapse to 0, and the proxy is explicit."""
    det = CUTOFF - timedelta(hours=5)
    p = score(_inp(latest_original_publication=None, latest_detection=det))
    assert p.components.U > 0.8 and "detección" in p.components.rationale["U"]
    real = score(_inp(latest_original_publication=CUTOFF - timedelta(days=30), latest_detection=det))
    assert real.components.U < 0.01  # a real (old) publication date always wins over detection


def test_missing_both_dates_gives_zero_urgency():
    assert score(_inp(latest_original_publication=None, latest_detection=None)).components.U == 0.0
