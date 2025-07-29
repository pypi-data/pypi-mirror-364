import json
from typing import Any, Union, List
from redis.client import Redis
from agentmemory.connection.shortterm.interface import ShorttermMemoryInterface


class RedisConnection(ShorttermMemoryInterface):
    def __init__(
        self,
        host: str,
        port: str = "6379",
        db: int = 0,
        password: str = None
    ):
        self._client = Redis(
            host=host,
            port=port,
            db=db,
            password=password
        )

    def get(self, key: str) -> Union[Any, None]:
        value_str = self._client.get(key)
        if value_str is None:
            return None
        value = json.loads(value_str)
        print("FROM CACHE:", value)
        return value

    def set(self, key: str, value: dict, ex: int) -> None:
        value_str = json.dumps(value)
        self._client.set(key, value_str, ex=ex)

    def clear(self, pattern: Union[str, List[str]]) -> None:
        patterns = [pattern] if isinstance(pattern, str) else pattern
        if not patterns:
            return

        seen_keys = set()
        pipe = self._client.pipeline()
        batch_size = 1000
        batch_count = 0

        for p in patterns:
            for key in self._client.scan_iter(match=p, count=batch_size):
                if key not in seen_keys:
                    seen_keys.add(key)
                    pipe.delete(key)
                    batch_count += 1
                    if batch_count >= batch_size:
                        pipe.execute()
                        batch_count = 0

        if batch_count > 0:
            pipe.execute()

        if seen_keys:
            print("CLEAR KEYS:", list(seen_keys), len(patterns))

    def keys(self, pattern: str) -> List[str]:
        return [
            key.decode("utf-8") if isinstance(key, bytes) else key
            for key in self._client.scan_iter(match=pattern)
        ]
