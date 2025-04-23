import asyncio
from typing import Any, Dict, List, Optional, Union, Tuple

from flask_socketio import SocketIO
import google.generativeai

from google.adk.agents import LlmAgent, BaseAgent # Import BaseAgent for type hinting
from google.adk.models import Gemini, BaseLlm
from google.adk.tools import ToolContext
from google.adk.events import Event, EventActions, Action, Content, Part
from google.adk.sessions import InvocationContext
from utils.logger import setup_logger
from app.config import settings # Import centralized settings

logger = setup_logger('agents.orchestrator')

class OrchestratorAgent(LlmAgent):
    """
    Orchestrator agent refactored to use ADK patterns.
    Handles tasks, interacts with Gemini via ADK model abstraction,
    and emits updates via SocketIO.
    """
    socketio: SocketIO # Add socketio as a class member

    agents: Dict[str, BaseAgent] # Dictionary to hold references to other agents

    def __init__(
        self,
        socketio: SocketIO,
        agent_ids: Dict[str, str], # Add agent IDs parameter
        model_name: Optional[str] = None, # Changed from 'model' to 'model_name'
        instruction: Optional[str] = None,
        name: str = "OrchestratorAgent",
        description: str = "Handles user prompts and orchestrates tasks, potentially delegating to specialized agents.",
        **kwargs: Any,
    ):
        """
        Initializes the ADK-based Orchestrator Agent.

        Args:
            socketio: The Flask-SocketIO instance.
            agent_ids: A dictionary mapping logical agent names (e.g., 'market_analyzer') to their ADK agent IDs.
            model_name: The name of the Gemini model to use (e.g., 'gemini-2.5-pro-preview-03-25').
                        Defaults to a suitable model for orchestration if None.
            instruction: Default instruction for the LLM agent.
            name: Name of the agent.
            description: Description of the agent.
            **kwargs: Additional arguments for LlmAgent.
        """
        # Determine the model name to use
        effective_model_name = model_name if model_name else 'gemini-2.5-pro-preview-03-25' # Default for Orchestrator
        self.model_name = effective_model_name # Store the actual model name used

        # Initialize the ADK Gemini model
        adk_model = Gemini(model=self.model_name)

        # Ensure instruction is provided, even if basic
        if instruction is None:
            instruction = "Process the user's request."

        super().__init__(
            name=name,
            description=description,
            model=adk_model, # Pass the initialized ADK model object
            instruction=instruction,
            **kwargs
        )
        self.socketio = socketio
        self.agent_ids = agent_ids # Store the agent IDs dictionary
        # Use self.model_name which holds the string name, self.model.model also works if super().__init__ sets it
        logger.info(f"{self.name} initialized with SocketIO, model: {self.model_name}, and agent IDs: {list(self.agent_ids.keys())}.")


    async def run_async(self, context: InvocationContext) -> Event:
        """
        Processes a task using ADK patterns and emits updates via SocketIO.

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

        logger.info(f"{self.name} received task {task_id} with prompt: '{prompt}'")

        # --- LLM-based Delegation Logic ---
        target_agent_key, classification_error = await self._classify_intent(prompt, task_id)

        if classification_error:
            # Handle classification error (e.g., log it, maybe default to 'self' or return error)
            logger.error(f"Task {task_id} classification failed: {classification_error}. Defaulting to 'self'.")
            target_agent_key = "self"
            # Optionally emit a specific error update here
            # self.socketio.emit(...)

        target_agent_id = self.agent_ids.get(target_agent_key)

        # --- Handle Delegation or Direct Processing ---
        if target_agent_key != "self" and target_agent_id:
            logger.info(f"Task {task_id} classified for delegation to {target_agent_key}.")
            self.socketio.emit('task_update', {
                'task_id': task_id,
                'status': 'delegating',
                'agent': target_agent_key,
                'message': f"Delegating task to {target_agent_key}..."
            })
            logger.info(f"Emitted 'task_update' (delegating to {target_agent_key}) for task {task_id}")

            try:
                # Prepare context for the delegated agent
                # TODO: Implement more sophisticated parameter extraction if needed later.
                # For now, pass the original context. Specific agents might need tailored metadata.
                delegated_context = self._prepare_delegation_context(context, target_agent_key, prompt)

                # Invoke the target agent skill using ADK A2A
                # Assuming 'run' is the default skill for delegated agents
                delegated_output_event = await context.invoke_skill(
                    target_agent_id=target_agent_id,
                    skill_name="run", # Assuming a default 'run' skill
                    input=delegated_context.input_event,
                    # timeout_seconds=... # Optional: Add timeout if needed
                )

                # Extract result from the delegated agent's response
                delegated_result_text = self._extract_text_from_event(delegated_output_event, f"No text response from {target_agent_key}.")

                # Emit final completion update
                completion_message = f"Task completed by {target_agent.name}."
                self.socketio.emit('task_update', {
                    'task_id': task_id,
                    'status': 'completed',
                    'message': completion_message,
                    'result': delegated_result_text
                })
                logger.info(f"Emitted 'task_update' (completed by {target_agent_key}) for task {task_id}.")
                return delegated_output_event # Return the event from the delegate

            except Exception as e:
                error_message = f"Delegation to {target_agent_key} failed: {str(e)}"
                logger.error(f"Task {task_id} delegation to {target_agent_key} failed: {error_message}", exc_info=True)
                self.socketio.emit('task_update', {
                    'task_id': task_id,
                    'status': 'failed',
                    'message': error_message,
                    'result': None
                })
                logger.info(f"Emitted 'task_update' ({target_agent_key} delegation failed) for task {task_id}")
                return self._create_error_event(error_message, context.input_event)

        else:
            # Handle directly by Orchestrator ('self' or no valid agent found)
            if target_agent_key != "self":
                 logger.warning(f"Task {task_id} classified for '{target_agent_key}', but agent not found or invalid. Handling directly.")
            else:
                 logger.info(f"Task {task_id} classified for 'self'. Handling directly by {self.name}.")

            # Emit initial acknowledgment via SocketIO
            self.socketio.emit('task_update', {
                'task_id': task_id,
                'status': 'submitted',
                'message': f"Task received by Orchestrator: {prompt}"
            })
            logger.info(f"Emitted 'task_update' (submitted by orchestrator) for task {task_id}")

            # Emit processing update
            processing_message = f"Processing prompt with {self.model.model}..."
            self.socketio.emit('task_update', {
                'task_id': task_id,
                'status': 'working',
                'message': processing_message
            })
            logger.info(f"Emitted 'task_update' (working by orchestrator) for task {task_id}")

            try:
                # Execute the core LLM logic using the parent LlmAgent's run_async
                # Use the original context here
                output_event = await super().run_async(context)

                # Extract the result text
                llm_response_text = self._extract_text_from_event(output_event, "No text response generated by orchestrator.")

                # Check for errors indicated by the ADK event structure
                if not output_event.actions:
                    raise ValueError("Orchestrator LLM Agent did not produce any output actions.")

                # Emit final completion update
                completion_message = "Task completed successfully by Orchestrator."
                self.socketio.emit('task_update', {
                    'task_id': task_id,
                    'status': 'completed',
                    'message': completion_message,
                    'result': llm_response_text
                })
                logger.info(f"Emitted 'task_update' (completed by orchestrator) for task {task_id} with LLM response.")
                return output_event

            except Exception as e:
                error_message = f"Orchestrator processing failed: {str(e)}"
                logger.error(f"Task {task_id} failed during orchestrator processing: {error_message}", exc_info=True)
                self.socketio.emit('task_update', {
                    'task_id': task_id,
                    'status': 'failed',
                    'message': error_message,
                    'result': None
                })
                logger.info(f"Emitted 'task_update' (orchestrator failed) for task {task_id}")
                return self._create_error_event(error_message, context.input_event)


    async def _classify_intent(self, user_prompt: str, task_id: str) -> Tuple[str, Optional[str]]:
        """
        Uses the agent's LLM to classify the user prompt's intent.

        Args:
            user_prompt: The user's input prompt.
            task_id: The ID of the current task for logging.

        Returns:
            A tuple containing the classified agent key (str) and an optional error message (str).
            Defaults to "self" on error.
        """
        CLASSIFICATION_PROMPT_TEMPLATE = """
Analyze the following user prompt and classify the primary intent. Your goal is to determine which specialized agent should handle this request, or if the orchestrator should handle it directly ('self').

Available agents and their functions:
- market_analyzer: Handles market analysis, trend identification, and finding business opportunities.
- content_generator: Writes articles, marketing copy, or other forms of content.
- lead_generator: Finds potential leads, often involving web scraping or searching specific platforms like Quora.
- freelance_tasker: Finds and manages freelance jobs on platforms like Upwork.
- web_searcher: Performs general web searches to find information.
- workflow_manager: Manages the multi-step autonomous income generation workflow.
- self: Use this if the request is general, doesn't fit other agents, or is a direct request to the orchestrator.

User Prompt:
"{user_prompt}"

Based on the user prompt, output ONLY the key of the most appropriate agent from the list above (market_analyzer, content_generator, lead_generator, freelance_tasker, web_searcher, workflow_manager, self). Do not add any explanation or other text.
"""
        VALID_AGENT_KEYS = [
            "market_analyzer", "content_generator", "lead_generator",
            "freelance_tasker", "web_searcher", "workflow_manager", "self"
        ]

        classification_prompt = CLASSIFICATION_PROMPT_TEMPLATE.format(user_prompt=user_prompt)
        logger.debug(f"Task {task_id}: Sending classification prompt to LLM: {classification_prompt}")

        try:
            # Create a simple event for the classification call
            classification_event = Event(
                author="system", # Or self.name?
                actions=[Action(content=Content(parts=[Part(text=classification_prompt)]))]
                # No invocation_id needed here as it's an internal call
            )
            # Use a temporary context for the internal LLM call
            # We don't want to pollute the main session or context history with this internal step
            temp_context = InvocationContext(
                 session=InvocationContext.create_session(), # Create a temporary session
                 input_event=classification_event
            )

            # Call the LLM using the base class method but with the classification prompt
            # Note: We are calling super().run_async which uses the agent's configured model (Gemini)
            classification_output_event = await super().run_async(temp_context)

            # Extract the classification result
            llm_response_text = self._extract_text_from_event(classification_output_event, "").strip()

            logger.debug(f"Task {task_id}: Received classification response from LLM: '{llm_response_text}'")

            # Validate the response
            if llm_response_text in VALID_AGENT_KEYS:
                return llm_response_text, None
            else:
                logger.warning(f"Task {task_id}: LLM classification returned invalid key: '{llm_response_text}'. Valid keys: {VALID_AGENT_KEYS}")
                return "self", f"LLM returned invalid classification key: {llm_response_text}"

        except Exception as e:
            error_message = f"LLM classification call failed: {str(e)}"
            logger.error(f"Task {task_id}: {error_message}", exc_info=True)
            return "self", error_message


    def _prepare_delegation_context(self, original_context: InvocationContext, target_agent_key: str, prompt: str) -> InvocationContext:
        """
        Prepares the InvocationContext for the delegated agent.
        Currently passes the original context but adds agent-specific metadata if needed.
        """
        # Start with the original event
        input_event = original_context.input_event
        metadata = (input_event.metadata or {}).copy() # Start with existing metadata

        # --- Add agent-specific metadata ---
        # This section can be expanded based on the specific needs of each agent
        # For example, extracting API keys or specific parameters from the prompt.

        if target_agent_key == "lead_generator":
            # Use settings object
            firecrawl_api_key = settings.FIRECRAWL_API_KEY
            gemini_api_key = settings.GEMINI_API_KEY # Use settings
            composio_api_key = settings.COMPOSIO_API_KEY # Use settings
            # Check if keys obtained from settings are None or empty
            if not all([firecrawl_api_key, gemini_api_key, composio_api_key]):
                 logger.warning(f"Missing API keys (checked via settings) for {target_agent_key}. Delegation might fail.")
            metadata.update({
                "firecrawl_api_key": firecrawl_api_key,
                "gemini_api_key": gemini_api_key, # Pass key from settings
                "composio_api_key": composio_api_key,
                "user_query": prompt # Pass original prompt explicitly
            })

        elif target_agent_key == "freelance_tasker":
             # Basic example: Determine action and user ID
             action = 'execute_task' # Default
             if any(k in prompt.lower() for k in ["bid", "monitor"]):
                 action = 'monitor_and_bid'
             user_identifier = original_context.session.metadata.get('user_id', 'placeholder_user_id')
             metadata.update({
                 'action': action,
                 'user_identifier': user_identifier,
                 'keywords': prompt # Simplistic keyword extraction
             })

        elif target_agent_key == "web_searcher":
            # Use settings object
            brave_api_key = settings.BRAVE_API_KEY
            if not brave_api_key:
                 logger.warning(f"Missing BRAVE_API_KEY (checked via settings) for {target_agent_key}. Delegation might fail.")
            metadata.update({
                "brave_api_key": brave_api_key, # Pass key from settings
                "query": prompt # Use original prompt as query
            })

        # Add more elif blocks here for other agents requiring specific metadata

        # Create a potentially modified input event if metadata changed
        if metadata != (original_context.input_event.metadata or {}):
            modified_input_event = Event(
                author=input_event.author,
                actions=input_event.actions,
                invocation_id=input_event.invocation_id,
                metadata=metadata
            )
        else:
             modified_input_event = input_event # No changes needed

        # Return a new context with the potentially modified event
        # Use the original session to maintain conversation history if needed by the delegate
        return InvocationContext(
            session=original_context.session,
            input_event=modified_input_event
        )


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

    # Removed process_task and get_task_status as they are replaced by run_async and ADK session management.
