# backend/agents/web_search_agent.py
import asyncio
import os
from typing import Dict, Any, Optional

import httpx
import logfire
from google.adk.agents import Agent
from google.adk.runtime import InvocationContext, Event

# Load API key from environment variable - consider moving to a config manager
BRAVE_API_KEY = os.getenv("BRAVE_API_KEY")

class WebSearchAgent(Agent):
    """
    An agent that performs web searches using the Brave Search API.
    """

    async def run_async(self, context: InvocationContext) -> Optional[Event]:
        """
        Executes the web search based on the query provided in the context.

        Args:
            context: The invocation context containing the input data.
                     Expected input: context.data['query'] (str)

        Returns:
            An Event containing the search results or an error message,
            or None if no query is provided.
        """
        query = context.data.get("query")
        if not query:
            logfire.warn("WebSearchAgent received no query in context.data")
            # Optionally return an error event or None
            return Event(data={"error": "No search query provided."})

        if not BRAVE_API_KEY:
            logfire.error("BRAVE_API_KEY environment variable not set.")
            # Return a test result or an error event
            # return Event(data={"results": "This is a test web search result. BRAVE_API_KEY not configured."})
            return Event(data={"error": "Brave API key not configured."})

        headers = {
            'X-Subscription-Token': BRAVE_API_KEY,
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
                    response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
                    data = response.json()
                    span.set_attribute('response_status', response.status_code)
                    # span.set_attribute('response_data', data) # Be cautious logging full response data

            # Format results
            results_list = []
            web_results = data.get('web', {}).get('results', [])
            for item in web_results[:3]: # Limit to top 3 results for brevity
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
                return Event(data={"results": results_list})
            else:
                return Event(data={"message": f"No results found for query: '{query}'"})

        except httpx.HTTPStatusError as e:
            logfire.error(f"Brave API request failed: {e.response.status_code} - {e.response.text}", exc_info=True)
            return Event(data={"error": f"Brave API request failed: {e.response.status_code}"})
        except httpx.RequestError as e:
            logfire.error(f"Error connecting to Brave API: {e}", exc_info=True)
            return Event(data={"error": f"Could not connect to Brave API: {e}"})
        except Exception as e:
            logfire.error(f"An unexpected error occurred during web search: {e}", exc_info=True)
            return Event(data={"error": f"An unexpected error occurred: {e}"})

# Example of how this agent might be invoked (for testing purposes, not part of the agent file itself)
# async def main():
#     # This requires the ADK runtime environment setup
#     from google.adk.runtime import LocalAgentExecutor
#
#     agent = WebSearchAgent()
#     executor = LocalAgentExecutor()
#     context = InvocationContext(agent_id="web-search-agent", data={"query": "React 19 release date"})
#     result_event = await executor.run_agent(agent, context)
#
#     if result_event:
#         print("Search Results:")
#         print(result_event.data)
#     else:
#         print("Agent execution failed or returned no event.")
#
# if __name__ == "__main__":
#     # Note: Running this directly requires BRAVE_API_KEY to be set
#     # and assumes ADK environment setup for LocalAgentExecutor.
#     # This is primarily for illustrative purposes.
#     # asyncio.run(main())
#     pass