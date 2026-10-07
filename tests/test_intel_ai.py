"""Protocol and taxonomy tests without loading model weights."""
import numpy as np
import pytest
from datetime import datetime, timedelta, timezone

from scayl.contracts import Topic
from scayl.intel.embed_st import SentenceTransformerEmbedder
from scayl.intel import topics_ai
from tests.factories import news


def test_embedder_preserves_multilingual_text_and_normalizes_float32():
    class FakeModel:
        def encode(self, texts, **kwargs):
            assert texts == ["query: Canal de Panamá", "query: Sécheresse au canal"]
            assert kwargs["normalize_embeddings"] is True
            return [[3, 4], [0, 2]]
    embedder = SentenceTransformerEmbedder()
    embedder._model = FakeModel()
    result = embedder.encode(["Canal de Panamá", "Sécheresse au canal"])
    assert result.dtype == np.float32
    np.testing.assert_allclose(np.linalg.norm(result, axis=1), 1)
    assert embedder.name == "st:intfloat/multilingual-e5-base"


def test_empty_embedding_batch_does_not_load_optional_library():
    embedder = SentenceTransformerEmbedder()
    assert embedder.encode([]).shape == (0, 0)
    assert embedder._model is None


@pytest.mark.parametrize("vectors", [[[float("nan"), 0]], [[0, 0]], [1, 2]])
def test_invalid_embedding_output_is_rejected(vectors):
    class FakeModel:
        def encode(self, *args, **kwargs):
            return vectors
    embedder = SentenceTransformerEmbedder()
    embedder._model = FakeModel()
    with pytest.raises(ValueError):
        embedder.encode(["[SINTÉTICO] Titular"])


def test_prototype_classifier_preserves_order_and_official_taxonomy(monkeypatch):
    class FakeEmbedder:
        def encode(self, texts):
            assert texts[0] == "[SINTÉTICO] Canal"
            assert texts[1] == "[SINTÉTICO] Terremoto"
            prototypes = np.eye(len(topics_ai.PROTOTYPES), dtype=np.float32)
            return np.vstack([prototypes[0], prototypes[4], prototypes])
    monkeypatch.setattr(topics_ai, "SentenceTransformerEmbedder", FakeEmbedder)
    labels = topics_ai.classify([news("a", "[SINTÉTICO] Canal"), news("b", "[SINTÉTICO] Terremoto")])
    assert labels == [(Topic.LOGISTICA_CANAL, 1.0), (Topic.EVENTOS_NATURALES, 1.0)]
    assert topics_ai.classify([]) == []


def test_ai_similarity_cannot_override_seven_day_guard():
    from scayl.intel.cluster import cluster
    class IdenticalEmbedder:
        name = "st:intfloat/multilingual-e5-base"

        def encode(self, texts):
            return np.ones((len(texts), 1), dtype=np.float32)
    date = datetime(2025, 9, 1, tzinfo=timezone.utc)
    items = [news("a", "[SINTÉTICO] Canal", pub=date),
             news("b", "[SINTÉTICO] Canal", pub=date + timedelta(days=10))]
    assert cluster(items, IdenticalEmbedder()) == [["a"], ["b"]]


def test_calibration_rejects_c01_before_loading_model(tmp_path):
    from scayl.eval.calibrate_cluster import calibrate
    item = news("a", "[SINTÉTICO] Titular", pub=datetime(2026, 9, 1, tzinfo=timezone.utc))
    news_path = tmp_path / "news.jsonl"
    news_path.write_text(item.model_dump_json() + "\n", encoding="utf-8")
    pairs = tmp_path / "pairs.csv"
    pairs.write_text("id_a,id_b,same_event,labeler\na,a,1,test\n", encoding="utf-8")
    with pytest.raises(ValueError, match="2025 development"):
        calibrate(news_path, pairs, tmp_path / "result.json")
    assert not (tmp_path / "result.json").exists()
