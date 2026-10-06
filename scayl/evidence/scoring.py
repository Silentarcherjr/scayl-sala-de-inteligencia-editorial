"""Attention score P = 30R + 25I + 20U + 15N + 10E (rules: scayl/config/scoring_rules.v1.yaml).

Deterministic and reproducible. The LLM never participates. The score ranks what deserves
editorial attention; it is not a probability of truth and it never authorizes publication.
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from datetime import datetime
from functools import lru_cache
from pathlib import Path

import yaml

from scayl.contracts import Event, PriorityScore, PriorityTier, ScoreComponents, Topic

CONFIG_DIR = Path(__file__).resolve().parents[1] / "config"
DEFAULT_RULES = CONFIG_DIR / "scoring_rules.v1.yaml"
COMPONENTS = ("R", "I", "U", "N", "E")


@lru_cache(maxsize=8)
def load_rules(path: Path = DEFAULT_RULES) -> dict:
    rules = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if sum(rules["weights"].values()) != 100:
        raise ValueError("scoring weights must sum to 100")
    return rules


@dataclass(frozen=True)
class ScoringInput:
    """Everything the score needs about an event, computed upstream by the evidence engine."""

    mentions_panama: bool
    is_tvn: bool
    topic: Topic
    topic_confidence: float | None
    has_official_evidence: bool
    latest_original_publication: datetime | None
    cutoff: datetime
    max_prior_similarity: float | None  # None = no earlier event to compare with
    max_possible_independent: int
    confirmed_independent: int


def _clamp(x: float) -> float:
    return max(0.0, min(1.0, x))


def relevance(inp: ScoringInput, rules: dict) -> tuple[float, str]:
    cfg = rules["relevance"]
    panama = inp.mentions_panama or inp.is_tvn
    in_scope = inp.topic != Topic.OTRO
    conf = 0.5 if inp.topic_confidence is None else inp.topic_confidence
    value = cfg["panama_signal"] * panama + cfg["topic_in_scope"] * in_scope * conf
    why = ("Relacionado con Panamá" if panama else "Sin vínculo explícito con Panamá") + (
        f"; tema en alcance ({inp.topic.value}, confianza {conf:.2f})" if in_scope else "; tema fuera de alcance"
    )
    return _clamp(value), why


def impact(inp: ScoringInput, rules: dict) -> tuple[float, str]:
    cfg = rules["impact"]
    base = cfg["topic_base"][inp.topic.value]
    bonus = cfg["official_evidence_bonus"] if inp.has_official_evidence else 0.0
    why = f"Peso editorial del tema {inp.topic.value} = {base}"
    if bonus:
        why += f"; +{bonus} por evidencia oficial pertinente"
    return _clamp(base + bonus), why


def urgency(inp: ScoringInput, rules: dict) -> tuple[float, str]:
    if inp.latest_original_publication is None:
        return 0.0, "Sin fecha de publicación válida: urgencia no calculable (0)"
    hours = max(0.0, (inp.cutoff - inp.latest_original_publication).total_seconds() / 3600)
    value = math.exp(-hours / rules["urgency"]["half_life_hours"])
    return _clamp(value), f"Publicación original más reciente: hace {hours:.0f} h respecto al corte"


def novelty(inp: ScoringInput, rules: dict) -> tuple[float, str]:
    if inp.max_prior_similarity is None:
        return 1.0, "Sin eventos previos similares en la ventana"
    sim = _clamp(inp.max_prior_similarity)
    return 1.0 - sim, f"Similitud máxima con eventos previos = {sim:.2f}; los duplicados no suman"


def evidence(inp: ScoringInput, rules: dict) -> tuple[float, str]:
    cfg = rules["evidence"]
    groups = min(max(inp.max_possible_independent, 0), 3)
    value = (
        cfg["official"] * inp.has_official_evidence
        + cfg["independent_groups"] * groups / 3
        + cfg["confirmed_independent"] * (inp.confirmed_independent >= 1)
    )
    why = (
        f"{'1+' if inp.has_official_evidence else '0'} evidencia oficial; "
        f"hasta {inp.max_possible_independent} procedencias posibles; "
        f"{inp.confirmed_independent} independientes confirmadas"
    )
    return _clamp(value), why


def tier_for(score: float, rules: dict) -> PriorityTier:
    if score >= rules["tiers"]["alto"]:
        return PriorityTier.ALTO
    if score >= rules["tiers"]["medio"]:
        return PriorityTier.MEDIO
    return PriorityTier.BAJO


def combine(components: ScoreComponents, weights: dict[str, int], rules: dict, version: str) -> PriorityScore:
    p = round(sum(weights[k] * getattr(components, k) for k in COMPONENTS), 1)
    return PriorityScore(score=p, tier=tier_for(p, rules), components=components, rules_version=version)


def score(inp: ScoringInput, rules: dict | None = None) -> PriorityScore:
    rules = rules or load_rules()
    values, why = {}, {}
    for key, fn in zip(COMPONENTS, (relevance, impact, urgency, novelty, evidence)):
        values[key], why[key] = fn(inp, rules)
        values[key] = round(values[key], 4)
    return combine(ScoreComponents(**values, rationale=why), rules["weights"], rules, rules["version"])


def rank(events: list[Event]) -> list[Event]:
    """Official order: P desc, then U desc, then event_id asc."""
    return sorted(events, key=lambda e: (-e.priority.score, -e.priority.components.U, e.event_id))


def custom_version(weights: dict[str, int], rules: dict) -> str:
    digest = hashlib.sha256(json.dumps(weights, sort_keys=True).encode()).hexdigest()[:8]
    return f"{rules['version']}+custom:{digest}"


def rescore(events: list[Event], weights: dict[str, int], rules: dict | None = None) -> list[Event]:
    """Weight simulator (L-15): re-rank with alternative weights. Official weights reproduce v1 exactly."""
    rules = rules or load_rules()
    if set(weights) != set(COMPONENTS) or sum(weights.values()) != 100 or min(weights.values()) < 0:
        raise ValueError("weights must be non-negative, cover R/I/U/N/E and sum to 100")
    version = rules["version"] if weights == rules["weights"] else custom_version(weights, rules)
    rescored = [
        e.model_copy(update={"priority": combine(e.priority.components, weights, rules, version)}) for e in events
    ]
    return rank(rescored)
