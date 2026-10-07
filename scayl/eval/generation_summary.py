"""Summarize saved Story Studio reports; no inference or changes to the processed bundle."""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

import numpy as np

from scayl.ingest.common import json_bytes, utc_now


def summarize(report: Path) -> dict:
    raw = report.read_bytes()
    rows = [json.loads(line) for line in raw.decode("utf-8").splitlines() if line.strip()]
    live = [r for r in rows if r["mode"] == "live"]
    latencies = [r["latency_ms"] for r in live if r["latency_ms"] is not None]
    def coverage(batch):
        num = sum(r["kept_sentences_with_valid_citation"] for r in batch)
        den = sum(r["kept_brief_script"] for r in batch)
        return dict(num=num, den=den, value=num / den if den else None)
    return dict(run_at=utc_now(), source=str(report), source_sha256=hashlib.sha256(raw).hexdigest(),
                packages=len(rows), modes=dict(Counter(r["mode"] for r in rows)),
                models=sorted({r["model"] for r in rows if r["model"]}),
                latency_ms=dict(n=len(latencies), median=float(np.median(latencies)) if latencies else None,
                                p95=float(np.percentile(latencies, 95, method="linear")) if latencies else None,
                                scope="Story Studio live successful responses, wall clock; includes first load if any. Claims calls excluded. Cached/fallback latency excluded.",
                                percentile_method="linear / Hyndman-Fan type 7"),
                citation_coverage=coverage(rows), live_citation_coverage=coverage(live),
                citation_scope="Kept brief/script sentences with claim_ids, from generation_report; includes nonfactual disclaimer sentences in denominator. Social copy excluded by existing report. Not support-validity or human fact-checking.",
                fallback_count=sum(r["fallback_reason"] is not None for r in rows),
                sentences_generated=sum(r["sentences_generated"] for r in rows),
                sentences_kept=sum(r["sentences_kept"] for r in rows),
                removed_by_code=dict(sum((Counter(r["removed_by_code"]) for r in rows), Counter())),
                hardware="AMD Radeon RX 9060 XT, 8 GiB; Ollama 0.40.0 Vulkan; qwen3:8b 37/37 layers offloaded (server log). Embeddings E5 on CPU.",
                invocation="make unavailable on Windows; exact recipe: .venv/Scripts/python -m scayl.pipeline build --snapshot data/raw/v1 --llm live --top 15",
                cache="Dedicated initially empty data/cache/llm/recent-official-20261007; all calls are local.",
                api_cost_usd=0.0)


if __name__ == "__main__":
    report = Path("data/processed/v1/generation_report.jsonl")
    result = summarize(report)
    Path("eval/results/b13-b14-generation_report.jsonl").write_bytes(report.read_bytes())
    Path("eval/results/b13-b14-precompute.json").write_bytes(json_bytes(result))
    print(json.dumps(result, indent=2))
