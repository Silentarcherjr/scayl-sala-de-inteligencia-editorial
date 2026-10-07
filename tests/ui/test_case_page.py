"""A-03 integration tests: synthetic inputs and isolated review storage."""
import hashlib
import json
from pathlib import Path
from unittest.mock import Mock

import pytest
from streamlit.testing.v1 import AppTest

from scayl import service
from scayl.contracts import ReviewState
from tests.factories import news

PAGE = Path(__file__).resolve().parents[2] / "app/pages/1_Ficha_de_Caso.py"


@pytest.fixture
def page(monkeypatch, tmp_path, bundle):
    service.reload()
    monkeypatch.setenv("SCAYL_STATE_DIR", str(tmp_path / "state"))
    monkeypatch.setenv("SCAYL_LLM_MODE", "template")
    monkeypatch.setattr(service, "load_bundle", lambda: bundle)
    yield AppTest.from_file(str(PAGE), default_timeout=10)
    service._store.cache_clear()


def values(elements):
    return "\n".join(str(item.value) for item in elements)


def button(page, label):
    return next(item for item in page.button if item.label == label)


@pytest.mark.parametrize("event_id", ["EVT-0001", "EVT-0002", "EVT-0003"])
def test_all_six_tabs_render_synthetic_cases(page, event_id):
    page.query_params["event_id"] = event_id
    page.run()
    assert not page.exception
    assert [tab.label for tab in page.tabs] == [
        "Evento", "Fuentes", "Evidencia", "Vacíos", "Producir", "Revisión"
    ]
    assert "SINTÉTICO" in values(page.warning)
    assert "Puntaje de atención P" == page.metric[0].label
    assert "Estado de evidencia:" in values(page.info)
    assert "Prioridad alta NO habilita publicación" in values(page.warning)


def test_conflict_preserves_both_versions_and_historical_evidence(page):
    page.query_params["event_id"] = "EVT-0002"
    page.run()
    evidence = page.tabs[2]
    assert "Versión A" in values(evidence.subheader)
    assert "Versión B" in values(evidence.subheader)
    assert "1.2%" in values(evidence.text) and "2.1%" in values(evidence.text)
    assert "Verificación pendiente" in values(evidence.warning)
    assert "Dato histórico — 2024" in values(evidence.warning)
    card = next(item for item in evidence.expander if "wb:PAN:FP.CPI.TOTL.ZG:2024" in item.label)
    assert "Campo: valor" in values(card.text)
    assert "Valor: 0.7" in values(card.text)
    assert "Período: 2024" in values(card.text)
    assert "URL: https://data.worldbank.org/" in values(card.text)


def test_member_headlines_null_dates_and_security_notice(page, bundle):
    bundle.news = [news("syn-n001", "[SINTÉTICO] Titular miembro", pub=None),
                   news("outside", "[SINTÉTICO] No pertenece al caso")]
    bundle.events[0].security_flags = ["posible_inyeccion:news:syn-n001"]
    bundle.events[0].is_recirculated = True
    page.run()
    assert not page.exception
    assert "Titular miembro" in values(page.tabs[0].text)
    assert "No pertenece" not in values(page.tabs[0].text)
    assert "Publicación: no disponible" in values(page.caption)
    assert "2025-09-11 23:00 Panamá" in values(page.text)
    assert "Noticia recirculada" in values(page.warning)
    assert "fuente con instrucciones sospechosas, tratada como dato" in values(page.warning)


def test_review_requires_justification_and_persists_valid_transition(page):
    page.run()
    assert page.selectbox[1].options == ["en_revision"]
    page.text_input[0].set_value("LowCrime")
    page.text_area[0].set_value("   ")
    button(page, "Guardar revisión").click().run()
    assert "La justificación es obligatoria" in values(page.error)
    assert service.review_history("EVT-0001") == []
    page.text_area[0].set_value("Verificar daños antes de producir")
    button(page, "Guardar revisión").click().run()
    assert not page.exception
    assert service.current_state("EVT-0001") == ReviewState.EN_REVISION
    record = service.review_history("EVT-0001")[0]
    assert record.reviewer == "LowCrime" and record.package_id == "PKG-0001-v1"
    assert record.evidence_snapshot_sha256 in values(page.caption)
    assert set(page.selectbox[1].options) == {
        "aprobado_como_borrador", "descartado", "requiere_evidencia"
    }


def test_review_rechecks_transition_after_concurrent_change(page, monkeypatch):
    page.run()
    page.text_input[0].set_value("LowCrime")
    page.text_area[0].set_value("Revisar fuentes")
    current = Mock(side_effect=[ReviewState.NUEVO, ReviewState.EN_REVISION])
    record = Mock()
    monkeypatch.setattr(service, "current_state", current)
    monkeypatch.setattr(service, "review", record)
    button(page, "Guardar revisión").click().run()
    assert "Transición no permitida" in values(page.error)
    record.assert_not_called()


def test_generated_package_citations_and_review_identity(page):
    page.run()
    button(page, "Generar").click().run()
    assert not page.exception
    assert "Modo: template" in values(page.caption)
    assert any("Afirmación CLM-0001-001" == item.label for item in page.expander)
    assert "ID de evidencia: usgs:syn0001" in values(page.text)
    assert not button(page, "Guardar revisión").disabled
    shown = page.session_state["case-package:fixture-synthetic-0:EVT-0001"]
    page.text_input[0].set_value("LowCrime")
    page.text_area[0].set_value("Reviso el paquete generado visible")
    button(page, "Guardar revisión").click().run()
    assert not page.exception
    record = service.review_history("EVT-0001")[0]
    receipt = service.receipt(record.review_id)
    payload = json.dumps(shown.model_dump(mode="json"), sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    assert receipt["package_id"] == shown.package_id
    assert receipt["package_sha256"] == hashlib.sha256(payload.encode()).hexdigest()
    assert receipt["receipt_sha256"] in values(page.caption)
    assert page.get("download_button")[0].label == "Descargar recibo JSON"
    button(page, "Volver al paquete del snapshot").click().run()
    assert not button(page, "Guardar revisión").disabled


def test_missing_receipt_keeps_review_history_visible(page, monkeypatch):
    service.review("EVT-0001", ReviewState.EN_REVISION, "LowCrime", "Verificar fuentes")
    monkeypatch.setattr(service, "receipt", Mock(side_effect=FileNotFoundError))
    page.run()
    assert not page.exception
    assert "Verificar fuentes" in values(page.text)
    assert "Recibo no disponible" in values(page.warning)


def test_empty_bundle(page, bundle):
    bundle.events = []
    page.run()
    assert not page.exception
    assert "No hay casos disponibles" in values(page.info)
