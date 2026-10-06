"""Local LLM access (Ollama REST) with a content-addressed cache and generation metadata (L-08).

Modes:
  live     -> call Ollama, store the result in the cache
  cache    -> read only from the cache (hosted demo / no GPU); a miss raises CacheMiss
  template -> no LLM at all (callers use deterministic builders)

No new dependency: plain HTTP via ``requests``. Structured output is enforced with Ollama's
``format=<JSON schema>``; temperature 0 and a fixed seed for reproducibility; thinking disabled.

    python -m scayl.gen.llm ping      # warm-up + latency check on the demo machine
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal, Protocol

from scayl.contracts import GenerationMeta

Mode = Literal["live", "cache", "template"]
ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CACHE = ROOT / "data" / "cache" / "llm"
PROMPTS_DIR = Path(__file__).resolve().parent / "prompts"
DEFAULT_OPTIONS = {"temperature": 0, "seed": 42, "num_ctx": 4096}


class LLMError(RuntimeError):
    pass


class CacheMiss(LLMError):
    pass


class LLMUnavailable(LLMError):
    pass


def load_prompt(name: str, version: str = "v1") -> str:
    return (PROMPTS_DIR / f"{name}.{version}.md").read_text(encoding="utf-8")


@dataclass
class RawResult:
    data: dict
    tokens_in: int | None
    tokens_out: int | None
    latency_ms: int


class ChatBackend(Protocol):
    model: str

    def chat_json(self, system: str, user: str, schema: dict) -> RawResult: ...


class OllamaBackend:
    def __init__(self, model: str | None = None, host: str | None = None, timeout: float = 300.0,
                 options: dict | None = None):
        self.model = model or os.environ.get("SCAYL_LLM_MODEL", "qwen3:8b")
        self.host = (host or os.environ.get("OLLAMA_HOST", "http://localhost:11434")).rstrip("/")
        self.timeout = timeout
        self.options = {**DEFAULT_OPTIONS, **(options or {})}

    def chat_json(self, system: str, user: str, schema: dict) -> RawResult:
        import requests

        body = {
            "model": self.model, "stream": False, "think": False, "format": schema, "options": self.options,
            "keep_alive": "30m",
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
        }
        start = time.perf_counter()
        try:
            resp = requests.post(f"{self.host}/api/chat", json=body, timeout=self.timeout)
        except requests.RequestException as exc:
            raise LLMUnavailable(f"Ollama no disponible en {self.host}: {exc}") from exc
        latency = int((time.perf_counter() - start) * 1000)
        if resp.status_code != 200:
            raise LLMError(f"Ollama respondió {resp.status_code}: {resp.text[:300]}")
        payload = resp.json()
        content = payload.get("message", {}).get("content", "")
        try:
            data = json.loads(content)
        except json.JSONDecodeError as exc:
            raise LLMError(f"Salida no es JSON válido: {content[:200]}") from exc
        return RawResult(data=data, tokens_in=payload.get("prompt_eval_count"),
                         tokens_out=payload.get("eval_count"), latency_ms=latency)


def cache_key(prompt_version: str, model: str, system: str, user: str, schema: dict) -> str:
    blob = json.dumps([prompt_version, model, system, user, schema], sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


class LLM:
    """Mode-aware, cached JSON generation. Every result carries GenerationMeta."""

    def __init__(self, mode: Mode | None = None, backend: ChatBackend | None = None,
                 cache_dir: Path | None = None, model: str | None = None):
        self.mode: Mode = mode or os.environ.get("SCAYL_LLM_MODE", "cache")  # type: ignore[assignment]
        self.backend = backend
        self.model = model or (backend.model if backend else os.environ.get("SCAYL_LLM_MODEL", "qwen3:8b"))
        self.cache_dir = Path(cache_dir or os.environ.get("SCAYL_LLM_CACHE", DEFAULT_CACHE))

    def _backend(self) -> ChatBackend:
        if self.backend is None:
            self.backend = OllamaBackend(model=self.model)
        return self.backend

    def generate(self, prompt_version: str, system: str, user: str, schema: dict) -> tuple[dict, GenerationMeta]:
        if self.mode == "template":
            raise LLMUnavailable("Modo plantilla: sin LLM")
        key = cache_key(prompt_version, self.model, system, user, schema)
        path = self.cache_dir / f"{key}.json"
        if path.exists():
            stored = json.loads(path.read_text(encoding="utf-8"))
            meta = GenerationMeta.model_validate({**stored["meta"], "mode": "cache"})
            return stored["data"], meta
        if self.mode == "cache":
            raise CacheMiss(f"Sin salida precalculada para {prompt_version} (clave {key[:12]})")

        raw = self._backend().chat_json(system, user, schema)
        meta = GenerationMeta(mode="live", model=f"ollama:{self.model}", prompt_version=prompt_version,
                              params={k: v for k, v in DEFAULT_OPTIONS.items()}, latency_ms=raw.latency_ms,
                              tokens_in=raw.tokens_in, tokens_out=raw.tokens_out, cost_usd=0.0,
                              created_at=datetime.now(UTC))
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"data": raw.data, "meta": meta.model_dump(mode="json")}, ensure_ascii=False,
                                   indent=1), encoding="utf-8")
        return raw.data, meta


def _ping() -> None:
    llm = LLM(mode="live", cache_dir=Path(os.environ.get("TMPDIR", "/tmp")) / "scayl-ping")
    schema = {"type": "object", "properties": {"ok": {"type": "boolean"}}, "required": ["ok"]}
    for i in range(2):  # first call loads the model (cold), second is warm
        start = time.perf_counter()
        raw = llm._backend().chat_json("Responde solo JSON.", 'Devuelve {"ok": true}', schema)
        print(f"call {i + 1}: {int((time.perf_counter() - start) * 1000)} ms, data={raw.data}, "
              f"tokens_out={raw.tokens_out}, model={llm.model}")


if __name__ == "__main__":
    if sys.argv[1:] == ["ping"]:
        _ping()
    else:
        print("usage: python -m scayl.gen.llm ping")
