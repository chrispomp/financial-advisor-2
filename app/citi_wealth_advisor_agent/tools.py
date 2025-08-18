# citi_wealth_advisor_agent/tools.py

import json

def get_preferred_name() -> str:
    """
    Retrieves the client's preferred name.
    """
    profile_data = {
      "preferred_name": "Chris",
    }
    return json.dumps(profile_data, indent=2)

def get_client_net_worth() -> str:
    """
    Retrieves the client's total net worth.
    """
    profile_data = {
      "net_worth": 7450000
    }
    return json.dumps(profile_data, indent=2)

def get_client_goals() -> str:
    """
    Retrieves the client's stated financial goals.
    """
    profile_data = {
      "goals_and_objectives": [
        {"priority": "Primary", "goal": "Retirement Planning"},
        {"priority": "Secondary", "goal": "Education Funding"}
      ]
    }
    return json.dumps(profile_data, indent=2)

def get_client_dependents() -> str:
    """
    Retrieves the names and ages of the client's dependents.
    """
    profile_data = {
      "family": {"dependents": [{"name": "Sophia", "age": 16}, {"name": "Liam", "age": 13}]}
    }
    return json.dumps(profile_data, indent=2)

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
      "summary": "High-earning tech executive focused on long-term growth. Key opportunities include asset consolidation and advanced financial planning.",
      "personal_info": {
        "age": 45,
        "occupation": "Senior Director, Product Management",
        "residence": {"city": "Long Beach", "state": "NY"},
        "family": {"dependents": [{"name": "Sophia", "age": 16}, {"name": "Liam", "age": 13}]}
      },
      "financial_snapshot_usd": {
        "net_worth": 7450000,
        "assets": [
          {"category": "Cash & Equivalents", "institution": "Citi", "value": 350000},
          {"category": "Investments", "institution": "Citi", "account_type": "Brokerage Account", "value": 3200000}
        ]
      },
      "goals_and_objectives": [
        {"priority": "Primary", "goal": "Retirement Planning"},
        {"priority": "Secondary", "goal": "Education Funding"}
      ],
      "citi_relationship": {
        "client_since": 2015,
        "actionable_opportunities": [
          {"area": "Consolidation", "action": "Propose plan to move competitor-held Money Market fund to Citi."},
          {"area": "Education Planning", "action": "Discuss benefits and funding of 529 College Savings Plans."}
        ]
      }
    }
    return json.dumps(profile_data, indent=2)

def get_citi_guidance() -> str:
    """
    Retrieves the official investment strategy and market outlook from Citi's Chief Investment Officer (CIO).
    This information should be used as the basis for all investment recommendations and market commentary.
    """
    guidance = {
        "cio_outlook_summary": "We maintain a moderately constructive outlook on global markets, balancing resilient economic growth against persistent inflationary pressures. We advocate for a strategy of quality and diversification.",
        "date_of_guidance": "2025-08-12",
        "key_themes": [
            "Quality Over Growth: Prioritize companies with proven profitability and low debt.",
            "Yield is Back: Take advantage of attractive yields in high-quality fixed income.",
            "Diversify Globally: Opportunities exist in international developed markets."
        ],
        "disclaimer": "This guidance is for informational purposes only and does not constitute a personalized investment recommendation."
    }
    return json.dumps(guidance, indent=2)