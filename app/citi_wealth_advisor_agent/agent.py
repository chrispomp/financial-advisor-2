import json
import asyncio
from google.adk.agents import Agent, LiveRequestQueue
from google.adk.tools import google_search, agent_tool
from google.adk.agents.callback_context import CallbackContext
from google.genai import types
from google.adk.runners import Runner, InMemoryRunner
from google.adk.sessions import InMemorySessionService
from google.adk.agents.run_config import RunConfig, StreamingMode
from google.adk.plugins.base_plugin import BasePlugin
import datetime
from zoneinfo import ZoneInfo
import os

# --- Live Interrupt Plugin ---
class LiveInterruptPlugin(BasePlugin):
    """A plugin to check for new user input and interrupt the agent's ongoing generation."""

    def __init__(self):
        super().__init__(name="live_interrupt_plugin")

    async def before_model_callback(self, *, callback_context: CallbackContext, **kwargs):
        """
        Check if there are any new messages in the LiveRequestQueue.
        If so, force the agent to stop its current LLM call.
        """
        invocation_context = callback_context.invocation_context
        live_request_queue = invocation_context.live_request_queue
        
        if live_request_queue and not live_request_queue.empty():
            print("DEBUG: New message detected. Interrupting current model call.")
            invocation_context.end_invocation = True
            return types.Content(parts=[types.Part(text="I'm listening.")])

        return None

# --- Tool Definition: Client Profile ---
def get_client_profile() -> str:
    """
    Retrieves the detailed profile for the wealth management client, Chris Evans.
    """
    profile_data = {
      "profile_id": "CEVANS-2025-0815",
      "client_name": "Christopher M. Evans",
      "preferred_name": "Chris",
      "relationship_manager": "Jane Foster",
      "status": "Active, High-Potential",
      "last_updated": "2025-08-15",
      "summary": "High-earning, time-poor tech executive focused on long-term growth for retirement and children's education. Digitally savvy, values data-driven advice. Key opportunities include asset consolidation and advanced financial planning.",
      "personal_info": {
        "age": 45,
        "occupation": "Senior Director, Product Management",
        "employer": "Global Tech Firm",
        "residence": {
          "city": "Long Beach",
          "state": "NY",
          "zip": "11561"
        },
        "family": {
          "marital_status": "Married",
          "spouse": {
            "name": "Emily Evans",
            "age": 44,
            "occupation": "Anesthesiologist, Stamford Hospital"
          },
          "dependents": [
            {
              "name": "Sophia Evans",
              "relation": "Daughter",
              "age": 16
            },
            {
              "name": "Liam Evans",
              "relation": "Son",
              "age": 13
            }
          ]
        }
      },
      "financial_snapshot_usd": {
        "net_worth": 7450000,
        "total_assets": 9050000,
        "total_liabilities": 1400000,
        "assets": [
          {
            "category": "Cash & Equivalents",
            "institution": "Citi",
            "account_type": "Citigold Checking",
            "value": 350000
          },
          {
            "category": "Cash & Equivalents",
            "institution": "Competitor Firm",
            "account_type": "Money Market Fund",
            "value": 250000
          },
          {
            "category": "Investments",
            "institution": "Citi",
            "account_type": "Brokerage Account",
            "value": 3200000,
            "notes": "70% Equities, 25% Fixed Income, 5% Alternatives.",
            "top_holdings": [
              { "ticker": "AAPL", "market_value": 150000 },
              { "ticker": "MSFT", "market_value": 140000 },
              { "ticker": "AMZN", "market_value": 130000 },
              { "ticker": "GOOGL", "market_value": 120000 },
              { "ticker": "JPM", "market_value": 110000 },
              { "ticker": "UNH", "market_value": 100000 }
            ]
          },
          { "category": "Investments", "account_type": "Employer 401(k)", "value": 1800000 },
          { "category": "Investments", "account_type": "Vested Stock Options", "value": 950000 },
          { "category": "Real Estate", "property_type": "Primary Residence", "value": 2500000 }
        ],
        "liabilities": [
          { "type": "Primary Mortgage", "balance": 1400000, "notes": "30-year fixed at 3.25%." }
        ]
      },
      "goals_and_objectives": [
        { "priority": "Primary", "goal": "Retirement Planning", "details": { "target_age": 65, "desired_annual_income_post_tax": 350000 } },
        { "priority": "Secondary", "goal": "Education Funding", "details": { "beneficiaries": ["Sophia Evans", "Liam Evans"], "target_amount_per_child": 300000 } },
        { "priority": "Tertiary", "goal": "Estate Planning", "details": { "objective": "Efficient wealth transfer and tax burden minimization." } }
      ],
      "citi_relationship": {
        "client_since": 2015,
        "actionable_opportunities": [
          {"area": "Consolidation", "action": "Propose plan to move competitor-held Money Market fund to Citi."},
          {"area": "Education Planning", "action": "Discuss benefits and funding of 529 College Savings Plans."},
          {"area": "Concentrated Stock", "action": "Present options for hedging or systematically selling vested company stock."}
        ]
      }
    }
    return json.dumps(profile_data, indent=2)

# --- Tool Definition: Citi Guidance ---
def get_citi_guidance() -> str:
    """
    Retrieves the official investment strategy and market outlook from Citi's CIO.
    """
    guidance = {
        "cio_outlook_summary": "We maintain a moderately constructive outlook on global markets, balancing resilient economic growth against persistent inflationary pressures and geopolitical risks. We advocate for a strategy of quality and diversification, focusing on companies with strong balance sheets and durable earnings power.",
        "strategic_asset_allocation_moderate_risk": {
            "equities": { "total_allocation": "55%", "us_large_cap": "30%", "international_developed": "15%", "emerging_markets": "5%" },
            "fixed_income": { "total_allocation": "35%", "investment_grade_corporate": "20%", "us_treasuries": "10%", "high_yield": "5%" },
            "alternatives": { "total_allocation": "10%" }
        },
        "key_themes": ["Quality Over Growth", "Yield is Back", "Diversify Globally", "Hedge Inflation"]
    }
    return json.dumps(guidance, indent=2)

# --- Greeting Callback: ---
def greeting_callback(callback_context: CallbackContext) -> types.Content | None:
    """Greets the user at the beginning of a session."""
    try:
        if len(callback_context.session.events) == 1:
            client_profile = json.loads(get_client_profile())
            preferred_name = client_profile.get("preferred_name", "Chris")
            return types.Content(parts=[types.Part(text=f"Hello {preferred_name}, welcome. How can I help you today?")])
    except AttributeError as e:
        print(f"DEBUG: Could not find session attribute. Error: {e}")
    return None

# --- Specialist Agents: ---
profile_agent = Agent(name="ClientProfileAgent", model="gemini-1.5-flash-latest", description="Retrieves information about the client, Chris Evans.", tools=[get_client_profile])
search_agent = Agent(name="GoogleSearchAgent", model="gemini-1.5-flash-latest", description="Use for general knowledge questions.", tools=[google_search])
guidance_agent = Agent(name="CitiGuidanceAgent", model="gemini-1.5-flash-latest", description="Gets official investment strategy from Citi's CIO.", tools=[get_citi_guidance])

# --- Root Agent: ---
detailed_instructions = """You are a friendly, professional, and concise AI Wealth Advisor for your client, Chris Evans.
- **Location**: Assume location-based questions (e.g., weather) are for his home in Long Beach, NY.
- **Delegation**: Your main purpose is to delegate questions to the correct specialist agent.
- **Logic**:
  1.  **Vision**: Answer questions about what you see using video input.
  2.  **`CitiGuidanceAgent`**: Use for investment strategy, market outlook, or recommendations.
  3.  **`ClientProfileAgent`**: Use for questions about Chris's finances, goals, or portfolio.
  4.  **`GoogleSearchAgent`**: Use for all other questions (e.g., general news).
  5.  **Synthesize**: Relay the information from the specialist agent clearly to Chris."""

root_agent = Agent(
   name="citi_wealth_advisor_agent",
   model="gemini-live-2.5-flash",
   description="An AI wealth advisor for Citi clients.",
   instruction=detailed_instructions,
   tools=[
       agent_tool.AgentTool(agent=profile_agent),
       agent_tool.AgentTool(agent=search_agent),
       agent_tool.AgentTool(agent=guidance_agent)
   ],
   before_agent_callback=greeting_callback
)

# --- CONFIGURATION: Define the default native voice in one place ---
DEFAULT_VOICE = 'Aoede'

async def run_live_agent(query: str, user_id: str, session_id: str, voice_name: str = DEFAULT_VOICE):
    """Runs the agent in a live, bidirectional streaming session."""
    runner = InMemoryRunner(agent=root_agent, plugins=[LiveInterruptPlugin()])
    live_request_queue = LiveRequestQueue()

    run_config = RunConfig(
        streaming_mode=StreamingMode.BIDI,
        speech_config=types.SpeechConfig(
            voice_config=types.VoiceConfig(
                voice=voice_name  # CORRECTED: Use 'voice' for native voices
            )
        ),
        response_modalities=["AUDIO", "TEXT", "VIDEO"],
        proactivity=types.ProactivityConfig(level=0.2)
    )

    initial_message = types.Content(role="user", parts=[types.Part(text=query)])
    live_request_queue.send_content(initial_message)
    await live_request_queue.close()

    print(f"User Query: '{query}' (Voice: {voice_name})")
    print("-" * 30)

    async for event in runner.run_live(user_id=user_id, session_id=session_id, live_request_queue=live_request_queue, run_config=run_config):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    print(f"Agent Response: {part.text}")
                if hasattr(part, "inline_data") and part.inline_data:
                    print("...Agent is streaming audio...")
    await runner.close()

async def run_simulated_interruption(query1: str, query2: str, user_id: str, session_id: str, voice_name: str = DEFAULT_VOICE):
    """Simulates a user interrupting the agent."""
    runner = InMemoryRunner(agent=root_agent, plugins=[LiveInterruptPlugin()])
    live_request_queue = LiveRequestQueue()

    run_config = RunConfig(
        streaming_mode=StreamingMode.BIDI,
        speech_config=types.SpeechConfig(
            voice_config=types.VoiceConfig(
                voice=voice_name  # CORRECTED: Use 'voice' for native voices
            )
        ),
        response_modalities=["AUDIO", "TEXT", "VIDEO"],
        proactivity=types.ProactivityConfig(level=0.5)
    )

    async def send_first_query():
        live_request_queue.send_content(types.Content(role="user", parts=[types.Part(text=query1)]))

    async def send_interrupt_query():
        await asyncio.sleep(2)
        print("\n--- Simulating User Interruption ---")
        live_request_queue.send_content(types.Content(role="user", parts=[types.Part(text=query2)]))
        await live_request_queue.close()

    print(f"Simulated Query 1: '{query1}' (Voice: {voice_name})")
    print(f"Simulated Interruption Query 2: '{query2}'")
    print("-" * 30)

    async with asyncio.TaskGroup() as tg:
        tg.create_task(send_first_query())
        tg.create_task(send_interrupt_query())
        async for event in runner.run_live(user_id=user_id, session_id=session_id, live_request_queue=live_request_queue, run_config=run_config):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        print(f"Agent Response: {part.text}")
                    if hasattr(part, "inline_data") and part.inline_data:
                        print("...Agent is streaming audio...")
    await runner.close()

async def main():
    # Example 1: Standard conversation
    print("--- Running Standard Conversation ---")
    await run_live_agent("Hello, who are you?", "user_123", "session_001")
    
    print("\n\n" + "="*50 + "\n\n")

    # Example 2: Interruption demo
    print("--- Running Interruption Simulation ---")
    await run_simulated_interruption(
        "Give me a detailed summary of the CIO's latest market outlook.",
        "Actually, just tell me my net worth.",
        "user_123",
        "session_002",
        voice_name='Aoede'
    )

if __name__ == "__main__":
    asyncio.run(main())