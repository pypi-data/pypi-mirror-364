import pytest

from agentmemory import AgentMemory
from agentmemory.schema.conversations import Conversation, ConversationItem
from agentmemory.exc.errors import ObjectNotFoundError
from agentmemory.utils.dataclasses.default_factory_functions import uuid


def delete_all_conversations(memory: AgentMemory, cascade: bool) -> None:
    for conversation in memory.conversations.list():
        memory.conversations.delete(conversation.conversation_id, cascade=cascade)


def test_create_conversation(pymongo_memory: AgentMemory):
    # --- Prepare ---
    conversation = Conversation(
        title="Test Conversation",
        data={"key": "value"}
    )

    # --- Execute ---
    created_conversation = pymongo_memory.conversations.create(conversation)

    # --- Check ---
    assert created_conversation is not None

    assert created_conversation._id is not None
    assert created_conversation.conversation_id is not None
    assert created_conversation.created_at is not None
    assert created_conversation.updated_at is not None

    assert created_conversation._id == conversation._id
    assert created_conversation.conversation_id == conversation.conversation_id
    assert created_conversation.title == conversation.title
    assert created_conversation.data.get("key") == conversation.data["key"]
    assert created_conversation.created_at == conversation.created_at
    assert created_conversation.updated_at == conversation.updated_at


def test_get_conversation(pymongo_memory: AgentMemory):
    # --- Prepare ---
    conversation = Conversation(
        title="Test Conversation",
        data={"key": "value"}
    )
    pymongo_memory.conversations.create(conversation)

    # --- Execute ---
    fetched_conversation = pymongo_memory.conversations.get(conversation.conversation_id)

    # --- Check ---
    assert fetched_conversation is not None

    assert fetched_conversation._id == conversation._id
    assert fetched_conversation.conversation_id == conversation.conversation_id
    assert fetched_conversation.title == conversation.title
    assert fetched_conversation.data.get("key") == conversation.data["key"]
    assert fetched_conversation.created_at == conversation.created_at
    assert fetched_conversation.updated_at == conversation.updated_at


def test_get_conversation_not_found(pymongo_memory: AgentMemory):
    # --- Prepare ---
    non_existent_conversation_id = uuid()

    # --- Execute & Check ---
    # Should raise ObjectNotFoundError for non-existent conversation
    with pytest.raises(ObjectNotFoundError):
        pymongo_memory.conversations.get(non_existent_conversation_id)


def test_list_conversations(pymongo_memory: AgentMemory):
    # --- Prepare ---
    delete_all_conversations(pymongo_memory, True)

    conversation_count = 5
    limit_count = 3
    for i in range(conversation_count):
        pymongo_memory.conversations.create(
            conversation=Conversation(
                title=f"title{i}"
            )
        )

    # --- Execute ---
    all_conversations = pymongo_memory.conversations.list()
    limited_conversations = pymongo_memory.conversations.list(limit=limit_count)
    queried_conversations = pymongo_memory.conversations.list(query={"title": "title1"})
    queried_conversations_fail = pymongo_memory.conversations.list(query={"title": "titleX"})

    # --- Check ---
    assert len(all_conversations) == conversation_count
    assert len(limited_conversations) == limit_count
    assert len(queried_conversations) == 1
    assert queried_conversations[0].title == "title1"
    assert len(queried_conversations_fail) == 0


def test_update_conversation(pymongo_memory: AgentMemory):
    # --- Prepare ---
    conversation = Conversation(
        title="Test Conversation",
        data={"key": "value"}
    )
    created_conversation = pymongo_memory.conversations.create(conversation)

    # --- Execute ---
    conversation.title = "New title"
    conversation.data = {"keyNew": "valueNew"}

    pymongo_memory.conversations.update(conversation)
    updated_conversation = pymongo_memory.conversations.get(created_conversation.conversation_id)

    # --- Check ---
    assert updated_conversation is not None

    assert updated_conversation.title == conversation.title
    assert updated_conversation.title != created_conversation.title

    assert updated_conversation.data.get("key") is None
    assert updated_conversation.data.get("keyNew") is not None
    assert updated_conversation.data.get("keyNew") == conversation.data.get("keyNew")

    assert updated_conversation.created_at == conversation.created_at
    assert updated_conversation.updated_at > updated_conversation.created_at


def test_update_conversation_read_only_fields(pymongo_memory: AgentMemory):
    # --- Prepare ---
    conversation = Conversation(
        title="Test Conversation",
        data={"key": "value"}
    )
    created_conversation = pymongo_memory.conversations.create(conversation)

    # --- Execute ---
    conversation.created_at = None

    pymongo_memory.conversations.update(conversation)
    updated_conversation = pymongo_memory.conversations.get(created_conversation.conversation_id)

    # --- Check ---
    assert updated_conversation is not None

    assert updated_conversation.created_at != conversation.created_at
    assert updated_conversation.created_at == created_conversation.created_at


def test_delete_conversation(pymongo_memory: AgentMemory):
    # --- Prepare ---
    conversation = Conversation(
        title="Test Conversation",
        data={"key": "value"}
    )
    created_conversation = pymongo_memory.conversations.create(conversation)

    # --- Execute ---
    found_conversation = pymongo_memory.conversations.get(created_conversation.conversation_id)
    pymongo_memory.conversations.delete(created_conversation.conversation_id)

    # --- Check ---
    assert found_conversation is not None

    with pytest.raises(ObjectNotFoundError):
        pymongo_memory.conversations.get(created_conversation.conversation_id)


def test_delete_conversation_cascade(pymongo_memory: AgentMemory):
    # --- Prepare ---
    conversation_1 = Conversation(
        title="Test Conversation",
        data={"key": "value"}
    )
    conversation_2 = Conversation(
        title="Test Conversation 2"
    )
    created_conversation_1 = pymongo_memory.conversations.create(conversation_1)
    created_conversation_2 = pymongo_memory.conversations.create(conversation_2)

    item_count = 3

    for i in range(item_count):
        pymongo_memory.conversation_items.create(
            item=ConversationItem(
                conversation_id=created_conversation_1.conversation_id,
                role=f"role{i}-1",
                content=f"content-{i}-1"
            )
        )
        pymongo_memory.conversation_items.create(
            item=ConversationItem(
                conversation_id=created_conversation_2.conversation_id,
                role=f"role{i}-2",
                content=f"content-{i}-2"
            )
        )

    # --- Execute ---
    pymongo_memory.conversations.delete(created_conversation_1.conversation_id, cascade=True)
    pymongo_memory.conversations.delete(created_conversation_2.conversation_id, cascade=False)
    items_1 = pymongo_memory.conversation_items.list_by_conversation_id(created_conversation_1.conversation_id)
    items_2 = pymongo_memory.conversation_items.list_by_conversation_id(created_conversation_2.conversation_id)

    # --- Check ---
    assert len(items_1) == 0
    assert len(items_2) == item_count
