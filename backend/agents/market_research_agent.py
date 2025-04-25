"""
Market Research Agent for Decision Points.

This agent performs market research using various tools and APIs.
It implements the A2A protocol for agent communication.
"""

import json
import httpx
import asyncio
import traceback
import logging
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, HttpUrl, ValidationError

# ADK Imports
from google.adk.runtime import InvocationContext
from google.adk.runtime.event import Event, EventSeverity

# A2A Imports
from python_a2a import skill

# Tooling Imports
from exa_py import Exa
from firecrawl import FirecrawlApp, AsyncFirecrawlApp
import google.generativeai as genai
from google.api_core import exceptions as google_exceptions

from agents.base_agent import BaseSpecializedAgent
from app.config import settings

# Setup logging
logger = logging.getLogger(__name__)

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

class MarketResearchAgent(BaseSpecializedAgent):
    """
    Agent responsible for market research.
    Finds competitors, extracts data, performs web search, and generates a MarketOpportunityReport.
    Implements A2A protocol for agent communication.
    """
    def __init__(
        self,
        name: str = "market_research",
        description: str = "Performs market research using various tools and APIs",
        model_name: Optional[str] = None,
        port: Optional[int] = None,
        **kwargs: Any,
    ):
        """
        Initialize the MarketResearchAgent.

        Args:
            name: The name of the agent.
            description: The description of the agent.
            model_name: The name of the model to use. Defaults to settings.GEMINI_MODEL_NAME.
            port: The port to run the A2A server on. Defaults to settings.MARKET_RESEARCH_AGENT_URL port.
            **kwargs: Additional arguments for BaseSpecializedAgent.
        """
        # Extract port from URL if not provided
        if port is None and settings.MARKET_RESEARCH_AGENT_URL:
            try:
                port = int(settings.MARKET_RESEARCH_AGENT_URL.split(':')[-1])
            except (ValueError, IndexError):
                port = 8004  # Default port

        # Initialize BaseSpecializedAgent
        super().__init__(
            name=name,
            description=description,
            model_name=model_name,
            port=port,
            **kwargs
        )

        # Load configuration from the central settings object
        self.google_api_key = settings.GOOGLE_API_KEY
        self.firecrawl_api_key = settings.FIRECRAWL_API_KEY
        self.exa_api_key = settings.EXA_API_KEY
        self.perplexity_api_key = settings.PERPLEXITY_API_KEY
        self.search_provider = settings.COMPETITOR_SEARCH_PROVIDER.lower()
        self.agent_web_search_id = settings.AGENT_WEB_SEARCH_ID
        self.brave_api_key = settings.BRAVE_API_KEY
        self.content_generation_agent_id = settings.CONTENT_GENERATION_AGENT_ID

        # Initialize shared httpx client
        self.http_client = httpx.AsyncClient(timeout=30.0)

        # --- Validation & Client Initialization ---
        if not self.firecrawl_api_key:
            raise ValueError("FIRECRAWL_API_KEY not configured in settings.")
        self.firecrawl_client = AsyncFirecrawlApp(api_key=self.firecrawl_api_key)

        if self.search_provider == "exa":
            if not self.exa_api_key:
                raise ValueError("EXA_API_KEY not configured in settings for Exa search provider.")
            self.exa_client = Exa(api_key=self.exa_api_key)
            logger.info("Using Exa for competitor search (configured via settings).")
        elif self.search_provider == "perplexity":
            if not self.perplexity_api_key:
                raise ValueError("PERPLEXITY_API_KEY not configured in settings for Perplexity search provider.")
            logger.info("Using Perplexity for competitor search (configured via settings).")
        else:
            raise ValueError(f"Unsupported COMPETITOR_SEARCH_PROVIDER in settings: {self.search_provider}. Use 'exa' or 'perplexity'.")

        # --- Gemini Initialization ---
        if not self.google_api_key:
            logger.warning("GOOGLE_API_KEY not configured in settings. Gemini model initialization skipped.")
            self.gemini_model = None
        else:
            try:
                genai.configure(api_key=self.google_api_key)
                self.gemini_model = genai.GenerativeModel(
                    self.model_name,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.5,
                        response_mime_type="application/json",
                    ),
                )
                logger.info(f"Gemini client configured successfully using model: {self.model_name}")
            except Exception as e:
                logger.error(f"Failed to configure or initialize Gemini client with model {self.model_name}: {e}", exc_info=True)
                self.gemini_model = None

        # --- A2A Validation ---
        if not self.agent_web_search_id:
            logger.warning("AGENT_WEB_SEARCH_ID not configured in settings. Cannot call WebSearchAgent.")
        if not self.content_generation_agent_id:
            logger.warning("CONTENT_GENERATION_AGENT_ID not configured in settings. Cannot call ContentGenerationAgent.")

        logger.info(f"MarketResearchAgent initialized with port: {self.port}")


    # ... (_find_competitor_urls_exa, _find_competitor_urls_perplexity, _extract_competitor_info, _call_agent_web_search remain the same) ...
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
            # Use httpx for external Perplexity API call
            async with httpx.AsyncClient(timeout=30.0) as client:
                 response = await client.post(perplexity_url, json=payload, headers=headers)

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

    # --- A2A Skills ---
    @skill(
        name="research_market",
        description="Perform market research for a given niche or product",
        tags=["research", "market"]
    )
    async def research_market(self, topic: str, target_url: Optional[str] = None, num_competitors: int = 3) -> Dict[str, Any]:
        """
        Perform market research for a given niche or product.

        Args:
            topic: The niche or product to research.
            target_url: Optional URL of the user's company for comparison.
            num_competitors: Number of competitors to find and analyze.

        Returns:
            A dictionary containing the research results.
        """
        logger.info(f"Performing market research for '{topic}' with target URL '{target_url}' and {num_competitors} competitors")

        try:
            # Create input model
            inputs = MarketResearchInput(
                initial_topic=topic,
                target_url=target_url,
                num_competitors=num_competitors
            )

            # Find competitor URLs
            if self.search_provider == "exa":
                competitor_urls = await self._find_competitor_urls_exa(
                    topic=inputs.initial_topic,
                    target_url=str(inputs.target_url) if inputs.target_url else None,
                    num_results=inputs.num_competitors
                )
            elif self.search_provider == "perplexity":
                competitor_urls = await self._find_competitor_urls_perplexity(
                    topic=inputs.initial_topic,
                    target_url=str(inputs.target_url) if inputs.target_url else None,
                    num_results=inputs.num_competitors
                )
            else:
                return {"error": f"Unsupported search provider: {self.search_provider}"}

            if not competitor_urls:
                return {
                    "success": False,
                    "message": "No competitor URLs found for the given topic/URL.",
                    "competitors": [],
                    "analysis": {
                        "market_gaps": ["N/A - No competitors found"],
                        "opportunities": ["N/A - No competitors found"],
                        "competitor_weaknesses": ["N/A - No competitors found"],
                        "pricing_strategies": ["N/A - No competitors found"],
                        "positioning_strategies": ["N/A - No competitors found"]
                    },
                    "feature_recommendations": [],
                    "target_audience_suggestions": []
                }

            # Extract data for each competitor
            extraction_tasks = [self._extract_competitor_info(url) for url in competitor_urls]
            results = await asyncio.gather(*extraction_tasks, return_exceptions=True)

            competitors_data = []
            failed_extractions = 0
            extraction_errors = []

            for i, res in enumerate(results):
                if isinstance(res, CompetitorInfo):
                    competitors_data.append(res)
                else:
                    failed_extractions += 1
                    error_detail = f"URL: {competitor_urls[i]}, Error: {str(res)}"
                    extraction_errors.append(error_detail)

            if not competitors_data:
                return {
                    "success": False,
                    "message": "Could not extract data from any identified competitor URLs.",
                    "competitor_urls_found": competitor_urls,
                    "extraction_errors": extraction_errors
                }

            # Generate analysis using Gemini
            if self.gemini_model:
                analysis = await self._generate_analysis(competitors_data, topic)
            else:
                analysis = {
                    "analysis": {
                        "market_gaps": ["Gemini model not available for analysis"],
                        "opportunities": ["Gemini model not available for analysis"],
                        "competitor_weaknesses": ["Gemini model not available for analysis"],
                        "pricing_strategies": ["Gemini model not available for analysis"],
                        "positioning_strategies": ["Gemini model not available for analysis"]
                    },
                    "feature_recommendations": ["Gemini model not available for analysis"],
                    "target_audience_suggestions": ["Gemini model not available for analysis"]
                }

            # Construct final report
            final_report = {
                "success": True,
                "message": f"Market research completed. Analyzed {len(competitors_data)} competitors.",
                "competitors": [c.model_dump(exclude_none=True) for c in competitors_data],
                "analysis": analysis.get("analysis", {}),
                "feature_recommendations": analysis.get("feature_recommendations", []),
                "target_audience_suggestions": analysis.get("target_audience_suggestions", [])
            }

            return final_report

        except Exception as e:
            logger.error(f"Error performing market research: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"Error performing market research: {str(e)}"
            }

    @skill(
        name="analyze_competitors",
        description="Analyze competitors in a given niche",
        tags=["research", "competitors"]
    )
    async def analyze_competitors(self, topic: str, max_competitors: int = 5) -> Dict[str, Any]:
        """
        Analyze competitors in a given niche.

        Args:
            topic: The niche to analyze competitors for.
            max_competitors: The maximum number of competitors to analyze.

        Returns:
            A dictionary containing the competitor analysis.
        """
        logger.info(f"Analyzing competitors for '{topic}' (max: {max_competitors})")

        try:
            # Find competitor URLs
            if self.search_provider == "exa":
                competitor_urls = await self._find_competitor_urls_exa(
                    topic=topic,
                    target_url=None,
                    num_results=max_competitors
                )
            elif self.search_provider == "perplexity":
                competitor_urls = await self._find_competitor_urls_perplexity(
                    topic=topic,
                    target_url=None,
                    num_results=max_competitors
                )
            else:
                return {"error": f"Unsupported search provider: {self.search_provider}"}

            if not competitor_urls:
                return {
                    "success": False,
                    "message": "No competitor URLs found for the given topic.",
                    "competitors": []
                }

            # Extract data for each competitor
            extraction_tasks = [self._extract_competitor_info(url) for url in competitor_urls]
            results = await asyncio.gather(*extraction_tasks, return_exceptions=True)

            competitors_data = []
            failed_extractions = 0
            extraction_errors = []

            for i, res in enumerate(results):
                if isinstance(res, CompetitorInfo):
                    competitors_data.append(res)
                else:
                    failed_extractions += 1
                    error_detail = f"URL: {competitor_urls[i]}, Error: {str(res)}"
                    extraction_errors.append(error_detail)

            if not competitors_data:
                return {
                    "success": False,
                    "message": "Could not extract data from any identified competitor URLs.",
                    "competitor_urls_found": competitor_urls,
                    "extraction_errors": extraction_errors
                }

            return {
                "success": True,
                "message": f"Competitor analysis completed. Analyzed {len(competitors_data)} competitors.",
                "competitors": [c.model_dump(exclude_none=True) for c in competitors_data]
            }

        except Exception as e:
            logger.error(f"Error analyzing competitors: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"Error analyzing competitors: {str(e)}"
            }

    async def _generate_analysis(self, competitors_data: List[CompetitorInfo], topic: str) -> Dict[str, Any]:
        """Generate analysis using Gemini."""
        try:
            # Convert competitors data to JSON
            competitors_json = json.dumps([c.model_dump(exclude_none=True) for c in competitors_data], indent=2)

            # Create prompt for Gemini
            prompt = f"""
            Analyze the following market research data for competitors in the {topic} niche.
            Generate a structured report summarizing the findings and providing actionable insights.

            Competitor Data:
            ```json
            {competitors_json}
            ```

            Based on the provided data, generate a JSON object containing:
            1. 'analysis': An object with fields 'market_gaps', 'opportunities', 'competitor_weaknesses', 'pricing_strategies', 'positioning_strategies' (each a list of strings).
            2. 'feature_recommendations': A list of strings suggesting potential features.
            3. 'target_audience_suggestions': A list of strings suggesting target audiences.

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
            """

            # Generate response
            response = await self.gemini_model.generate_content_async(prompt)

            # Parse response
            response_text = response.text

            # Extract JSON from response
            try:
                # Try to parse the entire response as JSON
                analysis = json.loads(response_text)
                return analysis
            except json.JSONDecodeError:
                # If that fails, try to extract JSON from the response
                import re
                json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
                if json_match:
                    try:
                        analysis = json.loads(json_match.group(1))
                        return analysis
                    except json.JSONDecodeError:
                        logger.error(f"Failed to parse JSON from Gemini response: {response_text}")
                        return {}
                else:
                    logger.error(f"No JSON found in Gemini response: {response_text}")
                    return {}

        except Exception as e:
            logger.error(f"Error generating analysis: {e}", exc_info=True)
            return {}

    # --- WebSearchAgent A2A Call ---
    async def _call_agent_web_search(self, query: str) -> Optional[Dict[str, Any]]:
        """Calls the WebSearchAgent via A2A to perform a general web search."""
        if not self.agent_web_search_id:
            logger.error("WebSearchAgent ID not configured for A2A call.")
            return None

        logger.info(f"Invoking WebSearchAgent skill 'web_search' with query: '{query}' via agent network...")

        try:
            from agents.agent_network import agent_network

            # Get the agent from the network
            agent = agent_network.get_agent("web_search")
            if not agent:
                logger.error("WebSearchAgent not found in agent network.")
                return None

            # Invoke the web_search skill
            result = await agent.invoke_skill(
                skill_name="web_search",
                input_data={"query": query},
                timeout=30.0
            )

            logger.info(f"WebSearchAgent skill invocation successful.")
            return result
        except Exception as e:
            logger.error(f"Error calling WebSearchAgent: {e}", exc_info=True)
            return None

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

        # Prepare the input Event for the ContentGenerationAgent skill
        input_payload = {
            "prompt": prompt,
            "output_format": "json" # Assuming ContentGenAgent supports this
        }
        input_event = Event(payload=input_payload)

        try:
            # Use context.invoke_skill for ADK A2A
            result_event = await context.invoke_skill(
                target_agent_id=self.content_generation_agent_id,
                skill_name="generate", # Assuming skill name
                input=input_event,
                timeout_seconds=60.0 # Keep timeout
            )

            if result_event.type == "error":
                error_msg = result_event.payload.get('message', 'Unknown error from ContentGenerationAgent skill')
                logger.error(f"ContentGenerationAgent skill invocation failed: {error_msg}")
                return None
            elif result_event.payload and result_event.payload.get("status") == "success":
                logger.info(f"ContentGenerationAgent skill invocation successful.")
                # Assuming the structured JSON is in the payload under 'generated_content'
                generated_content = result_event.payload.get('generated_content')
                if isinstance(generated_content, str):
                    try:
                        return json.loads(generated_content)
                    except json.JSONDecodeError as json_err:
                        logger.error(f"Failed to parse JSON from ContentGenerationAgent payload: {json_err}. Content: {generated_content}")
                        return None
                elif isinstance(generated_content, dict):
                    return generated_content # Already a dict
                else:
                    logger.error(f"Unexpected type for 'generated_content' in ContentGenerationAgent payload: {type(generated_content)}")
                    return None
            else:
                # Handle cases where the skill call succeeded but indicated an internal failure or unexpected payload
                error_msg = result_event.payload.get("message", "Unknown or unsuccessful response from ContentGenerationAgent skill")
                logger.error(f"ContentGenerationAgent skill call reported failure or unexpected payload: {error_msg}")
                logger.debug(f"ContentGenerationAgent Payload: {result_event.payload}")
                return None

        except TimeoutError:
            logger.error(f"ADK skill invocation for ContentGenerationAgent timed out.", exc_info=True)
            return None
        except ConnectionError as conn_err:
            logger.error(f"ADK skill invocation for ContentGenerationAgent failed (Connection Error): {conn_err}", exc_info=True)
            return None
        except Exception as e:
            logger.error(f"Unexpected error during ContentGenerationAgent skill invocation: {str(e)}", exc_info=True)
            return None


    async def run_async(self, context: InvocationContext) -> Event:
        """
        Executes the market research workflow asynchronously according to ADK spec.
        Maintained for backward compatibility with ADK.

        Args:
            context: The invocation context containing the input data.

        Returns:
            An Event containing the research results or an error.
        """
        logger.info(f"Received invocation for MarketResearchAgent (ID: {context.invocation_id})")
        agent_id = getattr(context, 'agent_id', self.name)
        invocation_id = getattr(context, 'invocation_id', str(id(context)))

        try:
            # Extract input from context
            input_data = {}
            if hasattr(context, 'input') and isinstance(context.input, dict):
                input_data = context.input
            elif hasattr(context, 'data') and isinstance(context.data, dict):
                input_data = context.data
            elif hasattr(context, 'input_event') and hasattr(context.input_event, 'data'):
                input_data = context.input_event.data

            # Parse and validate input
            try:
                inputs = MarketResearchInput(**input_data)
                logger.info(f"Parsed input: Topic='{inputs.initial_topic}', Target URL='{inputs.target_url}', Num Competitors={inputs.num_competitors}")
            except (ValidationError, TypeError) as e:
                error_msg = f"Input validation/parsing failed: {e}"
                logger.error(error_msg, exc_info=True)
                return Event(
                    agent_id=agent_id,
                    invocation_id=invocation_id,
                    severity=EventSeverity.FATAL,
                    message=error_msg,
                    payload={"error": str(e), "received_input": input_data}
                )

            # Use the A2A skill
            result = await self.research_market(
                topic=inputs.initial_topic,
                target_url=inputs.target_url,
                num_competitors=inputs.num_competitors
            )

            # Create an event from the result
            if result.get("success", False):
                return Event(
                    agent_id=agent_id,
                    invocation_id=invocation_id,
                    severity=EventSeverity.INFO,
                    message=result.get("message", "Market research completed successfully."),
                    payload=result
                )
            else:
                return Event(
                    agent_id=agent_id,
                    invocation_id=invocation_id,
                    severity=EventSeverity.ERROR,
                    message=result.get("message", "Market research failed."),
                    payload=result
                )

        except Exception as e:
            # Catch-all for unexpected errors
            error_msg = f"Unexpected fatal error in MarketResearchAgent execution: {str(e)}"
            logger.critical(error_msg, exc_info=True)
            payload = {"error": str(e), "traceback": traceback.format_exc()}
            return Event(
                agent_id=agent_id,
                invocation_id=invocation_id,
                severity=EventSeverity.FATAL,
                message=error_msg,
                payload=payload
            )


# Example of how to run this agent as a standalone A2A server
if __name__ == "__main__":
    # Create the agent
    agent = MarketResearchAgent()

    # Run the A2A server
    agent.run_server(host="0.0.0.0", port=agent.port or 8004)