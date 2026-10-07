"""Official taxonomy by multilingual prototype similarity; confidence is cosine, not truth."""
from __future__ import annotations

import numpy as np

from scayl.contracts import NewsItem, Topic

from .embed_st import SentenceTransformerEmbedder

PROTOTYPES: dict[Topic, str] = {
    Topic.LOGISTICA_CANAL: "Canal de Panamá, esclusas, tránsito de barcos, calado, puertos, transporte marítimo y logística.",
    Topic.ECONOMIA: "Economía: inflación, precios, empleo, crecimiento del PIB, inversión, comercio, deuda y presupuesto.",
    Topic.TURISMO: "Turismo: viajeros, hoteles, destinos turísticos, visitantes internacionales, vuelos y cruceros de vacaciones.",
    Topic.SERVICIOS_PUBLICOS: "Servicios públicos: suministro de agua potable, electricidad, salud, hospitales, escuelas y transporte público.",
    Topic.EVENTOS_NATURALES: "Eventos naturales: terremotos, sismos, inundaciones, lluvias, sequías, huracanes y riesgos climáticos.",
    Topic.REGULACION: "Regulación: leyes, decretos, asamblea legislativa, normas, tribunales, auditorías y reformas legales.",
    Topic.OTRO: "Otras noticias: deportes, fútbol, celebridades, entretenimiento, arte y temas fuera de la taxonomía editorial.",
}


def classify(items: list[NewsItem]) -> list[tuple[Topic, float]]:
    if not items:
        return []
    embedder = SentenceTransformerEmbedder()
    labels = list(PROTOTYPES)
    texts = [" ".join(filter(None, (item.titulo, item.descripcion))) for item in items]
    vectors = embedder.encode([*texts, *PROTOTYPES.values()])
    scores = vectors[:len(items)] @ vectors[len(items):].T
    winners = np.argmax(scores, axis=1)
    return [(labels[int(index)], float(np.clip(scores[row, index], 0, 1)))
            for row, index in enumerate(winners)]
