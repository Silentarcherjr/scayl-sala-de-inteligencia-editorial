"""Read only public bundle and cache; never accept live mode or caller paths."""
from __future__ import annotations

import json
import sys
from functools import lru_cache
from pathlib import Path

WEB = Path(__file__).resolve().parents[1]
RUNTIME = WEB / ".python-runtime"
sys.path.insert(0, str(RUNTIME))

from scayl import service
from scayl.contracts import UIBundle
from scayl.gen.llm import LLM


class CacheOnlyLLM(LLM):
    def __init__(self, mode=None, **kwargs):
        # Equivalent to deploy.runtime.enforce_cache, with an immutable public path.
        kwargs.pop("cache_dir", None)
        kwargs.pop("backend", None)
        kwargs.pop("model", None)
        super().__init__(mode="cache", cache_dir=RUNTIME / "llm", model="qwen3:8b", **kwargs)


@lru_cache(maxsize=1)
def public_bundle() -> UIBundle:
    path = RUNTIME / "data/processed/v1/bundle.json"
    return UIBundle.model_validate(json.loads(path.read_text(encoding="utf-8")))


def enforce_cache() -> None:
    service.LLM = CacheOnlyLLM
    service.load_bundle = public_bundle
