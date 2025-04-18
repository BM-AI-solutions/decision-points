import os
import asyncio
from typing import Any, Dict, List, Optional, Union

from flask_socketio import SocketIO
from google.ai import generativelanguage as glm

from google.adk.agents import LlmAgent, BaseAgent # Import BaseAgent for type hinting
from google.adk.models import Gemini, BaseLlm
from google.adk.tools import ToolContext
from google.adk.events import Event, EventActions, Action, Content, Part
from google.adk.sessions import InvocationContext
from utils.logger import setup_logger

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
        agents: Dict[str, BaseAgent], # Add agents parameter
        model: Optional[Union[BaseLlm, str]] = None,
        instruction: Optional[str] = None,
        name: str = "OrchestratorAgent",
        description: str = "Handles user prompts and orchestrates tasks, potentially delegating to specialized agents.",
        **kwargs: Any,
    ):
        """
        Initializes the ADK-based Orchestrator Agent.

        Args:
            socketio: The Flask-SocketIO instance.
            agents: A dictionary mapping agent names to agent instances.
            model: The ADK model instance or model name string (e.g., 'gemini-1.5-flash'). Defaults to Gemini 1.5 Flash.
            instruction: Default instruction for the LLM agent.
            name: Name of the agent.
            description: Description of the agent.
            **kwargs: Additional arguments for LlmAgent.
        """
        if model is None:
            model = Gemini(model='gemini-1.5-flash-latest') # Default to a Gemini model via ADK
        elif isinstance(model, str):
             model = Gemini(model=model) # Allow passing model name string

        # Ensure instruction is provided, even if basic
        if instruction is None:
            instruction = "Process the user's request."

        super().__init__(
            name=name,
            description=description,
            model=model,
            instruction=instruction,
            **kwargs
        )
        self.socketio = socketio
        self.agents = agents # Store the agents dictionary
        logger.info(f"{self.name} initialized with SocketIO, model: {self.model.model}, and agents: {list(self.agents.keys())}.")


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

        # --- Delegation Logic ---
        delegation_keywords = ["market analysis", "analyze trends", "find opportunities", "market research"]
        should_delegate_to_market_analyzer = any(keyword in prompt.lower() for keyword in delegation_keywords)
        market_agent = self.agents.get("market_analyzer")
        content_agent = self.agents.get("content_generator") # Get content agent
        lead_agent = self.agents.get("lead_generator") # Get lead agent
        freelance_agent = self.agents.get("freelance_tasker") # Get freelance agent
        web_search_agent = self.agents.get("web_searcher") # Get web search agent
        workflow_manager_agent = self.agents.get("workflow_manager") # Get workflow manager agent

        # --- Market Analysis Delegation ---
        if should_delegate_to_market_analyzer and market_agent:
            logger.info(f"Task {task_id} identified for delegation to MarketAnalysisAgent.")
            self.socketio.emit('task_update', {
                'task_id': task_id,
                'status': 'delegating',
                'agent': 'market_analyzer',
                'message': f"Delegating task to Market Analysis Agent..."
            })
            logger.info(f"Emitted 'task_update' (delegating to market_analyzer) for task {task_id}")

            try:
                delegated_context = InvocationContext(session=context.session, input_event=context.input_event)
                delegated_output_event = await market_agent.run_async(delegated_context)
                delegated_result_text = "No text response from market analysis agent."
                if delegated_output_event.actions and delegated_output_event.actions[0].parts:
                    text_parts = [p.text for p in delegated_output_event.actions[0].parts if p.type == 'text']
                    if text_parts:
                        delegated_result_text = text_parts[0]

                completion_message = "Task completed by Market Analysis Agent."
                self.socketio.emit('task_update', {
                    'task_id': task_id,
                    'status': 'completed',
                    'message': completion_message,
                    'result': delegated_result_text
                })
                logger.info(f"Emitted 'task_update' (completed by market_analyzer) for task {task_id}.")
                return delegated_output_event

            except Exception as e:
                error_message = f"Delegation to MarketAnalysisAgent failed: {str(e)}"
                logger.error(f"Task {task_id} delegation to market_analyzer failed: {error_message}", exc_info=True)
                self.socketio.emit('task_update', {
                    'task_id': task_id,
                    'status': 'failed',
                    'message': error_message,
                    'result': None
                })
                logger.info(f"Emitted 'task_update' (market_analyzer delegation failed) for task {task_id}")
                error_action = Action(content=Content(parts=[Part(text=f"Error: {error_message}")]))
                invocation_id = getattr(context.input_event, 'invocation_id', None)
                return Event(author=self.name, actions=[error_action], invocation_id=invocation_id)

        # --- Content Generation Delegation ---
        elif content_agent and any(keyword in prompt.lower() for keyword in ["write", "create content", "generate article", "marketing copy"]):
            logger.info(f"Task {task_id} identified for delegation to ContentGenerationAgent.")
            self.socketio.emit('task_update', {
                'task_id': task_id,
                'status': 'delegating',
                'agent': 'content_generator',
                'message': f"Delegating task to Content Generation Agent..."
            })
            logger.info(f"Emitted 'task_update' (delegating to content_generator) for task {task_id}")

            try:
                # Extract relevant parameters for ContentGenerationAgent if needed
                # For now, pass the same context
                # TODO: Enhance context creation based on ContentGenerationAgent's needs
                delegated_context = InvocationContext(session=context.session, input_event=context.input_event)

                # Invoke the ContentGenerationAgent
                delegated_output_event = await content_agent.run_async(delegated_context)

                # Extract result from the delegated agent's response
                delegated_result_text = "No text response from content generation agent."
                if delegated_output_event.actions and delegated_output_event.actions[0].parts:
                    text_parts = [p.text for p in delegated_output_event.actions[0].parts if p.type == 'text']
                    if text_parts:
                        delegated_result_text = text_parts[0]

                # Emit final completion update
                completion_message = "Task completed by Content Generation Agent."
                self.socketio.emit('task_update', {
                    'task_id': task_id,
                    'status': 'completed',
                    'message': completion_message,
                    'result': delegated_result_text
                })
                logger.info(f"Emitted 'task_update' (completed by content_generator) for task {task_id}.")
                return delegated_output_event # Return the event from the delegate

            except Exception as e:
                error_message = f"Delegation to ContentGenerationAgent failed: {str(e)}"
                logger.error(f"Task {task_id} delegation to content_generator failed: {error_message}", exc_info=True)
                self.socketio.emit('task_update', {
                    'task_id': task_id,
                    'status': 'failed',
                    'message': error_message,
                    'result': None
                })
                logger.info(f"Emitted 'task_update' (content_generator delegation failed) for task {task_id}")
                # Return an error event
                error_action = Action(content=Content(parts=[Part(text=f"Error: {error_message}")]))
                invocation_id = getattr(context.input_event, 'invocation_id', None)
                return Event(author=self.name, actions=[error_action], invocation_id=invocation_id)

        # --- Lead Generation Delegation ---
        elif lead_agent and any(keyword in prompt.lower() for keyword in ["find leads", "generate leads", "search quora", "prospecting"]):
            logger.info(f"Task {task_id} identified for delegation to LeadGenerationAgent.")
            self.socketio.emit('task_update', {
                'task_id': task_id,
                'status': 'delegating',
                'agent': 'lead_generator',
                'message': f"Delegating task to Lead Generation Agent..."
            })
            logger.info(f"Emitted 'task_update' (delegating to lead_generator) for task {task_id}")

            try:
                # Fetch required API keys from environment variables
                firecrawl_api_key = os.getenv("FIRECRAWL_API_KEY")
                openai_api_key = os.getenv("OPENAI_API_KEY") # Assuming OPENAI_API_KEY is the correct env var name
                composio_api_key = os.getenv("COMPOSIO_API_KEY") # Assuming COMPOSIO_API_KEY is the correct env var name

                if not all([firecrawl_api_key, openai_api_key, composio_api_key]):
                    missing_keys = [k for k, v in {
                        "FIRECRAWL_API_KEY": firecrawl_api_key,
                        "OPENAI_API_KEY": openai_api_key,
                        "COMPOSIO_API_KEY": composio_api_key
                    }.items() if not v]
                    raise ValueError(f"Missing required API keys for LeadGenerationAgent: {', '.join(missing_keys)}")

                # Create a new input event with API keys in metadata
                delegated_input_event = Event(
                    author=context.input_event.author, # Keep original author or set to orchestrator?
                    actions=context.input_event.actions, # Pass original actions (containing prompt)
                    invocation_id=context.input_event.invocation_id,
                    metadata={
                        "firecrawl_api_key": firecrawl_api_key,
                        "openai_api_key": openai_api_key,
                        "composio_api_key": composio_api_key,
                        "user_query": prompt # Pass the original prompt explicitly if needed by agent
                    }
                )

                # Create a new context with the modified input event
                delegated_context = InvocationContext(
                    session=context.session,
                    input_event=delegated_input_event
                )

                # Invoke the LeadGenerationAgent
                delegated_output_event = await lead_agent.run_async(delegated_context)

                # Extract result from the delegated agent's response
                delegated_result_text = "No text response from lead generation agent."
                if delegated_output_event.actions and delegated_output_event.actions[0].parts:
                    text_parts = [p.text for p in delegated_output_event.actions[0].parts if p.type == 'text']
                    if text_parts:
                        delegated_result_text = text_parts[0]
                    # TODO: Handle potential structured data (e.g., JSON) if the agent returns it

                # Emit final completion update
                completion_message = "Task completed by Lead Generation Agent."
                self.socketio.emit('task_update', {
                    'task_id': task_id,
                    'status': 'completed',
                    'message': completion_message,
                    'result': delegated_result_text # Or potentially structured result
                })
                logger.info(f"Emitted 'task_update' (completed by lead_generator) for task {task_id}.")
                return delegated_output_event # Return the event from the delegate

            except Exception as e:
                error_message = f"Delegation to LeadGenerationAgent failed: {str(e)}"
                logger.error(f"Task {task_id} delegation to lead_generator failed: {error_message}", exc_info=True)
                self.socketio.emit('task_update', {
                    'task_id': task_id,
                    'status': 'failed',
                    'message': error_message,
                    'result': None
                })
                logger.info(f"Emitted 'task_update' (lead_generator delegation failed) for task {task_id}")
                # Return an error event
                error_action = Action(content=Content(parts=[Part(text=f"Error: {error_message}")]))
                invocation_id = getattr(context.input_event, 'invocation_id', None)
                return Event(author=self.name, actions=[error_action], invocation_id=invocation_id)


        # --- Freelance Task Delegation ---
        elif freelance_agent and any(keyword in prompt.lower() for keyword in ["find freelance jobs", "search upwork", "bid on task", "monitor tasks", "freelance task"]):
            logger.info(f"Task {task_id} identified for delegation to FreelanceTaskAgent.")
            self.socketio.emit('task_update', {
                'task_id': task_id,
                'status': 'delegating',
                'agent': 'freelance_tasker',
                'message': f"Delegating task to Freelance Task Agent..."
            })
            logger.info(f"Emitted 'task_update' (delegating to freelance_tasker) for task {task_id}")

            try:
                # Determine action based on prompt keywords
                action = 'execute_task' # Default action
                if any(k in prompt.lower() for k in ["bid", "monitor"]):
                    action = 'monitor_and_bid'

                # Determine user identifier (using placeholder for now)
                user_identifier = context.session.metadata.get('user_id', 'placeholder_user_id') # Try to get from session, fallback

                # Extract other potential parameters (e.g., keywords, platform) - basic example
                # This part would need more sophisticated NLP or structured input in a real scenario
                task_keywords = prompt # Simplistic: use the whole prompt as keywords for now

                # Create a new input event with specific metadata for the FreelanceTaskAgent
                delegated_input_event = Event(
                    author=context.input_event.author,
                    actions=context.input_event.actions, # Pass original actions (containing prompt)
                    invocation_id=context.input_event.invocation_id,
                    metadata={
                        'action': action,
                        'user_identifier': user_identifier,
                        'keywords': task_keywords,
                        # Add other necessary parameters here based on FreelanceTaskAgent needs
                        **(context.input_event.metadata or {}) # Merge original metadata if any
                    }
                )

                # Create a new context with the modified input event
                delegated_context = InvocationContext(
                    session=context.session,
                    input_event=delegated_input_event
                )

                # Invoke the FreelanceTaskAgent
                delegated_output_event = await freelance_agent.run_async(delegated_context)

                # Extract result from the delegated agent's response
                delegated_result_text = "No text response from freelance task agent."
                if delegated_output_event.actions and delegated_output_event.actions[0].parts:
                    text_parts = [p.text for p in delegated_output_event.actions[0].parts if p.type == 'text']
                    if text_parts:
                        delegated_result_text = text_parts[0]
                    # TODO: Handle potential structured data if the agent returns it

                # Emit final completion update
                completion_message = "Task completed by Freelance Task Agent."
                self.socketio.emit('task_update', {
                    'task_id': task_id,
                    'status': 'completed',
                    'message': completion_message,
                    'result': delegated_result_text
                })
                logger.info(f"Emitted 'task_update' (completed by freelance_tasker) for task {task_id}.")
                return delegated_output_event # Return the event from the delegate

            except Exception as e:
                error_message = f"Delegation to FreelanceTaskAgent failed: {str(e)}"
                logger.error(f"Task {task_id} delegation to freelance_tasker failed: {error_message}", exc_info=True)
                self.socketio.emit('task_update', {
                    'task_id': task_id,
                    'status': 'failed',
                    'message': error_message,
                    'result': None
                })
                logger.info(f"Emitted 'task_update' (freelance_tasker delegation failed) for task {task_id}")
                # Return an error event
                error_action = Action(content=Content(parts=[Part(text=f"Error: {error_message}")]))
                invocation_id = getattr(context.input_event, 'invocation_id', None)
                return Event(author=self.name, actions=[error_action], invocation_id=invocation_id)

        # --- Web Search Delegation ---
        elif web_search_agent and any(keyword in prompt.lower() for keyword in ["search web for", "find information on", "google", "search", "look up"]):
            logger.info(f"Task {task_id} identified for delegation to WebSearchAgent.")
            self.socketio.emit('task_update', {
                'task_id': task_id,
                'status': 'delegating',
                'agent': 'web_searcher',
                'message': f"Delegating task to Web Search Agent..."
            })
            logger.info(f"Emitted 'task_update' (delegating to web_searcher) for task {task_id}")

            try:
                # Fetch required API key from environment variables
                brave_api_key = os.getenv("BRAVE_API_KEY")
                if not brave_api_key:
                    raise ValueError("Missing required BRAVE_API_KEY for WebSearchAgent.")

                # Extract query (simple approach: use the whole prompt for now)
                # TODO: Implement more sophisticated query extraction if needed
                search_query = prompt

                # Create a new input event with API key and query in metadata
                delegated_input_event = Event(
                    author=context.input_event.author,
                    actions=context.input_event.actions, # Pass original actions
                    invocation_id=context.input_event.invocation_id,
                    metadata={
                        "brave_api_key": brave_api_key,
                        "query": search_query,
                        **(context.input_event.metadata or {}) # Merge original metadata
                    }
                )

                # Create a new context with the modified input event
                delegated_context = InvocationContext(
                    session=context.session,
                    input_event=delegated_input_event
                )

                # Invoke the WebSearchAgent
                delegated_output_event = await web_search_agent.run_async(delegated_context)

                # Extract result from the delegated agent's response
                delegated_result_text = "No text response from web search agent."
                if delegated_output_event.actions and delegated_output_event.actions[0].parts:
                    text_parts = [p.text for p in delegated_output_event.actions[0].parts if p.type == 'text']
                    if text_parts:
                        delegated_result_text = text_parts[0]
                    # TODO: Handle potential structured data if the agent returns it

                # Emit final completion update
                completion_message = "Task completed by Web Search Agent."
                self.socketio.emit('task_update', {
                    'task_id': task_id,
                    'status': 'completed',
                    'message': completion_message,
                    'result': delegated_result_text
                })
                logger.info(f"Emitted 'task_update' (completed by web_searcher) for task {task_id}.")
                return delegated_output_event # Return the event from the delegate

            except Exception as e:
                error_message = f"Delegation to WebSearchAgent failed: {str(e)}"
                logger.error(f"Task {task_id} delegation to web_searcher failed: {error_message}", exc_info=True)
                self.socketio.emit('task_update', {
                    'task_id': task_id,
                    'status': 'failed',
                    'message': error_message,
                    'result': None
                })
                logger.info(f"Emitted 'task_update' (web_searcher delegation failed) for task {task_id}")
                # Return an error event
                error_action = Action(content=Content(parts=[Part(text=f"Error: {error_message}")]))
                invocation_id = getattr(context.input_event, 'invocation_id', None)
                return Event(author=self.name, actions=[error_action], invocation_id=invocation_id)

        # --- Autonomous Income Workflow Delegation ---
        elif workflow_manager_agent and any(keyword in prompt.lower() for keyword in ["start income workflow", "run autonomous business", "find and deploy product", "autonomous income", "generate business"]):
            logger.info(f"Task {task_id} identified for delegation to WorkflowManagerAgent.")
            self.socketio.emit('task_update', {
                'task_id': task_id,
                'status': 'delegating',
                'agent': 'workflow_manager',
                'message': f"Delegating task to Autonomous Income Workflow Manager..."
            })
            logger.info(f"Emitted 'task_update' (delegating to workflow_manager) for task {task_id}")

            try:
                # Create context for the Workflow Manager Agent
                # Pass necessary starting parameters if needed via metadata
                # For now, just passing the original prompt within the standard context
                delegated_context = InvocationContext(
                    session=context.session,
                    input_event=context.input_event # Pass the original event, agent should extract needed info
                    # Example of adding specific metadata if needed:
                    # input_event=Event(
                    #     author=context.input_event.author,
                    #     actions=context.input_event.actions,
                    #     invocation_id=context.input_event.invocation_id,
                    #     metadata={
                    #         "initial_prompt": prompt,
                    #         **(context.input_event.metadata or {})
                    #     }
                    # )
                )

                # Invoke the WorkflowManagerAgent
                delegated_output_event = await workflow_manager_agent.run_async(delegated_context)

                # Extract result from the workflow manager's response
                delegated_result_text = "Workflow completed. Check logs or specific outputs for details." # Default message
                if delegated_output_event.actions and delegated_output_event.actions[0].parts:
                    text_parts = [p.text for p in delegated_output_event.actions[0].parts if p.type == 'text']
                    if text_parts:
                        delegated_result_text = text_parts[0]
                    # TODO: Handle potential structured data (e.g., final product URL, summary)

                # Emit final completion update
                completion_message = "Autonomous Income Workflow completed."
                self.socketio.emit('task_update', {
                    'task_id': task_id,
                    'status': 'completed',
                    'message': completion_message,
                    'result': delegated_result_text
                })
                logger.info(f"Emitted 'task_update' (completed by workflow_manager) for task {task_id}.")
                return delegated_output_event # Return the final event from the workflow manager

            except Exception as e:
                error_message = f"Delegation to WorkflowManagerAgent failed: {str(e)}"
                logger.error(f"Task {task_id} delegation to workflow_manager failed: {error_message}", exc_info=True)
                self.socketio.emit('task_update', {
                    'task_id': task_id,
                    'status': 'failed',
                    'message': error_message,
                    'result': None
                })
                logger.info(f"Emitted 'task_update' (workflow_manager delegation failed) for task {task_id}")
                # Return an error event
                error_action = Action(content=Content(parts=[Part(text=f"Error: {error_message}")]))
                invocation_id = getattr(context.input_event, 'invocation_id', None)
                return Event(author=self.name, actions=[error_action], invocation_id=invocation_id)

        # --- Fallback to Orchestrator Processing ---
        else:
            logger.info(f"Task {task_id} will be handled directly by {self.name} (no suitable delegate found or web search agent not available).")
            # Emit initial acknowledgment via SocketIO
            self.socketio.emit('task_update', {
            'task_id': task_id,
            'status': 'submitted', # ADK/A2A state
            'message': f"Task received: {prompt}"
            })
            logger.info(f"Emitted 'task_update' (submitted) for task {task_id}")

            # Emit processing update
            processing_message = f"Processing prompt with {self.model.model}..."
            self.socketio.emit('task_update', {
            'task_id': task_id,
            'status': 'working', # ADK/A2A state
            'message': processing_message
        })
        logger.info(f"Emitted 'task_update' (working) for task {task_id}")

        try:
            # Execute the core LLM logic using the parent LlmAgent's run_async
            output_event = await super().run_async(context)

            # Extract the result text
            llm_response_text = "No text response generated."
            if output_event.actions and output_event.actions[0].parts:
                 text_parts = [p.text for p in output_event.actions[0].parts if p.type == 'text']
                 if text_parts:
                    llm_response_text = text_parts[0]


            # Check for errors indicated by the ADK event structure (e.g., empty actions might imply an issue)
            # Note: LlmAgent's run_async might raise exceptions for model errors, caught below.
            # This check is more for logical errors or empty responses.
            if not output_event.actions:
                 raise ValueError("LLM Agent did not produce any output actions.")


            # Emit final completion update
            completion_message = "Task completed successfully."
            self.socketio.emit('task_update', {
                'task_id': task_id,
                'status': 'completed', # ADK/A2A state
                'message': completion_message,
                'result': llm_response_text # Send the actual LLM text response
            })
            logger.info(f"Emitted 'task_update' (completed) for task {task_id} with LLM response.")
            return output_event

        except Exception as e:
            error_message = f"Processing failed: {str(e)}"
            logger.error(f"Task {task_id} failed: {error_message}", exc_info=True)

            # Emit error update (Mapping 'error' -> 'failed')
            self.socketio.emit('task_update', {
                'task_id': task_id,
                'status': 'failed', # ADK/A2A state
                'message': error_message,
                'result': None
            })
            logger.info(f"Emitted 'task_update' (failed) for task {task_id}")

            # Return an error event
            error_action = Action(
                content=Content(parts=[Part(text=f"Error: {error_message}")])
            )
            # Create a minimal error event, copying invocation_id if possible
            invocation_id = getattr(context.input_event, 'invocation_id', None)
            return Event(
                 author=self.name, actions=[error_action], invocation_id=invocation_id
            )

    # Removed process_task and get_task_status as they are replaced by run_async and ADK session management.