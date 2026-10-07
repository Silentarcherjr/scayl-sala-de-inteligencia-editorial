import json
from pathlib import Path

import pytest

from scayl.eval.run import build_report


def test_saved_precompute_is_imported_with_its_hardware_and_scope(bundle):
    source = Path("eval/results/b13-b14-precompute.json")
    expected = json.loads(source.read_text(encoding="utf-8"))
    report = build_report(bundle, {"ids": []}, precompute_report=source)
    metrics = report["metrics"]
    assert metrics["citation_coverage"]["num"] == expected["citation_coverage"]["num"]
    assert metrics["citation_coverage"]["den"] == expected["citation_coverage"]["den"]
    assert metrics["latency_ms"]["package"]["n"] == expected["latency_ms"]["n"]
    assert metrics["latency_ms"]["package"]["p95"] == expected["latency_ms"]["p95"]
    assert metrics["latency_ms"]["package"]["measurement"]["hardware"] == expected["hardware"]
    assert metrics["latency_ms"]["qa"]["status"] == "no medido"
    assert metrics["support_validity"]["status"] == "no medido"
    assert "no mide validez humana" in report["limitations"][1]


def test_empty_and_invalid_measurements_are_not_invented(bundle, tmp_path):
    data = json.loads(Path("eval/results/b13-b14-precompute.json").read_text(encoding="utf-8"))
    data["citation_coverage"] = {"num": 0, "den": 0}
    data["latency_ms"] = {"n": 0, "median": None, "p95": None}
    path = tmp_path / "precompute.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    metrics = build_report(bundle, {"ids": []}, precompute_report=path)["metrics"]
    assert metrics["citation_coverage"]["status"] == "no medido"
    assert metrics["latency_ms"]["package"]["median"] is None
    data["citation_coverage"] = {"num": 5, "den": 2}
    path.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ValueError, match="Cobertura"):
        build_report(bundle, {"ids": []}, precompute_report=path)
