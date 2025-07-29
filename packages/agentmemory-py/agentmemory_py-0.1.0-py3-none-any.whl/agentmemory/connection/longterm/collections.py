from enum import Enum


CONVERSATIONS = "conversations"
CONVERSATION_ITEMS = "conversation_items"
WORKFLOWS = "workflows"
WORKFLOW_STEPS = "workflow_steps"
PERSONAS = "personas"


class Collection(str, Enum):
    CONVERSATIONS = CONVERSATIONS
    CONVERSATION_ITEMS = CONVERSATION_ITEMS
    PERSONAS = PERSONAS
    WORKFLOWS = WORKFLOWS
    WORKFLOW_STEPS = WORKFLOW_STEPS
