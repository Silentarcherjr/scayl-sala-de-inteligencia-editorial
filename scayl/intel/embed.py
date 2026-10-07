"""Embedders behind one interface (ARCHITECTURE §5.1). ``tfidf`` = baseline, no ML weights needed.

The ``st`` (sentence-transformers) embedder is Worker B's AI variant (B-05); until it exists,
get_embedder("st") raises ImportError and the pipeline falls back to the labelled baseline.
"""

from __future__ import annotations

import re
import unicodedata
from typing import Literal, Protocol

import numpy as np


class Embedder(Protocol):
    name: str

    def encode(self, texts: list[str]) -> np.ndarray: ...  # L2-normalized rows


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().lower()
    return " ".join(re.sub(r"[^a-z0-9 ]+", " ", text).split())


class TfidfEmbedder:
    """Character n-gram TF-IDF fitted on the batch (robust to inflections and short headlines)."""

    name = "tfidf-char-3-5"

    def encode(self, texts: list[str]) -> np.ndarray:
        from sklearn.feature_extraction.text import TfidfVectorizer

        if not texts:
            return np.zeros((0, 0), dtype=np.float32)
        vec = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), min_df=1, sublinear_tf=True)
        matrix = vec.fit_transform([normalize(t) for t in texts]).astype(np.float32)
        return matrix.toarray()  # rows already L2-normalized by TfidfVectorizer


def get_embedder(kind: Literal["tfidf", "st"] = "tfidf", model: str | None = None) -> Embedder:
    if kind == "tfidf":
        return TfidfEmbedder()
    try:
        from scayl.intel.embed_st import SentenceTransformerEmbedder  # B-05 (Worker B)
    except ImportError as exc:
        raise ImportError("Embedder 'st' (B-05) no disponible todavía") from exc
    return SentenceTransformerEmbedder(model)
