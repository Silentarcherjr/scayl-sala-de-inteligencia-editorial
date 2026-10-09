"""Native API actions: shared Q&A, stateless human-review receipt."""
from __future__ import annotations

import hashlib
import hmac
import os
import threading
import uuid
from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, StrictStr, field_validator

from python_api.runtime import enforce_cache, service
from scayl.contracts import ReviewRecord, ReviewState, can_transition
from scayl.review.store import canonical_sha256


class Input(BaseModel):
    model_config = ConfigDict(extra="forbid")

    @field_validator("*", mode="before")
    @classmethod
    def strip_strings(cls, value):
        return value.strip() if isinstance(value, str) else value


class AskInput(Input):
    question: StrictStr = Field(min_length=1, max_length=300)
    # Optional, off by default: "online" is honoured only with server-side env + a matching access code.
    mode: Literal["cache", "online"] | None = None
    access_code: StrictStr | None = Field(default=None, max_length=200)


class ReviewInput(Input):
    event_id: StrictStr = Field(min_length=1, max_length=80)
    from_state: ReviewState
    to_state: ReviewState
    reviewer: StrictStr = Field(min_length=1, max_length=100)
    justification: StrictStr = Field(min_length=1, max_length=500)


class _OnlineQuota:
    """Per-instance cap on external provider calls (extra guard only; the real spending cap is set in
    Google AI Studio / Cloud billing). Counts actual provider calls, not abstentions."""

    def __init__(self):
        self.calls = 0
        self.lock = threading.Lock()

    def take(self) -> bool:
        try:
            limit = int(os.environ.get("SCAYL_LIVE_MAX_CALLS", "50"))
        except ValueError:
            limit = 50
        with self.lock:
            if self.calls >= limit:
                return False
            self.calls += 1
            return True


ONLINE_QUOTA = _OnlineQuota()


MAX_FAILED_CODES = 20  # per instance: slows down guessing; the access code is not a strong secret by itself
_failed = {"n": 0}
NOT_CONFIGURED = "La IA generativa en vivo no está configurada en este despliegue. Usa «Consulta con evidencia»."
NOT_AUTHORIZED = "Código de acceso no autorizado. No se llamó al proveedor externo."


def online_allowed(request: AskInput) -> bool:
    """Online only if the key AND the access code are configured server-side AND the request asks for it with
    the matching code (constant-time compare). A request that asks for online and is not allowed gets an explicit
    error (PermissionError -> 403), never a cached or extractive answer presented as if Gemini had answered."""
    if request.mode != "online":
        return False
    key = os.environ.get("GEMINI_API_KEY", "").strip()
    code = os.environ.get("SCAYL_LIVE_ACCESS_CODE", "").strip()
    if not key or not code:
        raise PermissionError(NOT_CONFIGURED)
    if _failed["n"] >= MAX_FAILED_CODES:
        raise PermissionError("Demasiados intentos con código incorrecto en esta instancia. Inténtalo más tarde.")
    if not request.access_code or not hmac.compare_digest(request.access_code.encode("utf-8"), code.encode("utf-8")):
        _failed["n"] += 1
        raise PermissionError(NOT_AUTHORIZED)
    return True


def _ask_online(question: str) -> dict:
    from scayl.gen import qa
    from scayl.gen.llm import LLM, GeminiBackend, LLMUnavailable

    class QuotaBackend(GeminiBackend):
        def chat_json(self, system, user, schema):
            if not ONLINE_QUOTA.take():
                raise LLMUnavailable("Cupo de llamadas en vivo agotado en esta instancia")
            return super().chat_json(system, user, schema)

    llm = LLM(mode="online", backend=QuotaBackend())
    return qa.answer(question, service.load_bundle(), llm, retriever=service._retriever()).model_dump(mode="json")


def ask(payload: dict) -> dict:
    request = AskInput.model_validate(payload)
    enforce_cache()
    if online_allowed(request):
        return _ask_online(request.question)
    return service.ask(request.question, mode="cache").model_dump(mode="json")


def review(payload: dict) -> dict:
    request = ReviewInput.model_validate(payload)
    if not can_transition(request.from_state, request.to_state):
        raise ValueError(f"Transición no permitida: {request.from_state.value} → {request.to_state.value}")
    enforce_cache()
    event = service.get_event(request.event_id)
    package = service.get_package(request.event_id)
    record = ReviewRecord(
        review_id=f"REV-{uuid.uuid4().hex[:12]}", event_id=event.event_id,
        package_id=package.package_id if package else None,
        from_state=request.from_state, to_state=request.to_state,
        reviewer=request.reviewer, justification=request.justification,
        decided_at=datetime.now(UTC), evidence_snapshot_sha256=canonical_sha256(event),
    )
    # Same receipt fields and canonical hashes as ReviewStore; no SQLite, files or outbox.
    from python_api.runtime import RUNTIME

    body = {
        "review": record.model_dump(mode="json"),
        "snapshot_sha256": hashlib.sha256((RUNTIME / "data/processed/v1/bundle.json").read_bytes()).hexdigest(),
        "evidence_snapshot_sha256": record.evidence_snapshot_sha256,
        "claims": [claim.model_dump(mode="json") for claim in event.claims],
        "package_id": package.package_id if package else None,
        "package_sha256": canonical_sha256(package) if package else None,
        "generated_by": package.generated_by.model_dump(mode="json") if package else None,
        "note": "Aprobado como borrador NO significa publicado.",
        "storage_note": "Registro de esta demo en tu navegador; en la redacción iría a su base de datos",
        "state_authority": "from_state proporcionado por el navegador; sin estado global ni autenticación",
    }
    return {**body, "receipt_sha256": canonical_sha256(body)}
