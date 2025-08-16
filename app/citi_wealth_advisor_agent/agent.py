import json
from google.adk.agents import Agent
from google.adk.tools import google_search, AgentTool
from google.adk.agents.callback_context import CallbackContext

# --- Data Source Tools ---
def get_client_profile() -> str:
    """Retrieves the personal, non-financial profile for the client, Chris Evans."""
    return json.dumps({
        "profile_id": "CEVANS-2025-08-16", "preferred_name": "Chris",
        "personal_info": {
            "age": 45, "residence": {"city": "Long Beach", "state": "NY"},
            "family": {"dependents": [{"name": "Sophia", "age": 16}, {"name": "Liam", "age": 13}]},
            "personal_interests": ["New York Jets", "technology", "punk rock music"],
        },
        "investment_profile": {
            "risk_tolerance": "Moderate Growth",
            "investment_horizon": "Long-term (15+ years)",
            "primary_goals": ["Retirement Planning", "Education Funding"]
        }
    })

def get_client_portfolio() -> str:
    """Retrieves the financial portfolio for the client, Chris Evans."""
    return json.dumps({
        "financial_snapshot_usd": {
            "net_worth": 8250000,
            "assets": [
                {"category": "Cash & Equivalents", "value": 1150000},
                {"category": "Investments", "top_holdings": ["AAPL", "MSFT", "GOOGL"]}
            ]
        },
        "recent_activity": "Large cash deposit of $800,000."
    })

def preload_client_context(callback_context: CallbackContext):
    """Loads the full client context into the agent's memory before the model is called."""
    if "client_context" not in callback_context.invocation_context:
        try:
            profile = json.loads(get_client_profile())
            portfolio = json.loads(get_client_portfolio())
            callback_context.invocation_context["client_context"] = {**profile, **portfolio}
            print("✅ DEBUG: Client context pre-loaded.")
        except Exception as e:
            print(f"❌ DEBUG: Error pre-loading context: {e}")

# --- Specialist Agents ---
profile_agent = Agent(name="ProfileAgent", model="gemini-2.5-flash", description="For client's personal info.", tools=[get_client_profile])
portfolio_agent = Agent(name="PortfolioAgent", model="gemini-2.5-flash", description="For client's financial accounts.", tools=[get_client_portfolio])
search_agent = Agent(name="GoogleSearchAgent", model="gemini-2.5-flash", description="For general knowledge.", tools=[google_search])

# --- Root Agent ---
detailed_instructions = """
You are an elite AI Wealth Advisor from Citi. You communicate only through voice.
**Core Directives:**
1.  **Context First:** You MUST use the `client_context` as your primary source of truth for any question about the client.
2.  **First Turn Greeting:** On the first turn, greet the client by their `preferred_name` from the context.
3.  **Vision First:** If asked about what you see, answer based on visual input.
"""

root_agent = Agent(
  name="citi_wealth_advisor_agent",
  model="gemini-live-2.5-flash-preview-native-audio",
  description="An AI wealth advisor for Citi clients.",
  instruction=detailed_instructions,
  tools=[
      AgentTool(agent=profile_agent),
      AgentTool(agent=portfolio_agent),
      AgentTool(agent=search_agent)
  ],
  before_model_callback=preload_client_context
)