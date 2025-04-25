"""
Improvement Agent for Decision Points (ADK Version).

This agent analyzes market research input and suggests product improvements/features using ADK tools.
"""

import asyncio
import logging
import json
from typing import List, Optional, Dict, Any

import google.generativeai as genai
from pydantic import BaseModel, Field, ValidationError

# ADK Imports
from google.adk.agents import Agent # Use ADK Agent
from google.adk.tools import tool, ToolContext # Import tool decorator and context
from google.adk.events import Event # Import Event for tool return type

# Removed A2A and BaseSpecializedAgent imports
from app.config import settings

# Configure logging
logger = logging.getLogger(__name__)

# --- LLM Initialization ---
try:
    genai.configure(api_key=settings.GEMINI_API_KEY)
    gemini_model_name = settings.GEMINI_MODEL_NAME # Or a specific model for strategy
    gemini_model = genai.GenerativeModel(gemini_model_name)
    logger.info(f"Direct Gemini model {gemini_model_name} initialized for improvement tools.")
except Exception as e:
    logger.error(f"Failed to initialize direct Gemini model: {e}", exc_info=True)
    gemini_model = None

# --- Pydantic Models (Keep as they define data structures) ---

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
    feasibility_score: Optional[float] = Field(None, description="Estimated market/technical feasibility score (0.0 to 1.0).")
    potential_rating: Optional[str] = Field(None, description="Overall potential rating (e.g., 'Low', 'Medium', 'High').")
    assessment_rationale: Optional[str] = Field(None, description="Brief rationale for the feasibility score and potential rating.")

# --- Helper Function ---

def _build_llm_prompt(inputs: ImprovementAgentInput, web_search_results: Optional[List[Dict]] = None) -> str:
    """Constructs the prompt for the LLM based on input data and optional web search results."""
    output_schema_description = json.dumps(ImprovedProductSpec.model_json_schema(), indent=2)
    search_context = "No web search performed or no relevant results found."
    if web_search_results:
        search_context = "Web Search Results Summary:\n"
        for i, result in enumerate(web_search_results[:5]): # Limit context
             title = result.get('title', 'N/A')
             # Use 'summary' or 'description' based on web_search_adk output format
             snippet = result.get('summary') or result.get('description', 'N/A')
             link = result.get('source', '#') # Use 'source' based on web_search_adk output
             search_context += f"{i+1}. {title}: {snippet} ({link})\n"
        search_context = search_context.strip()

    prompt = f"""
You are an expert Product Strategist AI. Analyze market research data and web search results to generate a detailed, innovative, and actionable specification for an improved product.

**Input Data:**
*   Initial Product Concept: {inputs.product_concept}
*   Competitor Weaknesses: {inputs.competitor_weaknesses or 'None identified'}
*   Market Gaps: {inputs.market_gaps or 'None identified'}
*   Target Audience Suggestions: {inputs.target_audience_suggestions or 'None provided'}
*   Feature Recommendations (from research): {inputs.feature_recommendations_from_market or 'None provided'}
*   Business Model Type: {inputs.business_model_type or 'Not specified'}

**Web Search Context:**
{search_context}

**Analysis & Generation Task:**
Generate a JSON object representing the `ImprovedProductSpec`. Follow these steps:
1.  **Analyze:** Synthesize insights from all inputs. Identify core problems/opportunities. Consider web search context for feasibility/innovation.
2.  **Refine Concept:** Write a concise, compelling, refined product concept.
3.  **Define Audience:** Define primary/secondary target audience(s) with justification.
4.  **Prioritize Features:** Brainstorm features. Select 3-5 core features. For each: `feature_name`, `description` (user benefit), `estimated_difficulty` (1-10), `estimated_impact` (Low/Medium/High), `implementation_steps` (brief list).
5.  **Develop USPs:** Formulate 2-3 clear, compelling Unique Selling Propositions.
6.  **Assess Feasibility/Potential:** Provide `feasibility_score` (0.0-1.0), `potential_rating` (Low/Medium/High), and `assessment_rationale`.
7.  **Estimate Overall Impact (Optional):** Provide `implementation_difficulty_estimate` (1-10) and `potential_revenue_impact_estimate` (Low/Medium/High).

**Output Format Constraint:**
**CRITICAL:** Generate *ONLY* a single, valid JSON object adhering to the schema below. No extra text, markdown, etc.
```json
{output_schema_description}
```
Example Feature: {{"feature_name": "AI Summary", "description": "...", "estimated_difficulty": 7, "estimated_impact": "High", "implementation_steps": [...]}}

Generate the JSON object now.
"""
    return prompt

# --- ADK Tool Definitions ---

@tool(description="Analyze market research and suggest product improvements, potentially using web search for context.")
async def improve_product_tool(
    context: ToolContext, # Add context for invoking web search
    product_concept: str,
    competitor_weaknesses: List[str] = [],
    market_gaps: List[str] = [],
    target_audience_suggestions: List[str] = [],
    feature_recommendations_from_market: List[str] = [],
    business_model_type: Optional[str] = None
) -> Dict[str, Any]:
    """
    ADK Tool: Analyze market research and suggest product improvements.
    Returns a dictionary representing the ImprovedProductSpec or an error.
    """
    logger.info(f"Tool: Improving product concept: {product_concept}")

    if not gemini_model:
        return {"success": False, "error": "Gemini model not initialized"}

    try:
        inputs = ImprovementAgentInput(
            product_concept=product_concept,
            competitor_weaknesses=competitor_weaknesses,
            market_gaps=market_gaps,
            target_audience_suggestions=target_audience_suggestions,
            feature_recommendations_from_market=feature_recommendations_from_market,
            business_model_type=business_model_type
        )

        # Optional Web Search via ADK invoke_agent
        web_search_results = None
        trigger_search = "technology" in inputs.product_concept.lower() or "competitor" in inputs.product_concept.lower()
        target_web_search_agent_id = "web_search_adk" # Name of the refactored agent

        if trigger_search:
            logger.info("Tool: Web search triggered.")
            search_query = f"Technical details and competitors for product concept: {inputs.product_concept}"
            try:
                search_input_event = Event(data={"query": search_query})
                search_response_event = await context.invoke_agent(
                    target_agent_id=target_web_search_agent_id,
                    input=search_input_event,
                    timeout_seconds=30.0
                )
                # Extract results carefully from the response event
                if search_response_event and search_response_event.actions and search_response_event.actions[0].content and search_response_event.actions[0].content.parts:
                    part_data = search_response_event.actions[0].content.parts[0].data
                    if isinstance(part_data, dict) and "results" in part_data:
                        web_search_results = part_data["results"]
                        logger.info(f"Tool: Received {len(web_search_results)} results from {target_web_search_agent_id}.")
                    elif isinstance(part_data, dict) and "error" in part_data:
                         logger.warning(f"Tool: {target_web_search_agent_id} returned error: {part_data['error']}")
                    else:
                         logger.warning(f"Tool: Unexpected payload structure from {target_web_search_agent_id}: {part_data}")
                elif search_response_event and search_response_event.actions and search_response_event.actions[0].parts:
                     # Fallback for tool output directly in parts
                     part_data = search_response_event.actions[0].parts[0].data
                     if isinstance(part_data, dict) and "results" in part_data:
                         web_search_results = part_data["results"]
                         logger.info(f"Tool: Received {len(web_search_results)} results from {target_web_search_agent_id} (fallback parse).")
                     elif isinstance(part_data, dict) and "error" in part_data:
                         logger.warning(f"Tool: {target_web_search_agent_id} returned error (fallback parse): {part_data['error']}")
                     else:
                         logger.warning(f"Tool: Unexpected payload structure from {target_web_search_agent_id} (fallback parse): {part_data}")
                else:
                     logger.warning(f"Tool: No valid results structure found in response from {target_web_search_agent_id}: {search_response_event}")

            except Exception as e:
                logger.error(f"Tool: Error invoking {target_web_search_agent_id}: {e}", exc_info=True)
                # Continue without search results, but log the error

        # LLM Analysis
        prompt = _build_llm_prompt(inputs, web_search_results)
        logger.info("Tool: Calling LLM for product improvement analysis...")
        response = await gemini_model.generate_content_async(prompt)
        response_text = response.text

        # Parse and Validate LLM Output
        try:
            cleaned_output = response_text.strip().removeprefix("```json").removesuffix("```").strip()
            if not cleaned_output: raise ValueError("LLM returned empty content.")
            llm_data = json.loads(cleaned_output)
            spec = ImprovedProductSpec(**llm_data) # Validate against Pydantic model
            logger.info("Tool: LLM output parsed and validated successfully.")
            return {"success": True, "improved_spec": spec.model_dump()}
        except (json.JSONDecodeError, ValidationError, ValueError) as e:
            logger.error(f"Tool: Error processing LLM output: {e}", exc_info=True)
            return {"success": False, "error": f"Error processing LLM output: {str(e)}", "raw_output": response_text}

    except Exception as e:
        logger.error(f"Tool: Error improving product: {e}", exc_info=True)
        return {"success": False, "error": f"Error improving product: {str(e)}"}

@tool(description="Assess the market and technical feasibility of a product concept.")
async def assess_product_feasibility_tool(product_concept: str) -> Dict[str, Any]:
    """
    ADK Tool: Assess the feasibility of a product concept.
    Returns a dictionary containing the assessment or an error.
    """
    logger.info(f"Tool: Assessing feasibility of product concept: {product_concept}")

    if not gemini_model:
        return {"success": False, "error": "Gemini model not initialized"}

    try:
        prompt = f"""
        You are an expert Product Strategist AI. Assess the feasibility of: "{product_concept}"

        Provide:
        1. feasibility_score (0.0-1.0)
        2. potential_rating ('Low', 'Medium', 'High')
        3. assessment_rationale (brief justification)

        Format as JSON: {{"feasibility_score": N.N, "potential_rating": "...", "assessment_rationale": "..."}}
        Respond ONLY with the JSON object.
        """
        response = await gemini_model.generate_content_async(prompt)
        response_text = response.text

        try:
            cleaned_output = response_text.strip().removeprefix("```json").removesuffix("```").strip()
            if not cleaned_output: raise ValueError("LLM returned empty content.")
            assessment = json.loads(cleaned_output)
            # Basic validation of expected keys
            if not all(k in assessment for k in ["feasibility_score", "potential_rating", "assessment_rationale"]):
                 raise ValueError("LLM response missing required assessment keys.")
            logger.info("Tool: Feasibility assessment parsed successfully.")
            return {"success": True, "assessment": assessment}
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Tool: Error parsing feasibility assessment output: {e}", exc_info=True)
            return {"success": False, "error": f"Error parsing LLM output: {str(e)}", "raw_output": response_text}

    except Exception as e:
        logger.error(f"Tool: Error assessing product feasibility: {e}", exc_info=True)
        return {"success": False, "error": f"Error assessing feasibility: {str(e)}"}


# --- Instantiate the ADK Agent ---
agent = Agent(
    name="improvement_adk", # ADK specific name
    description="Analyzes market research, suggests product improvements, and assesses feasibility.",
    tools=[
        improve_product_tool,
        assess_product_feasibility_tool,
    ],
)

# Removed A2A server specific code and old class structure
