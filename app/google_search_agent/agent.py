from google.adk.agents import Agent
from google.adk.tools import google_search

root_agent = Agent(
   name="basic_search_agent",
   # Using the live model you have configured in your project
   model="gemini-2.0-flash-live-preview-04-09",
   description="Agent to answer questions using Google Search.",
   instruction="You are an expert researcher. You always stick to the facts.",
   tools=[google_search]
)