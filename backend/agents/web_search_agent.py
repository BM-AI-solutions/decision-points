# backend/agents/web_search_agent.py
import asyncio
import os
import argparse
from typing import Dict, Any, Optional

import httpx
import logfire
import uvicorn
from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel # For request body validation

from google.adk.agents import Agent
from google.adk.runtime import InvocationContext, Event

# # # from backend.app.config import settings # Import centralized settings (if needed directly)

# BRAVE_API_KEY is expected to be in environment variables

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
            return Event(data={"error": "No search query provided."})

        # Get API key from environment
        brave_api_key = os.environ.get('BRAVE_API_KEY')
        if not brave_api_key:
            logfire.error("BRAVE_API_KEY not configured in environment.")
            return Event(data={"error": "Brave API key not configured."})

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
                with logfire.span('Calling Brave Search API', query=query) as span:
                    response = await client.get(search_url, params=params, headers=headers)
                    response.raise_for_status()
                    data = response.json()
                    span.set_attribute('response_status', response.status_code)

            # Format results
            results_list = []
            web_results = data.get('web', {}).get('results', [])
            for item in web_results[:3]: # Limit to top 3 results
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
                logfire.info(f"No Brave search results found for query: '{query}'")
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

# --- FastAPI Server Setup ---

# Define request model for validation
class InvokeRequest(BaseModel):
    query: str

# Create FastAPI app
app = FastAPI(title="WebSearchAgent A2A Server")

# Instantiate the agent
web_search_agent_instance = WebSearchAgent()

@app.post("/invoke", response_model=Dict[str, Any])
async def invoke_agent(request: InvokeRequest = Body(...)):
    """
    A2A endpoint to invoke the WebSearchAgent.
    Expects a JSON body with a "query" field.
    """
    logfire.info(f"WebSearchAgent /invoke called with query: {request.query}")
    # Create a basic InvocationContext. Adjust agent_id if needed.
    context = InvocationContext(agent_id="web-search-agent", data={"query": request.query})

    try:
        result_event = await web_search_agent_instance.run_async(context)
        if result_event:
            logfire.info(f"WebSearchAgent returning result: {result_event.data}")
            return result_event.data # Return the data part of the event
        else:
            logfire.error("WebSearchAgent run_async returned None")
            raise HTTPException(status_code=500, detail="Agent execution failed to return an event.")
    except Exception as e:
        logfire.error(f"Error during agent invocation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

@app.get("/health")
async def health_check():
    return {"status": "ok"}

# --- Main execution block ---

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the WebSearchAgent A2A server.")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind the server to.")
    parser.add_argument("--port", type=int, default=8080, help="Port to run the server on.")
    args = parser.parse_args()

    print(f"Starting WebSearchAgent A2A server on {args.host}:{args.port}")
    # Configure logfire (optional, adjust as needed)
    # logfire.configure()

    uvicorn.run(app, host=args.host, port=args.port)