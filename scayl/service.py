"""Read/act API for the UI (ARCHITECTURE §6). The UI imports only this module and scayl.contracts.

Source resolution: data/processed/<snapshot>/bundle.json if it exists, otherwise the synthetic
fixture (and ``bundle.snapshot_version`` says so). Everything works offline.
"""

from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Literal

from scayl.contracts import (
    Event,
    QAAnswer,
    ReviewRecord,
    ReviewState,
    SectorBulletin,
    StoryPackage,
    UIBundle,
)
from scayl.gen import qa, studio
from scayl.gen.llm import LLM
from scayl.review.store import ReviewStore

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "ui_bundle.example.json"
Mode = Literal["live", "cache", "template"]


def _snapshot_name() -> str:
    return Path(os.environ.get("SCAYL_SNAPSHOT_DIR", "data/raw/v1")).name


def bundle_path() -> Path:
    candidate = ROOT / "data" / "processed" / _snapshot_name() / "bundle.json"
    return candidate if candidate.exists() else FIXTURE


@lru_cache(maxsize=1)
def load_bundle() -> UIBundle:
    return UIBundle.model_validate(json.loads(bundle_path().read_text(encoding="utf-8")))


def reload() -> None:
    load_bundle.cache_clear()
    _store.cache_clear()
    _retriever.cache_clear()


@lru_cache(maxsize=1)
def _store() -> ReviewStore:
    snap_manifest = ROOT / "data" / "raw" / _snapshot_name() / "manifest.json"
    sha = None
    if snap_manifest.exists():
        import hashlib
        sha = hashlib.sha256(snap_manifest.read_bytes()).hexdigest()
    return ReviewStore(Path(os.environ.get("SCAYL_STATE_DIR", ROOT / "data" / "state")), snapshot_sha256=sha)


def get_event(event_id: str) -> Event:
    for e in load_bundle().events:
        if e.event_id == event_id:
            return e
    raise KeyError(event_id)


def get_package(event_id: str) -> StoryPackage | None:
    return next((p for p in load_bundle().packages if p.event_id == event_id), None)


def generate_package(event_id: str, mode: Mode | None = None) -> StoryPackage:
    """Story Studio. mode: live (Ollama), cache (precomputed), template (deterministic).
    Default: SCAYL_LLM_MODE (cache). Any LLM problem falls back to template, reported in validation."""
    return studio.generate(get_event(event_id), LLM(mode=mode))


@lru_cache(maxsize=1)
def _retriever() -> qa.Retriever:
    return qa.Retriever(qa.build_units(load_bundle()))


def ask(question: str, mode: Mode | None = None) -> QAAnswer:
    """Grounded Q&A with explicit abstention (T06). Never invents a figure or a citation."""
    return qa.answer(question, load_bundle(), LLM(mode=mode), retriever=_retriever())


def review(event_id: str, to_state: ReviewState, reviewer: str, justification: str,
           package: StoryPackage | None = None) -> ReviewRecord:
    """Record a human decision about the package the reviewer is ACTUALLY looking at (AP-011).

    ``package`` defaults to the snapshot package. A package generated in the session can be passed;
    its id and sha256 go into the review receipt, so the decision is traceable to exact content.
    """
    if package is not None and package.event_id != event_id:
        raise ValueError(f"El paquete {package.package_id} no pertenece al caso {event_id}")
    return _store().record(get_event(event_id), to_state, reviewer, justification,
                           package=package if package is not None else get_package(event_id))


def receipt(review_id: str) -> dict:
    """Traceability receipt of a review (JSON with its own sha256), for display or download."""
    return _store().receipt(review_id)


def review_history(event_id: str) -> list[ReviewRecord]:
    return _store().history(event_id)


def current_state(event_id: str) -> ReviewState:
    return _store().current_state(event_id)


def official_weights() -> dict[str, int]:
    from scayl.evidence.scoring import load_rules

    return dict(load_rules()["weights"])


def simulate_weights(weights: dict[str, int]) -> list[Event]:
    """Weight simulator (L-15/A-10): re-rank the bundle; official weights reproduce scoring-v1 exactly."""
    from scayl.evidence.scoring import rescore

    return rescore(list(load_bundle().events), weights)


def record_weight_change(weights: dict[str, int], author: str, justification: str) -> dict:
    """Weight changes must be justified (PDF §4). Appended to data/state/weight_changes.jsonl + Notion outbox."""
    from datetime import UTC, datetime

    from scayl.evidence.scoring import custom_version, load_rules

    if not author.strip() or not justification.strip():
        raise ValueError("Autor y justificación son obligatorios para cambiar pesos.")
    ranked = simulate_weights(weights)  # validates weights (sum 100, R/I/U/N/E, non-negative)
    entry = {
        "at_utc": datetime.now(UTC).isoformat(), "author": author.strip(), "justification": justification.strip(),
        "weights": weights, "official_weights": official_weights(),
        "rules_version": ranked[0].priority.rules_version if ranked else custom_version(weights, load_rules()),
        "snapshot_version": load_bundle().snapshot_version,
        "top5_official": [e.event_id for e in simulate_weights(official_weights())[:5]],
        "top5_new": [e.event_id for e in ranked[:5]],
        "note": "Simulación: no cambia el ranking oficial (scoring-v1) hasta una decisión registrada.",
    }
    state = _store().state_dir
    with (state / "weight_changes.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    with (state / "notion_outbox.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps({"op": "append_weight_change", "page": "02_DECISION_LOG", "payload": entry,
                            "created_at": entry["at_utc"], "synced_at": None}, ensure_ascii=False) + "\n")
    return entry


def generation_summary() -> dict:
    """Measured facts from data/processed/<snap>/generation_report.jsonl (Trust Lab). Never estimates."""
    import statistics

    path = bundle_path().parent / "generation_report.jsonl"
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()] \
        if path.exists() and bundle_path() != FIXTURE else []
    if not rows:
        return {"status": "no medido", "packages": 0}
    removed: dict[str, int] = {}
    for r in rows:
        for code, n in (r.get("removed_by_code") or {}).items():
            removed[code] = removed.get(code, 0) + n
    llm_rows = [r for r in rows if r.get("mode") in ("live", "cache") and not r.get("fallback_reason")]
    lat = sorted(r["latency_ms"] for r in llm_rows if r.get("latency_ms"))
    attr = [r["attribution"] for r in rows if r.get("attribution")]
    kept = sum(r.get("sentences_kept", 0) for r in rows)
    cited = sum(r.get("kept_sentences_with_valid_citation", 0) for r in rows)
    return {
        "status": "medido",
        "packages": len(rows),
        "llm_packages": len(llm_rows),
        "fallbacks": sum(1 for r in rows if r.get("fallback_reason")),
        "models": sorted({r["model"] for r in rows if r.get("model")}),
        "prompt_versions": sorted({r["prompt_version"] for r in rows if r.get("prompt_version")}),
        "sentences_generated": sum(r.get("sentences_generated", 0) for r in rows),
        "sentences_kept": kept,
        "removed_by_code": removed,
        "citation_coverage": {"num": cited, "den": sum(r.get("kept_brief_script", 0) for r in rows)},
        "attribution": {"candidates": sum(a["candidates"] for a in attr),
                        "preserved_before": sum(a["preserved_before_validation"] for a in attr),
                        "preserved_after": sum(a["preserved_after_validation"] for a in attr)},
        "latency_ms": {"n": len(lat), "median": statistics.median(lat) if lat else None,
                       "p95": lat[min(len(lat) - 1, round(0.95 * (len(lat) - 1)))] if lat else None},
        "tokens_out": sum(r.get("tokens_out") or 0 for r in llm_rows),
        "cost_usd": sum(r.get("cost_usd") or 0.0 for r in rows),
    }


def trust_lab() -> dict:
    path = ROOT / "eval" / "results" / "latest.json"
    if not path.exists():
        return {"status": "no medido", "metrics": {}, "tests": {}}
    return json.loads(path.read_text(encoding="utf-8"))


__all__ = [
    "ask",
    "bundle_path",
    "current_state",
    "generate_package",
    "generation_summary",
    "get_event",
    "get_package",
    "load_bundle",
    "official_weights",
    "receipt",
    "record_weight_change",
    "reload",
    "review",
    "review_history",
    "sector_bulletin",
    "simulate_weights",
    "trust_lab",
]


def sector_bulletin(sector: str) -> SectorBulletin:
    """DL-035 additive extension; existing editorial functions are unchanged."""
    from scayl.gen.bulletin import generate_bulletin

    bundle = load_bundle()
    return generate_bulletin(sector, LLM(), events=bundle.events, cutoff=bundle.snapshot_cutoff_utc)
