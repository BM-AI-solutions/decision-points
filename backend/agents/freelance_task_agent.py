"""
Freelance Task Agent for Decision Points.

This agent monitors freelance platforms, analyzes tasks, and potentially bids or executes them.
It implements the A2A protocol for agent communication.
"""

import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from google.cloud import secretmanager
from google.adk.runtime import InvocationContext
from google.adk.runtime.events import Event

# A2A Imports
from python_a2a import skill

from agents.base_agent import BaseSpecializedAgent
from app.config import settings
from app.services.db_service import DatabaseService

# Configure logging
logger = logging.getLogger(__name__)

class FreelanceTaskAgent(BaseSpecializedAgent):
    """
    Agent responsible for freelance tasks.
    Monitors freelance platforms, analyzes tasks, and potentially bids or executes them.
    Implements A2A protocol for agent communication.

    Features:
    - Interacts with freelance platform APIs (e.g., Upwork, Fiverr).
    - Manages state related to freelance activities.
    - Uses Secret Manager for platform credentials.
    - Communicates results and events using A2A protocol.
    """

    # Configuration keys
    CONFIG_GCP_PROJECT_ID = "gcp_project_id"
    CONFIG_SECRET_PREFIX = "secret_prefix" # e.g., "freelance-credentials-"

    def __init__(
        self,
        name: str = "freelance_tasker",
        description: str = "Monitors freelance platforms, analyzes tasks, and potentially bids or executes them",
        model_name: Optional[str] = None,
        port: Optional[int] = None,
        config: Dict[str, Any] = None,
        **kwargs: Any,
    ):
        """
        Initialize the FreelanceTaskAgent.

        Args:
            name: The name of the agent.
            description: The description of the agent.
            model_name: The name of the model to use. Defaults to settings.GEMINI_MODEL_NAME.
            port: The port to run the A2A server on. Defaults to settings.FREELANCE_TASKER_AGENT_URL port.
            config: Additional configuration for the agent.
            **kwargs: Additional arguments for BaseSpecializedAgent.
        """
        # Extract port from URL if not provided
        if port is None and settings.FREELANCE_TASKER_AGENT_URL:
            try:
                port = int(settings.FREELANCE_TASKER_AGENT_URL.split(':')[-1])
            except (ValueError, IndexError):
                port = 8011  # Default port

        # Initialize BaseSpecializedAgent
        super().__init__(
            name=name,
            description=description,
            model_name=model_name,
            port=port,
            **kwargs
        )

        # --- Configuration ---
        resolved_config = config or {}
        self.gcp_project_id = resolved_config.get(self.CONFIG_GCP_PROJECT_ID, settings.GCP_PROJECT_ID)
        if not self.gcp_project_id:
            logger.warning("No GCP project ID provided. Some functionality may be limited.")

        self.secret_prefix = resolved_config.get(self.CONFIG_SECRET_PREFIX, "freelance-credentials-")

        # --- Client Initialization ---
        if self.gcp_project_id:
            try:
                self.secret_manager_client = secretmanager.SecretManagerServiceClient()
                logger.info("Secret Manager client initialized.")
            except Exception as e:
                logger.error(f"Failed to initialize Secret Manager client: {e}", exc_info=True)
                logger.warning("Continuing with limited functionality.")
                self.secret_manager_client = None
        else:
            logger.warning("Secret Manager client not initialized due to missing project ID.")
            self.secret_manager_client = None

        logger.info(f"FreelanceTaskAgent initialized with port: {self.port}")

    async def run_async(self, context: InvocationContext) -> Event:
        """
        Main execution logic for the FreelanceTaskAgent asynchronously according to ADK spec.
        Maintained for backward compatibility with ADK.

        Args:
            context: The invocation context containing the input data.

        Returns:
            An Event containing the results or an error.
        """
        logger.info(f"Received invocation for FreelanceTaskAgent (ID: {context.invocation_id})")

        try:
            # Extract parameters from context
            if not hasattr(context, 'params') or not context.params:
                logger.error("Input parameters are missing in the invocation context.")
                return Event(
                    type="error",
                    data={"error": "Input parameters are missing."}
                )

            action = context.params.get("action")
            user_identifier = context.params.get("user_identifier")

            if not user_identifier:
                return self._create_error_event(context, "Missing 'user_identifier' in invocation parameters.")
            if not action:
                return self._create_error_event(context, "Missing 'action' in invocation parameters.")

            # Use the A2A skills
            if action == "monitor_and_bid":
                platform = context.params.get("platform")
                criteria = context.params.get("criteria")
                secret_id_suffix = context.params.get("secret_id_suffix")

                if not platform or not criteria or not secret_id_suffix:
                    return self._create_error_event(context, "Missing parameters for 'monitor_and_bid' action.")

                result = await self.monitor_and_bid_skill(
                    user_identifier=user_identifier,
                    platform=platform,
                    criteria=criteria,
                    secret_id_suffix=secret_id_suffix
                )

            elif action == "execute_task":
                task_details = context.params.get("task_details")

                if not task_details:
                    return self._create_error_event(context, "Missing 'task_details' for 'execute_task' action.")

                result = await self.execute_task_skill(
                    user_identifier=user_identifier,
                    task_details=task_details
                )

            elif action == "get_state":
                result = self.get_state_skill(user_identifier=user_identifier)

            elif action == "update_state":
                new_state = context.params.get("new_state")

                if new_state is None:
                    return self._create_error_event(context, "Missing 'new_state' for 'update_state' action.")

                result = self.update_state_skill(
                    user_identifier=user_identifier,
                    new_state=new_state
                )

            else:
                return self._create_error_event(context, f"Unsupported action: {action}")

            # Create an event from the result
            if result.get("success", False):
                return Event(
                    type=f"{action}_succeeded",
                    data={k: v for k, v in result.items() if k != "success" and k != "message"}
                )
            else:
                return Event(
                    type=f"{action}_failed",
                    data={"error": result.get("error", f"{action} failed.")}
                )

        except Exception as e:
            # Catch-all for unexpected errors
            logger.error(f"Unexpected error in FreelanceTaskAgent: {e}", exc_info=True)
            return Event(
                type="error",
                data={"error": f"An unexpected error occurred: {str(e)}"}
            )

    async def _get_state(self, user_identifier: str) -> dict:
        """Retrieves the agent's state for a specific user from PostgreSQL."""
        try:
            state_data = await DatabaseService.get_agent_state(
                agent_id=self.name,
                user_identifier=user_identifier,
                state_key="freelance_state"
            )

            if not state_data:
                logger.info(f"No state found for {user_identifier}. Returning empty state.")
                return {}

            return state_data
        except Exception as e:
            logger.error(f"Error retrieving state for {user_identifier}: {e}", exc_info=True)
            # Depending on requirements, might re-raise or return specific error indicator
            return {"error": f"Failed to fetch state: {e}"}

    async def _update_state(self, user_identifier: str, new_state_value: dict):
        """Updates the agent's state for a specific user in PostgreSQL."""
        try:
            await DatabaseService.update_agent_state(
                agent_id=self.name,
                user_identifier=user_identifier,
                state_key="freelance_state",
                state_data=new_state_value
            )
            logger.info(f"State updated for {user_identifier}.")
        except Exception as e:
            logger.error(f"Error updating state for {user_identifier}: {e}", exc_info=True)
            # Re-raise to be caught by the main run_async handler
            raise RuntimeError(f"Failed to update state for {user_identifier}: {e}") from e

    def _get_platform_credentials(self, user_identifier: str, secret_id_suffix: str) -> str | None:
        """Retrieves platform credentials from Secret Manager."""
        # Construct secret ID using prefix and user-specific suffix
        secret_id = f"{self.secret_prefix}{user_identifier}-{secret_id_suffix}"
        try:
            name = f"projects/{self.gcp_project_id}/secrets/{secret_id}/versions/latest"
            self.logger.info(f"Attempting to access secret: {name}")
            response = self.secret_manager_client.access_secret_version(request={"name": name})
            credentials = response.payload.data.decode("UTF-8")
            self.logger.info(f"Successfully retrieved credentials for secret suffix {secret_id_suffix} for user {user_identifier}")
            return credentials
        except Exception as e:
            self.logger.error(f"Error retrieving credentials for secret {secret_id}: {e}", exc_info=True)
            # Return None, let the calling function handle the missing credentials
            return None

    async def _handle_monitor_and_bid(self, context: InvocationContext, user_identifier: str, platform: str, criteria: dict, secret_id_suffix: str) -> Event:
        """Placeholder for monitoring and bidding logic."""
        self.logger.info(f"[{user_identifier}] Monitoring {platform} with criteria: {criteria}")

        credentials = self._get_platform_credentials(user_identifier, secret_id_suffix)
        if not credentials:
            return self._create_error_event(context, f"Failed to retrieve credentials for platform {platform} (secret suffix: {secret_id_suffix}).")

        # TODO: Implement actual platform monitoring and bidding logic using credentials
        # Example: platform_client = initialize_platform_client(platform, credentials)
        #          jobs = platform_client.search_jobs(criteria)
        #          bids_placed = []
        #          for job in jobs:
        #              if should_bid(job):
        #                  bid_result = platform_client.place_bid(job['id'], ...)
        #                  bids_placed.append(bid_result)
        #                  # Update state or emit events about bids
        #                  self._publish_event(user_identifier, {"event": "bid_placed", "job_id": job['id'], ...})


        # Placeholder result
        result_payload = {
            "status": "monitoring_started",
            "platform": platform,
            "criteria": criteria,
            "message": "Placeholder: Monitoring and bidding logic initiated."
            # "bids_placed": bids_placed # Include actual results later
        }
        self.logger.info(f"Placeholder: Monitoring complete for {platform}.")

        # Update state (example)
        current_state = await self._get_state(user_identifier)
        current_state.setdefault('monitoring', {})[platform] = {'status': 'active', 'last_run': datetime.now().isoformat()}
        await self._update_state(user_identifier, current_state)

        return Event(
            invocation_context=context,
            payload=result_payload,
            severity=EventSeverity.INFO,
            message=f"Monitoring and bidding initiated for {platform}."
        )

    async def _handle_execute_task(self, context: InvocationContext, user_identifier: str, task_details: dict) -> Event:
        """Placeholder for executing a freelance task."""
        self.logger.info(f"[{user_identifier}] Executing task: {task_details}")

        # TODO: Implement actual task execution logic
        # This might involve:
        # 1. Analyzing task_details to understand requirements.
        # 2. Retrieving necessary credentials if platform interaction is needed.
        # 3. Using LLMs for content generation, analysis, etc. (consider inheriting LlmAgent).
        # 4. Delegating sub-tasks to other agents via A2A calls (e.g., ContentGenerationAgent).
        #    - This would require adding A2A capabilities (e.g., using AgentServiceClient).
        # 5. Interacting with platform APIs to deliver work or update status.
        # 6. Updating state upon completion or progress.

        # Placeholder result
        result_payload = {
            "status": "execution_initiated",
            "task_id": task_details.get("id", "unknown"),
            "message": "Placeholder: Task execution logic initiated."
        }
        self.logger.info(f"Placeholder: Task execution complete for task {task_details.get('id', 'unknown')}.")

        # Update state (example)
        current_state = await self._get_state(user_identifier)
        current_state.setdefault('tasks', {})[task_details.get('id', 'unknown')] = {'status': 'in_progress', 'last_update': datetime.now().isoformat()}
        await self._update_state(user_identifier, current_state)

        # Publish event via Pub/Sub (retained from prototype, consider ADK events too)
        self._publish_event(user_identifier, {"event": "task_execution_started", "task_details": task_details})

        return Event(
            invocation_context=context,
            payload=result_payload,
            severity=EventSeverity.INFO,
            message=f"Task execution initiated for task {task_details.get('id', 'unknown')}."
        )

    def _publish_event(self, user_identifier: str, event_data: dict):
        """Publishes an event to the configured Pub/Sub topic."""
        # This replicates prototype behavior. Consider if self.emit_event is more suitable for ADK integration.
        try:
            topic_path = self.pubsub_publisher.topic_path(self.gcp_project_id, self.pubsub_topic)
            # Add user identifier to attributes for potential filtering on subscriber side
            future = self.pubsub_publisher.publish(
                topic_path,
                data=json.dumps(event_data).encode("utf-8"),
                user_identifier=user_identifier # Custom attribute
            )
            future.result() # Wait for publish confirmation (optional, adds latency)
            self.logger.info(f"Published event to {self.pubsub_topic} for user {user_identifier}: {event_data.get('event')}")
        except Exception as e:
            self.logger.error(f"Error publishing event to {self.pubsub_topic} for {user_identifier}: {e}", exc_info=True)
            # Decide how to handle publish failures

    def _create_error_event(self, context: InvocationContext, message: str) -> Event:
        """Helper to create a standardized error Event."""
        logger.error(f"Error for invocation {context.invocation_id}: {message}")
        return Event(
            type="error",
            data={"error": message}
        )

    # --- A2A Skills ---
    @skill(
        name="monitor_and_bid",
        description="Monitor freelance platforms and bid on matching tasks",
        tags=["freelance", "bidding"]
    )
    async def monitor_and_bid_skill(self, user_identifier: str, platform: str,
                                   criteria: Dict[str, Any], secret_id_suffix: str) -> Dict[str, Any]:
        """
        Monitor freelance platforms and bid on matching tasks.

        Args:
            user_identifier: Unique ID for the user/tenant.
            platform: The freelance platform to monitor (e.g., 'Upwork', 'Fiverr').
            criteria: Criteria for matching tasks (e.g., keywords, budget).
            secret_id_suffix: Suffix for the secret ID containing platform credentials.

        Returns:
            A dictionary containing the monitoring and bidding results.
        """
        logger.info(f"[{user_identifier}] Monitoring {platform} with criteria: {criteria}")

        if not self.db or not self.secret_manager_client or not self.pubsub_publisher:
            return {
                "success": False,
                "error": "GCP clients not initialized. Cannot monitor platforms."
            }

        try:
            # Get platform credentials
            credentials = self._get_platform_credentials(user_identifier, secret_id_suffix)
            if not credentials:
                return {
                    "success": False,
                    "error": f"Failed to retrieve credentials for platform {platform} (secret suffix: {secret_id_suffix})."
                }

            # TODO: Implement actual platform monitoring and bidding logic using credentials
            # For now, return a placeholder result

            # Update state
            current_state = await self._get_state(user_identifier)
            current_state.setdefault('monitoring', {})[platform] = {'status': 'active', 'last_run': datetime.now().isoformat()}
            await self._update_state(user_identifier, current_state)

            # Publish event
            self._publish_event(user_identifier, {"event": "monitoring_started", "platform": platform})

            return {
                "success": True,
                "message": f"Monitoring and bidding initiated for {platform}.",
                "status": "monitoring_started",
                "platform": platform,
                "criteria": criteria
            }

        except Exception as e:
            logger.error(f"Error monitoring and bidding on {platform}: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"Error monitoring and bidding on {platform}: {str(e)}"
            }

    @skill(
        name="execute_task",
        description="Execute a freelance task",
        tags=["freelance", "task"]
    )
    async def execute_task_skill(self, user_identifier: str, task_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a freelance task.

        Args:
            user_identifier: Unique ID for the user/tenant.
            task_details: Details of the task to execute.

        Returns:
            A dictionary containing the task execution results.
        """
        logger.info(f"[{user_identifier}] Executing task: {task_details}")

        if not self.db or not self.pubsub_publisher:
            return {
                "success": False,
                "error": "GCP clients not initialized. Cannot execute tasks."
            }

        try:
            # TODO: Implement actual task execution logic
            # For now, return a placeholder result

            # Update state
            current_state = await self._get_state(user_identifier)
            current_state.setdefault('tasks', {})[task_details.get('id', 'unknown')] = {
                'status': 'in_progress',
                'last_update': datetime.now().isoformat()
            }
            await self._update_state(user_identifier, current_state)

            # Publish event
            self._publish_event(user_identifier, {"event": "task_execution_started", "task_details": task_details})

            return {
                "success": True,
                "message": f"Task execution initiated for task {task_details.get('id', 'unknown')}.",
                "status": "execution_initiated",
                "task_id": task_details.get("id", "unknown")
            }

        except Exception as e:
            logger.error(f"Error executing task: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"Error executing task: {str(e)}"
            }

    @skill(
        name="get_state",
        description="Get the state for a user",
        tags=["freelance", "state"]
    )
    async def get_state_skill(self, user_identifier: str) -> Dict[str, Any]:
        """
        Get the state for a user.

        Args:
            user_identifier: Unique ID for the user/tenant.

        Returns:
            A dictionary containing the user's state.
        """
        logger.info(f"Getting state for user: {user_identifier}")

        try:
            state = await self._get_state(user_identifier)
            return {
                "success": True,
                "message": f"Retrieved state for {user_identifier}.",
                "state": state
            }

        except Exception as e:
            logger.error(f"Error getting state for {user_identifier}: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"Error getting state for {user_identifier}: {str(e)}"
            }

    @skill(
        name="update_state",
        description="Update the state for a user",
        tags=["freelance", "state"]
    )
    async def update_state_skill(self, user_identifier: str, new_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update the state for a user.

        Args:
            user_identifier: Unique ID for the user/tenant.
            new_state: The new state to set.

        Returns:
            A dictionary indicating success or failure.
        """
        logger.info(f"Updating state for user: {user_identifier}")

        try:
            await self._update_state(user_identifier, new_state)
            return {
                "success": True,
                "message": f"State updated successfully for {user_identifier}."
            }

        except Exception as e:
            logger.error(f"Error updating state for {user_identifier}: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"Error updating state for {user_identifier}: {str(e)}"
            }

# Example of how to run this agent as a standalone A2A server
if __name__ == "__main__":
    # Create the agent
    agent = FreelanceTaskAgent()

    # Run the A2A server
    agent.run_server(host="0.0.0.0", port=agent.port or 8011)