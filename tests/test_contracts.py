import json
from pathlib import Path

from scayl.contracts import (
    PriorityTier,
    ReviewState,
    UIBundle,
    can_transition,
)

FIXTURE = Path(__file__).parent / "fixtures" / "ui_bundle.example.json"


def test_fixture_matches_contract():
    bundle = UIBundle.model_validate(json.loads(FIXTURE.read_text(encoding="utf-8")))
    assert bundle.events, "fixture must contain events"
    assert all(e.synthetic for e in bundle.events), "fixture content must be labelled synthetic"


def test_priority_is_independent_of_evidence_status():
    bundle = UIBundle.model_validate(json.loads(FIXTURE.read_text(encoding="utf-8")))
    pairs = {(e.priority.tier, e.evidence_status) for e in bundle.events}
    assert (PriorityTier.ALTO, "insuficiente") in {(t, s.value) for t, s in pairs}


def test_approval_is_not_publication_and_transitions_are_guarded():
    assert can_transition(ReviewState.EN_REVISION, ReviewState.APROBADO_COMO_BORRADOR)
    assert not can_transition(ReviewState.NUEVO, ReviewState.APROBADO_COMO_BORRADOR)
    assert "publicado" not in {s.value for s in ReviewState}
