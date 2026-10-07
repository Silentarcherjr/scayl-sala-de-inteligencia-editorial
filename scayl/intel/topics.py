"""Topic classification. ``baseline`` = transparent keyword rules (official taxonomy, PDF stage 2).

The AI method (prototype similarity with embeddings) is Worker B's B-05; it plugs in through
``classify(items, method="ai")`` and must be compared against this baseline with macro-F1.
"""

from __future__ import annotations

import re

from scayl.contracts import NewsItem, Topic
from scayl.intel.embed import normalize

KEYWORDS: dict[Topic, list[str]] = {
    Topic.LOGISTICA_CANAL: ["canal", "esclusa", "calado", "transito", "buque", "naviera", "puerto", "portuario",
                            "contenedor", "logistic", "gatun", "balboa", "acp", "maritim", "shipping", "carga"],
    Topic.EVENTOS_NATURALES: ["sismo", "temblor", "terremoto", "lluvia", "inundacion", "tormenta", "sequia",
                              "el nino", "huracan", "deslizamiento", "earthquake", "flood", "drought", "sinaproc",
                              "clima", "incendio forestal", "oleaje"],
    Topic.ECONOMIA: ["economia", "economic", "inflacion", "pib", "precio", "empleo", "desempleo", "inversion",
                     "deuda", "fiscal", "mef", "exportacion", "importacion", "impuesto", "crecimiento", "banco",
                     "salario", "mercado", "comercio", "presupuesto", "mineria"],
    Topic.TURISMO: ["turismo", "turista", "touris", "hotel", "visitante", "vuelo", "aeropuerto", "copa airlines",
                    "crucero", "festival", "atp"],
    Topic.SERVICIOS_PUBLICOS: ["agua potable", "idaan", "electricidad", "energia", "apagon", "salud", "hospital",
                               "caja de seguro social", "css", "educacion", "escuela", "transporte", "metro de panama",
                               "basura", "recoleccion", "vacuna", "minsa", "meduca"],
    Topic.REGULACION: ["ley", "decreto", "asamblea", "regulacion", "normativa", "resolucion", "gaceta", "reforma",
                       "corte suprema", "tribunal", "proyecto de ley", "contraloria", "sancion"],
}
_PATTERNS = {t: [re.compile(rf"\b{re.escape(k)}") for k in kws] for t, kws in KEYWORDS.items()}


def classify_one(text: str) -> tuple[Topic, float | None]:
    norm = normalize(text)
    hits = {t: sum(bool(p.search(norm)) for p in pats) for t, pats in _PATTERNS.items()}
    best = max(hits.values())
    if best == 0:
        return Topic.OTRO, None
    winners = [t for t, h in hits.items() if h == best]
    topic = min(winners, key=lambda t: list(KEYWORDS).index(t))
    conf = min(1.0, 0.5 + 0.2 * (best - 1)) * (1.0 if len(winners) == 1 else 0.6)
    return topic, round(conf, 2)


def classify(items: list[NewsItem], method: str = "baseline") -> list[tuple[Topic, float | None]]:
    if method == "ai":
        try:
            from scayl.intel.topics_ai import classify as ai_classify  # B-05 (Worker B)
        except ImportError:
            method = "baseline"
        else:
            return ai_classify(items)
    return [classify_one(" ".join(filter(None, [i.titulo, i.descripcion]))) for i in items]
