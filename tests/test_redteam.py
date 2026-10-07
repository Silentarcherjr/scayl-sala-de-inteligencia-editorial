"""Test the evaluator's accounting and real adapters, not a claim of perfect resistance."""
import json
from pathlib import Path

import pytest

from scayl import service
from scayl.eval.redteam import ROOT, metrics, run_cases
from scayl.eval.run import build_report


def cases():
    return [json.loads(line) for line in (ROOT / "eval/redteam/cases.jsonl").read_text(encoding="utf-8").splitlines()]


def test_real_service_and_validator_run_offline_and_restore_source(monkeypatch):
    from scayl.gen.llm import OllamaBackend

    def forbidden(*args, **kwargs):
        pytest.fail("Template evaluation must not call a model")

    monkeypatch.setattr(OllamaBackend, "chat_json", forbidden)
    before = service.bundle_path()
    report = run_cases(cases())
    assert service.bundle_path() == before
    assert service.load_bundle.cache_info().currsize == 0
    assert len(report["cases"]) >= 19
    assert report["metrics"]["redteam_resistance"]["den"] >= 15
    assert report["metrics"]["abstention_false"]["den"] == 4
    assert all(r["answer"]["generated_by"]["mode"] == "template" for r in report["cases"])
    assert report["metrics"]["validator_probes"]["den"] == 9
    assert report["failed_ids"] == [r["id"] for r in report["cases"] if r["failures"]]
    for row in report["cases"]:
        if len(row["output_validation"]["kept"]) < len(row["answer"]["answer"]):
            assert not row["passed"]  # post-hoc rejection cannot hide unsafe original output


def test_metric_denominators_separate_unanswerable_from_controls():
    rows = [{"category": category, "expected_abstain": expected, "answer": {"abstained": observed},
             "passed": observed == expected} for category, expected, observed in [
                 ("attack", True, True), ("attack", True, False),
                 ("answerable_control", False, True), ("answerable_control", False, False)]]
    result = metrics(rows)
    assert result["abstention_correct"]["num"] == 1
    assert result["abstention_correct"]["den"] == 2
    assert result["abstention_false"]["num"] == 1
    assert result["abstention_false"]["den"] == 2
    assert result["validator_probes"]["status"] == "no medido"
    assert metrics([])["abstention_correct"]["num"] is None


def test_duplicate_or_unlabelled_cases_rejected():
    with pytest.raises(ValueError, match="únicos"):
        run_cases([cases()[0], cases()[0]])
    with pytest.raises(ValueError, match="sintético"):
        run_cases([{**cases()[0], "synthetic": False}])


def test_eval_recomputes_metrics_and_keeps_unmeasured_fields(bundle, tmp_path):
    report = run_cases([cases()[12], cases()[16]])
    report["metrics"]["abstention_correct"]["num"] = 999
    saved = tmp_path / "redteam.json"
    saved.write_text(json.dumps(report), encoding="utf-8")
    result = build_report(bundle, {"ids": []}, redteam_report=saved)
    assert result["metrics"]["abstention_correct"]["num"] == 1
    assert result["metrics"]["abstention_correct"]["den"] == 1
    assert result["metrics"]["support_validity"]["status"] == "no medido"
    assert result["metrics"]["latency_ms"]["qa"]["n"] is None
    report["cases"][0]["answer"]["generated_by"]["mode"] = "live"
    saved.write_text(json.dumps(report), encoding="utf-8")
    with pytest.raises(ValueError, match="inválido"):
        build_report(bundle, {"ids": []}, redteam_report=saved)


def test_adapter_restores_after_service_exception(monkeypatch):
    before = service.bundle_path
    def broken(*args, **kwargs):
        raise RuntimeError("execution failed")
    monkeypatch.setattr(service, "ask", broken)
    with pytest.raises(RuntimeError):
        run_cases([cases()[0]])
    assert service.bundle_path is before
    assert service.load_bundle.cache_info().currsize == 0
