from abc import ABC, abstractmethod
from typing import List, Optional, Dict

from agentmemory.schema.conversations import Conversation, ConversationItem
from agentmemory.schema.personas import Persona
from agentmemory.schema.workflows import Workflow, WorkflowStep


class LongtermMemoryConversationsSchemaInterface(ABC):
    @abstractmethod
    def get(self, conversation_id: str) -> Conversation:
        pass

    @abstractmethod
    def list(
        self,
        query: Optional[Dict] = None,
        limit: Optional[int] = None
    ) -> List[Conversation]:
        pass

    @abstractmethod
    def create(self, conversation: Conversation) -> Conversation:
        pass

    @abstractmethod
    def update(
        self,
        conversation_id: str,
        update_data: Dict
    ) -> None:
        pass

    @abstractmethod
    def delete(
        self,
        conversation_id: str,
        cascade: bool
    ) -> None:
        pass


class LongtermMemoryConversationItemsSchemaInterface(ABC):
    @abstractmethod
    def get(
        self,
        conversation_id: str,
        item_id: str
    ) -> ConversationItem:
        pass

    @abstractmethod
    def list(
        self,
        query: Optional[Dict] = None,
        limit: Optional[int] = None
    ) -> List[ConversationItem]:
        pass

    @abstractmethod
    def list_by_conversation_id(
        self,
        conversation_id: str,
        query: Optional[Dict] = None,
        limit: Optional[int] = None
    ) -> List[ConversationItem]:
        pass

    @abstractmethod
    def list_until_id_found(
        self,
        conversation_id: str,
        item_id: str,
        limit: Optional[int] = None
    ) -> List[ConversationItem]:
        pass

    @abstractmethod
    def create(self, item: ConversationItem) -> ConversationItem:
        pass

    @abstractmethod
    def update(
        self,
        conversation_id: str,
        item_id: str,
        update_data: Dict
    ) -> None:
        pass

    @abstractmethod
    def delete(
        self,
        conversation_id: str,
        item_id: str
    ) -> None:
        pass


class LongtermMemoryPersonasSchemaInterface(ABC):
    @abstractmethod
    def get(self, persona_id: str) -> Persona:
        pass

    @abstractmethod
    def get_by_name(self, name: str) -> Persona:
        pass

    @abstractmethod
    def list(
        self,
        query: Optional[Dict] = None,
        limit: Optional[int] = None
    ) -> List[Persona]:
        pass

    @abstractmethod
    def create(self, persona: Persona) -> Persona:
        pass

    @abstractmethod
    def update(
        self,
        persona_id: str,
        update_data: Dict
    ) -> None:
        pass

    @abstractmethod
    def delete(self, persona_id: str) -> None:
        pass


class LongtermMemoryWorkflowsSchemaInterface(ABC):
    @abstractmethod
    def get(self, workflow_id: str) -> Workflow:
        pass

    @abstractmethod
    def list(
        self,
        query: Optional[Dict] = None,
        limit: Optional[int] = None
    ) -> List[Workflow]:
        pass

    @abstractmethod
    def list_by_conversation_item_id(
        self,
        conversation_item_id: str,
        query: Optional[Dict] = None,
        limit: Optional[int] = None
    ) -> List[Workflow]:
        pass

    @abstractmethod
    def create(self, workflow: Workflow) -> Workflow:
        pass

    @abstractmethod
    def update(
        self,
        workflow_id: str,
        update_data: Dict
    ) -> None:
        pass

    @abstractmethod
    def delete(
        self,
        workflow_id: str,
        cascade: bool
    ) -> None:
        pass


class LongtermMemoryWorkflowStepsSchemaInterface(ABC):
    @abstractmethod
    def get(
        self,
        workflow_id: str,
        step_id: str
    ) -> WorkflowStep:
        pass

    @abstractmethod
    def list(
        self,
        query: Optional[Dict] = None,
        limit: Optional[int] = None
    ) -> List[WorkflowStep]:
        pass

    @abstractmethod
    def list_by_workflow_id(
        self,
        workflow_id: str,
        query: Optional[Dict] = None,
        limit: Optional[int] = None
    ) -> List[WorkflowStep]:
        pass

    @abstractmethod
    def create(self, step: WorkflowStep) -> WorkflowStep:
        pass

    @abstractmethod
    def update(
        self,
        workflow_id: str,
        step_id: str,
        update_data: Dict
    ) -> WorkflowStep:
        pass

    @abstractmethod
    def delete(
        self,
        workflow_id: str,
        step_id: str
    ) -> None:
        pass


class LongtermMemoryConnectionInterface(ABC):
    @abstractmethod
    def conversations(
        self
    ) -> LongtermMemoryConversationsSchemaInterface:
        pass

    @abstractmethod
    def conversation_items(
        self
    ) -> LongtermMemoryConversationItemsSchemaInterface:
        pass

    @abstractmethod
    def personas(
        self
    ) -> LongtermMemoryPersonasSchemaInterface:
        pass

    @abstractmethod
    def workflows(
        self
    ) -> LongtermMemoryWorkflowsSchemaInterface:
        pass

    @abstractmethod
    def workflow_steps(
        self
    ) -> LongtermMemoryWorkflowStepsSchemaInterface:
        pass
