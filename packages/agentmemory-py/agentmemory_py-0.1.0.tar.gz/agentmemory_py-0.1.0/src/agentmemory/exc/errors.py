from typing import Type, Union, Tuple


class AgentMemoryError(Exception):
    def __init__(self, *args):
        super().__init__(*args)


class ObjectNotFoundError(AgentMemoryError):
    def __init__(self, collection: str, id: Union[str, Tuple[str]]):
        obj_id = str(id)
        msg = (
            f"Object with ID '{obj_id}' not found in "
            f"collection '{collection}'."
        )
        super().__init__(msg)


class ObjectNotUpdatedError(AgentMemoryError):
    def __init__(self, collection: str, id: Union[str, Tuple[str]]):
        obj_id = str(id)
        msg = (
            f"Object with ID '{obj_id}' in collection "
            f"'{collection}' could not be updated."
        )
        super().__init__(msg)


class ObjectNotDeletedError(AgentMemoryError):
    def __init__(
        self, collection: str, id: Union[str, Tuple[str]], e: Exception
    ):
        obj_id = str(id)
        msg = (
            f"Object with ID '{obj_id}' in collection "
            f"'{collection}' could not be deleted because: {e}."
        )
        super().__init__(msg)


class ObjectNotCreatedError(AgentMemoryError):
    def __init__(self, msg: str = None, e: Exception = None):
        final_msg = msg or f"Object could not be created because: {e}"
        super().__init__(final_msg)


class InstanceTypeError(AgentMemoryError):
    def __init__(self, obj: object, cls: Type):
        obj_name = type(obj).__name__
        cls_name = cls.__name__ if hasattr(cls, "__name__") else str(cls)
        msg = (
            f"Unexpected type: Given is an object of type "
            f"'{obj_name}', but expected is an object of type "
            f"'{cls_name}'."
        )
        super().__init__(msg)
