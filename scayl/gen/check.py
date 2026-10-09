"""Editorial claim checker: contrasts a user's claim with the snapshot evidence. No LLM, no verdicts.

Reuses the Q&A retriever, date normalization, figure parsing and injection scanner (scayl.gen.qa / guard). It only
compares what the engine can actually compare: figures (with stated precision), periods (exact granularity),
countries and units, between the claim and evidence units about the same topic. Everything else is reported as
"no comparable" with what would need to be checked. It never says "true" or "false".
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

from scayl.gen.guard import scan as scan_injection
from scayl.gen.qa import (
    _CURRENT,
    _DATES,
    _NUMBER,
    COVERAGE_THRESHOLD,
    Retriever,
    Unit,
    _figures_with_precision,
    _is_null,
    _matches,
    _requested_periods,
    coverage,
    coverage_terms,
    normalize_dates,
    tokens,
)

MIN_CHARS, MAX_CHARS = 12, 300
TOP_K = 12
MAX_CONTEXT = 3  # context rows shown (not compared); compared rows are always all shown
_SCALE = re.compile(r"\b(millones|millon|miles|mil|billones)\b", re.IGNORECASE)
SCOPE_NOTE = ("SCAYL no declara la afirmación verdadera ni falsa: muestra qué evidencia del snapshot es compatible, "
              "cuál difiere y qué falta comprobar. La decisión es editorial.")
METHOD = "Recuperación BM25 + comparación determinista de cifras, períodos, países y unidades. Sin IA generativa."

_PROVINCES = ["bocas del toro", "chiriqui", "colon", "darien", "cocle", "herrera", "los santos", "veraguas",
              "panama oeste", "guna yala", "ngabe bugle", "emberá", "santa cruz", "david", "boquete", "tocumen",
              "gatun", "burica"]
_COUNTRIES = {"panama": "Panamá", "costa rica": "Costa Rica", "colombia": "Colombia", "mexico": "México",
              "guatemala": "Guatemala", "republica dominicana": "República Dominicana", "ecuador": "Ecuador",
              "nicaragua": "Nicaragua", "honduras": "Honduras", "el salvador": "El Salvador", "venezuela": "Venezuela"}
_TARGET = re.compile(r"\b(?:para|hacia)\s+(?:el\s+|la\s+)?$")


def _fold(text: str) -> str:
    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().lower()


def _signed_figures(text: str) -> list[tuple[float, int]]:
    """Keep the sign in this verifier without changing the shared Q&A parser."""
    dated = _DATES.sub(" ", text)
    out = []
    for match in _NUMBER.finditer(dated):
        for value, precision in _figures_with_precision(match.group(0)):
            negative = match.start() > 0 and dated[match.start() - 1] in "-−"
            out.append((-value if negative else value, precision))
    return out


def _known_figures(u: Unit) -> set[float]:
    if u.official and isinstance(u.ref.value, (int, float)):
        return {float(u.ref.value)}
    return {value for value, _ in _signed_figures(u.text)}


def countries(text: str) -> set[str]:
    """Countries a text locates something in; Panamanian places map to Panamá; 'para Panamá' (who is affected)
    does not locate."""
    t = _fold(text)
    found = set()
    for name, label in _COUNTRIES.items():
        for m in re.finditer(rf"\b{re.escape(name)}\b", t):
            if not _TARGET.search(t[:m.start()]):
                found.add(label)
    if any(re.search(rf"\b{re.escape(p)}\b", t) for p in _PROVINCES):
        found.add("Panamá")
    # "Canal de Panamá" names the waterway; it does not by itself say where a figure was measured
    if re.search(r"canal de panama", t) and len(re.findall(r"\bpanama\b", t)) == 1:
        found.discard("Panamá")
    return found


def unit_kind(text: str) -> str | None:
    t = _fold(text)
    if "%" in text or "por ciento" in t or "porcentaje" in t:
        return "porcentaje"
    if re.search(r"\bpies\b", t):
        return "pies"
    for name, pattern in (("metros", r"\bmetros?\b"), ("kilómetros", r"\bkilometros?\b"),
                          ("centímetros", r"\bcentimetros?\b")):
        if re.search(pattern, t):
            return name
    if "magnitud" in t or re.search(r"\bsismo|temblor|terremoto\b", t):
        return "magnitud"
    if re.search(r"\b(dolares|usd|b/\.|balboas)\b", t) or "$" in text:
        return "moneda"
    return None


def _unit_kind_of(u: Unit) -> str | None:
    if u.evidence_id.startswith("usgs:"):
        return "magnitud"
    return unit_kind(u.text) if not u.evidence_id.startswith("news:") else None


def _series(u: Unit) -> str:
    return u.evidence_id.rsplit(":", 1)[0] if u.evidence_id.startswith(("wb:", "ind:")) else u.evidence_id


def _period_matches(periods: list[str], u: Unit) -> bool:
    period = u.ref.period or ""
    return bool(period) and any(period == p or (len(p) == 10 and period.startswith(p)) for p in periods)


def _source(u: Unit) -> str:
    return u.source or u.evidence_id.split(":")[0]


def _stems(text: str) -> set[str]:
    return {t[:5] for t in tokens(text) if len(t) >= 5 and not t[0].isdigit()}


def _closest(claim: str, units: list[Unit]) -> list[Unit]:
    """Units that share the most topic words with the claim (exact words first, then 5-letter stems:
    'creció' ~ 'crecimiento'). Ties are kept: the caller refuses to pick between different indicators."""
    terms = set(coverage_terms(tokens(claim), keep_years=False))
    stems = _stems(claim)

    def score(u: Unit) -> tuple[int, int]:
        words = set(tokens(u.text))
        return len(terms & words), len(stems & _stems(u.text))
    top = max(score(u) for u in units)
    return [u for u in units if score(u) == top]


def _fmt(value: object) -> str:
    return f"{value:.2f}".rstrip("0").rstrip(".") if isinstance(value, float) else str(value)


def cite(u: Unit) -> dict:
    return {"evidence_id": u.evidence_id, "fuente": _source(u), "tipo": "oficial" if u.official else "noticia",
            "url": u.ref.url, "campo": u.ref.field, "periodo": u.ref.period, "valor": u.ref.value,
            "extracto": u.ref.excerpt or u.text}


@dataclass
class Finding:
    unit: Unit
    relation: str  # coincide | difiere | contexto
    note: str

    def to_dict(self) -> dict:
        return {"relacion": self.relation, "nota": self.note, "evidencia": cite(self.unit)}


STATUS_LABELS = {
    "compatible_oficial": "Compatible con evidencia oficial",
    "discrepancia_oficial": "Discrepa de evidencia oficial",
    "solo_reportado": "Solo reportado por medios",
    "discrepancia_reportada": "Difiere de lo reportado por medios",
    "no_comparable": "Evidencia pertinente, pero no comparable",
    "evidencia_insuficiente": "Evidencia insuficiente",
    "abstencion_inyeccion": "Abstención: instrucciones en el texto",
}


def _result(claim: str, status: str, explanation: str, findings: list[Finding], to_verify: list[str],
            detected: dict) -> dict:
    compared = [f for f in findings if f.relation != "contexto"]
    context = [f for f in findings if f.relation == "contexto"][:MAX_CONTEXT]
    return {"afirmacion": claim, "estado": status, "estado_etiqueta": STATUS_LABELS[status],
            "explicacion": explanation, "hallazgos": [f.to_dict() for f in compared + context],
            "por_comprobar": to_verify, "detectado": detected, "alcance": SCOPE_NOTE, "metodo": METHOD,
            "modo": "extractivo · sin IA generativa"}


def clean(claim: object) -> str:
    if not isinstance(claim, str):
        raise ValueError("La afirmación debe ser texto.")  # noqa: TRY004 - the API maps ValueError to 422
    text = re.sub(r"[\x00-\x08\x0b-\x1f\x7f]", " ", claim)
    text = re.sub(r"\s+", " ", text).strip()
    if not MIN_CHARS <= len(text) <= MAX_CHARS:
        raise ValueError(f"La afirmación debe tener entre {MIN_CHARS} y {MAX_CHARS} caracteres.")
    return text


def check(claim: str, retriever: Retriever) -> dict:
    claim = clean(claim)
    if scan_injection(claim):
        return _result(claim, "abstencion_inyeccion",
                       "El texto contiene instrucciones dirigidas al sistema; se trata como dato y no se ejecuta.",
                       [], ["Reformular la afirmación sin instrucciones."], {})
    norm = normalize_dates(claim)
    asked = _signed_figures(norm)
    periods = _requested_periods(norm)
    where = countries(claim)
    kind = unit_kind(claim)
    current = bool(_CURRENT.search(claim))
    detected = {"cifras": [f for f, _ in asked], "periodos": periods, "paises": sorted(where), "unidad": kind,
                "pide_dato_actual": current}

    # Topic-only search too, so a period missing from the corpus does not hide the topic; "actual" scans
    # the whole corpus for the most recent official datum (same rule as Q&A).
    k = len(retriever.units) if current else TOP_K
    topic = re.sub(r"\b(19|20)\d{2}(-\d{2}){0,2}\b", " ", norm)
    seen, hits = set(), []
    for u, c in retriever.search(norm, k=k) + retriever.search(topic, k=k):
        if u.evidence_id not in seen:
            seen.add(u.evidence_id)
            hits.append((u, c))
    # Pertinence is about the topic; the period is compared afterwards (other period != no evidence).
    with_periods, topic_only = coverage_terms(tokens(norm)), coverage_terms(tokens(norm), keep_years=False)
    pertinent = [u for u, _ in hits if not u.flagged and not _is_null(u)
                 and max(coverage(with_periods, set(tokens(u.text))),
                         coverage(topic_only, set(tokens(u.text)))) >= COVERAGE_THRESHOLD]
    if not pertinent:
        return _result(claim, "evidencia_insuficiente",
                       "El snapshot no contiene evidencia suficientemente pertinente sobre este tema.", [],
                       ["Una fuente primaria que trate directamente el tema (organismo oficial del sector)."], detected)

    if _SCALE.search(claim):
        return _result(claim, "no_comparable",
                       "La cifra usa una escala (millones, miles); SCAYL no convierte escalas automáticamente y no la "
                       "compara para no producir una discrepancia falsa.", [],
                       ["Expresar la cifra completa (por ejemplo, 4 500 000) o verificarla con la fuente primaria."],
                       detected)
    official = [u for u in pertinent if u.official]
    news = [u for u in pertinent if not u.official]
    findings: list[Finding] = []
    to_verify: list[str] = []

    # Official evidence: comparable only with same unit kind, same country and the exact period granularity.
    comparable = []
    for u in official:
        u_where = countries(u.text)
        # Monthly and year-on-year IPC are different indicators even with the same period and unit.
        frequency = re.search(r"\b(mensual|interanual)\b", norm)
        if frequency and u.evidence_id.startswith("ind:inec:INEC.IPC.") and (
                frequency.group(1).upper() not in u.evidence_id):
            findings.append(Finding(u, "contexto", "Otro indicador (mensual/interanual): no se compara."))
            continue
        if kind and _unit_kind_of(u) and _unit_kind_of(u) != kind:
            findings.append(Finding(u, "contexto", "Otra unidad de medida: no se compara."))
            continue
        if where and u_where and not (where & u_where):
            findings.append(Finding(u, "contexto", f"Otro país ({', '.join(sorted(u_where))}): no se compara."))
            continue
        if periods and not _period_matches(periods, u):
            findings.append(Finding(u, "contexto", f"Otro período ({u.ref.period}): no se compara."))
            continue
        comparable.append(u)

    if asked and comparable and periods:
        # Select by the topic first: a matching number must never select a different indicator.
        comparable = _closest(norm, comparable)
        if len({_series(u) for u in comparable}) > 1:
            findings = [Finding(u, "contexto", "Indicador candidato: no se elige por coincidencia de cifra.")
                        for u in comparable] + findings
            return _result(claim, "no_comparable",
                           "Varios indicadores oficiales distintos encajan; precisar el indicador antes de comparar.",
                           findings, ["Precisar el indicador y su definición (por ejemplo, mensual o interanual)."], detected)
        match = [u for u in comparable if any(_matches(f, d, k) for f, d in asked for k in _known_figures(u))]
        if match:
            findings = [Finding(u, "coincide", "La cifra coincide con este registro (redondeo incluido).")
                        for u in match] + findings
            hist = [u for u in match if u.evidence_id.startswith("wb:")]
            explanation = "La cifra y el período coinciden con evidencia oficial del snapshot."
            if current and hist:
                explanation += " Atención: es un dato histórico anual, no una medición actual."
            to_verify.append("Confirmar que la afirmación se refiere al mismo indicador y definición que la fuente.")
            return _result(claim, "compatible_oficial", explanation, findings, to_verify, detected)
        best = _closest(norm, comparable)
        series = {_series(u) for u in best}
        if len(series) == 1:
            comparable = best
            u = comparable[0]
            findings = [Finding(u, "difiere", f"El registro oficial indica {_fmt(u.ref.value)}; la afirmación indica "
                                              f"{', '.join(_fmt(f) for f, _ in asked)}.")] + findings
            note = ("Distintas agencias pueden publicar magnitudes distintas; verificar que se trata del mismo sismo "
                    "(hora y epicentro)." if u.evidence_id.startswith("usgs:")
                    else "Verificar si la afirmación usa otra definición, fuente o revisión del dato.")
            return _result(claim, "discrepancia_oficial",
                           "Hay un registro oficial comparable (mismo tema, país, período y unidad) con otra cifra.",
                           findings, [note, "Citar la fuente de cada cifra si se publica."], detected)
        findings = [Finding(u, "contexto", "Indicador candidato: no se elige uno por la afirmación.")
                    for u in comparable] + findings
        return _result(claim, "no_comparable",
                       "Varios indicadores oficiales distintos encajan con el tema y el período; la comparación sería "
                       "ambigua y no se hace.", findings,
                       ["Precisar el indicador (por ejemplo, variación mensual o interanual) y la fuente."], detected)

    # News: figures in headlines are what a medium reported, never a confirmation.
    reported = [u for u in news if asked and any(_matches(f, d, k) for f, d in asked for k in _known_figures(u))]
    if reported:
        findings = [Finding(u, "coincide", f"Lo reporta {_source(u)} (declaración periodística, no confirmación).")
                    for u in reported] + findings
        return _result(claim, "solo_reportado",
                       "La cifra aparece en titulares de medios; no hay evidencia oficial comparable en el snapshot.",
                       findings, ["Confirmar con la fuente primaria (organismo oficial) antes de presentarlo como hecho.",
                                  "Comprobar si los medios replican una misma fuente."], detected)
    with_figures = [u for u in news if asked and _known_figures(u)]
    if with_figures:
        findings = [Finding(u, "difiere", f"El titular de {_source(u)} menciona otras cifras.")
                    for u in with_figures[:3]] + findings
        return _result(claim, "discrepancia_reportada",
                       "Los titulares pertinentes mencionan cifras distintas; SCAYL no determina cuál es correcta.",
                       findings, ["Contrastar la cifra con la fuente primaria y con el contenido completo del artículo."],
                       detected)

    if current and not periods and official:
        latest = max(official, key=lambda u: (u.ref.period or ""))
        findings = [Finding(latest, "contexto", f"Dato oficial más reciente del snapshot sobre el tema: {latest.ref.period}.")]
        hist = latest.evidence_id.startswith("wb:")
        return _result(claim, "no_comparable",
                       "La afirmación habla de un dato actual sin fecha. " + (
                           "La evidencia oficial disponible es histórica (anual); no se presenta como actual."
                           if hist else f"El dato oficial más reciente del snapshot es de {latest.ref.period}; "
                                        "no equivale a «actual» sin su fecha."),
                       findings, ["Indicar la fecha o período de la cifra.",
                                  "Consultar la publicación oficial más reciente del indicador."], detected)
    findings = findings + [Finding(u, "contexto", "Evidencia pertinente sin cifra comparable.")
                           for u in (comparable + news)[:4] if u not in [f.unit for f in findings]]
    needs = []
    if periods and official and not comparable:
        needs.append(f"El snapshot no tiene datos oficiales del período {', '.join(periods)} para este tema.")
    if asked and not periods:
        needs.append("Indicar el período (año, mes o fecha) de la cifra para poder compararla.")
    if not asked:
        needs.append("La afirmación no contiene una cifra comparable; verificar el hecho con la fuente primaria.")
    if not where and official:
        needs.append("Indicar el país o lugar al que se refiere la cifra.")
    needs.append("Consultar la fuente primaria del dato.")
    return _result(claim, "no_comparable",
                   "Hay evidencia sobre el tema, pero no con el mismo período, país o unidad: no se puede comparar.",
                   findings[:6], needs, detected)
