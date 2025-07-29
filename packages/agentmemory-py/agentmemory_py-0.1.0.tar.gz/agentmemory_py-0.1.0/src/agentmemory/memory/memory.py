from agentmemory.connection.connection import AgentMemoryConnection
from agentmemory.memory.conversations import (
    Conversations, ConversationItems
)
from agentmemory.memory.personas import Personas
from agentmemory.memory.workflows import (
    Workflows, WorkflowSteps
)
from agentmemory.memory.cache import Cache, AutoCache


class AgentMemory:
    def __init__(
        self,
        name: str,
        con: AgentMemoryConnection,
        auto_caching: bool = True
    ):
        self._name = name
        self._con = con
        self._cache = Cache(con)

        auto_cache = AutoCache(
            self._cache,
            use_auto_caching=auto_caching
        )
        self._conversations = Conversations(
            con, cache=auto_cache
        )
        self._conversation_items = ConversationItems(
            con, cache=auto_cache
        )
        self._personas = Personas(
            con, cache=auto_cache
        )
        self._workflows = Workflows(
            con, cache=auto_cache
        )
        self._workflow_steps = WorkflowSteps(
            con, cache=auto_cache
        )

    @property
    def name(self) -> str:
        return self._name

    @property
    def con(self) -> AgentMemoryConnection:
        return self._con

    @property
    def cache(self) -> Cache:
        return self._cache

    @property
    def conversations(self) -> Conversations:
        return self._conversations

    @property
    def conversation_items(self) -> ConversationItems:
        return self._conversation_items

    @property
    def personas(self) -> Personas:
        return self._personas

    @property
    def workflows(self) -> Workflows:
        return self._workflows

    @property
    def workflow_steps(self) -> WorkflowSteps:
        return self._workflow_steps
