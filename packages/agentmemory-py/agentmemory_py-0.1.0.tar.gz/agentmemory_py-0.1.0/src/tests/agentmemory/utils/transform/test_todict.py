import pytest

from bson import ObjectId

from agentmemory.utils.transform.todict import (
    ToDictInterface, list_to_dict, to_dict_factory
)


def test_to_dict_interface():
    # Prepare
    class ToDictInterfaceFailImplementation(ToDictInterface):
        pass

    # Execute & Check
    with pytest.raises(Exception):
        _ = ToDictInterfaceFailImplementation()


def test_list_to_dict():
    # Prepare
    class ToDictImplementation(ToDictInterface):
        def __init__(self, value: str):
            self._value = value

        def to_dict(self) -> dict:
            return {
                "value": self._value
            }

    COUNT = 10
    items = [
        ToDictImplementation(f"value-{i}")
        for i in range(0, COUNT)
    ]

    # Execute
    items_dict_list = list_to_dict(items)

    # Check
    assert isinstance(items_dict_list, list)
    assert any(isinstance(item, dict) for item in items_dict_list)


def test_to_dict_factory():
    # Prepare
    data = {
        "id": ObjectId(),
        "name": "name",
        "data": {
            "str": "value",
            "int": 5,
            "float": 1.0,
            "list": [1.0],
            "tuple": (1.0, 2.0),
        }
    }

    # Execute
    result = to_dict_factory(data.items())

    # Check
    assert isinstance(result.get("id"), str)
    assert isinstance(result.get("name"), str)
    assert isinstance(result.get("data"), dict)
    assert isinstance(result.get("data", {}).get("str"), str)
    assert isinstance(result.get("data", {}).get("int"), int)
    assert isinstance(result.get("data", {}).get("float"), float)
    assert isinstance(result.get("data", {}).get("list"), list)
    assert isinstance(result.get("data", {}).get("tuple"), tuple)
