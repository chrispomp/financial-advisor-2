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
    """A plugin to check for new user input and interrupt the agent's ongoing generation."""
    def __init__(self):
        super().__init__(name="live_interrupt_plugin")

    async def before_model_callback(self, *, callback_context: CallbackContext, **kwargs):
        invocation_context = callback_context.invocation_context
        live_request_queue = invocation_context.live_request_queue
        if live_request_queue and not live_request_queue.empty():
            print("DEBUG: New message detected. Interrupting current model call.")
            invocation_context.end_invocation = True
            return types.Content(parts=[types.Part(text="I'm listening.")])
        return None

# --- Data Source Tools ---

def get_client_profile() -> str:
    """Retrieves the personal profile for the client, Chris Evans."""
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
    """Retrieves the financial portfolio for the client, Chris Evans."""
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
def initialize_and_greet(callback_context: CallbackContext) -> types.Content | None:
    """Loads client context at the start of the turn and greets the user on the first turn."""
    try:
        profile_data = json.loads(get_client_profile())
        portfolio_data = json.loads(get_client_portfolio())
        full_context = {**profile_data, **portfolio_data}
        callback_context.invocation_context["client_context"] = full_context
        print("DEBUG: Client context successfully loaded.")

        if callback_context.session and len(callback_context.session.events) == 1:
            preferred_name = full_context.get("preferred_name", "there")
            interests = full_context.get("personal_info", {}).get("personal_interests", [])
            greeting = f"Hello {preferred_name}, welcome back. "
            if "New York Jets" in interests:
                 greeting += "Hope you're looking forward to the Jets game this weekend. "
            greeting += "How can I help you today?"
            return types.Content(parts=[types.Part(text=greeting)])
    except Exception as e:
        print(f"DEBUG: Error in callback: {e}")
    return None

# --- Specialist Agents ---
profile_agent = Agent(name="ProfileAgent", model="gemini-2.5-flash-lite", description="For client's personal info (family, residence, interests).", tools=[get_client_profile])
portfolio_agent = Agent(name="PortfolioAgent", model="gemini-2.5-flash-lite", description="For client's financial accounts, holdings, and net worth.", tools=[get_client_portfolio])
product_rec_agent = Agent(name="ProductRecAgent", model="gemini-2.5-flash-lite", description="To find and recommend the best Citi product for the client.", tools=[get_citi_product_catalog])
guidance_agent = Agent(name="CitiGuidanceAgent", model="gemini-2.5-flash-lite", description="For Citi's official investment strategy and market outlook.", tools=[get_citi_guidance])
search_agent = Agent(name="GoogleSearchAgent", model="gemini-2.5-flash-lite", description="For general knowledge, news, weather, or real-time market data.", tools=[google_search])

# --- Root Agent ---
detailed_instructions = """
You are an elite AI Wealth Advisor from Citi, a trusted, hyper-personalized partner to your client, Chris Evans.

**Core Directives & Operational Plan:**
You MUST follow these rules in order:
1.  **Hyper-Personalize (CRITICAL):** You MUST use the `personal_info` and `investment_profile` from the `client_context` to make the conversation feel personal. Reference their interests, preferences, goals, and risk tolerance.
2.  **Location Mandate:** For ANY location-sensitive query (e.g., "things to do," "restaurants"), you MUST use the client's residence from the context in your tool call.
3.  **Vision First:** If asked about what you see, answer based on the visual input.
4.  **Check Context First:** For all other questions, check the pre-loaded `client_context` first.
5.  **Formulate a Plan & Execute:** If the answer is not in the context, determine the tool sequence, execute the calls, and synthesize the results into a single, insightful response.

**Crucial Example 1: Personalized Recommendation**
-   **User Query:** "Any good restaurants around here?"
-   **Your Thought Process:**
    1.  "This is a location-based, personal question. I must use both critical directives."
    2.  "Step 1: Check `client_context`. Residence is 'Long Beach, NY'. Favorite food is 'Mexican'."
    3.  "Step 2: My plan is to call `GoogleSearchAgent`."
    4.  "Step 3: I will execute the call with the query 'best Mexican restaurants in Long Beach NY'."
    5.  "Step 4: I will synthesize the results and respond, 'Since you enjoy Mexican food, you might like...'"

**Crucial Example 2: Personalized Advice**
-   **User Query:** "What should I do with the extra cash in my account?"
-   **Your Thought Process:** "This requires personalized financial advice. I'll check the client's `investment_profile` for their goals and risk tolerance, then call `CitiGuidanceAgent` to get the bank's official strategy, and finally synthesize the two into a tailored recommendation."
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
   before_agent_callback=initialize_and_greet
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
        proactivity=types.Proactivity(proactivity=0.5)
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
    print("--- 1. Testing Personalized Restaurant Recommendation ---")
    await run_live_agent("I'm hungry. Any ideas for dinner?", "user_123", "session_001")

    print("\n\n" + "="*50 + "\n\n")

    print("--- 2. Testing Personal Interest Knowledge ---")
    await run_live_agent("What's my favorite football team?", "user_123", "session_002", voice_name='en-US-Standard-J')

if __name__ == "__main__":
    asyncio.run(main())