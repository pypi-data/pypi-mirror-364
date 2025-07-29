from typing import Any, Optional, Union, List
from agentmemory.connection.connection import AgentMemoryConnection


class Cache:
    def __init__(self, con: AgentMemoryConnection):
        self._con = con

    def get(self, key: str) -> Optional[Any]:
        shortterm = self._con.shortterm
        if shortterm is None:
            return None
        return shortterm.get(key)

    def set(
        self, key: str, value: dict, ex: int = 60
    ) -> None:
        shortterm = self._con.shortterm
        if shortterm is None:
            return None
        return shortterm.set(key, value, ex)

    def clear(
        self, pattern: Union[str, List[str]]
    ) -> None:
        shortterm = self._con.shortterm
        if shortterm is None:
            return None
        return shortterm.clear(pattern)

    def keys(self, pattern: str) -> Optional[List[str]]:
        shortterm = self._con.shortterm
        if shortterm is None:
            return None
        return shortterm.keys(pattern)


class AutoCache(Cache):
    def __init__(
        self, cache: Cache, use_auto_caching: bool
    ):
        self._use_auto_caching = use_auto_caching
        self._cache = cache

    def get(self, key: str) -> Optional[Any]:
        if self._use_auto_caching:
            return self._cache.get(key)
        return None

    def set(
        self, key: str, value: dict, ex: int = 60
    ) -> None:
        if self._use_auto_caching:
            return self._cache.set(key, value, ex)
        return None

    def clear(
        self, pattern: Union[str, List[str]]
    ) -> None:
        if self._use_auto_caching:
            return self._cache.clear(pattern)
        return None

    def keys(self, pattern: str) -> Optional[List[str]]:
        if self._use_auto_caching:
            return self._cache.keys(pattern)
        return None
