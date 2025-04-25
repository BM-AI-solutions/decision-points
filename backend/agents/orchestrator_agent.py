import asyncio
from typing import Any, Dict, List, Optional, Union, Tuple

# TODO: Replace flask_socketio with a FastAPI-compatible WebSocket solution (e.g., using Depends)
from google.ai import generativelanguage as glm

from google.adk.agents import LlmAgent, BaseAgent # Import BaseAgent for type hinting
from google.adk.models import Gemini, BaseLlm
from google.adk.tools import ToolContext
from google.adk.events import Event, EventActions, Action, Content, Part
from google.adk.sessions import InvocationContext

from python_a2a import A2AServer, agent, skill, run_server
from python_a2a import TaskStatus, TaskState, Message, TextContent, MessageRole
from python_a2a import StreamingClient

from utils.logger import setup_logger
from app.config import settings # Import centralized settings
from agents.agent_network import agent_network # Import the agent network singleton

logger = setup_logger('agents.orchestrator')

@agent(
    name="OrchestratorAgent",
    description="Handles user prompts and orchestrates tasks, potentially delegating to specialized agents.",
    version="1.0.0"
)
class OrchestratorAgent(A2AServer, LlmAgent):
    """
    Orchestrator agent refactored to use both ADK and A2A patterns.
    Handles tasks, interacts with Gemini via ADK model abstraction,
    and delegates to specialized agents using A2A protocol.
    """
    websocket_manager: Any # TODO: Replace Any with the actual type of your WebSocket manager dependency

    def __init__(
        self,
        websocket_manager: Any, # Changed from socketio: SocketIO
        agent_ids: Dict[str, str],
        model_name: Optional[str] = None, # Changed from 'model' to 'model_name'
        instruction: Optional[str] = None,
        name: str = "OrchestratorAgent",
        description: str = "Handles user prompts and orchestrates tasks, potentially delegating to specialized agents.",
        **kwargs: Any,
    ):
        """
        Initializes the ADK-based Orchestrator Agent with A2A protocol support.

        Args:
            websocket_manager: The WebSocket manager instance (injected dependency).
            agent_ids: A dictionary mapping logical agent names (e.g., 'market_analyzer') to their ADK agent IDs.
            model_name: The name of the Gemini model to use (e.g., 'gemini-2.5-pro-preview-03-25').
                         Defaults to a suitable model for orchestration if None.
            instruction: Default instruction for the LLM agent.
            name: Name of the agent.
            description: Description of the agent.
            **kwargs: Additional arguments for LlmAgent.
        """
        # Initialize A2AServer
        A2AServer.__init__(self)

        # Determine the model name to use
        effective_model_name = model_name if model_name else settings.GEMINI_MODEL_NAME
        self.model_name = effective_model_name # Store the actual model name used

        # Initialize the ADK Gemini model
        adk_model = Gemini(model=self.model_name)

        # Ensure instruction is provided, even if basic
        if instruction is None:
            instruction = "Process the user's request and delegate to specialized agents when appropriate."

        # Initialize LlmAgent
        LlmAgent.__init__(
            self,
            name=name,
            description=description,
            model=adk_model, # Pass the initialized ADK model object
            instruction=instruction,
            **kwargs
        )

        self.websocket_manager = websocket_manager # Changed from self.socketio = socketio
        self.agent_ids = agent_ids # Store the agent IDs dictionary

        # Initialize the agent network router with self as the LLM client
        # This allows the router to use this agent's LLM for routing decisions
        self.a2a_client = StreamingClient(f"http://localhost:{settings.A2A_ORCHESTRATOR_PORT}")
        agent_network.initialize_router(self.a2a_client)

        # Use self.model_name which holds the string name, self.model.model also works if super().__init__ sets it
        logger.info(f"{self.name} initialized with WebSocket Manager, model: {self.model_name}, and agent IDs: {list(self.agent_ids.keys())}.")

    @skill(
        name="orchestrate",
        description="Orchestrate a task, potentially delegating to specialized agents",
        tags=["orchestration", "delegation"]
    )
    async def orchestrate(self, prompt: str) -> str:
        """
        Orchestrates a task using A2A protocol, potentially delegating to specialized agents.

        Args:
            prompt: The user's prompt to orchestrate.

        Returns:
            The result of the orchestration.
        """
        task_id = f"task-{id(prompt)}"
        logger.info(f"{self.name} received task {task_id} with prompt: '{prompt}'")

        # Use the agent network to route the query
        target_agent_name, confidence = agent_network.route_query(prompt)

        if target_agent_name != "orchestrator" and confidence > 0.7:
            # Delegate to specialized agent
            logger.info(f"Task {task_id} routed to {target_agent_name} with {confidence:.2f} confidence")

            # Send WebSocket update
            if self.websocket_manager:
                self.websocket_manager.broadcast(task_id, {
                    'status': 'delegating',
                    'agent': target_agent_name,
                    'message': f"Delegating task to {target_agent_name}..."
                })

            try:
                # Get the agent client
                agent_client = agent_network.get_agent(target_agent_name)
                if not agent_client:
                    raise ValueError(f"Agent '{target_agent_name}' not found in network")

                # Invoke the agent's skill
                response = await agent_client.ask(prompt)

                # Send WebSocket update
                if self.websocket_manager:
                    self.websocket_manager.broadcast(task_id, {
                        'status': 'completed',
                        'agent': target_agent_name,
                        'message': f"Task completed by {target_agent_name}",
                        'result': response
                    })

                return response
            except Exception as e:
                error_message = f"Delegation to {target_agent_name} failed: {str(e)}"
                logger.error(f"Task {task_id} delegation failed: {error_message}", exc_info=True)

                # Send WebSocket update
                if self.websocket_manager:
                    self.websocket_manager.broadcast(task_id, {
                        'status': 'failed',
                        'message': error_message
                    })

                return f"Error: {error_message}"
        else:
            # Handle directly by orchestrator
            logger.info(f"Task {task_id} handled directly by orchestrator (confidence: {confidence:.2f})")

            # Send WebSocket update
            if self.websocket_manager:
                self.websocket_manager.broadcast(task_id, {
                    'status': 'processing',
                    'message': f"Processing task with {self.model_name}..."
                })

            try:
                # Create a message for the LLM
                message = Message(
                    content=TextContent(text=prompt),
                    role=MessageRole.USER
                )

                # Get response from LLM
                response = await self.handle_message(message)
                result = response.content.text

                # Send WebSocket update
                if self.websocket_manager:
                    self.websocket_manager.broadcast(task_id, {
                        'status': 'completed',
                        'message': "Task completed by orchestrator",
                        'result': result
                    })

                return result
            except Exception as e:
                error_message = f"Orchestrator processing failed: {str(e)}"
                logger.error(f"Task {task_id} failed: {error_message}", exc_info=True)

                # Send WebSocket update
                if self.websocket_manager:
                    self.websocket_manager.broadcast(task_id, {
                        'status': 'failed',
                        'message': error_message
                    })

                return f"Error: {error_message}"

    async def run_async(self, context: InvocationContext) -> Event:
        """
        Processes a task using ADK patterns and emits updates via SocketIO.
        This method is maintained for backward compatibility with ADK.

        Args:
            context: The invocation context containing session and input event.

        Returns:
            The final event containing the result or error.
        """
        task_id = context.session.id
        input_event = context.input_event
        prompt = "No prompt provided"
        if input_event.actions and input_event.actions[0].parts:
            # Assuming the prompt is the first text part of the first action
            text_parts = [p.text for p in input_event.actions[0].parts if p.type == 'text']
            if text_parts:
                prompt = text_parts[0]

        logger.info(f"{self.name} received ADK task {task_id} with prompt: '{prompt}'")

        try:
            # Use the orchestrate skill
            result = await self.orchestrate(prompt)

            # Create an output event
            output_action = Action(content=Content(parts=[Part(text=result)]))
            return Event(author=self.name, actions=[output_action], invocation_id=input_event.invocation_id)
        except Exception as e:
            error_message = f"Orchestration failed: {str(e)}"
            logger.error(f"Task {task_id} failed: {error_message}", exc_info=True)
            return self._create_error_event(error_message, input_event)

    def handle_task(self, task):
        """
        Handles a task using A2A protocol.

        Args:
            task: The task to handle.

        Returns:
            The updated task with results.
        """
        # Extract message from task
        message_data = task.message or {}
        content = message_data.get("content", {})
        prompt = content.get("text", "") if isinstance(content, dict) else ""

        if not prompt:
            task.status = TaskStatus(
                state=TaskState.INPUT_REQUIRED,
                message={"role": "agent", "content": {"type": "text", "text": "Please provide a prompt."}}
            )
            return task

        # Create a task for async execution
        asyncio.create_task(self._handle_task_async(task, prompt))

        # Return the task with pending status
        task.status = TaskStatus(state=TaskState.PENDING)
        return task

    async def _handle_task_async(self, task, prompt):
        """
        Handles a task asynchronously using A2A protocol.

        Args:
            task: The task to handle.
            prompt: The prompt to process.
        """
        try:
            # Use the orchestrate skill
            result = await self.orchestrate(prompt)

            # Update the task with the result
            task.artifacts = [{
                "parts": [{"type": "text", "text": result}]
            }]
            task.status = TaskStatus(state=TaskState.COMPLETED)
        except Exception as e:
            error_message = f"Orchestration failed: {str(e)}"
            logger.error(f"Task handling failed: {error_message}", exc_info=True)

            task.artifacts = [{
                "parts": [{"type": "text", "text": f"Error: {error_message}"}]
            }]
            task.status = TaskStatus(state=TaskState.FAILED)


    def _extract_text_from_event(self, event: Event, default_text: str = "") -> str:
        """Extracts the first text part from an event's actions."""
        if event and event.actions and event.actions[0].parts:
            text_parts = [p.text for p in event.actions[0].parts if p.type == 'text']
            if text_parts:
                return text_parts[0]
        return default_text

    def _create_error_event(self, error_message: str, input_event: Optional[Event] = None) -> Event:
         """Creates a standard error event."""
         error_action = Action(content=Content(parts=[Part(text=f"Error: {error_message}")]))
         invocation_id = getattr(input_event, 'invocation_id', None) if input_event else None
         return Event(author=self.name, actions=[error_action], invocation_id=invocation_id)

    def run_server(self, host: str = "0.0.0.0", port: Optional[int] = None):
        """
        Run the A2A server for this agent.

        Args:
            host: The host to bind to.
            port: The port to bind to. Defaults to settings.A2A_ORCHESTRATOR_PORT.
        """
        effective_port = port or settings.A2A_ORCHESTRATOR_PORT
        logger.info(f"Starting A2A server for {self.name} on {host}:{effective_port}")
        run_server(self, host=host, port=effective_port)
