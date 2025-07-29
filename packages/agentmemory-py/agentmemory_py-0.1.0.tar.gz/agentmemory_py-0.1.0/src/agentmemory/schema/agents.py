from dataclasses import dataclass, field, asdict
from typing import Any, Optional

from agentmemory.utils.dataclasses.default_factory_functions import (
    current_iso_datetime, uuid, empty_dict
)
from agentmemory.utils.transform.todict import ToDictInterface, to_dict_factory


@dataclass
class Agent(ToDictInterface):
    name: str
    purpose: str
    instructions: str
    persona_id: str
    tool_ids: list[str]
    _id: Optional[Any] = None
    agent_id: str = field(default_factory=uuid)
    max_steps: int = 20
    data: dict = field(default_factory=empty_dict)
    created_at: str = field(default_factory=current_iso_datetime)
    updated_at: str = field(default_factory=current_iso_datetime)

    def to_dict(self) -> dict:
        return asdict(self, dict_factory=to_dict_factory)
