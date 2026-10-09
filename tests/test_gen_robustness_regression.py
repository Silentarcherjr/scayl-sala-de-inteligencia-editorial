"""A5 robustness: every model failure ends in an explicit, visible safe fallback (never a crash).

Covers the real Ollama backend's parsing (invalid/truncated/empty JSON, HTTP error, timeout) with a
patched transport, plus malformed-but-parseable outputs through tests/fake_llm.py.
"""
import pytest
import requests

from scayl.gen import claims, studio
from scayl.gen.llm import LLM, OllamaBackend
from tests.fake_llm import fake_llm
from tests.test_t09_studio import good_response, seismic_event


class _Resp:
    def __init__(self, status=200, content="", payload=None):
        self.status_code, self.text = status, content
        self._payload = payload if payload is not None else {"message": {"content": content}}

    def json(self):
        return self._payload


def _ollama_llm(tmp_path, monkeypatch, outcome):
    def post(*_a, **_k):
        if isinstance(outcome, Exception):
            raise outcome
        return outcome
    monkeypatch.setattr(requests, "post", post)
    return LLM(mode="live", backend=OllamaBackend(model="m", host="http://127.0.0.1:9"), cache_dir=tmp_path)


@pytest.mark.parametrize("outcome", [
    _Resp(content='{"proposed_title": "Sismo", "brief": [{"text": "USGS'),  # truncated
    _Resp(content="no es json"),                                              # invalid JSON
    _Resp(content=""),                                                        # empty response
    _Resp(status=500, content="model not found"),                             # model unavailable
    requests.Timeout("read timed out"),                                       # timeout
    requests.ConnectionError("refused"),                                      # server down
], ids=["truncated", "invalid", "empty", "http500", "timeout", "down"])
def test_backend_failures_fall_back_to_template_visibly(tmp_path, monkeypatch, outcome):
    e, items = seismic_event()
    llm = _ollama_llm(tmp_path, monkeypatch, outcome)
    pkg, report = studio.generate_with_report(e, llm)
    assert pkg.generated_by.mode == "template" and pkg.validation.passed
    assert pkg.validation.issues[0].code == "LLM_FALLBACK" and report["fallback_reason"]
    assert claims.extract(e, items, llm) == []
    assert not list(tmp_path.glob("*.json"))  # failures are never cached as answers


@pytest.mark.parametrize("mutate", [
    lambda r: r | {"proposed_title": None},
    lambda r: r | {"investigation_questions": [1, 2]},
    lambda r: r | {"brief": "texto suelto"},
    lambda r: r | {"social_copy": None},
    lambda r: [r],
], ids=["null-title", "non-string-questions", "brief-not-list", "null-social", "top-level-list"])
def test_malformed_but_parseable_output_falls_back(tmp_path, mutate):
    e, _ = seismic_event()
    llm, _ = fake_llm(tmp_path, {"studio": mutate(good_response(e))})
    pkg = studio.generate(e, llm)
    assert pkg.generated_by.mode == "template" and pkg.validation.issues[0].code == "LLM_FALLBACK"


@pytest.mark.parametrize("data", [[], {"claims": "x"}, {"claims": ["texto", 3]},
                                  {"claims": [{"source_id": "a", "statement": "Sismo en Chiriquí",
                                               "type": "HECHO", "attributed_to": 7}]}])
def test_malformed_claim_extraction_never_raises(tmp_path, data):
    e, items = seismic_event()
    llm, _ = fake_llm(tmp_path, {"claims": data})
    out = claims.extract(e, items, llm)
    assert all(c.status.value == "SOLO_REPORTADA" for c in out)


def test_all_sentences_rejected_falls_back_with_reason(tmp_path):
    e, _ = seismic_event()
    bad = good_response(e)
    sid = bad["brief"][0]["claim_ids"]
    bad["brief"] = [{"text": "El sismo dejó 99 muertos.", "tag": "HECHO", "claim_ids": sid}]
    llm, _ = fake_llm(tmp_path, {"studio": bad})
    pkg, report = studio.generate_with_report(e, llm)
    assert pkg.generated_by.mode == "template"
    assert report["fallback_reason"] == "ninguna oración del brief sobrevivió a la validación"
    assert any(i.code == "NUMBER_NOT_IN_EVIDENCE" for i in pkg.validation.issues)
