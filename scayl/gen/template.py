"""Deterministic 'template' StoryPackage built only from an event's claims (no LLM).

Guarantees the full flow works offline (T10) and serves as the floor the LLM must beat.
Its output still goes through ``validators.validate_package``.
"""

from __future__ import annotations

import re
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
from scayl.gen.validators import (
    LANGUAGE_NAMES,
    QUALIFIER_PHRASES,
    SCOPE_PHRASE,
    _non_latin,
    validate_package,
)

TEMPLATE_VERSION = "template-v1"

# Function words that identify the language of a headline (support review SR05/SR22/SR25). Deterministic,
# no model: the corpus has no per-claim language field, so the headline text itself is inspected.
_STOPWORDS = {
    "es": {"el", "la", "los", "las", "del", "y", "que", "por", "una", "con", "para", "se", "su", "al", "es", "en",
           "de", "un"},
    "pt": {"do", "da", "dos", "das", "pelo", "pela", "não", "em", "ao", "às", "uma", "são", "é", "novas", "pode"},
    "en": {"the", "of", "and", "to", "on", "for", "with", "is", "are", "by", "from", "at", "its", "after", "over"},
    "fr": {"le", "les", "des", "du", "et", "est", "une", "au", "aux", "sur", "dans", "pour", "avec", "fait"},
    "it": {"il", "della", "delle", "degli", "nel", "gli", "sono", "dello", "alla", "per"},
    "de": {"der", "die", "und", "mit", "von", "für", "ist", "den", "dem", "auf", "wird"},
}
# Judicial vocabulary: an attributed headline about a case must not read as an established responsibility.
_JUDICIAL = re.compile(r"\b(fiscal[ií]a|imputad\w*|acusad\w*|acusaci[oó]n|medidas cautelares|detenid[oa]s?|"
                       r"capturad[oa]s?|arrestad[oa]s?|procesad[oa]s?|condenad[oa]s?|juicio|tribunal|lavado|fraude|"
                       r"corrupci[oó]n|soborno|peculado|estafa|delito\w*|indagatoria|allanamiento\w*)\b", re.IGNORECASE)


def headline_language(text: str) -> str | None:
    """Code of a non-Spanish Latin-script headline, or None when Spanish/undetermined."""
    tokens = re.findall(r"[^\W\d_]+", text.lower())
    scores = {lang: sum(t in vocab for t in tokens) for lang, vocab in _STOPWORDS.items()}
    best = max((lang for lang in scores if lang != "es"), key=lambda lang: scores[lang])
    return best if scores[best] >= 2 and scores[best] > scores["es"] else None


def _event_date(event: Event | None) -> str | None:
    if event is None:
        return None
    if event.first_published:
        return f"primera publicación del evento: {event.first_published.date().isoformat()}"
    if event.first_detected:
        return f"evento detectado: {event.first_detected.date().isoformat()}"
    return None


def _reported_sentence(claim: Claim, statement: str, event: Event | None) -> TaggedSentence:
    """'Según <medio> (<date>; <status>[; <language>][; <judicial>]): <headline>.'

    Qualifiers come from metadata only. Support-review fixes: the date stops an undated present-tense
    headline from reading as current (SR04); the status keeps one outlet's claim from reading as
    confirmed (SR10); the judicial note keeps an attributed case from reading as established
    responsibility (SR19); foreign headlines are labelled (SR25) and non-Latin script is never
    reproduced untranslated (SR05)."""
    who = claim.attributed_to or "publicaciones del corpus"
    parts = [p for p in [_event_date(event)] if p]
    parts.append(QUALIFIER_PHRASES["conflict" if claim.status == ClaimStatus.EN_CONFLICTO else "unconfirmed"])
    if _non_latin(statement):
        parts.append(QUALIFIER_PHRASES["non_latin"])
        return TaggedSentence(text=f"Según {who} ({'; '.join(parts)}).", tag=ClaimType.DECLARACION,
                              claim_ids=[claim.claim_id])
    lang = headline_language(statement)
    if lang:
        parts.append(f"titular original en {LANGUAGE_NAMES[lang]}, sin traducir")
    if _JUDICIAL.search(statement):
        parts.append(QUALIFIER_PHRASES["judicial"])
    # Headlines start with proper nouns too often ("Canal de Panamá"): keep their capitalization.
    return TaggedSentence(text=f"Según {who} ({'; '.join(parts)}): {statement}.", tag=ClaimType.DECLARACION,
                          claim_ids=[claim.claim_id])


def _sentence(claim: Claim, event: Event | None = None) -> TaggedSentence | None:
    statement = claim.statement.rstrip(".")
    if claim.status == ClaimStatus.SUSTENTADA:
        source = claim.evidence[0].evidence_id if claim.evidence else "evidencia citada"
        return TaggedSentence(text=f"{statement} (fuente: {source}).", tag=ClaimType.HECHO,
                              claim_ids=[claim.claim_id])
    if claim.status in (ClaimStatus.SOLO_REPORTADA, ClaimStatus.EN_CONFLICTO):
        return _reported_sentence(claim, statement, event)
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
    sentences = [s for s in (_sentence(c, event) for c in event.claims) if s is not None]
    facts = [s for s in sentences if s.tag == ClaimType.HECHO and "No hay evidencia" not in s.text]
    pending = [f"Verificar: {c.statement}" for c in event.claims if c.status != ClaimStatus.SUSTENTADA]
    pending += [c.verification_needed for c in event.conflicts]
    pending += [w.message for w in event.temporal_warnings]
    pending += [f"Traducir y verificar el titular original de {c.attributed_to or 'la fuente'} "
                f"({', '.join(r.evidence_id for r in c.evidence)})"
                for c in event.claims if c.status != ClaimStatus.SUSTENTADA
                and (_non_latin(c.statement) or headline_language(c.statement))]
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
