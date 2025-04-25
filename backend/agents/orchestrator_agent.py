import asyncio
import json
import logging
import os # Added for environment variables
import argparse # Added for server args
import httpx # Added for A2A HTTP calls
from datetime import datetime
from typing import Any, Dict, List, Optional, Union, Tuple

# Assuming Flask-SocketIO is still used for real-time updates
try:
    from flask_socketio import SocketIO
    SOCKETIO_AVAILABLE = True
except ImportError:
    SOCKETIO_AVAILABLE = False
    SocketIO = None # Define as None if not available

# Assuming ADK and Gemini libraries are installed
from google.adk.agents import LlmAgent, BaseAgent # Import BaseAgent for type hinting
from google.adk.models import Gemini, BaseLlm
from google.adk.tools import ToolContext # Keep if tools are used by Orchestrator's LLM
from google.adk.runtime import InvocationContext
from google.adk.runtime.events import Event, EventSeverity # Use EventSeverity

# Configure logging
# Use logfire if configured globally, otherwise standard logging
try:
    import logfire
    logger = logfire
except ImportError:
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO"))

# --- Pydantic Models for FastAPI ---

class OrchestratorInput(BaseModel):
    """Input model for the /invoke endpoint."""
    prompt: str = Field(description="The user's input prompt.")
    session_id: str = Field(description="The ID of the user session.")
    # Add any other relevant input parameters here

class OrchestratorOutput(BaseModel):
    """Generic output model for the /invoke endpoint."""
    status: str = Field(description="Status of the orchestration task (e.g., 'submitted', 'delegating', 'completed', 'failed').")
    message: str = Field(description="A human-readable message about the task status.")
    result: Optional[Any] = Field(None, description="The final result of the task, if completed.")
    agent: Optional[str] = Field(None, description="The agent that handled the task (e.g., 'self', 'market_analyzer').")
    task_id: str = Field(description="The ID of the task/invocation.")

class OrchestratorErrorOutput(BaseModel):
    """Output model for the /invoke endpoint on failure."""
    error: str
    details: Optional[Any] = None


# --- Orchestrator Agent ---

class OrchestratorAgent(LlmAgent):
    """
    Orchestrator agent refactored to use ADK patterns and A2A HTTP communication.
    Handles user prompts, classifies intent, delegates to specialized agents via HTTP,
    and emits updates (potentially via SocketIO if configured).
    """
    # Environment variables for agent URLs
    ENV_MARKET_ANALYSIS_AGENT_URL = "MARKET_ANALYSIS_AGENT_URL"
    ENV_CONTENT_GENERATION_AGENT_URL = "CONTENT_GENERATION_AGENT_URL"
    ENV_LEAD_GENERATION_AGENT_URL = "LEAD_GENERATION_AGENT_URL"
    ENV_FREELANCE_TASK_AGENT_URL = "FREELANCE_TASK_AGENT_URL"
    ENV_WEB_SEARCH_AGENT_URL = "WEB_SEARCH_AGENT_URL"
    ENV_WORKFLOW_MANAGER_AGENT_URL = "WORKFLOW_MANAGER_AGENT_URL"
    ENV_BRANDING_AGENT_URL = "BRANDING_AGENT_URL"
    ENV_CODE_GENERATION_AGENT_URL = "CODE_GENERATION_AGENT_URL"
    ENV_DEPLOYMENT_AGENT_URL = "DEPLOYMENT_AGENT_URL"

    ENV_GEMINI_MODEL_NAME = "GEMINI_MODEL_NAME" # For classification LLM
    DEFAULT_GEMINI_MODEL = "gemini-1.5-flash-latest" # Updated default for classification

    # Mapping of logical agent keys to their environment variable names
    AGENT_URL_ENVS = {
        "market_analyzer": ENV_MARKET_ANALYSIS_AGENT_URL,
        "content_generator": ENV_CONTENT_GENERATION_AGENT_URL,
        "lead_generator": ENV_LEAD_GENERATION_AGENT_URL,
        "freelance_tasker": ENV_FREELANCE_TASK_AGENT_URL,
        "web_searcher": ENV_WEB_SEARCH_AGENT_URL,
        "workflow_manager": ENV_WORKFLOW_MANAGER_AGENT_URL,
        "branding_agent": ENV_BRANDING_AGENT_URL,
        "code_generation_agent": ENV_CODE_GENERATION_AGENT_URL,
        "deployment_agent": ENV_DEPLOYMENT_AGENT_URL,
    }

    # Mapping of logical agent keys to their expected input Pydantic models (for delegation payload)
    # This requires the orchestrator to know the input schemas of other agents.
    # This is a simplified mapping; in a real system, this might be discovered or more formal.
    AGENT_INPUT_MODELS = {
        # Assuming simple input models for now based on agent refactors
        "market_analyzer": "MarketAnalysisInput", # Needs to be imported or defined
        "content_generator": "ContentGenInput", # Needs to be imported or defined
        "lead_generator": "LeadGenInput", # Needs to be imported or defined
        "freelance_tasker": "FreelanceTaskInput", # Needs to be imported or defined
        "web_searcher": "WebSearchInput", # Assuming a simple input model exists
        "workflow_manager": "WorkflowManagerInput", # Assuming input model exists
        "branding_agent": "BrandingAgentInput", # Needs to be imported or defined
        "code_generation_agent": "CodeGenInput", # Needs to be imported or defined
        "deployment_agent": "DeploymentAgentInputData", # Needs to be imported or defined
    }
    # TODO: Import or define these input models within this file or a shared location.
    # For now, we'll pass raw dicts based on assumptions.

    # If SocketIO is used, it needs to be passed during initialization or accessed globally
    # Keeping it as a parameter for now, assuming it's injected.
    def __init__(
        self,
        socketio: Optional[SocketIO] = None, # Make SocketIO optional
        agent_id: str = "orchestrator-agent", # Use agent_id convention
        model_name: Optional[str] = None, # For classification LLM
        instruction: Optional[str] = None,
        name: str = "OrchestratorAgent",
        description: str = "Handles user prompts and orchestrates tasks, potentially delegating to specialized agents.",
        **kwargs: Any,
    ):
        """
        Initializes the ADK-based Orchestrator Agent.
        """
        # Determine the model name for classification
        effective_model_name = model_name or os.environ.get(self.ENV_GEMINI_MODEL_NAME, self.DEFAULT_GEMINI_MODEL)
        self.model_name = effective_model_name

        # Initialize the ADK Gemini model for classification
        # Assumes GOOGLE_API_KEY is configured via environment variable for ADK/Gemini
        try:
            # Use the ADK model abstraction if possible, or configure genai directly
            # If using LlmAgent base, it handles model init. If not, configure genai here.
            # Since we inherit LlmAgent, it should handle this if GOOGLE_API_KEY is set.
            # adk_model = Gemini(model=self.model_name) # LlmAgent base does this
            pass # LlmAgent handles model init

        except Exception as e:
            logger.error(f"Failed to initialize Gemini client for classification with model {self.model_name}: {e}", exc_info=True)
            # Decide how to handle this - classification will fail without LLM
            # For now, log and continue, classification will return "self" on error.

        # Ensure instruction is provided, even if basic
        if instruction is None:
            instruction = "Process the user's request."

        # Initialize the LlmAgent base class
        super().__init__(
            agent_id=agent_id, # Pass agent_id
            name=name,
            description=description,
            model=Gemini(model=self.model_name), # Initialize model here for LlmAgent base
            instruction=instruction,
            **kwargs
        )

        self.socketio = socketio # Store SocketIO instance
        self.agent_urls: Dict[str, str] = {} # Store resolved agent URLs

        # Resolve agent URLs from environment variables
        for key, env_var in self.AGENT_URL_ENVS.items():
            url = os.environ.get(env_var)
            if url:
                self.agent_urls[key] = url.rstrip('/') # Store URL, remove trailing slash
                logger.info(f"Resolved URL for agent '{key}': {self.agent_urls[key]}")
            else:
                logger.warning(f"Environment variable {env_var} not set. Delegation to '{key}' will be disabled.")

        # Initialize httpx client for A2A calls
        self.http_client = httpx.AsyncClient(timeout=120.0) # Increased timeout for agent calls

        logger.info(f"{self.name} ({self.agent_id}) initialized with resolved agent URLs: {list(self.agent_urls.keys())}.")
        if not SOCKETIO_AVAILABLE:
            logger.warning("Flask-SocketIO not available. Real-time task updates will be disabled.")


    async def run_async(self, context: InvocationContext) -> Event:
        """
        Processes a task using ADK patterns, delegates via A2A HTTP, and emits updates.
        Reads input from context.data.
        """
        task_id = context.invocation_id # Use invocation_id as task ID
        # Assuming prompt is directly in context.data
        prompt = context.data.get("prompt", "No prompt provided")
        session_id = context.data.get("session_id", "unknown_session") # Get session ID from input

        logger.info(f"[{self.agent_id}] Received task {task_id} for session {session_id} with prompt: '{prompt}'")

        # Emit initial acknowledgment via SocketIO if available
        self._emit_task_update(session_id, task_id, 'submitted', f"Task received by Orchestrator: {prompt}")

        # --- LLM-based Delegation Logic ---
        target_agent_key, classification_error = await self._classify_intent(prompt, task_id)

        if classification_error:
            logger.error(f"[{self.agent_id}] Task {task_id} classification failed: {classification_error}. Defaulting to 'self'.")
            target_agent_key = "self"
            self._emit_task_update(session_id, task_id, 'warning', f"Could not classify task intent: {classification_error}. Handling directly.")

        target_agent_url = self.agent_urls.get(target_agent_key)

        # --- Handle Delegation or Direct Processing ---
        if target_agent_key != "self" and target_agent_url:
            logger.info(f"[{self.agent_id}] Task {task_id} classified for delegation to {target_agent_key} at {target_agent_url}.")
            self._emit_task_update(session_id, task_id, 'delegating', f"Delegating task to {target_agent_key}...")

            try:
                # Prepare the request payload for the delegated agent's /invoke endpoint
                # This is a simplified approach; a real orchestrator might need more complex mapping
                delegation_payload = self._prepare_delegation_payload(context.data, target_agent_key, prompt)

                if delegation_payload is None:
                     error_message = f"Failed to prepare delegation payload for {target_agent_key}."
                     logger.error(f"[{self.agent_id}] Task {task_id} {error_message}")
                     raise ValueError(error_message) # Raise to be caught below

                # Make the A2A HTTP call
                logger.info(f"[{self.agent_id}] Calling {target_agent_key} /invoke endpoint at {target_agent_url}/invoke with payload...")
                response = await self.http_client.post(f"{target_agent_url}/invoke", json=delegation_payload)
                response.raise_for_status() # Raise HTTPError for bad responses

                delegated_response_data = response.json()

                # Assuming delegated agents return their result payload directly on success
                # and raise HTTPException with error details on failure.
                # We need to wrap the response data in an ADK Event structure for consistency.
                # This might require knowing the target agent's output schema or having a generic wrapper.
                # For simplicity, let's assume the response data is the 'data' part of a success event.
                # If the target agent returns a full ADK Event structure, we can parse it.

                # Let's assume target agents return a structure that can be wrapped in Event(data=...)
                # or Event(payload=...) depending on their design.
                # If they return a Pydantic model directly, we can use that.

                # Based on other agent refactors, they return Pydantic models on success via FastAPI.
                # Let's assume the response JSON is the success payload.
                # We need to create a *new* ADK Event to represent the result of this delegation step.
                # This event's payload will be the response data from the delegated agent.

                # Create a success event for the orchestration step
                orchestration_result_event = context.create_event(
                    event_type=f"orchestration.delegation.{target_agent_key}.completed",
                    data={"delegated_agent": target_agent_key, "result_payload": delegated_response_data},
                    metadata={"status": "success", "delegated_invocation_id": "unknown"} # Add delegated invocation ID if available
                )

                # Emit final completion update
                completion_message = f"Task completed by {target_agent_key}."
                # The actual result might be in delegated_response_data, decide how to present it
                self._emit_task_update(session_id, task_id, 'completed', completion_message, result=delegated_response_data)
                logger.info(f"[{self.agent_id}] Emitted 'task_update' (completed by {target_agent_key}) for task {task_id}.")

                return orchestration_result_event # Return the event representing the delegation result

            except httpx.HTTPStatusError as e:
                error_details = {"status_code": e.response.status_code, "response_text": e.response.text}
                try: error_details["response_json"] = e.response.json()
                except json.JSONDecodeError: pass
                error_message = f"Delegation to {target_agent_key} failed (HTTP Error {e.response.status_code})."
                logger.error(f"[{self.agent_id}] Task {task_id} delegation to {target_agent_key} failed: {error_message}", exc_info=True)
                self._emit_task_update(session_id, task_id, 'failed', error_message, result=error_details)
                return context.create_event(
                    event_type=f"orchestration.delegation.{target_agent_key}.failed",
                    data={"error": error_message, "details": error_details},
                    metadata={"status": "error"}
                )
            except httpx.RequestError as e:
                error_message = f"Delegation to {target_agent_key} failed (Request Error): {str(e)}"
                logger.error(f"[{self.agent_id}] Task {task_id} delegation to {target_agent_key} failed: {error_message}", exc_info=True)
                self._emit_task_update(session_id, task_id, 'failed', error_message, result={"exception": str(e)})
                return context.create_event(
                    event_type=f"orchestration.delegation.{target_agent_key}.failed",
                    data={"error": error_message, "details": {"exception": str(e)}},
                    metadata={"status": "error"}
                )
            except Exception as e:
                error_message = f"Delegation to {target_agent_key} failed (Unexpected Error): {str(e)}"
                logger.error(f"[{self.agent_id}] Task {task_id} delegation to {target_agent_key} failed: {error_message}", exc_info=True)
                self._emit_task_update(session_id, task_id, 'failed', error_message, result={"exception": str(e), "traceback": traceback.format_exc()})
                return context.create_event(
                    event_type=f"orchestration.delegation.{target_agent_key}.failed",
                    data={"error": error_message, "details": {"exception": str(e), "traceback": traceback.format_exc()}},
                    metadata={"status": "error"}
                )

        else:
            # Handle directly by Orchestrator ('self' or no valid agent found/configured)
            if target_agent_key != "self":
                 logger.warning(f"[{self.agent_id}] Task {task_id} classified for '{target_agent_key}', but agent URL not found or invalid. Handling directly.")
                 self._emit_task_update(session_id, task_id, 'warning', f"Could not delegate to '{target_agent_key}'. Handling directly.")
            else:
                 logger.info(f"[{self.agent_id}] Task {task_id} classified for 'self'. Handling directly.")

            # Emit processing update
            processing_message = f"Processing prompt with {self.model.model}..."
            self._emit_task_update(session_id, task_id, 'working', processing_message)

            try:
                # Execute the core LLM logic using the parent LlmAgent's run_async
                # The input for the LlmAgent's run_async is expected in context.input_event.actions[0].parts
                # We need to create an input event from the prompt in context.data
                llm_input_event = Event(
                    author="user", # Or "orchestrator"?
                    actions=[Action(content=Content(parts=[Part(text=prompt)]))],
                    invocation_id=task_id # Use the same invocation ID
                )
                # Create a new context for the LLM call with the correctly formatted input event
                llm_context = InvocationContext(
                    session=context.session, # Use the original session
                    input_event=llm_input_event
                )

                output_event = await super().run_async(llm_context) # Call parent's run_async

                # Extract the result text from the LLM output event
                llm_response_text = self._extract_text_from_event(output_event, "No text response generated by orchestrator.")

                # Check for errors indicated by the ADK event structure (e.g., error type, metadata status)
                if output_event.metadata.get("status") == "error":
                     error_message = output_event.data.get("error", "Orchestrator LLM processing failed.")
                     logger.error(f"[{self.agent_id}] Task {task_id} failed during orchestrator LLM processing: {error_message}")
                     self._emit_task_update(session_id, task_id, 'failed', error_message, result=output_event.data)
                     return output_event # Return the error event

                # Emit final completion update
                completion_message = "Task completed successfully by Orchestrator."
                self._emit_task_update(session_id, task_id, 'completed', completion_message, result=llm_response_text)
                logger.info(f"[{self.agent_id}] Emitted 'task_update' (completed by orchestrator) for task {task_id} with LLM response.")

                return output_event # Return the success event from the LLM call

            except Exception as e:
                error_message = f"Orchestrator processing failed: {str(e)}"
                logger.error(f"[{self.agent_id}] Task {task_id} failed during orchestrator processing: {error_message}", exc_info=True)
                self._emit_task_update(session_id, task_id, 'failed', error_message, result={"exception": str(e), "traceback": traceback.format_exc()})
                return context.create_event( # Create and return a new error event
                    event_type="orchestration.self.failed",
                    data={"error": error_message, "details": {"exception": str(e), "traceback": traceback.format_exc()}},
                    metadata={"status": "error"}
                )

    def _emit_task_update(self, session_id: str, task_id: str, status: str, message: str, result: Optional[Any] = None):
        """Emits a task update event via SocketIO if available."""
        if SOCKETIO_AVAILABLE and self.socketio:
            try:
                update_data = {
                    'task_id': task_id,
                    'status': status,
                    'message': message,
                    'result': result,
                    'timestamp': datetime.now().isoformat() # Add timestamp
                }
                # Emit to a specific room or user based on session_id if SocketIO is configured that way
                self.socketio.emit('task_update', update_data, room=session_id) # Assuming session_id is used as room
                logger.debug(f"[{self.agent_id}] Emitted SocketIO update for session {session_id}, task {task_id}: {status}")
            except Exception as e:
                logger.error(f"[{self.agent_id}] Failed to emit SocketIO update for session {session_id}, task {task_id}: {e}", exc_info=True)
        else:
            logger.warning(f"[{self.agent_id}] SocketIO not available or initialized. Cannot emit task update for task {task_id}.")


    def _prepare_delegation_payload(self, original_context_data: Dict[str, Any], target_agent_key: str, prompt: str) -> Optional[Dict[str, Any]]:
        """
        Prepares the request payload (dict) for the target agent's /invoke endpoint.
        This requires knowledge of the target agent's expected input schema.
        """
        # This is a simplified mapping based on assumptions about target agent inputs.
        # In a real system, this mapping would need to be robust and potentially dynamic.
        payload: Optional[Dict[str, Any]] = None

        if target_agent_key == "market_analyzer":
            # MarketAnalysisInput: action, niche, depth, niches, business_type, limit
            # Assume prompt contains the action and relevant parameters
            # This is complex; a better approach is to have the orchestrator's input
            # explicitly define parameters for sub-tasks, or use LLM to extract.
            # For now, let's assume the prompt implies the action and niche.
            # Example: "Analyze market trends for AI" -> action="analyze_trends", niche="AI"
            # This requires LLM output from classification to be more structured.
            # Let's simplify: Assume the prompt IS the primary input for the target agent.
            # The target agent's /invoke endpoint needs to handle parsing the prompt.
            # This contradicts the Pydantic models defined for other agents.

            # Let's revert to the idea that the orchestrator's input (context.data)
            # contains structured data, and the prompt is just a natural language request.
            # The orchestrator's LLM classifies the intent and identifies which *structured*
            # data from the original input should be passed to the target agent.

            # Re-evaluating: The original plan implies the orchestrator receives a prompt,
            # classifies it, and then calls other agents. The input to other agents
            # should likely be structured data derived from the *original* user request
            # or previous agent outputs, not just the raw prompt.

            # Let's assume the orchestrator's input `context.data` contains ALL
            # potential data needed by downstream agents, and the orchestrator's
            # LLM classification determines which subset of this data, plus the action,
            # to send to the target agent.

            # Example: Orchestrator receives { "prompt": "Analyze market trends for AI", "niche": "AI", "depth": "deep" }
            # LLM classifies as "market_analyzer". Orchestrator then constructs payload for MarketAnalysisAgent.
            # MarketAnalysisAgentInput expects { "action": "analyze_trends", "niche": "AI", "depth": "deep" }

            # This requires the orchestrator to map its input fields to target agent input fields.
            # This is getting complex. Let's simplify based on the *current* refactored agents' /invoke inputs.

            # Current refactored agent inputs:
            # - MarketAnalysisInput: action, niche, depth, niches, business_type, limit
            # - ContentGenInput: action, niche, quantity, focus, product_name, style
            # - LeadGenInput: user_query, num_links (API keys from env)
            # - FreelanceTaskInput: action, user_identifier, platform, criteria, task_details, new_state
            # - WebSearchInput (assumed): query, numResults
            # - BrandingAgentInput: product_concept, target_audience, keywords, business_model_type
            # - CodeGenInput: product_spec, branding
            # - DeploymentAgentInputData: brand_name, product_concept, key_features, deployment_target, generated_code_dict

            # The orchestrator's input `original_context_data` needs to contain fields
            # that can map to these. The initial `OrchestratorInput` only has `prompt` and `session_id`.
            # This means the orchestrator's LLM must extract parameters from the `prompt`.

            # Let's assume the orchestrator's LLM output from `_classify_intent`
            # could be more structured, e.g., {"agent": "market_analyzer", "params": {"action": "analyze_trends", "niche": "AI"}}.
            # But the current `_classify_intent` only returns the agent key.

            # Okay, let's make a pragmatic assumption: The orchestrator's input `context.data`
            # will contain the `prompt` and potentially other fields that can be directly
            # passed to target agents if their input schema matches. The orchestrator's
            # LLM classification determines the target agent and the *action* for that agent.
            # The rest of the payload comes from the original `context.data`.

            # This means the orchestrator's input needs to be richer than just prompt/session_id.
            # Let's update OrchestratorInput to include a generic 'params' field.
            # This requires changing the OrchestratorInput model and the /invoke endpoint.

            # Let's stick to the current OrchestratorInput (prompt, session_id) and the current
            # `_classify_intent` (returns agent key). This implies the orchestrator's LLM
            # needs to generate the *full payload* for the target agent based on the prompt.
            # This is a complex LLM task.

            # Alternative: The orchestrator's LLM output from `_classify_intent` is just the agent key.
            # The orchestrator then uses the *original prompt* as the primary input for the target agent.
            # This means target agents must be able to parse a raw prompt.
            # Looking at the refactored agents, they expect structured Pydantic inputs.

            # Let's go back to the idea that the orchestrator's input contains structured data.
            # The initial `OrchestratorInput` should include fields for potential downstream use.
            # This requires changing the API contract for the orchestrator.

            # Let's assume the orchestrator's `/invoke` endpoint will receive a body like:
            # { "prompt": "...", "session_id": "...", "task_data": { ... structured data ... } }
            # And `task_data` contains fields like `niche`, `product_spec`, `branding_package`, etc.

            # This requires changing the OrchestratorInput model. Let's do that.

            # New OrchestratorInput model: prompt, session_id, task_data (Dict[str, Any])

            task_data = original_context_data.get("task_data", {}) # Get the structured data

            # Now, map target_agent_key to the required payload structure using task_data and prompt.
            if target_agent_key == "market_analyzer":
                # MarketAnalysisInput: action, niche, depth, niches, business_type, limit
                # Assume prompt implies the action, and task_data has the rest.
                # This still requires LLM to identify the action from the prompt.
                # Let's assume the LLM classification output is just the agent key,
                # and the *action* for the target agent is also determined by the LLM
                # or is a default 'run' action that parses the prompt internally.
                # The refactored agents have specific actions like 'analyze_trends'.

                # Let's assume the orchestrator's LLM output from `_classify_intent`
                # *should* ideally include the action and parameters, but since it doesn't,
                # we'll make a simplifying assumption: the target agent's `/invoke` endpoint
                # can handle a payload that includes the original `prompt` and the `task_data`.
                # The target agent is then responsible for parsing this combined input.

                # This means the target agent's input models need to be updated to accept this.
                # This is a cascading change.

                # Alternative: The orchestrator's LLM output *must* be more structured.
                # Let's modify `_classify_intent` to return `(agent_key, action, params_dict)`.
                # This is a significant change to the LLM prompt and parsing.

                # Let's try the simplest approach first: Pass the original prompt and task_data
                # to the target agent's `/invoke` endpoint. The target agent's endpoint
                # needs to be flexible enough to handle this. This might require
                # updating the target agent's input models to include optional fields
                # or a generic `Any` field for the orchestrator's data.

                # Let's assume target agents' /invoke endpoints can accept a payload like:
                # { "prompt": "...", "task_data": { ... } }
                # And they parse this internally. This simplifies the orchestrator but
                # pushes complexity to the target agents.

                # Let's try this simplified delegation payload structure.
                payload = {
                    "prompt": prompt,
                    "task_data": task_data # Pass the structured data received by orchestrator
                }
                return payload

            # Add elif blocks for other agents, using the same payload structure
            # This requires target agents to be refactored to accept this.
            # This contradicts the Pydantic models defined in previous refactors.

            # Okay, the previous refactors defined specific Pydantic input models for each agent's /invoke.
            # The orchestrator *must* construct a payload that matches the target agent's specific input model.
            # This means the orchestrator needs to know the mapping.

            # Let's go back to the idea that the orchestrator's input `context.data`
            # contains the necessary structured data. The orchestrator's LLM
            # classifies the intent and identifies which *action* to call on the target agent.
            # The orchestrator then constructs the specific payload for that action
            # using fields from its own `context.data`.

            # This requires the orchestrator's input to be structured.
            # Let's update OrchestratorInput to include potential fields.

            # New OrchestratorInput: prompt, session_id, niche, product_spec, branding_package, etc.
            # This makes the orchestrator's input model very large and complex.

            # Alternative: The orchestrator's LLM output from `_classify_intent`
            # *must* include the action and parameters for the target agent.
            # Let's modify `_classify_intent` to return `(agent_key, action, params_dict)`.
            # This is the most robust approach for a true orchestrator.

            # Modifying _classify_intent to return action and params:
            # The LLM prompt needs to be updated to ask for the action and parameters in a structured format (e.g., JSON).
            # The parsing logic needs to handle this structured output.

            # Let's try this approach. Update _classify_intent prompt and parsing.

            # This means the `_classify_intent` method will return something like:
            # ("market_analyzer", "analyze_trends", {"niche": "AI", "depth": "deep"})

            # Then, in `run_async`, after getting `(target_agent_key, action, params_dict)`:
            # Construct the payload: `payload = {"action": action, **params_dict}`
            # This assumes all target agents take an "action" field and then other parameters.
            # Looking at refactored agents:
            # - MarketAnalysisInput: action, ...
            # - ContentGenInput: action, ...
            # - LeadGenInput: user_query, num_links (no explicit 'action' field, but user_query implies the action)
            # - FreelanceTaskInput: action, ...
            # - WebSearchInput (assumed): query (no explicit 'action')
            # - BrandingAgentInput: product_concept, ... (no explicit 'action')
            # - CodeGenInput: product_spec, branding (no explicit 'action')
            # - DeploymentAgentInputData: brand_name, ... (no explicit 'action')

            # This means the target agent's API contract is not uniform.
            # The orchestrator needs to know the specific input structure for each agent key.

            # Let's refine the `_prepare_delegation_payload` method. It will take the original prompt,
            # the target agent key, and the *full original context data*. It will then
            # construct the *specific* payload required by that target agent's `/invoke` endpoint.

            # This requires hardcoding the mapping from agent key to payload structure.
            # This is maintainable if the number of agents is small and their interfaces stable.

            # Let's implement `_prepare_delegation_payload` based on the refactored agent inputs.

            # Update OrchestratorInput to include potential fields needed by downstream agents.
            # This is the most practical approach given the current state of other agents.
            # OrchestratorInput: prompt, session_id, niche, product_spec, branding_package, etc.
            # This makes the orchestrator's API the central point for all potential inputs.

            # Let's update OrchestratorInput to include common potential fields.
            # This requires changing the FastAPI endpoint signature.

            # Let's try a compromise: Keep OrchestratorInput simple (prompt, session_id).
            # Modify `_classify_intent` to return `(agent_key, extracted_params_dict)`.
            # The LLM extracts parameters from the prompt.
            # Then `_prepare_delegation_payload` uses `extracted_params_dict` to build the target payload.

            # Modifying _classify_intent prompt and parsing to extract parameters:
            # Prompt needs to ask for agent key and a JSON object of parameters.
            # Parsing needs to handle JSON output from LLM.

            # Let's try this approach.

            CLASSIFICATION_PROMPT_TEMPLATE = """
Analyze the following user prompt and classify the primary intent. Your goal is to determine which specialized agent should handle this request, or if the orchestrator should handle it directly ('self'). Also, extract any relevant parameters from the prompt that the target agent might need.

Available agents and their functions:
- market_analyzer: Handles market analysis, trend identification, and finding business opportunities. Relevant parameters: niche (str), depth (str, 'standard' or 'deep'), niches (List[str]), business_type (str), limit (int).
- content_generator: Writes articles, marketing copy, or other forms of content. Relevant parameters: action (str, e.g., 'generate_marketing_copy', 'generate_text'), niche (str), quantity (int), focus (str), product_name (str), style (str), prompt (str - for 'generate_text').
- lead_generator: Finds potential leads, often involving web scraping or searching specific platforms like Quora. Relevant parameters: user_query (str), num_links (int).
- freelance_tasker: Finds and manages freelance jobs on platforms like Upwork. Relevant parameters: action (str, e.g., 'monitor_and_bid', 'execute_task', 'get_state', 'update_state'), user_identifier (str), platform (str), criteria (Dict), task_details (Dict), new_state (Dict), secret_id_suffix (str).
- web_searcher: Performs general web searches to find information. Relevant parameters: query (str), numResults (int).
- workflow_manager: Manages the multi-step autonomous income generation workflow. Relevant parameters: action (str, e.g., 'start_workflow', 'get_status'), workflow_id (str), input_data (Dict).
- branding_agent: Generates brand identity. Relevant parameters: product_concept (str), target_audience (List[str]), keywords (List[str]), business_model_type (str).
- code_generation_agent: Generates project code. Relevant parameters: product_spec (Dict), branding (Dict).
- deployment_agent: Deploys generated code. Relevant parameters: brand_name (str), product_concept (str), key_features (List[Dict]), deployment_target (str), generated_code_dict (Dict[str, str]).
- self: Use this if the request is general, doesn't fit other agents, or is a direct request to the orchestrator. No specific parameters needed for 'self'.

User Prompt:
"{user_prompt}"

Based on the user prompt, output a JSON object with two keys:
1.  "agent": The key of the most appropriate agent from the list above ('market_analyzer', 'content_generator', etc., or 'self').
2.  "params": A JSON object containing the relevant parameters extracted from the prompt for the chosen agent, matching the parameter names listed above. If no relevant parameters are found or the agent is 'self', this should be an empty JSON object {{}}.

Example Output:
{{
  "agent": "market_analyzer",
  "params": {{
    "action": "analyze_trends",
    "niche": "AI",
    "depth": "deep"
  }}
}}

Example Output for 'self':
{{
  "agent": "self",
  "params": {{}}
}}

Ensure your output is ONLY the JSON object.
"""
            # Update _classify_intent to parse this JSON output.

            # Update _prepare_delegation_payload to take extracted_params_dict and build the target payload.

            # This seems like a viable approach. Let's implement it.

            # Need to import the input models for other agents to use in _prepare_delegation_payload
            # This will create import cycles if agents import each other's models.
            # A shared models file is needed. Let's assume a `backend/app/schemas/agents.py` exists
            # and contains all necessary input/output models.

            # Assuming backend/app/schemas/agents.py exists and contains:
            # MarketAnalysisInput, ContentGenInput, LeadGenInput, FreelanceTaskInput,
            # WebSearchInput (define a simple one), BrandingAgentInput, CodeGenInput,
            # DeploymentAgentInputData, WorkflowManagerInput (define a simple one).

            # Let's add placeholder imports and assume these models exist.

            # Need to handle the case where the LLM output for params might not exactly match the Pydantic model.
            # Use Pydantic's `model_validate` or similar with `strict=False` or handle validation errors.

            # Let's proceed with this plan.

    async def _classify_intent(self, user_prompt: str, task_id: str) -> Tuple[str, Optional[Dict[str, Any]], Optional[str]]:
        """
        Uses the agent's LLM to classify the user prompt's intent and extract parameters.

        Returns:
            A tuple containing:
            - Classified agent key (str).
            - Extracted parameters (Dict[str, Any]) or None.
            - Optional error message (str).
            Defaults to ("self", {}, error_message) on classification error.
        """
        CLASSIFICATION_PROMPT_TEMPLATE = """
Analyze the following user prompt and classify the primary intent. Your goal is to determine which specialized agent should handle this request, or if the orchestrator should handle it directly ('self'). Also, extract any relevant parameters from the prompt that the target agent might need.

Available agents and their functions:
- market_analyzer: Handles market analysis, trend identification, and finding business opportunities. Relevant parameters: niche (str), depth (str, 'standard' or 'deep'), niches (List[str]), business_type (str), limit (int).
- content_generator: Writes articles, marketing copy, or other forms of content. Relevant parameters: action (str, e.g., 'generate_marketing_copy', 'generate_text'), niche (str), quantity (int), focus (str), product_name (str), style (str), prompt (str - for 'generate_text').
- lead_generator: Finds potential leads, often involving web scraping or searching specific platforms like Quora. Relevant parameters: user_query (str), num_links (int).
- freelance_tasker: Finds and manages freelance jobs on platforms like Upwork. Relevant parameters: action (str, e.g., 'monitor_and_bid', 'execute_task', 'get_state', 'update_state'), user_identifier (str), platform (str), criteria (Dict), task_details (Dict), new_state (Dict), secret_id_suffix (str).
- web_searcher: Performs general web searches to find information. Relevant parameters: query (str), numResults (int).
- workflow_manager: Manages the multi-step autonomous income generation workflow. Relevant parameters: action (str, e.g., 'start_workflow', 'get_status'), workflow_id (str), input_data (Dict).
- branding_agent: Generates brand identity. Relevant parameters: product_concept (str), target_audience (List[str]), keywords (List[str]), business_model_type (str).
- code_generation_agent: Generates project code. Relevant parameters: product_spec (Dict), branding (Dict).
- deployment_agent: Deploys generated code. Relevant parameters: brand_name (str), product_concept (str), key_features (List[Dict]), deployment_target (str), generated_code_dict (Dict[str, str]).
- self: Use this if the request is general, doesn't fit other agents, or is a direct request to the orchestrator. No specific parameters needed for 'self'.

User Prompt:
"{user_prompt}"

Based on the user prompt, output a JSON object with two keys:
1.  "agent": The key of the most appropriate agent from the list above ('market_analyzer', 'content_generator', etc., or 'self').
2.  "params": A JSON object containing the relevant parameters extracted from the prompt for the chosen agent, matching the parameter names listed above. If no relevant parameters are found or the agent is 'self', this should be an empty JSON object {{}}.

Example Output:
{{
  "agent": "market_analyzer",
  "params": {{
    "action": "analyze_trends",
    "niche": "AI",
    "depth": "deep"
  }}
}}

Example Output for 'self':
{{
  "agent": "self",
  "params": {{}}
}}

Ensure your output is ONLY the JSON object.
"""
        VALID_AGENT_KEYS = list(self.AGENT_URL_ENVS.keys()) + ["self"]

        classification_prompt = CLASSIFICATION_PROMPT_TEMPLATE.format(user_prompt=user_prompt)
        logger.debug(f"[{self.agent_id}] Task {task_id}: Sending classification prompt to LLM.") # Avoid logging full prompt

        try:
            # Use the agent's configured LLM via the base class's generate_content_async
            # Need to create a minimal context for this internal call
            llm_context = InvocationContext(
                session=InvocationContext.create_session(), # Temporary session
                input_event=Event(author="system", actions=[Action(content=Content(parts=[Part(text=classification_prompt)]))])
            )
            # Call the LLM using the base class method
            # Assuming LlmAgent base provides generate_content_async or similar
            # If not, need to use self.model directly (which is a Gemini model)
            # Let's assume LlmAgent provides a way to call the underlying model.
            # Looking at LlmAgent base, it has self.model which is the BaseLlm instance.
            # BaseLlm has generate_content_async.
            response = await self.model.generate_content_async(classification_prompt)

            llm_response_text = response.text.strip()
            logger.debug(f"[{self.agent_id}] Task {task_id}: Received classification response from LLM: '{llm_response_text}'")

            # Parse the JSON output
            try:
                classification_data = json.loads(llm_response_text)
                agent_key = classification_data.get("agent")
                params = classification_data.get("params", {})

                if agent_key in VALID_AGENT_KEYS:
                    logger.info(f"[{self.agent_id}] Task {task_id}: Classified as '{agent_key}' with params: {params}")
                    return agent_key, params, None
                else:
                    error_message = f"LLM classification returned invalid agent key: '{agent_key}'."
                    logger.warning(f"[{self.agent_id}] Task {task_id}: {error_message} Valid keys: {VALID_AGENT_KEYS}")
                    return "self", {}, error_message

            except json.JSONDecodeError as e:
                error_message = f"Failed to parse LLM classification JSON: {e}. Response: {llm_response_text}"
                logger.error(f"[{self.agent_id}] Task {task_id}: {error_message}", exc_info=True)
                return "self", {}, error_message
            except Exception as e:
                error_message = f"Error processing LLM classification response: {str(e)}. Response: {llm_response_text}"
                logger.error(f"[{self.agent_id}] Task {task_id}: {error_message}", exc_info=True)
                return "self", {}, error_message

        except Exception as e:
            error_message = f"LLM classification call failed: {str(e)}"
            logger.error(f"[{self.agent_id}] Task {task_id}: {error_message}", exc_info=True)
            return "self", {}, error_message


    def _prepare_delegation_payload(self, target_agent_key: str, extracted_params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Prepares the request payload (dict) for the target agent's /invoke endpoint
        based on the target agent key and extracted parameters.
        This requires hardcoded knowledge of each target agent's input schema.
        """
        payload: Optional[Dict[str, Any]] = None

        # Map extracted_params to the specific input model structure for each agent
        try:
            if target_agent_key == "market_analyzer":
                # MarketAnalysisInput: action, niche, depth, niches, business_type, limit
                # Assume extracted_params contains these fields
                payload = extracted_params # Direct mapping if params match
                # Validate against Pydantic model if possible (requires importing models)
                # MarketAnalysisInput(**payload) # Example validation
            elif target_agent_key == "content_generator":
                # ContentGenInput: action, niche, quantity, focus, product_name, style, prompt
                payload = extracted_params
                # ContentGenInput(**payload) # Example validation
            elif target_agent_key == "lead_generator":
                # LeadGenInput: user_query, num_links (API keys from env, added in endpoint)
                payload = extracted_params
                # LeadGenInput(**payload) # Example validation
            elif target_agent_key == "freelance_tasker":
                # FreelanceTaskInput: action, user_identifier, platform, criteria, task_details, new_state, secret_id_suffix
                payload = extracted_params
                # FreelanceTaskInput(**payload) # Example validation
            elif target_agent_key == "web_searcher":
                # WebSearchInput (assumed): query, numResults
                payload = extracted_params
                # WebSearchInput(**payload) # Example validation
            elif target_agent_key == "workflow_manager":
                # WorkflowManagerInput (assumed): action, workflow_id, input_data
                payload = extracted_params
                # WorkflowManagerInput(**payload) # Example validation
            elif target_agent_key == "branding_agent":
                # BrandingAgentInput: product_concept, target_audience, keywords, business_model_type
                payload = extracted_params
                # BrandingAgentInput(**payload) # Example validation
            elif target_agent_key == "code_generation_agent":
                # CodeGenInput: product_spec, branding
                payload = extracted_params
                # CodeGenInput(**payload) # Example validation
            elif target_agent_key == "deployment_agent":
                # DeploymentAgentInputData: brand_name, product_concept, key_features, deployment_target, generated_code_dict
                payload = extracted_params
                # DeploymentAgentInputData(**payload) # Example validation
            else:
                logger.error(f"[{self.agent_id}] Unknown target agent key '{target_agent_key}' for payload preparation.")
                return None # Cannot prepare payload for unknown agent

            # Add common fields if needed by target agents (e.g., session_id, invocation_id)
            # This depends on how target agents use their input.
            # Let's assume they primarily use the fields defined in their Pydantic models.

            return payload

        except Exception as e:
            logger.error(f"[{self.agent_id}] Error preparing delegation payload for '{target_agent_key}': {e}", exc_info=True)
            return None


    def _extract_text_from_event(self, event: Event, default_text: str = "") -> str:
        """Extracts the first text part from an event's actions."""
        if event and event.actions:
            for action in event.actions:
                if action.content and action.content.parts:
                    for part in action.content.parts:
                        if part.type == 'text' and part.text:
                            return part.text
        return default_text

    def _create_error_event(self, error_message: str, invocation_id: Optional[str] = None) -> Event:
         """Creates a standard error event using context helper."""
         # Need a context to use context.create_event.
         # If called outside run_async, need to create a minimal context or return raw Event.
         # Let's return a raw Event for simplicity here.
         return Event(
             agent_id=self.agent_id,
             invocation_id=invocation_id,
             severity=EventSeverity.ERROR,
             message=error_message,
             data={"error": error_message}
         )

    async def close_clients(self):
        """Close any open HTTP clients."""
        if self.http_client and not self.http_client.is_closed:
            await self.http_client.aclose()
            logger.info(f"[{self.agent_id}] Closed httpx client.")


# --- FastAPI Server Setup ---

app = FastAPI(title="OrchestratorAgent A2A Server")

# Instantiate the agent (reads env vars internally)
# SocketIO instance needs to be created and passed if used.
# For a simple A2A server, SocketIO might be handled elsewhere or not used by the agent itself.
# Let's create a dummy SocketIO instance if the library is available but not provided.
# In a real Flask-SocketIO app, the instance would be created and passed.
orchestrator_socketio_instance = None
if SOCKETIO_AVAILABLE:
    # Assuming SocketIO is initialized elsewhere and imported or passed.
    # For this standalone server, we might not have a Flask app/SocketIO server running here.
    # If the plan requires SocketIO updates *from this FastAPI server*, it's complex.
    # Let's assume for now that the SocketIO emission logic is just a placeholder
    # or requires a separate SocketIO server process that this agent connects to.
    # Or, the backend API (the A2A client) also runs a SocketIO server that the frontend connects to.
    # Let's remove the SocketIO parameter from __init__ and the class member,
    # and log a warning if emission is attempted without a configured SocketIO client.
    # This simplifies the agent's initialization for the A2A server context.

    # Reverting: The original code *does* pass SocketIO to __init__.
    # This implies the SocketIO server is running alongside or accessible.
    # Let's keep the parameter but make it optional and log if missing.
    # The FastAPI server itself doesn't host SocketIO directly.
    # This suggests a hybrid setup where FastAPI is for A2A invocation,
    # and SocketIO is for separate real-time updates.

    # Let's create a dummy SocketIO instance if needed for the agent init,
    # but note that emission will only work if a real SocketIO server is running
    # and this agent instance is somehow connected to it. This is complex.

    # Simplest approach: Keep the SocketIO parameter in __init__, but the FastAPI
    # server doesn't manage it. The user/system running this agent as a service
    # is responsible for providing a connected SocketIO instance if real-time updates are needed.
    pass # Keep socketio parameter in __init__

try:
    # Pass None for socketio if it's not available or managed externally
    orchestrator_agent_instance = OrchestratorAgent(socketio=None) # Pass None for SocketIO in this A2A server context
except ValueError as e:
    logger.critical(f"Failed to initialize OrchestratorAgent: {e}. Server cannot start.", exc_info=True)
    import sys
    sys.exit(f"Agent Initialization Error: {e}")


@app.post("/invoke", response_model=OrchestratorOutput, responses={500: {"model": OrchestratorErrorOutput}})
async def invoke_agent(request: OrchestratorInput = Body(...)):
    """
    A2A endpoint to invoke the OrchestratorAgent.
    Expects JSON body matching OrchestratorInput.
    Returns OrchestratorOutput on success, or raises HTTPException on error.
    """
    logger.info(f"OrchestratorAgent /invoke called for session: {request.session_id}, prompt: {request.prompt}")
    # Generate a unique invocation ID for this task
    invocation_id = f"orchestrate-{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(1000,9999)}"

    # Create InvocationContext for the agent's run_async method
    # Pass the input data directly in context.data
    context_data = request.model_dump()
    # Add invocation_id to context data if the agent needs it there
    context_data["invocation_id"] = invocation_id

    context = InvocationContext(
        agent_id="orchestrator-agent", # Use the agent's ID
        invocation_id=invocation_id,
        session=InvocationContext.create_session(session_id=request.session_id), # Create session with provided ID
        data=context_data # Pass the input data
    )

    try:
        # Call the agent's run_async method
        result_event = await orchestrator_agent_instance.run_async(context)

        # Process the event returned by run_async
        if result_event and isinstance(result_event.data, dict):
            # Check metadata for status
            if result_event.metadata.get("status") == "error":
                 error_msg = result_event.data.get("error", "Unknown agent error")
                 error_details = result_event.data.get("details")
                 logger.error(f"OrchestratorAgent run_async returned error event: {error_msg}")
                 # Return error response matching OrchestratorErrorOutput
                 raise HTTPException(status_code=500, detail=OrchestratorErrorOutput(error=error_msg, details=error_details).model_dump(exclude_none=True))
            else:
                 # Assume success if status is not error
                 logger.info(f"OrchestratorAgent returning success result for task {invocation_id}.")
                 # Construct success response matching OrchestratorOutput
                 # The result might be in result_event.data or nested.
                 # Let's assume the final result is in result_event.data.results or similar,
                 # or the entire data payload is the result.
                 # Based on other agents, the success event data *is* the result payload.
                 # The orchestrator's success event data contains {"delegated_agent": ..., "result_payload": ...}
                 # or the LLM response text for 'self'.

                 # Let's simplify the OrchestratorOutput to reflect the final state and a message.
                 # The actual detailed result payload from the delegated agent or LLM
                 # should be included in the 'result' field.

                 final_status = result_event.metadata.get("status", "completed") # Default to completed
                 message = result_event.message or f"Task {final_status}."
                 final_result_payload = result_event.data # Pass the entire data payload as the result

                 # If it was a delegation event, maybe extract the nested result_payload?
                 # This adds complexity. Let's just return the event's data payload as the result for now.

                 output_payload = OrchestratorOutput(
                     status=final_status,
                     message=message,
                     result=final_result_payload, # The data payload from the final event
                     agent=result_event.data.get("delegated_agent", "self"), # Infer agent from data or default
                     task_id=invocation_id
                 )
                 return output_payload

        else:
            logger.error(f"OrchestratorAgent run_async returned None or invalid event data: {result_event}")
            raise HTTPException(status_code=500, detail=OrchestratorErrorOutput(error="Agent execution failed to return a valid event.").model_dump())

    except HTTPException as http_exc:
        raise http_exc # Re-raise FastAPI exceptions
    except Exception as e:
        logger.error(f"Error during agent invocation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=OrchestratorErrorOutput(error=f"Internal server error: {e}").model_dump())

@app.get("/health")
async def health_check():
    # Add checks for LLM client and agent URLs if needed
    status = "ok"
    if not orchestrator_agent_instance.model:
        status = "warning: LLM client not initialized (check GOOGLE_API_KEY)"
    missing_urls = [key for key, url in orchestrator_agent_instance.agent_urls.items() if not url]
    if missing_urls:
        status = f"warning: Missing agent URLs: {', '.join(missing_urls)}"
    return {"status": status}

# --- Server Shutdown Hook ---
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down OrchestratorAgent server...")
    await orchestrator_agent_instance.close_clients() # Close httpx client

# --- Main execution block ---

if __name__ == "__main__":
    # Load .env for local development if needed
    try:
        from dotenv import load_dotenv
        if load_dotenv(): logger.info("Loaded .env file for local run.")
        else: logger.info("No .env file found or it was empty.")
    except ImportError: logger.info("dotenv library not found, skipping .env load.")

    parser = argparse.ArgumentParser(description="Run the OrchestratorAgent A2A server.")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind the server to.")
    parser.add_argument("--port", type=int, default=8091, help="Port to run the server on.") # Default matches compose
    args = parser.parse_args()

    # Optional: Check for critical env vars before starting server
    # if not os.environ.get(OrchestratorAgent.ENV_GOOGLE_API_KEY):
    #      print(f"WARNING: Environment variable {OrchestratorAgent.ENV_GOOGLE_API_KEY} not set. LLM classification disabled.")
    # if not os.environ.get(OrchestratorAgent.ENV_CONTENT_GENERATION_AGENT_URL):
    #      print(f"WARNING: Environment variable {OrchestratorAgent.ENV_CONTENT_GENERATION_AGENT_URL} not set. Content generation delegation disabled.")

    print(f"Starting OrchestratorAgent A2A server on {args.host}:{args.port}")

    # Note: SocketIO is not managed by this FastAPI server process.
    # If real-time updates are needed, a separate SocketIO server must be running,
    # and this agent instance must be configured to connect to it.
    # The current implementation passes socketio=None, disabling real-time updates from this process.

    uvicorn.run(app, host=args.host, port=args.port)
