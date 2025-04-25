import json
import httpx
import asyncio
import traceback
import logging
import os # Added for env vars
import argparse # Added for server args
from datetime import datetime
from typing import List, Optional, Dict, Any, Union

import uvicorn # Added for server
from fastapi import FastAPI, HTTPException, Body # Added for server
from pydantic import BaseModel, Field, HttpUrl, ValidationError

# ADK Imports
from google.adk.agents import Agent
from google.adk.runtime import InvocationContext
from google.adk.runtime.events import Event, EventSeverity # Corrected import

# Tooling Imports
from exa_py import Exa
from firecrawl import FirecrawlApp, AsyncFirecrawlApp # Keep both if needed
# Gemini for analysis (if ContentGenAgent isn't used or for fallback)
try:
    import google.generativeai as genai
    GEMINI_SDK_AVAILABLE = True
except ImportError:
    genai = None
    GEMINI_SDK_AVAILABLE = False

# Setup basic logging
# Use logfire if configured globally, otherwise standard logging
try:
    import logfire
    logger = logfire
except ImportError:
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO"), format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


# --- Pydantic Models ---

class MarketResearchInput(BaseModel):
    """Input for the Market Research Agent /invoke endpoint."""
    initial_topic: str = Field(description="A keyword, domain, or description defining the area of interest.")
    target_url: Optional[HttpUrl] = Field(None, description="Optional URL of the user's company for comparison.")
    num_competitors: int = Field(default=3, description="Number of competitors to find and analyze.")

class CompetitorInfo(BaseModel):
    """Structured information extracted for a single competitor."""
    competitor_url: HttpUrl
    company_name: Optional[str] = None
    pricing: Optional[str] = None
    key_features: List[str] = []
    tech_stack: List[str] = []
    marketing_focus: Optional[str] = None
    customer_feedback: Optional[str] = None

class MarketAnalysis(BaseModel):
    """Structured analysis of the market based on competitor data."""
    market_gaps: List[str] = Field(description="Identified gaps or unmet needs in the market.")
    opportunities: List[str] = Field(description="Potential opportunities based on competitor weaknesses or market trends.")
    competitor_weaknesses: List[str] = Field(description="Specific weaknesses observed in competitors.")
    pricing_strategies: List[str] = Field(description="Observations or suggestions regarding pricing.")
    positioning_strategies: List[str] = Field(description="Observations or suggestions regarding market positioning.")

class MarketOpportunityReport(BaseModel):
    """Output schema for the Market Research Agent /invoke endpoint on success."""
    competitors: List[CompetitorInfo] = Field(description="List of identified competitors and their extracted data.")
    analysis: MarketAnalysis = Field(description="Structured analysis of the market, competitors, and opportunities.")
    feature_recommendations: List[str] = Field(description="List of potential features to consider based on the analysis.")
    target_audience_suggestions: List[str] = Field(description="Suggestions for potential target demographics or niches.")
    # Optional field for web search summary if needed
    # web_search_summary: Optional[str] = None

class MarketResearchErrorOutput(BaseModel):
    """Output model for the /invoke endpoint on failure."""
    error: str
    details: Optional[Any] = None

class FirecrawlExtractSchema(BaseModel):
    """Schema specifically for Firecrawl extraction."""
    company_name: str = Field(description="Name of the company")
    pricing: str = Field(description="Pricing details, tiers, and plans")
    key_features: List[str] = Field(description="Main features and capabilities of the product/service")
    tech_stack: List[str] = Field(description="Technologies, frameworks, and tools used")
    marketing_focus: str = Field(description="Main marketing angles and target audience")
    customer_feedback: str = Field(description="Customer testimonials, reviews, and feedback")


# --- Agent Class ---

class MarketResearchAgent(Agent):
    """
    ADK Agent responsible for Stage 1: Market Research.
    Finds competitors, extracts data, performs web search, and generates a MarketOpportunityReport.
    Uses A2A server structure and environment variables for config.
    Requires: GOOGLE_API_KEY, FIRECRAWL_API_KEY, EXA_API_KEY (or PERPLEXITY_API_KEY),
              WEB_SEARCH_AGENT_URL, CONTENT_GENERATION_AGENT_URL, COMPETITOR_SEARCH_PROVIDER.
    """
    ENV_GOOGLE_API_KEY = "GOOGLE_API_KEY" # For Gemini analysis fallback/direct use
    ENV_FIRECRAL_API_KEY = "FIRECRAWL_API_KEY"
    ENV_EXA_API_KEY = "EXA_API_KEY"
    ENV_PERPLEXITY_API_KEY = "PERPLEXITY_API_KEY"
    ENV_SEARCH_PROVIDER = "COMPETITOR_SEARCH_PROVIDER"
    ENV_WEB_SEARCH_AGENT_URL = "WEB_SEARCH_AGENT_URL" # Changed from ID
    ENV_CONTENT_GENERATION_AGENT_URL = "CONTENT_GENERATION_AGENT_URL" # Changed from ID
    ENV_GEMINI_MODEL_NAME = "GEMINI_MODEL_NAME" # Optional, for analysis model

    DEFAULT_GEMINI_MODEL = "gemini-1.5-flash-latest"

    def __init__(self, agent_id: str = "market-research-agent"):
        """Initialize the agent and required clients."""
        super().__init__(agent_id=agent_id)
        logger.info(f"Initializing MarketResearchAgent ({self.agent_id})...")

        # Load configuration from environment variables
        self.google_api_key = os.environ.get(self.ENV_GOOGLE_API_KEY)
        self.firecrawl_api_key = os.environ.get(self.ENV_FIRECRAL_API_KEY)
        self.exa_api_key = os.environ.get(self.ENV_EXA_API_KEY)
        self.perplexity_api_key = os.environ.get(self.ENV_PERPLEXITY_API_KEY)
        self.search_provider = os.environ.get(self.ENV_SEARCH_PROVIDER, "exa").lower() # Default to exa
        self.web_search_agent_url = os.environ.get(self.ENV_WEB_SEARCH_AGENT_URL)
        self.content_generation_agent_url = os.environ.get(self.ENV_CONTENT_GENERATION_AGENT_URL)
        self.model_name = os.environ.get(self.ENV_GEMINI_MODEL_NAME, self.DEFAULT_GEMINI_MODEL)

        # Initialize shared httpx client
        self.http_client = httpx.AsyncClient(timeout=30.0)

        # --- Validation & Client Initialization ---
        if not self.firecrawl_api_key: raise ValueError(f"{self.ENV_FIRECRAL_API_KEY} not configured.")
        self.firecrawl_client = AsyncFirecrawlApp(api_key=self.firecrawl_api_key)

        self.exa_client = None
        if self.search_provider == "exa":
            if not self.exa_api_key: raise ValueError(f"{self.ENV_EXA_API_KEY} not configured for Exa search provider.")
            self.exa_client = Exa(api_key=self.exa_api_key)
            logger.info("Using Exa for competitor search.")
        elif self.search_provider == "perplexity":
            if not self.perplexity_api_key: raise ValueError(f"{self.ENV_PERPLEXITY_API_KEY} not configured for Perplexity search provider.")
            logger.info("Using Perplexity for competitor search.")
        else:
            raise ValueError(f"Unsupported {self.ENV_SEARCH_PROVIDER}: {self.search_provider}. Use 'exa' or 'perplexity'.")

        # --- Gemini Initialization (Optional - primarily uses ContentGenAgent now) ---
        self.gemini_model = None
        if not GEMINI_SDK_AVAILABLE: logger.warning("google-generativeai SDK not installed. Direct Gemini analysis disabled.")
        elif not self.google_api_key: logger.warning(f"{self.ENV_GOOGLE_API_KEY} not configured. Direct Gemini analysis disabled.")
        else:
            try:
                genai.configure(api_key=self.google_api_key)
                self.gemini_model = genai.GenerativeModel(self.model_name) # Config removed, handled by ContentGenAgent
                logger.info(f"Gemini client configured for potential direct use with model: {self.model_name}")
            except Exception as e: logger.error(f"Failed to initialize Gemini client: {e}", exc_info=True)

        # --- A2A Agent URL Validation ---
        if not self.web_search_agent_url: logger.warning(f"{self.ENV_WEB_SEARCH_AGENT_URL} not configured. Web search via A2A disabled.")
        else: logger.info(f"WebSearchAgent URL configured: {self.web_search_agent_url}")
        if not self.content_generation_agent_url: raise ValueError(f"{self.ENV_CONTENT_GENERATION_AGENT_URL} not configured. Cannot generate report.")
        else: logger.info(f"ContentGenerationAgent URL configured: {self.content_generation_agent_url}")

        logger.info(f"MarketResearchAgent ({self.agent_id}) initialized successfully.")


    # --- Helper Methods (Keep original logic, ensure async where needed) ---
    async def _find_competitor_urls_exa(self, topic: str, target_url: Optional[str], num_results: int) -> List[str]:
        """Finds competitor URLs using Exa asynchronously."""
        if not self.exa_client: raise RuntimeError("Exa client not initialized.")
        try:
            logger.info(f"Searching Exa for companies related to topic/URL: {topic or target_url}")
            loop = asyncio.get_running_loop()
            if target_url:
                result = await loop.run_in_executor(None, lambda: self.exa_client.find_similar(
                    url=target_url, num_results=num_results, exclude_source_domain=True, category="company"
                ))
            else:
                result = await loop.run_in_executor(None, lambda: self.exa_client.search(
                    topic, type="neural", category="company", use_autoprompt=True, num_results=num_results
                ))
            urls = [item.url for item in result.results if hasattr(item, 'url')]
            logger.info(f"Exa found URLs: {urls}")
            return urls
        except Exception as e:
            logger.error(f"Error fetching competitor URLs from Exa: {str(e)}", exc_info=True)
            return []

    async def _find_competitor_urls_perplexity(self, topic: str, target_url: Optional[str], num_results: int) -> List[str]:
        """Finds competitor URLs using Perplexity asynchronously."""
        if not self.perplexity_api_key: raise RuntimeError("Perplexity API key not configured.")
        perplexity_url = "https://api.perplexity.ai/chat/completions"
        content = f"Find me {num_results} competitor company URLs "
        if target_url and topic: content += f"similar to the company with URL '{target_url}' and description '{topic}'"
        elif target_url: content += f"similar to the company with URL: {target_url}"
        else: content += f"related to the topic: {topic}"
        content += ". ONLY RESPOND WITH THE URLS, each on a new line, NO OTHER TEXT."
        logger.info(f"Querying Perplexity API...")
        payload = {"model": "sonar-large-32k-online", "messages": [{"role": "system", "content": f"You are an assistant that finds competitor websites. Only return {num_results} company URLs, each on a new line."}, {"role": "user", "content": content}], "max_tokens": 1000, "temperature": 0.1}
        headers = {"Authorization": f"Bearer {self.perplexity_api_key}", "Content-Type": "application/json", "Accept": "application/json"}
        try:
            response = await self.http_client.post(perplexity_url, json=payload, headers=headers) # Use shared client
            response.raise_for_status()
            response_data = response.json()
            message_content = response_data.get('choices', [{}])[0].get('message', {}).get('content', '')
            urls = [url.strip() for url in message_content.strip().split('\n') if url.strip().startswith('http')]
            logger.info(f"Perplexity found URLs: {urls}")
            return urls[:num_results]
        except httpx.HTTPStatusError as e: logger.error(f"HTTP error fetching competitor URLs from Perplexity: {e.response.status_code} - {e.response.text}", exc_info=True); return []
        except httpx.RequestError as e: logger.error(f"Request error fetching competitor URLs from Perplexity: {str(e)}", exc_info=True); return []
        except Exception as e: logger.error(f"Unexpected error processing Perplexity response: {str(e)}", exc_info=True); return []

    async def _extract_competitor_info(self, competitor_url: str) -> Optional[CompetitorInfo]:
        """Extracts structured data from a competitor URL using AsyncFirecrawlApp."""
        logger.info(f"Extracting data from URL: {competitor_url} using AsyncFirecrawlApp")
        try:
            extraction_prompt = f"""Extract detailed information about the company's offerings from its website ({competitor_url}), focusing on: Company name, Pricing details, Key features (top 5-7), Technology stack (if mentioned), Marketing focus/target audience, Customer feedback/testimonials (summarize). Analyze the website content to provide comprehensive information for each field based *only* on the website's content. If information isn't found, indicate 'N/A' or omit the field."""
            response = await self.firecrawl_client.extract(
                url=competitor_url,
                params={'extractorOptions': {'mode': 'llm-extraction', 'extractionPrompt': extraction_prompt, 'extractionSchema': FirecrawlExtractSchema.model_json_schema()}, 'pageOptions': {'onlyMainContent': True}},
                timeout=60
            )
            if response and isinstance(response, dict) and response.get('data'):
                extracted_data = response['data']
                info = CompetitorInfo(
                    competitor_url=competitor_url, company_name=extracted_data.get('company_name'),
                    pricing=extracted_data.get('pricing'), key_features=extracted_data.get('key_features', []),
                    tech_stack=extracted_data.get('tech_stack', []), marketing_focus=extracted_data.get('marketing_focus'),
                    customer_feedback=extracted_data.get('customer_feedback')
                )
                logger.info(f"Successfully extracted data for {competitor_url}")
                return info
            else: logger.warning(f"Firecrawl extraction did not return valid data for {competitor_url}. Response: {response}"); return None
        except (ValidationError, TypeError) as e: logger.error(f"Pydantic validation error processing Firecrawl data for {competitor_url}: {e}", exc_info=True); return None
        except Exception as e: logger.error(f"Error extracting data from {competitor_url}: {str(e)}", exc_info=True); return None

    async def _call_web_search_agent(self, context: InvocationContext, query: str) -> Optional[Dict[str, Any]]:
        """Calls the WebSearchAgent via A2A HTTP call."""
        if not self.web_search_agent_url: logger.error("WebSearchAgent URL not configured."); return None
        invoke_url = f"{self.web_search_agent_url.rstrip('/')}/invoke" # Assuming /invoke endpoint
        logger.info(f"Calling WebSearchAgent A2A at {invoke_url} with query: '{query}'")
        payload = {"query": query} # Simple payload
        try:
            response = await self.http_client.post(invoke_url, json=payload)
            response.raise_for_status()
            data = response.json()
            logger.info(f"WebSearchAgent A2A call successful.")
            return data # Return the full response payload
        except httpx.RequestError as e: logger.error(f"A2A call to WebSearchAgent failed (Request Error): {e}", exc_info=True); return None
        except httpx.HTTPStatusError as e: logger.error(f"A2A call to WebSearchAgent failed (Status Code {e.response.status_code}): {e.response.text}", exc_info=True); return None
        except Exception as e: logger.error(f"Unexpected error during WebSearchAgent A2A call: {str(e)}", exc_info=True); return None

    async def _call_content_generation_agent(self, context: InvocationContext, competitors_data: List[CompetitorInfo], web_search_results: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Calls the ContentGenerationAgent via A2A HTTP call."""
        if not self.content_generation_agent_url: logger.error("ContentGenerationAgent URL not configured."); return None
        invoke_url = f"{self.content_generation_agent_url.rstrip('/')}/invoke" # Assuming /invoke endpoint
        logger.info(f"Calling ContentGenerationAgent A2A at {invoke_url}")
        try: competitors_json = json.dumps([c.model_dump(exclude_none=True) for c in competitors_data], indent=2)
        except TypeError as e: logger.error(f"Failed to serialize competitor data: {e}", exc_info=True); return None
        web_search_summary = "N/A"
        if web_search_results:
            try: web_search_summary = json.dumps(web_search_results, indent=2, default=str)[:1000] + "..."
            except Exception: web_search_summary = "Could not serialize web search results."
        prompt = f"""Analyze the following market research data (competitors, web search). Generate a structured JSON report with 'analysis' (market_gaps, opportunities, competitor_weaknesses, pricing_strategies, positioning_strategies - all lists of strings), 'feature_recommendations' (list of strings), and 'target_audience_suggestions' (list of strings). Focus on synthesizing insights into actionable recommendations. Competitor Data: ```json\n{competitors_json}\n``` Web Search Summary: ```text\n{web_search_summary}\n``` Output ONLY the valid JSON object adhering to the structure."""
        payload = {"action": "generate_structured_report", "prompt": prompt} # Assuming ContentGen takes an action and prompt
        try:
            response = await self.http_client.post(invoke_url, json=payload)
            response.raise_for_status()
            data = response.json()
            # Assuming the response payload *is* the generated report structure
            if isinstance(data, dict) and "analysis" in data: # Basic check
                logger.info(f"ContentGenerationAgent A2A call successful.")
                return data
            else:
                logger.error(f"ContentGenerationAgent returned unexpected payload format: {data}")
                return None
        except httpx.RequestError as e: logger.error(f"A2A call to ContentGenerationAgent failed (Request Error): {e}", exc_info=True); return None
        except httpx.HTTPStatusError as e: logger.error(f"A2A call to ContentGenerationAgent failed (Status Code {e.response.status_code}): {e.response.text}", exc_info=True); return None
        except Exception as e: logger.error(f"Unexpected error during ContentGenerationAgent A2A call: {str(e)}", exc_info=True); return None


    async def run_async(self, context: InvocationContext) -> Event:
        """Executes the market research workflow asynchronously."""
        logger.info(f"[{self.agent_id}] Invoked: {context.invocation_id}")
        web_search_results = None
        competitors_data: List[CompetitorInfo] = []
        extraction_errors = []

        try:
            # 1. Parse and Validate Input
            if not isinstance(context.data, dict): raise ValueError("Input data must be a dictionary.")
            inputs = MarketResearchInput(**context.data)
            logger.info(f"Parsed input: Topic='{inputs.initial_topic}', Target URL='{inputs.target_url}', Num Competitors={inputs.num_competitors}")

            # 2. Find Competitor URLs
            logger.info(f"Finding competitors using {self.search_provider}...")
            target_url_str = str(inputs.target_url) if inputs.target_url else None
            if self.search_provider == "exa":
                competitor_urls = await self._find_competitor_urls_exa(inputs.initial_topic, target_url_str, inputs.num_competitors)
            elif self.search_provider == "perplexity":
                 competitor_urls = await self._find_competitor_urls_perplexity(inputs.initial_topic, target_url_str, inputs.num_competitors)
            else: raise ValueError(f"Internal config error: Invalid search provider '{self.search_provider}'") # Should be caught in init

            # 3. Perform General Web Search via A2A
            logger.info(f"Performing general web search for topic: '{inputs.initial_topic}' via A2A...")
            web_search_results = await self._call_web_search_agent(context, inputs.initial_topic) # Pass context
            if web_search_results: logger.info("Successfully received web search results via A2A.")
            else: logger.warning("Web search via A2A failed or returned no results.")

            # 4. Extract Data for Competitors (if any found)
            if not competitor_urls:
                logger.warning("No competitor URLs found.")
                # Construct an empty/minimal report if desired, or raise specific error
            else:
                logger.info(f"Attempting to extract data for {len(competitor_urls)} competitors: {competitor_urls}")
                extraction_tasks = [self._extract_competitor_info(url) for url in competitor_urls]
                results = await asyncio.gather(*extraction_tasks, return_exceptions=True)
                for i, res in enumerate(results):
                    if isinstance(res, CompetitorInfo): competitors_data.append(res)
                    else: extraction_errors.append(f"URL: {competitor_urls[i]}, Error: {str(res)}")
                if not competitors_data: raise RuntimeError("Could not extract data from any competitor URLs.", {"extraction_errors": extraction_errors})
                if extraction_errors: logger.warning(f"Proceeding with data from {len(competitors_data)} competitors. Errors: {extraction_errors}")

            # 5. Generate Final Analysis Report via ContentGenerationAgent A2A
            logger.info(f"Calling ContentGenerationAgent A2A to generate report...")
            analysis_payload = await self._call_content_generation_agent(context, competitors_data, web_search_results) # Pass context
            if not analysis_payload or not isinstance(analysis_payload, dict):
                raise RuntimeError("Failed to generate analysis report via ContentGenerationAgent A2A.", {"a2a_payload_received": analysis_payload})

            # 6. Construct Final Report
            final_report = MarketOpportunityReport(
                competitors=competitors_data,
                analysis=MarketAnalysis(**analysis_payload.get("analysis", {})),
                feature_recommendations=analysis_payload.get("feature_recommendations", []),
                target_audience_suggestions=analysis_payload.get("target_audience_suggestions", [])
            )
            success_message = f"Market research completed. Analyzed {len(competitors_data)} competitors."
            if extraction_errors: success_message += f" ({len(extraction_errors)} extraction errors)"
            logger.info(success_message)

            # 7. Return Success Event
            return context.create_event(
                event_type="market.research.completed", data=final_report.model_dump(), metadata={"status": "success"}
            )

        except Exception as e:
            error_msg = f"Unexpected error in MarketResearchAgent: {str(e)}"
            logger.critical(error_msg, exc_info=True)
            return context.create_event(
                event_type="market.research.failed",
                data={"error": error_msg, "details": traceback.format_exc()},
                metadata={"status": "error"}
            )

    async def close_clients(self):
        """Close any open HTTP clients."""
        if self.http_client and not self.http_client.is_closed:
            await self.http_client.aclose()
            logger.info("Closed shared httpx client.")


# --- FastAPI Server Setup ---

app = FastAPI(title="MarketResearchAgent A2A Server")

# Instantiate the agent
try:
    market_research_agent_instance = MarketResearchAgent()
except ValueError as e:
    logger.critical(f"Failed to initialize MarketResearchAgent: {e}. Server cannot start.", exc_info=True)
    import sys
    sys.exit(f"Agent Initialization Error: {e}")


@app.post("/invoke", response_model=MarketOpportunityReport, responses={500: {"model": MarketResearchErrorOutput}})
async def invoke_agent(request: MarketResearchInput = Body(...)):
    """
    A2A endpoint to invoke the MarketResearchAgent.
    Expects JSON body matching MarketResearchInput.
    Returns MarketOpportunityReport on success, or raises HTTPException on error.
    """
    logger.info(f"MarketResearchAgent /invoke called for topic: {request.initial_topic}")
    invocation_id = f"research-{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(1000,9999)}"
    context = InvocationContext(agent_id="market-research-agent", invocation_id=invocation_id, data=request.model_dump())

    try:
        result_event = await market_research_agent_instance.run_async(context)

        if result_event and isinstance(result_event.data, dict):
            if result_event.metadata.get("status") == "error":
                 error_msg = result_event.data.get("error", "Unknown agent error")
                 logger.error(f"MarketResearchAgent run_async returned error event: {error_msg}")
                 raise HTTPException(status_code=500, detail=MarketResearchErrorOutput(error=error_msg, details=result_event.data.get("details")).model_dump())
            else:
                 # Validate success payload against MarketOpportunityReport
                 try:
                     output_payload = MarketOpportunityReport(**result_event.data)
                     logger.info(f"MarketResearchAgent returning success result.")
                     return output_payload
                 except ValidationError as val_err:
                     logger.error(f"Success event payload validation failed: {val_err}. Payload: {result_event.data}")
                     raise HTTPException(status_code=500, detail=MarketResearchErrorOutput(error="Internal validation error on success payload.", details=val_err.errors()).model_dump())
        else:
            logger.error(f"MarketResearchAgent run_async returned None or invalid event data: {result_event}")
            raise HTTPException(status_code=500, detail=MarketResearchErrorOutput(error="Agent execution failed to return a valid event.").model_dump())

    except HTTPException as http_exc:
        raise http_exc # Re-raise FastAPI exceptions
    except Exception as e:
        logger.error(f"Error during agent invocation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=MarketResearchErrorOutput(error=f"Internal server error: {e}").model_dump())

@app.get("/health")
async def health_check():
    # Add checks for API key presence and client initialization
    return {"status": "ok"}

# --- Server Shutdown Hook ---
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down MarketResearchAgent server...")
    await market_research_agent_instance.close_clients() # Close httpx client

# --- Main execution block ---

if __name__ == "__main__":
    # Load .env for local development if needed
    try:
        from dotenv import load_dotenv
        if load_dotenv(): logger.info("Loaded .env file for local run.")
        else: logger.info("No .env file found or it was empty.")
    except ImportError: logger.info("dotenv library not found, skipping .env load.")

    parser = argparse.ArgumentParser(description="Run the MarketResearchAgent A2A server.")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind the server to.")
    parser.add_argument("--port", type=int, default=8089, help="Port to run the server on.") # Default matches compose
    args = parser.parse_args()

    # Optional: Add checks here for required env vars before starting server

    print(f"Starting MarketResearchAgent A2A server on {args.host}:{args.port}")

    uvicorn.run(app, host=args.host, port=args.port)