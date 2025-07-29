import pytest

from agentmemory.utils.validation.instance import check_isinstance
from agentmemory.exc.errors import InstanceTypeError


def test_check_instance():
    # Prepare & Execute & Check

    # Check valid type assertions
    check_isinstance("str", str)
    check_isinstance(1, int)
    check_isinstance(1.5, float)
    check_isinstance({}, dict)
    check_isinstance([1.0, 2.0], list)
    check_isinstance((1.0, 2.0), tuple)

    # Check that an incorrect type raises the correct exception
    with pytest.raises(InstanceTypeError):
        check_isinstance("dict", dict)
