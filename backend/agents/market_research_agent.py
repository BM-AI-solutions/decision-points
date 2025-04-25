"""
Market Research Agent for Decision Points (ADK Version).

This agent performs market research using various tools and APIs via ADK tools.
"""

import json
import httpx
import asyncio
import traceback
import logging
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, HttpUrl, ValidationError

# ADK Imports
from google.adk.agents import Agent # Use ADK Agent


# Tooling Imports
from exa_py import Exa
from firecrawl import FirecrawlApp, AsyncFirecrawlApp
import google.generativeai as genai
from google.api_core import exceptions as google_exceptions

# Removed BaseSpecializedAgent import
from app.config import settings

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Global Clients & Config (Consider dependency injection for production) ---
AGENT_ID = "market_research_adk"
GOOGLE_API_KEY = settings.GOOGLE_API_KEY
FIRECRAWL_API_KEY = settings.FIRECRAWL_API_KEY
EXA_API_KEY = settings.EXA_API_KEY
PERPLEXITY_API_KEY = settings.PERPLEXITY_API_KEY
SEARCH_PROVIDER = settings.COMPETITOR_SEARCH_PROVIDER.lower()

# Initialize clients globally (handle potential errors)
HTTP_CLIENT = httpx.AsyncClient(timeout=30.0)
FIRECRAWL_CLIENT = None
EXA_CLIENT = None
GEMINI_MODEL = None

if not FIRECRAWL_API_KEY:
    logger.error("FIRECRAWL_API_KEY not configured. Market research agent cannot function.")
else:
    FIRECRAWL_CLIENT = AsyncFirecrawlApp(api_key=FIRECRAWL_API_KEY)

if SEARCH_PROVIDER == "exa":
    if not EXA_API_KEY: logger.error("EXA_API_KEY not configured for Exa search provider.")
    else: EXA_CLIENT = Exa(api_key=EXA_API_KEY)
elif SEARCH_PROVIDER == "perplexity":
    if not PERPLEXITY_API_KEY: logger.error("PERPLEXITY_API_KEY not configured for Perplexity search provider.")
else:
    logger.error(f"Unsupported COMPETITOR_SEARCH_PROVIDER: {SEARCH_PROVIDER}. Use 'exa' or 'perplexity'.")

if not GOOGLE_API_KEY:
    logger.warning("GOOGLE_API_KEY not configured. Gemini analysis will be skipped.")
else:
    try:
        genai.configure(api_key=GOOGLE_API_KEY)
        GEMINI_MODEL = genai.GenerativeModel(
            settings.GEMINI_MODEL_NAME, # Use model from settings
            generation_config=genai.types.GenerationConfig(temperature=0.5, response_mime_type="application/json")
        )
        logger.info(f"Gemini client configured successfully using model: {settings.GEMINI_MODEL_NAME}")
    except Exception as e:
        logger.error(f"Failed to configure Gemini client: {e}", exc_info=True)

# --- Pydantic Models (Keep as they define data structures) ---
class MarketResearchInput(BaseModel):
    initial_topic: str = Field(description="A keyword, domain, or description defining the area of interest.")
    target_url: Optional[HttpUrl] = Field(None, description="Optional URL of the user's company for comparison.")
    num_competitors: int = Field(3, description="Number of competitors to find and analyze.")

class CompetitorInfo(BaseModel):
    competitor_url: HttpUrl
    company_name: Optional[str] = None
    pricing: Optional[str] = None
    key_features: List[str] = []
    tech_stack: List[str] = []
    marketing_focus: Optional[str] = None
    customer_feedback: Optional[str] = None

class MarketAnalysis(BaseModel):
    market_gaps: List[str] = Field(description="Identified gaps or unmet needs in the market.")
    opportunities: List[str] = Field(description="Potential opportunities based on competitor weaknesses or market trends.")
    competitor_weaknesses: List[str] = Field(description="Specific weaknesses observed in competitors.")
    pricing_strategies: List[str] = Field(description="Observations or suggestions regarding pricing.")
    positioning_strategies: List[str] = Field(description="Observations or suggestions regarding market positioning.")

class MarketOpportunityReport(BaseModel):
    competitors: List[CompetitorInfo] = Field(description="List of identified competitors and their extracted data.")
    analysis: MarketAnalysis = Field(description="Structured analysis of the market, competitors, and opportunities.")
    feature_recommendations: List[str] = Field(description="List of potential features to consider based on the analysis.")
    target_audience_suggestions: List[str] = Field(description="Suggestions for potential target demographics or niches.")

class FirecrawlExtractSchema(BaseModel):
    company_name: str = Field(description="Name of the company")
    pricing: str = Field(description="Pricing details, tiers, and plans")
    key_features: List[str] = Field(description="Main features and capabilities of the product/service")
    tech_stack: List[str] = Field(description="Technologies, frameworks, and tools used")
    marketing_focus: str = Field(description="Main marketing angles and target audience")
    customer_feedback: str = Field(description="Customer testimonials, reviews, and feedback")

# --- Helper Functions (Standalone) ---

async def _find_competitor_urls_exa(topic: str, target_url: Optional[str], num_results: int) -> List[str]:
    """Helper: Finds competitor URLs using Exa asynchronously."""
    if not EXA_CLIENT: raise ValueError("Exa client not initialized.")
    try:
        logger.info(f"Helper: Searching Exa for topic/URL: {topic or target_url}")
        loop = asyncio.get_running_loop()
        if target_url:
            result = await loop.run_in_executor(None, lambda: EXA_CLIENT.find_similar(url=target_url, num_results=num_results, exclude_source_domain=True, category="company"))
        else:
            result = await loop.run_in_executor(None, lambda: EXA_CLIENT.search(topic, type="neural", category="company", use_autoprompt=True, num_results=num_results))
        urls = [item.url for item in result.results]
        logger.info(f"Helper: Exa found URLs: {urls}")
        return urls
    except Exception as e:
        logger.error(f"Helper: Error fetching competitor URLs from Exa: {str(e)}", exc_info=True)
        return []

async def _find_competitor_urls_perplexity(topic: str, target_url: Optional[str], num_results: int) -> List[str]:
    """Helper: Finds competitor URLs using Perplexity asynchronously."""
    if not PERPLEXITY_API_KEY: raise ValueError("Perplexity API key not configured.")
    perplexity_url = "https://api.perplexity.ai/chat/completions"
    content = f"Find me {num_results} competitor company URLs "
    if target_url and topic: content += f"similar to the company with URL '{target_url}' and description '{topic}'"
    elif target_url: content += f"similar to the company with URL: {target_url}"
    else: content += f"related to the topic: {topic}"
    content += ". ONLY RESPOND WITH THE URLS, each on a new line, NO OTHER TEXT."
    logger.info("Helper: Querying Perplexity API...")
    payload = {"model": "sonar-large-32k-online", "messages": [{"role": "system", "content": f"You are an assistant that finds competitor websites. Only return {num_results} company URLs, each on a new line."}, {"role": "user", "content": content}], "max_tokens": 1000, "temperature": 0.1}
    headers = {"Authorization": f"Bearer {PERPLEXITY_API_KEY}", "Content-Type": "application/json", "Accept": "application/json"}
    try:
        response = await HTTP_CLIENT.post(perplexity_url, json=payload, headers=headers) # Use global client
        response.raise_for_status()
        response_data = response.json()
        message_content = response_data.get('choices', [{}])[0].get('message', {}).get('content', '')
        urls = [url.strip() for url in message_content.strip().split('\n') if url.strip().startswith('http')]
        logger.info(f"Helper: Perplexity found URLs: {urls}")
        return urls[:num_results]
    except Exception as e:
        logger.error(f"Helper: Error processing Perplexity response: {str(e)}", exc_info=True)
        return []

async def _extract_competitor_info(competitor_url: str) -> Optional[CompetitorInfo]:
    """Helper: Extracts structured data from a competitor URL using AsyncFirecrawlApp."""
    if not FIRECRAWL_CLIENT: raise ValueError("Firecrawl client not initialized.")
    logger.info(f"Helper: Extracting data from URL: {competitor_url}")
    try:
        extraction_prompt = f"Extract detailed information about the company from its website ({competitor_url}), focusing on: Company name, Pricing, Key features, Tech stack, Marketing focus, Customer feedback. Analyze the website content. If info isn't found, indicate 'N/A'."
        response = await FIRECRAWL_CLIENT.extract(
            url=competitor_url,
            params={'extractorOptions': {'mode': 'llm-extraction', 'extractionPrompt': extraction_prompt, 'extractionSchema': FirecrawlExtractSchema.model_json_schema()}, 'pageOptions': {'onlyMainContent': True}},
            timeout=60
        )
        if response and isinstance(response, dict) and response.get('data'):
            extracted_data = response['data']
            info = CompetitorInfo(competitor_url=competitor_url, **extracted_data)
            logger.info(f"Helper: Successfully extracted data for {competitor_url}")
            return info
        else:
             logger.warning(f"Helper: Firecrawl extraction did not return valid data for {competitor_url}. Response: {response}")
             return None
    except (ValidationError, TypeError) as e:
         logger.error(f"Helper: Pydantic validation error for {competitor_url}: {e}", exc_info=True)
         return None
    except Exception as e:
        logger.error(f"Helper: Error extracting data from {competitor_url}: {str(e)}", exc_info=True)
        return None

async def _generate_analysis(competitors_data: List[CompetitorInfo], topic: str) -> Dict[str, Any]:
    """Helper: Generate analysis using Gemini."""
    if not GEMINI_MODEL:
        logger.warning("Helper: Gemini model not available for analysis.")
        return {"analysis": {}, "feature_recommendations": [], "target_audience_suggestions": []}
    try:
        competitors_json = json.dumps([c.model_dump(exclude_none=True) for c in competitors_data], indent=2)
        prompt = f"""Analyze the market research data for competitors in the {topic} niche. Generate a JSON report summarizing findings and insights.

Competitor Data: ```json\n{competitors_json}\n```

Generate a JSON object containing:
1. 'analysis': {{ 'market_gaps': [], 'opportunities': [], 'competitor_weaknesses': [], 'pricing_strategies': [], 'positioning_strategies': [] }} (each a list of strings).
2. 'feature_recommendations': List of strings.
3. 'target_audience_suggestions': List of strings.

Output ONLY the valid JSON object. Example: {{"analysis": {{"market_gaps": ["Gap..."], ...}}, "feature_recommendations": ["Feature..."], ...}}
"""
        response = await GEMINI_MODEL.generate_content_async(prompt)
        response_text = response.text
        try:
            # Attempt to parse directly, then try extracting from markdown
            analysis = json.loads(response_text)
        except json.JSONDecodeError:
            import re
            json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
            if json_match: analysis = json.loads(json_match.group(1))
            else: raise ValueError("No JSON found in Gemini response")
        # Basic validation
        if not isinstance(analysis.get("analysis"), dict) or \
           not isinstance(analysis.get("feature_recommendations"), list) or \
           not isinstance(analysis.get("target_audience_suggestions"), list):
            raise ValueError("Gemini response structure invalid.")
        logger.info("Helper: Successfully generated analysis from Gemini.")
        return analysis
    except Exception as e:
        logger.error(f"Helper: Error generating analysis: {e}", exc_info=True)
        # Return empty structure on error
        return {"analysis": {}, "feature_recommendations": [], "target_audience_suggestions": []}

# --- ADK Tool Definitions ---

@tool(description="Perform market research: find competitors, extract data, analyze market.")
async def research_market_tool(
    topic: str,
    target_url: Optional[str] = None,
    num_competitors: int = 3
) -> Dict[str, Any]:
    """
    ADK Tool: Performs market research for a given niche or product.
    Returns a MarketOpportunityReport or an error dictionary.
    """
    logger.info(f"Tool: Researching market for '{topic}' (Target: {target_url}, Competitors: {num_competitors})")
    try:
        # Validate essential clients
        if not FIRECRAWL_CLIENT or not (EXA_CLIENT or PERPLEXITY_API_KEY):
            return {"success": False, "error": "Required clients (Firecrawl, Exa/Perplexity) not initialized."}

        # Find competitor URLs
        if SEARCH_PROVIDER == "exa":
            competitor_urls = await _find_competitor_urls_exa(topic, target_url, num_competitors)
        elif SEARCH_PROVIDER == "perplexity":
            competitor_urls = await _find_competitor_urls_perplexity(topic, target_url, num_competitors)
        else: # Should not happen if validation passed, but defensive check
             return {"success": False, "error": f"Invalid search provider configured: {SEARCH_PROVIDER}"}

        if not competitor_urls:
            return {"success": False, "message": "No competitor URLs found.", "competitors": [], "analysis": {}, "feature_recommendations": [], "target_audience_suggestions": []}

        # Extract data
        extraction_tasks = [_extract_competitor_info(url) for url in competitor_urls]
        results = await asyncio.gather(*extraction_tasks, return_exceptions=True)
        competitors_data = [res for res in results if isinstance(res, CompetitorInfo)]
        errors = [str(res) for res in results if not isinstance(res, CompetitorInfo)]
        if errors: logger.warning(f"Tool: Errors during extraction: {errors}")
        if not competitors_data:
            return {"success": False, "message": "Could not extract data from any competitors.", "competitor_urls_found": competitor_urls, "extraction_errors": errors}

        # Generate analysis
        analysis_data = await _generate_analysis(competitors_data, topic)

        # Construct final report using Pydantic model for validation
        report = MarketOpportunityReport(
            competitors=competitors_data,
            analysis=analysis_data.get("analysis", {}), # Use empty dict as default
            feature_recommendations=analysis_data.get("feature_recommendations", []),
            target_audience_suggestions=analysis_data.get("target_audience_suggestions", [])
        )

        logger.info(f"Tool: Market research completed for '{topic}'.")
        return {"success": True, "report": report.model_dump(exclude_none=True)}

    except Exception as e:
        logger.error(f"Tool: Error performing market research: {e}", exc_info=True)
        return {"success": False, "error": f"Error performing market research: {str(e)}"}

@tool(description="Analyze competitors in a given niche by extracting data from their websites.")
async def analyze_competitors_tool(topic: str, max_competitors: int = 5) -> Dict[str, Any]:
    """
    ADK Tool: Analyzes competitors in a given niche.
    Returns a list of competitor info or an error dictionary.
    """
    logger.info(f"Tool: Analyzing competitors for '{topic}' (max: {max_competitors})")
    try:
        # Validate essential clients
        if not FIRECRAWL_CLIENT or not (EXA_CLIENT or PERPLEXITY_API_KEY):
            return {"success": False, "error": "Required clients (Firecrawl, Exa/Perplexity) not initialized."}

        # Find competitor URLs
        if SEARCH_PROVIDER == "exa":
            competitor_urls = await _find_competitor_urls_exa(topic, None, max_competitors)
        elif SEARCH_PROVIDER == "perplexity":
            competitor_urls = await _find_competitor_urls_perplexity(topic, None, max_competitors)
        else:
             return {"success": False, "error": f"Invalid search provider configured: {SEARCH_PROVIDER}"}

        if not competitor_urls:
            return {"success": False, "message": "No competitor URLs found.", "competitors": []}

        # Extract data
        extraction_tasks = [_extract_competitor_info(url) for url in competitor_urls]
        results = await asyncio.gather(*extraction_tasks, return_exceptions=True)
        competitors_data = [res for res in results if isinstance(res, CompetitorInfo)]
        errors = [str(res) for res in results if not isinstance(res, CompetitorInfo)]
        if errors: logger.warning(f"Tool: Errors during extraction: {errors}")

        if not competitors_data:
            return {"success": False, "message": "Could not extract data from any competitors.", "competitor_urls_found": competitor_urls, "extraction_errors": errors}

        logger.info(f"Tool: Competitor analysis completed for '{topic}'.")
        return {"success": True, "competitors": [c.model_dump(exclude_none=True) for c in competitors_data]}

    except Exception as e:
        logger.error(f"Tool: Error analyzing competitors: {e}", exc_info=True)
        return {"success": False, "error": f"Error analyzing competitors: {str(e)}"}


# --- Instantiate the ADK Agent ---
agent = Agent(
    name=AGENT_ID,
    description="Performs market research using Exa/Perplexity, Firecrawl, and Gemini.",
    tools=[
        research_market_tool,
        analyze_competitors_tool,
    ],
)

# Removed A2A server specific code and old class structure
