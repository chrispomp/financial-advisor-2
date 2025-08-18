# citi_wealth_advisor_agent/agent.py

from google.adk.agents import Agent
from google.adk.tools import google_search, agent_tool

# Import the tools from your tools.py file
from . import tools

# --- Specialist Agents ---
model = "gemini-2.5-flash-lite"

profile_agent = Agent(
    name="ClientProfileAgent",
    model=model,
    description="Use this agent to retrieve information about your wealth management client. It can access information on a client's personal and financial situation, including their preferred name, age, family, occupation, and residence. The tool also provides a summary of their financial holdings, such as net worth, cash, and investments, as well as their stated financial goals. The agent can use this information to answer questions about a client's relationship with Citi, including how long they've been a client, their relationship manager, and specific opportunities to grow their wealth with Citi. This is the primary source for any client-related questions.",
    tools=[
        tools.get_client_profile,
        tools.get_preferred_name,
        tools.get_client_net_worth,
        tools.get_client_goals,
        tools.get_client_dependents
    ]
)

guidance_agent = Agent(
    name="CitiGuidanceAgent",
    model=model,
    description="Use this agent to retrieve the latest investment strategy and market outlook from Citi's Chief Investment Officer (CIO). The agent can answer questions about the official view on global markets, including key investment themes and the general market outlook. This information is the basis for all investment recommendations and market commentary. The agent should be aware that this is general guidance, not a personalized recommendation.",
    tools=[tools.get_citi_guidance]
)

search_agent = Agent(
    name="GoogleSearchAgent",
    model=model,
    description="Use this agent for all general knowledge questions, such as current events, market news, or any information not found in the client's profile.",
    tools=[google_search]
)

# --- Root Agent ---
detailed_instructions = """
You are a friendly, professional, and concise AI Wealth Advisor for your client, Chris Evans.

**Your Primary Directive:** You must follow these operational rules precisely.

**Operational Logic & Tools**
1.  **First Turn Protocol:** On the very first turn of a new conversation, your first action MUST be to call the `ClientProfileAgent` and use the `get_preferred_name` tool to learn the client's `preferred_name`. After the tool call, you MUST begin your response with "Hello, [preferred_name]," and then immediately answer the user's original question in the same sentence or paragraph.
2.  **Subsequent Turns:** After the first turn, do not repeat the greeting. Proceed directly to answering the user's questions.
3.  **Use `CitiGuidanceAgent` for Investment Advice:** For any questions about investment strategy, market outlook, or asset allocation, you MUST use the `CitiGuidanceAgent`.
4.  **Use `ClientProfileAgent` for Client Questions:** For any questions about Chris's personal finances, goals, or existing holdings, you MUST use the `ClientProfileAgent`.
5.  **Use `GoogleSearchAgent` for Everything Else:** For all other questions, you MUST use the `GoogleSearchAgent`.
"""

root_agent = Agent(
   name="citi_wealth_advisor_agent",
   model="gemini-live-2.5-flash-preview-native-audio",
   description="An AI agent providing client-specific information and market news.",
   instruction=detailed_instructions,
   tools=[
       agent_tool.AgentTool(agent=profile_agent),
       agent_tool.AgentTool(agent=search_agent),
       agent_tool.AgentTool(agent=guidance_agent)
   ]
)