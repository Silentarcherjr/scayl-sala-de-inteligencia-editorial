"""Official-source linking, Temporal Guard and deterministic numeric conflicts (ARCHITECTURE §4.4–4.5).

Rule of thumb: never force a relation. World Bank data is historical CONTEXT, never confirmation of
a headline and never "current". USGS confirms a seismic headline only when time and magnitude match.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
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
PERCENT_CONFLICT_REL = 0.05

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
    claims: list[Claim]
    conflicts: list[Conflict]


def link_seismic(event_id: str, items: list[NewsItem], quakes: list[SeismicEvent]) -> SeismicLink:
    """Match seismic headlines with USGS events by time (±48 h) and magnitude (±0.3)."""
    link = SeismicLink([], [], [])
    if not is_seismic(items):
        return link
    candidates = []
    for it in items:
        when = it.fecha_publicacion or it.fecha_deteccion
        if when is None:
            continue
        mag = headline_magnitude(it)
        for q in quakes:
            if q.time is None or abs(q.time - when) > SEISMIC_WINDOW:
                continue
            if mag is not None and q.magnitude is not None and abs(q.magnitude - mag) > MAGNITUDE_TOLERANCE:
                continue
            candidates.append((abs((q.time - when).total_seconds()), q, it, mag))
    if not candidates:
        return link

    _, q, _item, _mag = min(candidates, key=lambda c: c[0])
    usgs_mag = EvidenceRef(evidence_id=f"usgs:{q.id}", kind=EvidenceKind.SEISMIC, field="magnitude",
                           value=q.magnitude, period=q.time.isoformat().replace("+00:00", "Z") if q.time else None,
                           url=q.url, excerpt=q.place)
    usgs_place = usgs_mag.model_copy(update={"field": "place", "value": q.place})
    link.evidence += [usgs_mag, usgs_place]
    n = 1
    if q.magnitude is not None:
        link.claims.append(Claim(
            claim_id=f"CLM-{event_id.removeprefix('EVT-')}-{n:03d}", event_id=event_id,
            statement=f"USGS registró un sismo de magnitud {q.magnitude} ({q.place or 'lugar no indicado'})",
            type=ClaimType.HECHO, status=ClaimStatus.SUSTENTADA, evidence=[usgs_mag, usgs_place],
            reason=f"USGS:{q.id} → magnitude = {q.magnitude}", extracted_by="rule"))
    # Different magnitudes among headlines of the same event -> conflict, never pick one.
    mags = {(headline_magnitude(i), i.id_noticia) for i in items if headline_magnitude(i) is not None}
    values = sorted({m for m, _ in mags})
    if len(values) >= 2 and values[-1] - values[0] > MAGNITUDE_CONFLICT:
        a = next(i for i in items if headline_magnitude(i) == values[0])
        b = next(i for i in items if headline_magnitude(i) == values[-1])
        link.conflicts.append(Conflict(
            conflict_id=f"CNF-{event_id.removeprefix('EVT-')}-001", event_id=event_id, kind=ConflictKind.NUMERIC,
            field="magnitud", version_a=ConflictVersion(value=str(values[0]), evidence=[news_ref(a)]),
            version_b=ConflictVersion(value=str(values[-1]), evidence=[news_ref(b)]),
            verification_needed=f"Contrastar con USGS:{q.id} (magnitud {q.magnitude}) y con el Instituto de Geociencias."))
    return link


def percent_conflicts(event_id: str, items: list[NewsItem], start: int = 1) -> list[Conflict]:
    """Same indicator keyword + incompatible percentages across headlines -> conflict."""
    by_indicator: dict[str, list[tuple[float, NewsItem]]] = {}
    for it in items:
        for ind, kw in INDICATOR_KEYWORDS.items():
            if re.search(kw, it.titulo, re.IGNORECASE):
                for m in _PERCENT.finditer(it.titulo):
                    by_indicator.setdefault(ind, []).append((float(m.group(1).replace(",", ".")), it))
    out = []
    for ind, vals in by_indicator.items():
        lo, hi = min(vals, key=lambda v: v[0]), max(vals, key=lambda v: v[0])
        if hi[0] and (hi[0] - lo[0]) / hi[0] > PERCENT_CONFLICT_REL:
            out.append(Conflict(
                conflict_id=f"CNF-{event_id.removeprefix('EVT-')}-{start + len(out):03d}", event_id=event_id,
                kind=ConflictKind.NUMERIC, field=ind,
                version_a=ConflictVersion(value=f"{lo[0]}%", evidence=[news_ref(lo[1])]),
                version_b=ConflictVersion(value=f"{hi[0]}%", evidence=[news_ref(hi[1])]),
                verification_needed="Confirmar cifra, período y fuente primaria (p. ej., INEC) antes de publicar."))
    return out


def link_indicators(topic: Topic, items: list[NewsItem], observations: list[IndicatorObservation],
                    country: str = "PAN") -> tuple[list[EvidenceRef], list[TemporalWarning]]:
    """Latest non-null value of pertinent indicators, as historical CONTEXT with a temporal warning."""
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
