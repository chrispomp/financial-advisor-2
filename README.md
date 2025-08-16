AI Wealth Advisor Agent
This project implements a sophisticated AI Wealth Advisor agent for Citi, built using the Google Agent Development Kit (ADK). The agent is designed to be a hyper-personalized partner for clients, providing instant access to their profile, portfolio, and relevant financial guidance in a live, interactive conversation.

It uses a hierarchical structure, with a central "Root Agent" that delegates tasks to specialized agents for handling specific domains like client profiles, portfolios, product recommendations, and real-time market data via Google Search.

✨ Features
Hierarchical Agent System: A root agent orchestrates multiple specialist agents for modular and efficient task handling.

Context Pre-loading: Client profile and portfolio data are pre-loaded at the start of each turn for immediate access and reduced latency.

Live Interruptibility: A custom plugin allows the agent to be interrupted mid-task if new user input is detected, creating a highly responsive and natural conversational experience.

Multi-modal Responses: Capable of streaming responses that include text and audio.

Consolidated Knowledge Base: Integrates static client data with real-time information from Google Search and official Citi guidance.

🛠️ Setup and Installation
Prerequisites
Python 3.8+

Access to Google AI services and a configured Google Cloud project.

1. Clone the Repository
First, clone this repository to your local machine.

git clone <your-repository-url>
cd <your-repository-directory>

2. Install Dependencies
Install the necessary Python libraries using pip. The primary dependency is the Google Agent Development Kit.

pip install google-adk

3. Authentication
To run the agent, you need to be authenticated with Google Cloud. Run the following command and follow the instructions to log in:

gcloud auth application-default login

🚀 Running the Agent
Execute the main Python script from your terminal to start the agent. The script will run predefined queries to demonstrate the agent's capabilities.

python your_agent_script_name.py

You will see output in the console as the agent processes the hardcoded queries, greets the client, and answers questions based on the pre-loaded context.

Example Output:
--- 1. Testing Knowledge of Age ---
User Query: 'How old am I?' (Voice: Aoede)
------------------------------
Agent Response: Hello Chris, you are 45 years old.

==================================================

--- 2. Testing Personal Interest Knowledge ---
User Query: 'What's my favorite football team?' (Voice: en-US-Standard-J)
------------------------------
Agent Response: Your favorite football team is the New York Jets.

⚙️ How It Works
Initialization: When main() is executed, it calls run_live_agent.

Context Loading: The preload_client_context callback is triggered. It calls the mock data functions (get_client_profile, get_client_portfolio) and loads the combined data into the agent's memory (invocation_context).

Query Processing: The Root Agent receives the user's query. Its core instructions mandate that it must check the client_context first before using any tools.

Task Delegation:

If the answer is in the context (e.g., "How old am I?"), the agent synthesizes a response directly.

If the query requires information not in the context (e.g., "latest news about MSFT"), the Root Agent delegates the task to the appropriate specialist agent (in this case, GoogleSearchAgent).

Live Interruption: Throughout the process, the LiveInterruptPlugin continuously checks a request queue for new user messages. If a new message arrives, it sets an end_invocation flag, gracefully stopping the agent's current action to immediately address the new input.

Response Streaming: The final response is streamed back to the user in the specified modalities (text and audio).