from __future__ import annotations

import os
import asyncio
from dataclasses import dataclass
from config import Config  # Import Config for model selection
from typing import Any, Dict, List, Optional, Union, TypeVar

import loguru
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext, ModelRetry, Tool

from models.business_model import (
    BusinessModel,
    MarketResearchResult,
    FeatureImplementation,
    HumanTaskRequest,
    GuideInstruction
)

from utils.logger import setup_logger
from utils.cache import cached

logger = setup_logger("guide_agent")

# Define AgentDeps at the module level
@dataclass
class AgentDeps:
    """Dependencies for the Guide Agent"""
    api_keys: Dict[str, str]
    user_profile: Dict[str, Any]
    storage_path: str

class GuideAgentManager:
    """Manager for the Guide Agent functionality."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize the Guide Agent Manager.

        Args:
            api_key: Gemini API key (uses env var if None)
        """
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("Google Gemini API key is required")

        # Select the model name from configuration (set via environment variable GUIDE_AGENT_MODEL)
        self.model_name = Config.GUIDE_AGENT_MODEL
        self._initialize_agent()

    def _initialize_agent(self) -> None:
        """Initialize the Guide Agent with required tools."""
        # Initialize the agent
        self.guide_agent = Agent(
            self.model_name,
            deps_type=AgentDeps,
            system_prompt="""You are the Guide Agent in the Decision Points system. Your role is to analyze markets, identify profitable
            business opportunities, and create detailed instructions for the Action Agent to implement these opportunities.

            Your primary responsibilities include:
            1. Conducting market research to identify top-performing business models, products, or services
            2. Analyzing which features drive revenue and would be most effective to implement
            3. Creating step-by-step instructions for the Action Agent to follow
            4. Identifying when human input is required and creating clear task requests

            You should always focus on opportunities that:
            - Can generate passive income with minimal ongoing human input
            - Have a clear path to implementation using available APIs and services
            - Can be fully automated once set up

            When you need the human to complete a task (like signing up for an API or service), create a clear
            task request with all necessary information.""",
            name="guide_agent"
        )

        # Add tools to agent
        @self.guide_agent.tool
        async def analyze_market_opportunities(ctx: RunContext[AgentDeps], market_segment: str) -> MarketResearchResult:
            """Analyze market opportunities in a particular segment to identify top-performing business models.

            Args:
                ctx: The run context with dependencies.
                market_segment: The market segment to analyze (e.g., 'e-commerce', 'online education', 'digital products')

            Returns:
                MarketResearchResult: Detailed analysis of market opportunities.
            """
            logger.info(f"Analyzing market opportunities for segment: {market_segment}")

            # In a real implementation, this might call external APIs or use a more sophisticated analysis
            # For demonstration, we'll return synthesized data based on the market segment

            if market_segment.lower() == "e-commerce":
                return MarketResearchResult(
                    top_performing_models=[
                        BusinessModel(
                            name="Dropshipping Specialty Items",
                            type="e-commerce",
                            potential_revenue=2500.0,
                            implementation_difficulty=6,
                            market_saturation=7,
                            required_apis=["Shopify", "Oberlo", "PayPal"]
                        ),
                        BusinessModel(
                            name="Print on Demand Personalized Products",
                            type="e-commerce",
                            potential_revenue=1800.0,
                            implementation_difficulty=4,
                            market_saturation=5,
                            required_apis=["Printful", "Etsy", "Stripe"]
                        )
                    ],
                    trending_keywords=["sustainable products", "personalized gifts", "home office accessories"],
                    target_demographics=["millennials", "home office workers", "eco-conscious consumers"],
                    revenue_generating_features=["personalization options", "subscription models", "bundle discounts"]
                )
            elif market_segment.lower() == "digital-products":
                return MarketResearchResult(
                    top_performing_models=[
                        BusinessModel(
                            name="Niche Knowledge Products",
                            type="digital_products",
                            potential_revenue=3200.0,
                            implementation_difficulty=3,
                            market_saturation=4,
                            required_apis=["Gumroad", "Stripe", "MailChimp"]
                        ),
                        BusinessModel(
                            name="AI-Generated Content Templates",
                            type="digital_products",
                            potential_revenue=2700.0,
                            implementation_difficulty=5,
                            market_saturation=3,
                            required_apis=["Gemini", "MemberStack", "Stripe"]
                        )
                    ],
                    trending_keywords=["passive income", "AI tools", "productivity templates", "learn new skills"],
                    target_demographics=["entrepreneurs", "content creators", "professionals"],
                    revenue_generating_features=["tiered pricing", "upsells", "affiliate programs"]
                )
            else:
                # Default response for other market segments
                return MarketResearchResult(
                    top_performing_models=[
                        BusinessModel(
                            name="Subscription Service",
                            type="recurring_revenue",
                            potential_revenue=1500.0,
                            implementation_difficulty=5,
                            market_saturation=6,
                            required_apis=["Stripe", "SendGrid", "AWS"]
                        )
                    ],
                    trending_keywords=["automation", "passive income", "recurring revenue"],
                    target_demographics=["online consumers", "small businesses"],
                    revenue_generating_features=["automation", "subscription tiers", "referral programs"]
                )

        @self.guide_agent.tool
        async def identify_revenue_features(
            ctx: RunContext[AgentDeps],
            business_model_name: str,
            market_data: MarketResearchResult
        ) -> List[FeatureImplementation]:
            """Identify specific features that would increase revenue for a given business model.

            Args:
                ctx: The run context with dependencies.
                business_model_name: The name of the business model to analyze.
                market_data: Market research data containing top performing models and features.

            Returns:
                List[FeatureImplementation]: List of features that could be implemented to increase revenue.
            """
            logger.info(f"Identifying revenue features for business model: {business_model_name}")

            # Find the business model in the market data
            business_model = next((model for model in market_data.top_performing_models
                                if model.name.lower() == business_model_name.lower()), None)

            if not business_model:
                raise ModelRetry(f"Business model '{business_model_name}' not found in market data")

            # Generate features based on the business model type
            features = []

            if business_model.type == "e-commerce":
                features.append(FeatureImplementation(
                    feature_name="Automated Upsell System",
                    description="System that suggests complementary products at checkout",
                    implementation_steps=[
                        "Integrate product tagging system",
                        "Create product relationship database",
                        "Implement checkout page modifications",
                        "Add upsell API endpoints"
                    ],
                    required_apis=["Shopify API", "Custom Database"],
                    estimated_implementation_time="4 hours"
                ))
                features.append(FeatureImplementation(
                    feature_name="Abandoned Cart Recovery",
                    description="Automatically emails customers who abandon their carts",
                    implementation_steps=[
                        "Set up email templates",
                        "Configure tracking scripts",
                        "Implement timing logic",
                        "Create conversion analytics"
                    ],
                    required_apis=["Email Service API", "Store API"],
                    estimated_implementation_time="3 hours"
                ))

            elif business_model.type == "digital_products":
                features.append(FeatureImplementation(
                    feature_name="Tiered Access System",
                    description="Multiple pricing tiers with different access levels",
                    implementation_steps=[
                        "Define tier benefits",
                        "Set up payment processing for multiple tiers",
                        "Create access control system",
                        "Implement upgrade paths"
                    ],
                    required_apis=["Payment Gateway API", "Authentication System"],
                    estimated_implementation_time="5 hours"
                ))
                features.append(FeatureImplementation(
                    feature_name="Affiliate Program",
                    description="System allowing others to promote products for commission",
                    implementation_steps=[
                        "Create affiliate registration system",
                        "Implement unique tracking links",
                        "Build commission calculation logic",
                        "Develop affiliate dashboard"
                    ],
                    required_apis=["Affiliate Tracking Service", "Payment API"],
                    estimated_implementation_time="6 hours"
                ))

            else:  # Default for other business models
                features.append(FeatureImplementation(
                    feature_name="Automated Marketing Funnel",
                    description="Series of automated emails to nurture prospects",
                    implementation_steps=[
                        "Set up email sequence templates",
                        "Configure triggers and timing",
                        "Implement lead scoring",
                        "Create conversion tracking"
                    ],
                    required_apis=["Email Marketing API", "CRM API"],
                    estimated_implementation_time="4 hours"
                ))

            return features

        @self.guide_agent.tool
        async def create_action_instructions(
            ctx: RunContext[AgentDeps],
            business_model: BusinessModel,
            selected_features: List[FeatureImplementation]
        ) -> GuideInstruction:
            """Create detailed instructions for the Action Agent to implement the business model and features.

            Args:
                ctx: The run context with dependencies.
                business_model: The business model to implement.
                selected_features: The features to implement for the business model.

            Returns:
                GuideInstruction: Detailed instructions for the Action Agent.
            """
            logger.info(f"Creating action instructions for business model: {business_model.name}")

            # Generate instructions based on the business model type and selected features
            if business_model.type == "e-commerce":
                return GuideInstruction(
                    instruction_type="MARKET_RESEARCH",
                    description=f"Implement a {business_model.name} store with focus on the selected revenue-generating features",
                    steps=[
                        f"Set up a new {business_model.name} store using Shopify or similar platform",
                        "Configure payment processing through Stripe and PayPal",
                        "Set up product categories based on trending keywords",
                        "Implement the selected features: " + ", ".join([f.feature_name for f in selected_features]),
                        "Configure analytics to track conversion rates"
                    ],
                    success_criteria=[
                        "Store is fully operational",
                        "Payment processing is configured",
                        "At least 10 products are listed",
                        "All selected features are implemented"
                    ],
                    expected_output="A fully functional e-commerce store with automated revenue generation capabilities"
                )
            elif business_model.type == "digital_products":
                return GuideInstruction(
                    instruction_type="FEATURE_IMPLEMENTATION",
                    description=f"Create and set up a {business_model.name} platform",
                    steps=[
                        "Set up a landing page to showcase digital products",
                        "Configure a payment and delivery system",
                        "Create product structures and templates",
                        "Implement automatic delivery of digital goods",
                        "Set up the selected features: " + ", ".join([f.feature_name for f in selected_features])
                    ],
                    success_criteria=[
                        "Landing page is live and optimized for conversion",
                        "Payment system is processing transactions",
                        "Digital product delivery is automated",
                        "Selected features are operational"
                    ],
                    expected_output="A digital product platform that generates passive income through automated sales and delivery"
                )
            else:
                return GuideInstruction(
                    instruction_type="DEPLOYMENT",
                    description=f"Deploy and automate the {business_model.name} system",
                    steps=[
                        "Configure the core business functionality",
                        "Set up payment processing and subscription management",
                        "Implement marketing automation",
                        "Deploy the selected features: " + ", ".join([f.feature_name for f in selected_features]),
                        "Set up monitoring and analytics"
                    ],
                    success_criteria=[
                        "System is fully operational",
                        "Payment processing works end-to-end",
                        "Marketing automation is functioning",
                        "All features are implemented correctly"
                    ],
                    expected_output="An automated system that generates recurring revenue with minimal human intervention"
                )

        @self.guide_agent.tool
        async def request_human_task(
            ctx: RunContext[AgentDeps],
            service_name: str,
            reason: str,
            required_fields: List[str]
        ) -> HumanTaskRequest:
            """Create a request for the human to complete a necessary task like API signup.

            Args:
                ctx: The run context with dependencies.
                service_name: Name of the service or API that needs human setup.
                reason: Why this service is needed for the business model.
                required_fields: Information fields that need to be collected.

            Returns:
                HumanTaskRequest: Structured request for the human to complete.
            """
            logger.info(f"Creating human task request for service: {service_name}")

            # Map common services to their signup URLs
            service_urls = {
                "shopify": "https://www.shopify.com/signup",
                "stripe": "https://dashboard.stripe.com/register",
                "paypal": "https://www.paypal.com/business/sign-up",
                "aws": "https://aws.amazon.com/free/",
                "gemini": "https://aistudio.google.com/app/apikey",
                "gumroad": "https://app.gumroad.com/signup",
                "mailchimp": "https://login.mailchimp.com/signup/",
                "etsy": "https://www.etsy.com/sell",
                "printful": "https://www.printful.com/auth/register"
            }

            # Get the signup URL or use a default search URL
            signup_url = service_urls.get(service_name.lower(), f"https://www.google.com/search?q=signup+for+{service_name}")

            # Create environment variable name
            env_var_name = f"{service_name.upper().replace(' ', '_')}_API_KEY"

            return HumanTaskRequest(
                task_title=f"Sign up for {service_name}",
                task_description=f"We need to use {service_name} for {reason}. Please sign up for an account and obtain API credentials.",
                api_service_name=service_name,
                signup_url=signup_url,
                required_fields=required_fields,
                environment_variable_name=env_var_name
            )

    @cached(timeout=1800)  # Cache for 30 minutes
    async def analyze_market(self, market_segment: str, user_id: str) -> Dict[str, Any]:
        """Analyze a market segment to find business opportunities.

        Args:
            market_segment: Market segment to analyze
            user_id: User ID for personalization

        Returns:
            Analysis results
        """
        logger.info(f"Starting market analysis for segment '{market_segment}' for user {user_id}")

        # Set up agent dependencies
        deps = self._create_deps(user_id)

        # Run the guide agent to analyze the market
        result = await self.guide_agent.run(
            f"Please analyze the market opportunities in {market_segment} and identify the top performing business models.",
            deps=deps
        )

        # Extract market research data directly from agent result
        market_data = await self.guide_agent.run(
            f"Based on your previous analysis of {market_segment}, please provide a structured summary of the top business models, their features, and target demographics.",
            deps=deps
        )

        logger.info(f"Completed market analysis for segment '{market_segment}' for user {user_id}")

        return {
            "analysis": result.data,
            "market_data": market_data.data,
            "segment": market_segment
        }

    async def identify_features(
        self,
        business_model_name: str,
        market_data: Dict[str, Any],
        user_id: str
    ) -> List[Dict[str, Any]]:
        """Identify revenue-generating features for a business model.

        Args:
            business_model_name: Name of the business model
            market_data: Market research data
            user_id: User ID for personalization

        Returns:
            List of features
        """
        logger.info(f"Identifying features for business model '{business_model_name}' for user {user_id}")

        # Set up agent dependencies
        deps = self._create_deps(user_id)

        # Convert market_data to MarketResearchResult if needed
        if isinstance(market_data, dict) and not isinstance(market_data, MarketResearchResult):
            # Convert dictionary to MarketResearchResult
            market_research = self._dict_to_market_research(market_data)
        else:
            market_research = market_data

        # Use the guide agent to identify features
        result = await self.guide_agent.run(
            f"Please identify the top revenue-generating features for the {business_model_name} business model.",
            deps=deps
        )

        # For more structured data, we could directly call the tool
        # features = await identify_revenue_features(RunContext(deps), business_model_name, market_research)

        logger.info(f"Identified features for business model '{business_model_name}' for user {user_id}")

        # Parse the result to extract features
        # In a real implementation, this would be more sophisticated
        return [
            {
                "feature_name": "Automated Upsell System",
                "description": "System that suggests complementary products at checkout",
                "revenue_impact": 500.0,
                "implementation_difficulty": 6,
                "implementation_steps": [
                    "Integrate product tagging system",
                    "Create product relationship database",
                    "Implement checkout page modifications",
                    "Add upsell API endpoints"
                ]
            },
            {
                "feature_name": "Abandoned Cart Recovery",
                "description": "Automatically emails customers who abandon their carts",
                "revenue_impact": 400.0,
                "implementation_difficulty": 4,
                "implementation_steps": [
                    "Set up email templates",
                    "Configure tracking scripts",
                    "Implement timing logic",
                    "Create conversion analytics"
                ]
            }
        ]

    async def create_instructions(
        self,
        business_model: Dict[str, Any],
        selected_features: List[Dict[str, Any]],
        user_id: str
    ) -> Dict[str, Any]:
        """Create implementation instructions for a business model and features.

        Args:
            business_model: Business model details
            selected_features: Selected features to implement
            user_id: User ID for personalization

        Returns:
            Implementation instructions
        """
        logger.info(f"Creating implementation instructions for user {user_id}")

        # Set up agent dependencies
        deps = self._create_deps(user_id)

        # Convert business model dict to BusinessModel if needed
        if isinstance(business_model, dict) and not isinstance(business_model, BusinessModel):
            model = BusinessModel(
                name=business_model.get("name", "Unnamed Business Model"),
                type=business_model.get("type", "generic"),
                potential_revenue=float(business_model.get("potential_revenue", 1000.0)),
                implementation_difficulty=int(business_model.get("implementation_difficulty", 5)),
                market_saturation=int(business_model.get("market_saturation", 5)),
                required_apis=business_model.get("required_apis", [])
            )
        else:
            model = business_model

        # Convert feature dicts to FeatureImplementation if needed
        feature_objs = []
        for feature in selected_features:
            if isinstance(feature, dict) and not isinstance(feature, FeatureImplementation):
                feature_objs.append(FeatureImplementation(
                    feature_name=feature.get("feature_name", "Unnamed Feature"),
                    description=feature.get("description", ""),
                    implementation_steps=feature.get("implementation_steps", []),
                    required_apis=feature.get("required_apis", []),
                    estimated_implementation_time=feature.get("estimated_implementation_time", "3 hours")
                ))
            else:
                feature_objs.append(feature)

        # If you want more structured output, you could directly call the tool:
        # instructions = await create_action_instructions(RunContext(deps), model, feature_objs)

        # Run the guide agent to create instructions
        result = await self.guide_agent.run(
            f"Please create detailed implementation instructions for the {model.name} business model with the following features: "
            f"{', '.join([f.feature_name for f in feature_objs])}",
            deps=deps
        )

        logger.info(f"Created implementation instructions for user {user_id}")

        return {
            "instructions": result.data,
            "business_model": model.name,
            "features": [f.feature_name for f in feature_objs]
        }

    async def identify_human_tasks(
        self,
        business_model: Dict[str, Any],
        features: List[Dict[str, Any]],
        user_id: str
    ) -> List[Dict[str, Any]]:
        """Identify tasks that require human input.

        Args:
            business_model: Business model details
            features: Features to implement
            user_id: User ID

        Returns:
            List of human tasks
        """
        logger.info(f"Identifying human tasks for user {user_id}")

        # Set up agent dependencies
        deps = self._create_deps(user_id)

        # Run the guide agent to identify human tasks
        result = await self.guide_agent.run(
            f"Please identify all tasks that require human input for implementing the {business_model.get('name', 'business model')} "
            f"with features: {', '.join([f.get('feature_name', 'feature') for f in features])}. "
            f"Create a human task request for each required service or API.",
            deps=deps
        )

        # In a real implementation, you would parse the result to get structured tasks
        # For demonstration, we'll return a fixed set of tasks

        required_apis = business_model.get("required_apis", [])
        human_tasks = []

        for api in required_apis:
            human_tasks.append({
                "task_title": f"Sign up for {api}",
                "task_description": f"We need to use {api} for implementing the {business_model.get('name', 'business model')}. Please sign up for an account and obtain API credentials.",
                "api_service_name": api,
                "signup_url": f"https://www.google.com/search?q=signup+for+{api.lower().replace(' ', '+')}",
                "required_fields": ["API Key", "Account ID"],
                "environment_variable_name": f"{api.upper().replace(' ', '_')}_API_KEY"
            })

        logger.info(f"Identified {len(human_tasks)} human tasks for user {user_id}")

        return human_tasks

    def _create_deps(self, user_id: str) -> AgentDeps:
        """Create agent dependencies for a user.

        Args:
            user_id: User ID

        Returns:
            Agent dependencies
        """
        # In a real implementation, would load user profile from database
        return AgentDeps(
            api_keys={"GOOGLE_API_KEY": self.api_key},
            user_profile={"id": user_id, "name": "User"},
            storage_path=f"./data/users/{user_id}"
        )

    def _dict_to_market_research(self, data: Dict[str, Any]) -> MarketResearchResult:
        """Convert dictionary to MarketResearchResult.

        Args:
            data: Dictionary with market research data

        Returns:
            MarketResearchResult object
        """
        models = []
        for model_data in data.get("top_performing_models", []):
            if isinstance(model_data, dict):
                models.append(BusinessModel(
                    name=model_data.get("name", "Unnamed Model"),
                    type=model_data.get("type", "generic"),
                    potential_revenue=float(model_data.get("potential_revenue", 1000.0)),
                    implementation_difficulty=int(model_data.get("implementation_difficulty", 5)),
                    market_saturation=int(model_data.get("market_saturation", 5)),
                    required_apis=model_data.get("required_apis", [])
                ))

        return MarketResearchResult(
            top_performing_models=models,
            trending_keywords=data.get("trending_keywords", []),
            target_demographics=data.get("target_demographics", []),
            revenue_generating_features=data.get("revenue_generating_features", [])
        )
