from agentmemory.connection.longterm.interface import (
    LongtermMemoryConnectionInterface,
)
from agentmemory.connection.shortterm.interface import (
    ShorttermMemoryInterface,
)


class AgentMemoryConnection:
    def __init__(
        self,
        longterm_con: LongtermMemoryConnectionInterface,
        shortterm_con: ShorttermMemoryInterface = None,
    ):
        self._longterm_con = longterm_con
        self._shortterm_con = shortterm_con

    @property
    def longterm(self) -> LongtermMemoryConnectionInterface:
        return self._longterm_con

    @property
    def shortterm(self) -> ShorttermMemoryInterface | None:
        return self._shortterm_con
