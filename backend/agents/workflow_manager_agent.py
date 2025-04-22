import json
import time
import random
import httpx
import asyncio # Already imported
import uuid
from enum import Enum
from typing import Dict, Any, Optional, Union
import logging # Import logging

from app.config import settings # Import centralized settings

# Firestore client
from google.cloud import firestore
from google.cloud.firestore_v1.async_client import AsyncClient as FirestoreAsyncClient

# Import SocketIO type hint if needed (optional but good practice)
try:
    from flask_socketio import SocketIO
except ImportError:
    SocketIO = Any # Fallback if flask_socketio is not installed here

from pydantic import BaseModel, Field, HttpUrl, ValidationError

from google.adk.agents import Agent
from google.adk.runtime import InvocationContext
from google.adk.runtime.event import Event, EventType

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Data Models (Input/Output Schemas) ---
# These should ideally match the actual schemas defined in the respective agent files.
# Simplified versions are kept here for clarity and potential fallback.
# NOTE: These models are used for structuring data internally within the workflow manager,
#       but the actual A2A calls will send/receive data compatible with the target agent's
#       expected input/output Event schemas.
# These should ideally match the actual schemas defined in the respective agent files.
# Simplified versions are kept here for clarity and potential fallback.

class MarketResearchInput(BaseModel):
    initial_topic: str
    target_url: Optional[HttpUrl] = None
    num_competitors: int = 3

class MarketOpportunityReport(BaseModel):
    competitors: list = []
    analysis: dict = {}
    feature_recommendations: list = []
    target_audience_suggestions: list = []
    # Adding fields potentially used by ImprovementAgent based on old code
    competitor_weaknesses: list = Field(default_factory=list)
    market_gaps: list = Field(default_factory=list)

    status: str = "completed" # Added for failure check
    error_message: Optional[str] = None # Added for failure check

class ImprovementAgentInput(BaseModel):
    product_concept: str
    competitor_weaknesses: list = []
    market_gaps: list = []
    target_audience_suggestions: list = []
    feature_recommendations_from_market: list = []
    business_model_type: Optional[str] = None

class ImprovedProductSpec(BaseModel):
    product_concept: str
    target_audience: list = []
    key_features: list = []
    unique_selling_propositions: list = [] # Renamed from identified_improvements for clarity
    implementation_difficulty_estimate: Optional[int] = None
    potential_revenue_impact_estimate: Optional[str] = None

    potential_rating: Optional[str] = None # Existing field used for feasibility
    feasibility_score: Optional[float] = None # Existing field used for feasibility
    assessment_rationale: Optional[str] = None # Existing field used for feasibility
    status: str = "completed" # Added for failure check
    error_message: Optional[str] = None # Added for failure check

class BrandingAgentInput(BaseModel):
    product_concept: str
    target_audience: list = []
    keywords: Optional[list] = None
    business_model_type: Optional[str] = None

class BrandPackage(BaseModel):
    brand_name: str
    tagline: str
    color_scheme: dict = {}
    positioning_statement: str
    key_messages: list = []
    voice_tone: list = []
    alternative_names: list = []
    target_demographics: list = [] # Assuming this aligns with target_audience

    status: str = "completed" # Added for failure check
    error_message: Optional[str] = None # Added for failure check

class DeploymentAgentInput(BaseModel):
    brand_name: str
    product_concept: str
    key_features: list = []
    # Add field to accept generated code structure
    generated_code_dict: Optional[Dict[str, str]] = None # e.g., {"app.py": "...", "requirements.txt": "..."}

class DeploymentResult(BaseModel):
    deployment_url: Optional[str] = None # Make optional as it might fail before URL generation
    status: str # e.g., "ACTIVE", "FAILED"
    brand_name: Optional[str] = None # Make optional
    features_deployed: list = []
    monitoring_url: Optional[str] = None
    deployment_details: dict = {}
    domains: list = []
    dns_settings: dict = {}
    error_message: Optional[str] = None # Added for failure check

# --- New Models for Code Generation ---
class CodeGenerationAgentInput(BaseModel):
    product_spec: ImprovedProductSpec # Pass the whole spec
    brand_package: BrandPackage # Pass the whole package

class CodeGenerationResult(BaseModel):
    generated_code_dict: Dict[str, str] = Field(..., description="Dictionary mapping filenames to code content")
    status: str = "completed" # Or "failed"

    error_message: Optional[str] = None # Added for failure check

# --- Marketing Agent Models ---
class MarketingAgentInput(BaseModel):
   product_spec: ImprovedProductSpec
   brand_package: BrandPackage
   deployment_url: Optional[str] = None # From DeploymentResult

class MarketingMaterialsPackage(BaseModel):
   # Define fields based on MarketingAgent's expected output
   # Example fields:
   social_media_posts: Optional[Dict[str, list[str]]] = None # e.g., {"twitter": [...], "linkedin": [...]}
   blog_post_ideas: Optional[list[str]] = None
   email_campaign_snippets: Optional[list[str]] = None
   ad_copy_suggestions: Optional[list[str]] = None
   landing_page_copy: Optional[str] = None
   # ---
   status: str = "completed"
   error_message: Optional[str] = None


# --- Workflow State Tracking (Internal) ---
class WorkflowStatus(str, Enum):
    STARTING = "STARTING"
    RUNNING_MARKET_RESEARCH = "RUNNING_MARKET_RESEARCH"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED_RESUMING = "APPROVED_RESUMING"
    RUNNING_IMPROVEMENT = "RUNNING_IMPROVEMENT"
    COMPLETED_IMPROVEMENT = "COMPLETED_IMPROVEMENT"
    STOPPED_LOW_POTENTIAL = "STOPPED_LOW_POTENTIAL"
    RUNNING_BRANDING = "RUNNING_BRANDING"
    COMPLETED_BRANDING = "COMPLETED_BRANDING"
    RUNNING_CODE_GENERATION = "RUNNING_CODE_GENERATION" # New
    COMPLETED_CODE_GENERATION = "COMPLETED_CODE_GENERATION" # New
    RUNNING_DEPLOYMENT = "RUNNING_DEPLOYMENT"
    COMPLETED_DEPLOYMENT = "COMPLETED_DEPLOYMENT" # Added intermediate state
    RUNNING_MARKETING = "RUNNING_MARKETING" # New Marketing state
    COMPLETED_MARKETING = "COMPLETED_MARKETING" # New Marketing state
    COMPLETED = "COMPLETED" # Final state after marketing
    FAILED = "FAILED"

class WorkflowStep(str, Enum):
    MARKET_RESEARCH = "MARKET_RESEARCH"
    IMPROVEMENT = "IMPROVEMENT"
    BRANDING = "BRANDING"
    CODE_GENERATION = "CODE_GENERATION" # New
    DEPLOYMENT = "DEPLOYMENT"
    MARKETING = "MARKETING" # New Marketing step

# --- Workflow Manager Agent ---

class WorkflowManagerAgent(Agent):
    """
    Orchestrates the 4-step autonomous income generation workflow using ADK.
    Manages state and asynchronous communication between specialized agents via REST APIs.
    Includes retry logic for A2A calls.
    """

    def __init__(
        self,
        socketio: SocketIO,
        firestore_db: Optional[FirestoreAsyncClient], # Accept Firestore client
        collection_name: str, # Firestore collection name
        market_research_agent_id: Optional[str],
        improvement_agent_id: Optional[str],
        branding_agent_id: Optional[str],
        code_generation_agent_id: Optional[str], # Added
        deployment_agent_id: Optional[str],
        marketing_agent_id: Optional[str], # Added Marketing Agent ID
        # timeout_seconds parameter removed, will use settings directly
    ):
        super().__init__(agent_id="workflow_manager_agent")
        self.socketio = socketio
        self.db = firestore_db
        self.collection_name = collection_name
        self.market_research_agent_id = market_research_agent_id
        self.improvement_agent_id = improvement_agent_id
        self.branding_agent_id = branding_agent_id
        self.code_generation_agent_id = code_generation_agent_id # Added
        self.deployment_agent_id = deployment_agent_id
        self.marketing_agent_id = marketing_agent_id # Added Marketing Agent ID
        self.timeout_seconds = settings.AGENT_TIMEOUT_SECONDS # Use settings
        self.max_retries = settings.A2A_MAX_RETRIES # Use settings
        self.retry_delay = settings.A2A_RETRY_DELAY_SECONDS # Use settings

        if not self.db:
            logger.warning("WorkflowManagerAgent initialized without a valid Firestore client. State persistence will fail.")
        else:
             logger.info(f"WorkflowManagerAgent initialized with Firestore collection: {self.collection_name}")

        # Async HTTP client for A2A calls
        self._http_client = httpx.AsyncClient(timeout=self.timeout_seconds)

    async def close(self):
        """Clean up resources, like the HTTP client."""
        await self._http_client.aclose()
        logger.info("WorkflowManagerAgent closed.")

    async def _invoke_adk_skill(
        self,
        context: InvocationContext, # Pass the context
        agent_name: str, # For logging
        target_agent_id: Optional[str],
        skill_name: str,
        payload: Dict[str, Any],
    ) -> Event:
        """
        Helper function to invoke another agent's skill asynchronously using ADK
        with retry logic.

        Args:
            context: The current InvocationContext.
            agent_name: User-friendly name of the agent (for logging).
            target_agent_id: The ID of the agent to invoke.
            skill_name: The name of the skill to invoke on the target agent.
            payload: The data dictionary for the input event.

        Returns:
            An Event object representing the result or error from the agent skill.
        """
        invocation_id = context.invocation_id # Get invocation ID from context

        if not target_agent_id:
            error_msg = f"Agent ID for '{agent_name}' is not configured."
            logger.error(f"[{invocation_id}] Error: {error_msg}")
            return Event(type=EventType.ERROR, data={"error": error_msg})

        input_event = Event(type=EventType.INPUT, data=payload)
        last_exception: Optional[Exception] = None

        logger.info(f"[{invocation_id}] Invoking {agent_name} skill '{skill_name}' on agent '{target_agent_id}' (Retries: {self.max_retries}, Delay: {self.retry_delay}s)...")

        for attempt in range(self.max_retries):
            try:
                # Use context.invoke_skill for ADK A2A communication
                result_event = await context.invoke_skill(
                    target_agent_id=target_agent_id,
                    skill_name=skill_name,
                    input=input_event,
                    timeout_seconds=self.timeout_seconds # Use configured timeout
                )

                # Check if the result is a valid Event (basic check)
                if not isinstance(result_event, Event) or not hasattr(result_event, 'type') or not hasattr(result_event, 'data'):
                     # This case might indicate an ADK internal issue or unexpected return type
                     raise TypeError(f"Invalid response type received from {agent_name} skill '{skill_name}'. Expected Event, got {type(result_event)}.")

                # Log success (even if the event type is ERROR, the call itself succeeded)
                logger.info(f"[{invocation_id}] Agent '{agent_name}' skill '{skill_name}' invocation successful (Attempt {attempt + 1}/{self.max_retries}). Result Event Type: {result_event.type}")
                return result_event # Return the received event (could be RESULT or ERROR)

            except TimeoutError as e: # Catch specific timeout error if ADK raises it
                last_exception = e
                logger.warning(f"[{invocation_id}] Skill invocation for {agent_name} timed out (Attempt {attempt + 1}/{self.max_retries}).")
                # Fall through to retry logic

            except ConnectionError as e: # Catch connection errors if ADK raises them
                 last_exception = e
                 logger.warning(f"[{invocation_id}] Skill invocation for {agent_name} failed (Attempt {attempt + 1}/{self.max_retries}): Connection Error ({type(e).__name__}).")
                 # Fall through to retry logic

            except Exception as e:
                 # Catch other potential errors during invoke_skill
                 last_exception = e
                 logger.error(f"[{invocation_id}] Unexpected error during {agent_name} skill '{skill_name}' invocation attempt {attempt + 1}/{self.max_retries}: {type(e).__name__}: {e}", exc_info=True)
                 # If it's the last attempt, let it be handled below. Otherwise, retry.
                 if attempt >= self.max_retries - 1:
                     break # Exit loop to handle final error

            # --- Retry Logic ---
            if attempt < self.max_retries - 1:
                wait_time = self.retry_delay * (2 ** attempt) # Exponential backoff
                logger.info(f"[{invocation_id}] Retrying in {wait_time:.2f}s...")
                await asyncio.sleep(wait_time)
            else:
                logger.error(f"[{invocation_id}] Skill invocation for {agent_name} failed after {self.max_retries} attempts.")
                break # Exit loop after last attempt

        # --- Handle Failure After Retries ---
        error_msg = f"Skill invocation for {agent_name} ('{skill_name}') failed after {self.max_retries} attempts."
        error_details = "Max retries exceeded"
        if last_exception:
            error_msg += f" Last error: {type(last_exception).__name__}: {last_exception}"
            if isinstance(last_exception, TimeoutError):
                error_details = "Timeout"
            elif isinstance(last_exception, ConnectionError):
                error_details = "Connection Error"
            else:
                 error_details = f"{type(last_exception).__name__}"

        logger.error(f"[{invocation_id}] Final Error: {error_msg}")
        return Event(type=EventType.ERROR, data={"error": error_msg, "details": error_details})

    async def _invoke_a2a_agent(
        self,
        agent_name: str,
        agent_url: Optional[str],
        endpoint_suffix: str,
        invocation_id: str,
        payload: Dict[str, Any],
    ) -> Event:
        """
        Helper function to invoke another agent's A2A endpoint asynchronously with retry logic.

        Args:
            agent_name: User-friendly name of the agent (for logging).
            agent_url: The specific agent URL.
            endpoint_suffix: The specific part for the A2A route (e.g., 'market_research').
            invocation_id: The current workflow invocation ID (for logging).
            payload: The data dictionary to send as the JSON body.

        Returns:
            An Event object representing the result or error from the agent.
        """
        if not agent_url:
            error_msg = f"URL for agent '{agent_name}' is not configured."
            logger.error(f"[{invocation_id}] Error: {error_msg}")
            return Event(type=EventType.ERROR, data={"error": error_msg})

        endpoint_url = f"{agent_url.rstrip('/')}/a2a/{endpoint_suffix}/invoke"
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        last_exception: Optional[Exception] = None

        logger.info(f"[{invocation_id}] Invoking {agent_name} A2A endpoint at {endpoint_url} (Retries: {self.max_retries}, Delay: {self.retry_delay}s)...")

        for attempt in range(self.max_retries):
            try:
                response = await self._http_client.post(
                    endpoint_url,
                    json=payload,
                    headers=headers,
                    timeout=self.timeout_seconds
                )
                response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)

                # --- Success Case ---
                try:
                    event_data = response.json()
                    result_event = Event(**event_data)
                    if not hasattr(result_event, 'type') or not hasattr(result_event, 'data'):
                         raise ValidationError("Response is not a valid Event structure.")

                    logger.info(f"[{invocation_id}] Agent '{agent_name}' A2A call successful (Attempt {attempt + 1}/{self.max_retries}). Event Type: {result_event.type}")
                    return result_event # Success, return immediately

                except (json.JSONDecodeError, ValidationError, TypeError) as e:
                    # Handle issues with response format *after* successful HTTP call
                    error_msg = f"Failed to process or validate successful A2A response from {agent_name}: {e}"
                    logger.error(f"[{invocation_id}] Error: {error_msg}")
                    # Don't retry format errors, return error event immediately
                    return Event(type=EventType.ERROR, data={"error": error_msg, "details": "Invalid Response Format"})

            except (httpx.TimeoutException, httpx.ConnectError) as e:
                last_exception = e
                logger.warning(f"[{invocation_id}] A2A call to {agent_name} failed (Attempt {attempt + 1}/{self.max_retries}): Timeout or Connection Error ({type(e).__name__}).")
                # Fall through to retry logic

            except httpx.HTTPStatusError as e:
                last_exception = e
                # Retry only on 5xx server errors
                if e.response.status_code >= 500:
                    logger.warning(f"[{invocation_id}] A2A call to {agent_name} failed (Attempt {attempt + 1}/{self.max_retries}): Server Error ({e.response.status_code}).")
                    # Fall through to retry logic
                else:
                    # Non-5xx HTTP error (e.g., 4xx), likely not transient. Don't retry.
                    error_detail = str(e)
                    try:
                        error_detail += f" | Status: {e.response.status_code} | Response: {e.response.text[:500]}"
                    except Exception: pass
                    error_msg = f"HTTP error calling {agent_name} A2A endpoint (non-retryable): {error_detail}"
                    logger.error(f"[{invocation_id}] Error: {error_msg}")
                    return Event(type=EventType.ERROR, data={"error": error_msg, "details": f"HTTP Error {e.response.status_code}"})

            except httpx.RequestError as e:
                # Catch other potential request errors (less common)
                last_exception = e
                logger.warning(f"[{invocation_id}] A2A call to {agent_name} failed (Attempt {attempt + 1}/{self.max_retries}): Request Error ({type(e).__name__}: {e}).")
                # Fall through to retry logic

            except Exception as e:
                 # Catch unexpected errors during the call itself (not response processing)
                 last_exception = e
                 logger.error(f"[{invocation_id}] Unexpected error during {agent_name} A2A call attempt {attempt + 1}/{self.max_retries}: {type(e).__name__}: {e}", exc_info=True)
                 # If it's the last attempt, let it be handled below. Otherwise, retry.
                 if attempt >= self.max_retries - 1:
                     break # Exit loop to handle final error

            # --- Retry Logic ---
            if attempt < self.max_retries - 1:
                logger.info(f"[{invocation_id}] Retrying in {self.retry_delay}s...")
                await asyncio.sleep(self.retry_delay)
            else:
                logger.error(f"[{invocation_id}] A2A call to {agent_name} failed after {self.max_retries} attempts.")
                break # Exit loop after last attempt

        # --- Handle Failure After Retries ---
        # If the loop finished without returning a success event
        error_msg = f"A2A call to {agent_name} failed after {self.max_retries} attempts."
        error_details = "Max retries exceeded"
        if last_exception:
            error_msg += f" Last error: {type(last_exception).__name__}: {last_exception}"
            if isinstance(last_exception, httpx.TimeoutException):
                error_details = "Timeout"
            elif isinstance(last_exception, httpx.ConnectError):
                error_details = "Connection Error"
            elif isinstance(last_exception, httpx.HTTPStatusError):
                 error_details = f"HTTP Error {last_exception.response.status_code}"
            else:
                 error_details = f"{type(last_exception).__name__}"

        logger.error(f"[{invocation_id}] Final Error: {error_msg}")
        return Event(type=EventType.ERROR, data={"error": error_msg, "details": error_details})


    async def _update_workflow_state(self, workflow_run_id: str, state_data: Dict[str, Any]):
        """Helper to update workflow state in Firestore."""
        if not self.db:
            logger.error(f"[{workflow_run_id}] Error: Firestore client not available. Cannot update state.")
            return

        try:
            # Add timestamp for tracking
            state_data['last_updated'] = firestore.SERVER_TIMESTAMP
            doc_ref = self.db.collection(self.collection_name).document(workflow_run_id)
            await doc_ref.set(state_data, merge=True)
            logger.info(f"[{workflow_run_id}] Firestore state updated: Status={state_data.get('status')}, Step={state_data.get('current_step')}")
        except Exception as e:
            logger.error(f"[{workflow_run_id}] Error updating Firestore state: {type(e).__name__}: {e}", exc_info=True)
            # Decide if this error should propagate or just be logged


    async def _handle_step_failure(self, workflow_run_id: str, current_step: WorkflowStep, error_details: str, agent_name: str) -> Event:
        """Handles Firestore update, SocketIO emit, and returns final error event for a failed step."""
        logger.error(f"[{workflow_run_id}] Step {current_step.value} failed. Agent: {agent_name}. Reason: {error_details}")
        current_status = WorkflowStatus.FAILED
        await self._update_workflow_state(workflow_run_id, {
            "status": current_status.value,
            "current_step": current_step.value,
            "error_message": error_details
        })
        self.socketio.emit('workflow_failed', {'workflow_run_id': workflow_run_id, 'failed_step': current_step.value, 'error': error_details})
        return Event(type=EventType.ERROR, data={"error": error_details, "stage": current_step.value, "workflow_run_id": workflow_run_id})

    async def run_async(self, context: InvocationContext) -> Event:
        """
        ADK entry point to orchestrate the 4-step workflow asynchronously using Firestore for state.
        This method handles both initial invocation and resumption based on Firestore state.
        """
        invocation_id = context.invocation_id # ADK's invocation ID
        input_data = context.input.data or {}

        # Determine if starting new or potentially resuming
        workflow_run_id = input_data.get("workflow_run_id")
        is_new_workflow = not workflow_run_id

        # --- State Variables ---
        current_status: Optional[WorkflowStatus] = None # Will be loaded or set
        current_step: Optional[WorkflowStep] = None
        error_message: Optional[str] = None
        initial_topic: Optional[str] = None
        target_url: Optional[str] = None
        market_report_data: Optional[Dict] = None
        product_spec_data: Optional[Dict] = None
        brand_package_data: Optional[Dict] = None
        code_generation_result_data: Optional[Dict] = None # Added
        deployment_result_data: Optional[Dict] = None
        marketing_result_data: Optional[Dict] = None # Added Marketing result
        state: Dict[str, Any] = {} # To hold the loaded Firestore state

        # --- Firestore Check ---
        if not self.db:
             logger.critical(f"[{workflow_run_id or 'NEW'}] FATAL ERROR: Firestore client is not initialized. Aborting workflow.")
             return Event(type=EventType.ERROR, data={
                 "error": "Firestore client not available. Workflow cannot proceed or record state.",
                 "workflow_run_id": workflow_run_id or "N/A",
                 "stage": None
             })

        try:
            # --- Initialize or Load State ---
            if is_new_workflow:
                workflow_run_id = uuid.uuid4().hex
                logger.info(f"[{invocation_id}/{workflow_run_id}] New workflow run started.")
                initial_topic = input_data.get("initial_topic")
                target_url = input_data.get("target_url") # Optional
                if not initial_topic or not isinstance(initial_topic, str):
                    raise ValueError("Missing or invalid 'initial_topic' for new workflow.")
                logger.info(f"[{workflow_run_id}] Initial Topic: {initial_topic}, Target URL: {target_url}")

                # Initial state write
                current_status = WorkflowStatus.STARTING
                current_step = None # Explicitly null at start
                state = {
                    "status": current_status.value,
                    "initial_topic": initial_topic,
                    "target_url": target_url,
                    "invocation_id": invocation_id,
                    "current_step": None,
                }
                await self._update_workflow_state(workflow_run_id, state)
            else:
                # Load existing state from Firestore
                logger.info(f"[{invocation_id}/{workflow_run_id}] Attempting to load existing workflow run.")
                doc_ref = self.db.collection(self.collection_name).document(workflow_run_id)
                doc_snapshot = await doc_ref.get()
                if not doc_snapshot.exists:
                    raise ValueError(f"Workflow run ID '{workflow_run_id}' not found in Firestore.")

                state = doc_snapshot.to_dict()
                initial_topic = state.get("initial_topic")
                target_url = state.get("target_url")
                market_report_data = state.get("market_research_result")
                product_spec_data = state.get("improvement_result")
                brand_package_data = state.get("branding_result")
                code_generation_result_data = state.get("code_generation_result") # Added
                deployment_result_data = state.get("deployment_result") # Load deployment result too
                marketing_result_data = state.get("marketing_result") # Load marketing result
                current_status = WorkflowStatus(state.get("status", WorkflowStatus.FAILED.value)) # Default to FAILED if missing
                current_step = WorkflowStep(state["current_step"]) if state.get("current_step") else None

                logger.info(f"[{workflow_run_id}] State loaded from Firestore. Status: {current_status.value}, Last Step: {current_step.value if current_step else 'None'}")

                # Handle the case where the frontend signals approval
                # The frontend might trigger a resume call after user clicks 'approve'
                # We transition from PENDING_APPROVAL to APPROVED_RESUMING here
                if current_status == WorkflowStatus.PENDING_APPROVAL:
                    logger.info(f"[{workflow_run_id}] Workflow was pending approval. Transitioning to APPROVED_RESUMING.")
                    current_status = WorkflowStatus.APPROVED_RESUMING
                    await self._update_workflow_state(workflow_run_id, {"status": current_status.value})
                    # State is now updated, the logic below will pick up from here

                # Validation: Ensure necessary data exists for the expected next step
                if current_status == WorkflowStatus.APPROVED_RESUMING and not market_report_data:
                    raise ValueError("Cannot resume from improvement: Market research result missing in Firestore.")
                if current_status == WorkflowStatus.COMPLETED_IMPROVEMENT and not product_spec_data:
                     raise ValueError("Cannot resume from branding: Improvement result missing in Firestore.")
                if current_status == WorkflowStatus.COMPLETED_BRANDING and (not product_spec_data or not brand_package_data):
                     raise ValueError("Cannot resume from code generation: Improvement or Branding result missing in Firestore.")
                if current_status == WorkflowStatus.COMPLETED_CODE_GENERATION and (not brand_package_data or not code_generation_result_data): # Added check
                     raise ValueError("Cannot resume from deployment: Branding or Code Generation result missing in Firestore.")
                if current_status == WorkflowStatus.COMPLETED_DEPLOYMENT and (not product_spec_data or not brand_package_data or not deployment_result_data): # Added check
                     raise ValueError("Cannot resume from marketing: Product Spec, Branding, or Deployment result missing in Firestore.")
                if not initial_topic: # Should always exist if state was loaded
                     raise ValueError("Cannot resume: Initial topic missing in Firestore state.")


            # --- Workflow Execution Logic ---
            # Determine which steps need to run based on the current status

            # Step 1: Market Research
            if current_status == WorkflowStatus.STARTING:
                current_step = WorkflowStep.MARKET_RESEARCH
                logger.info(f"\n[{workflow_run_id}] --- Running Step: {current_step.value} ---")
                current_status = WorkflowStatus.RUNNING_MARKET_RESEARCH # Set specific running status
                await self._update_workflow_state(workflow_run_id, {"status": current_status.value, "current_step": current_step.value})

                market_research_payload = MarketResearchInput(
                    initial_topic=initial_topic,
                    target_url=target_url
                ).model_dump(exclude_none=True)

                market_event = await self._invoke_adk_skill(
                    context=context,
                    agent_name="Market Research", target_agent_id=self.market_research_agent_id,
                    skill_name="market_research",
                    payload=market_research_payload,
                )

                if market_event.type == EventType.ERROR:
                    # A2A call itself failed (handled by _invoke_a2a_agent returning ERROR event)
                    error_details = market_event.data.get('error', 'Market Research A2A call failed')
                    return await self._handle_step_failure(workflow_run_id, current_step, error_details, "Market Research")
                if not market_event.data: raise RuntimeError("Market Research Agent returned no data.")

                try:
                    market_report = MarketOpportunityReport(**market_event.data)
                    market_report_data = market_report.model_dump()
                    # Check if the agent reported failure *within* the successful event
                    if market_report.status.lower() == 'failed':
                        error_details = market_report.error_message or "Market Research Agent reported failure without details."
                        return await self._handle_step_failure(workflow_run_id, current_step, error_details, "Market Research")
                except ValidationError as ve:
                    error_details = f"Market Research Agent response validation failed: {ve}"
                    return await self._handle_step_failure(workflow_run_id, current_step, error_details, "Market Research")

                logger.info(f"[{workflow_run_id}] --- Step {current_step.value} Complete ---")

                # --- Pause for Approval ---
                logger.info(f"[{workflow_run_id}] Pausing for user approval after Market Research.")
                try:
                    # Ensure data is serializable before saving and emitting
                    serializable_market_data = json.loads(json.dumps(market_report_data))
                except (TypeError, ValueError) as json_err:
                    raise RuntimeError(f"Market research result could not be serialized: {json_err}")

                current_status = WorkflowStatus.PENDING_APPROVAL
                await self._update_workflow_state(workflow_run_id, {
                    "status": current_status.value,
                    "current_step": current_step.value, # Keep track of the last completed step
                    "market_research_result": serializable_market_data
                })

                logger.info(f"[{workflow_run_id}] Emitting 'workflow_approval_required' via SocketIO.")
                self.socketio.emit('workflow_approval_required', {
                    'workflow_run_id': workflow_run_id,
                    'data_to_approve': serializable_market_data
                })

                # End execution here; resumption happens in a new invocation triggered by approval
                return Event(type=EventType.RESULT, data={
                    "status": current_status.value,
                    "workflow_run_id": workflow_run_id,
                    "message": "Workflow paused for approval after market research."
                })

            # Step 2: Product Improvement
            # Run if status is APPROVED_RESUMING (meaning market research is done and approved)
            if current_status == WorkflowStatus.APPROVED_RESUMING:
                current_step = WorkflowStep.IMPROVEMENT
                logger.info(f"\n[{workflow_run_id}] --- Running Step: {current_step.value} ---")
                current_status = WorkflowStatus.RUNNING_IMPROVEMENT # Set specific running status
                await self._update_workflow_state(workflow_run_id, {"status": current_status.value, "current_step": current_step.value})

                if not market_report_data: raise ValueError("Market research data missing for improvement step.") # Should be loaded

                improvement_payload = ImprovementAgentInput(
                    product_concept=initial_topic,
                    competitor_weaknesses=market_report_data.get('competitor_weaknesses', []),
                    market_gaps=market_report_data.get('market_gaps', []),
                    target_audience_suggestions=market_report_data.get('target_audience_suggestions', []),
                    feature_recommendations_from_market=market_report_data.get('feature_recommendations', []),
                    business_model_type="saas" # Placeholder
                ).model_dump(exclude_none=True)

                improvement_event = await self._invoke_adk_skill(
                    context=context,
                    agent_name="Improvement", target_agent_id=self.improvement_agent_id,
                    skill_name="improvement",
                    payload=improvement_payload,
                )

                if improvement_event.type == EventType.ERROR:
                    error_details = improvement_event.data.get('error', 'Improvement A2A call failed')
                    return await self._handle_step_failure(workflow_run_id, current_step, error_details, "Improvement")
                if not improvement_event.data: raise RuntimeError("Improvement Agent returned no data.")

                try:
                    product_spec = ImprovedProductSpec(**improvement_event.data)
                    product_spec_data = product_spec.model_dump()
                    # Check if the agent reported failure *within* the successful event
                    if product_spec.status.lower() == 'failed':
                        error_details = product_spec.error_message or "Improvement Agent reported failure without details."
                        return await self._handle_step_failure(workflow_run_id, current_step, error_details, "Improvement")
                except ValidationError as ve:
                    error_details = f"Improvement Agent response validation failed: {ve}"
                    return await self._handle_step_failure(workflow_run_id, current_step, error_details, "Improvement")

                logger.info(f"[{workflow_run_id}] --- Step {current_step.value} Complete ---")
                current_status = WorkflowStatus.COMPLETED_IMPROVEMENT # Set completed status
                await self._update_workflow_state(workflow_run_id, {
                    "status": current_status.value,
                    "current_step": current_step.value,
                    "improvement_result": product_spec_data # Save the result
                })

                # --- Feasibility Check ---
                logger.info(f"[{workflow_run_id}] Performing feasibility check based on Improvement result.")
                potential_rating = product_spec_data.get('potential_rating', 'Low').capitalize() # Default to Low if missing
                feasibility_score = product_spec_data.get('feasibility_score') # Optional score
                assessment_rationale = product_spec_data.get('assessment_rationale', 'Assessment rationale not provided.')

                # Define threshold (e.g., Medium or High potential, or score >= 0.6)
                proceed_to_branding = False
                if potential_rating in ['Medium', 'High']:
                    proceed_to_branding = True
                    logger.info(f"[{workflow_run_id}] Feasibility check passed (Potential: {potential_rating}). Proceeding to Branding.")
                elif feasibility_score is not None:
                    try:
                        if float(feasibility_score) >= 0.6:
                             proceed_to_branding = True
                             logger.info(f"[{workflow_run_id}] Feasibility check passed (Score: {feasibility_score} >= 0.6). Proceeding to Branding.")
                        else:
                             logger.warning(f"[{workflow_run_id}] Feasibility check failed (Score: {feasibility_score} < 0.6). Stopping workflow.")
                    except (ValueError, TypeError):
                         logger.warning(f"[{workflow_run_id}] Invalid feasibility_score format ('{feasibility_score}'). Treating as low potential.")
                         # proceed_to_branding remains False
                else:
                    logger.warning(f"[{workflow_run_id}] Feasibility check failed (Potential: {potential_rating}). Stopping workflow.")


                if not proceed_to_branding:
                    # Stop the workflow due to low potential
                    current_status = WorkflowStatus.STOPPED_LOW_POTENTIAL
                    stop_message = f"Workflow stopped: Potential rated '{potential_rating}'"
                    if feasibility_score is not None:
                        stop_message += f" (Score: {feasibility_score})"
                    stop_message += "."

                    logger.warning(f"[{workflow_run_id}] {stop_message} Rationale: {assessment_rationale}")

                    await self._update_workflow_state(workflow_run_id, {
                        "status": current_status.value,
                        "current_step": current_step.value, # Still IMPROVEMENT step technically
                        "error": stop_message # Use error field for stop reason
                    })

                    # Emit SocketIO update
                    self.socketio.emit('task_update', {
                        'workflow_run_id': workflow_run_id,
                        'status': current_status.value,
                        'message': stop_message,
                        'rationale': assessment_rationale,
                        'step': current_step.value
                    })

                    # Return a final event indicating controlled stop
                    return Event(type=EventType.RESULT, data={
                        "status": current_status.value,
                        "workflow_run_id": workflow_run_id,
                        "message": stop_message,
                        "rationale": assessment_rationale
                    })
                # --- End Feasibility Check ---

                # Fall through to Branding ONLY IF feasibility check passed

            # Step 3: Rebranding
            # Run if status is COMPLETED_IMPROVEMENT (meaning improvement step finished successfully AND passed feasibility)
            if current_status == WorkflowStatus.COMPLETED_IMPROVEMENT:
                current_step = WorkflowStep.BRANDING
                logger.info(f"\n[{workflow_run_id}] --- Running Step: {current_step.value} ---")
                current_status = WorkflowStatus.RUNNING_BRANDING # Set specific running status
                await self._update_workflow_state(workflow_run_id, {"status": current_status.value, "current_step": current_step.value})

                if not product_spec_data: raise ValueError("Product spec data missing for branding step.") # Should be loaded or just generated

                keywords = product_spec_data.get('product_concept', '').lower().split()[:5]
                branding_payload = BrandingAgentInput(
                    product_concept=product_spec_data.get('product_concept', initial_topic),
                    target_audience=product_spec_data.get('target_audience', []),
                    keywords=keywords,
                    business_model_type="saas" # Placeholder
                ).model_dump(exclude_none=True)

                branding_event = await self._invoke_adk_skill(
                    context=context,
                    agent_name="Branding", target_agent_id=self.branding_agent_id,
                    skill_name="branding",
                    payload=branding_payload,
                )

                if branding_event.type == EventType.ERROR:
                    error_details = branding_event.data.get('error', 'Branding A2A call failed')
                    return await self._handle_step_failure(workflow_run_id, current_step, error_details, "Branding")
                if not branding_event.data: raise RuntimeError("Branding Agent returned no data.")

                try:
                    brand_package = BrandPackage(**branding_event.data)
                    brand_package_data = brand_package.model_dump()
                    # Check if the agent reported failure *within* the successful event
                    if brand_package.status.lower() == 'failed':
                        error_details = brand_package.error_message or "Branding Agent reported failure without details."
                        return await self._handle_step_failure(workflow_run_id, current_step, error_details, "Branding")
                except ValidationError as ve:
                    error_details = f"Branding Agent response validation failed: {ve}"
                    return await self._handle_step_failure(workflow_run_id, current_step, error_details, "Branding")

                logger.info(f"[{workflow_run_id}] --- Step {current_step.value} Complete ---")
                current_status = WorkflowStatus.COMPLETED_BRANDING # Set completed status
                await self._update_workflow_state(workflow_run_id, {
                    "status": current_status.value,
                    "current_step": current_step.value,
                    "branding_result": brand_package_data # Save the result
                })
                # Fall through to Code Generation

            # Step 4: Code Generation
            # Run if status is COMPLETED_BRANDING
            if current_status == WorkflowStatus.COMPLETED_BRANDING:
                current_step = WorkflowStep.CODE_GENERATION
                logger.info(f"\n[{workflow_run_id}] --- Running Step: {current_step.value} ---")
                current_status = WorkflowStatus.RUNNING_CODE_GENERATION
                await self._update_workflow_state(workflow_run_id, {"status": current_status.value, "current_step": current_step.value})

                if not product_spec_data or not brand_package_data:
                    raise ValueError("Product spec or brand package data missing for code generation step.")

                # Re-validate/parse data into expected Pydantic models for the input
                try:
                    product_spec_model = ImprovedProductSpec(**product_spec_data)
                    brand_package_model = BrandPackage(**brand_package_data)
                except ValidationError as ve:
                    raise RuntimeError(f"Failed to validate data for Code Generation input: {ve}")

                code_gen_payload = CodeGenerationAgentInput(
                    product_spec=product_spec_model,
                    brand_package=brand_package_model
                ).model_dump(exclude_none=True)

                code_gen_event = await self._invoke_adk_skill(
                    context=context,
                    agent_name="Code Generation", target_agent_id=self.code_generation_agent_id,
                    skill_name="code_generation",
                    payload=code_gen_payload,
                )

                if code_gen_event.type == EventType.ERROR:
                    error_details = code_gen_event.data.get('error', 'Code Generation A2A call failed')
                    return await self._handle_step_failure(workflow_run_id, current_step, error_details, "Code Generation")
                if not code_gen_event.data: raise RuntimeError("Code Generation Agent returned no data.")

                try:
                    code_gen_result = CodeGenerationResult(**code_gen_event.data)
                    code_generation_result_data = code_gen_result.model_dump()
                    # Check if the agent reported failure *within* the successful event
                    if code_gen_result.status.lower() == 'failed':
                        error_details = code_gen_result.error_message or "Code Generation Agent reported failure without details."
                        return await self._handle_step_failure(workflow_run_id, current_step, error_details, "Code Generation")

                    if not code_generation_result_data.get('generated_code_dict'):
                         raise ValueError("Code Generation Agent response missing 'generated_code_dict'.")
                except (ValidationError, ValueError) as ve:
                    error_details = f"Code Generation Agent response validation failed or missing data: {ve}"
                    return await self._handle_step_failure(workflow_run_id, current_step, error_details, "Code Generation")

                logger.info(f"[{workflow_run_id}] --- Step {current_step.value} Complete ---")
                current_status = WorkflowStatus.COMPLETED_CODE_GENERATION
                await self._update_workflow_state(workflow_run_id, {
                    "status": current_status.value,
                    "current_step": current_step.value,
                    "code_generation_result": code_generation_result_data # Save the result
                })
                # Fall through to Deployment

            # Step 5: Deployment (was Step 4)
            # Run if status is COMPLETED_CODE_GENERATION
            if current_status == WorkflowStatus.COMPLETED_CODE_GENERATION:
                current_step = WorkflowStep.DEPLOYMENT
                logger.info(f"\n[{workflow_run_id}] --- Running Step: {current_step.value} ---")
                current_status = WorkflowStatus.RUNNING_DEPLOYMENT # Set specific running status
                await self._update_workflow_state(workflow_run_id, {"status": current_status.value, "current_step": current_step.value})

                # Need brand package for brand name, code generation result for the code
                if not brand_package_data or not code_generation_result_data:
                    raise ValueError("Brand package or code generation data missing for deployment step.")
                # Also need product spec for concept/features (load from state if not already loaded)
                if not product_spec_data:
                    product_spec_data = state.get("improvement_result")
                    if not product_spec_data:
                         raise ValueError("Product spec data missing for deployment step (failed to load from state).")


                deployment_payload = DeploymentAgentInput(
                    brand_name=brand_package_data.get('brand_name', 'Unnamed Brand'),
                    product_concept=product_spec_data.get('product_concept', initial_topic), # Use spec data
                    key_features=product_spec_data.get('key_features', []), # Use spec data
                    generated_code_dict=code_generation_result_data.get('generated_code_dict') # Pass the generated code
                ).model_dump(exclude_none=True)

                deployment_event = await self._invoke_adk_skill(
                    context=context,
                    agent_name="Deployment", target_agent_id=self.deployment_agent_id,
                    skill_name="deployment",
                    payload=deployment_payload,
                )

                if deployment_event.type == EventType.ERROR:
                    error_details = deployment_event.data.get('error', 'Deployment A2A call failed')
                    return await self._handle_step_failure(workflow_run_id, current_step, error_details, "Deployment")
                if not deployment_event.data: raise RuntimeError("Deployment Agent returned no data.")

                try:
                    deployment_result = DeploymentResult(**deployment_event.data)
                    deployment_result_data = deployment_result.model_dump()
                    # Check if the agent reported failure *within* the successful event
                    # Treat 'failed' or non-'active' status as failure
                    agent_reported_status = deployment_result.status.lower()
                    if agent_reported_status == 'failed' or agent_reported_status != 'active':
                        error_details = deployment_result.error_message or f"Deployment Agent reported status '{deployment_result.status}'."
                        return await self._handle_step_failure(workflow_run_id, current_step, error_details, "Deployment")

                except ValidationError as ve:
                    error_details = f"Deployment Agent response validation failed: {ve}"
                    return await self._handle_step_failure(workflow_run_id, current_step, error_details, "Deployment")

                logger.info(f"[{workflow_run_id}] --- Step {current_step.value} Complete ---")
                current_status = WorkflowStatus.COMPLETED_DEPLOYMENT # Set intermediate status
                await self._update_workflow_state(workflow_run_id, {
                    "status": current_status.value,
                    "current_step": current_step.value,
                    "deployment_result": deployment_result_data # Save the result
                })
                # Fall through to Marketing

            # Step 6: Marketing (New)
            # Run if status is COMPLETED_DEPLOYMENT
            if current_status == WorkflowStatus.COMPLETED_DEPLOYMENT:
                current_step = WorkflowStep.MARKETING
                logger.info(f"\n[{workflow_run_id}] --- Running Step: {current_step.value} ---")
                current_status = WorkflowStatus.RUNNING_MARKETING
                await self._update_workflow_state(workflow_run_id, {"status": current_status.value, "current_step": current_step.value})

                # Need product spec, brand package, and deployment result
                if not product_spec_data or not brand_package_data or not deployment_result_data:
                    raise ValueError("Product spec, brand package, or deployment data missing for marketing step.")

                # Re-validate/parse data into expected Pydantic models for the input
                try:
                    product_spec_model = ImprovedProductSpec(**product_spec_data)
                    brand_package_model = BrandPackage(**brand_package_data)
                    # Deployment URL is optional in the result model
                    deployment_url = deployment_result_data.get('deployment_url')
                except ValidationError as ve:
                    raise RuntimeError(f"Failed to validate data for Marketing input: {ve}")

                marketing_payload = MarketingAgentInput(
                    product_spec=product_spec_model,
                    brand_package=brand_package_model,
                    deployment_url=deployment_url
                ).model_dump(exclude_none=True)

                marketing_event = await self._invoke_adk_skill(
                    context=context,
                    agent_name="Marketing", target_agent_id=self.marketing_agent_id,
                    skill_name="marketing",
                    payload=marketing_payload,
                )

                if marketing_event.type == EventType.ERROR:
                    error_details = marketing_event.data.get('error', 'Marketing A2A call failed')
                    return await self._handle_step_failure(workflow_run_id, current_step, error_details, "Marketing")
                if not marketing_event.data: raise RuntimeError("Marketing Agent returned no data.")

                try:
                    marketing_result = MarketingMaterialsPackage(**marketing_event.data)
                    marketing_result_data = marketing_result.model_dump()
                    # Check if the agent reported failure *within* the successful event
                    if marketing_result.status.lower() == 'failed':
                        error_details = marketing_result.error_message or "Marketing Agent reported failure without details."
                        return await self._handle_step_failure(workflow_run_id, current_step, error_details, "Marketing")

                except ValidationError as ve:
                    error_details = f"Marketing Agent response validation failed: {ve}"
                    return await self._handle_step_failure(workflow_run_id, current_step, error_details, "Marketing")

                logger.info(f"[{workflow_run_id}] --- Step {current_step.value} Complete ---")
                current_status = WorkflowStatus.COMPLETED_MARKETING
                await self._update_workflow_state(workflow_run_id, {
                    "status": current_status.value,
                    "current_step": current_step.value,
                    "marketing_result": marketing_result_data # Save the result
                })
                # Fall through to final completion

            # --- Workflow Completion ---
            # Run if status is COMPLETED_MARKETING
            if current_status == WorkflowStatus.COMPLETED_MARKETING:
                current_status = WorkflowStatus.COMPLETED # Final status
                logger.info(f"\n[{workflow_run_id}] --- Workflow COMPLETED Successfully (including Marketing) ---")
                final_result = {
                    "workflow_run_id": workflow_run_id,
                    "status": current_status.value,
                    "initial_topic": initial_topic,
                    "deployment_details": deployment_result_data,
                    "marketing_materials": marketing_result_data, # Include marketing materials
                    # Optionally include other results if needed for the final output
                    # "market_research_result": market_report_data, # Already in state
                    # "improvement_result": product_spec_data,
                    # "branding_result": brand_package_data,
                    # "code_generation_result": code_generation_result_data, # Already in state
                }
                await self._update_workflow_state(workflow_run_id, {
                    "status": current_status.value,
                    "current_step": current_step.value, # Mark final step completed
                    # marketing_result already saved in the previous step
                    "final_result": final_result # Store final summary result
                })
                # Emit final success event
                self.socketio.emit('workflow_completed', {'workflow_run_id': workflow_run_id, 'result': final_result})
                return Event(type=EventType.RESULT, data=final_result)

            # Handle unexpected states (e.g., if status is already COMPLETED or FAILED when invoked)
            if current_status in [WorkflowStatus.COMPLETED, WorkflowStatus.FAILED]:
                 logger.warning(f"[{workflow_run_id}] Workflow is already in a terminal state ({current_status.value}). No further action taken.")
                 # Return the final result if completed, or an error if failed
                 final_data = state.get("final_result") if current_status == WorkflowStatus.COMPLETED else state.get("error", "Workflow previously failed.")
                 event_type = EventType.RESULT if current_status == WorkflowStatus.COMPLETED else EventType.ERROR
                 return Event(type=event_type, data=final_data)

            # If execution reaches here without returning, it means the status didn't match any step logic
            # This might happen if the status is RUNNING_... but the process restarts unexpectedly
            # Or if the status is somehow invalid.
            raise RuntimeError(f"Invalid state or logic error: Reached end of workflow execution checks with status '{current_status.value}'")


        except (ValueError, TypeError, ConnectionError, TimeoutError, RuntimeError, ValidationError, json.JSONDecodeError) as e:
            error_message = f"Workflow failed at Step '{current_step.value if current_step else 'UNKNOWN'}': {type(e).__name__}: {e}"
            # Ensure status is updated to FAILED in Firestore even if it was already FAILED
            # Use workflow_run_id directly as it's guaranteed to be set by this point
            # Determine the step where the error occurred
            failed_step_value = current_step.value if current_step else state.get("current_step", "UNKNOWN")

            current_status = WorkflowStatus.FAILED
            logger.error(f"[{workflow_run_id}] Error: {error_message}", exc_info=True) # Log traceback for context
            # Use workflow_run_id directly as it's guaranteed to be set by this point
            await self._update_workflow_state(workflow_run_id, {
                "status": current_status.value,
                "current_step": current_step.value if current_step else state.get("current_step"), # Use last known step
                "error": error_message
            })
            # Emit SocketIO event for general exceptions caught here
            self.socketio.emit('workflow_failed', {'workflow_run_id': workflow_run_id, 'failed_step': failed_step_value, 'error': error_message})
            return Event(type=EventType.ERROR, data={"error": error_message, "stage": failed_step_value, "workflow_run_id": workflow_run_id})
        except Exception as e:
            error_message = f"Unexpected workflow error at Step '{current_step.value if current_step else 'UNKNOWN'}': {type(e).__name__}: {e}"
            # Ensure status is updated to FAILED in Firestore
            # Determine the step where the error occurred
            failed_step_value = current_step.value if current_step else state.get("current_step", "UNKNOWN")

            current_status = WorkflowStatus.FAILED
            logger.error(f"[{workflow_run_id}] Error: {error_message}", exc_info=True) # Log traceback
            await self._update_workflow_state(workflow_run_id, {
                "status": current_status.value,
                "current_step": current_step.value if current_step else state.get("current_step"), # Use last known step
                "error": "An unexpected internal error occurred."
            })
            # Emit SocketIO event for unexpected exceptions
            self.socketio.emit('workflow_failed', {'workflow_run_id': workflow_run_id, 'failed_step': failed_step_value, 'error': "An unexpected internal error occurred."})
            return Event(type=EventType.ERROR, data={"error": "An unexpected internal error occurred.", "stage": failed_step_value, "workflow_run_id": workflow_run_id})

# Note: The `if __name__ == "__main__":` block is removed as agent execution
# is handled by the ADK runtime.
