"""Evidence status (independent from the priority score) and recommended editorial action."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import yaml

from scayl.contracts import (
    Claim,
    ClaimStatus,
    Conflict,
    EvidenceRef,
    EvidenceStatus,
    PriorityTier,
    SourceDNA,
    Topic,
)

VERIFICATION_SOURCES = Path(__file__).resolve().parents[1] / "config" / "verification_sources.v1.yaml"
NOT_AUTHORIZED = "La prioridad alta NO habilita publicación."


@lru_cache(maxsize=2)
def verification_sources(path: Path = VERIFICATION_SOURCES) -> dict[str, list[str]]:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))["topics"]


def evidence_status(
    claims: list[Claim],
    conflicts: list[Conflict],
    official_evidence: list[EvidenceRef],
    source_dna: SourceDNA,
    central_claim_id: str | None = None,
) -> tuple[EvidenceStatus, str]:
    """Rules from ARCHITECTURE §4.7. ``central_claim_id`` defaults to the first claim."""
    central = next((c for c in claims if c.claim_id == central_claim_id), claims[0] if claims else None)
    unresolved = [c for c in conflicts if c.status == "sin_resolver"]

    if central and central.status == ClaimStatus.SUSTENTADA and any(central.evidence) and not unresolved:
        return EvidenceStatus.SUFICIENTE_PARA_BORRADOR, (
            "La afirmación central está respaldada por evidencia identificada y no hay conflictos sin resolver."
        )
    if unresolved:
        return EvidenceStatus.PARCIAL, f"Hay {len(unresolved)} conflicto(s) sin resolver entre versiones."
    if official_evidence:
        return EvidenceStatus.PARCIAL, (
            "Existe evidencia oficial de contexto, pero no respalda directamente la afirmación central."
        )
    if source_dna.max_possible_independent >= 2:
        return EvidenceStatus.PARCIAL, (
            f"Hasta {source_dna.max_possible_independent} procedencias posiblemente independientes, "
            "sin evidencia oficial."
        )
    return EvidenceStatus.INSUFICIENTE, "Fuente única o de procedencia común, sin evidencia oficial."


_ACTIONS = {
    (PriorityTier.ALTO, EvidenceStatus.SUFICIENTE_PARA_BORRADOR): "Preparar borrador para revisión.",
    (PriorityTier.ALTO, EvidenceStatus.PARCIAL): "Investigar los vacíos antes de producir.",
    (PriorityTier.ALTO, EvidenceStatus.INSUFICIENTE): "Investigar antes de producir.",
    (PriorityTier.MEDIO, EvidenceStatus.SUFICIENTE_PARA_BORRADOR): "Borrador opcional; evaluar en la reunión editorial.",
    (PriorityTier.MEDIO, EvidenceStatus.PARCIAL): "Seguimiento: reunir evidencia adicional.",
    (PriorityTier.MEDIO, EvidenceStatus.INSUFICIENTE): "Monitorear; no producir aún.",
    (PriorityTier.BAJO, EvidenceStatus.SUFICIENTE_PARA_BORRADOR): "Archivar como contexto disponible.",
    (PriorityTier.BAJO, EvidenceStatus.PARCIAL): "Monitorear.",
    (PriorityTier.BAJO, EvidenceStatus.INSUFICIENTE): "Sin acción.",
}


def recommended_action(tier: PriorityTier, status: EvidenceStatus, topic: Topic) -> str:
    action = _ACTIONS[(tier, status)]
    if status != EvidenceStatus.SUFICIENTE_PARA_BORRADOR and tier != PriorityTier.BAJO:
        sources = verification_sources().get(topic.value) or []
        if sources:
            action += f" Fuente sugerida para verificar: {sources[0]}."
    if tier == PriorityTier.ALTO:
        action += f" {NOT_AUTHORIZED}"
    return action
