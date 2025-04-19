import os
import random
import asyncio
import logging
import httpx  # For async HTTP requests (A2A calls)
from typing import List, Optional, Dict, Any
from google import genai
from flask import Blueprint, request, jsonify, current_app # Added Flask imports

import json

from pydantic import BaseModel, Field, ValidationError

# ADK Imports
from google.adk.agents import Agent
from google.adk.runtime import InvocationContext
from google.adk.runtime.events import Event, ErrorEvent, UserEvent # Added UserEvent

# --- Pydantic Models Aligned with Architecture ---

class MarketOpportunityReportInput(BaseModel):
    """Input for the Improvement Agent, directly mapping MarketOpportunityReport."""
    competitors: List[Dict[str, Any]] = Field(description="List of identified competitors (e.g., {'url': '...', 'description': '...'})")
    analysis: Dict[str, Any] = Field(description="Structured analysis (e.g., {'market_gaps': [...], 'competitor_weaknesses': [...], 'pricing_strategies': '...'})")
    feature_recommendations: List[str] = Field(description="List of potential features based on analysis.")
    target_audience_suggestions: List[str] = Field(description="Potential target demographics.")
    business_model_type: Optional[str] = Field(None, description="Optional: Type of business model to guide feature selection.")

class ImprovedProductSpecOutput(BaseModel):
    """Output schema for the Improvement Agent, aligning with the architecture plan."""
    product_concept: str = Field(description="Refined description of the core product/model derived from analysis.")
    target_audience: List[str] = Field(description="Defined target demographics for the improved product.")
    key_features: List[Dict[str, Any]] = Field(description="List of core features. Each feature dict should include 'feature_name', 'description', 'estimated_difficulty' (1-10), 'estimated_impact' ('Low'/'Medium'/'High'), 'implementation_steps' (list of strings).")
    identified_improvements: List[str] = Field(description="Specific improvements or unique selling propositions identified.")
    implementation_difficulty: Optional[int] = Field(None, description="Overall estimated difficulty score for the proposed spec (1-10).")
    revenue_impact: Optional[str] = Field(None, description="Overall qualitative estimate of revenue impact (e.g., Low, Medium, High).")


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
                genai.configure(api_key=gemini_api_key) # Ensure configuration is done
                self.llm = genai.GenerativeModel(self.model_name)
                self.logger.info(f"Gemini GenerativeModel initialized with model: {self.model_name}.")
            except Exception as e:
                self.logger.error(f"Failed to initialize Gemini client with model {self.model_name}: {e}", exc_info=True)
                self.llm = None
        else:
            self.llm = None
            self.logger.warning("GEMINI_API_KEY not found. LLM functionality will be disabled.")

        # --- Web Search Agent Integration (Optional - Kept for potential future use/context) ---
        self.web_search_agent_url = os.getenv('WEB_SEARCH_AGENT_URL')
        self.brave_api_key = os.getenv('BRAVE_API_KEY') # Needed if WebSearchAgent requires it implicitly
        self.http_client = httpx.AsyncClient(timeout=60.0) # Increased timeout for A2A calls

        if not self.web_search_agent_url:
            self.logger.info("WEB_SEARCH_AGENT_URL not found. Web search integration is disabled.")
        else:
            self.logger.info(f"Web Search Agent URL configured: {self.web_search_agent_url}")
            if not self.brave_api_key:
                 self.logger.warning("BRAVE_API_KEY not found. WebSearchAgent might fail if it requires this key.")


        self.logger.info("ImprovementAgent initialized.")

    async def _run_web_search(self, query: str, num_results: int = 5) -> Optional[List[Dict]]:
        """Helper to run web search via A2A call."""
        if not self.web_search_agent_url:
            self.logger.info("Web search skipped: URL not configured.")
            return None

        self.logger.info(f"Performing web search with query: {query}")
        try:
            search_payload = {"query": query, "num_results": num_results}
            # Note: Ensure BRAVE_API_KEY is implicitly available to the WebSearchAgent service
            # or pass it if the A2A endpoint requires it explicitly in the payload/headers.
            a2a_url = f"{self.web_search_agent_url}/a2a/web_search/invoke" # Assuming endpoint path
            self.logger.info(f"Calling WebSearchAgent at {a2a_url}")

            response = await self.http_client.post(a2a_url, json=search_payload)
            response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)

            search_response_data = response.json()

            if response.status_code == 200 and search_response_data.get("status") == "success":
                 results = search_response_data.get("results", []) # Adjust key based on actual response
                 self.logger.info(f"Received {len(results)} results from WebSearchAgent.")
                 self.logger.debug(f"Web Search Results: {results}")
                 return results
            else:
                error_msg = search_response_data.get("message", "Unknown error from WebSearchAgent")
                self.logger.error(f"WebSearchAgent call failed internally: {error_msg}")
                return None # Proceed without search results

        except httpx.RequestError as req_err:
            self.logger.error(f"A2A call to WebSearchAgent failed (Request Error): {req_err}", exc_info=True)
        except httpx.HTTPStatusError as status_err:
             self.logger.error(f"A2A call to WebSearchAgent failed (Status Code {status_err.response.status_code}): {status_err.response.text}", exc_info=True)
        except json.JSONDecodeError as json_err:
             self.logger.error(f"Failed to decode JSON response from WebSearchAgent: {json_err}", exc_info=True)
        except Exception as search_err: # Catch any other unexpected errors during search
            self.logger.error(f"Unexpected error during web search A2A call: {search_err}", exc_info=True)

        return None # Return None on any error

    async def run_async(self, context: InvocationContext) -> Event:
        """Executes the product improvement workflow asynchronously using LLM."""
        self.logger.info(f"Received invocation: {context.invocation_id}")

        # --- 1. Input Validation ---
        try:
            if not isinstance(context.input_event.payload, dict):
                raise ValueError("Input payload must be a dictionary.")
            # Use the new input model based on MarketOpportunityReport
            inputs = MarketOpportunityReportInput(**context.input_event.payload)
            self.logger.info(f"Starting product improvement analysis based on market report.")
            self.logger.debug(f"Input Analysis Keys: {list(inputs.analysis.keys())}")
            self.logger.debug(f"Input Competitors Count: {len(inputs.competitors)}")
        except (ValidationError, ValueError) as e:
            self.logger.error(f"Input validation failed: {e}")
            return ErrorEvent(
                error_code="INPUT_VALIDATION_ERROR",
                message=f"Invalid input payload (expected MarketOpportunityReport structure): {e}",
                details=e.errors() if isinstance(e, ValidationError) else None
            )

        # --- 2. Optional: Web Search (Example: Search based on competitor analysis) ---
        # Decide if web search is needed based on input. E.g., search for tech mentioned in features.
        web_search_results = None
        search_query = None
        if inputs.feature_recommendations:
            # Example: Search for the first recommended feature if it seems technical
            first_feature = inputs.feature_recommendations[0]
            if any(tech_kw in first_feature.lower() for tech_kw in ["api", "sdk", "integration", "platform"]):
                 search_query = f"Technical details and existing solutions for feature: {first_feature}"

        if search_query and self.web_search_agent_url:
            web_search_results = await self._run_web_search(search_query)

        # --- 3. LLM Analysis ---
        if not self.llm:
            self.logger.error("LLM client not initialized. Cannot proceed with core analysis.")
            return ErrorEvent(
                error_code="LLM_NOT_INITIALIZED",
                message="LLM client (Gemini) is not available. Check API key and configuration.",
            )

        try:
            # Prepare Prompt using the new input model and output spec
            prompt = self._build_llm_prompt(inputs, web_search_results)
            self.logger.debug(f"Generated LLM Prompt:\n{prompt[:500]}...") # Log beginning of prompt

            # Call LLM
            self.logger.info("Calling LLM for product improvement analysis...")
            # Consider enabling JSON mode if the model supports it reliably
            # generation_config = genai.types.GenerationConfig(response_mime_type="application/json")
            # response = await self.llm.generate_content_async(prompt, generation_config=generation_config)
            response = await self.llm.generate_content_async(prompt)
            self.logger.info("LLM call completed.")
            llm_output_text = response.text

        except Exception as llm_error:
            self.logger.error(f"LLM call failed: {llm_error}", exc_info=True)
            # Attempt to get more details from the exception if available
            details = {"exception_type": type(llm_error).__name__, "exception_args": llm_error.args}
            if hasattr(llm_error, 'response'): # Handle potential API errors with response details
                details["response_status"] = getattr(llm_error.response, 'status_code', None)
                details["response_text"] = getattr(llm_error.response, 'text', None)

            return ErrorEvent(
                error_code="LLM_API_ERROR",
                message=f"Error interacting with the LLM: {str(llm_error)}",
                details=details
            )

        # --- 4. Parse and Validate LLM Output ---
        try:
            # Clean the output (remove potential markdown fences)
            cleaned_output = llm_output_text.strip().removeprefix("```json").removesuffix("```").strip()
            if not cleaned_output:
                 raise ValueError("LLM returned empty content after cleaning.")
            llm_data = json.loads(cleaned_output)
            # Validate against the new output model
            spec = ImprovedProductSpecOutput(**llm_data)
            self.logger.info("LLM output parsed and validated successfully against ImprovedProductSpecOutput.")
        except json.JSONDecodeError as json_err:
            self.logger.error(f"Failed to parse LLM JSON output: {json_err}")
            self.logger.debug(f"Raw LLM Output:\n{llm_output_text}")
            return ErrorEvent(
                error_code="LLM_OUTPUT_PARSE_ERROR",
                message=f"Failed to parse JSON from LLM response: {json_err}",
                details={"raw_output": llm_output_text}
            )
        except ValidationError as validation_err:
            self.logger.error(f"LLM output validation failed against ImprovedProductSpecOutput: {validation_err}")
            parsed_data_str = json.dumps(llm_data, indent=2) if 'llm_data' in locals() else 'N/A'
            self.logger.debug(f"Parsed LLM Data:\n{parsed_data_str}")
            return ErrorEvent(
                error_code="LLM_OUTPUT_VALIDATION_ERROR",
                message=f"LLM output did not match expected ImprovedProductSpecOutput format: {validation_err}",
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

    def _build_llm_prompt(self, inputs: MarketOpportunityReportInput, web_search_results: Optional[List[Dict]] = None) -> str:
        """Constructs the prompt for the LLM based on market report data and optional web search results."""

        # Use the new output model schema
        output_schema_description = json.dumps(ImprovedProductSpecOutput.model_json_schema(), indent=2)

        # --- Build Web Search Context String ---
        search_context = "No web search performed or no relevant results found."
        if web_search_results:
            search_context = "Web Search Results Summary (Potential technical context):\n"
            for i, result in enumerate(web_search_results[:5]): # Limit context length
                 title = result.get('title', 'N/A')
                 snippet = result.get('snippet', 'N/A') # Adjust keys based on actual WebSearchAgent output
                 link = result.get('link', '#')
                 search_context += f"{i+1}. {title}: {snippet} ({link})\n"
            search_context = search_context.strip()

        # --- Build Market Analysis Context String ---
        analysis_summary = "Market Analysis Summary:\n"
        for key, value in inputs.analysis.items():
            analysis_summary += f"*   **{key.replace('_', ' ').title()}:** {value}\n"
        analysis_summary = analysis_summary.strip()

        # --- Build Competitor Context String ---
        competitor_summary = "Competitor Summary:\n"
        if inputs.competitors:
            for i, comp in enumerate(inputs.competitors[:5]): # Limit context
                url = comp.get('url', 'N/A')
                desc = comp.get('description', 'N/A')
                competitor_summary += f"{i+1}. {url}: {desc}\n"
        else:
            competitor_summary += "No specific competitors listed in the report."
        competitor_summary = competitor_summary.strip()


        # --- Enhanced Prompt ---
        prompt = f"""
You are an expert Product Strategist AI. Your task is to analyze the provided Market Opportunity Report, potentially supplemented by web search results, and generate a detailed, innovative, and actionable specification for an improved product or service.

**Input: Market Opportunity Report**

*   **Competitors:**
    {competitor_summary}
*   **Market Analysis:**
    {analysis_summary}
*   **Feature Recommendations (from research):** {inputs.feature_recommendations or 'None provided'}
*   **Target Audience Suggestions (from research):** {inputs.target_audience_suggestions or 'None provided'}
*   **Business Model Type:** {inputs.business_model_type or 'Not specified'}

**Web Search Context (if available):**

{search_context}

**Analysis & Generation Task:**

Perform a thorough analysis of all provided inputs (market data and web search context). Based on this analysis, generate a JSON object representing the `ImprovedProductSpecOutput`. Follow these steps meticulously:

1.  **Deep Analysis:**
    *   Synthesize insights from competitor analysis (especially weaknesses if mentioned), market gaps, feature recommendations, and target audience suggestions.
    *   Identify the core problems to solve or opportunities to seize. What is the *most promising direction* based on the report?
    *   Consider how the web search results (if provided) inform technical feasibility, competitor landscape, or innovative approaches for features.
2.  **Derive & Refine Product Concept:** Based *solely* on your analysis of the market report, formulate a concise, compelling description of the core product/service concept. This concept should directly address the opportunities identified.
3.  **Define Target Audience:** Clearly define the primary (and potentially secondary) target audience(s) based on the suggestions and your analysis. Be specific about demographics, needs, and pain points this product will address.
4.  **Brainstorm & Select Key Features:**
    *   Generate a list of potential features that directly address the identified problems/opportunities and target audience needs, drawing inspiration from the report's recommendations and your analysis. Think creatively.
    *   Select the 3-5 *most impactful* core features for the initial product.
    *   For each selected feature, provide:
        *   `feature_name`: A clear, concise name.
        *   `description`: A detailed explanation of what the feature does and the user benefit, linking it back to the market analysis if possible.
        *   `estimated_difficulty`: An integer score (1-10, 1=trivial, 10=very complex) estimating implementation effort.
        *   `estimated_impact`: A qualitative assessment ("Low", "Medium", "High") of the feature's potential contribution to user value or business goals.
        *   `implementation_steps`: A *brief* list (3-5 high-level steps) outlining the technical or process steps required.
5.  **Identify Improvements / USPs:** Formulate 2-3 clear, concise `identified_improvements`. These should highlight what makes the proposed product unique or better compared to alternatives, directly derived from addressing market gaps, competitor weaknesses, or leveraging unique features. These are the Unique Selling Propositions.
6.  **Estimate Overall Difficulty & Impact (Optional):** If you can confidently estimate based on the features:
    *   `implementation_difficulty`: An overall integer score (1-10) reflecting the complexity of building the complete spec.
    *   `revenue_impact`: An overall qualitative estimate ("Low", "Medium", "High") of the potential market success and revenue generation.

**Output Format Constraint:**

**CRITICAL:** Generate *ONLY* a single, valid JSON object that strictly adheres to the following Pydantic schema (`ImprovedProductSpecOutput`). Do *NOT* include any introductory text, concluding remarks, explanations, apologies, markdown formatting (like ```json), or any characters outside the JSON object itself.

```json
{output_schema_description}
```

**Example Feature Structure (within `key_features` list):**
```json
{{
  "feature_name": "AI-Powered Market Gap Finder",
  "description": "Analyzes competitor reviews and market trends (using NLP) to automatically identify underserved niches, addressing the 'market gap identification' need from the report.",
  "estimated_difficulty": 8,
  "estimated_impact": "High",
  "implementation_steps": [
    "Select and integrate NLP model for sentiment/topic analysis",
    "Develop data ingestion pipeline for reviews/trends",
    "Build backend analysis engine",
    "Create frontend dashboard for visualization",
    "Implement alert system for new gaps"
  ]
}}
```

Now, based *only* on the provided Market Opportunity Report and optional web search context, generate the required JSON object.
"""
        return prompt


# --- Flask Blueprint for A2A REST Endpoint ---

improvement_a2a_bp = Blueprint('improvement_a2a_bp', __name__, url_prefix='/a2a/improvement')

# Configure logger for the blueprint
logger = logging.getLogger(__name__) # Use module-level logger

# --- Agent Instantiation (Simple Approach) ---
# In a real app, consider managing agent instances via Flask app context
# or a dedicated service layer for better lifecycle management and configuration.
improvement_agent_instance = None

def get_improvement_agent():
    """Gets or creates the ImprovementAgent instance."""
    global improvement_agent_instance
    if improvement_agent_instance is None:
        logger.info("Creating new ImprovementAgent instance for A2A endpoint.")
        # You could pass specific model names or configs here if needed
        improvement_agent_instance = ImprovementAgent()
    return improvement_agent_instance

@improvement_a2a_bp.route('/run', methods=['POST'])
def run_improvement_stage():
    """REST endpoint for WorkflowManagerAgent to trigger Stage 2."""
    data = request.get_json()
    task_id = data.get('task_id')
    stage = data.get('stage')
    input_data = data.get('input_data') # Expected to be MarketOpportunityReport dict

    logger.info(f"[A2A /run] Received improvement request for task_id: {task_id}, stage: {stage}")

    # --- Basic Request Validation ---
    if not task_id or stage != 'stage_2_improvement' or not isinstance(input_data, dict):
        logger.error(f"[A2A /run] Invalid request data for task_id: {task_id}. Stage: {stage}, Input Type: {type(input_data)}")
        return jsonify({
            "task_id": task_id,
            "status": "failure",
            "error_message": "Invalid request data. Required: task_id (string), stage='stage_2_improvement', input_data (dict representing MarketOpportunityReport)."
        }), 400

    # --- Input Mapping & Agent Invocation ---
    try:
        # 1. Get Agent Instance
        agent = get_improvement_agent()
        if not agent.llm: # Check if agent initialized correctly (e.g., has LLM)
             logger.error(f"[A2A /run] ImprovementAgent LLM not available for task_id: {task_id}")
             return jsonify({
                "task_id": task_id,
                "status": "failure",
                "error_message": "ImprovementAgent failed to initialize (LLM unavailable). Check API key/config."
             }), 500

        # 2. Prepare Invocation Context
        # The input_data *is* the payload expected by the agent's run_async method
        # after validation via MarketOpportunityReportInput.
        # We create a simple UserEvent containing this payload.
        input_event = UserEvent(payload=input_data)
        context = InvocationContext(
            invocation_id=f"a2a-{task_id}-{stage}-{random.randint(1000,9999)}", # Generate unique invocation ID
            input_event=input_event
        )

        # 3. Run Agent Logic (Synchronously execute the async method)
        # Note: Using asyncio.run() in a sync Flask route can have limitations
        # in production environments with certain WSGI servers (like Gunicorn).
        # Consider using async Flask (Quart or flask[async]) for better async handling.
        logger.info(f"[A2A /run] Invoking ImprovementAgent.run_async for task_id: {task_id}")
        result_event = asyncio.run(agent.run_async(context))
        logger.info(f"[A2A /run] Agent execution completed for task_id: {task_id}. Event type: {type(result_event)}")

        # 4. Process Result
        if isinstance(result_event, ErrorEvent):
            logger.error(f"[A2A /run] Agent returned error for task_id: {task_id}. Code: {result_event.error_code}, Message: {result_event.message}")
            return jsonify({
                "task_id": task_id,
                "status": "failure",
                "error_message": f"Agent error ({result_event.error_code}): {result_event.message}",
                "error_details": result_event.details # Include details if available
            }), 500 # Internal Server Error or appropriate code based on error_code
        elif isinstance(result_event, Event) and result_event.event_type == "product.improvement.completed":
            logger.info(f"[A2A /run] Agent returned success for task_id: {task_id}")
            # Payload should be the ImprovedProductSpecOutput dict
            improved_spec = result_event.payload
            return jsonify({
                "task_id": task_id,
                "status": "success",
                "result": improved_spec, # This is the ImprovedProductSpec dict
                "error_message": None
            }), 200
        else:
            # Handle unexpected event types
            logger.error(f"[A2A /run] Agent returned unexpected event type for task_id: {task_id}. Type: {type(result_event)}")
            return jsonify({
                "task_id": task_id,
                "status": "failure",
                "error_message": f"Agent returned unexpected result type: {type(result_event).__name__}"
            }), 500

    except ValidationError as e:
        # This catches validation errors if MarketOpportunityReportInput(**input_data) fails
        # *before* calling the agent, though the agent does its own validation now.
        logger.error(f"[A2A /run] Input data validation failed before agent call for task_id: {task_id}: {e}", exc_info=True)
        return jsonify({
            "task_id": task_id,
            "status": "failure",
            "error_message": f"Invalid input_data structure (does not match MarketOpportunityReport): {e}",
            "error_details": e.errors()
        }), 400
    except Exception as e:
        logger.error(f"[A2A /run] Unexpected error during agent execution for task_id: {task_id}: {e}", exc_info=True)
        return jsonify({
            "task_id": task_id,
            "status": "failure",
            "error_message": f"An unexpected server error occurred: {str(e)}"
        }), 500

# Note: This blueprint needs to be registered in the main Flask app (app.py or main.py)
# Example registration in backend/app.py:
# from backend.agents.improvement_agent import improvement_a2a_bp
# app.register_blueprint(improvement_a2a_bp)