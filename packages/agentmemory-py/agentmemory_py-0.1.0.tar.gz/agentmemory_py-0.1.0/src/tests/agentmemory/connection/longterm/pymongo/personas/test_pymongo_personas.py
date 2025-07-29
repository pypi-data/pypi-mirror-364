import pytest

from agentmemory import AgentMemory
from agentmemory.schema.personas import Persona
from agentmemory.exc.errors import ObjectNotFoundError
from agentmemory.utils.dataclasses.default_factory_functions import uuid


def delete_all_personas(memory: AgentMemory, cascade: bool) -> None:
    for persona in memory.personas.list():
        memory.personas.delete(persona.persona_id)


def test_create_persona(pymongo_memory: AgentMemory):
    # --- Prepare ---
    persona = Persona(
        name=f"Name-{uuid()}",
        role="Role",
        goals="Goals",
        background="Background"
    )

    # --- Execute ---
    created_persona = pymongo_memory.personas.create(persona)

    # --- Check ---
    assert created_persona is not None

    assert created_persona._id is not None
    assert created_persona.persona_id is not None
    assert created_persona.created_at is not None
    assert created_persona.updated_at is not None

    assert created_persona._id == persona._id
    assert created_persona.persona_id == persona.persona_id
    assert created_persona.name == persona.name
    assert created_persona.role == persona.role
    assert created_persona.goals == persona.goals
    assert created_persona.background == persona.background
    assert created_persona.created_at == persona.created_at
    assert created_persona.updated_at == persona.updated_at


def test_get_persona(pymongo_memory: AgentMemory):
    # Prepare
    persona = Persona(
        name=f"Name-{uuid()}",
        role="Role",
        goals="Goals",
        background="Background"
    )
    _ = pymongo_memory.personas.create(persona)

    # Execute
    persona_get = pymongo_memory.personas.get(persona.persona_id)

    # Check
    assert persona_get is not None

    assert persona_get._id == persona._id
    assert persona_get.persona_id == persona.persona_id
    assert persona_get.name == persona.name
    assert persona_get.role == persona.role
    assert persona_get.goals == persona.goals
    assert persona_get.background == persona.background
    assert persona_get.created_at == persona.created_at
    assert persona_get.updated_at == persona.updated_at


def test_get_persona_by_name(pymongo_memory: AgentMemory):
    # Prepare
    NAME = f"Name-{uuid()}"
    persona = Persona(
        name=NAME,
        role="Role",
        goals="Goals",
        background="Background"
    )
    _ = pymongo_memory.personas.create(persona)

    # Execute
    persona_get = pymongo_memory.personas.get_by_name(NAME)

    # Check
    assert persona_get is not None

    assert persona_get._id == persona._id
    assert persona_get.persona_id == persona.persona_id
    assert persona_get.name == persona.name
    assert persona_get.role == persona.role
    assert persona_get.goals == persona.goals
    assert persona_get.background == persona.background
    assert persona_get.created_at == persona.created_at
    assert persona_get.updated_at == persona.updated_at


def test_get_persona_not_found(pymongo_memory: AgentMemory):
    # Prepare
    not_existing_persona_id = uuid()

    # Execute & Check
    with pytest.raises(ObjectNotFoundError):
        pymongo_memory.personas.get(not_existing_persona_id)


def test_get_persona_by_name_not_found(pymongo_memory: AgentMemory):
    # Prepare
    not_existing_persona_id = uuid()

    # Execute & Check
    with pytest.raises(ObjectNotFoundError):
        pymongo_memory.personas.get_by_name(not_existing_persona_id)


def test_list_personas(pymongo_memory: AgentMemory):
    # Prepare
    delete_all_personas(pymongo_memory, True)

    COUNT = 5
    LIMIT_COUNT = 3
    for i in range(0, COUNT):
        pymongo_memory.personas.create(
            persona=Persona(
                name=f"Name-{i}",
                role="Role",
                goals="Goals",
                background="Background"
            )
        )

    # Execute
    personas = pymongo_memory.personas.list()
    personas_limit = pymongo_memory.personas.list(limit=LIMIT_COUNT)
    personas_query = pymongo_memory.personas.list(query={"name": "Name-1"})
    personas_query_fail = pymongo_memory.personas.list(query={"name": "Name-X"})

    # Check
    assert len(personas) == COUNT
    assert len(personas_limit) == LIMIT_COUNT
    assert len(personas_query) == 1
    assert personas_query[0].name == "Name-1"
    assert len(personas_query_fail) == 0


def test_update_persona(pymongo_memory: AgentMemory):
    # Prepare
    persona = Persona(
        name=f"Name-{uuid()}",
        role="Role",
        goals="Goals",
        background="Background"
    )
    persona_created = pymongo_memory.personas.create(persona)

    # Execute
    persona.name = "New name"
    persona.background = "New background"
    persona.embedding = [1.0, 5.0, 10.0, 80.0]
    persona.goals = "New goals"
    persona.role = "New role"

    pymongo_memory.personas.update(persona)
    persona_updated = pymongo_memory.personas.get(persona_created.persona_id)

    # Check
    assert persona_updated is not None

    assert persona_updated.name == persona.name
    assert persona_updated.background == persona.background
    assert persona_updated.goals == persona.goals
    assert persona_updated.role == persona.role
    assert len(persona_updated.embedding) == len(persona.embedding)

    assert persona_updated.name != persona_created.name
    assert persona_updated.background != persona_created.background
    assert persona_updated.goals != persona_created.goals
    assert persona_updated.role != persona_created.role
    assert len(persona_updated.embedding) != len(persona_created.embedding or [])

    assert persona_updated.created_at == persona.created_at
    assert persona_updated.updated_at > persona_updated.created_at


def test_update_persona_read_only_fields(pymongo_memory: AgentMemory):
    # Prepare
    persona = Persona(
        name=f"Name-{uuid()}",
        role="Role",
        goals="Goals",
        background="Background"
    )
    persona_created = pymongo_memory.personas.create(persona)

    # Execute
    persona.created_at = None

    pymongo_memory.personas.update(persona)
    persona_updated = pymongo_memory.personas.get(persona_created.persona_id)

    # Check
    assert persona_updated is not None

    assert persona_updated.created_at != persona.created_at
    assert persona_updated.created_at == persona_created.created_at


def test_delete_persona(pymongo_memory: AgentMemory):
    # Prepare
    persona = Persona(
        name=f"Name-{uuid()}",
        role="Role",
        goals="Goals",
        background="Background"
    )
    persona_created = pymongo_memory.personas.create(persona)

    # Execute
    persona_found = pymongo_memory.personas.get(persona_created.persona_id)
    pymongo_memory.personas.delete(persona_created.persona_id)

    # Check
    assert persona_found is not None

    with pytest.raises(ObjectNotFoundError):
        pymongo_memory.personas.get(persona_created.persona_id)
