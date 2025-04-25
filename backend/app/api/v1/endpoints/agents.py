import asyncio
import logging
import uuid
import os # Added for environment variables
import httpx # Added for A2A HTTP calls
from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel, Field # Ensure Field is imported

# Assuming shared schema file exists and contains necessary models
# from backend.app.schemas.agents import OrchestratorInput, OrchestratorOutput, OrchestratorErrorOutput
# Define minimal models here if shared file is not available or for clarity
class OrchestratorInput(BaseModel):
    prompt: str
    session_id: str

class OrchestratorOutput(BaseModel):
    status: str
    message: str
    result: Optional[Any] = None
    agent: Optional[str] = None
    task_id: str

class OrchestratorErrorOutput(BaseModel):
    error: str
    details: Optional[Any] = None


# Assuming SocketIO is still used for real-time updates from the backend API server
# from app.main import sio # Import the initialized SocketIO server (if running in this process)
# If SocketIO is managed externally, the agent might emit directly or updates are polled.
# For this refactor, we assume SocketIO is handled elsewhere or not directly by this API endpoint.
# Keep the import and handlers commented out if they were for a different setup.
# try:
#     from app.main import sio # Import the initialized SocketIO server
#     SOCKETIO_AVAILABLE = True
# except ImportError:
#     SOCKETIO_AVAILABLE = False
#     sio = None # Define as None if not available


logger = logging.getLogger(__name__)
router = APIRouter()

# --- Configuration ---
# Get OrchestratorAgent A2A URL from environment variables
ORCHESTRATOR_AGENT_URL = os.environ.get("ORCHESTRATOR_AGENT_URL")
if not ORCHESTRATOR_AGENT_URL:
    logger.error("ORCHESTRATOR_AGENT_URL environment variable is not set. Orchestration will fail.")
    # Decide how to handle this: raise error on startup or handle in endpoint
    # Handling in endpoint allows the server to start even if one agent URL is missing.

# Initialize HTTP client for A2A calls
# Use a global client for efficiency
http_client = httpx.AsyncClient(timeout=180.0) # Increased timeout for potentially long agent tasks

# --- API Models ---
class AgentPrompt(BaseModel):
    """Input model for the /orchestrate endpoint."""
    prompt: str = Field(description="The user's input prompt for the orchestrator.")
    user_id: str = Field(description="The ID of the user session.") # Using user_id as session_id

class OrchestrationResponse(BaseModel):
    """Response model for the /orchestrate endpoint indicating task acceptance."""
    task_id: str = Field(description="The ID assigned to the orchestration task.")
    message: str = Field(description="A message confirming task initiation.")

# --- API Endpoint ---
@router.post("/orchestrate", status_code=status.HTTP_202_ACCEPTED, response_model=OrchestrationResponse)
async def run_orchestration(
    payload: AgentPrompt,
):
    """
    Receives a prompt and initiates the orchestration process by calling the OrchestratorAgent A2A endpoint.
    Returns a response indicating the task was accepted.
    """
    # Generate a unique task ID for this request
    task_id = str(uuid.uuid4())
    logger.info(f"Received orchestration request. Task ID: {task_id}, User ID: {payload.user_id}, Prompt: '{payload.prompt}'")

    if not ORCHESTRATOR_AGENT_URL:
        error_msg = "OrchestratorAgent URL is not configured."
        logger.error(f"Task ID: {task_id} - {error_msg}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"error": error_msg, "task_id": task_id}
        )

    # Prepare the payload for the OrchestratorAgent's /invoke endpoint
    # The OrchestratorAgent expects OrchestratorInput: { "prompt": "...", "session_id": "..." }
    orchestrator_payload = OrchestratorInput(
        prompt=payload.prompt,
        session_id=payload.user_id # Map user_id to session_id for the agent
    ).model_dump() # Use model_dump for Pydantic v2 serialization

    # Construct the full URL for the OrchestratorAgent's invoke endpoint
    invoke_url = f"{ORCHESTRATOR_AGENT_URL.rstrip('/')}/invoke"

    try:
        logger.info(f"Task ID: {task_id} - Calling OrchestratorAgent A2A endpoint: {invoke_url}")
        # Make the asynchronous HTTP POST request
        response = await http_client.post(
            invoke_url,
            json=orchestrator_payload,
            # Add headers if needed (e.g., API key for agent-to-agent auth)
            # headers={"X-Agent-Auth": "..."}
        )

        # Raise an exception for bad status codes (4xx or 5xx)
        response.raise_for_status()

        # Assuming the OrchestratorAgent returns a success response (2xx)
        # The response body might contain the initial status or task ID from the agent.
        # The detailed workflow progress/result will likely come via SocketIO or polling.
        # We can optionally parse the response body if it contains useful info,
        # but the primary goal of this endpoint is just to initiate the task.

        # Let's parse the response body to get the agent's task ID if available
        # Assuming the agent's success response matches OrchestratorOutput structure
        try:
            agent_response_data = response.json()
            # Validate against the expected output model
            orchestrator_output = OrchestratorOutput(**agent_response_data)
            agent_task_id = orchestrator_output.task_id # Get the task ID from the agent's response
            logger.info(f"Task ID: {task_id} - OrchestratorAgent accepted task. Agent Task ID: {agent_task_id}")
        except (json.JSONDecodeError, ValidationError) as e:
            logger.warning(f"Task ID: {task_id} - Failed to parse or validate OrchestratorAgent response body: {e}. Response: {response.text}", exc_info=True)
            # Use a fallback task ID if parsing fails
            agent_task_id = task_id # Fallback to the API's task ID

        # Return the acceptance response
        return OrchestrationResponse(
            task_id=agent_task_id, # Return the agent's task ID if available, else API's ID
            message="Orchestration task accepted and initiated by OrchestratorAgent."
        )

    except httpx.HTTPStatusError as e:
        # Handle HTTP errors from the OrchestratorAgent
        error_details = {"status_code": e.response.status_code, "response_text": e.response.text}
        try:
            # Attempt to parse error details from the response body if it's JSON
            error_details["response_json"] = e.response.json()
            # If the agent returned a structured error (OrchestratorErrorOutput), use its details
            if isinstance(error_details["response_json"], dict) and "error" in error_details["response_json"]:
                 agent_error = OrchestratorErrorOutput(**error_details["response_json"])
                 error_message = f"OrchestratorAgent Error: {agent_error.error}"
                 detail_payload = agent_error.model_dump(exclude_none=True)
            else:
                 # Generic HTTP error message
                 error_message = f"OrchestratorAgent HTTP Error: {e.response.status_code}"
                 detail_payload = error_details
        except json.JSONDecodeError:
            # Response was not JSON
            error_message = f"OrchestratorAgent HTTP Error: {e.response.status_code}"
            detail_payload = error_details

        logger.error(f"Task ID: {task_id} - {error_message}", exc_info=True)
        raise HTTPException(
            status_code=e.response.status_code, # Use the status code from the agent's response
            detail=detail_payload
        )
    except httpx.RequestError as e:
        # Handle network or request errors when calling the agent
        error_message = f"Failed to connect to OrchestratorAgent: {str(e)}"
        logger.error(f"Task ID: {task_id} - {error_message}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"error": error_message, "task_id": task_id}
        )
    except Exception as e:
        # Handle any other unexpected errors
        error_message = f"An unexpected error occurred while calling OrchestratorAgent: {str(e)}"
        logger.error(f"Task ID: {task_id} - {error_message}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": error_message, "task_id": task_id}
        )

# --- Socket.IO Event Handlers (Keep if needed for frontend communication) ---
# These handlers are part of the main FastAPI application's SocketIO server (if configured).
# They are separate from the agent's internal A2A communication.
# If the main app uses SocketIO, these handlers might be needed to manage frontend connections
# and potentially relay updates received from agents (e.g., via a message queue or polling).

# @sio.event
# async def connect(sid, environ):
#     logger.info(f"Socket.IO client connected: {sid}")

# @sio.event
# async def disconnect(sid):
#     logger.info(f"Socket.IO client disconnected: {sid}")

# @sio.event
# async def join_task_room(sid, data):
#     task_id = data.get('task_id')
#     if task_id:
#         logger.info(f"Client {sid} joining room for task {task_id}")
#         sio.enter_room(sid, task_id)

# --- Server Shutdown Hook (Optional, for the API's HTTP client) ---
# This is for the httpx client used by this API endpoint, not the agent's internal client.
@router.on_event("shutdown")
async def shutdown_http_client():
    logger.info("Closing API endpoint HTTP client...")
    await http_client.aclose()
    logger.info("API endpoint HTTP client closed.")