import json
import logging
import random
import time
import asyncio
import os # Added for environment variables
import argparse # Added for server args
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

import httpx # Added for APIClient
import uvicorn # Added for server
from fastapi import FastAPI, HTTPException, Body # Added for server
from pydantic import BaseModel, Field # Added for server models

# Assuming ADK is installed
from google.adk.agents import Agent, AgentError # Removed AgentConfig as we use env vars
from google.adk.runtime import InvocationContext, Event

# Configure logging
# Use logfire if configured globally, otherwise standard logging
try:
    import logfire
    logger = logfire
except ImportError:
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO"))

# --- Reusable API Client (Adapted from backend.utils.api_client) ---
# Including it here for simplicity, could be kept separate
class APIError(Exception):
    """Custom exception for API client errors."""
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        super().__init__(f"API Error {status_code}: {message}")

class APIClient:
    """Simple asynchronous HTTP client for interacting with an API."""
    def __init__(self, base_url: str, api_key: Optional[str] = None, default_timeout: float = 15.0):
        if not base_url:
            raise ValueError("API base_url cannot be empty.")
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.default_timeout = default_timeout
        headers = {"Accept": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}" # Common pattern, adjust if needed
        self._client = httpx.AsyncClient(base_url=self.base_url, headers=headers, timeout=self.default_timeout)
        logger.info(f"APIClient initialized for base URL: {self.base_url}")

    async def get(self, endpoint: str, params: Optional[Dict] = None) -> Any:
        """Perform a GET request."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        logger.debug(f"GET request to: {url} with params: {params}")
        try:
            response = await self._client.get(endpoint, params=params)
            response.raise_for_status() # Raise HTTPStatusError for 4xx/5xx
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error on GET {url}: {e.response.status_code} - {e.response.text}")
            raise APIError(e.response.status_code, e.response.text) from e
        except httpx.RequestError as e:
            logger.error(f"Request error on GET {url}: {e}")
            raise APIError(500, f"Request failed: {e}") from e
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode JSON response from GET {url}: {e}")
            raise APIError(500, f"Invalid JSON response: {e}") from e

    async def close(self):
        """Close the underlying httpx client."""
        if not self._client.is_closed:
            await self._client.aclose()
            logger.info("APIClient httpx client closed.")

# --- Pydantic Models for FastAPI ---

class MarketAnalysisInput(BaseModel):
    """Input model for the /invoke endpoint."""
    action: str = Field(description="Analysis action (e.g., 'analyze_trends', 'identify_opportunities', 'evaluate_competition', 'analyze_keywords').")
    # Optional fields used by different actions
    niche: Optional[str] = Field("technology", description="The niche or topic for analysis.")
    depth: Optional[str] = Field("standard", description="Depth of trend analysis ('standard' or 'deep').")
    niches: Optional[List[str]] = Field(None, description="List of niches for opportunity identification.")
    business_type: Optional[str] = Field("affiliate_marketing", description="Business type for competition evaluation.")
    limit: Optional[int] = Field(10, description="Limit for keyword analysis.")

# Output can be dynamic based on the action's results
class MarketAnalysisOutput(BaseModel):
    """Generic output model, actual content depends on the action."""
    task_id: str
    action: str
    input_params: Dict[str, Any]
    results: Any # Can be Dict or List[Dict]
    success: bool
    timestamp: str
    error: Optional[str] = None # Include error message if success is False

# --- Agent Class ---

class MarketAnalysisAgent(Agent):
    """
    ADK-compliant agent that analyzes market trends, identifies opportunities,
    evaluates competition, and analyzes keywords based on input requests.
    Uses A2A server structure and environment variables for config.
    """
    ENV_MARKET_API_BASE_URL = "MARKET_DATA_API_BASE_URL"
    ENV_MARKET_API_KEY = "MARKET_DATA_API_KEY"

    def __init__(self, agent_id: str = "market-analysis-agent"):
        """Initialize the Market Analysis Agent."""
        super().__init__(agent_id=agent_id)
        logger.info(f"Initializing MarketAnalysisAgent ({self.agent_id})...")
        self.cached_data = {} # Simple instance cache
        self.last_analysis = {} # Instance state

        # Initialize API Client using environment variables
        base_url = os.environ.get(self.ENV_MARKET_API_BASE_URL)
        api_key = os.environ.get(self.ENV_MARKET_API_KEY)

        self.market_api_client = None
        if base_url:
            try:
                self.market_api_client = APIClient(base_url=base_url, api_key=api_key)
                logger.info(f"Market Analysis Agent [{self.agent_id}] initialized with API client for URL: {base_url}")
            except ValueError as e:
                 logger.error(f"Configuration error for Market Analysis Agent [{self.agent_id}]: {e}. API client not initialized.")
            except Exception as e:
                 logger.error(f"Unexpected error initializing API client: {e}", exc_info=True)
        else:
            logger.warning(f"{self.ENV_MARKET_API_BASE_URL} not set. Real market data fetching disabled.")


    async def run_async(self, context: InvocationContext) -> Event:
        """Execute a market analysis task based on the invocation context data."""
        logger.info(f"Market Analysis Agent [{self.agent_id}] received task for invocation: {context.invocation_id}")
        action = "unknown" # Default for error reporting
        input_params = {}

        try:
            if not isinstance(context.data, dict):
                raise ValueError("Input data must be a dictionary.")
            input_params = context.data # Store for event payload
            action = input_params.get("action")
            if not action:
                raise ValueError("Missing 'action' in input data.")

            results: Any = None
            event_type: str = f"market.{action}.failed" # Default to failure

            # Use asyncio.to_thread for synchronous helper methods
            loop = asyncio.get_running_loop()

            if action == "analyze_trends":
                niche = input_params.get("niche", "technology")
                depth = input_params.get("depth", "standard")
                results = await self.analyze_trends(niche, depth) # analyze_trends is now async
                event_type = f"market.trends.analyzed"

            elif action == "identify_opportunities":
                niches = input_params.get("niches")
                results = await self.identify_opportunities(niches) # identify_opportunities is now async
                event_type = f"market.opportunities.identified"

            elif action == "evaluate_competition":
                niche = input_params.get("niche", "technology")
                business_type = input_params.get("business_type", "affiliate_marketing")
                # Run sync helper in thread
                results = await loop.run_in_executor(
                    None, self._evaluate_competition_sync, niche, business_type
                )
                event_type = f"market.competition.evaluated"

            elif action == "analyze_keywords":
                niche = input_params.get("niche", "technology")
                limit = input_params.get("limit", 10)
                 # Run sync helper in thread
                results = await loop.run_in_executor(
                    None, self._analyze_keywords_sync, niche, limit
                )
                event_type = f"market.keywords.analyzed"

            else:
                raise ValueError(f"Unknown action: {action}")

            # Return success event using context helper
            return context.create_event(
                event_type=event_type,
                data={
                    "task_id": context.invocation_id, "action": action,
                    "input_params": input_params, "results": results,
                    "success": True, "timestamp": datetime.now().isoformat()
                },
                metadata={"status": "success"}
            )

        except (APIError, ValueError, TypeError, Exception) as e:
            logger.error(f"Market Analysis Agent [{self.agent_id}] error processing action '{action}': {e}", exc_info=True)
            # Return error event using context helper
            return context.create_event(
                event_type=f"market.{action or 'task'}.failed",
                data={
                    "task_id": context.invocation_id, "action": action,
                    "input_params": input_params, "success": False,
                    "error": f"{type(e).__name__}: {e}",
                    "timestamp": datetime.now().isoformat()
                },
                metadata={"status": "error"}
            )

    # --- Analysis Methods (Adapted from Prototype) ---

    async def fetch_trend_data(self, niche: str) -> Optional[Dict[str, Any]]:
        """Fetch real trend data from market data API."""
        if not self.market_api_client:
            logger.warning(f"Market API client not initialized for niche: {niche}. Cannot fetch real data.")
            return None
        try:
            endpoint = f"trends/{niche}" # Adjust endpoint as needed
            logger.info(f"Attempting to fetch real trend data for {niche} from {endpoint}")
            response = await self.market_api_client.get(endpoint)
            if response and isinstance(response, dict) and 'trends' in response:
                logger.info(f"Successfully fetched real trend data for {niche}")
                return response['trends']
            else:
                logger.warning(f"Invalid or missing 'trends' data in API response for {niche}: {response}")
                return None
        except APIError as e:
            logger.warning(f"Market data API error fetching trends for {niche}: {e}")
        except Exception as e:
            logger.warning(f"Unexpected error fetching market data for {niche}: {e}", exc_info=True)
        return None

    async def analyze_trends(self, niche: str, depth: str = "standard") -> Dict[str, Any]:
        """Analyze trends in a specific niche. (Async version)"""
        logger.info(f"Analyzing {depth} trends for {niche} niche")
        cache_key = f"{niche}_{depth}"
        current_time = datetime.now().timestamp()
        if cache_key in self.cached_data and (current_time - self.cached_data[cache_key]["timestamp"] < 3600):
            logger.info(f"Using cached trend data for {niche}")
            return self.cached_data[cache_key]["data"]

        real_data = await self.fetch_trend_data(niche)
        if real_data:
            logger.info(f"Using fetched real trend data for {niche}")
            # Run sync processing in thread
            analysis_results = await asyncio.to_thread(
                self._process_real_trend_data, real_data, niche, depth
            )
        else:
            logger.info(f"Falling back to mock trend data generation for {niche}")
            # Run sync generation in thread
            analysis_results = await asyncio.to_thread(
                self._generate_trend_data, niche, depth
            )

        self.cached_data[cache_key] = {"timestamp": current_time, "data": analysis_results}
        self.last_analysis = {"niche": niche, "depth": depth, "timestamp": datetime.now().isoformat(), "results": analysis_results}
        return analysis_results

    def _process_real_trend_data(self, real_data: Dict[str, Any], niche: str, depth: str) -> Dict[str, Any]:
        """Synchronous helper to process/enhance real data."""
        logger.info(f"Processing real trend data for {niche} (depth: {depth}) (sync)")
        processed_data = real_data.copy()
        processed_data["niche"] = niche
        processed_data["analysis_depth"] = depth
        processed_data["timestamp"] = datetime.now().isoformat()
        processed_data["data_source"] = "api"
        if depth == "deep":
            if "demographics" not in processed_data: processed_data["demographics"] = self._generate_demographics(niche)
            if "competitive_landscape" not in processed_data: processed_data["competitive_landscape"] = self._generate_competitive_landscape(niche)
            if "pricing_analysis" not in processed_data: processed_data["pricing_analysis"] = self._generate_pricing_analysis(niche)
        return processed_data

    async def identify_opportunities(self, niches: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Identify business opportunities across multiple niches. (Async)"""
        default_niches = ["technology", "health", "finance", "education", "e-commerce", "sustainability", "productivity"]
        niches_to_analyze = niches or default_niches
        logger.info(f"Identifying opportunities across {len(niches_to_analyze)} niches: {niches_to_analyze}")
        opportunities = []
        trend_analysis_tasks = [self.analyze_trends(niche) for niche in niches_to_analyze]
        trend_results_list = await asyncio.gather(*trend_analysis_tasks)

        # Run synchronous extraction part in thread pool
        loop = asyncio.get_running_loop()
        extraction_tasks = []
        for niche, trends in zip(niches_to_analyze, trend_results_list):
            if trends:
                extraction_tasks.append(
                    loop.run_in_executor(None, self._extract_opportunities, niche, trends)
                )
            else:
                logger.warning(f"Could not analyze trends for niche '{niche}', skipping opportunity identification.")

        niche_opportunities_list = await asyncio.gather(*extraction_tasks)
        for niche_ops in niche_opportunities_list:
            opportunities.extend(niche_ops)

        opportunities.sort(key=lambda x: x.get("potential_revenue", 0), reverse=True)
        logger.info(f"Identified {len(opportunities)} opportunities.")
        return opportunities

    # --- Synchronous Helpers (Keep original logic, but rename to indicate sync) ---
    # These will be called via asyncio.to_thread

    def _evaluate_competition_sync(self, niche: str, business_type: str) -> Dict[str, Any]:
        """Synchronous helper to evaluate competition."""
        logger.info(f"Evaluating competition for {business_type} in {niche} niche (sync)")
        competition_levels = {
            "technology": {"affiliate_marketing": 8, "digital_product": 7, "saas": 9},
            "health": {"affiliate_marketing": 9, "digital_product": 8, "saas": 6},
            # ... (rest of competition_levels map) ...
             "sustainability": {"affiliate_marketing": 5, "digital_product": 6, "saas": 7},
             "productivity": {"affiliate_marketing": 7, "digital_product": 7, "saas": 8}
        }
        competition_level = competition_levels.get(niche, {}).get(business_type, 7)
        competitors = self._generate_competitors(niche, business_type)
        return {
            "niche": niche, "business_type": business_type,
            "competition_level": competition_level,
            "saturation": self._calculate_saturation(competition_level),
            "top_competitors": competitors,
            "entry_barriers": self._generate_entry_barriers(niche, business_type),
            "timestamp": datetime.now().isoformat()
        }

    def _analyze_keywords_sync(self, niche: str, limit: int = 10) -> Dict[str, Any]:
        """Synchronous helper to analyze keywords."""
        logger.info(f"Analyzing keywords for {niche} niche (limit: {limit}) (sync)")
        keywords = self._generate_keywords(niche)
        top_keywords = keywords[:limit]
        if not top_keywords: avg_competition = 0
        else: avg_competition = sum(k.get("competition", 0) for k in top_keywords) / len(top_keywords)
        return {
            "niche": niche, "keywords": top_keywords,
            "search_volume_total": sum(k.get("search_volume", 0) for k in top_keywords),
            "competition_average": round(avg_competition, 2),
            "timestamp": datetime.now().isoformat()
        }

    def _generate_trend_data(self, niche: str, depth: str) -> Dict[str, Any]:
        """Generate mock trend data (sync)."""
        # (Content identical to prototype _generate_trend_data method)
        trend_data = {
            "technology": {"growing_segments": ["AI tools", "no-code platforms", "cybersecurity"], "declining_segments": ["mobile apps", "general web hosting"], "growth_rate": 12.5, "sentiment": 8.2},
            "health": {"growing_segments": ["mental wellness", "home fitness", "nutrition tracking"], "declining_segments": ["general supplements", "diet programs"], "growth_rate": 9.8, "sentiment": 7.5},
            "finance": {"growing_segments": ["crypto education", "financial literacy", "passive income"], "declining_segments": ["day trading courses", "general investing"], "growth_rate": 7.2, "sentiment": 6.8},
            "education": {"growing_segments": ["skill certifications", "cohort courses", "specialized tutorials"], "declining_segments": ["general e-books", "broad courses"], "growth_rate": 14.3, "sentiment": 8.7},
            "e-commerce": {"growing_segments": ["niche marketplaces", "subscription boxes", "sustainable products"], "declining_segments": ["general dropshipping", "print on demand"], "growth_rate": 8.5, "sentiment": 7.1},
            "sustainability": {"growing_segments": ["zero waste products", "sustainable fashion", "eco-education"], "declining_segments": ["general green blogs", "carbon offsetting"], "growth_rate": 15.7, "sentiment": 8.9},
            "productivity": {"growing_segments": ["AI assistants", "focus tools", "knowledge management"], "declining_segments": ["general productivity apps", "time tracking"], "growth_rate": 11.2, "sentiment": 7.8}
        }
        base_data = trend_data.get(niche, trend_data["technology"]).copy()
        if depth == "deep":
            base_data["demographics"] = self._generate_demographics(niche)
            base_data["growing_segments"].extend(self._generate_additional_segments(niche, True))
            base_data["declining_segments"].extend(self._generate_additional_segments(niche, False))
            base_data["competitive_landscape"] = self._generate_competitive_landscape(niche)
            base_data["pricing_analysis"] = self._generate_pricing_analysis(niche)
        base_data["niche"] = niche
        base_data["analysis_depth"] = depth
        base_data["timestamp"] = datetime.now().isoformat()
        base_data["data_source"] = "mock"
        return base_data

    def _extract_opportunities(self, niche: str, trends: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract mock business opportunities (sync)."""
        # (Content identical to prototype _extract_opportunities method)
        opportunities = []
        for segment in trends.get("growing_segments", []):
            business_type = self._determine_business_type(segment, niche)
            growth_rate = trends.get("growth_rate", 10.0)
            base_revenue = random.randint(1000, 5000)
            potential_revenue = int(base_revenue * (1 + growth_rate / 100))
            difficulty = self._generate_difficulty(segment, niche)
            risk_level = self._determine_risk_level(difficulty, potential_revenue)
            opportunity = {
                "name": f"{segment} {business_type.replace('_', ' ').title()}", "type": business_type, "niche": niche,
                "segment": segment, "potential_revenue": potential_revenue, "implementation_difficulty": difficulty,
                "market_saturation": self._calculate_saturation(difficulty), "risk_level": risk_level
            }
            opportunities.append(opportunity)
        return opportunities

    def _determine_business_type(self, segment: str, niche: str) -> str:
        """Determine mock business type (sync)."""
        # (Content identical to prototype _determine_business_type method)
        segment_types = {
            "AI tools": "saas", "no-code platforms": "saas", "cybersecurity": "digital_product",
            "mental wellness": "digital_product", "home fitness": "digital_product", "nutrition tracking": "saas",
            "crypto education": "digital_product", "financial literacy": "digital_product", "passive income": "affiliate_marketing",
            "skill certifications": "digital_product", "cohort courses": "digital_product", "specialized tutorials": "digital_product",
            "niche marketplaces": "e-commerce", "subscription boxes": "e-commerce", "sustainable products": "e-commerce",
            "zero waste products": "e-commerce", "sustainable fashion": "e-commerce", "eco-education": "digital_product",
            "AI assistants": "saas", "focus tools": "saas", "knowledge management": "saas"
        }
        if segment in segment_types: return segment_types[segment]
        else:
            if niche in ["technology", "productivity"]: return random.choice(["saas", "digital_product"])
            if niche == "e-commerce": return "e-commerce"
            if niche == "finance": return random.choice(["affiliate_marketing", "digital_product"])
            return random.choice(["affiliate_marketing", "digital_product", "saas", "e-commerce"])

    def _generate_difficulty(self, segment: str, niche: str) -> int:
        """Generate mock difficulty score (sync)."""
        # (Content identical to prototype _generate_difficulty method)
        base_difficulties = {"affiliate_marketing": 5, "digital_product": 7, "saas": 9, "e-commerce": 6}
        business_type = self._determine_business_type(segment, niche)
        base = base_difficulties.get(business_type, 7)
        variation = random.randint(-1, 1)
        return max(1, min(10, base + variation))

    def _determine_risk_level(self, difficulty: int, revenue: int) -> str:
        """Determine mock risk level (sync)."""
        # (Content identical to prototype _determine_risk_level method)
        risk_score = difficulty - (revenue / 1000)
        if risk_score > 5: return "high"
        elif risk_score > 2: return "medium"
        else: return "low"

    def _calculate_saturation(self, competition_level: int) -> int:
        """Calculate mock market saturation (sync)."""
        # (Content identical to prototype _calculate_saturation method)
        variation = random.randint(-1, 1)
        return max(1, min(10, competition_level + variation))

    def _generate_competitors(self, niche: str, business_type: str) -> List[Dict[str, Any]]:
        """Generate mock competitors (sync)."""
        # (Content identical to prototype _generate_competitors method)
        num_competitors = random.randint(3, 5)
        competitors = []
        for i in range(num_competitors):
            name = self._generate_competitor_name(niche, business_type)
            market_share = round(random.uniform(5.0, 25.0), 1)
            monthly_revenue = random.randint(5000, 50000)
            competitors.append({"name": name, "market_share": market_share, "monthly_revenue": monthly_revenue, "years_active": random.randint(1, 10)})
        competitors.sort(key=lambda x: x["market_share"], reverse=True)
        return competitors

    def _generate_competitor_name(self, niche: str, business_type: str) -> str:
        """Generate mock competitor name (sync)."""
        # (Content identical to prototype _generate_competitor_name method)
        prefixes = {"technology": ["Tech", "Digital", "Cyber", "Code", "Dev"], "health": ["Health", "Vital", "Wellness", "Fit", "Nutri"], "finance": ["Finance", "Money", "Wealth", "Capital", "Invest"], "education": ["Learn", "Edu", "Skill", "Academy", "Master"], "e-commerce": ["Shop", "Store", "Market", "Buy", "Retail"], "sustainability": ["Eco", "Green", "Sustain", "Earth", "Bio"], "productivity": ["Focus", "Task", "Time", "Boost", "Flow"]}
        suffixes = {"affiliate_marketing": ["Affiliate", "Partner", "Promote", "Refer", "Link"], "digital_product": ["Course", "Guide", "Academy", "School", "Learn"], "saas": ["App", "Tool", "Suite", "Cloud", "Platform"], "e-commerce": ["Shop", "Store", "Market", "Goods", "Products"]}
        prefix = random.choice(prefixes.get(niche, ["Brand"]))
        suffix = random.choice(suffixes.get(business_type, ["Pro"]))
        return f"{prefix}{suffix}"

    def _generate_entry_barriers(self, niche: str, business_type: str) -> List[str]:
        """Generate mock entry barriers (sync)."""
        # (Content identical to prototype _generate_entry_barriers method)
        common_barriers = ["High initial investment", "Technical expertise required", "Established brand loyalty", "Complex regulations", "Network effects favoring incumbents", "High customer acquisition costs", "Intellectual property protections", "Economies of scale"]
        specific_barriers = {"affiliate_marketing": ["Saturated affiliate networks", "Commission rate competition", "Cookie duration limitations"], "digital_product": ["Content creation expertise", "High-quality production requirements", "Platform fees and restrictions"], "saas": ["Development costs", "Ongoing maintenance requirements", "User onboarding complexity"], "e-commerce": ["Inventory management", "Shipping logistics", "Return handling costs"]}
        selected_barriers = random.sample(common_barriers, random.randint(2, 3))
        if business_type in specific_barriers:
            specific_list = specific_barriers[business_type]
            num_specific = min(len(specific_list), random.randint(1, 2))
            selected_barriers.extend(random.sample(specific_list, num_specific))
        return selected_barriers

    def _generate_demographics(self, niche: str) -> Dict[str, Any]:
        """Generate mock audience demographics (sync)."""
        # (Content identical to prototype _generate_demographics method)
        default_demographics = {"age_groups": {"18-24": 15, "25-34": 30, "35-44": 25, "45-54": 15, "55+": 15}, "gender_split": {"male": 55, "female": 45}, "income_levels": {"low": 20, "medium": 50, "high": 30}, "education_levels": {"high_school": 25, "bachelors": 45, "masters": 20, "phd": 10}}
        niche_demographics = {"technology": {"age_groups": {"18-24": 20, "25-34": 35, "35-44": 25, "45-54": 15, "55+": 5}, "gender_split": {"male": 65, "female": 35}}, "health": {"age_groups": {"18-24": 15, "25-34": 30, "35-44": 25, "45-54": 20, "55+": 10}, "gender_split": {"male": 40, "female": 60}}, "finance": {"age_groups": {"18-24": 10, "25-34": 25, "35-44": 30, "45-54": 20, "55+": 15}, "income_levels": {"low": 15, "medium": 45, "high": 40}}}
        demographics = default_demographics.copy()
        if niche in niche_demographics:
            for key, value in niche_demographics[niche].items(): demographics[key] = value.copy() if isinstance(value, dict) else value
        return demographics

    def _generate_additional_segments(self, niche: str, growing: bool) -> List[str]:
        """Generate mock additional market segments (sync)."""
        # (Content identical to prototype _generate_additional_segments method)
        additional_segments = {"technology": {"growing": ["AR/VR solutions", "blockchain applications", "edge computing"], "declining": ["traditional CMS", "on-premise software", "generic mobile apps"]}, "health": {"growing": ["personalized nutrition", "sleep optimization", "biohacking"], "declining": ["general fitness apps", "generic meal plans", "broad supplements"]}, "finance": {"growing": ["DeFi education", "sustainable investing", "financial independence"], "declining": ["traditional stock picking", "general budgeting", "forex trading"]}, "education": {"growing": ["microlearning", "community-based learning", "AI-assisted education"], "declining": ["general online courses", "static e-books", "non-interactive content"]}}
        niche_segments = additional_segments.get(niche, {})
        segment_type = "growing" if growing else "declining"
        return niche_segments.get(segment_type, [])

    def _generate_competitive_landscape(self, niche: str) -> Dict[str, Any]:
        """Generate mock competitive landscape (sync)."""
        # (Content identical to prototype _generate_competitive_landscape method)
        return {"total_competitors": random.randint(50, 200), "market_leaders": random.randint(5, 15), "new_entrants_monthly": random.randint(3, 12), "average_lifespan": f"{random.randint(2, 5)} years", "consolidation_trend": random.choice(["increasing", "stable", "decreasing"])}

    def _generate_pricing_analysis(self, niche: str) -> Dict[str, Any]:
        """Generate mock pricing analysis (sync)."""
        # (Content identical to prototype _generate_pricing_analysis method)
        return {"average_price_point": f"${random.randint(20, 100)}", "price_sensitivity": random.randint(1, 10), "subscription_model_adoption": f"{random.randint(40, 90)}%", "freemium_conversion_rate": f"{random.randint(2, 8)}%", "pricing_trend": random.choice(["increasing", "stable", "decreasing"])}

    def _generate_keywords(self, niche: str) -> List[Dict[str, Any]]:
        """Generate mock keywords (sync)."""
        # (Content identical to prototype _generate_keywords method)
        base_keywords = {"technology": ["software tools", "AI assistant", "coding platform", "tech solution"], "health": ["fitness program", "nutrition plan", "wellness app", "health tracker"], "finance": ["investment strategy", "passive income", "financial freedom", "wealth building"], "education": ["online course", "skill development", "learning platform", "certification"], "e-commerce": ["online store", "product marketplace", "subscription box", "direct to consumer"], "sustainability": ["eco-friendly products", "sustainable living", "zero waste", "green solutions"], "productivity": ["time management", "focus app", "productivity system", "workflow optimization"]}
        keywords_list = base_keywords.get(niche, base_keywords["technology"])[:]
        additional_keywords = [f"best {niche} {random.choice(['tools', 'solutions', 'platforms', 'services'])}", f"{niche} for {random.choice(['beginners', 'professionals', 'businesses', 'students'])}", f"how to {random.choice(['start', 'improve', 'optimize', 'scale'])} {niche}", f"{niche} {random.choice(['tips', 'tricks', 'hacks', 'strategies'])}", f"affordable {niche} {random.choice(['tools', 'solutions', 'platforms', 'services'])}"]
        keywords_list.extend(additional_keywords)
        keywords = []
        for keyword in keywords_list: keywords.append({"keyword": keyword, "search_volume": random.randint(1000, 50000), "competition": round(random.uniform(0.1, 0.9), 2), "cpc": round(random.uniform(0.5, 10.0), 2)})
        keywords.sort(key=lambda x: x["search_volume"], reverse=True)
        return keywords

    async def close_clients(self):
        """Close any open HTTP clients."""
        if self.market_api_client and hasattr(self.market_api_client, 'close'):
            await self.market_api_client.close()
            logger.info("Closed Market API client.")


# --- FastAPI Server Setup ---

app = FastAPI(title="MarketAnalysisAgent A2A Server")

# Instantiate the agent (reads env vars internally)
try:
    market_agent_instance = MarketAnalysisAgent()
except ValueError as e:
    logger.critical(f"Failed to initialize MarketAnalysisAgent: {e}. Server cannot start.", exc_info=True)
    import sys
    sys.exit(f"Agent Initialization Error: {e}")


@app.post("/invoke") # Response model can be dynamic based on event payload
async def invoke_agent(request: MarketAnalysisInput = Body(...)):
    """
    A2A endpoint to invoke the MarketAnalysisAgent.
    Expects JSON body matching MarketAnalysisInput.
    Returns result payload on success, or raises HTTPException on error.
    """
    logger.info(f"MarketAnalysisAgent /invoke called for action: {request.action}")
    invocation_id = f"market-{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(1000,9999)}"
    context = InvocationContext(agent_id="market-analysis-agent", invocation_id=invocation_id, data=request.model_dump())

    try:
        result_event = await market_agent_instance.run_async(context)

        if result_event and isinstance(result_event.data, dict):
            # Check metadata for success/error status if available
            if result_event.metadata.get("status") == "error":
                 error_msg = result_event.data.get("error", "Unknown agent error")
                 logger.error(f"MarketAnalysisAgent run_async returned error event: {error_msg}")
                 raise HTTPException(status_code=500, detail=result_event.data) # Return error payload
            else:
                 # Assume success if status is not explicitly error
                 logger.info(f"MarketAnalysisAgent returning success result for action: {request.action}")
                 # Validate against generic output model if needed, or return directly
                 try:
                     # We expect the payload to match MarketAnalysisOutput structure now
                     output_payload = MarketAnalysisOutput(**result_event.data)
                     return output_payload
                 except ValidationError as val_err:
                     logger.error(f"Success event payload validation failed: {val_err}. Payload: {result_event.data}")
                     # Return raw data if validation fails but status was success
                     return result_event.data
        else:
            logger.error(f"MarketAnalysisAgent run_async returned None or invalid event data: {result_event}")
            raise HTTPException(status_code=500, detail={"error": "Agent execution failed to return a valid event."})

    except HTTPException as http_exc:
        raise http_exc # Re-raise FastAPI exceptions
    except Exception as e:
        logger.error(f"Error during agent invocation: {e}", exc_info=True)
        # Construct error payload consistent with MarketAnalysisOutput
        error_output = MarketAnalysisOutput(
            task_id=invocation_id, action=request.action, input_params=request.model_dump(),
            results=None, success=False, timestamp=datetime.now().isoformat(),
            error=f"Internal server error: {e}"
        )
        raise HTTPException(status_code=500, detail=error_output.model_dump(exclude_none=True))


@app.get("/health")
async def health_check():
    # Add checks for API client initialization if needed
    status = "ok"
    if not market_agent_instance.market_api_client:
        status = "warning: Market API client not initialized (check config)"
    return {"status": status}

# --- Server Shutdown Hook ---
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down MarketAnalysisAgent server...")
    await market_agent_instance.close_clients() # Close API client

# --- Main execution block ---

if __name__ == "__main__":
    # Load .env for local development if needed
    try:
        from dotenv import load_dotenv
        if load_dotenv():
             logger.info("Loaded .env file for local run.")
        else:
             logger.info("No .env file found or it was empty.")
    except ImportError:
        logger.info("dotenv library not found, skipping .env load.")

    parser = argparse.ArgumentParser(description="Run the MarketAnalysisAgent A2A server.")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind the server to.")
    parser.add_argument("--port", type=int, default=8088, help="Port to run the server on.") # Default matches compose
    args = parser.parse_args()

    # Optional: Check for MARKET_DATA_API_BASE_URL before starting
    # if not os.environ.get(MarketAnalysisAgent.ENV_MARKET_API_BASE_URL):
    #     print(f"WARNING: Environment variable {MarketAnalysisAgent.ENV_MARKET_API_BASE_URL} not set. Real data fetching disabled.")

    print(f"Starting MarketAnalysisAgent A2A server on {args.host}:{args.port}")

    uvicorn.run(app, host=args.host, port=args.port)