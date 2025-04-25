"""
Improvement Agent for Decision Points.

This agent analyzes market research input and suggests product improvements/features.
It implements the A2A protocol for agent communication.
"""

import random
import asyncio
import logging
import httpx
from typing import List, Optional, Dict, Any
import google.generativeai as genai
import json

from pydantic import BaseModel, Field, ValidationError

# ADK Imports
from google.adk.runtime import InvocationContext
from google.adk.runtime.events import Event, ErrorEvent

# A2A Imports
from python_a2a import skill

from agents.base_agent import BaseSpecializedAgent
from app.config import settings

# TODO: Potentially align this more closely with the actual MarketOpportunityReport structure
# if it becomes significantly different. For now, assume the necessary fields are passed.
class ImprovementAgentInput(BaseModel):
    """Input for the Improvement Agent, derived from MarketOpportunityReport."""
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
    # New assessment fields
    feasibility_score: Optional[float] = Field(None, description="Estimated market/technical feasibility score (0.0 to 1.0).")
    potential_rating: Optional[str] = Field(None, description="Overall potential rating (e.g., 'Low', 'Medium', 'High').")
    assessment_rationale: Optional[str] = Field(None, description="Brief rationale for the feasibility score and potential rating.")

# --- Agent Class ---

class ImprovementAgent(BaseSpecializedAgent):
    """
    Agent responsible for product improvement.
    Analyzes market research input and suggests product improvements/features.
    Implements A2A protocol for agent communication.
    """
    def __init__(
        self,
        name: str = "improvement",
        description: str = "Analyzes market research input and suggests product improvements/features",
        model_name: Optional[str] = None,
        port: Optional[int] = None,
        **kwargs: Any,
    ):
        """
        Initialize the ImprovementAgent.

        Args:
            name: The name of the agent.
            description: The description of the agent.
            model_name: The name of the model to use. Defaults to settings.GEMINI_MODEL_NAME.
            port: The port to run the A2A server on. Defaults to settings.IMPROVEMENT_AGENT_URL port.
            **kwargs: Additional arguments for BaseSpecializedAgent.
        """
        # Extract port from URL if not provided
        if port is None and settings.IMPROVEMENT_AGENT_URL:
            try:
                port = int(settings.IMPROVEMENT_AGENT_URL.split(':')[-1])
            except (ValueError, IndexError):
                port = 8005  # Default port

        # Initialize BaseSpecializedAgent
        super().__init__(
            name=name,
            description=description,
            model_name=model_name,
            port=port,
            **kwargs
        )

        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info("Initializing ImprovementAgent...")

        # --- Web Search Agent Integration ---
        # Get Agent ID from settings
        self.agent_web_search_id = settings.AGENT_WEB_SEARCH_ID

        if not self.agent_web_search_id:
            self.logger.warning("AGENT_WEB_SEARCH_ID not configured in settings. Web search integration will be disabled.")
        else:
            self.logger.info(f"Web Search Agent ID configured via settings: {self.agent_web_search_id}")

        self.logger.info(f"ImprovementAgent initialized with port: {self.port}")

    # --- A2A Skills ---
    @skill(
        name="improve_product",
        description="Analyze market research and suggest product improvements",
        tags=["improvement", "product"]
    )
    async def improve_product(self, product_concept: str, competitor_weaknesses: List[str] = None,
                             market_gaps: List[str] = None, target_audience_suggestions: List[str] = None,
                             feature_recommendations_from_market: List[str] = None,
                             business_model_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze market research and suggest product improvements.

        Args:
            product_concept: Initial description of the product/model concept.
            competitor_weaknesses: List of weaknesses identified in competitors.
            market_gaps: List of gaps identified in the market.
            target_audience_suggestions: Suggested target audiences from market research.
            feature_recommendations_from_market: Initial feature ideas from market research.
            business_model_type: Type of business model (e.g., 'saas', 'e-commerce').

        Returns:
            A dictionary containing the improved product specification.
        """
        self.logger.info(f"Improving product concept: {product_concept}")

        try:
            # Create input model
            inputs = ImprovementAgentInput(
                product_concept=product_concept,
                competitor_weaknesses=competitor_weaknesses or [],
                market_gaps=market_gaps or [],
                target_audience_suggestions=target_audience_suggestions or [],
                feature_recommendations_from_market=feature_recommendations_from_market or [],
                business_model_type=business_model_type
            )

            # Optional: Web Search for Technical Details/Competitors
            web_search_results = None
            trigger_search = "technology" in inputs.product_concept.lower() or "competitor" in inputs.product_concept.lower()

            if self.agent_web_search_id and trigger_search:
                self.logger.info("Web search triggered based on product concept.")
                search_query = f"Technical details and competitors for product concept: {inputs.product_concept}"

                try:
                    from agents.agent_network import agent_network

                    # Get the agent from the network
                    agent = agent_network.get_agent("web_search")
                    if agent:
                        # Invoke the web_search skill
                        search_result = await agent.invoke_skill(
                            skill_name="web_search",
                            input_data={"query": search_query, "num_results": 5},
                            timeout=30.0
                        )

                        if search_result and "results" in search_result:
                            web_search_results = search_result["results"]
                            self.logger.info(f"Received {len(web_search_results)} results from WebSearchAgent.")
                    else:
                        self.logger.warning("WebSearchAgent not found in agent network.")
                except Exception as e:
                    self.logger.error(f"Error calling WebSearchAgent: {e}", exc_info=True)

            # LLM Analysis
            if not self.llm_client:
                return {
                    "success": False,
                    "error": "LLM client not initialized. Cannot proceed with analysis."
                }

            # Prepare Prompt
            prompt = self._build_llm_prompt(inputs, web_search_results)

            # Call LLM
            self.logger.info("Calling LLM for product improvement analysis...")
            response = await self.llm_client.generate_text_async(prompt=prompt)

            # Parse and Validate LLM Output
            try:
                # Clean the output (remove potential markdown fences)
                cleaned_output = response.strip().removeprefix("```json").removesuffix("```").strip()
                if not cleaned_output:
                    raise ValueError("LLM returned empty content after cleaning.")

                llm_data = json.loads(cleaned_output)
                spec = ImprovedProductSpec(**llm_data)
                self.logger.info("LLM output parsed and validated successfully.")

                # Return the improved product spec
                return {
                    "success": True,
                    "message": "Product improvement analysis completed successfully.",
                    **spec.model_dump()
                }
            except (json.JSONDecodeError, ValidationError, ValueError) as e:
                self.logger.error(f"Error processing LLM output: {e}", exc_info=True)
                return {
                    "success": False,
                    "error": f"Error processing LLM output: {str(e)}",
                    "raw_output": response
                }

        except Exception as e:
            self.logger.error(f"Error improving product: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"Error improving product: {str(e)}"
            }

    @skill(
        name="assess_product_feasibility",
        description="Assess the feasibility of a product concept",
        tags=["improvement", "assessment"]
    )
    async def assess_product_feasibility(self, product_concept: str) -> Dict[str, Any]:
        """
        Assess the feasibility of a product concept.

        Args:
            product_concept: Description of the product concept to assess.

        Returns:
            A dictionary containing the feasibility assessment.
        """
        self.logger.info(f"Assessing feasibility of product concept: {product_concept}")

        try:
            # Create a prompt for the LLM
            prompt = f"""
            You are an expert Product Strategist AI. Your task is to assess the feasibility of the following product concept:

            Product Concept: {product_concept}

            Provide a detailed assessment including:
            1. Feasibility score (0.0 to 1.0, where 1.0 is highly feasible)
            2. Potential rating ('Low', 'Medium', 'High')
            3. Assessment rationale (brief explanation justifying the score and rating)

            Format your response as a JSON object with the following structure:
            {{
                "feasibility_score": 0.8,
                "potential_rating": "High",
                "assessment_rationale": "This product concept is highly feasible because..."
            }}
            """

            # Call LLM
            response = await self.llm_client.generate_text_async(prompt=prompt)

            # Parse the response
            try:
                # Clean the output
                cleaned_output = response.strip().removeprefix("```json").removesuffix("```").strip()
                assessment = json.loads(cleaned_output)

                return {
                    "success": True,
                    "message": "Feasibility assessment completed successfully.",
                    "product_concept": product_concept,
                    "assessment": assessment
                }
            except (json.JSONDecodeError, ValueError) as e:
                self.logger.error(f"Error parsing LLM output: {e}", exc_info=True)
                return {
                    "success": False,
                    "error": f"Error parsing LLM output: {str(e)}",
                    "raw_output": response
                }

        except Exception as e:
            self.logger.error(f"Error assessing product feasibility: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"Error assessing product feasibility: {str(e)}"
            }

    async def run_async(self, context: InvocationContext) -> Event:
        """
        Executes the product improvement workflow asynchronously according to ADK spec.
        Maintained for backward compatibility with ADK.

        Args:
            context: The invocation context containing the input data.

        Returns:
            An Event containing the improvement results or an error.
        """
        self.logger.info(f"Received invocation for ImprovementAgent (ID: {context.invocation_id})")

        try:
            # Extract input from context
            input_data = {}
            if hasattr(context, 'input_event') and hasattr(context.input_event, 'payload'):
                input_data = context.input_event.payload
            elif hasattr(context, 'input') and isinstance(context.input, dict):
                input_data = context.input

            # Parse and validate input
            try:
                inputs = ImprovementAgentInput(**input_data)
            except (ValidationError, ValueError) as e:
                self.logger.error(f"Input validation failed: {e}")
                return ErrorEvent(
                    error_code="INPUT_VALIDATION_ERROR",
                    message=f"Invalid input payload: {e}",
                    details=e.errors() if isinstance(e, ValidationError) else None
                )

            # Use the A2A skill
            result = await self.improve_product(
                product_concept=inputs.product_concept,
                competitor_weaknesses=inputs.competitor_weaknesses,
                market_gaps=inputs.market_gaps,
                target_audience_suggestions=inputs.target_audience_suggestions,
                feature_recommendations_from_market=inputs.feature_recommendations_from_market,
                business_model_type=inputs.business_model_type
            )

            # Create an event from the result
            if result.get("success", False):
                return Event(
                    event_type="product.improvement.completed",
                    payload={k: v for k, v in result.items() if k != "success" and k != "message"}
                )
            else:
                return ErrorEvent(
                    error_code="IMPROVEMENT_FAILED",
                    message=result.get("error", "Product improvement failed."),
                    details=result
                )

        except Exception as e:
            # Catch-all for unexpected errors
            self.logger.error(f"Unexpected error in ImprovementAgent: {e}", exc_info=True)
            return ErrorEvent(
                error_code="UNEXPECTED_ERROR",
                message=f"An unexpected error occurred: {str(e)}",
                details={"exception_type": type(e).__name__, "exception_args": e.args}
            )

    def _build_llm_prompt(self, inputs: ImprovementAgentInput, web_search_results: Optional[List[Dict]] = None) -> str:
        """Constructs the prompt for the LLM based on input data and optional web search results."""

        output_schema_description = json.dumps(ImprovedProductSpec.model_json_schema(), indent=2)

        # --- Build Web Search Context String ---
        search_context = "No web search performed or no relevant results found."
        if web_search_results:
            search_context = "Web Search Results Summary:\n"
            for i, result in enumerate(web_search_results[:5]): # Limit context length
                 title = result.get('title', 'N/A')
                 snippet = result.get('snippet', 'N/A') # Adjust keys based on actual WebSearchAgent output
                 link = result.get('link', '#')
                 search_context += f"{i+1}. {title}: {snippet} ({link})\n"
            search_context = search_context.strip()


        # --- Enhanced Prompt ---
        prompt = f"""
You are an expert Product Strategist AI. Your task is to analyze market research data, potentially supplemented by web search results, and generate a detailed, innovative, and actionable specification for an improved product or service.

**Input Data:**

*   **Initial Product Concept:** {inputs.product_concept}
*   **Competitor Weaknesses:** {inputs.competitor_weaknesses or 'None identified'}
*   **Market Gaps:** {inputs.market_gaps or 'None identified'}
*   **Target Audience Suggestions (from research):** {inputs.target_audience_suggestions or 'None provided'}
*   **Feature Recommendations (from research):** {inputs.feature_recommendations_from_market or 'None provided'}
*   **Business Model Type:** {inputs.business_model_type or 'Not specified'}

**Web Search Context (if available):**

{search_context}

**Analysis & Generation Task:**

Perform a thorough analysis of all provided inputs (market data and web search context). Based on this analysis, generate a JSON object representing the `ImprovedProductSpec`. Follow these steps meticulously:

1.  **Deep Analysis:**
    *   Synthesize insights from competitor weaknesses, market gaps, and target audience needs.
    *   Identify the core problems to solve or opportunities to seize.
    *   Consider how the web search results (if provided) inform technical feasibility, competitor landscape, or innovative approaches.
2.  **Refine Product Concept:** Write a concise, compelling, and refined description of the core product/service concept, incorporating key insights from your analysis. Make it clearer and more focused than the initial concept.
3.  **Define Target Audience:** Clearly define the primary and secondary target audience(s). Be specific about demographics, needs, and pain points this product will address. Justify your choice based on the input data.
4.  **Brainstorm & Prioritize Key Features:**
    *   Generate a list of potential features that directly address the identified problems/opportunities and target audience needs. Think creatively and consider innovative solutions.
    *   Prioritize and select the 3-5 *most impactful* core features for the Minimum Viable Product (MVP) or initial launch.
    *   For each selected feature, provide:
        *   `feature_name`: A clear, concise name.
        *   `description`: A detailed explanation of what the feature does and the user benefit.
        *   `estimated_difficulty`: An integer score (1-10, 1=trivial, 10=very complex) estimating implementation effort.
        *   `estimated_impact`: A qualitative assessment ("Low", "Medium", "High") of the feature's potential contribution to user value or business goals.
        *   `implementation_steps`: A *brief* list (3-5 steps) outlining the high-level technical or process steps required to build this feature.
5.  **Develop Unique Selling Propositions (USPs):** Formulate 2-3 clear, concise, and compelling USPs. These should highlight what makes the improved product truly unique and desirable compared to alternatives, based on the refined concept and key features.
6.  **Develop Unique Selling Propositions (USPs):** Formulate 2-3 clear, concise, and compelling USPs. These should highlight what makes the improved product truly unique and desirable compared to alternatives, based on the refined concept and key features.
7.  **Assess Feasibility & Potential:** Provide a realistic assessment of the proposed specification:
    *   `feasibility_score`: A float score between 0.0 and 1.0 representing the overall market and technical feasibility. 1.0 is highly feasible.
    *   `potential_rating`: A qualitative rating ('Low', 'Medium', 'High') indicating the overall potential for success and impact.
    *   `assessment_rationale`: A brief (1-2 sentences) explanation justifying the feasibility score and potential rating, considering market fit, technical challenges, and competitive landscape.
8.  **Estimate Implementation & Revenue Impact (Optional but Recommended):** Provide holistic estimates if possible:
    *   `implementation_difficulty_estimate`: An overall integer score (1-10) reflecting the complexity of building the complete spec.
    *   `potential_revenue_impact_estimate`: An overall qualitative estimate ("Low", "Medium", "High") of the potential market success and revenue generation.


**Output Format Constraint:**

**CRITICAL:** Generate *ONLY* a single, valid JSON object that strictly adheres to the following Pydantic schema. Do *NOT* include any introductory text, concluding remarks, explanations, apologies, markdown formatting (like ```json), or any characters outside the JSON object itself.

```json
{output_schema_description}
```

**Example Feature Structure (within `key_features` list):**
```json
{{
  "feature_name": "AI-Powered Content Summarization",
  "description": "Automatically generates concise summaries of long articles or documents using advanced NLP, saving users time.",
  "estimated_difficulty": 7,
  "estimated_impact": "High",
  "implementation_steps": [
    "Integrate with a suitable NLP model API (e.g., Gemini)",
    "Develop text extraction logic",
    "Build backend processing pipeline",
    "Create frontend UI for input and display",
    "Implement user feedback mechanism"
  ]
}}
```

Now, based *only* on the provided input data and web search context, generate the required JSON object.
"""
        return prompt

# Example of how to run this agent as a standalone A2A server
if __name__ == "__main__":
    # Create the agent
    agent = ImprovementAgent()

    # Run the A2A server
    agent.run_server(host="0.0.0.0", port=agent.port or 8005)