from typing import List
from bson import ObjectId
from pymongo.database import Database

from agentmemory.connection.longterm.interface import (
    LongtermMemoryWorkflowsSchemaInterface,
    LongtermMemoryWorkflowStepsSchemaInterface,
)
from agentmemory.exc.errors import (
    ObjectNotUpdatedError,
    ObjectNotFoundError,
)
from agentmemory.connection.longterm.collections import (
    WORKFLOWS,
    WORKFLOW_STEPS,
)
from agentmemory.schema.workflows import Workflow, WorkflowStep
from agentmemory.utils.validation.utils import is_valid_limit

WORKFLOW_ID = "workflow_id"
STEP_ID = "step_id"


class MongoDBWorkflowsSchema(LongtermMemoryWorkflowsSchemaInterface):
    def __init__(self, db: Database):
        self._db = db
        self._col = db[WORKFLOWS]

    def get(self, workflow_id: str) -> Workflow:
        data = self._col.find_one({WORKFLOW_ID: workflow_id})
        if not data:
            raise ObjectNotFoundError(WORKFLOWS, workflow_id)
        return Workflow(**data)

    def list(self, query: dict = None, limit: int = None) -> List[Workflow]:
        query = query or {}
        cursor = self._col.find(query).sort("created_at", -1)
        if is_valid_limit(limit):
            cursor = cursor.limit(limit)
        return [Workflow(**doc) for doc in cursor][::-1]

    def list_by_conversation_item_id(
        self,
        conversation_item_id: str,
        query: dict = None,
        limit: int = None,
    ) -> List[Workflow]:
        query = query or {}
        query["conversation_item_id"] = conversation_item_id
        return self.list(query, limit)

    def create(self, workflow: Workflow) -> Workflow:
        workflow._id = ObjectId()
        data = workflow.to_dict()
        res = self._col.insert_one(data)
        workflow._id = str(res.inserted_id)
        return Workflow(**workflow.to_dict())

    def update(self, workflow_id: str, update_data: dict) -> None:
        res = self._col.update_one(
            {WORKFLOW_ID: workflow_id},
            {"$set": update_data},
        )
        if res.modified_count == 0:
            raise ObjectNotUpdatedError(WORKFLOWS, workflow_id)

    def delete(self, workflow_id: str, cascade: bool) -> None:
        self._col.delete_one({WORKFLOW_ID: workflow_id})
        if cascade:
            self._db[WORKFLOW_STEPS].delete_many({WORKFLOW_ID: workflow_id})


class MongoDBWorkflowStepsSchema(LongtermMemoryWorkflowStepsSchemaInterface):
    def __init__(self, db: Database):
        self._db = db
        self._col = db[WORKFLOW_STEPS]

    def get(self, workflow_id: str, step_id: str) -> WorkflowStep:
        data = self._col.find_one({
            WORKFLOW_ID: workflow_id,
            STEP_ID: step_id,
        })
        if not data:
            raise ObjectNotFoundError(WORKFLOW_STEPS, (workflow_id, step_id))
        return WorkflowStep(**data)

    def list(self, query: dict = None, limit: int = None) -> List[WorkflowStep]:
        query = query or {}
        cursor = self._col.find(query).sort("created_at", -1)
        if is_valid_limit(limit):
            cursor = cursor.limit(limit)
        return [WorkflowStep(**doc) for doc in cursor][::-1]

    def list_by_workflow_id(
        self,
        workflow_id: str,
        query: dict = None,
        limit: int = None,
    ) -> List[WorkflowStep]:
        query = query or {}
        query[WORKFLOW_ID] = workflow_id
        return self.list(query, limit)

    def create(self, step: WorkflowStep) -> WorkflowStep:
        step._id = ObjectId()
        data = step.to_dict()
        res = self._col.insert_one(data)
        step._id = str(res.inserted_id)
        return WorkflowStep(**step.to_dict())

    def update(
        self,
        workflow_id: str,
        step_id: str,
        update_data: dict,
    ) -> None:
        res = self._col.update_one(
            {WORKFLOW_ID: workflow_id, STEP_ID: step_id},
            {"$set": update_data},
        )
        if res.modified_count == 0:
            raise ObjectNotUpdatedError(WORKFLOW_STEPS, (workflow_id, step_id))

    def delete(self, workflow_id: str, step_id: str) -> None:
        self._col.delete_one({
            WORKFLOW_ID: workflow_id,
            STEP_ID: step_id,
        })
