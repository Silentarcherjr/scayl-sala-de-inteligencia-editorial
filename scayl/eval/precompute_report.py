"""Persist a named, byte-exact generation report and its measured summary."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess

from scayl.eval.generation_summary import summarize
from scayl.ingest.common import json_bytes, write_once


def save(report: Path, output: Path, name: str) -> dict:
    summary = summarize(report)
    summary["code_git_sha"] = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    summary["cache"] = os.environ.get("SCAYL_LLM_CACHE", "data/cache/llm")
    summary["invocation"] = "python -m scayl.pipeline build --snapshot data/raw/v1 --llm live --top 15 (make precompute recipe; make unavailable)"
    summary["hardware"] = "AMD Radeon RX 9060 XT 8 GiB / Ollama Vulkan; E5 embeddings CPU"
    summary["changes"] = "DL-026 recent evidence context and DL-027 Q&A guards; no changes to model, tau or ranking weights."
    output.mkdir(parents=True, exist_ok=True)
    write_once(output / f"{name}-generation_report.jsonl", report.read_bytes())
    write_once(output / f"{name}.json", json_bytes(summary))
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, default=Path("data/processed/v1/generation_report.jsonl"))
    parser.add_argument("--out", type=Path, default=Path("eval/results"))
    parser.add_argument("--name", default="final-precompute")
    args = parser.parse_args()
    print(json.dumps(save(args.report, args.out, args.name), indent=2))
