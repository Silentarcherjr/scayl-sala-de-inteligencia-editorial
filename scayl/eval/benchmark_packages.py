"""B-10: compare a smaller local model against a saved run on the same top 15."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import requests

from scayl.eval.generation_summary import summarize
from scayl.gen.llm import LLM
from scayl.ingest.common import json_bytes, utc_now
from scayl.pipeline import _cutoff, _load_worker_b, build_bundle, write_outputs


def run() -> dict:
    snapshot = Path("data/raw/v1")
    cache = Path("data/cache/llm/benchmark-qwen3-4b-20261007")
    if list(cache.glob("*.json")):
        raise ValueError("Benchmark requires an initially empty dedicated cache")
    baseline_path = Path("eval/results/b10-qwen3-8b.json")
    baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
    baseline_reports = [json.loads(line) for line in
        Path("eval/results/b10-qwen3-8b-generation_report.jsonl").read_text(encoding="utf-8").splitlines()]
    news, indicators, quakes, classify, cluster, total = _load_worker_b(snapshot)
    bundle = build_bundle(news, indicators, quakes, _cutoff(snapshot), "v1", total,
                          classify, cluster, llm=LLM(mode="live", model="qwen3:4b", cache_dir=cache), llm_top_n=15)
    output = Path("data/processed/b10-qwen3-4b")
    write_outputs(bundle, output)
    report = output / "generation_report.jsonl"
    rows = [json.loads(line) for line in report.read_text(encoding="utf-8").splitlines()]
    if [r["event_id"] for r in rows] != [r["event_id"] for r in baseline_reports]:
        raise ValueError("Top 15 changed; do not compare different event sets")
    smaller = summarize(report)
    smaller["hardware"] = requests.get("http://127.0.0.1:11434/api/ps", timeout=10).json()
    smaller["cache"] = str(cache)
    smaller["invocation"] = "B-10 live full claims+Studio pipeline; same fixed E5 top15, model qwen3:4b"
    Path("eval/results/b10-qwen3-4b-generation_report.jsonl").write_bytes(report.read_bytes())
    Path("eval/results/b10-qwen3-4b.json").write_bytes(json_bytes(smaller))
    results = {"qwen3:8b": baseline, "qwen3:4b": smaller}
    eligible = [(name, r) for name, r in results.items()
                if r["live_citation_coverage"]["value"] is not None
                and r["live_citation_coverage"]["value"] >= .95 and r["fallback_count"] == 0
                and r["latency_ms"]["n"] == 15]
    winner = min(eligible, key=lambda pair: pair[1]["latency_ms"]["median"])[0] if eligible else None
    result = {"run_at": utc_now(), "snapshot_manifest_sha256": hashlib.sha256((snapshot / "manifest.json").read_bytes()).hexdigest(),
              "models": results, "recommended_model": winner,
              "selection_rule": "Among models with 15 live samples, zero fallback and citation coverage >=95%, choose lower median Studio latency. Not a truth/quality claim.",
              "baseline_reused": "Actual final-precompute run from dc1a990; same core/snapshot and exact same ordered top15 event IDs verified.",
              "top15_event_ids": [r["event_id"] for r in rows],
              "unmeasured": ["QA latency", "human support validity", "human editorial quality", "topics gold"],
              "limitations": ["n=15, one run per model; no repeated benchmark/confidence intervals.",
                               "Whole pipeline includes model-dependent claim extraction, so Studio claim inputs can differ.",
                               "Only validator removals and post-validation citations, not independent fact verification."]}
    Path("eval/results/b10-model-comparison.json").write_bytes(json_bytes(result))
    return result


if __name__ == "__main__":
    result = run()
    print(json.dumps({"recommended_model": result["recommended_model"],
                      "models": {name: {"latency_ms": r["latency_ms"], "citations": r["citation_coverage"],
                                        "removed": r["removed_by_code"], "modes": r["modes"]}
                                 for name, r in result["models"].items()}}, indent=2))
