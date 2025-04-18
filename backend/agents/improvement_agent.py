import os
import random
import asyncio # Added for async
import logging # Added for logging
from typing import List, Optional, Dict, Any

from pydantic import BaseModel, Field, ValidationError

# ADK Imports
from google.adk.agents import Agent
from google.adk.runtime import InvocationContext
from google.adk.runtime.events import Event, ErrorEvent

# Assuming MarketOpportunityReport structure is available or defined elsewhere
# For now, let's define a simplified input structure based on what this agent needs
class ImprovementAgentInput(BaseModel):
    """Input for the Improvement Agent."""
    product_concept: str = Field(description="Initial description of the product/model concept derived from market research.")
    competitor_weaknesses: List[str] = Field(default=[], description="List of weaknesses identified in competitors.")
    market_gaps: List[str] = Field(default=[], description="List of gaps identified in the market.")
    target_audience_suggestions: List[str] = Field(default=[], description="Suggested target audiences from market research.")
    feature_recommendations_from_market: List[str] = Field(default=[], description="Initial feature ideas from market research.")
    business_model_type: Optional[str] = Field(None, description="Optional: Type of business model (e.g., 'saas', 'e-commerce') to help guide feature selection.")

class ImprovedProductSpec(BaseModel):
    """Output schema for the Improvement Agent, aligning with the architecture plan."""
    product_concept: str = Field(description="Refined description of the core product/model.")
    target_audience: List[str] = Field(description="Defined target demographics for the improved product.")
    key_features: List[Dict[str, Any]] = Field(description="List of core features for the improved product, potentially with implementation details.")
    unique_selling_propositions: List[str] = Field(description="Specific improvements or unique selling points identified.")
    implementation_difficulty_estimate: Optional[int] = Field(None, description="Overall estimated difficulty score for the proposed spec (1-10).")
    potential_revenue_impact_estimate: Optional[str] = Field(None, description="Qualitative estimate of revenue impact (e.g., Low, Medium, High).")

# --- Agent Class ---

class ImprovementAgent(Agent): # Inherit from ADK Agent
    """
    ADK Agent responsible for Stage 2: Product Improvement.
    Analyzes market research input and suggests product improvements/features.
    """
    def __init__(self):
        """Initialize the Improvement Agent."""
        super().__init__() # Call parent initializer
        self.logger = logging.getLogger(self.__class__.__name__) # Setup logger
        self.logger.info("Initializing ImprovementAgent...")
        # In a real scenario, load feature ideas from feature.manager.py logic or a database
        self._load_feature_ideas()
        self.logger.info("ImprovementAgent initialized.")

    def _load_feature_ideas(self):
        """Loads or defines potential feature ideas (based on feature.manager.py)."""
        # This is a simplified version of the logic in feature.manager.py
        # In a real implementation, this could be more dynamic or load from a config/DB
        self.feature_ideas_by_type = {
             "generic": [
                {"name": "Automated Marketing Funnel", "desc": "Nurture prospects via email.", "difficulty": 5, "impact": "Medium"},
                {"name": "Referral System", "desc": "Encourage word-of-mouth.", "difficulty": 4, "impact": "Medium"},
                {"name": "Basic Analytics Dashboard", "desc": "Track key metrics.", "difficulty": 3, "impact": "Low"},
                {"name": "User Feedback Collection", "desc": "Gather input for improvement.", "difficulty": 2, "impact": "Low"},
            ],
            "e-commerce": [
                {"name": "Automated Upsell System", "desc": "Suggest related products.", "difficulty": 6, "impact": "High"},
                {"name": "Abandoned Cart Recovery", "desc": "Email reminders for carts.", "difficulty": 4, "impact": "High"},
                {"name": "Dynamic Pricing Engine", "desc": "Adjust prices automatically.", "difficulty": 8, "impact": "High"},
                {"name": "Customer Loyalty Program", "desc": "Reward repeat customers.", "difficulty": 5, "impact": "Medium"},
            ],
            "digital_products": [
                {"name": "Tiered Access System", "desc": "Multiple pricing/access levels.", "difficulty": 5, "impact": "High"},
                {"name": "Affiliate Program", "desc": "Allow promotion for commission.", "difficulty": 7, "impact": "High"},
                {"name": "Limited-Time Offers", "desc": "Create urgency.", "difficulty": 3, "impact": "Medium"},
                {"name": "Bundle Packages", "desc": "Combine products.", "difficulty": 4, "impact": "Medium"},
            ],
            "saas": [
                {"name": "Annual Billing Discount", "desc": "Incentivize annual payment.", "difficulty": 2, "impact": "High"},
                {"name": "Feature-Based Pricing Tiers", "desc": "Unlock features per tier.", "difficulty": 6, "impact": "High"},
                {"name": "Enterprise Custom Quotes", "desc": "Handle large client needs.", "difficulty": 4, "impact": "High"},
                {"name": "Referral Rewards", "desc": "Reward user referrals.", "difficulty": 5, "impact": "Medium"},
                {"name": "Usage-Based Billing", "desc": "Charge based on consumption.", "difficulty": 7, "impact": "High"},
                {"name": "API Access for Integrations", "desc": "Allow other tools to connect.", "difficulty": 6, "impact": "Medium"},
            ]
        }
        self.logger.debug("Loaded basic feature ideas.")


    def _select_features(self, inputs: ImprovementAgentInput) -> List[Dict[str, Any]]:
        """Selects and prioritizes features based on input."""
        potential_features = []
        # Add generic features
        potential_features.extend(self.feature_ideas_by_type.get("generic", []))
        # Add features based on business model type
        if inputs.business_model_type:
            potential_features.extend(self.feature_ideas_by_type.get(inputs.business_model_type.lower(), []))

        # TODO: Add more sophisticated logic here using LLM or rules:
        # - Prioritize features addressing competitor weaknesses/market gaps.
        # - Align features with target audience suggestions.
        # - Consider features from market research recommendations.
        # - Avoid redundant features.

        # For now, randomly select a few relevant features as a placeholder
        num_features_to_select = random.randint(3, 5)
        selected_features_info = []

        # Simple selection logic (placeholder)
        candidates = potential_features + [{"name": f"Custom: {feat}", "desc": "From market research", "difficulty": random.randint(3,7), "impact": "Medium"} for feat in inputs.feature_recommendations_from_market]
        # De-duplicate based on name
        unique_candidates_dict = {feat['name']: feat for feat in candidates}
        unique_candidates = list(unique_candidates_dict.values())


        if len(unique_candidates) <= num_features_to_select:
             selected_features_info = unique_candidates
        else:
             # Ensure random.sample gets a list, not a dict_values object if needed by older python versions
             selected_features_info = random.sample(unique_candidates, num_features_to_select)

        # Format for output
        formatted_features = [
            {
                "feature_name": f.get("name"),
                "description": f.get("desc"),
                "estimated_difficulty": f.get("difficulty"),
                "estimated_impact": f.get("impact"),
                # Add placeholder implementation steps (could be LLM generated later)
                "implementation_steps": [
                    f"Define requirements for {f.get('name')}",
                    "Develop backend logic",
                    "Implement frontend interface",
                    "Test feature thoroughly"
                ]
            } for f in selected_features_info
        ]

        return formatted_features

    def _generate_usps(self, inputs: ImprovementAgentInput, selected_features: List[Dict[str, Any]]) -> List[str]:
        """Generates Unique Selling Propositions based on inputs and selected features."""
        usps = []
        # Simple heuristic: focus on features addressing weaknesses/gaps
        # TODO: Use LLM for better USP generation
        if inputs.competitor_weaknesses:
            usps.append(f"Addresses key competitor weakness: {random.choice(inputs.competitor_weaknesses)}")
        if inputs.market_gaps:
             usps.append(f"Fills market gap: {random.choice(inputs.market_gaps)}")
        if selected_features:
             # Highlight a potentially high-impact or unique feature
             high_impact_features = [f for f in selected_features if f.get("estimated_impact") == "High"]
             if high_impact_features:
                 usps.append(f"Offers unique high-impact feature: {random.choice(high_impact_features)['feature_name']}")
             elif selected_features: # Ensure selected_features is not empty before choosing
                 usps.append(f"Includes key feature: {random.choice(selected_features)['feature_name']}")

        return list(set(usps))[:3] # Limit to 3 unique USPs

    async def run_async(self, context: InvocationContext) -> Event: # Changed to async def run_async
        """Executes the product improvement workflow asynchronously."""
        self.logger.info(f"Received invocation: {context.invocation_id}")
        try:
            # 1. Validate and parse input payload
            if not isinstance(context.input_event.payload, dict):
                 raise ValueError("Input payload must be a dictionary.")
            try:
                inputs = ImprovementAgentInput(**context.input_event.payload)
                self.logger.info(f"Starting product improvement analysis for concept: {inputs.product_concept}")
            except ValidationError as e:
                self.logger.error(f"Input validation failed: {e}")
                return ErrorEvent(
                    error_code="INPUT_VALIDATION_ERROR",
                    message=f"Invalid input payload: {e}",
                    details=e.errors()
                )

            # 2. Refine Product Concept (Placeholder - could use LLM)
            # Note: If LLM calls are added, make them async
            refined_concept = f"Improved {inputs.product_concept} focusing on identified market opportunities."

            # 3. Define Target Audience (Use suggestions or refine with LLM)
            target_audience = inputs.target_audience_suggestions if inputs.target_audience_suggestions else ["General Audience"]

            # 4. Select Key Features (Synchronous for now)
            selected_features = self._select_features(inputs)

            # 5. Generate USPs (Synchronous for now)
            usps = self._generate_usps(inputs, selected_features)

            # 6. Estimate Difficulty and Impact (Simple aggregation for now)
            total_difficulty = sum(f.get("estimated_difficulty", 5) for f in selected_features)
            avg_difficulty = total_difficulty / len(selected_features) if selected_features else None
            # Simple impact assessment
            has_high_impact = any(f.get("estimated_impact") == "High" for f in selected_features)
            potential_impact = "High" if has_high_impact else "Medium" if selected_features else "Low"


            # 7. Construct the Output Specification
            spec = ImprovedProductSpec(
                product_concept=refined_concept,
                target_audience=target_audience,
                key_features=selected_features,
                unique_selling_propositions=usps,
                implementation_difficulty_estimate=int(round(avg_difficulty)) if avg_difficulty is not None else None,
                potential_revenue_impact_estimate=potential_impact
            )

            self.logger.info("Product improvement analysis finished successfully.")
            # 8. Return result as an ADK Event
            return Event(
                event_type="product.improvement.completed",
                payload=spec.model_dump() # Use model_dump for Pydantic v2
            )

        except Exception as e:
            self.logger.exception(f"Agent execution failed: {e}", exc_info=True) # Log exception with traceback
            # Return an ErrorEvent
            return ErrorEvent(
                error_code="AGENT_EXECUTION_ERROR",
                message=f"An unexpected error occurred: {str(e)}",
                details={"exception_type": type(e).__name__, "exception_args": e.args}
            )

# Removed the __main__ block as it's not typical for ADK agents