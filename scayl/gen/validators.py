"""Deterministic validators for every generated text (LLM or template). ARCHITECTURE §5.2.

Claim-first rule: a sentence may only state what its cited claims support. Invalid sentences are
removed (or re-tagged when that is safe) and every action is reported. Nothing is silently fixed.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from scayl.contracts import (
    Claim,
    ClaimStatus,
    ClaimType,
    Event,
    StoryPackage,
    TaggedSentence,
    TextScope,
    ValidationIssue,
    ValidationReport,
)

SCOPE_PHRASE = "Basado únicamente en titular/metadatos."
BRIEF_MAX_WORDS = 250
SOCIAL_MAX_WORDS = 80
SCRIPT_MIN_WORDS, SCRIPT_MAX_WORDS = 110, 160  # 45-60 s at ~2.5 words/s

_CLAIM_ID = re.compile(r"\b(?:CLM|EVT|CNF|PKG)-[\w-]+")
_NUMBER = re.compile(r"(?<![\w])\d+(?:[.,]\d+)*")
_ATTRIBUTION = re.compile(
    r"\b(según|de acuerdo con|reporta|reportan|reportó|afirma|afirman|afirmó|indica|indicó|señala|señaló|"
    r"publicó|publicaron|asegura|aseguró|informa|informó)\b",
    re.IGNORECASE,
)
_ABSENCE = re.compile(
    r"\b(no hay|no existen?|no se (ha|han)|no consta|no se dispone|no contiene|no se reporta[n]?|"
    r"sin (datos|reportes?|registros?|evidencia|informaci[oó]n|confirmaci[oó]n))\b",
    re.IGNORECASE,
)
_PRESENT = re.compile(r"\b(actual|actualmente|hoy|este año|en la actualidad|ahora mismo|vigente)\b", re.IGNORECASE)
_INVENTION = re.compile(
    r"(entrevist|en exclusiva|declaró a tvn|dijo a tvn|imágenes exclusivas|video exclusivo|fotograf[ií]as? de)",
    re.IGNORECASE,
)
_QUOTE = re.compile(r"[\"“«]([^\"”»]+)[\"”»]")


def _injection_echo(text: str) -> bool:
    from scayl.gen.guard import output_obeys_injection

    return output_obeys_injection(text)


def words(text: str) -> int:
    return len(text.split())


def _number_variants(token: str) -> set[float]:
    """'4,6' -> {4.6, 46}; '1.350' -> {1.35, 1350}: tolerate both decimal conventions."""
    out: set[float] = set()
    for cand in (token.replace(",", "."), token.replace(".", "").replace(",", "."), token.replace(",", "")):
        try:
            out.add(round(float(cand), 6))
        except ValueError:
            continue
    return out


def numbers_in(text: str) -> set[float]:
    text = _CLAIM_ID.sub(" ", text)
    found: set[float] = set()
    for tok in _NUMBER.findall(text):
        found |= _number_variants(tok)
    return found


_MONTHS = (r"enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|setiembre|octubre|noviembre|diciembre"
           r"|ene|feb|mar|abr|may|jun|jul|ago|sep|oct|nov|dic")
_DATE_CONTEXT = re.compile(rf"^\s*(de\s+)?({_MONTHS})\b|^[/:\-]\d|^\s*(h|hrs?|horas)\b", re.IGNORECASE)
_DATE_BEFORE = re.compile(rf"(\b({_MONTHS})\s+(de\s+)?|\d[/:\-])$", re.IGNORECASE)
_ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}(T.*)?$")


def _tokens_with_context(text: str) -> list[tuple[set[float], bool]]:
    """Each number in the text with a flag telling whether it is used as a date/time/year."""
    text = _CLAIM_ID.sub(" ", text)
    out = []
    for m in _NUMBER.finditer(text):
        tok = m.group(0)
        before, after = text[max(0, m.start() - 16):m.start()], text[m.end():m.end() + 20]
        is_year = len(tok) == 4 and tok.isdigit() and 1900 <= int(tok) <= 2100
        dateish = is_year or bool(_DATE_CONTEXT.search(after)) or bool(_DATE_BEFORE.search(before))
        out.append((_number_variants(tok), dateish))
    return out


def evidence_number_sets(claims: list[Claim]) -> tuple[set[float], set[float]]:
    """(value numbers, date numbers). Date parts may only support numbers used as dates."""
    values: set[float] = set()
    dates: set[float] = set()
    for c in claims:
        values |= numbers_in(c.statement)
        if c.attributed_to:
            values |= numbers_in(c.attributed_to)
        for ref in c.evidence:
            for part in (ref.value, ref.excerpt):
                if part is not None:
                    target = dates if isinstance(part, str) and _ISO_DATE.match(part) else values
                    target |= numbers_in(str(part))
            if ref.period is not None:
                dates |= numbers_in(str(ref.period))
    return values, dates


def evidence_numbers(claims: list[Claim]) -> set[float]:
    values, dates = evidence_number_sets(claims)
    return values | dates


def _is_historical(claim: Claim) -> bool:
    periods = [r.period for r in claim.evidence if r.period]
    return bool(periods) and all(re.fullmatch(r"\d{4}", p) for p in periods)


@dataclass
class AttributionStats:
    """L-18 metric: sentences built on attributed/reported claims that keep their attribution."""

    candidates: int = 0
    preserved_before: int = 0
    preserved_after: int = 0


@dataclass
class _Ctx:
    claims: dict[str, Claim]
    issues: list[ValidationIssue] = field(default_factory=list)
    attribution: AttributionStats = field(default_factory=AttributionStats)

    def add(self, code: str, severity: str, detail: str, location: str) -> None:
        self.issues.append(ValidationIssue(code=code, severity=severity, detail=detail, location=location))


def check_sentence(s: TaggedSentence, ctx: _Ctx, location: str) -> TaggedSentence | None:
    """Return the sentence (possibly re-tagged) or None if it must be removed."""
    cited = [ctx.claims[cid] for cid in s.claim_ids if cid in ctx.claims]
    unknown = [cid for cid in s.claim_ids if cid not in ctx.claims]
    if unknown:
        ctx.add("UNKNOWN_CLAIM", "error", f"Cita afirmaciones inexistentes: {unknown}", location)
        return None
    if s.tag in (ClaimType.HECHO, ClaimType.DECLARACION) and not cited:
        ctx.add("UNCITED_FACT", "error", f"Oración {s.tag.value} sin afirmación citada: «{s.text}»", location)
        return None

    if _injection_echo(s.text):
        ctx.add("INJECTION_ECHO", "error", f"La salida reproduce/obedece una instrucción de una fuente: «{s.text}»",
                location)
        return None

    if _INVENTION.search(s.text) or any(words(q) >= 3 for q in _QUOTE.findall(s.text)):
        ctx.add("FORBIDDEN_INVENTION", "error", f"Posible cita, entrevista o material inventado: «{s.text}»", location)
        return None

    tokens = _tokens_with_context(s.text)
    if tokens:
        values, dates = evidence_number_sets(cited)
        missing = [n for n, dateish in tokens if not (n & (values | dates if dateish else values))]
        if missing:
            ctx.add("NUMBER_NOT_IN_EVIDENCE", "error", f"Cifra sin respaldo en la evidencia citada: «{s.text}»",
                    location)
            return None

    if cited and all(_is_historical(c) for c in cited) and _PRESENT.search(s.text):
        ctx.add("TEMPORAL_PRESENT", "error", f"Presenta un dato histórico como actual: «{s.text}»", location)
        return None

    reported = [c for c in cited if c.status == ClaimStatus.SOLO_REPORTADA or c.type == ClaimType.DECLARACION]
    attributed = bool(_ATTRIBUTION.search(s.text))
    if reported:
        ctx.attribution.candidates += 1
        ctx.attribution.preserved_before += s.tag != ClaimType.HECHO or attributed

    if s.tag == ClaimType.HECHO:
        for c in cited:
            if c.status == ClaimStatus.SUSTENTADA:
                continue
            if c.status == ClaimStatus.SIN_SUSTENTO and _ABSENCE.search(s.text):
                continue  # stating the absence of evidence is itself supported
            if c.status in (ClaimStatus.SOLO_REPORTADA, ClaimStatus.EN_CONFLICTO) and attributed:
                ctx.add("STATUS_MISMATCH", "warning",
                        f"HECHO sobre afirmación {c.status.value}; reetiquetada como DECLARACION", location)
                s = s.model_copy(update={"tag": ClaimType.DECLARACION})
                break
            ctx.add("STATUS_MISMATCH", "error",
                    f"Presenta como HECHO una afirmación {c.status.value} sin atribución: «{s.text}»", location)
            return None

    if reported:
        ctx.attribution.preserved_after += 1  # survived: tag is not HECHO or it is attributed
    return s


def _check_list(items: list[TaggedSentence], ctx: _Ctx, section: str) -> list[TaggedSentence]:
    kept = []
    for i, s in enumerate(items):
        checked = check_sentence(s, ctx, f"{section}[{i}]")
        if checked is not None:
            kept.append(checked)
    return kept


def _trim_to(items: list[TaggedSentence], max_words: int, ctx: _Ctx, section: str) -> list[TaggedSentence]:
    while items and sum(words(s.text) for s in items) > max_words:
        dropped = items.pop()
        ctx.add("WORD_LIMIT", "warning", f"Se recortó «{dropped.text}» para respetar {max_words} palabras", section)
    return items


def validate_package(pkg: StoryPackage, event: Event) -> tuple[StoryPackage, AttributionStats]:
    """Return a cleaned package whose ``validation`` reports every removal/re-tag."""
    ctx = _Ctx(claims={c.claim_id: c for c in event.claims})

    brief = _trim_to(_check_list(pkg.brief, ctx, "brief"), BRIEF_MAX_WORDS, ctx, "brief")
    script = _trim_to(_check_list(pkg.script, ctx, "script"), SCRIPT_MAX_WORDS, ctx, "script")
    social = check_sentence(pkg.social_copy, ctx, "social_copy")
    if social is not None and words(social.text) > SOCIAL_MAX_WORDS:
        ctx.add("WORD_LIMIT", "error", f"Copy digital de {words(social.text)} palabras (> {SOCIAL_MAX_WORDS})",
                "social_copy")
        social = None
    if social is None:
        social = TaggedSentence(text="", tag=ClaimType.HECHO, claim_ids=[])

    if script and sum(words(s.text) for s in script) < SCRIPT_MIN_WORDS:
        ctx.add("SCRIPT_SHORT", "warning",
                "Guion menor a 45 s: la evidencia disponible no permite más sin inventar", "script")

    disclaimer = pkg.scope_disclaimer
    scope_is_headline = (event.text_scope_note or "").lower().startswith("basado únicamente")
    if (scope_is_headline or pkg.scope_disclaimer) and (disclaimer or "").strip() != SCOPE_PHRASE:
        ctx.add("SCOPE_DISCLAIMER", "warning", "Se inyectó la frase obligatoria de alcance", "scope_disclaimer")
        disclaimer = SCOPE_PHRASE

    if not brief:
        ctx.add("EMPTY_BRIEF", "error", "Ninguna oración del brief sobrevivió a la validación", "brief")

    passed = bool(brief) and not any(i.code in {"EMPTY_BRIEF"} for i in ctx.issues)
    cleaned = pkg.model_copy(update={
        "brief": brief, "script": script, "social_copy": social, "scope_disclaimer": disclaimer,
        "validation": ValidationReport(passed=passed, issues=ctx.issues),
    })
    return cleaned, ctx.attribution


def scope_for(alcance: TextScope) -> str | None:
    return SCOPE_PHRASE if alcance == TextScope.TITULAR_METADATOS else None
