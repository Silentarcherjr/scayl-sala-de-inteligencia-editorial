from pathlib import Path
from unittest.mock import Mock

import pytest
from streamlit.testing.v1 import AppTest

from scayl import service
from scayl.contracts import ClaimType, QAAnswer, TaggedSentence

PAGE = Path(__file__).resolve().parents[2] / "app/pages/2_Consultas.py"


@pytest.fixture
def query_page(bundle, monkeypatch):
    monkeypatch.setattr(service, "load_bundle", lambda: bundle)
    return AppTest.from_file(str(PAGE.parents[1] / "Home.py"), default_timeout=15).run().switch_page(
        "pages/2_Consultas.py")


def click(page, label):
    next(b for b in page.button if b.label == label).click().run()


def text(elements):
    return "\n".join(str(item.value) for item in elements)


@pytest.mark.parametrize("mode", ["live", "cache", "template"])
def test_grounded_answer_shows_real_mode_and_exact_citation(query_page, bundle, monkeypatch, mode):
    ref = bundle.events[0].official_evidence[0]
    meta = bundle.packages[0].generated_by.model_copy(update={"mode": mode})
    answer = QAAnswer(question="Magnitud del sismo", abstained=False,
                      answer=[TaggedSentence(text="Magnitud 4.6", tag=ClaimType.HECHO,
                                             claim_ids=[ref.evidence_id])],
                      citations=[ref], validation=bundle.packages[0].validation, generated_by=meta)
    ask = Mock(return_value=answer)
    monkeypatch.setattr(service, "ask", ask)
    query_page.run()
    query_page.text_input[0].set_value("Magnitud del sismo")
    click(query_page, "Consultar")
    assert not query_page.exception
    ask.assert_called_once_with("Magnitud del sismo", mode="cache")
    assert f"Modo de generación: {mode}" in text(query_page.caption)
    assert "HECHO" in text(query_page.markdown)
    assert "Campo: magnitude" in text(query_page.text)
    assert "Valor: 4.6" in text(query_page.text)


def test_abstention_never_shows_answer_text(query_page, bundle, monkeypatch):
    answer = QAAnswer(question="Sin evidencia", abstained=True, abstention_reason="Falta el período 2035",
                      needed_information=["Estadísticas oficiales del período"],
                      validation=bundle.packages[0].validation, generated_by=bundle.packages[0].generated_by)
    monkeypatch.setattr(service, "ask", Mock(return_value=answer))
    query_page.run()
    click(query_page, "¿Qué pasa si no hay evidencia?")
    assert "2035" in query_page.text_input[0].value
    click(query_page, "Consultar")
    assert not query_page.exception
    assert "No hay evidencia suficiente en el corpus" in text(query_page.warning)
    assert "Falta el período 2035" in text(query_page.text)
    assert "Estadísticas oficiales" in text(query_page.text)
    assert "Modo de generación: template" in text(query_page.caption)


def test_empty_question_does_not_call_service(query_page, monkeypatch):
    ask = Mock()
    monkeypatch.setattr(service, "ask", ask)
    query_page.run()
    click(query_page, "Consultar")
    ask.assert_not_called()
    assert "Escribe una pregunta" in text(query_page.error)


def test_jury_routes_to_existing_cases_or_explicit_missing_case(query_page):
    query_page.run()
    for label in ["¿De dónde viene esta cifra y de qué año es?",
                  "Si 5 medios replican una agencia, ¿cuántas fuentes independientes hay?"]:
        click(query_page, label)
        assert not query_page.exception
        assert query_page.get("page_link")[0].label == "Abrir caso EVT-0001"
    click(query_page, "Fuente con instrucciones maliciosas")
    assert "no contiene un caso" in text(query_page.info)
    assert "Trust Lab" in query_page.get("page_link")[0].label


def test_jury_flags_synthetic_injection_case(query_page, bundle):
    bundle.events[2].security_flags = ["posible_inyeccion"]
    query_page.run()
    click(query_page, "Fuente con instrucciones maliciosas")
    assert not query_page.exception
    assert "tratada como dato" in text(query_page.warning)
    assert query_page.get("page_link")[0].label == "Abrir caso EVT-0003"
