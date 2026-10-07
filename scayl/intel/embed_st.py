"""Local multilingual sentence embeddings; optional weights and ML imports are lazy."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import numpy as np

DEFAULT_MODEL = "intfloat/multilingual-e5-base"


class SentenceTransformerEmbedder:
    """E5 uses query prefixes for symmetric similarity, including non-English text.

    See https://huggingface.co/intfloat/multilingual-e5-base . No network downloads
    occur here: use a local model directory or an already cached model.
    """

    def __init__(self, model: str | None = None, *, device: str | None = None,
                 batch_size: int = 16) -> None:
        self.model_id = model or os.environ.get("SCAYL_EMBED_MODEL", DEFAULT_MODEL)
        local = Path(__file__).parents[2] / "models/embeddings" / self.model_id.replace("/", "--")
        self.model_path = str(local) if local.is_dir() else self.model_id
        # Preserve a stable calibrated name when the canonical model is a local directory.
        canonical = DEFAULT_MODEL if Path(self.model_id).name == "intfloat--multilingual-e5-base" else self.model_id
        self.name = "st:" + canonical
        self.device = device or os.environ.get("SCAYL_EMBED_DEVICE", "cpu")
        if batch_size < 1:
            raise ValueError("batch_size must be positive")
        self.batch_size = batch_size
        self._model: Any = None

    def _load(self) -> Any:
        if self._model is None:
            # Initialize clustering's native dependencies before PyTorch on Windows.
            # Loading them afterward failed under this machine's DLL policy.
            import sklearn.cluster  # noqa: F401
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self.model_path, device=self.device,
                                               local_files_only=True, trust_remote_code=False)
            self._model.max_seq_length = min(512, self._model.max_seq_length)
        return self._model

    def encode(self, texts: list[str]) -> np.ndarray:
        if not texts:
            return np.zeros((0, 0), dtype=np.float32)
        prefix = "query: " if "e5" in self.model_id.lower() else ""
        result = np.asarray(self._load().encode(
            [prefix + text for text in texts], batch_size=self.batch_size,
            convert_to_numpy=True, normalize_embeddings=True, show_progress_bar=False,
        ), dtype=np.float32)
        if result.ndim != 2 or result.shape[0] != len(texts) or not np.isfinite(result).all():
            raise ValueError("Invalid sentence embedding matrix")
        norms = np.linalg.norm(result, axis=1, keepdims=True)
        if np.any(norms == 0):
            raise ValueError("Zero sentence embedding")
        return np.asarray(result / norms, dtype=np.float32)
