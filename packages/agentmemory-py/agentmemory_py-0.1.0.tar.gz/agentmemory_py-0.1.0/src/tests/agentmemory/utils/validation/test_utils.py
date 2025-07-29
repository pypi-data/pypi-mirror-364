from agentmemory.utils.validation.utils import is_valid_limit


def test_is_valid_limit():
    # Prepare & Execute & Check

    # Check valid integer limits
    assert is_valid_limit(1)
    assert is_valid_limit(10)
    assert is_valid_limit(100)

    # Check invalid limits (None, zero, negative, float, non-integer types)
    assert not is_valid_limit(None)
    assert not is_valid_limit(0)
    assert not is_valid_limit(-1)
    assert not is_valid_limit(1.5)
    assert not is_valid_limit([])
