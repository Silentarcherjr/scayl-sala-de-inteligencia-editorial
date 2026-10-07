import json

from scayl.eval.generation_summary import summarize


def test_summary_separates_live_latency_from_cache_and_fallback(tmp_path):
    rows = []
    for mode, latency, num, den, fallback in [
        ("live", 100, 2, 3, None), ("live", 300, 3, 4, None),
        ("cache", 9999, 1, 2, None), ("template", None, 1, 2, "unavailable")]:
        rows.append({"mode": mode, "model": "local", "latency_ms": latency,
                     "kept_sentences_with_valid_citation": num, "kept_brief_script": den,
                     "fallback_reason": fallback, "sentences_generated": 4, "sentences_kept": 3,
                     "removed_by_code": {"UNCITED_FACT": 1}})
    report = tmp_path / "report.jsonl"
    report.write_text("\n".join(json.dumps(r) for r in rows), encoding="utf-8")
    measured = summarize(report)
    assert measured["latency_ms"]["n"] == 2
    assert measured["latency_ms"]["median"] == 200
    assert measured["latency_ms"]["p95"] == 290
    assert measured["citation_coverage"] == {"num": 7, "den": 11, "value": 7 / 11}
    assert measured["live_citation_coverage"] == {"num": 5, "den": 7, "value": 5 / 7}
    assert measured["fallback_count"] == 1
