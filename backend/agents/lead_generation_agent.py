import json
import logging
import os
import argparse # Added for server args
import asyncio
from typing import List, Dict, Any, Optional

import httpx
import uvicorn # Added for server
from fastapi import FastAPI, HTTPException, Body # Added for server
from pydantic import BaseModel, Field # Added for server models

# Assuming ADK and necessary libraries are installed
from google.adk.agents import Agent # Using base Agent as per original
from google.adk.runtime import InvocationContext
from google.adk.runtime.events import Event
# Firecrawl SDK
from firecrawl import FirecrawlApp
# Agno/Composio for Sheets (as per prototype) - Requires these libraries installed
try:
    from agno.agent import Agent as AgnoAgent
    from agno.tools.firecrawl import FirecrawlTools # Might not be needed
    from agno.models.google import Gemini as AgnoGeminiChat
    from composio_phidata import Action, ComposioToolSet
    AGNO_COMPOSIO_AVAILABLE = True
except ImportError:
    AGNO_COMPOSIO_AVAILABLE = False
    AgnoAgent = None # Define as None if not available
    AgnoGeminiChat = None
    ComposioToolSet = None
    Action = None
# Gemini library for query transformation (as per prototype)
try:
    import google.generativeai as genai
    GEMINI_SDK_AVAILABLE = True
except ImportError:
    genai = None
    GEMINI_SDK_AVAILABLE = False


# Configure logging
# Use logfire if configured globally, otherwise standard logging
try:
    import logfire
    logger = logfire
except ImportError:
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO"))

# --- Pydantic Schemas ---

class QuoraUserInteractionSchema(BaseModel):
    username: str = Field(description="The username of the user who posted the question or answer")
    bio: str = Field(description="The bio or description of the user")
    post_type: str = Field(description="The type of post, either 'question' or 'answer'")
    timestamp: str = Field(description="When the question or answer was posted")
    upvotes: int = Field(default=0, description="Number of upvotes received")
    links: List[str] = Field(default_factory=list, description="Any links included in the post")

class QuoraPageSchema(BaseModel):
    interactions: List[QuoraUserInteractionSchema] = Field(description="List of all user interactions (questions and answers) on the page")

class LeadGenInput(BaseModel):
    """Input model for the /invoke endpoint."""
    user_query: str = Field(description="Description of leads to find.")
    # API Keys are expected as environment variables now, not passed in request
    num_links: int = Field(default=3, description="Number of links to search.")

class LeadGenOutput(BaseModel):
    """Output model for the /invoke endpoint on success."""
    status: str
    google_sheet_link: Optional[str] = None
    leads_generated: Optional[int] = None
    message: Optional[str] = None # For cases like "No URLs found"

class LeadGenErrorOutput(BaseModel):
    """Output model for the /invoke endpoint on failure."""
    error: str


# --- Helper Functions (adapted from prototype) ---
# These will be run in a thread pool executor

def search_for_urls_sync(company_description: str, firecrawl_api_key: str, num_links: int) -> List[str]:
    """Synchronous version of Firecrawl search."""
    logger.info(f"Searching Firecrawl for '{company_description}' (sync)...")
    url = "https://api.firecrawl.dev/v1/search"
    headers = {"Authorization": f"Bearer {firecrawl_api_key}", "Content-Type": "application/json"}
    query = f"quora websites where people are looking for {company_description} services"
    payload = {"query": query, "limit": num_links, "lang": "en", "location": "United States", "timeout": 60000}
    try:
        # Use synchronous httpx client or requests library here
        with httpx.Client() as client:
            response = client.post(url, json=payload, headers=headers, timeout=70.0) # Slightly longer timeout
            response.raise_for_status()
        data = response.json()
        if data.get("success"):
            results = data.get("data", [])
            urls = [result["url"] for result in results if "url" in result]
            logger.info(f"Found {len(urls)} relevant URLs (sync).")
            return urls
        else:
            logger.warning(f"Firecrawl search API call was not successful (sync): {data}")
            return []
    except httpx.RequestError as e:
        logger.error(f"Error during Firecrawl search API call (sync): {e}", exc_info=True)
        return []
    except Exception as e:
        logger.error(f"Unexpected error during Firecrawl search (sync): {e}", exc_info=True)
        return []


def extract_user_info_from_urls_sync(urls: List[str], firecrawl_api_key: str) -> List[dict]:
    """Synchronous version of Firecrawl extraction."""
    user_info_list = []
    if not urls: return user_info_list
    try:
        firecrawl_app = FirecrawlApp(api_key=firecrawl_api_key)
        logger.info(f"Attempting to extract info from {len(urls)} URLs (sync).")
        for url in urls:
             logger.info(f"Extracting from: {url} (sync)")
             response = firecrawl_app.extract( # Assuming SDK handles sync/async internally or provides sync methods
                 url=url,
                 params={
                     'extractorOptions': {
                         'mode': 'llm-extraction',
                         'extractionPrompt': 'Extract all user information including username, bio, post type (question/answer), timestamp, upvotes, and any links from Quora posts. Focus on identifying potential leads who are asking questions or providing answers related to the topic.',
                         'extractionSchema': QuoraPageSchema.model_json_schema(),
                     }
                 }
             )
             if response and response.get('data'):
                 extracted_data = response['data']
                 interactions = extracted_data.get('interactions', [])
                 if isinstance(interactions, list) and interactions:
                     user_info_list.append({"website_url": url, "user_info": interactions})
                     logger.info(f"Successfully extracted info from {url} (sync)")
                 else: logger.warning(f"No interactions found or format incorrect for {url} (sync). Data: {extracted_data}")
             else: logger.warning(f"Extraction failed or returned no data for {url} (sync). Response: {response}")
    except Exception as e:
        logger.error(f"Error during Firecrawl extraction (sync): {e}", exc_info=True)
    logger.info(f"Extracted info for {len(user_info_list)} URLs (sync).")
    return user_info_list


def format_user_info_to_flattened_json_sync(user_info_list: List[dict]) -> List[dict]:
    """Synchronous formatting function."""
    flattened_data = []
    for info in user_info_list:
        website_url = info.get("website_url", "N/A")
        user_interactions = info.get("user_info", [])
        if not isinstance(user_interactions, list):
            logger.warning(f"Expected list for user_info, got {type(user_interactions)} for URL {website_url}")
            continue
        for interaction in user_interactions:
            if isinstance(interaction, dict):
                flattened_interaction = {
                    "Website URL": website_url,
                    "Username": interaction.get("username", ""), "Bio": interaction.get("bio", ""),
                    "Post Type": interaction.get("post_type", ""), "Timestamp": interaction.get("timestamp", ""),
                    "Upvotes": interaction.get("upvotes", 0), "Links": ", ".join(interaction.get("links", [])),
                }
                flattened_data.append(flattened_interaction)
            else: logger.warning(f"Expected dict for interaction, got {type(interaction)} for URL {website_url}")
    logger.info(f"Formatted data into {len(flattened_data)} flattened records (sync).")
    return flattened_data


def create_google_sheets_agent_sync(composio_api_key: str, gemini_api_key: str) -> Optional[AgnoAgent]:
    """Synchronous creation of Agno Agent."""
    if not AGNO_COMPOSIO_AVAILABLE:
        logger.error("Agno/Composio libraries not available. Cannot create Sheets agent.")
        return None
    try:
        composio_toolset = ComposioToolSet(api_key=composio_api_key)
        # Ensure Action enum is available and action name is correct
        if Action is None or not hasattr(Action, 'GOOGLESHEETS_SHEET_FROM_JSON'):
             logger.error("Composio Action 'GOOGLESHEETS_SHEET_FROM_JSON' not found.")
             return None
        google_sheets_tool = composio_toolset.get_tools(actions=[Action.GOOGLESHEETS_SHEET_FROM_JSON])[0]
        google_sheets_agent = AgnoAgent(
            model=AgnoGeminiChat(id="gemini-1.5-flash-latest", api_key=gemini_api_key), # Use updated model
            tools=[google_sheets_tool], show_tool_calls=True,
            system_prompt="You are an expert at creating Google Sheets. You will be given user information in JSON format, and you need to write it into a new Google Sheet.",
            markdown=True
        )
        logger.info("Created Google Sheets AgnoAgent (sync).")
        return google_sheets_agent
    except Exception as e:
        logger.error(f"Failed to create Google Sheets AgnoAgent (sync): {e}", exc_info=True)
        return None


def write_to_google_sheets_sync(flattened_data: List[dict], composio_api_key: str, gemini_api_key: str) -> str | None:
    """Synchronous writing to Google Sheets."""
    if not flattened_data:
        logger.warning("No data to write to Google Sheets (sync).")
        return None
    google_sheets_agent = create_google_sheets_agent_sync(composio_api_key, gemini_api_key)
    if not google_sheets_agent: return None
    try:
        message = (
            "Create a new Google Sheet with this data. "
            "Columns: Website URL, Username, Bio, Post Type, Timestamp, Upvotes, Links. "
            f"Data:\n\n{json.dumps(flattened_data, indent=2)}"
        )
        logger.info("Attempting to write data to Google Sheets (sync)...")
        create_sheet_response = google_sheets_agent.run(message) # Assuming run is synchronous
        if create_sheet_response and hasattr(create_sheet_response, 'content'):
             content = create_sheet_response.content
             if "https://docs.google.com/spreadsheets/d/" in content:
                 start_index = content.find("https://docs.google.com/spreadsheets/d/")
                 link_part = content[start_index:]
                 end_index = link_part.find(" ")
                 google_sheets_link = link_part if end_index == -1 else link_part[:end_index]
                 if google_sheets_link.startswith("https://docs.google.com/spreadsheets/d/"):
                     logger.info(f"Successfully wrote data to Google Sheet (sync): {google_sheets_link}")
                     return google_sheets_link
                 else: logger.error(f"Extracted link seems invalid (sync): {google_sheets_link}")
             else: logger.error(f"Google Sheet link not found in response content (sync): {content}")
        else: logger.error(f"Invalid or empty response from Google Sheets agent (sync): {create_sheet_response}")
    except Exception as e:
        logger.error(f"Error writing to Google Sheets (sync): {e}", exc_info=True)
    return None


# --- ADK Agent Definition ---

class LeadGenerationAgent(Agent):
    """
    An ADK agent that generates leads by searching Quora, extracting user info,
    and saving it to a Google Sheet. Uses A2A server structure.
    Requires FIRECRAWL_API_KEY, GEMINI_API_KEY, COMPOSIO_API_KEY env vars.
    """
    ENV_FIRECRAL_API_KEY = "FIRECRAWL_API_KEY"
    ENV_GEMINI_API_KEY = "GEMINI_API_KEY"
    ENV_COMPOSIO_API_KEY = "COMPOSIO_API_KEY" # For Sheets writing via Agno/Composio

    def __init__(self, agent_id: str = "lead-generation-agent"):
        super().__init__(agent_id=agent_id)
        logger.info(f"Initializing LeadGenerationAgent ({self.agent_id})...")
        # Get API keys from environment
        self.firecrawl_api_key = os.environ.get(self.ENV_FIRECRAL_API_KEY)
        self.gemini_api_key = os.environ.get(self.ENV_GEMINI_API_KEY)
        self.composio_api_key = os.environ.get(self.ENV_COMPOSIO_API_KEY)

        # Validate required keys
        if not self.firecrawl_api_key: logger.warning(f"{self.ENV_FIRECRAL_API_KEY} not set. Lead generation will likely fail.")
        if not self.gemini_api_key: logger.warning(f"{self.ENV_GEMINI_API_KEY} not set. Query transformation will fail.")
        if not self.composio_api_key: logger.warning(f"{self.ENV_COMPOSIO_API_KEY} not set. Google Sheets writing will fail.")
        if not AGNO_COMPOSIO_AVAILABLE: logger.warning("Agno/Composio libraries not installed. Google Sheets writing disabled.")
        if not GEMINI_SDK_AVAILABLE: logger.warning("google-generativeai library not installed. Query transformation disabled.")

        logger.info(f"LeadGenerationAgent ({self.agent_id}) initialized.")


    async def transform_query_async(self, user_query: str) -> str:
        """Transforms the user query into a concise company description using Gemini."""
        if not self.gemini_api_key or not genai:
            logger.error("Gemini API key or SDK not available for query transformation.")
            raise ValueError("Query transformation prerequisites not met.")
        logger.info("Transforming user query...")
        try:
            # Configure genai if not done globally (might be redundant if done elsewhere)
            # genai.configure(api_key=self.gemini_api_key)
            model = genai.GenerativeModel("gemini-1.5-flash-latest") # Use configured model
            prompt = f"""You are an expert at transforming detailed user queries into concise company descriptions.
Extract the core business/product focus in 3-4 words. Examples:
Input: "Generate leads looking for AI-powered customer support chatbots for e-commerce stores." Output: "AI customer support chatbots for e commerce"
Input: "Find people interested in voice cloning technology for creating audiobooks and podcasts" Output: "voice cloning technology"
Input: "Looking for users who need automated video editing software with AI capabilities" Output: "AI video editing software"
Input: "Need to find businesses interested in implementing machine learning solutions for fraud detection" Output: "ML fraud detection"
Always focus on the core product/service and keep it concise but clear. Transform this query: "{user_query}"
"""
            # Use async generation
            response = await model.generate_content_async(prompt)
            transformed_query = response.text.strip()
            logger.info(f"Transformed query: '{transformed_query}'")
            return transformed_query
        except Exception as e:
            logger.error(f"Error transforming query with LLM: {e}", exc_info=True)
            raise ValueError(f"Failed to transform query: {e}")


    async def run_async(self, context: InvocationContext) -> Event:
        """Executes the lead generation workflow."""
        logger.info(f"[{self.agent_id}] Invoked: {context.invocation_id}")
        google_sheet_link = None # Initialize
        leads_generated_count = 0

        try:
            # 1. Get inputs from context data
            if not isinstance(context.data, dict):
                raise ValueError("Input data must be a dictionary.")
            input_data = LeadGenInput(**context.data) # Validate input
            user_query = input_data.user_query
            num_links = input_data.num_links

            # Check for required API keys loaded during init
            if not self.firecrawl_api_key or not self.gemini_api_key or not self.composio_api_key or not AGNO_COMPOSIO_AVAILABLE or not GEMINI_SDK_AVAILABLE:
                 missing = []
                 if not self.firecrawl_api_key: missing.append(self.ENV_FIRECRAL_API_KEY)
                 if not self.gemini_api_key: missing.append(self.ENV_GEMINI_API_KEY)
                 if not self.composio_api_key: missing.append(self.ENV_COMPOSIO_API_KEY)
                 if not AGNO_COMPOSIO_AVAILABLE: missing.append("Agno/Composio libs")
                 if not GEMINI_SDK_AVAILABLE: missing.append("google-generativeai lib")
                 raise ValueError(f"Missing prerequisites: {', '.join(missing)}")

            # 2. Transform user query (async)
            company_description = await self.transform_query_async(user_query)
            await context.emit(Event(type="query_transformed", data={"description": company_description})) # Use emit

            # 3. Search for URLs (run sync in executor)
            urls = await asyncio.to_thread(
                search_for_urls_sync, company_description, self.firecrawl_api_key, num_links
            )
            if not urls:
                logger.warning("No relevant URLs found.")
                return context.create_event(event_type="lead_generation_complete", data={"status": "No URLs found", "google_sheet_link": None}, metadata={"status": "success"})
            await context.emit(Event(type="urls_found", data={"count": len(urls), "urls": urls}))

            # 4. Extract user info (run sync in executor)
            user_info_list = await asyncio.to_thread(
                extract_user_info_from_urls_sync, urls, self.firecrawl_api_key
            )
            await context.emit(Event(type="info_extracted", data={"records_found": len(user_info_list)}))

            # 5. Format data (run sync in executor)
            flattened_data = await asyncio.to_thread(
                format_user_info_to_flattened_json_sync, user_info_list
            )
            leads_generated_count = len(flattened_data)
            if not flattened_data:
                 logger.warning("No data available after formatting.")
                 return context.create_event(event_type="lead_generation_complete", data={"status": "No leads generated after formatting", "google_sheet_link": None}, metadata={"status": "success"})
            await context.emit(Event(type="data_formatted", data={"records_formatted": leads_generated_count}))

            # 6. Write to Google Sheets (run sync in executor)
            google_sheets_link = await asyncio.to_thread(
                write_to_google_sheets_sync, flattened_data, self.composio_api_key, self.gemini_api_key
            )

            if google_sheets_link:
                logger.info("Lead generation process completed successfully.")
                final_payload = {
                    "status": "Success", "google_sheet_link": google_sheets_link,
                    "leads_generated": leads_generated_count
                }
                return context.create_event(event_type="lead_generation_complete", data=final_payload, metadata={"status": "success"})
            else:
                logger.error("Failed to write data to Google Sheets.")
                raise RuntimeError("Failed to write data to Google Sheets.") # Raise error to be caught below

        except Exception as e:
            logger.exception(f"An unexpected error occurred during lead generation: {e}")
            # Use context helper to create error event
            return context.create_event(
                event_type="lead_generation_failed",
                data={"error": f"An unexpected error occurred: {str(e)}"},
                metadata={"status": "error"}
            )


# --- FastAPI Server Setup ---

app = FastAPI(title="LeadGenerationAgent A2A Server")

# Instantiate the agent (reads env vars internally)
try:
    lead_gen_agent_instance = LeadGenerationAgent()
except ValueError as e:
    logger.critical(f"Failed to initialize LeadGenerationAgent: {e}. Server cannot start.", exc_info=True)
    import sys
    sys.exit(f"Agent Initialization Error: {e}")


@app.post("/invoke") # Define specific output models later if needed
async def invoke_agent(request: LeadGenInput = Body(...)):
    """
    A2A endpoint to invoke the LeadGenerationAgent.
    Expects JSON body matching LeadGenInput.
    Returns result payload on success, or raises HTTPException on error.
    """
    logger.info(f"LeadGenerationAgent /invoke called for query: {request.user_query}")
    invocation_id = f"leadgen-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(1000,9999)}"
    # Pass API keys from agent instance (loaded from env) into context data if needed by run_async
    # Or modify run_async to access self.api_keys directly
    context_data = request.model_dump()
    # Add keys if run_async expects them (it currently does, but could be refactored)
    context_data["firecrawl_api_key"] = lead_gen_agent_instance.firecrawl_api_key
    context_data["gemini_api_key"] = lead_gen_agent_instance.gemini_api_key
    context_data["composio_api_key"] = lead_gen_agent_instance.composio_api_key

    context = InvocationContext(agent_id="lead-generation-agent", invocation_id=invocation_id, data=context_data)

    try:
        result_event = await lead_gen_agent_instance.run_async(context)

        if result_event and isinstance(result_event.data, dict):
            if result_event.metadata.get("status") == "error":
                 error_msg = result_event.data.get("error", "Unknown agent error")
                 logger.error(f"LeadGenerationAgent run_async returned error event: {error_msg}")
                 raise HTTPException(status_code=500, detail=LeadGenErrorOutput(error=error_msg).model_dump())
            else:
                 logger.info(f"LeadGenerationAgent returning success result.")
                 # Validate against success output model
                 try:
                     output_payload = LeadGenOutput(**result_event.data)
                     return output_payload
                 except ValidationError as val_err:
                     logger.error(f"Success event payload validation failed: {val_err}. Payload: {result_event.data}")
                     raise HTTPException(status_code=500, detail={"error": "Internal validation error on success payload.", "details": val_err.errors()})
        else:
            logger.error(f"LeadGenerationAgent run_async returned None or invalid event data: {result_event}")
            raise HTTPException(status_code=500, detail=LeadGenErrorOutput(error="Agent execution failed to return a valid event.").model_dump())

    except HTTPException as http_exc:
        raise http_exc # Re-raise FastAPI exceptions
    except Exception as e:
        logger.error(f"Error during agent invocation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=LeadGenErrorOutput(error=f"Internal server error: {e}").model_dump())


@app.get("/health")
async def health_check():
    # Add checks for API key presence if desired
    return {"status": "ok"}

# --- Main execution block ---

if __name__ == "__main__":
    # Load .env for local development if needed
    try:
        from dotenv import load_dotenv
        if load_dotenv():
             logger.info("Loaded .env file for local run.")
        else:
             logger.info("No .env file found or it was empty.")
    except ImportError:
        logger.info("dotenv library not found, skipping .env load.")

    parser = argparse.ArgumentParser(description="Run the LeadGenerationAgent A2A server.")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind the server to.")
    parser.add_argument("--port", type=int, default=8087, help="Port to run the server on.") # Default matches compose
    args = parser.parse_args()

    # Optional: Add checks here for required env vars before starting server
    # required_vars = [LeadGenerationAgent.ENV_FIRECRAL_API_KEY, LeadGenerationAgent.ENV_GEMINI_API_KEY, LeadGenerationAgent.ENV_COMPOSIO_API_KEY]
    # missing_vars = [v for v in required_vars if not os.environ.get(v)]
    # if missing_vars:
    #     print(f"CRITICAL ERROR: Missing environment variables: {', '.join(missing_vars)}")
    #     import sys
    #     sys.exit(1)

    print(f"Starting LeadGenerationAgent A2A server on {args.host}:{args.port}")

    uvicorn.run(app, host=args.host, port=args.port)