import json
import asyncio
import queue
import threading
import time
import wave
from io import BytesIO

import cv2
import numpy as np
import pyaudio
from google.adk.agents import Agent, LiveRequestQueue
from google.adk.agents.callback_context import CallbackContext
from google.adk.agents.run_config import RunConfig, StreamingMode
from google.adk.plugins.base_plugin import BasePlugin
from google.adk.runners import Runner, InMemoryRunner
from google.adk.tools import agent_tool, google_search
from google.genai import types
from PIL import Image


# --- Real-time I/O Handlers ---

# Constants for audio stream
RATE = 16000
CHUNK = int(RATE / 10)  # 100ms

class AudioPlayer:
    """Plays back audio stream."""

    def __init__(self, audio_queue: queue.Queue):
        self._audio_queue = audio_queue
        self._p = pyaudio.PyAudio()
        self._stream = self._p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=24000,  # The API documentation specifies 24kHz for output audio
            output=True,
        )
        self._thread = threading.Thread(target=self._play_audio, daemon=True)
        self._running = False

    def start(self):
        """Starts the audio playback thread."""
        self._running = True
        self._thread.start()
        print("INFO: Audio player started.")

    def stop(self):
        """Stops the audio playback and cleans up resources."""
        self._running = False
        # Give the thread a moment to finish processing its current item
        self._thread.join(timeout=2)
        self._stream.stop_stream()
        self._stream.close()
        self._p.terminate()
        print("INFO: Audio player stopped.")

    def add_data(self, data: bytes):
        """Adds audio data to the playback queue."""
        self._audio_queue.put(data)

    def clear_queue(self):
        """Clears the audio playback queue."""
        with self._audio_queue.mutex:
            self._audio_queue.queue.clear()
        print("DEBUG: Audio playback queue cleared for interruption.")

    def _play_audio(self):
        """The target function for the playback thread."""
        while self._running:
            try:
                data = self._audio_queue.get(timeout=1)
                self._stream.write(data)
            except queue.Empty:
                # If the queue is empty, just continue waiting
                if not self._running:
                    break
                continue

class AudioCapturer:
    """Captures audio from the microphone."""

    def __init__(self, audio_queue: queue.Queue):
        self._audio_queue = audio_queue
        self._p = pyaudio.PyAudio()
        self._stream = self._p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK,
        )
        self._thread = threading.Thread(target=self._record_audio, daemon=True)
        self._running = False

    def start(self):
        """Starts the audio recording thread."""
        self._running = True
        self._thread.start()
        print("INFO: Audio capturer started.")

    def stop(self):
        """Stops audio recording and cleans up."""
        self._running = False
        self._thread.join(timeout=2)
        self._stream.stop_stream()
        self._stream.close()
        self._p.terminate()
        print("INFO: Audio capturer stopped.")

    def _record_audio(self):
        """The target function for the recording thread."""
        while self._running and not self._stream.is_stopped():
            try:
                data = self._stream.read(CHUNK, exception_on_overflow=False)
                self._audio_queue.put(data)
            except IOError as e:
                print(f"ERROR: Audio recording error: {e}")
                self._running = False
                break

class VideoCapturer:
    """Captures video from the camera."""

    def __init__(self, video_queue: queue.Queue, resolution=(640, 480), fps=15):
        self._video_queue = video_queue
        self._resolution = resolution
        self._fps = fps
        self._cap = cv2.VideoCapture(0)
        if not self._cap.isOpened():
            raise IOError("Cannot open webcam")
        self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, self._resolution[0])
        self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self._resolution[1])
        self._cap.set(cv2.CAP_PROP_FPS, self._fps)
        self._thread = threading.Thread(target=self._record_video, daemon=True)
        self._running = False

    def start(self):
        """Starts the video recording thread."""
        self._running = True
        self._thread.start()
        print("INFO: Video capturer started.")

    def stop(self):
        """Stops video recording and releases the camera."""
        self._running = False
        self._thread.join(timeout=2)
        self._cap.release()
        print("INFO: Video capturer stopped.")

    def _record_video(self):
        """The target function for the video recording thread."""
        while self._running:
            ret, frame = self._cap.read()
            if not ret:
                print("ERROR: Failed to grab frame from camera.")
                time.sleep(0.1)
                continue

            # Encode frame as JPEG
            ret, buffer = cv2.imencode('.jpg', frame)
            if not ret:
                print("ERROR: Failed to encode frame.")
                continue

            self._video_queue.put(buffer.tobytes())

            # Let the camera's FPS setting handle the rate
            # A small sleep can prevent this loop from pegging a CPU core if frame grabbing is too fast
            time.sleep(1 / (self._fps * 2))


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

# --- Main Execution (New Real-time Implementation) ---
DEFAULT_VOICE = 'Aoede'

async def run_live_agent(user_id: str, session_id: str, voice_name: str = DEFAULT_VOICE):
    """Runs the agent in a live, bidirectional streaming session."""

    # 1. Create queues for I/O
    audio_input_queue = queue.Queue()
    video_input_queue = queue.Queue()
    audio_output_queue = queue.Queue()

    # 2. Initialize and start I/O handlers
    audio_player = AudioPlayer(audio_output_queue)
    audio_capturer = AudioCapturer(audio_input_queue)
    video_capturer = None
    try:
        video_capturer = VideoCapturer(video_input_queue)
    except IOError as e:
        print(f"WARNING: Could not initialize video capturer: {e}. Running in audio-only mode.")

    audio_player.start()
    audio_capturer.start()
    if video_capturer:
        video_capturer.start()

    # 3. Setup runner and request queue
    runner = InMemoryRunner(agent=root_agent)
    live_request_queue = LiveRequestQueue()

    # 4. Configure the run
    run_config = RunConfig(
        streaming_mode=StreamingMode.BIDI,
        speech_config=types.SpeechConfig(voice_config=types.VoiceConfig(voice=voice_name)),
        response_modalities=["AUDIO"],
        output_audio_transcription={},  # Enable for debugging
        input_video_config={"enabled": bool(video_capturer)},  # Enable video if capturer is available
        media_resolution=types.MediaResolution.MEDIA_RESOLUTION_LOW,
    )

    # Coroutine to handle sending data to the agent
    async def send_data():
        print("INFO: Starting to send media stream...")
        while True:
            parts = []
            # Get audio data if available
            try:
                audio_chunk = audio_input_queue.get(block=False)
                parts.append(types.Part(inline_data=types.Blob(
                    data=audio_chunk,
                    mime_type=f"audio/pcm;rate={RATE}"
                )))
            except queue.Empty:
                pass  # No audio data

            # Get video data if available
            if video_capturer:
                try:
                    video_chunk = video_input_queue.get(block=False)
                    parts.append(types.Part(inline_data=types.Blob(
                        data=video_chunk,
                        mime_type="image/jpeg"
                    )))
                except queue.Empty:
                    pass  # No video data

            if parts:
                content = types.Content(role="user", parts=parts)
                live_request_queue.send_content(content)

            await asyncio.sleep(0.05)

    # Coroutine to handle receiving data from the agent
    async def receive_data():
        print("INFO: Starting to receive server events...")
        try:
            async for event in runner.run_live(
                user_id=user_id,
                session_id=session_id,
                live_request_queue=live_request_queue,
                run_config=run_config
            ):
                if event.server_content:
                    if event.server_content.interrupted:
                        print("DEBUG: Agent generation interrupted by user.")
                        audio_player.clear_queue()
                    if event.server_content.output_transcription:
                        print(f"Agent Transcript: {event.server_content.output_transcription.text}")

                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.inline_data and part.inline_data.mime_type.startswith("audio/"):
                            audio_player.add_data(part.inline_data.data)
                        if part.text:
                            print(f"Agent Response (Text): {part.text}")
        except Exception as e:
            print(f"ERROR: An error occurred during the live session: {e}")

    # Main execution logic
    try:
        print("\nStarting real-time conversation. Press Ctrl+C to exit.")
        send_task = asyncio.create_task(send_data())
        receive_task = asyncio.create_task(receive_data())
        await asyncio.gather(send_task, receive_task)
    except asyncio.CancelledError:
        print("\nINFO: Conversation cancelled.")
    except KeyboardInterrupt:
        print("\nINFO: Exiting conversation.")
    finally:
        print("INFO: Cleaning up resources...")
        audio_capturer.stop()
        if video_capturer:
            video_capturer.stop()
        audio_player.stop()
        await runner.close()
        await live_request_queue.close()
        print("INFO: Cleanup complete. Goodbye.")


async def main():
    # Replace with your actual user_id and a unique session_id
    user_id = "test-user-123"
    session_id = f"session-{int(time.time())}"
    await run_live_agent(user_id=user_id, session_id=session_id)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"FATAL: Top-level error: {e}")
