from agentmemory import AgentMemory
from agentmemory.schema.personas import Persona
from agentmemory.connection.shortterm.cache import CacheRetrieveType
from agentmemory.connection.longterm.collections import Collection
from agentmemory.utils.dataclasses.default_factory_functions import uuid


def delete_all_personas(memory: AgentMemory) -> None:
    for persona in memory.personas.list():
        memory.personas.delete(persona.persona_id)


def clear_cache_complete(memory: AgentMemory) -> None:
    memory.cache.clear("*")


def prepare_test(memory: AgentMemory) -> None:
    delete_all_personas(memory)
    clear_cache_complete(memory)


def test_cache_get_persona(pymongo_cache_memory: AgentMemory):
    # --- Prepare ---
    prepare_test(pymongo_cache_memory)
    persona = Persona(
        name=f"Name-{uuid()}",
        role="Role",
        goals="Goals",
        background="Background"
    )
    pymongo_cache_memory.personas.create(persona)

    # --- Execute ---
    persona_from_db = pymongo_cache_memory.personas.get(persona.persona_id)
    persona_from_cache = pymongo_cache_memory.personas.get(persona.persona_id)
    cache_keys = pymongo_cache_memory.cache.keys("*")

    # --- Check ---
    assert len(cache_keys) == 1
    assert f"id:{persona.persona_id}" in cache_keys[0]
    assert f"type:{CacheRetrieveType.GET.value}" in cache_keys[0]
    assert f"col:{Collection.PERSONAS.value}" in cache_keys[0]

    assert persona.name == persona_from_db.name == persona_from_cache.name
    assert persona.role == persona_from_db.role == persona_from_cache.role
    assert persona.goals == persona_from_db.goals == persona_from_cache.goals
    assert persona.background == persona_from_db.background == persona_from_cache.background


def test_cache_list_persona(pymongo_cache_memory: AgentMemory):
    # --- Prepare ---
    prepare_test(pymongo_cache_memory)

    item_count = 10
    created_personas: list[Persona] = []
    for i in range(item_count):
        persona = Persona(
            name=f"Name-{uuid()}",
            role=f"Role-{i}",
            goals="Goals",
            background="Background"
        )
        created_personas.append(persona)
        pymongo_cache_memory.personas.create(persona)

    # --- Execute ---
    personas_from_db = pymongo_cache_memory.personas.list()
    personas_from_cache = pymongo_cache_memory.personas.list()
    cache_keys = pymongo_cache_memory.cache.keys("*")

    # --- Check ---
    assert len(cache_keys) == 1
    assert f"type:{CacheRetrieveType.LIST.value}" in cache_keys[0]
    assert f"col:{Collection.PERSONAS.value}" in cache_keys[0]

    for i, persona in enumerate(created_personas):
        assert persona.name == personas_from_db[i].name == personas_from_cache[i].name
        assert persona.role == personas_from_db[i].role == personas_from_cache[i].role
        assert persona.goals == personas_from_db[i].goals == personas_from_cache[i].goals
        assert persona.background == personas_from_db[i].background == personas_from_cache[i].background


def test_cache_persona_clear_by_create(pymongo_cache_memory: AgentMemory):
    # Prepare
    prepare_test(pymongo_cache_memory)

    COUNT = 10
    personas: list[Persona] = []
    for i in range(0, COUNT):
        persona = Persona(
            name=f"Name-{uuid()}",
            role=f"Role-{i}",
            goals="Goals",
            background="Background"
        )
        personas.append(persona)
        pymongo_cache_memory.personas.create(persona)

    # Execute & Check
    _ = pymongo_cache_memory.personas.get(personas[0].persona_id)  # GET 1
    _ = pymongo_cache_memory.personas.get(personas[0].persona_id)  # GET 1
    _ = pymongo_cache_memory.personas.get(personas[1].persona_id)  # GET 2
    _ = pymongo_cache_memory.personas.get(personas[2].persona_id)  # GET 3

    _ = pymongo_cache_memory.personas.list()  # list 1
    _ = pymongo_cache_memory.personas.list()  # list 1
    _ = pymongo_cache_memory.personas.list(query={"title": "title-1"})  # list 2
    _ = pymongo_cache_memory.personas.list(query={"title": "title-2"})  # list 3
    _ = pymongo_cache_memory.personas.list(limit=2)  # list 4
    _ = pymongo_cache_memory.personas.list(query={"title": "title-2"}, limit=2)  # list 5

    assert len(pymongo_cache_memory.cache.keys("*")) == (3 + 5)

    persona_new = Persona(name="New name", role="role", goals="goals", background="bck")
    pymongo_cache_memory.personas.create(persona_new)
    keys = pymongo_cache_memory.cache.keys("*")

    assert len(keys) == (3 + 0)
    assert any(personas[0].persona_id in key for key in keys)
    assert any(personas[1].persona_id in key for key in keys)
    assert any(personas[2].persona_id in key for key in keys)


def test_cache_persona_clear_by_update(pymongo_cache_memory: AgentMemory):
    # Prepare
    prepare_test(pymongo_cache_memory)

    COUNT = 10
    personas: list[Persona] = []
    for i in range(0, COUNT):
        persona = Persona(
            name=f"Name-{uuid()}",
            role=f"Role-{i}",
            goals="Goals",
            background="Background"
        )
        personas.append(persona)
        pymongo_cache_memory.personas.create(persona)

    # Execute & Check
    GET_0_IDX = 0
    UPDATE_IDX = 5
    UPDATE_ID = personas[UPDATE_IDX].persona_id
    _ = pymongo_cache_memory.personas.get(personas[GET_0_IDX].persona_id)  # GET 1
    _ = pymongo_cache_memory.personas.get(personas[GET_0_IDX].persona_id)  # GET 1
    _ = pymongo_cache_memory.personas.get(UPDATE_ID)  # GET 2

    _ = pymongo_cache_memory.personas.list()  # list 1
    _ = pymongo_cache_memory.personas.list()  # list 1
    _ = pymongo_cache_memory.personas.list(query={"title": "title-1"})  # list 2
    _ = pymongo_cache_memory.personas.list(query={"title": "title-2"})  # list 3
    _ = pymongo_cache_memory.personas.list(limit=2)  # list 4
    _ = pymongo_cache_memory.personas.list(query={"title": "title-2"}, limit=2)  # list 5

    assert len(pymongo_cache_memory.cache.keys("*")) == (2 + 5)

    persona_updated = personas[UPDATE_IDX]
    persona_updated.name = "New name"

    pymongo_cache_memory.personas.update(persona_updated)
    keys = pymongo_cache_memory.cache.keys("*")

    assert len(keys) == (1 + 0)
    assert personas[GET_0_IDX].persona_id in keys[0]


def test_cache_persona_clear_by_delete(pymongo_cache_memory: AgentMemory):
    # Prepare
    prepare_test(pymongo_cache_memory)

    COUNT = 10
    personas: list[Persona] = []
    for i in range(0, COUNT):
        persona = Persona(
            name=f"Name-{uuid()}",
            role=f"Role-{i}",
            goals="Goals",
            background="Background"
        )
        personas.append(persona)
        pymongo_cache_memory.personas.create(persona)

    # Execute & Check
    GET_0_IDX = 0
    DELETE_ID = personas[5].persona_id
    _ = pymongo_cache_memory.personas.get(personas[GET_0_IDX].persona_id)  # GET 1
    _ = pymongo_cache_memory.personas.get(personas[GET_0_IDX].persona_id)  # GET 1
    _ = pymongo_cache_memory.personas.get(DELETE_ID)  # GET 2

    _ = pymongo_cache_memory.personas.list()  # list 1
    _ = pymongo_cache_memory.personas.list()  # list 1
    _ = pymongo_cache_memory.personas.list(query={"title": "title-1"})  # list 2
    _ = pymongo_cache_memory.personas.list(query={"title": "title-2"})  # list 3
    _ = pymongo_cache_memory.personas.list(limit=2)  # list 4
    _ = pymongo_cache_memory.personas.list(query={"title": "title-2"}, limit=2)  # list 5

    assert len(pymongo_cache_memory.cache.keys("*")) == (2 + 5)

    pymongo_cache_memory.personas.delete(DELETE_ID)
    keys = pymongo_cache_memory.cache.keys("*")

    assert len(keys) == (1 + 0)
    assert personas[GET_0_IDX].persona_id in keys[0]
