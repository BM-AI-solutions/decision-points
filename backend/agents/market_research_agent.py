import os
import json
# import requests # Removed, using httpx
import httpx # Added for async requests
import asyncio
import traceback # Add traceback import
import logging # Add logging import
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, HttpUrl, ValidationError

# ADK Imports
from google.adk.agents import Agent
from google.adk.runtime import InvocationContext
from google.adk.runtime.event import Event, EventSeverity

# Assuming Exa and Firecrawl libraries are installed
from exa_py import Exa
from firecrawl import FirecrawlApp, AsyncFirecrawlApp # Import AsyncFirecrawlApp
import openai # Keep openai import for now, ADK might provide its own LLM client

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

logger.info("Attempting to load API keys from environment variables...")

# --- Configuration ---
# Load API keys from environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")
EXA_API_KEY = os.getenv("EXA_API_KEY")
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
SEARCH_PROVIDER = os.getenv("COMPETITOR_SEARCH_PROVIDER", "exa").lower() # 'exa' or 'perplexity'

# --- Pydantic Models ---

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
    Finds competitors, extracts data, and generates a MarketOpportunityReport.
    Inherits from google.adk.agents.Agent.
    """
    def __init__(self):
        """Initialize the agent and required clients."""
        # Basic validation - In a real ADK agent, config might be injected.
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.firecrawl_api_key = os.getenv("FIRECRAWL_API_KEY")
        self.exa_api_key = os.getenv("EXA_API_KEY")
        self.perplexity_api_key = os.getenv("PERPLEXITY_API_KEY")
        self.search_provider = os.getenv("COMPETITOR_SEARCH_PROVIDER", "exa").lower()

        if not self.firecrawl_api_key:
            # In ADK, initialization errors should ideally prevent agent loading
            # or be reported during startup. Raising here is okay for now.
            raise ValueError("FIRECRAWL_API_KEY environment variable not set.")
        # Use AsyncFirecrawlApp
        self.firecrawl_client = AsyncFirecrawlApp(api_key=self.firecrawl_api_key)

        if self.search_provider == "exa":
            if not self.exa_api_key:
                raise ValueError("EXA_API_KEY environment variable not set for Exa search provider.")
            self.exa_client = Exa(api_key=self.exa_api_key)
            logger.info("Using Exa for competitor search.")
        elif self.search_provider == "perplexity":
            if not self.perplexity_api_key:
                raise ValueError("PERPLEXITY_API_KEY environment variable not set for Perplexity search provider.")
            # Initialize httpx client for Perplexity
            self.http_client = httpx.AsyncClient(timeout=30.0) # Reuse client
            logger.info("Using Perplexity for competitor search.")
        else:
            raise ValueError(f"Unsupported SEARCH_PROVIDER: {self.search_provider}. Use 'exa' or 'perplexity'.")

        if not self.openai_api_key:
            # ADK might handle LLM client injection differently.
            # Log a warning, but don't prevent initialization. run_async will handle the error.
            logger.warning("OPENAI_API_KEY not set. Analysis step might fail if using direct OpenAI call.")


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

    async def _generate_analysis(self, competitors_data: List[CompetitorInfo]) -> Union[MarketOpportunityReport, str]:
        """
        Analyzes competitor data using an LLM to generate the final report asynchronously.
        Returns MarketOpportunityReport on success, or an error message string on failure.
        """
        logger.info("Generating analysis using LLM...")
        if not self.openai_api_key:
             error_msg = "OPENAI_API_KEY is required for the analysis step but is not configured."
             logger.error(error_msg)
             return error_msg # Return error message string

        # Prepare data, ensuring it's valid JSON
        try:
            competitors_json = json.dumps([c.model_dump(exclude_none=True) for c in competitors_data], indent=2)
        except TypeError as e:
            error_msg = f"Failed to serialize competitor data to JSON: {e}"
            logger.error(error_msg, exc_info=True)
            return error_msg

        system_prompt = f"""
You are an expert market analyst. Analyze the following competitor data (in JSON format) for a business operating in the same space.
Your goal is to identify opportunities for a new entrant or existing player based on this data.

Competitor Data:
```json
{competitors_json}
```

Generate a report with the following structure:
1.  **Market Analysis**: Identify market gaps, opportunities, competitor weaknesses, and suggest potential pricing and positioning strategies.
2.  **Feature Recommendations**: Suggest unique features or capabilities the user's company should develop based on the analysis. List specific, actionable features.
3.  **Target Audience Suggestions**: Suggest potential target demographics or niches that appear underserved or could be targeted effectively.

Provide the output STRICTLY in the following JSON format, matching the Pydantic models `MarketAnalysis`, `MarketOpportunityReport`:

```json
{{
  "analysis": {{
    "market_gaps": ["Gap 1...", "Gap 2..."],
    "opportunities": ["Opportunity 1...", "Opportunity 2..."],
    "competitor_weaknesses": ["Weakness 1...", "Weakness 2..."],
    "pricing_strategies": ["Strategy 1...", "Strategy 2..."],
    "positioning_strategies": ["Strategy 1...", "Strategy 2..."]
  }},
  "feature_recommendations": ["Feature 1...", "Feature 2...", "Feature 3..."],
  "target_audience_suggestions": ["Audience 1...", "Audience 2..."]
}}
```

Focus on actionable insights derived *only* from the provided competitor data. Be specific in your recommendations. Do not include the competitor data itself in the final JSON output structure (it will be added back later). Ensure the output is valid JSON.
"""
        analysis_json_str = "N/A" # Initialize for error reporting
        try:
            # Use ADK's LLM client if available, otherwise use direct OpenAI call
            # Using AsyncOpenAI client directly for now
            # NOTE: Replace with ADK's LLM mechanism when available
            client = openai.AsyncOpenAI(api_key=self.openai_api_key)
            response = await client.chat.completions.create(
                model="gpt-4o", # Consider making model configurable via env var
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": "Generate the market opportunity report based on the provided competitor data."}
                ],
                response_format={"type": "json_object"},
                temperature=0.5, # Adjust temperature for creativity vs. factuality
                timeout=120 # Add timeout for LLM call
            )
            analysis_json_str = response.choices[0].message.content
            analysis_data = json.loads(analysis_json_str) # Parse the JSON string

            # Validate structure before creating the report object using Pydantic
            # This ensures the LLM output conforms to the expected nested structure
            report = MarketOpportunityReport(
                competitors=competitors_data, # Add back the competitor data list
                analysis=MarketAnalysis(**analysis_data.get("analysis", {})),
                feature_recommendations=analysis_data.get("feature_recommendations", []),
                target_audience_suggestions=analysis_data.get("target_audience_suggestions", [])
            )
            logger.info("Successfully generated and validated analysis.")
            return report # Return the Pydantic model instance

        except ImportError:
             error_msg = "OpenAI library not installed or async client not available. Cannot perform analysis."
             logger.error(error_msg, exc_info=True)
             return error_msg
        except openai.APIError as e:
            error_msg = f"OpenAI API error during analysis: {e}"
            logger.error(error_msg, exc_info=True)
            return error_msg
        except (json.JSONDecodeError, ValueError, ValidationError, TypeError) as e: # Catch JSON, structure, Pydantic, and Type errors
            error_msg = f"Failed to process or validate LLM response: {e}. Response received: {analysis_json_str}"
            logger.error(error_msg, exc_info=True)
            return error_msg # Return error message string
        except Exception as e:
            # Catch any other unexpected errors
            error_msg = f"Unexpected error during LLM analysis: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return error_msg # Return error message string


    async def run_async(self, context: InvocationContext) -> Event:
        """
        Executes the market research workflow asynchronously according to ADK spec.
        Reads input from context, performs research, and returns an Event.
        """
        logger.info(f"Received invocation for MarketResearchAgent (ID: {context.invocation_id})")
        agent_id = context.agent_id
        invocation_id = context.invocation_id

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

            if not competitor_urls:
                warning_msg = "No competitor URLs found for the given topic/URL."
                logger.warning(warning_msg)
                # Return a successful event but indicate no competitors found via payload
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
                return Event(
                    agent_id=agent_id,
                    invocation_id=invocation_id,
                    severity=EventSeverity.INFO, # Changed to INFO as it's a valid outcome, not a warning/error
                    message=warning_msg, # Message indicates the outcome
                    payload=empty_report.model_dump() # Payload contains the empty report
                )

            # 3. Extract Data for each Competitor (concurrently)
            logger.info(f"Attempting to extract data for {len(competitor_urls)} competitors: {competitor_urls}")
            extraction_tasks = [self._extract_competitor_info(url) for url in competitor_urls]
            # Use gather with return_exceptions=True to handle individual extraction failures
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
                 # Return error event as extraction failed completely
                 return Event(
                     agent_id=agent_id,
                    invocation_id=invocation_id,
                    severity=EventSeverity.ERROR, # Extraction failure is an error
                    message=error_msg,
                    payload={"competitor_urls_found": competitor_urls, "extraction_errors": extraction_errors}
                 )

            # Log a warning if some extractions failed but not all
            partial_extraction_warning = ""
            if failed_extractions > 0:
                partial_extraction_warning = f" Failed to extract data for {failed_extractions} URL(s)."
                logger.warning(f"Proceeding with data from {len(competitors_data)} out of {len(competitor_urls)} competitors. Errors: {extraction_errors}")

            # 4. Generate Final Analysis Report using LLM
            logger.info(f"Generating final analysis report based on data from {len(competitors_data)} competitors...")
            analysis_result = await self._generate_analysis(competitors_data)

            if isinstance(analysis_result, str): # Check if analysis returned an error message string
                error_msg = f"Analysis generation failed: {analysis_result}"
                logger.error(error_msg)
                # Return error event, include extracted data for debugging
                return Event(
                    agent_id=agent_id,
                    invocation_id=invocation_id,
                    severity=EventSeverity.ERROR, # Analysis failure is an error
                    message=error_msg,
                    payload={
                        "extracted_competitor_data": [c.model_dump() for c in competitors_data],
                        "extraction_errors": extraction_errors # Include extraction errors if any
                        }
                )

            # If analysis succeeded, analysis_result is a MarketOpportunityReport
            final_report: MarketOpportunityReport = analysis_result
            success_message = f"Market research completed. Analyzed {len(competitors_data)} competitors." + partial_extraction_warning
            logger.info(success_message)

            # 5. Return Success Event
            return Event(
                agent_id=agent_id,
                invocation_id=invocation_id,
                severity=EventSeverity.INFO, # Use INFO for successful completion
                message=success_message,
                payload=final_report.model_dump() # Send the full report as payload
            )

        except Exception as e:
            # Catch-all for unexpected errors during the main execution flow
            error_msg = f"Unexpected fatal error in MarketResearchAgent execution: {str(e)}"
            logger.critical(error_msg, exc_info=True) # Use critical for fatal errors
            # Use severity FATAL for unhandled exceptions in the main flow
            return Event(
                agent_id=agent_id if 'agent_id' in locals() else 'unknown', # Use agent_id if available
                invocation_id=invocation_id if 'invocation_id' in locals() else 'unknown', # Use invocation_id if available
                severity=EventSeverity.FATAL,
                message=error_msg,
                payload={"error": str(e), "traceback": traceback.format_exc()} # Include traceback for debugging
            )


# Removed old run method and __main__ block. Agent now uses run_async.