"""DL-035: additive, deterministic sector bulletins over the existing evidence.

Templates and future LLM output share banking, citation, numeric and temporal controls.
The fixed limits notice alone may name prohibited financial concepts to negate them.
"""
from __future__ import annotations

import re
import unicodedata
from datetime import datetime

from scayl.contracts import (
    Claim,
    ClaimStatus,
    ClaimType,
    Event,
    EvidenceRef,
    GenerationMeta,
    SectorBulletin,
    TaggedSentence,
    ValidationReport,
)
from scayl.gen.guard import scan
from scayl.gen.validators import SCOPE_PHRASE, _Ctx, check_sentence, evidence_numbers, numbers_in, words

LIMITS_NOTICE = (
    "Boletín de contexto sectorial para análisis. No evalúa clientes, no recomienda "
    "comprar ni vender, no infiere pérdidas, impagos ni exposición de cartera, y no es una alerta regulatoria."
)
QUESTIONS = {
    "logistica_canal": "¿Qué señales públicas del entorno logístico debo revisar?",
    "economia": "¿Qué señales públicas del entorno económico debo revisar?",
}
RELATED = {
    "logistica_canal": ["transporte marítimo", "comercio exterior", "zona libre / logística terrestre"],
    "economia": ["consumo", "construcción", "turismo"],
}
HYPOTHESES = {
    "logistica_canal": (
        "Si se mantienen los ajustes de calado, podrían variar los tiempos de tránsito; "
        "requiere verificación con la ACP."
    ),
    "economia": (
        "Si cambian las condiciones de precios, podrían variar las decisiones de consumo; "
        "requiere verificación con indicadores del mismo período."
    ),
}
ANALYST_QUESTIONS = {
    "logistica_canal": [
        "¿Qué ajustes operativos confirma la ACP y desde qué fecha?",
        "¿Qué fuentes permiten comprobar cambios en los tiempos de tránsito?",
        "¿Qué información falta para relacionar estas señales con el comercio exterior?",
    ],
    "economia": [
        "¿A qué país, período y unidad corresponde cada indicador citado?",
        "¿Qué datos del INEC permiten contrastar los titulares del período?",
        "¿Qué información falta para estudiar su relación con consumo, construcción o turismo?",
    ],
}
_FORBIDDEN = re.compile(
    r"\b(?:comprar|vender|invertir|recomendamos|oportunidad\s+de\s+inversion|impagos?|moras?|defaults?|"
    r"perdidas?|carteras?|exposicion|solvencia|riesgo\s+de\s+credito|calificacion\s+crediticia|clientes?)\b"
)
_CONDITIONAL = re.compile(r"\b(si|podria|podrian|hipotesis)\b")
_NUMBER_TOKEN = re.compile(r"(?<![\w])\d+(?:[.,]\d+)*")


def _normalized(text: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", text.casefold()) if not unicodedata.combining(c))


def forbidden_banking_term(text: str) -> bool:
    return bool(_FORBIDDEN.search(_normalized(text)))


def select_events(events: list[Event], sector: str) -> list[Event]:
    if sector not in QUESTIONS:
        raise ValueError(f"Sector no soportado: {sector}")
    return sorted((e for e in events if e.topic.value == sector),
                  key=lambda e: (-e.priority.score, -e.priority.components.U, e.event_id))[:5]


def _usable_ref(ref: EvidenceRef) -> bool:
    return ref.value is not None and not any(
        scan(str(x)) or forbidden_banking_term(str(x)) for x in (ref.value, ref.excerpt) if x is not None
    )


def _claims(events: list[Event]) -> dict[str, Claim]:
    claims = {}
    for event in events:
        for c in event.claims:
            if (c.status in (ClaimStatus.SUSTENTADA, ClaimStatus.SOLO_REPORTADA)
                    and c.evidence and all(_usable_ref(r) for r in c.evidence)
                    and not scan(c.statement) and not forbidden_banking_term(c.statement)
                    and not scan(c.attributed_to) and not forbidden_banking_term(c.attributed_to or "")):
                claims[c.claim_id] = c
        for ref in event.official_evidence:
            if not _usable_ref(ref):
                continue
            # Evidence IDs are accepted in TaggedSentence.claim_ids, as in Q&A.
            # A local adapter supplies check_sentence with a supported claim for that exact row.
            claims.setdefault(ref.evidence_id, Claim(
                claim_id=ref.evidence_id, event_id=event.event_id,
                statement=ref.excerpt or f"{ref.field}: {ref.value}",
                type=ClaimType.HECHO, status=ClaimStatus.SUSTENTADA,
                evidence=[ref], reason="Observación oficial; contexto, no confirmación del titular.",
                extracted_by="rule",
            ))
    return claims


def _refs(claims: dict[str, Claim]) -> list[EvidenceRef]:
    return list({(r.evidence_id, r.field): r for c in claims.values() for r in c.evidence}.values())


def _issue(ctx: _Ctx, code: str, text: str, location: str) -> None:
    ctx.add(code, "error", text, location)


def _validate_sentence(s: TaggedSentence, ctx: _Ctx, location: str, section: str) -> TaggedSentence | None:
    if forbidden_banking_term(s.text):
        _issue(ctx, "FORBIDDEN_BANKING_TERM", "Se descartó texto con lenguaje financiero fuera de alcance.", location)
        return None
    if section == "observations" and s.tag not in (ClaimType.HECHO, ClaimType.DECLARACION):
        _issue(ctx, "BANKING_TAG_MISMATCH", "Observación con etiqueta de hipótesis/inferencia.", location)
        return None
    if section == "impact_hypotheses" and (
        s.tag not in (ClaimType.HIPOTESIS, ClaimType.INFERENCIA)
        or not _CONDITIONAL.search(_normalized(s.text))
        or "requiere verificacion" not in _normalized(s.text)
    ):
        _issue(ctx, "BANKING_TAG_MISMATCH", "Hipótesis sin condición o verificación explícitas.", location)
        return None
    # The exact required historical warning negates "actual"; validate the factual text
    # separately so the existing present-tense guard remains unchanged for all other output.
    validation_text = s.text
    for cid in s.claim_ids:
        if cid in ctx.claims:
            for ref in ctx.claims[cid].evidence:
                if ref.evidence_id.startswith("wb:") and ref.period:
                    validation_text = validation_text.replace(
                        f" Dato histórico — {ref.period}. No presentarlo como medición actual.", ""
                    )
    checked = check_sentence(s.model_copy(update={"text": validation_text}), ctx, location)
    if checked is not None:
        checked = checked.model_copy(update={"text": s.text})
    if checked is None:
        return None
    cited = [ctx.claims[cid] for cid in checked.claim_ids]
    if any(c.status == ClaimStatus.SOLO_REPORTADA for c in cited) and not re.search(
        r"se reporta|según|de acuerdo con", checked.text, re.IGNORECASE
    ):
        _issue(ctx, "BANKING_ATTRIBUTION", "Declaración sin atribución explícita.", location)
        return None
    # Unlike a claim's statement, only the cited evidence rows may support numbers here.
    refs_only = [c.model_copy(update={"statement": "", "attributed_to": None}) for c in cited]
    allowed = evidence_numbers(refs_only)
    text_without_ids = re.sub(r"\b(?:CLM|EVT|CNF|PKG)-[\w-]+", " ", checked.text)
    if any(not (numbers_in(token) & allowed) for token in _NUMBER_TOKEN.findall(text_without_ids)):
        _issue(ctx, "NUMBER_NOT_IN_EVIDENCE", "Cifra ausente de las filas de evidencia citadas.", location)
        return None
    return checked


def validate_bulletin(b: SectorBulletin, events: list[Event]) -> SectorBulletin:
    """Rebuild citation/metadata fields from trusted input and report every removed sentence."""
    selected = select_events(events, b.sector)
    ctx = _Ctx(claims=_claims(selected))
    sections = {}
    for section in ("summary", "observations", "impact_hypotheses"):
        cleaned = []
        for i, sentence in enumerate(getattr(b, section)):
            s = _validate_sentence(sentence, ctx, f"{section}[{i}]", section)
            if s is not None:
                cleaned.append(s)
        sections[section] = cleaned
    while sum(words(s.text) for s in sections["summary"]) > 250:
        sections["summary"].pop()
        ctx.add("WORD_LIMIT", "warning", "Resumen recortado a un máximo de 250 palabras.", "summary")
    safe_questions = []
    for q in b.analyst_questions:
        if forbidden_banking_term(q) or scan(q) or numbers_in(q):
            _issue(ctx, "FORBIDDEN_BANKING_TERM" if forbidden_banking_term(q) else "BANKING_QUESTION_REPLACED",
                   "Pregunta fuera de alcance o con cifras sin cita; sustituida.", "analyst_questions")
        elif q.strip():
            safe_questions.append(q.strip())
    safe_questions = list(dict.fromkeys(safe_questions + ANALYST_QUESTIONS[b.sector]))[:3]
    if not sections["summary"]:
        _issue(ctx, "EMPTY_BULLETIN", "Ninguna oración del resumen sobrevivió.", "summary")
    return b.model_copy(update={
        **sections, "sources": _refs(ctx.claims), "event_ids": [e.event_id for e in selected],
        "related_sectors": RELATED[b.sector].copy(), "analyst_questions": safe_questions,
        "limits_notice": LIMITS_NOTICE, "question": QUESTIONS[b.sector],
        "validation": ValidationReport(passed=bool(sections["summary"] and sections["observations"]), issues=ctx.issues),
    })


def build_template_bulletin(events: list[Event], sector: str, cutoff: datetime) -> SectorBulletin:
    selected = select_events(events, sector)
    claims = _claims(selected)
    observations = []
    # One reported/supported lead per event, followed by all unique official rows.
    # Keep every selected event represented before adding the economic context.
    ordered_ids = []
    for event in selected:
        lead = next((c.claim_id for c in event.claims if c.claim_id in claims), None)
        if lead:
            ordered_ids.append(lead)
    ordered_ids += [r.evidence_id for event in selected for r in event.official_evidence
                    if r.evidence_id in claims]
    for cid in dict.fromkeys(ordered_ids):
        c = claims[cid]
        if c.status == ClaimStatus.SOLO_REPORTADA or c.type == ClaimType.DECLARACION:
            text = f"Se reporta, según {c.attributed_to or 'la fuente citada'}: {c.statement.rstrip('.')}."
            tag = ClaimType.DECLARACION
        else:
            text = c.statement.rstrip('.') + "."
            tag = ClaimType.HECHO
        periods = list(dict.fromkeys(r.period for r in c.evidence if r.period))
        if periods:
            text += " Período de la evidencia: " + ", ".join(periods) + "."
        for ref in c.evidence:
            if ref.evidence_id.startswith("wb:") and ref.period:
                text += f" Dato histórico — {ref.period}. No presentarlo como medición actual."
        observations.append(TaggedSentence(text=text, tag=tag, claim_ids=[c.claim_id]))
    questions = [q for e in selected if e.gap for q in e.gap.investigate_next]
    questions = [q for q in questions if not scan(q) and not forbidden_banking_term(q) and not numbers_in(q)]
    questions = list(dict.fromkeys(questions + ANALYST_QUESTIONS[sector]))[:3]
    bulletin = SectorBulletin(
        bulletin_id=f"BUL-{sector}-v1", sector=sector, question=QUESTIONS[sector],
        horizon=f"Snapshot con corte {cutoff.isoformat()} (UTC); cada dato conserva su período de referencia.",
        summary=observations.copy(), observations=observations,
        impact_hypotheses=[TaggedSentence(text=HYPOTHESES[sector], tag=ClaimType.HIPOTESIS)],
        related_sectors=RELATED[sector].copy(), analyst_questions=questions,
        event_ids=[e.event_id for e in selected], sources=_refs(claims),
        scope_disclaimer=SCOPE_PHRASE if any(e.text_scope_note for e in selected) else None,
        limits_notice=LIMITS_NOTICE, validation=ValidationReport(passed=False),
        generated_by=GenerationMeta(mode="template", model=None, prompt_version="bulletin-template-v1",
                                    latency_ms=0, tokens_in=None, tokens_out=None, created_at=cutoff),
    )
    return validate_bulletin(bulletin, selected)
