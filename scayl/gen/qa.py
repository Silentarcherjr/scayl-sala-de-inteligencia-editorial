"""Grounded Q&A in Spanish with explicit abstention (L-11, T06).

1. Evidence units are built from the bundle: headlines (news:), World Bank rows (wb:), USGS events (usgs:).
2. Deterministic pre-guard: if retrieval coverage is low, or the question asks for a year no unit has,
   abstain WITHOUT calling the LLM.
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
from scayl.gen.guard import SYSTEM_DATA_RULE, data_block
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
STOPWORDS = frozenset(["a", "al", "algo", "algun", "alguna", "algunos", "ante", "con", "como", "cual", "cuales", "cuando", "cuanto", "cuanta", "cuantos", "cuantas", "de", "del", "desde", "donde", "el", "ella", "ellos", "en", "entre", "era", "es", "esta", "este", "esto", "fue", "fueron", "ha", "han", "hay", "la", "las", "le", "lo", "los", "mas", "me", "mi", "muy", "no", "nos", "o", "para", "pero", "por", "porque", "que", "quien", "se", "segun", "ser", "si", "sin", "sobre", "su", "sus", "tal", "te", "tiene", "tu", "un", "una", "uno", "unos", "y", "ya", "dime", "cual", "fue", "cuales", "fueron", "sabes", "informacion", "datos", "dato"])
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


def tokens(text: str) -> list[str]:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().lower()
    return [t for t in re.findall(r"[a-z0-9]+(?:\.[0-9]+)?", text) if t not in STOPWORDS and len(t) > 1]


@dataclass(frozen=True)
class Unit:
    evidence_id: str
    text: str
    ref: EvidenceRef
    official: bool
    source: str | None  # outlet for news


def build_units(bundle: UIBundle) -> list[Unit]:
    units: list[Unit] = []
    for n in bundle.news:
        date = n.fecha_publicacion.date().isoformat() if n.fecha_publicacion else "fecha desconocida"
        ref = EvidenceRef(evidence_id=f"news:{n.id_noticia}", kind=EvidenceKind.NEWS, field="titulo",
                          value=n.titulo, url=n.url, excerpt=n.titulo)
        units.append(Unit(ref.evidence_id, f"{n.titulo} — {n.medio or 'medio desconocido'}, {date}", ref, False,
                          n.medio))
    for o in bundle.indicators:
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
        return [(self.units[i], len(set(q) & self.docs[i]) / len(set(q))) for i in order if scores[i] > 0]


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


def pre_guard(question: str, hits: list[tuple[Unit, float]]) -> tuple[str, list[str]] | None:
    """Deterministic reasons to abstain before any generation."""
    if not hits or hits[0][1] < COVERAGE_THRESHOLD:
        return ("El corpus no contiene evidencia suficientemente pertinente para esta pregunta.",
                ["Una fuente que trate directamente el tema preguntado (por ejemplo, el organismo oficial del sector)."])
    years = set(re.findall(r"\b(19\d{2}|20\d{2})\b", question))
    if years and not any(y in (u.text + (u.ref.period or "")) for u, _ in hits for y in years):
        return (f"No hay datos para el período solicitado ({', '.join(sorted(years))}) en el corpus.",
                [f"Datos oficiales del período {', '.join(sorted(years))}."])
    in_period = [u for u, _ in hits if any(y in u.text for y in years)]
    if years and in_period and "sin dato disponible" in in_period[0].text:  # most pertinent unit is NULL
        return ("El dato existe en la fuente pero está vacío (nulo) para ese período; no se reemplaza por cero.",
                ["Publicación oficial más reciente del indicador."])
    return None


def answer(question: str, bundle: UIBundle, llm: LLM, retriever: Retriever | None = None) -> QAAnswer:
    question = question.strip()
    retriever = retriever or Retriever(build_units(bundle))
    hits = retriever.search(question)
    guard = pre_guard(question, hits)
    if guard:
        return _abstain(question, guard[0], guard[1], _meta("template"))
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
    """No-model mode: show the most pertinent evidence verbatim, clearly labelled."""
    top = [u for u, cov in hits if cov >= COVERAGE_THRESHOLD][:3] or [hits[0][0]]
    sentences = [TaggedSentence(text=(f"Dato oficial: {u.text}." if u.official else f"Según {u.source}: {u.ref.value}."),
                                tag=ClaimType.HECHO if u.official else ClaimType.DECLARACION,
                                claim_ids=[u.evidence_id]) for u in top]
    issue = ValidationIssue(code="EXTRACTIVE_MODE", severity="warning",
                            detail="Sin modelo: se muestra la evidencia más pertinente, no una síntesis.")
    return QAAnswer(question=question, abstained=False, answer=sentences, citations=[u.ref for u in top],
                    validation=ValidationReport(passed=True, issues=[issue]), generated_by=_meta("template"))
