import json
from google.adk.agents import Agent
from google.adk.tools import google_search, agent_tool
from google.adk.agents.callback_context import CallbackContext
from google.genai import types

# --- Tool Definition: Client Profile ---
def get_client_profile() -> str:
    """
    Retrieves the detailed profile for the wealth management client, Chris Evans.
    The data is returned as a JSON string for efficient processing.
    This should be the primary source of information for answering any client-related questions.
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
              {
                "ticker": "AAPL",
                "market_value": 150000,
                "shares": 649
              },
              {
                "ticker": "MSFT",
                "market_value": 140000,
                "shares": 268
              },
              {
                "ticker": "AMZN",
                "market_value": 130000,
                "shares": 562
              },
              {
                "ticker": "GOOGL",
                "market_value": 120000,
                "shares": 583
              },
              {
                "ticker": "JPM",
                "market_value": 110000,
                "shares": 378
              },
              {
                "ticker": "UNH",
                "market_value": 100000,
                "shares": 329
              }
            ]
          },
          {
            "category": "Investments",
            "account_type": "Employer 401(k)",
            "value": 1800000
          },
          {
            "category": "Investments",
            "account_type": "Vested Stock Options",
            "value": 950000,
            "notes": "Significant concentration in a single tech stock."
          },
          {
            "category": "Real Estate",
            "property_type": "Primary Residence",
            "value": 2500000
          }
        ],
        "liabilities": [
          {
            "type": "Primary Mortgage",
            "balance": 1400000,
            "notes": "30-year fixed at 3.25%."
          }
        ]
      },
      "goals_and_objectives": [
        {
          "priority": "Primary",
          "goal": "Retirement Planning",
          "details": {
            "target_age": 65,
            "desired_annual_income_post_tax": 350000
          }
        },
        {
          "priority": "Secondary",
          "goal": "Education Funding",
          "details": {
            "beneficiaries": ["Sophia Evans", "Liam Evans"],
            "college_timeline_years": {"Sophia": 2, "Liam": 5},
            "target_amount_per_child": 300000,
            "notes": "High-priority: No dedicated 529 plans established."
          }
        },
        {
          "priority": "Tertiary",
          "goal": "Estate Planning",
          "details": {
            "objective": "Efficient wealth transfer and tax burden minimization.",
            "notes": "Has basic wills but no advanced trust structures."
          }
        }
      ],
      "client_profile": {
        "risk_tolerance": "Moderate Growth",
        "investment_knowledge": "High",
        "investment_philosophy": "Prefers a diversified, long-term approach but lacks time for active management.",
        "interaction_preference": "Quarterly video reviews, one annual in-person review, and concise email summaries."
      },
      "citi_relationship": {
        "client_since": 2015,
        "actionable_opportunities": [
          {"area": "Consolidation", "action": "Propose plan to move competitor-held Money Market fund to Citi."},
          {"area": "Education Planning", "action": "Discuss benefits and funding of 529 College Savings Plans."},
          {"area": "Concentrated Stock", "action": "Present options for hedging or systematically selling vested company stock."},
          {"area": "Credit & Lending", "action": "Introduce mortgage specialists to review refinancing options."},
          {"area": "Estate Planning", "action": "Schedule introduction with a Trust & Estate specialist."}
        ]
      }
    }
    return json.dumps(profile_data, indent=2)

# --- Tool Definition: Citi Guidance ---
def get_citi_guidance() -> str:
    """
    Retrieves the official investment strategy and market outlook from Citi's Chief Investment Officer (CIO).
    This information should be used as the basis for all investment recommendations and market commentary.
    """
    guidance = {
        "cio_outlook_summary": "We maintain a moderately constructive outlook on global markets, balancing resilient economic growth against persistent inflationary pressures and geopolitical risks. We advocate for a strategy of quality and diversification, focusing on companies with strong balance sheets and durable earnings power. We are neutral on equities and moderately overweight fixed income, with a preference for high-quality corporate and municipal bonds. Alternative investments play a key role for diversification.",
        "date_of_guidance": "2025-08-12",
        "strategic_asset_allocation_moderate_risk": {
            "equities": {
                "total_allocation": "55%",
                "us_large_cap": "30%",
                "us_smid_cap": "5%",
                "international_developed": "15%",
                "emerging_markets": "5%"
            },
            "fixed_income": {
                "total_allocation": "35%",
                "investment_grade_corporate": "20%",
                "us_treasuries": "10%",
                "high_yield": "5%"
            },
            "alternatives": {
                "total_allocation": "10%",
                "notes": "Includes real estate, private credit, and commodities for inflation hedging and diversification."
            },
            "cash_and_equivalents": "0-5% (Tactical)"
        },
        "key_themes": [
            "Quality Over Growth: Prioritize companies with proven profitability and low debt.",
            "Yield is Back: Take advantage of attractive yields in high-quality fixed income.",
            "Diversify Globally: US market leadership may narrow; opportunities exist in international developed markets.",
            "Hedge Inflation: Real assets and alternative investments can provide a buffer against persistent inflation."
        ],
        "disclaimer": "This guidance is for informational purposes only and does not constitute a personalized investment recommendation. All investment decisions should be made in consultation with a qualified financial advisor based on the client's individual circumstances and risk tolerance."
    }
    return json.dumps(guidance, indent=2)

# --- Greeting Callback: ---
def greeting_callback(callback_context: CallbackContext) -> types.Content | None:
    """
    Greets the user at the beginning of a session.
    """
    try:
        session = callback_context.session
        if len(session.events) == 1:
            client_profile = json.loads(get_client_profile())
            preferred_name = client_profile.get("preferred_name", "Chris")
            greeting_message = f"Hello {preferred_name}, welcome. How can I help you today?"
            return types.Content(parts=[types.Part(text=greeting_message)])
    except AttributeError as e:
        print(f"DEBUG: Could not find session attribute. Error: {e}")
        return None
    return None

# --- Specialist Agents: ---
profile_agent = Agent(
    name="ClientProfileAgent",
<<<<<<< Updated upstream
    model="gemini-2.5-flash-lite",
    description="Use this agent to retrieve information about the client, Chris Evans. It can access all of his profile information like his financial snapshot, goals, and personal details. It can provide things like current stock holdings, total assets, total liabilities, etc.",
    instruction="You are an expert at retrieving information from a client's profile. Use your tool to answer questions about the client.",
    tools=[get_client_profile]
=======
    model=model,
    description="Use this agent to retrieve the client's complete profile, including personal details, financial data, goals, and relationship history.",
    tools=[tools.get_client_profile]
)

guidance_agent = Agent(
    name="GuidanceAgent",
    model=model,
    description="Retrieves the latest investment strategy and market outlook from the firm's Chief Investment Officer.",
    tools=[tools.get_guidance]
>>>>>>> Stashed changes
)

search_agent = Agent(
    name="GoogleSearchAgent",
<<<<<<< Updated upstream
    model="gemini-2.5-flash-lite",
    description="Use this agent for all general knowledge questions, such as current events, market news, or any information not found in the client's profile.",
    instruction="You are an expert researcher. You answer questions by searching the internet.",
=======
    model=model,
    description="Your primary tool for accessing real-time, external information from the internet. Use this for timely financial data, such as latest stock performance, overall market trends, and breaking industry news. It is also the go-to tool for all general and lifestyle questions, including weather forecasts, researching local restaurants or activities, and checking sports scores. If the information is not in the client's profile or in the guidance, use this agent.",
>>>>>>> Stashed changes
    tools=[google_search]
)

# --- Specialist Agent: Citi Guidance ---
guidance_agent = Agent(
    name="CitiGuidanceAgent",
    model="gemini-2.5-flash-lite",
    description="Use this agent to get the official investment strategy and market outlook from Citi's Chief Investment Officer (CIO).",
    instruction="You are an expert at retrieving and presenting official investment guidance. Use your tool to provide the current CIO outlook.",
    tools=[get_citi_guidance]
)


# --- Root Agent: ---
detailed_instructions = """
<<<<<<< Updated upstream
You are a friendly, professional, and concise AI Wealth Advisor for Citi's wealth management clients. You are always speaking with your client, Chris Evans. If the user asks questions that are location based (e.g., weather forecast, things to do this weekend, etc.), assume they're asking for where they live unless otherwise specified. For example, Chris Evans lives in Long Beach, NY, so give him weather forecasts for Long Beach, NY.
=======
You are an elite AI Wealth Advisor. You are a trusted, hyper-personalized, and conversational partner to your client.

### Persona & Tone
- **Pace and Tone:** Speak at a brisk, efficient pace while maintaining a friendly, professional, and clear tone. Avoid being overly robotic or unnaturally slow.
- **Conciseness:** Provide direct and concise answers. Avoid unnecessary conversational fillers.
- **Data-Driven Responses:** When discussing financial performance, you MUST prioritize providing specific metrics (e.g., "up 1.5%" or "down $5.20") over vague descriptions (e.g., "up slightly").

### Core Logic

1.  **First Turn Protocol (ABSOLUTE RULE):** On the very first turn of a new conversation, your first and ONLY action MUST be to call the `ClientProfileAgent` to retrieve the user's full profile. Do not say anything to the user yet. After the tool call returns, your first response MUST greet the user by their `preferred_name` and then address their original question.

2.  **Stateful Memory (CRITICAL):** After the first turn, the complete client profile is stored in your memory. For ALL subsequent questions about the client (personal details, finances, goals), you MUST use this stored information. DO NOT call the `ClientProfileAgent` again unless the user asks you to refresh their data.

3.  **Tool Usage Hierarchy:**
    a.  First: Use the stored client profile from your memory.
    b.  Second: For market outlook or investment strategy, use the `GuidanceAgent`.
    c.  Last Resort: For real-time news or external information, use the `GoogleSearchAgent`.

4.  **Synthesize, Don't Recite:** Never just output raw data. Synthesize information into a single, natural-sounding response.

5.  **Vision & Stop Commands:** If asked about what you see, use visual input. If the user says "STOP", cease your response.

6.  **Personalization (Location & Interests):** For any query that can be personalized, you MUST use the stored client profile to inform your `GoogleSearchAgent` call.
    a.  **Location-Based Queries:** For questions about weather, restaurants, or local events, you MUST use the client's `residence` from the stored profile as the location unless the user specifies a different one.
    b.  **Interest-Based Queries:** For subjective recommendations (e.g., "what should I do this weekend?"), you MUST use the `personal_interests` from the stored profile to create a more relevant and personalized query.

### Specific Briefing Protocols

7.  **Stock Performance Protocol:** If the user asks a general question about how their stocks are performing (e.g., "how are my stocks doing?", "what's the update on my holdings?"), you MUST follow this two-step process:
    a. Access the `top_holdings` list from the `financial_snapshot_usd` section of the stored client profile in your memory.
    b. Call the `GoogleSearchAgent` with the list of stock tickers to find their latest performance data (e.g., daily change, current price).
    c. Synthesize the results into a clear, metric-driven summary for the client.

8.  **Market Briefing Protocol:** If the user explicitly asks for a "market briefing" or "market update," call the `GoogleSearchAgent` to:
    a.  Provide the latest performance data for major market indices like the S&P 500 and NASDAQ.
    b.  Provide the top news stories that may impact financial markets.
>>>>>>> Stashed changes

**Your Primary Directive:** Your main purpose is to answer Chris's questions by delegating them to the correct specialist agent. You must follow the operational logic below precisely.

**Operational Logic & Tools**
1.  **Vision for Visual Questions:** If Chris asks a question about what you see (e.g., "what am I wearing?"), answer based on the video input.
2.  **Use `CitiGuidanceAgent` for Investment Advice:** For any questions about investment strategy, market outlook, asset allocation, or specific recommendations, you MUST use the `CitiGuidanceAgent` FIRST to retrieve the official CIO guidance. Then, use that guidance to inform your answer.
3.  **Use `ClientProfileAgent` for Client Questions:** For any questions about Chris's personal finances, goals, family, or existing holdings, including investments, stocks, or the portfolio, you MUST use the `ClientProfileAgent`.
4.  **Use `GoogleSearchAgent` for Everything Else:** For all other questions, including general market news (e.g., "what did the S&P 500 close at?"), or information not covered by the other agents, you MUST use the `GoogleSearchAgent`.
5.  **Answer Directly:** Once you receive the information from the specialist agent, synthesize it and relay it clearly and concisely to Chris.
"""

root_agent = Agent(
<<<<<<< Updated upstream
   name="citi_wealth_advisor_agent",
   model="gemini-live-2.5-flash-preview-native-audio",
   description="An AI agent providing client-specific information and market news for a Citi Wealth Management advisor.",
   instruction=detailed_instructions,
   tools=[
       agent_tool.AgentTool(agent=profile_agent),
       agent_tool.AgentTool(agent=search_agent),
       agent_tool.AgentTool(agent=guidance_agent)
   ],
   before_agent_callback=greeting_callback
)
=======
    name="wealth_advisor_agent",
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
        speech_config=types.SpeechConfig(
            voice_config=types.VoiceConfig(
                voice='Puck',
                speaking_rate=1.5
            )
        ),
        response_modalities=["AUDIO", "VIDEO"],
        input_video_config={},
        proactivity=types.Proactivity(proactivity=1.0)
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
>>>>>>> Stashed changes
