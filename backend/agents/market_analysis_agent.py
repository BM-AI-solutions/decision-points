"""
Market Analysis Agent - ADK Version
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
from google.adk.tools import tool # Import tool decorator

# Assuming backend.config and backend.utils.api_client are accessible
# Adjust imports if the structure changed during refactoring elsewhere
try:
    import backend.config as config
    from backend.utils.api_client import APIClient, APIError
except ImportError:
    # Fallback if running standalone or structure differs
    logger.warning("Could not import backend config/utils. API client might not work.")
    config = None
    APIClient = None
    APIError = Exception # Fallback error type

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Global State / Clients (Consider better dependency injection for production) ---
AGENT_ID = "market_analysis_adk" # Define agent ID
CACHED_DATA = {} # Simple in-memory cache
MARKET_API_CLIENT = None

# Initialize API Client globally
if config and APIClient:
    try:
        MARKET_API_CLIENT = APIClient(
            base_url=config.Config.MARKET_DATA_API_BASE_URL,
            api_key=config.Config.MARKET_DATA_API_KEY
        )
        logger.info(f"Market Analysis Agent [{AGENT_ID}] initialized with API client.")
    except AttributeError as e:
        logger.error(f"Configuration error for Market Analysis Agent [{AGENT_ID}]: {e}. API client not initialized.")
    except Exception as e:
         logger.error(f"Error initializing API client for Market Analysis Agent [{AGENT_ID}]: {e}")
else:
    logger.warning(f"Market Analysis Agent [{AGENT_ID}]: API client cannot be initialized (missing config or APIClient class).")


# --- Helper Methods (Standalone Functions) ---

async def _fetch_trend_data(niche: str) -> Optional[Dict[str, Any]]:
    """Helper: Fetch real trend data from market data API."""
    if not MARKET_API_CLIENT:
        logger.warning(f"Helper: Market API client not initialized for niche: {niche}.")
        return None
    try:
        endpoint = f"trends/{niche}"
        logger.info(f"Helper: Attempting to fetch real trend data for {niche} from {endpoint}")
        response = await MARKET_API_CLIENT.get(endpoint)
        if response and isinstance(response, dict) and 'trends' in response:
            logger.info(f"Helper: Successfully fetched real trend data for {niche}")
            return response['trends']
        else:
            logger.warning(f"Helper: Invalid or missing 'trends' data in API response for {niche}: {response}")
            return None
    except APIError as e:
        logger.warning(f"Helper: Market data API error fetching trends for {niche}: {e}")
    except Exception as e:
        logger.warning(f"Helper: Unexpected error fetching market data for {niche}: {e}", exc_info=True)
    return None

def _generate_demographics(niche: str) -> Dict[str, Any]:
    """Helper: Generate mock audience demographics."""
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
             demographics[key] = value.copy() if isinstance(value, dict) else value
    return demographics

def _generate_additional_segments(niche: str, growing: bool) -> List[str]:
    """Helper: Generate mock additional market segments."""
    additional_segments = {
        "technology": {"growing": ["AR/VR solutions", "blockchain applications", "edge computing"], "declining": ["traditional CMS", "on-premise software", "generic mobile apps"]},
        "health": {"growing": ["personalized nutrition", "sleep optimization", "biohacking"], "declining": ["general fitness apps", "generic meal plans", "broad supplements"]},
        "finance": {"growing": ["DeFi education", "sustainable investing", "financial independence"], "declining": ["traditional stock picking", "general budgeting", "forex trading"]},
        "education": {"growing": ["microlearning", "community-based learning", "AI-assisted education"], "declining": ["general online courses", "static e-books", "non-interactive content"]}
    }
    niche_segments = additional_segments.get(niche, {})
    segment_type = "growing" if growing else "declining"
    return niche_segments.get(segment_type, [])

def _generate_competitive_landscape(niche: str) -> Dict[str, Any]:
    """Helper: Generate mock competitive landscape."""
    return {
        "total_competitors": random.randint(50, 200), "market_leaders": random.randint(5, 15),
        "new_entrants_monthly": random.randint(3, 12), "average_lifespan": f"{random.randint(2, 5)} years",
        "consolidation_trend": random.choice(["increasing", "stable", "decreasing"])
    }

def _generate_pricing_analysis(niche: str) -> Dict[str, Any]:
    """Helper: Generate mock pricing analysis."""
    return {
        "average_price_point": f"${random.randint(20, 100)}", "price_sensitivity": random.randint(1, 10),
        "subscription_model_adoption": f"{random.randint(40, 90)}%", "freemium_conversion_rate": f"{random.randint(2, 8)}%",
        "pricing_trend": random.choice(["increasing", "stable", "decreasing"])
    }

def _process_real_trend_data(real_data: Dict[str, Any], niche: str, depth: str) -> Dict[str, Any]:
    """Helper: Placeholder to process/enhance real data based on depth."""
    logger.info(f"Helper: Processing real trend data for {niche} (depth: {depth})")
    processed_data = real_data.copy()
    processed_data["niche"] = niche
    processed_data["analysis_depth"] = depth
    processed_data["timestamp"] = datetime.now().isoformat()
    processed_data["data_source"] = "api"
    if depth == "deep":
        if "demographics" not in processed_data: processed_data["demographics"] = _generate_demographics(niche)
        if "competitive_landscape" not in processed_data: processed_data["competitive_landscape"] = _generate_competitive_landscape(niche)
        if "pricing_analysis" not in processed_data: processed_data["pricing_analysis"] = _generate_pricing_analysis(niche)
    return processed_data

def _generate_trend_data(niche: str, depth: str) -> Dict[str, Any]:
    """Helper: Generate mock trend data."""
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
        base_data["demographics"] = _generate_demographics(niche)
        base_data["growing_segments"].extend(_generate_additional_segments(niche, True))
        base_data["declining_segments"].extend(_generate_additional_segments(niche, False))
        base_data["competitive_landscape"] = _generate_competitive_landscape(niche)
        base_data["pricing_analysis"] = _generate_pricing_analysis(niche)
    base_data["niche"] = niche
    base_data["analysis_depth"] = depth
    base_data["timestamp"] = datetime.now().isoformat()
    base_data["data_source"] = "mock"
    return base_data

def _determine_business_type(segment: str, niche: str) -> str:
    """Helper: Determine mock business type."""
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
    if niche in ["technology", "productivity"]: return random.choice(["saas", "digital_product"])
    if niche == "e-commerce": return "e-commerce"
    if niche == "finance": return random.choice(["affiliate_marketing", "digital_product"])
    return random.choice(["affiliate_marketing", "digital_product", "saas", "e-commerce"])

def _generate_difficulty(segment: str, niche: str) -> int:
    """Helper: Generate mock difficulty score."""
    base_difficulties = {"affiliate_marketing": 5, "digital_product": 7, "saas": 9, "e-commerce": 6}
    business_type = _determine_business_type(segment, niche)
    base = base_difficulties.get(business_type, 7)
    return max(1, min(10, base + random.randint(-1, 1)))

def _determine_risk_level(difficulty: int, revenue: int) -> str:
    """Helper: Determine mock risk level."""
    risk_score = difficulty - (revenue / 1000)
    if risk_score > 5: return "high"
    elif risk_score > 2: return "medium"
    else: return "low"

def _calculate_saturation(competition_level: int) -> int:
    """Helper: Calculate mock market saturation."""
    return max(1, min(10, competition_level + random.randint(-1, 1)))

def _generate_competitor_name(niche: str, business_type: str) -> str:
    """Helper: Generate mock competitor name."""
    prefixes = {"technology": ["Tech", "Digital", "Cyber"], "health": ["Health", "Vital", "Wellness"], "finance": ["Finance", "Money", "Wealth"], "education": ["Learn", "Edu", "Skill"], "e-commerce": ["Shop", "Store", "Market"], "sustainability": ["Eco", "Green", "Sustain"], "productivity": ["Focus", "Task", "Time"]}
    suffixes = {"affiliate_marketing": ["Affiliate", "Partner", "Promote"], "digital_product": ["Course", "Guide", "Academy"], "saas": ["App", "Tool", "Suite"], "e-commerce": ["Shop", "Store", "Market"]}
    prefix = random.choice(prefixes.get(niche, ["Brand"]))
    suffix = random.choice(suffixes.get(business_type, ["Pro"]))
    return f"{prefix}{suffix}"

def _generate_competitors(niche: str, business_type: str) -> List[Dict[str, Any]]:
    """Helper: Generate mock competitors."""
    num_competitors = random.randint(3, 5)
    competitors = []
    for _ in range(num_competitors):
        name = _generate_competitor_name(niche, business_type)
        competitors.append({
            "name": name, "market_share": round(random.uniform(5.0, 25.0), 1),
            "monthly_revenue": random.randint(5000, 50000), "years_active": random.randint(1, 10)
        })
    competitors.sort(key=lambda x: x["market_share"], reverse=True)
    return competitors

def _generate_entry_barriers(niche: str, business_type: str) -> List[str]:
    """Helper: Generate mock entry barriers."""
    common = ["High initial investment", "Technical expertise", "Brand loyalty", "Regulations", "Network effects", "Acquisition costs"]
    specific = {
        "affiliate_marketing": ["Saturated networks", "Commission competition"],
        "digital_product": ["Content creation", "Production quality"],
        "saas": ["Development costs", "Maintenance", "Onboarding"],
        "e-commerce": ["Inventory", "Logistics", "Returns"]
    }
    barriers = random.sample(common, random.randint(2, 3))
    if business_type in specific:
        barriers.extend(random.sample(specific[business_type], min(len(specific[business_type]), random.randint(1, 2))))
    return barriers

def _generate_keywords(niche: str) -> List[Dict[str, Any]]:
    """Helper: Generate mock keywords."""
    base = {"technology": ["software tools", "AI assistant"], "health": ["fitness program", "nutrition plan"], "finance": ["investment strategy", "passive income"], "education": ["online course", "skill development"], "e-commerce": ["online store", "product marketplace"], "sustainability": ["eco-friendly products", "sustainable living"], "productivity": ["time management", "focus app"]}
    keywords_list = base.get(niche, base["technology"])[:]
    keywords_list.extend([f"best {niche} tools", f"{niche} for beginners", f"how to start {niche}", f"{niche} tips"])
    keywords = []
    for kw in keywords_list:
        keywords.append({"keyword": kw, "search_volume": random.randint(1000, 50000), "competition": round(random.uniform(0.1, 0.9), 2), "cpc": round(random.uniform(0.5, 10.0), 2)})
    keywords.sort(key=lambda x: x["search_volume"], reverse=True)
    return keywords

def _extract_opportunities(niche: str, trends: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Helper: Extract mock business opportunities."""
    opportunities = []
    for segment in trends.get("growing_segments", []):
        business_type = _determine_business_type(segment, niche)
        growth_rate = trends.get("growth_rate", 10.0)
        potential_revenue = int(random.randint(1000, 5000) * (1 + growth_rate / 100))
        difficulty = _generate_difficulty(segment, niche)
        risk_level = _determine_risk_level(difficulty, potential_revenue)
        opportunities.append({
            "name": f"{segment} {business_type.replace('_', ' ').title()}", "type": business_type,
            "niche": niche, "segment": segment, "potential_revenue": potential_revenue,
            "implementation_difficulty": difficulty, "market_saturation": _calculate_saturation(difficulty),
            "risk_level": risk_level
        })
    return opportunities

# --- ADK Tool Definitions ---

@tool(description="Analyze market trends for a specific niche, optionally fetching real data.")
async def analyze_trends_tool(niche: str, depth: str = "standard") -> Dict[str, Any]:
    """
    ADK Tool: Analyze trends in a specific niche.
    Returns analysis results or an error dictionary.
    """
    logger.info(f"Tool: Analyzing {depth} trends for {niche} niche")
    # Note: Caching removed for simplicity in tool context, each call is fresh.
    try:
        real_data = await _fetch_trend_data(niche)
        if real_data:
            logger.info(f"Tool: Using fetched real trend data for {niche}")
            analysis_results = _process_real_trend_data(real_data, niche, depth)
            return {"success": True, "results": analysis_results}
        else:
            logger.info(f"Tool: Falling back to mock trend data generation for {niche}")
            trends = _generate_trend_data(niche, depth)
            return {"success": True, "results": trends}
    except Exception as e:
        logger.error(f"Tool: Error analyzing trends for {niche}: {e}", exc_info=True)
        return {"success": False, "error": f"Error analyzing trends: {str(e)}"}

@tool(description="Identify business opportunities across multiple niches based on trend analysis.")
async def identify_opportunities_tool(niches: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    ADK Tool: Identify business opportunities across multiple niches.
    Returns a list of opportunities or an error dictionary.
    """
    default_niches = ["technology", "health", "finance", "education", "e-commerce", "sustainability", "productivity"]
    niches_to_analyze = niches or default_niches
    logger.info(f"Tool: Identifying opportunities across {len(niches_to_analyze)} niches: {niches_to_analyze}")
    opportunities = []
    errors = []
    try:
        # Analyze trends concurrently using the analyze_trends_tool logic (via helper)
        async def get_trends(n):
             # Simulate calling the trend analysis logic directly
             # In a real scenario, might call context.invoke_tool if needed, but direct call is simpler here
             return await analyze_trends_tool(niche=n)

        trend_results_list = await asyncio.gather(*(get_trends(n) for n in niches_to_analyze))

        for niche, trends_result in zip(niches_to_analyze, trend_results_list):
             if trends_result.get("success"):
                 niche_opportunities = _extract_opportunities(niche, trends_result["results"])
                 opportunities.extend(niche_opportunities)
             else:
                 logger.warning(f"Tool: Trend analysis failed for niche '{niche}', skipping opportunities. Error: {trends_result.get('error')}")
                 errors.append({"niche": niche, "error": trends_result.get("error", "Unknown error")})

        opportunities.sort(key=lambda x: x.get("potential_revenue", 0), reverse=True)
        logger.info(f"Tool: Identified {len(opportunities)} opportunities.")

        if opportunities:
             return {"success": True, "opportunities": opportunities, "errors_encountered": errors or None}
        elif errors:
             return {"success": False, "error": "Failed to identify opportunities due to errors in trend analysis.", "details": errors}
        else:
             return {"success": False, "error": "No opportunities identified (trend analysis returned no results)."}

    except Exception as e:
        logger.error(f"Tool: Error identifying opportunities: {e}", exc_info=True)
        return {"success": False, "error": f"Error identifying opportunities: {str(e)}"}

@tool(description="Evaluate competition level for a business type within a specific niche.")
async def evaluate_competition_tool(niche: str, business_type: str) -> Dict[str, Any]:
    """
    ADK Tool: Evaluate competition level in a specific niche and business type.
    Returns competition analysis or an error dictionary.
    """
    logger.info(f"Tool: Evaluating competition for {business_type} in {niche} niche")
    try:
        competition_levels = {"technology": {"affiliate_marketing": 8, "digital_product": 7, "saas": 9}, "health": {"affiliate_marketing": 9, "digital_product": 8, "saas": 6}, "finance": {"affiliate_marketing": 9, "digital_product": 7, "saas": 8}, "education": {"affiliate_marketing": 7, "digital_product": 9, "saas": 6}, "e-commerce": {"affiliate_marketing": 8, "digital_product": 6, "saas": 7}, "sustainability": {"affiliate_marketing": 5, "digital_product": 6, "saas": 7}, "productivity": {"affiliate_marketing": 7, "digital_product": 7, "saas": 8}}
        competition_level = competition_levels.get(niche, {}).get(business_type, 7)
        competitors = _generate_competitors(niche, business_type)
        results = {
            "niche": niche, "business_type": business_type, "competition_level": competition_level,
            "saturation": _calculate_saturation(competition_level), "top_competitors": competitors,
            "entry_barriers": _generate_entry_barriers(niche, business_type), "timestamp": datetime.now().isoformat()
        }
        return {"success": True, "results": results}
    except Exception as e:
        logger.error(f"Tool: Error evaluating competition for {niche}/{business_type}: {e}", exc_info=True)
        return {"success": False, "error": f"Error evaluating competition: {str(e)}"}

@tool(description="Analyze keywords, search volume, and competition for a specific niche.")
async def analyze_keywords_tool(niche: str, limit: int = 10) -> Dict[str, Any]:
    """
    ADK Tool: Analyze keywords for a specific niche.
    Returns keyword analysis or an error dictionary.
    """
    logger.info(f"Tool: Analyzing keywords for {niche} niche (limit: {limit})")
    try:
        keywords = _generate_keywords(niche)
        top_keywords = keywords[:limit]
        avg_competition = 0
        if top_keywords: avg_competition = sum(k.get("competition", 0) for k in top_keywords) / len(top_keywords)
        results = {
            "niche": niche, "keywords": top_keywords,
            "search_volume_total": sum(k.get("search_volume", 0) for k in top_keywords),
            "competition_average": round(avg_competition, 2), "timestamp": datetime.now().isoformat()
        }
        return {"success": True, "results": results}
    except Exception as e:
        logger.error(f"Tool: Error analyzing keywords for {niche}: {e}", exc_info=True)
        return {"success": False, "error": f"Error analyzing keywords: {str(e)}"}


# --- Instantiate the ADK Agent ---
agent = Agent(
    name="market_analysis_adk", # ADK specific name
    description="Analyzes market trends, opportunities, competition, and keywords.",
    tools=[
        analyze_trends_tool,
        identify_opportunities_tool,
        evaluate_competition_tool,
        analyze_keywords_tool,
    ],
)

# Removed original class structure and run_async method
