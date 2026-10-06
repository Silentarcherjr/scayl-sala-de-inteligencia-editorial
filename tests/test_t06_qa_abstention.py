"""T06: a question the corpus cannot answer -> explicit abstention, no invented figure or citation."""
from datetime import UTC, datetime

from scayl.contracts import UIBundle
from scayl.gen.llm import LLM
from scayl.gen.qa import answer
from tests.factories import CUTOFF, news, quake, wb
from tests.fake_llm import fake_llm


def bundle():
    return UIBundle(snapshot_version="t", snapshot_cutoff_utc=CUTOFF, signals_total=3, signals_valid=3, events=[],
                    news=[news("a", "Canal de Panamá ajusta calados por sequía", medio="tvn-2.com")],
                    indicators=[wb("FP.CPI.TOTL.ZG", 2023, 1.5), wb("FP.CPI.TOTL.ZG", 2024, 0.7),
                                wb("SL.UEM.TOTL.ZS", 2024, None)],
                    seismic=[quake("us1", 4.6, datetime(2024, 5, 3, tzinfo=UTC))])


def test_unanswerable_question_abstains_before_calling_llm(tmp_path):
    llm, backend = fake_llm(tmp_path, {"qa": {"abstain": False, "answer": [
        {"text": "Llegaron 2.3 millones de turistas.", "tag": "HECHO", "evidence_ids": ["wb:PAN:FP.CPI.TOTL.ZG:2024"]}]}})
    a = answer("¿Cuántos turistas llegaron a Panamá en agosto de 2025?", bundle(), llm)
    assert a.abstained and not a.answer and not a.citations
    assert backend.calls == []  # deterministic pre-guard, no generation


def test_hallucinated_figure_is_removed_and_system_abstains(tmp_path):
    llm, _ = fake_llm(tmp_path, {"qa": {"abstain": False, "answer": [
        {"text": "La inflación de Panamá en 2024 fue 3.9%.", "tag": "HECHO",
         "evidence_ids": ["wb:PAN:FP.CPI.TOTL.ZG:2024"]}]}})
    a = answer("¿Cuál fue la inflación de Panamá en 2024?", bundle(), llm)
    assert a.abstained and any(i.code == "NUMBER_NOT_IN_EVIDENCE" for i in a.validation.issues)


def test_supported_answer_cites_evidence_with_year(tmp_path):
    llm, _ = fake_llm(tmp_path, {"qa": {"abstain": False, "answer": [
        {"text": "Según el Banco Mundial, la inflación de Panamá en 2024 fue 0.7%.", "tag": "HECHO",
         "evidence_ids": ["wb:PAN:FP.CPI.TOTL.ZG:2024"]}]}})
    a = answer("¿Cuál fue la inflación de Panamá en 2024?", bundle(), llm)
    assert not a.abstained and a.citations[0].evidence_id == "wb:PAN:FP.CPI.TOTL.ZG:2024"
    assert a.generated_by.mode == "live"


def test_historical_value_never_presented_as_current(tmp_path):
    llm, _ = fake_llm(tmp_path, {"qa": {"abstain": False, "answer": [
        {"text": "La inflación actual de Panamá es 0.7%.", "tag": "HECHO", "evidence_ids": ["wb:PAN:FP.CPI.TOTL.ZG:2024"]}]}})
    a = answer("¿Cuál fue la inflación de Panamá en 2024?", bundle(), llm)
    assert a.abstained and any(i.code == "TEMPORAL_PRESENT" for i in a.validation.issues)


def test_null_value_is_not_zero_and_abstains():
    a = answer("¿Cuál fue el desempleo de Panamá en 2024?", bundle(), LLM(mode="template"))
    assert a.abstained and "nulo" in a.abstention_reason


def test_cache_mode_reuses_live_output_identically(tmp_path):
    resp = {"qa": {"abstain": False, "answer": [
        {"text": "Según el Banco Mundial, la inflación de Panamá en 2023 fue 1.5%.", "tag": "HECHO",
         "evidence_ids": ["wb:PAN:FP.CPI.TOTL.ZG:2023"]}]}}
    live, _ = fake_llm(tmp_path, resp)
    first = answer("¿Cuál fue la inflación de Panamá en 2023?", bundle(), live)
    cached = answer("¿Cuál fue la inflación de Panamá en 2023?", bundle(),
                    LLM(mode="cache", cache_dir=tmp_path / "llm-cache", model="fake-model"))
    assert cached.generated_by.mode == "cache" and [s.text for s in cached.answer] == [s.text for s in first.answer]


def test_template_mode_is_extractive_and_labelled():
    a = answer("¿Cuál fue la inflación de Panamá en 2024?", bundle(), LLM(mode="template"))
    assert not a.abstained and a.citations
    assert any(i.code == "EXTRACTIVE_MODE" for i in a.validation.issues)
