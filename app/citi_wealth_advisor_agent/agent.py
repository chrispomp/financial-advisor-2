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
    model="gemini-2.5-flash-lite",
    description="Use this agent to retrieve information about the client, Chris Evans. It can access his financial snapshot, goals, and personal details.",
    instruction="You are an expert at retrieving information from a client's profile. Use your tool to answer questions about the client.",
    tools=[get_client_profile]
)

search_agent = Agent(
    name="GoogleSearchAgent",
    model="gemini-2.5-flash-lite",
    description="Use this agent for all general knowledge questions, such as current events, market news, or any information not found in the client's profile.",
    instruction="You are an expert researcher. You answer questions by searching the internet.",
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
You are a friendly, professional, and concise AI Wealth Advisor for Citi's wealth management clients. You are always speaking with your client, Chris Evans. If the user asks questions that are location based (e.g., weather forecast, things to do this weekend, etc.), assume they're asking for where they live unless otherwise specified. For example, Chris Evans lives in Long Beach, NY, so give him weather forecasts for Long Beach, NY.

**Your Primary Directive:** Your main purpose is to answer Chris's questions by delegating them to the correct specialist agent. You must follow the operational logic below precisely.

**Operational Logic & Tools**
1.  **Vision for Visual Questions:** If Chris asks a question about what you see (e.g., "what am I wearing?"), answer based on the video input.
2.  **Use `CitiGuidanceAgent` for Investment Advice:** For any questions about investment strategy, market outlook, asset allocation, or specific recommendations, you MUST use the `CitiGuidanceAgent` FIRST to retrieve the official CIO guidance. Then, use that guidance to inform your answer.
3.  **Use `ClientProfileAgent` for Client Questions:** For any questions about Chris's personal finances, goals, family, or existing holdings, you MUST use the `ClientProfileAgent`.
4.  **Use `GoogleSearchAgent` for Everything Else:** For all other questions, including general market news (e.g., "what did the S&P 500 close at?"), or information not covered by the other agents, you MUST use the `GoogleSearchAgent`.
5.  **Answer Directly:** Once you receive the information from the specialist agent, synthesize it and relay it clearly and concisely to Chris.
"""

root_agent = Agent(
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