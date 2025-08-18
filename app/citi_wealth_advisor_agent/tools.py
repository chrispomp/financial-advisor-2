# citi_wealth_advisor_agent/tools.py

import json

def get_client_profile() -> str:
    """
    Retrieves the comprehensive profile for the wealth management client.
    This is the single source of truth for all client-related information.
    """
    profile_data = {
      "profile_id": "CEVANS-2025-0815",
      "client_name": "Christopher M. Evans",
      "preferred_name": "Chris",
      "relationship_manager": "Jane Foster",
      "personal_info": {
        "age": 43,
        "birthday": "1982-08-16",
        "occupation": "Senior Director, Product Management",
        "employer": "Global Tech Firm",
        "residence": {"city": "Long Beach", "state": "NY"},
        "family": {
          "marital_status": "Married",
          "spouse": {"name": "Emily Evans", "age": 41, "occupation": "Anesthesiologist"},
          "dependents": [
            {"name": "Sophia", "relation": "Daughter", "age": 16, "interests": "College applications, soccer"},
            {"name": "Liam", "relation": "Son", "age": 13, "interests": "Video games, learning to code"}
          ]
        },
        "personal_interests": "The client is a sports fan, specifically of the New York Jets football team. He has a strong interest in technology, including AI and machine learning, which aligns with his career. For leisure, he enjoys listening to punk rock music and exploring the local culinary scene by trying new restaurants."
      },
      "financial_snapshot_usd": {
        "net_worth": 8250000,
        "assets": [
          {"category": "Cash & Equivalents", "account_type": "Citigold Checking", "value": 1150000},
          {"category": "Investments", "account_type": "Brokerage Account", "value": 3200000, "top_holdings": ["AAPL", "MSFT", "GOOGL"]}
        ],
        "recent_activity": {
          "description": "Unusually large cash deposit of $800,000, which may indicate a significant life event (e.g., inheritance, property sale).",
          "date": "2025-08-14"
        }
      },
      "goals_and_objectives": [
        {"priority": "Primary", "goal": "Retirement Planning", "target_age": 65},
        {"priority": "Secondary", "goal": "Education Funding for children"}
      ],
      "citi_relationship": {
        "client_since": 2015,
        "last_human_contact": {"date": "2025-07-15", "topic": "Quarterly portfolio review with Jane Foster."},
        "last_agent_interaction": {
            "date": "2025-08-17",
            "summary": "Client asked about their portfolio performance and inquired about local activities for the upcoming weekend. The agent provided details on their top holdings and suggested attending the New York Jets game."
        },
        "personalized_recommendations": [
          {"area": "Wealth Planning", "action": "Discuss investment strategies for the recent large cash deposit."},
          {"area": "Credit & Lending", "action": "Client does not have a Citi credit card. They are an excellent candidate for the Citi Strata Elite Card based on their net worth and spending patterns."},
          {"area": "Education Planning", "action": "Discuss benefits and funding of 529 College Savings Plans for Sophia and Liam."}
        ]
      }
    }
    return json.dumps(profile_data, indent=2)

def get_citi_guidance() -> str:
    """
    Retrieves the official investment strategy and market outlook from Citi's CIO.
    This is the basis for all investment recommendations and market commentary.
    """
    guidance = {
        "cio_outlook_summary": "We maintain a moderately constructive outlook on global markets, balancing resilient economic growth against persistent inflationary pressures. We advocate for a strategy of quality and diversification, focusing on companies with strong balance sheets and durable earnings power.",
        "date_of_guidance": "2025-08-12",
        "strategic_asset_allocation_moderate_risk": {
            "equities": {"total_allocation": "55%", "us_large_cap": "30%", "international_developed": "15%", "emerging_markets": "10%"},
            "fixed_income": {"total_allocation": "35%", "investment_grade_corporate": "20%", "us_treasuries": "15%"},
            "alternatives": {"total_allocation": "10%", "notes": "Real estate, private credit for diversification."}
        },
        "key_themes": [
            "Quality Over Growth: Prioritize companies with proven profitability and low debt.",
            "The Return of Yield: Take advantage of attractive yields in high-quality fixed income.",
            "Go Global for Growth: Opportunities exist in international developed markets as US market leadership may narrow."
        ],
        "disclaimer": "This guidance is for informational purposes only and does not constitute a personalized investment recommendation."
    }
    return json.dumps(guidance, indent=2)