# LexrChainer Client Usage Examples

This document provides practical examples for using the `lexrchainer-client` to interact with the LexrChainer API. It covers agent creation, conversation management, sending messages (including streaming), error handling, and a case study for building an event planner bot.

---

## 1. Creating an Agent Using AgentBuilder (Single Agent)

```python
from lexrchainer.chain.agent_builder import AgentBuilder
from lexrchainer_client.client_interface import ValidationError

# Initialize the client (API mode by default)
# You can configure via environment variables:
#   LEXRCHAINER_API_KEY, LEXRCHAINER_JWT_TOKEN, LEXRCHAINER_API_URL

try:
    agent_builder = AgentBuilder("EventPlannerBot")
    # Add description, system prompt, model, tools, etc.
    agent_builder.with_description("Helps plan events for women.")
    agent_builder.with_model("gpt-4")  # Validates model existence
    agent_builder.with_tool("SerpTool")  # Validates tool existence
    # Create the agent and its gateway conversation
    agent_wrapper = agent_builder.create_agent()
    print(f"Agent user ID: {agent_wrapper.agent_user_id}")
    print(f"Gateway conversation ID: {agent_wrapper.conversation_id}")
except ValidationError as e:
    print(f"Validation error: {e}")
```

**Note:**
- `with_model` and `with_tool` will validate against the server's model/tool repository and raise `ValidationError` if not found.
- Always handle `ValidationError` when configuring agents.

---

## 2. Sending a Message to the Agent (Gateway Conversation)

When you use `AgentWrapper.send_message`, you are sending a message to the agent's **gateway conversation**. The sender and recipient are both the agent's user ID for direct agent messaging.

```python
# Send a message to the agent (non-streaming)
response = agent_wrapper.send_message("Hello, can you help me plan a birthday party?")
print(response)

# Send a message to the agent (streaming)
streaming_response = agent_wrapper.send_message("List some venues.", streaming=True)
# If streaming=True, you get a streaming response (see requests streaming below)

# To process streaming responses:
if hasattr(streaming_response, 'iter_lines'):
    for line in streaming_response.iter_lines(decode_unicode=True):
        if line:
            print(line)
```

---

## 3. Creating a Conversation and Adding Members

```python
from lexrchainer.api.models import CreateConversationRequest, ConversationMember
from lexrchainer.conversation.schema import ConversationMedium, ConversationTurnType, ConversationIterationEndCriteria, ConversationMemberRole

# Create a conversation with two members (user and agent)
conversation_request = CreateConversationRequest(
    medium=ConversationMedium.WEB,
    turn_type=ConversationTurnType.SEQUENTIAL,
    iteration_end_criteria=ConversationIterationEndCriteria.ALL_TURNS_DONE,
    members=[
        ConversationMember(id="<user_id>", role=ConversationMemberRole.ACTIVE_PARTICIPATION),
        ConversationMember(id="<agent_id>", role=ConversationMemberRole.ACTIVE_PARTICIPATION)
    ]
)
conversation = agent_wrapper.client.create_conversation(conversation_request)
conversation_id = conversation["conversation_id"]

# Add a new member
agent_wrapper.client.add_conversation_member(conversation_id, user_id="<new_user_id>", role="observer")
```

---

## 4. Sending Messages to a Conversation (Streaming and Non-Streaming)

### Non-Streaming Example

```python
from lexrchainer.api.models import ClientConversationMessageRequest
from lexrchainer.chain.models.responses import Message, MessageRole, MessageContent, MessageType

message = Message(
    role=MessageRole.USER,
    content=[MessageContent(type=MessageType.TEXT, text="What's the agenda?")],
    entity_id="<user_id>",
    conversation_id=conversation_id
)

request = ClientConversationMessageRequest(
    sender_id="<user_id>",
    messages=[message],
    streaming=False
)

response = agent_wrapper.client.send_conversation_message(conversation_id, request.model_dump(), streaming=False)
print(response)
```

### Streaming Example

```python
import requests
from lexrchainer.api.models import ClientConversationMessageRequest

# Prepare the message as above
request = ClientConversationMessageRequest(
    sender_id="<user_id>",
    messages=[message],
    streaming=True
)

# Use the client to get a streaming response
streaming_response = agent_wrapper.client.send_conversation_message(conversation_id, request.model_dump(), streaming=True)

# Process the streaming response using requests
for line in streaming_response.iter_lines(decode_unicode=True):
    if line:
        print(line)  # Each line is a chunk of the streaming response
```

---

## 5. Difference Between `submit_conversation_message` and `send_message`

- **`send_message`**: Sends a message and expects a response immediately (synchronous or streaming). Use this for interactive chat.
- **`submit_conversation_message`**: Submits a message for background processing. The user is **not** expecting a response in the same API call. Use this for fire-and-forget or webhook-style integrations.

```python
# Submit a message (no immediate response expected)
submit_request = {
    "sender_id": "<user_id>",
    "recepient_id": "<agent_id>",
    "messages": [message],
    "medium": "web"
}
result = agent_wrapper.client.submit_conversation_message(conversation_id, submit_request)
print(result)  # Typically just an acknowledgement
```

---

## 6. Getting Conversation Messages

```python
# Get all messages in a conversation
messages = agent_wrapper.client.get_conversation_messages(conversation_id)
for msg in messages:
    print(msg)
```

---

## 7. Using Tools (SerpTool, ScraperTool, etc) with Agents

You can add tools to your agent using `with_tool` and enable tool use by instructing the agent via the system prompt. You do **not** need to use `add_step` for tool use—just add the tool and set an appropriate system prompt.

### Adding Tools to an Agent

```python
from lexrchainer.chain.agent_builder import AgentBuilder
from lexrchainer_client.client_interface import ValidationError

try:
    agent_builder = (
        AgentBuilder("ResearchBot")
        .with_model("gpt-4o")
        .with_tool("SerpTool")  # Enables Google search
        .with_tool("ScraperTool")  # Enables website scraping
        .with_system_prompt(
            "You are a research assistant. If the user asks for information not in your knowledge, use the SerpTool to search the web. "
            "If you need to extract content from a website, use the ScraperTool. Always use tools when appropriate to provide the most accurate and up-to-date information."
        )
    )
    agent_wrapper = agent_builder.create_agent()
except ValidationError as e:
    print(f"Validation error: {e}")
```

### Tool Parameters
- **SerpTool**: `{ "query": <search string>, "limit": <number of results>, "city": <city for search> }`
- **ScraperTool**: `{ "urls": [<url1>, <url2>, ...], "user_query": <context for filtering scraped content> }`

### Example: Sending a Message that Triggers Tool Use

```python
# User asks a question that requires a web search
response = agent_wrapper.send_message("What are the latest AI trends in 2024?")
print(response)

# The agent will use SerpTool internally and return the search results in its reply.

# User asks to extract content from a specific website
response = agent_wrapper.send_message("Scrape the main points from https://www.example.com/ai-news")
print(response)

# The agent will use ScraperTool and return the extracted content.
```

### How Tool Results are Returned
- Tool results are included in the agent's reply as part of the message content.
- For SerpTool, you will get a list of search results (title, link, description).
- For ScraperTool, you will get extracted content from the specified URLs.

---

## 8. Creating an Agent with Custom Chain Steps

You can define a multi-step reasoning process for your agent using `.add_step()` on the `AgentBuilder`. Each step can have its own prompt, type, flow direction, response format, and role. This is useful for building agents that follow a structured workflow or reasoning chain.

### Example: Content Creation Agent with Multi-Step Process

```python
from lexrchainer.chain.agent_builder import AgentBuilder
from lexrchainer.chain.models.responses import MessageRole
from lexrchainer_client.client_interface import ValidationError
from lexrchainer_client.models import ChainStepType, ChainStepFlowDirection
from lexrchainer_client.config import get_settings

try:
    system_prompt = """
        You are a professional content creation assistant. You help users create high-quality, 
        engaging content for various platforms including blogs, social media, and marketing materials.
        You are creative, detail-oriented, and always strive to produce content that resonates with the target audience.
    """
    
    agent_builder = (
        AgentBuilder("ContentCreator")
        .with_model("gpt-4o")
        .with_system_prompt(system_prompt)
        .with_tool("SerpTool")  # For research
        .add_step(
            "research",
            prompt="""
                Analyze the user's content request and conduct research to gather relevant information.
                Use the SerpTool to search for current trends, statistics, and examples related to the topic.
                Focus on finding:
                - Recent statistics and data
                - Current trends in the industry
                - Successful examples of similar content
                - Target audience insights
                
                Provide a comprehensive research summary that will inform the content creation.
            """,
            tool_use=True,  # Enable tool use for this step
            type=ChainStepType.HIDDEN_TURN_USER,
            flow=ChainStepFlowDirection.TO_USER
        )
        .add_step(
            "outline",
            prompt="""
                Based on the research findings, create a detailed content outline.
                Structure the content with:
                - Compelling headline options
                - Key points to cover
                - Supporting evidence and examples
                - Call-to-action suggestions
                - SEO considerations
                
                Ensure the outline follows best practices for the specified content type and platform.
            """,
            type=ChainStepType.HIDDEN_TURN_USER,
            flow=ChainStepFlowDirection.TO_USER
        )
        .add_step(
            "content_creation",
            prompt="""
                Using the research and outline, create the final content piece.
                Write engaging, well-structured content that:
                - Captures attention from the first sentence
                - Provides valuable insights and actionable information
                - Uses appropriate tone and style for the target audience
                - Incorporates the research findings naturally
                - Includes relevant examples and statistics
                - Ends with a strong call-to-action
                
                Make the content ready for immediate use on the specified platform.
            """,
            type=ChainStepType.HIDDEN_TURN_USER,
            flow=ChainStepFlowDirection.TO_USER
        )
        .add_step(
            "optimization_suggestions",
            prompt="""
                Provide optimization suggestions for the created content.
                Include recommendations for:
                - SEO improvements
                - Social media optimization
                - Engagement enhancement
                - A/B testing ideas
                - Performance tracking metrics
                
                Format the suggestions as actionable items that can be easily implemented.
            """,
            type=ChainStepType.HIDDEN_TURN_USER,
            flow=ChainStepFlowDirection.TO_USER,
            response_format={
                "type": "object",
                "properties": {
                    "type": {"type": "string", "enum": ["optimization_suggestions"]},
                    "seo_tips": {"type": "array", "items": {"type": "string"}},
                    "social_media_tips": {"type": "array", "items": {"type": "string"}},
                    "engagement_tips": {"type": "array", "items": {"type": "string"}},
                    "testing_ideas": {"type": "array", "items": {"type": "string"}},
                    "metrics_to_track": {"type": "array", "items": {"type": "string"}}
                }
            },
            role=MessageRole.UI
        )
    )
    
    agent_wrapper = agent_builder.create_agent()
    print(f"Content Creator Agent created: {agent_wrapper.agent_user_id}")
    
    # Test the multi-step agent
    response = agent_wrapper.send_message(
        "Create a blog post about sustainable fashion trends for 2024"
    )
    print(response)
    
except ValidationError as e:
    print(f"Validation error: {e}")
```

### Example: Customer Support Agent with Escalation Steps

```python
try:
    support_agent = (
        AgentBuilder("CustomerSupport")
        .with_model("gpt-4o")
        .with_system_prompt("You are a helpful customer support agent.")
        .add_step(
            "initial_assessment",
            prompt="""
                Quickly assess the customer's issue and determine its complexity level.
                Categorize the issue as: simple, moderate, or complex.
                For simple issues, provide immediate solutions.
                For moderate/complex issues, proceed to detailed analysis.
            """,
            type=ChainStepType.HIDDEN_TURN_USER,
            flow=ChainStepFlowDirection.TO_USER
        )
        .add_step(
            "detailed_analysis",
            prompt="""
                For moderate and complex issues, conduct a thorough analysis.
                Ask clarifying questions if needed.
                Research solutions using available tools.
                Prepare a comprehensive response with step-by-step instructions.
            """,
            type=ChainStepType.HIDDEN_TURN_USER,
            flow=ChainStepFlowDirection.TO_USER,
            tool_use=True
        )
        .add_step(
            "escalation_check",
            prompt="""
                Determine if the issue requires escalation to a specialist.
                If escalation is needed, prepare a summary for the specialist.
                If not, provide final resolution steps.
            """,
            type=ChainStepType.HIDDEN_TURN_USER,
            flow=ChainStepFlowDirection.TO_USER
        )
    )
    
    support_wrapper = support_agent.create_agent()
    print(f"Support Agent created: {support_wrapper.agent_user_id}")
    
except ValidationError as e:
    print(f"Validation error: {e}")
```

**Notes:**
- Each `.add_step()` call adds a new reasoning or workflow step to the agent.
- You can specify prompts, types, flow, response formats, and roles for each step.
- Use `tool_use=True` to enable tool usage for specific steps.
- The `response_format` parameter allows you to structure the output in JSON format.
- This pattern is useful for agents that need to perform multi-stage reasoning or output structured results.
- Always handle `ValidationError` for model/tool/step validation.

---

# Case Study: Event Planner Bot for Women

## Scenario
You are building an event planning bot for women. Each user interacts with the bot (agent) via a new conversation. Messages may come from platforms like Telegram or WhatsApp.

### 1. Create the Agent

```python
from lexrchainer.chain.agent_builder import AgentBuilder
from lexrchainer.conversation.schema import ConversationMedium

agent_builder = AgentBuilder("EventPlannerBot")
# Add description, tools, etc. as needed
agent_wrapper = agent_builder.create_agent(
    medium=ConversationMedium.WHATSAPP,
    is_public=False,  # Set to True if you want the agent to be publicly accessible
    version=1  # Version number for the agent
)
```

### 2. For Each New User, Create a Conversation with the Agent

```python
from lexrchainer.api.models import CreateConversationRequest, ConversationMember
from lexrchainer.conversation.schema import ConversationMemberRole, ConversationTurnType, ConversationIterationEndCriteria, ConversationMedium

user_id = "<telegram_or_whatsapp_user_id>"
agent_id = agent_wrapper.agent_user_id

# Note: The agent creation automatically creates a gateway conversation
# For user-specific conversations, you can create additional conversations
conversation_request = CreateConversationRequest(
    medium=ConversationMedium.WHATSAPP,
    turn_type=ConversationTurnType.SEQUENTIAL,
    iteration_end_criteria=ConversationIterationEndCriteria.PERPETUAL,
    members=[
        ConversationMember(id=user_id, role=ConversationMemberRole.ACTIVE_PARTICIPATION),
        ConversationMember(id=agent_id, role=ConversationMemberRole.ACTIVE_PARTICIPATION)
    ]
)
conversation = agent_wrapper.client.create_conversation(conversation_request)
conversation_id = conversation["conversation_id"]
```

### 3. Forward User Messages from Telegram/WhatsApp to the Conversation

```python
from lexrchainer.api.models import ClientConversationMessageRequest
from lexrchainer.chain.models.responses import Message, MessageRole, MessageContent, MessageType

# When a user sends a message on Telegram/WhatsApp:
user_message = "I want to plan a baby shower."
message = Message(
    role=MessageRole.USER,
    content=[MessageContent(type=MessageType.TEXT, text=user_message)],
    entity_id=user_id,
    conversation_id=conversation_id
)

request = ClientConversationMessageRequest(
    sender_id=user_id,
    messages=[message],
    streaming=False
)

response = agent_wrapper.client.send_conversation_message(conversation_id, request.model_dump(), streaming=False)
print(response)
```

### 4. What to Store and What to Skip
- **Store:**
  - `user_id` (from Telegram/WhatsApp)
  - `conversation_id` (for mapping user to conversation)
  - Message history if you want to show chat history or for analytics
- **Skip:**
  - Raw platform payloads unless needed for audit
  - Temporary tokens or session data unless required for re-authentication

---

## Notes
- For streaming responses, use `requests` streaming patterns (`iter_lines`) as shown above.
- Always check for errors using `response.raise_for_status()` when using `requests` directly.
- Use the appropriate conversation medium (`WEB`, `WHATSAPP`, etc.) to match your integration platform.
- `with_model` and `with_tool` will raise `ValidationError` if the model/tool is not found in the repository.
- The `create_agent()` method automatically creates a gateway conversation for the agent.
- Use the `client_interface` methods for direct API calls if you need more control.
- The `medium` parameter in `create_agent()` is ignored as the API creates the gateway conversation automatically.
- Set `is_public=True` when creating agents that should be publicly accessible.

---

For more advanced usage, see the API documentation and explore the models in `lexrchainer.api.models` and `lexrchainer.chain.models.responses`. 