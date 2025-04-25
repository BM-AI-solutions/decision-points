"""
Lead Generation Agent for Decision Points (ADK Version).

This agent generates leads by searching Quora, extracting user info, and saving it to a Google Sheet using ADK tools.
"""

import json
import logging
import httpx
from typing import List, Dict, Any, Optional

# ADK Imports
from google.adk.agents import Agent # Use ADK Agent
from google.adk.tools import tool # Import tool decorator

from firecrawl import FirecrawlApp
from pydantic import BaseModel, Field
# Keep agno/composio for Sheets writing as per prototype logic transfer
from agno.agent import Agent as AgnoAgent
from agno.tools.firecrawl import FirecrawlTools # Might not be needed if using SDK directly
from agno.models.google import Gemini as AgnoGeminiChat
from composio_phidata import Action, ComposioToolSet

# Removed BaseSpecializedAgent import
from app.config import settings

# Configure logging
logger = logging.getLogger(__name__)

# --- Pydantic Schemas (Keep as they define data structures) ---

class QuoraUserInteractionSchema(BaseModel):
    username: str = Field(description="The username of the user who posted the question or answer")
    bio: str = Field(description="The bio or description of the user")
    post_type: str = Field(description="The type of post, either 'question' or 'answer'")
    timestamp: str = Field(description="When the question or answer was posted")
    upvotes: int = Field(default=0, description="Number of upvotes received")
    links: List[str] = Field(default_factory=list, description="Any links included in the post")

class QuoraPageSchema(BaseModel):
    interactions: List[QuoraUserInteractionSchema] = Field(description="List of all user interactions (questions and answers) on the page")

# --- Helper Functions (Keep as they contain core logic) ---

def search_for_urls(company_description: str, firecrawl_api_key: str, num_links: int) -> List[str]:
    """Searches Firecrawl for relevant Quora URLs."""
    # (Implementation remains the same)
    url = "https://api.firecrawl.dev/v1/search"
    headers = {"Authorization": f"Bearer {firecrawl_api_key}", "Content-Type": "application/json"}
    query = f"quora websites where people are looking for {company_description} services"
    payload = {"query": query, "limit": num_links, "lang": "en", "location": "United States", "timeout": 60000}
    try:
        response = httpx.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        if data.get("success"):
            urls = [result["url"] for result in data.get("data", [])]
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
    # (Implementation remains the same)
    user_info_list = []
    if not urls: return user_info_list
    firecrawl_app = FirecrawlApp(api_key=firecrawl_api_key)
    logger.info(f"Attempting to extract info from {len(urls)} URLs.")
    try:
        for url in urls:
             logger.info(f"Extracting from: {url}")
             response = firecrawl_app.extract(
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
                     logger.info(f"Successfully extracted info from {url}")
                 else:
                     logger.warning(f"No interactions found or format incorrect for {url}. Data: {extracted_data}")
             else:
                 logger.warning(f"Extraction failed or returned no data for {url}. Response: {response}")
    except Exception as e:
        logger.error(f"Error during Firecrawl extraction: {e}", exc_info=True)
    logger.info(f"Extracted info for {len(user_info_list)} URLs.")
    return user_info_list

def format_user_info_to_flattened_json(user_info_list: List[dict]) -> List[dict]:
    """Formats the extracted user info into a flattened list of dictionaries."""
    # (Implementation remains the same)
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
            else:
                logger.warning(f"Expected dict for interaction, got {type(interaction)} for URL {website_url}")
    logger.info(f"Formatted data into {len(flattened_data)} flattened records.")
    return flattened_data

def create_google_sheets_agent(composio_api_key: str, gemini_api_key: str) -> AgnoAgent:
    """Creates an Agno Agent configured for Google Sheets via Composio."""
    # (Implementation remains the same, relies on Agno/Composio)
    try:
        composio_toolset = ComposioToolSet(api_key=composio_api_key)
        google_sheets_tool = composio_toolset.get_tools(actions=[Action.GOOGLESHEETS_SHEET_FROM_JSON])[0]
        google_sheets_agent = AgnoAgent(
            model=AgnoGeminiChat(id="gemini-1.5-flash", api_key=gemini_api_key), # Updated model ID example
            tools=[google_sheets_tool], show_tool_calls=True,
            system_prompt="You are an expert at creating Google Sheets from JSON data.", markdown=True
        )
        logger.info("Created Google Sheets AgnoAgent.")
        return google_sheets_agent
    except Exception as e:
        logger.error(f"Failed to create Google Sheets AgnoAgent: {e}", exc_info=True)
        raise

def write_to_google_sheets(flattened_data: List[dict], composio_api_key: str, gemini_api_key: str) -> Optional[str]:
    """Writes data to Google Sheets using the Agno/Composio agent."""
    # (Implementation remains the same, relies on Agno/Composio)
    if not flattened_data: return None
    try:
        google_sheets_agent = create_google_sheets_agent(composio_api_key, gemini_api_key)
        message = (
            "Create a new Google Sheet with this data. Columns: Website URL, Username, Bio, Post Type, Timestamp, Upvotes, Links.\n\n"
            f"{json.dumps(flattened_data, indent=2)}"
        )
        logger.info("Attempting to write data to Google Sheets...")
        response = google_sheets_agent.run(message)
        if response and hasattr(response, 'content'):
             content = response.content
             if "https://docs.google.com/spreadsheets/d/" in content:
                 start_index = content.find("https://docs.google.com/spreadsheets/d/")
                 link_part = content[start_index:]
                 end_index = link_part.find(" ")
                 google_sheets_link = link_part if end_index == -1 else link_part[:end_index]
                 if google_sheets_link.startswith("https://docs.google.com/spreadsheets/d/"):
                     logger.info(f"Successfully wrote data to Google Sheet: {google_sheets_link}")
                     return google_sheets_link
                 else: logger.error(f"Extracted link seems invalid: {google_sheets_link}")
             else: logger.error(f"Google Sheet link not found in response: {content}")
        else: logger.error(f"Invalid response from Google Sheets agent: {response}")
    except Exception as e:
        logger.error(f"Error writing to Google Sheets: {e}", exc_info=True)
    return None

async def transform_query_async(user_query: str, gemini_api_key: str) -> str:
    """Transforms the user query into a concise company description using Gemini."""
    # (Implementation remains the same, uses direct Gemini call)
    logger.info("Transforming user query...")
    try:
        # Direct Gemini call (replace with ADK LLM client if available/preferred)
        import google.generativeai as genai
        genai.configure(api_key=gemini_api_key)
        model = genai.GenerativeModel("gemini-1.5-flash") # Use appropriate model

        prompt = f"""Extract the core business/product focus (3-4 words) from the query: "{user_query}"
Examples:
Input: "AI chatbots for e-commerce support" -> Output: "AI e-commerce chatbots"
Input: "voice cloning for audiobooks" -> Output: "voice cloning technology"
Input: "automated video editing software" -> Output: "AI video editing software"
Input: "ML for fraud detection" -> Output: "ML fraud detection"
Output:"""
        response = await model.generate_content_async(prompt)
        transformed_query = response.text.strip()
        logger.info(f"Transformed query: '{transformed_query}'")
        return transformed_query
    except Exception as e:
        logger.error(f"Error transforming query with LLM: {e}", exc_info=True)
        raise ValueError(f"Failed to transform query: {e}") from e

# --- ADK Tool Definition ---

@tool(description="Generate leads by searching Quora based on a user query, extracting info, and saving to a Google Sheet.")
async def generate_leads_tool(
    user_query: str,
    firecrawl_api_key: str,
    gemini_api_key: str,
    composio_api_key: str,
    num_links: int = 3
) -> Dict[str, Any]:
    """
    ADK Tool: Generate leads from Quora and save to Google Sheets.
    Requires Firecrawl, Gemini, and Composio API keys.
    """
    logger.info(f"Tool: Generating leads for query: {user_query}")
    try:
        # Validate inputs
        if not all([user_query, firecrawl_api_key, gemini_api_key, composio_api_key]):
            missing = [k for k, v in locals().items() if k.endswith('_api_key') and not v]
            raise ValueError(f"Missing required API keys: {', '.join(missing)}")

        # --- Workflow Steps (using helper functions) ---
        company_description = await transform_query_async(user_query, gemini_api_key)
        urls = search_for_urls(company_description, firecrawl_api_key, num_links)
        if not urls: return {"success": False, "error": "No relevant URLs found."}
        user_info_list = extract_user_info_from_urls(urls, firecrawl_api_key)
        if not user_info_list: return {"success": False, "error": "No user information extracted."}
        flattened_data = format_user_info_to_flattened_json(user_info_list)
        if not flattened_data: return {"success": False, "error": "No data available after formatting."}
        google_sheets_link = write_to_google_sheets(flattened_data, composio_api_key, gemini_api_key)
        # --- End Workflow Steps ---

        if google_sheets_link:
            logger.info("Tool: Lead generation process completed successfully.")
            return {
                "success": True,
                "message": "Lead generation complete.",
                "google_sheet_link": google_sheets_link,
                "leads_generated": len(flattened_data),
                "urls_processed": urls
            }
        else:
            logger.error("Tool: Failed to write data to Google Sheets.")
            return {"success": False, "error": "Failed to write data to Google Sheets."}

    except Exception as e:
        logger.error(f"Tool: Error generating leads: {e}", exc_info=True)
        return {"success": False, "error": f"Error generating leads: {str(e)}"}


# --- Instantiate the ADK Agent ---
agent = Agent(
    name="lead_generation_adk", # ADK specific name
    description="Generates leads by searching Quora, extracting user info via Firecrawl, and saving results to Google Sheets via Composio.",
    tools=[
        generate_leads_tool,
    ],
)

# Removed A2A server specific code and old class structure
