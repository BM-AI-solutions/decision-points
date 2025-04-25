import asyncio
from typing import Any, Dict, List, Optional, Union, Tuple

# Import Google Generative AI
import google.generativeai as genai

from google.adk.agents import LlmAgent # Use only ADK LlmAgent
from google.adk.models import Gemini
from google.adk.tools import ToolContext, tool # Import tool decorator
from google.adk.events import Event, Action, Content, Part
from google.adk.sessions import InvocationContext

# Removed A2A imports

from utils.logger import setup_logger
from app.config import settings # Import centralized settings
# Removed agent_network import - delegation handled via ADK tools

logger = setup_logger('agents.orchestrator_adk') # Renamed logger

# Mapping from logical agent name to the expected ADK agent ID/name
# These names should match the 'name' parameter used when defining the ADK agents
# (e.g., 'web_search_adk' from the refactored web search agent)
ADK_AGENT_TARGETS = {
    "web_search": "web_search_adk",
    "content_generation": "content_generation_adk",
    "market_research": "market_research_adk",
    "improvement": "improvement_adk",
    "branding": "branding_adk",
    "code_generation": "code_generation_adk",
    "deployment": "deployment_adk",
    "marketing": "marketing_adk",
    "lead_generation": "lead_generation_adk",
    "freelance_tasker": "freelance_tasker_adk",
    "workflow_manager": "workflow_manager_adk",
}

class OrchestratorAgentADK(LlmAgent):
    """
    Orchestrator agent refactored to use ADK patterns.
    Handles tasks, interacts with Gemini via ADK model abstraction,
    and delegates to specialized ADK agents using ADK tools.
    """
    websocket_manager: Any # TODO: Replace Any with the actual type

    def __init__(
        self,
        websocket_manager: Any,
        model_name: Optional[str] = None,
        instruction: Optional[str] = None,
        name: str = "orchestrator_adk", # Renamed for clarity
        description: str = "Handles user prompts and orchestrates tasks by delegating to specialized ADK agents.",
        **kwargs: Any,
    ):
        """
        Initializes the ADK-based Orchestrator Agent.

        Args:
            websocket_manager: The WebSocket manager instance (injected dependency).
            model_name: The name of the Gemini model to use. Defaults to settings.GEMINI_MODEL_NAME.
            instruction: Default instruction for the LLM agent. Should guide tool use.
            name: Name of the agent.
            description: Description of the agent.
            **kwargs: Additional arguments for LlmAgent.
        """
        # Determine the model name to use
        effective_model_name = model_name if model_name else settings.GEMINI_MODEL_NAME
        self.model_name = effective_model_name

        # Initialize the ADK Gemini model
        adk_model = Gemini(model=self.model_name)

        # Define default instruction guiding tool use
        if instruction is None:
            instruction = (
                "You are an orchestrator agent. Your goal is to fulfill the user's request. "
                "Analyze the request and determine if it requires specialized capabilities. "
                "Available specialized agents and their functions:\n"
                "- Web Search: Use the 'delegate_web_search' tool for searching the web.\n"
                "- Content Generation: Use 'delegate_content_generation' for creating text content.\n"
                "- Market Research: Use 'delegate_market_research' for market analysis and research.\n"
                "- Improvement Suggestions: Use 'delegate_improvement' for suggesting improvements.\n"
                "- Branding: Use 'delegate_branding' for branding-related tasks.\n"
                "- Code Generation: Use 'delegate_code_generation' for writing code.\n"
                "- Deployment: Use 'delegate_deployment' for deployment tasks.\n"
                "- Marketing: Use 'delegate_marketing' for marketing strategies.\n"
                "- Lead Generation: Use 'delegate_lead_generation' for finding leads.\n"
                "- Freelance Tasking: Use 'delegate_freelance_tasker' for freelance tasks.\n"
                "- Workflow Management: Use 'delegate_workflow_manager' for managing workflows.\n"
                "If the request matches one of these capabilities, use the corresponding tool to delegate the task. "
                "Pass the user's original prompt or relevant parts as input to the tool. "
                "If the request does not require a specialist or you are unsure, handle it directly using your own capabilities."
            )

        # Define tools for delegation
        delegation_tools = [
            self._delegate_web_search,
            self._delegate_content_generation,
            self._delegate_market_research,
            self._delegate_improvement,
            self._delegate_branding,
            self._delegate_code_generation,
            self._delegate_deployment,
            self._delegate_marketing,
            self._delegate_lead_generation,
            self._delegate_freelance_tasker,
            self._delegate_workflow_manager,
        ]

        # Initialize LlmAgent
        super().__init__(
            name=name,
            description=description,
            model=adk_model,
            instruction=instruction,
            tools=delegation_tools, # Pass the delegation tools
            **kwargs
        )

        self.websocket_manager = websocket_manager
        logger.info(f"{self.name} initialized with WebSocket Manager and model: {self.model_name}.")

    # --- Tool Definitions for Delegation ---

    @tool(description="Delegates a web search task to the specialized Web Search agent.")
    async def _delegate_web_search(self, context: ToolContext, query: str) -> Event:
        return await self._delegate_to_agent("web_search", context, {"query": query})

    @tool(description="Delegates a content generation task to the specialized Content Generation agent.")
    async def _delegate_content_generation(self, context: ToolContext, prompt: str) -> Event:
         return await self._delegate_to_agent("content_generation", context, {"prompt": prompt})

    @tool(description="Delegates a market research task to the specialized Market Research agent.")
    async def _delegate_market_research(self, context: ToolContext, research_topic: str) -> Event:
         return await self._delegate_to_agent("market_research", context, {"research_topic": research_topic})

    @tool(description="Delegates an improvement suggestion task to the specialized Improvement agent.")
    async def _delegate_improvement(self, context: ToolContext, area_to_improve: str) -> Event:
         return await self._delegate_to_agent("improvement", context, {"area_to_improve": area_to_improve})

    @tool(description="Delegates a branding task to the specialized Branding agent.")
    async def _delegate_branding(self, context: ToolContext, branding_request: str) -> Event:
         return await self._delegate_to_agent("branding", context, {"branding_request": branding_request})

    @tool(description="Delegates a code generation task to the specialized Code Generation agent.")
    async def _delegate_code_generation(self, context: ToolContext, code_description: str) -> Event:
         return await self._delegate_to_agent("code_generation", context, {"code_description": code_description})

    @tool(description="Delegates a deployment task to the specialized Deployment agent.")
    async def _delegate_deployment(self, context: ToolContext, deployment_details: str) -> Event:
         return await self._delegate_to_agent("deployment", context, {"deployment_details": deployment_details})

    @tool(description="Delegates a marketing task to the specialized Marketing agent.")
    async def _delegate_marketing(self, context: ToolContext, marketing_goal: str) -> Event:
         return await self._delegate_to_agent("marketing", context, {"marketing_goal": marketing_goal})

    @tool(description="Delegates a lead generation task to the specialized Lead Generation agent.")
    async def _delegate_lead_generation(self, context: ToolContext, lead_criteria: str) -> Event:
         return await self._delegate_to_agent("lead_generation", context, {"lead_criteria": lead_criteria})

    @tool(description="Delegates a freelance task to the specialized Freelance Tasker agent.")
    async def _delegate_freelance_tasker(self, context: ToolContext, task_description: str) -> Event:
         return await self._delegate_to_agent("freelance_tasker", context, {"task_description": task_description})

    @tool(description="Delegates a workflow management task to the specialized Workflow Manager agent.")
    async def _delegate_workflow_manager(self, context: ToolContext, workflow_request: str) -> Event:
         return await self._delegate_to_agent("workflow_manager", context, {"workflow_request": workflow_request})

    # --- Helper for Delegation ---

    async def _delegate_to_agent(self, logical_agent_name: str, context: ToolContext, input_data: Dict[str, Any]) -> Event:
        """Helper function to invoke a target ADK agent."""
        task_id = context.session.id # Use session ID for tracking
        target_adk_agent_id = ADK_AGENT_TARGETS.get(logical_agent_name)

        if not target_adk_agent_id:
            error_msg = f"No ADK target configured for logical agent name: {logical_agent_name}"
            logger.error(error_msg)
            return self._create_error_event(error_msg)

        logger.info(f"Task {task_id}: Orchestrator delegating to {logical_agent_name} (ADK ID: {target_adk_agent_id}) with input: {input_data}")

        # Send WebSocket update
        if self.websocket_manager:
            # Use context.session.id for task tracking if available
            self.websocket_manager.broadcast(task_id, {
                'status': 'delegating',
                'agent': logical_agent_name,
                'message': f"Delegating task to {logical_agent_name}..."
            })

        # Create input event for the target agent
        input_event = Event(data=input_data)

        try:
            # Use context.invoke_agent to call the target ADK agent
            response_event = await context.invoke_agent(
                target_agent_id=target_adk_agent_id,
                input=input_event,
                timeout_seconds=settings.AGENT_TIMEOUT_SECONDS # Use appropriate timeout
            )
            logger.info(f"Task {task_id}: Received response from {target_adk_agent_id}")

            # Send WebSocket update (optional: could parse response_event)
            if self.websocket_manager:
                 self.websocket_manager.broadcast(task_id, {
                     'status': 'completed_delegation',
                     'agent': logical_agent_name,
                     'message': f"Received result from {logical_agent_name}",
                     # 'result': self._extract_text_from_event(response_event) # Example
                 })

            # Return the event received from the target agent
            # The orchestrator's LLM will process this tool output
            return response_event

        except Exception as e:
            error_msg = f"Task {task_id}: Error invoking {target_adk_agent_id}: {e}"
            logger.error(error_msg, exc_info=True)
            # Send WebSocket update
            if self.websocket_manager:
                 self.websocket_manager.broadcast(task_id, {
                     'status': 'failed_delegation',
                     'agent': logical_agent_name,
                     'message': error_msg
                 })
            return self._create_error_event(error_msg)

    # --- Main ADK Entry Point ---

    async def run_async(self, context: InvocationContext) -> Event:
        """
        Processes a task using ADK LlmAgent capabilities, potentially using tools for delegation.

        Args:
            context: The invocation context containing session and input event.

        Returns:
            The final event containing the result or error.
        """
        task_id = context.session.id
        input_event = context.input_event
        prompt = self._extract_text_from_event(input_event, "No prompt provided")

        logger.info(f"{self.name} received ADK task {task_id} with prompt: '{prompt}'")

        # Send initial WebSocket update
        if self.websocket_manager:
            self.websocket_manager.broadcast(task_id, {
                'status': 'processing',
                'agent': self.name,
                'message': f"Orchestrator processing prompt..."
            })

        try:
            # Let the LlmAgent handle the invocation, which includes deciding
            # whether to call a tool (delegate) or respond directly.
            # The super().run_async handles the LLM call and tool execution flow.
            final_event = await super().run_async(context)

            result_text = self._extract_text_from_event(final_event)
            logger.info(f"Task {task_id}: Orchestration completed. Final result: '{result_text[:100]}...'")

            # Send final WebSocket update
            if self.websocket_manager:
                self.websocket_manager.broadcast(task_id, {
                    'status': 'completed',
                    'agent': self.name,
                    'message': "Orchestration complete.",
                    'result': result_text
                })

            return final_event

        except Exception as e:
            error_message = f"Orchestration failed: {str(e)}"
            logger.error(f"Task {task_id} failed: {error_message}", exc_info=True)
            # Send WebSocket update
            if self.websocket_manager:
                 self.websocket_manager.broadcast(task_id, {
                     'status': 'failed',
                     'message': error_message
                 })
            return self._create_error_event(error_message, input_event)

    # --- Helper Methods ---

    def _extract_text_from_event(self, event: Event, default_text: str = "") -> str:
        """Extracts the first text part from an event's actions."""
        if event and event.actions and event.actions[0].content and event.actions[0].content.parts:
            text_parts = [p.text for p in event.actions[0].content.parts if hasattr(p, 'text')]
            if text_parts:
                return text_parts[0]
        # Fallback for tool output events which might be directly in actions[0].parts
        elif event and event.actions and event.actions[0].parts:
             text_parts = [p.text for p in event.actions[0].parts if hasattr(p, 'text')]
             if text_parts:
                 return text_parts[0]
        logger.warning(f"Could not extract text from event: {event}")
        return default_text


    def _create_error_event(self, error_message: str, input_event: Optional[Event] = None) -> Event:
         """Creates a standard error event."""
         # Ensure error message is a string
         error_text = str(error_message)
         error_part = Part(text=f"Error: {error_text}")
         error_action = Action(content=Content(parts=[error_part]))
         # Use invocation_id from the original input if available
         invocation_id = getattr(input_event, 'invocation_id', None) if input_event else None
         # Ensure author is set
         return Event(author=self.name, actions=[error_action], invocation_id=invocation_id)

# Instantiate the agent (assuming websocket_manager is provided elsewhere)
# This instance will be discovered by `adk web` if this file is in the target directory
# Example instantiation (replace None with actual manager):
# websocket_manager_instance = None # Provide your WebSocketManager instance here
# agent = OrchestratorAgentADK(websocket_manager=websocket_manager_instance)
