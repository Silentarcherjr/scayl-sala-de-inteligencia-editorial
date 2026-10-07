"""Event clustering (ARCHITECTURE §4.2): average-linkage agglomerative over cosine similarity,
with a hard time constraint (publications more than 7 days apart never merge).

``tau`` is a similarity threshold: higher = stricter (precision over recall, by design).
Defaults per embedder are provisional until B-05/B-07 calibrate them on the development set (DL-018).
"""

from __future__ import annotations

from datetime import timedelta

import numpy as np

from scayl.contracts import NewsItem
from scayl.intel.embed import Embedder

DEFAULT_TAU = {"tfidf-char-3-5": 0.55}
MAX_GAP = timedelta(days=7)


def _when(item: NewsItem):
    return item.fecha_publicacion or item.fecha_deteccion or item.fecha_extraccion


def similarity(items: list[NewsItem], embedder: Embedder) -> np.ndarray:
    vectors = embedder.encode([" ".join(filter(None, [i.titulo, i.descripcion])) for i in items])
    return np.clip(vectors @ vectors.T, -1.0, 1.0)


def cluster(items: list[NewsItem], embedder: Embedder, tau: float | None = None) -> list[list[str]]:
    if not items:
        return []
    if len(items) == 1:
        return [[items[0].id_noticia]]
    from sklearn.cluster import AgglomerativeClustering

    tau = DEFAULT_TAU.get(embedder.name, 0.78) if tau is None else tau
    sim = similarity(items, embedder)
    dist = 1.0 - sim
    times = [_when(i) for i in items]
    for a in range(len(items)):
        for b in range(a + 1, len(items)):
            if abs(times[a] - times[b]) > MAX_GAP:
                dist[a, b] = dist[b, a] = 1.0
    np.fill_diagonal(dist, 0.0)
    labels = AgglomerativeClustering(n_clusters=None, metric="precomputed", linkage="average",
                                     distance_threshold=1.0 - tau).fit_predict(dist)
    groups: dict[int, list[str]] = {}
    for item, label in zip(items, labels):
        groups.setdefault(int(label), []).append(item.id_noticia)
    return sorted((sorted(g) for g in groups.values()), key=lambda g: g[0])
