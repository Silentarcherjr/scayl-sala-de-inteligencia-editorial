"""Build the public cache recipe and export only entries actually consumed by it (A-06)."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

from deploy.prepare import check_public
from scayl.gen.llm import LLM, cache_key
from scayl.ingest.common import json_bytes, utc_now, write_once
from scayl.pipeline import _cutoff, _load_worker_b, build_bundle


class ReviewedCache(LLM):
    def __init__(self, cache_dir: Path):
        super().__init__(mode="cache", cache_dir=cache_dir, model="qwen3:8b")
        self.used: dict[str, dict] = {}

    def generate(self, prompt_version, system, user, schema):
        data, meta = super().generate(prompt_version, system, user, schema)
        key = cache_key(prompt_version, self.model, system, user, schema)
        check_public(data)
        self.used[key] = {"prompt_version": prompt_version,
                          "input_sha256": hashlib.sha256(user.encode()).hexdigest()}
        return data, meta


def export(snapshot: Path, cache: Path, destination: Path) -> dict:
    if destination.exists():
        raise ValueError("Destination exists; use a new directory")
    news, indicators, quakes, classify, cluster, total = _load_worker_b(snapshot)
    if any(item.descripcion is not None for item in news):
        raise ValueError("Source descriptions must be absent BEFORE model/cache input")
    llm = ReviewedCache(cache)
    bundle = build_bundle(news, indicators, quakes, _cutoff(snapshot), snapshot.name,
                          total, classify, cluster, llm=llm, llm_top_n=15, public=True)
    raw = bundle.model_dump(mode="json")
    check_public(raw)
    files = {"bundle.public.json": json_bytes(raw)}
    audit = []
    for key, trace in sorted(llm.used.items()):
        content = (cache / f"{key}.json").read_bytes()
        entry = json.loads(content)
        check_public(entry)
        if set(entry) != {"data", "meta"}:
            raise ValueError(f"Unexpected cache schema: {key}")
        files[f"llm/{key}.json"] = content
        audit.append({"key": key, **trace, "sha256": hashlib.sha256(content).hexdigest(),
                      "review": "Codex: metadata-only inputs; no description data/citations; actual pipeline schema/validators applied. Raw model output is revalidated when read."})
    report = {"created_at": utc_now(), "published": False,
              "code_git_sha": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
              "snapshot_manifest_sha256": hashlib.sha256((snapshot / "manifest.json").read_bytes()).hexdigest(),
              "news": len(news), "source_descriptions": 0, "events": len(bundle.events),
              "top15_modes": [p.generated_by.mode for p in bundle.packages[:15]],
              "cache_entries": len(audit), "reviewed_by": "Codex / frictionspp-svg",
              "reviewed_entries": audit,
              "limitations": ["Agent review of privacy/schema, not human support-validity review.",
                              "Cached raw model output can contain sentences removed by validators; only the validated package is displayed.",
                              "No deployment performed; Lead confirmation required."],
              "files": {name: hashlib.sha256(content).hexdigest() for name, content in files.items()}}
    for name, content in files.items():
        write_once(destination / name, content)
    write_once(destination / "PUBLIC_CACHE_REVIEW.json", json_bytes(report))
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", type=Path, default=Path("data/raw/v1"))
    parser.add_argument("--cache", type=Path, required=True)
    parser.add_argument("--out", type=Path, default=Path("deploy/artifacts/v1"))
    args = parser.parse_args()
    result = export(args.snapshot, args.cache, args.out)
    print(json.dumps({k: result[k] for k in ("news", "events", "source_descriptions", "cache_entries", "top15_modes")}, indent=2))
