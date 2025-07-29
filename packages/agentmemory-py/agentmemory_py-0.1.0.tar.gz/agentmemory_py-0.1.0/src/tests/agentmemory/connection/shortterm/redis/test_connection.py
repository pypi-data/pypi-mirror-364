import time

from agentmemory import AgentMemory


def test_redis_set_and_get(pymongo_cache_memory: AgentMemory):
    # Prepare
    key = "test:key:1"
    value = {"foo": "bar", "num": 42}
    expire_seconds = 5

    # Execute
    pymongo_cache_memory.cache.set(key, value, ex=expire_seconds)
    result = pymongo_cache_memory.cache.get(key)

    # Check
    assert result == value


def test_redis_get_nonexistent_key(pymongo_cache_memory: AgentMemory):
    # Prepare
    key = "test:key:nonexistent"

    # Execute
    result = pymongo_cache_memory.cache.get(key)

    # Check
    assert result is None


def test_redis_expiry(pymongo_cache_memory: AgentMemory):
    # Prepare
    key = "test:key:expire"
    value = {"foo": "expire"}
    expire_seconds = 1

    # Execute
    pymongo_cache_memory.cache.set(key, value, ex=expire_seconds)
    result = pymongo_cache_memory.cache.get(key)
    assert result == value

    # Wait for expiry
    time.sleep(expire_seconds + 1)
    expired_result = pymongo_cache_memory.cache.get(key)

    # Check
    assert expired_result is None


def test_redis_clear_and_keys(pymongo_cache_memory: AgentMemory):
    # Prepare
    key1 = "test:clear:1"
    key2 = "test:clear:2"
    value = {"foo": "clear"}
    pattern = "test:clear:*"

    pymongo_cache_memory.cache.set(key1, value, ex=10)
    pymongo_cache_memory.cache.set(key2, value, ex=10)

    # Execute
    keys_before = pymongo_cache_memory.cache.keys(pattern)
    pymongo_cache_memory.cache.clear(pattern)
    keys_after = pymongo_cache_memory.cache.keys(pattern)

    # Check
    assert key1 in keys_before
    assert key2 in keys_before
    assert key1 not in keys_after
    assert key2 not in keys_after


def test_redis_clear_with_empty_pattern(pymongo_cache_memory: AgentMemory):
    # Prepare
    # No keys should be deleted, should not raise
    pattern = []

    # Execute & Check
    pymongo_cache_memory.cache.clear(pattern)
    # No assertion needed, just ensure no exception is raised


def test_redis_keys_decoding(pymongo_cache_memory: AgentMemory):
    # Prepare
    key = "test:decode:1"
    value = {"foo": "decode"}
    pattern = "test:decode:*"

    pymongo_cache_memory.cache.set(key, value, ex=10)

    # Execute
    keys = pymongo_cache_memory.cache.keys(pattern)

    # Check
    # All returned keys should be strings, not bytes
    assert all(isinstance(k, str) for k in keys)
    assert key in keys

    # Cleanup
    pymongo_cache_memory.cache.clear(pattern)
