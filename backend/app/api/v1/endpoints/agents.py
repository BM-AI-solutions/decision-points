import asyncio
import logging
import uuid
from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel

# Import necessary components from ADK and A2A
from google.adk.events import Event, Action, Content, Part
from google.adk.sessions import InvocationContext

from python_a2a import Message, TextContent, MessageRole

from app.core.socketio import sio # Import the initialized SocketIO server
from app.config import settings
from agents.orchestrator_agent import OrchestratorAgent
from agents.agent_network import agent_network

logger = logging.getLogger(__name__)
router = APIRouter()

# --- Agent Instantiation ---
# Simple global instance for now. Consider dependency injection for better management.
orchestrator_agent_instance: OrchestratorAgent | None = None

def get_orchestrator_agent() -> OrchestratorAgent:
    """Gets the singleton OrchestratorAgent instance."""
    global orchestrator_agent_instance
    if orchestrator_agent_instance is None:
        # Define the agent IDs mapping using settings
        agent_ids = {
            "web_searcher": settings.AGENT_WEB_SEARCH_ID,
            "content_generator": settings.CONTENT_GENERATION_AGENT_ID,
            "market_research": settings.MARKET_RESEARCH_AGENT_ID,
            "improvement": settings.IMPROVEMENT_AGENT_ID,
            "branding": settings.BRANDING_AGENT_ID,
            "code_generation": settings.CODE_GENERATION_AGENT_ID,
            "deployment": settings.DEPLOYMENT_AGENT_ID,
            "marketing": settings.MARKETING_AGENT_ID,
            "lead_generator": settings.LEAD_GENERATION_AGENT_ID,
            "freelance_tasker": settings.FREELANCE_TASKER_AGENT_ID,
            "workflow_manager": settings.WORKFLOW_MANAGER_AGENT_ID,
        }
        # Filter out None values in case some IDs are not set
        filtered_agent_ids = {k: v for k, v in agent_ids.items() if v is not None}

        # Create a WebSocket manager class that wraps the SocketIO instance
        class WebSocketManager:
            def __init__(self, sio_instance):
                self.sio = sio_instance

            def broadcast(self, room, data):
                """Broadcast a message to a room."""
                asyncio.create_task(self.sio.emit('agent_update', data, room=room))
                return True

        websocket_manager = WebSocketManager(sio)

        logger.info(f"Instantiating OrchestratorAgent with WebSocket Manager and agent IDs: {filtered_agent_ids}")
        orchestrator_agent_instance = OrchestratorAgent(
            websocket_manager=websocket_manager,
            agent_ids=filtered_agent_ids,
            model_name=settings.GEMINI_MODEL_NAME, # Pass model name from settings
            instruction="Process user requests and delegate to specialized agents when appropriate. Use the agent network for routing."
        )

        # Start the A2A server in a background task
        asyncio.create_task(
            start_a2a_server(orchestrator_agent_instance)
        )

    return orchestrator_agent_instance

async def start_a2a_server(agent: OrchestratorAgent):
    """Start the A2A server for the orchestrator agent."""
    try:
        # Run the server in a separate thread to avoid blocking
        import threading
        server_thread = threading.Thread(
            target=agent.run_server,
            kwargs={"host": "0.0.0.0", "port": settings.A2A_ORCHESTRATOR_PORT}
        )
        server_thread.daemon = True
        server_thread.start()
        logger.info(f"A2A server started for orchestrator agent on port {settings.A2A_ORCHESTRATOR_PORT}")
    except Exception as e:
        logger.error(f"Failed to start A2A server: {e}", exc_info=True)

# --- API Models ---
class AgentPrompt(BaseModel):
    prompt: str
    user_id: str | None = None # Optional user identifier

class OrchestrationResponse(BaseModel):
    task_id: str
    message: str

# --- API Endpoint ---
@router.post("/orchestrate", status_code=status.HTTP_202_ACCEPTED, response_model=OrchestrationResponse)
async def run_orchestration(
    payload: AgentPrompt,
    orchestrator: OrchestratorAgent = Depends(get_orchestrator_agent)
):
    """
    Receives a prompt and initiates the orchestration process via the OrchestratorAgent.
    Uses the A2A protocol for agent communication.
    """
    task_id = str(uuid.uuid4())
    logger.info(f"Received orchestration request. Task ID: {task_id}, Prompt: '{payload.prompt}'")

    # Create a background task to run the orchestration
    async def run_orchestration_task():
        try:
            # Use the orchestrate skill directly
            result = await orchestrator.orchestrate(payload.prompt)
            logger.info(f"Orchestration completed for task {task_id}")
        except Exception as e:
            logger.error(f"Orchestration failed for task {task_id}: {e}", exc_info=True)

    # Start the orchestration task in the background
    logger.info(f"Creating background task for orchestration (Task ID: {task_id})")
    asyncio.create_task(run_orchestration_task())
    logger.info(f"Background task created for Task ID: {task_id}")

    return OrchestrationResponse(
        task_id=task_id,
        message="Orchestration task accepted and initiated."
    )

# --- Socket.IO Event Handlers (Example) ---
@sio.event
async def connect(sid, environ):
    logger.info(f"Socket.IO client connected: {sid}")

@sio.event
async def disconnect(sid):
    logger.info(f"Socket.IO client disconnected: {sid}")

# Add more specific Socket.IO event handlers if needed, e.g., for joining rooms
# @sio.event
# async def join_task_room(sid, data):
#     task_id = data.get('task_id')
#     if task_id:
#         logger.info(f"Client {sid} joining room for task {task_id}")
#         sio.enter_room(sid, task_id)