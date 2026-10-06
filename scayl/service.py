"""Read/act API for the UI (ARCHITECTURE §6). The UI imports only this module and scayl.contracts.

Source resolution: data/processed/<snapshot>/bundle.json if it exists, otherwise the synthetic
fixture (and ``bundle.snapshot_version`` says so). Everything works offline.
"""

from __future__ import annotations

import json
import os
from datetime import UTC, datetime
from functools import lru_cache
from pathlib import Path
from typing import Literal

from scayl.contracts import (
    Event,
    GenerationMeta,
    QAAnswer,
    ReviewRecord,
    ReviewState,
    StoryPackage,
    UIBundle,
    ValidationIssue,
    ValidationReport,
)
from scayl.gen.template import build_template_package
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


def generate_package(event_id: str, mode: Mode = "template") -> StoryPackage:
    """'live'/'cache' arrive with L-08/L-10; until then they fall back to template (reported in meta)."""
    pkg = build_template_package(get_event(event_id))
    if mode != "template":
        pkg.validation.issues.append(ValidationIssue(
            code="MODE_FALLBACK", severity="warning",
            detail=f"Modo '{mode}' aún no disponible; se usó la plantilla determinista."))
    return pkg


def ask(question: str, mode: Mode = "cache") -> QAAnswer:
    """Placeholder until L-11: honest abstention, never an invented answer."""
    return QAAnswer(
        question=question, abstained=True,
        abstention_reason="El módulo de consultas con evidencia (L-11) aún no está integrado.",
        needed_information=["Recuperación de evidencia (B-06) y generación de respuestas citadas (L-11)."],
        validation=ValidationReport(passed=True),
        generated_by=GenerationMeta(mode="template", model=None, prompt_version=None, latency_ms=0,
                                    tokens_in=None, tokens_out=None, created_at=datetime.now(UTC)),
    )


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
