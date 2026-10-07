"""Hosting-only adapter: the public UI cannot enable live generation."""
from scayl import service
from scayl.gen.llm import LLM


class CacheOnlyLLM(LLM):
    def __init__(self, mode=None, **kwargs):
        super().__init__(mode="cache", **kwargs)


def enforce_cache() -> None:
    service.LLM = CacheOnlyLLM
