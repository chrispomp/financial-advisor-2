import json
from google.adk.agents import Agent
from google.adk.tools import google_search, agent_tool
from google.adk.agents.callback_context import CallbackContext
from google.genai import types
from google.adk.plugins.base_plugin import BasePlugin

# --- Live Interrupt Plugin ---
class LiveInterruptPlugin(BasePlugin):
   def __init__(self):
       super().__init__(name="live_interrupt_plugin")

   async def _check_for_interrupt(self, callback_context: CallbackContext):
       if not hasattr(callback_context, 'invocation_context') or not hasattr(callback_context.invocation_context, 'live_request_queue'):
           return None
       live_request_queue = callback_context.invocation_context.live_request_queue
       if live_request_queue and not live_request_queue.empty():
           print("DEBUG: New message detected. Interrupting agent's current action.")
           callback_context.invocation_context.end_invocation = True
           return types.Content()
       return None

   async def before_model_callback(self, *, callback_context: CallbackContext, **kwargs):
       return await self._check_for_interrupt(callback_context)

# --- Data Source Tools ---
def get_client_profile() -> str:
   """Retrieves the personal profile for the client."""
   profile_data = {
     "profile_id": "CEVANS-2025-08-16", "client_name": "Christopher M. Evans", "preferred_name": "Chris",
     "personal_info": {
       "age": 45, "residence": {"city": "Long Beach", "state": "NY"},
       "family": {"dependents": [{"name": "Sophia", "age": 16}, {"name": "Liam", "age": 13}]},
       "personal_interests": ["New York Jets", "technology", "punk rock music"],
       "preferences": { "favorite_food": ["Mexican", "Sushi", "Burgers"] }
     },
     "investment_profile": { "risk_tolerance": "Moderate Growth", "investment_horizon": "Long-term (15+ years)", "primary_goals": ["Retirement Planning", "Education Funding for children"] }
   }
   return json.dumps(profile_data, indent=2)

def get_client_portfolio() -> str:
   """Retrieves the financial portfolio for the client."""
   portfolio_data = {
     "financial_snapshot_usd": {
       "net_worth": 8250000, "assets": [
         {"category": "Cash & Equivalents", "account_type": "Citigold Checking", "value": 1150000},
         {"category": "Investments", "account_type": "Brokerage Account", "top_holdings": [{"ticker": "AAPL"}, {"ticker": "MSFT"}, {"ticker": "GOOGL"}]}
       ]
     },
     "recent_activity": "Chris recently had an unusually large cash deposit of $800,000, which may indicate a significant life event."
   }
   return json.dumps(portfolio_data, indent=2)

def get_citi_product_catalog() -> str:
   """Retrieves Citi's catalog of featured products and services."""
   return json.dumps({"products": [{"product_name": "Citi Strata Elite Card", "category": "Credit Card"}]})

def get_citi_guidance() -> str:
   """Retrieves the official investment strategy and market outlook from Citi's CIO."""
   guidance = { "cio_message_summary": "We are navigating a complex global market, favoring quality and diversification.", "key_investment_themes": ["Focus on Quality", "The Return of Yield", "Go Global for Growth"] }
   return json.dumps(guidance, indent=2)

# --- Optimized Callback ---
def preload_client_context(callback_context: CallbackContext):
   """Loads the full client context into the agent's memory before the model is called."""
   if "client_context" in callback_context.invocation_context:
       return
   try:
       profile_data = json.loads(get_client_profile())
       portfolio_data = json.loads(get_client_portfolio())
       full_context = {**profile_data, **portfolio_data}
       callback_context.invocation_context["client_context"] = full_context
       print("DEBUG: Client context successfully pre-loaded.")
   except Exception as e:
       print(f"DEBUG: Error pre-loading client context: {e}")

# --- Specialist Agents ---
profile_agent = Agent(name="ProfileAgent", model="gemini-2.5-flash-lite", description="For client's personal info.", tools=[get_client_profile])
portfolio_agent = Agent(name="PortfolioAgent", model="gemini-2.5-flash-lite", description="For client's financial accounts.", tools=[get_client_portfolio])
product_rec_agent = Agent(name="ProductRecAgent", model="gemini-2.5-flash-lite", description="To recommend Citi products.", tools=[get_citi_product_catalog])
guidance_agent = Agent(name="CitiGuidanceAgent", model="gemini-2.5-flash-lite", description="For Citi's investment strategy.", tools=[get_citi_guidance])
search_agent = Agent(name="GoogleSearchAgent", model="gemini-2.5-flash-lite", description="For general knowledge.", tools=[google_search])

# --- Root Agent ---
detailed_instructions = """
You are an elite AI Wealth Advisor from Citi, a trusted, hyper-personalized partner to your client. You communicate only through voice.
**Core Directives & Operational Plan:**
1.  **Context First:** You MUST use the `client_context` as your primary source of truth for any question about the client.
2.  **First Turn Greeting:** On the first turn, greet the client by their `preferred_name` from the context.
3.  **Location Mandate:** For location-sensitive queries, you MUST use the client's residence from the context.
4.  **Vision First:** If asked about what you see, answer based on visual input.
5.  **Plan & Execute:** If the answer is not in the context, determine the tool sequence, execute, and synthesize the results.
"""

root_agent = Agent(
  name="citi_wealth_advisor_agent",
  model="gemini-live-2.5-flash-preview-native-audio",
  description="An AI wealth advisor for Citi clients.",
  instruction=detailed_instructions,
  tools=[
      agent_tool.AgentTool(agent=profile_agent),
      agent_tool.AgentTool(agent=portfolio_agent),
      agent_tool.AgentTool(agent=product_rec_agent),
      agent_tool.AgentTool(agent=guidance_agent),
      agent_tool.AgentTool(agent=search_agent)
  ],
  before_model_callback=preload_client_context
)