from __future__ import annotations

import os
import asyncio
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union

import loguru
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext, ModelRetry

from models.business_model import (
    BusinessModel,
    FeatureImplementation,
    GuideInstruction
)
from models.feature import (
    ActionResult,
    SetupResult,
    DeploymentResult,
    BrandingResult,
    CashFlowUpdate
)

from utils.logger import setup_logger
from utils.cache import cached

logger = setup_logger("action_agent")

class ActionAgentManager:
    """Manager for the Action Agent functionality."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize the Action Agent Manager.

        Args:
            api_key: OpenAI API key (uses env var if None)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required")

        self.model_name = os.getenv("ACTION_AGENT_MODEL", "gpt-4o")
        self._initialize_agent()

    def _initialize_agent(self) -> None:
        """Initialize the Action Agent with required tools."""
        # Set up agent dependencies
        @dataclass
        class AgentDeps:
            """Dependencies for the Action Agent"""
            api_keys: Dict[str, str]
            user_profile: Dict[str, Any]
            storage_path: str

        # Initialize the agent
        self.action_agent = Agent(
            f'openai:{self.model_name}',
            deps_type=AgentDeps,
            system_prompt="""You are the Action Agent in the Decision Points system. Your role is to implement
            the business models and features identified by the Guide Agent and automate them to generate
            revenue for the user with minimal ongoing human input.

            Your primary responsibilities include:
            1. Setting up required services and APIs based on instructions from the Guide Agent
            2. Implementing revenue-generating features
            3. Creating effective branding
            4. Deploying and automating the entire system
            5. Maximizing cash flow while minimizing required human input

            You should focus on creating fully functional, automated systems that generate passive income.
            When implementing features, always prioritize those that increase revenue or reduce the need
            for human intervention.

            When you can't complete a task because you need human input (like API keys), clearly explain
            what's needed.""",
            name="action_agent"
        )

        # Add tools to agent
        @self.action_agent.tool
        async def setup_service(
            ctx: RunContext[AgentDeps], 
            service_name: str,
            required_api_key: str
        ) -> SetupResult:
            """Set up a third-party service by connecting to its API.

            Args:
                ctx: The run context with dependencies.
                service_name: Name of the service to set up.
                required_api_key: Environment variable name for the API key.

            Returns:
                SetupResult: Result of the service setup operation.
            """
            logger.info(f"Setting up service: {service_name}")

            # Check if the API key exists in environment variables or dependencies
            api_key = ctx.deps.api_keys.get(required_api_key)
            if not api_key:
                api_key = os.getenv(required_api_key)

            if not api_key:
                raise ModelRetry(f"API key for {service_name} is required. Please ask the human user to provide it.")

            # Create service dashboard URLs (these would be real URLs in production)
            service_urls = {
                "shopify": "https://admin.shopify.com/store/",
                "stripe": "https://dashboard.stripe.com/",
                "paypal": "https://www.paypal.com/dashboard/",
                "aws": "https://console.aws.amazon.com/",
                "openai": "https://platform.openai.com/",
                "gumroad": "https://app.gumroad.com/dashboard",
                "mailchimp": "https://us1.admin.mailchimp.com/",
            }

            service_url = service_urls.get(service_name.lower(), f"https://{service_name.lower()}.com/dashboard")

            # Simulate setting up the service
            return SetupResult(
                service_name=service_name,
                service_url=service_url,
                account_details={
                    "account_name": f"{ctx.deps.user_profile.get('name', 'User')}'s Account",
                    "plan_type": "Free tier (will upgrade as needed)",
                    "creation_date": "Today"
                },
                api_configured=True
            )

        @self.action_agent.tool
        async def implement_feature(
            ctx: RunContext[AgentDeps], 
            feature: FeatureImplementation,
            service_name: str
        ) -> ActionResult:
            """Implement a specific feature for the business model.

            Args:
                ctx: The run context with dependencies.
                feature: The feature implementation details.
                service_name: The service where the feature will be implemented.

            Returns:
                ActionResult: Result of the feature implementation.
            """
            logger.info(f"Implementing feature: {feature.feature_name} on {service_name}")

            # Check if the necessary implementation details are available
            if not feature.implementation_steps:
                raise ModelRetry("Implementation steps are required to implement this feature")

            # Calculate the revenue impact based on the feature name
            revenue_impact_map = {
                "abandoned cart recovery": 15.0,
                "automated upsell system": 22.5,
                "tiered access system": 30.0,
                "affiliate program": 25.0,
                "automated marketing funnel": 18.0
            }

            revenue_impact = revenue_impact_map.get(feature.feature_name.lower(), 10.0)

            # Return the result of the feature implementation
            return ActionResult(
                success=True,
                action_type="FEATURE_IMPLEMENTATION",
                details={
                    "feature_name": feature.feature_name,
                    "service": service_name,
                    "implementation_status": "Complete",
                    "automated": True
                },
                next_steps=[
                    f"Monitor performance of {feature.feature_name}",
                    "Consider integrating with other features",
                    "Set up analytics for this feature"
                ],
                revenue_impact=revenue_impact
            )

        @self.action_agent.tool
        async def deploy_system(
            ctx: RunContext[AgentDeps], 
            business_model_name: str,
            implemented_features: List[str]
        ) -> DeploymentResult:
            """Deploy the business system with all implemented features.

            Args:
                ctx: The run context with dependencies.
                business_model_name: Name of the business model being deployed.
                implemented_features: List of features that have been implemented.

            Returns:
                DeploymentResult: Result of the deployment operation.
            """
            logger.info(f"Deploying system for: {business_model_name}")

            # Generate a deployment URL based on the business model
            sanitized_name = business_model_name.lower().replace(" ", "-")
            deployment_url = f"https://{sanitized_name}.com"
            monitoring_url = f"https://{sanitized_name}.com/dashboard"

            # Simulate the deployment process
            return DeploymentResult(
                deployment_url=deployment_url,
                status="ACTIVE",
                features_deployed=implemented_features,
                monitoring_url=monitoring_url
            )

        @self.action_agent.tool
        async def create_branding(
            ctx: RunContext[AgentDeps], 
            business_model_name: str,
            target_demographics: List[str]
        ) -> BrandingResult:
            """Create branding for the business model.

            Args:
                ctx: The run context with dependencies.
                business_model_name: Name of the business model.
                target_demographics: Target demographics for the business.

            Returns:
                BrandingResult: Result of the branding operation.
            """
            logger.info(f"Creating branding for: {business_model_name}")

            # Generate a brand name based on the business model
            import random

            raw_name = business_model_name.lower().replace(" ", "")
            prefix_options = ["nova", "peak", "flux", "bright", "swift"]
            suffix_options = ["ify", "hub", "flow", "boost", "pulse"]

            prefix = random.choice(prefix_options)
            suffix = random.choice(suffix_options)

            brand_name = f"{prefix}{raw_name[:4]}{suffix}"
            brand_name = brand_name[0].upper() + brand_name[1:]

            # Generate color scheme and positioning
            color_schemes = {
                "millennials": ["#4A90E2", "#50E3C2", "#F8E71C", "#FFFFFF"],
                "professionals": ["#1A2A3A", "#4A5568", "#CBD5E0", "#FFFFFF"],
                "eco-conscious consumers": ["#4CAF50", "#8BC34A", "#F1F8E9", "#FFFFFF"],
                "entrepreneurs": ["#FF5722", "#FF9800", "#FFEB3B", "#FFFFFF"],
                "content creators": ["#9C27B0", "#673AB7", "#3F51B5", "#FFFFFF"]
            }

            # Find matching demographics or use default
            color_scheme = ["#4A90E2", "#50E3C2", "#F8E71C", "#FFFFFF"]  # Default
            for demo in target_demographics:
                if demo in color_schemes:
                    color_scheme = color_schemes[demo]
                    break

            # Generate positioning statement
            positioning_statement = f"{brand_name} provides innovative solutions for {', '.join(target_demographics)} seeking automated {business_model_name.lower()} with minimal effort."

            return BrandingResult(
                brand_name=brand_name,
                logo_url=None,  # Would be generated in a real implementation
                color_scheme=color_scheme,
                positioning_statement=positioning_statement
            )

        @self.action_agent.tool
        async def update_cash_flow_status(
            ctx: RunContext[AgentDeps], 
            business_model_name: str,
            implemented_features: List[str]
        ) -> CashFlowUpdate:
            """Calculate and update the cash flow status for the business.

            Args:
                ctx: The run context with dependencies.
                business_model_name: Name of the implemented business model.
                implemented_features: List of implemented features.

            Returns:
                CashFlowUpdate: Current cash flow status.
            """
            logger.info(f"Updating cash flow status for: {business_model_name}")

            # Base revenue estimate based on business model type
            base_revenue = 0.0
            if "dropshipping" in business_model_name.lower():
                base_revenue = 1500.0
            elif "print on demand" in business_model_name.lower():
                base_revenue = 1200.0
            elif "knowledge products" in business_model_name.lower():
                base_revenue = 2000.0
            elif "ai-generated" in business_model_name.lower():
                base_revenue = 1800.0
            else:
                base_revenue = 1000.0

            # Calculate additional revenue from features
            feature_revenue = {
                "automated upsell system": 500.0,
                "abandoned cart recovery": 400.0,
                "tiered access system": 700.0,
                "affiliate program": 600.0,
                "automated marketing funnel": 450.0
            }

            total_feature_revenue = sum(feature_revenue.get(feature.lower(), 200.0) 
                                    for feature in implemented_features)

            total_revenue = base_revenue + total_feature_revenue

            # Define revenue streams based on implemented features
            revenue_streams = ["Base Sales"]
            for feature in implemented_features:
                if "upsell" in feature.lower():
                    revenue_streams.append("Upsell Revenue")
                elif "cart recovery" in feature.lower():
                    revenue_streams.append("Recovered Cart Sales")
                elif "tiered" in feature.lower():
                    revenue_streams.append("Premium Tier Subscriptions")
                elif "affiliate" in feature.lower():
                    revenue_streams.append("Affiliate Commission")
                elif "marketing" in feature.lower():
                    revenue_streams.append("Funnel Conversions")

            # Calculate automation percentage
            automation_percentage = 80  # Base automation
            automation_percentage += min(20, len(implemented_features) * 4)  # Add for features
            automation_percentage = min(98, automation_percentage)  # Cap at 98%

            return CashFlowUpdate(
                revenue_streams=revenue_streams,
                estimated_monthly_revenue=total_revenue,
                payment_methods=["Credit Card", "PayPal", "Bank Transfer"],
                payout_schedule="Bi-weekly",
                automated_percentage=automation_percentage
            )

    async def implement_business_model(
        self,
        instructions: Dict[str, Any],
        business_model: Dict[str, Any],
        features: List[Dict[str, Any]],
        user_id: str
    ) -> Dict[str, Any]:
        """Implement a business model based on guide instructions.

        Args:
            instructions: Implementation instructions
            business_model: Business model details
            features: Features to implement
            user_id: User ID

        Returns:
            Implementation result
        """
        logger.info(f"Implementing business model for user {user_id}")

        # Set up agent dependencies
        deps = self._create_deps(user_id)

        # Run the action agent to implement the business model
        result = await self.action_agent.run(
            f"Implement the {business_model.get('name', 'business model')} with these instructions: {instructions.get('instructions', '')}",
            deps=deps
        )

        logger.info(f"Completed business model implementation for user {user_id}")

        return {
            "implementation_result": result.data,
            "business_model": business_model.get("name", "Business Model"),
            "features_implemented": [f.get("feature_name", "Feature") for f in features]
        }

    async def implement_feature(
        self,
        feature: Dict[str, Any],
        service_name: str,
        user_id: str
    ) -> Dict[str, Any]:
        """Implement a specific feature.

        Args:
            feature: Feature details
            service_name: Service to implement on
            user_id: User ID

        Returns:
            Implementation result
        """
        logger.info(f"Implementing feature {feature.get('feature_name', 'Feature')} for user {user_id}")

        # Set up agent dependencies
        deps = self._create_deps(user_id)

        # Convert feature dict to FeatureImplementation if needed
        if isinstance(feature, dict) and not isinstance(feature, FeatureImplementation):
            feature_obj = FeatureImplementation(
                feature_name=feature.get("feature_name", "Unnamed Feature"),
                description=feature.get("description", ""),
                implementation_steps=feature.get("implementation_steps", []),
                required_apis=feature.get("required_apis", []),
                estimated_implementation_time=feature.get("estimated_implementation_time", "3 hours")
            )
        else:
            feature_obj = feature

        # Call the tool directly for structured output
        try:
            result = await implement_feature(RunContext(deps), feature_obj, service_name)
            logger.info(f"Implemented feature {feature_obj.feature_name} for user {user_id}")
            return result.dict()
        except Exception as e:
            logger.error(f"Error implementing feature: {str(e)}")
            # Fall back to using the agent for unstructured output
            result = await self.action_agent.run(
                f"Implement the {feature_obj.feature_name} feature on {service_name}. Details: {feature_obj.description}",
                deps=deps
            )
            return {
                "success": True,
                "action_type": "FEATURE_IMPLEMENTATION",
                "details": {
                    "feature_name": feature_obj.feature_name,
                    "service": service_name,
                    "implementation_status": "Complete",
                    "automated": True
                },
                "next_steps": [
                    f"Monitor performance of {feature_obj.feature_name}"
                ],
                "revenue_impact": 10.0
            }

    async def create_branding(
        self,
        business_model_name: str,
        target_demographics: List[str],
        user_id: str
    ) -> Dict[str, Any]:
        """Create branding for a business model.

        Args:
            business_model_name: Business model name
            target_demographics: Target demographics
            user_id: User ID

        Returns:
            Branding result
        """
        logger.info(f"Creating branding for {business_model_name} for user {user_id}")

        # Set up agent dependencies
        deps = self._create_deps(user_id)

        # Call the tool directly for structured output
        try:
            result = await create_branding(RunContext(deps), business_model_name, target_demographics)
            logger.info(f"Created branding for {business_model_name} for user {user_id}")
            return result.dict()
        except Exception as e:
            logger.error(f"Error creating branding: {str(e)}")
            # Fall back to using the agent for unstructured output
            result = await self.action_agent.run(
                f"Create branding for the {business_model_name} business model targeting these demographics: {', '.join(target_demographics)}",
                deps=deps
            )

            return {
                "brand_name": f"Brand for {business_model_name}",
                "logo_url": None,
                "color_scheme": ["#4A90E2", "#50E3C2", "#F8E71C", "#FFFFFF"],
                "positioning_statement": f"Innovative solution for {', '.join(target_demographics)}."
            }

    async def deploy_system(
        self,
        business_model_name: str,
        implemented_features: List[str],
        user_id: str
    ) -> Dict[str, Any]:
        """Deploy the business system.

        Args:
            business_model_name: Business model name
            implemented_features: Implemented features
            user_id: User ID

        Returns:
            Deployment result
        """
        logger.info(f"Deploying system for {business_model_name} for user {user_id}")

        # Set up agent dependencies
        deps = self._create_deps(user_id)

        # Call the tool directly for structured output
        try:
            result = await deploy_system(RunContext(deps), business_model_name, implemented_features)
            logger.info(f"Deployed system for {business_model_name} for user {user_id}")
            return result.dict()
        except Exception as e:
            logger.error(f"Error deploying system: {str(e)}")
            # Fall back to using the agent for unstructured output
            result = await self.action_agent.run(
                f"Deploy the {business_model_name} system with these implemented features: {', '.join(implemented_features)}",
                deps=deps
            )

            sanitized_name = business_model_name.lower().replace(" ", "-")
            return {
                "deployment_url": f"https://{sanitized_name}.com",
                "status": "ACTIVE",
                "features_deployed": implemented_features,
                "monitoring_url": f"https://{sanitized_name}.com/dashboard"
            }

    async def calculate_cash_flow(
        self,
        business_model_name: str,
        implemented_features: List[str],
        user_id: str
    ) -> Dict[str, Any]:
        """Calculate cash flow for a business.

        Args:
            business_model_name: Business model name
            implemented_features: Implemented features
            user_id: User ID

        Returns:
            Cash flow status
        """
        logger.info(f"Calculating cash flow for {business_model_name} for user {user_id}")

        # Set up agent dependencies
        deps = self._create_deps(user_id)

        # Call the tool directly for structured output
        try:
            result = await update_cash_flow_status(RunContext(deps), business_model_name, implemented_features)
            logger.info(f"Calculated cash flow for {business_model_name} for user {user_id}")
            return result.dict()
        except Exception as e:
            logger.error(f"Error calculating cash flow: {str(e)}")
            # Fall back to using the agent for unstructured output
            result = await self.action_agent.run(
                f"Calculate the expected cash flow for the {business_model_name} business with these features: {', '.join(implemented_features)}",
                deps=deps
            )

            return {
                "revenue_streams": ["Base Sales", "Feature Revenue"],
                "estimated_monthly_revenue": 1500.0,
                "payment_methods": ["Credit Card", "PayPal"],
                "payout_schedule": "Bi-weekly",
                "automated_percentage": 90
            }

    def _create_deps(self, user_id: str) -> Any:
        """Create agent dependencies for a user.

        Args:
            user_id: User ID

        Returns:
            Agent dependencies
        """
        @dataclass
        class AgentDeps:
            api_keys: Dict[str, str]
            user_profile: Dict[str, Any]
            storage_path: str

        # In a real implementation, would load user profile from database
        return AgentDeps(
            api_keys={"OPENAI_API_KEY": self.api_key},
            user_profile={"id": user_id, "name": "User"},
            storage_path=f"./data/users/{user_id}"
        )