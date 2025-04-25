# backend/agents/agent_web_search.py
# backend/agents/agent_web_search.py
import os
from typing import Dict, Any

import httpx
import logfire
from google.adk.agents import Agent  # Import the standard ADK Agent
from app.config import settings

# Define the tool logic as a standalone async function
async def web_search_tool(query: str) -> Dict[str, Any]:
    """
    Perform a web search using the Brave Search API.

    Args:
        query: The search query.

    Returns:
        A dictionary containing the search results or an error message.
    """
    if not query:
        logfire.warn("WebSearchAgent tool received empty query")
        return {"error": "No search query provided."}

    brave_api_key = settings.BRAVE_API_KEY
    if not brave_api_key:
        logfire.error("BRAVE_API_KEY not configured in settings.")
        return {"error": "Brave API key not configured in settings."}

    headers = {
        'X-Subscription-Token': brave_api_key,
        'Accept': 'application/json',
    }
    params = {
        'q': query,
        'count': 5,  # Number of results
        'text_decorations': True,
        'search_lang': 'en'
    }
    search_url = 'https://api.search.brave.com/res/v1/web/search'

    try:
        async with httpx.AsyncClient() as client:
            with logfire.span('Calling Brave Search API via ADK tool', query=query) as span:
                response = await client.get(search_url, params=params, headers=headers)
                response.raise_for_status()
                data = response.json()
                span.set_attribute('response_status', response.status_code)

        # Format results
        results_list = []
        web_results = data.get('web', {}).get('results', [])
        for item in web_results[:3]:  # Limit to top 3 results for brevity
            title = item.get('title', '')
            description = item.get('description', '')
            url = item.get('url', '')
            if title and description and url:
                results_list.append({
                    "title": title,
                    "summary": description,
                    "source": url
                })

        if results_list:
            logfire.info(f"Web search successful for query: '{query}'")
            return {"results": results_list}
        else:
            logfire.info(f"No web search results found for query: '{query}'")
            return {"message": f"No results found for query: '{query}'"}

    except httpx.HTTPStatusError as e:
        logfire.error(f"Brave API request failed: {e.response.status_code} - {e.response.text}", exc_info=True)
        return {"error": f"Brave API request failed: {e.response.status_code}"}
    except httpx.RequestError as e:
        logfire.error(f"Error connecting to Brave API: {e}", exc_info=True)
        return {"error": f"Could not connect to Brave API: {e}"}
    except Exception as e:
        logfire.error(f"An unexpected error occurred during web search: {e}", exc_info=True)
        return {"error": f"An unexpected error occurred: {e}"}


# Instantiate the ADK Agent
# This instance will be discovered by `adk web`
agent = Agent(
    name="web_search_adk", # Renamed slightly to avoid potential conflicts if old code is cached
    description="Performs web searches using the Brave Search API (ADK Version)",
    # instruction="Use the web_search_tool to find information online.", # Instruction is more relevant for LlmAgent
    tools=[web_search_tool], # Register the function as a tool
)

# No need for the __main__ block or run_server call for adk web discovery
