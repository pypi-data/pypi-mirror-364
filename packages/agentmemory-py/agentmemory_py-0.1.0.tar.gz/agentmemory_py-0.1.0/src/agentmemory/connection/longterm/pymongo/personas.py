from typing import List, Optional
from bson import ObjectId
from pymongo.database import Database

from agentmemory.exc.errors import (
    ObjectNotUpdatedError,
    ObjectNotFoundError,
)
from agentmemory.connection.longterm.interface import (
    LongtermMemoryPersonasSchemaInterface,
)
from agentmemory.connection.longterm.collections import PERSONAS
from agentmemory.schema.personas import Persona
from agentmemory.utils.validation.utils import is_valid_limit

PERSONA_ID = "persona_id"


class MongoDBPersonasSchema(LongtermMemoryPersonasSchemaInterface):
    def __init__(self, db: Database):
        self._db = db
        self._col = db[PERSONAS]

    def get(self, persona_id: str) -> Persona:
        data = self._col.find_one({PERSONA_ID: persona_id})
        if not data:
            raise ObjectNotFoundError(PERSONAS, persona_id)
        return Persona(**data)

    def get_by_name(self, name: str) -> Persona:
        data = self._col.find_one({"name": name})
        if not data:
            raise ObjectNotFoundError(PERSONAS, name)
        return Persona(**data)

    def list(
        self,
        query: Optional[dict] = None,
        limit: Optional[int] = None
    ) -> List[Persona]:
        query = query or {}
        cursor = self._col.find(query).sort("created_at", -1)
        if is_valid_limit(limit):
            cursor = cursor.limit(limit)
        personas = [Persona(**doc) for doc in cursor]
        return personas[::-1]

    def create(self, persona: Persona) -> Persona:
        persona._id = ObjectId()
        data = persona.to_dict()
        res = self._col.insert_one(data)
        persona._id = str(res.inserted_id)
        return Persona(**persona.to_dict())

    def update(self, persona_id: str, update_data: dict) -> None:
        res = self._col.update_one(
            {PERSONA_ID: persona_id},
            {"$set": update_data}
        )
        if res.modified_count == 0:
            raise ObjectNotUpdatedError(PERSONAS, persona_id)

    def delete(self, persona_id: str) -> None:
        self._col.delete_one({PERSONA_ID: persona_id})
