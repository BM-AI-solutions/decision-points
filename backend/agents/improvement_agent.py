import os
import random
import asyncio
import logging
import httpx  # For async HTTP requests (A2A calls)
from typing import List, Optional, Dict, Any
import google.generativeai as genai
import json

from pydantic import BaseModel, Field, ValidationError

# ADK Imports
from google.adk.agents import Agent
from google.adk.runtime import InvocationContext
from google.adk.runtime.events import Event, ErrorEvent

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

class ImprovementAgent(Agent): # Inherit from ADK Agent
    """
    ADK Agent responsible for Stage 2: Product Improvement.
    Analyzes market research input and suggests product improvements/features.
    """
    def __init__(self, model_name: Optional[str] = None):
        """
        Initialize the Improvement Agent.

        Args:
            model_name: The name of the Gemini model to use for analysis (e.g., 'gemini-1.5-flash-latest').
                        Defaults to a suitable model if None.
        """
        super().__init__()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info("Initializing ImprovementAgent...")

        # Determine the model name to use
        effective_model_name = model_name if model_name else 'gemini-1.5-flash-latest' # Default for specialized agent
        self.model_name = effective_model_name # Store the actual model name used

        # --- LLM Client Initialization ---
        gemini_api_key = os.getenv('GEMINI_API_KEY')
        if gemini_api_key:
            try:
                # Initialize the Gemini model using the determined model name
                self.llm = genai.GenerativeModel(self.model_name)
                self.logger.info(f"Gemini GenerativeModel initialized with model: {self.model_name}.")
            except Exception as e:
                self.logger.error(f"Failed to initialize Gemini client with model {self.model_name}: {e}", exc_info=True)
                self.llm = None
        else:
            self.llm = None
            self.logger.warning("GEMINI_API_KEY not found. LLM functionality will be disabled.")

        # --- Web Search Agent Integration ---
        self.web_search_agent_url = os.getenv('WEB_SEARCH_AGENT_URL')
        self.brave_api_key = os.getenv('BRAVE_API_KEY') # Needed if WebSearchAgent requires it implicitly
        self.http_client = httpx.AsyncClient(timeout=60.0) # Increased timeout for A2A calls

        if not self.web_search_agent_url:
            self.logger.warning("WEB_SEARCH_AGENT_URL not found. Web search integration will be disabled.")
        else:
            self.logger.info(f"Web Search Agent URL configured: {self.web_search_agent_url}")
            if not self.brave_api_key:
                 # Log warning if Brave key is missing, as the search agent likely needs it.
                 self.logger.warning("BRAVE_API_KEY not found. WebSearchAgent might fail if it requires this key.")


        self.logger.info("ImprovementAgent initialized.")

    # Removed _load_feature_ideas as LLM will handle this.

    # Removed _select_features and _generate_usps methods. Logic moved to LLM call in run_async.
    async def run_async(self, context: InvocationContext) -> Event:
        """Executes the product improvement workflow asynchronously, potentially using web search and LLM."""
        self.logger.info(f"Received invocation: {context.invocation_id}")

        # --- 1. Input Validation ---
        try:
            if not isinstance(context.input_event.payload, dict):
                raise ValueError("Input payload must be a dictionary.")
            inputs = ImprovementAgentInput(**context.input_event.payload)
            self.logger.info(f"Starting product improvement analysis for concept: {inputs.product_concept}")
        except (ValidationError, ValueError) as e:
            self.logger.error(f"Input validation failed: {e}")
            return ErrorEvent(
                error_code="INPUT_VALIDATION_ERROR",
                message=f"Invalid input payload: {e}",
                details=e.errors() if isinstance(e, ValidationError) else None
            )

        # --- 2. Optional: Web Search for Technical Details/Competitors ---
        web_search_results = None
        # Condition to trigger web search (can be refined)
        # Example: Search if concept is complex or mentions specific tech
        trigger_search = "technology" in inputs.product_concept.lower() or "competitor" in inputs.product_concept.lower()

        if self.web_search_agent_url and trigger_search:
            self.logger.info("Web search triggered based on product concept.")
            search_query = f"Technical details and competitors for product concept: {inputs.product_concept}"
            try:
                search_payload = {
                    "query": search_query,
                    # Add other params WebSearchAgent might expect, e.g., num_results
                    "num_results": 5
                }
                # Note: Ensure BRAVE_API_KEY is implicitly available to the WebSearchAgent service
                # or pass it if the A2A endpoint requires it explicitly in the payload/headers.
                a2a_url = f"{self.web_search_agent_url}/a2a/web_search/invoke" # Assuming this is the correct endpoint path
                self.logger.info(f"Calling WebSearchAgent at {a2a_url} with query: {search_query}")

                response = await self.http_client.post(a2a_url, json=search_payload)
                response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)

                search_response_data = response.json()

                # Assuming WebSearchAgent returns results in a structured way, e.g., under a 'results' key
                if response.status_code == 200 and search_response_data.get("status") == "success":
                     web_search_results = search_response_data.get("results", []) # Adjust key based on actual response
                     self.logger.info(f"Received {len(web_search_results)} results from WebSearchAgent.")
                     self.logger.debug(f"Web Search Results: {web_search_results}")
                else:
                    # Handle cases where the agent call succeeded (2xx) but indicated an internal failure
                    error_msg = search_response_data.get("message", "Unknown error from WebSearchAgent")
                    self.logger.error(f"WebSearchAgent call failed internally: {error_msg}")
                    # Decide whether to proceed without search results or return an error
                    # For now, we'll proceed without search results but log the error.

            except httpx.RequestError as req_err:
                self.logger.error(f"A2A call to WebSearchAgent failed (Request Error): {req_err}", exc_info=True)
                # Proceed without search results, log the error
            except httpx.HTTPStatusError as status_err:
                 self.logger.error(f"A2A call to WebSearchAgent failed (Status Code {status_err.response.status_code}): {status_err.response.text}", exc_info=True)
                 # Proceed without search results, log the error
            except json.JSONDecodeError as json_err:
                 self.logger.error(f"Failed to decode JSON response from WebSearchAgent: {json_err}", exc_info=True)
                 # Proceed without search results, log the error
            except Exception as search_err: # Catch any other unexpected errors during search
                self.logger.error(f"Unexpected error during web search A2A call: {search_err}", exc_info=True)
                # Proceed without search results, log the error

        # --- 3. LLM Analysis ---
        if not self.llm:
            self.logger.error("LLM client not initialized. Cannot proceed with core analysis.")
            return ErrorEvent(
                error_code="LLM_NOT_INITIALIZED",
                message="LLM client (Gemini) is not available. Check API key and configuration.",
            )

        try:
            # Prepare Prompt (now includes optional search results)
            prompt = self._build_llm_prompt(inputs, web_search_results)
            self.logger.debug(f"Generated LLM Prompt:\n{prompt}")

            # Call LLM
            self.logger.info("Calling LLM for product improvement analysis...")
            # TODO: Explore direct JSON output mode if available and reliable for the model
            # generation_config = genai.types.GenerationConfig(response_mime_type="application/json")
            # response = await self.llm.generate_content_async(prompt, generation_config=generation_config)
            response = await self.llm.generate_content_async(prompt)
            self.logger.info("LLM call completed.")
            llm_output_text = response.text

        except Exception as llm_error:
            self.logger.error(f"LLM call failed: {llm_error}", exc_info=True)
            return ErrorEvent(
                error_code="LLM_API_ERROR",
                message=f"Error interacting with the LLM: {str(llm_error)}",
                details={"exception_type": type(llm_error).__name__, "exception_args": llm_error.args}
            )

        # --- 4. Parse and Validate LLM Output ---
        try:
            # Clean the output (remove potential markdown fences)
            cleaned_output = llm_output_text.strip().removeprefix("```json").removesuffix("```").strip()
            if not cleaned_output:
                 raise ValueError("LLM returned empty content after cleaning.")
            llm_data = json.loads(cleaned_output)
            spec = ImprovedProductSpec(**llm_data)
            self.logger.info("LLM output parsed and validated successfully.")
        except json.JSONDecodeError as json_err:
            self.logger.error(f"Failed to parse LLM JSON output: {json_err}")
            self.logger.debug(f"Raw LLM Output:\n{llm_output_text}")
            return ErrorEvent(
                error_code="LLM_OUTPUT_PARSE_ERROR",
                message=f"Failed to parse JSON from LLM response: {json_err}",
                details={"raw_output": llm_output_text}
            )
        except ValidationError as validation_err:
            self.logger.error(f"LLM output validation failed: {validation_err}")
            self.logger.debug(f"Parsed LLM Data:\n{llm_data if 'llm_data' in locals() else 'N/A'}")
            return ErrorEvent(
                error_code="LLM_OUTPUT_VALIDATION_ERROR",
                message=f"LLM output did not match expected format: {validation_err}",
                details={"parsed_data": llm_data if 'llm_data' in locals() else 'N/A', "validation_errors": validation_err.errors()}
            )
        except Exception as parse_err: # Catch any other parsing/validation issues
             self.logger.error(f"Error processing LLM output: {parse_err}", exc_info=True)
             self.logger.debug(f"Raw LLM Output during processing error:\n{llm_output_text}")
             return ErrorEvent(
                error_code="LLM_PROCESSING_ERROR",
                message=f"An unexpected error occurred while processing LLM output: {str(parse_err)}",
                details={"exception_type": type(parse_err).__name__, "exception_args": parse_err.args, "raw_output": llm_output_text}
            )

        # --- 5. Return Success Event ---
        self.logger.info("Product improvement analysis finished successfully.")
        return Event(
            event_type="product.improvement.completed",
            payload=spec.model_dump() # Use model_dump for Pydantic v2
        )

        # Note: General exception handling removed from here as specific errors are caught above.
        # If an uncaught exception occurs before returning, ADK runtime might handle it.

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

# Removed the __main__ block as it's not typical for ADK agents