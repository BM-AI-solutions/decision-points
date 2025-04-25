# backend/agents/agent_web_search.py
import asyncio
import os
from typing import Dict, Any, Optional

import httpx
import logfire
from google.adk.runtime import InvocationContext, Event
from python_a2a import skill

from agents.base_agent import BaseSpecializedAgent
from app.config import settings

class WebSearchAgent(BaseSpecializedAgent):
    """
    An agent that performs web searches using the Brave Search API.
    Implements A2A protocol for agent communication.
    """

    def __init__(
        self,
        name: str = "web_search",
        description: str = "Performs web searches using the Brave Search API",
        model_name: Optional[str] = None,
        port: Optional[int] = None,
        **kwargs: Any,
    ):
        """
        Initialize the WebSearchAgent.

        Args:
            name: The name of the agent.
            description: The description of the agent.
            model_name: The name of the model to use. Defaults to settings.GEMINI_MODEL_NAME.
            port: The port to run the A2A server on. Defaults to settings.AGENT_WEB_SEARCH_URL port.
            **kwargs: Additional arguments for BaseSpecializedAgent.
        """
        # Extract port from URL if not provided
        if port is None and settings.AGENT_WEB_SEARCH_URL:
            try:
                port = int(settings.AGENT_WEB_SEARCH_URL.split(':')[-1])
            except (ValueError, IndexError):
                port = 8002  # Default port

        super().__init__(
            name=name,
            description=description,
            model_name=model_name,
            port=port,
            **kwargs
        )

        # Get API key from settings
        self.brave_api_key = settings.BRAVE_API_KEY
        if not self.brave_api_key:
            logfire.warning("BRAVE_API_KEY not configured in settings.")

        logfire.info(f"WebSearchAgent initialized with port: {self.port}")

    @skill(
        name="web_search",
        description="Perform a web search using the Brave Search API",
        tags=["search", "web"]
    )
    async def web_search(self, query: str) -> Dict[str, Any]:
        """
        Perform a web search using the Brave Search API.

        Args:
            query: The search query.

        Returns:
            A dictionary containing the search results or an error message.
        """
        if not query:
            logfire.warn("WebSearchAgent received empty query")
            return {"error": "No search query provided."}

        if not self.brave_api_key:
            logfire.error("BRAVE_API_KEY not configured in settings.")
            return {"error": "Brave API key not configured in settings."}

        headers = {
            'X-Subscription-Token': self.brave_api_key,
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
                with logfire.span('Calling Brave Search API', query=query) as span:
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
                return {"results": results_list}
            else:
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

    async def run_async(self, context: InvocationContext) -> Optional[Event]:
        """
        Executes the web search based on the query provided in the context.
        Maintained for backward compatibility with ADK.

        Args:
            context: The invocation context containing the input data.
                     Expected input: context.data['query'] (str)

        Returns:
            An Event containing the search results or an error message,
            or None if no query is provided.
        """
        # Extract query from context
        query = None
        if hasattr(context, 'data') and isinstance(context.data, dict):
            query = context.data.get("query")
        elif hasattr(context, 'input_event') and hasattr(context.input_event, 'data'):
            query = context.input_event.data.get("query")

        if not query:
            logfire.warn("WebSearchAgent received no query in context")
            return Event(data={"error": "No search query provided."})

        # Use the web_search skill
        result = await self.web_search(query)

        # Return as Event
        return Event(data=result)

# Example of how to run this agent as a standalone A2A server
if __name__ == "__main__":
    # Create the agent
    agent = WebSearchAgent()

    # Run the A2A server
    agent.run_server(host="0.0.0.0", port=agent.port or 8002)