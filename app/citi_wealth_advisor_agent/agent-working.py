# agent.py

from google.adk.agents import Agent

def get_client_profile() -> str:
    """
    Retrieves the detailed profile for the wealth management client, Chris Evans.
    This should be the primary source of information for answering any client-related questions.
    """
    return """
    Citi Private Bank - Client Profile: Christopher Evans
    Date: August 15, 2025
    Relationship Manager: Jane Foster
    Status: Active, High-Potential

    1. Client Summary
    Christopher "Chris" Evans is a 45-year-old technology executive residing in Greenwich, CT with his wife, Dr. Emily Evans, and their two teenage children. As a high-earning, time-poor professional, Chris is focused on strategic, long-term growth to secure a comfortable retirement and fund his children's education. He is digitally savvy and prefers efficient, data-driven advice but values a personal relationship for major financial and life decisions. The primary opportunity is to deepen the relationship by consolidating outside assets and providing comprehensive financial planning, including trust and estate services.

    2. Personal Information
    Client Name: Christopher M. Evans
    Age: 45
    Occupation: Senior Director, Product Management (Global Tech Firm)
    Marital Status: Married
    Spouse: Dr. Emily Evans, 44 (Anesthesiologist, Stamford Hospital)
    Dependents:
    - Sophia Evans (Daughter, 16)
    - Liam Evans (Son, 13)
    Residence: Greenwich, CT 06830

    3. Financial Snapshot (Household)
    Category                Asset/Liability         Value (USD)     Notes
    Cash & Equivalents      Citi Checking Account   $150,000        Primary transactional account. Maintains a high balance for liquidity.
    Money Market Fund       $250,000        Held at a competitor firm. Opportunity for consolidation.
    Investments             Citi Brokerage Account  $3,150,000      70% Equities, 25% Fixed Income, 5% Alternatives.
    Employer 401(k)         $1,800,000      Managed through his employer's plan.
    Vested Stock Options    $950,000        Significant concentration in a single tech stock.
    Real Estate             Primary Residence       $2,500,000      Estimated market value.
    Liabilities             Primary Mortgage        ($1,400,000)    30-year fixed at 3.25%. Opportunity to review refinancing options.
    Total Assets                                    $8,850,000
    Total Liabilities                               ($1,400,000)
    Estimated Net Worth                             $7,450,000

    Top Holdings in Brokerage Account:
    Ticker  Company Name          Shares    Market Value
    AAPL    Apple Inc.            500       $150,000.00
    MSFT    Microsoft Corp.       400       $140,000.00
    AMZN    Amazon.com, Inc.      100       $130,000.00
    GOOGL   Alphabet Inc.         100       $120,000.00
    JPM     JPMorgan Chase & Co.  500       $110,000.00
    UNH     United Health Group   100       $100,000.00

    4. Financial Goals & Objectives
    - Primary Goal: Retirement Planning
      - Target Age: 65
      - Desired Lifestyle: Maintain current standard of living ($350k/year post-tax).
      - Notes: Aims for capital preservation with moderate growth to outpace inflation during retirement.
    - Secondary Goal: Education Funding
      - Beneficiaries: Sophia (college in 2 years) and Liam (college in 5 years).
      - Target Amount: $300,000 per child for undergraduate education.
      - Notes: Currently has no dedicated 529 plans. This is a high-priority discussion topic.
    - Tertiary Goal: Estate Planning
      - Objective: Efficiently transfer wealth and minimize tax burden.
      - Notes: Has basic wills but no advanced trust structures in place.

    5. Risk Profile & Investment Philosophy
    - Risk Tolerance: Moderate Growth
    - Investment Knowledge: High. Chris is well-informed on market trends, particularly in the tech sector, but lacks the time for active management.
    - Philosophy: Believes in a diversified, long-term approach. He is concerned about the high concentration of his personal wealth in his company's stock and is open to strategies for diversification.

    6. Relationship with Citi & Actionable Opportunities
    - Client Since: 2015 (10 years)
    - Accounts Held: Citigold Checking, Citi Brokerage Account.
    - Interaction Preference: Prefers quarterly reviews via video conference and one annual in-person comprehensive review. Responds well to concise email summaries with clear action items.
    - Opportunities / Next Steps:
      - Consolidation: Propose a plan to move the competitor-held Money Market fund to Citi.
      - Education Planning: Discuss benefits of establishing and funding 529 College Savings Plans.
      - Concentrated Stock Strategy: Present options for hedging or systematically selling his vested company stock.
      - Credit & Lending: Review current mortgage and explore refinancing options.
      - Estate Planning: Schedule an introduction with a Citi Trust & Estate specialist.
    """

# A detailed set of instructions to define the agent's persona and rules.
detailed_instructions = """
You are a friendly, professional, and concise AI Wealth Advisor for Citi's wealth management clients.
You have a camera and can see the user. When asked, describe what you see.

**Your Primary Directive:** Your main purpose is to answer questions about the client, Chris, by using the `get_client_profile` tool. You can also answer questions about what you see through your camera.

**Operational Logic**
1.  **Use Vision for Visual Questions:** If the user asks a question about what you see (e.g., "what am I wearing?", "what is this object?"), answer based on the video input.
2.  **Use the Profile Tool for Client Questions:** For any client query, your first action is to use the `get_client_profile` tool to find the answer.
3.  **Answer from the Tool:** If you find the answer in the profile, respond directly to the client with the information.
4.  **Decline if Unavailable:** If the information is not available in the client profile, you must state that you cannot answer the question. For example, say "I do not have access to that information in the client's profile."
"""

root_agent = Agent(
   name="citi_wealth_advisor_agent",
   model="gemini-live-2.5-flash-preview-native-audio",
   description="An AI agent providing client-specific information for a Citi Wealth Management advisor.",
   instruction=detailed_instructions,
   # The function object is passed directly into the list.
   tools=[get_client_profile]
)