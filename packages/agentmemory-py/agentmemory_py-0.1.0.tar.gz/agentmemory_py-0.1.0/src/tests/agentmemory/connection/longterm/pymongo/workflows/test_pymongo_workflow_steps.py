import pytest

from agentmemory import AgentMemory
from agentmemory.schema.workflows import WorkflowStep, WorkflowStatus
from agentmemory.exc.errors import ObjectNotFoundError
from agentmemory.utils.dataclasses.default_factory_functions import uuid


def delete_all_workflow_steps(memory: AgentMemory, cascade: bool) -> None:
    for step in memory.workflow_steps.list():
        memory.workflow_steps.delete(step.workflow_id, step.step_id)


def test_create_workflow_step(pymongo_memory: AgentMemory):
    # --- Prepare ---
    workflow_step = WorkflowStep(
        workflow_id=uuid(),
        name=f"Name-{uuid()}",
        tool="tool",
        arguments={"arg1": "value1"},
        status=WorkflowStatus.RUNNING
    )

    # --- Execute ---
    created_step = pymongo_memory.workflow_steps.create(workflow_step)

    # --- Check ---
    assert created_step is not None

    assert created_step._id is not None
    assert created_step.workflow_id is not None
    assert created_step.created_at is not None
    assert created_step.updated_at is not None

    assert created_step._id == workflow_step._id
    assert created_step.workflow_id == workflow_step.workflow_id
    assert created_step.name == workflow_step.name
    assert created_step.tool == workflow_step.tool
    assert created_step.status == workflow_step.status
    assert created_step.arguments.get("arg1") == workflow_step.arguments["arg1"]
    assert created_step.created_at == workflow_step.created_at
    assert created_step.updated_at == workflow_step.updated_at


def test_get_workflow_step(pymongo_memory: AgentMemory):
    # Prepare
    step = WorkflowStep(
        workflow_id=uuid(),
        name=f"Name-{uuid()}",
        tool="tool",
        arguments={"arg1": "value1"},
        status=WorkflowStatus.RUNNING
    )
    _ = pymongo_memory.workflow_steps.create(step)

    # Execute
    step_get = pymongo_memory.workflow_steps.get(step.workflow_id, step.step_id)

    # Check
    assert step_get is not None

    assert step_get._id == step._id
    assert step_get.workflow_id == step.workflow_id
    assert step_get.name == step.name
    assert step_get.tool == step.tool
    assert step_get.status == step.status
    assert step_get.arguments.get("arg1") == step.arguments["arg1"]
    assert step_get.created_at == step.created_at
    assert step_get.updated_at == step.updated_at


def test_get_workflow_step_not_found(pymongo_memory: AgentMemory):
    # Prepare
    not_existing_workflow_id = uuid()
    not_existing_workflow_step_id = uuid()

    # Execute & Check
    with pytest.raises(ObjectNotFoundError):
        pymongo_memory.workflow_steps.get(
            not_existing_workflow_id,
            not_existing_workflow_step_id
        )


def test_list_workflow_steps(pymongo_memory: AgentMemory):
    # Prepare
    delete_all_workflow_steps(pymongo_memory, True)

    COUNT = 5
    LIMIT_COUNT = 3
    for i in range(0, COUNT):
        pymongo_memory.workflow_steps.create(
            step=WorkflowStep(
                workflow_id=uuid(),
                name=f"Name-{uuid()}",
                tool=f"tool-{i}",
                arguments={"arg1": "value1"},
                status=WorkflowStatus.RUNNING
            )
        )

    # Execute
    steps = pymongo_memory.workflow_steps.list()
    steps_limit = pymongo_memory.workflow_steps.list(limit=LIMIT_COUNT)
    steps_query = pymongo_memory.workflow_steps.list(query={"tool": "tool-1"})
    steps_query_fail = pymongo_memory.workflow_steps.list(query={"tool": "tool-X"})

    # Check
    assert len(steps) == COUNT
    assert len(steps_limit) == LIMIT_COUNT
    assert len(steps_query) == 1
    assert steps_query[0].tool == "tool-1"
    assert len(steps_query_fail) == 0


def test_list_workflow_steps_by_workflow_id(pymongo_memory: AgentMemory):
    # Prepare
    delete_all_workflow_steps(pymongo_memory, True)

    workflow_id_1 = uuid()
    workflow_id_2 = uuid()

    COUNT = 5
    LIMIT_COUNT = 3
    for workflow_id in [workflow_id_1, workflow_id_2]:
        for i in range(0, COUNT):
            pymongo_memory.workflow_steps.create(
                step=WorkflowStep(
                    workflow_id=workflow_id,
                    name=f"Name-{uuid()}",
                    tool=f"tool-{i}",
                    arguments={"arg1": "value1"},
                    status=WorkflowStatus.RUNNING
                )
            )

    pymongo_memory.workflow_steps.create(
        step=WorkflowStep(
            workflow_id=workflow_id_2,
            name=f"Name-{uuid()}",
            tool="tool-1",
            arguments={"arg1": "value1"},
            status=WorkflowStatus.RUNNING
        )
    )

    # Execute
    conv_steps_1 = pymongo_memory.workflow_steps.list_by_workflow_id(workflow_id_1)
    conv_steps_2 = pymongo_memory.workflow_steps.list_by_workflow_id(workflow_id_2)
    conv_steps_limit = pymongo_memory.workflow_steps.list_by_workflow_id(workflow_id_1, limit=LIMIT_COUNT)
    conv_steps_query_1 = pymongo_memory.workflow_steps.list_by_workflow_id(workflow_id_1, query={"tool": "tool-1"})
    conv_steps_query_2 = pymongo_memory.workflow_steps.list_by_workflow_id(workflow_id_2, query={"tool": "tool-1"})
    conv_steps_query_fail = pymongo_memory.workflow_steps.list_by_workflow_id(workflow_id_1, query={"tool": "XXX"})

    # Check
    assert len(conv_steps_1) == COUNT
    assert len(conv_steps_2) == COUNT + 1

    assert len(conv_steps_limit) == LIMIT_COUNT

    assert len(conv_steps_query_1) == 1
    assert len(conv_steps_query_2) == 2
    assert conv_steps_query_1[0].tool == "tool-1"
    assert len(conv_steps_query_fail) == 0


def test_update_workflow_step(pymongo_memory: AgentMemory):
    # Prepare
    step = WorkflowStep(
        workflow_id=uuid(),
        name=f"Name-{uuid()}",
        tool="tool",
        arguments={"arg1": "value1"},
        status=WorkflowStatus.RUNNING
    )
    step_created = pymongo_memory.workflow_steps.create(step)

    # Execute
    step.name = "New role"
    step.tool = "New content"
    step.status = WorkflowStatus.ERROR
    step.arguments = {"keyNew": "valueNew"}

    pymongo_memory.workflow_steps.update(step)
    step_updated = pymongo_memory.workflow_steps.get(
        step_created.workflow_id,
        step_created.step_id
    )

    # Check
    assert step_updated is not None

    assert step_updated.name == step.name
    assert step_updated.tool == step.tool
    assert step_updated.status == step.status

    assert step_updated.name != step_created.name
    assert step_updated.tool != step_created.tool
    assert step_updated.status != step_created.status

    assert step_updated.arguments.get("arg1") is None
    assert step_updated.arguments.get("keyNew") is not None
    assert step_updated.arguments.get("keyNew") == step.arguments.get("keyNew")

    assert step_updated.created_at == step.created_at
    assert step_updated.updated_at > step_updated.created_at


def test_update_conversation_read_only_fields(pymongo_memory: AgentMemory):
    # Prepare
    step = WorkflowStep(
        workflow_id=uuid(),
        name=f"Name-{uuid()}",
        tool="tool",
        arguments={"arg1": "value1"},
        status=WorkflowStatus.RUNNING
    )
    step_created = pymongo_memory.workflow_steps.create(step)

    # Execute
    step.created_at = None

    pymongo_memory.workflow_steps.update(step)
    step_updated = pymongo_memory.workflow_steps.get(step_created.workflow_id, step_created.step_id)

    # Check
    assert step_updated is not None

    assert step_updated.created_at != step.created_at
    assert step_updated.created_at == step_created.created_at


def test_delete_conversation(pymongo_memory: AgentMemory):
    # Prepare
    step = WorkflowStep(
        workflow_id=uuid(),
        name=f"Name-{uuid()}",
        tool="tool",
        arguments={"arg1": "value1"},
        status=WorkflowStatus.RUNNING
    )
    step_created = pymongo_memory.workflow_steps.create(step)

    # Execute
    step_found = pymongo_memory.workflow_steps.get(step_created.workflow_id, step_created.step_id)
    pymongo_memory.workflow_steps.delete(step_created.workflow_id, step_created.step_id)

    # Check
    assert step_found is not None

    with pytest.raises(ObjectNotFoundError):
        pymongo_memory.workflow_steps.get(step_created.workflow_id, step_created.step_id)
