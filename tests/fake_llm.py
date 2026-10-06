"""Deterministic stand-in for Ollama: returns canned JSON per prompt version and records prompts."""
from scayl.gen.llm import LLM, RawResult


class FakeBackend:
    model = "fake-model"

    def __init__(self, responses: dict):
        self.responses = responses  # prompt_version prefix ("studio"|"claims"|"qa") -> dict | Exception
        self.calls: list[tuple[str, str]] = []

    def chat_json(self, system, user, schema):
        self.calls.append((system, user))
        key = "studio" if "paquete editorial" in user else "claims" if "Extrae" in user else "qa"
        value = self.responses[key]
        if isinstance(value, Exception):
            raise value
        return RawResult(data=value, tokens_in=100, tokens_out=50, latency_ms=12)


def fake_llm(tmp_path, responses: dict) -> tuple[LLM, FakeBackend]:
    backend = FakeBackend(responses)
    return LLM(mode="live", backend=backend, cache_dir=tmp_path / "llm-cache"), backend
