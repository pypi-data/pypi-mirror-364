from dataclasses import dataclass, field, asdict
from typing import Any, Optional

from agentmemory.utils.dataclasses.default_factory_functions import (
    current_iso_datetime, uuid, empty_dict
)
from agentmemory.utils.transform.todict import ToDictInterface, to_dict_factory


@dataclass
class Conversation(ToDictInterface):
    title: str
    _id: Optional[Any] = None
    conversation_id: str = field(default_factory=uuid)
    data: dict = field(default_factory=empty_dict)
    created_at: str = field(default_factory=current_iso_datetime)
    updated_at: str = field(default_factory=current_iso_datetime)

    def to_dict(self) -> dict:
        return asdict(self, dict_factory=to_dict_factory)


@dataclass
class ConversationItem(ToDictInterface):
    conversation_id: str
    role: str
    content: str
    _id: Optional[Any] = None
    item_id: str = field(default_factory=uuid)
    data: dict = field(default_factory=empty_dict)
    created_at: str = field(default_factory=current_iso_datetime)
    updated_at: str = field(default_factory=current_iso_datetime)

    def to_dict(self) -> dict:
        return asdict(self, dict_factory=to_dict_factory)
