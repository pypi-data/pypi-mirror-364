from pymongo import MongoClient, IndexModel, ASCENDING, DESCENDING

from agentmemory.connection.longterm.interface import (
    LongtermMemoryConnectionInterface
)
from agentmemory.connection.longterm.pymongo.conversations import (
    MongoDBConversationsSchema,
    MongoDBConversationItemsSchema
)
from agentmemory.connection.longterm.pymongo.personas import (
    MongoDBPersonasSchema
)
from agentmemory.connection.longterm.pymongo.workflows import (
    MongoDBWorkflowsSchema,
    MongoDBWorkflowStepsSchema
)
from agentmemory.connection.longterm.collections import Collection


class MongoDBConnection(LongtermMemoryConnectionInterface):
    def __init__(self, mongo_uri: str, database: str):
        self._uri = mongo_uri
        self._client = MongoClient(mongo_uri)
        self._db = self._client[database]

        self._conversations = MongoDBConversationsSchema(self._db)
        self._conversation_items = MongoDBConversationItemsSchema(self._db)
        self._personas = MongoDBPersonasSchema(self._db)
        self._workflows = MongoDBWorkflowsSchema(self._db)
        self._workflow_steps = MongoDBWorkflowStepsSchema(self._db)

        self._create_indexes()

    def conversations(self) -> MongoDBConversationsSchema:
        return self._conversations

    def conversation_items(self) -> MongoDBConversationItemsSchema:
        return self._conversation_items

    def personas(self) -> MongoDBPersonasSchema:
        return self._personas

    def workflows(self) -> MongoDBWorkflowsSchema:
        return self._workflows

    def workflow_steps(self) -> MongoDBWorkflowStepsSchema:
        return self._workflow_steps

    def _create_indexes(self) -> None:
        if self._db is None:
            raise ValueError("self._db is None")

        collections = [
            (Collection.CONVERSATIONS, conversation_indexes()),
            (Collection.CONVERSATION_ITEMS, conversation_item_indexes()),
            (Collection.PERSONAS, persona_indexes()),
            (Collection.WORKFLOWS, workflow_indexes()),
            (Collection.WORKFLOW_STEPS, workflow_step_indexes()),
        ]

        for name, indexes in collections:
            self._db[name].create_indexes(indexes=indexes)


def conversation_indexes() -> list[IndexModel]:
    return [
        IndexModel(
            [("conversation_id", ASCENDING)],
            unique=True,
            name="idx_conversation_id_unique"
        ),
        IndexModel(
            [("created_at", DESCENDING)],
            name="idx_created_at_desc"
        ),
    ]


def conversation_item_indexes() -> list[IndexModel]:
    return [
        IndexModel(
            [("item_id", ASCENDING)],
            unique=True,
            name="idx_item_id_unique"
        ),
        IndexModel(
            [("conversation_id", ASCENDING), ("created_at", DESCENDING)],
            name="idx_conversation_id_created_at"
        ),
    ]


def persona_indexes() -> list[IndexModel]:
    return [
        IndexModel(
            [("name", ASCENDING)],
            unique=True,
            name="idx_name_unique"
        ),
        IndexModel(
            [("persona_id", ASCENDING)],
            unique=True,
            name="idx_persona_id_unique"
        ),
        IndexModel(
            [("created_at", DESCENDING)],
            name="idx_created_at_desc"
        ),
    ]


def workflow_indexes() -> list[IndexModel]:
    return [
        IndexModel(
            [("workflow_id", ASCENDING)],
            unique=True,
            name="idx_workflow_id_unique"
        ),
        IndexModel(
            [("conversation_item_id", ASCENDING), ("created_at", DESCENDING)],
            name="idx_conversation_item_id_created_at"
        ),
    ]


def workflow_step_indexes() -> list[IndexModel]:
    return [
        IndexModel(
            [("step_id", ASCENDING)],
            unique=True,
            name="idx_step_id_unique"
        ),
        IndexModel(
            [("workflow_id", ASCENDING), ("created_at", DESCENDING)],
            name="idx_workflow_id_created_at"
        ),
    ]
