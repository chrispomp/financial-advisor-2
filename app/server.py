import asyncio
import websockets
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from google.adk.agents.run_config import RunConfig, StreamingMode
from google.adk.agents import LiveRequestQueue
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# --- Import your root_agent from your existing agent file ---
# Make sure your agent file is in a package (a folder with an __init__.py)
from citi_wealth_advisor_agent.agent import root_agent

# --- Configuration ---
APP_NAME = "citi_wealth_advisor_agent"
USER_ID = "user" # Using a static user_id for this example
SESSION_ID = "session" # Using a static session_id for this example

# --- ADK Setup ---
# The session service keeps track of the conversation history
session_service = InMemorySessionService()

# The runner is responsible for executing the agent
runner = Runner(
    agent=root_agent,
    app_name=APP_NAME,
    session_service=session_service,
)

# --- FastAPI Web Server ---
# This creates the main application instance
app = FastAPI()

# This is the core of our solution.
# We create a RunConfig to enable proactivity, which allows for interruptions.
run_config_with_interrupts = RunConfig(
    streaming_mode=StreamingMode.BIDI,
    # 💡 This is the key setting to enable interruptions!
    proactivity=types.ProactivityConfig(enabled=True),
    response_modalities=[types.Modality.AUDIO, types.Modality.TEXT],
)

@app.websocket("/run_live")
async def websocket_endpoint(websocket: WebSocket):
    """This function handles the live, bidirectional communication."""
    await websocket.accept()
    print("WebSocket connection accepted.")

    live_request_queue = LiveRequestQueue()

    try:
        # Create the user's session if it doesn't exist
        try:
            await session_service.get_session(
                app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
            )
        except Exception:
            print("Session not found, creating a new one.")
            await session_service.create_session(
                app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
            )

        # This task runs the agent and listens for responses
        async def run_agent():
            print("Starting agent run...")
            async for event in runner.run_live(
                user_id=USER_ID,
                session_id=SESSION_ID,
                live_request_queue=live_request_queue,
                run_config=run_config_with_interrupts, # Use our new config
            ):
                if event.content:
                    await websocket.send_json(event.to_dict())
            print("Agent run finished.")

        # This task listens for incoming messages from the client (your browser)
        async def forward_to_agent():
            while True:
                data = await websocket.receive_bytes()
                live_request_queue.send_realtime(
                    types.Blob(data=data, mime_type="audio/webm")
                )

        # Run both tasks concurrently
        agent_task = asyncio.create_task(run_agent())
        forwarding_task = asyncio.create_task(forward_to_agent())

        await asyncio.gather(agent_task, forwarding_task)

    except WebSocketDisconnect:
        print("Client disconnected.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        live_request_queue.close()
        print("WebSocket connection closed.")

# --- To run this server ---
# 1. Make sure you are in the 'app' directory in your terminal.
# 2. Run the command: uvicorn server:app --reload