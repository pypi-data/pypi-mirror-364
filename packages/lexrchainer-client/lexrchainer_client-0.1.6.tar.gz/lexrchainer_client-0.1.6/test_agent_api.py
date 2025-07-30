import os
from lexrchainer_client import ClientInterface, AgentBuilder, AgentWrapper
from lexrchainer_client.models import ChainMeta, ModelParams, AgentCreate, UserType, ChainStepType, ChainStepFlowDirection, MessageRole
from dotenv import load_dotenv
import uuid
import traceback
import json
from lexrchainer_client.config import get_settings

def setup_client():
    # Set API key for authentication
    os.environ["LEXRCHAINER_API_KEY"] = "BpXlQI4iLYNI95KLKi9oPhWyVTZbfTHf-fUQ95duJGI"
    # Optionally set API URL if needed, e.g.:
    os.environ["LEXRCHAINER_API_URL"] = "http://localhost:8000"
    #os.environ["LEXRCHAINER_API_URL"] = "http://lexr-api-lb-492309865.us-east-1.elb.amazonaws.com"
    os.environ["LEXRCHAINER_API_KEY"] = "master-test-api-key"
    load_dotenv()
    return ClientInterface()

def make_minimal_chain_meta():
    return ChainMeta(
        id=str(uuid.uuid4()),
        name="test_agent_chain_" + str(uuid.uuid4())[:8],
        description="Test chain for agent CRUD",
        version="1.0.0",
        default_system_prompt="You are a test agent.",
        static_meta={},
        tools=[],
        models=[],
        default_model_params=ModelParams(
            model="gpt-4o",
            max_tokens=100,
            temperature=0.5,
            top_p=0.9,
            top_k=10
        )
    )

def test_create_agent(client):
    print("\n--- test_create_agent ---")
    chain_meta = make_minimal_chain_meta()
    agent_req = AgentCreate(agent_name="TestAgentAPI", config=chain_meta)
    try:
        # The API expects a dict, not a pydantic object
        resp = client.create_user({
            "username": agent_req.agent_name.lower(),
            "email": agent_req.agent_name.lower() + "@lexr.ai",
            "phone": "9999999999",
            "user_type": UserType.AGENT.value,
            "chain_config": {"json_content": json.dumps(agent_req.config.model_dump())}
        })
        print("Agent created:", resp)
        return resp
    except Exception as e:
        print("Error creating agent:", e)
        traceback.print_exc()
        return None

def test_list_agents(client):
    print("\n--- test_list_agents ---")
    try:
        agents = client.get_agents()
        print(f"Found {len(agents)} agents.")
        for a in agents:
            print(a)
        return agents
    except Exception as e:
        print("Error listing agents:", e)
        traceback.print_exc()
        return None

def test_update_agent(client, agent_id, new_name):
    print("\n--- test_update_agent ---")
    chain_meta = make_minimal_chain_meta()
    agent_update = {
        "agent_name": new_name,
        "config": chain_meta.model_dump()
    }
    try:
        resp = client.update_agent(agent_id, agent_update)
        print("Agent updated:", resp)
        return resp
    except Exception as e:
        print("Error updating agent:", e)
        traceback.print_exc()
        return None

def test_delete_agent(client, agent_id):
    print("\n--- test_delete_agent ---")
    try:
        client.delete_user(agent_id)
        print(f"Agent {agent_id} deleted.")
        return True
    except Exception as e:
        print("Error deleting agent:", e)
        traceback.print_exc()
        return False

def test_invalid_agent_creation(client):
    print("\n--- test_invalid_agent_creation (missing name) ---")
    try:
        chain_meta = make_minimal_chain_meta()
        # Missing agent_name
        agent_req = {"config": chain_meta.model_dump()}
        resp = client.create_user(agent_req)
        print("Unexpected success:", resp)
    except Exception as e:
        print("Expected error (missing name):", e)
    print("\n--- test_invalid_agent_creation (missing config) ---")
    try:
        agent_req = {"username": "bad_agent", "user_type": UserType.AGENT.value}
        resp = client.create_user(agent_req)
        print("Unexpected success:", resp)
    except Exception as e:
        print("Expected error (missing config):", e)

def test_agent_builder(agent_name: str, msg: str, streaming: bool = False):
    try:
        '''
        .with_system_prompt("""You are a VP of marketing. Your job is to manage the marketing team of agents and create a marketing strategy for a new Legal AI product. 
                            Always use SequentialThinking tool to think step by step to create the execution plan.
                            Always use TaskManagerTool to create tasks and assign them to yourself or other agents. Create separate conversations with agents to give them tasks and get their outcomes.
                            Always provide tools to the agents to use. This will empower them to do more and be more productive.

                            You have following tools at your disposal to provide to the agents: SerpTool, ScraperTool, SequentialThinking, TaskManagerTool, AgentConversationTool.
                            "SerpTool" to search web and "ScraperTool" to get Website content to answer the user's question. Make sure you visit the website to get the latest information. 
                            "AgentConversationTool" to create a new agents, conversations and send messages to an existing agent or conversation. Use this to create teams of agents to discuss and collaborate.
                            "LexrIndex" to search for caselaw, statutes, rules and regulations and other legal documents.
                                """)
        '''
        system_prompt = "You are a helpful assistant. Use SerpTool to search the web and get the latest information."
        system_prompt = """
            You are LexR, an expert and helpful AI lawyer for India, developed by Aethon Legal Tech (India).
            You assume India as the default jurisdiction for all queries you get.
            You are highly technical legal researcher who has the ability to analyse a legal situation using minimum information available.
            Your professional background has given you a unique perspective on people's issues, blending legal expertise with a deep understanding of human nature.
            Your key expertise is that you can converse in any language.
            You mirror the user's writing style to build rapport and make them comfortable.
            Keep the responses concise and precise.
            Always use LexrIndex to search for caselaw, statutes, rules and regulations and other legal documents.
            """
        agent = (AgentBuilder(agent_name)
            .with_model("lexr/gpt-4o")
            #.with_system_prompt("You are a helpful assistant. Use AgentConversationTool to create a new agents, conversations and send messages to an existing agent or conversation. Use this to create teams of agents to discuss and collaborate.")
            .with_system_prompt(system_prompt)
            #.with_tool("AgentConversationTool")
            .with_tool("LexrIndex")
            #.with_tool("SerpTool")
            #.with_tool("ScraperTool")
            .add_step("step1", system_prompt="""
                        You are LexR, an expert and helpful AI lawyer for India jurisdiction, developed by Aethon Legal Tech (India).
                        You are highly technical legal researcher who has the ability to analyse a legal situation using minimum information available.
                        Your professional background has given you a unique perspective on people's issues, blending legal expertise with a deep understanding of human nature.
                        You mirror the user's writing style to build rapport and make them comfortable.
                        You integrate reasoning seamlessly, staying neutral, concise (<300 words), including statutes/caselaw, offering specific legal remedies, avoiding repetition, and suggesting follow-up queries..
                       """, prompt=
                       """
                        Respond to users latest query. If the user's query is legal in nature, use LexrIndex tool to get the latest legal information if necessary.
                        Follow below steps to conduct the reasoning:
                        Use *ONLY* the references provided by LexrIndex, SerpTool and ScraperTool tools. Do not use your knowledge.
                        - List the references relevant to the the specific requirement or concern of the user query and mention the reason why each of the reference is relevant.
                        - Based on the references filtered as relevant, deliberate to construct a chain of reasoning that stitches together the strongest thoughts in a natural order as follows:
                        -- Apply the law precisely - Accurately explain how statutes, case law and other information from google govern the facts and how they apply to the legal issues.
                        -- Mention the statutes and caselaw applied.
                        -- Analogize and distinguish - Compare facts to favourable precedent. Distinguish unfavourable precedent.
                        -- Define terms - Define legal terms and acronyms on first use.
                        -- Weave in facts chronologically - Integrate facts seamlessly rather than in isolated chunks.
                        -- Cite all the sources here - Cite statutes, cases, and articles to substantiate the analysis.
                        -- Include Citations from within the references if necessary.
                        -- The citations should use \"Standard Indian Legal Citation\", should be datewise descending, prefer supreme court precedents higher and deduplicated.                       
                        -- Address user's concerns directly first and then provide the reasoning.
                        -- If user's query is not clear, ask for more details.
                        -- Always provide ALL the references used in the response so that user can verify the information.
                       """, type=ChainStepType(get_settings().default_step_type), flow=ChainStepFlowDirection(get_settings().default_flow_direction))
            .add_step("step2", prompt=
                       """
                        Generate a list of 4 suggested follow up queries to the user's query.
                       """, type=ChainStepType(get_settings().default_step_type), flow=ChainStepFlowDirection(get_settings().default_flow_direction),
                       response_format={
                            "type": "object",
                            "properties": {
                                "type": {"type": "string", "enum": ["suggested_queries"]},
                                "queries": {"type": "array", "items": {"type": "string"}}
                            }
                        },
                        role=MessageRole.UI
                       )
            .create_agent(is_public=True))
        print(f"Agent created: {agent_name}, Agent ID: {agent.agent_user_id}")
        response = None
        '''
        print("Sending message to agent...")
        response = agent.send_message(msg, streaming=streaming)
        if streaming:
            print("Streaming response:")
            for chunk in response:
                print(chunk, end="", flush=True)
            print()
        else:
            print("Agent response:", response)
        #print(f"Final Message:\n{json.loads(response[-1].replace('data: ', ''))['content']}")
        '''
        return agent, response
    except Exception as e:
        traceback.print_exc()
        print("Error testing agent:", e)
        return None, None

def test_webhook_agent(agent_name: str, msg: str):
    try:
        system_prompt = "You are a helpful assistant. Use DummyAsyncJokeTool to get a random joke."
        agent = (AgentBuilder(agent_name)
            .with_model("lexr/gpt-4o")
            .with_system_prompt(system_prompt)
            .with_tool("DummyAsyncJokeTool")
            .create_agent())
        print(f"Agent created: {agent_name}, Agent ID: {agent.agent_user_id}")
        response = None
        print("Sending message to agent...")
        response = agent.send_message(msg)
        print("Agent response:", response)
        return agent, response
    except Exception as e:
        traceback.print_exc()
        print("Error testing agent:", e)
        return None, None
    
def test_agent_conversation(agent: AgentWrapper):
    try:
        response1 = agent.send_message("What is your name?")
        print("First response:", response1)
        response2 = agent.send_message("Can you help me with a task?")
        print("Second response:", response2)
        return response1, response2
    except Exception as e:
        print("Error in conversation test:", e)
        return None, None

def test_agent_memory(agent: AgentWrapper):
    try:
        response = agent.send_message("Can you summarize our previous conversation?")
        print("Memory test response:", response)
        return response
    except Exception as e:
        print("Error in memory test:", e)
        return None

def test_agent_capabilities(agent: AgentWrapper):
    try:
        code_response = agent.send_message("Write a simple Python function to calculate factorial")
        print("Code generation response:", code_response)
        explain_response = agent.send_message("Explain how a binary search works")
        print("Explanation response:", explain_response)
        return code_response, explain_response
    except Exception as e:
        print("Error in capabilities test:", e)
        return None, None

def test_agent_chain_operations(agent: AgentWrapper):
    try:
        list_response = agent.send_message("Generate a list of 5 random numbers between 1 and 100")
        print("List generation response:", list_response)
        sort_response = agent.send_message("Now sort those numbers in ascending order")
        print("Sorting response:", sort_response)
        stats_response = agent.send_message("Calculate the mean and median of these sorted numbers")
        print("Statistics response:", stats_response)
        return list_response, sort_response, stats_response
    except Exception as e:
        print("Error in chain operations test:", e)
        return None, None, None

def test_invalid_agent_creation():
    try:
        print("\n--- test_invalid_agent_creation (missing model) ---")
        agent = (AgentBuilder("BadAgent")
            .with_system_prompt("Missing model should fail.")
            .create_agent())
        print("Unexpected success:", agent)
    except Exception as e:
        print("Expected error (missing model):", e)
    try:
        print("\n--- test_invalid_agent_creation (invalid tool) ---")
        agent = (AgentBuilder("BadAgent2")
            .with_model("lexr/gpt-4o")
            .with_tool("NonExistentTool")
            .create_agent())
        print("Unexpected success:", agent)
    except Exception as e:
        print("Expected error (invalid tool):", e)

def main():
    load_dotenv()
    client = setup_client()
    # Create agent
    #agent = test_create_agent(client)
    #agent_id = agent["id"] if agent and "id" in agent else None
    #agent, initial_response = test_agent_builder("test_agent_" + str(uuid.uuid4())[:8], "Design a marketing strategy for a new Legal AI product. Create agents with varied backgrounds and tool access to discuss and collaborate on the strategy. After detailed research, create a report in MD format.")
    #agent, initial_response = test_agent_builder("test_agent_" + str(uuid.uuid4())[:8], "Create multiple agents of different backgrounds and expertise. Always provide them with tools (SerpTool, ScraperTool, SequentialThinking). Analyse the market size for an AI based event planning app, targeting women aged 20-40 in India who purchase online regularly. Create multiple conversations with these agents to discuss on different topics. Keep asking agents to provide more details and perspectives. Your job is to make sure that the topic is discussed in detail and a lot of perspectives are considered. Instruct agents to use tools to do their job. Encourage them to provide new perspectives and insights by conducting research. Create a comprehensive report with detailed numbers, reasoning and citations in MD format.")
    agent, initial_response = test_agent_builder("test_agent_" + str(uuid.uuid4())[:8], "What is your name?", streaming=True)
    #agent, initial_response = test_webhook_agent("test_webhook_agent_" + str(uuid.uuid4())[:8], "Get a random joke")
    #agent, initial_response = test_agent_builder("test_agent_" + str(uuid.uuid4())[:8], "Find a good pizza place in Mumbai")
    '''
    if agent:
        test_agent_conversation(agent)
        test_agent_memory(agent)
        test_agent_capabilities(agent)
        test_agent_chain_operations(agent)
    test_invalid_agent_creation()

    
    # List agents
    test_list_agents(client)
    # Update agent
    if agent_id:
        test_update_agent(client, agent_id, "TestAgentAPIUpdated")
    # Invalid agent creation
    test_invalid_agent_creation(client)
    # Delete agent
    if agent_id:
        test_delete_agent(client, agent_id)
    '''
if __name__ == "__main__":
    main()
