"""Grounded Q&A in Spanish with explicit abstention (L-11, T06).

1. Evidence units are built from the bundle: headlines (news:), World Bank rows (wb:), USGS events (usgs:).
2. Deterministic pre-guard, WITHOUT calling the LLM: abstain if retrieval coverage is low, if the question
   asks for a year no pertinent unit has, if it states a figure the evidence does not contain (false premise),
   or if it asks for a CURRENT value and only historical rows exist. Sources flagged as possible prompt
   injection are never used as answer material (B-12, AP-013).
3. LLM (live/cache) answers only from the retrieved units, citing evidence_ids; it may abstain.
4. The same validators as Story Studio check every sentence (numbers, attribution, temporal, injection).
   If nothing survives, the system abstains. Without a model, an extractive answer lists the most
   pertinent evidence and says so.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from datetime import UTC, datetime

from rank_bm25 import BM25Okapi

from scayl.contracts import (
    Claim,
    ClaimStatus,
    ClaimType,
    EvidenceKind,
    EvidenceRef,
    GenerationMeta,
    QAAnswer,
    TaggedSentence,
    UIBundle,
    ValidationIssue,
    ValidationReport,
)
from scayl.evidence.recent import ref_for as recent_ref
from scayl.gen.guard import SYSTEM_DATA_RULE, data_block
from scayl.gen.guard import scan as scan_injection
from scayl.gen.llm import LLM, LLMError, load_prompt
from scayl.gen.validators import _Ctx, check_sentence

PROMPT_VERSION = "qa-v1"
TOP_K = 8
COVERAGE_THRESHOLD = 0.6
INDICATOR_ES = {
    "NY.GDP.MKTP.KD.ZG": "crecimiento del PIB (% anual)",
    "FP.CPI.TOTL.ZG": "inflación, precios al consumidor (% anual)",
    "SL.UEM.TOTL.ZS": "desempleo (% de la población activa)",
    "SP.POP.TOTL": "población total",
    "IT.NET.USER.ZS": "personas que usan internet (% de la población)",
    "NE.EXP.GNFS.ZS": "exportaciones de bienes y servicios (% del PIB)",
}
COUNTRY_ES = {"PAN": "Panamá", "CRI": "Costa Rica", "COL": "Colombia", "DOM": "República Dominicana",
              "MEX": "México", "GTM": "Guatemala"}
STOPWORDS = frozenset(["a", "al", "algo", "algun", "alguna", "algunos", "ante", "con", "como", "cual", "cuales", "cuando", "cuanto", "cuanta", "cuantos", "cuantas", "de", "del", "desde", "donde", "el", "ella", "ellos", "en", "entre", "era", "es", "esta", "este", "esto", "fue", "fueron", "ha", "han", "hay", "la", "las", "le", "lo", "los", "mas", "me", "mi", "muy", "no", "nos", "o", "para", "pero", "por", "porque", "que", "quien", "se", "segun", "ser", "si", "sin", "sobre", "su", "sus", "tal", "te", "tiene", "tu", "un", "una", "uno", "unos", "y", "ya", "dime", "cual", "fue", "cuales", "fueron", "sabes", "informacion", "datos", "dato",
                       # time words: handled by the CURRENT guard, never as retrieval terms ("hoy" in headlines)
                       "hoy", "actual", "actuales", "actualmente", "ahora", "vigente",
                       "cierto", "verdad"])  # "¿es cierto que…?" frames a premise, not a topic
SCHEMA = {
    "type": "object",
    "properties": {
        "abstain": {"type": "boolean"},
        "reason": {"type": ["string", "null"]},
        "needed_information": {"type": "array", "items": {"type": "string"}},
        "answer": {"type": "array", "items": {
            "type": "object",
            "properties": {"text": {"type": "string"}, "tag": {"type": "string", "enum": [t.value for t in ClaimType]},
                           "evidence_ids": {"type": "array", "items": {"type": "string"}}},
            "required": ["text", "tag", "evidence_ids"]}},
    },
    "required": ["abstain", "answer"],
}


MONTHS = {m: i for i, m in enumerate(["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
                                       "septiembre", "octubre", "noviembre", "diciembre"], start=1)} | {"setiembre": 9}
_ES_DAY = re.compile(r"\b(\d{1,2})\s+de\s+(" + "|".join(MONTHS) + r")(?:\s+(?:de|del)\s+(\d{4}))?\b", re.IGNORECASE)
_ES_MONTH = re.compile(r"\b(" + "|".join(MONTHS) + r")\s+(?:de|del)\s+(\d{4})\b", re.IGNORECASE)


def normalize_dates(text: str) -> str:
    """'28 de septiembre de 2026' -> '2026-09-28'; 'agosto de 2026' -> '2026-08' (the format of the evidence)."""
    def day(m):
        return f"{m[3]}-{MONTHS[m[2].lower()]:02d}-{int(m[1]):02d}" if m[3] else m[0]
    text = _ES_DAY.sub(day, text)
    return _ES_MONTH.sub(lambda m: f"{m[2]}-{MONTHS[m[1].lower()]:02d}", text)


def tokens(text: str) -> list[str]:
    dates = re.findall(r"\b\d{4}-\d{2}(?:-\d{2})?\b", text)  # whole ISO periods are strong terms
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().lower()
    words = [t for t in re.findall(r"[a-z0-9]+(?:\.[0-9]+)?", text) if t not in STOPWORDS and len(t) > 1]
    return words + dates


@dataclass(frozen=True)
class Unit:
    evidence_id: str
    text: str
    ref: EvidenceRef
    official: bool
    source: str | None  # outlet for news
    flagged: bool = False  # possible prompt injection: retrievable (to explain abstention), never quoted


def build_units(bundle: UIBundle) -> list[Unit]:
    units: list[Unit] = []
    for n in bundle.news:
        date = n.fecha_publicacion.date().isoformat() if n.fecha_publicacion else "fecha desconocida"
        ref = EvidenceRef(evidence_id=f"news:{n.id_noticia}", kind=EvidenceKind.NEWS, field="titulo",
                          value=n.titulo, url=n.url, excerpt=n.titulo)
        units.append(Unit(ref.evidence_id, f"{n.titulo} — {n.medio or 'medio desconocido'}, {date}", ref, False,
                          n.medio, flagged=scan_injection(n.titulo) or scan_injection(n.descripcion)))
    for o in bundle.indicators:
        if o.fuente != "wb":  # recent official series (ACP, INEC): cited with their period
            ref = recent_ref(o)
            value = "sin dato disponible" if o.valor is None else f"{o.valor} {o.unidad or ''}".strip()
            units.append(Unit(ref.evidence_id, f"{ref.excerpt.split(':')[0]}: {ref.excerpt.split(': ', 1)[1].rsplit(':', 1)[0]}"
                              f", período {o.periodo}: {value}" + (" (proyección, no medición)" if o.es_proyeccion else "")
                              + f" [{COUNTRY_ES.get(o.pais_iso3, o.pais_iso3)}"
                              + ("; inflación]" if o.indicador_id.startswith("INEC.IPC") else "]"),
                              ref, not o.es_proyeccion, o.fuente.upper()))
            continue
        name = INDICATOR_ES.get(o.indicador_id, o.indicador_nombre or o.indicador_id)
        country = COUNTRY_ES.get(o.pais_iso3, o.pais_iso3)
        value = "sin dato disponible" if o.valor is None else f"{o.valor} {o.unidad or ''}".strip()
        ref = EvidenceRef(evidence_id=f"wb:{o.pais_iso3}:{o.indicador_id}:{o.anio}", kind=EvidenceKind.INDICATOR,
                          field="valor", value=o.valor, period=str(o.anio), url=o.fuente_url,
                          excerpt=f"{name}, {country}, {o.anio}: {value}")
        units.append(Unit(ref.evidence_id, f"Banco Mundial: {name} en {country}, año {o.anio}: {value}", ref, True,
                          "Banco Mundial"))
    for q in bundle.seismic:
        when = q.time.isoformat().replace("+00:00", "Z") if q.time else None
        ref = EvidenceRef(evidence_id=f"usgs:{q.id}", kind=EvidenceKind.SEISMIC, field="magnitude", value=q.magnitude,
                          period=when, url=q.url, excerpt=q.place)
        units.append(Unit(ref.evidence_id, f"USGS: sismo de magnitud {q.magnitude} {q.place or ''} {when or ''}", ref,
                          True, "USGS"))
    return units


def coverage_terms(q: list[str], keep_years: bool = True) -> set[str]:
    """Topic words (and years, unless excluded) of a query; asserted figures do not count toward coverage."""
    def keep(t: str) -> bool:
        if re.fullmatch(r"(19|20)\d{2}", t):
            return keep_years
        return not re.fullmatch(r"\d+(?:\.\d+)?", t)
    return {t for t in q if keep(t)} or set(q)


class Retriever:
    """BM25 ranking + query-term coverage in [0,1] (the interpretable abstention signal)."""

    def __init__(self, units: list[Unit]):
        self.units = units
        self.docs = [set(tokens(u.text)) for u in units]
        self.bm25 = BM25Okapi([tokens(u.text) or ["_"] for u in units]) if units else None

    def search(self, question: str, k: int = TOP_K) -> list[tuple[Unit, float]]:
        q = tokens(question)
        if not q or not self.bm25:
            return []
        scores = self.bm25.get_scores(q)
        order = sorted(range(len(self.units)), key=lambda i: (-scores[i], self.units[i].evidence_id))[:k]
        # Coverage counts topic words (and years), not the figures a question asserts: a false figure must reach
        # the false-premise guard and be reported as such, not hide behind "low coverage".
        terms = coverage_terms(q)
        return [(self.units[i], len(terms & self.docs[i]) / len(terms)) for i in order if scores[i] > 0]


def _meta(mode: str, model: str | None = None) -> GenerationMeta:
    return GenerationMeta(mode=mode, model=model, prompt_version=PROMPT_VERSION, latency_ms=0, tokens_in=None,
                          tokens_out=None, created_at=datetime.now(UTC))


def _abstain(question: str, reason: str, needed: list[str], meta: GenerationMeta,
             issues: list[ValidationIssue] | None = None) -> QAAnswer:
    return QAAnswer(question=question, abstained=True, abstention_reason=reason, needed_information=needed,
                    validation=ValidationReport(passed=True, issues=issues or []), generated_by=meta)


def _pseudo_claim(u: Unit) -> Claim:
    return Claim(claim_id=u.evidence_id, event_id="QA", statement=u.text,
                 type=ClaimType.HECHO if u.official else ClaimType.DECLARACION,
                 status=ClaimStatus.SUSTENTADA if u.official else ClaimStatus.SOLO_REPORTADA,
                 attributed_to=u.source, evidence=[u.ref], reason="unidad de evidencia recuperada", extracted_by="rule")


_YEAR = re.compile(r"\b(19\d{2}|20\d{2})\b")
_NUMBER = re.compile(r"(?<![\w.])(\d+(?:[.,]\d+)?)\s*(%|por ciento|millones|mil\b)?", re.IGNORECASE)
_CURRENT = re.compile(r"\b(actual(es|mente)?|hoy|ahora|este a[nñ]o|en este momento|vigente|al d[ií]a de hoy)\b",
                      re.IGNORECASE)


_DATES = re.compile(r"\b\d{4}-\d{2}(?:-\d{2})?\b|\b\d{1,2}\s+de\s+(?:enero|febrero|marzo|abril|mayo|junio|julio|"
                    r"agosto|septiembre|setiembre|octubre|noviembre|diciembre)\b", re.IGNORECASE)


def _figures(text: str) -> set[float]:
    """Numbers in a text that are not years or dates (periods are handled by the period guard)."""
    out = set()
    for m in _NUMBER.finditer(_DATES.sub(" ", text)):
        raw = m.group(1)
        if _YEAR.fullmatch(raw) and not m.group(2):
            continue
        out.add(float(raw.replace(",", ".")))
    return out


def _coverage(question_terms: set[str], unit: Unit) -> float:
    return len(question_terms & set(tokens(unit.text))) / len(question_terms) if question_terms else 0.0


def pre_guard(question: str, hits: list[tuple[Unit, float]]) -> tuple[str, list[str]] | None:
    """Deterministic reasons to abstain before any generation."""
    if not hits or hits[0][1] < COVERAGE_THRESHOLD:
        return ("El corpus no contiene evidencia suficientemente pertinente para esta pregunta.",
                ["Una fuente que trate directamente el tema preguntado (por ejemplo, el organismo oficial del sector)."])
    usable = [(u, c) for u, c in hits if not u.flagged]
    if not usable or usable[0][1] < COVERAGE_THRESHOLD:
        return (("La única evidencia pertinente contiene instrucciones sospechosas (posible inyección); se trata "
                 "como dato y no se reproduce como respuesta."),
                ["Una fuente distinta y confiable sobre el tema preguntado."])
    years = set(_YEAR.findall(question))
    # The year must belong to a unit that is also about the topic (a headline dated 2026 about the Canal
    # does not answer "inflation in 2026").
    topic_terms = coverage_terms(tokens(question), keep_years=False)
    in_period = [u for u, _ in usable if any(y in (u.text + (u.ref.period or "")) for y in years)
                 and _coverage(topic_terms, u) >= COVERAGE_THRESHOLD]
    if years and not in_period:
        return (f"No hay datos para el período solicitado ({', '.join(sorted(years))}) en el corpus.",
                [f"Datos oficiales del período {', '.join(sorted(years))}."])
    if years and "sin dato disponible" in in_period[0].text:  # most pertinent unit is NULL
        return ("El dato existe en la fuente pero está vacío (nulo) para ese período; no se reemplaza por cero.",
                ["Publicación oficial más reciente del indicador."])
    pertinent = in_period or [u for u, c in usable if c >= COVERAGE_THRESHOLD]
    asked = _figures(question)
    if asked:
        known = set().union(*(_figures(u.text) for u in pertinent))
        missing = [f for f in sorted(asked) if not any(abs(f - k) <= 1e-9 for k in known)]
        if missing:
            return (("La cifra planteada en la pregunta no aparece en la evidencia del corpus; no se confirma ni "
                     "se sustituye por otra sin una fuente que la respalde."),
                    ["Fuente primaria que publique esa cifra, con su período."])
    if _CURRENT.search(question) and pertinent and all(u.evidence_id.startswith("wb:") for u in pertinent):
        last = max((u.ref.period or "" for u in pertinent), default="")
        return ((f"La pregunta pide un dato actual y la evidencia disponible es histórica (último año: {last}); "
                 "no se presenta como actual."),
                ["Publicación oficial reciente del indicador, con su fecha (por ejemplo, INEC)."])
    return None


def answer(question: str, bundle: UIBundle, llm: LLM, retriever: Retriever | None = None) -> QAAnswer:
    question = question.strip()
    query = normalize_dates(question)
    retriever = retriever or Retriever(build_units(bundle))
    current = bool(_CURRENT.search(question))
    hits = retriever.search(query, k=len(retriever.units) if current else TOP_K)
    if current:  # "actual/hoy": the most recent dated official unit first, never an undated or older one
        hits.sort(key=lambda h: h[0].ref.period or "", reverse=True)
        hits.sort(key=lambda h: (h[1] < COVERAGE_THRESHOLD, not h[0].evidence_id.startswith("ind:")))
        hits = hits[:TOP_K]
    guard = pre_guard(query, hits)
    if guard:
        return _abstain(question, guard[0], guard[1], _meta("template"))
    hits = [(u, c) for u, c in hits if not u.flagged]  # flagged sources never reach the model or the answer
    units = {u.evidence_id: u for u, _ in hits}

    if llm.mode == "template":
        return _extractive(question, hits)
    payload = {"pregunta": question,
               "evidencia": [{"evidence_id": u.evidence_id, "texto": u.text, "oficial": u.official} for u, _ in hits]}
    system = load_prompt("qa", "v1").replace("REGLA_DE_SEGURIDAD", SYSTEM_DATA_RULE)
    try:
        data, meta = llm.generate(PROMPT_VERSION, system, "Responde la pregunta.\n" + data_block(payload), SCHEMA)
    except LLMError:
        return _extractive(question, hits)

    if data.get("abstain"):
        return _abstain(question, data.get("reason") or "El modelo determinó que la evidencia no basta.",
                        list(data.get("needed_information") or []), meta)

    ctx = _Ctx(claims={eid: _pseudo_claim(u) for eid, u in units.items()})
    kept = []
    for i, raw in enumerate(data.get("answer", [])):
        try:
            s = TaggedSentence(text=raw["text"], tag=raw["tag"], claim_ids=list(raw.get("evidence_ids", [])))
        except (KeyError, ValueError):
            continue
        checked = check_sentence(s, ctx, f"answer[{i}]")
        if checked is not None:
            kept.append(checked)
    if not kept:
        return _abstain(question, "La respuesta generada no pudo sustentarse con la evidencia; se descartó.",
                        ["Evidencia que respalde directamente la respuesta."], meta, ctx.issues)
    cited = list(dict.fromkeys(cid for s in kept for cid in s.claim_ids))
    return QAAnswer(question=question, abstained=False, answer=kept, citations=[units[c].ref for c in cited],
                    validation=ValidationReport(passed=True, issues=ctx.issues), generated_by=meta)


def _extractive(question: str, hits: list[tuple[Unit, float]]) -> QAAnswer:
    """No-model mode: show the most pertinent evidence verbatim, clearly labelled, through the same validator."""
    top = [u for u, cov in hits if cov >= COVERAGE_THRESHOLD][:3] or [hits[0][0]]
    ctx = _Ctx(claims={u.evidence_id: _pseudo_claim(u) for u in top})
    sentences = []
    for i, u in enumerate(top):
        s = TaggedSentence(text=(f"Dato oficial: {u.text}." if u.official else f"Según {u.source}: {u.ref.value}."),
                           tag=ClaimType.HECHO if u.official else ClaimType.DECLARACION, claim_ids=[u.evidence_id])
        checked = check_sentence(s, ctx, f"answer[{i}]")
        if checked is not None:
            sentences.append(checked)
    meta = _meta("template")
    if not sentences:
        return _abstain(question, "La evidencia recuperada no superó la validación; no se muestra.",
                        ["Evidencia que respalde directamente la respuesta."], meta, ctx.issues)
    issue = ValidationIssue(code="EXTRACTIVE_MODE", severity="warning",
                            detail="Sin modelo: se muestra la evidencia más pertinente, no una síntesis.")
    cited = list(dict.fromkeys(cid for s in sentences for cid in s.claim_ids))
    by_id = {u.evidence_id: u for u in top}
    return QAAnswer(question=question, abstained=False, answer=sentences, citations=[by_id[c].ref for c in cited],
                    validation=ValidationReport(passed=True, issues=[issue, *ctx.issues]), generated_by=meta)
