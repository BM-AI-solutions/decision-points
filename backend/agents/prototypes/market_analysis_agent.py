"""
Market Analysis Agent - Specialized AI agent for market trend analysis.

This module implements the Market Analysis Agent, which:
1. Analyzes market trends and opportunities
2. Identifies profitable niches
3. Evaluates competition and saturation
4. Reports findings back to the Orchestrator
"""

import json
import logging
import random
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
import backend.config as config
from backend.utils.api_client import APIClient, APIError
import asyncio


class MarketAnalysisAgent:
    """
    The Market Analysis Agent analyzes market trends, identifies opportunities,
    and provides intelligence to the Orchestrator for strategy formulation.
    """
    
    def __init__(self, api_keys: Optional[Dict[str, str]] = None):
        """
        Initialize the Market Analysis Agent with optional API keys.
        
        Args:
            api_keys: Dictionary of API keys for market data sources
        """
        self.api_keys = api_keys or {}
        self.cached_data = {}
        self.last_analysis = {}
        
        # Log initialization
        logger.info("Market Analysis Agent initialized")
        self.market_api_client = APIClient(
            base_url=config.Config.MARKET_DATA_API_BASE_URL,
            api_key=config.Config.MARKET_DATA_API_KEY
        )

    async def fetch_trend_data(self, niche: str) -> Optional[Dict[str, Any]]:
        """Fetch real trend data from market data API."""
        try:
            # Example endpoint and params, adjust based on actual API
            endpoint = f"trends/{niche}"
            response = await self.market_api_client.get(endpoint)
            # Assume response contains 'trends' dict
            if response and 'trends' in response:
                return response['trends']
        except APIError as e:
            logger.warning(f"Market data API error: {e}")
        except Exception as e:
            logger.warning(f"Unexpected error fetching market data: {e}")
        return None

    
    def analyze_trends(self, niche: str, depth: str = "standard") -> Dict[str, Any]:
        """
        Analyze trends in a specific niche.
        """
        logger.info(f"Analyzing {depth} trends for {niche} niche")

        cache_key = f"{niche}_{depth}"
        if cache_key in self.cached_data and (datetime.now().timestamp() - self.cached_data[cache_key]["timestamp"] < 3600):
            logger.info(f"Using cached trend data for {niche}")
            return self.cached_data[cache_key]["data"]

        # Try to fetch real trend data asynchronously
        loop = asyncio.get_event_loop()
        real_data = loop.run_until_complete(self.fetch_trend_data(niche))
        if real_data:
            logger.info(f"Fetched real trend data for {niche}")
            self.cached_data[cache_key] = {
                "timestamp": datetime.now().timestamp(),
                "data": real_data
            }
            return real_data

        # Fallback to mock data
        logger.info(f"Falling back to mock trend data for {niche}")
        time.sleep(0.5)
        trends = self._generate_trend_data(niche, depth)
        self.cached_data[cache_key] = {
            "timestamp": datetime.now().timestamp(),
            "data": trends
        }
        return trends

    def analyze_trends(self, niche: str, depth: str = "standard") -> Dict[str, Any]:
        """
        Analyze trends in a specific niche.
        
        Args:
            niche: Market niche to analyze (e.g., "technology", "fitness")
            depth: Analysis depth ("standard" or "deep")
            
        Returns:
            Dictionary with trend analysis results
        """
        logger.info(f"Analyzing {depth} trends for {niche} niche")
        
        # In Phase 2, this will connect to real market data sources
        # For now, return mocked trend analysis
        
        # Check if we have cached data for this niche
        cache_key = f"{niche}_{depth}"
        if cache_key in self.cached_data and (datetime.now().timestamp() - self.cached_data[cache_key]["timestamp"] < 3600):
            logger.info(f"Using cached trend data for {niche}")
            return self.cached_data[cache_key]["data"]
        
        # Simulate API call delay
        time.sleep(0.5)
        
        # Generate trend data based on niche
        trends = self._generate_trend_data(niche, depth)
        
        # Cache the results
        self.cached_data[cache_key] = {
            "timestamp": datetime.now().timestamp(),
            "data": trends
        }
        
        # Store as last analysis
        self.last_analysis = {
            "niche": niche,
            "depth": depth,
            "timestamp": datetime.now().isoformat(),
            "results": trends
        }
        
        return trends
    
    def identify_opportunities(self, niches: List[str] = None) -> List[Dict[str, Any]]:
        """
        Identify business opportunities across multiple niches.
        
        Args:
            niches: List of niches to analyze (if None, uses default set)
            
        Returns:
            List of opportunity dictionaries with metrics
        """
        default_niches = [
            "technology", "health", "finance", "education", 
            "e-commerce", "sustainability", "productivity"
        ]
        
        niches = niches or default_niches
        logger.info(f"Identifying opportunities across {len(niches)} niches")
        
        opportunities = []
        
        for niche in niches:
            # Analyze trends for this niche
            trends = self.analyze_trends(niche)
            
            # Generate opportunities based on trends
            niche_opportunities = self._extract_opportunities(niche, trends)
            opportunities.extend(niche_opportunities)
        
        # Sort by potential revenue (descending)
        opportunities.sort(key=lambda x: x["potential_revenue"], reverse=True)
        
        return opportunities
    
    def evaluate_competition(self, niche: str, business_type: str) -> Dict[str, Any]:
        """
        Evaluate competition level in a specific niche and business type.
        
        Args:
            niche: Market niche to analyze
            business_type: Type of business model
            
        Returns:
            Dictionary with competition analysis
        """
        logger.info(f"Evaluating competition for {business_type} in {niche} niche")
        
        # In Phase 2, this will use real competitive analysis
        # For now, return mocked competition data
        
        # Simulate API call delay
        time.sleep(0.3)
        
        # Competition levels vary by niche and business type
        competition_levels = {
            "technology": {"affiliate_marketing": 8, "digital_product": 7, "saas": 9},
            "health": {"affiliate_marketing": 9, "digital_product": 8, "saas": 6},
            "finance": {"affiliate_marketing": 9, "digital_product": 7, "saas": 8},
            "education": {"affiliate_marketing": 7, "digital_product": 9, "saas": 6},
            "e-commerce": {"affiliate_marketing": 8, "digital_product": 6, "saas": 7},
            "sustainability": {"affiliate_marketing": 5, "digital_product": 6, "saas": 7},
            "productivity": {"affiliate_marketing": 7, "digital_product": 7, "saas": 8}
        }
        
        # Get competition level or default to 7
        competition_level = competition_levels.get(niche, {}).get(business_type, 7)
        
        # Generate top competitors
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
    
    def analyze_keywords(self, niche: str, limit: int = 10) -> Dict[str, Any]:
        """
        Analyze keywords for a specific niche.
        
        Args:
            niche: Market niche to analyze
            limit: Maximum number of keywords to return
            
        Returns:
            Dictionary with keyword analysis
        """
        logger.info(f"Analyzing keywords for {niche} niche")
        
        # In Phase 2, this will use real keyword research APIs
        # For now, return mocked keyword data
        
        # Simulate API call delay
        time.sleep(0.4)
        
        # Generate keywords based on niche
        keywords = self._generate_keywords(niche)
        
        # Limit the number of keywords
        top_keywords = keywords[:limit]
        
        return {
            "niche": niche,
            "keywords": top_keywords,
            "search_volume_total": sum(k["search_volume"] for k in top_keywords),
            "competition_average": sum(k["competition"] for k in top_keywords) / len(top_keywords),
            "timestamp": datetime.now().isoformat()
        }
    
    def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a task assigned by the Orchestrator.
        
        Args:
            task: Task dictionary with action and parameters
            
        Returns:
            Results dictionary
        """
        action = task.get("action")
        
        if action == "analyze_trends":
            niche = task.get("niche", "technology")
            depth = task.get("depth", "standard")
            results = self.analyze_trends(niche, depth)
            return {
                "task_id": task.get("id", "unknown"),
                "action": action,
                "niche": niche,
                "results": results,
                "success": True,
                "timestamp": datetime.now().isoformat()
            }
        
        elif action == "identify_opportunities":
            niches = task.get("niches")
            results = self.identify_opportunities(niches)
            return {
                "task_id": task.get("id", "unknown"),
                "action": action,
                "niches": niches,
                "results": results,
                "success": True,
                "timestamp": datetime.now().isoformat()
            }
        
        elif action == "evaluate_competition":
            niche = task.get("niche", "technology")
            business_type = task.get("business_type", "affiliate_marketing")
            results = self.evaluate_competition(niche, business_type)
            return {
                "task_id": task.get("id", "unknown"),
                "action": action,
                "niche": niche,
                "business_type": business_type,
                "results": results,
                "success": True,
                "timestamp": datetime.now().isoformat()
            }
        
        elif action == "analyze_keywords":
            niche = task.get("niche", "technology")
            limit = task.get("limit", 10)
            results = self.analyze_keywords(niche, limit)
            return {
                "task_id": task.get("id", "unknown"),
                "action": action,
                "niche": niche,
                "results": results,
                "success": True,
                "timestamp": datetime.now().isoformat()
            }
        
        else:
            logger.warning(f"Unknown action: {action}")
            return {
                "task_id": task.get("id", "unknown"),
                "action": action,
                "success": False,
                "error": f"Unknown action: {action}",
                "timestamp": datetime.now().isoformat()
            }
    
    def _generate_trend_data(self, niche: str, depth: str) -> Dict[str, Any]:
        """
        Generate trend data for a specific niche.
        
        Args:
            niche: Market niche
            depth: Analysis depth
            
        Returns:
            Dictionary with trend data
        """
        # Trend data varies by niche
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
        
        # Get base data for this niche or use technology as default
        base_data = trend_data.get(niche, trend_data["technology"])
        
        # Add more detailed data for deep analysis
        if depth == "deep":
            # Add audience demographics
            base_data["demographics"] = self._generate_demographics(niche)
            
            # Add more detailed segments
            base_data["growing_segments"].extend(self._generate_additional_segments(niche, True))
            base_data["declining_segments"].extend(self._generate_additional_segments(niche, False))
            
            # Add competitive landscape
            base_data["competitive_landscape"] = self._generate_competitive_landscape(niche)
            
            # Add pricing analysis
            base_data["pricing_analysis"] = self._generate_pricing_analysis(niche)
        
        # Add common fields
        base_data["niche"] = niche
        base_data["analysis_depth"] = depth
        base_data["timestamp"] = datetime.now().isoformat()
        
        return base_data
    
    def _extract_opportunities(self, niche: str, trends: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract business opportunities from trend data.
        
        Args:
            niche: Market niche
            trends: Trend data dictionary
            
        Returns:
            List of opportunity dictionaries
        """
        opportunities = []
        
        # Generate opportunities from growing segments
        for segment in trends.get("growing_segments", []):
            # Determine business type based on segment and niche
            business_type = self._determine_business_type(segment, niche)
            
            # Generate potential revenue based on growth rate
            growth_rate = trends.get("growth_rate", 10.0)
            base_revenue = random.randint(1000, 5000)
            potential_revenue = int(base_revenue * (1 + growth_rate / 100))
            
            # Generate difficulty based on segment and niche
            difficulty = self._generate_difficulty(segment, niche)
            
            # Generate risk level
            risk_level = self._determine_risk_level(difficulty, potential_revenue)
            
            # Create opportunity
            opportunity = {
                "name": f"{segment} {business_type.replace('_', ' ').title()}",
                "type": business_type,
                "niche": niche,
                "segment": segment,
                "potential_revenue": potential_revenue,
                "implementation_difficulty": difficulty,
                "market_saturation": self._calculate_saturation(difficulty),
                "risk_level": risk_level
            }
            
            opportunities.append(opportunity)
        
        return opportunities
    
    def _determine_business_type(self, segment: str, niche: str) -> str:
        """
        Determine the most suitable business type for a segment and niche.
        
        Args:
            segment: Market segment
            niche: Market niche
            
        Returns:
            Business type string
        """
        # Map of segments to likely business types
        segment_types = {
            "AI tools": "saas",
            "no-code platforms": "saas",
            "cybersecurity": "digital_product",
            "mental wellness": "digital_product",
            "home fitness": "digital_product",
            "nutrition tracking": "saas",
            "crypto education": "digital_product",
            "financial literacy": "digital_product",
            "passive income": "affiliate_marketing",
            "skill certifications": "digital_product",
            "cohort courses": "digital_product",
            "specialized tutorials": "digital_product",
            "niche marketplaces": "e-commerce",
            "subscription boxes": "e-commerce",
            "sustainable products": "e-commerce",
            "zero waste products": "e-commerce",
            "sustainable fashion": "e-commerce",
            "eco-education": "digital_product",
            "AI assistants": "saas",
            "focus tools": "saas",
            "knowledge management": "saas"
        }
        
        # Get business type or choose randomly
        if segment in segment_types:
            return segment_types[segment]
        else:
            return random.choice(["affiliate_marketing", "digital_product", "saas", "e-commerce"])
    
    def _generate_difficulty(self, segment: str, niche: str) -> int:
        """
        Generate implementation difficulty score for a segment and niche.
        
        Args:
            segment: Market segment
            niche: Market niche
            
        Returns:
            Difficulty score (1-10)
        """
        # Base difficulties by business type
        base_difficulties = {
            "affiliate_marketing": 5,
            "digital_product": 7,
            "saas": 9,
            "e-commerce": 6
        }
        
        # Determine business type
        business_type = self._determine_business_type(segment, niche)
        
        # Get base difficulty
        base = base_difficulties.get(business_type, 7)
        
        # Add random variation (-1 to +1)
        variation = random.randint(-1, 1)
        
        # Ensure difficulty is between 1-10
        return max(1, min(10, base + variation))
    
    def _determine_risk_level(self, difficulty: int, revenue: int) -> str:
        """
        Determine risk level based on difficulty and potential revenue.
        
        Args:
            difficulty: Implementation difficulty (1-10)
            revenue: Potential monthly revenue
            
        Returns:
            Risk level string
        """
        # Calculate risk score
        risk_score = difficulty - (revenue / 1000)
        
        # Determine risk level
        if risk_score > 5:
            return "high"
        elif risk_score > 2:
            return "medium"
        else:
            return "low"
    
    def _calculate_saturation(self, competition_level: int) -> int:
        """
        Calculate market saturation based on competition level.
        
        Args:
            competition_level: Competition level (1-10)
            
        Returns:
            Saturation level (1-10)
        """
        # Add random variation (-1 to +1)
        variation = random.randint(-1, 1)
        
        # Ensure saturation is between 1-10
        return max(1, min(10, competition_level + variation))
    
    def _generate_competitors(self, niche: str, business_type: str) -> List[Dict[str, Any]]:
        """
        Generate top competitors for a niche and business type.
        
        Args:
            niche: Market niche
            business_type: Type of business model
            
        Returns:
            List of competitor dictionaries
        """
        # Number of competitors to generate
        num_competitors = random.randint(3, 5)
        
        competitors = []
        
        for i in range(num_competitors):
            # Generate competitor name
            name = self._generate_competitor_name(niche, business_type)
            
            # Generate market share and monthly revenue
            market_share = round(random.uniform(5.0, 25.0), 1)
            monthly_revenue = random.randint(5000, 50000)
            
            competitors.append({
                "name": name,
                "market_share": market_share,
                "monthly_revenue": monthly_revenue,
                "years_active": random.randint(1, 10)
            })
        
        # Sort by market share (descending)
        competitors.sort(key=lambda x: x["market_share"], reverse=True)
        
        return competitors
    
    def _generate_competitor_name(self, niche: str, business_type: str) -> str:
        """
        Generate a competitor name based on niche and business type.
        
        Args:
            niche: Market niche
            business_type: Type of business model
            
        Returns:
            Competitor name string
        """
        # Prefixes by niche
        prefixes = {
            "technology": ["Tech", "Digital", "Cyber", "Code", "Dev"],
            "health": ["Health", "Vital", "Wellness", "Fit", "Nutri"],
            "finance": ["Finance", "Money", "Wealth", "Capital", "Invest"],
            "education": ["Learn", "Edu", "Skill", "Academy", "Master"],
            "e-commerce": ["Shop", "Store", "Market", "Buy", "Retail"],
            "sustainability": ["Eco", "Green", "Sustain", "Earth", "Bio"],
            "productivity": ["Focus", "Task", "Time", "Boost", "Flow"]
        }
        
        # Suffixes by business type
        suffixes = {
            "affiliate_marketing": ["Affiliate", "Partner", "Promote", "Refer", "Link"],
            "digital_product": ["Course", "Guide", "Academy", "School", "Learn"],
            "saas": ["App", "Tool", "Suite", "Cloud", "Platform"],
            "e-commerce": ["Shop", "Store", "Market", "Goods", "Products"]
        }
        
        # Get random prefix and suffix
        prefix = random.choice(prefixes.get(niche, ["Brand"]))
        suffix = random.choice(suffixes.get(business_type, ["Pro"]))
        
        # Generate name
        return f"{prefix}{suffix}"
    
    def _generate_entry_barriers(self, niche: str, business_type: str) -> List[str]:
        """
        Generate entry barriers for a niche and business type.
        
        Args:
            niche: Market niche
            business_type: Type of business model
            
        Returns:
            List of entry barrier strings
        """
        # Common entry barriers
        common_barriers = [
            "High initial investment",
            "Technical expertise required",
            "Established brand loyalty",
            "Complex regulations",
            "Network effects favoring incumbents",
            "High customer acquisition costs",
            "Intellectual property protections",
            "Economies of scale"
        ]
        
        # Specific barriers by business type
        specific_barriers = {
            "affiliate_marketing": [
                "Saturated affiliate networks",
                "Commission rate competition",
                "Cookie duration limitations"
            ],
            "digital_product": [
                "Content creation expertise",
                "High-quality production requirements",
                "Platform fees and restrictions"
            ],
            "saas": [
                "Development costs",
                "Ongoing maintenance requirements",
                "User onboarding complexity"
            ],
            "e-commerce": [
                "Inventory management",
                "Shipping logistics",
                "Return handling costs"
            ]
        }
        
        # Select 2-3 common barriers
        selected_barriers = random.sample(common_barriers, random.randint(2, 3))
        
        # Add 1-2 specific barriers
        if business_type in specific_barriers:
            selected_barriers.extend(random.sample(specific_barriers[business_type], 
                                                 min(len(specific_barriers[business_type]), random.randint(1, 2))))
        
        return selected_barriers
    
    def _generate_demographics(self, niche: str) -> Dict[str, Any]:
        """
        Generate audience demographics for a niche.
        
        Args:
            niche: Market niche
            
        Returns:
            Demographics dictionary
        """
        # Default demographics
        default_demographics = {
            "age_groups": {
                "18-24": 15,
                "25-34": 30,
                "35-44": 25,
                "45-54": 15,
                "55+": 15
            },
            "gender_split": {
                "male": 55,
                "female": 45
            },
            "income_levels": {
                "low": 20,
                "medium": 50,
                "high": 30
            },
            "education_levels": {
                "high_school": 25,
                "bachelors": 45,
                "masters": 20,
                "phd": 10
            }
        }
        
        # Niche-specific demographics
        niche_demographics = {
            "technology": {
                "age_groups": {
                    "18-24": 20,
                    "25-34": 35,
                    "35-44": 25,
                    "45-54": 15,
                    "55+": 5
                },
                "gender_split": {
                    "male": 65,
                    "female": 35
                }
            },
            "health": {
                "age_groups": {
                    "18-24": 15,
                    "25-34": 30,
                    "35-44": 25,
                    "45-54": 20,
                    "55+": 10
                },
                "gender_split": {
                    "male": 40,
                    "female": 60
                }
            },
            "finance": {
                "age_groups": {
                    "18-24": 10,
                    "25-34": 25,
                    "35-44": 30,
                    "45-54": 20,
                    "55+": 15
                },
                "income_levels": {
                    "low": 15,
                    "medium": 45,
                    "high": 40
                }
            }
        }
        
        # Start with default demographics
        demographics = default_demographics.copy()
        
        # Update with niche-specific demographics if available
        if niche in niche_demographics:
            for key, value in niche_demographics[niche].items():
                demographics[key] = value
        
        return demographics
    
    def _generate_additional_segments(self, niche: str, growing: bool) -> List[str]:
        """
        Generate additional market segments for a niche.
        
        Args:
            niche: Market niche
            growing: Whether to generate growing or declining segments
            
        Returns:
            List of segment strings
        """
        # Additional segments by niche
        additional_segments = {
            "technology": {
                "growing": ["AR/VR solutions", "blockchain applications", "edge computing"],
                "declining": ["traditional CMS", "on-premise software", "generic mobile apps"]
            },
            "health": {
                "growing": ["personalized nutrition", "sleep optimization", "biohacking"],
                "declining": ["general fitness apps", "generic meal plans", "broad supplements"]
            },
            "finance": {
                "growing": ["DeFi education", "sustainable investing", "financial independence"],
                "declining": ["traditional stock picking", "general budgeting", "forex trading"]
            },
            "education": {
                "growing": ["microlearning", "community-based learning", "AI-assisted education"],
                "declining": ["general online courses", "static e-books", "non-interactive content"]
            }
        }
        
        # Get segments for this niche or return empty list
        niche_segments = additional_segments.get(niche, {})
        segment_type = "growing" if growing else "declining"
        
        return niche_segments.get(segment_type, [])
    
    def _generate_competitive_landscape(self, niche: str) -> Dict[str, Any]:
        """
        Generate competitive landscape for a niche.
        
        Args:
            niche: Market niche
            
        Returns:
            Competitive landscape dictionary
        """
        return {
            "total_competitors": random.randint(50, 200),
            "market_leaders": random.randint(5, 15),
            "new_entrants_monthly": random.randint(3, 12),
            "average_lifespan": f"{random.randint(2, 5)} years",
            "consolidation_trend": random.choice(["increasing", "stable", "decreasing"])
        }
    
    def _generate_pricing_analysis(self, niche: str) -> Dict[str, Any]:
        """
        Generate pricing analysis for a niche.
        
        Args:
            niche: Market niche
            
        Returns:
            Pricing analysis dictionary
        """
        return {
            "average_price_point": f"${random.randint(20, 100)}",
            "price_sensitivity": random.randint(1, 10),
            "subscription_model_adoption": f"{random.randint(40, 90)}%",
            "freemium_conversion_rate": f"{random.randint(2, 8)}%",
            "pricing_trend": random.choice(["increasing", "stable", "decreasing"])
        }
    
    def _generate_keywords(self, niche: str) -> List[Dict[str, Any]]:
        """
        Generate keywords for a niche.
        
        Args:
            niche: Market niche
            
        Returns:
            List of keyword dictionaries
        """
        # Base keywords by niche
        base_keywords = {
            "technology": ["software tools", "AI assistant", "coding platform", "tech solution"],
            "health": ["fitness program", "nutrition plan", "wellness app", "health tracker"],
            "finance": ["investment strategy", "passive income", "financial freedom", "wealth building"],
            "education": ["online course", "skill development", "learning platform", "certification"],
            "e-commerce": ["online store", "product marketplace", "subscription box", "direct to consumer"],
            "sustainability": ["eco-friendly products", "sustainable living", "zero waste", "green solutions"],
            "productivity": ["time management", "focus app", "productivity system", "workflow optimization"]
        }
        
        # Get base keywords for this niche or use technology as default
        keywords_list = base_keywords.get(niche, base_keywords["technology"])
        
        # Generate additional keywords
        additional_keywords = [
            f"best {niche} {random.choice(['tools', 'solutions', 'platforms', 'services'])}",
            f"{niche} for {random.choice(['beginners', 'professionals', 'businesses', 'students'])}",
            f"how to {random.choice(['start', 'improve', 'optimize', 'scale'])} {niche}",
            f"{niche} {random.choice(['tips', 'tricks', 'hacks', 'strategies'])}",
            f"affordable {niche} {random.choice(['tools', 'solutions', 'platforms', 'services'])}"
        ]
        
        keywords_list.extend(additional_keywords)
        
        # Create keyword objects
        keywords = []
        for keyword in keywords_list:
            keywords.append({
                "keyword": keyword,
                "search_volume": random.randint(1000, 50000),
                "competition": round(random.uniform(0.1, 0.9), 2),
                "cpc": round(random.uniform(0.5, 10.0), 2)
            })
        
        # Sort by search volume (descending)
        keywords.sort(key=lambda x: x["search_volume"], reverse=True)
        
        return keywords


# Example usage
if __name__ == "__main__":
    # Initialize agent
    agent = MarketAnalysisAgent()
    
    # Analyze trends
    trends = agent.analyze_trends("technology", "deep")
    print(f"Trends: {trends['growing_segments']}")
    
    # Identify opportunities
    opportunities = agent.identify_opportunities(["technology", "education"])
    print(f"Found {len(opportunities)} opportunities")
    
    # Execute a task
    task = {
        "id": "task-123",
        "action": "analyze_keywords",
        "niche": "productivity",
        "limit": 5
    }
    result = agent.execute_task(task)
    print(json.dumps(result, indent=2))