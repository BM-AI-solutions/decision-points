import json
import time
import random
import httpx
import asyncio
import uuid
import os # Added for environment variables
import argparse # Added for server args
from enum import Enum
from typing import Dict, Any, Optional, Union, Tuple
import logging

import uvicorn # Added for server
from fastapi import FastAPI, HTTPException, Body # Added for server
from pydantic import BaseModel, Field, HttpUrl, ValidationError

# Firestore client
from google.cloud import firestore
from google.cloud.firestore_v1.async_client import AsyncClient as FirestoreAsyncClient

# Import SocketIO type hint if needed (optional but good practice)
try:
    from flask_socketio import SocketIO
    SOCKETIO_AVAILABLE = True
except ImportError:
    SOCKETIO_AVAILABLE = False
    SocketIO = Any # Fallback if flask_socketio is not installed here

from google.adk.agents import Agent
from google.adk.runtime import InvocationContext
from google.adk.runtime.event import Event, EventType # Use EventType enum


# Configure logging
# Use logfire if configured globally, otherwise standard logging
try:
    import logfire
    logger = logfire
except ImportError:
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO"))

# --- Data Models (Input/Output Schemas) ---
# These models are used for structuring data internally and for FastAPI endpoints.
# They should ideally match the actual schemas defined in the respective agent files.

class MarketResearchInput(BaseModel):
    initial_topic: str
    target_url: Optional[HttpUrl] = None
    num_competitors: int = 3

class MarketOpportunityReport(BaseModel):
    competitors: list = []
    analysis: dict = {}
    feature_recommendations: list = []
    target_audience_suggestions: list = []
    competitor_weaknesses: list = Field(default_factory=list)
    market_gaps: list = Field(default_factory=list)
    status: str = "completed"
    error_message: Optional[str] = None

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
    unique_selling_propositions: list = []
    implementation_difficulty_estimate: Optional[int] = None
    potential_revenue_impact_estimate: Optional[str] = None
    potential_rating: Optional[str] = None
    feasibility_score: Optional[float] = None
    assessment_rationale: Optional[str] = None
    status: str = "completed"
    error_message: Optional[str] = None

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
    target_demographics: list = []
    status: str = "completed"
    error_message: Optional[str] = None

class CodeGenerationAgentInput(BaseModel):
    product_spec: ImprovedProductSpec
    brand_package: BrandPackage

class CodeGenerationResult(BaseModel):
    generated_code_dict: Dict[str, str] = Field(..., description="Dictionary mapping filenames to code content")
    status: str = "completed"
    error_message: Optional[str] = None

class DeploymentAgentInput(BaseModel):
    brand_name: str
    product_concept: str
    key_features: list = []
    generated_code_dict: Optional[Dict[str, str]] = None

class DeploymentResult(BaseModel):
    deployment_url: Optional[str] = None
    status: str
    brand_name: Optional[str] = None
    features_deployed: list = []
    monitoring_url: Optional[str] = None
    deployment_details: dict = {}
    domains: list = []
    dns_settings: dict = {}
    error_message: Optional[str] = None

class MarketingAgentInput(BaseModel):
   product_spec: ImprovedProductSpec
   brand_package: BrandPackage
   deployment_url: Optional[str] = None

class MarketingMaterialsPackage(BaseModel):
   social_media_posts: Optional[Dict[str, list[str]]] = None
   blog_post_ideas: Optional[list[str]] = None
   email_campaign_snippets: Optional[list[str]] = None
   ad_copy_suggestions: Optional[list[str]] = None
   landing_page_copy: Optional[str] = None
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
    RUNNING_CODE_GENERATION = "RUNNING_CODE_GENERATION"
    COMPLETED_CODE_GENERATION = "COMPLETED_CODE_GENERATION"
    RUNNING_DEPLOYMENT = "RUNNING_DEPLOYMENT"
    COMPLETED_DEPLOYMENT = "COMPLETED_DEPLOYMENT"
    RUNNING_MARKETING = "RUNNING_MARKETING"
    COMPLETED_MARKETING = "COMPLETED_MARKETING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class WorkflowStep(str, Enum):
    MARKET_RESEARCH = "MARKET_RESEARCH"
    IMPROVEMENT = "IMPROVEMENT"
    BRANDING = "BRANDING"
    CODE_GENERATION = "CODE_GENERATION"
    DEPLOYMENT = "DEPLOYMENT"
    MARKETING = "MARKETING"

# --- FastAPI Input/Output Models ---
class WorkflowManagerInput(BaseModel):
    """Input model for the WorkflowManagerAgent /invoke endpoint."""
    initial_topic: str = Field(description="The initial topic for market research.")
    target_url: Optional[HttpUrl] = Field(None, description="Optional target URL.")
    workflow_run_id: Optional[str] = Field(None, description="Existing workflow run ID to resume.")
    # Add other potential input fields needed for resuming or specific steps
    # e.g., approval_data: Optional[Dict[str, Any]] = None # If approval sends data back

class WorkflowManagerOutput(BaseModel):
    """Output model for the WorkflowManagerAgent /invoke endpoint."""
    workflow_run_id: str = Field(description="The ID of the workflow run.")
    status: WorkflowStatus = Field(description="The current status of the workflow.")
    current_step: Optional[WorkflowStep] = Field(None, description="The current or last completed step.")
    message: Optional[str] = Field(None, description="A human-readable message about the workflow status.")
    result: Optional[Any] = Field(None, description="The final result data if the workflow completed successfully.")
    error: Optional[str] = Field(None, description="Error message if the workflow failed.")
    # Include results from steps if needed in the final output, or rely on Firestore/SocketIO


# --- Workflow Manager Agent ---

class WorkflowManagerAgent(Agent):
    """
    Orchestrates the autonomous income generation workflow using ADK and A2A HTTP.
    Manages state in Firestore and communicates with specialized agents via HTTP.
    Includes retry logic for A2A calls.
    """
    # Environment variables for agent URLs
    ENV_GCP_PROJECT_ID = "GCP_PROJECT_ID" # For Firestore
    ENV_FIRESTORE_COLLECTION = "WORKFLOW_FIRESTORE_COLLECTION" # For Firestore workflow state

    ENV_MARKET_RESEARCH_AGENT_URL = "MARKET_RESEARCH_AGENT_URL"
    ENV_IMPROVEMENT_AGENT_URL = "IMPROVEMENT_AGENT_URL"
    ENV_BRANDING_AGENT_URL = "BRANDING_AGENT_URL"
    ENV_CODE_GENERATION_AGENT_URL = "CODE_GENERATION_AGENT_URL"
    ENV_DEPLOYMENT_AGENT_URL = "DEPLOYMENT_AGENT_URL"
    ENV_MARKETING_AGENT_URL = "MARKETING_AGENT_URL"

    # Mapping of logical agent keys to their environment variable names
    AGENT_URL_ENVS = {
        "market_research": ENV_MARKET_RESEARCH_AGENT_URL,
        "improvement": ENV_IMPROVEMENT_AGENT_URL,
        "branding": ENV_BRANDING_AGENT_URL,
        "code_generation": ENV_CODE_GENERATION_AGENT_URL,
        "deployment": ENV_DEPLOYMENT_AGENT_URL,
        "marketing": ENV_MARKETING_AGENT_URL,
    }

    def __init__(
        self,
        socketio: Optional[SocketIO] = None, # SocketIO is optional for A2A server
        agent_id: str = "workflow-manager-agent",
    ):
        """
        Initializes the WorkflowManagerAgent.
        Reads configuration from environment variables.
        """
        super().__init__(agent_id=agent_id)
        logger.info(f"Initializing WorkflowManagerAgent ({self.agent_id})...")

        # --- Configuration from Environment ---
        self.gcp_project_id = os.environ.get(self.ENV_GCP_PROJECT_ID)
        self.collection_name = os.environ.get(self.ENV_FIRESTORE_COLLECTION, "workflow_runs") # Default collection name

        # Resolve agent URLs from environment variables
        self.agent_urls: Dict[str, str] = {}
        for key, env_var in self.AGENT_URL_ENVS.items():
            url = os.environ.get(env_var)
            if url:
                self.agent_urls[key] = url.rstrip('/') # Store URL, remove trailing slash
                logger.info(f"Resolved URL for agent '{key}': {self.agent_urls[key]}")
            else:
                logger.warning(f"Environment variable {env_var} not set. Delegation to '{key}' will be disabled.")

        # Firestore client
        self.db: Optional[FirestoreAsyncClient] = None
        if not self.gcp_project_id:
            logger.warning(f"{self.ENV_GCP_PROJECT_ID} not set. Firestore state persistence disabled.")
        else:
            try:
                self.db = firestore.AsyncClient(project=self.gcp_project_id)
                logger.info(f"WorkflowManagerAgent initialized with Firestore collection: {self.collection_name}")
            except Exception as e:
                logger.error(f"Failed to initialize Firestore client: {e}", exc_info=True)
                self.db = None # Ensure db is None on error

        # Async HTTP client for A2A calls
        self.timeout_seconds = int(os.environ.get("A2A_TIMEOUT_SECONDS", 120)) # Use env var for timeout
        self.max_retries = int(os.environ.get("A2A_MAX_RETRIES", 3)) # Use env var for retries
        self.retry_delay = int(os.environ.get("A2A_RETRY_DELAY_SECONDS", 5)) # Use env var for retry delay
        self._http_client = httpx.AsyncClient(timeout=self.timeout_seconds)

        self.socketio = socketio # Store SocketIO instance (optional)
        if not SOCKETIO_AVAILABLE:
            logger.warning("Flask-SocketIO not available. Real-time task updates will be disabled.")
        elif not self.socketio:
             logger.warning("SocketIO instance not provided. Real-time task updates will be disabled.")


        logger.info(f"WorkflowManagerAgent ({self.agent_id}) initialized successfully.")


    async def close_clients(self):
        """Clean up resources, like the HTTP client and Firestore."""
        if self._http_client and not self._http_client.is_closed:
            await self._http_client.aclose()
            logger.info(f"[{self.agent_id}] Closed httpx client.")
        # Firestore client doesn't typically need explicit closing in this context


    async def _call_agent_a2a(
        self,
        agent_key: str, # Logical agent key (e.g., 'market_research')
        invocation_id: str, # The current workflow invocation ID
        payload: Dict[str, Any], # The data dictionary to send as the JSON body
    ) -> Event:
        """
        Helper function to invoke another agent's A2A /invoke endpoint asynchronously with retry logic.
        Constructs the URL based on the agent_key.
        """
        agent_url = self.agent_urls.get(agent_key)
        if not agent_url:
            error_msg = f"URL for agent '{agent_key}' is not configured."
            logger.error(f"[{invocation_id}] Error: {error_msg}")
            return Event(type=EventType.ERROR, data={"error": error_msg, "agent": agent_key})

        # Assuming all agents have a standard '/invoke' endpoint
        invoke_url = f"{agent_url}/invoke"
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        last_exception: Optional[Exception] = None

        logger.info(f"[{invocation_id}] Invoking {agent_key} A2A endpoint at {invoke_url} (Retries: {self.max_retries}, Delay: {self.retry_delay}s)...")

        for attempt in range(self.max_retries):
            try:
                response = await self._http_client.post(
                    invoke_url,
                    json=payload,
                    headers=headers,
                    timeout=self.timeout_seconds
                )
                response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)

                # --- Success Case ---
                try:
                    # Assuming the response body is the data payload of the result
                    # We need to wrap this in an ADK Event structure
                    response_data = response.json()
                    # Check if the response data itself indicates an error (e.g., has an 'error' key)
                    # This depends on the target agent's error response format.
                    # Let's assume if the HTTP status is 2xx, the response body is the result payload.
                    # If the target agent returns a specific error structure on 2xx, handle it here.
                    # Based on other agent refactors, they return a Pydantic model on 2xx success.
                    # If the model has an 'error' field or 'status'=='failed', it's an internal agent error.

                    # Let's assume the target agent's 2xx response body is the data payload.
                    # We need to create an ADK Event to represent this.
                    # The type should be RESULT, and the data is the response body.
                    result_event = Event(
                        type=EventType.RESULT, # Assume RESULT type for 2xx HTTP status
                        data=response_data, # The response body is the data payload
                        metadata={"status": "success", "agent": agent_key, "http_status": response.status_code} # Add metadata
                    )

                    # Check if the agent's *internal* status within the payload indicates failure
                    # This requires knowing the structure of the response_data.
                    # Let's assume a common pattern like {'status': 'completed'/'failed', 'error_message': '...'}
                    agent_status = response_data.get('status', 'completed').lower()
                    if agent_status == 'failed':
                         error_msg = response_data.get('error_message', f"{agent_key} reported internal failure.")
                         logger.error(f"[{invocation_id}] Agent '{agent_key}' reported internal failure: {error_msg}")
                         # Return an ERROR event based on the agent's internal status
                         return Event(type=EventType.ERROR, data={"error": error_msg, "agent": agent_key, "details": response_data})


                    logger.info(f"[{invocation_id}] Agent '{agent_key}' A2A call successful (Attempt {attempt + 1}/{self.max_retries}).")
                    return result_event # Success, return immediately

                except (json.JSONDecodeError, ValidationError, TypeError) as e:
                    # Handle issues with response format *after* successful HTTP call
                    error_msg = f"Failed to process or validate successful A2A response from {agent_key}: {e}"
                    logger.error(f"[{invocation_id}] Error: {error_msg}. Response text: {response.text[:500]}", exc_info=True)
                    # Don't retry format errors, return error event immediately
                    return Event(type=EventType.ERROR, data={"error": error_msg, "agent": agent_key, "details": "Invalid Response Format"})

            except (httpx.TimeoutException, httpx.ConnectError) as e:
                last_exception = e
                logger.warning(f"[{invocation_id}] A2A call to {agent_key} failed (Attempt {attempt + 1}/{self.max_retries}): Timeout or Connection Error ({type(e).__name__}).")
                # Fall through to retry logic

            except httpx.HTTPStatusError as e:
                last_exception = e
                # Retry only on 5xx server errors
                if e.response.status_code >= 500:
                    logger.warning(f"[{invocation_id}] A2A call to {agent_key} failed (Attempt {attempt + 1}/{self.max_retries}): Server Error ({e.response.status_code}).")
                    # Fall through to retry logic
                else:
                    # Non-5xx HTTP error (e.g., 4xx), likely not transient. Don't retry.
                    error_detail = str(e)
                    try:
                        error_detail += f" | Status: {e.response.status_code} | Response: {e.response.text[:500]}"
                    except Exception: pass
                    error_msg = f"HTTP error calling {agent_key} A2A endpoint (non-retryable): {error_detail}"
                    logger.error(f"[{invocation_id}] Error: {error_msg}")
                    return Event(type=EventType.ERROR, data={"error": error_msg, "agent": agent_key, "details": f"HTTP Error {e.response.status_code}"})

            except httpx.RequestError as e:
                last_exception = e
                logger.warning(f"[{invocation_id}] A2A call to {agent_key} failed (Attempt {attempt + 1}/{self.max_retries}): Request Error ({type(e).__name__}: {e}).")
                # Fall through to retry logic

            except Exception as e:
                 last_exception = e
                 logger.error(f"[{invocation_id}] Unexpected error during {agent_key} A2A call attempt {attempt + 1}/{self.max_retries}: {type(e).__name__}: {e}", exc_info=True)
                 # If it's the last attempt, let it be handled below. Otherwise, retry.
                 if attempt >= self.max_retries - 1:
                     break # Exit loop to handle final error

            # --- Retry Logic ---
            if attempt < self.max_retries - 1:
                logger.info(f"[{invocation_id}] Retrying in {self.retry_delay}s...")
                await asyncio.sleep(self.retry_delay)
            else:
                logger.error(f"[{invocation_id}] A2A call to {agent_key} failed after {self.max_retries} attempts.")
                break # Exit loop after last attempt

        # --- Handle Failure After Retries ---
        # If the loop finished without returning a success event
        error_msg = f"A2A call to {agent_key} failed after {self.max_retries} attempts."
        error_details = "Max retries exceeded"
        if last_exception:
            error_msg += f" Last error: {type(last_exception).__name__}: {last_exception}"
            if isinstance(last_exception, httpx.TimeoutException): error_details = "Timeout"
            elif isinstance(last_exception, httpx.ConnectError): error_details = "Connection Error"
            elif isinstance(last_exception, httpx.HTTPStatusError): error_details = f"HTTP Error {last_exception.response.status_code}"
            else: error_details = f"{type(last_exception).__name__}"

        logger.error(f"[{invocation_id}] Final Error: {error_msg}")
        return Event(type=EventType.ERROR, data={"error": error_msg, "agent": agent_key, "details": error_details})


    async def _update_workflow_state(self, workflow_run_id: str, state_data: Dict[str, Any]):
        """Helper to update workflow state in Firestore."""
        if not self.db:
            logger.error(f"[{workflow_run_id}] Error: Firestore client not available. Cannot update state.")
            return

        try:
            state_data['last_updated'] = firestore.SERVER_TIMESTAMP
            doc_ref = self.db.collection(self.collection_name).document(workflow_run_id)
            await doc_ref.set(state_data, merge=True)
            logger.info(f"[{workflow_run_id}] Firestore state updated: Status={state_data.get('status')}, Step={state_data.get('current_step')}")
        except Exception as e:
            logger.error(f"[{workflow_run_id}] Error updating Firestore state: {type(e).__name__}: {e}", exc_info=True)


    async def _handle_step_failure(self, workflow_run_id: str, current_step: WorkflowStep, error_details: str, agent_name: str) -> Event:
        """Handles Firestore update, SocketIO emit, and returns final error event for a failed step."""
        logger.error(f"[{workflow_run_id}] Step {current_step.value} failed. Agent: {agent_name}. Reason: {error_details}")
        current_status = WorkflowStatus.FAILED
        await self._update_workflow_state(workflow_run_id, {
            "status": current_status.value,
            "current_step": current_step.value,
            "error_message": error_details
        })
        # Emit SocketIO update if available
        self._emit_task_update(workflow_run_id, workflow_run_id, 'failed', f"Workflow failed at {current_step.value}: {error_details}", result={"failed_step": current_step.value, "error": error_details})

        return Event(type=EventType.ERROR, data={"error": error_details, "stage": current_step.value, "workflow_run_id": workflow_run_id})


    async def run_async(self, context: InvocationContext) -> Event:
        """
        ADK entry point to orchestrate the workflow asynchronously using Firestore for state.
        This method handles both initial invocation and resumption based on Firestore state.
        Input is expected in context.data.
        """
        invocation_id = context.invocation_id
        input_data = context.data or {}

        workflow_run_id = input_data.get("workflow_run_id")
        is_new_workflow = not workflow_run_id

        # --- State Variables ---
        current_status: Optional[WorkflowStatus] = None
        current_step: Optional[WorkflowStep] = None
        initial_topic: Optional[str] = None
        target_url: Optional[str] = None
        market_report_data: Optional[Dict] = None
        product_spec_data: Optional[Dict] = None
        brand_package_data: Optional[Dict] = None
        code_generation_result_data: Optional[Dict] = None
        deployment_result_data: Optional[Dict] = None
        marketing_result_data: Optional[Dict] = None
        state: Dict[str, Any] = {}

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
                target_url = input_data.get("target_url")
                if not initial_topic or not isinstance(initial_topic, str):
                    raise ValueError("Missing or invalid 'initial_topic' for new workflow.")
                logger.info(f"[{workflow_run_id}] Initial Topic: {initial_topic}, Target URL: {target_url}")

                current_status = WorkflowStatus.STARTING
                current_step = None
                state = {
                    "status": current_status.value,
                    "initial_topic": initial_topic,
                    "target_url": target_url,
                    "invocation_id": invocation_id, # Store the initial invocation ID
                    "current_step": None,
                    "created_at": firestore.SERVER_TIMESTAMP,
                }
                await self._update_workflow_state(workflow_run_id, state)
                # Emit SocketIO update for new workflow
                self._emit_task_update(workflow_run_id, workflow_run_id, current_status.value, f"Workflow started for topic: {initial_topic}")

            else:
                # Load existing state from Firestore
                logger.info(f"[{invocation_id}/{workflow_run_id}] Attempting to load existing workflow run.")
                doc_ref = self.db.collection(self.collection_name).document(workflow_run_id)
                doc_snapshot = await doc_ref.get()
                if not doc_snapshot.exists:
                    raise ValueError(f"Workflow run ID '{workflow_run_id}' not found in Firestore.")

                state = doc_snapshot.to_dict() or {} # Ensure state is a dict
                initial_topic = state.get("initial_topic")
                target_url = state.get("target_url")
                market_report_data = state.get("market_research_result")
                product_spec_data = state.get("improvement_result")
                brand_package_data = state.get("branding_result")
                code_generation_result_data = state.get("code_generation_result")
                deployment_result_data = state.get("deployment_result")
                marketing_result_data = state.get("marketing_result")
                current_status_str = state.get("status", WorkflowStatus.FAILED.value)
                try:
                    current_status = WorkflowStatus(current_status_str)
                except ValueError:
                    logger.error(f"[{workflow_run_id}] Invalid status '{current_status_str}' loaded from state. Defaulting to FAILED.")
                    current_status = WorkflowStatus.FAILED

                current_step_str = state.get("current_step")
                try:
                    current_step = WorkflowStep(current_step_str) if current_step_str else None
                except ValueError:
                    logger.error(f"[{workflow_run_id}] Invalid step '{current_step_str}' loaded from state. Setting to None.")
                    current_step = None


                logger.info(f"[{workflow_run_id}] State loaded from Firestore. Status: {current_status.value}, Last Step: {current_step.value if current_step else 'None'}")

                # Handle the case where the frontend signals resumption after approval
                # The input data might contain a flag or the status might be PENDING_APPROVAL
                # Let's assume a resume invocation has status PENDING_APPROVAL in state
                if current_status == WorkflowStatus.PENDING_APPROVAL:
                    logger.info(f"[{workflow_run_id}] Workflow was pending approval. Transitioning to APPROVED_RESUMING.")
                    current_status = WorkflowStatus.APPROVED_RESUMING
                    await self._update_workflow_state(workflow_run_id, {"status": current_status.value})
                    self._emit_task_update(workflow_run_id, workflow_run_id, current_status.value, "Approval received. Resuming workflow...")


                # Validation: Ensure necessary data exists for the expected next step
                if current_status == WorkflowStatus.APPROVED_RESUMING and not market_report_data: raise ValueError("Cannot resume from improvement: Market research result missing in Firestore.")
                if current_status == WorkflowStatus.COMPLETED_IMPROVEMENT and not product_spec_data: raise ValueError("Cannot resume from branding: Improvement result missing in Firestore.")
                if current_status == WorkflowStatus.COMPLETED_BRANDING and (not product_spec_data or not brand_package_data): raise ValueError("Cannot resume from code generation: Improvement or Branding result missing in Firestore.")
                if current_status == WorkflowStatus.COMPLETED_CODE_GENERATION and (not brand_package_data or not code_generation_result_data): raise ValueError("Cannot resume from deployment: Branding or Code Generation result missing in Firestore.")
                if current_status == WorkflowStatus.COMPLETED_DEPLOYMENT and (not product_spec_data or not brand_package_data or not deployment_result_data): raise ValueError("Cannot resume from marketing: Product Spec, Branding, or Deployment result missing in Firestore.")
                if not initial_topic: raise ValueError("Cannot resume: Initial topic missing in Firestore state.")


            # --- Workflow Execution Logic ---
            # Determine which steps need to run based on the current status

            # Step 1: Market Research
            if current_status == WorkflowStatus.STARTING:
                current_step = WorkflowStep.MARKET_RESEARCH
                logger.info(f"\n[{workflow_run_id}] --- Running Step: {current_step.value} ---")
                current_status = WorkflowStatus.RUNNING_MARKET_RESEARCH
                await self._update_workflow_state(workflow_run_id, {"status": current_status.value, "current_step": current_step.value})
                self._emit_task_update(workflow_run_id, workflow_run_id, current_status.value, f"Starting {current_step.value}...")

                market_research_payload = MarketResearchInput(
                    initial_topic=initial_topic,
                    target_url=target_url
                ).model_dump(exclude_none=True)

                market_event = await self._call_agent_a2a(
                    agent_key="market_research",
                    invocation_id=workflow_run_id, # Use workflow_run_id for traceability
                    payload=market_research_payload,
                )

                if market_event.type == EventType.ERROR:
                    error_details = market_event.data.get('error', 'Market Research A2A call failed')
                    return await self._handle_step_failure(workflow_run_id, current_step, error_details, "Market Research")
                if not market_event.data: raise RuntimeError("Market Research Agent returned no data.")

                try:
                    # Validate the response data against the expected output model
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
                    serializable_market_data = json.loads(json.dumps(market_report_data))
                except (TypeError, ValueError) as json_err:
                    raise RuntimeError(f"Market research result could not be serialized: {json_err}")

                current_status = WorkflowStatus.PENDING_APPROVAL
                await self._update_workflow_state(workflow_run_id, {
                    "status": current_status.value,
                    "current_step": current_step.value,
                    "market_research_result": serializable_market_data
                })

                # Emit SocketIO update for approval
                self._emit_task_update(workflow_run_id, workflow_run_id, current_status.value, "Market research complete. Awaiting approval.", result=serializable_market_data)

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
                current_status = WorkflowStatus.RUNNING_IMPROVEMENT
                await self._update_workflow_state(workflow_run_id, {"status": current_status.value, "current_step": current_step.value})
                self._emit_task_update(workflow_run_id, workflow_run_id, current_status.value, f"Starting {current_step.value}...")

                if not market_report_data: raise ValueError("Market research data missing for improvement step.")

                improvement_payload = ImprovementAgentInput(
                    product_concept=initial_topic,
                    competitor_weaknesses=market_report_data.get('competitor_weaknesses', []),
                    market_gaps=market_report_data.get('market_gaps', []),
                    target_audience_suggestions=market_report_data.get('target_audience_suggestions', []),
                    feature_recommendations_from_market=market_report_data.get('feature_recommendations', []),
                    business_model_type="saas" # Placeholder, get from input if available
                ).model_dump(exclude_none=True)

                improvement_event = await self._call_agent_a2a(
                    agent_key="improvement",
                    invocation_id=workflow_run_id,
                    payload=improvement_payload,
                )

                if improvement_event.type == EventType.ERROR:
                    error_details = improvement_event.data.get('error', 'Improvement A2A call failed')
                    return await self._handle_step_failure(workflow_run_id, current_step, error_details, "Improvement")
                if not improvement_event.data: raise RuntimeError("Improvement Agent returned no data.")

                try:
                    product_spec = ImprovedProductSpec(**improvement_event.data)
                    product_spec_data = product_spec.model_dump()
                    if product_spec.status.lower() == 'failed':
                        error_details = product_spec.error_message or "Improvement Agent reported failure without details."
                        return await self._handle_step_failure(workflow_run_id, current_step, error_details, "Improvement")
                except ValidationError as ve:
                    error_details = f"Improvement Agent response validation failed: {ve}"
                    return await self._handle_step_failure(workflow_run_id, current_step, error_details, "Improvement")

                logger.info(f"[{workflow_run_id}] --- Step {current_step.value} Complete ---")
                current_status = WorkflowStatus.COMPLETED_IMPROVEMENT
                await self._update_workflow_state(workflow_run_id, {
                    "status": current_status.value,
                    "current_step": current_step.value,
                    "improvement_result": product_spec_data
                })
                self._emit_task_update(workflow_run_id, workflow_run_id, current_status.value, f"{current_step.value} complete.")

                # --- Feasibility Check ---
                logger.info(f"[{workflow_run_id}] Performing feasibility check based on Improvement result.")
                potential_rating = product_spec_data.get('potential_rating', 'Low').capitalize()
                feasibility_score = product_spec_data.get('feasibility_score')
                assessment_rationale = product_spec_data.get('assessment_rationale', 'Assessment rationale not provided.')

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
                else:
                    logger.warning(f"[{workflow_run_id}] Feasibility check failed (Potential: {potential_rating}). Stopping workflow.")


                if not proceed_to_branding:
                    current_status = WorkflowStatus.STOPPED_LOW_POTENTIAL
                    stop_message = f"Workflow stopped: Potential rated '{potential_rating}'"
                    if feasibility_score is not None: stop_message += f" (Score: {feasibility_score})"
                    stop_message += "."
                    logger.warning(f"[{workflow_run_id}] {stop_message} Rationale: {assessment_rationale}")
                    await self._update_workflow_state(workflow_run_id, {
                        "status": current_status.value, "current_step": current_step.value, "error": stop_message
                    })
                    self._emit_task_update(workflow_run_id, workflow_run_id, current_status.value, stop_message, result={'rationale': assessment_rationale, 'step': current_step.value})
                    return Event(type=EventType.RESULT, data={"status": current_status.value, "workflow_run_id": workflow_run_id, "message": stop_message, "rationale": assessment_rationale})

                # Fall through to Branding ONLY IF feasibility check passed


            # Step 3: Rebranding
            # Run if status is COMPLETED_IMPROVEMENT
            if current_status == WorkflowStatus.COMPLETED_IMPROVEMENT:
                current_step = WorkflowStep.BRANDING
                logger.info(f"\n[{workflow_run_id}] --- Running Step: {current_step.value} ---")
                current_status = WorkflowStatus.RUNNING_BRANDING
                await self._update_workflow_state(workflow_run_id, {"status": current_status.value, "current_step": current_step.value})
                self._emit_task_update(workflow_run_id, workflow_run_id, current_status.value, f"Starting {current_step.value}...")

                if not product_spec_data: raise ValueError("Product spec data missing for branding step.")

                keywords = product_spec_data.get('product_concept', initial_topic).lower().split()[:5]
                branding_payload = BrandingAgentInput(
                    product_concept=product_spec_data.get('product_concept', initial_topic),
                    target_audience=product_spec_data.get('target_audience', []),
                    keywords=keywords,
                    business_model_type="saas" # Placeholder
                ).model_dump(exclude_none=True)

                branding_event = await self._call_agent_a2a(
                    agent_key="branding",
                    invocation_id=workflow_run_id,
                    payload=branding_payload,
                )

                if branding_event.type == EventType.ERROR:
                    error_details = branding_event.data.get('error', 'Branding A2A call failed')
                    return await self._handle_step_failure(workflow_run_id, current_step, error_details, "Branding")
                if not branding_event.data: raise RuntimeError("Branding Agent returned no data.")

                try:
                    brand_package = BrandPackage(**branding_event.data)
                    brand_package_data = brand_package.model_dump()
                    if brand_package.status.lower() == 'failed':
                        error_details = brand_package.error_message or "Branding Agent reported failure without details."
                        return await self._handle_step_failure(workflow_run_id, current_step, error_details, "Branding")
                except ValidationError as ve:
                    error_details = f"Branding Agent response validation failed: {ve}"
                    return await self._handle_step_failure(workflow_run_id, current_step, error_details, "Branding")

                logger.info(f"[{workflow_run_id}] --- Step {current_step.value} Complete ---")
                current_status = WorkflowStatus.COMPLETED_BRANDING
                await self._update_workflow_state(workflow_run_id, {
                    "status": current_status.value,
                    "current_step": current_step.value,
                    "branding_result": brand_package_data
                })
                self._emit_task_update(workflow_run_id, workflow_run_id, current_status.value, f"{current_step.value} complete.")
                # Fall through to Code Generation


            # Step 4: Code Generation
            # Run if status is COMPLETED_BRANDING
            if current_status == WorkflowStatus.COMPLETED_BRANDING:
                current_step = WorkflowStep.CODE_GENERATION
                logger.info(f"\n[{workflow_run_id}] --- Running Step: {current_step.value} ---")
                current_status = WorkflowStatus.RUNNING_CODE_GENERATION
                await self._update_workflow_state(workflow_run_id, {"status": current_status.value, "current_step": current_step.value})
                self._emit_task_update(workflow_run_id, workflow_run_id, current_status.value, f"Starting {current_step.value}...")

                if not product_spec_data or not brand_package_data:
                    raise ValueError("Product spec or brand package data missing for code generation step.")

                try:
                    product_spec_model = ImprovedProductSpec(**product_spec_data)
                    brand_package_model = BrandPackage(**brand_package_data)
                except ValidationError as ve:
                    raise RuntimeError(f"Failed to validate data for Code Generation input: {ve}")

                code_gen_payload = CodeGenerationAgentInput(
                    product_spec=product_spec_model,
                    brand_package=brand_package_model
                ).model_dump(exclude_none=True)

                code_gen_event = await self._call_agent_a2a(
                    agent_key="code_generation",
                    invocation_id=workflow_run_id,
                    payload=code_gen_payload,
                )

                if code_gen_event.type == EventType.ERROR:
                    error_details = code_gen_event.data.get('error', 'Code Generation A2A call failed')
                    return await self._handle_step_failure(workflow_run_id, current_step, error_details, "Code Generation")
                if not code_gen_event.data: raise RuntimeError("Code Generation Agent returned no data.")

                try:
                    code_gen_result = CodeGenerationResult(**code_gen_event.data)
                    code_generation_result_data = code_gen_result.model_dump()
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
                    "code_generation_result": code_generation_result_data
                })
                self._emit_task_update(workflow_run_id, workflow_run_id, current_status.value, f"{current_step.value} complete.")
                # Fall through to Deployment


            # Step 5: Deployment
            # Run if status is COMPLETED_CODE_GENERATION
            if current_status == WorkflowStatus.COMPLETED_CODE_GENERATION:
                current_step = WorkflowStep.DEPLOYMENT
                logger.info(f"\n[{workflow_run_id}] --- Running Step: {current_step.value} ---")
                current_status = WorkflowStatus.RUNNING_DEPLOYMENT
                await self._update_workflow_state(workflow_run_id, {"status": current_status.value, "current_step": current_step.value})
                self._emit_task_update(workflow_run_id, workflow_run_id, current_status.value, f"Starting {current_step.value}...")

                if not brand_package_data or not code_generation_result_data:
                    raise ValueError("Brand package or code generation data missing for deployment step.")
                if not product_spec_data:
                    product_spec_data = state.get("improvement_result")
                    if not product_spec_data:
                         raise ValueError("Product spec data missing for deployment step (failed to load from state).")

                deployment_payload = DeploymentAgentInput(
                    brand_name=brand_package_data.get('brand_name', 'Unnamed Brand'),
                    product_concept=product_spec_data.get('product_concept', initial_topic),
                    key_features=product_spec_data.get('key_features', []),
                    generated_code_dict=code_generation_result_data.get('generated_code_dict')
                ).model_dump(exclude_none=True)

                deployment_event = await self._call_agent_a2a(
                    agent_key="deployment",
                    invocation_id=workflow_run_id,
                    payload=deployment_payload,
                )

                if deployment_event.type == EventType.ERROR:
                    error_details = deployment_event.data.get('error', 'Deployment A2A call failed')
                    return await self._handle_step_failure(workflow_run_id, current_step, error_details, "Deployment")
                if not deployment_event.data: raise RuntimeError("Deployment Agent returned no data.")

                try:
                    deployment_result = DeploymentResult(**deployment_event.data)
                    deployment_result_data = deployment_result.model_dump()
                    agent_reported_status = deployment_result.status.lower()
                    if agent_reported_status == 'failed' or agent_reported_status != 'active':
                        error_details = deployment_result.error_message or f"Deployment Agent reported status '{deployment_result.status}'."
                        return await self._handle_step_failure(workflow_run_id, current_step, error_details, "Deployment")

                except ValidationError as ve:
                    error_details = f"Deployment Agent response validation failed: {ve}"
                    return await self._handle_step_failure(workflow_run_id, current_step, error_details, "Deployment")

                logger.info(f"[{workflow_run_id}] --- Step {current_step.value} Complete ---")
                current_status = WorkflowStatus.COMPLETED_DEPLOYMENT
                await self._update_workflow_state(workflow_run_id, {
                    "status": current_status.value,
                    "current_step": current_step.value,
                    "deployment_result": deployment_result_data
                })
                self._emit_task_update(workflow_run_id, workflow_run_id, current_status.value, f"{current_step.value} complete.", result=deployment_result_data)
                # Fall through to Marketing


            # Step 6: Marketing
            # Run if status is COMPLETED_DEPLOYMENT
            if current_status == WorkflowStatus.COMPLETED_DEPLOYMENT:
                current_step = WorkflowStep.MARKETING
                logger.info(f"\n[{workflow_run_id}] --- Running Step: {current_step.value} ---")
                current_status = WorkflowStatus.RUNNING_MARKETING
                await self._update_workflow_state(workflow_run_id, {"status": current_status.value, "current_step": current_step.value})
                self._emit_task_update(workflow_run_id, workflow_run_id, current_status.value, f"Starting {current_step.value}...")

                if not product_spec_data or not brand_package_data or not deployment_result_data:
                    raise ValueError("Product spec, brand package, or deployment data missing for marketing step.")

                try:
                    product_spec_model = ImprovedProductSpec(**product_spec_data)
                    brand_package_model = BrandPackage(**brand_package_data)
                    deployment_url = deployment_result_data.get('deployment_url')
                except ValidationError as ve:
                    raise RuntimeError(f"Failed to validate data for Marketing input: {ve}")

                marketing_payload = MarketingAgentInput(
                    product_spec=product_spec_model,
                    brand_package=brand_package_model,
                    deployment_url=deployment_url
                ).model_dump(exclude_none=True)

                marketing_event = await self._call_agent_a2a(
                    agent_key="marketing",
                    invocation_id=workflow_run_id,
                    payload=marketing_payload,
                )

                if marketing_event.type == EventType.ERROR:
                    error_details = marketing_event.data.get('error', 'Marketing A2A call failed')
                    return await self._handle_step_failure(workflow_run_id, current_step, error_details, "Marketing")
                if not marketing_event.data: raise RuntimeError("Marketing Agent returned no data.")

                try:
                    marketing_result = MarketingMaterialsPackage(**marketing_event.data)
                    marketing_result_data = marketing_result.model_dump()
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
                    "marketing_result": marketing_result_data
                })
                self._emit_task_update(workflow_run_id, workflow_run_id, current_status.value, f"{current_step.value} complete.", result=marketing_result_data)
                # Fall through to final completion


            # --- Workflow Completion ---
            # Run if status is COMPLETED_MARKETING
            if current_status == WorkflowStatus.COMPLETED_MARKETING:
                current_status = WorkflowStatus.COMPLETED
                logger.info(f"\n[{workflow_run_id}] --- Workflow COMPLETED Successfully ---")
                final_result = {
                    "workflow_run_id": workflow_run_id,
                    "status": current_status.value,
                    "initial_topic": initial_topic,
                    "deployment_details": deployment_result_data,
                    "marketing_materials": marketing_result_data,
                }
                await self._update_workflow_state(workflow_run_id, {
                    "status": current_status.value,
                    "current_step": current_step.value,
                    "final_result": final_result
                })
                # Emit final success event
                self._emit_task_update(workflow_run_id, workflow_run_id, current_status.value, "Workflow completed successfully!", result=final_result)

                return Event(type=EventType.RESULT, data=final_result)

            # Handle unexpected states (e.g., if status is already COMPLETED or FAILED when invoked)
            if current_status in [WorkflowStatus.COMPLETED, WorkflowStatus.FAILED, WorkflowStatus.STOPPED_LOW_POTENTIAL]:
                 logger.warning(f"[{workflow_run_id}] Workflow is already in a terminal state ({current_status.value}). No further action taken.")
                 # Return the final result if completed, or an error if failed/stopped
                 final_data = state.get("final_result") if current_status == WorkflowStatus.COMPLETED else state.get("error", "Workflow previously failed or stopped.")
                 event_type = EventType.RESULT if current_status == WorkflowStatus.COMPLETED else EventType.ERROR
                 return Event(type=event_type, data=final_data)


            # If execution reaches here without returning, it means the status didn't match any step logic
            raise RuntimeError(f"Invalid state or logic error: Reached end of workflow execution checks with status '{current_status.value}'")


        except (ValueError, TypeError, ConnectionError, TimeoutError, RuntimeError, ValidationError, json.JSONDecodeError) as e:
            error_message = f"Workflow failed at Step '{current_step.value if current_step else 'UNKNOWN'}': {type(e).__name__}: {e}"
            failed_step_value = current_step.value if current_step else state.get("current_step", "UNKNOWN")
            current_status = WorkflowStatus.FAILED
            logger.error(f"[{workflow_run_id}] Error: {error_message}", exc_info=True)
            await self._update_workflow_state(workflow_run_id, {
                "status": current_status.value,
                "current_step": current_step.value if current_step else state.get("current_step"),
                "error": error_message
            })
            self._emit_task_update(workflow_run_id, workflow_run_id, current_status.value, f"Workflow failed at {failed_step_value}: {error_message}", result={"failed_step": failed_step_value, "error": error_message})
            return Event(type=EventType.ERROR, data={"error": error_message, "stage": failed_step_value, "workflow_run_id": workflow_run_id})
        except Exception as e:
            error_message = f"Unexpected workflow error at Step '{current_step.value if current_step else 'UNKNOWN'}': {type(e).__name__}: {e}"
            failed_step_value = current_step.value if current_step else state.get("current_step", "UNKNOWN")
            current_status = WorkflowStatus.FAILED
            logger.error(f"[{workflow_run_id}] Error: {error_message}", exc_info=True)
            await self._update_workflow_state(workflow_run_id, {
                "status": current_status.value,
                "current_step": current_step.value if current_step else state.get("current_step"),
                "error": "An unexpected internal error occurred."
            })
            self._emit_task_update(workflow_run_id, workflow_run_id, current_status.value, f"Workflow failed at {failed_step_value}: An unexpected internal error occurred.", result={"failed_step": failed_step_value, "error": "An unexpected internal error occurred."})
            return Event(type=EventType.ERROR, data={"error": "An unexpected internal error occurred.", "stage": failed_step_value, "workflow_run_id": workflow_run_id})


    def _emit_task_update(self, session_id: str, task_id: str, status: str, message: str, result: Optional[Any] = None):
        """Emits a task update event via SocketIO if available and configured."""
        if SOCKETIO_AVAILABLE and self.socketio:
            try:
                update_data = {
                    'task_id': task_id, # Use task_id (workflow_run_id)
                    'status': status,
                    'message': message,
                    'result': result,
                    'timestamp': datetime.now().isoformat()
                }
                # Emit to a specific room or user based on session_id
                self.socketio.emit('workflow_update', update_data, room=session_id) # Assuming 'workflow_update' event and session_id as room
                logger.debug(f"[{task_id}] Emitted SocketIO update for session {session_id}: {status}")
            except Exception as e:
                logger.error(f"[{task_id}] Failed to emit SocketIO update for session {session_id}: {e}", exc_info=True)
        else:
            logger.warning(f"[{task_id}] SocketIO not available or initialized. Cannot emit task update.")


# --- FastAPI Server Setup ---

app = FastAPI(title="WorkflowManagerAgent A2A Server")

# Instantiate the agent (reads env vars internally)
# SocketIO instance needs to be created and passed if used.
# For this standalone A2A server, we pass None for SocketIO.
# Firestore AsyncClient needs to be initialized and passed.
firestore_async_client: Optional[FirestoreAsyncClient] = None
gcp_project_id = os.environ.get(WorkflowManagerAgent.ENV_GCP_PROJECT_ID)
if gcp_project_id:
    try:
        firestore_async_client = firestore.AsyncClient(project=gcp_project_id)
        logger.info("Firestore AsyncClient initialized for WorkflowManagerAgent.")
    except Exception as e:
        logger.error(f"Failed to initialize Firestore AsyncClient: {e}", exc_info=True)
        firestore_async_client = None
else:
    logger.warning(f"{WorkflowManagerAgent.ENV_GCP_PROJECT_ID} not set. Firestore state persistence disabled.")


try:
    # Pass the initialized Firestore client and None for SocketIO
    workflow_manager_agent_instance = WorkflowManagerAgent(
        socketio=None,
        firestore_db=firestore_async_client,
        collection_name=os.environ.get(WorkflowManagerAgent.ENV_FIRESTORE_COLLECTION, "workflow_runs")
    )
except ValueError as e:
    logger.critical(f"Failed to initialize WorkflowManagerAgent: {e}. Server cannot start.", exc_info=True)
    import sys
    sys.exit(f"Agent Initialization Error: {e}")


@app.post("/invoke", response_model=WorkflowManagerOutput) # Define response model
async def invoke_agent(request: WorkflowManagerInput = Body(...)):
    """
    A2A endpoint to invoke the WorkflowManagerAgent.
    Expects JSON body matching WorkflowManagerInput.
    Returns WorkflowManagerOutput on success, or raises HTTPException on error.
    """
    logger.info(f"WorkflowManagerAgent /invoke called for workflow_run_id: {request.workflow_run_id}, topic: {request.initial_topic}")

    # Create InvocationContext for the agent's run_async method
    # Pass the input data directly in context.data
    context_data = request.model_dump(exclude_none=True) # Use exclude_none for optional fields
    # Add invocation_id if not already present (run_async will generate if new workflow)
    if 'workflow_run_id' not in context_data or not context_data['workflow_run_id']:
         # Generate a temporary invocation ID for this specific HTTP call if it's a new workflow
         # The agent's run_async will generate the actual workflow_run_id
         invocation_id = f"invoke-{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(1000,9999)}"
    else:
         # If resuming, use the workflow_run_id as the invocation_id for this call
         invocation_id = request.workflow_run_id

    context = InvocationContext(
        agent_id="workflow-manager-agent",
        invocation_id=invocation_id, # Use the determined invocation_id
        session=InvocationContext.create_session(session_id=request.workflow_run_id or invocation_id), # Use workflow_run_id as session ID if available
        data=context_data # Pass the input data
    )

    try:
        # Call the agent's run_async method
        result_event = await workflow_manager_agent_instance.run_async(context)

        # Process the event returned by run_async
        if result_event and isinstance(result_event.data, dict):
            # Check metadata for status
            event_status = result_event.metadata.get("status")
            if event_status == "error" or result_event.type == EventType.ERROR:
                 error_msg = result_event.data.get("error", "Unknown agent error")
                 error_details = result_event.data.get("details")
                 logger.error(f"WorkflowManagerAgent run_async returned error event: {error_msg}")
                 # Return error response matching WorkflowManagerOutput structure
                 # Ensure the output includes workflow_run_id even on error if known
                 response_payload = WorkflowManagerOutput(
                     workflow_run_id=result_event.data.get("workflow_run_id", request.workflow_run_id or invocation_id),
                     status=WorkflowStatus.FAILED,
                     current_step=result_event.data.get("stage"), # Use 'stage' from error data
                     message=f"Workflow failed: {error_msg}",
                     error=error_msg,
                     result=result_event.data # Include full error data in result for debugging
                 )
                 raise HTTPException(status_code=500, detail=response_payload.model_dump(exclude_none=True))

            else:
                 # Assume success if status is not error
                 logger.info(f"WorkflowManagerAgent returning success result for task {invocation_id}.")
                 # Construct success response matching WorkflowManagerOutput
                 # The result_event.data should contain the final state or result payload
                 # The run_async method is designed to return the final state/result on completion/pause.
                 try:
                     # Attempt to validate the data against the final output model
                     output_payload = WorkflowManagerOutput(**result_event.data)
                     return output_payload
                 except ValidationError as val_err:
                     logger.error(f"Success event data validation failed: {val_err}. Data: {result_event.data}")
                     # Return a generic success with validation error details
                     response_payload = WorkflowManagerOutput(
                         workflow_run_id=result_event.data.get("workflow_run_id", request.workflow_run_id or invocation_id),
                         status=WorkflowStatus(result_event.data.get("status", WorkflowStatus.COMPLETED.value)), # Use status from data
                         current_step=WorkflowStep(result_event.data.get("current_step")) if result_event.data.get("current_step") else None,
                         message="Workflow completed with data validation errors.",
                         error="Output data validation failed.",
                         result={"validation_errors": val_err.errors(), "original_data": result_event.data}
                     )
                     return response_payload # Return 200 OK with error details in payload

        else:
            logger.error(f"WorkflowManagerAgent run_async returned None or invalid event data: {result_event}")
            raise HTTPException(status_code=500, detail=WorkflowManagerOutput(
                workflow_run_id=request.workflow_run_id or invocation_id,
                status=WorkflowStatus.FAILED,
                message="Agent execution failed to return a valid event.",
                error="Agent execution failed to return a valid event."
            ).model_dump(exclude_none=True))

    except HTTPException as http_exc:
        raise http_exc # Re-raise FastAPI exceptions
    except Exception as e:
        logger.error(f"Error during agent invocation: {e}", exc_info=True)
        # Construct error payload consistent with WorkflowManagerOutput
        raise HTTPException(status_code=500, detail=WorkflowManagerOutput(
            workflow_run_id=request.workflow_run_id or invocation_id,
            status=WorkflowStatus.FAILED,
            message=f"Internal server error: {e}",
            error=f"Internal server error: {e}"
        ).model_dump(exclude_none=True))

@app.get("/health")
async def health_check():
    # Add checks for Firestore and agent URLs if needed
    status = "ok"
    if not workflow_manager_agent_instance.db:
        status = "warning: Firestore client not initialized (check GCP_PROJECT_ID)"
    missing_urls = [key for key, url in workflow_manager_agent_instance.agent_urls.items() if not url]
    if missing_urls:
        status = f"warning: Missing agent URLs: {', '.join(missing_urls)}"
    return {"status": status}

# --- Server Shutdown Hook ---
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down WorkflowManagerAgent server...")
    await workflow_manager_agent_instance.close_clients() # Close httpx client
    # Close Firestore client if it was initialized
    if firestore_async_client:
        await firestore_async_client.close()
        logger.info("Firestore AsyncClient closed.")


# --- Main execution block ---

if __name__ == "__main__":
    # Load .env for local development if needed
    try:
        from dotenv import load_dotenv
        if load_dotenv(): logger.info("Loaded .env file for local run.")
        else: logger.info("No .env file found or it was empty.")
    except ImportError: logger.info("dotenv library not found, skipping .env load.")

    parser = argparse.ArgumentParser(description="Run the WorkflowManagerAgent A2A server.")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind the server to.")
    parser.add_argument("--port", type=int, default=8092, help="Port to run the server on.") # Default matches compose
    args = parser.parse_args()

    # Optional: Check for critical env vars before starting server
    # if not os.environ.get(WorkflowManagerAgent.ENV_GCP_PROJECT_ID):
    #      print(f"CRITICAL ERROR: Environment variable {WorkflowManagerAgent.ENV_GCP_PROJECT_ID} must be set.")
    #      import sys
    #      sys.exit(1)
    # Add checks for agent URLs if they are considered critical for startup

    print(f"Starting WorkflowManagerAgent A2A server on {args.host}:{args.port}")

    # Note: SocketIO is not managed by this FastAPI server process.
    # If real-time updates are needed, a separate SocketIO server must be running,
    # and this agent instance must be configured to connect to it.
    # The current implementation passes socketio=None, disabling real-time updates from this process.

    uvicorn.run(app, host=args.host, port=args.port)
