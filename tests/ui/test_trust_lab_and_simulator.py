"""A-05 and A-10 on synthetic inputs."""
import json
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from scayl import service

ROOT = Path(__file__).resolve().parents[2]
LAB = ROOT / "app/pages/3_Trust_Lab.py"
SIM = ROOT / "app/pages/4_Simulador_de_pesos.py"


def values(elements):
    return "\n".join(str(item.value) for item in elements)


@pytest.fixture
def isolated(monkeypatch, tmp_path, bundle):
    service.reload()
    monkeypatch.setenv("SCAYL_STATE_DIR", str(tmp_path / "state"))
    monkeypatch.setattr(service, "load_bundle", lambda: bundle)
    yield tmp_path
    service._store.cache_clear()


def test_trust_lab_without_runs_says_not_measured(isolated, monkeypatch):
    monkeypatch.setattr(service, "trust_lab", lambda: {"status": "no medido", "metrics": {}, "tests": {}})
    monkeypatch.setattr(service, "generation_summary", lambda: {"status": "no medido", "packages": 0})
    at = AppTest.from_file(str(LAB), default_timeout=10).run()
    assert not at.exception
    text = values(at.text)
    assert "T01" in text and "T10" in text and "sin ejecución registrada" in text
    assert "Cobertura de citas (evaluación): no medido" in text
    assert "Precision@5 frente al editor: no medido (exploratoria)" in text
    assert "no medido" in values(at.info)


def test_trust_lab_shows_numerator_denominator_and_generation(isolated, monkeypatch):
    lab = {"run_at": "2026-10-08T10:00Z", "hardware": "AMD RX 9060 XT",
           "metrics": {"abstention_correct": {"num": 9, "den": 10}, "citation_coverage": {"num": 40, "den": 40}},
           "tests": {"T06": {"status": "PASA", "evidence": "tests/test_t06_qa_abstention.py"}}}
    gen = {"status": "medido", "packages": 3, "llm_packages": 2, "fallbacks": 1, "models": ["ollama:qwen3:8b"],
           "prompt_versions": ["studio-v1"], "sentences_generated": 20, "sentences_kept": 17,
           "removed_by_code": {"NUMBER_NOT_IN_EVIDENCE": 2}, "citation_coverage": {"num": 15, "den": 15},
           "attribution": {"candidates": 4, "preserved_before": 2, "preserved_after": 4},
           "latency_ms": {"n": 2, "median": 9000, "p95": 12000}, "tokens_out": 900, "cost_usd": 0.0}
    monkeypatch.setattr(service, "trust_lab", lambda: lab)
    monkeypatch.setattr(service, "generation_summary", lambda: gen)
    at = AppTest.from_file(str(LAB), default_timeout=10).run()
    text = values(at.text)
    assert "Abstención correcta (preguntas sin respuesta): 9/10 = 90.0%" in text
    assert "T06 · Consulta sin respuesta en el corpus → PASA" in text
    assert "NUMBER_NOT_IN_EVIDENCE: 2" in text
    assert "antes de validar 2/4 = 50.0% · después 4/4 = 100.0%" in text


def test_generation_summary_reads_measured_report(isolated, monkeypatch, tmp_path):
    out = tmp_path / "processed"
    out.mkdir()
    (out / "bundle.json").write_text("{}", encoding="utf-8")
    rows = [{"mode": "live", "model": "ollama:x", "prompt_version": "studio-v1", "latency_ms": 100,
             "tokens_out": 10, "cost_usd": 0.0, "sentences_generated": 5, "sentences_kept": 4,
             "kept_brief_script": 3, "kept_sentences_with_valid_citation": 3,
             "removed_by_code": {"UNCITED_FACT": 1}, "fallback_reason": None,
             "attribution": {"candidates": 1, "preserved_before_validation": 0, "preserved_after_validation": 1}}]
    (out / "generation_report.jsonl").write_text("\n".join(json.dumps(r) for r in rows), encoding="utf-8")
    monkeypatch.setattr(service, "bundle_path", lambda: out / "bundle.json")
    s = service.generation_summary()
    assert s["citation_coverage"] == {"num": 3, "den": 3} and s["removed_by_code"] == {"UNCITED_FACT": 1}
    assert s["latency_ms"]["median"] == 100 and s["attribution"]["preserved_after"] == 1


def test_simulator_official_weights_reproduce_ranking(isolated):
    at = AppTest.from_file(str(SIM), default_timeout=10).run()
    assert not at.exception
    assert "Pesos oficiales del reto (scoring-v1)." in values(at.success)
    rows = at.table[0].value
    assert list(rows["Cambio"]) == ["="] * len(rows)


def test_simulator_rejects_bad_sum_and_requires_justification(isolated):
    at = AppTest.from_file(str(SIM), default_timeout=10).run()
    at.number_input(key="w-R").set_value(50).run()
    assert "deben sumar 100" in values(at.error)
    at.number_input(key="w-I").set_value(5).run()  # 50+5+20+15+10 = 100
    assert "Pesos simulados." in values(at.success)
    at.button[0].click().run()  # submit with empty justification
    assert "obligatorios" in values(at.error)
    at.text_input[0].set_value("editor-demo")
    at.text_area[0].set_value("Probar más peso a relevancia para la agenda local")
    at.button[0].click().run()
    assert "Registrado (scoring-v1+custom:" in values(at.success)
    log = (isolated / "state" / "weight_changes.jsonl").read_text(encoding="utf-8").strip().splitlines()
    assert json.loads(log[-1])["weights"]["R"] == 50
