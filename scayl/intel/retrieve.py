"""Opt-in B-06 retrieval experiment. Does not replace the guarded QA retriever."""
from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass

import numpy as np

from scayl.contracts import EvidenceKind, EvidenceRef, UIBundle
from scayl.evidence.linking import news_ref
from scayl.evidence.recent import ref_for
from scayl.gen.guard import scan
from scayl.intel.embed import Embedder, get_embedder, normalize


@dataclass(frozen=True)
class EvidenceUnit:
    text: str
    ref: EvidenceRef


def units_from_bundle(bundle: UIBundle) -> list[EvidenceUnit]:
    """Titles and typed numeric fields only. Keep periods, units and source IDs."""
    units = [EvidenceUnit(item.titulo, news_ref(item)) for item in bundle.news
             if not scan(item.titulo) and not scan(item.descripcion)]
    for row in bundle.indicators:
        if row.valor is None:
            continue  # Missing evidence is not numeric zero.
        period = row.periodo or str(row.anio)
        if row.fuente == "wb":
            ref = EvidenceRef(evidence_id=f"wb:{row.pais_iso3}:{row.indicador_id}:{row.anio}",
                              kind=EvidenceKind.INDICATOR, field="valor", value=row.valor,
                              period=period, excerpt=f"{row.valor} {row.unidad or ''}", url=row.fuente_url)
        else:
            ref = ref_for(row)
        text = f"{row.pais_iso3} {row.indicador_nombre or row.indicador_id} {period}: {row.valor} {row.unidad or ''}"
        if row.es_proyeccion:
            text += " (proyección, no observación)"
        units.append(EvidenceUnit(text, ref))
    for row in bundle.seismic:
        if row.magnitude is None:
            continue
        period = row.time.isoformat() if row.time else None
        ref = EvidenceRef(evidence_id=f"usgs:{row.id}", kind=EvidenceKind.SEISMIC,
                          field="magnitude", value=row.magnitude, period=period,
                          excerpt=f"magnitud {row.magnitude} {row.mag_type or ''}", url=row.url)
        units.append(EvidenceUnit(f"Sismo {row.place or ''} {period or 'fecha desconocida'} magnitud {row.magnitude}", ref))
    return units


class Retriever:
    """Instance-bound index; hybrid=False avoids importing/loading model weights.

    BM25 uses positive Robertson IDF (k1=1.5, b=.75), mapped with s/(1+s).
    Opt-in hybrid averages this lexical score and cosine clipped to [0,1].
    Scores are similarity, not calibrated probabilities or QA abstention scores.
    """

    def __init__(self, units: list[EvidenceUnit], *, hybrid: bool = False,
                 embedder: Embedder | None = None) -> None:
        self.units = sorted(units, key=lambda unit: unit.ref.evidence_id)
        if len({u.ref.evidence_id for u in self.units}) != len(self.units):
            raise ValueError("Evidence IDs must be unique")
        self.hybrid = hybrid
        self.embedder = embedder
        self._vectors: np.ndarray | None = None
        self._counts = [Counter(normalize(u.text).split()) for u in self.units]
        self._lengths = [sum(c.values()) for c in self._counts]
        self._avg_length = sum(self._lengths) / len(self.units) if self.units else 0
        self._df = Counter(term for counts in self._counts for term in counts)

    @staticmethod
    def _normalize_vectors(values: np.ndarray, rows: int) -> np.ndarray:
        values = np.asarray(values, dtype=float)
        if values.ndim != 2 or values.shape[0] != rows or not np.isfinite(values).all():
            raise ValueError("Invalid embeddings")
        lengths = np.linalg.norm(values, axis=1, keepdims=True)
        if np.any(lengths == 0):
            raise ValueError("Zero embeddings")
        return values / lengths

    def search(self, query: str, k: int = 8) -> list[tuple[str, float, EvidenceRef]]:
        if k < 0:
            raise ValueError("k must be nonnegative")
        terms = set(normalize(query).split())
        if not terms or not self.units or k == 0 or scan(query):
            return []
        lexical = []
        for counts, length in zip(self._counts, self._lengths):
            score = 0.0
            for term in terms:
                tf = counts.get(term, 0)
                if not tf:
                    continue
                df = self._df[term]
                idf = math.log1p((len(self.units) - df + .5) / (df + .5))
                norm = 1.5 * (1 - .75 + .75 * length / self._avg_length)
                score += idf * tf * 2.5 / (tf + norm)
            lexical.append(score / (1 + score))
        scores = np.asarray(lexical)
        if self.hybrid:
            if self.embedder is None:
                self.embedder = get_embedder("st")
            if self._vectors is None:
                self._vectors = self._normalize_vectors(self.embedder.encode([u.text for u in self.units]), len(self.units))
            query_vector = self._normalize_vectors(self.embedder.encode([query]), 1)
            if query_vector.shape[1] != self._vectors.shape[1]:
                raise ValueError("Embedding dimensions changed")
            cosine = np.clip(self._vectors @ query_vector[0], 0, 1)
            scores = .5 * scores + .5 * cosine
        ranked = sorted(zip(self.units, scores), key=lambda pair: (-pair[1], pair[0].ref.evidence_id))
        return [(unit.ref.evidence_id, float(score), unit.ref) for unit, score in ranked[:k] if score > 0]
