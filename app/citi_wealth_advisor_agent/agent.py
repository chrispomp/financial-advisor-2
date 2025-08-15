import json
from google.adk.agents import Agent
from google.adk.tools import google_search, agent_tool
from google.adk.agents.callback_context import CallbackContext
from google.genai import types

# --- Tool Definition: No changes here ---
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
          "city": "Greenwich",
          "state": "CT",
          "zip": "06830"
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
        "total_assets": 8850000,
        "total_liabilities": 1400000,
        "assets": [
          {
            "category": "Cash & Equivalents",
            "institution": "Citi",
            "account_type": "Citigold Checking",
            "value": 150000
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
          {"area": "Education Planning", "action": "Schedule meeting to discuss benefits and funding of 529 College Savings Plans."},
          {"area": "Concentrated Stock", "action": "Present options for hedging or systematically selling vested company stock."},
          {"area": "Credit & Lending", "action": "Introduce mortgage specialists to review refinancing options."},
          {"area": "Estate Planning", "action": "Schedule introduction with a Trust & Estate specialist."}
        ]
      }
    }
    return json.dumps(profile_data, indent=2)

# --- Greeting Callback: Updated with debugging and error handling ---
def greeting_callback(callback_context: CallbackContext) -> types.Content | None:
    """
    Greets the user at the beginning of a session.
    """
    # 💡 DEBUG: This line will print all available attributes of the context object
    # to your server log. This will tell us the correct way to access the session.
    print(f"DEBUG: Attributes of callback_context are: {dir(callback_context)}")

    try:
        # Based on the InvocationContext class, the 'session' attribute
        # should exist directly on the context object.
        session = callback_context.session
        
        if len(session.events) == 1:
            client_profile = json.loads(get_client_profile())
            preferred_name = client_profile.get("preferred_name", "Chris")
            greeting_message = f"Hello {preferred_name}, welcome. How can I help you today?"
            return types.Content(parts=[types.Part(text=greeting_message)])

    except AttributeError as e:
        # If the 'session' attribute doesn't exist, this will prevent a crash
        # and print a helpful message to the server log.
        print(f"DEBUG: Could not find session attribute. Error: {e}")
        # The greeting will be skipped, but the agent will continue to function.
        return None
    
    # Returning None allows the agent to continue its normal processing on subsequent turns.
    return None

# --- Specialist Agents: No changes here ---
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

# --- Root Agent: No changes here ---
detailed_instructions = """
You are a friendly, professional, and concise AI Wealth Advisor for Citi's wealth management clients. You are always speaking with your client, Chris Evans.

**Your Primary Directive:** Your main purpose is to answer Chris's questions by delegating them to the correct specialist agent.

**Operational Logic & Tools**
1.  **Vision for Visual Questions:** If Chris asks a question about what you see (e.g., "what am I wearing?"), answer based on the video input.
2.  **Use `ClientProfileAgent` for Client Questions:** For any questions about Chris's finances, goals, family, or holdings, you MUST use the `ClientProfileAgent`.
3.  **Use `GoogleSearchAgent` for Everything Else:** For all other questions, including market news, general information, or anything not related to Chris's profile, you MUST use the `GoogleSearchAgent`.
4.  **Answer Directly:** Once you receive the information from the specialist agent, relay it clearly and concisely to Chris.
"""

root_agent = Agent(
   name="citi_wealth_advisor_agent",
   model="gemini-live-2.5-flash-preview-native-audio",
   description="An AI agent providing client-specific information and market news for a Citi Wealth Management advisor.",
   instruction=detailed_instructions,
   tools=[
       agent_tool.AgentTool(agent=profile_agent),
       agent_tool.AgentTool(agent=search_agent)
   ],
   before_agent_callback=greeting_callback
)