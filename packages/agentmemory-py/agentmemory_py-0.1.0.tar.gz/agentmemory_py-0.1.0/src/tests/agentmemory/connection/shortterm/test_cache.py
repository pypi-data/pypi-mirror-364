import pytest

from agentmemory.connection.shortterm.cache import (
    CacheRetrieveType,
    ClearCacheTransactionType,
    CacheKey,
    ClearCacheKey,
    _create_rtype,
    _create_col,
    _create_id,
    _create_query,
    _create_kwargs,
    _get_anchor_id
)
from agentmemory.connection.longterm.collections import Collection


def test_create_rtype():
    # Prepare & Execute & Check
    assert _create_rtype(CacheRetrieveType.GET) == "type:GET"
    assert _create_rtype(CacheRetrieveType.LIST) == "type:LIST"
    assert _create_rtype(CacheRetrieveType.LIST_BY_ANCHOR) == "type:LIST_BY_ANCHOR"
    assert _create_rtype(CacheRetrieveType.LIST_UNTIL_ID_FOUND) == "type:LIST_UNTIL_ID_FOUND"

    with pytest.raises(ValueError):
        _create_rtype("INVALID")


def test_create_col():
    # Prepare & Execute & Check
    assert _create_col(Collection.CONVERSATIONS) == f"col:{Collection.CONVERSATIONS.value}"
    assert _create_col(Collection.PERSONAS) == f"col:{Collection.PERSONAS.value}"

    with pytest.raises(ValueError):
        _create_col("INVALID")


def test_create_id():
    # Prepare & Execute & Check
    assert _create_id("abc123", CacheRetrieveType.GET) == "id:abc123"
    assert _create_id(("id1", "id2"), CacheRetrieveType.LIST) == "id:id1,id2"
    assert _create_id(None, CacheRetrieveType.LIST) is None

    with pytest.raises(ValueError):
        _create_id(None, CacheRetrieveType.GET)
    with pytest.raises(ValueError):
        _create_id(123, CacheRetrieveType.GET)


def test_get_anchor_id():
    # Prepare & Execute & Check
    assert _get_anchor_id("anchor") == "anchor"
    assert _get_anchor_id(("anchor", "other")) == "anchor"
    assert _get_anchor_id(["anchor", "other"]) == "anchor"

    with pytest.raises(ValueError):
        _get_anchor_id(123)
    with pytest.raises(ValueError):
        _get_anchor_id(())


def test_create_query():
    # Prepare & Execute & Check
    assert _create_query({"a": 1}) == "q:{'a': 1}"
    assert _create_query(None) is None

    with pytest.raises(ValueError):
        _create_query([1, 2, 3])


def test_create_kwargs():
    # Prepare & Execute & Check
    assert _create_kwargs({}) is None
    assert _create_kwargs({"a": 1, "b": None, "c": 2}) == "a:1;c:2"


def test_cache_key():
    # Prepare
    rtype = CacheRetrieveType.GET
    col = Collection.CONVERSATIONS
    id_val = "abc123"
    query = {"foo": "bar"}
    extra = {"x": 1, "ymca": None}

    # Execute
    cache_key = CacheKey(rtype=rtype, col=col, id=id_val, query=query, **extra)
    key_str = cache_key.key()

    # Check
    assert isinstance(key_str, str)
    assert f"type:{rtype.value}" in key_str
    assert f"col:{col.value}" in key_str
    assert f"id:{id_val}" in key_str
    assert "q:{'foo': 'bar'}" in key_str
    assert "x:1" in key_str
    assert "ymca" not in key_str  # None values should be skipped


def test_clear_cache_key_create_and_update():
    col = Collection.CONVERSATIONS
    id_val = ("id1", "id2")

    # --- Test CREATE transaction type with is_first_id_anchor=True ---
    # Prepare
    clear_key_create_anchor = ClearCacheKey(
        ttype=ClearCacheTransactionType.CREATE,
        col=col,
        id=id_val,
        is_first_id_anchor=True
    )
    # Execute
    keys_create_anchor = clear_key_create_anchor.clear_keys()

    # Check
    assert any("type:LIST" in k for k in keys_create_anchor)
    assert any("type:LIST_BY_ANCHOR" in k for k in keys_create_anchor)
    assert any("type:LIST_UNTIL_ID_FOUND" in k for k in keys_create_anchor)

    # --- Test CREATE transaction type with is_first_id_anchor=False ---
    # Prepare
    clear_key_create_no_anchor = ClearCacheKey(
        ttype=ClearCacheTransactionType.CREATE,
        col=col,
        id=id_val,
        is_first_id_anchor=False
    )
    # Execute
    keys_create_no_anchor = clear_key_create_no_anchor.clear_keys()

    # Check
    assert any("type:LIST" in k for k in keys_create_no_anchor)
    # Should NOT contain anchor-specific keys
    assert not any("type:LIST_BY_ANCHOR" in k for k in keys_create_no_anchor)
    assert not any("type:LIST_UNTIL_ID_FOUND" in k for k in keys_create_no_anchor)

    # --- Test UPDATE transaction type with is_first_id_anchor=True ---
    # Prepare
    clear_key_update_anchor = ClearCacheKey(
        ttype=ClearCacheTransactionType.UPDATE,
        col=col,
        id=id_val,
        is_first_id_anchor=True
    )
    # Execute
    keys_update_anchor = clear_key_update_anchor.clear_keys()

    # Check
    assert any("type:GET" in k for k in keys_update_anchor)
    assert any("type:LIST" in k for k in keys_update_anchor)
    assert any("type:LIST_BY_ANCHOR" in k for k in keys_update_anchor)
    assert any("type:LIST_UNTIL_ID_FOUND" in k for k in keys_update_anchor)

    # --- Test UPDATE transaction type with is_first_id_anchor=False ---
    # Prepare
    clear_key_update_no_anchor = ClearCacheKey(
        ttype=ClearCacheTransactionType.UPDATE,
        col=col,
        id=id_val,
        is_first_id_anchor=False
    )
    # Execute
    keys_update_no_anchor = clear_key_update_no_anchor.clear_keys()

    # Check
    assert any("type:GET" in k for k in keys_update_no_anchor)
    assert any("type:LIST" in k for k in keys_update_no_anchor)
    # Should NOT contain anchor-specific keys
    assert not any("type:LIST_BY_ANCHOR" in k for k in keys_update_no_anchor)
    assert not any("type:LIST_UNTIL_ID_FOUND" in k for k in keys_update_no_anchor)


def test_clear_cache_key_invalid_type():
    # Prepare & Execute & Check
    with pytest.raises(Exception):
        ClearCacheKey(ttype="INVALID", col=Collection.CONVERSATIONS, id="abc").clear_keys()
