"""SCAYL shared data contracts.

LEAD-OWNED, CROSS-CUTTING. Any change to field names, enums or semantics must be
proposed first in docs/AGENT_PROPOSALS.md and bump CONTRACT_VERSION.

Conventions (from the official challenge spec, section 7):
- UTF-8, stable IDs, ISO 8601 datetimes in UTC (UI converts to America/Panama).
- NULL is preserved: missing values are ``None``, never 0 or "".
- Publication date is distinct from detection date (GDELT ``seendate``).
- Original units are kept.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

CONTRACT_VERSION = "0.4.0"  # 0.4.0: SectorBulletin (additive; existing models unchanged)


class _Model(BaseModel):
    model_config = ConfigDict(extra="forbid", use_enum_values=False)


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------


class Topic(str, Enum):
    """Fixed taxonomy from the official spec (stage 2 · Organizar) + OTRO."""

    ECONOMIA = "economia"
    LOGISTICA_CANAL = "logistica_canal"
    TURISMO = "turismo"
    SERVICIOS_PUBLICOS = "servicios_publicos"
    EVENTOS_NATURALES = "eventos_naturales"
    REGULACION = "regulacion"
    OTRO = "otro"


class Origin(str, Enum):
    TVN_RSS = "tvn_rss"
    GDELT = "gdelt"
    SYNTHETIC = "sintetico"  # controlled test cases; must be labelled in the UI


class TextScope(str, Enum):
    """How much of the article the system actually has."""

    TITULAR_METADATOS = "titular_metadatos"
    TITULAR_DESCRIPCION = "titular_descripcion"


class EvidenceKind(str, Enum):
    NEWS = "noticia"
    INDICATOR = "indicador"
    SEISMIC = "sismo"


class ProvenanceLabel(str, Enum):
    """Conservative provenance categories (Source DNA). Never infer copying."""

    MISMO_MEDIO = "mismo_medio"
    PROCEDENCIA_COMUN_IDENTIFICADA = "procedencia_comun_identificada"
    PROCEDENCIA_INDEPENDIENTE_CONFIRMADA = "procedencia_independiente_confirmada"
    INDEPENDENCIA_DESCONOCIDA = "independencia_desconocida"


class ClaimType(str, Enum):
    HECHO = "HECHO"
    DECLARACION = "DECLARACION"
    INFERENCIA = "INFERENCIA"
    HIPOTESIS = "HIPOTESIS"


class ClaimStatus(str, Enum):
    SUSTENTADA = "SUSTENTADA"  # supported by an identified evidence field
    SOLO_REPORTADA = "SOLO_REPORTADA"  # only asserted by media; no official support
    EN_CONFLICTO = "EN_CONFLICTO"  # incompatible versions exist
    SIN_SUSTENTO = "SIN_SUSTENTO"  # no evidence in the corpus


class ConflictKind(str, Enum):
    NUMERIC = "numerico"
    DATE = "fecha"
    UNIT = "unidad"
    PERIOD = "periodo"
    ENTITY = "entidad"
    SEMANTIC = "semantico"


class EvidenceStatus(str, Enum):
    """Official three levels; independent of the priority score."""

    INSUFICIENTE = "insuficiente"
    PARCIAL = "parcial"
    SUFICIENTE_PARA_BORRADOR = "suficiente_para_borrador"


class PriorityTier(str, Enum):
    BAJO = "bajo"  # [0, 40)
    MEDIO = "medio"  # [40, 70)
    ALTO = "alto"  # [70, 100]


class ReviewState(str, Enum):
    NUEVO = "nuevo"
    EN_REVISION = "en_revision"
    REQUIERE_EVIDENCIA = "requiere_evidencia"
    APROBADO_COMO_BORRADOR = "aprobado_como_borrador"  # NOT published
    DESCARTADO = "descartado"


REVIEW_TRANSITIONS: dict[ReviewState, frozenset[ReviewState]] = {
    ReviewState.NUEVO: frozenset({ReviewState.EN_REVISION}),
    ReviewState.EN_REVISION: frozenset(
        {
            ReviewState.REQUIERE_EVIDENCIA,
            ReviewState.APROBADO_COMO_BORRADOR,
            ReviewState.DESCARTADO,
        }
    ),
    ReviewState.REQUIERE_EVIDENCIA: frozenset({ReviewState.EN_REVISION}),
    ReviewState.APROBADO_COMO_BORRADOR: frozenset({ReviewState.EN_REVISION}),
    ReviewState.DESCARTADO: frozenset({ReviewState.EN_REVISION}),
}


def can_transition(src: ReviewState, dst: ReviewState) -> bool:
    return dst in REVIEW_TRANSITIONS[src]


# ---------------------------------------------------------------------------
# Normalized source records (data/processed/*)
# ---------------------------------------------------------------------------


class NewsItem(_Model):
    """One row of noticias.csv (official minimum fields + SCAYL extras)."""

    id_noticia: str
    titulo: str
    url: str | None
    medio: str | None  # outlet name or domain
    idioma: str | None
    fecha_publicacion: datetime | None  # when the outlet published
    fecha_deteccion: datetime | None  # GDELT seendate / RSS fetch time
    fecha_extraccion: datetime
    tema: Topic | None = None  # filled by the classifier, None before
    origen: Origin
    alcance_texto: TextScope
    licencia: str | None
    # extras
    descripcion: str | None = None  # RSS description, only if rights allow
    sintetico: bool = False
    quality_flags: list[str] = Field(default_factory=list)


class IndicatorObservation(_Model):
    """One row of indicadores.csv (WB, annual) or indicadores_recientes.csv (ACP/INEC, AP-010).

    ``valor`` stays None when missing. Annual WB rows keep the defaults below. Recent series set
    ``periodo`` ("2026-07" monthly, "2026-09-28" daily) and ``anio`` = year of the period.
    """

    pais_iso3: str
    indicador_id: str
    indicador_nombre: str | None = None
    anio: int
    valor: float | None
    unidad: str | None
    fuente_url: str
    fecha_extraccion: datetime
    licencia: str | None
    periodo: str | None = None
    fuente: str = "wb"  # wb | acp | inec
    frecuencia: Literal["anual", "mensual", "diaria"] = "anual"
    es_proyeccion: bool = False  # ACP projections are estimates, never measurements


class SeismicEvent(_Model):
    """One feature of eventos.geojson, flattened."""

    id: str
    magnitude: float | None
    mag_type: str | None = None
    time: datetime | None
    updated: datetime | None
    longitude: float | None
    latitude: float | None
    depth: float | None
    place: str | None
    status: str | None
    url: str | None


# ---------------------------------------------------------------------------
# Evidence, claims and analysis
# ---------------------------------------------------------------------------


class EvidenceRef(_Model):
    """A citation is an evidence ID + the exact field that supports a claim.

    evidence_id formats:
      news:<id_noticia>
      wb:<pais_iso3>:<indicador_id>:<anio>
      usgs:<id>
    """

    evidence_id: str
    kind: EvidenceKind
    field: str  # e.g. "titulo", "valor", "magnitude"
    value: str | float | int | None
    period: str | None = None  # e.g. "2023" for annual data; None for news
    url: str | None = None
    excerpt: str | None = None  # short quoted text, never the full article


class ProvenanceGroup(_Model):
    group_id: str
    label: ProvenanceLabel
    member_ids: list[str]  # news ids
    basis: str  # human-readable reason, e.g. "titular idéntico; firma EFE"


class SourceDNA(_Model):
    publications: int
    outlets: int
    groups: list[ProvenanceGroup]
    confirmed_independent: int  # usually 0 from headlines alone
    max_possible_independent: int  # upper bound after collapsing common provenance
    statement: str  # e.g. "La procedencia independiente no puede determinarse..."


class Claim(_Model):
    claim_id: str  # CLM-<event>-NNN
    event_id: str
    statement: str
    type: ClaimType
    status: ClaimStatus
    attributed_to: str | None = None  # required when type == DECLARACION
    evidence: list[EvidenceRef] = Field(default_factory=list)
    reason: str  # why this status
    temporal_note: str | None = None
    extracted_by: str  # "rule", "llm:<model>@<prompt_version>", "human"


class ConflictVersion(_Model):
    value: str
    evidence: list[EvidenceRef]


class Conflict(_Model):
    conflict_id: str
    event_id: str
    kind: ConflictKind
    field: str
    version_a: ConflictVersion
    version_b: ConflictVersion
    status: Literal["sin_resolver"] = "sin_resolver"
    verification_needed: str


class TemporalWarning(_Model):
    evidence_id: str
    period: str
    message: str  # "Dato histórico — 2024. No presentarlo como medición actual."


class ScoreComponents(_Model):
    """Each component normalized to [0, 1] with a documented rule."""

    R: float = Field(ge=0, le=1)
    I: float = Field(ge=0, le=1)
    U: float = Field(ge=0, le=1)
    N: float = Field(ge=0, le=1)
    E: float = Field(ge=0, le=1)
    rationale: dict[str, str] = Field(default_factory=dict)


class PriorityScore(_Model):
    score: float = Field(ge=0, le=100)  # P = 30R + 25I + 20U + 15N + 10E
    tier: PriorityTier
    components: ScoreComponents
    rules_version: str


class InvestigationGap(_Model):
    we_know: list[str]  # claim_ids with status SUSTENTADA
    it_is_claimed: list[str]  # claim_ids SOLO_REPORTADA / DECLARACION
    we_infer: list[str]  # explicit inference sentences (labelled)
    we_dont_know: list[str]
    investigate_next: list[str] = Field(min_length=3, max_length=3)


class Event(_Model):
    """A cluster of publications about the same real-world event."""

    event_id: str  # EVT-NNNN, stable for a given snapshot
    title: str  # representative headline (verbatim)
    topic: Topic
    topic_confidence: float | None
    member_ids: list[str]
    first_published: datetime | None
    last_published: datetime | None
    first_detected: datetime | None
    is_recirculated: bool = False  # old story detected again recently
    entities: list[str] = Field(default_factory=list)
    source_dna: SourceDNA
    official_evidence: list[EvidenceRef] = Field(default_factory=list)
    claims: list[Claim] = Field(default_factory=list)
    conflicts: list[Conflict] = Field(default_factory=list)
    temporal_warnings: list[TemporalWarning] = Field(default_factory=list)
    priority: PriorityScore
    evidence_status: EvidenceStatus
    evidence_status_reason: str
    recommended_action: str
    gap: InvestigationGap | None = None
    text_scope_note: str | None = None  # "Basado únicamente en titular/metadatos"
    synthetic: bool = False
    # e.g. ["posible_inyeccion:news:<id>"]: source text with instruction-like content, treated as data
    security_flags: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Generation (Story Studio, Q&A)
# ---------------------------------------------------------------------------


class GenerationMeta(_Model):
    mode: Literal["live", "cache", "template"]
    model: str | None  # e.g. "ollama:qwen3:8b-q4_K_M"; None for template
    prompt_version: str | None
    params: dict[str, float | int | str] = Field(default_factory=dict)
    latency_ms: int | None
    tokens_in: int | None
    tokens_out: int | None
    cost_usd: float = 0.0
    created_at: datetime


class ValidationIssue(_Model):
    code: str  # e.g. UNCITED_FACT, NUMBER_NOT_IN_EVIDENCE, WORD_LIMIT
    severity: Literal["error", "warning"]
    detail: str
    location: str | None = None


class ValidationReport(_Model):
    passed: bool
    issues: list[ValidationIssue] = Field(default_factory=list)


class TaggedSentence(_Model):
    text: str
    tag: ClaimType
    claim_ids: list[str] = Field(default_factory=list)


class StoryPackage(_Model):
    package_id: str
    event_id: str
    proposed_title: str
    public_interest_angle: str
    brief: list[TaggedSentence]  # <= 250 words total
    investigation_questions: list[str] = Field(min_length=3, max_length=3)
    script: list[TaggedSentence]  # 45-60 s (~110-160 Spanish words)
    social_copy: TaggedSentence  # <= 80 words
    pending_verifications: list[str]
    sources: list[EvidenceRef]
    scope_disclaimer: str | None  # "Basado únicamente en titular/metadatos"
    validation: ValidationReport
    generated_by: GenerationMeta


class SectorBulletin(_Model):
    """Additive DL-035 extension: sector context, never individual financial decisions."""

    bulletin_id: str
    sector: str
    question: str
    horizon: str
    summary: list[TaggedSentence]  # <= 250 words, checked by the bulletin validator
    observations: list[TaggedSentence]
    impact_hypotheses: list[TaggedSentence]
    related_sectors: list[str]
    analyst_questions: list[str] = Field(min_length=3, max_length=3)
    event_ids: list[str]
    sources: list[EvidenceRef]
    scope_disclaimer: str | None
    limits_notice: str
    validation: ValidationReport
    generated_by: GenerationMeta


class QAAnswer(_Model):
    question: str
    abstained: bool
    answer: list[TaggedSentence] = Field(default_factory=list)
    abstention_reason: str | None = None
    needed_information: list[str] = Field(default_factory=list)
    citations: list[EvidenceRef] = Field(default_factory=list)
    validation: ValidationReport
    generated_by: GenerationMeta


# ---------------------------------------------------------------------------
# Human review
# ---------------------------------------------------------------------------


class ReviewRecord(_Model):
    review_id: str
    event_id: str
    package_id: str | None
    from_state: ReviewState
    to_state: ReviewState
    reviewer: str
    justification: str
    decided_at: datetime
    evidence_snapshot_sha256: str  # hash of the Event JSON at decision time


# ---------------------------------------------------------------------------
# Official export contract: fichas.jsonl (Spanish field names, spec section 7)
# ---------------------------------------------------------------------------


class Ficha(_Model):
    id_caso: str
    modalidad: Literal["tvn"] = "tvn"
    ids_fuente: list[str]
    afirmaciones: list[Claim]
    citas: list[EvidenceRef]
    puntaje: float
    componentes: ScoreComponents
    estado_evidencia: EvidenceStatus
    borrador: StoryPackage | None
    estado_revision: ReviewState


class UIBundle(_Model):
    """Everything the UI reads for one snapshot (data/processed/bundle.json)."""

    contract_version: str = CONTRACT_VERSION
    snapshot_version: str
    snapshot_cutoff_utc: datetime
    signals_total: int
    signals_valid: int
    events: list[Event]
    packages: list[StoryPackage] = Field(default_factory=list)
    # Source records (titles + metadata only; descriptions stripped in public builds). Used by the
    # Event Room (constituent publications) and by Q&A retrieval.
    news: list[NewsItem] = Field(default_factory=list)
    indicators: list[IndicatorObservation] = Field(default_factory=list)
    seismic: list[SeismicEvent] = Field(default_factory=list)
    reviews: list[ReviewRecord] = Field(default_factory=list)
