"""Assemble one Event from a cluster of publications + official sources (deterministic, no LLM).

Inputs come from Worker B (validated NewsItems, clusters, topics); this module owns the evidence
logic: Source DNA, official linking, Temporal Guard, conflicts, claims, score, status and gap.
LLM-extracted claims (L-10) are merged later and re-validated by the same status rules.
"""

from __future__ import annotations

import re
from datetime import datetime, timedelta

from scayl.contracts import (
    Claim,
    ClaimStatus,
    ClaimType,
    Event,
    IndicatorObservation,
    InvestigationGap,
    NewsItem,
    Origin,
    SeismicEvent,
    TextScope,
    Topic,
)
from scayl.evidence.linking import link_indicators, link_seismic, news_ref, percent_conflicts
from scayl.evidence.provenance import outlet_key, source_dna
from scayl.evidence.scoring import ScoringInput, score
from scayl.evidence.status import evidence_status, recommended_action, verification_sources
from scayl.gen.validators import SCOPE_PHRASE

RECIRCULATION_GAP = timedelta(days=7)
PANAMA_PLACES = [
    "Panamá", "Panama", "Chiriquí", "Colón", "Darién", "Bocas del Toro", "Coclé", "Herrera", "Los Santos",
    "Veraguas", "Panamá Oeste", "Canal de Panamá", "Guna Yala", "Emberá", "Ngäbe", "Azuero", "San Miguelito",
    "David", "Santiago", "Chitré", "La Chorrera", "Arraiján",
]
_PANAMA_RE = re.compile(r"\b(" + "|".join(re.escape(p) for p in PANAMA_PLACES) + r")\b", re.IGNORECASE)


def mentions_panama(items: list[NewsItem]) -> bool:
    return any(_PANAMA_RE.search(" ".join(filter(None, [i.titulo, i.descripcion]))) for i in items)


def entities(items: list[NewsItem]) -> list[str]:
    found = {m.group(0) for i in items for m in _PANAMA_RE.finditer(i.titulo)}
    return sorted(found, key=str.lower)


def is_tvn(item: NewsItem) -> bool:
    return item.origen == Origin.TVN_RSS or "tvn" in outlet_key(item)


def representative(items: list[NewsItem]) -> NewsItem:
    tvn = [i for i in items if is_tvn(i)]
    pool = tvn or items
    # TVN first, then the earliest original publication (undated items last), then id.
    return min(pool, key=lambda i: (i.fecha_publicacion is None, i.fecha_publicacion or i.fecha_extraccion,
                                    i.id_noticia))


def _claim_id(event_id: str, n: int) -> str:
    return f"CLM-{event_id.removeprefix('EVT-')}-{n:03d}"


def build_claims(event_id: str, items: list[NewsItem], rep: NewsItem, seismic_claims: list[Claim],
                 has_conflict: bool, seismic: bool) -> list[Claim]:
    claims = list(seismic_claims)
    others = len({outlet_key(i) for i in items}) - 1
    who = f"{rep.medio or outlet_key(rep)}" + (f" y {others} medio(s) más" if others > 0 else "")
    claims.append(Claim(
        claim_id=_claim_id(event_id, len(claims) + 1), event_id=event_id, statement=rep.titulo.rstrip("."),
        type=ClaimType.DECLARACION,
        status=ClaimStatus.EN_CONFLICTO if has_conflict else ClaimStatus.SOLO_REPORTADA,
        attributed_to=who, evidence=[news_ref(rep)],
        reason=("Hay versiones incompatibles entre publicaciones." if has_conflict
                else "Afirmado por medios; sin respaldo oficial directo en el corpus."),
        extracted_by="rule"))
    if seismic:
        claims.append(Claim(
            claim_id=_claim_id(event_id, len(claims) + 1), event_id=event_id,
            statement="El sismo causó daños o personas afectadas", type=ClaimType.HECHO,
            status=ClaimStatus.SIN_SUSTENTO,
            reason="La evidencia disponible confirma el evento sísmico pero no contiene datos verificados de daños.",
            extracted_by="rule"))
    return claims


def build_gap(topic: Topic, claims: list[Claim], has_official: bool, headline_only: bool) -> InvestigationGap:
    know = [c.claim_id for c in claims if c.status == ClaimStatus.SUSTENTADA]
    claimed = [c.claim_id for c in claims if c.status in (ClaimStatus.SOLO_REPORTADA, ClaimStatus.EN_CONFLICTO)]
    dont_know = [c.statement for c in claims if c.status == ClaimStatus.SIN_SUSTENTO]
    if not has_official:
        dont_know.append("Ninguna fuente oficial del corpus confirma el hecho central.")
    if headline_only:
        dont_know.append("El contenido completo de los artículos (solo se dispone de titular/metadatos).")
    if any(c.status == ClaimStatus.EN_CONFLICTO for c in claims):
        dont_know.append("Cuál de las versiones en conflicto es correcta.")
    source = (verification_sources().get(topic.value) or ["la fuente primaria"])[0]
    questions = [f"¿Qué confirma {source} sobre el hecho central?"]
    questions += [f"¿Qué evidencia respalda o descarta: «{c.statement}»?"
                  for c in claims if c.status != ClaimStatus.SUSTENTADA][:1]
    questions += ["¿Qué fuentes primarias e independientes (no replicadas) pueden consultarse?",
                  "¿Existen datos más recientes y de qué fecha son?"]
    return InvestigationGap(we_know=know, it_is_claimed=claimed, we_infer=[], we_dont_know=dont_know,
                            investigate_next=list(dict.fromkeys(questions))[:3])


def build_event(
    event_id: str,
    items: list[NewsItem],
    topic: Topic,
    topic_confidence: float | None,
    observations: list[IndicatorObservation],
    quakes: list[SeismicEvent],
    cutoff: datetime,
    max_prior_similarity: float | None = None,
) -> Event:
    if not items:
        raise ValueError("an event needs at least one publication")
    rep = representative(items)
    dna = source_dna(items, group_prefix=f"PG-{event_id.removeprefix('EVT-')}")

    seismic = link_seismic(event_id, items, quakes)
    wb_refs, warnings = link_indicators(topic, items, observations)
    conflicts = seismic.conflicts + percent_conflicts(event_id, items, start=len(seismic.conflicts) + 1)
    official = seismic.evidence + wb_refs
    is_seismic_event = bool(seismic.claims)
    claims = build_claims(event_id, items, rep, seismic.claims, bool(conflicts), is_seismic_event)

    pubs = [i.fecha_publicacion for i in items if i.fecha_publicacion]
    dets = [i.fecha_deteccion for i in items if i.fecha_deteccion]
    recirculated = any(i.fecha_publicacion and i.fecha_deteccion and
                       i.fecha_deteccion - i.fecha_publicacion > RECIRCULATION_GAP for i in items)

    priority = score(ScoringInput(
        mentions_panama=mentions_panama(items), is_tvn=any(is_tvn(i) for i in items), topic=topic,
        topic_confidence=topic_confidence, has_official_evidence=bool(official),
        latest_original_publication=max(pubs) if pubs else None, cutoff=cutoff,
        max_prior_similarity=max_prior_similarity, max_possible_independent=dna.max_possible_independent,
        confirmed_independent=dna.confirmed_independent))
    status, reason = evidence_status(claims, conflicts, official, dna)
    headline_only = all(i.alcance_texto == TextScope.TITULAR_METADATOS for i in items)

    return Event(
        event_id=event_id, title=rep.titulo, topic=topic, topic_confidence=topic_confidence,
        member_ids=sorted(i.id_noticia for i in items),
        first_published=min(pubs) if pubs else None, last_published=max(pubs) if pubs else None,
        first_detected=min(dets) if dets else None, is_recirculated=recirculated,
        entities=entities(items), source_dna=dna, official_evidence=official, claims=claims,
        conflicts=conflicts, temporal_warnings=warnings, priority=priority, evidence_status=status,
        evidence_status_reason=reason, recommended_action=recommended_action(priority.tier, status, topic),
        gap=build_gap(topic, claims, bool(official), headline_only),
        text_scope_note=SCOPE_PHRASE if headline_only else "Basado en titular y descripción del RSS.",
        synthetic=any(i.sintetico for i in items),
    )
