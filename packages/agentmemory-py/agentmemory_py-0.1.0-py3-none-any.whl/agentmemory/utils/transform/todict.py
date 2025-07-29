from bson import ObjectId
from abc import ABC, abstractmethod
from typing import Any


class ToDictInterface(ABC):
    @abstractmethod
    def to_dict(self) -> dict: pass


def list_to_dict(records: list[ToDictInterface]) -> list[dict]:
    return [record.to_dict() for record in records]


def to_dict_factory(items: list[tuple[str, Any]]) -> dict:
    return {
        k: str(v) if isinstance(v, ObjectId) else v
        for k, v in items
    }
