from typing import List, Optional, Dict, Tuple

from agentmemory.schema.conversations import Conversation, ConversationItem
from agentmemory.connection.connection import AgentMemoryConnection
from agentmemory.utils.dataclasses.default_factory_functions import (
    current_iso_datetime,
)
from agentmemory.utils.validation.instance import check_isinstance
from agentmemory.connection.longterm.collections import Collection
from agentmemory.connection.shortterm.cache import (
    CacheKey,
    ClearCacheKey,
    CacheRetrieveType,
    ClearCacheTransactionType,
)
from agentmemory.memory.cache import AutoCache
from agentmemory.utils.transform.todict import list_to_dict


class Conversations:
    def __init__(
        self, con: AgentMemoryConnection, cache: AutoCache
    ):
        self._con = con
        self._conversations = con.longterm.conversations()
        self._cache = cache

    def get(
        self, conversation_id: str, cache: bool = True
    ) -> Conversation:
        cache_key = self._cache_key(
            CacheRetrieveType.GET, id=conversation_id
        )
        if cache:
            cache_data = self._cache.get(cache_key)
            if cache_data is not None:
                return Conversation(**cache_data)

        data = self._conversations.get(conversation_id)
        self._cache.set(cache_key, data.to_dict())
        return data

    def list(
        self,
        query: Optional[Dict] = None,
        cache: bool = True,
        limit: Optional[int] = None,
    ) -> List[Conversation]:
        cache_key = self._cache_key(
            rtype=CacheRetrieveType.LIST,
            query=query,
            limit=limit,
        )
        if cache:
            cache_data_list = self._cache.get(cache_key)
            if cache_data_list is not None:
                return [
                    Conversation(**cache_data)
                    for cache_data in cache_data_list
                ]

        data = self._conversations.list(query, limit)
        self._cache.set(cache_key, list_to_dict(data))
        return data

    def create(self, conversation: Conversation) -> Conversation:
        check_isinstance(conversation, Conversation)
        data = self._conversations.create(conversation)
        clear_keys = self._clear_cache_keys(
            ClearCacheTransactionType.CREATE
        )
        self._cache.clear(clear_keys)
        return data

    def update(self, conversation: Conversation) -> None:
        check_isinstance(conversation, Conversation)
        conversation.updated_at = current_iso_datetime()
        update_data = {
            "title": conversation.title,
            "data": conversation.data,
            "updated_at": conversation.updated_at,
        }
        self._conversations.update(
            conversation.conversation_id,
            update_data=update_data,
        )
        clear_keys = self._clear_cache_keys(
            ttype=ClearCacheTransactionType.UPDATE,
            id=conversation.conversation_id,
        )
        self._cache.clear(clear_keys)

    def delete(
        self, conversation_id: str, cascade: bool = False
    ) -> None:
        self._conversations.delete(conversation_id, cascade)
        clear_keys = self._clear_cache_keys(
            ttype=ClearCacheTransactionType.DELETE,
            id=conversation_id,
        )
        self._cache.clear(clear_keys)

    def _cache_key(
        self,
        rtype: CacheRetrieveType,
        id: Optional[str] = None,
        query: Optional[Dict] = None,
        limit: Optional[int] = None,
    ) -> str:
        key = CacheKey(
            rtype=rtype,
            col=Collection.CONVERSATIONS,
            id=id,
            query=query,
            limit=limit,
        ).key()
        return key

    def _clear_cache_keys(
        self,
        ttype: ClearCacheTransactionType,
        id: Optional[str] = None,
    ) -> List[str]:
        clear_cache_keys = ClearCacheKey(
            ttype=ttype,
            col=Collection.CONVERSATIONS,
            id=id,
            is_first_id_anchor=False,
        ).clear_keys()
        return clear_cache_keys


class ConversationItems:
    def __init__(
        self, con: AgentMemoryConnection, cache: AutoCache
    ):
        self._con = con
        self._conversation_items = con.longterm.conversation_items()
        self._cache = cache

    def get(
        self,
        conversation_id: str,
        item_id: str,
        cache: bool = True,
    ) -> ConversationItem:
        cache_key = self._cache_key(
            CacheRetrieveType.GET, id=(conversation_id, item_id)
        )
        if cache:
            cache_data = self._cache.get(cache_key)
            if cache_data is not None:
                return ConversationItem(**cache_data)

        data = self._conversation_items.get(conversation_id, item_id)
        self._cache.set(cache_key, data.to_dict())
        return data

    def list(
        self,
        query: Optional[Dict] = None,
        cache: bool = True,
        limit: Optional[int] = None,
    ) -> List[ConversationItem]:
        cache_key = self._cache_key(
            rtype=CacheRetrieveType.LIST,
            query=query,
            limit=limit,
        )
        if cache:
            cache_data_list = self._cache.get(cache_key)
            if cache_data_list is not None:
                return [
                    ConversationItem(**cache_data)
                    for cache_data in cache_data_list
                ]

        data = self._conversation_items.list(query, limit)
        self._cache.set(cache_key, list_to_dict(data))
        return data

    def list_by_conversation_id(
        self,
        conversation_id: str,
        query: Optional[Dict] = None,
        cache: bool = True,
        limit: Optional[int] = None,
    ) -> List[ConversationItem]:
        cache_key = self._cache_key(
            rtype=CacheRetrieveType.LIST_BY_ANCHOR,
            id=conversation_id,
            query=query,
            limit=limit,
        )
        if cache:
            cache_data_list = self._cache.get(cache_key)
            if cache_data_list is not None:
                return [
                    ConversationItem(**cache_data)
                    for cache_data in cache_data_list
                ]

        data = self._conversation_items.list_by_conversation_id(
            conversation_id, query, limit
        )
        self._cache.set(cache_key, list_to_dict(data))
        return data

    def list_until_id_found(
        self,
        conversation_id: str,
        item_id: str,
        cache: bool = True,
        limit: Optional[int] = None,
    ) -> List[ConversationItem]:
        cache_key = self._cache_key(
            rtype=CacheRetrieveType.LIST_UNTIL_ID_FOUND,
            id=(conversation_id, item_id),
            limit=limit,
        )
        if cache:
            cache_data_list = self._cache.get(cache_key)
            if cache_data_list is not None:
                return [
                    ConversationItem(**cache_data)
                    for cache_data in cache_data_list
                ]

        data = self._conversation_items.list_until_id_found(
            conversation_id, item_id, limit
        )
        self._cache.set(cache_key, list_to_dict(data))
        return data

    def create(self, item: ConversationItem) -> ConversationItem:
        check_isinstance(item, ConversationItem)
        data = self._conversation_items.create(item)
        clear_keys = self._clear_cache_keys(
            ttype=ClearCacheTransactionType.CREATE,
            id=(item.conversation_id, item.item_id),
        )
        self._cache.clear(clear_keys)
        return data

    def update(self, item: ConversationItem) -> None:
        check_isinstance(item, ConversationItem)
        item.updated_at = current_iso_datetime()
        update_data = {
            "role": item.role,
            "content": item.content,
            "data": item.data,
            "updated_at": item.updated_at,
        }
        self._conversation_items.update(
            conversation_id=item.conversation_id,
            item_id=item.item_id,
            update_data=update_data,
        )
        clear_keys = self._clear_cache_keys(
            ttype=ClearCacheTransactionType.UPDATE,
            id=(item.conversation_id, item.item_id),
        )
        self._cache.clear(clear_keys)

    def delete(
        self, conversation_id: str, item_id: str
    ) -> None:
        self._conversation_items.delete(conversation_id, item_id)
        clear_keys = self._clear_cache_keys(
            ttype=ClearCacheTransactionType.DELETE,
            id=(conversation_id, item_id),
        )
        self._cache.clear(clear_keys)

    def _cache_key(
        self,
        rtype: CacheRetrieveType,
        id: Optional[Tuple[str, str]] = None,
        query: Optional[Dict] = None,
        limit: Optional[int] = None,
    ) -> str:
        key = CacheKey(
            rtype=rtype,
            col=Collection.CONVERSATION_ITEMS,
            id=id,
            query=query,
            limit=limit,
        ).key()
        return key

    def _clear_cache_keys(
        self,
        ttype: ClearCacheTransactionType,
        id: Optional[Tuple[str, str]] = None,
    ) -> List[str]:
        clear_cache_keys = ClearCacheKey(
            ttype=ttype,
            col=Collection.CONVERSATION_ITEMS,
            id=id,
            is_first_id_anchor=True,
        ).clear_keys()
        return clear_cache_keys
