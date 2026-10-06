"""Build a small, fully SYNTHETIC UIBundle so the UI can be built before the core.

Usage: python scripts/make_ui_fixture.py  -> tests/fixtures/ui_bundle.example.json

All content here is invented for interface development and is labelled synthetic.
It must never be presented as real TVN/GDELT news.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scayl.contracts import (  # noqa: E402
    Claim,
    ClaimStatus,
    ClaimType,
    Conflict,
    ConflictKind,
    ConflictVersion,
    EvidenceKind,
    EvidenceRef,
    EvidenceStatus,
    Event,
    GenerationMeta,
    InvestigationGap,
    PriorityScore,
    PriorityTier,
    ProvenanceGroup,
    ProvenanceLabel,
    ScoreComponents,
    SourceDNA,
    StoryPackage,
    TaggedSentence,
    TemporalWarning,
    Topic,
    UIBundle,
    ValidationReport,
)

OUT = Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "ui_bundle.example.json"
UTC = timezone.utc
NO_INDEP = "La procedencia independiente no puede determinarse con la evidencia disponible."
SCOPE = "Basado únicamente en titular/metadatos."
WEIGHTS = {"R": 30, "I": 25, "U": 20, "N": 15, "E": 10}


def score(r: float, i: float, u: float, n: float, e: float, why: dict[str, str]) -> PriorityScore:
    comps = ScoreComponents(R=r, I=i, U=u, N=n, E=e, rationale=why)
    p = round(sum(WEIGHTS[k] * getattr(comps, k) for k in WEIGHTS), 1)
    tier = PriorityTier.ALTO if p >= 70 else PriorityTier.MEDIO if p >= 40 else PriorityTier.BAJO
    return PriorityScore(score=p, tier=tier, components=comps, rules_version="scoring-v1")


def news_ref(nid: str, title: str) -> EvidenceRef:
    return EvidenceRef(evidence_id=f"news:{nid}", kind=EvidenceKind.NEWS, field="titulo",
                       value=title, url=f"https://example.invalid/{nid}", excerpt=title)


def build() -> UIBundle:
    t1 = "[SINTÉTICO] Sismo de magnitud 4.6 sacude el occidente de Panamá"
    usgs = EvidenceRef(evidence_id="usgs:syn0001", kind=EvidenceKind.SEISMIC, field="magnitude",
                       value=4.6, period="2025-09-12T03:14:00Z",
                       url="https://earthquake.usgs.gov/earthquakes/eventpage/syn0001")
    e1 = Event(
        event_id="EVT-0001", title=t1, topic=Topic.EVENTOS_NATURALES, topic_confidence=0.91,
        member_ids=["syn-n001", "syn-n002", "syn-n003"],
        first_published=datetime(2025, 9, 12, 4, 0, tzinfo=UTC),
        last_published=datetime(2025, 9, 12, 9, 30, tzinfo=UTC),
        first_detected=datetime(2025, 9, 12, 4, 15, tzinfo=UTC),
        entities=["Panamá", "Chiriquí"],
        source_dna=SourceDNA(
            publications=3, outlets=3,
            groups=[
                ProvenanceGroup(group_id="PG-1", label=ProvenanceLabel.PROCEDENCIA_COMUN_IDENTIFICADA,
                                member_ids=["syn-n002", "syn-n003"],
                                basis="Titular idéntico en dos medios; firma de agencia en ambos."),
                ProvenanceGroup(group_id="PG-2", label=ProvenanceLabel.INDEPENDENCIA_DESCONOCIDA,
                                member_ids=["syn-n001"], basis="Sin información de procedencia."),
            ],
            confirmed_independent=0, max_possible_independent=2, statement=NO_INDEP),
        official_evidence=[usgs],
        claims=[
            Claim(claim_id="CLM-0001-001", event_id="EVT-0001", statement="La magnitud fue 4.6",
                  type=ClaimType.HECHO, status=ClaimStatus.SUSTENTADA, evidence=[usgs],
                  reason="USGS:syn0001 → magnitude = 4.6", extracted_by="rule"),
            Claim(claim_id="CLM-0001-002", event_id="EVT-0001", statement="El sismo causó daños",
                  type=ClaimType.HECHO, status=ClaimStatus.SIN_SUSTENTO,
                  reason="La evidencia confirma el sismo pero no contiene datos verificados de daños.",
                  extracted_by="rule"),
        ],
        priority=score(0.9, 0.7, 0.9, 0.8, 0.7, {
            "R": "Menciona Panamá; tema en alcance", "I": "Evento natural M≥4.5",
            "U": "Publicado hace <24 h respecto al corte", "N": "Sin evento previo similar",
            "E": "1 fuente oficial; 0 independientes confirmadas"}),
        evidence_status=EvidenceStatus.SUFICIENTE_PARA_BORRADOR,
        evidence_status_reason="El hecho central (sismo, magnitud) está respaldado por USGS.",
        recommended_action="Preparar borrador; verificar daños con SINAPROC antes de mencionarlos.",
        gap=InvestigationGap(
            we_know=["CLM-0001-001"], it_is_claimed=[],
            we_infer=["[INFERENCIA] El sismo fue perceptible en Chiriquí (basado en la ubicación reportada por USGS)."],
            we_dont_know=["Si hubo daños o personas afectadas."],
            investigate_next=["¿SINAPROC reporta daños?", "¿Hubo réplicas?", "¿Qué zonas lo sintieron?"]),
        text_scope_note=SCOPE, synthetic=True,
    )
    wb = EvidenceRef(evidence_id="wb:PAN:FP.CPI.TOTL.ZG:2024", kind=EvidenceKind.INDICATOR,
                     field="valor", value=0.7, period="2024",
                     url="https://data.worldbank.org/indicator/FP.CPI.TOTL.ZG?locations=PA")
    e2 = Event(
        event_id="EVT-0002", title="[SINTÉTICO] Inflación en Panamá: medios reportan cifras distintas",
        topic=Topic.ECONOMIA, topic_confidence=0.84, member_ids=["syn-n010", "syn-n011"],
        first_published=datetime(2025, 9, 20, 13, 0, tzinfo=UTC),
        last_published=datetime(2025, 9, 21, 15, 0, tzinfo=UTC),
        first_detected=datetime(2025, 9, 20, 13, 5, tzinfo=UTC),
        entities=["Panamá"],
        source_dna=SourceDNA(publications=2, outlets=2, groups=[
            ProvenanceGroup(group_id="PG-3", label=ProvenanceLabel.INDEPENDENCIA_DESCONOCIDA,
                            member_ids=["syn-n010", "syn-n011"], basis="Titulares distintos; sin firma.")],
            confirmed_independent=0, max_possible_independent=2, statement=NO_INDEP),
        official_evidence=[wb],
        conflicts=[Conflict(
            conflict_id="CNF-0002-001", event_id="EVT-0002", kind=ConflictKind.NUMERIC, field="inflacion_anual",
            version_a=ConflictVersion(value="1.2%", evidence=[news_ref("syn-n010", "[SINTÉTICO] Inflación sube a 1.2%")]),
            version_b=ConflictVersion(value="2.1%", evidence=[news_ref("syn-n011", "[SINTÉTICO] Inflación llega a 2.1%")]),
            verification_needed="Confirmar cifra y período con INEC antes de publicar cualquiera.")],
        temporal_warnings=[TemporalWarning(evidence_id=wb.evidence_id, period="2024",
                                           message="Dato histórico — 2024. No presentarlo como medición actual.")],
        priority=score(0.8, 0.8, 0.6, 0.5, 0.4, {"R": "Panamá + economía", "I": "Indicador macro",
                                                   "U": "2 días", "N": "Tema recurrente", "E": "Conflicto sin resolver"}),
        evidence_status=EvidenceStatus.PARCIAL,
        evidence_status_reason="Hay dato oficial histórico, pero las cifras recientes están en conflicto.",
        recommended_action="Requiere verificación: no publicar ninguna cifra hasta confirmar con INEC.",
        text_scope_note=SCOPE, synthetic=True,
    )
    e3 = Event(
        event_id="EVT-0003", title="[SINTÉTICO] Rumor de cierre de esclusas del Canal circula en redes",
        topic=Topic.LOGISTICA_CANAL, topic_confidence=0.77, member_ids=["syn-n020"],
        first_published=datetime(2025, 9, 29, 22, 0, tzinfo=UTC),
        last_published=datetime(2025, 9, 29, 22, 0, tzinfo=UTC),
        first_detected=datetime(2025, 9, 29, 22, 10, tzinfo=UTC),
        source_dna=SourceDNA(publications=1, outlets=1, groups=[
            ProvenanceGroup(group_id="PG-4", label=ProvenanceLabel.INDEPENDENCIA_DESCONOCIDA,
                            member_ids=["syn-n020"], basis="Fuente única.")],
            confirmed_independent=0, max_possible_independent=1, statement=NO_INDEP),
        claims=[Claim(claim_id="CLM-0003-001", event_id="EVT-0003",
                      statement="Las esclusas cerrarán la próxima semana", type=ClaimType.DECLARACION,
                      status=ClaimStatus.SOLO_REPORTADA, attributed_to="medio syn-n020",
                      evidence=[news_ref("syn-n020", "[SINTÉTICO] Rumor de cierre de esclusas")],
                      reason="Solo un medio lo afirma; no hay fuente oficial en el corpus.", extracted_by="rule")],
        priority=score(0.9, 0.9, 1.0, 0.9, 0.1, {"R": "Canal de Panamá", "I": "Logística global",
                                                   "U": "<12 h", "N": "Nuevo", "E": "Fuente única, sin oficial"}),
        evidence_status=EvidenceStatus.INSUFICIENTE,
        evidence_status_reason="Una sola publicación y ninguna fuente oficial.",
        recommended_action="Investigar: contactar a la ACP. Prioridad alta NO habilita publicación.",
        text_scope_note=SCOPE, synthetic=True,
    )
    pkg = StoryPackage(
        package_id="PKG-0001-v1", event_id="EVT-0001", proposed_title="[SINTÉTICO] Sismo de 4.6 en el occidente",
        public_interest_angle="Informar con precisión y evitar alarma por daños no confirmados.",
        brief=[TaggedSentence(text="USGS registró un sismo de magnitud 4.6.", tag=ClaimType.HECHO,
                              claim_ids=["CLM-0001-001"]),
               TaggedSentence(text="No hay datos verificados de daños en el corpus.", tag=ClaimType.HECHO,
                              claim_ids=["CLM-0001-002"])],
        investigation_questions=["¿SINAPROC reporta daños?", "¿Hubo réplicas?", "¿Qué zonas lo sintieron?"],
        script=[TaggedSentence(text="Un sismo de magnitud 4.6 fue registrado por el USGS.", tag=ClaimType.HECHO,
                               claim_ids=["CLM-0001-001"])],
        social_copy=TaggedSentence(text="USGS: sismo de magnitud 4.6. Sin reportes verificados de daños.",
                                   tag=ClaimType.HECHO, claim_ids=["CLM-0001-001"]),
        pending_verifications=["Daños (SINAPROC)"], sources=[usgs], scope_disclaimer=SCOPE,
        validation=ValidationReport(passed=True),
        generated_by=GenerationMeta(mode="template", model=None, prompt_version=None, latency_ms=None,
                                    tokens_in=None, tokens_out=None,
                                    created_at=datetime(2025, 10, 1, 0, 0, tzinfo=UTC)),
    )
    return UIBundle(snapshot_version="fixture-synthetic-0", snapshot_cutoff_utc=datetime(2025, 10, 1, tzinfo=UTC),
                    signals_total=6, signals_valid=6, events=[e1, e2, e3], packages=[pkg])


if __name__ == "__main__":
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(build().model_dump(mode="json"), ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {OUT}")
