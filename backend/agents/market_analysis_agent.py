"""
Market Analysis Agent - ADK Compliant Agent
"""

import json
import logging
import random
import time
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

from google.adk.agents import Agent, AgentConfig, AgentError
from google.adk.runtime import InvocationContext, Event

import backend.config as config
from backend.utils.api_client import APIClient, APIError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MarketAnalysisAgent(Agent):
    """
    ADK-compliant agent that analyzes market trends, identifies opportunities,
    evaluates competition, and analyzes keywords based on input requests.
    """

    def __init__(self, agent_id: str, agent_config: Optional[AgentConfig] = None):
        """
        Initialize the Market Analysis Agent.

        Args:
            agent_id: The unique identifier for this agent instance.
            agent_config: Configuration for the agent (optional).
        """
        super().__init__(agent_id=agent_id, agent_config=agent_config)
        self.cached_data = {}
        self.last_analysis = {} # Consider if this state is needed or should be event-driven

        # Initialize API Client using configuration
        # Ensure MARKET_DATA_API_BASE_URL and MARKET_DATA_API_KEY are set in config.py
        try:
            self.market_api_client = APIClient(
                base_url=config.Config.MARKET_DATA_API_BASE_URL,
                api_key=config.Config.MARKET_DATA_API_KEY
            )
            logger.info(f"Market Analysis Agent [{self.agent_id}] initialized with API client.")
        except AttributeError as e:
            logger.error(f"Configuration error for Market Analysis Agent [{self.agent_id}]: {e}. API client not initialized.")
            # Decide how to handle this - raise error, or operate without API client?
            # For now, allow operation but log error. Real data fetching will fail.
            self.market_api_client = None # type: ignore

    async def run_async(self, context: InvocationContext) -> Event:
        """
        Execute a market analysis task based on the invocation context.

        Args:
            context: The invocation context containing input data.

        Returns:
            An Event object containing the results or an error.
        """
        logger.info(f"Market Analysis Agent [{self.agent_id}] received task: {context.input.event_type}")

        try:
            if not isinstance(context.input.data, dict):
                raise ValueError("Input data must be a dictionary.")

            action = context.input.data.get("action")
            if not action:
                raise ValueError("Missing 'action' in input data.")

            results: Any = None
            event_type: str = f"market.{action}.failed" # Default to failure

            if action == "analyze_trends":
                niche = context.input.data.get("niche", "technology")
                depth = context.input.data.get("depth", "standard")
                results = await self.analyze_trends(niche, depth)
                event_type = f"market.trends.analyzed"

            elif action == "identify_opportunities":
                niches = context.input.data.get("niches") # Can be None
                results = await self.identify_opportunities(niches)
                event_type = f"market.opportunities.identified"

            elif action == "evaluate_competition":
                niche = context.input.data.get("niche", "technology")
                business_type = context.input.data.get("business_type", "affiliate_marketing")
                results = await self.evaluate_competition(niche, business_type)
                event_type = f"market.competition.evaluated"

            elif action == "analyze_keywords":
                niche = context.input.data.get("niche", "technology")
                limit = context.input.data.get("limit", 10)
                results = await self.analyze_keywords(niche, limit)
                event_type = f"market.keywords.analyzed"

            else:
                raise ValueError(f"Unknown action: {action}")

            # Return success event
            return Event(
                event_type=event_type,
                data={
                    "task_id": context.invocation_id, # Use invocation_id as task_id
                    "action": action,
                    "input_params": context.input.data, # Include original params for context
                    "results": results,
                    "success": True,
                    "timestamp": datetime.now().isoformat()
                }
            )

        except (APIError, ValueError, TypeError, Exception) as e:
            logger.error(f"Market Analysis Agent [{self.agent_id}] error processing action '{action}': {e}", exc_info=True)
            # Return error event
            return Event(
                event_type=f"market.{action or 'task'}.failed",
                data={
                    "task_id": context.invocation_id,
                    "action": action,
                    "input_params": context.input.data if isinstance(context.input.data, dict) else {},
                    "success": False,
                    "error": f"{type(e).__name__}: {e}",
                    "timestamp": datetime.now().isoformat()
                }
            )

    # --- Analysis Methods (Adapted from Prototype) ---

    async def fetch_trend_data(self, niche: str) -> Optional[Dict[str, Any]]:
        """Fetch real trend data from market data API."""
        if not self.market_api_client:
            logger.warning(f"Market API client not initialized for niche: {niche}. Cannot fetch real data.")
            return None
        try:
            # Example endpoint and params, adjust based on actual API
            endpoint = f"trends/{niche}" # Ensure this endpoint exists
            logger.info(f"Attempting to fetch real trend data for {niche} from {endpoint}")
            response = await self.market_api_client.get(endpoint)
            # Assume response contains 'trends' dict
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
        """
        Analyze trends in a specific niche. (Async version)
        """
        logger.info(f"Analyzing {depth} trends for {niche} niche")

        cache_key = f"{niche}_{depth}"
        current_time = datetime.now().timestamp()
        if cache_key in self.cached_data and (current_time - self.cached_data[cache_key]["timestamp"] < 3600):
            logger.info(f"Using cached trend data for {niche}")
            return self.cached_data[cache_key]["data"]

        # Try to fetch real trend data asynchronously
        real_data = await self.fetch_trend_data(niche)
        if real_data:
            logger.info(f"Using fetched real trend data for {niche}")
            # Potentially enhance real_data if depth is 'deep' - requires API support or LLM analysis
            analysis_results = self._process_real_trend_data(real_data, niche, depth)
            self.cached_data[cache_key] = {
                "timestamp": current_time,
                "data": analysis_results
            }
            return analysis_results

        # Fallback to mock data generation if API fails or returns None
        logger.info(f"Falling back to mock trend data generation for {niche}")
        # Simulate async delay if needed, though generation is quick
        # await asyncio.sleep(0.1) # Simulate work if generation were complex
        trends = self._generate_trend_data(niche, depth) # This is synchronous
        self.cached_data[cache_key] = {
            "timestamp": current_time,
            "data": trends
        }
        # Store as last analysis (optional, consider if needed)
        self.last_analysis = {
            "niche": niche, "depth": depth, "timestamp": datetime.now().isoformat(), "results": trends
        }
        return trends

    def _process_real_trend_data(self, real_data: Dict[str, Any], niche: str, depth: str) -> Dict[str, Any]:
        """Placeholder to process/enhance real data based on depth."""
        # In a real scenario, you might:
        # - Validate/clean the real_data
        # - If depth is 'deep', potentially make more API calls or use an LLM to enrich the data
        # - Format the data consistently with mock data structure if needed
        logger.info(f"Processing real trend data for {niche} (depth: {depth})")
        # For now, just add common fields and return
        processed_data = real_data.copy()
        processed_data["niche"] = niche
        processed_data["analysis_depth"] = depth
        processed_data["timestamp"] = datetime.now().isoformat()
        processed_data["data_source"] = "api" # Indicate source

        # Add mock deep analysis fields if depth is deep and API didn't provide them
        if depth == "deep":
            if "demographics" not in processed_data:
                 processed_data["demographics"] = self._generate_demographics(niche)
            if "competitive_landscape" not in processed_data:
                 processed_data["competitive_landscape"] = self._generate_competitive_landscape(niche)
            if "pricing_analysis" not in processed_data:
                 processed_data["pricing_analysis"] = self._generate_pricing_analysis(niche)
            # Potentially add more segments if API data is basic
            # processed_data["growing_segments"].extend(self._generate_additional_segments(niche, True))
            # processed_data["declining_segments"].extend(self._generate_additional_segments(niche, False))

        return processed_data


    async def identify_opportunities(self, niches: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Identify business opportunities across multiple niches. (Async)
        """
        default_niches = [
            "technology", "health", "finance", "education",
            "e-commerce", "sustainability", "productivity"
        ]
        niches_to_analyze = niches or default_niches
        logger.info(f"Identifying opportunities across {len(niches_to_analyze)} niches: {niches_to_analyze}")

        opportunities = []
        # Analyze trends for each niche concurrently
        trend_analysis_tasks = [self.analyze_trends(niche) for niche in niches_to_analyze]
        trend_results_list = await asyncio.gather(*trend_analysis_tasks)

        for niche, trends in zip(niches_to_analyze, trend_results_list):
            if trends: # Ensure trends were successfully analyzed
                # Generate opportunities based on trends (synchronous part)
                niche_opportunities = self._extract_opportunities(niche, trends)
                opportunities.extend(niche_opportunities)
            else:
                logger.warning(f"Could not analyze trends for niche '{niche}', skipping opportunity identification.")

        # Sort by potential revenue (descending)
        opportunities.sort(key=lambda x: x.get("potential_revenue", 0), reverse=True)
        logger.info(f"Identified {len(opportunities)} opportunities.")
        return opportunities

    async def evaluate_competition(self, niche: str, business_type: str) -> Dict[str, Any]:
        """
        Evaluate competition level in a specific niche and business type. (Async)
        """
        logger.info(f"Evaluating competition for {business_type} in {niche} niche")

        # In Phase 2, this could use real competitive analysis APIs or LLMs
        # For now, return mocked competition data (synchronous generation)
        # Simulate async delay if needed
        # await asyncio.sleep(0.1)

        # Competition levels vary by niche and business type (Mock data)
        competition_levels = {
            "technology": {"affiliate_marketing": 8, "digital_product": 7, "saas": 9},
            "health": {"affiliate_marketing": 9, "digital_product": 8, "saas": 6},
            "finance": {"affiliate_marketing": 9, "digital_product": 7, "saas": 8},
            "education": {"affiliate_marketing": 7, "digital_product": 9, "saas": 6},
            "e-commerce": {"affiliate_marketing": 8, "digital_product": 6, "saas": 7},
            "sustainability": {"affiliate_marketing": 5, "digital_product": 6, "saas": 7},
            "productivity": {"affiliate_marketing": 7, "digital_product": 7, "saas": 8}
        }
        competition_level = competition_levels.get(niche, {}).get(business_type, 7)
        competitors = self._generate_competitors(niche, business_type)

        return {
            "niche": niche,
            "business_type": business_type,
            "competition_level": competition_level,
            "saturation": self._calculate_saturation(competition_level),
            "top_competitors": competitors,
            "entry_barriers": self._generate_entry_barriers(niche, business_type),
            "timestamp": datetime.now().isoformat()
        }

    async def analyze_keywords(self, niche: str, limit: int = 10) -> Dict[str, Any]:
        """
        Analyze keywords for a specific niche. (Async)
        """
        logger.info(f"Analyzing keywords for {niche} niche (limit: {limit})")

        # In Phase 2, this could use real keyword research APIs or LLMs
        # For now, return mocked keyword data (synchronous generation)
        # Simulate async delay if needed
        # await asyncio.sleep(0.1)

        keywords = self._generate_keywords(niche)
        top_keywords = keywords[:limit]

        # Basic validation
        if not top_keywords:
             avg_competition = 0
        else:
             avg_competition = sum(k.get("competition", 0) for k in top_keywords) / len(top_keywords)


        return {
            "niche": niche,
            "keywords": top_keywords,
            "search_volume_total": sum(k.get("search_volume", 0) for k in top_keywords),
            "competition_average": round(avg_competition, 2),
            "timestamp": datetime.now().isoformat()
        }

    # --- Helper Methods (Copied from Prototype, potentially make async if they involve I/O) ---
    # Note: Most helpers are currently synchronous data generation logic.

    def _generate_trend_data(self, niche: str, depth: str) -> Dict[str, Any]:
        """Generate mock trend data."""
        # (Content identical to prototype _generate_trend_data method)
        trend_data = {
            "technology": {
                "growing_segments": ["AI tools", "no-code platforms", "cybersecurity"],
                "declining_segments": ["mobile apps", "general web hosting"],
                "growth_rate": 12.5,
                "sentiment": 8.2
            },
            "health": {
                "growing_segments": ["mental wellness", "home fitness", "nutrition tracking"],
                "declining_segments": ["general supplements", "diet programs"],
                "growth_rate": 9.8,
                "sentiment": 7.5
            },
            "finance": {
                "growing_segments": ["crypto education", "financial literacy", "passive income"],
                "declining_segments": ["day trading courses", "general investing"],
                "growth_rate": 7.2,
                "sentiment": 6.8
            },
            "education": {
                "growing_segments": ["skill certifications", "cohort courses", "specialized tutorials"],
                "declining_segments": ["general e-books", "broad courses"],
                "growth_rate": 14.3,
                "sentiment": 8.7
            },
            "e-commerce": {
                "growing_segments": ["niche marketplaces", "subscription boxes", "sustainable products"],
                "declining_segments": ["general dropshipping", "print on demand"],
                "growth_rate": 8.5,
                "sentiment": 7.1
            },
            "sustainability": {
                "growing_segments": ["zero waste products", "sustainable fashion", "eco-education"],
                "declining_segments": ["general green blogs", "carbon offsetting"],
                "growth_rate": 15.7,
                "sentiment": 8.9
            },
            "productivity": {
                "growing_segments": ["AI assistants", "focus tools", "knowledge management"],
                "declining_segments": ["general productivity apps", "time tracking"],
                "growth_rate": 11.2,
                "sentiment": 7.8
            }
        }
        base_data = trend_data.get(niche, trend_data["technology"]).copy() # Use copy
        if depth == "deep":
            base_data["demographics"] = self._generate_demographics(niche)
            base_data["growing_segments"].extend(self._generate_additional_segments(niche, True))
            base_data["declining_segments"].extend(self._generate_additional_segments(niche, False))
            base_data["competitive_landscape"] = self._generate_competitive_landscape(niche)
            base_data["pricing_analysis"] = self._generate_pricing_analysis(niche)
        base_data["niche"] = niche
        base_data["analysis_depth"] = depth
        base_data["timestamp"] = datetime.now().isoformat()
        base_data["data_source"] = "mock" # Indicate source
        return base_data

    def _extract_opportunities(self, niche: str, trends: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract mock business opportunities."""
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
                "name": f"{segment} {business_type.replace('_', ' ').title()}",
                "type": business_type,
                "niche": niche,
                "segment": segment,
                "potential_revenue": potential_revenue,
                "implementation_difficulty": difficulty,
                "market_saturation": self._calculate_saturation(difficulty), # Use difficulty as proxy for competition
                "risk_level": risk_level
            }
            opportunities.append(opportunity)
        return opportunities

    def _determine_business_type(self, segment: str, niche: str) -> str:
        """Determine mock business type."""
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
        if segment in segment_types:
            return segment_types[segment]
        else:
            # Consider niche influence if segment unknown
            if niche in ["technology", "productivity"]: return random.choice(["saas", "digital_product"])
            if niche == "e-commerce": return "e-commerce"
            if niche == "finance": return random.choice(["affiliate_marketing", "digital_product"])
            return random.choice(["affiliate_marketing", "digital_product", "saas", "e-commerce"])


    def _generate_difficulty(self, segment: str, niche: str) -> int:
        """Generate mock difficulty score."""
        # (Content identical to prototype _generate_difficulty method)
        base_difficulties = {"affiliate_marketing": 5, "digital_product": 7, "saas": 9, "e-commerce": 6}
        business_type = self._determine_business_type(segment, niche)
        base = base_difficulties.get(business_type, 7)
        variation = random.randint(-1, 1)
        return max(1, min(10, base + variation))

    def _determine_risk_level(self, difficulty: int, revenue: int) -> str:
        """Determine mock risk level."""
        # (Content identical to prototype _determine_risk_level method)
        risk_score = difficulty - (revenue / 1000) # Simplified risk calc
        if risk_score > 5: return "high"
        elif risk_score > 2: return "medium"
        else: return "low"

    def _calculate_saturation(self, competition_level: int) -> int:
        """Calculate mock market saturation."""
        # (Content identical to prototype _calculate_saturation method)
        variation = random.randint(-1, 1)
        return max(1, min(10, competition_level + variation))

    def _generate_competitors(self, niche: str, business_type: str) -> List[Dict[str, Any]]:
        """Generate mock competitors."""
        # (Content identical to prototype _generate_competitors method)
        num_competitors = random.randint(3, 5)
        competitors = []
        for i in range(num_competitors):
            name = self._generate_competitor_name(niche, business_type)
            market_share = round(random.uniform(5.0, 25.0), 1)
            monthly_revenue = random.randint(5000, 50000)
            competitors.append({
                "name": name,
                "market_share": market_share,
                "monthly_revenue": monthly_revenue,
                "years_active": random.randint(1, 10)
            })
        competitors.sort(key=lambda x: x["market_share"], reverse=True)
        return competitors

    def _generate_competitor_name(self, niche: str, business_type: str) -> str:
        """Generate mock competitor name."""
        # (Content identical to prototype _generate_competitor_name method)
        prefixes = {
            "technology": ["Tech", "Digital", "Cyber", "Code", "Dev"], "health": ["Health", "Vital", "Wellness", "Fit", "Nutri"],
            "finance": ["Finance", "Money", "Wealth", "Capital", "Invest"], "education": ["Learn", "Edu", "Skill", "Academy", "Master"],
            "e-commerce": ["Shop", "Store", "Market", "Buy", "Retail"], "sustainability": ["Eco", "Green", "Sustain", "Earth", "Bio"],
            "productivity": ["Focus", "Task", "Time", "Boost", "Flow"]
        }
        suffixes = {
            "affiliate_marketing": ["Affiliate", "Partner", "Promote", "Refer", "Link"], "digital_product": ["Course", "Guide", "Academy", "School", "Learn"],
            "saas": ["App", "Tool", "Suite", "Cloud", "Platform"], "e-commerce": ["Shop", "Store", "Market", "Goods", "Products"]
        }
        prefix = random.choice(prefixes.get(niche, ["Brand"]))
        suffix = random.choice(suffixes.get(business_type, ["Pro"]))
        return f"{prefix}{suffix}"

    def _generate_entry_barriers(self, niche: str, business_type: str) -> List[str]:
        """Generate mock entry barriers."""
        # (Content identical to prototype _generate_entry_barriers method)
        common_barriers = [
            "High initial investment", "Technical expertise required", "Established brand loyalty",
            "Complex regulations", "Network effects favoring incumbents", "High customer acquisition costs",
            "Intellectual property protections", "Economies of scale"
        ]
        specific_barriers = {
            "affiliate_marketing": ["Saturated affiliate networks", "Commission rate competition", "Cookie duration limitations"],
            "digital_product": ["Content creation expertise", "High-quality production requirements", "Platform fees and restrictions"],
            "saas": ["Development costs", "Ongoing maintenance requirements", "User onboarding complexity"],
            "e-commerce": ["Inventory management", "Shipping logistics", "Return handling costs"]
        }
        selected_barriers = random.sample(common_barriers, random.randint(2, 3))
        if business_type in specific_barriers:
            specific_list = specific_barriers[business_type]
            num_specific = min(len(specific_list), random.randint(1, 2))
            selected_barriers.extend(random.sample(specific_list, num_specific))
        return selected_barriers

    def _generate_demographics(self, niche: str) -> Dict[str, Any]:
        """Generate mock audience demographics."""
        # (Content identical to prototype _generate_demographics method)
        default_demographics = {
            "age_groups": {"18-24": 15, "25-34": 30, "35-44": 25, "45-54": 15, "55+": 15},
            "gender_split": {"male": 55, "female": 45},
            "income_levels": {"low": 20, "medium": 50, "high": 30},
            "education_levels": {"high_school": 25, "bachelors": 45, "masters": 20, "phd": 10}
        }
        niche_demographics = {
            "technology": {"age_groups": {"18-24": 20, "25-34": 35, "35-44": 25, "45-54": 15, "55+": 5}, "gender_split": {"male": 65, "female": 35}},
            "health": {"age_groups": {"18-24": 15, "25-34": 30, "35-44": 25, "45-54": 20, "55+": 10}, "gender_split": {"male": 40, "female": 60}},
            "finance": {"age_groups": {"18-24": 10, "25-34": 25, "35-44": 30, "45-54": 20, "55+": 15}, "income_levels": {"low": 15, "medium": 45, "high": 40}}
        }
        demographics = default_demographics.copy()
        if niche in niche_demographics:
            for key, value in niche_demographics[niche].items():
                 # Deep copy nested dicts if necessary, though here they are overwritten
                 demographics[key] = value.copy() if isinstance(value, dict) else value
        return demographics


    def _generate_additional_segments(self, niche: str, growing: bool) -> List[str]:
        """Generate mock additional market segments."""
        # (Content identical to prototype _generate_additional_segments method)
        additional_segments = {
            "technology": {"growing": ["AR/VR solutions", "blockchain applications", "edge computing"], "declining": ["traditional CMS", "on-premise software", "generic mobile apps"]},
            "health": {"growing": ["personalized nutrition", "sleep optimization", "biohacking"], "declining": ["general fitness apps", "generic meal plans", "broad supplements"]},
            "finance": {"growing": ["DeFi education", "sustainable investing", "financial independence"], "declining": ["traditional stock picking", "general budgeting", "forex trading"]},
            "education": {"growing": ["microlearning", "community-based learning", "AI-assisted education"], "declining": ["general online courses", "static e-books", "non-interactive content"]}
        }
        niche_segments = additional_segments.get(niche, {})
        segment_type = "growing" if growing else "declining"
        return niche_segments.get(segment_type, [])

    def _generate_competitive_landscape(self, niche: str) -> Dict[str, Any]:
        """Generate mock competitive landscape."""
        # (Content identical to prototype _generate_competitive_landscape method)
        return {
            "total_competitors": random.randint(50, 200), "market_leaders": random.randint(5, 15),
            "new_entrants_monthly": random.randint(3, 12), "average_lifespan": f"{random.randint(2, 5)} years",
            "consolidation_trend": random.choice(["increasing", "stable", "decreasing"])
        }

    def _generate_pricing_analysis(self, niche: str) -> Dict[str, Any]:
        """Generate mock pricing analysis."""
        # (Content identical to prototype _generate_pricing_analysis method)
        return {
            "average_price_point": f"${random.randint(20, 100)}", "price_sensitivity": random.randint(1, 10),
            "subscription_model_adoption": f"{random.randint(40, 90)}%", "freemium_conversion_rate": f"{random.randint(2, 8)}%",
            "pricing_trend": random.choice(["increasing", "stable", "decreasing"])
        }

    def _generate_keywords(self, niche: str) -> List[Dict[str, Any]]:
        """Generate mock keywords."""
        # (Content identical to prototype _generate_keywords method)
        base_keywords = {
            "technology": ["software tools", "AI assistant", "coding platform", "tech solution"],
            "health": ["fitness program", "nutrition plan", "wellness app", "health tracker"],
            "finance": ["investment strategy", "passive income", "financial freedom", "wealth building"],
            "education": ["online course", "skill development", "learning platform", "certification"],
            "e-commerce": ["online store", "product marketplace", "subscription box", "direct to consumer"],
            "sustainability": ["eco-friendly products", "sustainable living", "zero waste", "green solutions"],
            "productivity": ["time management", "focus app", "productivity system", "workflow optimization"]
        }
        keywords_list = base_keywords.get(niche, base_keywords["technology"])[:] # Use copy
        additional_keywords = [
            f"best {niche} {random.choice(['tools', 'solutions', 'platforms', 'services'])}",
            f"{niche} for {random.choice(['beginners', 'professionals', 'businesses', 'students'])}",
            f"how to {random.choice(['start', 'improve', 'optimize', 'scale'])} {niche}",
            f"{niche} {random.choice(['tips', 'tricks', 'hacks', 'strategies'])}",
            f"affordable {niche} {random.choice(['tools', 'solutions', 'platforms', 'services'])}"
        ]
        keywords_list.extend(additional_keywords)
        keywords = []
        for keyword in keywords_list:
            keywords.append({
                "keyword": keyword,
                "search_volume": random.randint(1000, 50000),
                "competition": round(random.uniform(0.1, 0.9), 2),
                "cpc": round(random.uniform(0.5, 10.0), 2)
            })
        keywords.sort(key=lambda x: x["search_volume"], reverse=True)
        return keywords