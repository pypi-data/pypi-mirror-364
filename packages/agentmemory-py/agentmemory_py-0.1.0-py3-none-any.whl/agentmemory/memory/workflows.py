from typing import List, Optional, Tuple

from agentmemory.schema.workflows import Workflow, WorkflowStep
from agentmemory.connection.connection import AgentMemoryConnection
from agentmemory.utils.dataclasses.default_factory_functions import current_iso_datetime
from agentmemory.utils.validation.instance import check_isinstance
from agentmemory.connection.longterm.collections import Collection
from agentmemory.connection.shortterm.cache import (
    CacheKey,
    ClearCacheKey,
    CacheRetrieveType,
    ClearCacheTransactionType,
)
from agentmemory.memory.cache import AutoCache
from agentmemory.utils.transform.todict import list_to_dict


class Workflows:
    def __init__(self, con: AgentMemoryConnection, cache: AutoCache):
        self._con = con
        self._workflows = con.longterm.workflows()
        self._cache = cache

    def get(self, workflow_id: str, cache: bool = True) -> Workflow:
        cache_key = self._cache_key(
            CacheRetrieveType.GET, id=workflow_id
        )
        if cache:
            cache_data = self._cache.get(cache_key)
            if cache_data is not None:
                return Workflow(**cache_data)
        data = self._workflows.get(workflow_id)
        self._cache.set(cache_key, data.to_dict())
        return data

    def list(
        self,
        query: Optional[dict] = None,
        cache: bool = True,
        limit: Optional[int] = None,
    ) -> List[Workflow]:
        cache_key = self._cache_key(
            rtype=CacheRetrieveType.LIST, query=query, limit=limit
        )
        if cache:
            cache_data_list = self._cache.get(cache_key)
            if cache_data_list is not None:
                return [
                    Workflow(**cache_data)
                    for cache_data in cache_data_list
                ]
        data = self._workflows.list(query, limit)
        self._cache.set(cache_key, list_to_dict(data))
        return data

    def list_by_conversation_item_id(
        self,
        conversation_item_id: str,
        query: Optional[dict] = None,
        cache: bool = True,
        limit: Optional[int] = None,
    ) -> List[Workflow]:
        cache_key = self._cache_key(
            rtype=CacheRetrieveType.LIST_BY_ANCHOR,
            id=conversation_item_id,
            query=query,
            limit=limit,
        )
        if cache:
            cache_data_list = self._cache.get(cache_key)
            if cache_data_list is not None:
                return [
                    Workflow(**cache_data)
                    for cache_data in cache_data_list
                ]
        data = self._workflows.list_by_conversation_item_id(
            conversation_item_id, query, limit
        )
        self._cache.set(cache_key, list_to_dict(data))
        return data

    def create(self, workflow: Workflow) -> Workflow:
        check_isinstance(workflow, Workflow)
        data = self._workflows.create(workflow)
        clear_keys = self._clear_cache_keys(
            ttype=ClearCacheTransactionType.CREATE,
            id=(workflow.conversation_item_id, workflow.workflow_id),
        )
        self._cache.clear(clear_keys)
        return data

    def update(self, workflow: Workflow) -> None:
        check_isinstance(workflow, Workflow)
        workflow.updated_at = current_iso_datetime()
        update_data = {
            "status": workflow.status,
            "user_query": workflow.user_query,
            "data": workflow.data,
            "updated_at": workflow.updated_at,
        }
        self._workflows.update(workflow.workflow_id, update_data)
        clear_keys = self._clear_cache_keys(
            ttype=ClearCacheTransactionType.UPDATE,
            id=workflow.workflow_id,
        )
        self._cache.clear(clear_keys)

    def delete(self, workflow_id: str, cascade: bool = False) -> None:
        self._workflows.delete(workflow_id, cascade)
        clear_keys = self._clear_cache_keys(
            ttype=ClearCacheTransactionType.DELETE,
            id=workflow_id,
        )
        self._cache.clear(clear_keys)

    def _cache_key(
        self,
        rtype: CacheRetrieveType,
        id: Optional[str] = None,
        query: Optional[dict] = None,
        limit: Optional[int] = None,
    ) -> str:
        key = CacheKey(
            rtype=rtype,
            col=Collection.WORKFLOWS,
            id=id,
            query=query,
            limit=limit,
        ).key()
        return key

    def _clear_cache_keys(
        self,
        ttype: ClearCacheTransactionType,
        id: Optional[str | Tuple[str, str]] = None,
    ) -> List[str]:
        clear_cache_keys = ClearCacheKey(
            ttype=ttype,
            col=Collection.WORKFLOWS,
            id=id,
            is_first_id_anchor=True,
        ).clear_keys()
        return clear_cache_keys


class WorkflowSteps:
    def __init__(self, con: AgentMemoryConnection, cache: AutoCache):
        self._con = con
        self._workflow_steps = con.longterm.workflow_steps()
        self._cache = cache

    def get(
        self,
        workflow_id: str,
        step_id: str,
        cache: bool = True,
    ) -> WorkflowStep:
        cache_key = self._cache_key(
            CacheRetrieveType.GET, id=(workflow_id, step_id)
        )
        if cache:
            cache_data = self._cache.get(cache_key)
            if cache_data is not None:
                return WorkflowStep(**cache_data)
        data = self._workflow_steps.get(workflow_id, step_id)
        self._cache.set(cache_key, data.to_dict())
        return data

    def list(
        self,
        query: Optional[dict] = None,
        cache: bool = True,
        limit: Optional[int] = None,
    ) -> List[WorkflowStep]:
        cache_key = self._cache_key(
            rtype=CacheRetrieveType.LIST, query=query, limit=limit
        )
        if cache:
            cache_data_list = self._cache.get(cache_key)
            if cache_data_list is not None:
                return [
                    WorkflowStep(**cache_data)
                    for cache_data in cache_data_list
                ]
        data = self._workflow_steps.list(query, limit)
        self._cache.set(cache_key, list_to_dict(data))
        return data

    def list_by_workflow_id(
        self,
        workflow_id: str,
        query: Optional[dict] = None,
        cache: bool = True,
        limit: Optional[int] = None,
    ) -> List[WorkflowStep]:
        cache_key = self._cache_key(
            rtype=CacheRetrieveType.LIST_BY_ANCHOR,
            id=workflow_id,
            query=query,
            limit=limit,
        )
        if cache:
            cache_data_list = self._cache.get(cache_key)
            if cache_data_list is not None:
                return [
                    WorkflowStep(**cache_data)
                    for cache_data in cache_data_list
                ]
        data = self._workflow_steps.list_by_workflow_id(
            workflow_id, query, limit
        )
        self._cache.set(cache_key, list_to_dict(data))
        return data

    def create(self, step: WorkflowStep) -> WorkflowStep:
        check_isinstance(step, WorkflowStep)
        data = self._workflow_steps.create(step)
        clear_keys = self._clear_cache_keys(
            ttype=ClearCacheTransactionType.CREATE,
            id=(step.workflow_id, step.step_id),
        )
        self._cache.clear(clear_keys)
        return data

    def update(self, step: WorkflowStep) -> None:
        check_isinstance(step, WorkflowStep)
        step.updated_at = current_iso_datetime()
        update_data = {
            "name": step.name,
            "tool": step.tool,
            "arguments": step.arguments,
            "status": step.status,
            "result": step.result,
            "logs": step.logs,
            "error": step.error,
            "data": step.data,
            "updated_at": step.updated_at,
        }
        self._workflow_steps.update(
            workflow_id=step.workflow_id,
            step_id=step.step_id,
            update_data=update_data,
        )
        clear_keys = self._clear_cache_keys(
            ttype=ClearCacheTransactionType.UPDATE,
            id=(step.workflow_id, step.step_id),
        )
        self._cache.clear(clear_keys)

    def delete(self, workflow_id: str, step_id: str) -> None:
        self._workflow_steps.delete(workflow_id, step_id)
        clear_keys = self._clear_cache_keys(
            ttype=ClearCacheTransactionType.DELETE,
            id=(workflow_id, step_id),
        )
        self._cache.clear(clear_keys)

    def _cache_key(
        self,
        rtype: CacheRetrieveType,
        id: Optional[Tuple[str, str]] = None,
        query: Optional[dict] = None,
        limit: Optional[int] = None,
    ) -> str:
        key = CacheKey(
            rtype=rtype,
            col=Collection.WORKFLOW_STEPS,
            id=id,
            query=query,
            limit=limit,
        ).key()
        return key

    def _clear_cache_keys(
        self,
        ttype: ClearCacheTransactionType,
        id: Optional[Tuple[str, str]] = None,
    ) -> List[str]:
        clear_cache_keys = ClearCacheKey(
            ttype=ttype,
            col=Collection.WORKFLOW_STEPS,
            id=id,
            is_first_id_anchor=True,
        ).clear_keys()
        return clear_cache_keys
