"""DL-035: additive, deterministic sector bulletins over the existing evidence.

Templates and future LLM output share banking, citation, numeric and temporal controls.
The fixed limits notice alone may name prohibited financial concepts to negate them.
"""
from __future__ import annotations

import re
import unicodedata
from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from urllib.parse import urlparse
from zoneinfo import ZoneInfo

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from scayl.contracts import (
    Claim,
    ClaimStatus,
    ClaimType,
    Event,
    EvidenceKind,
    EvidenceRef,
    GenerationMeta,
    SectorBulletin,
    TaggedSentence,
    ValidationIssue,
    ValidationReport,
)
from scayl.gen.guard import SYSTEM_DATA_RULE, data_block, scan
from scayl.gen.llm import LLM, LLMError, load_prompt
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
        "¿Qué calado máximo y cupos diarios publica la ACP en sus avisos vigentes y desde cuándo rigen?",
        "¿Cómo se compara el nivel observado del lago Gatún con el mismo mes del año anterior en datos de la ACP?",
        "¿Qué fuentes independientes, no replicadas, confirman la reducción de tránsitos reportada?",
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
    if events and all(e.topic.value == "logistica_canal" for e in events):
        claims.update(_count_claims(events, claims))
    return claims



def _count_claims(events: list[Event], claims: dict[str, Claim]) -> dict[str, Claim]:
    """Measured snapshot counts with explicit inputs; these are not independent confirmations."""
    news_refs = {r.evidence_id: r for c in claims.values() for r in c.evidence
                 if r.kind == EvidenceKind.NEWS and r.url}
    domains = sorted({urlparse(r.url).hostname.removeprefix("www.")
                      for r in news_refs.values() if urlparse(r.url).hostname})
    basis = ("Cálculo local reproducible sobre eventos seleccionados: "
             + ", ".join(e.event_id for e in events) + "; noticias cuyas URLs se cuentan: "
             + ", ".join(r.evidence_id for r in news_refs.values())
             + "; dominios distintos: " + ", ".join(domains)
             + ". No mide independencia ni corroboración.")
    result = {}
    for name, value in (("eventos", len(events)), ("medios", len(domains))):
        cid = f"bulletin:logistica_canal:{name}"
        ref = EvidenceRef(evidence_id=cid, kind=EvidenceKind.INDICATOR, field=f"conteo_{name}",
                          value=value, period="snapshot", excerpt=basis)
        result[cid] = Claim(claim_id=cid, event_id=events[0].event_id,
                            statement=f"Conteo del snapshot: {value} {name}.",
                            type=ClaimType.HECHO, status=ClaimStatus.SUSTENTADA,
                            evidence=[ref], reason="Derivado por código de los metadatos citados, no dato externo.",
                            extracted_by="rule")
    return result


def format_number(value: float) -> str:
    rounded = Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    text = format(rounded, "f").rstrip("0").rstrip(".")
    return text + ".0" if isinstance(value, float) and "." not in text else text


def _format_text(text: str) -> str:
    def replace(match):
        token = match.group(0)
        if re.fullmatch(r"\d+[.,]\d{3,}", token):
            return format_number(float(token.replace(",", ".")))
        return token
    return _NUMBER_TOKEN.sub(replace, text)


def _numeric_context(ctx: _Ctx) -> _Ctx:
    """Temporary display aliases only here; original evidence and shared validators are untouched."""
    claims = {}
    for cid, c in ctx.claims.items():
        aliases = [r.model_copy(update={"field": "redondeo_boletin", "value": format_number(r.value),
                                        "excerpt": None}) for r in c.evidence
                   if isinstance(r.value, (int, float)) and not isinstance(r.value, bool)]
        claims[cid] = c.model_copy(update={"evidence": c.evidence + aliases})
    return _Ctx(claims=claims, issues=ctx.issues, attribution=ctx.attribution)


def _synthesis(events: list[Event], claims: dict[str, Claim]) -> list[TaggedSentence]:
    result = []
    count_ids = [f"bulletin:logistica_canal:{name}" for name in ("eventos", "medios")]
    if all(cid in claims for cid in count_ids):
        counts = [claims[cid].evidence[0].value for cid in count_ids]
        result.append(TaggedSentence(
            text=f"El snapshot reúne {counts[0]} eventos de logística y {counts[1]} medios "
                 "(dominios distintos de las URLs citadas); estos conteos no prueban independencia.",
            tag=ClaimType.HECHO, claim_ids=count_ids))
    leads = [next((c for c in e.claims if c.claim_id in claims), None) for e in events]
    recurring = [c for c in leads if c and "el nino" in _normalized(c.statement)]
    if len(recurring) >= 2:
        result.append(TaggedSentence(
            text="Según los titulares citados, recurren los ajustes de calado y tránsito asociados a El Niño; "
                 "repetición no es corroboración. La procedencia independiente no puede determinarse "
                 "con la evidencia disponible.", tag=ClaimType.DECLARACION,
            claim_ids=[c.claim_id for c in recurring]))
    lake = sorted([c for cid, c in claims.items() if cid.startswith("ind:acp:ACP.GATUN.NIVEL:")],
                  key=lambda c: c.evidence[0].period)
    if lake:
        values = [c.evidence[0].value for c in lake]
        trend = "descenso y posterior recuperación" if (len(values) == 3 and
                 values[1] < values[0] and values[2] > values[1]) else "variación entre observaciones"
        series = " → ".join(f"{format_number(c.evidence[0].value)} pies ({c.evidence[0].period})" for c in lake)
        result.append(TaggedSentence(
            text=f"La serie observada de la ACP muestra {trend} del nivel del lago Gatún: {series}; "
                 "son observaciones fechadas, no una condición actual.", tag=ClaimType.HECHO,
            claim_ids=[c.claim_id for c in lake]))
    exports = next((c for cid, c in claims.items() if cid.startswith("wb:PAN:NE.EXP.GNFS.ZS:")), None)
    if exports:
        r = exports.evidence[0]
        result.append(TaggedSentence(
            text="Como contexto del comercio exterior, las exportaciones de bienes y servicios equivalen al "
                 f"{format_number(r.value)} % del PIB en {r.period}. "
                 f"Dato histórico — {r.period}. No presentarlo como medición actual.",
            tag=ClaimType.HECHO, claim_ids=[exports.claim_id]))
    return result


def _logistics_hypotheses(observations: list[TaggedSentence]) -> list[TaggedSentence]:
    ids = [cid for s in observations for cid in s.claim_ids]
    lake = max((cid for cid in ids if cid.startswith("ind:acp:ACP.GATUN.NIVEL:")), default=None)
    exports = next((cid for cid in ids if cid.startswith("wb:PAN:NE.EXP.GNFS.ZS:")), None)
    weather = [s.claim_ids[0] for s in observations if "el nino" in _normalized(s.text)]
    candidates = [
        (("Si el nivel del lago Gatún limitara la operación, podrían imponerse restricciones de calado; "
         "requiere verificación con los avisos de la ACP."), [lake] if lake else []),
        (("Si se mantienen las condiciones asociadas a El Niño según los titulares citados, podrían variar "
         "los tránsitos; requiere verificación con la ACP y fuentes independientes."), weather),
        (("Si el peso de las exportaciones condicionara la actividad logística, el comercio exterior podría "
         "ser sensible a variaciones del tránsito; requiere verificación con datos del mismo período."),
         [exports] if exports else []),
    ]
    return [TaggedSentence(text=text, tag=ClaimType.HIPOTESIS, claim_ids=cids)
            for text, cids in candidates if cids]


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
    if section == "impact_hypotheses" and (not s.claim_ids or numbers_in(s.text)):
        _issue(ctx, "BANKING_UNCITED_HYPOTHESIS", "Hipótesis sin observación citada o con cifras.", location)
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
    checked = check_sentence(s.model_copy(update={"text": validation_text}), _numeric_context(ctx), location)
    if checked is not None:
        checked = checked.model_copy(update={"text": s.text})
    if checked is None:
        return None
    cited = [ctx.claims[cid] for cid in checked.claim_ids]
    if section != "impact_hypotheses" and any(c.status == ClaimStatus.SOLO_REPORTADA for c in cited) and not re.search(
        r"se reporta|según|de acuerdo con", checked.text, re.IGNORECASE
    ):
        _issue(ctx, "BANKING_ATTRIBUTION", "Declaración sin atribución explícita.", location)
        return None
    for c in cited if section != "impact_hypotheses" else []:
        if numbers_in(c.statement) and not any(r.period for r in c.evidence) and (
            "Período del hecho: no disponible en la evidencia citada; no asumir condiciones actuales."
            not in checked.text
        ):
            _issue(ctx, "BANKING_PERIOD_MISSING", "Cifra sin período ni advertencia de su ausencia.", location)
            return None
        for ref in c.evidence:
            if ref.period and ref.period not in checked.text:
                _issue(ctx, "BANKING_PERIOD_MISSING", "Dato citado sin su período explícito.", location)
                return None
            if ref.evidence_id.startswith("wb:") and ref.period and (
                f"Dato histórico — {ref.period}. No presentarlo como medición actual." not in checked.text
            ):
                _issue(ctx, "BANKING_HISTORY_WARNING", "Indicador histórico sin advertencia temporal.", location)
                return None
    # Unlike a claim's statement, only the cited evidence rows may support numbers here.
    refs_only = [c.model_copy(update={
        "statement": "", "attributed_to": None,
        "evidence": [r.model_copy(update={"excerpt": None}) if r.evidence_id.startswith("bulletin:")
                     else r for r in c.evidence],
    }) for c in cited]
    allowed = evidence_numbers(refs_only)
    rounded = {Decimal(str(r.value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
               for c in cited for r in c.evidence if isinstance(r.value, (int, float))
               and not isinstance(r.value, bool)}
    text_without_ids = re.sub(r"\b(?:CLM|EVT|CNF|PKG)-[\w-]+", " ", checked.text)
    tokens = _NUMBER_TOKEN.findall(text_without_ids)
    if any(re.fullmatch(r"\d+[.,]\d{3,}", token) for token in tokens):
        _issue(ctx, "BANKING_NUMBER_PRECISION", "Texto con más de dos decimales; la fuente conserva el valor completo.",
               location)
        return None
    def supported(token):
        if numbers_in(token) & allowed:
            return True
        try:
            return Decimal(token.replace(",", ".")) in rounded
        except InvalidOperation:
            return False
    if any(not supported(token) for token in tokens):
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
    complete = True
    if b.sector == "logistica_canal":
        obs_ids = {cid for s in sections["observations"] for cid in s.claim_ids}
        if len(sections["impact_hypotheses"]) != 3 or any(
            not set(s.claim_ids).issubset(obs_ids) for s in sections["impact_hypotheses"]
        ):
            _issue(ctx, "BANKING_HYPOTHESES_INCOMPLETE", "Se requieren tres hipótesis ligadas a observaciones.",
                   "impact_hypotheses")
            complete = False
        if sections["summary"] != _synthesis(selected, ctx.claims) or not 3 <= len(sections["summary"]) <= 4 or any(
            s.text in {o.text for o in sections["observations"]} for s in sections["summary"]
        ):
            _issue(ctx, "BANKING_SYNTHESIS_REQUIRED", "Se requieren tres o cuatro oraciones de síntesis distintas.",
                   "summary")
            complete = False
    if not sections["summary"]:
        _issue(ctx, "EMPTY_BULLETIN", "Ninguna oración del resumen sobrevivió.", "summary")
    return b.model_copy(update={
        **sections, "sources": _refs(ctx.claims), "event_ids": [e.event_id for e in selected],
        "related_sectors": RELATED[b.sector].copy(), "analyst_questions": safe_questions,
        "limits_notice": LIMITS_NOTICE, "question": QUESTIONS[b.sector],
        "validation": ValidationReport(
            passed=bool(complete and sections["summary"] and sections["observations"] and sections["impact_hypotheses"]),
            issues=ctx.issues),
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
            attribution = re.sub(r" y \d+ medio\(s\) más$", "", c.attributed_to or "la fuente citada")
            text = f"Se reporta, según {attribution}: {c.statement.rstrip('.')}."
            tag = ClaimType.DECLARACION
        else:
            text = _format_text(c.statement.rstrip('.')) + "."
            tag = ClaimType.HECHO
        periods = list(dict.fromkeys(r.period for r in c.evidence if r.period))
        if not periods and numbers_in(c.statement):
            text += " Período del hecho: no disponible en la evidencia citada; no asumir condiciones actuales."
        if periods:
            text += " Período de la evidencia: " + ", ".join(periods) + "."
        for ref in c.evidence:
            if ref.evidence_id.startswith("wb:") and ref.period:
                text += f" Dato histórico — {ref.period}. No presentarlo como medición actual."
        observations.append(TaggedSentence(text=text, tag=tag, claim_ids=[c.claim_id]))
    questions = [q for e in selected if e.gap for q in e.gap.investigate_next]
    questions = [q for q in questions if not scan(q) and not forbidden_banking_term(q) and not numbers_in(q)]
    questions = (ANALYST_QUESTIONS[sector].copy() if sector == "logistica_canal" else
                 list(dict.fromkeys(questions + ANALYST_QUESTIONS[sector]))[:3])
    bulletin = SectorBulletin(
        bulletin_id=f"BUL-{sector}-v1", sector=sector, question=QUESTIONS[sector],
        horizon=(f"Snapshot con corte {cutoff.astimezone(ZoneInfo('America/Panama')).strftime('%d/%m/%Y %H:%M')} "
                 "(hora de Panamá); cada dato conserva su período de referencia."),
        summary=_synthesis(selected, claims) if sector == "logistica_canal" else observations.copy(),
        observations=observations,
        impact_hypotheses=(_logistics_hypotheses(observations) if sector == "logistica_canal" else
                           [TaggedSentence(text=HYPOTHESES[sector], tag=ClaimType.HIPOTESIS,
                                           claim_ids=observations[-1].claim_ids if observations else [])]),
        related_sectors=RELATED[sector].copy(), analyst_questions=questions,
        event_ids=[e.event_id for e in selected], sources=_refs(claims),
        scope_disclaimer=SCOPE_PHRASE if any(e.text_scope_note for e in selected) else None,
        limits_notice=LIMITS_NOTICE, validation=ValidationReport(passed=False),
        generated_by=GenerationMeta(mode="template", model=None, prompt_version="bulletin-template-v2",
                                    latency_ms=0, tokens_in=None, tokens_out=None, created_at=cutoff),
    )
    return validate_bulletin(bulletin, selected)


class _BulletinText(BaseModel):
    model_config = ConfigDict(extra="forbid")
    summary: list[TaggedSentence]
    observations: list[TaggedSentence]
    impact_hypotheses: list[TaggedSentence]
    analyst_questions: list[str] = Field(min_length=3, max_length=3)


def generate_bulletin(sector: str, llm: LLM, *, events: list[Event] | None = None,
                      cutoff: datetime | None = None) -> SectorBulletin:
    """Generate using the existing local/cache LLM; never return unvalidated model text."""
    if events is None or cutoff is None:
        from scayl.service import load_bundle

        bundle = load_bundle()
        events, cutoff = bundle.events, bundle.snapshot_cutoff_utc
    template = build_template_bulletin(events, sector, cutoff)
    if llm.mode == "template":
        return template
    claims = _claims(select_events(events, sector))
    payload = {
        "sector": sector, "pregunta": QUESTIONS[sector], "horizonte": template.horizon,
        "afirmaciones": [
            {"numero": i, "claim_id": c.claim_id, "afirmacion": c.statement,
             "estado": c.status.value, "atribuida_a": c.attributed_to,
             "evidencia": [r.model_dump(mode="json") for r in c.evidence]}
            for i, c in enumerate(claims.values(), 1)
        ],
        "plantilla_validada": {k: template.model_dump(mode="json")[k] for k in
                              ("summary", "observations", "impact_hypotheses", "analyst_questions")},
    }
    issues = []
    try:
        data, meta = llm.generate(
            "bulletin-v2", load_prompt("bulletin", "v2").replace("REGLA_DE_SEGURIDAD", SYSTEM_DATA_RULE),
            "Prepara el boletín con estos datos.\n" + data_block(payload), _BulletinText.model_json_schema(),
        )
        parsed = _BulletinText.model_validate(data)
        candidate = validate_bulletin(template.model_copy(update={
            **{k: getattr(parsed, k) for k in _BulletinText.model_fields}, "generated_by": meta,
        }), events)
        if candidate.validation.passed:
            if sector == "logistica_canal":
                previous_issues = candidate.validation.issues
                candidate = validate_bulletin(candidate.model_copy(update={"summary": template.summary}), events)
                candidate.validation.issues = previous_issues + candidate.validation.issues
            if candidate.validation.passed:
                return candidate
        issues = candidate.validation.issues
        reason = "La salida no conservó resumen, observaciones e hipótesis válidos."
    except (LLMError, ValidationError, ValueError, TypeError, KeyError) as exc:
        # Record the failure class, never raw model output or transport messages.
        reason = f"Salida no disponible o inválida ({type(exc).__name__})."
    template.validation.issues = [
        ValidationIssue(code="LLM_FALLBACK", severity="warning",
                        detail=f"Se usó la plantilla determinista: {reason}"),
        *issues, *template.validation.issues,
    ]
    return template
