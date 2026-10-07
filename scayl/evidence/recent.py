"""Recent official evidence: ACP Gatún Lake levels and INEC monthly CPI (AP-010, DL-019).

Unlike World Bank context, these series are recent (within the news window) and can SUPPORT a
headline when its figure matches an observation close in time. Projections are never support.
Every value is cited with its period; nothing is presented as "current" without its date.
"""

from __future__ import annotations

import calendar
import re
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta

from scayl.contracts import (
    Claim,
    ClaimStatus,
    ClaimType,
    EvidenceKind,
    EvidenceRef,
    IndicatorObservation,
    NewsItem,
    TemporalWarning,
)
from scayl.evidence.linking import news_ref


@dataclass(frozen=True)
class Series:
    series_id: str
    fuente: str
    nombre: str
    keywords: str
    unit_pattern: str  # how the figure appears in a headline
    tolerance: float
    max_gap: timedelta  # publication must be within this gap AFTER the period ends


SERIES = {
    "ACP.GATUN.NIVEL": Series("ACP.GATUN.NIVEL", "ACP", "nivel del lago Gatún (observado)",
                              r"gat[uú]n|nivel del lago|calado|sequ[ií]a|restricci[oó]n|agua (del|para el) canal",
                              r"(\d+(?:[.,]\d+)?)\s*(?:pies|ft)\b", 0.1, timedelta(days=3)),
    "INEC.IPC.VAR_MENSUAL": Series("INEC.IPC.VAR_MENSUAL", "INEC", "variación mensual del IPC urbano nacional",
                                   r"inflaci[oó]n|\bipc\b|precios al consumidor|costo de vida",
                                   r"(\d+(?:[.,]\d+)?)\s*%", 0.05, timedelta(days=50)),
    "INEC.IPC.VAR_INTERANUAL": Series("INEC.IPC.VAR_INTERANUAL", "INEC", "variación interanual del IPC urbano nacional",
                                      r"inflaci[oó]n|\bipc\b|precios al consumidor|costo de vida",
                                      r"(\d+(?:[.,]\d+)?)\s*%", 0.05, timedelta(days=50)),
}
PROJECTION_KEYWORDS = r"gat[uú]n|nivel del lago|sequ[ií]a|restricci[oó]n"


def period_end(o: IndicatorObservation) -> datetime:
    p = o.periodo or str(o.anio)
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", p):
        return datetime.fromisoformat(p).replace(tzinfo=UTC) + timedelta(days=1)
    if re.fullmatch(r"\d{4}-\d{2}", p):
        y, m = map(int, p.split("-"))
        return datetime(y, m, calendar.monthrange(y, m)[1], tzinfo=UTC) + timedelta(days=1)
    return datetime(int(p[:4]) + 1, 1, 1, tzinfo=UTC)


def evidence_id(o: IndicatorObservation) -> str:
    return f"ind:{o.fuente}:{o.indicador_id}:{o.periodo or o.anio}"


def ref_for(o: IndicatorObservation) -> EvidenceRef:
    label = SERIES[o.indicador_id].nombre if o.indicador_id in SERIES else (o.indicador_nombre or o.indicador_id)
    kind = "proyección (estimación informativa)" if o.es_proyeccion else label
    return EvidenceRef(evidence_id=evidence_id(o), kind=EvidenceKind.INDICATOR, field="valor", value=o.valor,
                       period=o.periodo or str(o.anio), url=o.fuente_url,
                       excerpt=f"{o.fuente.upper()}: {kind}, {o.periodo or o.anio}: {o.valor} {o.unidad or ''}".strip())


@dataclass
class RecentLink:
    confirming: list[Claim] = field(default_factory=list)  # headline figure matches an observation
    context: list[Claim] = field(default_factory=list)  # latest official fact (supported, but not the headline)
    evidence: list[EvidenceRef] = field(default_factory=list)
    warnings: list[TemporalWarning] = field(default_factory=list)


def _usable(observations: list[IndicatorObservation], series_id: str, cutoff: datetime) -> list[IndicatorObservation]:
    return sorted((o for o in observations if o.indicador_id == series_id and o.valor is not None
                   and not o.es_proyeccion and period_end(o) <= cutoff), key=period_end)


def link_recent(event_id: str, items: list[NewsItem], observations: list[IndicatorObservation],
                cutoff: datetime) -> RecentLink:
    link = RecentLink()
    text = " ".join(i.titulo for i in items)
    for sid, s in SERIES.items():
        if not re.search(s.keywords, text, re.IGNORECASE):
            continue
        rows = _usable(observations, sid, cutoff)
        if not rows:
            continue
        # 1) confirmation: same figure, published shortly after the observed period
        for item in items:
            when = item.fecha_publicacion or item.fecha_deteccion
            if when is None:
                continue
            for m in re.finditer(s.unit_pattern, item.titulo, re.IGNORECASE):
                value = float(m.group(1).replace(",", "."))
                candidates = [o for o in rows if timedelta(days=-1) <= when - period_end(o) <= s.max_gap
                              and abs(abs(o.valor) - value) <= s.tolerance]
                if not candidates:
                    continue
                o = min(candidates, key=lambda c: (abs(abs(c.valor) - value), when - period_end(c)))
                ref = ref_for(o)
                link.evidence.append(ref)
                link.confirming.append(Claim(
                    claim_id="tmp", event_id=event_id,
                    statement=f"{s.fuente} registró {s.nombre} de {o.valor} {o.unidad or ''} en {o.periodo}".strip(),
                    type=ClaimType.HECHO, status=ClaimStatus.SUSTENTADA, evidence=[ref, news_ref(item)],
                    reason=(f"La cifra del titular ({value}) coincide con {ref.evidence_id} y la publicación es "
                            f"posterior al período. Verificar que se trate de la misma medida."),
                    extracted_by="rule"))
        # 2) context: latest observation before the event, always cited with its period
        latest = rows[-1]
        ref = ref_for(latest)
        if ref.evidence_id not in {r.evidence_id for r in link.evidence}:
            link.evidence.append(ref)
            link.context.append(Claim(
                claim_id="tmp", event_id=event_id,
                statement=f"Según {s.fuente}, {s.nombre} en {latest.periodo}: {latest.valor} {latest.unidad or ''}".strip(),
                type=ClaimType.HECHO, status=ClaimStatus.SUSTENTADA, evidence=[ref],
                reason="Dato oficial reciente de contexto; no confirma por sí mismo el titular.",
                extracted_by="rule"))
        link.warnings.append(TemporalWarning(
            evidence_id=ref.evidence_id, period=latest.periodo or str(latest.anio),
            message=f"Dato de {latest.periodo} ({s.fuente}). Citarlo siempre con su fecha; no es una medición en tiempo real."))
    # ACP projections: context only, explicitly labelled
    if re.search(PROJECTION_KEYWORDS, text, re.IGNORECASE):
        proj = [o for o in observations if o.fuente == "acp" and o.es_proyeccion and o.valor is not None]
        if proj:
            nxt = min(proj, key=period_end)
            ref = ref_for(nxt)
            link.evidence.append(ref)
            link.warnings.append(TemporalWarning(
                evidence_id=ref.evidence_id, period=nxt.periodo or str(nxt.anio),
                message="Proyección de la ACP (estimación informativa): no es una medición ni un hecho."))
    return link
