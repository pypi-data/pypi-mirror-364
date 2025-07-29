from agentmemory import AgentMemory
from agentmemory.schema.workflows import Workflow, WorkflowStatus
from agentmemory.connection.shortterm.cache import CacheRetrieveType
from agentmemory.connection.longterm.collections import Collection
from agentmemory.utils.dataclasses.default_factory_functions import uuid


def delete_all_workflows(memory: AgentMemory) -> None:
    for workflow in memory.workflows.list():
        memory.workflows.delete(workflow.workflow_id, cascade=True)


def clear_cache_complete(memory: AgentMemory) -> None:
    memory.cache.clear("*")


def prepare_test(memory: AgentMemory) -> None:
    delete_all_workflows(memory)
    clear_cache_complete(memory)


def test_cache_get_workflow(pymongo_cache_memory: AgentMemory):
    # --- Prepare ---
    prepare_test(pymongo_cache_memory)
    workflow = Workflow(
        conversation_item_id=uuid(),
        user_query="User query",
        status=WorkflowStatus.RUNNING,
        data={"key": "value"}
    )
    pymongo_cache_memory.workflows.create(workflow)

    # --- Execute ---
    workflow_from_db = pymongo_cache_memory.workflows.get(workflow.workflow_id)
    workflow_from_cache = pymongo_cache_memory.workflows.get(workflow.workflow_id)
    cache_keys = pymongo_cache_memory.cache.keys("*")

    # --- Check ---
    assert len(cache_keys) == 1
    assert f"id:{workflow.workflow_id}" in cache_keys[0]
    assert f"type:{CacheRetrieveType.GET.value}" in cache_keys[0]
    assert f"col:{Collection.WORKFLOWS.value}" in cache_keys[0]

    assert workflow.user_query == workflow_from_db.user_query == workflow_from_cache.user_query
    assert workflow.status == workflow_from_db.status == workflow_from_cache.status
    assert (
        workflow.data.get("key") ==
        workflow_from_db.data.get("key") ==
        workflow_from_cache.data.get("key")
    )


def test_cache_list_workflow(pymongo_cache_memory: AgentMemory):
    # --- Prepare ---
    prepare_test(pymongo_cache_memory)

    item_count = 10
    created_workflows: list[Workflow] = []
    for i in range(item_count):
        workflow = Workflow(
            conversation_item_id=uuid(),
            user_query=f"User query-{i}",
            status=WorkflowStatus.RUNNING,
            data={"key": "value"}
        )
        created_workflows.append(workflow)
        pymongo_cache_memory.workflows.create(workflow)

    # --- Execute ---
    workflows_from_db = pymongo_cache_memory.workflows.list()
    workflows_from_cache = pymongo_cache_memory.workflows.list()
    cache_keys = pymongo_cache_memory.cache.keys("*")

    # --- Check ---
    assert len(cache_keys) == 1
    assert f"type:{CacheRetrieveType.LIST.value}" in cache_keys[0]
    assert f"col:{Collection.WORKFLOWS.value}" in cache_keys[0]

    for i, workflow in enumerate(created_workflows):
        assert workflow.user_query == workflows_from_db[i].user_query == workflows_from_cache[i].user_query
        assert workflow.status == workflows_from_db[i].status == workflows_from_cache[i].status
        assert (
            workflow.data.get("key") ==
            workflows_from_db[i].data.get("key") ==
            workflows_from_cache[i].data.get("key")
        )


def test_cache_list_workflows_by_conversation_item_id(pymongo_cache_memory: AgentMemory):
    # Prepare
    prepare_test(pymongo_cache_memory)

    conv_id_1 = uuid()
    conv_id_2 = uuid()

    COUNT = 10
    workflows_1: list[Workflow] = []
    workflows_2: list[Workflow] = []
    for i in range(0, COUNT):
        workflow_1 = Workflow(
            conversation_item_id=conv_id_1,
            user_query=f"User query-{i}-1",
            status=WorkflowStatus.RUNNING,
            data={"key": "value1"}
        )
        workflow_2 = Workflow(
            conversation_item_id=conv_id_2,
            user_query=f"User query-{i}-2",
            status=WorkflowStatus.ERROR,
            data={"key": "value2"}
        )
        workflows_1.append(workflow_1)
        workflows_2.append(workflow_2)
        pymongo_cache_memory.workflows.create(workflow_1)
        pymongo_cache_memory.workflows.create(workflow_2)

    # Execute
    workflow_list_1 = pymongo_cache_memory.workflows.list_by_conversation_item_id(conv_id_1)
    workflow_list_cache_1 = pymongo_cache_memory.workflows.list_by_conversation_item_id(conv_id_1)
    workflow_list_2 = pymongo_cache_memory.workflows.list_by_conversation_item_id(conv_id_2)
    workflow_list_cache_2 = pymongo_cache_memory.workflows.list_by_conversation_item_id(conv_id_2)
    keys = pymongo_cache_memory.cache.keys("*")

    # Check
    assert len(keys) == 2
    assert any(conv_id_1 in key for key in keys)
    assert any(conv_id_2 in key for key in keys)

    assert all(f"type:{CacheRetrieveType.LIST_BY_ANCHOR.value}" in key for key in keys)
    assert all(f"col:{Collection.WORKFLOWS.value}" in key for key in keys)

    assert len(pymongo_cache_memory.workflows.list()) == COUNT * 2
    assert len(workflow_list_1) == COUNT
    assert len(workflow_list_2) == COUNT
    assert len(workflow_list_cache_1) == COUNT
    assert len(workflow_list_cache_2) == COUNT

    for i, workflow in enumerate(workflows_1):
        assert workflow.user_query == workflow_list_1[i].user_query == workflow_list_cache_1[i].user_query
        assert workflow.status == workflow_list_1[i].status == workflow_list_cache_1[i].status
        assert (
            workflow.data.get("key") ==
            workflow_list_1[i].data.get("key") ==
            workflow_list_cache_1[i].data.get("key")
        )

    for i, workflow in enumerate(workflows_2):
        assert workflow.user_query == workflow_list_2[i].user_query == workflow_list_cache_2[i].user_query
        assert workflow.status == workflow_list_2[i].status == workflow_list_cache_2[i].status
        assert (
            workflow.data.get("key") ==
            workflow_list_2[i].data.get("key") ==
            workflow_list_cache_2[i].data.get("key")
        )


def test_cache_workflow_clear_by_create(pymongo_cache_memory: AgentMemory):
    # Prepare
    prepare_test(pymongo_cache_memory)

    random_id = uuid()

    COUNT = 10
    workflows: list[Workflow] = []
    for i in range(0, COUNT):
        workflow = Workflow(
            conversation_item_id=uuid(),
            user_query=f"User query-{i}",
            status=WorkflowStatus.RUNNING,
            data={"key": "value"}
        )
        workflows.append(workflow)
        pymongo_cache_memory.workflows.create(workflow)

    # Execute & Check
    _ = pymongo_cache_memory.workflows.get(workflows[0].workflow_id)  # GET 1
    _ = pymongo_cache_memory.workflows.get(workflows[0].workflow_id)  # GET 1
    _ = pymongo_cache_memory.workflows.get(workflows[1].workflow_id)  # GET 2
    _ = pymongo_cache_memory.workflows.get(workflows[2].workflow_id)  # GET 3

    _ = pymongo_cache_memory.workflows.list()  # list 1
    _ = pymongo_cache_memory.workflows.list()  # list 1
    _ = pymongo_cache_memory.workflows.list(query={"title": "title-1"})  # list 2
    _ = pymongo_cache_memory.workflows.list(query={"title": "title-2"})  # list 3
    _ = pymongo_cache_memory.workflows.list(limit=2)  # list 4
    _ = pymongo_cache_memory.workflows.list(query={"title": "title-2"}, limit=2)  # list 5

    _ = pymongo_cache_memory.workflows.list_by_conversation_item_id(random_id)  # list_anchor 1
    _ = pymongo_cache_memory.workflows.list_by_conversation_item_id(random_id)  # list_anchor 1
    _ = pymongo_cache_memory.workflows.list_by_conversation_item_id(random_id, query={"title": "title-1"})  # list_anchor 2
    _ = pymongo_cache_memory.workflows.list_by_conversation_item_id(random_id, query={"title": "title-2"})  # list_anchor 3
    _ = pymongo_cache_memory.workflows.list_by_conversation_item_id(random_id, limit=2)  # list_anchor 4
    _ = pymongo_cache_memory.workflows.list_by_conversation_item_id(random_id, query={"title": "title-2"}, limit=2)  # list_anchor 5

    assert len(pymongo_cache_memory.cache.keys("*")) == (3 + 5 + 5)

    workflow_new = Workflow(conversation_item_id=uuid(), user_query="query", status=WorkflowStatus.ERROR)
    pymongo_cache_memory.workflows.create(workflow_new)
    keys = pymongo_cache_memory.cache.keys("*")

    assert len(keys) == (3 + 5)
    assert any(workflows[0].workflow_id in key for key in keys)
    assert any(workflows[1].workflow_id in key for key in keys)
    assert any(workflows[2].workflow_id in key for key in keys)
    assert len([key for key in keys if random_id in key]) == 5


def test_cache_workflow_clear_by_update(pymongo_cache_memory: AgentMemory):
    # Prepare
    prepare_test(pymongo_cache_memory)

    random_id = uuid()

    COUNT = 10
    workflows: list[Workflow] = []
    for i in range(0, COUNT):
        workflow = Workflow(
            conversation_item_id=uuid(),
            user_query=f"User query-{i}",
            status=WorkflowStatus.RUNNING,
            data={"key": "value"}
        )
        workflows.append(workflow)
        pymongo_cache_memory.workflows.create(workflow)

    # Execute & Check
    GET_0_IDX = 0
    UPDATE_IDX = 5
    UPDATE_ID = workflows[UPDATE_IDX].workflow_id
    _ = pymongo_cache_memory.workflows.get(workflows[GET_0_IDX].workflow_id)  # GET 1
    _ = pymongo_cache_memory.workflows.get(workflows[GET_0_IDX].workflow_id)  # GET 1
    _ = pymongo_cache_memory.workflows.get(UPDATE_ID)  # GET 2

    _ = pymongo_cache_memory.workflows.list()  # list 1
    _ = pymongo_cache_memory.workflows.list()  # list 1
    _ = pymongo_cache_memory.workflows.list(query={"title": "title-1"})  # list 2
    _ = pymongo_cache_memory.workflows.list(query={"title": "title-2"})  # list 3
    _ = pymongo_cache_memory.workflows.list(limit=2)  # list 4
    _ = pymongo_cache_memory.workflows.list(query={"title": "title-2"}, limit=2)  # list 5

    _ = pymongo_cache_memory.workflows.list_by_conversation_item_id(UPDATE_ID)  # list_anchor 1 / 0
    _ = pymongo_cache_memory.workflows.list_by_conversation_item_id(random_id)  # list_anchor 2 / 1
    _ = pymongo_cache_memory.workflows.list_by_conversation_item_id(random_id, query={"title": "title-1"})  # list_anchor 3 / 2
    _ = pymongo_cache_memory.workflows.list_by_conversation_item_id(random_id, query={"title": "title-2"})  # list_anchor 4 / 3
    _ = pymongo_cache_memory.workflows.list_by_conversation_item_id(random_id, limit=2)  # list_anchor 5 / 4
    _ = pymongo_cache_memory.workflows.list_by_conversation_item_id(random_id, query={"title": "title-2"}, limit=2)  # list_anchor 6 / 5

    assert len(pymongo_cache_memory.cache.keys("*")) == (2 + 5 + 6)

    workflow_updated = workflows[UPDATE_IDX]
    workflow_updated.user_query = "New query"

    pymongo_cache_memory.workflows.update(workflow_updated)
    keys = pymongo_cache_memory.cache.keys("*")

    assert len(keys) == (1 + 5)
    assert any(workflows[GET_0_IDX].workflow_id in key for key in keys)
    assert not any(UPDATE_ID in key for key in keys)
    assert len([key for key in keys if random_id in key]) == 5


def test_cache_workflow_clear_by_delete(pymongo_cache_memory: AgentMemory):
    # Prepare
    prepare_test(pymongo_cache_memory)

    random_id = uuid()

    COUNT = 10
    workflows: list[Workflow] = []
    for i in range(0, COUNT):
        workflow = Workflow(
            conversation_item_id=uuid(),
            user_query=f"User query-{i}",
            status=WorkflowStatus.RUNNING,
            data={"key": "value"}
        )
        workflows.append(workflow)
        pymongo_cache_memory.workflows.create(workflow)

    # Execute & Check
    GET_0_IDX = 0
    DELETE_ID = workflows[5].workflow_id
    _ = pymongo_cache_memory.workflows.get(workflows[GET_0_IDX].workflow_id)  # GET 1
    _ = pymongo_cache_memory.workflows.get(workflows[GET_0_IDX].workflow_id)  # GET 1
    _ = pymongo_cache_memory.workflows.get(DELETE_ID)  # GET 2

    _ = pymongo_cache_memory.workflows.list()  # list 1
    _ = pymongo_cache_memory.workflows.list()  # list 1
    _ = pymongo_cache_memory.workflows.list(query={"title": "title-1"})  # list 2
    _ = pymongo_cache_memory.workflows.list(query={"title": "title-2"})  # list 3
    _ = pymongo_cache_memory.workflows.list(limit=2)  # list 4
    _ = pymongo_cache_memory.workflows.list(query={"title": "title-2"}, limit=2)  # list 5

    _ = pymongo_cache_memory.workflows.list_by_conversation_item_id(DELETE_ID)  # list_anchor 1 / 0
    _ = pymongo_cache_memory.workflows.list_by_conversation_item_id(random_id)  # list_anchor 2 / 1
    _ = pymongo_cache_memory.workflows.list_by_conversation_item_id(random_id, query={"title": "title-1"})  # list_anchor 3 / 2
    _ = pymongo_cache_memory.workflows.list_by_conversation_item_id(random_id, query={"title": "title-2"})  # list_anchor 4 / 3
    _ = pymongo_cache_memory.workflows.list_by_conversation_item_id(random_id, limit=2)  # list_anchor 5 / 4
    _ = pymongo_cache_memory.workflows.list_by_conversation_item_id(random_id, query={"title": "title-2"}, limit=2)  # list_anchor 6 / 5

    assert len(pymongo_cache_memory.cache.keys("*")) == (2 + 5 + 6)

    pymongo_cache_memory.workflows.delete(DELETE_ID)
    keys = pymongo_cache_memory.cache.keys("*")

    assert len(keys) == (1 + 5)
    assert any(workflows[GET_0_IDX].workflow_id in key for key in keys)
    assert not any(DELETE_ID in key for key in keys)
    assert len([key for key in keys if random_id in key]) == 5
