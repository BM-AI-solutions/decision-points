from __future__ import annotations as _annotations

import os
import asyncio
import json
from dataclasses import dataclass
from typing import Any, Literal, Optional, Union, List, Dict

import logfire
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext, ModelRetry

# Configure logging - will only send logs if token is present
logfire.configure(send_to_logfire='if-token-present')

# Define our dependency container for sharing resources between agents
@dataclass
class AgentDeps:
    """Dependencies for the Decision Points agents"""
    api_keys: Dict[str, str]
    user_profile: Dict[str, Any]
    storage_path: str

# ----------------------
# Guide Agent Definition
# ----------------------

class BusinessModel(BaseModel):
    """A potential business model identified by the Guide Agent"""
    name: str = Field(..., description="Name of the business model")
    type: str = Field(..., description="Type of business model (e.g., e-commerce, SaaS, etc.)")
    potential_revenue: float = Field(..., description="Estimated monthly revenue potential in USD")
    implementation_difficulty: int = Field(..., description="Difficulty to implement on a scale of 1-10")
    market_saturation: int = Field(..., description="Market saturation level on a scale of 1-10")
    required_apis: List[str] = Field(default_factory=list, description="List of APIs needed to implement this model")

class MarketResearchResult(BaseModel):
    """Results of market research conducted by the Guide Agent"""
    top_performing_models: List[BusinessModel] = Field(..., description="List of top performing business models")
    trending_keywords: List[str] = Field(..., description="Trending keywords in this market")
    target_demographics: List[str] = Field(..., description="Target demographics for these business models")
    revenue_generating_features: List[str] = Field(..., description="Features that are most effective at generating revenue")

class FeatureImplementation(BaseModel):
    """A feature implementation plan created by the Guide Agent"""
    feature_name: str = Field(..., description="Name of the feature to implement")
    description: str = Field(..., description="Description of the feature and its benefits")
    implementation_steps: List[str] = Field(..., description="Step-by-step guide to implement this feature")
    required_apis: List[str] = Field(default_factory=list, description="List of APIs needed for this feature")
    estimated_implementation_time: str = Field(..., description="Estimated time to implement (e.g., '2 hours')")

class HumanTaskRequest(BaseModel):
    """A request for the human to perform a necessary task"""
    task_title: str = Field(..., description="Short title of the task")
    task_description: str = Field(..., description="Detailed description of what the human needs to do")
    api_service_name: str = Field(..., description="Name of the service/API that requires setup")
    signup_url: str = Field(..., description="URL where the human can sign up or complete the task")
    required_fields: List[str] = Field(..., description="List of fields or information the human needs to provide")
    environment_variable_name: str = Field(..., description="Name of the environment variable to store the API key/credentials")

class GuideInstruction(BaseModel):
    """An instruction from the Guide Agent to the Action Agent"""
    instruction_type: Literal["MARKET_RESEARCH", "FEATURE_IMPLEMENTATION", "BRANDING", "DEPLOYMENT"]
    description: str = Field(..., description="Detailed description of what should be done")
    steps: List[str] = Field(..., description="Specific steps to follow")
    success_criteria: List[str] = Field(..., description="How to determine if the task was successful")
    expected_output: str = Field(..., description="Description of the expected output format")

guide_agent = Agent(
    'openai:gpt-4o',
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
    result_type=str,  # Default to string response
    name="guide_agent"
)

# Research tools for Guide Agent
@guide_agent.tool
async def analyze_market_opportunities(ctx: RunContext[AgentDeps], market_segment: str) -> MarketResearchResult:
    """Analyze market opportunities in a particular segment to identify top-performing business models.

    Args:
        ctx: The run context with dependencies.
        market_segment: The market segment to analyze (e.g., 'e-commerce', 'online education', 'digital products')

    Returns:
        MarketResearchResult: Detailed analysis of market opportunities.
    """
    with logfire.span(f"analyzing market opportunities in {market_segment}"):
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
        elif market_segment.lower() == "digital products":
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
                        required_apis=["OpenAI", "MemberStack", "Stripe"]
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

@guide_agent.tool
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
    with logfire.span(f"identifying revenue features for {business_model_name}"):
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

@guide_agent.tool
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
    with logfire.span(f"creating action instructions for {business_model.name}"):
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

@guide_agent.tool
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
    with logfire.span(f"creating human task request for {service_name}"):
        # Map common services to their signup URLs
        service_urls = {
            "shopify": "https://www.shopify.com/signup",
            "stripe": "https://dashboard.stripe.com/register",
            "paypal": "https://www.paypal.com/business/sign-up",
            "aws": "https://aws.amazon.com/free/",
            "openai": "https://platform.openai.com/signup",
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

# ----------------------
# Action Agent Definition
# ----------------------

class ActionResult(BaseModel):
    """Result of an action performed by the Action Agent"""
    success: bool = Field(..., description="Whether the action was successful")
    action_type: str = Field(..., description="Type of action performed")
    details: Dict[str, Any] = Field(..., description="Details of the action result")
    next_steps: List[str] = Field(..., description="Recommended next steps")
    revenue_impact: Optional[float] = Field(None, description="Estimated impact on revenue, if applicable")

class SetupResult(BaseModel):
    """Result of a setup operation performed by the Action Agent"""
    service_name: str = Field(..., description="Name of the service that was set up")
    service_url: str = Field(..., description="URL of the service dashboard")
    account_details: Dict[str, str] = Field(..., description="Details of the account that was set up")
    api_configured: bool = Field(..., description="Whether the API was successfully configured")

class DeploymentResult(BaseModel):
    """Result of a deployment operation performed by the Action Agent"""
    deployment_url: str = Field(..., description="URL where the system is deployed")
    status: str = Field(..., description="Status of the deployment")
    features_deployed: List[str] = Field(..., description="Features that were successfully deployed")
    monitoring_url: Optional[str] = Field(None, description="URL for monitoring the deployed system")

class BrandingResult(BaseModel):
    """Result of a branding operation performed by the Action Agent"""
    brand_name: str = Field(..., description="Selected brand name")
    logo_url: Optional[str] = Field(None, description="URL of the generated logo")
    color_scheme: List[str] = Field(..., description="Selected color scheme")
    positioning_statement: str = Field(..., description="Brand positioning statement")

class CashFlowUpdate(BaseModel):
    """Update on the cash flow status of the implemented system"""
    revenue_streams: List[str] = Field(..., description="Active revenue streams")
    estimated_monthly_revenue: float = Field(..., description="Estimated monthly revenue in USD")
    payment_methods: List[str] = Field(..., description="Configured payment methods")
    payout_schedule: str = Field(..., description="When payments are received")
    automated_percentage: int = Field(..., description="Percentage of the process that is automated")

action_agent = Agent(
    'openai:gpt-4o',
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
    result_type=str,  # Default to string response
    name="action_agent"
)

@action_agent.tool
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
    with logfire.span(f"setting up service {service_name}"):
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

@action_agent.tool
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
    with logfire.span(f"implementing feature {feature.feature_name} on {service_name}"):
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

@action_agent.tool
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
    with logfire.span(f"deploying system for {business_model_name}"):
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

@action_agent.tool
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
    with logfire.span(f"creating branding for {business_model_name}"):
        # Generate a brand name based on the business model
        raw_name = business_model_name.lower().replace(" ", "")
        prefix_options = ["nova", "peak", "flux", "bright", "swift"]
        suffix_options = ["ify", "hub", "flow", "boost", "pulse"]

        import random
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

@action_agent.tool
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
    with logfire.span(f"updating cash flow status for {business_model_name}"):
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

# Function to run the multi-agent workflow
async def run_decision_points_system(market_segment: str):
    """Run the complete Decision Points system workflow."""
    # Initialize dependencies
    deps = AgentDeps(
        api_keys={},
        user_profile={"name": "User"},
        storage_path="./decision_points_data"
    )

    print("🔍 Starting Guide Agent - Market Analysis...")
    # First: Have the Guide Agent analyze market opportunities
    market_analysis = await guide_agent.run(
        f"Please analyze the market opportunities in {market_segment} and identify the top performing business models.",
        deps=deps
    )
    print(f"✅ Guide Agent Market Analysis Complete:\n{market_analysis.data}\n")

    # Use Guide Agent to research specific market opportunities
    market_data = await analyze_market_opportunities(RunContext(deps), market_segment)

    if not market_data or not market_data.top_performing_models:
        print("❌ No viable business models found in this market segment.")
        return

    # Select the top business model
    top_model = market_data.top_performing_models[0]
    print(f"🏆 Selected Business Model: {top_model.name}")

    # Identify revenue-generating features
    print("🔍 Identifying revenue-generating features...")
    features = await identify_revenue_features(RunContext(deps), top_model.name, market_data)
    print(f"✅ Identified {len(features)} revenue-generating features")

    # Create instructions for the Action Agent
    print("📝 Creating instructions for Action Agent...")
    instructions = await create_action_instructions(RunContext(deps), top_model, features)
    print(f"✅ Created instructions of type: {instructions.instruction_type}")

    # Check if we need human input for APIs
    human_tasks = []
    for api in top_model.required_apis:
        print(f"🔑 Checking if {api} API is required...")
        if api not in deps.api_keys:
            print(f"👤 Human input needed for {api} API")
            task = await request_human_task(
                RunContext(deps),
                api,
                f"implementing {top_model.name}",
                ["API Key", "Account ID", "Secret Key"]
            )
            human_tasks.append(task)

    # Display human tasks
    if human_tasks:
        print("\n🚨 Human Tasks Required:")
        for i, task in enumerate(human_tasks):
            print(f"\nTask {i+1}: {task.task_title}")
            print(f"Description: {task.task_description}")
            print(f"URL: {task.signup_url}")
            print(f"Required Fields: {', '.join(task.required_fields)}")
            print(f"Set environment variable: {task.environment_variable_name}")

    # Pass instructions to Action Agent
    print("\n🚀 Starting Action Agent - Implementation...")
    implementation_result = await action_agent.run(
        f"Implement the {top_model.name} business model with the following instructions: {json.dumps(instructions.dict())}",
        deps=deps
    )
    print(f"✅ Action Agent Implementation Progress:\n{implementation_result.data}\n")

    # Simulate feature implementation
    implemented_feature_names = [feature.feature_name for feature in features[:2]]  # Implement first 2 features
    print(f"🔧 Implementing features: {', '.join(implemented_feature_names)}")

    for feature in features[:2]:
        result = await implement_feature(
            RunContext(deps),
            feature,
            top_model.required_apis[0] if top_model.required_apis else "Generic Platform"
        )
        print(f"  ✅ Implemented {feature.feature_name} - Revenue Impact: ${result.revenue_impact}")

    # Create branding
    print("🎨 Creating branding...")
    branding = await create_branding(
        RunContext(deps),
        top_model.name,
        market_data.target_demographics
    )
    print(f"✅ Created brand: {branding.brand_name}")
    print(f"   Positioning: {branding.positioning_statement}")

    # Deploy the system
    print("🚀 Deploying system...")
    deployment = await deploy_system(
        RunContext(deps),
        top_model.name,
        implemented_feature_names
    )
    print(f"✅ Deployed at: {deployment.deployment_url}")
    print(f"   Monitoring at: {deployment.monitoring_url}")

    # Calculate cash flow
    print("💰 Calculating potential cash flow...")
    cash_flow = await update_cash_flow_status(
        RunContext(deps),
        top_model.name,
        implemented_feature_names
    )
    print(f"✅ Monthly Revenue Estimate: ${cash_flow.estimated_monthly_revenue:.2f}")
    print(f"   Revenue Streams: {', '.join(cash_flow.revenue_streams)}")
    print(f"   Process Automation: {cash_flow.automated_percentage}%")

    # Final summary from Guide Agent
    print("\n📊 Generating final summary...")
    summary = await guide_agent.run(
        f"Create a summary of the implemented system: {top_model.name} with brand {branding.brand_name}, "
        f"features {', '.join(implemented_feature_names)}, and estimated monthly revenue of ${cash_flow.estimated_monthly_revenue:.2f}",
        deps=deps
    )
    print(f"\n📋 FINAL SUMMARY:\n{summary.data}")

if __name__ == "__main__":
    # Run the complete system
    asyncio.run(run_decision_points_system("digital products"))