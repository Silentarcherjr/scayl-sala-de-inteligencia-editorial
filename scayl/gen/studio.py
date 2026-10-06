"""Story Studio (L-10): evidence-grounded editorial package from an event's claims.

The LLM only sees numbered claims (inside an untrusted-data block) and must cite claim_ids per
sentence. Its output is schema-checked, then passed through the deterministic validators. Any
failure falls back to the template package, and the fallback is reported in the validation issues.
"""

from __future__ import annotations

from pydantic import ValidationError

from scayl.contracts import ClaimType, Event, StoryPackage, TaggedSentence, ValidationIssue
from scayl.gen.guard import SYSTEM_DATA_RULE, data_block
from scayl.gen.llm import LLM, LLMError, load_prompt
from scayl.gen.template import _questions, build_template_package
from scayl.gen.validators import SCOPE_PHRASE, evidence_numbers, numbers_in, validate_package

PROMPT_VERSION = "studio-v1"
_TAGS = [t.value for t in ClaimType]
_SENTENCE = {
    "type": "object",
    "properties": {
        "text": {"type": "string"},
        "tag": {"type": "string", "enum": _TAGS},
        "claim_ids": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["text", "tag", "claim_ids"],
}
SCHEMA = {
    "type": "object",
    "properties": {
        "proposed_title": {"type": "string"},
        "public_interest_angle": {"type": "string"},
        "brief": {"type": "array", "items": _SENTENCE},
        "investigation_questions": {"type": "array", "items": {"type": "string"}},
        "script": {"type": "array", "items": _SENTENCE},
        "social_copy": _SENTENCE,
        "pending_verifications": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["proposed_title", "public_interest_angle", "brief", "investigation_questions", "script",
                 "social_copy", "pending_verifications"],
}


def system_prompt() -> str:
    return load_prompt("studio", "v1").replace("REGLA_DE_SEGURIDAD", SYSTEM_DATA_RULE)


def event_payload(event: Event) -> dict:
    return {
        "evento": {"titulo_representativo": event.title, "tema": event.topic.value,
                   "estado_de_evidencia": event.evidence_status.value, "alcance": event.text_scope_note},
        "afirmaciones": [
            {"claim_id": c.claim_id, "afirmacion": c.statement, "tipo": c.type.value, "estado": c.status.value,
             "atribuida_a": c.attributed_to,
             "evidencia": [{"evidence_id": r.evidence_id, "campo": r.field, "valor": r.value, "periodo": r.period}
                           for r in c.evidence]}
            for c in event.claims
        ],
        "conflictos": [{"campo": c.field, "version_a": c.version_a.value, "version_b": c.version_b.value,
                        "verificacion": c.verification_needed} for c in event.conflicts],
        "advertencias_temporales": [w.message for w in event.temporal_warnings],
        "no_sabemos": event.gap.we_dont_know if event.gap else [],
    }


def user_prompt(event: Event) -> str:
    return "Prepara el paquete editorial para este evento.\n" + data_block(event_payload(event))


def _fallback(event: Event, reason: str) -> StoryPackage:
    pkg = build_template_package(event)
    pkg.validation.issues.insert(0, ValidationIssue(code="LLM_FALLBACK", severity="warning",
                                                    detail=f"Se usó la plantilla determinista: {reason}"))
    return pkg


def _safe_free_text(text: str, allowed: set[float]) -> bool:
    """Title/angle are not cited sentences: they may not introduce numbers absent from the evidence."""
    return all(n & allowed for n in (numbers_in(tok) for tok in text.split()) if n)


def generate(event: Event, llm: LLM) -> StoryPackage:
    return generate_with_report(event, llm)[0]


def _report(event: Event, pkg: StoryPackage, generated: int, attribution=None, fallback: str | None = None) -> dict:
    """Measured facts about one generation, consumed by the Trust Lab (B-08). No estimates."""
    removed: dict[str, int] = {}
    for i in pkg.validation.issues:
        if i.severity == "error" and i.location:
            removed[i.code] = removed.get(i.code, 0) + 1
    kept = len(pkg.brief) + len(pkg.script) + (1 if pkg.social_copy.text else 0)
    meta = pkg.generated_by
    return {
        "event_id": event.event_id, "package_id": pkg.package_id, "mode": meta.mode, "model": meta.model,
        "prompt_version": meta.prompt_version, "latency_ms": meta.latency_ms, "tokens_in": meta.tokens_in,
        "tokens_out": meta.tokens_out, "cost_usd": meta.cost_usd, "sentences_generated": generated,
        "sentences_kept": kept, "removed_by_code": removed, "fallback_reason": fallback,
        "kept_sentences_with_valid_citation": sum(1 for s in pkg.brief + pkg.script if s.claim_ids),
        "attribution": None if attribution is None else {
            "candidates": attribution.candidates, "preserved_before_validation": attribution.preserved_before,
            "preserved_after_validation": attribution.preserved_after},
    }


def generate_with_report(event: Event, llm: LLM) -> tuple[StoryPackage, dict]:
    if llm.mode == "template" or not event.claims:
        pkg = build_template_package(event)
        return pkg, _report(event, pkg, len(pkg.brief) + len(pkg.script) + 1)
    try:
        data, meta = llm.generate(PROMPT_VERSION, system_prompt(), user_prompt(event), SCHEMA)
    except LLMError as exc:
        pkg = _fallback(event, str(exc))
        return pkg, _report(event, pkg, 0, fallback=str(exc))

    template = build_template_package(event)
    allowed = evidence_numbers(event.claims)
    issues: list[ValidationIssue] = []
    try:
        title = data["proposed_title"].strip()
        angle = data["public_interest_angle"].strip()
        if not _safe_free_text(title, allowed) or not title:
            issues.append(ValidationIssue(code="TITLE_REPLACED", severity="warning",
                                          detail=f"Título con cifras sin respaldo: «{title}»"))
            title = template.proposed_title
        if not _safe_free_text(angle, allowed) or not angle:
            issues.append(ValidationIssue(code="ANGLE_REPLACED", severity="warning",
                                          detail=f"Ángulo con cifras sin respaldo: «{angle}»"))
            angle = template.public_interest_angle
        questions = [q.strip() for q in data["investigation_questions"] if q.strip()]
        questions = list(dict.fromkeys(questions + _questions(event)))[:3]
        pkg = StoryPackage(
            package_id=f"PKG-{event.event_id.removeprefix('EVT-')}-{PROMPT_VERSION}",
            event_id=event.event_id, proposed_title=title, public_interest_angle=angle,
            brief=[TaggedSentence.model_validate(s) for s in data["brief"]],
            investigation_questions=questions,
            script=[TaggedSentence.model_validate(s) for s in data["script"]],
            social_copy=TaggedSentence.model_validate(data["social_copy"]),
            pending_verifications=list(dict.fromkeys(
                [p.strip() for p in data["pending_verifications"] if p.strip()] + template.pending_verifications)),
            sources=template.sources,
            scope_disclaimer=SCOPE_PHRASE if event.text_scope_note == SCOPE_PHRASE else None,
            validation=template.validation.model_copy(update={"issues": []}),
            generated_by=meta,
        )
    except (KeyError, TypeError, ValidationError) as exc:
        reason = f"salida del modelo con formato inválido ({type(exc).__name__})"
        pkg = _fallback(event, reason)
        return pkg, _report(event, pkg, 0, fallback=reason)

    generated = len(pkg.brief) + len(pkg.script) + 1
    cleaned, attribution = validate_package(pkg, event)
    if not cleaned.validation.passed:
        reason = "ninguna oración del brief sobrevivió a la validación"
        fb = _fallback(event, reason)
        fb.validation.issues.extend(cleaned.validation.issues)
        return fb, _report(event, cleaned, generated, attribution, fallback=reason)
    cleaned.validation.issues[:0] = issues
    return cleaned, _report(event, cleaned, generated, attribution)
