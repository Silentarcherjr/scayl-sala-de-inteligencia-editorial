import pytest

from scayl.contracts import ReviewState
from scayl.review.store import ReviewError, ReviewStore


@pytest.fixture
def store(tmp_path):
    return ReviewStore(tmp_path, snapshot_sha256="abc123")


def test_full_review_cycle_records_reviewer_time_hash_and_receipt(store, events):
    e = events["EVT-0003"]
    assert store.current_state(e.event_id) == ReviewState.NUEVO
    store.record(e, ReviewState.EN_REVISION, "editor-demo", "Abro revisión")
    rec = store.record(e, ReviewState.REQUIERE_EVIDENCIA, "editor-demo", "Falta fuente oficial (ACP)")
    assert store.current_state(e.event_id) == ReviewState.REQUIERE_EVIDENCIA
    assert len(rec.evidence_snapshot_sha256) == 64
    receipt = store.receipt(rec.review_id)
    assert receipt["snapshot_sha256"] == "abc123" and len(receipt["receipt_sha256"]) == 64
    assert len(store.pending_notion()) == 2


def test_invalid_transition_and_empty_justification_are_rejected(store, events):
    e = events["EVT-0001"]
    with pytest.raises(ReviewError):
        store.record(e, ReviewState.APROBADO_COMO_BORRADOR, "editor", "directo")  # must go through review
    with pytest.raises(ReviewError):
        store.record(e, ReviewState.EN_REVISION, "editor", "   ")


def test_evidence_hash_changes_when_evidence_changes(store, events):
    e = events["EVT-0001"]
    r1 = store.record(e, ReviewState.EN_REVISION, "a", "x")
    changed = e.model_copy(update={"title": e.title + " (actualizado)"})
    r2 = store.record(changed, ReviewState.DESCARTADO, "a", "y")
    assert r1.evidence_snapshot_sha256 != r2.evidence_snapshot_sha256
