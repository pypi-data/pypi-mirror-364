import pytest

from agentmemory import AgentMemory
from agentmemory.schema.conversations import ConversationItem
from agentmemory.exc.errors import ObjectNotFoundError
from agentmemory.utils.dataclasses.default_factory_functions import uuid


def delete_all_conversation_items(memory: AgentMemory) -> None:
    for item in memory.conversation_items.list():
        memory.conversation_items.delete(item.conversation_id, item.item_id)


def test_create_conversation_item(pymongo_memory: AgentMemory):
    # --- Prepare ---
    conversation_item = ConversationItem(
        conversation_id=uuid(),
        role="role",
        content="content",
        data={"key": "value"}
    )

    # --- Execute ---
    created_item = pymongo_memory.conversation_items.create(conversation_item)

    # --- Check ---
    assert created_item is not None

    assert created_item._id is not None
    assert created_item.conversation_id is not None
    assert created_item.created_at is not None
    assert created_item.updated_at is not None

    assert created_item._id == conversation_item._id
    assert created_item.conversation_id == conversation_item.conversation_id
    assert created_item.role == conversation_item.role
    assert created_item.content == conversation_item.content
    assert created_item.data.get("key") == conversation_item.data["key"]
    assert created_item.created_at == conversation_item.created_at
    assert created_item.updated_at == conversation_item.updated_at


def test_get_conversation_item(pymongo_memory: AgentMemory):
    # --- Prepare ---
    conversation_item = ConversationItem(
        conversation_id=uuid(),
        role="role",
        content="content",
        data={"key": "value"}
    )
    pymongo_memory.conversation_items.create(conversation_item)

    # --- Execute ---
    fetched_item = pymongo_memory.conversation_items.get(
        conversation_item.conversation_id,
        conversation_item.item_id
    )

    # --- Check ---
    assert fetched_item is not None

    assert fetched_item._id == conversation_item._id
    assert fetched_item.conversation_id == conversation_item.conversation_id
    assert fetched_item.role == conversation_item.role
    assert fetched_item.content == conversation_item.content
    assert fetched_item.data.get("key") == conversation_item.data["key"]
    assert fetched_item.created_at == conversation_item.created_at
    assert fetched_item.updated_at == conversation_item.updated_at


def test_get_conversation_item_not_found(pymongo_memory: AgentMemory):
    # --- Prepare ---
    non_existent_conversation_id = uuid()
    non_existent_item_id = uuid()

    # --- Execute & Check ---
    # Should raise ObjectNotFoundError for non-existent item
    with pytest.raises(ObjectNotFoundError):
        pymongo_memory.conversation_items.get(
            non_existent_conversation_id,
            non_existent_item_id
        )


def test_list_conversation_items(pymongo_memory: AgentMemory):
    # --- Prepare ---
    delete_all_conversation_items(pymongo_memory)

    conversation_id = uuid()
    item_count = 5
    limit_count = 3

    for i in range(item_count):
        pymongo_memory.conversation_items.create(
            item=ConversationItem(
                conversation_id=conversation_id,
                role="role",
                content=f"content-{i}",
                data={"key": "value"}
            )
        )

    # --- Execute ---
    all_items = pymongo_memory.conversation_items.list()
    limited_items = pymongo_memory.conversation_items.list(limit=limit_count)
    queried_items = pymongo_memory.conversation_items.list(query={"content": "content-1"})
    queried_items_fail = pymongo_memory.conversation_items.list(query={"content": "content-X"})

    # --- Check ---
    assert len(all_items) == item_count
    assert len(limited_items) == limit_count
    assert len(queried_items) == 1
    assert queried_items[0].content == "content-1"
    assert len(queried_items_fail) == 0


def test_list_conversation_items_by_conversation_id(pymongo_memory: AgentMemory):
    # --- Prepare ---
    delete_all_conversation_items(pymongo_memory)

    conversation_id_1 = uuid()
    conversation_id_2 = uuid()
    item_count = 5
    limit_count = 3

    for conv_id in [conversation_id_1, conversation_id_2]:
        for i in range(item_count):
            pymongo_memory.conversation_items.create(
                item=ConversationItem(
                    conversation_id=conv_id,
                    role="role",
                    content=f"content-{i}",
                    data={"key": "value"}
                )
            )

    # Add an extra item to conversation_id_2 with duplicate content for query test
    pymongo_memory.conversation_items.create(
        item=ConversationItem(
            conversation_id=conversation_id_2,
            role="role",
            content="content-1",
            data={"key": "value"}
        )
    )

    # --- Execute ---
    items_conv1 = pymongo_memory.conversation_items.list_by_conversation_id(conversation_id_1)
    items_conv2 = pymongo_memory.conversation_items.list_by_conversation_id(conversation_id_2)
    items_conv1_limited = pymongo_memory.conversation_items.list_by_conversation_id(conversation_id_1, limit=limit_count)
    items_conv1_query = pymongo_memory.conversation_items.list_by_conversation_id(conversation_id_1, query={"content": "content-1"})
    items_conv2_query = pymongo_memory.conversation_items.list_by_conversation_id(conversation_id_2, query={"content": "content-1"})
    items_conv1_query_fail = pymongo_memory.conversation_items.list_by_conversation_id(conversation_id_1, query={"content": "XXX"})

    # --- Check ---
    assert len(items_conv1) == item_count
    assert len(items_conv2) == item_count + 1

    assert len(items_conv1_limited) == limit_count

    assert len(items_conv1_query) == 1
    assert len(items_conv2_query) == 2
    assert items_conv1_query[0].content == "content-1"
    assert len(items_conv1_query_fail) == 0


def test_list_conversation_items_until_id_found(pymongo_memory: AgentMemory):
    # --- Prepare ---
    delete_all_conversation_items(pymongo_memory)

    conversation_id_1 = uuid()
    conversation_id_2 = uuid()
    created_items: list[ConversationItem] = []

    find_item_index = 7
    item_count = 10
    limit_count = 3

    for i in range(item_count):
        item_1 = ConversationItem(
            conversation_id=conversation_id_1,
            role="role",
            content=f"content-{i}",
            data={"key": "value"}
        )
        item_2 = ConversationItem(
            conversation_id=conversation_id_2,
            role="role",
            content=f"content-{i}",
            data={"key": "value"}
        )
        created_items.append(item_1)
        pymongo_memory.conversation_items.create(item_1)
        pymongo_memory.conversation_items.create(item_2)

    find_item = created_items[find_item_index]

    # --- Execute ---
    items_until_found = pymongo_memory.conversation_items.list_until_id_found(
        conversation_id=find_item.conversation_id,
        item_id=find_item.item_id
    )
    items_until_found_limited = pymongo_memory.conversation_items.list_until_id_found(
        conversation_id=find_item.conversation_id,
        item_id=find_item.item_id,
        limit=limit_count
    )

    # --- Check ---
    assert len(items_until_found) == find_item_index + 1
    assert len(items_until_found_limited) == limit_count

    assert items_until_found[-1].item_id == created_items[find_item_index].item_id
    assert items_until_found_limited[-1].item_id == created_items[find_item_index].item_id

    assert items_until_found[0].item_id == created_items[0].item_id
    assert items_until_found_limited[0].item_id == created_items[find_item_index - limit_count + 1].item_id


def test_update_conversation_item(pymongo_memory: AgentMemory):
    # --- Prepare ---
    conversation_item = ConversationItem(
        conversation_id=uuid(),
        role="role",
        content="content",
        data={"key": "value"}
    )
    created_item = pymongo_memory.conversation_items.create(conversation_item)

    # --- Execute ---
    conversation_item.role = "New role"
    conversation_item.content = "New content"
    conversation_item.data = {"keyNew": "valueNew"}

    pymongo_memory.conversation_items.update(conversation_item)
    updated_item = pymongo_memory.conversation_items.get(
        created_item.conversation_id,
        created_item.item_id
    )

    # --- Check ---
    assert updated_item is not None

    assert updated_item.role == conversation_item.role
    assert updated_item.content != created_item.content

    assert updated_item.data.get("key") is None
    assert updated_item.data.get("keyNew") is not None
    assert updated_item.data.get("keyNew") == conversation_item.data.get("keyNew")

    assert updated_item.created_at == conversation_item.created_at
    assert updated_item.updated_at > updated_item.created_at


def test_update_conversation_read_only_fields(pymongo_memory: AgentMemory):
    # --- Prepare ---
    conversation_item = ConversationItem(
        conversation_id=uuid(),
        role="role",
        content="content",
        data={"key": "value"}
    )
    created_item = pymongo_memory.conversation_items.create(conversation_item)

    # --- Execute ---
    conversation_item.created_at = None

    pymongo_memory.conversation_items.update(conversation_item)
    updated_item = pymongo_memory.conversation_items.get(created_item.conversation_id, created_item.item_id)

    # --- Check ---
    assert updated_item is not None

    assert updated_item.created_at != conversation_item.created_at
    assert updated_item.created_at == created_item.created_at


def test_delete_conversation(pymongo_memory: AgentMemory):
    # --- Prepare ---
    conversation_item = ConversationItem(
        conversation_id=uuid(),
        role="role",
        content="content",
        data={"key": "value"}
    )
    created_item = pymongo_memory.conversation_items.create(conversation_item)

    # --- Execute ---
    found_item = pymongo_memory.conversation_items.get(created_item.conversation_id, created_item.item_id)
    pymongo_memory.conversation_items.delete(created_item.conversation_id, created_item.item_id)

    # --- Check ---
    assert found_item is not None

    with pytest.raises(ObjectNotFoundError):
        pymongo_memory.conversation_items.get(created_item.conversation_id, created_item.item_id)
