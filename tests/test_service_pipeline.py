"""T10 (core half): the whole flow runs offline from local data, without LLM or network."""
import json
import socket

import pytest

from scayl import service
from scayl.contracts import ReviewState, Topic, UIBundle
from scayl.pipeline import build_bundle, write_outputs
from tests.factories import CUTOFF, news, wb


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    def guard(*a, **k):
        raise OSError("network disabled in test (T10)")
    monkeypatch.setattr(socket, "create_connection", guard)
    monkeypatch.setattr(socket.socket, "connect", guard)


@pytest.fixture
def svc(tmp_path, monkeypatch):
    monkeypatch.setenv("SCAYL_STATE_DIR", str(tmp_path / "state"))
    # This fixture exercises a fresh installation without evaluation artifacts (B-08).
    monkeypatch.setattr(service, "ROOT", tmp_path)
    monkeypatch.setattr(service, "bundle_path", lambda: service.FIXTURE)
    service.reload()
    yield service
    service.reload()


def test_service_over_fixture_end_to_end(svc):
    b = svc.load_bundle()
    e = b.events[0]
    assert svc.get_event(e.event_id).event_id == e.event_id
    pkg = svc.generate_package(e.event_id, mode="template")
    assert pkg.generated_by.mode == "template"
    live = svc.generate_package(e.event_id, mode="live")
    assert any(i.code == "LLM_FALLBACK" for i in live.validation.issues)  # no Ollama offline
    svc.review(e.event_id, ReviewState.EN_REVISION, "editor-demo", "Revisar")
    assert svc.current_state(e.event_id) == ReviewState.EN_REVISION
    assert svc.trust_lab()["status"] == "no medido"
    answer = svc.ask("¿Cuántos turistas llegaron en agosto?")
    assert answer.abstained and not answer.answer and not answer.citations


def test_pipeline_builds_bundle_and_fichas_offline(tmp_path):
    items = [news("a", "Inflación en Panamá sube a 1.2%", medio="x.com"),
             news("b", "Inflación en Panamá llega a 2.1%", medio="y.com"),
             news("c", "Canal de Panamá ajusta calados", medio="z.com")]
    bundle = build_bundle(items, [wb("FP.CPI.TOTL.ZG", 2024, 0.7)], [], CUTOFF, "test", signals_total=4,
                          classify=lambda xs: [(Topic.ECONOMIA, 0.9), (Topic.ECONOMIA, 0.8), (Topic.LOGISTICA_CANAL, 0.9)],
                          cluster=lambda xs: [["a", "b"], ["c"]])
    assert len(bundle.events) == 2 and bundle.signals_total == 4 and bundle.signals_valid == 3
    write_outputs(bundle, tmp_path)
    UIBundle.model_validate(json.loads((tmp_path / "bundle.json").read_text(encoding="utf-8")))
    fichas = [json.loads(line) for line in (tmp_path / "fichas.jsonl").read_text(encoding="utf-8").splitlines()]
    assert {f["id_caso"] for f in fichas} == {e.event_id for e in bundle.events}
    assert all(set(f) >= {"id_caso", "modalidad", "ids_fuente", "afirmaciones", "citas", "puntaje", "componentes",
                          "estado_evidencia", "borrador", "estado_revision"} for f in fichas)


def test_default_cutoff_follows_organizer_clarification():
    from datetime import UTC, datetime

    from scayl.pipeline import data_window_cutoff
    assert data_window_cutoff() == datetime(2026, 10, 1, tzinfo=UTC)


def test_review_records_the_package_actually_shown_and_exposes_receipt(svc):
    e = svc.load_bundle().events[0]
    shown = svc.generate_package(e.event_id, mode="template")
    rec = svc.review(e.event_id, ReviewState.EN_REVISION, "editor-demo", "Reviso el borrador generado", package=shown)
    assert rec.package_id == shown.package_id
    r = svc.receipt(rec.review_id)
    assert r["package_id"] == shown.package_id and len(r["package_sha256"]) == 64 and len(r["receipt_sha256"]) == 64
    other = svc.load_bundle().events[1]
    with pytest.raises(ValueError):
        svc.review(other.event_id, ReviewState.EN_REVISION, "x", "y", package=shown)
