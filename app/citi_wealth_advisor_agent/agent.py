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

# --- State Management Logic ---
def save_profile_to_state(*, callback_context: CallbackContext):
    """
    After 'get_client_profile' is called, this saves the result into the
    session_state to be reused across the conversation.
    """
    tool_call_event = callback_context.tool_code_execution
    if not tool_call_event or tool_call_event.tool_name != "get_client_profile":
        return

    try:
        profile_data = json.loads(tool_call_event.tool_result)
        session_state = callback_context.session_state
        if "client_context" not in session_state:
            session_state["client_context"] = profile_data
            print(f"DEBUG: Client profile for '{profile_data.get('preferred_name')}' saved to session state.")
    except Exception as e:
        print(f"DEBUG: ERROR saving profile to state: {e}")

# --- Live Interrupt & State Management Plugin ---
class LiveInterruptPlugin(BasePlugin):
    """
    A plugin to handle both live interrupts and state management.
    """
    def __init__(self):
        super().__init__(name="live_interrupt_plugin")

    async def _check_for_interrupt(self, callback_context: CallbackContext):
        """Checks the live request queue for interrupts."""
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
        """
        This method now handles both saving the profile to state AND checking for interrupts.
        """
        save_profile_to_state(callback_context=callback_context)
        return await self._check_for_interrupt(callback_context)

# --- Specialist Agents ---
model = "gemini-2.5-flash-lite"

profile_agent = Agent(
    name="ClientProfileAgent",
    model=model,
    description="Use this agent to retrieve the client's complete profile, including personal details, financial data, goals, and relationship history.",
    tools=[tools.get_client_profile]
)

guidance_agent = Agent(
    name="CitiGuidanceAgent",
    model=model,
    description="Retrieves the latest investment strategy and market outlook from Citi's CIO.",
    tools=[tools.get_citi_guidance]
)

search_agent = Agent(
    name="GoogleSearchAgent",
    model=model,
    description="Used for general knowledge, current events, or real-time market news.",
    tools=[google_search]
)

# --- Root Agent ---
detailed_instructions = """
You are an elite AI Wealth Advisor from Citi. You are a trusted, hyper-personalized, and conversational partner to your client.

### Core Logic

1.  **First Turn Protocol (ABSOLUTE RULE):** On the very first turn of a new conversation, your first and ONLY action MUST be to call the `ClientProfileAgent` to retrieve the user's full profile. Do not say anything to the user yet. After the tool call returns, your first response MUST greet the user by their `preferred_name` and then address their original question.

2.  **Stateful Memory (CRITICAL):** After the first turn, the complete client profile is stored in your memory. For ALL subsequent questions about the client (personal details, finances, goals), you MUST use this stored information. DO NOT call the `ClientProfileAgent` again unless the user asks you to refresh their data.

3.  **Tool Usage Hierarchy:**
    a.  First: Use the stored client profile from your memory.
    b.  Second: For market outlook or investment strategy, use the `CitiGuidanceAgent`.
    c.  Last Resort: For real-time news or external information, use the `GoogleSearchAgent`.

4.  **Synthesize, Don't Recite:** Never just output raw data. Synthesize information into a single, natural-sounding response.

5.  **Vision & Stop Commands:** If asked about what you see, use visual input. If the user says "STOP", cease your response.

### Conversational Flow & Briefings

6.  **Personalization:** For any query that can be personalized (local activities, weather), you MUST use the `residence` and `personal_interests` from the stored profile to inform your `GoogleSearchAgent` call.

7.  **Briefing Protocols:** When asked for a "personal briefing," "market briefing," or "stock performance," use the relevant data from your stored profile and the appropriate specialist agent (`CitiGuidanceAgent` or `GoogleSearchAgent`) to construct a comprehensive answer.
"""

root_agent = Agent(
    name="citi_wealth_advisor_agent",
    model="gemini-live-2.5-flash-preview-native-audio",
    description="An AI agent providing personalized, client-specific guidance and market news.",
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
    # The runner must be initialized with the plugin to handle interrupts and state.
    runner = InMemoryRunner(agent=root_agent, plugins=[LiveInterruptPlugin()])
    run_config = RunConfig(
        streaming_mode=StreamingMode.BIDI,
        speech_config=types.SpeechConfig(voice_config=types.VoiceConfig(voice='en-US-Standard-H')),
        response_modalities=["AUDIO", "VIDEO"],
        input_video_config={},
        proactivity=types.Proactivity(proactivity=0.1)
    )

    query = "What is my daughter's age?"
    user_id = "user_123"
    session_id = "session_def"

    live_request_queue = LiveRequestQueue()
    live_request_queue.send_content(types.Content(role="user", parts=[types.Part(text=query)]))
    # Add a second turn to test state
    await asyncio.sleep(4) # Simulate pause in conversation
    live_request_queue.send_content(types.Content(role="user", parts=[types.Part(text="And how old is my son?")]))
    await live_request_queue.close()


    print(f"\nUser Queries Sent...")
    print("-" * 30)
    try:
        full_response = []
        async for event in runner.run_live(user_id=user_id, session_id=session_id, live_request_queue=live_request_queue, run_config=run_config):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        print(f"Agent Response Chunk: {part.text}")
                        full_response.append(part.text)
        print(f"\nFull Agent Response: {''.join(full_response)}")
    finally:
        await runner.close()

if __name__ == "__main__":
    asyncio.run(main())