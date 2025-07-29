from abc import ABC, abstractmethod
from typing import Any, Optional, Union, List


class ShorttermMemoryInterface(ABC):
    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        pass

    @abstractmethod
    def set(self, key: str, value: Any, ex: int) -> None:
        pass

    @abstractmethod
    def clear(self, pattern: Union[str, List[str]]) -> None:
        pass

    @abstractmethod
    def keys(self, pattern: str) -> List[str]:
        pass
