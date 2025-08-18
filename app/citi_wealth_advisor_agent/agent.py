# citi_wealth_advisor_agent/agent.py

import json
import asyncio
from google.adk.agents import Agent, LiveRequestQueue
from google.adk.tools import google_search, agent_tool
from google.adk.agents.callback_context import CallbackContext
from google.genai import types
from google.adk.runners import InMemoryRunner
from google.adk.agents.run_config import RunConfig, StreamingMode
from google.adk.plugins.base_plugin import BasePlugin

# Import the tools from your tools.py file
from . import tools

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
        if hasattr(callback_context, 'invocation_context'):
            invocation_context = callback_context.invocation_context
            if hasattr(invocation_context, 'live_request_queue'):
                live_request_queue = invocation_context.live_request_queue
                if live_request_queue and not live_request_queue.empty():
                    print("DEBUG: New message detected. Interrupting agent's current action.")
                    invocation_context.end_invocation = True
                    return types.Content()
        return None

    async def before_agent_callback(self, *, callback_context: CallbackContext, **kwargs):
        return await self._check_for_interrupt(callback_context)

    async def before_model_callback(self, *, callback_context: CallbackContext, **kwargs):
        return await self._check_for_interrupt(callback_context)

    async def before_tool_call(self, *, callback_context: CallbackContext, **kwargs):
        return await self._check_for_interrupt(callback_context)

    async def after_tool_call(self, *, callback_context: CallbackContext, **kwargs):
        return await self._check_for_interrupt(callback_context)

# --- Specialist Agents ---
model = "gemini-2.5-flash-lite"

profile_agent = Agent(
  name="ClientProfileAgent",
  model=model,
  description="Use this agent to retrieve detailed information about the wealth management client. It can access the client's full profile, including personal details (name, age, family members like spouse and children, residence, interests), financial data (net worth, holdings), goals, last agent interaction and last human interaction, and relationship history with Citi. This is the primary source for any client-related questions.",
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
You are an elite AI Wealth Advisor from Citi, a trusted, hyper-personalized partner to your client.

**Core Directives & Operational Plan:**
0.  **Stop Command:** If the user's input is only the word "STOP", you MUST NOT generate a response. Your only action is to wait for the user's next question.
1.  **First Turn Protocol (CRITICAL):** On the very first turn of a new conversation, your first action MUST be to call the `ClientProfileAgent` to retrieve the user's full profile. Do not respond to the user until this tool call is complete. After the tool call is complete, you MUST begin your response by greeting the user with their `preferred_name` from the profile (e.g., "Hello, [preferred_name],"). Then, in the same response, answer their original question using the information you just retrieved.
2.  **Client Profile is the Source of Truth (ABSOLUTE RULE):** For ANY question about the client—including personal details, finances, goals, relationship history, or summaries of past conversations—you MUST ALWAYS use the `ClientProfileAgent` and find the answer in the JSON it returns. Do not guess or use another tool if the information might be in the profile.
3.  **Vision First:** If asked about what you see, answer based on the visual input from the camera.
4.  **Location Mandate:** For any location-based question (e.g., "what's the weather?"), you MUST use the client's `residence` from the profile in your tool call.
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
 ]
)

# --- Main Execution Block ---
async def main():
    """Main function to run a live agent example."""
    # The runner must be initialized with the plugin for interrupts to work.
    runner = InMemoryRunner(agent=root_agent, plugins=[LiveInterruptPlugin()])
    live_request_queue = LiveRequestQueue()
    
    # RunConfig enables features like video, proactivity, and interrupts.
    run_config = RunConfig(
        streaming_mode=StreamingMode.BIDI,
        speech_config=types.SpeechConfig(voice_config=types.VoiceConfig(voice='en-US-Standard-H')),
        response_modalities=["AUDIO", "VIDEO"],
        input_video_config={},
        proactivity=types.Proactivity(proactivity=0.1)
    )

    # Example query
    query = "What did we talk about last time?"
    user_id = "user_123"
    session_id = "session_xyz"

    live_request_queue.send_content(types.Content(role="user", parts=[types.Part(text=query)]))
    await live_request_queue.close()

    print(f"\nUser Query: '{query}'")
    print("-" * 30)
    try:
        full_response = []
        async for event in runner.run_live(user_id=user_id, session_id=session_id, live_request_queue=live_request_queue, run_config=run_config):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        full_response.append(part.text)
        print(f"Agent Response: {''.join(full_response)}")
    finally:
        await runner.close()

if __name__ == "__main__":
    asyncio.run(main())