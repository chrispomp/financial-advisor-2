import json
import asyncio
import uvicorn
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from google.adk.agents import Agent, LiveRequestQueue
from google.adk.tools import google_search, agent_tool
from google.adk.agents.callback_context import CallbackContext
from google.genai import types
from google.adk.agents.run_config import RunConfig, StreamingMode
from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.genai.types import Content, Part

# --- Data Source Tools (No changes needed here) ---

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

# --- Context Loading Callback (No changes needed here) ---
def load_context_on_turn(callback_context: CallbackContext):
    """Loads client context into memory at the start of a turn if not already present."""
    if "client_context" in callback_context.invocation_context:
        return

    try:
        print("DEBUG: `client_context` not found. Loading now.")
        profile_data = json.loads(get_client_profile())
        portfolio_data = json.loads(get_client_portfolio())
        full_context = {**profile_data, **portfolio_data}
        callback_context.invocation_context["client_context"] = full_context
        print("DEBUG: Client context successfully pre-loaded.")
    except json.JSONDecodeError as e:
        print(f"DEBUG: Error decoding JSON from data source: {e}")
    except Exception as e:
        print(f"DEBUG: An unexpected error occurred while pre-loading client context: {e}")


# --- Specialist Agents (No changes needed here) ---
profile_agent = Agent(name="ProfileAgent", model="gemini-2.5-flash-lite", description="For client's personal info (family, residence, interests).", tools=[get_client_profile])
portfolio_agent = Agent(name="PortfolioAgent", model="gemini-2.5-flash-lite", description="For client's financial accounts, holdings, and net worth.", tools=[get_client_portfolio])
product_rec_agent = Agent(name="ProductRecAgent", model="gemini-2.5-flash-lite", description="To find and recommend the best Citi product for the client.", tools=[get_citi_product_catalog])
guidance_agent = Agent(name="CitiGuidanceAgent", model="gemini-2.5-flash-lite", description="For Citi's official investment strategy and market outlook.", tools=[get_citi_guidance])
search_agent = Agent(name="GoogleSearchAgent", model="gemini-2.5-flash-lite", description="For general knowledge, news, weather, or real-time market data.", tools=[google_search])


# --- Root Agent (No changes needed here) ---
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
   before_model_callback=load_context_on_turn
)

# --- FastAPI Server Setup ---
app = FastAPI()

# Allow requests from your web page
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"], # In production, restrict this to your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

runner = Runner(
    app_name="citi_wealth_advisor_agent",
    agent=root_agent,
    session_service=InMemorySessionService(),
)

async def start_agent_session(user_id, is_audio=False):
    """Starts an agent session"""
    # Create a Session
    session = await runner.session_service.create_session(
        app_name="citi_wealth_advisor_agent",
        user_id=user_id,
    )

    # Set response modality
    modality = "AUDIO" if is_audio else "TEXT"
    run_config = RunConfig(
        response_modalities=[modality],
        speech_config=types.SpeechConfig(
            input_audio_config=types.InputAudioConfig(
                encoding="LINEAR16",
                sample_rate_hertz=16000
            )
        )
    )

    # Create a LiveRequestQueue for this session
    live_request_queue = LiveRequestQueue()

    # Start agent session
    live_events = runner.run_live(
        session=session,
        live_request_queue=live_request_queue,
        run_config=run_config,
    )
    return live_events, live_request_queue

async def agent_to_client_messaging(websocket, live_events):
    """Agent to client communication"""
    while True:
        async for event in live_events:
            if event.turn_complete or event.interrupted:
                message = {
                    "turn_complete": event.turn_complete,
                    "interrupted": event.interrupted,
                }
                await websocket.send_text(json.dumps(message))
                continue

            part: Part = (
                event.content and event.content.parts and event.content.parts[0]
            )
            if not part:
                continue

            if part.text:
                message = {
                    "text": part.text
                }
                await websocket.send_text(json.dumps(message))

            if part.inline_data:
                await websocket.send_bytes(part.inline_data.data)


async def client_to_agent_messaging(websocket, live_request_queue):
    """Client to agent communication"""
    while True:
        data = await websocket.receive_bytes()
        live_request_queue.send_realtime(
            types.Blob(data=data, mime_type="audio/webm")
        )

@app.websocket("/run_live")
async def websocket_endpoint(websocket: WebSocket):
    """Client websocket endpoint"""
    await websocket.accept()
    live_events, live_request_queue = await start_agent_session("user", is_audio=True)

    agent_to_client_task = asyncio.create_task(
        agent_to_client_messaging(websocket, live_events)
    )
    client_to_agent_task = asyncio.create_task(
        client_to_agent_messaging(websocket, live_request_queue)
    )

    tasks = [agent_to_client_task, client_to_agent_task]
    await asyncio.wait(tasks, return_when=asyncio.FIRST_EXCEPTION)

    live_request_queue.close()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)