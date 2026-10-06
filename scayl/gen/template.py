"""Deterministic 'template' StoryPackage built only from an event's claims (no LLM).

Guarantees the full flow works offline (T10) and serves as the floor the LLM must beat.
Its output still goes through ``validators.validate_package``.
"""

from __future__ import annotations

from datetime import UTC, datetime

from scayl.contracts import (
    Claim,
    ClaimStatus,
    ClaimType,
    Event,
    GenerationMeta,
    StoryPackage,
    TaggedSentence,
    ValidationReport,
)
from scayl.evidence.status import verification_sources
from scayl.gen.validators import SCOPE_PHRASE, validate_package

TEMPLATE_VERSION = "template-v1"


def _sentence(claim: Claim) -> TaggedSentence | None:
    statement = claim.statement.rstrip(".")
    if claim.status == ClaimStatus.SUSTENTADA:
        source = claim.evidence[0].evidence_id if claim.evidence else "evidencia citada"
        return TaggedSentence(text=f"{statement} (fuente: {source}).", tag=ClaimType.HECHO,
                              claim_ids=[claim.claim_id])
    if claim.status in (ClaimStatus.SOLO_REPORTADA, ClaimStatus.EN_CONFLICTO):
        who = claim.attributed_to or "publicaciones del corpus"
        lowered = statement[:1].lower() + statement[1:]
        return TaggedSentence(text=f"Según {who}, {lowered}.", tag=ClaimType.DECLARACION,
                              claim_ids=[claim.claim_id])
    if claim.status == ClaimStatus.SIN_SUSTENTO:
        lowered = statement[:1].lower() + statement[1:]
        return TaggedSentence(text=f"No hay evidencia en el corpus de que {lowered}.", tag=ClaimType.HECHO,
                              claim_ids=[claim.claim_id])
    return None


def _questions(event: Event) -> list[str]:
    qs = list(event.gap.investigate_next) if event.gap else []
    qs += [f"¿Qué evidencia respalda que {c.statement[:1].lower() + c.statement[1:].rstrip('.')}?"
           for c in event.claims if c.status != ClaimStatus.SUSTENTADA]
    sources = verification_sources().get(event.topic.value) or ["la fuente primaria"]
    qs += [f"¿Qué confirma {sources[0]} sobre este hecho?",
           "¿Qué fuentes primarias e independientes pueden consultarse?",
           "¿Qué datos actualizados existen y de qué fecha son?"]
    unique = list(dict.fromkeys(qs))
    return unique[:3]


def build_template_package(event: Event, now: datetime | None = None) -> StoryPackage:
    sentences = [s for s in (_sentence(c) for c in event.claims) if s is not None]
    facts = [s for s in sentences if s.tag == ClaimType.HECHO and "No hay evidencia" not in s.text]
    pending = [f"Verificar: {c.statement}" for c in event.claims if c.status != ClaimStatus.SUSTENTADA]
    pending += [c.verification_needed for c in event.conflicts]
    pending += [w.message for w in event.temporal_warnings]
    sources = [ref for c in event.claims for ref in c.evidence] + list(event.official_evidence)
    lead = facts[0] if facts else (sentences[0] if sentences else None)

    pkg = StoryPackage(
        package_id=f"PKG-{event.event_id.removeprefix('EVT-')}-{TEMPLATE_VERSION}",
        event_id=event.event_id,
        proposed_title=f"Lo que se sabe y lo que falta verificar: {event.title}",
        public_interest_angle=(
            f"Tema de {event.topic.value.replace('_', ' ')} con relevancia para Panamá; "
            f"estado de la evidencia: {event.evidence_status.value.replace('_', ' ')}."
        ),
        brief=sentences,
        investigation_questions=_questions(event),
        script=sentences,
        social_copy=lead or TaggedSentence(text="", tag=ClaimType.HECHO),
        pending_verifications=list(dict.fromkeys(pending)),
        sources=list({r.evidence_id: r for r in sources}.values()),
        scope_disclaimer=SCOPE_PHRASE if event.text_scope_note else None,
        validation=ValidationReport(passed=False),
        generated_by=GenerationMeta(mode="template", model=None, prompt_version=TEMPLATE_VERSION,
                                    latency_ms=0, tokens_in=None, tokens_out=None,
                                    created_at=now or datetime.now(UTC)),
    )
    cleaned, _ = validate_package(pkg, event)
    return cleaned
