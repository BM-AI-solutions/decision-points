TITLE: Google Cloud Authentication for RAG Setup
DESCRIPTION: Command to authenticate with Google Cloud for accessing Vertex AI services. This is required before running the corpus preparation script.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/RAG/README.md#2025-04-21_snippet_4

LANGUAGE: bash
CODE:
```
gcloud auth application-default login
```

----------------------------------------

TITLE: Deploying Agent to Vertex AI
DESCRIPTION: Command to deploy an agent to Vertex AI Agent Engine
SOURCE: https://github.com/google/adk-samples/blob/main/agents/RAG/README.md#2025-04-21_snippet_11

LANGUAGE: python
CODE:
```
python deployment/deploy.py
```

----------------------------------------

TITLE: Interacting with a deployed agent using Vertex AI Agent Engines API
DESCRIPTION: Python code snippet that demonstrates how to use the Vertex AI Agent Engines API to create a session and stream queries to a deployed agent. This is the core functionality of the test deployment script.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/fomc-research/README.md#2025-04-21_snippet_15

LANGUAGE: python
CODE:
```
from vertexai import agent_engines
remote_agent = vertexai.agent_engines.get(RESOURCE_ID)
session = remote_agent.create_session(user_id=USER_ID)
while True:
    user_input = input("Input: ")
    if user_input == "quit":
      break

    for event in remote_agent.stream_query(
        user_id=USER_ID,
        session_id=session["id"],
        message=user_input,
    ):
        parts = event["content"]["parts"]
        for part in parts:
            if "text" in part:
                text_part = part["text"]
                print(f"Response: {text_part}")
```

----------------------------------------

TITLE: Interacting with Deployed Personalized Shopping Agent in Python
DESCRIPTION: Python code snippet to interact programmatically with the deployed personalized shopping agent using Vertex AI Agent Engine.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/personalized-shopping/README.md#2025-04-21_snippet_10

LANGUAGE: python
CODE:
```
import dotenv
dotenv.load_dotenv()  # May skip if you have exported environment variables.
from vertexai import agent_engines

agent_engine_id = "AGENT_ENGINE_ID" #Remember to update the ID here. 
user_input = "Hello, can you help me find a summer dress? I want something flowy and floral."

agent_engine = agent_engines.get(agent_engine_id)
session = agent_engine.create_session(user_id="new_user")
for event in agent_engine.stream_query(
    user_id=session["user_id"], session_id=session["id"], message=user_input
):
    for part in event["content"]["parts"]:
        print(part["text"])
```

----------------------------------------

TITLE: Vertex AI Deployment Success Log
DESCRIPTION: Example of successful deployment confirmation message showing the resource name format
SOURCE: https://github.com/google/adk-samples/blob/main/agents/RAG/README.md#2025-04-21_snippet_12

LANGUAGE: plaintext
CODE:
```
Deployed agent to Vertex AI Agent Engine successfully, resource name: projects/<PROJECT_NUMBER>/locations/us-central1/reasoningEngines/<AGENT_ENGINE_ID>
```

----------------------------------------

TITLE: Testing the deployed agent on Vertex AI Agent Engine
DESCRIPTION: Commands to set up environment variables and run a script that interacts with the deployed agent. The script uses the Agent Engine API to send queries and receive responses.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/fomc-research/README.md#2025-04-21_snippet_14

LANGUAGE: bash
CODE:
```
export RESOURCE_ID=...
export USER_ID=<any string>
python test_deployment.py --resource_id=$RESOURCE_ID --user_id=$USER_ID
```

----------------------------------------

TITLE: Deploying the Agent to Vertex AI
DESCRIPTION: Python command to deploy the agent to Vertex AI Agent Engine. Requires setting DISABLE_WEB_DRIVER=1 in the .env file before deployment.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/brand-search-optimization/README.md#2025-04-21_snippet_4

LANGUAGE: bash
CODE:
```
python deployment/deploy.py --create
```

----------------------------------------

TITLE: Displaying Travel Concierge Folder Structure
DESCRIPTION: Shows the organization of the travel concierge project with directories for shared libraries, tools, sub-agents, tests, evaluation data, and deployment configurations.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/travel-concierge/README.md#2025-04-21_snippet_0

LANGUAGE: bash
CODE:
```
.
├── README.md
├── travel-concierge-arch.png
├── pyproject.toml
├── travel_concierge/
│   ├── shared_libraries/
│   ├── tools/
│   └── sub_agents/
│       ├── inspiration/
│       ├── planning/
│       ├── booking/
│       ├── pre_trip/
│       ├── in_trip/
│       └── post_trip/
├── tests/
│   └── unit/
├── eval/
│   └── data/
└── deployment/
```

----------------------------------------

TITLE: Interacting with Deployed LLM Auditor Agent in Python
DESCRIPTION: Python code for programmatically interacting with a deployed LLM Auditor agent. It establishes a session with the agent and streams responses to a user query about factual accuracy.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/llm-auditor/README.md#2025-04-21_snippet_9

LANGUAGE: python
CODE:
```
import dotenv
dotenv.load_dotenv()  # May skip if you have exported environment variables.
from vertexai import agent_engines

agent_engine_id = "AGENT_ENGINE_ID"
user_input = "Double check this: Earth is further away from the Sun than Mars."

agent_engine = agent_engines.get(agent_engine_id)
session = agent_engine.create_session(user_id="new_user")
for event in agent_engine.stream_query(
    user_id=session["user_id"], session_id=session["id"], message=user_input
):
    for part in event["content"]["parts"]:
        print(part["text"])
```

----------------------------------------

TITLE: Deploying Personalized Shopping Agent to Vertex AI Agent Engine
DESCRIPTION: Command to deploy the personalized shopping agent to Vertex AI Agent Engine.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/personalized-shopping/README.md#2025-04-21_snippet_9

LANGUAGE: bash
CODE:
```
cd agents/personalized-shopping/deployment
python3 deploy.py
```

----------------------------------------

TITLE: Displaying Agent Directory Tree Structure in Bash
DESCRIPTION: A tree-like representation showing the standard directory structure for agents, including core agent code, sub-agents, deployment, evaluation, and testing directories. This structure demonstrates the organization of components like shared libraries, tools, prompts, and configuration files.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/README.md#2025-04-21_snippet_4

LANGUAGE: bash
CODE:
```
├── agent-name
│   ├── agent_name/
│   │   ├── shared_libraries/               # Folder contains helper functions for tools
│   │   ├── sub_agents/                     # Folder for each sub agent
│   │   │   │   ├── tools/                  # tools folder for the subagent
│   │   │   │   ├── agent.py                # core logic of the sub agent
│   │   │   │   └── prompt.py               # prompt of the subagent
│   │   │   └── ...                         # More sub-agents    
│   │   ├── __init__.py                     # Initializes the agent
│   │   ├── tools/                          # Contains the code for tools used by the router agent
│   │   ├── agent.py                        # Contains the core logic of the agent
│   │   ├── prompt.py                       # Contains the prompts for the agent
│   ├── deployment/                         # Deployment to Agent Engine
│   ├── eval/                               # Folder containing the evaluation method
│   ├── tests/                              # Folder containing unit tests for tools
│   ├── agent_pattern.png                   # Diagram of the agent pattern
│   ├── .env.example                        # Store agent specific env variables
│   ├── pyproject.toml                      # Project configuration
│   └── README.md                           # Provides an overview of the agent
```

----------------------------------------

TITLE: Customizing Corpus Preparation in Python
DESCRIPTION: Code snippet showing how to modify the corpus preparation script variables to configure a custom corpus name, description, and document URL. This allows users to customize their RAG implementation.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/RAG/README.md#2025-04-21_snippet_6

LANGUAGE: python
CODE:
```
# --- Please fill in your configurations ---
# ... project and location are read from .env ...
CORPUS_DISPLAY_NAME = "Your_Corpus_Name"  # Change as needed
CORPUS_DESCRIPTION = "Description of your corpus" # Change as needed
PDF_URL = "https://path/to/your/document.pdf"  # URL to YOUR PDF document
PDF_FILENAME = "your_document.pdf"  # Name for the file in the corpus
# --- Start of the script ---
```

----------------------------------------

TITLE: Deleting Deployed Personalized Shopping Agent
DESCRIPTION: Command to delete the deployed personalized shopping agent from Vertex AI Agent Engine.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/personalized-shopping/README.md#2025-04-21_snippet_11

LANGUAGE: bash
CODE:
```
python3 deployment/deploy.py --delete --resource_id=${AGENT_ENGINE_ID}
```

----------------------------------------

TITLE: Confirming Flight Reservation (JSON)
DESCRIPTION: JSON function call to confirm flight reservations from San Diego to Lima and back, including outbound and return flights.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/travel-concierge/tests/pre_booking_sample.md#2025-04-21_snippet_29

LANGUAGE: json
CODE:
```
function call: "confirm_reservation_agent"
args: {
  "request": "Flight: American Airlines (AA123) from San Diego (SAN) to Lima (LIM) on May 4, 2025, departing at 2:00 PM, Seat: 1A. AND Flight: LATAM Airlines (LATAM2345) from Lima (LIM) to San Diego (SAN) on May 11, 2025, departing at 2:00 PM. Seat: 2A."
}
```

----------------------------------------

TITLE: Installing and Setting Up the Brand Search Optimization Agent
DESCRIPTION: Bash script to clone the repository, navigate to the agent directory, and run the deployment script which sets up the environment, installs dependencies, and populates BigQuery data.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/brand-search-optimization/README.md#2025-04-21_snippet_1

LANGUAGE: bash
CODE:
```
# Clone this repository.
git clone https://github.com/google/adk-samples.git
cd adk-samples/agents/brand-search-optimization

# Run This script
# 1. Creates and activates a new virtual env
# 2. Installs python packages
# 3. Populates BigQuery data using variables set in `.env` file
sh deployment/run.sh
```

----------------------------------------

TITLE: Running Travel Concierge Agent via Web Interface
DESCRIPTION: Command to start the ADK web interface for interacting with the travel concierge agent through a browser-based chatbot interface.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/travel-concierge/README.md#2025-04-21_snippet_6

LANGUAGE: bash
CODE:
```
# Under the travel-concierge directory:
adk web
```

----------------------------------------

TITLE: Deploying the agent to Vertex AI Agent Engine
DESCRIPTION: Command to run the deployment script that creates the agent on Vertex AI Agent Engine. The script handles uploading the wheel file and configuring the agent.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/fomc-research/README.md#2025-04-21_snippet_13

LANGUAGE: bash
CODE:
```
cd deployment
python3 deploy.py --create
```

----------------------------------------

TITLE: Uploading Local PDF to Corpus in Python
DESCRIPTION: Example of modifying the main() function in the preparation script to upload a local PDF file to the RAG corpus. This shows how to customize the script for local file processing.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/RAG/README.md#2025-04-21_snippet_7

LANGUAGE: python
CODE:
```
def main():
  initialize_vertex_ai()
  corpus = create_or_get_corpus() # Uses CORPUS_DISPLAY_NAME & CORPUS_DESCRIPTION

  # Upload your local PDF to the corpus
  local_file_path = "/path/to/your/local/file.pdf" # Set the correct path
  display_name = "Your_File_Name.pdf" # Set the desired display name
  description = "Description of your file" # Set the description

  # Ensure the file exists before uploading
  if os.path.exists(local_file_path):
      upload_pdf_to_corpus(
          corpus_name=corpus.name,
          pdf_path=local_file_path,
          display_name=display_name,
          description=description
      )
  else:
      print(f"Error: Local file not found at {local_file_path}")

  # List all files in the corpus
  list_corpus_files(corpus_name=corpus.name)
```

----------------------------------------

TITLE: Environment Variables Configuration
DESCRIPTION: Required environment variables setup in .env file for agent deployment and RAG corpus access
SOURCE: https://github.com/google/adk-samples/blob/main/agents/RAG/README.md#2025-04-21_snippet_13

LANGUAGE: plaintext
CODE:
```
AGENT_ENGINE_ID=projects/<PROJECT_NUMBER>/locations/us-central1/reasoningEngines/<AGENT_ENGINE_ID>

GOOGLE_CLOUD_PROJECT=your-project-id
RAG_CORPUS=projects/<project-number>/locations/us-central1/ragCorpora/<corpus-id>
```

----------------------------------------

TITLE: Installing Dependencies with Poetry
DESCRIPTION: Command to install all required dependencies for the Documentation Retrieval Agent using Poetry package manager. This reads the pyproject.toml file and sets up the project environment.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/RAG/README.md#2025-04-21_snippet_1

LANGUAGE: bash
CODE:
```
poetry install
```

----------------------------------------

TITLE: Setting Up BigQuery for FOMC Research Agent
DESCRIPTION: Command to set up a BigQuery table with Fed Futures pricing data, which is required for the FOMC Research Agent's rate change probability calculations.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/fomc-research/README.md#2025-04-21_snippet_6

LANGUAGE: bash
CODE:
```
python bigquery_setup.py --project_id=$GOOGLE_CLOUD_PROJECT \
    --dataset_id=$GOOGLE_CLOUD_BQ_DATASET \
    --location=$GOOGLE_CLOUD_LOCATION \
    --data_file=sample_timeseries_data.csv
```

----------------------------------------

TITLE: Installing Poetry and Project Dependencies for Personalized Shopping Agent
DESCRIPTION: Commands to set up a Python virtual environment, install Poetry, and install project dependencies for the personalized shopping agent.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/personalized-shopping/README.md#2025-04-21_snippet_0

LANGUAGE: bash
CODE:
```
cd ~
python3 -m venv myenv
source ~/myenv/bin/activate
pip install poetry

cd adk-samples/agents/personalized-shopping
poetry install
```

----------------------------------------

TITLE: Activating Poetry Virtual Environment
DESCRIPTION: Command to activate the Poetry-managed virtual environment where the project dependencies are installed. This ensures all commands run in the properly configured environment.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/RAG/README.md#2025-04-21_snippet_2

LANGUAGE: bash
CODE:
```
poetry env activate
```

----------------------------------------

TITLE: Transferring to Booking Agent in JSON
DESCRIPTION: Function call to transfer the conversation to the booking agent for finalizing reservations and payments.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/travel-concierge/tests/pre_booking_sample.md#2025-04-21_snippet_28

LANGUAGE: json
CODE:
```
function call: "transfer_to_agent"
args: {
  "agent_name": "booking_agent"
}
```

----------------------------------------

TITLE: Deploying Agent to Vertex AI Agent Engine
DESCRIPTION: Commands to install deployment dependencies and deploy the travel concierge agent to Vertex AI Agent Engine.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/travel-concierge/README.md#2025-04-21_snippet_12

LANGUAGE: bash
CODE:
```
poetry install --with deployment
python deployment/deploy.py --create
```

----------------------------------------

TITLE: Running Corpus Preparation Script
DESCRIPTION: Command to execute the preparation script that sets up a RAG corpus and uploads an initial document. By default, this script downloads and uploads Alphabet's 2024 10-K PDF.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/RAG/README.md#2025-04-21_snippet_5

LANGUAGE: bash
CODE:
```
python rag/shared_libraries/prepare_corpus_and_data.py
```

----------------------------------------

TITLE: Running the RAG Agent with Web UI
DESCRIPTION: Command to launch the Agent Development Kit's web interface for running the Documentation Retrieval Agent. This provides a graphical interface for interacting with the agent.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/RAG/README.md#2025-04-21_snippet_9

LANGUAGE: bash
CODE:
```
adk web
```

----------------------------------------

TITLE: Flight Status Check Function Calls
DESCRIPTION: Function calls to check the status of two flights, providing flight number, date, check-in time, and departure time for each flight.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/travel-concierge/tests/post_booking_sample.md#2025-04-21_snippet_6

LANGUAGE: json
CODE:
```
function call: "flight_status_check"
args: {
  "flight_date": "2025-06-15",
  "checkin_time": "07:30",
  "departure_time": "08:00",
  "flight_number": "AA1234"
}
```

LANGUAGE: json
CODE:
```
function call: "flight_status_check"
args: {
  "flight_number": "UA5678",
  "checkin_time": "15:30",
  "departure_time": "16:00",
  "flight_date": "2025-06-17"
}
```

----------------------------------------

TITLE: Running Personalized Shopping Agent via Web Interface
DESCRIPTION: Commands to start a web server for interacting with the personalized shopping agent through a chatbot interface.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/personalized-shopping/README.md#2025-04-21_snippet_5

LANGUAGE: bash
CODE:
```
cd personalized-shopping
adk web
```

----------------------------------------

TITLE: Creating Itinerary using Itinerary Agent in JSON
DESCRIPTION: Function call to the itinerary agent to create a detailed trip plan based on the provided information including flights, hotel, and daily activities.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/travel-concierge/tests/pre_booking_sample.md#2025-04-21_snippet_27

LANGUAGE: json
CODE:
```
function call: "itinerary_agent"
args: {
  "request": "Origin: San Diego, CA, USA; Destination: Peru; Start Date: 2025-05-04; End Date: 2025-05-11; Outbound Flight: American Airlines (AA123) from SAN to LIM on 2025-05-04, Seat 1A; Return Flight: LATAM Airlines (LATAM2345) from LIM to SAN on 2025-05-11, Seat 2A; Hotel: Belmond Hotel Monasterio in Cusco, Peru; Room: Queen Room with Balcony; Day 1: Depart from home and fly to Lima; Day 2: Arrive in Lima, connecting flight to Cusco, check into hotel; Day 3: Explore Cusco; Day 4: Machu Picchu; Day 5: Vegan Food in Cusco; Day 6: Lake Titicaca; Day 7: Travel back to Lima; Day 8: Depart from Lima; Day 9: Arrive in San Diego."
}
```

----------------------------------------

TITLE: Running Agent Evaluation Tests
DESCRIPTION: Command to run the evaluation tests for the Documentation Retrieval Agent using pytest through Poetry. This validates the agent's performance and behavior.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/RAG/README.md#2025-04-21_snippet_10

LANGUAGE: bash
CODE:
```
poetry run pytest eval
```

----------------------------------------

TITLE: Searching for Floral Summer Dress using JSON Function Call
DESCRIPTION: A function call to search for flowy floral summer dresses using keywords. This demonstrates how the shopping agent initiates a search query based on user preferences.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/personalized-shopping/tests/example_interactions/text_search_floral_dress.session.md#2025-04-21_snippet_0

LANGUAGE: json
CODE:
```
function call: "search"
args: {
  "keywords": "flowy floral summer dress"
}
```

----------------------------------------

TITLE: Sending Video Connection Link using Tool Function
DESCRIPTION: This snippet demonstrates the agent's use of a tool function to send a secure video connection link to a customer's phone number, enabling visual communication capabilities for product identification.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/customer-service/README.md#2025-04-21_snippet_0

LANGUAGE: python
CODE:
```
print(send_call_companion_link(phone_number='+12065550123'))
```

----------------------------------------

TITLE: Running the RAG Agent in CLI Mode
DESCRIPTION: Command to run the Documentation Retrieval Agent in command-line interface mode using the Agent Development Kit (ADK). This launches the agent for interactive use.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/RAG/README.md#2025-04-21_snippet_8

LANGUAGE: bash
CODE:
```
adk run rag
```

----------------------------------------

TITLE: Running Agent in Command Line Interface
DESCRIPTION: Command to run the customer service agent in the terminal using the ADK (Agent Development Kit) command line interface.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/customer-service/README.md#2025-04-21_snippet_5

LANGUAGE: bash
CODE:
```
adk run customer_service
```

----------------------------------------

TITLE: Confirming Lake Titicaca Visit Reservation (JSON)
DESCRIPTION: JSON function call to confirm a reservation for a Lake Titicaca visit.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/travel-concierge/tests/pre_booking_sample.md#2025-04-21_snippet_37

LANGUAGE: json
CODE:
```
function call: "confirm_reservation_agent"
args: {
  "request": "Lake Titicaca visit on May 9, 2025"
}
```

----------------------------------------

TITLE: Starting API Server for Programmatic Access
DESCRIPTION: Command to start a FastAPI server for the travel concierge agent, enabling programmatic access to the agent's functionality through HTTP requests.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/travel-concierge/README.md#2025-04-21_snippet_7

LANGUAGE: bash
CODE:
```
adk api_server travel_concierge
```

----------------------------------------

TITLE: Authenticating with Google Cloud SDK for FOMC Research Agent
DESCRIPTION: This command authenticates the user with Google Cloud SDK, which is required for BigQuery setup and Agent Engine deployment.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/fomc-research/README.md#2025-04-21_snippet_0

LANGUAGE: bash
CODE:
```
gcloud auth login
```

----------------------------------------

TITLE: Running Agent with Web User Interface
DESCRIPTION: Command to launch the agent with the ADK web-based user interface, which provides a graphical environment for interacting with the agent.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/customer-service/README.md#2025-04-21_snippet_6

LANGUAGE: bash
CODE:
```
adk web
```

----------------------------------------

TITLE: Product Details Response
DESCRIPTION: Response containing detailed product information including available sizes and colors
SOURCE: https://github.com/google/adk-samples/blob/main/agents/personalized-shopping/tests/example_interactions/image_search_denim_skirt.session.md#2025-04-21_snippet_3

LANGUAGE: json
CODE:
```
Response from: "click"
response: {
  "result": "Back to Search [SEP] < Prev [SEP] size [SEP] 12 plus [SEP] 12 plus petite [SEP] 14 plus [SEP] 14 plus petite [SEP] 16 plus [SEP] 16 plus petite [SEP] 18 plus [SEP] 18 plus petite [SEP] 20 plus [SEP] 20 plus petite [SEP] 22 plus [SEP] 22 plus petite [SEP] 24 plus [SEP] 24 plus petite [SEP] 26 plus [SEP] 26 plus petite [SEP] 28 plus [SEP] 28 plus petite [SEP] 30 plus [SEP] 30 plus petite [SEP] 32 plus [SEP] 32 plus petite [SEP] 34 plus [SEP] 34 plus petite [SEP] 36 plus [SEP] 36 plus petite [SEP] 38 plus [SEP] 38 plus petite [SEP] color [SEP] indigo [SEP] natural khaki [SEP] black [SEP] light wash [SEP] stonewash [SEP] white [SEP] Woman Within Women's Plus Size Petite Flared Denim Skirt [SEP] Price: $24.41 to $29.95 [SEP] Rating: N.A. [SEP] Description [SEP] Features [SEP] Reviews [SEP] Buy Now"
}
```

----------------------------------------

TITLE: Cloning the Repository for Documentation Retrieval Agent
DESCRIPTION: Command to clone the repository containing the Documentation Retrieval Agent code and navigate to the RAG directory. This is the first step in the project setup process.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/RAG/README.md#2025-04-21_snippet_0

LANGUAGE: bash
CODE:
```
git clone https://github.com/google/adk-samples.git
cd adk-samples/agents/RAG
```

----------------------------------------

TITLE: Making Function Call to Memorize Flight Selection in JSON
DESCRIPTION: A JSON function call to store the selected outbound flight details. This uses a memory service to persist the chosen flight information including airline, departure/arrival details, price, and stops.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/travel-concierge/tests/pre_booking_sample.md#2025-04-21_snippet_19

LANGUAGE: json
CODE:
```
function call: "memorize"
args: {
  "value": "{\"airline_logo\": \"/images/american.png\", \"airlines\": [\"American Airlines\"], \"arrival\": {\"airportCode\": \"LIM\", \"cityName\": \"Lima\", \"timestamp\": \"2025-05-05T02:00:00Z\"}, \"departure\": {\"airportCode\": \"SAN\", \"cityName\": \"San Diego\", \"timestamp\": \"2025-05-04T14:00:00Z\"}, \"flight_number\": \"AA123\", \"numberOfStops\": 1, \"priceInUSD\": 600}",
  "key": "outbound_flight_selection"
}
```

----------------------------------------

TITLE: Running Agent via ADK CLI - Bash Commands
DESCRIPTION: Commands to navigate to agent directory and run it using ADK CLI interface.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/README.md#2025-04-21_snippet_2

LANGUAGE: bash
CODE:
```
# Example (check agent's README for exact path)
cd agents/fomc-research/fomc_research/ 
adk run .
```

----------------------------------------

TITLE: Making Function Call to Memorize Seat Selection in JSON
DESCRIPTION: A JSON function call to store the selected seat number for the outbound flight. The function call specifies a key-value pair to be stored in the memory service.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/travel-concierge/tests/pre_booking_sample.md#2025-04-21_snippet_21

LANGUAGE: json
CODE:
```
function call: "memorize"
args: {
  "value": "1A",
  "key": "outbound_seat_number"
}
```

----------------------------------------

TITLE: Running Travel Concierge Agent via CLI
DESCRIPTION: Command to run the travel concierge agent using ADK's command-line interface, allowing direct interaction with the agent in the terminal.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/travel-concierge/README.md#2025-04-21_snippet_5

LANGUAGE: bash
CODE:
```
# Under the travel-concierge directory:
adk run travel_concierge
```

----------------------------------------

TITLE: Sample JSON Response from Place Agent
DESCRIPTION: Example of a structured JSON response from the place agent showing destination information including images, highlights and ratings.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/travel-concierge/README.md#2025-04-21_snippet_17

LANGUAGE: json
CODE:
```
{
  "id": "af-be786618-b60b-45ee-a801-c40fd6811e60",
  "name": "place_agent",
  "response": {
    "places": [
      {
        "name": "Malé",
        "country": "Maldives",
        "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1c/Male%2C_Maldives_panorama_2016.jpg/1280px-Male%2C_Maldives_panorama_2016.jpg",
        "highlights": "The vibrant capital city, offering bustling markets, historic mosques, and a glimpse into local Maldivian life.",
        "rating": "4.2"
      },
      {
        "name": "Baa Atoll",
        "country": "Maldives",
        "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/95/Baa_Atoll_Maldives.jpg/1280px-Baa_Atoll_Maldives.jpg",
        "highlights": "A UNESCO Biosphere Reserve, famed for its rich marine biodiversity, including manta rays and whale sharks, perfect for snorkeling and diving.",
        "rating": "4.8"
      },
      {
        "name": "Addu Atoll",
        "country": "Maldives",
        "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c3/Addu_Atoll_Maldives.jpg/1280px-Addu_Atoll_Maldives.jpg",
        "highlights": "The southernmost atoll, known for its unique equatorial vegetation, historic WWII sites, and excellent diving spots with diverse coral formations.",
        "rating": "4.5"
      }
    ]
  }
}
```

----------------------------------------

TITLE: Running Personalized Shopping Agent via CLI
DESCRIPTION: Command to run the personalized shopping agent using the ADK CLI interface.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/personalized-shopping/README.md#2025-04-21_snippet_4

LANGUAGE: bash
CODE:
```
adk run personalized_shopping
```

----------------------------------------

TITLE: Processing Memorize Response for Seat Selection in JSON
DESCRIPTION: The JSON response confirming successful storage of the outbound seat selection in the memory service. The response includes a status message with the stored key and value.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/travel-concierge/tests/pre_booking_sample.md#2025-04-21_snippet_22

LANGUAGE: json
CODE:
```
Response from: "memorize"
response: {
  "status": "Stored \"outbound_seat_number\": \"1A\""
}
```

----------------------------------------

TITLE: Transferring to Planning Agent
DESCRIPTION: Function call to transfer control from inspiration agent to planning agent for itinerary creation.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/travel-concierge/tests/pre_booking_sample.md#2025-04-21_snippet_8

LANGUAGE: json
CODE:
```
function call: "transfer_to_agent"
args: {
  "agent_name": "planning_agent"
}
```

----------------------------------------

TITLE: Responses from Packing Agent with Travel Information
DESCRIPTION: A series of responses from the what_to_pack_agent providing information on visa requirements, medical requirements, weather conditions, travel advisories, and a list of recommended items to pack.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/travel-concierge/tests/post_booking_sample.md#2025-04-21_snippet_3

LANGUAGE: json
CODE:
```
Response from: "what_to_pack_agent"
response: {
  "result": "To visit San Diego or Seattle, ensure you have a valid passport, and if required based on your nationality, apply for a US visa or ESTA through the Electronic System for Travel Authorization.\n"
}
```

LANGUAGE: json
CODE:
```
Response from: "what_to_pack_agent"
response: {
  "result": "To ensure a safe and healthy trip from San Diego to Seattle, make sure your routine vaccinations are up to date, consult your doctor about any medical concerns, and carry sufficient prescription medications; for detailed travel health advice, consider contacting Kaiser Permanente's Travel Advisory Service at 1-206-326-3488.\n"
}
```

LANGUAGE: json
CODE:
```
Response from: "what_to_pack_agent"
response: {
  "result": "San Diego: Expect patchy drizzle tonight and partly cloudy skies tomorrow with a high around 65\u00b0F.\n\nSeattle: Expect cloudy conditions with periods of rain today and a high of 53\u00b0F, with rain likely to continue through the weekend.\n"
}
```

LANGUAGE: json
CODE:
```
Response from: "what_to_pack_agent"
response: {
  "result": "Currently, there are health advisories in San Diego regarding Xylazine in the drug supply and a measles outbreak, and it's always wise to review visitor safety tips in Seattle, such as being aware of your surroundings and protecting your valuables.\n"
}
```

LANGUAGE: json
CODE:
```
Response from: "what_to_pack_agent"
response: {
  "items": [
    "light jacket",
    "umbrella",
    "comfortable walking shoes",
    "layers",
    "sunscreen"
  ]
}
```

----------------------------------------

TITLE: Running the FOMC Research Agent via ADK Command Line
DESCRIPTION: Command to run the FOMC Research Agent using the ADK (Agent Development Kit) command line interface from the fomc-research directory.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/fomc-research/README.md#2025-04-21_snippet_7

LANGUAGE: bash
CODE:
```
adk run fomc_research
```

----------------------------------------

TITLE: Selecting a Product Using Click Function
DESCRIPTION: A function call to click on a specific product identified by its ID. This shows how the shopping agent selects a particular product based on the user's interest in the B092QL1FLW dress.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/personalized-shopping/tests/example_interactions/text_search_floral_dress.session.md#2025-04-21_snippet_2

LANGUAGE: json
CODE:
```
function call: "click"
args: {
  "button_name": "B092QL1FLW"
}
```

----------------------------------------

TITLE: Setting Google Cloud Environment Variables
DESCRIPTION: Bash commands to set the required environment variables for connecting the agent to Google Cloud services, including project name, Vertex AI usage, and region configuration.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/customer-service/README.md#2025-04-21_snippet_4

LANGUAGE: bash
CODE:
```
export GOOGLE_CLOUD_PROJECT=YOUR_ROJECT_NAME_HERE
export GOOGLE_GENAI_USE_VERTEXAI=1
export GOOGLE_CLOUD_LOCATION=us-central1
```

----------------------------------------

TITLE: POI Agent Response with Activity Recommendations
DESCRIPTION: Response containing five recommended points of interest in Peru with their details and locations.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/travel-concierge/tests/pre_booking_sample.md#2025-04-21_snippet_5

LANGUAGE: json
CODE:
```
Response from: "poi_agent"
response: {
  "places": [
    {
      "place_name": "Machu Picchu",
      "address": "Machu Picchu, Aguas Calientes, Peru",
      "lat": "-13.1631",
      "long": "-72.5450",
      "review_ratings": "4.7",
      "highlights": "Ancient Inca citadel set high in the Andes Mountains.",
      "image_url": "https://example.com/machu_picchu.jpg",
      "map_url": "",
      "place_id": ""
    },
    {
      "place_name": "Sacsayhuam\u00e1n",
      "address": "Sacsayhuam\u00e1n, Cusco, Peru",
      "lat": "-13.5081",
      "long": "-71.9805",
      "review_ratings": "4.5",
      "highlights": "A walled complex on the northern outskirts of Cusco, Peru.",
      "image_url": "https://example.com/sacsayhuaman.jpg",
      "map_url": "",
      "place_id": ""
    },
    {
      "place_name": "Plaza de Armas, Cusco",
      "address": "Plaza de Armas, Cusco, Peru",
      "lat": "-13.5167",
      "long": "-71.9786",
      "review_ratings": "4.6",
      "highlights": "The heart of Cusco, surrounded by historical buildings and churches.",
      "image_url": "https://example.com/plaza_de_armas_cusco.jpg",
      "map_url": "",
      "place_id": ""
    },
    {
      "place_name": "Nazca Lines",
      "address": "Nazca Lines, Nazca, Peru",
      "lat": "-14.8344",
      "long": "-75.4742",
      "review_ratings": "4.3",
      "highlights": "Ancient geoglyphs in the Nazca Desert, best viewed from the air.",
      "image_url": "https://example.com/nazca_lines.jpg",
      "map_url": "",
      "place_id": ""
    },
    {
      "place_name": "Lake Titicaca",
      "address": "Lake Titicaca, Puno, Peru",
      "lat": "-15.8333",
      "long": "-69.3333",
      "review_ratings": "4.4",
      "highlights": "South America's largest lake, known for its floating islands.",
      "image_url": "https://example.com/lake_titicaca.jpg",
      "map_url": "",
      "place_id": ""
    }
  ]
}
```

----------------------------------------

TITLE: Running Programmatic Client Example
DESCRIPTION: Command to execute a Python script that demonstrates programmatic interaction with the travel concierge agent through its API server.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/travel-concierge/README.md#2025-04-21_snippet_8

LANGUAGE: bash
CODE:
```
python tests/programmatic_example.py
```

----------------------------------------

TITLE: Retrieving Product Description Content
DESCRIPTION: A JSON response containing the product description for the selected dress. The response includes details about the dress's style, material, pattern, and sizing information for the customer.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/personalized-shopping/tests/example_interactions/text_search_floral_dress.session.md#2025-04-21_snippet_5

LANGUAGE: json
CODE:
```
Response from: "click"
response: {
  "result": "Back to Search [SEP] < Prev [SEP] Women's Casual Long Dress with Striped Floral Print Short Sleeve Maxi Dress\u2605Description:\u25cfSeason:Spring,Summer\u25cfGender:Women\u25cfStyle:Casual\u25cfMaterial:Cottonblend\u25cfPattern Type:Print\u25cfDecoration: None\u2764What you get:1 X dress\u203bDesign can make you more sexy, more energetic and more attractive\u2605\u2605PLEASE NOTE:\u2764Our clothes all are designed for Asian figure, which means would be smaller than normal US sizes. Please refer to our own size chart and you can find it in our pictures or from the description.\u2764Garment Care: Hand Wash Recommand or Dry Clean Your Shirt Dress. The Pattern on the Original Product May Vary Please Know .\u2764Colors may be slightly different depending on computer and monitor settings\u2764Please check the Size Chart before order. If you are not sure the size, please send message to us."
}
```

----------------------------------------

TITLE: Deploying LLM Auditor to Vertex AI Agent Engine
DESCRIPTION: Commands to install dependencies and deploy the LLM Auditor to Vertex AI Agent Engine. This creates a new agent in the specified project.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/llm-auditor/README.md#2025-04-21_snippet_7

LANGUAGE: bash
CODE:
```
poetry install --with deployment
python3 deployment/deploy.py --create
```

----------------------------------------

TITLE: Authenticating with Google Cloud
DESCRIPTION: Command to authenticate with your Google Cloud account using gcloud CLI for accessing Google Cloud services needed by the agent.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/brand-search-optimization/README.md#2025-04-21_snippet_0

LANGUAGE: bash
CODE:
```
gcloud auth application-default login
```

----------------------------------------

TITLE: Programmatic Interaction with LLM Auditor
DESCRIPTION: Python code example showing how to interact with the LLM Auditor programmatically using ADK
SOURCE: https://github.com/google/adk-samples/blob/main/agents/llm-auditor/README.md#2025-04-21_snippet_5

LANGUAGE: python
CODE:
```
import dotenv
dotenv.load_dotenv()  # May skip if you have exported environment variables.
from google.adk.runners import InMemoryRunner
from google.genai.types import Part, UserContent
from llm_auditor.agent import root_agent

user_input = "Double check this: Earth is further away from the Sun than Mars."

runner = InMemoryRunner(agent=root_agent)
session = runner.session_service.create_session(
    app_name=runner.app_name, user_id="test_user"
)
content = UserContent(parts=[Part(text=user_input)])
for event in runner.run(
    user_id=session.user_id, session_id=session.id, new_message=content
):
    for part in event.content.parts:
        print(part.text)
```

----------------------------------------

TITLE: Viewing Product Features
DESCRIPTION: A function call to navigate to the Features section of the product page. This shows how the shopping agent accesses additional product information to provide comprehensive details to the user.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/personalized-shopping/tests/example_interactions/text_search_floral_dress.session.md#2025-04-21_snippet_8

LANGUAGE: json
CODE:
```
function call: "click"
args: {
  "button_name": "Features"
}
```

----------------------------------------

TITLE: Granting RAG Permissions
DESCRIPTION: Commands to execute the permissions script for RAG corpus access
SOURCE: https://github.com/google/adk-samples/blob/main/agents/RAG/README.md#2025-04-21_snippet_14

LANGUAGE: bash
CODE:
```
chmod +x deployment/grant_permissions.sh
./deployment/grant_permissions.sh
```

----------------------------------------

TITLE: Processing Return Flight Search Response in JSON
DESCRIPTION: The JSON response containing available return flights from Peru to San Diego. Each flight includes details such as flight number, departure/arrival information, airline, price, and number of stops.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/travel-concierge/tests/pre_booking_sample.md#2025-04-21_snippet_24

LANGUAGE: json
CODE:
```
Response from: "flight_search_agent"
response: {
  "flights": [
    {
      "flight_number": "LATAM2345",
      "departure": {
        "cityName": "Lima",
        "airportCode": "LIM",
        "timestamp": "2025-05-11T14:00:00Z"
      },
      "arrival": {
        "cityName": "San Diego",
        "airportCode": "SAN",
        "timestamp": "2025-05-12T02:00:00Z"
      },
      "airlines": [
        "LATAM Airlines"
      ],
      "airline_logo": "/images/LATAM.png",
      "priceInUSD": 650,
      "numberOfStops": 1
    },
    {
      "flight_number": "AVIANCA1234",
      "departure": {
        "cityName": "Lima",
        "airportCode": "LIM",
        "timestamp": "2025-05-11T18:00:00Z"
      },
      "arrival": {
        "cityName": "San Diego",
        "airportCode": "SAN",
        "timestamp": "2025-05-12T08:00:00Z"
      },
      "airlines": [
        "Avianca"
      ],
      "airline_logo": "/images/avianca.png",
      "priceInUSD": 700,
      "numberOfStops": 1
    },
    {
      "flight_number": "AmericanAirlines5678",
      "departure": {
        "cityName": "Cusco",
        "airportCode": "CUZ",
        "timestamp": "2025-05-11T10:00:00Z"
      },
      "arrival": {
        "cityName": "San Diego",
        "airportCode": "SAN",
        "timestamp": "2025-05-12T16:00:00Z"
      },
      "airlines": [
        "American Airlines"
      ],

```

----------------------------------------

TITLE: Running Agent Evaluation
DESCRIPTION: Command to run the agent evaluation using ADK's evaluation component, which tests the agent against predefined scenarios in the eval directory.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/brand-search-optimization/README.md#2025-04-21_snippet_2

LANGUAGE: bash
CODE:
```
sh deployment/eval.sh
```

----------------------------------------

TITLE: Transferring to Trip Monitor Agent
DESCRIPTION: Function call to transfer control from in_trip_agent to trip_monitor_agent with response handling.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/travel-concierge/tests/post_booking_sample.md#2025-04-21_snippet_5

LANGUAGE: json
CODE:
```
function call: "transfer_to_agent"
args: {
  "agent_name": "trip_monitor_agent"
}
```

LANGUAGE: json
CODE:
```
Response from: "transfer_to_agent"
response: {}
```

----------------------------------------

TITLE: Setting up IAM permissions for Reasoning Engine Service Agent in Bash
DESCRIPTION: Commands to grant BigQuery User and BigQuery Data Viewer permissions to the Reasoning Engine Service Agent, which are required for the agent to access BigQuery data.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/fomc-research/README.md#2025-04-21_snippet_11

LANGUAGE: bash
CODE:
```
export RE_SA="service-${GOOGLE_CLOUD_PROJECT_NUMBER}@gcp-sa-aiplatform-re.iam.gserviceaccount.com"
gcloud projects add-iam-policy-binding ${GOOGLE_CLOUD_PROJECT} \
    --member="serviceAccount:${RE_SA}" \
    --condition=None \
    --role="roles/bigquery.user"
gcloud projects add-iam-policy-binding ${GOOGLE_CLOUD_PROJECT} \
    --member="serviceAccount:${RE_SA}" \
    --condition=None \
    --role="roles/bigquery.dataViewer"
```

----------------------------------------

TITLE: Running the FOMC Research Agent with ADK Dev UI
DESCRIPTION: Command to start the ADK web-based development UI for the FOMC Research Agent, which provides a visual interface for interacting with the agent.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/fomc-research/README.md#2025-04-21_snippet_9

LANGUAGE: bash
CODE:
```
adk web .
```

----------------------------------------

TITLE: Cloning the ADK Samples Repository
DESCRIPTION: Commands to clone the ADK samples repository from GitHub and navigate to the repository directory.
SOURCE: https://github.com/google/adk-samples/blob/main/README.md#2025-04-21_snippet_0

LANGUAGE: bash
CODE:
```
git clone https://github.com/google/adk-samples.git
cd adk-samples
```

----------------------------------------

TITLE: POI Agent Function Call
DESCRIPTION: Function call to retrieve points of interest in Peru from a POI agent.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/travel-concierge/tests/pre_booking_sample.md#2025-04-21_snippet_4

LANGUAGE: json
CODE:
```
function call: "poi_agent"
args: {
  "request": "Peru"
}
```

----------------------------------------

TITLE: Testing Deployed Agent
DESCRIPTION: Command to run the test script for verifying the deployed agent
SOURCE: https://github.com/google/adk-samples/blob/main/agents/RAG/README.md#2025-04-21_snippet_15

LANGUAGE: bash
CODE:
```
python deployment/run.py
```

----------------------------------------

TITLE: Processing Seat Selection Response in JSON
DESCRIPTION: The JSON response from the seat selection agent containing available seats on the flight. The data is structured as a 2D array representing rows and seats, with each seat having availability status, price, and seat number.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/travel-concierge/tests/pre_booking_sample.md#2025-04-21_snippet_18

LANGUAGE: json
CODE:
```
Response from: "flight_seat_selection_agent"
response: {
  "seats": [
    [
      {
        "isAvailable": true,
        "priceInUSD": 60,
        "seatNumber": "1A"
      },
      {
        "isAvailable": true,
        "priceInUSD": 60,
        "seatNumber": "1B"
      },
      {
        "isAvailable": false,
        "priceInUSD": 60,
        "seatNumber": "1C"
      },
      {
        "isAvailable": true,
        "priceInUSD": 70,
        "seatNumber": "1D"
      },
      {
        "isAvailable": true,
        "priceInUSD": 70,
        "seatNumber": "1E"
      },
      {
        "isAvailable": true,
        "priceInUSD": 50,
        "seatNumber": "1F"
      }
    ],
    [
      {
        "isAvailable": true,
        "priceInUSD": 60,
        "seatNumber": "2A"
      },
      {
        "isAvailable": false,
        "priceInUSD": 60,
        "seatNumber": "2B"
      },
      {
        "isAvailable": true,
        "priceInUSD": 60,
        "seatNumber": "2C"
      },
      {
        "isAvailable": true,
        "priceInUSD": 70,
        "seatNumber": "2D"
      },
      {
        "isAvailable": true,
        "priceInUSD": 70,
        "seatNumber": "2E"
      },
      {
        "isAvailable": true,
        "priceInUSD": 50,
        "seatNumber": "2F"
      }
    ],
    [
      {
        "isAvailable": true,
        "priceInUSD": 60,
        "seatNumber": "3A"
      },
      {
        "isAvailable": true,
        "priceInUSD": 60,
        "seatNumber": "3B"
      },
      {
        "isAvailable": true,
        "priceInUSD": 60,
        "seatNumber": "3C"
      },
      {
        "isAvailable": true,
        "priceInUSD": 70,
        "seatNumber": "3D"
      },
      {
        "isAvailable": true,
        "priceInUSD": 70,
        "seatNumber": "3E"
      },
      {
        "isAvailable": true,
        "priceInUSD": 50,
        "seatNumber": "3F"
      }
    ],
    [
      {
        "isAvailable": true,
        "priceInUSD": 60,
        "seatNumber": "4A"
      },
      {
        "isAvailable": true,
        "priceInUSD": 60,
        "seatNumber": "4B"
      },
      {
        "isAvailable": true,
        "priceInUSD": 60,
        "seatNumber": "4C"
      },
      {
        "isAvailable": true,
        "priceInUSD": 70,
        "seatNumber": "4D"
      },
      {
        "isAvailable": true,
        "priceInUSD": 70,
        "seatNumber": "4E"
      },
      {
        "isAvailable": true,
        "priceInUSD": 50,
        "seatNumber": "4F"
      }
    ],
    [
      {
        "isAvailable": true,
        "priceInUSD": 60,
        "seatNumber": "5A"
      },
      {
        "isAvailable": true,
        "priceInUSD": 60,
        "seatNumber": "5B"
      },
      {
        "isAvailable": true,
        "priceInUSD": 60,
        "seatNumber": "5C"
      },
      {
        "isAvailable": true,
        "priceInUSD": 70,
        "seatNumber": "5D"
      },
      {
        "isAvailable": true,
        "priceInUSD": 70,
        "seatNumber": "5E"
      },
      {
        "isAvailable": true,
        "priceInUSD": 50,
        "seatNumber": "5F"
      }
    ]
  ]
}
```

----------------------------------------

TITLE: Cloning and Setting Up the FOMC Research Agent Repository
DESCRIPTION: Commands to clone the repository containing the FOMC Research Agent code and navigate to the correct directory.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/fomc-research/README.md#2025-04-21_snippet_2

LANGUAGE: bash
CODE:
```
git clone https://github.com/google/adk-samples.git
cd adk-samples/agents/fomc-research
```

----------------------------------------

TITLE: Map Tool Response with POI Details
DESCRIPTION: Response containing detailed map information for the points of interest in Peru, including Google Maps URLs and place IDs.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/travel-concierge/tests/pre_booking_sample.md#2025-04-21_snippet_7

LANGUAGE: json
CODE:
```
Response from: "map_tool"
response: {
  "result": [
    {
      "place_name": "Machu Picchu",
      "address": "Machu Picchu, Aguas Calientes, Peru",
      "lat": "-13.1547062",
      "long": "-72.5254412",
      "review_ratings": "4.7",
      "highlights": "Ancient Inca citadel set high in the Andes Mountains.",
      "image_url": "https://example.com/machu_picchu.jpg",
      "map_url": "https://www.google.com/maps/place/?q=place_id:ChIJNf_BuIOabZERglGl1iKpiYQ",
      "place_id": "ChIJNf_BuIOabZERglGl1iKpiYQ"
    },
    {
      "place_name": "Sacsayhuam\u00e1n",
      "address": "Sacsayhuam\u00e1n, Cusco, Peru",
      "lat": "-13.509856",
      "long": "-71.9816878",
      "review_ratings": "4.5",
      "highlights": "A walled complex on the northern outskirts of Cusco, Peru.",
      "image_url": "https://example.com/sacsayhuaman.jpg",
      "map_url": "https://www.google.com/maps/place/?q=place_id:ChIJ_agIfG7WbZERPIDD5LG4PJ4",
      "place_id": "ChIJ_agIfG7WbZERPIDD5LG4PJ4"
    },
    {
      "place_name": "Plaza de Armas, Cusco",
      "address": "Plaza de Armas, Cusco, Peru",
      "lat": "-13.5167681",
      "long": "-71.9787795",
      "review_ratings": "4.6",
      "highlights": "The heart of Cusco, surrounded by historical buildings and churches.",
      "image_url": "https://example.com/plaza_de_armas_cusco.jpg",
      "map_url": "https://www.google.com/maps/place/?q=place_id:ChIJdfHXnHPWbZERQ2P8gpCafAI",
      "place_id": "ChIJdfHXnHPWbZERQ2P8gpCafAI"
    },
    {
      "place_name": "Nazca Lines",
      "address": "Nazca Lines, Nazca, Peru",
      "lat": "-14.739027",
      "long": "-75.130005",
      "review_ratings": "4.3",
      "highlights": "Ancient geoglyphs in the Nazca Desert, best viewed from the air.",
      "image_url": "https://example.com/nazca_lines.jpg",
      "map_url": "https://www.google.com/maps/place/?q=place_id:ChIJrTK1zEYeFJERkbWXZrnSAhg",
      "place_id": "ChIJrTK1zEYeFJERkbWXZrnSAhg"
    },
    {
      "place_name": "Lake Titicaca",
      "address": "Lake Titicaca, Puno, Peru",
      "lat": "-15.8402218",
      "long": "-70.0218805",
      "review_ratings": "4.4",
      "highlights": "South America's largest lake, known for its floating islands.",
      "image_url": "https://example.com/lake_titicaca.jpg",
      "map_url": "https://www.google.com/maps/place/?q=place_id:ChIJNUHn9IVpXZERzzJN8tgdNB4",
      "place_id": "ChIJNUHn9IVpXZERzzJN8tgdNB4"
    }
  ]
}
```

----------------------------------------

TITLE: Testing Deployed Agent with Quick Test
DESCRIPTION: Command to quickly test a deployed agent with a simple prompt to verify functionality.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/travel-concierge/README.md#2025-04-21_snippet_13

LANGUAGE: bash
CODE:
```
python deployment/deploy.py --quicktest --resource_id=<RESOURCE_ID>
```

----------------------------------------

TITLE: Running Agent Trajectory Tests
DESCRIPTION: Command to run tests that evaluate the agent's conversational trajectory and decision paths.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/travel-concierge/README.md#2025-04-21_snippet_11

LANGUAGE: bash
CODE:
```
pytest eval
```

----------------------------------------

TITLE: Installing Project Dependencies with Poetry
DESCRIPTION: Command to install all required dependencies using Poetry, which manages the virtual environment and package installation for the project.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/travel-concierge/README.md#2025-04-21_snippet_2

LANGUAGE: bash
CODE:
```
poetry install
```

----------------------------------------

TITLE: Memorizing Trip End Date
DESCRIPTION: Function call to store the user's trip end date in the system memory.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/travel-concierge/tests/pre_booking_sample.md#2025-04-21_snippet_13

LANGUAGE: json
CODE:
```
function call: "memorize"
args: {
  "key": "end_date",
  "value": "2025-05-11"
}
```

----------------------------------------

TITLE: Enabling Required Google Cloud APIs for FOMC Research Agent
DESCRIPTION: These commands enable the necessary Google Cloud APIs (AI Platform and BigQuery) required for the FOMC Research Agent to function properly.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/fomc-research/README.md#2025-04-21_snippet_1

LANGUAGE: bash
CODE:
```
gcloud services enable aiplatform.googleapis.com
gcloud services enable bigquery.googleapis.com
```

----------------------------------------

TITLE: Transferring to Inspiration Agent
DESCRIPTION: Function call from root agent to transfer control to a specialized inspiration agent.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/travel-concierge/tests/pre_booking_sample.md#2025-04-21_snippet_0

LANGUAGE: json
CODE:
```
function call: "transfer_to_agent"
args: {
  "agent_name": "inspiration_agent"
}
```

----------------------------------------

TITLE: Installing FOMC Research Agent Requirements with Poetry
DESCRIPTION: Command to install all the dependencies required for the FOMC Research Agent using Poetry, including the Google Agent Development Kit.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/fomc-research/README.md#2025-04-21_snippet_4

LANGUAGE: bash
CODE:
```
poetry install
```

----------------------------------------

TITLE: Packing Recommendations Function Call
DESCRIPTION: Function call to the what_to_pack_agent with a request for packing recommendations for a trip from San Diego to Seattle in June.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/travel-concierge/tests/post_booking_sample.md#2025-04-21_snippet_2

LANGUAGE: json
CODE:
```
function call: "what_to_pack_agent"
args: {
  "request": "San Diego to Seattle in June"
}
```

----------------------------------------

TITLE: Installing Travel Concierge Project Dependencies
DESCRIPTION: Commands for cloning the repository, navigating to the travel-concierge directory, and installing dependencies using Poetry package manager.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/travel-concierge/README.md#2025-04-21_snippet_1

LANGUAGE: bash
CODE:
```
git clone https://github.com/google/adk-samples.git
cd adk-samples/agents/travel-concierge
```

----------------------------------------

TITLE: Google Search Grounding API Calls for Travel Information
DESCRIPTION: A series of function calls to gather travel information through Google Search API, including visa requirements, medical requirements, storm monitoring, and travel advisories.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/travel-concierge/tests/post_booking_sample.md#2025-04-21_snippet_1

LANGUAGE: json
CODE:
```
function call: "google_search_grounding"
args: {
  "request": "visa_requirements San Diego Seattle"
}
```

LANGUAGE: json
CODE:
```
function call: "google_search_grounding"
args: {
  "request": "medical_requirements San Diego Seattle"
}
```

LANGUAGE: json
CODE:
```
function call: "google_search_grounding"
args: {
  "request": "storm_monitor San Diego Seattle"
}
```

LANGUAGE: json
CODE:
```
function call: "google_search_grounding"
args: {
  "request": "travel_advisory San Diego Seattle"
}
```

----------------------------------------

TITLE: Downloading Product Data Files for Personalized Shopping Agent
DESCRIPTION: Bash commands to create a data directory and download necessary JSON files containing product information for initializing the web environment.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/personalized-shopping/README.md#2025-04-21_snippet_1

LANGUAGE: bash
CODE:
```
cd personalized_shopping/shared_libraries
mkdir data
cd data

# Download items_shuffle_1000 (4.5MB)
gdown https://drive.google.com/uc?id=1EgHdxQ_YxqIQlvvq5iKlCrkEKR6-j0Ib;

# Download items_ins_v2_1000 (147KB)
gdown https://drive.google.com/uc?id=1IduG0xl544V_A_jv3tHXC0kyFi7PnyBu;

# Download items_shuffle (5.1GB)
gdown https://drive.google.com/uc?id=1A2whVgOO0euk5O13n2iYDM0bQRkkRduB;

# Download items_ins_v2 (178MB)
gdown https://drive.google.com/uc?id=1s2j6NgHljiZzQNL3veZaAiyW_qDEgBNi;

# Download items_human_ins (4.9MB)
gdown https://drive.google.com/uc?id=14Kb5SPBk_jfdLZ_CDBNitW98QLDlKR5O
```

----------------------------------------

TITLE: Navigating Back to Main Product Page
DESCRIPTION: A function call to navigate back to the main product page from the description section. This shows how the shopping agent returns to the main page to access other sections of product information.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/personalized-shopping/tests/example_interactions/text_search_floral_dress.session.md#2025-04-21_snippet_6

LANGUAGE: json
CODE:
```
function call: "click"
args: {
  "button_name": "< Prev"
}
```

----------------------------------------

TITLE: Running Agent via ADK Dev UI - Bash Commands
DESCRIPTION: Commands to navigate to agent directory and launch the ADK web interface.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/README.md#2025-04-21_snippet_3

LANGUAGE: bash
CODE:
```
# Example (check agent's README for exact path)
cd agents/fomc-research/
adk web
```

----------------------------------------

TITLE: Place Agent Response with Destination Options
DESCRIPTION: Response containing three highlighted destinations in the Americas with their details including rating, country, and image URLs.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/travel-concierge/tests/pre_booking_sample.md#2025-04-21_snippet_3

LANGUAGE: json
CODE:
```
Response from: "place_agent"
response: {
  "places": [
    {
      "name": "Machu Picchu",
      "country": "Peru",
      "image": "https://upload.wikimedia.org/wikipedia/commons/e/eb/Machu_Picchu%2C_Peru.jpg",
      "highlights": "Ancient Inca citadel set high in the Andes Mountains, offering stunning views and rich history.",
      "rating": "4.8"
    },
    {
      "name": "Banff National Park",
      "country": "Canada",
      "image": "https://upload.wikimedia.org/wikipedia/commons/1/1e/Moraine_Lake_Sunrise.jpg",
      "highlights": "Turquoise glacial lakes, majestic mountains, and abundant wildlife in the heart of the Canadian Rockies.",
      "rating": "4.7"
    },
    {
      "name": "New York City",
      "country": "USA",
      "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/02/NYC_Downtown_Manhattan_ skyline_seen_from_Jersey_City_--_Oct_2019.jpg/1280px-NYC_Downtown_Manhattan_skyline_seen_from_Jersey_City_--_Oct_2019.jpg",
      "highlights": "Iconic landmarks, world-class museums, diverse neighborhoods, and vibrant cultural experiences.",
      "rating": "4.6"
    }
  ]
}
```

----------------------------------------

TITLE: Indexing Product Data for Personalized Shopping Agent
DESCRIPTION: Commands to convert product data to the required format and index them for use by the search engine.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/personalized-shopping/README.md#2025-04-21_snippet_2

LANGUAGE: bash
CODE:
```
cd ../search_engine
mkdir -p resources_100 resources_1k resources_10k resources_50k
python convert_product_file_format.py

mkdir -p indexes
bash run_indexing.sh
cd ../../
```

----------------------------------------

TITLE: Place Agent Function Call
DESCRIPTION: Function call to request place information about the Americas from a place agent.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/travel-concierge/tests/pre_booking_sample.md#2025-04-21_snippet_2

LANGUAGE: json
CODE:
```
function call: "place_agent"
args: {
  "request": "the americas"
}
```

----------------------------------------

TITLE: Running LLM Auditor with ADK
DESCRIPTION: Commands to run the LLM Auditor using ADK CLI and web interface
SOURCE: https://github.com/google/adk-samples/blob/main/agents/llm-auditor/README.md#2025-04-21_snippet_4

LANGUAGE: bash
CODE:
```
adk run llm_auditor
```

LANGUAGE: bash
CODE:
```
adk web
```

----------------------------------------

TITLE: Processing Search Results for Summer Dresses
DESCRIPTION: A JSON response containing search results for summer dresses. The response includes product IDs, names, and prices for multiple dress options that match the search criteria.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/personalized-shopping/tests/example_interactions/text_search_floral_dress.session.md#2025-04-21_snippet_1

LANGUAGE: json
CODE:
```
Response from: "search"
response: {
  "result": "Back to Search [SEP] Page 1 (Total results: 50) [SEP] Next > [SEP] B092QL1FLW [SEP] Women Summer Cold Shoulder Dress,Beach Vintage Bohemian Print Sundress Party Prom Swing Loose A-Line Dress with Pocket [SEP] $16.29 to $17.59 [SEP] B094Z77449 [SEP] Casual Summer Dress for Women,V-Neck Sleeveless High Waist Maternity Dress Loose Floral Print Maxi Pregnant Dress [SEP] $1.69 to $12.19 [SEP] B09MW6NN3H [SEP] Mind of My Own Maxi Dress for Womens Sexy Deep V Bodycon Long Dress Fashion Bag Hip Tie dye Printed Dresses [SEP] $7.99 to $14.99 [SEP] B09P8R92RL [SEP] SERCFGYUJ Women's Party Dresses Fashion V Neck Long Sleeve Slit Mini Dress Casual Printed Wrap Buttocks Ruched Prom Dress [SEP] $8.99 to $18.99 [SEP] B09P8RQFHL [SEP] New Years Dress for Women Plus Size Crew Neck Butterfly Print A-Line Long Dresses Casual Lace Splicing Prom Dress [SEP] $8.99 to $19.99 [SEP] B09P8S93S8 [SEP] Sparkly Dresses for Women Long Sleeve Stylish V Neck Mini Dress Casual Flower Butterfly Print Sequin Black Dress [SEP] $5.99 to $15.99 [SEP] B09MW5XWSZ [SEP] NaRHbrg Summer Casual Dress for Women's Boho V Neck Sleeveless Long Maxi Dresses Ladies Loose Pockets Dress Floor-Length [SEP] $4.99 to $13.99 [SEP] B08GRRPFHP [SEP] Alex Evenings Women's Long 3/4 Sleeve Velvet Dress [SEP] $109.65 to $192.06 [SEP] B09RDX8KQJ [SEP] FABIURT Sundresses for Women Casual Beach, Women's Summer Butterfly Printed Dress V-Neck Sleeveless Long Dresses with Pockets [SEP] $4.99 to $7.99 [SEP] B09JWJ5L8S [SEP] BB&KK Women's Summer Maxi Long Cold Shoulder Loose Kaftan Flowy Batwing Beach Cover Up Dress [SEP] $29.99"
}
```

----------------------------------------

TITLE: Authenticating GCloud Account for Personalized Shopping Agent
DESCRIPTION: Command to authenticate the user's GCloud account for accessing cloud resources.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/personalized-shopping/README.md#2025-04-21_snippet_3

LANGUAGE: bash
CODE:
```
gcloud auth application-default login
```

----------------------------------------

TITLE: Authenticating GCloud Account for API Access
DESCRIPTION: Command to authenticate the user's Google Cloud account for accessing Google APIs and services required by the travel concierge application.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/travel-concierge/README.md#2025-04-21_snippet_3

LANGUAGE: bash
CODE:
```
gcloud auth application-default login
```

----------------------------------------

TITLE: Running Tests and Evaluation
DESCRIPTION: Commands to install development dependencies and run tests
SOURCE: https://github.com/google/adk-samples/blob/main/agents/llm-auditor/README.md#2025-04-21_snippet_6

LANGUAGE: bash
CODE:
```
poetry install --with dev
```

LANGUAGE: bash
CODE:
```
python3 -m pytest tests
python3 -m pytest eval
```

----------------------------------------

TITLE: Authenticating with Google Cloud
DESCRIPTION: Command for authenticating with Google Cloud using gcloud CLI, necessary for accessing Google Cloud services required by the agent.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/customer-service/README.md#2025-04-21_snippet_8

LANGUAGE: bash
CODE:
```
gcloud auth login
```

----------------------------------------

TITLE: Day of Agent Function Call for Transport Help
DESCRIPTION: Function call to day_of_agent for assistance with transportation, providing a simple help request.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/travel-concierge/tests/post_booking_sample.md#2025-04-21_snippet_11

LANGUAGE: json
CODE:
```
function call: "day_of_agent"
args: {
  "request": "help"
}
```

LANGUAGE: json
CODE:
```
Response from: "day_of_agent"
response: {
```

----------------------------------------

TITLE: Enabling Required Google Cloud APIs
DESCRIPTION: Command to enable the necessary Google Cloud APIs for the agent, specifically the AI Platform service for Vertex AI integration.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/customer-service/README.md#2025-04-21_snippet_7

LANGUAGE: bash
CODE:
```
gcloud services enable aiplatform.googleapis.com
```

----------------------------------------

TITLE: Memory Storage Responses for Trip Details
DESCRIPTION: Series of confirmation responses showing the successful storage of trip details (origin, destination, start date, and end date) in the system memory.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/travel-concierge/tests/pre_booking_sample.md#2025-04-21_snippet_14

LANGUAGE: json
CODE:
```
Response from: "memorize"
response: {
  "status": "Stored \"origin\": \"San Diego, CA, USA\""
}


Response from: "memorize"
response: {
  "status": "Stored \"destination\": \"Peru\""
}


Response from: "memorize"
response: {
  "status": "Stored \"start_date\": \"2025-05-04\""
}


Response from: "memorize"
response: {
  "status": "Stored \"end_date\": \"2025-05-11\""
}
```

----------------------------------------

TITLE: Building a wheel file for agent deployment with Poetry
DESCRIPTION: Command to build a Python wheel file for the agent, which is required for deploying to Vertex AI Agent Engine.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/fomc-research/README.md#2025-04-21_snippet_12

LANGUAGE: bash
CODE:
```
poetry build --format=wheel --output=deployment
```

----------------------------------------

TITLE: Installing Dependencies and Running Tests with Poetry
DESCRIPTION: Commands for installing development dependencies and running tests using Poetry package manager.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/travel-concierge/README.md#2025-04-21_snippet_9

LANGUAGE: bash
CODE:
```
poetry install --with dev
pytest
```

----------------------------------------

TITLE: Running Unit Tests for Personalized Shopping Agent Tools
DESCRIPTION: Command to run unit tests for the tools used by the personalized shopping agent.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/personalized-shopping/README.md#2025-04-21_snippet_7

LANGUAGE: bash
CODE:
```
python3 -m pytest tests
```

----------------------------------------

TITLE: Running and Logging FOMC Research Agent in Background
DESCRIPTION: Commands to run the FOMC Research Agent in the background while capturing its output to a log file, and then viewing the log in real-time.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/fomc-research/README.md#2025-04-21_snippet_10

LANGUAGE: bash
CODE:
```
adk web . > fomc_research_log.txt 2>&1 &
tail -f fomc_research_log.txt
```

----------------------------------------

TITLE: Building Wheel File for Personalized Shopping Agent Deployment
DESCRIPTION: Command to build a wheel file of the personalized shopping agent for deployment.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/personalized-shopping/README.md#2025-04-21_snippet_8

LANGUAGE: bash
CODE:
```
cd agents/personalized-shopping
poetry build --format=wheel --output=deployment
```

----------------------------------------

TITLE: Transferring to Pre-trip Agent
DESCRIPTION: Function call to transfer control from root agent to pre_trip_agent with response handling.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/travel-concierge/tests/post_booking_sample.md#2025-04-21_snippet_0

LANGUAGE: json
CODE:
```
function call: "transfer_to_agent"
args: {
  "agent_name": "pre_trip_agent"
}
```

LANGUAGE: json
CODE:
```
Response from: "transfer_to_agent"
response: {}
```

----------------------------------------

TITLE: Transferring to In-trip Agent
DESCRIPTION: Function call to transfer control from pre_trip_agent to in_trip_agent with response handling.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/travel-concierge/tests/post_booking_sample.md#2025-04-21_snippet_4

LANGUAGE: json
CODE:
```
function call: "transfer_to_agent"
args: {
  "agent_name": "in_trip_agent"
}
```

LANGUAGE: json
CODE:
```
Response from: "transfer_to_agent"
response: {}
```

----------------------------------------

TITLE: Processing Hotel Payment (JSON)
DESCRIPTION: JSON function call to process payment for the hotel reservation using the credit card on file.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/travel-concierge/tests/pre_booking_sample.md#2025-04-21_snippet_34

LANGUAGE: json
CODE:
```
function call: "payment_agent"
args: {
  "request": "Pay $3,120 for hotel booking with reservation ID BHMC-4957 using credit card on file."
}
```

----------------------------------------

TITLE: Installing Agent Dependencies - Poetry Command
DESCRIPTION: Command to install Python dependencies using Poetry package manager.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/README.md#2025-04-21_snippet_1

LANGUAGE: bash
CODE:
```
poetry install
```

----------------------------------------

TITLE: Weather Impact Check Function Calls
DESCRIPTION: Function calls to check weather impacts for three outdoor activities in Seattle, providing activity name, location, and date for each.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/travel-concierge/tests/post_booking_sample.md#2025-04-21_snippet_8

LANGUAGE: json
CODE:
```
function call: "weather_impact_check"
args: {
  "activity_location": "85 Pike St, Seattle, WA 98101",
  "activity_date": "2025-06-16",
  "activity_name": "Pike Place Market"
}
```

LANGUAGE: json
CODE:
```
function call: "weather_impact_check"
args: {
  "activity_name": "Ivar's Acres of Clams",
  "activity_date": "2025-06-16",
  "activity_location": "1001 Alaskan Way, Pier 54, Seattle, WA 98104"
}
```

LANGUAGE: json
CODE:
```
function call: "weather_impact_check"
args: {
  "activity_name": "Capitol Hill Neighborhood",
  "activity_location": "Capitol Hill, Seattle, WA",
  "activity_date": "2025-06-16"
}
```

----------------------------------------

TITLE: Processing Connecting Flight Payment (JSON)
DESCRIPTION: JSON function call to process payment for the connecting flight reservation using the credit card on file.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/travel-concierge/tests/pre_booking_sample.md#2025-04-21_snippet_32

LANGUAGE: json
CODE:
```
function call: "payment_agent"
args: {
  "request": "Pay $120 for connecting flight with reservation ID 49285 using credit card on file."
}
```

----------------------------------------

TITLE: Map Tool Function Call
DESCRIPTION: Function call to retrieve map information for points of interest.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/travel-concierge/tests/pre_booking_sample.md#2025-04-21_snippet_6

LANGUAGE: json
CODE:
```
function call: "map_tool"
args: {
  "key": "poi"
}
```

----------------------------------------

TITLE: Weather Impact Check Responses
DESCRIPTION: Responses from the weather_impact_check function calls, indicating status of various flights and attractions including a closure notification for Space Needle.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/travel-concierge/tests/post_booking_sample.md#2025-04-21_snippet_9

LANGUAGE: json
CODE:
```
Response from: "weather_impact_check"
response: {
  "status": "Flight AA1234 checked"
}
```

LANGUAGE: json
CODE:
```
Response from: "weather_impact_check"
response: {
  "status": "Flight UA5678 checked"
}
```

LANGUAGE: json
CODE:
```
Response from: "weather_impact_check"
response: {
  "status": "Space Needle is closed."
}
```

LANGUAGE: json
CODE:
```
Response from: "weather_impact_check"
response: {
  "status": "Museum of Pop Culture (MoPOP) checked"
}
```

LANGUAGE: json
CODE:
```
Response from: "weather_impact_check"
response: {
  "status": "Pike Place Market checked"
}
```

LANGUAGE: json
CODE:
```
Response from: "weather_impact_check"
response: {
  "status": "Ivar's Acres of Clams checked"
}
```

LANGUAGE: json
CODE:
```
Response from: "weather_impact_check"
response: {
  "status": "Capitol Hill Neighborhood checked"
}
```

----------------------------------------

TITLE: Memorizing Hotel Selection in JSON
DESCRIPTION: Function call to memorize the selected hotel details including address, check-in/out times, name, price, and thumbnail image.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/travel-concierge/tests/pre_booking_sample.md#2025-04-21_snippet_25

LANGUAGE: json
CODE:
```
function call: "memorize"
args: {
  "value": "{\"address\": \"Calle Plazoleta Nazarenas, Cusco 08001, Peru\", \"check_in_time\": \"14:00\", \"check_out_time\": \"11:00\", \"name\": \"Belmond Hotel Monasterio\", \"price\": 450, \"thumbnail\": \"/src/images/hotel.png\"}",
  "key": "hotel_selection"
}
```

----------------------------------------

TITLE: Configuring Google Cloud Environment Variables
DESCRIPTION: Environment variable configuration for Google Cloud services
SOURCE: https://github.com/google/adk-samples/blob/main/agents/llm-auditor/README.md#2025-04-21_snippet_2

LANGUAGE: bash
CODE:
```
export GOOGLE_GENAI_USE_VERTEXAI=true
export GOOGLE_CLOUD_PROJECT=<your-project-id>
export GOOGLE_CLOUD_LOCATION=<your-project-location>
export GOOGLE_CLOUD_STORAGE_BUCKET=<your-storage-bucket>
```

----------------------------------------

TITLE: Memorize Function Call for Storing Date Information
DESCRIPTION: Function call to memorize a date value (2025-06-15 04:00:00) and store it in a variable named 'itinerary_datetime' with response handling.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/travel-concierge/tests/post_booking_sample.md#2025-04-21_snippet_10

LANGUAGE: json
CODE:
```
function call: "memorize"
args: {
  "key": "itinerary_datetime",
  "value": "2025-06-15 04:00:00"
}
```

LANGUAGE: json
CODE:
```
Response from: "memorize"
response: {
  "status": "Stored \"itinerary_datetime\": \"2025-06-15 04:00:00\""
}
```

----------------------------------------

TITLE: Running Evaluation Tests for Personalized Shopping Agent
DESCRIPTION: Command to run evaluation tests for the personalized shopping agent using pytest.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/personalized-shopping/README.md#2025-04-21_snippet_6

LANGUAGE: bash
CODE:
```
python3 -m pytest eval
```

----------------------------------------

TITLE: Cloning and Navigating to Repository
DESCRIPTION: Commands to clone the ADK samples repository from GitHub and navigate to the customer service agent directory.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/customer-service/README.md#2025-04-21_snippet_9

LANGUAGE: bash
CODE:
```
git clone https://github.com/google/adk-samples.git
cd adk-samples/agents/customer-service
```

----------------------------------------

TITLE: Running Unit Tests
DESCRIPTION: Command to run the unit tests for the agent, which include tests with a mock BigQuery client. Requires setting DISABLE_WEB_DRIVER=1 in the .env file.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/brand-search-optimization/README.md#2025-04-21_snippet_3

LANGUAGE: bash
CODE:
```
sh deployment/test.sh
```

----------------------------------------

TITLE: Processing Flight Payment (JSON)
DESCRIPTION: JSON function call to process payment for flight reservations using the credit card on file.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/travel-concierge/tests/pre_booking_sample.md#2025-04-21_snippet_30

LANGUAGE: json
CODE:
```
function call: "payment_agent"
args: {
  "request": "Pay $1250 for flights with reservation ID FLT987654321 using credit card on file."
}
```

----------------------------------------

TITLE: Deleting a deployed agent from Vertex AI Agent Engine
DESCRIPTION: Command to run the deployment script with the delete flag and a resource ID to remove the agent from Vertex AI Agent Engine.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/fomc-research/README.md#2025-04-21_snippet_16

LANGUAGE: bash
CODE:
```
python3 deployment/deploy.py --delete --resource_id=$RESOURCE_ID
```

----------------------------------------

TITLE: Response from Purchase Click Function
DESCRIPTION: Response data returned after clicking the Buy Now button, showing order confirmation details including product ASIN, selected options (size and color), and confirmation code for MTurk interface.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/personalized-shopping/tests/example_interactions/image_search_denim_skirt.session.md#2025-04-21_snippet_10

LANGUAGE: json
CODE:
```
Response from: "click"
response: {
  "result": "Thank you for shopping with us! [SEP] Your code: [SEP] None [SEP] (Paste it in your MTurk interface.) [SEP] Purchased [SEP] asin [SEP] B085T3HMGR [SEP] options [SEP] {\"color\": \"natural khaki\", \"size\": \"12 plus\"} [SEP] attrs [SEP] None [SEP] category [SEP] None [SEP] query [SEP] None [SEP] product category [SEP] None [SEP] Target [SEP] asin [SEP] options [SEP] attrs [SEP] price upper [SEP] instuction text [SEP] category [SEP] product category [SEP] query [SEP] Goal [SEP] None [SEP] Reward [SEP] Your score (min 0.0, max 1.0) [SEP] 0.0 [SEP] Reward Details [SEP] None"
}
```

----------------------------------------

TITLE: Processing Machu Picchu Visit Payment (JSON)
DESCRIPTION: JSON function call to process payment for the Machu Picchu visit reservation using the credit card on file.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/travel-concierge/tests/pre_booking_sample.md#2025-04-21_snippet_36

LANGUAGE: json
CODE:
```
function call: "payment_agent"
args: {
  "request": "Pay $150 for Machu Picchu visit with reservation ID MP-7594 using credit card on file."
}
```

----------------------------------------

TITLE: Listing Deployed LLM Auditor Agents
DESCRIPTION: Command to list all existing LLM Auditor agents deployed to Vertex AI Agent Engine, displaying their IDs, names, creation times, and update times.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/llm-auditor/README.md#2025-04-21_snippet_8

LANGUAGE: bash
CODE:
```
python3 deployment/deploy.py --list
```

----------------------------------------

TITLE: Deleting Deployed Agent from Vertex AI
DESCRIPTION: Command to delete a previously deployed agent from Vertex AI Agent Engine using its resource ID.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/travel-concierge/README.md#2025-04-21_snippet_14

LANGUAGE: bash
CODE:
```
python3 deployment/deploy.py --delete --resource_id=<RESOURCE_ID>
```

----------------------------------------

TITLE: Confirming Connecting Flight Reservation (JSON)
DESCRIPTION: JSON function call to confirm a connecting flight reservation from Lima to Cusco.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/travel-concierge/tests/pre_booking_sample.md#2025-04-21_snippet_31

LANGUAGE: json
CODE:
```
function call: "confirm_reservation_agent"
args: {
  "request": "Connecting flight from Lima (LIM) to Cusco (CUZ) on May 5, 2025, best available time"
}
```

----------------------------------------

TITLE: Memorizing Room Selection in JSON
DESCRIPTION: Function call to memorize the selected room type for the hotel booking.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/travel-concierge/tests/pre_booking_sample.md#2025-04-21_snippet_26

LANGUAGE: json
CODE:
```
function call: "memorize"
args: {
  "key": "room_selection",
  "value": "Queen Room with Balcony"
}
```

----------------------------------------

TITLE: Deleting a Deployed LLM Auditor Agent
DESCRIPTION: Command to delete a specific LLM Auditor agent from Vertex AI Agent Engine using its resource ID. This completely removes the agent from the platform.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/llm-auditor/README.md#2025-04-21_snippet_10

LANGUAGE: bash
CODE:
```
python3 deployment/deploy.py --delete --resource_id=${AGENT_ENGINE_ID}
```

----------------------------------------

TITLE: Confirming Hotel Reservation (JSON)
DESCRIPTION: JSON function call to confirm a hotel reservation at Belmond Hotel Monasterio in Cusco, Peru.
SOURCE: https://github.com/google/adk-samples/blob/main/agents/travel-concierge/tests/pre_booking_sample.md#2025-04-21_snippet_33

LANGUAGE: json
CODE:
```
function call: "confirm_reservation_agent"
args: {
  "request": "Hotel: Belmond Hotel Monasterio in Cusco, Peru. Check-in: May 5, 2025, Check-out: May 11, 2025. Room: Queen Room with Balcony."
}
```