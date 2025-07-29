import pytest

from agentmemory import AgentMemory
from agentmemory.schema.workflows import Workflow, WorkflowStep, WorkflowStatus
from agentmemory.exc.errors import ObjectNotFoundError
from agentmemory.utils.dataclasses.default_factory_functions import uuid


def delete_all_workflows(memory: AgentMemory, cascade: bool) -> None:
    for workflow in memory.workflows.list():
        memory.workflows.delete(workflow.workflow_id, cascade=cascade)


def test_create_workflow(pymongo_memory: AgentMemory):
    # Prepare
    workflow = Workflow(
        conversation_item_id=uuid(),
        user_query="User query",
        status=WorkflowStatus.RUNNING,
        data={"key": "value"}
    )

    # Execute
    created_workflow = pymongo_memory.workflows.create(workflow)

    # Check
    assert created_workflow is not None

    assert created_workflow._id is not None
    assert created_workflow.workflow_id is not None
    assert created_workflow.conversation_item_id is not None
    assert created_workflow.created_at is not None
    assert created_workflow.updated_at is not None

    assert created_workflow._id == workflow._id
    assert created_workflow.workflow_id == workflow.workflow_id
    assert created_workflow.conversation_item_id == workflow.conversation_item_id
    assert created_workflow.user_query == workflow.user_query
    assert created_workflow.status == workflow.status
    assert created_workflow.data.get("key") == workflow.data.get("key")
    assert created_workflow.created_at == workflow.created_at
    assert created_workflow.updated_at == workflow.updated_at


def test_get_workflow(pymongo_memory: AgentMemory):
    # Prepare
    workflow = Workflow(
        conversation_item_id=uuid(),
        user_query="User query",
        status=WorkflowStatus.RUNNING
    )
    pymongo_memory.workflows.create(workflow)

    # Execute
    retrieved_workflow = pymongo_memory.workflows.get(workflow.workflow_id)

    # Check
    assert retrieved_workflow is not None

    assert retrieved_workflow._id == workflow._id
    assert retrieved_workflow.workflow_id == workflow.workflow_id
    assert retrieved_workflow.conversation_item_id == workflow.conversation_item_id
    assert retrieved_workflow.user_query == workflow.user_query
    assert retrieved_workflow.status == workflow.status
    assert retrieved_workflow.created_at == workflow.created_at
    assert retrieved_workflow.updated_at == workflow.updated_at


def test_get_workflow_not_found(pymongo_memory: AgentMemory):
    # Prepare
    non_existent_workflow_id = uuid()

    # Execute & Check
    with pytest.raises(ObjectNotFoundError):
        pymongo_memory.workflows.get(non_existent_workflow_id)


def test_list_workflows(pymongo_memory: AgentMemory):
    # Prepare
    delete_all_workflows(pymongo_memory, cascade=True)

    workflow_count = 5
    limit_count = 3

    for i in range(workflow_count):
        pymongo_memory.workflows.create(
            workflow=Workflow(
                conversation_item_id=uuid(),
                user_query=f"User query XYZ-{i}",
                status=WorkflowStatus.RUNNING
            )
        )

    # Execute
    all_workflows = pymongo_memory.workflows.list()
    limited_workflows = pymongo_memory.workflows.list(limit=limit_count)
    filtered_workflows = pymongo_memory.workflows.list(query={"user_query": "User query XYZ-1"})
    no_match_workflows = pymongo_memory.workflows.list(query={"user_query": "XXX"})

    # Check
    assert len(all_workflows) == workflow_count
    assert len(limited_workflows) == limit_count
    assert len(filtered_workflows) == 1
    assert filtered_workflows[0].user_query == "User query XYZ-1"
    assert len(no_match_workflows) == 0


def test_list_workflows_by_conversation_item_id(pymongo_memory: AgentMemory):
    # Prepare
    delete_all_workflows(pymongo_memory, cascade=True)

    conversation_item_id_1 = uuid()
    conversation_item_id_2 = uuid()
    workflow_count = 5
    limit_count = 3

    # Create workflows for two different conversation item IDs
    for item_id in [conversation_item_id_1, conversation_item_id_2]:
        for i in range(workflow_count):
            pymongo_memory.workflows.create(
                workflow=Workflow(
                    conversation_item_id=item_id,
                    user_query=f"User query XYZ-{i}",
                    status=WorkflowStatus.RUNNING
                )
            )

    # Add an extra workflow for conversation_item_id_2 with a duplicate user_query
    pymongo_memory.workflows.create(
        workflow=Workflow(
            conversation_item_id=conversation_item_id_2,
            user_query="User query XYZ-1",
            status=WorkflowStatus.RUNNING
        )
    )

    # Execute
    workflows_for_item_1 = pymongo_memory.workflows.list_by_conversation_item_id(conversation_item_id_1)
    workflows_for_item_2 = pymongo_memory.workflows.list_by_conversation_item_id(conversation_item_id_2)
    limited_workflows = pymongo_memory.workflows.list_by_conversation_item_id(conversation_item_id_1, limit=limit_count)
    filtered_item_1 = pymongo_memory.workflows.list_by_conversation_item_id(conversation_item_id_1, query={"user_query": "User query XYZ-1"})
    filtered_item_2 = pymongo_memory.workflows.list_by_conversation_item_id(conversation_item_id_2, query={"user_query": "User query XYZ-1"})
    no_match_item_1 = pymongo_memory.workflows.list_by_conversation_item_id(conversation_item_id_1, query={"user_query": "XXX"})

    # Check
    assert len(workflows_for_item_1) == workflow_count
    assert len(workflows_for_item_2) == workflow_count + 1

    assert len(limited_workflows) == limit_count

    assert len(filtered_item_1) == 1
    assert len(filtered_item_2) == 2
    assert filtered_item_1[0].user_query == "User query XYZ-1"
    assert len(no_match_item_1) == 0


def test_update_workflow(pymongo_memory: AgentMemory):
    # Prepare
    workflow = Workflow(
        conversation_item_id=uuid(),
        user_query="User query",
        status=WorkflowStatus.RUNNING,
        data={"key": "value"}
    )
    created_workflow = pymongo_memory.workflows.create(workflow)

    # Execute
    workflow.user_query = "New query"
    workflow.status = WorkflowStatus.SUCCESS
    workflow.data = {"keyNew": "valueNew"}

    pymongo_memory.workflows.update(workflow)
    updated_workflow = pymongo_memory.workflows.get(created_workflow.workflow_id)

    # Check
    assert updated_workflow is not None
    assert updated_workflow.data.get("key") is None
    assert updated_workflow.data.get("keyNew") is not None

    assert updated_workflow.user_query == workflow.user_query
    assert updated_workflow.status == workflow.status
    assert updated_workflow.data.get("keyNew") == workflow.data.get("keyNew")

    assert updated_workflow.created_at == workflow.created_at
    assert updated_workflow.updated_at > updated_workflow.created_at


def test_update_workflow_read_only_fields(pymongo_memory: AgentMemory):
    # Prepare
    workflow = Workflow(
        conversation_item_id=uuid(),
        user_query="User query",
        status=WorkflowStatus.RUNNING
    )
    created_workflow = pymongo_memory.workflows.create(workflow)

    # Execute
    # Attempt to update read-only fields (should be ignored by update logic)
    workflow.conversation_item_id = None
    workflow.created_at = None

    pymongo_memory.workflows.update(workflow)
    updated_workflow = pymongo_memory.workflows.get(created_workflow.workflow_id)

    # Check
    assert updated_workflow is not None

    assert updated_workflow.created_at != workflow.created_at
    assert updated_workflow.conversation_item_id != workflow.conversation_item_id

    assert updated_workflow.conversation_item_id == created_workflow.conversation_item_id
    assert updated_workflow.created_at == created_workflow.created_at


def test_delete_workflow(pymongo_memory: AgentMemory):
    # Prepare
    workflow = Workflow(
        conversation_item_id=uuid(),
        user_query="User query",
        status=WorkflowStatus.RUNNING
    )
    created_workflow = pymongo_memory.workflows.create(workflow)

    # Execute
    found_workflow = pymongo_memory.workflows.get(created_workflow.workflow_id)
    pymongo_memory.workflows.delete(created_workflow.workflow_id)

    # Check
    assert found_workflow is not None

    with pytest.raises(ObjectNotFoundError):
        pymongo_memory.workflows.get(created_workflow.workflow_id)


def test_delete_workflow_cascade(pymongo_memory: AgentMemory):
    # Prepare
    workflow_1 = Workflow(
        conversation_item_id=uuid(),
        user_query="User query",
        status=WorkflowStatus.RUNNING
    )
    workflow_2 = Workflow(
        conversation_item_id=uuid(),
        user_query="User query 2",
        status=WorkflowStatus.RUNNING
    )
    created_workflow_1 = pymongo_memory.workflows.create(workflow_1)
    created_workflow_2 = pymongo_memory.workflows.create(workflow_2)

    step_count = 3

    # Create steps for both workflows
    for i in range(step_count):
        pymongo_memory.workflow_steps.create(
            step=WorkflowStep(
                workflow_id=created_workflow_1.workflow_id,
                name=f"Name-{i}-1",
                tool=f"Tool-{i}-1",
                arguments={"arg1": "value1"},
                status=WorkflowStatus.SUCCESS
            )
        )
        pymongo_memory.workflow_steps.create(
            step=WorkflowStep(
                workflow_id=created_workflow_2.workflow_id,
                name=f"Name-{i}-2",
                tool=f"Tool-{i}-2",
                arguments={"arg1": "value1"},
                status=WorkflowStatus.SUCCESS
            )
        )

    # Execute
    # Cascade delete: steps for workflow_1 should be deleted, steps for workflow_2 should remain
    pymongo_memory.workflows.delete(created_workflow_1.workflow_id, cascade=True)
    pymongo_memory.workflows.delete(created_workflow_2.workflow_id, cascade=False)
    steps_for_workflow_1 = pymongo_memory.workflow_steps.list_by_workflow_id(created_workflow_1.workflow_id)
    steps_for_workflow_2 = pymongo_memory.workflow_steps.list_by_workflow_id(created_workflow_2.workflow_id)

    # Check
    assert len(steps_for_workflow_1) == 0  # All steps for workflow_1 should be deleted
    assert len(steps_for_workflow_2) == step_count  # Steps for workflow_2 should remain
