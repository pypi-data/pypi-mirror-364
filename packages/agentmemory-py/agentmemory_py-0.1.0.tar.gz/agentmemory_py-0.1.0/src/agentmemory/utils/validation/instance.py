from typing import Type
from agentmemory.exc.errors import InstanceTypeError


def check_isinstance(obj: object, cls: Type) -> None:
    if not isinstance(obj, cls):
        raise InstanceTypeError(obj, cls)
