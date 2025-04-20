import json
import logging
import httpx
from typing import List, Dict, Any

from google.adk.agents import Agent
from google.adk.runtime import InvocationContext
from google.adk.runtime.events import Event
# Assuming ADK provides LLM integration, replace if needed
# from google.adk.llm import LlmClient
from firecrawl import FirecrawlApp
from pydantic import BaseModel, Field
# Keep agno/composio for Sheets writing as per prototype logic transfer
from agno.agent import Agent as AgnoAgent
from agno.tools.firecrawl import FirecrawlTools # Might not be needed if using SDK directly
from agno.models.google import Gemini as AgnoGeminiChat
from composio_phidata import Action, ComposioToolSet

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Pydantic Schemas (from prototype) ---

class QuoraUserInteractionSchema(BaseModel):
    username: str = Field(description="The username of the user who posted the question or answer")
    bio: str = Field(description="The bio or description of the user")
    post_type: str = Field(description="The type of post, either 'question' or 'answer'")
    timestamp: str = Field(description="When the question or answer was posted")
    upvotes: int = Field(default=0, description="Number of upvotes received")
    links: List[str] = Field(default_factory=list, description="Any links included in the post")

class QuoraPageSchema(BaseModel):
    interactions: List[QuoraUserInteractionSchema] = Field(description="List of all user interactions (questions and answers) on the page")

# --- Helper Functions (adapted from prototype) ---

def search_for_urls(company_description: str, firecrawl_api_key: str, num_links: int) -> List[str]:
    """Searches Firecrawl for relevant Quora URLs."""
    url = "https://api.firecrawl.dev/v1/search"
    headers = {
        "Authorization": f"Bearer {firecrawl_api_key}",
        "Content-Type": "application/json"
    }
    query = f"quora websites where people are looking for {company_description} services"
    payload = {
        "query": query,
        "limit": num_links,
        "lang": "en",
        "location": "United States", # Consider making this configurable
        "timeout": 60000,
    }
    try:
        response = httpx.post(url, json=payload, headers=headers)
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
        data = response.json()
        if data.get("success"):
            results = data.get("data", [])
            urls = [result["url"] for result in results]
            logger.info(f"Found {len(urls)} relevant URLs.")
            return urls
        else:
            logger.warning(f"Firecrawl search API call was not successful: {data}")
            return []
    except httpx.exceptions.RequestException as e:
        logger.error(f"Error during Firecrawl search API call: {e}")
        return []

def extract_user_info_from_urls(urls: List[str], firecrawl_api_key: str) -> List[dict]:
    """Extracts user info from URLs using Firecrawl SDK."""
    user_info_list = []
    if not urls:
        return user_info_list

    firecrawl_app = FirecrawlApp(api_key=firecrawl_api_key)
    logger.info(f"Attempting to extract info from {len(urls)} URLs.")

    # Note: FirecrawlApp.extract takes a list of URLs, process them potentially in batch
    try:
        # Process URLs one by one as in prototype, though batch might be possible
        for url in urls:
             logger.info(f"Extracting from: {url}")
             # Using extract method as per prototype logic
             response = firecrawl_app.extract(
                 url=url, # Pass single URL
                 params={
                     'extractorOptions': {
                         'mode': 'llm-extraction',
                         'extractionPrompt': 'Extract all user information including username, bio, post type (question/answer), timestamp, upvotes, and any links from Quora posts. Focus on identifying potential leads who are asking questions or providing answers related to the topic.',
                         'extractionSchema': QuoraPageSchema.model_json_schema(),
                     }
                 }
             )

             # Check response structure - adjust based on actual Firecrawl SDK v0.1.18+ response
             if response and response.get('data'):
                 extracted_data = response['data']
                 # Ensure interactions data is present and is a list
                 interactions = extracted_data.get('interactions', [])
                 if isinstance(interactions, list) and interactions:
                     user_info_list.append({
                         "website_url": url,
                         "user_info": interactions # interactions should be list of dicts matching schema
                     })
                     logger.info(f"Successfully extracted info from {url}")
                 else:
                     logger.warning(f"No interactions found or interactions format incorrect for {url}. Data: {extracted_data}")
             else:
                 logger.warning(f"Extraction failed or returned no data for {url}. Response: {response}")

    except Exception as e:
        logger.error(f"Error during Firecrawl extraction: {e}", exc_info=True)
        # Continue processing other URLs if one fails

    logger.info(f"Extracted info for {len(user_info_list)} URLs.")
    return user_info_list


def format_user_info_to_flattened_json(user_info_list: List[dict]) -> List[dict]:
    """Formats the extracted user info into a flattened list of dictionaries."""
    flattened_data = []
    for info in user_info_list:
        website_url = info.get("website_url", "N/A")
        user_interactions = info.get("user_info", []) # This should be a list of dicts

        # Ensure user_interactions is a list
        if not isinstance(user_interactions, list):
            logger.warning(f"Expected list for user_info, got {type(user_interactions)} for URL {website_url}")
            continue

        for interaction in user_interactions:
             # Ensure interaction is a dictionary before accessing keys
            if isinstance(interaction, dict):
                flattened_interaction = {
                    "Website URL": website_url,
                    "Username": interaction.get("username", ""),
                    "Bio": interaction.get("bio", ""),
                    "Post Type": interaction.get("post_type", ""),
                    "Timestamp": interaction.get("timestamp", ""),
                    "Upvotes": interaction.get("upvotes", 0),
                    "Links": ", ".join(interaction.get("links", [])), # Handle if links is not list
                }
                flattened_data.append(flattened_interaction)
            else:
                logger.warning(f"Expected dict for interaction, got {type(interaction)} for URL {website_url}")

    logger.info(f"Formatted data into {len(flattened_data)} flattened records.")
    return flattened_data

# Placeholder for Google Sheets writing using Agno/Composio as per prototype
# Ideally, this would use ADK tools or direct Google API client
def create_google_sheets_agent(composio_api_key: str, gemini_api_key: str) -> AgnoAgent:
    """Creates an Agno Agent configured for Google Sheets via Composio."""
    try:
        composio_toolset = ComposioToolSet(api_key=composio_api_key)
        # Ensure the action name is correct
        google_sheets_tool = composio_toolset.get_tools(actions=[Action.GOOGLESHEETS_SHEET_FROM_JSON])[0]

        google_sheets_agent = AgnoAgent(
            model=AgnoGeminiChat(id="gemini-2.5-flash-preview-04-17", api_key=gemini_api_key), # Consider making model configurable
            tools=[google_sheets_tool],
            show_tool_calls=True, # For debugging
            system_prompt="You are an expert at creating Google Sheets. You will be given user information in JSON format, and you need to write it into a new Google Sheet.",
            markdown=True
        )
        logger.info("Created Google Sheets AgnoAgent.")
        return google_sheets_agent
    except Exception as e:
        logger.error(f"Failed to create Google Sheets AgnoAgent: {e}", exc_info=True)
        raise

def write_to_google_sheets(flattened_data: List[dict], composio_api_key: str, gemini_api_key: str) -> str | None:
    """Writes data to Google Sheets using the Agno/Composio agent."""
    if not flattened_data:
        logger.warning("No data to write to Google Sheets.")
        return None

    try:
        google_sheets_agent = create_google_sheets_agent(composio_api_key, gemini_api_key)
        message = (
            "Create a new Google Sheet with this data. "
            "The sheet should have these columns: Website URL, Username, Bio, Post Type, Timestamp, Upvotes, and Links in the same order as mentioned. "
            "Here's the data in JSON format:\n\n"
            f"{json.dumps(flattened_data, indent=2)}"
        )

        logger.info("Attempting to write data to Google Sheets...")
        create_sheet_response = google_sheets_agent.run(message) # Assuming run is synchronous

        # Parse the response to find the Google Sheet link
        if create_sheet_response and hasattr(create_sheet_response, 'content'):
             content = create_sheet_response.content
             if "https://docs.google.com/spreadsheets/d/" in content:
                 # Extract the link robustly
                 start_index = content.find("https://docs.google.com/spreadsheets/d/")
                 link_part = content[start_index:]
                 # Find the end of the link (space or end of string)
                 end_index = link_part.find(" ")
                 if end_index == -1:
                     google_sheets_link = link_part
                 else:
                     google_sheets_link = link_part[:end_index]

                 # Basic validation
                 if google_sheets_link.startswith("https://docs.google.com/spreadsheets/d/"):
                     logger.info(f"Successfully wrote data to Google Sheet: {google_sheets_link}")
                     return google_sheets_link
                 else:
                     logger.error(f"Extracted link seems invalid: {google_sheets_link}")
             else:
                 logger.error(f"Google Sheet link not found in response content: {content}")
        else:
            logger.error(f"Invalid or empty response from Google Sheets agent: {create_sheet_response}")

    except Exception as e:
        logger.error(f"Error writing to Google Sheets: {e}", exc_info=True)

    return None

# --- ADK Agent Definition ---

class LeadGenerationAgent(Agent):
    """
    An ADK agent that generates leads by searching Quora, extracting user info,
    and saving it to a Google Sheet.
    """

    def __init__(self, llm_client=None): # Accept optional LLM client if needed
        super().__init__()
        # Placeholder for ADK LLM Client initialization if needed for transformation
        # self.llm = llm_client or LlmClient() # Example
        # Or initialize Gemini client directly if ADK doesn't provide one easily
        # self.gemini_client = Gemini(api_key=...) # Needs API key source

    async def transform_query_async(self, user_query: str, gemini_api_key: str) -> str:
        """Transforms the user query into a concise company description using an LLM."""
        # This part replaces the prototype's `create_prompt_transformation_agent`
        # Using direct Gemini call as a placeholder for ADK's LLM integration
        # In a real ADK setup, you'd use the provided LLM client/mechanism
        logger.info("Transforming user query...")
        try:
            # Example using Gemini client directly (requires 'gemini' package)
            from gemini import Gemini
            client = Gemini(api_key=gemini_api_key)

            prompt = f"""You are an expert at transforming detailed user queries into concise company descriptions.
Your task is to extract the core business/product focus in 3-4 words.

Examples:
Input: "Generate leads looking for AI-powered customer support chatbots for e-commerce stores."
Output: "AI customer support chatbots for e commerce"

Input: "Find people interested in voice cloning technology for creating audiobooks and podcasts"
Output: "voice cloning technology"

Input: "Looking for users who need automated video editing software with AI capabilities"
Output: "AI video editing software"

Input: "Need to find businesses interested in implementing machine learning solutions for fraud detection"
Output: "ML fraud detection"

Always focus on the core product/service and keep it concise but clear.

Transform this query: "{user_query}"
"""
            response = client.chat.completions.create(
                model="gemini-2.5-flash-preview-04-17", # Consider making model configurable
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
            )
            transformed_query = response.choices[0].message.content.strip()
            logger.info(f"Transformed query: '{transformed_query}'")
            return transformed_query
        except Exception as e:
            logger.error(f"Error transforming query with LLM: {e}", exc_info=True)
            # Fallback or re-raise? For now, return original query or raise error
            raise ValueError(f"Failed to transform query: {e}")


    async def run_async(self, context: InvocationContext) -> Event:
        """
        Executes the lead generation workflow.

        Expected context.data keys:
        - user_query: str - Description of leads to find.
        - firecrawl_api_key: str - Firecrawl API key.
        - gemini_api_key: str - Gemini API key.
        - composio_api_key: str - Composio API key.
        - num_links: int (optional, default 3) - Number of links to search.
        """
        logger.info(f"LeadGenerationAgent invoked with context ID: {context.invocation_id}")

        try:
            # 1. Get inputs from context
            user_query = context.data.get("user_query")
            firecrawl_api_key = context.data.get("firecrawl_api_key")
            gemini_api_key = context.data.get("gemini_api_key")
            composio_api_key = context.data.get("composio_api_key")
            num_links = context.data.get("num_links", 3) # Default to 3 links

            if not all([user_query, firecrawl_api_key, gemini_api_key, composio_api_key]):
                missing_keys = [k for k, v in {
                    "user_query": user_query,
                    "firecrawl_api_key": firecrawl_api_key,
                    "gemini_api_key": gemini_api_key,
                    "composio_api_key": composio_api_key
                }.items() if not v]
                error_msg = f"Missing required context data: {', '.join(missing_keys)}"
                logger.error(error_msg)
                return Event(
                    type="lead_generation_failed",
                    data={"error": error_msg}
                )

            # 2. Transform user query
            # Note: Using await for async function
            company_description = await self.transform_query_async(user_query, gemini_api_key)
            await context.post_event_async(Event(type="query_transformed", data={"description": company_description}))

            # 3. Search for URLs (Synchronous function, run in executor if needed)
            # For simplicity, calling sync function directly in async context (consider thread pool)
            urls = search_for_urls(company_description, firecrawl_api_key, num_links)
            if not urls:
                logger.warning("No relevant URLs found.")
                return Event(type="lead_generation_complete", data={"status": "No URLs found", "google_sheet_link": None})
            await context.post_event_async(Event(type="urls_found", data={"count": len(urls), "urls": urls}))

            # 4. Extract user info (Synchronous function)
            user_info_list = extract_user_info_from_urls(urls, firecrawl_api_key)
            if not user_info_list:
                 logger.warning("No user information extracted from found URLs.")
                 # Proceed to formatting, it will handle empty list
            await context.post_event_async(Event(type="info_extracted", data={"records_found": len(user_info_list)}))


            # 5. Format data (Synchronous function)
            flattened_data = format_user_info_to_flattened_json(user_info_list)
            if not flattened_data:
                 logger.warning("No data available after formatting.")
                 # Decide if this is an error or just completion with no results
                 return Event(type="lead_generation_complete", data={"status": "No leads generated after formatting", "google_sheet_link": None})
            await context.post_event_async(Event(type="data_formatted", data={"records_formatted": len(flattened_data)}))


            # 6. Write to Google Sheets (Synchronous function using Agno/Composio)
            google_sheets_link = write_to_google_sheets(flattened_data, composio_api_key, gemini_api_key)

            if google_sheets_link:
                logger.info("Lead generation process completed successfully.")
                return Event(
                    type="lead_generation_complete",
                    data={
                        "status": "Success",
                        "google_sheet_link": google_sheets_link,
                        "leads_generated": len(flattened_data)
                    }
                )
            else:
                logger.error("Failed to write data to Google Sheets.")
                return Event(
                    type="lead_generation_failed",
                    data={"error": "Failed to write data to Google Sheets."}
                )

        except Exception as e:
            logger.exception(f"An unexpected error occurred during lead generation: {e}")
            return Event(
                type="lead_generation_failed",
                data={"error": f"An unexpected error occurred: {str(e)}"}
            )