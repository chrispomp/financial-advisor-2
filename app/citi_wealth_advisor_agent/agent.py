import json
from google.adk.agents import Agent
from google.adk.tools import google_search, agent_tool

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

# 1. Define the Specialist Agent for Client Profiles
profile_agent = Agent(
    name="ClientProfileAgent",
    model="gemini-2.5-flash-lite",
    description="Use this agent to retrieve information about the client, Chris Evans. It can access his financial snapshot, goals, and personal details.",
    instruction="You are an expert at retrieving information from a client's profile. Use your tool to answer questions about the client.",
    tools=[get_client_profile]
)

# 2. Define the Specialist Agent for Google Search
search_agent = Agent(
    name="GoogleSearchAgent",
    model="gemini-2.5-flash-lite",
    description="Use this agent for all general knowledge questions, such as current events, market news, or any information not found in the client's profile.",
    instruction="You are an expert researcher. You answer questions by searching the internet.",
    tools=[google_search]
)

# 3. Define the Root Agent (Orchestrator)
# This agent's instructions tell it HOW to use the other agents as tools.
detailed_instructions = """
You are a friendly, professional, and concise AI Wealth Advisor for Citi's wealth management clients.
You have a camera and can see the user. When asked, describe what you see. You are always talking to Chris Evans.

**Your Primary Directive:** You have access to two specialist agents: one for client profile information and one for Google Search. Your main purpose is to delegate the user's question to the correct specialist.

**Operational Logic & Tools**
1.  **Vision for Visual Questions:** If the user asks a question about what you see (e.g., "what am I wearing?"), answer based on the video input.
2.  **Use `ClientProfileAgent` for Client Questions:** For any questions about the client, Chris Evans, you MUST use the `ClientProfileAgent`. This includes questions about his finances, goals, family, or holdings.
3.  **Use `GoogleSearchAgent` for Everything Else:** For all other questions, including market news, general information, or anything not related to Chris's profile, you MUST use the `GoogleSearchAgent`.
4.  **Answer Directly:** Once you receive the information from the specialist agent, relay it to the user.
"""

root_agent = Agent(
   name="citi_wealth_advisor_agent",
   # This model is correct for the root agent, as it handles the live user interaction.
   model="gemini-live-2.5-flash-preview-native-audio",
   description="An AI agent providing client-specific information and market news for a Citi Wealth Management advisor.",
   instruction=detailed_instructions,
   # Wrap the specialist agents using AgentTool to make them usable by the root agent.
   tools=[
       agent_tool.AgentTool(agent=profile_agent),
       agent_tool.AgentTool(agent=search_agent)
   ]
)