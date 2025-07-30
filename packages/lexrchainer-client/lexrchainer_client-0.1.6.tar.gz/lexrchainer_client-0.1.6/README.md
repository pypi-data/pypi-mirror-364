# LexrChainer Client

A Python client library for interacting with the LexrChainer API.

## Installation

```bash
pip install lexrchainer-client
```

## Configuration

Configure the client using environment variables:

```bash
# API Key authentication
LEXRCHAINER_API_KEY=your_api_key

# Or JWT token authentication
LEXRCHAINER_JWT_TOKEN=your_jwt_token

# API URL (default: http://localhost:8000)
LEXRCHAINER_API_URL=http://your-api-url
```

## Usage

### 1. Agent Builder Interface

#### Creating a Single Agent

```python
from lexrchainer.client import AgentBuilder

# Create an agent with basic configuration
agent = (AgentBuilder("Simple Assistant")
    .with_model("gpt-4")
    .with_system_prompt("You are a helpful assistant")
    .with_description("A simple assistant for basic tasks")
    .create_agent())

# Send a message to the agent
response = agent.send_message("Hello, how are you?")
```

#### Advanced Agent Configuration

```python
agent = (AgentBuilder("Advanced Assistant")
    .with_model("gpt-4", temperature=0.7, max_tokens=1000)  # Model with parameters
    .with_system_prompt("You are a helpful assistant")
    .with_description("An advanced assistant with multiple tools")
    .with_tool("search")  # Add a tool
    .with_tool("calculator", credentials={"api_key": "your_key"})  # Add a tool with credentials
    .with_static_meta({"version": "1.0", "category": "general"})  # Add static metadata
    .create_agent())
```

#### Custom Steps Configuration

```python
agent = (AgentBuilder("Step-Based Assistant")
    .with_model("gpt-4")
    .add_step(
        name="Research Step",
        prompt="Research the given topic thoroughly.",
        type="HIDDEN_TURN_USER",
        flow="TO_USER",
        flow_type="AT_ONCE",
        tool_use=True
    )
    .add_step(
        name="Summary Step",
        prompt="Summarize the research findings.",
        flow_state="CONTINUE",
        response_treatment="APPEND"
    )
    .create_agent())
```

#### Managing Existing Agents

```python
# Load an existing agent
agent = AgentBuilder("Existing Assistant").load_agent(agent_id="agent_123", conversation_id="conv_456")

# Update an existing agent
updated_agent = (AgentBuilder("Updated Assistant")
    .with_model("gpt-4")
    .with_system_prompt("New system prompt")
    .update_agent(agent_id="agent_123"))

# Get agent conversations
conversations = agent.get_agent_conversations(medium="WHATSAPP")

# Get all available agents
agents = agent.get_agents()
```

#### Creating Multiple Agents

```python
from lexrchainer.client import MultiAgentBuilder

# Create multiple agents
multi_agent = MultiAgentBuilder()

# Configure first agent
assistant = multi_agent.add_agent("Assistant")
assistant.with_model("gpt-4").with_system_prompt("You are a helpful assistant")

# Configure second agent
expert = multi_agent.add_agent("Expert")
expert.with_model("gpt-4").with_system_prompt("You are an expert in your field")

# Create all agents and start conversation
agents = multi_agent.create_agents()

# Send a message to all agents
responses = agents.send_message("Hello everyone!")
```

### 2. Conversation API

```python
from lexrchainer.client import ClientInterface

client = ClientInterface()

# Create a conversation
conversation = client.create_conversation({
    "medium": "WHATSAPP",
    "members": [...],
    "turn_type": "SEQUENTIAL",
    "iteration_end_criteria": "ALL_TURNS_DONE"
})

# Send a message
response = client.send_message(
    conversation_id="conv_123",
    messages=[...],
    streaming=True
)

# Add/remove members
client.add_conversation_member("conv_123", "user_456", "ACTIVE_PARTICIPATION")
client.remove_conversation_member("conv_123", "user_456")

# Get conversation messages
messages = client.get_conversation_messages("conv_123")

# Send message to specific agent
response = client.send_message_to_agent("agent_name", {
    "messages": [...],
    "streaming": True
})

# Send message to public agent
response = client.send_public_agent_message("public_agent", {
    "messages": [...],
    "streaming": True
})
```

### 3. User API

```python
from lexrchainer.client import ClientInterface

client = ClientInterface()

# Create a user
user = client.create_user({
    "username": "john_doe",
    "email": "john@example.com",
    "phone": "+1234567890",
    "user_type": "HUMAN"
})

# Get user details
user = client.get_user("user_123")

# Update user
updated_user = client.update_user("user_123", {
    "email": "new_email@example.com"
})

# Delete user
client.delete_user("user_123")

# List users
users = client.list_users(skip=0, limit=100)

# Get current user
current_user = client.get_current_user()
```

### 4. Organization API

```python
from lexrchainer.client import ClientInterface

client = ClientInterface()

# Create organization
org = client.create_organization({
    "name": "My Organization"
})

# Update organization
updated_org = client.update_organization("org_123", {
    "name": "Updated Organization Name"
})
```

### 5. Workspace API

```python
from lexrchainer.client import ClientInterface

client = ClientInterface()

# Create workspace
workspace = client.create_workspace({
    "name": "My Workspace",
    "description": "A workspace for collaboration",
    "is_private": True
})

# Get workspace
workspace = client.get_workspace("workspace_123")

# Update workspace
updated_workspace = client.update_workspace("workspace_123", {
    "name": "Updated Workspace Name"
})

# Delete workspace
client.delete_workspace("workspace_123")

# List workspaces
workspaces = client.list_workspaces(skip=0, limit=100)

# Manage workspace members
members = client.list_workspace_members("workspace_123")
client.add_workspace_member("workspace_123", {
    "user_id": "user_456",
    "role": "member"
})
client.remove_workspace_member("workspace_123", "user_456")
```

### 6. Chain API

```python
from lexrchainer.client import ClientInterface

client = ClientInterface()

# Create chain
chain = client.create_chain({
    "name": "My Chain",
    "description": "A custom chain",
    "json_content": {...}
})

# Get chain
chain = client.get_chain("chain_123")

# Update chain
updated_chain = client.update_chain("chain_123", {
    "description": "Updated description"
})

# Delete chain
client.delete_chain("chain_123")

# List chains
chains = client.list_chains(skip=0, limit=100)

# Trigger chain execution
result = client.trigger_chain("chain_123", {
    "message": "Hello",
    "meta_data": {...}
})

# Schedule chain execution
schedule = client.schedule_chain("chain_123", {
    "cron": "0 0 * * *",
    "message": "Scheduled message"
})
```

## Features

- Simple and intuitive API
- Support for single and multi-agent conversations
- Advanced tool integration with credential support
- Custom step configuration with flow control
- Static metadata support
- Agent management (create, update, load)
- Streaming responses
- Authentication via API key or JWT token
- Error handling and validation
- Complete coverage of all API endpoints
- Type hints and documentation

## License

MIT License 