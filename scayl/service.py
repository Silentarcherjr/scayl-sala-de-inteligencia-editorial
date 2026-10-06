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


def review(event_id: str, to_state: ReviewState, reviewer: str, justification: str) -> ReviewRecord:
    return _store().record(get_event(event_id), to_state, reviewer, justification, package=get_package(event_id))


def review_history(event_id: str) -> list[ReviewRecord]:
    return _store().history(event_id)


def current_state(event_id: str) -> ReviewState:
    return _store().current_state(event_id)


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
    "get_event",
    "get_package",
    "load_bundle",
    "reload",
    "review",
    "review_history",
    "trust_lab",
]
