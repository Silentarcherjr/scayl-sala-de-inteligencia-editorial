import json

import pytest

from scayl.contracts import GenerationMeta
from scayl.gen.llm import cache_key
from scayl.ingest import export_public_cache as exporter
from tests.factories import CUTOFF, news


def test_source_description_rejected_before_cache_read(monkeypatch, tmp_path):
    item = news("private", "[SINTÉTICO] Titular", descripcion="Descripción que no debe publicarse")
    monkeypatch.setattr(exporter, "_load_worker_b", lambda _: ([item], [], [], None, None, 1))
    with pytest.raises(ValueError, match="BEFORE"):
        exporter.export(tmp_path, tmp_path, tmp_path / "public")
    assert not (tmp_path / "public").exists()


def test_description_in_cached_output_is_rejected(tmp_path):
    key = cache_key("claims-v1", "qwen3:8b", "system", "user", {})
    meta = GenerationMeta(mode="live", model="ollama:qwen3:8b", prompt_version="claims-v1",
                          created_at=CUTOFF, latency_ms=None, tokens_in=None, tokens_out=None)
    (tmp_path / f"{key}.json").write_text(json.dumps({"data": {"descripcion": "private"},
        "meta": meta.model_dump(mode="json")}), encoding="utf-8")
    with pytest.raises(ValueError, match="descripción"):
        exporter.ReviewedCache(tmp_path).generate("claims-v1", "system", "user", {})
