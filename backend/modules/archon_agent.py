"""
Archon Agent - AI agent for automated passive income generation through the Archon MCP server

This module provides a powerful agent specifically designed for:
1. Creating autonomous income streams with minimal human intervention
2. Implementing subscription-based business models
3. Managing and optimizing passive income systems
4. Scaling profitable streams for maximum revenue

The agent integrates with the Archon MCP server to leverage advanced AI capabilities
for creating sustainable income streams. It can work independently or as part of the
dual agent system with the Guide and Action agents.
"""

import os
import json
import asyncio
from typing import Dict, List, Any, Optional, Union, Tuple

class ArchonAgent:
    """
    AI agent for automated passive income generation powered by Gemini (Google Gemini AI) and Archon
    """
    
    def __init__(self, api_key: Optional[str] = None, debug_mode: bool = False):
        """
        Initialize the ArchonAgent
        
        Args:
            api_key: Optional API key for external services
            debug_mode: If True, provides verbose logging
        """
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        self.debug_mode = debug_mode
        self.income_streams = []
        self.subscription_tiers = []
        self.integrations = {
            "stripe": False,
            "shopify": False,
            "memberstack": False,
            "gumroad": False
        }
        
    def create_income_stream(self, 
                          stream_type: str, 
                          name: str, 
                          description: str,
                          automation_level: int = 8,
                          required_services: List[str] = None) -> Dict[str, Any]:
        """
        Create a new passive income stream based on the specified type
        
        Args:
            stream_type: Type of income stream (e.g. 'membership', 'digital_product', 'affiliate')
            name: Name of the income stream
            description: Description of the income stream
            automation_level: Level of automation from 1-10
            required_services: List of services required for implementation
            
        Returns:
            Details of the created income stream
        """
        if required_services is None:
            required_services = []
            
        # Validate the stream type
        valid_types = ['membership', 'digital_product', 'affiliate', 'saas', 'marketplace']
        if stream_type not in valid_types:
            raise ValueError(f"Invalid stream type: {stream_type}. Must be one of {valid_types}")
        
        # Create the income stream
        stream = {
            "id": len(self.income_streams) + 1,
            "name": name,
            "type": stream_type,
            "description": description,
            "automation_level": min(10, max(1, automation_level)),  # Ensure between 1-10
            "required_services": required_services,
            "status": "created",
            "monthly_revenue": 0.0,
            "automated_percentage": min(automation_level * 10, 95),  # Max 95% automated
            "implementation_steps": self._generate_implementation_steps(stream_type),
            "integrations": []
        }
        
        self.income_streams.append(stream)
        return stream
    
    def _generate_implementation_steps(self, stream_type: str) -> List[str]:
        """
        Generate implementation steps based on the stream type
        
        Args:
            stream_type: Type of income stream
            
        Returns:
            List of implementation steps
        """
        steps = {
            "membership": [
                "Create membership tiers and pricing",
                "Set up Stripe subscription integration",
                "Build membership dashboard",
                "Create automated content delivery system",
                "Implement retention strategies"
            ],
            "digital_product": [
                "Create digital product and assets",
                "Set up payment processing",
                "Implement automated delivery system",
                "Create upsell and cross-sell flows",
                "Establish affiliate program"
            ],
            "affiliate": [
                "Research and select high-converting products",
                "Create affiliate landing pages",
                "Implement tracking and analytics",
                "Set up automated email sequences",
                "Optimize conversion rates"
            ],
            "saas": [
                "Define core SaaS functionality",
                "Implement subscription billing",
                "Create user onboarding flow",
                "Set up automated customer support",
                "Develop retention and upsell systems"
            ],
            "marketplace": [
                "Define marketplace model and fee structure",
                "Implement vendor and customer registration",
                "Create listing and discovery system",
                "Set up secure payment processing",
                "Implement automated quality control"
            ]
        }
        
        return steps.get(stream_type, ["Define model", "Create implementation plan", "Execute implementation"])
    
    def create_subscription_tier(self, 
                              name: str, 
                              price: float, 
                              features: List[str],
                              billing_cycle: str = "monthly") -> Dict[str, Any]:
        """
        Create a subscription tier for the passive income system
        
        Args:
            name: Name of the subscription tier
            price: Price of the subscription
            features: List of features included in this tier
            billing_cycle: Billing cycle (monthly, yearly, etc.)
            
        Returns:
            Details of the created subscription tier
        """
        # Validate billing cycle
        valid_cycles = ['monthly', 'yearly', 'quarterly']
        if billing_cycle not in valid_cycles:
            raise ValueError(f"Invalid billing cycle: {billing_cycle}. Must be one of {valid_cycles}")
        
        # Create the subscription tier
        tier = {
            "id": len(self.subscription_tiers) + 1,
            "name": name,
            "price": price,
            "billing_cycle": billing_cycle,
            "features": features,
            "subscribers": 0,
            "monthly_revenue": 0.0,
            "annual_revenue": 0.0,
            "churn_rate": 5.0  # Default 5% churn rate
        }
        
        self.subscription_tiers.append(tier)
        return tier
    
    def integrate_stripe(self, 
                       api_key: str, 
                       webhook_secret: Optional[str] = None) -> Dict[str, Any]:
        """
        Integrate Stripe for payment processing
        
        Args:
            api_key: Stripe API key
            webhook_secret: Optional Stripe webhook secret
            
        Returns:
            Status of the integration
        """
        # In a real implementation, this would validate the API key
        # and configure the Stripe integration
        
        self.integrations["stripe"] = True
        
        return {
            "service": "stripe",
            "status": "connected",
            "configuration": {
                "payment_methods": ["credit_card", "debit_card"],
                "subscriptions_enabled": True,
                "webhooks_configured": webhook_secret is not None
            }
        }
    
    def forecast_revenue(self, 
                       months: int = 12, 
                       growth_rate: float = 5.0) -> Dict[str, Any]:
        """
        Forecast revenue for all income streams
        
        Args:
            months: Number of months to forecast
            growth_rate: Monthly growth rate percentage
            
        Returns:
            Revenue forecast and projections
        """
        # Calculate baseline monthly revenue from all streams
        baseline_revenue = sum(stream.get("monthly_revenue", 0) for stream in self.income_streams)
        
        # If no existing revenue, estimate based on subscription tiers
        if baseline_revenue == 0 and self.subscription_tiers:
            # Assume 10 initial subscribers per tier for estimation
            initial_subscribers = 10
            for tier in self.subscription_tiers:
                tier["subscribers"] = initial_subscribers
                
                # Calculate monthly revenue for this tier
                monthly_price = tier["price"]
                if tier["billing_cycle"] == "yearly":
                    monthly_price = tier["price"] / 12
                elif tier["billing_cycle"] == "quarterly":
                    monthly_price = tier["price"] / 3
                
                tier["monthly_revenue"] = monthly_price * initial_subscribers
                tier["annual_revenue"] = tier["monthly_revenue"] * 12
                
                baseline_revenue += tier["monthly_revenue"]
        
        # If still no revenue, use a default starting amount
        if baseline_revenue == 0:
            baseline_revenue = 500.0  # Default starting revenue
            
        # Generate monthly projections
        monthly_projections = []
        current_revenue = baseline_revenue
        
        for month in range(1, months + 1):
            current_revenue *= (1 + (growth_rate / 100))  # Apply monthly growth
            
            monthly_projections.append({
                "month": month,
                "revenue": round(current_revenue, 2),
                "growth": f"{growth_rate:.1f}%"
            })
        
        # Calculate total and average metrics
        total_revenue = sum(month["revenue"] for month in monthly_projections)
        average_monthly_revenue = total_revenue / months
        
        return {
            "baseline_monthly_revenue": baseline_revenue,
            "growth_rate_monthly": growth_rate,
            "forecast_months": months,
            "total_projected_revenue": round(total_revenue, 2),
            "average_monthly_revenue": round(average_monthly_revenue, 2),
            "final_monthly_revenue": round(monthly_projections[-1]["revenue"], 2),
            "monthly_projections": monthly_projections
        }
    
    def generate_archon_agent_prompt(self, income_stream: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a prompt for the Archon MCP server to implement an income stream
        
        Args:
            income_stream: The income stream to implement
            
        Returns:
            Prompt for the Archon MCP server
        """
        stream_type = income_stream["type"]
        
        # Define template prompts based on stream type
        templates = {
            "membership": {
                "system_prompt": """You are a passive income expert who specializes in creating and optimizing 
                membership sites. Your goal is to implement a fully automated membership platform that generates 
                recurring revenue with minimal human intervention. Focus on creating systems for content delivery, 
                member retention, and consistent value delivery.""",
                
                "user_prompt": f"""Create a comprehensive implementation plan for a membership site called 
                "{income_stream['name']}". 

                Description: {income_stream['description']}
                
                Your implementation should:
                1. Be at least {income_stream['automated_percentage']}% automated
                2. Include multiple membership tiers
                3. Handle payment processing with Stripe
                4. Deliver content automatically based on membership level
                5. Include retention strategies to minimize cancellations
                
                Provide detailed, step-by-step instructions that could be followed to implement this 
                membership site and generate passive income."""
            },
            
            "digital_product": {
                "system_prompt": """You are a digital product creation and marketing expert who specializes in 
                creating automated income streams through digital products. Your goal is to implement systems 
                that create, market, and deliver digital products with minimal human intervention.""",
                
                "user_prompt": f"""Create a comprehensive implementation plan for a digital product business called 
                "{income_stream['name']}". 

                Description: {income_stream['description']}
                
                Your implementation should:
                1. Be at least {income_stream['automated_percentage']}% automated
                2. Include product creation systems
                3. Implement automated marketing funnels
                4. Handle secure delivery of digital products
                5. Include upsell and cross-sell opportunities
                
                Provide detailed, step-by-step instructions that could be followed to implement this 
                digital product business and generate passive income."""
            },
            
            "affiliate": {
                "system_prompt": """You are an affiliate marketing expert who specializes in creating 
                automated affiliate income streams. Your goal is to implement systems that identify, promote,
                and optimize affiliate offers with minimal human intervention.""",
                
                "user_prompt": f"""Create a comprehensive implementation plan for an affiliate marketing business called 
                "{income_stream['name']}". 

                Description: {income_stream['description']}
                
                Your implementation should:
                1. Be at least {income_stream['automated_percentage']}% automated
                2. Include methods for finding high-converting affiliate offers
                3. Implement automated traffic and lead generation
                4. Create conversion-optimized landing pages
                5. Include tracking and optimization systems
                
                Provide detailed, step-by-step instructions that could be followed to implement this 
                affiliate marketing business and generate passive income."""
            },
            
            "saas": {
                "system_prompt": """You are a SaaS development and marketing expert who specializes in 
                creating automated software-as-a-service businesses. Your goal is to implement systems 
                that develop, market, and support SaaS products with minimal human intervention.""",
                
                "user_prompt": f"""Create a comprehensive implementation plan for a SaaS business called 
                "{income_stream['name']}". 

                Description: {income_stream['description']}
                
                Your implementation should:
                1. Be at least {income_stream['automated_percentage']}% automated
                2. Include core SaaS functionality development
                3. Implement subscription and billing management
                4. Create user onboarding and support systems
                5. Include marketing and growth automation
                
                Provide detailed, step-by-step instructions that could be followed to implement this 
                SaaS business and generate passive income."""
            },
            
            "marketplace": {
                "system_prompt": """You are a marketplace development expert who specializes in creating 
                two-sided marketplaces that generate passive income. Your goal is to implement systems 
                that attract vendors and customers while automating operations.""",
                
                "user_prompt": f"""Create a comprehensive implementation plan for a marketplace business called 
                "{income_stream['name']}". 

                Description: {income_stream['description']}
                
                Your implementation should:
                1. Be at least {income_stream['automated_percentage']}% automated
                2. Include vendor and customer acquisition systems
                3. Implement secure payment processing
                4. Create listing and discovery mechanisms
                5. Include automated quality control and dispute resolution
                
                Provide detailed, step-by-step instructions that could be followed to implement this 
                marketplace business and generate passive income."""
            }
        }
        
        # Use default template if specific type not found
        template = templates.get(stream_type, {
            "system_prompt": """You are a passive income expert who specializes in creating automated 
            income systems. Your goal is to implement profitable business models that generate income 
            with minimal human intervention.""",
            
            "user_prompt": f"""Create a comprehensive implementation plan for a passive income business called 
            "{income_stream['name']}". 

            Description: {income_stream['description']}
            
            Your implementation should:
            1. Be at least {income_stream['automated_percentage']}% automated
            2. Generate consistent monthly revenue
            3. Require minimal ongoing maintenance
            4. Include scalability options
            5. Leverage automation and AI wherever possible
            
            Provide detailed, step-by-step instructions that could be followed to implement this 
            business and generate passive income."""
        })
        
        # Add implementation steps to the prompt
        steps_text = "\n".join([f"- {step}" for step in income_stream["implementation_steps"]])
        template["user_prompt"] += f"\n\nThe key implementation steps include:\n{steps_text}"
        
        return template
    
    def generate_agent_config(self, income_stream: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a configuration for the Archon agent to implement an income stream
        
        Args:
            income_stream: The income stream to implement
            
        Returns:
            Configuration for the Archon agent
        """
        # Generate prompts
        prompts = self.generate_archon_agent_prompt(income_stream)
        
        # Define tools based on stream type
        tools = ["web_research", "code_generation", "content_creation", "web_development"]
        
        if income_stream["type"] == "membership":
            tools.extend(["stripe_integration", "content_management", "email_automation"])
        elif income_stream["type"] == "digital_product":
            tools.extend(["digital_product_creation", "email_automation", "payment_processing"])
        elif income_stream["type"] == "affiliate":
            tools.extend(["traffic_analysis", "landing_page_optimization", "analytics"])
        elif income_stream["type"] == "saas":
            tools.extend(["software_development", "subscription_management", "user_support"])
        elif income_stream["type"] == "marketplace":
            tools.extend(["two_sided_marketplace", "payment_processing", "quality_control"])
            
        # Create configuration
        config = {
            "agent_name": f"{income_stream['name']}_agent",
            "system_prompt": prompts["system_prompt"],
            "user_prompt": prompts["user_prompt"],
            "tools": tools,
            "parameters": {
                "temperature": 0.7,
                "max_tokens": 4000,
                "stream_type": income_stream["type"],
                "automation_level": income_stream["automation_level"],
                "required_services": income_stream["required_services"]
            }
        }
        
        return config
    
    def get_run_agent_json(self, income_stream: Dict[str, Any]) -> str:
        """
        Get the JSON configuration for the run_agent command in Archon MCP
        
        Args:
            income_stream: The income stream to implement
            
        Returns:
            JSON string for the run_agent command
        """
        config = self.generate_agent_config(income_stream)
        
        run_agent_json = {
            "agent": {
                "name": config["agent_name"],
                "description": f"Agent for implementing {income_stream['name']} passive income stream",
                "instructions": config["system_prompt"]
            },
            "task": {
                "description": config["user_prompt"],
                "tools": config["tools"],
                "parameters": config["parameters"]
            },
            "output_format": {
                "type": "structured",
                "schema": {
                    "implementation_plan": "array",
                    "revenue_streams": "array",
                    "automation_level": "number",
                    "required_services": "array",
                    "estimated_monthly_revenue": "number"
                }
            }
        }
        
        return json.dumps(run_agent_json, indent=2)
        
    def estimate_income_potential(self, income_stream: Dict[str, Any]) -> Dict[str, Any]:
        """
        Estimate the income potential for a given income stream
        
        Args:
            income_stream: The income stream to analyze
            
        Returns:
            Income potential estimates
        """
        # Base revenue estimates by stream type (monthly)
        base_revenue = {
            "membership": 2000.0,
            "digital_product": 1500.0,
            "affiliate": 1200.0,
            "saas": 2500.0,
            "marketplace": 3000.0
        }.get(income_stream["type"], 1000.0)
        
        # Adjust based on automation level
        automation_factor = income_stream["automation_level"] / 10
        automation_adjusted = base_revenue * (0.8 + (automation_factor * 0.4))
        
        # Calculate revenue projections
        monthly_revenue = round(automation_adjusted, 2)
        annual_revenue = monthly_revenue * 12
        
        # Calculate expected effort (hours/week)
        weekly_effort = round(10 - (income_stream["automation_level"] * 0.8), 1)
        weekly_effort = max(0.5, weekly_effort)  # Minimum 0.5 hours/week
        
        # Calculate ROI (Annual Revenue / (Weekly Effort * 52 weeks * $50/hour))
        hourly_rate = 50  # Assumed hourly value of time
        annual_effort_value = weekly_effort * 52 * hourly_rate
        roi = round((annual_revenue / annual_effort_value) * 100, 2)
        
        return {
            "monthly_revenue_estimate": monthly_revenue,
            "annual_revenue_estimate": annual_revenue,
            "weekly_effort_hours": weekly_effort,
            "roi_percentage": roi,
            "automation_percentage": income_stream["automated_percentage"],
            "scaling_potential": "High" if roi > 300 else "Medium" if roi > 150 else "Low"
        }
    
    def implement_income_stream(self, income_stream_id: int) -> Dict[str, Any]:
        """
        Prepare for implementing an income stream with the Archon MCP server
        
        Args:
            income_stream_id: ID of the income stream to implement
            
        Returns:
            Implementation details including the Archon agent configuration
        """
        # Find the income stream
        income_stream = next((s for s in self.income_streams if s["id"] == income_stream_id), None)
        if not income_stream:
            raise ValueError(f"Income stream with ID {income_stream_id} not found")
        
        # Generate the run_agent JSON for Archon MCP
        run_agent_json = self.get_run_agent_json(income_stream)
        
        # Estimate income potential
        income_potential = self.estimate_income_potential(income_stream)
        
        # Update the income stream status
        income_stream["status"] = "ready_for_implementation"
        income_stream["monthly_revenue"] = income_potential["monthly_revenue_estimate"]
        
        return {
            "income_stream": income_stream,
            "income_potential": income_potential,
            "archon_run_agent_json": run_agent_json,
            "next_steps": [
                "Run the Archon agent using the provided JSON configuration",
                "Implement the generated implementation plan",
                "Configure required services and integrations",
                "Set up monitoring and optimization"
            ]
        }
    
    def generate_deployment_guide(self, 
                               income_stream_id: int,
                               implementation_result: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate a comprehensive deployment guide for an income stream
        
        Args:
            income_stream_id: ID of the income stream
            implementation_result: Optional result from Archon implementation
            
        Returns:
            Deployment guide
        """
        # Find the income stream
        income_stream = next((s for s in self.income_streams if s["id"] == income_stream_id), None)
        if not income_stream:
            raise ValueError(f"Income stream with ID {income_stream_id} not found")
        
        # Generate deployment steps based on stream type
        deployment_steps = []
        
        if income_stream["type"] == "membership":
            deployment_steps = [
                "Set up a web hosting account with a reliable provider",
                "Install a content management system (WordPress recommended)",
                "Install and configure a membership plugin",
                "Set up Stripe payment integration",
                "Create membership levels and configure pricing",
                "Set up content protection for member-only areas",
                "Configure automated email sequences for onboarding and retention",
                "Set up analytics to track member engagement",
                "Create a backup system for all content and member data",
                "Implement a support system for member questions"
            ]
        elif income_stream["type"] == "digital_product":
            deployment_steps = [
                "Select a digital product platform (Gumroad, SendOwl, etc.)",
                "Create product listings with compelling copy and images",
                "Upload digital product files to the platform",
                "Configure pricing and payment options",
                "Set up automated delivery systems",
                "Create upsell and cross-sell funnels",
                "Configure email marketing integration",
                "Set up affiliate program if applicable",
                "Implement tracking and analytics",
                "Create a customer support system"
            ]
        elif income_stream["type"] == "affiliate":
            deployment_steps = [
                "Register domain name for affiliate website",
                "Set up hosting and install WordPress",
                "Install an SEO-optimized theme",
                "Set up content structure for affiliate reviews",
                "Apply to relevant affiliate programs",
                "Create comparison and review content",
                "Implement proper affiliate link tracking",
                "Set up email capture and nurture sequences",
                "Configure analytics and conversion tracking",
                "Implement a content publishing calendar"
            ]
        elif income_stream["type"] == "saas":
            deployment_steps = [
                "Select a cloud hosting provider (AWS, Azure, etc.)",
                "Set up development and production environments",
                "Deploy the SaaS application code",
                "Configure database and storage systems",
                "Set up subscription billing through Stripe",
                "Implement user authentication and account management",
                "Configure automated email sequences",
                "Set up monitoring and error logging",
                "Implement analytics and usage tracking",
                "Create documentation and support resources"
            ]
        elif income_stream["type"] == "marketplace":
            deployment_steps = [
                "Select a marketplace platform or framework",
                "Set up hosting infrastructure",
                "Configure vendor and buyer registration systems",
                "Implement secure payment processing",
                "Set up commission structure and payment schedules",
                "Create listing creation and management tools",
                "Implement search and discovery features",
                "Configure notification systems",
                "Set up dispute resolution processes",
                "Implement analytics and reporting dashboards"
            ]
        else:
            deployment_steps = [
                "Select appropriate technology stack for your business model",
                "Set up hosting and infrastructure",
                "Implement core business functionality",
                "Configure payment processing",
                "Set up automated marketing and customer acquisition",
                "Implement analytics and tracking",
                "Create documentation and support resources",
                "Set up monitoring and maintenance systems",
                "Configure backup and recovery processes",
                "Create standard operating procedures for any manual tasks"
            ]
            
        # Add ongoing maintenance tasks
        maintenance_tasks = [
            "Weekly: Review performance metrics and adjust as needed",
            "Weekly: Check for and resolve any customer support issues",
            "Monthly: Update content or products as needed",
            "Monthly: Review and optimize marketing campaigns",
            "Quarterly: Perform security updates and patches",
            "Quarterly: Analyze pricing and consider adjustments",
            "Annually: Comprehensive business review and strategy update"
        ]
        
        # Calculate time requirements
        setup_time = {
            "membership": "10-15 hours",
            "digital_product": "8-12 hours",
            "affiliate": "15-20 hours",
            "saas": "20-40 hours",
            "marketplace": "30-50 hours"
        }.get(income_stream["type"], "15-25 hours")
        
        # Generate optimization strategies
        optimization_strategies = [
            "Implement A/B testing for landing pages and sales funnels",
            "Optimize pricing structure based on customer data",
            "Expand product offerings with complementary items",
            "Implement referral program to leverage existing customers",
            "Create advanced analytics to identify expansion opportunities",
            "Automate additional aspects of the business using AI tools",
            "Implement advanced segmentation for marketing messages"
        ]
        
        # Include specific Archon implementation details if provided
        archon_implementation = {}
        if implementation_result:
            archon_implementation = {
                "implementation_plan": implementation_result.get("implementation_plan", []),
                "revenue_streams": implementation_result.get("revenue_streams", []),
                "automation_level": implementation_result.get("automation_level", income_stream["automation_level"]),
                "estimated_monthly_revenue": implementation_result.get("estimated_monthly_revenue", 0)
            }
            
            # Update deployment steps with any additional steps from Archon
            if "implementation_plan" in implementation_result:
                additional_steps = [
                    step for step in implementation_result["implementation_plan"] 
                    if step not in deployment_steps
                ]
                if additional_steps:
                    deployment_steps.extend(additional_steps)
            
        # Create the comprehensive deployment guide
        deployment_guide = {
            "income_stream": {
                "name": income_stream["name"],
                "type": income_stream["type"],
                "description": income_stream["description"],
                "automation_level": income_stream["automation_level"],
                "automated_percentage": income_stream["automated_percentage"]
            },
            "deployment": {
                "steps": deployment_steps,
                "estimated_setup_time": setup_time,
                "required_services": income_stream["required_services"],
                "technical_requirements": [
                    "Web hosting account",
                    "Domain name",
                    "SSL certificate",
                    "Payment processor account (Stripe recommended)"
                ]
            },
            "maintenance": {
                "recurring_tasks": maintenance_tasks,
                "estimated_weekly_effort": f"{max(0.5, 10 - income_stream['automation_level'])} hours"
            },
            "optimization": {
                "strategies": optimization_strategies,
                "recommended_tools": [
                    "Google Analytics",
                    "Hotjar or similar heat mapping tool",
                    "Email marketing automation platform",
                    "Social media scheduling tool",
                    "SEO monitoring tool"
                ]
            },
            "profitability": {
                "estimated_monthly_revenue": income_stream["monthly_revenue"],
                "estimated_annual_revenue": income_stream["monthly_revenue"] * 12,
                "expected_expenses": [
                    {"name": "Web hosting", "amount": "$20-50/month"},
                    {"name": "Software subscriptions", "amount": "$50-150/month"},
                    {"name": "Payment processing fees", "amount": "2.9% + $0.30 per transaction"},
                    {"name": "Marketing", "amount": "$100-500/month"}
                ],
                "estimated_profit_margin": "70-85%"
            }
        }
        
        # Add Archon implementation details if available
        if archon_implementation:
            deployment_guide["archon_implementation"] = archon_implementation
            
        return deployment_guide
