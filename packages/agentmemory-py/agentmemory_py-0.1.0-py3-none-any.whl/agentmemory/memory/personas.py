from typing import List

from agentmemory.schema.personas import Persona
from agentmemory.connection.connection import AgentMemoryConnection
from agentmemory.utils.dataclasses.default_factory_functions import current_iso_datetime
from agentmemory.utils.validation.instance import check_isinstance
from agentmemory.connection.longterm.collections import Collection
from agentmemory.utils.transform.todict import list_to_dict
from agentmemory.connection.shortterm.cache import (
    CacheKey,
    ClearCacheKey,
    CacheRetrieveType,
    ClearCacheTransactionType,
)
from agentmemory.memory.cache import AutoCache


class Personas:
    def __init__(self, con: AgentMemoryConnection, cache: AutoCache):
        self._con = con
        self._personas = con.longterm.personas()
        self._cache = cache

    def get(self, persona_id: str, cache: bool = True) -> Persona:
        cache_key = self._cache_key(CacheRetrieveType.GET, id=persona_id)
        if cache:
            cache_data = self._cache.get(cache_key)
            if cache_data is not None:
                return Persona(**cache_data)
        data = self._personas.get(persona_id)
        self._cache.set(cache_key, data.to_dict())
        return data

    def get_by_name(self, name: str, cache: bool = True) -> Persona:
        cache_key = self._cache_key(CacheRetrieveType.GET, id=name)
        if cache:
            cache_data = self._cache.get(cache_key)
            if cache_data is not None:
                return Persona(**cache_data)
        data = self._personas.get_by_name(name)
        self._cache.set(cache_key, data.to_dict())
        return data

    def list(
        self,
        query: dict = None,
        cache: bool = True,
        limit: int = None
    ) -> List[Persona]:
        cache_key = self._cache_key(
            rtype=CacheRetrieveType.LIST,
            query=query,
            limit=limit
        )
        if cache:
            cache_data_list = self._cache.get(cache_key)
            if cache_data_list is not None:
                return [
                    Persona(**cache_data)
                    for cache_data in cache_data_list
                ]
        data = self._personas.list(query, limit)
        self._cache.set(cache_key, list_to_dict(data))
        return data

    def create(self, persona: Persona) -> Persona:
        check_isinstance(persona, Persona)
        data = self._personas.create(persona)
        clear_keys = self._clear_cache_keys(ClearCacheTransactionType.CREATE)
        self._cache.clear(clear_keys)
        return data

    def update(self, persona: Persona) -> None:
        check_isinstance(persona, Persona)
        persona.updated_at = current_iso_datetime()
        update_data = {
            "name": persona.name,
            "role": persona.role,
            "goals": persona.goals,
            "background": persona.background,
            "embedding": persona.embedding,
            "updated_at": persona.updated_at,
        }
        self._personas.update(persona.persona_id, update_data)
        clear_keys = self._clear_cache_keys(
            ttype=ClearCacheTransactionType.UPDATE,
            id=persona.persona_id
        )
        self._cache.clear(clear_keys)

    def delete(self, persona_id: str) -> None:
        self._personas.delete(persona_id)
        clear_keys = self._clear_cache_keys(
            ttype=ClearCacheTransactionType.DELETE,
            id=persona_id
        )
        self._cache.clear(clear_keys)

    def _cache_key(
        self,
        rtype: CacheRetrieveType,
        id: str = None,
        query: dict = None,
        limit: int = None
    ) -> str:
        key = CacheKey(
            rtype=rtype,
            col=Collection.PERSONAS,
            id=id,
            query=query,
            limit=limit
        ).key()
        return key

    def _clear_cache_keys(
        self,
        ttype: ClearCacheTransactionType,
        id: str = None
    ) -> List[str]:
        clear_cache_keys = ClearCacheKey(
            ttype=ttype,
            col=Collection.PERSONAS,
            id=id,
            is_first_id_anchor=False
        ).clear_keys()
        return clear_cache_keys
