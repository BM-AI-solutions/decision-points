"""
Lead Generation Agent for Decision Points.

This agent generates leads by searching Quora, extracting user info, and saving it to a Google Sheet.
It implements the A2A protocol for agent communication.
"""

import json
import logging
import httpx
from typing import List, Dict, Any, Optional

# ADK Imports
from google.adk.runtime import InvocationContext
from google.adk.runtime.events import Event

# A2A Imports
from python_a2a import skill

from firecrawl import FirecrawlApp
from pydantic import BaseModel, Field
# Keep agno/composio for Sheets writing as per prototype logic transfer
from agno.agent import Agent as AgnoAgent
from agno.tools.firecrawl import FirecrawlTools # Might not be needed if using SDK directly
from agno.models.google import Gemini as AgnoGeminiChat
from composio_phidata import Action, ComposioToolSet

from agents.base_agent import BaseSpecializedAgent
from app.config import settings

# Configure logging
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

class LeadGenerationAgent(BaseSpecializedAgent):
    """
    Agent responsible for lead generation.
    Generates leads by searching Quora, extracting user info, and saving it to a Google Sheet.
    Implements A2A protocol for agent communication.
    """

    def __init__(
        self,
        name: str = "lead_generator",
        description: str = "Generates leads by searching Quora, extracting user info, and saving it to a Google Sheet",
        model_name: Optional[str] = None,
        port: Optional[int] = None,
        **kwargs: Any,
    ):
        """
        Initialize the LeadGenerationAgent.

        Args:
            name: The name of the agent.
            description: The description of the agent.
            model_name: The name of the model to use. Defaults to settings.GEMINI_MODEL_NAME.
            port: The port to run the A2A server on. Defaults to settings.LEAD_GENERATION_AGENT_URL port.
            **kwargs: Additional arguments for BaseSpecializedAgent.
        """
        # Extract port from URL if not provided
        if port is None and settings.LEAD_GENERATION_AGENT_URL:
            try:
                port = int(settings.LEAD_GENERATION_AGENT_URL.split(':')[-1])
            except (ValueError, IndexError):
                port = 8010  # Default port

        # Initialize BaseSpecializedAgent
        super().__init__(
            name=name,
            description=description,
            model_name=model_name,
            port=port,
            **kwargs
        )

        logger.info(f"LeadGenerationAgent initialized with port: {self.port}")

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


    # --- A2A Skills ---
    @skill(
        name="generate_leads",
        description="Generate leads by searching Quora, extracting user info, and saving it to a Google Sheet",
        tags=["leads", "quora"]
    )
    async def generate_leads_skill(self, user_query: str, firecrawl_api_key: str,
                                  gemini_api_key: str, composio_api_key: str,
                                  num_links: int = 3) -> Dict[str, Any]:
        """
        Generate leads by searching Quora, extracting user info, and saving it to a Google Sheet.

        Args:
            user_query: Description of leads to find.
            firecrawl_api_key: Firecrawl API key.
            gemini_api_key: Gemini API key.
            composio_api_key: Composio API key.
            num_links: Number of links to search. Defaults to 3.

        Returns:
            A dictionary containing the generated leads and Google Sheet link.
        """
        logger.info(f"Generating leads for query: {user_query}")

        try:
            # Validate inputs
            if not all([user_query, firecrawl_api_key, gemini_api_key, composio_api_key]):
                missing_keys = [k for k, v in {
                    "user_query": user_query,
                    "firecrawl_api_key": firecrawl_api_key,
                    "gemini_api_key": gemini_api_key,
                    "composio_api_key": composio_api_key
                }.items() if not v]
                error_msg = f"Missing required parameters: {', '.join(missing_keys)}"
                logger.error(error_msg)
                return {
                    "success": False,
                    "error": error_msg
                }

            # Transform user query
            company_description = await self.transform_query_async(user_query, gemini_api_key)
            logger.info(f"Transformed query to: {company_description}")

            # Search for URLs
            urls = search_for_urls(company_description, firecrawl_api_key, num_links)
            if not urls:
                logger.warning("No relevant URLs found.")
                return {
                    "success": False,
                    "error": "No relevant URLs found."
                }
            logger.info(f"Found {len(urls)} relevant URLs.")

            # Extract user info
            user_info_list = extract_user_info_from_urls(urls, firecrawl_api_key)
            if not user_info_list:
                logger.warning("No user information extracted from found URLs.")
                return {
                    "success": False,
                    "error": "No user information extracted from found URLs."
                }
            logger.info(f"Extracted information from {len(user_info_list)} URLs.")

            # Format data
            flattened_data = format_user_info_to_flattened_json(user_info_list)
            if not flattened_data:
                logger.warning("No data available after formatting.")
                return {
                    "success": False,
                    "error": "No data available after formatting."
                }
            logger.info(f"Formatted {len(flattened_data)} records.")

            # Write to Google Sheets
            google_sheets_link = write_to_google_sheets(flattened_data, composio_api_key, gemini_api_key)

            if google_sheets_link:
                logger.info("Lead generation process completed successfully.")
                return {
                    "success": True,
                    "message": "Lead generation process completed successfully.",
                    "google_sheet_link": google_sheets_link,
                    "leads_generated": len(flattened_data),
                    "urls": urls
                }
            else:
                logger.error("Failed to write data to Google Sheets.")
                return {
                    "success": False,
                    "error": "Failed to write data to Google Sheets."
                }

        except Exception as e:
            logger.error(f"Error generating leads: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"Error generating leads: {str(e)}"
            }

    async def run_async(self, context: InvocationContext) -> Event:
        """
        Executes the lead generation workflow asynchronously according to ADK spec.
        Maintained for backward compatibility with ADK.

        Args:
            context: The invocation context containing the input data.

        Returns:
            An Event containing the lead generation results or an error.
        """
        logger.info(f"Received invocation for LeadGenerationAgent (ID: {context.invocation_id})")

        try:
            # Extract input from context
            if not hasattr(context, 'data') or not context.data:
                logger.error("Input data is missing in the invocation context.")
                return Event(
                    type="lead_generation_failed",
                    data={"error": "Input data is missing."}
                )

            # Use the A2A skill
            result = await self.generate_leads_skill(
                user_query=context.data.get("user_query"),
                firecrawl_api_key=context.data.get("firecrawl_api_key"),
                gemini_api_key=context.data.get("gemini_api_key"),
                composio_api_key=context.data.get("composio_api_key"),
                num_links=context.data.get("num_links", 3)
            )

            # Create an event from the result
            if result.get("success", False):
                return Event(
                    type="lead_generation_complete",
                    data={k: v for k, v in result.items() if k != "success" and k != "message"}
                )
            else:
                return Event(
                    type="lead_generation_failed",
                    data={"error": result.get("error", "Lead generation failed.")}
                )

        except Exception as e:
            # Catch-all for unexpected errors
            logger.error(f"Unexpected error in LeadGenerationAgent: {e}", exc_info=True)
            return Event(
                type="lead_generation_failed",
                data={"error": f"An unexpected error occurred: {str(e)}"}
            )

# Example of how to run this agent as a standalone A2A server
if __name__ == "__main__":
    # Create the agent
    agent = LeadGenerationAgent()

    # Run the A2A server
    agent.run_server(host="0.0.0.0", port=agent.port or 8010)