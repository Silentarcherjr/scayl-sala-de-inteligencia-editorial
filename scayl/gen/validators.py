"""Deterministic validators for every generated text (LLM or template). ARCHITECTURE §5.2.

Claim-first rule: a sentence may only state what its cited claims support. Invalid sentences are
removed (or re-tagged when that is safe) and every action is reported. Nothing is silently fixed.
"""

from __future__ import annotations

import re
import unicodedata
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
_PRESENT = re.compile(r"\b(actual|actuales|actualmente|hoy|hoy en día|este año|este mes|esta semana|en la actualidad|"
                      r"ahora|ahora mismo|vigente|en este momento|en curso|a la fecha)\b", re.IGNORECASE)
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


def _fold(text: str) -> str:
    """Lowercase, accent-free text for containment checks."""
    text = unicodedata.normalize("NFKD", text or "").encode("ascii", "ignore").decode().lower()
    return " ".join(re.sub(r"[^a-z0-9%$.,: ]+", " ", text).split())


# --- Fixed qualifiers the template puts between "Según <medio>" and the headline (support-review fix).
# They are built from metadata, not from source text, so they are stripped before content checks; their
# dates must match the event's own metadata dates.
QUALIFIER_PHRASES = {
    "unconfirmed": "sin confirmación oficial en el corpus",
    "conflict": "versiones en conflicto en el corpus",
    "judicial": "asunto judicial: lo atribuido no establece responsabilidad",
    "non_latin": "titular en escritura no latina, no se reproduce sin traducción verificada",
}
LANGUAGE_NAMES = {"pt": "portugués", "en": "inglés", "fr": "francés", "it": "italiano", "de": "alemán"}
_DATE_LABELS = ("primera publicación del evento", "evento detectado")
_QUAL_ALT = "|".join(
    [re.escape(p) for p in QUALIFIER_PHRASES.values()]
    + [rf"(?:{'|'.join(_DATE_LABELS)}): \d{{4}}-\d{{2}}-\d{{2}}"]
    + [rf"titular original en {n}, sin traducir" for n in LANGUAGE_NAMES.values()]
)
QUALIFIER_RE = re.compile(rf"\s*\((?:{_QUAL_ALT})(?:; (?:{_QUAL_ALT}))*\)")
_QUAL_DATE = re.compile(r"\d{4}-\d{2}-\d{2}")


def _non_latin(text: str) -> bool:
    return any(ch.isalpha() and not unicodedata.name(ch, "").startswith("LATIN") for ch in text)


def _evidence_text(claims: list[Claim]) -> str:
    parts: list[str] = []
    for c in claims:
        parts += [c.statement, c.attributed_to or ""]
        for ref in c.evidence:
            parts += [str(ref.value or ""), ref.excerpt or "", ref.field, ref.evidence_id, ref.url or ""]
    return _fold(" ".join(parts))


_NEGATION = re.compile(r"\b(no|nunca|jamas|ningun\w*|tampoco|nadie|niega\w*|nego|negaron|descart\w*|desmient\w*|"
                       r"desmint\w*)\b")
_HEDGE = re.compile(r"\b(no (se )?(ha |han |hay |esta |estan |fue |fueron )?(sido )?"
                    r"(confirmad\w*|verificad\w*|precisad\w*|detallad\w*|informad\w*|oficial\w*|publicad\w*)|"
                    r"no consta\w*|no (se )?dispone\w*|no (se )?(conoce|sabe)n?|no hay (datos|evidencia|informacion|"
                    r"confirmacion|reportes?|registros?)|no se reporta\w*|no existen?|no contiene\w*|"
                    r"no se reproduce)\b")
_NEG_SKIP = {"se", "lo", "la", "le", "les", "los", "las", "ha", "han", "hay", "es", "son", "fue", "habra", "sera", "esta"}
_CAUSAL = re.compile(r"\b(debido a|a causa de|por culpa de|culpa de|como consecuencia de|como resultado de|gracias a|"
                     r"caus(o|aron|ado|ada|ados|adas|ara)|provoc(o|aron|ado|ada|ados|adas|ara)|"
                     r"ocasion(o|aron|ado|ada)|originad[oa]s? por|desencaden\w+|atribuy\w* a)\b")
_CAUSAL_IN_EVIDENCE = re.compile(r"\b(debido|causa\w*|culpa|consecuencia|resultado|gracias|caus\w*|provoc\w*|"
                                 r"ocasion\w*|originad\w*|desencaden\w*|atribuy\w*|por|tras|ante|enfrentar|"
                                 r"due|because|amid|pelo|pela|par|wegen)\b")
_ACCUSATION = re.compile(r"\b(culpab\w*|delit\w*|delincuen\w*|criminal\w*|corrupt\w*|corrupcion|fraud\w*|estaf\w*|"
                         r"soborn\w*|lavado|blanqueo|malversa\w*|peculado|ilicit\w*|ilegal\w*|robo|robos|robaron|"
                         r"acus\w*|imputad\w*|narcotrafic\w*|extorsion\w*|cohecho)\b")
_CHANGE = re.compile(r"\b(aument\w*|sub(e|en|io|ieron|ir)|crec\w*|creci\w*|ca(e|en|yo|yeron|ida)|baj(a|an|o|aron)|"
                     r"disminu\w*|reduj\w*|reduc\w*|increment\w*|descend\w*|retroced\w*|repunt\w*|"
                     r"se dispar\w*|desplom\w*)\b[^.;]{0,30}?\d+(?:[.,]\d+)*\s*(%|por ?ciento|puntos)")
_CHANGE_IN_EVIDENCE = re.compile(r"\b(aument\w*|sub\w*|crec\w*|creci\w*|ca(e|en|yo|yeron|ida)|baj\w*|disminu\w*|"
                                 r"reduj\w*|reduc\w*|increment\w*|descend\w*|retroced\w*|repunt\w*|dispar\w*|desplom\w*|"
                                 r"variacion\w*|respecto|comparacion|veces|interanual|rise\w*|fall\w*|increase\w*|"
                                 r"decrease\w*|up|down)\b")
_UNIT = re.compile(r"(\d+(?:[.,]\d+)*)\s*(%|por ?ciento|puntos? porcentuales|p\.?p\.?(?=\W)|mil millones|"
                   r"millones|millon|miles|mil|km|kilometros|metros|toneladas|dolares|usd|balboas|pies|grados)",
                   re.IGNORECASE)
_UNIT_CLASS = {"%": "pct", "por ciento": "pct", "porciento": "pct", "punto porcentual": "pp",
               "puntos porcentuales": "pp", "pp": "pp", "p.p.": "pp", "p.p": "pp", "mil millones": "1e9",
               "millones": "1e6", "millon": "1e6", "miles": "1e3", "mil": "1e3", "km": "km", "kilometros": "km",
               "metros": "m", "toneladas": "t", "dolares": "usd", "usd": "usd", "balboas": "usd", "pies": "ft",
               "grados": "deg"}
# Capitalised tokens that are generic in this corpus and need no textual support.
_GENERIC_NAMES = {"panama", "panamá", "segun", "según", "usgs", "tvn", "banco", "mundial", "canal"}


def _units(folded: str) -> list[tuple[set[float], str]]:
    out = []
    for m in _UNIT.finditer(folded):
        unit = " ".join(m.group(2).lower().split())
        cls = _UNIT_CLASS.get(unit) or _UNIT_CLASS.get(unit.rstrip("."))
        if cls:
            out.append((_number_variants(m.group(1)), cls))
    return out


def _unit_mismatch(sentence: str, evidence: str) -> bool:
    """True when a number carries a unit in the sentence and the evidence only has it with other units."""
    ev = _units(evidence)
    for nums, cls in _units(sentence):
        ev_classes = {c for n, c in ev if n & nums}
        if ev_classes and cls not in ev_classes:
            return True
    return False


_NEG_VERB = re.compile(r"\b(niega\w*|nego|negaron|descart\w*|desmient\w*|desmint\w*)\b")


def _negated_words(text: str) -> list[str]:
    """Content word governed by 'no/nunca/jamás' (skipping clitics and auxiliaries)."""
    out = []
    for m in re.finditer(r"\b(?:no|nunca|jamas)\s+(\w+)(?:\s+(\w+))?", text):
        word = m.group(2) if m.group(1) in _NEG_SKIP and m.group(2) else m.group(1)
        if len(word) >= 4 and word not in _NEG_SKIP:
            out.append(word)
    return out


def _negation_flip(sentence: str, evidence: str) -> str | None:
    """'added': negates a predicate the evidence states positively; 'dropped': the reverse.

    Only predicates that appear in the evidence are compared, so editorial caveats ("no prueba
    independencia") are not flagged."""
    core = _HEDGE.sub(" ", sentence)
    if not _NEGATION.search(evidence):
        if _NEG_VERB.search(core) or any(re.search(rf"\b{re.escape(w)}\b", evidence) for w in _negated_words(core)):
            return "added"
    if not _NEGATION.search(sentence):
        if any(re.search(rf"\b{re.escape(w)}\b", sentence) for w in _negated_words(evidence)):
            return "dropped"
    return None


_NAME_RUN = re.compile(r"(?<![#@\w])[A-ZÁÉÍÓÚÑ][\wáéíóúñü]{2,}(?:\s+(?:de\s+(?:la\s+|los\s+)?)?[A-ZÁÉÍÓÚÑ][\wáéíóúñü]{2,})*")


def _unsupported_names(text: str, evidence: str) -> list[str]:
    """Proper-name runs (not sentence-initial, not hashtags) with no word present in the cited evidence.

    A run like "José Raúl Mulino" is supported when any of its words is cited ("Mulino"): the check
    targets entities the evidence never mentions, not fuller forms of a cited name."""
    missing = []
    for m in _NAME_RUN.finditer(text):
        before = text[:m.start()].rstrip()
        words_ = [w for w in m.group(0).split() if w[:1].isupper()]
        if not before or before[-1] in ".:;¿¡!?\"“«(—-":
            words_ = words_[1:]  # sentence-initial capital is not evidence of a proper name
        folded = [_fold(w) for w in words_ if _fold(w) not in _GENERIC_NAMES]
        if folded and not any(re.search(rf"\b{re.escape(w)}", evidence) for w in folded):
            missing.append(" ".join(words_))
    return missing


def event_dates(event: Event) -> set[str]:
    return {d.date().isoformat() for d in (event.first_published, event.last_published, event.first_detected) if d}


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
    # ISO dates (YYYY-MM-DD) from the event's own metadata; the only dates a template qualifier may carry.
    event_dates: set[str] = field(default_factory=set)
    # Story Studio packages are Spanish editorial copy: untranslated non-Latin script is removed there.
    spanish_only: bool = False
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

    if ctx.spanish_only and _non_latin(s.text):
        ctx.add("NON_LATIN_SCRIPT", "error",
                f"Texto en escritura no latina sin traducción verificada: «{s.text}»", location)
        return None

    qualifier_dates = {d for q in QUALIFIER_RE.findall(s.text) for d in _QUAL_DATE.findall(q)}
    if qualifier_dates - ctx.event_dates:
        ctx.add("QUALIFIER_DATE_UNSUPPORTED", "error",
                f"Fecha del calificador ausente en los metadatos del evento: «{s.text}»", location)
        return None
    core = QUALIFIER_RE.sub("", s.text)  # fixed metadata qualifiers carry no claim content
    folded = _fold(core)
    evidence = _evidence_text(cited)

    if _ACCUSATION.search(folded):
        terms = {m.group(0) for m in _ACCUSATION.finditer(folded)}
        if any(not re.search(rf"\b{re.escape(t[:5])}", evidence) for t in terms):
            ctx.add("ACCUSATION_NOT_IN_EVIDENCE", "error",
                    f"Imputa delitos o culpas que la evidencia citada no contiene: «{s.text}»", location)
            return None

    tokens = _tokens_with_context(core)
    if tokens:
        values, dates = evidence_number_sets(cited)
        missing = [n for n, dateish in tokens if not (n & (values | dates if dateish else values))]
        if missing:
            ctx.add("NUMBER_NOT_IN_EVIDENCE", "error", f"Cifra sin respaldo en la evidencia citada: «{s.text}»",
                    location)
            return None

    if cited:
        problem = _content_problem(core, folded, evidence, cited, s.tag)
        if problem:
            code, detail = problem
            ctx.add(code, "error", f"{detail}: «{s.text}»", location)
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


_CAUSE_PHRASE = re.compile(r"\b(?:debido a|a causa de|por culpa de|culpa de|como consecuencia de|"
                           r"como resultado de|gracias a|originad[oa]s? por)\s+((?:\S+\s*){1,5})")
_FILLER = {"una", "unos", "unas", "los", "las", "del", "que", "por", "para", "con", "sus", "este", "esta", "esa", "ese"}


def _unsupported_cause(folded: str, evidence: str) -> bool:
    """'debido a <X>': at least one content word of X must appear in the cited evidence."""
    for m in _CAUSE_PHRASE.finditer(folded):
        content = [w.strip(".,;:") for w in m.group(1).split()]
        content = [w for w in content if len(w) >= 4 and w not in _FILLER]
        if content and not any(re.search(rf"\b{re.escape(w[:5])}", evidence) for w in content):
            return True
    return False


def _content_problem(core: str, folded: str, evidence: str, cited: list[Claim],
                     tag: ClaimType) -> tuple[str, str] | None:
    """Claim-vs-citation checks: the cited evidence must actually support what the sentence adds."""
    if _unit_mismatch(folded, evidence):
        return "UNIT_MISMATCH", "La unidad de la cifra no coincide con la evidencia citada"
    if _CHANGE.search(folded) and not _CHANGE_IN_EVIDENCE.search(evidence):
        return "RELATIVE_CHANGE_UNSUPPORTED", "Presenta como variación una cifra que la evidencia da como nivel"
    if not any(c.status == ClaimStatus.SIN_SUSTENTO for c in cited):
        flip = _negation_flip(folded, evidence)
        if flip == "added":
            return "NEGATION_FLIP", "Niega algo que la evidencia citada no niega"
        if flip == "dropped":
            return "NEGATION_FLIP", "Omite la negación que contiene la evidencia citada"
    if _CAUSAL.search(folded) and (not _CAUSAL_IN_EVIDENCE.search(evidence) or _unsupported_cause(folded, evidence)):
        return "CAUSALITY_NOT_IN_EVIDENCE", "Atribuye una causa que la evidencia citada no menciona"
    names = _unsupported_names(core, evidence) if tag in (ClaimType.HECHO, ClaimType.DECLARACION) else []
    if names:
        return "ENTITY_NOT_IN_EVIDENCE", f"Nombra {names} sin respaldo en la evidencia citada"
    return None


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
    ctx = _Ctx(claims={c.claim_id: c for c in event.claims}, event_dates=event_dates(event),
               spanish_only=True)

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
