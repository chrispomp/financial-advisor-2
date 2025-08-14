"""Financial advisor: provide reasonable investment strategies"""

from google.adk.agents import LlmAgent
from google.adk.tools import google_search

from . import prompt

MODEL = "gemini-2.5-flash"


market_analyst = LlmAgent(
    name="market_analyst",
    model=MODEL,
    description=(
        "Guides users through a structured process to receive financial "
        "advice. Helps them analyze a market ticker and develop holistic "
        "investment/trading strategies."
    ),
    instruction=prompt.MARKET_ANALYST_PROMPT,
    output_key="market_analyst_output",
    tools=[
        google_search,
    ],
)

root_agent = market_analyst