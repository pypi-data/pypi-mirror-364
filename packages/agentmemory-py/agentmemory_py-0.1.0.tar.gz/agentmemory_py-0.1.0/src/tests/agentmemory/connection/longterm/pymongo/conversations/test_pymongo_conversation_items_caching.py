from agentmemory import AgentMemory
from agentmemory.schema.conversations import ConversationItem
from agentmemory.connection.shortterm.cache import CacheRetrieveType
from agentmemory.connection.longterm.collections import Collection
from agentmemory.utils.dataclasses.default_factory_functions import uuid


def delete_all_conversation_items(memory: AgentMemory) -> None:
    for item in memory.conversation_items.list():
        memory.conversation_items.delete(item.conversation_id, item.item_id)


def clear_cache_complete(memory: AgentMemory) -> None:
    memory.cache.clear("*")


def prepare_test(memory: AgentMemory) -> None:
    delete_all_conversation_items(memory)
    clear_cache_complete(memory)


def test_cache_get_conversation_item(pymongo_cache_memory: AgentMemory):

    # --- Prepare ---
    prepare_test(pymongo_cache_memory)

    conversation_item = ConversationItem(
        conversation_id=uuid(),
        role="role",
        content="content",
        data={"key": "value"}
    )
    pymongo_cache_memory.conversation_items.create(conversation_item)

    # --- Execute ---
    # Retrieve the conversation item twice to test cache behavior
    item_from_db = pymongo_cache_memory.conversation_items.get(
        conversation_item.conversation_id,
        conversation_item.item_id
    )
    item_from_cache = pymongo_cache_memory.conversation_items.get(
        conversation_item.conversation_id,
        conversation_item.item_id
    )
    cache_keys = pymongo_cache_memory.cache.keys("*")

    # --- Check ---
    assert len(cache_keys) == 1
    assert f"id:{conversation_item.conversation_id},{conversation_item.item_id}" in cache_keys[0]
    assert f"type:{CacheRetrieveType.GET.value}" in cache_keys[0]
    assert f"col:{Collection.CONVERSATION_ITEMS.value}" in cache_keys[0]

    assert conversation_item.role == item_from_db.role == item_from_cache.role
    assert conversation_item.content == item_from_db.content == item_from_cache.content
    assert (
        conversation_item.data.get("key") ==
        item_from_db.data.get("key") ==
        item_from_cache.data.get("key")
    )


def test_cache_list_conversation_items(pymongo_cache_memory: AgentMemory):

    # --- Prepare ---
    prepare_test(pymongo_cache_memory)

    item_count = 10
    created_items: list[ConversationItem] = []
    for i in range(item_count):
        item = ConversationItem(
            conversation_id=uuid(),
            role="role",
            content=f"content-{i}",
            data={"key": "value"}
        )
        created_items.append(item)
        pymongo_cache_memory.conversation_items.create(item)

    # --- Execute ---
    items_from_db = pymongo_cache_memory.conversation_items.list()
    items_from_cache = pymongo_cache_memory.conversation_items.list()
    cache_keys = pymongo_cache_memory.cache.keys("*")

    # --- Check ---
    assert len(cache_keys) == 1
    assert f"type:{CacheRetrieveType.LIST.value}" in cache_keys[0]
    assert f"col:{Collection.CONVERSATION_ITEMS.value}" in cache_keys[0]

    for i, item in enumerate(created_items):
        assert item.role == items_from_db[i].role == items_from_cache[i].role
        assert item.content == items_from_db[i].content == items_from_cache[i].content
        assert (
            item.data.get("key") ==
            items_from_db[i].data.get("key") ==
            items_from_cache[i].data.get("key")
        )


def test_cache_list_conversation_items_by_conversation_id(pymongo_cache_memory: AgentMemory):

    # --- Prepare ---
    prepare_test(pymongo_cache_memory)

    conversation_id_1 = uuid()
    conversation_id_2 = uuid()
    item_count = 10
    items_conv1: list[ConversationItem] = []
    items_conv2: list[ConversationItem] = []

    for i in range(item_count):
        item1 = ConversationItem(
            conversation_id=conversation_id_1,
            role="role",
            content=f"content-{i}-1",
            data={"key": "value"}
        )
        item2 = ConversationItem(
            conversation_id=conversation_id_2,
            role="role",
            content=f"content-{i}-2",
            data={"key": "value"}
        )
        items_conv1.append(item1)
        items_conv2.append(item2)
        pymongo_cache_memory.conversation_items.create(item1)
        pymongo_cache_memory.conversation_items.create(item2)

    # --- Execute ---
    items_from_db_1 = pymongo_cache_memory.conversation_items.list_by_conversation_id(conversation_id_1)
    items_from_cache_1 = pymongo_cache_memory.conversation_items.list_by_conversation_id(conversation_id_1)
    items_from_db_2 = pymongo_cache_memory.conversation_items.list_by_conversation_id(conversation_id_2)
    items_from_cache_2 = pymongo_cache_memory.conversation_items.list_by_conversation_id(conversation_id_2)
    cache_keys = pymongo_cache_memory.cache.keys("*")

    # --- Check ---
    assert len(cache_keys) == 2
    assert any(conversation_id_1 in key for key in cache_keys)
    assert any(conversation_id_2 in key for key in cache_keys)

    assert all(f"type:{CacheRetrieveType.LIST_BY_ANCHOR.value}" in key for key in cache_keys)
    assert all(f"col:{Collection.CONVERSATION_ITEMS.value}" in key for key in cache_keys)

    assert len(pymongo_cache_memory.conversation_items.list()) == item_count * 2
    assert len(items_from_db_1) == item_count
    assert len(items_from_db_2) == item_count
    assert len(items_from_cache_1) == item_count
    assert len(items_from_cache_2) == item_count

    for i, item in enumerate(items_conv1):
        assert item.role == items_from_db_1[i].role == items_from_cache_1[i].role
        assert item.content == items_from_db_1[i].content == items_from_cache_1[i].content
        assert (
            item.data.get("key") ==
            items_from_db_1[i].data.get("key") ==
            items_from_cache_1[i].data.get("key")
        )

    for i, item in enumerate(items_conv2):
        assert item.role == items_from_db_2[i].role == items_from_cache_2[i].role
        assert item.content == items_from_db_2[i].content == items_from_cache_2[i].content
        assert (
            item.data.get("key") ==
            items_from_db_2[i].data.get("key") ==
            items_from_cache_2[i].data.get("key")
        )


def test_cache_conversation_item_clear_by_create(pymongo_cache_memory: AgentMemory):
    # Prepare
    prepare_test(pymongo_cache_memory)

    random_id = uuid()
    conv_id = uuid()

    COUNT = 10
    conversation_items: list[ConversationItem] = []
    for i in range(0, COUNT):
        item = ConversationItem(
            conversation_id=uuid(),
            role="role",
            content=f"content-{i}",
            data={"key": "value"}
        )
        conversation_items.append(item)
        pymongo_cache_memory.conversation_items.create(item)

    # Execute & Check
    _ = pymongo_cache_memory.conversation_items.get(
        conversation_id=conversation_items[0].conversation_id,
        item_id=conversation_items[0].item_id
    )  # GET 1
    _ = pymongo_cache_memory.conversation_items.get(
        conversation_id=conversation_items[0].conversation_id,
        item_id=conversation_items[0].item_id
    )  # GET 1
    _ = pymongo_cache_memory.conversation_items.get(
        conversation_id=conversation_items[1].conversation_id,
        item_id=conversation_items[1].item_id
    )  # GET 2
    _ = pymongo_cache_memory.conversation_items.get(
        conversation_id=conversation_items[2].conversation_id,
        item_id=conversation_items[2].item_id
    )  # GET 3

    _ = pymongo_cache_memory.conversation_items.list()  # list 1
    _ = pymongo_cache_memory.conversation_items.list()  # list 1
    _ = pymongo_cache_memory.conversation_items.list(query={"title": "title-1"})  # list 2
    _ = pymongo_cache_memory.conversation_items.list(query={"title": "title-2"})  # list 3
    _ = pymongo_cache_memory.conversation_items.list(limit=2)  # list 4
    _ = pymongo_cache_memory.conversation_items.list(query={"title": "title-2"}, limit=2)  # list 5

    _ = pymongo_cache_memory.conversation_items.list_by_conversation_id(random_id)  # list_anchor 1
    _ = pymongo_cache_memory.conversation_items.list_by_conversation_id(random_id)  # list_anchor 1
    _ = pymongo_cache_memory.conversation_items.list_by_conversation_id(random_id, query={"title": "title-1"})  # list_anchor 2
    _ = pymongo_cache_memory.conversation_items.list_by_conversation_id(random_id, query={"title": "title-2"})  # list_anchor 3
    _ = pymongo_cache_memory.conversation_items.list_by_conversation_id(random_id, limit=2)  # list_anchor 4
    _ = pymongo_cache_memory.conversation_items.list_by_conversation_id(random_id, query={"title": "title-2"}, limit=2)  # list_anchor 5

    _ = pymongo_cache_memory.conversation_items.list_until_id_found(conv_id, random_id)  # list_until 1 / 0
    _ = pymongo_cache_memory.conversation_items.list_until_id_found(random_id, random_id)  # list_until 2 / 1
    _ = pymongo_cache_memory.conversation_items.list_until_id_found(random_id, random_id)  # list_until 2 / 1
    _ = pymongo_cache_memory.conversation_items.list_until_id_found(random_id, "random_id")  # list_until 3 / 2
    _ = pymongo_cache_memory.conversation_items.list_until_id_found(random_id, random_id, limit=2)  # list_until 4 / 3

    assert len(pymongo_cache_memory.cache.keys("*")) == (3 + 5 + 5 + 4)

    conversation_item_new = ConversationItem(conversation_id=conv_id, role="role", content="content")
    pymongo_cache_memory.conversation_items.create(conversation_item_new)
    keys = pymongo_cache_memory.cache.keys("*")

    assert len(keys) == (3 + 5 + 3)
    assert any(conversation_items[0].conversation_id in key for key in keys)
    assert any(conversation_items[1].conversation_id in key for key in keys)
    assert any(conversation_items[2].conversation_id in key for key in keys)
    assert len([key for key in keys if random_id in key]) == 8


def test_cache_conversation_item_clear_by_update(pymongo_cache_memory: AgentMemory):
    # Prepare
    prepare_test(pymongo_cache_memory)

    random_id = uuid()

    COUNT = 10
    conversation_items: list[ConversationItem] = []
    for i in range(0, COUNT):
        item = ConversationItem(
            conversation_id=uuid(),
            role="role",
            content=f"content-{i}",
            data={"key": "value"}
        )
        conversation_items.append(item)
        pymongo_cache_memory.conversation_items.create(item)

    # Execute & Check
    GET_0_IDX = 0
    UPDATE_IDX = 5
    UPDATE_ITEM = conversation_items[UPDATE_IDX]
    _ = pymongo_cache_memory.conversation_items.get(
        conversation_items[GET_0_IDX].conversation_id,
        conversation_items[GET_0_IDX].item_id
    )  # GET 1
    _ = pymongo_cache_memory.conversation_items.get(
        conversation_items[GET_0_IDX].conversation_id,
        conversation_items[GET_0_IDX].item_id
    )  # GET 1
    _ = pymongo_cache_memory.conversation_items.get(UPDATE_ITEM.conversation_id, UPDATE_ITEM.item_id)  # GET 2

    _ = pymongo_cache_memory.conversation_items.list()  # list 1
    _ = pymongo_cache_memory.conversation_items.list()  # list 1
    _ = pymongo_cache_memory.conversation_items.list(query={"title": "title-1"})  # list 2
    _ = pymongo_cache_memory.conversation_items.list(query={"title": "title-2"})  # list 3
    _ = pymongo_cache_memory.conversation_items.list(limit=2)  # list 4
    _ = pymongo_cache_memory.conversation_items.list(query={"title": "title-2"}, limit=2)  # list 5

    _ = pymongo_cache_memory.conversation_items.list_by_conversation_id(UPDATE_ITEM.conversation_id)  # list_anchor 1 / 0
    _ = pymongo_cache_memory.conversation_items.list_by_conversation_id(random_id)  # list_anchor 2 / 1
    _ = pymongo_cache_memory.conversation_items.list_by_conversation_id(random_id, query={"title": "title-1"})  # list_anchor 3 / 2
    _ = pymongo_cache_memory.conversation_items.list_by_conversation_id(random_id, query={"title": "title-2"})  # list_anchor 4 / 3
    _ = pymongo_cache_memory.conversation_items.list_by_conversation_id(random_id, limit=2)  # list_anchor 5 / 4
    _ = pymongo_cache_memory.conversation_items.list_by_conversation_id(random_id, query={"title": "title-2"}, limit=2)  # list_anchor 6 / 5

    _ = pymongo_cache_memory.conversation_items.list_until_id_found(UPDATE_ITEM.conversation_id, UPDATE_ITEM.item_id)  # list_until 1 / 0
    _ = pymongo_cache_memory.conversation_items.list_until_id_found(random_id, random_id)  # list_until 2 / 1
    _ = pymongo_cache_memory.conversation_items.list_until_id_found(random_id, "random_id")  # list_until 3 / 2
    _ = pymongo_cache_memory.conversation_items.list_until_id_found(random_id, random_id, limit=2)  # list_until 4 / 3

    assert len(pymongo_cache_memory.cache.keys("*")) == (2 + 5 + 6 + 4)

    UPDATE_ITEM.content = "New content"

    pymongo_cache_memory.conversation_items.update(UPDATE_ITEM)
    keys = pymongo_cache_memory.cache.keys("*")

    assert len(keys) == (1 + 5 + 3)
    assert any(conversation_items[GET_0_IDX].conversation_id in key for key in keys)
    assert not any(UPDATE_ITEM.conversation_id in key for key in keys)
    assert len([key for key in keys if random_id in key]) == 8


def test_cache_conversation_item_clear_by_delete(pymongo_cache_memory: AgentMemory):
    # Prepare
    prepare_test(pymongo_cache_memory)

    random_id = uuid()

    COUNT = 10
    conversation_items: list[ConversationItem] = []
    for i in range(0, COUNT):
        item = ConversationItem(
            conversation_id=uuid(),
            role="role",
            content=f"content-{i}",
            data={"key": "value"}
        )
        conversation_items.append(item)
        pymongo_cache_memory.conversation_items.create(item)

    # Execute & Check
    GET_0_IDX = 0
    UPDATE_IDX = 5
    DELETE_ITEM = conversation_items[UPDATE_IDX]
    _ = pymongo_cache_memory.conversation_items.get(
        conversation_items[GET_0_IDX].conversation_id,
        conversation_items[GET_0_IDX].item_id
    )  # GET 1
    _ = pymongo_cache_memory.conversation_items.get(
        conversation_items[GET_0_IDX].conversation_id,
        conversation_items[GET_0_IDX].item_id
    )  # GET 1
    _ = pymongo_cache_memory.conversation_items.get(DELETE_ITEM.conversation_id, DELETE_ITEM.item_id)  # GET 2

    _ = pymongo_cache_memory.conversation_items.list()  # list 1
    _ = pymongo_cache_memory.conversation_items.list()  # list 1
    _ = pymongo_cache_memory.conversation_items.list(query={"title": "title-1"})  # list 2
    _ = pymongo_cache_memory.conversation_items.list(query={"title": "title-2"})  # list 3
    _ = pymongo_cache_memory.conversation_items.list(limit=2)  # list 4
    _ = pymongo_cache_memory.conversation_items.list(query={"title": "title-2"}, limit=2)  # list 5

    _ = pymongo_cache_memory.conversation_items.list_by_conversation_id(DELETE_ITEM.conversation_id)  # list_anchor 1 / 0
    _ = pymongo_cache_memory.conversation_items.list_by_conversation_id(random_id)  # list_anchor 2 / 1
    _ = pymongo_cache_memory.conversation_items.list_by_conversation_id(random_id, query={"title": "title-1"})  # list_anchor 3 / 2
    _ = pymongo_cache_memory.conversation_items.list_by_conversation_id(random_id, query={"title": "title-2"})  # list_anchor 4 / 3
    _ = pymongo_cache_memory.conversation_items.list_by_conversation_id(random_id, limit=2)  # list_anchor 5 / 4
    _ = pymongo_cache_memory.conversation_items.list_by_conversation_id(random_id, query={"title": "title-2"}, limit=2)  # list_anchor 6 / 5

    _ = pymongo_cache_memory.conversation_items.list_until_id_found(DELETE_ITEM.conversation_id, DELETE_ITEM.item_id)  # list_until 1 / 0
    _ = pymongo_cache_memory.conversation_items.list_until_id_found(random_id, random_id)  # list_until 2 / 1
    _ = pymongo_cache_memory.conversation_items.list_until_id_found(random_id, "random_id")  # list_until 3 / 2
    _ = pymongo_cache_memory.conversation_items.list_until_id_found(random_id, random_id, limit=2)  # list_until 4 / 3

    assert len(pymongo_cache_memory.cache.keys("*")) == (2 + 5 + 6 + 4)

    pymongo_cache_memory.conversation_items.delete(DELETE_ITEM.conversation_id, DELETE_ITEM.item_id)
    keys = pymongo_cache_memory.cache.keys("*")

    assert len(keys) == (1 + 5 + 3)
    assert any(conversation_items[GET_0_IDX].conversation_id in key for key in keys)
    assert not any(DELETE_ITEM.conversation_id in key for key in keys)
    assert len([key for key in keys if random_id in key]) == 8
