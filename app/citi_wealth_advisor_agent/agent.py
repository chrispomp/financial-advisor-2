# citi_wealth_advisor_agent/agent.py

import json
from google.adk.agents import Agent, LiveRequestQueue
from google.adk.tools import google_search, agent_tool
from google.adk.agents.callback_context import CallbackContext
from google.genai import types

# Import the tools from your tools.py file
from . import tools

def preload_client_context(callback_context: CallbackContext):
    """
    Loads the full client context into the agent's memory at the start of each turn.
    This ensures the agent has the client's name and other details available for
    the very first response without needing an initial tool call.
    """
    try:
        # Only load the context once per turn to avoid redundancy.
        if "client_context" in callback_context.context:
            return

        print("DEBUG: Pre-loading client context for the first time this turn.")
        profile_data = json.loads(tools.get_client_profile())
        
        # Store the entire profile and the preferred name in the context dictionary
        callback_context.context["client_context"] = profile_data
        callback_context.context["preferred_name"] = profile_data.get("preferred_name")
        
        print(f"DEBUG: Client context successfully pre-loaded for '{profile_data.get('preferred_name')}'.")
    except Exception as e:
        print(f"DEBUG: CRITICAL ERROR pre-loading client context: {e}")


# --- Specialist Agents ---
model = "gemini-2.5-flash-lite"

profile_agent = Agent(
    name="ClientProfileAgent",
    model=model,
    description="Use this agent to retrieve detailed information about the wealth management client. It can access personal and financial data, including family details, financial goals, account balances, recent transactions, and identified opportunities with Citi. This is the primary source for any client-related questions.",
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
You are an elite AI Wealth Advisor from Citi, a trusted and hyper-personalized partner to your client.

**Core Directives & Operational Plan:**
1.  **Greeting Protocol (First Turn Only):** On the first turn of a new conversation, you MUST greet the client using the `preferred_name` provided in your context. Your greeting MUST begin with "Hello, [preferred_name]," and then you must immediately address the user's initial question in the same response.
2.  **Context is King (ABSOLUTE RULE):** The `client_context` is your primary source of truth. For ANY question about the client (e.g., "what's my name?", "how old am I?", "what's in my portfolio?"), you MUST find the answer in the `client_context` first before using any other tool.
3.  **Synthesize, Don't Just State:** When providing financial data, frame it in the context of the client's goals. For example, instead of just stating a stock's performance, relate it to their 'Moderate Growth' risk profile.
4.  **Delegate to Specialists:** If the answer is not in your preloaded context, determine the correct specialist agent (CitiGuidanceAgent for market strategy, GoogleSearchAgent for news) and delegate the task. Synthesize the results into a single, insightful response.
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
   ],
   before_agent_callback=preload_client_context
)