"""
Base Agent Class for Specialized Agents.

This module provides a base class for all specialized agents to inherit from,
implementing common functionality for A2A protocol and ADK integration.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional, Union

from google.adk.agents import LlmAgent
from google.adk.models import Gemini, BaseLlm
from google.adk.events import Event, Action, Content, Part
from google.adk.sessions import InvocationContext

from python_a2a import A2AServer, agent, skill, run_server
from python_a2a import TaskStatus, TaskState, Message, TextContent, MessageRole

from app.config import settings

logger = logging.getLogger(__name__)

class BaseSpecializedAgent(A2AServer, LlmAgent):
    """
    Base class for all specialized agents.
    
    Implements common functionality for A2A protocol and ADK integration.
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
        
        # Initialize LlmAgent
        LlmAgent.__init__(
            self,
            name=name,
            description=description,
            model=adk_model,
            instruction=instruction,
            **kwargs
        )
        
        self.port = port
        logger.info(f"{self.name} initialized with model: {self.model_name}")
    
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
        
        Args:
            task: The task to handle.
            prompt: The prompt to process.
        """
        try:
            # Create a message for the LLM
            message = Message(
                content=TextContent(text=prompt),
                role=MessageRole.USER
            )
            
            # Get response from LLM
            response = await self.handle_message(message)
            result = response.content.text
            
            # Update the task with the result
            task.artifacts = [{
                "parts": [{"type": "text", "text": result}]
            }]
            task.status = TaskStatus(state=TaskState.COMPLETED)
        except Exception as e:
            error_message = f"Task processing failed: {str(e)}"
            logger.error(f"Task handling failed: {error_message}", exc_info=True)
            
            task.artifacts = [{
                "parts": [{"type": "text", "text": f"Error: {error_message}"}]
            }]
            task.status = TaskStatus(state=TaskState.FAILED)
    
    async def run_async(self, context: InvocationContext) -> Event:
        """
        Process a task using ADK patterns.
        
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
            # Create a message for the LLM
            message = Message(
                content=TextContent(text=prompt),
                role=MessageRole.USER
            )
            
            # Get response from LLM
            response = await self.handle_message(message)
            result = response.content.text
            
            # Create an output event
            output_action = Action(content=Content(parts=[Part(text=result)]))
            return Event(author=self.name, actions=[output_action], invocation_id=input_event.invocation_id)
        except Exception as e:
            error_message = f"Task processing failed: {str(e)}"
            logger.error(f"Task {task_id} failed: {error_message}", exc_info=True)
            
            # Create an error event
            error_action = Action(content=Content(parts=[Part(text=f"Error: {error_message}")]))
            return Event(author=self.name, actions=[error_action], invocation_id=input_event.invocation_id)
    
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
