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
        for q in quakes:
            if q.time is None or abs(q.time - when) > SEISMIC_WINDOW:
                continue
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

    # Different magnitudes among headlines of the same event -> conflict, never pick one.
    values = sorted({m for m in (headline_magnitude(i) for i in items) if m is not None})
    if len(values) >= 2 and values[-1] - values[0] > MAGNITUDE_CONFLICT:
        a = next(i for i in items if headline_magnitude(i) == values[0])
        b = next(i for i in items if headline_magnitude(i) == values[-1])
        link.conflicts.append(Conflict(
            conflict_id=f"CNF-{eid}-{len(link.conflicts) + 1:03d}", event_id=event_id, kind=ConflictKind.NUMERIC,
            field="magnitud", version_a=ConflictVersion(value=str(values[0]), evidence=[news_ref(a)]),
            version_b=ConflictVersion(value=str(values[-1]), evidence=[news_ref(b)]),
            verification_needed="Contrastar con USGS y con el Instituto de Geociencias (IGUP)."))
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
