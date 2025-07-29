from agentmemory import AgentMemory
from agentmemory.schema.conversations import Conversation
from agentmemory.connection.shortterm.cache import CacheRetrieveType
from agentmemory.connection.longterm.collections import Collection


def delete_all_conversations(memory: AgentMemory) -> None:
    for conversation in memory.conversations.list():
        memory.conversations.delete(conversation.conversation_id, cascade=True)


def clear_cache_complete(memory: AgentMemory) -> None:
    memory.cache.clear("*")


def prepare_test(memory: AgentMemory) -> None:
    delete_all_conversations(memory)
    clear_cache_complete(memory)


def test_is_cache_enabled(pymongo_cache_memory: AgentMemory):
    # --- Check ---
    assert pymongo_cache_memory.con.shortterm is not None


def test_cache_get_conversation(pymongo_cache_memory: AgentMemory):
    # --- Prepare ---
    prepare_test(pymongo_cache_memory)

    conversation = Conversation(
        title="title",
        data={"key": "value"}
    )
    pymongo_cache_memory.conversations.create(conversation)

    # --- Execute ---
    conversation_from_db = pymongo_cache_memory.conversations.get(conversation.conversation_id)
    conversation_from_cache = pymongo_cache_memory.conversations.get(conversation.conversation_id)
    cache_keys = pymongo_cache_memory.cache.keys("*")

    # --- Check ---
    assert len(cache_keys) == 1
    assert f"id:{conversation.conversation_id}" in cache_keys[0]
    assert f"type:{CacheRetrieveType.GET.value}" in cache_keys[0]
    assert f"col:{Collection.CONVERSATIONS.value}" in cache_keys[0]

    assert conversation.title == conversation_from_db.title == conversation_from_cache.title
    assert (
        conversation.data.get("key") ==
        conversation_from_db.data.get("key") ==
        conversation_from_cache.data.get("key")
    )


def test_cache_list_conversation(pymongo_cache_memory: AgentMemory):
    # --- Prepare ---
    prepare_test(pymongo_cache_memory)

    item_count = 10
    created_conversations: list[Conversation] = []
    for i in range(item_count):
        conversation = Conversation(
            title=f"title-{i}",
            data={"key": f"value-{i}"}
        )
        created_conversations.append(conversation)
        pymongo_cache_memory.conversations.create(conversation)

    # --- Execute ---
    conversations_from_db = pymongo_cache_memory.conversations.list()
    conversations_from_cache = pymongo_cache_memory.conversations.list()
    cache_keys = pymongo_cache_memory.cache.keys("*")

    # --- Check ---
    assert len(cache_keys) == 1
    assert f"type:{CacheRetrieveType.LIST.value}" in cache_keys[0]
    assert f"col:{Collection.CONVERSATIONS.value}" in cache_keys[0]

    for i, conversation in enumerate(created_conversations):
        assert conversation.title == conversations_from_db[i].title == conversations_from_cache[i].title
        assert (
            conversation.data.get("key") ==
            conversations_from_db[i].data.get("key") ==
            conversations_from_cache[i].data.get("key")
        )


def test_cache_conversation_clear_by_create(pymongo_cache_memory: AgentMemory):
    # --- Prepare ---
    prepare_test(pymongo_cache_memory)

    item_count = 10
    created_conversations: list[Conversation] = []
    for i in range(item_count):
        conversation = Conversation(
            title=f"title-{i}",
            data={"key": f"value-{i}"}
        )
        created_conversations.append(conversation)
        pymongo_cache_memory.conversations.create(conversation)

    # --- Execute & Check ---
    # Access several conversations and lists to populate the cache
    _ = pymongo_cache_memory.conversations.get(created_conversations[0].conversation_id)  # GET 1
    _ = pymongo_cache_memory.conversations.get(created_conversations[0].conversation_id)  # GET 1
    _ = pymongo_cache_memory.conversations.get(created_conversations[1].conversation_id)  # GET 2
    _ = pymongo_cache_memory.conversations.get(created_conversations[2].conversation_id)  # GET 3

    _ = pymongo_cache_memory.conversations.list()  # list 1
    _ = pymongo_cache_memory.conversations.list()  # list 1
    _ = pymongo_cache_memory.conversations.list(query={"title": "title-1"})  # list 2
    _ = pymongo_cache_memory.conversations.list(query={"title": "title-2"})  # list 3
    _ = pymongo_cache_memory.conversations.list(limit=2)  # list 4
    _ = pymongo_cache_memory.conversations.list(query={"title": "title-2"}, limit=2)  # list 5

    assert len(pymongo_cache_memory.cache.keys("*")) == (3 + 5)

    # Creating a new conversation should clear the list cache
    new_conversation = Conversation(title="New title")
    pymongo_cache_memory.conversations.create(new_conversation)
    cache_keys = pymongo_cache_memory.cache.keys("*")

    assert len(cache_keys) == 3  # Only GET caches remain
    assert any(created_conversations[0].conversation_id in key for key in cache_keys)
    assert any(created_conversations[1].conversation_id in key for key in cache_keys)
    assert any(created_conversations[2].conversation_id in key for key in cache_keys)


def test_cache_conversation_clear_by_update(pymongo_cache_memory: AgentMemory):
    # --- Prepare ---
    prepare_test(pymongo_cache_memory)

    item_count = 10
    created_conversations: list[Conversation] = []
    for i in range(item_count):
        conversation = Conversation(
            title=f"title-{i}",
            data={"key": f"value-{i}"}
        )
        created_conversations.append(conversation)
        pymongo_cache_memory.conversations.create(conversation)

    # --- Execute & Check ---
    get_0_idx = 0
    update_idx = 5
    update_id = created_conversations[update_idx].conversation_id

    # Populate cache with GET and LIST operations
    _ = pymongo_cache_memory.conversations.get(created_conversations[get_0_idx].conversation_id)  # GET 1
    _ = pymongo_cache_memory.conversations.get(created_conversations[get_0_idx].conversation_id)  # GET 1
    _ = pymongo_cache_memory.conversations.get(update_id)  # GET 2

    _ = pymongo_cache_memory.conversations.list()  # list 1
    _ = pymongo_cache_memory.conversations.list()  # list 1
    _ = pymongo_cache_memory.conversations.list(query={"title": "title-1"})  # list 2
    _ = pymongo_cache_memory.conversations.list(query={"title": "title-2"})  # list 3
    _ = pymongo_cache_memory.conversations.list(limit=2)  # list 4
    _ = pymongo_cache_memory.conversations.list(query={"title": "title-2"}, limit=2)  # list 5

    assert len(pymongo_cache_memory.cache.keys("*")) == (2 + 5)

    # Update a conversation, which should clear its GET and list caches
    updated_conversation = created_conversations[update_idx]
    updated_conversation.title = "New title"

    pymongo_cache_memory.conversations.update(updated_conversation)
    cache_keys = pymongo_cache_memory.cache.keys("*")

    assert len(cache_keys) == 1  # Only GET cache for get_0_idx remains
    assert created_conversations[get_0_idx].conversation_id in cache_keys[0]


def test_cache_conversation_clear_by_delete(pymongo_cache_memory: AgentMemory):
    # --- Prepare ---
    prepare_test(pymongo_cache_memory)

    item_count = 10
    created_conversations: list[Conversation] = []
    for i in range(item_count):
        conversation = Conversation(
            title=f"title-{i}",
            data={"key": f"value-{i}"}
        )
        created_conversations.append(conversation)
        pymongo_cache_memory.conversations.create(conversation)

    # --- Execute & Check ---
    get_0_idx = 0
    delete_idx = 5
    delete_id = created_conversations[delete_idx].conversation_id

    # Populate cache with GET and LIST operations
    _ = pymongo_cache_memory.conversations.get(created_conversations[get_0_idx].conversation_id)  # GET 1
    _ = pymongo_cache_memory.conversations.get(created_conversations[get_0_idx].conversation_id)  # GET 1
    _ = pymongo_cache_memory.conversations.get(delete_id)  # GET 2

    _ = pymongo_cache_memory.conversations.list()  # list 1
    _ = pymongo_cache_memory.conversations.list()  # list 1
    _ = pymongo_cache_memory.conversations.list(query={"title": "title-1"})  # list 2
    _ = pymongo_cache_memory.conversations.list(query={"title": "title-2"})  # list 3
    _ = pymongo_cache_memory.conversations.list(limit=2)  # list 4
    _ = pymongo_cache_memory.conversations.list(query={"title": "title-2"}, limit=2)  # list 5

    # --- Check cache state before delete ---
    assert len(pymongo_cache_memory.cache.keys("*")) == (2 + 5)

    # --- Execute: Delete a conversation, which should clear its GET and list caches ---
    pymongo_cache_memory.conversations.delete(delete_id)
    cache_keys = pymongo_cache_memory.cache.keys("*")

    # --- Check ---
    assert len(cache_keys) == 1  # Only GET cache for get_0_idx remains
    assert created_conversations[get_0_idx].conversation_id in cache_keys[0]
