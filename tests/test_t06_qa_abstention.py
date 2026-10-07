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


# --- B-12 red-team findings (AP-013): general rules, phrased differently from the red-team set ---

def test_false_premise_figure_abstains_without_model(tmp_path):
    llm, backend = fake_llm(tmp_path, {"qa": {"abstain": False, "answer": []}})
    a = answer("¿Es cierto que la inflación de Panamá llegó a 12.4% en 2024?", bundle(), llm)
    assert a.abstained and "cifra planteada" in a.abstention_reason and backend.calls == []


def test_figure_present_in_evidence_is_not_a_false_premise():
    a = answer("¿La inflación de Panamá fue 0.7% en 2024?", bundle(), LLM(mode="template"))
    assert not a.abstained and a.citations[0].evidence_id == "wb:PAN:FP.CPI.TOTL.ZG:2024"


def test_current_value_with_only_historical_rows_abstains():
    for q in ("¿Cuál es hoy la inflación en Panamá?", "¿Qué inflación tiene Panamá actualmente?"):
        a = answer(q, bundle(), LLM(mode="template"))
        assert a.abstained and "histórica" in a.abstention_reason, q


def test_current_value_uses_latest_dated_recent_series():
    from tests.factories import recent
    b = bundle().model_copy(update={"indicators": bundle().indicators + [
        recent("INEC.IPC.VAR_INTERANUAL", "2026-07", 1.9, "inec", "%"),
        recent("INEC.IPC.VAR_INTERANUAL", "2026-08", 2.2, "inec", "%")]})
    a = answer("¿Cuál es la inflación actual en Panamá?", b, LLM(mode="template"))
    assert not a.abstained and a.citations[0].evidence_id == "ind:inec:INEC.IPC.VAR_INTERANUAL:2026-08"
    assert "2026-08" in a.answer[0].text  # always with its period, never "actual"


def test_year_must_belong_to_a_unit_about_the_topic():
    """A headline dated 2025 about the Canal does not answer 'inflation in 2025'."""
    b = bundle().model_copy(update={"news": [news("z", "Panamá: Canal ajusta calados",
                                                  pub=datetime(2025, 9, 1, tzinfo=UTC))]})
    a = answer("¿Inflación de Panamá en 2025?", b, LLM(mode="template"))
    assert a.abstained and "2025" in a.abstention_reason


def test_spanish_dates_retrieve_the_exact_day():
    from tests.factories import recent
    b = bundle().model_copy(update={"indicators": [recent("ACP.GATUN.NIVEL", f"2026-0{m}-28", 80.0 + m, "acp", "pies")
                                                   for m in range(1, 10)]})
    a = answer("¿Cuál fue el nivel del lago Gatún el 28 de septiembre de 2026?", b, LLM(mode="template"))
    assert a.citations[0].evidence_id == "ind:acp:ACP.GATUN.NIVEL:2026-09-28"
