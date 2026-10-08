"""Native API actions: shared Q&A, stateless human-review receipt."""
from __future__ import annotations

import hashlib
import uuid
from datetime import UTC, datetime

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


class ReviewInput(Input):
    event_id: StrictStr = Field(min_length=1, max_length=80)
    from_state: ReviewState
    to_state: ReviewState
    reviewer: StrictStr = Field(min_length=1, max_length=100)
    justification: StrictStr = Field(min_length=1, max_length=500)


def ask(payload: dict) -> dict:
    request = AskInput.model_validate(payload)
    enforce_cache()
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
