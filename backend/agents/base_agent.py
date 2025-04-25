"""
Base Agent Class for Specialized Agents.

This module provides a base class for all specialized agents to inherit from,
implementing common functionality for A2A protocol and ADK integration.
Uses PostgreSQL for state persistence.
"""

import asyncio
import logging
import json
import uuid
from typing import Any, Dict, List, Optional, Union

import google.generativeai as genai
from pydantic import BaseModel

from google.adk.agents import LlmAgent
from google.adk.models import Gemini, BaseLlm
from google.adk.events import Event, Action, Content, Part
from google.adk.sessions import InvocationContext, DatabaseSessionService

from python_a2a import A2AServer, agent, skill, run_server
from python_a2a import TaskStatus, TaskState, Message, TextContent, MessageRole

from app.config import settings
from app.services.db_service import DatabaseService

logger = logging.getLogger(__name__)

class BaseSpecializedAgent(A2AServer, LlmAgent):
    """
    Base class for all specialized agents.

    Implements common functionality for A2A protocol and ADK integration.
    Uses PostgreSQL for state persistence via DatabaseService.
    """

    def __init__(
        self,
        name: str,
        description: str,
        model_name: Optional[str] = None,
        instruction: Optional[str] = None,
        port: Optional[int] = None,
        **kwargs: Any,
    ):
        """
        Initialize the base specialized agent.

        Args:
            name: The name of the agent.
            description: The description of the agent.
            model_name: The name of the model to use. Defaults to settings.GEMINI_MODEL_NAME.
            instruction: The instruction for the agent. Defaults to None.
            port: The port to run the A2A server on. Defaults to None.
            **kwargs: Additional arguments for LlmAgent.
        """
        # Initialize A2AServer
        A2AServer.__init__(self)

        # Determine the model name to use
        effective_model_name = model_name if model_name else settings.GEMINI_MODEL_NAME
        self.model_name = effective_model_name

        # Initialize the ADK Gemini model
        adk_model = Gemini(model=self.model_name)

        # Set up PostgreSQL session service for ADK
        db_url = settings.DATABASE_URL
        session_service = DatabaseSessionService(db_url=db_url)

        # Initialize LlmAgent with session service
        LlmAgent.__init__(
            self,
            name=name,
            description=description,
            model=adk_model,
            instruction=instruction,
            session_service=session_service,
            **kwargs
        )

        # Also initialize direct Gemini access for more control
        try:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.gemini_model = genai.GenerativeModel(
                self.model_name,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                )
            )
            logger.info(f"Direct Gemini model {self.model_name} initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize direct Gemini model: {e}")
            self.gemini_model = None

        # Initialize database service for A2A state persistence
        self.db_service = DatabaseService()

        self.port = port
        logger.info(f"{self.name} initialized with model: {self.model_name} and PostgreSQL persistence")

    async def generate_response(self, prompt: str, **kwargs) -> str:
        """
        Generate a response using the Gemini model.

        Args:
            prompt: The prompt to send to the model.
            **kwargs: Additional arguments to pass to the model.

        Returns:
            The generated response as a string.
        """
        if not self.gemini_model:
            raise ValueError("Gemini model not initialized")

        try:
            response = await self.gemini_model.generate_content_async(
                prompt,
                **kwargs
            )
            return response.text
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise

    def handle_task(self, task):
        """
        Handle a task using A2A protocol.

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
        Handle a task asynchronously using A2A protocol.
        Uses PostgreSQL for state persistence.

        Args:
            task: The task to handle.
            prompt: The prompt to process.
        """
        # Generate a task ID if not present
        task_id = getattr(task, 'id', str(uuid.uuid4()))
        user_id = "default_user"  # This should be extracted from the task or context in a real implementation

        try:
            # Create a task record in the database
            await self.create_agent_task(
                task_id=task_id,
                user_identifier=user_id,
                task_type="prompt_processing",
                input_data={"prompt": prompt}
            )

            # Update task status to started
            await self.update_agent_task(
                task_id=task_id,
                status="RUNNING",
                started=True
            )

            # Add the instruction to the prompt
            full_prompt = f"{self.instruction}\n\nUser request: {prompt}"

            # Generate response using Gemini
            result = await self.generate_response(full_prompt)

            # Update the task in the database
            await self.update_agent_task(
                task_id=task_id,
                status="COMPLETED",
                result_data={"response": result},
                completed=True
            )

            # Update the task with the result
            task.artifacts = [{
                "parts": [{"type": "text", "text": result}]
            }]
            task.status = TaskStatus(state=TaskState.COMPLETED)
        except Exception as e:
            error_message = f"Task processing failed: {str(e)}"
            logger.error(f"Task handling failed: {error_message}", exc_info=True)

            # Update the task in the database with error
            await self.update_agent_task(
                task_id=task_id,
                status="FAILED",
                error=error_message,
                completed=True
            )

            task.artifacts = [{
                "parts": [{"type": "text", "text": f"Error: {error_message}"}]
            }]
            task.status = TaskStatus(state=TaskState.FAILED)

    async def run_async(self, context: InvocationContext) -> Event:
        """
        Process a task using ADK patterns.
        Uses PostgreSQL for state persistence.

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

        # Extract user ID from context if available, otherwise use a default
        user_id = getattr(context.session, 'user_id', "default_user")

        logger.info(f"{self.name} received ADK task {task_id} with prompt: '{prompt}'")

        try:
            # Create a task record in the database
            await self.create_agent_task(
                task_id=str(task_id),
                user_identifier=user_id,
                task_type="adk_prompt_processing",
                input_data={"prompt": prompt}
            )

            # Update task status to started
            await self.update_agent_task(
                task_id=str(task_id),
                status="RUNNING",
                started=True
            )

            # Create a message for the LLM
            message = Message(
                content=TextContent(text=prompt),
                role=MessageRole.USER
            )

            # Get response from LLM
            response = await self.handle_message(message)
            result = response.content.text

            # Update the task in the database
            await self.update_agent_task(
                task_id=str(task_id),
                status="COMPLETED",
                result_data={"response": result},
                completed=True
            )

            # Create an output event
            output_action = Action(content=Content(parts=[Part(text=result)]))
            return Event(author=self.name, actions=[output_action], invocation_id=input_event.invocation_id)
        except Exception as e:
            error_message = f"Task processing failed: {str(e)}"
            logger.error(f"Task {task_id} failed: {error_message}", exc_info=True)

            # Update the task in the database with error
            await self.update_agent_task(
                task_id=str(task_id),
                status="FAILED",
                error=error_message,
                completed=True
            )

            # Create an error event
            error_action = Action(content=Content(parts=[Part(text=f"Error: {error_message}")]))
            return Event(author=self.name, actions=[error_action], invocation_id=input_event.invocation_id)

    async def get_agent_state(self, user_identifier: str, state_key: str) -> Optional[Dict[str, Any]]:
        """
        Get agent state from PostgreSQL.

        Args:
            user_identifier: The user identifier.
            state_key: The state key.

        Returns:
            The agent state data, or None if not found.
        """
        try:
            return await self.db_service.get_agent_state(
                agent_id=self.name,
                user_identifier=user_identifier,
                state_key=state_key
            )
        except Exception as e:
            logger.error(f"Error getting agent state: {e}")
            return None

    async def update_agent_state(self, user_identifier: str, state_key: str, state_data: Dict[str, Any]) -> bool:
        """
        Update agent state in PostgreSQL.

        Args:
            user_identifier: The user identifier.
            state_key: The state key.
            state_data: The state data.

        Returns:
            True if successful, False otherwise.
        """
        try:
            await self.db_service.update_agent_state(
                agent_id=self.name,
                user_identifier=user_identifier,
                state_key=state_key,
                state_data=state_data
            )
            return True
        except Exception as e:
            logger.error(f"Error updating agent state: {e}")
            return False

    async def create_agent_task(self, task_id: str, user_identifier: str, task_type: str, input_data: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """
        Create a new agent task in PostgreSQL.

        Args:
            task_id: The task ID.
            user_identifier: The user identifier.
            task_type: The type of task.
            input_data: The input data for the task.

        Returns:
            The task ID if successful, None otherwise.
        """
        try:
            task = await self.db_service.create_agent_task(
                task_id=task_id,
                agent_id=self.name,
                user_identifier=user_identifier,
                task_type=task_type,
                input_data=input_data
            )
            return task.id
        except Exception as e:
            logger.error(f"Error creating agent task: {e}")
            return None

    async def update_agent_task(self, task_id: str, status: Optional[str] = None, result_data: Optional[Dict[str, Any]] = None, error: Optional[str] = None, started: bool = False, completed: bool = False) -> bool:
        """
        Update an agent task in PostgreSQL.

        Args:
            task_id: The task ID.
            status: The new status of the task.
            result_data: The result data of the task.
            error: Any error message.
            started: Whether the task has started.
            completed: Whether the task is completed.

        Returns:
            True if successful, False otherwise.
        """
        try:
            await self.db_service.update_agent_task(
                task_id=task_id,
                status=status,
                result_data=result_data,
                error=error,
                started=started,
                completed=completed
            )
            return True
        except Exception as e:
            logger.error(f"Error updating agent task: {e}")
            return False

    def run_server(self, host: str = "0.0.0.0", port: Optional[int] = None):
        """
        Run the A2A server for this agent.

        Args:
            host: The host to bind to.
            port: The port to bind to. Defaults to self.port.
        """
        effective_port = port or self.port
        if not effective_port:
            raise ValueError("Port not specified for A2A server")

        logger.info(f"Starting A2A server for {self.name} on {host}:{effective_port}")
        run_server(self, host=host, port=effective_port)
