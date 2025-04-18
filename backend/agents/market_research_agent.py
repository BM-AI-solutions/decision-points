import os
import json
import httpx
import asyncio
import traceback
import logging
from typing import List, Optional, Dict, Any, Union
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, HttpUrl, ValidationError

# ADK Imports
from google.adk.agents import Agent
from google.adk.runtime import InvocationContext
from google.adk.runtime.event import Event, EventSeverity

# Tooling Imports
from exa_py import Exa
from firecrawl import FirecrawlApp, AsyncFirecrawlApp
# import openai # Removed OpenAI import
import google.generativeai as genai # Added Gemini import
from google.api_core import exceptions as google_exceptions # Added Google API exceptions

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

logger.info("Attempting to load API keys from environment variables...")

# --- Configuration ---
# Load API keys from environment variables
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") # Removed OpenAI Key
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") # Added Google API Key
FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")
EXA_API_KEY = os.getenv("EXA_API_KEY")
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
SEARCH_PROVIDER = os.getenv("COMPETITOR_SEARCH_PROVIDER", "exa").lower()
WEB_SEARCH_AGENT_URL = os.getenv("WEB_SEARCH_AGENT_URL")
BRAVE_API_KEY = os.getenv("BRAVE_API_KEY")
GEMINI_MODEL_NAME = os.getenv("GEMINI_MODEL_NAME", "gemini-1.5-flash-latest") # Configurable Gemini model
CONTENT_GENERATION_AGENT_URL = os.getenv("CONTENT_GENERATION_AGENT_URL")

# --- Pydantic Models ---
# ... (Models remain the same) ...
class MarketResearchInput(BaseModel):
    """Input for the Market Research Agent."""
    initial_topic: str = Field(description="A keyword, domain, or description defining the area of interest.")
    target_url: Optional[HttpUrl] = Field(None, description="Optional URL of the user's company for comparison.")
    num_competitors: int = Field(3, description="Number of competitors to find and analyze.")

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
    """Output schema for the Market Research Agent, aligning with the architecture plan."""
    competitors: List[CompetitorInfo] = Field(description="List of identified competitors and their extracted data.")
    analysis: MarketAnalysis = Field(description="Structured analysis of the market, competitors, and opportunities.")
    feature_recommendations: List[str] = Field(description="List of potential features to consider based on the analysis.")
    target_audience_suggestions: List[str] = Field(description="Suggestions for potential target demographics or niches.")
    # Optional: Add fields here if web search provides distinct, structured insights consistently
    # web_search_summary: Optional[str] = Field(None, description="Summary of relevant findings from general web search.")

class FirecrawlExtractSchema(BaseModel):
    """Schema specifically for Firecrawl extraction, based on prototype."""
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
    Finds competitors, extracts data, performs web search, and generates a MarketOpportunityReport using Gemini.
    Inherits from google.adk.agents.Agent.
    """
    def __init__(self, model_name: Optional[str] = None):
        """
        Initialize the agent and required clients.

        Args:
            model_name: The name of the Gemini model to use for analysis (e.g., 'gemini-1.5-flash-latest').
                        Defaults to a suitable model if None.
        """
        # Load API Keys (excluding Gemini model name)
        # self.openai_api_key = os.getenv("OPENAI_API_KEY") # Removed
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        self.firecrawl_api_key = os.getenv("FIRECRAWL_API_KEY")
        self.exa_api_key = os.getenv("EXA_API_KEY")
        self.perplexity_api_key = os.getenv("PERPLEXITY_API_KEY")
        self.search_provider = os.getenv("COMPETITOR_SEARCH_PROVIDER", "exa").lower()
        self.web_search_agent_url = os.getenv("WEB_SEARCH_AGENT_URL")
        self.brave_api_key = os.getenv("BRAVE_API_KEY")
        # self.gemini_model_name = os.getenv("GEMINI_MODEL_NAME", "gemini-1.5-flash-latest") # Removed direct env var read
        self.content_generation_agent_url = os.getenv("CONTENT_GENERATION_AGENT_URL")

        # Determine the model name to use
        effective_model_name = model_name if model_name else 'gemini-1.5-flash-latest' # Default for specialized agent
        self.model_name = effective_model_name # Store the actual model name used

        # Initialize shared httpx client
        self.http_client = httpx.AsyncClient(timeout=30.0)

        # --- Validation & Client Initialization ---
        if not self.firecrawl_api_key:
            raise ValueError("FIRECRAWL_API_KEY environment variable not set.")
        self.firecrawl_client = AsyncFirecrawlApp(api_key=self.firecrawl_api_key)

        if self.search_provider == "exa":
            if not self.exa_api_key:
                raise ValueError("EXA_API_KEY environment variable not set for Exa search provider.")
            self.exa_client = Exa(api_key=self.exa_api_key)
            logger.info("Using Exa for competitor search.")
        elif self.search_provider == "perplexity":
            if not self.perplexity_api_key:
                raise ValueError("PERPLEXITY_API_KEY environment variable not set for Perplexity search provider.")
            logger.info("Using Perplexity for competitor search.")
        else:
            raise ValueError(f"Unsupported SEARCH_PROVIDER: {self.search_provider}. Use 'exa' or 'perplexity'.")

        # --- Gemini Initialization ---
        if not self.google_api_key:
            # Log warning, analysis step will fail if key is missing
            logger.warning("GOOGLE_API_KEY not set. Gemini model initialization skipped.")
            self.gemini_model = None # Explicitly set to None
        else:
            try:
                genai.configure(api_key=self.google_api_key)
                # Initialize the Gemini model using the determined model name
                self.gemini_model = genai.GenerativeModel(
                    self.model_name, # Use the stored model name
                    # Define generation config for JSON output
                    generation_config=genai.types.GenerationConfig(
                        # candidate_count=1, # Default is 1
                        # stop_sequences=['...'], # Optional stop sequences
                        # max_output_tokens=2048, # Optional max tokens
                        temperature=0.5, # Adjust temperature
                        response_mime_type="application/json", # Request JSON output
                    ),
                    # safety_settings=... # Optional safety settings
                )
                logger.info(f"Gemini client configured successfully using model: {self.model_name}")
            except Exception as e:
                logger.error(f"Failed to configure or initialize Gemini client with model {self.model_name}: {e}", exc_info=True)
                self.gemini_model = None # Ensure model is None on error
        # --- End Gemini Initialization ---

        # --- WebSearchAgent A2A Validation ---
        if not self.web_search_agent_url:
            raise ValueError("WEB_SEARCH_AGENT_URL environment variable not set. Cannot call WebSearchAgent.")
        if not self.brave_api_key:
            logger.warning("BRAVE_API_KEY environment variable not set. WebSearchAgent might require it.")
        logger.info(f"WebSearchAgent A2A endpoint configured: {self.web_search_agent_url}")
        # --- End Additions ---
        # --- ContentGenerationAgent A2A Validation ---
        if not self.content_generation_agent_url:
            raise ValueError("CONTENT_GENERATION_AGENT_URL environment variable not set. Cannot call ContentGenerationAgent.")
        logger.info(f"ContentGenerationAgent A2A endpoint configured: {self.content_generation_agent_url}")


    # ... (_find_competitor_urls_exa, _find_competitor_urls_perplexity, _extract_competitor_info, _call_web_search_agent remain the same) ...
    async def _find_competitor_urls_exa(self, topic: str, target_url: Optional[str], num_results: int) -> List[str]:
        """Finds competitor URLs using Exa asynchronously."""
        try:
            logger.info(f"Searching Exa for companies related to topic/URL: {topic or target_url}")
            # Wrap synchronous Exa calls in run_in_executor
            loop = asyncio.get_running_loop()
            if target_url:
                result = await loop.run_in_executor(
                    None, # Use default executor
                    lambda: self.exa_client.find_similar(
                        url=target_url,
                        num_results=num_results,
                        exclude_source_domain=True, # Exclude the target itself
                        category="company"
                    )
                )
            else:
                result = await loop.run_in_executor(
                    None,
                    lambda: self.exa_client.search(
                        topic,
                        type="neural",
                        category="company",
                        use_autoprompt=True, # Let Exa optimize the query
                        num_results=num_results
                    )
                )
            urls = [item.url for item in result.results]
            logger.info(f"Exa found URLs: {urls}")
            return urls
        except Exception as e:
            logger.error(f"Error fetching competitor URLs from Exa: {str(e)}", exc_info=True)
            return [] # Return empty list on error, handled in run_async

    async def _find_competitor_urls_perplexity(self, topic: str, target_url: Optional[str], num_results: int) -> List[str]:
        """Finds competitor URLs using Perplexity asynchronously."""
        perplexity_url = "https://api.perplexity.ai/chat/completions"
        content = f"Find me {num_results} competitor company URLs "
        if target_url and topic:
             content += f"similar to the company with URL '{target_url}' and description '{topic}'"
        elif target_url:
            content += f"similar to the company with URL: {target_url}"
        else:
            content += f"related to the topic: {topic}"
        content += ". ONLY RESPOND WITH THE URLS, each on a new line, NO OTHER TEXT."

        logger.info(f"Querying Perplexity API...") # Don't log the full content potentially containing sensitive info

        payload = {
            "model": "sonar-large-32k-online", # Use online model for web search
            "messages": [
                {"role": "system", "content": f"You are an assistant that finds competitor websites. Only return {num_results} company URLs, each on a new line."},
                {"role": "user", "content": content}
            ],
            "max_tokens": 1000, # Adjust as needed
            "temperature": 0.1, # Low temperature for factual retrieval
        }
        headers = {
            "Authorization": f"Bearer {self.perplexity_api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        try:
            # Use native async httpx client
            async with self.http_client as client: # Use the initialized client
                 response = await client.post(perplexity_url, json=payload, headers=headers) # Removed timeout here, set on client init

            response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
            response_data = response.json()
            message_content = response_data.get('choices', [{}])[0].get('message', {}).get('content', '')
            # Robust URL parsing: handle potential extra text or formatting issues
            urls = [
                url.strip() for url in message_content.strip().split('\n')
                if url.strip().startswith('http')
            ]
            logger.info(f"Perplexity found URLs: {urls}")
            return urls[:num_results] # Ensure we only return the requested number
        except httpx.HTTPStatusError as e: # Catch httpx specific error
            logger.error(f"HTTP error fetching competitor URLs from Perplexity: {e.response.status_code} - {e.response.text}", exc_info=True)
            return [] # Return empty list on error
        except httpx.RequestError as e: # Catch other httpx request errors
            logger.error(f"Request error fetching competitor URLs from Perplexity: {str(e)}", exc_info=True)
            return [] # Return empty list on error
        except Exception as e:
            logger.error(f"Unexpected error processing Perplexity response: {str(e)}", exc_info=True)
            return [] # Return empty list on error


    async def _extract_competitor_info(self, competitor_url: str) -> Optional[CompetitorInfo]:
        """Extracts structured data from a competitor URL using AsyncFirecrawlApp."""
        logger.info(f"Extracting data from URL: {competitor_url} using AsyncFirecrawlApp")
        try:
            # Use AsyncFirecrawlApp directly
            extraction_prompt = """
            Extract detailed information about the company's offerings from its website ({competitor_url}), focusing on:
            - Company name and basic information
            - Pricing details, plans, and tiers (summarize if complex)
            - Key features and main capabilities (list top 5-7)
            - Technology stack and technical details (if mentioned, list key ones)
            - Marketing focus and target audience (who are they selling to?)
            - Customer feedback and testimonials (summarize key themes or quotes)

            Analyze the website content to provide comprehensive information for each field based *only* on the website's content. If information isn't found, indicate 'N/A' or omit the field.
            """
            # Call async extract method
            response = await self.firecrawl_client.extract(
                url=competitor_url,
                params={
                    'extractorOptions': {
                        'mode': 'llm-extraction',
                        'extractionPrompt': extraction_prompt.format(competitor_url=competitor_url),
                        'extractionSchema': FirecrawlExtractSchema.model_json_schema(),
                    },
                    'pageOptions': {
                        'onlyMainContent': True # Focus extraction
                    }
                },
                timeout=60 # Keep timeout for extraction
            )

            if response and isinstance(response, dict) and response.get('data'):
                extracted_data = response['data']
                # Use Pydantic validation during creation
                info = CompetitorInfo(
                    competitor_url=competitor_url, # Ensure URL is valid HttpUrl
                    company_name=extracted_data.get('company_name'),
                    pricing=extracted_data.get('pricing'),
                    key_features=extracted_data.get('key_features', []),
                    tech_stack=extracted_data.get('tech_stack', []),
                    marketing_focus=extracted_data.get('marketing_focus'),
                    customer_feedback=extracted_data.get('customer_feedback')
                )
                logger.info(f"Successfully extracted data for {competitor_url}")
                return info
            else:
                 logger.warning(f"Firecrawl extraction did not return valid data for {competitor_url}. Response: {response}")
                 return None

        except (ValidationError, TypeError) as e:
             logger.error(f"Pydantic validation error processing Firecrawl data for {competitor_url}: {e}", exc_info=True)
             return None
        except Exception as e:
            logger.error(f"Error extracting data from {competitor_url}: {str(e)}", exc_info=True)
            return None # Return None on error, handled in run_async

    # --- New Method for WebSearchAgent A2A Call ---
    async def _call_web_search_agent(self, query: str, parent_context: InvocationContext) -> Optional[Dict[str, Any]]:
        """Calls the WebSearchAgent via A2A to perform a general web search."""
        if not self.web_search_agent_url or not self.brave_api_key:
            logger.error("WebSearchAgent URL or Brave API Key not configured for A2A call.")
            return None

        a2a_endpoint = f"{self.web_search_agent_url.rstrip('/')}/a2a/web_search/invoke"
        logger.info(f"Calling WebSearchAgent A2A endpoint: {a2a_endpoint} with query: '{query}'")

        # Prepare the InvocationContext payload for the WebSearchAgent
        web_search_input = {
            "query": query,
            "config": { # Pass necessary config within the input payload
                "brave_api_key": self.brave_api_key
            }
        }

        # Construct a minimal InvocationContext data structure for the request body
        a2a_payload = {
            "agent_id": "web_search_agent", # Target agent ID
            "invocation_id": f"a2a-{parent_context.invocation_id}-{os.urandom(4).hex()}", # Generate unique ID for this call
            "parent_invocation_id": parent_context.invocation_id, # Link back
            "input": web_search_input,
            "credentials": {},
            "state": {}
        }

        try:
            async with self.http_client as client: # Reuse the client
                 response = await client.post(
                     a2a_endpoint,
                     json=a2a_payload,
                     headers={"Content-Type": "application/json", "Accept": "application/json"}
                 )
            response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)

            # Parse the Event response from WebSearchAgent
            event_data = response.json()
            event = Event(**event_data) # Validate response against Event model

            if event.severity >= EventSeverity.ERROR:
                 logger.error(f"WebSearchAgent A2A call failed. Severity: {event.severity}. Message: {event.message}. Payload: {event.payload}")
                 return None

            logger.info(f"WebSearchAgent A2A call successful. Message: {event.message}")
            return event.payload if event.payload else {} # Return payload or empty dict

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error calling WebSearchAgent A2A: {e.response.status_code} - {e.response.text}", exc_info=True)
            return None
        except httpx.RequestError as e:
            logger.error(f"Request error calling WebSearchAgent A2A: {str(e)}", exc_info=True)
            return None
        except (ValidationError, json.JSONDecodeError, TypeError) as e:
             logger.error(f"Error parsing/validating WebSearchAgent A2A response: {e}", exc_info=True)
             return None
        except Exception as e:
            logger.error(f"Unexpected error during WebSearchAgent A2A call: {str(e)}", exc_info=True)
            return None
    # --- End New Method ---

    async def _call_content_generation_agent(self, competitors_data: List[CompetitorInfo], web_search_results: Optional[Dict[str, Any]], parent_context: InvocationContext) -> Optional[Dict[str, Any]]:
        """Calls the ContentGenerationAgent via A2A to summarize and structure the research findings."""
        if not self.content_generation_agent_url:
            logger.error("ContentGenerationAgent URL not configured for A2A call.")
            return None

        a2a_endpoint = f"{self.content_generation_agent_url.rstrip('/')}/a2a/content_generation/invoke"
        logger.info(f"Calling ContentGenerationAgent A2A endpoint: {a2a_endpoint}")

        # Prepare data for the prompt
        try:
            competitors_json = json.dumps([c.model_dump(exclude_none=True) for c in competitors_data], indent=2)
        except TypeError as e:
            logger.error(f"Failed to serialize competitor data for A2A call: {e}", exc_info=True)
            return None # Cannot proceed without competitor data

        web_search_summary = "N/A"
        if web_search_results:
            # Simple summary for the prompt
            if isinstance(web_search_results, dict) and 'summary' in web_search_results:
                 web_search_summary = web_search_results['summary']
            elif isinstance(web_search_results, dict) and 'results' in web_search_results and isinstance(web_search_results['results'], list):
                 web_search_summary = "\n".join([f"- {item.get('title', 'N/A')}: {item.get('snippet', 'N/A')}" for item in web_search_results['results'][:5]])
            else:
                 try:
                     web_search_summary = json.dumps(web_search_results, indent=2, default=str)[:1000] + "..."
                 except Exception:
                     web_search_summary = "Could not serialize web search results."

        # Construct the prompt for ContentGenerationAgent
        prompt = f"""
        Analyze the following market research data, consisting of competitor information and general web search results.
        Generate a structured report summarizing the findings and providing actionable insights.

        Competitor Data:
        ```json
        {competitors_json}
        ```

        General Web Search Results (Summarized):
        ```text
        {web_search_summary}
        ```

        Based on ALL the provided data, generate a JSON object containing:
        1.  'analysis': An object with fields 'market_gaps', 'opportunities', 'competitor_weaknesses', 'pricing_strategies', 'positioning_strategies' (each a list of strings).
        2.  'feature_recommendations': A list of strings suggesting potential features.
        3.  'target_audience_suggestions': A list of strings suggesting target audiences.

        Structure the output EXACTLY like this example (ensure valid JSON):
        ```json
        {{
          "analysis": {{
            "market_gaps": ["Identified gap 1...", "Gap 2..."],
            "opportunities": ["Opportunity 1...", "Opportunity 2..."],
            "competitor_weaknesses": ["Weakness 1..."],
            "pricing_strategies": ["Strategy suggestion 1..."],
            "positioning_strategies": ["Positioning idea 1..."]
          }},
          "feature_recommendations": ["Recommended feature 1...", "Feature 2..."],
          "target_audience_suggestions": ["Target audience 1...", "Audience 2..."]
        }}
        ```
        Focus on synthesizing insights from *both* competitor data and web search results into actionable recommendations within the specified JSON structure.
        """

        # Prepare the InvocationContext payload for the ContentGenerationAgent
        content_gen_input = {
            "prompt": prompt,
            "output_format": "json" # Assuming ContentGenAgent supports this
            # Add any other necessary config/parameters for ContentGenerationAgent here
        }

        a2a_payload = {
            "agent_id": "content_generation_agent", # Target agent ID
            "invocation_id": f"a2a-{parent_context.invocation_id}-{os.urandom(4).hex()}",
            "parent_invocation_id": parent_context.invocation_id,
            "input": content_gen_input,
            "credentials": {},
            "state": {}
        }

        try:
            async with self.http_client as client:
                 response = await client.post(
                     a2a_endpoint,
                     json=a2a_payload,
                     headers={"Content-Type": "application/json", "Accept": "application/json"}
                 )
            response.raise_for_status()

            event_data = response.json()
            event = Event(**event_data)

            if event.severity >= EventSeverity.ERROR:
                 logger.error(f"ContentGenerationAgent A2A call failed. Severity: {event.severity}. Message: {event.message}. Payload: {event.payload}")
                 return None

            logger.info(f"ContentGenerationAgent A2A call successful. Message: {event.message}")
            # Assuming the structured JSON is in the payload under a key like 'generated_content' or directly as the payload
            # Adjust this based on ContentGenerationAgent's actual response structure
            if isinstance(event.payload, dict) and 'generated_content' in event.payload:
                # Attempt to parse if it's a string containing JSON
                if isinstance(event.payload['generated_content'], str):
                    try:
                        return json.loads(event.payload['generated_content'])
                    except json.JSONDecodeError as json_err:
                        logger.error(f"Failed to parse JSON from ContentGenerationAgent payload: {json_err}. Content: {event.payload['generated_content']}")
                        return None
                elif isinstance(event.payload['generated_content'], dict):
                     return event.payload['generated_content'] # Already a dict
                else:
                    logger.error(f"Unexpected type for 'generated_content' in ContentGenerationAgent payload: {type(event.payload['generated_content'])}")
                    return None
            elif isinstance(event.payload, dict):
                 # Maybe the payload *is* the structured content
                 logger.warning("ContentGenerationAgent payload does not have 'generated_content' key, assuming payload is the content.")
                 return event.payload
            else:
                logger.error(f"Unexpected payload structure from ContentGenerationAgent: {event.payload}")
                return None

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error calling ContentGenerationAgent A2A: {e.response.status_code} - {e.response.text}", exc_info=True)
            return None
        except httpx.RequestError as e:
            logger.error(f"Request error calling ContentGenerationAgent A2A: {str(e)}", exc_info=True)
            return None
        except (ValidationError, json.JSONDecodeError, TypeError) as e:
             logger.error(f"Error parsing/validating ContentGenerationAgent A2A response: {e}", exc_info=True)
             return None
        except Exception as e:
            logger.error(f"Unexpected error during ContentGenerationAgent A2A call: {str(e)}", exc_info=True)
            return None


    async def run_async(self, context: InvocationContext) -> Event:
        """
        Executes the market research workflow asynchronously according to ADK spec.
        Reads input from context, performs research (including web search), and returns an Event.
        """
        logger.info(f"Received invocation for MarketResearchAgent (ID: {context.invocation_id})")
        agent_id = context.agent_id
        invocation_id = context.invocation_id
        web_search_results = None # Initialize web search results

        try:
            # 1. Parse and Validate Input from context
            try:
                if not isinstance(context.input, dict):
                     raise TypeError(f"Expected dict input, got {type(context.input)}")
                inputs = MarketResearchInput(**context.input)
                logger.info(f"Parsed input: Topic='{inputs.initial_topic}', Target URL='{inputs.target_url}', Num Competitors={inputs.num_competitors}")
            except (ValidationError, TypeError) as e:
                error_msg = f"Input validation/parsing failed: {e}"
                logger.error(error_msg, exc_info=True)
                return Event(
                    agent_id=agent_id,
                    invocation_id=invocation_id,
                    severity=EventSeverity.FATAL, # Input error is fatal for this invocation
                    message=error_msg,
                    payload={"error": str(e), "received_input": context.input}
                )

            # 2. Find Competitor URLs (using configured provider)
            logger.info(f"Finding competitors using {self.search_provider}...")
            target_url_str = str(inputs.target_url) if inputs.target_url else None
            if self.search_provider == "exa":
                competitor_urls = await self._find_competitor_urls_exa(
                    topic=inputs.initial_topic,
                    target_url=target_url_str,
                    num_results=inputs.num_competitors
                )
            elif self.search_provider == "perplexity":
                 competitor_urls = await self._find_competitor_urls_perplexity(
                    topic=inputs.initial_topic,
                    target_url=target_url_str,
                    num_results=inputs.num_competitors
                )
            else:
                 # This case should be caught by __init__, but handle defensively
                 return Event(
                    agent_id=agent_id,
                    invocation_id=invocation_id,
                    severity=EventSeverity.FATAL,
                    message=f"Internal configuration error: Invalid search provider '{self.search_provider}'",
                    payload={"error": "Configuration error"}
                 )

            # --- New Step 2b: Perform General Web Search via A2A ---
            logger.info(f"Performing general web search for topic: '{inputs.initial_topic}' via A2A...")
            web_search_results = await self._call_web_search_agent(
                query=inputs.initial_topic,
                parent_context=context
            )
            if web_search_results:
                logger.info("Successfully received web search results via A2A.")
            else:
                logger.warning("Web search via A2A failed or returned no results. Proceeding without web context.")
            # --- End New Step ---


            if not competitor_urls:
                warning_msg = "No competitor URLs found for the given topic/URL."
                logger.warning(warning_msg)
                # Return a successful event but indicate no competitors found via payload
                # Include web search results if available
                empty_report = MarketOpportunityReport(
                    competitors=[],
                    analysis=MarketAnalysis(
                        market_gaps=["N/A - No competitors found"],
                        opportunities=["N/A - No competitors found"],
                        competitor_weaknesses=["N/A - No competitors found"],
                        pricing_strategies=["N/A - No competitors found"],
                        positioning_strategies=["N/A - No competitors found"]
                    ),
                    feature_recommendations=[],
                    target_audience_suggestions=[]
                )
                payload = empty_report.model_dump()

                return Event(
                    agent_id=agent_id,
                    invocation_id=invocation_id,
                    severity=EventSeverity.INFO,
                    message=warning_msg + (" Web search performed." if web_search_results else " Web search failed or skipped."),
                    payload=payload
                )

            # 3. Extract Data for each Competitor (concurrently)
            logger.info(f"Attempting to extract data for {len(competitor_urls)} competitors: {competitor_urls}")
            extraction_tasks = [self._extract_competitor_info(url) for url in competitor_urls]
            results = await asyncio.gather(*extraction_tasks, return_exceptions=True)

            competitors_data: List[CompetitorInfo] = []
            failed_extractions = 0
            extraction_errors = []
            for i, res in enumerate(results):
                if isinstance(res, CompetitorInfo):
                    competitors_data.append(res)
                else:
                    failed_extractions += 1
                    error_detail = f"URL: {competitor_urls[i]}, Error: {str(res)}"
                    extraction_errors.append(error_detail)
                    logger.warning(f"Failed extraction for {competitor_urls[i]}. Error: {res}", exc_info=res if isinstance(res, Exception) else None)


            if not competitors_data:
                 error_msg = "Could not extract data from any identified competitor URLs."
                 logger.error(f"{error_msg} Errors: {extraction_errors}")
                 payload = {
                     "competitor_urls_found": competitor_urls,
                     "extraction_errors": extraction_errors
                 }
                 return Event(
                     agent_id=agent_id,
                    invocation_id=invocation_id,
                    severity=EventSeverity.ERROR,
                    message=error_msg,
                    payload=payload
                 )

            # Log a warning if some extractions failed but not all
            partial_extraction_warning = ""
            if failed_extractions > 0:
                partial_extraction_warning = f" Failed to extract data for {failed_extractions} URL(s)."
                logger.warning(f"Proceeding with data from {len(competitors_data)} out of {len(competitor_urls)} competitors. Errors: {extraction_errors}")

            # 4. Generate Final Analysis Report via ContentGenerationAgent A2A
            logger.info(f"Calling ContentGenerationAgent A2A to generate report based on data from {len(competitors_data)} competitors and web search results...")
            analysis_payload = await self._call_content_generation_agent(
                competitors_data=competitors_data,
                web_search_results=web_search_results,
                parent_context=context
            )

            if not analysis_payload or not isinstance(analysis_payload, dict):
                error_msg = "Failed to generate analysis report via ContentGenerationAgent A2A or received invalid payload."
                logger.error(error_msg)
                payload = {
                    "extracted_competitor_data": [c.model_dump(exclude_none=True) for c in competitors_data],
                    "extraction_errors": extraction_errors,
                    "web_search_results": web_search_results # Include for debugging
                }
                return Event(
                    agent_id=agent_id,
                    invocation_id=invocation_id,
                    severity=EventSeverity.ERROR,
                    message=error_msg,
                    payload=payload
                )

            # 5. Construct Final Report from A2A Payload
            try:
                final_report = MarketOpportunityReport(
                    competitors=competitors_data, # Add back the competitor data
                    analysis=MarketAnalysis(**analysis_payload.get("analysis", {})),
                    feature_recommendations=analysis_payload.get("feature_recommendations", []),
                    target_audience_suggestions=analysis_payload.get("target_audience_suggestions", [])
                )
                logger.info("Successfully constructed final report from ContentGenerationAgent response.")
            except (ValidationError, TypeError) as e:
                 error_msg = f"Failed to validate or construct MarketOpportunityReport from ContentGenerationAgent payload: {e}"
                 logger.error(f"{error_msg}. Payload received: {analysis_payload}", exc_info=True)
                 payload = {
                    "extracted_competitor_data": [c.model_dump(exclude_none=True) for c in competitors_data],
                    "extraction_errors": extraction_errors,
                    "web_search_results": web_search_results,
                    "a2a_payload_received": analysis_payload # Include raw payload for debugging
                 }
                 return Event(
                     agent_id=agent_id,
                     invocation_id=invocation_id,
                     severity=EventSeverity.ERROR,
                     message=error_msg,
                     payload=payload
                 )


            success_message = f"Market research completed. Analyzed {len(competitors_data)} competitors. Report generated via ContentGenerationAgent."
            success_message += partial_extraction_warning
            success_message += (" Incorporated web search results." if web_search_results else " Web search failed or skipped.")
            logger.info(success_message)

            # 6. Return Success Event
            return Event(
                agent_id=agent_id,
                invocation_id=invocation_id,
                severity=EventSeverity.INFO,
                message=success_message,
                payload=final_report.model_dump()
            )

        except Exception as e:
            # Catch-all for unexpected errors during the main execution flow
            error_msg = f"Unexpected fatal error in MarketResearchAgent execution: {str(e)}"
            logger.critical(error_msg, exc_info=True)
            payload = {"error": str(e), "traceback": traceback.format_exc()}
            return Event(
                agent_id=agent_id if 'agent_id' in locals() else 'unknown',
                invocation_id=invocation_id if 'invocation_id' in locals() else 'unknown',
                severity=EventSeverity.FATAL,
                message=error_msg,
                payload=payload
            )


# Agent now uses run_async and delegates report generation to ContentGenerationAgent.