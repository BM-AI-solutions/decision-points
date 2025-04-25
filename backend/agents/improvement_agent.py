import random
import asyncio
import logging
import os
import argparse # Added for server args
import httpx
from typing import List, Optional, Dict, Any
import json

import uvicorn # Added for server
from fastapi import FastAPI, HTTPException, Body # Added for server
from pydantic import BaseModel, Field, ValidationError

# Assuming ADK and Gemini libraries are installed
from google.adk.agents import Agent # Using base Agent as LLM logic is custom
from google.adk.runtime import InvocationContext
from google.adk.runtime.events import Event # Using base Event, create specific payloads
# Assuming Gemini library is used directly if not using LlmAgent base class features
try:
    import google.generativeai as genai
except ImportError:
    genai = None # Handle case where library might not be installed

# Configure logging
# Use logfire if configured globally, otherwise standard logging
try:
    import logfire
    logger = logfire
except ImportError:
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO"))


# --- Pydantic Models ---

class ImprovementAgentInput(BaseModel):
    """Input for the Improvement Agent /invoke endpoint."""
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

# --- Agent Class ---

class ImprovementAgent(Agent):
    """
    ADK Agent responsible for Stage 2: Product Improvement.
    Analyzes market research input and suggests product improvements/features.
    Uses Gemini for analysis and can optionally call a WebSearchAgent via A2A.
    """
    ENV_GEMINI_API_KEY = "GEMINI_API_KEY"
    ENV_GEMINI_MODEL_NAME = "GEMINI_MODEL_NAME"
    ENV_WEB_SEARCH_AGENT_URL = "WEB_SEARCH_AGENT_URL" # Changed from ID

    DEFAULT_GEMINI_MODEL = "gemini-1.5-flash-latest" # Updated default

    def __init__(self, agent_id: str = "improvement-agent"):
        """Initialize the Improvement Agent."""
        super().__init__(agent_id=agent_id)
        logger.info(f"Initializing ImprovementAgent ({self.agent_id})...")

        # --- Configuration from Environment ---
        self.model_name = os.environ.get(self.ENV_GEMINI_MODEL_NAME, self.DEFAULT_GEMINI_MODEL)
        self.web_search_agent_url = os.environ.get(self.ENV_WEB_SEARCH_AGENT_URL)
        gemini_api_key = os.environ.get(self.ENV_GEMINI_API_KEY)

        # --- LLM Client Initialization ---
        self.llm = None
        if not genai:
             logger.warning("google.generativeai library not found. LLM functionality disabled.")
        elif not gemini_api_key:
            logger.warning(f"{self.ENV_GEMINI_API_KEY} not configured. LLM functionality disabled.")
        else:
            try:
                genai.configure(api_key=gemini_api_key)
                self.llm = genai.GenerativeModel(self.model_name)
                logger.info(f"Gemini GenerativeModel initialized with model: {self.model_name}.")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini client with model {self.model_name}: {e}", exc_info=True)
                self.llm = None # Ensure llm is None if init fails

        # --- Web Search Agent Integration ---
        self.http_client = None # Initialize httpx client for A2A calls
        if not self.web_search_agent_url:
            logger.warning(f"{self.ENV_WEB_SEARCH_AGENT_URL} not configured. Web search integration disabled.")
        else:
            self.http_client = httpx.AsyncClient(timeout=30.0) # Create client if URL is set
            logger.info(f"Web Search Agent URL configured: {self.web_search_agent_url}")

        logger.info("ImprovementAgent initialized.")

    async def run_async(self, context: InvocationContext) -> Event:
        """Executes the product improvement workflow asynchronously."""
        logger.info(f"[{self.agent_id}] Received invocation: {context.invocation_id}")

        # --- 1. Input Validation ---
        try:
            if not isinstance(context.data, dict):
                raise ValueError("Input data must be a dictionary.")
            inputs = ImprovementAgentInput(**context.data)
            logger.info(f"Starting product improvement analysis for concept: {inputs.product_concept}")
        except (ValidationError, ValueError, TypeError) as e:
            logger.error(f"Input validation failed: {e}", exc_info=True)
            # Use context helper to create error event
            return context.create_event(
                event_type="adk.agent.error",
                data={"error": "Input Validation Error", "details": str(e)},
                metadata={"status": "error"}
            )

        # --- 2. Optional: Web Search via A2A ---
        web_search_results = None
        trigger_search = "technology" in inputs.product_concept.lower() or "competitor" in inputs.product_concept.lower()

        if self.http_client and self.web_search_agent_url and trigger_search:
            logger.info("Web search triggered based on product concept.")
            search_query = f"Technical details and competitors for product concept: {inputs.product_concept}"
            try:
                search_payload = {"query": search_query, "num_results": 5} # Assuming WebSearchAgent takes query
                # Ensure the URL is complete
                if not self.web_search_agent_url.startswith(("http://", "https://")):
                    raise ValueError(f"Invalid WEB_SEARCH_AGENT_URL format: {self.web_search_agent_url}")

                # Assuming the target agent has an /invoke endpoint
                invoke_url = f"{self.web_search_agent_url.rstrip('/')}/invoke"
                logger.info(f"Calling WebSearchAgent at {invoke_url} with query: {search_query}")

                response = await self.http_client.post(invoke_url, json=search_payload)
                response.raise_for_status()
                search_response_data = response.json()

                # Check response structure (assuming it returns a dict with 'results')
                if isinstance(search_response_data, dict) and "results" in search_response_data:
                     web_search_results = search_response_data.get("results", [])
                     logger.info(f"Received {len(web_search_results)} results from WebSearchAgent.")
                     logger.debug(f"Web Search Results: {web_search_results}")
                else:
                     logger.warning(f"WebSearchAgent returned unexpected data format: {search_response_data}")

            except httpx.RequestError as req_err:
                logger.error(f"A2A call to WebSearchAgent failed (Request Error): {req_err}", exc_info=True)
            except httpx.HTTPStatusError as status_err:
                 logger.error(f"A2A call to WebSearchAgent failed (Status Code {status_err.response.status_code}): {status_err.response.text}", exc_info=True)
            except json.JSONDecodeError as json_err:
                 logger.error(f"Failed to decode JSON response from WebSearchAgent: {json_err}", exc_info=True)
            except Exception as search_err:
                logger.error(f"Unexpected error during web search A2A call: {search_err}", exc_info=True)

        # --- 3. LLM Analysis ---
        if not self.llm:
            logger.error("LLM client not initialized. Cannot proceed.")
            return context.create_event(
                event_type="adk.agent.error",
                data={"error": "LLM Not Initialized", "details": "Check GEMINI_API_KEY."},
                metadata={"status": "error"}
            )

        try:
            prompt = self._build_llm_prompt(inputs, web_search_results)
            logger.debug("Generated LLM Prompt.") # Avoid logging full prompt

            logger.info("Calling LLM for product improvement analysis...")
            response = await self.llm.generate_content_async(prompt)
            logger.info("LLM call completed.")
            llm_output_text = response.text

        except Exception as llm_error:
            logger.error(f"LLM call failed: {llm_error}", exc_info=True)
            return context.create_event(
                event_type="adk.agent.error",
                data={"error": "LLM API Error", "details": str(llm_error)},
                metadata={"status": "error"}
            )

        # --- 4. Parse and Validate LLM Output ---
        try:
            cleaned_output = llm_output_text.strip().removeprefix("```json").removesuffix("```").strip()
            if not cleaned_output: raise ValueError("LLM returned empty content after cleaning.")
            llm_data = json.loads(cleaned_output)
            spec = ImprovedProductSpec(**llm_data)
            logger.info("LLM output parsed and validated successfully.")
        except (json.JSONDecodeError, ValidationError, ValueError) as parse_err:
            logger.error(f"Error processing LLM output: {parse_err}", exc_info=True)
            logger.debug(f"Raw LLM Output during processing error:\n{llm_output_text}")
            return context.create_event(
                event_type="adk.agent.error",
                data={"error": "LLM Output Processing Error", "details": str(parse_err), "raw_output": llm_output_text},
                metadata={"status": "error"}
            )

        # --- 5. Return Success Event ---
        logger.info("Product improvement analysis finished successfully.")
        return context.create_event(
            event_type="product.improvement.completed", # Specific event type
            data=spec.model_dump(), # Use model_dump for Pydantic v2
            metadata={"status": "success"}
        )

    def _build_llm_prompt(self, inputs: ImprovementAgentInput, web_search_results: Optional[List[Dict]] = None) -> str:
        """Constructs the prompt for the LLM based on input data and optional web search results."""
        output_schema_description = json.dumps(ImprovedProductSpec.model_json_schema(), indent=2)
        search_context = "No web search performed or no relevant results found."
        if web_search_results:
            search_context = "Web Search Results Summary:\n"
            for i, result in enumerate(web_search_results[:5]): # Limit context
                 title = result.get('title', 'N/A')
                 # Adjust keys based on actual WebSearchAgent output ('summary' or 'description')
                 snippet = result.get('summary') or result.get('description', 'N/A')
                 link = result.get('source') or result.get('url', '#') # Adjust keys
                 search_context += f"{i+1}. {title}: {snippet} ({link})\n"
            search_context = search_context.strip()

        # --- Using the detailed prompt from the previous file content ---
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

1.  **Deep Analysis:** Synthesize insights, identify core problems/opportunities, consider web search context.
2.  **Refine Product Concept:** Write a concise, compelling, refined description.
3.  **Define Target Audience:** Clearly define primary/secondary audience, needs, pain points. Justify choice.
4.  **Brainstorm & Prioritize Key Features:** Generate potential features. Select 3-5 *most impactful* core features. For each: `feature_name`, `description`, `estimated_difficulty` (1-10), `estimated_impact` ('Low'/'Medium'/'High'), `implementation_steps` (brief list).
5.  **Develop Unique Selling Propositions (USPs):** Formulate 2-3 clear, concise USPs based on refined concept and features.
6.  **Assess Feasibility & Potential:** Provide `feasibility_score` (0.0-1.0), `potential_rating` ('Low'/'Medium'/'High'), `assessment_rationale` (brief justification).
7.  **Estimate Implementation & Revenue Impact (Optional):** Provide overall `implementation_difficulty_estimate` (1-10) and `potential_revenue_impact_estimate` ('Low'/'Medium'/'High').

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
"""
        return prompt

    async def close_clients(self):
        """Close any open HTTP clients."""
        if self.http_client and not self.http_client.is_closed:
            await self.http_client.aclose()
            logger.info("Closed httpx client.")


# --- FastAPI Server Setup ---

app = FastAPI(title="ImprovementAgent A2A Server")

# Instantiate the agent (reads env vars internally)
try:
    improvement_agent_instance = ImprovementAgent()
except ValueError as e:
    logger.critical(f"Failed to initialize ImprovementAgent: {e}. Server cannot start.", exc_info=True)
    import sys
    sys.exit(f"Agent Initialization Error: {e}")


@app.post("/invoke", response_model=ImprovedProductSpec) # Expect ImprovedProductSpec on success
async def invoke_agent(request: ImprovementAgentInput = Body(...)):
    """
    A2A endpoint to invoke the ImprovementAgent.
    Expects JSON body matching ImprovementAgentInput.
    Returns ImprovedProductSpec on success, or raises HTTPException on error.
    """
    logger.info(f"ImprovementAgent /invoke called for concept: {request.product_concept}")
    invocation_id = f"improve-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(1000,9999)}"
    context = InvocationContext(agent_id="improvement-agent", invocation_id=invocation_id, data=request.model_dump())

    try:
        result_event = await improvement_agent_instance.run_async(context)

        if result_event and result_event.metadata.get("status") == "success":
            # Validate the payload structure before returning
            try:
                # Assuming the payload directly matches ImprovedProductSpec
                validated_payload = ImprovedProductSpec(**result_event.data)
                logger.info(f"ImprovementAgent returning success result.")
                return validated_payload
            except ValidationError as val_err:
                 logger.error(f"Success event payload validation failed: {val_err}. Payload: {result_event.data}")
                 raise HTTPException(status_code=500, detail={"error": "Internal validation error on success payload.", "details": val_err.errors()})

        elif result_event and result_event.metadata.get("status") == "error":
             error_details = result_event.data.get("details", "Unknown agent error")
             logger.error(f"ImprovementAgent run_async returned error event: {error_details}")
             raise HTTPException(status_code=500, detail=result_event.data) # Return error payload
        else:
            logger.error(f"ImprovementAgent run_async returned None or invalid event data: {result_event}")
            raise HTTPException(status_code=500, detail="Agent execution failed to return a valid event.")

    except HTTPException as http_exc:
        raise http_exc # Re-raise FastAPI exceptions
    except Exception as e:
        logger.error(f"Error during agent invocation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail={"error": f"Internal server error: {e}"})

@app.get("/health")
async def health_check():
    # Add checks for LLM client and web search URL if needed
    return {"status": "ok"}

# --- Server Shutdown Hook ---
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down ImprovementAgent server...")
    await improvement_agent_instance.close_clients() # Close httpx client

# --- Main execution block ---

if __name__ == "__main__":
    # Load .env for local development if needed
    try:
        from dotenv import load_dotenv
        if load_dotenv():
             logger.info("Loaded .env file for local run.")
        else:
             logger.info("No .env file found or it was empty.")
    except ImportError:
        logger.info("dotenv library not found, skipping .env load.")

    parser = argparse.ArgumentParser(description="Run the ImprovementAgent A2A server.")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind the server to.")
    parser.add_argument("--port", type=int, default=8086, help="Port to run the server on.") # Default matches compose
    args = parser.parse_args()

    # Ensure critical env var is present before starting server (optional check)
    # if not os.environ.get(ImprovementAgent.ENV_GEMINI_API_KEY):
    #      print(f"WARNING: Environment variable {ImprovementAgent.ENV_GEMINI_API_KEY} not set. LLM features disabled.")

    print(f"Starting ImprovementAgent A2A server on {args.host}:{args.port}")

    uvicorn.run(app, host=args.host, port=args.port)