# AgentMemory Package

[![CI](https://github.com/enricogoerlitz/agentmemory-py/actions/workflows/ci.yml/badge.svg)](https://github.com/enricogoerlitz/agentmemory-py/actions/workflows/ci.yml)
[![release](https://github.com/enricogoerlitz/agentmemory-py/actions/workflows/release.yml/badge.svg)](https://github.com/enricogoerlitz/agentmemory-py/actions/workflows/release.yml)

## Description

AgentMemory is a Python package for managing agent memory structures in AI applications. It provides a flexible data model for long-term and short-term memory and supports storing and managing:

- **Persona**: Information and properties of an agent.
- **Conversation**: Conversations between agents and users.
- **ConversationItems**: Individual messages or actions within a conversation.
- **Workflows**: Workflows executed by agents.
- **WorkflowSteps**: Individual steps within a workflow.

Additionally, a cache system is provided for fast access and temporary storage.

## Installation

Install the package using pip or uv:

```bash
pip install agentmemory-py
# or
uv add agentmemory-py
```

## Quickstart

### Create a Memory Object

```python
from agentmemory import AgentMemory
from agentmemory.connection import AgentMemoryConnection
from agentmemory.connection.longterm import MongoDBConnection
from agentmemory.connection.shortterm import RedisConnection

con = AgentMemoryConnection(
    longterm_con=MongoDBConnection(
        mongo_uri="mongodb://localhost:27017",
        database="support-agentmemory"
    ),
    shortterm_con=RedisConnection(
        host="localhost"
    )
)

memory = AgentMemory("support-agentmemory", con=con)
```


## Manage Conversations

### Create a New Conversation

```python
from agentmemory.schema.conversations import Conversation

conversation = Conversation(
    title="New Conversation",
)

created_conversation = memory.conversations.create(conversation)
print(created_conversation)
```

### List Conversations

```python
# Get all conversations
conversations = memory.conversations.list()

# Get only 5 conversations
conversations = memory.conversations.list(limit=5)

# Filter by title
conversations = memory.conversations.list(query={"title": "title1"})
```

### Retrieve and Update a Conversation

```python
id = "<ID>"
conversation = memory.conversations.get(id)
conversation.title = "Updated Title"
memory.conversations.update(conversation)
```

### Delete a Conversation

```python
id = "<ID>"
memory.conversations.delete(id)
```


## Manage ConversationItems

```python
from agentmemory.schema.conversations import ConversationItem

item = ConversationItem(
    conversation_id="<CONVERSATION_ID>",
    role="system",
    content="Hello, how can I help?",
    data={
        "custom": "data"
    }
)

created_item = memory.conversation_items.create(item)
print(created_item)

# Get items of a conversation
items = memory.conversation_items.list_by_conversation_id("<CONVERSATION_ID>")
```


## Manage Personas

```python
from agentmemory.schema.personas import Persona

persona = Persona(
    name="<NAME>",
    role="<ROLE>",
    goals="<GOALS>",
    background="<BACKGROUND>",
    data={
        "custom": "data"
    }
)

created_persona = memory.personas.create(persona)
print(created_persona)

# Retrieve persona by name
persona = memory.personas.get_by_name("<NAME>")
```


## Manage Workflows and WorkflowSteps

```python
from agentmemory.schema.workflows import Workflow, WorkflowStep, WorkflowStatus

workflow = Workflow(
    conversation_item_id="<CONVERSATION_ITEM_ID>",
    user_query="<USER_QUERY>",
    status=WorkflowStatus.RUNNING,
    data={
        "custom": "data"
    }
)

created_workflow = memory.workflows.create(workflow)
print(created_workflow)

step = WorkflowStep(
    workflow_id=created_workflow.workflow_id,
    name="<NAME>",
    tool="<TOOL_NAME>",
    arguments={
        "arg1": "value1"
    },
    status=WorkflowStatus.SUCCESS,
    result="<RESULT>",
    logs=[],
    data={
        "custom": "data"
    }
)

created_step = memory.workflow_steps.create(step)
print(created_step)
```


## Custom Caching

The integrated cache system enables fast access to frequently used data.

```python
memory.cache.keys("*")                       # List all keys
memory.cache.get("<KEY>")                    # Get value
memory.cache.set("<KEY>", {"key": "value"})  # Set value
memory.cache.clear("<PATTERN>")              # Clear cache by pattern
```

## Tests

To run the tests:

```bash
uv run pytest
```

## License

MIT License. See [LICENSE](LICENSE) for details.
