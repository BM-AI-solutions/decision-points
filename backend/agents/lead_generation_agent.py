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
# Removed Agno/Composio imports

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
             if response and isinstance(response, dict) and response.get('data'): # Added isinstance check
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
Input: "find people interested in voice cloning technology for creating audiobooks and podcasts" -> Output: "voice cloning technology"
Input: "looking for users who need automated video editing software with AI capabilities" -> Output: "AI video editing software"
Input: "need to find businesses interested in implementing machine learning solutions for fraud detection" -> Output: "ML fraud detection"

Always focus on the core product/service and keep it concise but clear.

Transform this query: "{user_query}"
Output:"""
        response = await model.generate_content_async(prompt)
        transformed_query = response.text.strip()
        logger.info(f"Transformed query: '{transformed_query}'")
        return transformed_query
    except Exception as e:
        logger.error(f"Error transforming query with LLM: {e}", exc_info=True)
        raise ValueError(f"Failed to transform query: {e}") from e

# --- ADK Tool Definition ---

@tool(description="Generate leads by searching Quora based on a user query and extracting user info.")
async def generate_leads_tool(
    user_query: str,
    firecrawl_api_key: str,
    gemini_api_key: str, # Still needed for query transformation
    num_links: int = 3
) -> Dict[str, Any]:
    """
    ADK Tool: Generate leads from Quora.
    Requires Firecrawl and Gemini API keys.
    Returns extracted lead data.
    """
    logger.info(f"Tool: Generating leads for query: {user_query}")
    try:
        # Validate inputs
        if not all([user_query, firecrawl_api_key, gemini_api_key]):
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
        # Removed Google Sheets writing logic

        logger.info("Tool: Lead generation process completed successfully (without Sheets writing).")
        return {
            "success": True,
            "message": "Lead generation complete. Data extracted.",
            "leads_data": flattened_data, # Return the extracted data
            "urls_processed": urls
        }

    except Exception as e:
        logger.error(f"Tool: Error generating leads: {e}", exc_info=True)
        return {"success": False, "error": f"Error generating leads: {str(e)}"}


# --- Instantiate the ADK Agent ---
agent = Agent(
    name="lead_generation_adk", # ADK specific name
    description="Generates leads by searching Quora and extracting user info via Firecrawl.",
    tools=[
        generate_leads_tool,
    ],
)

# Removed A2A server specific code and old class structure
