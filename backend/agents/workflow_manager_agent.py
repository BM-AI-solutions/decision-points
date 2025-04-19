from __future__ import annotations

import asyncio
import json
import time
import uuid
from typing import Any, Dict, Optional, Tuple
from datetime import datetime, timezone

import httpx # Using httpx for async HTTP requests
from google.cloud import firestore
from flask_socketio import SocketIO

from google.adk.agents import BaseAgent
from google.adk.events import Event, EventActions, Action, Content, Part
from google.adk.sessions import InvocationContext

from utils.logger import setup_logger
from models.task import Task, TaskStatus # Import the Task model and status enum

logger = setup_logger('agents.workflow_manager')

class WorkflowManagerAgent(BaseAgent):
    """
    Manages the multi-step autonomous income generation workflow.
    Receives a task from the OrchestratorAgent and coordinates calls
    to specialized agents for each stage (Market Research, Improvement, Branding, Deployment).
    Updates task status via Firestore and SocketIO.
    """
    socketio: SocketIO
    firestore_db: firestore.AsyncClient
    collection_name: str
    market_research_agent_url: Optional[str]
    improvement_agent_url: Optional[str]
    branding_agent_url: Optional[str]
    deployment_agent_url: Optional[str]
    timeout_seconds: int

    def __init__(
        self,
        socketio: SocketIO,
        firestore_db: firestore.AsyncClient,
        collection_name: str,
        market_research_agent_url: Optional[str],
        improvement_agent_url: Optional[str],
        branding_agent_url: Optional[str],
        deployment_agent_url: Optional[str],
        timeout_seconds: int = 300, # Default timeout 5 minutes
        name: str = "WorkflowManagerAgent",
        description: str = "Manages the autonomous income generation workflow.",
        **kwargs: Any,
    ):
        super().__init__(name=name, description=description, **kwargs)
        self.socketio = socketio
        self.firestore_db = firestore_db
        self.collection_name = collection_name
        self.market_research_agent_url = market_research_agent_url
        self.improvement_agent_url = improvement_agent_url
        self.branding_agent_url = branding_agent_url
        self.deployment_agent_url = deployment_agent_url
        self.timeout_seconds = timeout_seconds

        # Log the URLs being used
        logger.info(f"{self.name} initialized with:")
        logger.info(f"  Firestore Collection: {self.collection_name}")
        logger.info(f"  Market Research URL: {self.market_research_agent_url}")
        logger.info(f"  Improvement URL: {self.improvement_agent_url}")
        logger.info(f"  Branding URL: {self.branding_agent_url}")
        logger.info(f"  Deployment URL: {self.deployment_agent_url}")
        logger.info(f"  Timeout: {self.timeout_seconds} seconds")

        if not all([self.market_research_agent_url, self.improvement_agent_url, self.branding_agent_url, self.deployment_agent_url]):
             logger.warning(f"{self.name}: One or more stage agent URLs are not configured. Workflow execution will likely fail.")
        if not self.firestore_db:
            logger.error(f"{self.name}: Firestore client is not available. Task state updates will fail.")


    async def run_async(self, context: InvocationContext) -> Event:
        """
        Executes the 4-step income generation workflow.

        Args:
            context: Invocation context containing task details in metadata.

        Returns:
            An Event indicating the final outcome (success or failure).
        """
        # Extract task details from invocation_data (passed via metadata by Orchestrator)
        invocation_data = context.invocation_data or {}
        task_id = invocation_data.get('task_id')
        initial_goal = invocation_data.get('goal')
        user_id = invocation_data.get('user_id')

        if not task_id or not initial_goal:
            error_msg = "WorkflowManagerAgent requires 'task_id' and 'goal' in invocation_data."
            logger.error(error_msg)
            return self._create_final_event(task_id, success=False, message=error_msg)

        logger.info(f"WorkflowManager starting task {task_id} for goal: '{initial_goal}' (User: {user_id})")

        # --- Workflow Stages ---
        stages = [
            ("stage_1_market_research", self.market_research_agent_url, self._run_market_research),
            ("stage_2_improvement", self.improvement_agent_url, self._run_improvement),
            ("stage_3_branding", self.branding_agent_url, self._run_branding),
            ("stage_4_deployment", self.deployment_agent_url, self._run_deployment),
        ]

        current_input_data = {"initial_goal": initial_goal}
        stage_outputs = {}
        final_result = None
        workflow_success = True
        last_stage_name = "initializing" # Keep track of the last attempted stage

        # Initialize Task in Firestore
        await self._update_task_state(
            task_id,
            user_id=user_id,
            goal=initial_goal,
            status=TaskStatus.PENDING,
            current_stage="initializing",
            stage_outputs=stage_outputs
        )

        for stage_name, agent_url, stage_runner_func in stages:
            last_stage_name = stage_name # Update last attempted stage
            if not agent_url:
                error_msg = f"URL for agent '{stage_name}' is not configured. Skipping stage and failing workflow."
                logger.error(f"Task {task_id}: {error_msg}")
                await self._update_task_state(task_id, status=TaskStatus.FAILED, error_message=error_msg)
                workflow_success = False
                break # Stop workflow if a stage URL is missing

            logger.info(f"Task {task_id}: Starting {stage_name}...")
            await self._update_task_state(task_id, status=TaskStatus.RUNNING, current_stage=stage_name)

            try:
                # Call the specific runner function for the stage
                success, result_data, error_message = await stage_runner_func(
                    task_id, agent_url, current_input_data, stage_outputs # Pass full stage_outputs
                )

                if success:
                    logger.info(f"Task {task_id}: Completed {stage_name} successfully.")
                    stage_outputs[stage_name] = result_data
                    current_input_data = result_data # Output of current stage is input for the next
                    final_result = result_data # Keep track of the last successful output as the final result
                    await self._update_task_state(task_id, stage_outputs=stage_outputs) # Persist intermediate output
                else:
                    error_msg = f"{stage_name} failed: {error_message}"
                    logger.error(f"Task {task_id}: {error_msg}")
                    await self._update_task_state(task_id, status=TaskStatus.FAILED, error_message=error_msg)
                    workflow_success = False
                    break # Stop workflow on failure

            except Exception as e:
                error_msg = f"Exception during {stage_name}: {str(e)}"
                logger.error(f"Task {task_id}: {error_msg}", exc_info=True)
                await self._update_task_state(task_id, status=TaskStatus.FAILED, error_message=error_msg)
                workflow_success = False
                break # Stop workflow on unexpected error

        # --- Finalize Workflow ---
        if workflow_success:
            logger.info(f"Task {task_id}: Workflow completed successfully.")
            await self._update_task_state(task_id, status=TaskStatus.COMPLETED, current_stage="completed", result=final_result)
            final_message = "Workflow completed successfully."
        else:
            logger.warning(f"Task {task_id}: Workflow failed.")
            # Status already set to FAILED in the loop
            final_message = f"Workflow failed during stage: {last_stage_name}. Check logs and task details." # Use last attempted stage_name

        return self._create_final_event(task_id, workflow_success, final_message, final_result)


    async def _run_market_research(self, task_id: str, agent_url: str, input_data: Dict[str, Any], stage_outputs: Dict[str, Any]) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """Runs the Market Research stage."""
        payload = {
            "task_id": task_id,
            "stage": "stage_1_market_research",
            "input_data": {
                "initial_topic": input_data.get("initial_goal") # Pass the initial goal as the topic
            }
        }
        return await self._call_stage_agent(task_id, "MarketResearchAgent", agent_url, payload)

    async def _run_improvement(self, task_id: str, agent_url: str, input_data: Dict[str, Any], stage_outputs: Dict[str, Any]) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """Runs the Improvement stage."""
        payload = {
            "task_id": task_id,
            "stage": "stage_2_improvement",
            "input_data": {
                "market_opportunity_report": input_data # Pass the full output from stage 1
            }
        }
        return await self._call_stage_agent(task_id, "ImprovementAgent", agent_url, payload)

    async def _run_branding(self, task_id: str, agent_url: str, input_data: Dict[str, Any], stage_outputs: Dict[str, Any]) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """Runs the Branding stage."""
        payload = {
            "task_id": task_id,
            "stage": "stage_3_branding",
            "input_data": {
                "improved_product_spec": input_data # Pass the full output from stage 2
            }
        }
        return await self._call_stage_agent(task_id, "BrandingAgent", agent_url, payload)

    async def _run_deployment(self, task_id: str, agent_url: str, input_data: Dict[str, Any], stage_outputs: Dict[str, Any]) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """Runs the Deployment stage."""
        # Deployment needs both the product spec (from stage 2) and brand package (from stage 3)
        improved_product_spec = stage_outputs.get("stage_2_improvement")
        brand_package = input_data # Stage 3 output is the brand package

        if not improved_product_spec:
             logger.warning(f"Task {task_id}: Missing 'ImprovedProductSpec' from stage 2 output for deployment stage.")
             # Decide how to handle: fail, or proceed with partial data? Failing is safer.
             # return False, None, "Missing required input 'ImprovedProductSpec' from previous stage."

        payload = {
            "task_id": task_id,
            "stage": "stage_4_deployment",
            "input_data": {
                 "improved_product_spec": improved_product_spec,
                 "brand_package": brand_package
            }
        }
        logger.info(f"Task {task_id}: Running deployment stage with product spec and brand package.")
        return await self._call_stage_agent(task_id, "DeploymentAgent", agent_url, payload)


    async def _call_stage_agent(self, task_id: str, agent_name: str, agent_url: str, payload: Dict[str, Any]) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        Helper function to call a stage agent's /run endpoint via REST API.

        Returns:
            Tuple: (success: bool, result_data: Optional[Dict], error_message: Optional[str])
        """
        logger.debug(f"Task {task_id}: Calling {agent_name} at {agent_url} with payload: {json.dumps(payload, indent=2)}")
        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                response = await client.post(f"{agent_url}/run", json=payload) # Assuming /run endpoint
                response.raise_for_status() # Raise exception for 4xx or 5xx status codes

            response_data = response.json()
            logger.debug(f"Task {task_id}: Received response from {agent_name}: {json.dumps(response_data, indent=2)}")

            if response_data.get("status") == "success":
                return True, response_data.get("result"), None
            else:
                error_msg = response_data.get("error_message", "Agent returned failure status without error message.")
                return False, None, error_msg

        except httpx.TimeoutException:
            error_msg = f"Timeout error calling {agent_name} after {self.timeout_seconds} seconds."
            logger.error(f"Task {task_id}: {error_msg}")
            return False, None, error_msg
        except httpx.RequestError as e:
            error_msg = f"HTTP request error calling {agent_name}: {e}"
            logger.error(f"Task {task_id}: {error_msg}", exc_info=True)
            return False, None, error_msg
        except json.JSONDecodeError as e:
             error_msg = f"Failed to decode JSON response from {agent_name}: {e}"
             logger.error(f"Task {task_id}: {error_msg}", exc_info=True)
             return False, None, error_msg
        except Exception as e:
            error_msg = f"Unexpected error calling {agent_name}: {str(e)}"
            logger.error(f"Task {task_id}: {error_msg}", exc_info=True)
            return False, None, error_msg


    async def _update_task_state(self, task_id: str, **updates: Any) -> None:
        """
        Updates the task document in Firestore and emits update via SocketIO.
        Handles partial updates.
        """
        if not self.firestore_db:
            logger.error(f"Task {task_id}: Firestore client not available. Cannot update task state.")
            # Optionally emit a failure state via SocketIO if possible?
            # self.socketio.emit('task_update', {'task_id': task_id, 'status': TaskStatus.FAILED.value, 'error_message': 'Internal Server Error: Database connection failed.'})
            return

        try:
            task_ref = self.firestore_db.collection(self.collection_name).document(task_id)
            timestamp = datetime.now(timezone.utc)
            update_data = {**updates, "updated_at": timestamp}

            # Ensure complex objects like stage_outputs are handled correctly
            # Firestore merge=True handles nested updates well for dicts
            # Convert Enums to strings if present
            if 'status' in update_data and isinstance(update_data['status'], TaskStatus):
                update_data['status'] = update_data['status'].value

            # Convert datetime objects to Firestore Timestamps before writing
            for key, value in update_data.items():
                if isinstance(value, datetime):
                    update_data[key] = firestore.SERVER_TIMESTAMP if value == timestamp else value # Use server timestamp for updated_at

            # If it's the first time setting status, also set created_at
            doc_snapshot = await task_ref.get()
            if not doc_snapshot.exists:
                 update_data['created_at'] = firestore.SERVER_TIMESTAMP # Use server timestamp
                 # Set initial fields if creating
                 if 'userId' in updates: update_data['userId'] = updates['userId']
                 if 'goal' in updates: update_data['goal'] = updates['goal']
                 if 'status' not in update_data: update_data['status'] = TaskStatus.PENDING.value
                 logger.info(f"Task {task_id}: Creating new task document in Firestore.")
                 await task_ref.set(update_data) # Use set for creation
            else:
                 logger.debug(f"Task {task_id}: Updating task document in Firestore with: {update_data}")
                 await task_ref.set(update_data, merge=True) # Use set with merge=True for updates

            # Fetch the updated document to send via SocketIO
            # Short delay to allow server timestamp to populate? Usually not needed but can help in some race conditions.
            # await asyncio.sleep(0.1)
            updated_doc = await task_ref.get()
            if updated_doc.exists:
                task_data = updated_doc.to_dict()
                # Convert Firestore Timestamps back to ISO strings for JSON
                for key, value in task_data.items():
                     if isinstance(value, datetime):
                         task_data[key] = value.isoformat()

                logger.info(f"Task {task_id}: Emitting task_update via SocketIO. Status: {task_data.get('status')}, Stage: {task_data.get('current_stage')}")
                self.socketio.emit('task_update', task_data) # Emit the full updated task data
            else:
                 logger.warning(f"Task {task_id}: Document not found after update/create for SocketIO emission.")


        except Exception as e:
            logger.error(f"Task {task_id}: Failed to update Firestore or emit SocketIO message: {str(e)}", exc_info=True)


    def _create_final_event(self, task_id: str, success: bool, message: str, result: Optional[Dict[str, Any]] = None) -> Event:
        """Creates the final event to return from run_async."""
        status = "completed" if success else "failed"
        final_content = f"Workflow {status} for task {task_id}. Message: {message}"
        if result and success:
            # Include result summary if successful
            try:
                # Attempt to pretty-print JSON result
                result_summary = json.dumps(result, indent=2, default=str)
                final_content += f"\n\nFinal Result:\n{result_summary}"
            except Exception as e:
                 logger.warning(f"Task {task_id}: Could not serialize final result for event: {e}")
                 final_content += "\n\nFinal Result: (Could not serialize)"

        logger.info(f"Task {task_id}: Creating final event. Success: {success}, Message: {message}")
        return Event(
            author=self.name,
            actions=[Action(content=Content(parts=[Part(text=final_content)]))],
            metadata={"task_id": task_id, "status": status, "final_message": message} # Add final message to metadata
        )

# Example of how this agent might be invoked by the OrchestratorAgent:
# (This code doesn't run here, it's for illustration)
# ```python
# async def orchestrator_delegation_example():
#     # Assume workflow_manager_agent is an instance of WorkflowManagerAgent
#     # Assume orchestrator_context is the InvocationContext received by OrchestratorAgent
#
#     # Prepare context for WorkflowManagerAgent
#     invocation_data = orchestrator_context.invocation_data or {}
#     task_id = invocation_data.get('task_id')
#     goal = invocation_data.get('goal')
#     user_id = invocation_data.get('user_id')
#
#     workflow_context = InvocationContext(
#         session=orchestrator_context.session, # Can reuse session or create new
#         input_event=orchestrator_context.input_event, # Pass original event if needed
#         invocation_data={ # Pass necessary data here
#             "task_id": task_id,
#             "goal": goal,
#             "user_id": user_id
#         }
#     )
#
#     # Call the WorkflowManagerAgent
#     final_event = await workflow_manager_agent.run_async(workflow_context)
#     print(f"Workflow Manager finished with event: {final_event}")
