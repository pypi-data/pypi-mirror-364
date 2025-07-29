from typing import List, Iterator
from collections import deque
from bson import ObjectId
from pymongo.database import Database

from agentmemory.exc.errors import (
    ObjectNotFoundError,
    ObjectNotUpdatedError,
)
from agentmemory.connection.longterm.interface import (
    LongtermMemoryConversationsSchemaInterface,
    LongtermMemoryConversationItemsSchemaInterface,
)
from agentmemory.connection.longterm.collections import (
    CONVERSATIONS,
    CONVERSATION_ITEMS,
)
from agentmemory.schema.conversations import Conversation, ConversationItem
from agentmemory.utils.validation.utils import is_valid_limit

CONVERSATION_ID = "conversation_id"
ITEM_ID = "item_id"


class MongoDBConversationsSchema(LongtermMemoryConversationsSchemaInterface):
    def __init__(self, db: Database):
        self._db = db
        self._col = db[CONVERSATIONS]

    def get(self, conversation_id: str) -> Conversation:
        data = self._col.find_one({CONVERSATION_ID: conversation_id})
        if not data:
            raise ObjectNotFoundError(CONVERSATIONS, conversation_id)
        return Conversation(**data)

    def list(self, query: dict = None, limit: int = None) -> List[Conversation]:
        query = query or {}
        cursor = self._col.find(query).sort("created_at", -1)
        if isinstance(limit, int) and limit > 0:
            cursor = cursor.limit(limit)
        return [Conversation(**doc) for doc in cursor][::-1]

    def create(self, conversation: Conversation) -> Conversation:
        conversation._id = ObjectId()
        data = conversation.to_dict()
        res = self._col.insert_one(data)
        conversation._id = str(res.inserted_id)
        return Conversation(**conversation.to_dict())

    def update(self, conversation_id: str, update_data: dict) -> None:
        res = self._col.update_one(
            {CONVERSATION_ID: conversation_id},
            {"$set": update_data},
        )
        if res.modified_count == 0:
            raise ObjectNotUpdatedError(CONVERSATIONS, conversation_id)

    def delete(self, conversation_id: str, cascade: bool = False) -> None:
        self._col.delete_one({CONVERSATION_ID: conversation_id})
        if cascade:
            self._db[CONVERSATION_ITEMS].delete_many(
                {CONVERSATION_ID: conversation_id}
            )


class MongoDBConversationItemsSchema(LongtermMemoryConversationItemsSchemaInterface):
    def __init__(self, db: Database):
        self._db = db
        self._col = db[CONVERSATION_ITEMS]

    def get(self, conversation_id: str, item_id: str) -> ConversationItem:
        data = self._col.find_one({
            CONVERSATION_ID: conversation_id,
            ITEM_ID: item_id,
        })
        if not data:
            raise ObjectNotFoundError(CONVERSATION_ITEMS, (conversation_id, item_id))
        return ConversationItem(**data)

    def list(self, query: dict = None, limit: int = None) -> List[ConversationItem]:
        query = query or {}
        cursor = self._col.find(query).sort("created_at", -1)
        if is_valid_limit(limit):
            cursor = cursor.limit(limit)
        return [ConversationItem(**doc) for doc in cursor][::-1]

    def list_by_conversation_id(
        self,
        conversation_id: str,
        query: dict = None,
        limit: int = None,
    ) -> List[ConversationItem]:
        query = query or {}
        query[CONVERSATION_ID] = conversation_id
        return self.list(query, limit)

    def list_until_id_found(
        self,
        conversation_id: str,
        item_id: str,
        limit: int = None,
    ) -> List[ConversationItem]:
        return list(self._list_until_id_found(conversation_id, item_id, limit))

    def _list_until_id_found(
        self,
        conversation_id: str,
        item_id: str,
        limit: int = None,
    ) -> Iterator[ConversationItem]:
        query = {CONVERSATION_ID: conversation_id}
        buffer = deque(maxlen=limit if is_valid_limit(limit) else None)
        for data in self._col.find(query).sort("created_at", 1):
            item = ConversationItem(**data)
            buffer.append(item)
            if data[ITEM_ID] == item_id:
                break
        yield from buffer

    def create(self, item: ConversationItem) -> ConversationItem:
        item._id = ObjectId()
        data = item.to_dict()
        res = self._col.insert_one(data)
        item._id = str(res.inserted_id)
        return ConversationItem(**item.to_dict())

    def update(
        self,
        conversation_id: str,
        item_id: str,
        update_data: dict,
    ) -> None:
        res = self._col.update_one(
            {CONVERSATION_ID: conversation_id, ITEM_ID: item_id},
            {"$set": update_data},
        )
        if res.modified_count == 0:
            raise ObjectNotUpdatedError(CONVERSATIONS, conversation_id)

    def delete(self, conversation_id: str, item_id: str) -> None:
        self._col.delete_one({
            CONVERSATION_ID: conversation_id,
            ITEM_ID: item_id,
        })
