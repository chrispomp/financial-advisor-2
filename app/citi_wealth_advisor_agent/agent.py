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
        "residence": {"city": "Long Beach", "state": "NY"},
        "family": {"dependents": [{"name": "Sophia"}, {"name": "Liam"}]},
        "personal_interests": ["technology", "reading", "music"],
        "preferences": {
            "favorite_football_team": "New York Jets",
            "favorite_food": "Taco Bell"
        }
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
    products = {
        "products": [
            {
                "product_name": "Citi Strata Elite Card",
                "category": "Credit Card",
                "features": "Flagship lifestyle card. 10x points on hotels, car rentals, and attractions booked through CitiTravel.com. 3x points on airlines, dining, and supermarkets. $300 annual travel credit. Global Entry/TSA PreCheck credit.",
                "ideal_for": ["premium lifestyle spender", "maximizing travel points", "values simplicity and high rewards"]
            },
            {
                "product_name": "Citi® / AAdvantage® Executive World Elite Mastercard®",
                "category": "Credit Card",
                "features": "Admirals Club membership, first checked bag free, priority boarding on American Airlines, high AAdvantage mile earn rate.",
                "ideal_for": ["frequent American Airlines flyer", "seeks elite airline status", "values airport lounge access"]
            }
        ]
    }
    return json.dumps(products, indent=2)


def get_citi_guidance() -> str:
    """
    Retrieves the official investment strategy, market outlook, and recommendations
    from Citi's Chief Investment Officer (CIO). This is a comprehensive guide for
    wealth management clients.
    """
    guidance = {
        "guidance_date": "2025-08-15",
        "cio_message_summary": "We are navigating a complex global market. While economic growth remains resilient, inflationary pressures and geopolitical tensions require a disciplined and diversified approach. We believe the current environment favors quality over speculation. Our strategy is focused on identifying durable, long-term opportunities while managing downside risk. We see potential in high-quality fixed income, which now offers attractive yields, and select global equities with strong fundamentals.",
        "market_outlook": "Neutral to Cautiously Optimistic",
        "strategic_asset_allocation_moderate_growth": {
            "equities": {
                "total": "55%",
                "us_large_cap": "30%",
                "us_smid_cap": "5%",
                "international_developed": "15%",
                "emerging_markets": "5%"
            },
            "fixed_income": {
                "total": "35%",
                "investment_grade_corporate": "20%",
                "us_treasuries_munis": "10%",
                "high_yield_other": "5%"
            },
            "alternatives": {"total": "5%", "description": "e.g., Real Estate, Private Credit"},
            "cash_and_equivalents": {"total": "5%", "description": "For liquidity and tactical opportunities"}
        },
        "tactical_outlook_tilts_3_to_6_months": {
            "us_equities": "Neutral",
            "international_equities": "Slightly Overweight",
            "investment_grade_bonds": "Overweight",
            "high_yield_bonds": "Underweight",
            "commodities": "Neutral"
        },
        "key_investment_themes": [
            {
                "theme": "Focus on Quality",
                "rationale": "In an environment of moderating growth, we prefer companies with strong balance sheets, consistent earnings, and competitive advantages (a 'moat'). These companies are better positioned to weather economic uncertainty than more speculative, high-growth stocks."
            },
            {
                "theme": "The Return of Yield",
                "rationale": "After years of low interest rates, high-quality fixed income now offers compelling yields. We believe investment-grade corporate and municipal bonds provide an attractive source of income and a valuable diversifier to equity risk."
            },
            {
                "theme": "Go Global for Growth",
                "rationale": "While the US market remains central, valuations in some international developed and emerging markets are more attractive. Diversifying globally can capture different economic cycles and opportunities, particularly in regions benefiting from long-term secular growth trends."
            }
        ],
        "actionable_recommendations": [
            "Review your portfolio's fixed-income allocation to ensure you are capturing current yield opportunities.",
            "Consider rebalancing from highly concentrated, speculative growth stocks towards a basket of quality, blue-chip global equities.",
            "For long-term goals like education, ensure you are adequately diversified beyond just US stocks."
        ],
        "disclaimer": "This information is for general informational purposes only and is not intended to be personal investment advice. All investment decisions should be made with a qualified financial advisor."
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
            return types.Content(parts=[types.Part(text=f"Hello {preferred_name}, welcome back. How can I help?")])
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
You are an elite AI Wealth Advisor from Citi, a trusted, hyper-personalized partner to your client, Chris Evans. Your persona is friendly, professional, and exceptionally proactive.

**Strict Operational Plan:**
You MUST follow these steps in order for every query:
1.  **Vision First:** If the user asks a question about what you see (e.g., "what am I wearing?"), you MUST answer based on the visual input from the camera.
2.  **Analyze & Check Context:** For all other questions, understand the user's intent. Immediately check the pre-loaded `client_context` to see if the answer is already there. For personal questions like "what's my favorite food?", the answer MUST come from the `preferences` section of the context. For location-based queries (e.g., weather), you MUST use the city/state from the context.
3.  **Formulate a Plan:** If the answer is not in the context, determine the sequence of tools needed.
4.  **Execute & Synthesize:** Call the specialist agents in order, passing information between them as necessary, and synthesize the final result into a single, insightful response.

**Crucial Example 1: Daily Briefing**
-   **User Query:** "Give me my daily briefing."
-   **Your Thought Process:**
    1.  "This is a request for a structured financial summary. I must follow a specific sequence."
    2.  "Step 1: Get a general market update. I will call `GoogleSearchAgent` with a query like 'today's financial market news summary'."
    3.  "Step 2: Get my client's specific holdings. The tickers are in the pre-loaded `client_context`. I see AAPL, MSFT, and GOOGL."
    4.  "Step 3: Get the performance of those holdings. I will call `GoogleSearchAgent` again with the query 'AAPL, MSFT, GOOGL stock performance'."
    5.  "Step 4: Check for recent portfolio activity. The `client_context` contains a `recent_activity` field. I see a large cash deposit of $800,000."
    6.  "Step 5: Synthesize all this information. I will start with the market overview, then the personal portfolio performance, and conclude by proactively addressing the large cash deposit with a recommendation based on Citi's guidance."

**Crucial Example 2: Personalized Portfolio Performance**
-   **User Query:** "How did my stocks perform this week?"
-   **Your Thought Process:**
    1.  "This requires a multi-step plan. I'll get the stock tickers from the `client_context` and then use `GoogleSearchAgent` to find their performance for the week."
    2.  "I will synthesize the search results into a concise summary for the client."
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
    print("--- 1. Testing Daily Briefing ---")
    await run_live_agent("Give me my daily briefing.", "user_123", "session_001")

    print("\n\n" + "="*50 + "\n\n")
    
    print("--- 2. Testing Personal Preference Question ---")
    await run_live_agent("What is my favorite sports team?", "user_123", "session_002", voice_name='en-US-Standard-J')


if __name__ == "__main__":
    asyncio.run(main())