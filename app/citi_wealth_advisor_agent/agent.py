import json
import asyncio
from google.adk.agents import Agent, LiveRequestQueue
from google.adk.tools import google_search, agent_tool
from google.adk.agents.callback_context import CallbackContext
from google.genai import types
from google.adk.runners import Runner, InMemoryRunner
from google.adk.agents.run_config import RunConfig, StreamingMode
from google.adk.plugins.base_plugin import BasePlugin


# --- Live Interrupt Plugin ---
class LiveInterruptPlugin(BasePlugin):
   """
   A plugin to check for new user input and interrupt the agent's ongoing generation
   at multiple points in the agent lifecycle for maximum responsiveness.
   """
   def __init__(self):
       super().__init__(name="live_interrupt_plugin")

   async def _check_for_interrupt(self, callback_context: CallbackContext):
       """Checks the live request queue and signals to end the invocation if new input is found."""
       # The invocation_context might not be available in all callback contexts.
       if not hasattr(callback_context, 'invocation_context'):
           return None
      
       invocation_context = callback_context.invocation_context
       # The live_request_queue is a specific attribute for live runs.
       if not hasattr(invocation_context, 'live_request_queue'):
           return None
          
       live_request_queue = invocation_context.live_request_queue
       if live_request_queue and not live_request_queue.empty():
           print("DEBUG: New message detected. Interrupting agent's current action.")
           # This flag tells the runner to stop the current processing.
           invocation_context.end_invocation = True
           # Returning empty content stops the current callback from proceeding (e.g., calling a model or tool).
           return types.Content()
       return None # Continue normally if no interruption.

   async def before_agent_callback(self, *, callback_context: CallbackContext, **kwargs):
       return await self._check_for_interrupt(callback_context)

   async def before_model_callback(self, *, callback_context: CallbackContext, **kwargs):
       return await self._check_for_interrupt(callback_context)
      
   async def before_tool_call(self, *, callback_context: CallbackContext, **kwargs):
       return await self._check_for_interrupt(callback_context)

   async def after_tool_call(self, *, callback_context: CallbackContext, **kwargs):
       return await self._check_for_interrupt(callback_context)


# --- Data Source Tools ---


def get_client_profile() -> str:
   """Retrieves the personal profile for the client."""
   profile_data = {
     "profile_id": "CEVANS-2025-08-16",
     "client_name": "Christopher M. Evans",
     "preferred_name": "Chris",
     "personal_info": {
       "age": 45,
       "residence": {"city": "Long Beach", "state": "NY"},
       "family": {"dependents": [{"name": "Sophia", "age": 16}, {"name": "Liam", "age": 13}]},
       "personal_interests": ["New York Jets", "technology", "punk rock music"],
       "preferences": {
           "favorite_food": ["Mexican", "Sushi", "Burgers"]
       }
     },
     "investment_profile": {
         "risk_tolerance": "Moderate Growth",
         "investment_horizon": "Long-term (15+ years)",
         "primary_goals": ["Retirement Planning", "Education Funding for children"]
     }
   }
   return json.dumps(profile_data, indent=2)


def get_client_portfolio() -> str:
   """Retrieves the financial portfolio for the client."""
   portfolio_data = {
     "financial_snapshot_usd": {
       "net_worth": 8250000,
       "assets": [
         {"category": "Cash & Equivalents", "account_type": "Citigold Checking", "value": 1150000},
         {"category": "Investments", "account_type": "Brokerage Account",
          "top_holdings": [{"ticker": "AAPL"}, {"ticker": "MSFT"}, {"ticker": "GOOGL"}]}
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
   guidance = {
       "cio_message_summary": "We are navigating a complex global market, favoring quality and diversification. We see potential in high-quality fixed income and select global equities.",
       "key_investment_themes": ["Focus on Quality", "The Return of Yield", "Go Global for Growth"]
   }
   return json.dumps(guidance, indent=2)


# --- Consolidated Callback ---
def preload_client_context(callback_context: CallbackContext):
   """Loads the full client context into the agent's memory at the start of each turn."""
   try:
       profile_data = json.loads(get_client_profile())
       portfolio_data = json.loads(get_client_portfolio())
       full_context = {**profile_data, **portfolio_data}
       callback_context.invocation_context["client_context"] = full_context
       print("DEBUG: Client context successfully pre-loaded.")
   except Exception as e:
       print(f"DEBUG: Error pre-loading client context: {e}")


# --- Specialist Agents ---
profile_agent = Agent(name="ProfileAgent", model="gemini-2.5-flash-lite", description="For client's personal info (family, residence, interests).", tools=[get_client_profile])
portfolio_agent = Agent(name="PortfolioAgent", model="gemini-2.5-flash-lite", description="For client's financial accounts, holdings, and net worth.", tools=[get_client_portfolio])
product_rec_agent = Agent(name="ProductRecAgent", model="gemini-2.5-flash-lite", description="To find and recommend the best Citi product for the client.", tools=[get_citi_product_catalog])
guidance_agent = Agent(name="CitiGuidanceAgent", model="gemini-2.5-flash-lite", description="For Citi's official investment strategy and market outlook.", tools=[get_citi_guidance])
search_agent = Agent(name="GoogleSearchAgent", model="gemini-2.5-flash-lite", description="For general knowledge, news, weather, or real-time market data.", tools=[google_search])


# --- Root Agent ---
detailed_instructions = """
You are an elite AI Wealth Advisor from Citi, a trusted, hyper-personalized partner to your client.


**Core Directives & Operational Plan:**
You MUST follow these rules in order:
1.  **Check Context First (CRITICAL):** The `client_context` is your primary source of truth. For ANY question about the client (e.g., "what's my name?", "how old am I?", "what's my favorite team?"), you MUST find the answer in the `client_context` first before using any other tool.
2.  **First Turn Greeting:** On the first turn of a new conversation, start your response by greeting the client by their `preferred_name` from the context. Then, answer their question in the same response.
3.  **Location Mandate:** For ANY location-sensitive query (e.g., "things to do"), you MUST use the client's residence from the context in your tool call.
4.  **Vision First:** If asked about what you see, answer based on the visual input.
5.  **Formulate a Plan & Execute:** If the answer is not in the context, determine the tool sequence, execute the calls, and synthesize the results into a single, insightful response.
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
  before_agent_callback=preload_client_context
)


# --- Main Execution ---
DEFAULT_VOICE = 'Aoede'


async def run_live_agent(query: str, user_id: str, session_id: str, voice_name: str = DEFAULT_VOICE):
   """Runs the agent in a live, bidirectional streaming session."""
   runner = InMemoryRunner(agent=root_agent, plugins=[LiveInterruptPlugin()])
   live_request_queue = LiveRequestQueue()
   run_config = RunConfig(
       streaming_mode=StreamingMode.BIDI,
       speech_config=types.SpeechConfig(voice_config=types.VoiceConfig(voice=voice_name)),
       response_modalities=["AUDIO", "TEXT", "VIDEO"],
       proactivity=types.Proactivity(proactivity=0.1)
   )


   live_request_queue.send_content(types.Content(role="user", parts=[types.Part(text=query)]))
   await live_request_queue.close()


   print(f"\nUser Query: '{query}' (Voice: {voice_name})")
   print("-" * 30)
   try:
       async for event in runner.run_live(user_id=user_id, session_id=session_id, live_request_queue=live_request_queue, run_config=run_config):
           if event.content and event.content.parts:
               for part in event.content.parts:
                   if part.text:
                       print(f"Agent Response: {part.text}")
   finally:
       await runner.close()


async def main():
   """Main function to run agent examples."""
   print("--- 1. Testing Knowledge of Age ---")
   await run_live_agent("How old am I?", "user_123", "session_001")


   print("\n\n" + "="*50 + "\n\n")


   print("--- 2. Testing Personal Interest Knowledge ---")
   await run_live_agent("What's my favorite football team?", "user_123", "session_002", voice_name='en-US-Standard-J')


if __name__ == "__main__":
   asyncio.run(main())