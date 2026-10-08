"""Official-source linking, Temporal Guard and deterministic numeric conflicts (ARCHITECTURE §4.4–4.5).

Rule of thumb: never force a relation. World Bank data is historical CONTEXT, never confirmation of
a headline and never "current". USGS confirms a seismic headline only when time and magnitude match.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import timedelta

from scayl.contracts import (
    Claim,
    ClaimStatus,
    ClaimType,
    Conflict,
    ConflictKind,
    ConflictVersion,
    EvidenceKind,
    EvidenceRef,
    IndicatorObservation,
    NewsItem,
    SeismicEvent,
    TemporalWarning,
    Topic,
)

SEISMIC_WINDOW = timedelta(hours=48)
MAGNITUDE_TOLERANCE = 0.3
MAGNITUDE_CONFLICT = 0.1

# Topic -> pertinent World Bank indicators for Panama (context only).
TOPIC_INDICATORS: dict[Topic, list[str]] = {
    Topic.ECONOMIA: ["FP.CPI.TOTL.ZG", "NY.GDP.MKTP.KD.ZG", "SL.UEM.TOTL.ZS"],
    Topic.LOGISTICA_CANAL: ["NE.EXP.GNFS.ZS"],
}
INDICATOR_KEYWORDS = {
    "FP.CPI.TOTL.ZG": r"inflaci[oó]n|precios|ipc",
    "NY.GDP.MKTP.KD.ZG": r"\bpib\b|crecimiento econ[oó]mico|econom[ií]a crec",
    "SL.UEM.TOTL.ZS": r"desemple|empleo",
    "NE.EXP.GNFS.ZS": r"exportaci",
    "IT.NET.USER.ZS": r"internet",
    "SP.POP.TOTL": r"poblaci[oó]n",
}

_SEISMIC_WORDS = re.compile(r"\b(sismo|temblor|terremoto|movimiento tel[uú]rico|earthquake)\b", re.IGNORECASE)
_MAGNITUDE = re.compile(r"(?:magnitud|grados|\bM)\s*(?:de\s*)?(\d(?:[.,]\d)?)|(\d[.,]\d)\s*(?:de magnitud|grados)",
                        re.IGNORECASE)
_PERCENT = re.compile(r"(\d+(?:[.,]\d+)?)\s*%")


def news_ref(item: NewsItem, field: str = "titulo") -> EvidenceRef:
    return EvidenceRef(evidence_id=f"news:{item.id_noticia}", kind=EvidenceKind.NEWS, field=field,
                       value=item.titulo, url=item.url, excerpt=item.titulo)


def headline_magnitude(item: NewsItem) -> float | None:
    if not _SEISMIC_WORDS.search(item.titulo):
        return None
    m = _MAGNITUDE.search(item.titulo)
    if not m:
        return None
    return float((m.group(1) or m.group(2)).replace(",", "."))


def is_seismic(items: list[NewsItem]) -> bool:
    return any(_SEISMIC_WORDS.search(i.titulo) for i in items)


@dataclass
class SeismicLink:
    evidence: list[EvidenceRef]
    claims: list[Claim]  # confirming claims (headline magnitude matches USGS): may become central
    conflicts: list[Conflict]
    context: list[Claim] = field(default_factory=list)  # nearby USGS event that does NOT confirm the headline

    @property
    def any(self) -> bool:
        return bool(self.claims or self.context)


def _usgs_refs(q: SeismicEvent) -> tuple[EvidenceRef, EvidenceRef]:
    mag = EvidenceRef(evidence_id=f"usgs:{q.id}", kind=EvidenceKind.SEISMIC, field="magnitude", value=q.magnitude,
                      period=q.time.isoformat().replace("+00:00", "Z") if q.time else None, url=q.url, excerpt=q.place)
    return mag, mag.model_copy(update={"field": "place", "value": q.place})


def link_seismic(event_id: str, items: list[NewsItem], quakes: list[SeismicEvent]) -> SeismicLink:
    """USGS confirms a seismic headline ONLY if the headline states a magnitude that matches (±0.3) an event
    within ±48 h. Without a headline magnitude, the nearest USGS event is context, never confirmation
    (real case: "IGUP descarta que se haya registrado algún temblor"). A magnitude difference > 0.1 between
    headline and USGS is surfaced as a conflict instead of being silently absorbed."""
    link = SeismicLink([], [], [])
    if not is_seismic(items):
        return link
    eid = event_id.removeprefix("EVT-")
    matched, nearby = [], []
    for it in items:
        when = it.fecha_publicacion or it.fecha_deteccion
        if when is None:
            continue
        mag = headline_magnitude(it)
        where = _seismic_places(it.titulo)
        for q in quakes:
            if q.time is None or abs(q.time - when) > SEISMIC_WINDOW:
                continue
            if _disjoint(where, _seismic_places(q.place or "")):
                continue  # near in time but in another country: neither confirmation nor context (C3)
            gap = abs((q.time - when).total_seconds())
            if mag is not None and q.magnitude is not None and abs(q.magnitude - mag) <= MAGNITUDE_TOLERANCE:
                matched.append((abs(q.magnitude - mag), gap, q, it, mag))
            elif mag is None:
                nearby.append((gap, q))

    if matched:
        _, _, q, item, mag = min(matched, key=lambda c: (c[0], c[1]))
        usgs_mag, usgs_place = _usgs_refs(q)
        link.evidence += [usgs_mag, usgs_place]
        link.claims.append(Claim(
            claim_id=f"CLM-{eid}-001", event_id=event_id,
            statement=f"USGS registró un sismo de magnitud {q.magnitude} ({q.place or 'lugar no indicado'})",
            type=ClaimType.HECHO, status=ClaimStatus.SUSTENTADA, evidence=[usgs_mag, usgs_place],
            reason=f"USGS:{q.id} → magnitude = {q.magnitude}; el titular indica {mag}", extracted_by="rule"))
        if q.magnitude is not None and abs(q.magnitude - mag) > MAGNITUDE_CONFLICT:
            link.conflicts.append(Conflict(
                conflict_id=f"CNF-{eid}-001", event_id=event_id, kind=ConflictKind.NUMERIC, field="magnitud",
                version_a=ConflictVersion(value=str(mag), evidence=[news_ref(item)]),
                version_b=ConflictVersion(value=str(q.magnitude), evidence=[usgs_mag]),
                verification_needed=("Magnitud distinta entre el titular y USGS. Distintas agencias (IGUP, USGS) "
                                     "pueden reportar valores diferentes: citar la fuente de cada cifra.")))
    elif nearby:
        _, q = min(nearby, key=lambda c: c[0])
        usgs_mag, usgs_place = _usgs_refs(q)
        link.evidence += [usgs_mag, usgs_place]
        link.context.append(Claim(
            claim_id=f"CLM-{eid}-ctx", event_id=event_id,
            statement=f"USGS registró un sismo de magnitud {q.magnitude} ({q.place or 'lugar no indicado'}) "
                      f"en las 48 h cercanas a la publicación",
            type=ClaimType.HECHO, status=ClaimStatus.SUSTENTADA, evidence=[usgs_mag, usgs_place],
            reason="Contexto: el titular no indica magnitud, así que este registro NO confirma el titular.",
            extracted_by="rule"))

    # Different magnitudes among headlines of the SAME quake -> conflict, never pick one. Two headlines
    # describe the same quake only if they are close in time and do not name disjoint places (C4).
    mentions = [Mention("magnitud", m, 0.0, _when(i), _seismic_places(i.titulo), frozenset(), frozenset(), None, False, i)
                for i in items if (m := headline_magnitude(i)) is not None]
    pair = _widest_pair(mentions, MAGNITUDE_CONFLICT, max_gap=SEISMIC_WINDOW)
    if pair:
        a, b = pair
        link.conflicts.append(Conflict(
            conflict_id=f"CNF-{eid}-{len(link.conflicts) + 1:03d}", event_id=event_id, kind=ConflictKind.NUMERIC,
            field="magnitud", version_a=ConflictVersion(value=str(a.value), evidence=[news_ref(a.item)]),
            version_b=ConflictVersion(value=str(b.value), evidence=[news_ref(b.item)]),
            verification_needed="Contrastar con USGS y con el Instituto de Geociencias (IGUP)." + _correction_note(items)))
    return link


# --- Deterministic conflict detection (C4) --------------------------------------------------------------
# Two figures are versions of the SAME fact only if: same indicator/measure, same period (when both state
# one), same place (when both name one), same unit, both observations (a projection never contradicts an
# observation, and two forecasts are different forecasts) and they come from different publications.
# Unknown period/place on one side is treated as compatible: the editor must check it (precision first
# would hide real discrepancies between "inflación 1,2%" and "inflación 2,1%" without dates).
_YEAR = re.compile(r"\b(19[89]\d|20[0-4]\d)\b")
_MONTHS = ("enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "setiembre",
           "octubre", "noviembre", "diciembre")
_MONTH_RE = re.compile(r"\b(" + "|".join(_MONTHS) + r")\b", re.IGNORECASE)
_VARIANTS = {"mensual": r"\bmensual", "interanual": r"interanual|anualizad|\ba[nñ]o a a[nñ]o",
             "acumulada": r"acumulad"}
HEADLINE_PROJECTION = re.compile(
    r"\b(proyecta\w*|proyecci[oó]n\w*|prev[eé]n?|previsi[oó]n|estima\w*|pronostica\w*|pron[oó]stico|"
    r"espera que|meta de|crecer[aá]n?|crecer[ií]a|caer[aá]n?|subir[aá]n?|bajar[aá]n?|se ubicar[aá])\b",
    re.IGNORECASE)
_PLACES = ["Bocas del Toro", "Chiriquí", "Chiriqui", "Colón", "Colon", "Darién", "Darien", "Coclé", "Cocle", "Herrera",
           "Los Santos", "Veraguas", "Panamá Oeste", "Panama Oeste", "Guna Yala", "Azuero", "San Miguelito", "Boquete",
           "David", "Chitré", "La Chorrera", "Arraiján", "Tocumen", "Panamá", "Panama", "Costa Rica", "Colombia",
           "México", "Mexico", "Ecuador", "Venezuela", "Nicaragua", "Guatemala", "Honduras", "El Salvador", "Perú",
           "Chile", "Argentina", "Brasil", "República Dominicana", "Cuba", "Estados Unidos", "China", "India"]
_PLACE_RE = re.compile(r"\b(" + "|".join(re.escape(p) for p in _PLACES) + r")\b", re.IGNORECASE)
_DENIAL = re.compile(r"\b(descarta\w*|desmient\w*|desmiente\w*|niega\w*|neg[oó]|no hubo|falso|falsa)\b",
                     re.IGNORECASE)
_CORRECTION = re.compile(r"\b(corrig\w*|corrige\w*|rectific\w*|fe de erratas)\b", re.IGNORECASE)
_STOP = {"panama", "para", "como", "esta", "este", "sobre", "tras", "desde", "entre", "hasta", "segun", "hace",
         "haya", "sido", "registrado", "registro", "dice", "informa", "reporta"}
INDICATOR_WINDOW = 60  # max characters between an indicator keyword and the figure attributed to it


def _norm_place(p: str) -> str:
    import unicodedata
    p = unicodedata.normalize("NFKD", p).encode("ascii", "ignore").decode().lower()
    return {"panama oeste": "panama oeste"}.get(p, p)


def _places(text: str) -> frozenset[str]:
    found = {_norm_place(m.group(0)) for m in _PLACE_RE.finditer(text)}
    # "Canal de Panamá" names the waterway, not a place that distinguishes national from local figures
    if re.search(r"canal de panam[aá]", text, re.IGNORECASE) and len(_PLACE_RE.findall(text)) == 1:
        found.discard("panama")
    return frozenset(found)


_COUNTRIES = {"panama", "costa rica", "colombia", "mexico", "ecuador", "venezuela", "nicaragua", "guatemala",
              "honduras", "el salvador", "peru", "chile", "argentina", "brasil", "republica dominicana", "cuba",
              "estados unidos", "china", "india"}


def _seismic_places(text: str) -> frozenset[str]:
    """Country level for quakes: a quake felt in Chiriquí and 'in Panamá' can be the same quake, so any
    Panamanian place maps to 'panama'. Different countries only -> different quakes (time also checked)."""
    return frozenset(p if p in _COUNTRIES else "panama" for p in (
        _norm_place(m.group(0)) for m in _PLACE_RE.finditer(text)))


def foreign_only(text: str) -> bool:
    """The headline names places and none of them is Panamanian (country mismatch guard, C3)."""
    places = _seismic_places(text)
    return bool(places) and "panama" not in places


def _when(item: NewsItem):
    return item.fecha_publicacion or item.fecha_deteccion


@dataclass(frozen=True)
class Mention:
    """One figure in one headline, with the context needed to decide comparability."""

    field: str
    value: float
    precision: float  # half a unit of the last stated digit: "9%" ±0.5, "9,4%" ±0.05 (rounding is not conflict)
    when: object
    places: frozenset[str]
    years: frozenset[str]
    months: frozenset[str]
    variant: str | None
    projection: bool
    item: NewsItem


def _disjoint(a: frozenset, b: frozenset) -> bool:
    return bool(a) and bool(b) and not (a & b)


def comparable(a: Mention, b: Mention, max_gap: timedelta | None = None) -> bool:
    """True when two mentions can be versions of the same fact (C4 rules above)."""
    if a.item.id_noticia == b.item.id_noticia or a.field != b.field:
        return False
    if _disjoint(a.places, b.places) or _disjoint(a.years, b.years) or _disjoint(a.months, b.months):
        return False
    if a.variant and b.variant and a.variant != b.variant:
        return False
    if a.projection or b.projection:
        return False
    return max_gap is None or not a.when or not b.when or abs(a.when - b.when) <= max_gap


def _widest_pair(mentions: list[Mention], min_diff: float,
                 max_gap: timedelta | None = None) -> tuple[Mention, Mention] | None:
    pairs = [(abs(a.value - b.value), a, b) for n, a in enumerate(mentions) for b in mentions[n + 1:]
             if comparable(a, b, max_gap)
             and abs(a.value - b.value) > max(min_diff, a.precision, b.precision)]
    if not pairs:
        return None
    _, a, b = max(pairs, key=lambda p: p[0])
    return (a, b) if a.value <= b.value else (b, a)


def _precision(raw: str) -> float:
    decimals = len(re.split(r"[.,]", raw)[1]) if re.search(r"[.,]", raw) else 0
    return 0.5 * 10 ** -decimals


def percent_mentions(item: NewsItem) -> list[Mention]:
    """Each percentage is attributed to the NEAREST indicator keyword (within INDICATOR_WINDOW chars), so
    "precios suben 4% y exportaciones caen 9%" yields CPI=4 and exports=9, never CPI=9."""
    title = item.titulo
    keywords = [(ind, m.start(), m.end()) for ind, kw in INDICATOR_KEYWORDS.items()
                for m in re.finditer(kw, title, re.IGNORECASE)]
    if not keywords:
        return []
    years = frozenset(_YEAR.findall(title))
    months = frozenset(m.lower().replace("setiembre", "septiembre") for m in _MONTH_RE.findall(title))
    variant = next((v for v, rx in _VARIANTS.items() if re.search(rx, title, re.IGNORECASE)), None)
    out = []
    for m in _PERCENT.finditer(title):
        dist, ind = min((max(s - m.end(), m.start() - e, 0), ind) for ind, s, e in keywords)
        if dist > INDICATOR_WINDOW:
            continue
        out.append(Mention(ind, float(m.group(1).replace(",", ".")), _precision(m.group(1)), _when(item),
                           _places(title), years, months, variant, bool(HEADLINE_PROJECTION.search(title)), item))
    return out


def _correction_note(items: list[NewsItem]) -> str:
    if any(_CORRECTION.search(i.titulo) for i in items):
        return " Una de las publicaciones informa una corrección: verificar cuál es la cifra vigente y su fecha."
    return ""


def percent_conflicts(event_id: str, items: list[NewsItem], start: int = 1) -> list[Conflict]:
    """Same indicator + same period + same place + same unit (%) + observed, across publications -> conflict."""
    by_field: dict[str, list[Mention]] = {}
    for it in items:
        for mention in percent_mentions(it):
            by_field.setdefault(mention.field, []).append(mention)
    out = []
    for ind in sorted(by_field):
        pair = _widest_pair(by_field[ind], 0.0)
        if not pair:
            continue
        lo, hi = pair
        out.append(Conflict(
            conflict_id=f"CNF-{event_id.removeprefix('EVT-')}-{start + len(out):03d}", event_id=event_id,
            kind=ConflictKind.NUMERIC, field=ind,
            version_a=ConflictVersion(value=f"{lo.value}%", evidence=[news_ref(lo.item)]),
            version_b=ConflictVersion(value=f"{hi.value}%", evidence=[news_ref(hi.item)]),
            verification_needed=("Confirmar cifra, período y fuente primaria (p. ej., INEC) antes de publicar."
                                 + _correction_note(items))))
    return out


def _content_tokens(text: str) -> set[str]:
    import unicodedata
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().lower()
    return {t for t in re.findall(r"[a-z]{4,}", text) if t not in _STOP and not _DENIAL.search(t)
            and t != "sintetico"}


def denial_conflicts(event_id: str, items: list[NewsItem], start: int = 1) -> list[Conflict]:
    """One publication asserts a fact and another (in the same event) denies it -> semantic conflict.
    Requires >= 2 shared content words besides 'Panamá', so unrelated denials are not paired."""
    denials = [i for i in items if _DENIAL.search(i.titulo)]
    asserts = [i for i in items if not _DENIAL.search(i.titulo)]
    best = None
    for d in denials:
        for a in asserts:
            shared = _content_tokens(d.titulo) & _content_tokens(a.titulo)
            if len(shared) >= 2 and (best is None or len(shared) > best[0]):
                best = (len(shared), a, d)
    if best is None:
        return []
    _, a, d = best
    return [Conflict(
        conflict_id=f"CNF-{event_id.removeprefix('EVT-')}-{start:03d}", event_id=event_id,
        kind=ConflictKind.SEMANTIC, field="hecho_central",
        version_a=ConflictVersion(value=a.titulo, evidence=[news_ref(a)]),
        version_b=ConflictVersion(value=d.titulo, evidence=[news_ref(d)]),
        verification_needed="Una publicación afirma el hecho y otra lo descarta o desmiente: confirmar con la "
                            "fuente primaria antes de producir.")]


def link_indicators(topic: Topic, items: list[NewsItem], observations: list[IndicatorObservation],
                    country: str = "PAN") -> tuple[list[EvidenceRef], list[TemporalWarning]]:
    """Latest non-null value of pertinent indicators, as historical CONTEXT with a temporal warning.
    Never attached to stories that only name other countries (a Panama series is not their context)."""
    if items and all(foreign_only(i.titulo) for i in items):
        return [], []
    wanted = set(TOPIC_INDICATORS.get(topic, []))
    text = " ".join(i.titulo for i in items)
    wanted |= {ind for ind, kw in INDICATOR_KEYWORDS.items() if re.search(kw, text, re.IGNORECASE)}
    refs, warnings = [], []
    for ind in sorted(wanted):
        rows = [o for o in observations if o.fuente == "wb" and o.pais_iso3 == country and o.indicador_id == ind
                and o.valor is not None]
        if not rows:
            continue
        latest = max(rows, key=lambda o: o.anio)
        ref = EvidenceRef(evidence_id=f"wb:{country}:{ind}:{latest.anio}", kind=EvidenceKind.INDICATOR,
                          field="valor", value=latest.valor, period=str(latest.anio), url=latest.fuente_url,
                          excerpt=f"{latest.indicador_nombre or ind} = {latest.valor} {latest.unidad or ''}".strip())
        refs.append(ref)
        warnings.append(TemporalWarning(
            evidence_id=ref.evidence_id, period=str(latest.anio),
            message=f"Dato histórico — {latest.anio}. No presentarlo como medición actual."))
    return refs, warnings
