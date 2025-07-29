from ....entities import ReasoningToken
from typing import Any, Iterable


class ReasoningParser:
    def __init__(
        self,
        *,
        start_tag: str = "<think>",
        end_tag: str = "</think>",
        prefixes: list[str] | None = None,
    ) -> None:
        self._start_tag = start_tag
        self._end_tag = end_tag
        self._prefixes = prefixes or ["Think:"]
        self._thinking = False

    def set_thinking(self, thinking: bool) -> None:
        self._thinking = thinking

    @property
    def is_thinking(self) -> bool:
        return self._thinking

    async def push(self, token_str: str) -> Iterable[Any]:
        token_clean = token_str.strip()
        if token_clean == self._start_tag:
            self._thinking = True
            return [ReasoningToken(token_str)]
        if token_clean == self._end_tag:
            self._thinking = False
            return [ReasoningToken(token_str)]
        if any(token_clean.startswith(p) for p in self._prefixes):
            self._thinking = True
            return [ReasoningToken(token_str)]
        if self._thinking:
            return [ReasoningToken(token_str)]
        return [token_str]

    async def flush(self) -> Iterable[Any]:
        return []
