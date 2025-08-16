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
    Retrieves the detailed profile for the wealth management client, Chris Bonanno.
    This should be the primary source for answering any client-related questions.
    """
    profile_data = {
      "profile_id": "12345",
      "client_name": "Christopher Bonanno",
      "preferred_name": "Chris",
      "client_overview": "tech executive, married to Catherine Bonanno, and has two kids - Emilie (9) and Aiden (7)",
      "investment_goal": "focused on long-term growth for retirement and children's education.",
      "recent_activity": "Chris recently had an unusually large cash deposit into his checking account of $800,000, which may indicate a significant life event.",
      "deepening_opportunities": "Chris currently does not have a credit card with Citi, and would be an ideal candidate for the new Citi Strate Elite card.",
      "financial_snapshot_usd": {
        "net_worth": 7450000,
        "assets": [
          {
            "category": "Deposits",
            "account_type": "Citigold Interest Checking",
            "value": 1030000,
            "rate": "0.10%"
          },
          {
            "category": "Investments",
            "account_type": "Brokerage Account",
            "value": 3200000,
            "top_holdings": [
              {"ticker": "AAPL", "market_value": 150000},
              {"ticker": "MSFT", "market_value": 140000},
              {"ticker": "AMZN", "market_value": 130000},
              {"ticker": "GOOGL", "market_value": 120000},
              {"ticker": "JPM", "market_value": 110000},
              {"ticker": "UNH", "market_value": 100000}
            ]
          }
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
        "cio_outlook_summary": "We maintain a moderately constructive outlook on global markets, balancing resilient economic growth against persistent inflationary pressures. We advocate for a strategy of quality and diversification.",
        "key_themes": ["Quality Over Growth", "Yield is Back", "Diversify Globally"]
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
profile_agent = Agent(
    name="ClientProfileAgent",
    model="gemini-2.5-flash-lite",
    description="Use this agent to retrieve information about the client such as their financial holdings and personal details.",
    tools=[get_client_profile]
)

search_agent = Agent(
    name="GoogleSearchAgent",
    model="gemini-2.5-flash-lite",
    description="Use this agent for general knowledge questions, such as current events, market news, or information about specific companies.",
    tools=[google_search]
)

guidance_agent = Agent(
    name="CitiGuidanceAgent",
    model="gemini-2.5-flash-lite",
    description="Use this agent to get the official investment strategy and market outlook from Citi's Chief Investment Officer (CIO).",
    tools=[get_citi_guidance]
)

# --- Root Agent: ---
detailed_instructions = """
You are a friendly, professional, and concise AI Wealth Advisor for your client. Your primary directive is to answer questions by orchestrating responses from specialist agents.

**Core Principles:**
- **Assume Location:** For location-based questions (e.g., weather), use Chris's home in Long Beach, NY, unless specified otherwise.
- **Maintain Context:** Remember previous turns in the conversation to provide relevant follow-up answers.
- **Synthesize Information:** After gathering information from specialist agents, synthesize it into a single, clear, and concise answer for Chris.

**Operational Logic & Multi-Step Reasoning:**
You must handle complex questions that require multiple steps and using several tools in sequence.

1.  **Deconstruct the Request:** First, break down the user's query into logical steps.
2.  **Tool Selection:** For each step, select the appropriate specialist agent.
    -   **`ClientProfileAgent`**: For questions about Chris's personal finances, goals, or portfolio holdings.
    -   **`GoogleSearchAgent`**: For all other questions, including general news or real-time market data.
    -   **`CitiGuidanceAgent`**: For official investment strategy and market outlook.
    -   **Vision**: For questions about what you see via video feed.
3.  **Execute and Pass Context:** Execute the steps in order. Crucially, you **MUST** use the output from one step as the input for the next.

**Example Multi-Step Scenario:**
- **User Query:** "How did my stocks perform this week?"
- **Your Thought Process:**
    1.  "I need to know *what* the user's stocks are. I will use the `ClientProfileAgent`."
    2.  "After I get the list of stock tickers, I need to find their performance. I will use the `GoogleSearchAgent`."
- **Execution:**
    1.  Call `ClientProfileAgent` to get the list of stock holdings (e.g., AAPL, MSFT, AMZN).
    2.  Call `GoogleSearchAgent` using the list to search for "AAPL, MSFT, AMZN stock performance this week".
    3.  Synthesize the results into a final, easy-to-understand answer.
"""

root_agent = Agent(
   name="citi_wealth_advisor_agent",
   model="gemini-live-2.5-flash-preview-native-audio", # Reverted to the model that supports native voices
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
                # For native voices like 'Aoede', use the 'voice' parameter.
                voice=voice_name
            )
        ),
        response_modalities=["AUDIO", "TEXT", "VIDEO"],
        proactivity=types.Proactivity(
            proactivity=0.1
        )
    )

    initial_message = types.Content(role="user", parts=[types.Part(text=query)])
    live_request_queue.send_content(initial_message)
    await live_request_queue.close()

    print(f"User Query: '{query}' (Voice: {voice_name})")
    print("-" * 30)

    try:
        async for event in runner.run_live(
            user_id=user_id,
            session_id=session_id,
            live_request_queue=live_request_queue,
            run_config=run_config
        ):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        print(f"Agent Response: {part.text}")
                    if hasattr(part, "inline_data") and part.inline_data:
                        print("...Agent is streaming audio/video...")
    finally:
        await runner.close()

async def main():
    """Main function to run agent examples."""
    print("--- Running Multi-Step Query Example ---")
    await run_live_agent(
        "How did my top stock holdings perform this week?",
        "user_123",
        "session_001",
        voice_name=DEFAULT_VOICE # Uses the default 'Aoede' voice
    )
    
    print("\n\n" + "="*50 + "\n\n")

    print("--- Running General Knowledge Example (with a different voice) ---")
    await run_live_agent(
        "What's the weather like in Long Beach, New York?",
        "user_123",
        "session_002",
        voice_name='en-US-Standard-J' # Example of overriding the default voice
    )

if __name__ == "__main__":
    asyncio.run(main())