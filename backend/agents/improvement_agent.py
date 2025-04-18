import os
import random
import asyncio # Added for async
import logging # Added for logging
from typing import List, Optional, Dict, Any
import google.generativeai as genai
import json # For parsing LLM JSON output

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
        # Initialize the Gemini client
        # TODO: Make model name configurable (e.g., via environment variable or config)
        try:
            # Check if API key is configured (as done in app.py)
            if os.getenv('GEMINI_API_KEY'):
                 self.llm = genai.GenerativeModel('gemini-pro') # Or a more advanced model if needed
                 self.logger.info("Gemini GenerativeModel initialized.")
            else:
                 self.llm = None
                 self.logger.warning("GEMINI_API_KEY not found. LLM functionality will be disabled.")
        except Exception as e:
            self.logger.error(f"Failed to initialize Gemini client: {e}", exc_info=True)
            self.llm = None # Ensure llm is None if init fails

        # self._load_feature_ideas() # Removed - LLM will generate features
        self.logger.info("ImprovementAgent initialized.")

    # Removed _load_feature_ideas as LLM will handle this.

    # Removed _select_features and _generate_usps methods. Logic moved to LLM call in run_async.
    async def run_async(self, context: InvocationContext) -> Event: # Changed to async def run_async
        """Executes the product improvement workflow asynchronously using an LLM."""
        self.logger.info(f"Received invocation: {context.invocation_id}")

        # Check if LLM is available
        if not self.llm:
            self.logger.error("LLM client not initialized. Cannot proceed.")
            return ErrorEvent(
                error_code="LLM_NOT_INITIALIZED",
                message="LLM client (Gemini) is not available. Check API key and configuration.",
            )

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

            # 2. Prepare Prompt for LLM
            prompt = self._build_llm_prompt(inputs)
            self.logger.debug(f"Generated LLM Prompt:\n{prompt}") # Log the prompt for debugging

            # 3. Call LLM Asynchronously
            self.logger.info("Calling LLM for product improvement analysis...")
            try:
                # Configure for JSON output if the model supports it directly
                # generation_config = genai.types.GenerationConfig(response_mime_type="application/json")
                # response = await self.llm.generate_content_async(prompt, generation_config=generation_config)

                # If direct JSON output isn't reliable/supported, ask for JSON in the prompt and parse manually
                response = await self.llm.generate_content_async(prompt)

                self.logger.info("LLM call completed.")
                # Accessing response text - adjust based on actual genai library structure if needed
                llm_output_text = response.text

            except Exception as llm_error:
                self.logger.error(f"LLM call failed: {llm_error}", exc_info=True)
                return ErrorEvent(
                    error_code="LLM_API_ERROR",
                    message=f"Error interacting with the LLM: {str(llm_error)}",
                    details={"exception_type": type(llm_error).__name__, "exception_args": llm_error.args}
                )

            # 4. Parse and Validate LLM Output
            try:
                # Clean the output if necessary (e.g., remove markdown code fences)
                cleaned_output = llm_output_text.strip().removeprefix("```json").removesuffix("```").strip()
                llm_data = json.loads(cleaned_output)
                spec = ImprovedProductSpec(**llm_data)
                self.logger.info("LLM output parsed and validated successfully.")
            except json.JSONDecodeError as json_err:
                self.logger.error(f"Failed to parse LLM JSON output: {json_err}")
                self.logger.debug(f"Raw LLM Output:\n{llm_output_text}") # Log raw output for debugging
                return ErrorEvent(
                    error_code="LLM_OUTPUT_PARSE_ERROR",
                    message=f"Failed to parse JSON from LLM response: {json_err}",
                    details={"raw_output": llm_output_text}
                )
            except ValidationError as validation_err:
                self.logger.error(f"LLM output validation failed: {validation_err}")
                self.logger.debug(f"Parsed LLM Data:\n{llm_data}") # Log parsed data for debugging
                return ErrorEvent(
                    error_code="LLM_OUTPUT_VALIDATION_ERROR",
                    message=f"LLM output did not match expected format: {validation_err}",
                    details={"parsed_data": llm_data, "validation_errors": validation_err.errors()}
                )
            except Exception as parse_err: # Catch any other parsing/validation issues
                 self.logger.error(f"Error processing LLM output: {parse_err}", exc_info=True)
                 return ErrorEvent(
                    error_code="LLM_PROCESSING_ERROR",
                    message=f"An unexpected error occurred while processing LLM output: {str(parse_err)}",
                    details={"exception_type": type(parse_err).__name__, "exception_args": parse_err.args}
                )


            # 5. Return result as an ADK Event
            self.logger.info("Product improvement analysis finished successfully using LLM.")
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

    def _build_llm_prompt(self, inputs: ImprovementAgentInput) -> str:
        """Constructs the prompt for the LLM based on the input data."""

        # Define the desired JSON output structure for the LLM
        # Use model_json_schema for Pydantic v2
        output_schema_description = json.dumps(ImprovedProductSpec.model_json_schema(), indent=2)


        prompt = f"""
Analyze the provided market research data and generate an improved product specification.

**Input Data:**

*   **Initial Product Concept:** {inputs.product_concept}
*   **Competitor Weaknesses:** {inputs.competitor_weaknesses or 'None provided'}
*   **Market Gaps:** {inputs.market_gaps or 'None provided'}
*   **Target Audience Suggestions (from research):** {inputs.target_audience_suggestions or 'None provided'}
*   **Feature Recommendations (from research):** {inputs.feature_recommendations_from_market or 'None provided'}
*   **Business Model Type:** {inputs.business_model_type or 'Not specified'}

**Task:**

Based on the input data, perform the following analysis and generate a JSON object matching the schema below:

1.  **Refine Product Concept:** Briefly refine the initial concept to incorporate market opportunities or address identified gaps/weaknesses.
2.  **Define Target Audience:** Specify the primary target audience(s) for the improved product, considering the research suggestions.
3.  **Identify Key Features:** Propose 3-5 core features for the improved product. Prioritize features that:
    *   Address competitor weaknesses or market gaps.
    *   Align with the target audience and business model.
    *   Incorporate relevant recommendations from the initial research.
    *   For each feature, provide a name (`feature_name`: string), description (`description`: string), estimated implementation difficulty (`estimated_difficulty`: integer 1-10), estimated potential impact (`estimated_impact`: string "Low", "Medium", or "High"), and brief potential implementation steps (`implementation_steps`: list of strings).
4.  **Generate Unique Selling Propositions (USPs):** List 2-3 compelling USPs based on the refined concept and key features. Highlight what makes this product stand out.
5.  **Estimate Overall Difficulty & Impact:** Provide an overall implementation difficulty estimate (`implementation_difficulty_estimate`: integer 1-10) and potential revenue impact estimate (`potential_revenue_impact_estimate`: string "Low", "Medium", or "High") for the entire proposed specification.

**Output Format:**

Generate ONLY a valid JSON object adhering to the following Pydantic schema. Do not include any explanatory text, markdown formatting, or code fences before or after the JSON object.

```json
{output_schema_description}
```

**Example Feature Structure (within key_features list):**
```json
{{
  "feature_name": "Example Feature",
  "description": "Detailed description of what the feature does.",
  "estimated_difficulty": 6,
  "estimated_impact": "High",
  "implementation_steps": [
    "Step 1: Define requirements",
    "Step 2: Backend development",
    "Step 3: Frontend integration",
    "Step 4: Testing"
  ]
}}
```

Now, generate the JSON output based on the provided input data.
"""
        return prompt

# Removed the __main__ block as it's not typical for ADK agents