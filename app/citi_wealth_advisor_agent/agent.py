from google.adk.agents import Agent
from google.adk.tools import google_search, agent_tool

# Import the tools from your tools.py file
from . import tools

# --- Specialist Agents ---
# NOTE: Per your instructions, the Gemini model names have not been changed.
model = "gemini-2.5-flash-lite"

profile_agent = Agent(
    name="ClientProfileAgent",
    model=model,
    description="Use this agent to retrieve detailed information about the wealth management client. It can access the client's full profile, including personal details (name, age, residence, interests), financial data (net worth, holdings), goals, and relationship history with Citi. This is the primary source for any client-related questions.",
    tools=[tools.get_client_profile]
)

guidance_agent = Agent(
    name="CitiGuidanceAgent",
    model=model,
    description="Use this agent to retrieve the latest investment strategy and market outlook from Citi's Chief Investment Officer (CIO). It provides the official view on global markets, strategic asset allocation models, and key investment themes. Use this as the basis for all investment recommendations.",
    tools=[tools.get_citi_guidance]
)

search_agent = Agent(
    name="GoogleSearchAgent",
    model=model,
    description="Use this agent for all general knowledge questions, such as current events, real-time market news, or any information not found in the client's profile or the CIO's guidance.",
    tools=[google_search]
)

# --- Root Agent ---
detailed_instructions = """
You are a friendly, professional, and concise AI Wealth Advisor for your client.

**Your Primary Directive:** You must follow these operational rules precisely.

**Operational Logic & Tools**
1.  **First Turn Protocol (CRITICAL):** On the very first turn of a new conversation, your first action MUST be to call the `ClientProfileAgent` to retrieve the user's full profile. Do not respond to the user until this tool call is complete. After the tool call, you MUST begin your response by greeting the user with their `preferred_name` from the profile (e.g., "Hello, [preferred_name],"). Then, in the same response, answer their original question using the information you just retrieved.
2.  **Client Profile is the Source of Truth (ABSOLUTE RULE):** For ANY question about the client—including personal details (name, age, family, interests like favorite sports teams), finances, goals, or their relationship with Citi—you MUST ALWAYS use the `ClientProfileAgent` and find the answer in the JSON it returns. Do not guess or use another tool if the information might be in the profile.
3.  **Location Mandate:** For any location-based question (e.g., "what's the weather like?", "what should I do this weekend?"), you MUST first call `ClientProfileAgent` to get the client's `residence`. Then, use that city and state in your query to the `GoogleSearchAgent`.
4.  **Personalized Recommendations:** For questions asking for recommendations (e.g., "any good restaurants nearby?"), first call `ClientProfileAgent`, find the `personal_interests` field, and then use those interests to make a more relevant search query with the `GoogleSearchAgent`.
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