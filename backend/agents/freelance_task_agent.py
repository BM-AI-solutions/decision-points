import json
from google.cloud import firestore, pubsub_v1, secretmanager
from google.adk.agents import LlmAgent, BaseAgent  # Assuming Agent is the base, LlmAgent might be needed later
from google.adk.runtime.event import Event, EventSeverity
from google.adk.runtime.invocation_context import InvocationContext
from backend.utils.logger import setup_logger

class FreelanceTaskAgent(BaseAgent):
    """
    ADK-compliant agent to monitor freelance platforms, analyze tasks, and potentially bid or execute them.
    - Interacts with freelance platform APIs (e.g., Upwork, Fiverr).
    - Manages state related to freelance activities.
    - Uses Secret Manager for platform credentials.
    - Communicates results and events using ADK mechanisms.
    """

    # Configuration keys (consider moving to a central config)
    CONFIG_GCP_PROJECT_ID = "gcp_project_id"
    CONFIG_FIRESTORE_COLLECTION = "firestore_collection"
    CONFIG_FIRESTORE_STATE_FIELD = "firestore_state_field"
    CONFIG_PUBSUB_TOPIC = "pubsub_topic"
    CONFIG_SECRET_PREFIX = "secret_prefix" # e.g., "freelance-credentials-"

    DEFAULT_FIRESTORE_COLLECTION = "agentStates" # Example ADK-style collection
    DEFAULT_FIRESTORE_STATE_FIELD = "freelanceTaskState"
    DEFAULT_PUBSUB_TOPIC = "freelance-task-events" # Keep prototype topic for now

    def __init__(self, config: dict | None = None):
        super().__init__(config)
        self.logger = setup_logger(f"FreelanceTaskAgent-{self.agent_id}") # Use ADK agent_id

        # --- Configuration ---
        resolved_config = self.resolve_config(config or {})
        self.gcp_project_id = resolved_config.get(self.CONFIG_GCP_PROJECT_ID)
        if not self.gcp_project_id:
            # Attempt to get from environment or default project discovery if needed
            # For now, raise error if not provided explicitly in config
            raise ValueError(f"Missing required configuration: {self.CONFIG_GCP_PROJECT_ID}")

        self.firestore_collection = resolved_config.get(self.CONFIG_FIRESTORE_COLLECTION, self.DEFAULT_FIRESTORE_COLLECTION)
        self.firestore_state_field = resolved_config.get(self.CONFIG_FIRESTORE_STATE_FIELD, self.DEFAULT_FIRESTORE_STATE_FIELD)
        self.pubsub_topic = resolved_config.get(self.CONFIG_PUBSUB_TOPIC, self.DEFAULT_PUBSUB_TOPIC)
        self.secret_prefix = resolved_config.get(self.CONFIG_SECRET_PREFIX, "freelance-credentials-")

        # --- Client Initialization ---
        try:
            self.db = firestore.Client(project=self.gcp_project_id)
            # Pub/Sub publisher might be replaced by self.emit_event for ADK-native events
            self.pubsub_publisher = pubsub_v1.PublisherClient()
            self.secret_manager_client = secretmanager.SecretManagerServiceClient()
            self.logger.info("Firestore, Pub/Sub Publisher, and Secret Manager clients initialized.")
        except Exception as e:
            self.logger.error(f"Failed to initialize GCP clients: {e}", exc_info=True)
            # Decide on error handling: raise, log and continue with limited functionality?
            raise RuntimeError(f"Failed to initialize GCP clients: {e}") from e

    async def run_async(self, context: InvocationContext) -> Event | list[Event]:
        """
        Main execution logic for the FreelanceTaskAgent.
        Expects context parameters like 'action', 'user_identifier', 'platform', 'criteria', 'task_details', 'secret_id_suffix'.
        """
        self.logger.info(f"Received invocation: {context.invocation_id} with params: {context.params}")

        action = context.params.get("action")
        user_identifier = context.params.get("user_identifier") # Unique ID for the user/tenant

        if not user_identifier:
            return self._create_error_event(context, "Missing 'user_identifier' in invocation parameters.")
        if not action:
            return self._create_error_event(context, "Missing 'action' in invocation parameters.")

        try:
            if action == "monitor_and_bid":
                platform = context.params.get("platform")
                criteria = context.params.get("criteria")
                secret_id_suffix = context.params.get("secret_id_suffix") # e.g., "upwork-api-key"
                if not platform or not criteria or not secret_id_suffix:
                    return self._create_error_event(context, "Missing parameters for 'monitor_and_bid' action.")
                result_event = await self._handle_monitor_and_bid(context, user_identifier, platform, criteria, secret_id_suffix)

            elif action == "execute_task":
                task_details = context.params.get("task_details")
                if not task_details:
                     return self._create_error_event(context, "Missing 'task_details' for 'execute_task' action.")
                result_event = await self._handle_execute_task(context, user_identifier, task_details)

            elif action == "get_state":
                 state = self._get_state(user_identifier)
                 result_event = Event(
                     invocation_context=context,
                     payload={"state": state},
                     severity=EventSeverity.INFO,
                     message=f"Retrieved state for {user_identifier}."
                 )

            elif action == "update_state":
                new_state = context.params.get("new_state")
                if new_state is None: # Allow empty dict {}
                    return self._create_error_event(context, "Missing 'new_state' for 'update_state' action.")
                self._update_state(user_identifier, new_state)
                result_event = Event(
                    invocation_context=context,
                    payload={"success": True},
                    severity=EventSeverity.INFO,
                    message=f"State updated successfully for {user_identifier}."
                )
            else:
                result_event = self._create_error_event(context, f"Unsupported action: {action}")

            return result_event

        except Exception as e:
            self.logger.error(f"Error during run_async for invocation {context.invocation_id}: {e}", exc_info=True)
            return self._create_error_event(context, f"An unexpected error occurred: {e}")

    def _get_state_ref(self, user_identifier: str):
        """Gets the Firestore document reference for the user's state."""
        # Using user_identifier as the document ID within the configured collection
        return self.db.collection(self.firestore_collection).document(user_identifier)

    def _get_state(self, user_identifier: str) -> dict:
        """Retrieves the specific freelance state field for the user."""
        try:
            doc_ref = self._get_state_ref(user_identifier)
            doc = doc_ref.get()
            if doc.exists:
                return doc.to_dict().get(self.firestore_state_field, {})
            self.logger.info(f"No state document found for {user_identifier} in {self.firestore_collection}.")
            return {}
        except Exception as e:
            self.logger.error(f"Error fetching state for {user_identifier}: {e}", exc_info=True)
            # Depending on requirements, might re-raise or return specific error indicator
            return {"error": f"Failed to fetch state: {e}"}

    def _update_state(self, user_identifier: str, new_state_value: dict):
        """Updates the specific freelance state field for the user."""
        try:
            doc_ref = self._get_state_ref(user_identifier)
            # Set the specific field within the document, merging with existing document data
            doc_ref.set({self.firestore_state_field: new_state_value}, merge=True)
            self.logger.info(f"State updated for {user_identifier} in field {self.firestore_state_field}.")
        except Exception as e:
            self.logger.error(f"Error updating state for {user_identifier}: {e}", exc_info=True)
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
        current_state = self._get_state(user_identifier)
        current_state.setdefault('monitoring', {})[platform] = {'status': 'active', 'last_run': firestore.SERVER_TIMESTAMP}
        self._update_state(user_identifier, current_state)

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
        current_state = self._get_state(user_identifier)
        current_state.setdefault('tasks', {})[task_details.get('id', 'unknown')] = {'status': 'in_progress', 'last_update': firestore.SERVER_TIMESTAMP}
        self._update_state(user_identifier, current_state)

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
        self.logger.error(f"Error for invocation {context.invocation_id}: {message}")
        return Event(
            invocation_context=context,
            payload={"error": message},
            severity=EventSeverity.ERROR,
            message=message
        )

    # Note: The prototype's receive_events and enforce_user_context are handled differently
    # in ADK. Event reception is managed by the runtime, and context is passed per invocation.
    # Multi-tenancy is handled by ensuring user_identifier is used correctly for state and credentials.

# Example Configuration (would typically come from app config or environment)
# agent_config = {
#     "gcp_project_id": "your-gcp-project-id",
#     "firestore_collection": "adkAgentStates",
#     "firestore_state_field": "freelanceData",
#     "pubsub_topic": "freelance-agent-updates",
#     "secret_prefix": "user-freelance-api-"
# }

# Example Invocation Context Params:
# context_params_monitor = {
#     "action": "monitor_and_bid",
#     "user_identifier": "user_123",
#     "platform": "Upwork",
#     "criteria": {"keywords": ["python", "api"], "min_budget": 100},
#     "secret_id_suffix": "upwork-key"
# }
# context_params_execute = {
#     "action": "execute_task",
#     "user_identifier": "user_456",
#     "task_details": {"id": "task_abc", "description": "Write API documentation", "platform": "Fiverr"},
#     "secret_id_suffix": "fiverr-key" # May or may not be needed depending on execution step
# }
# context_params_state = {
#     "action": "get_state",
#     "user_identifier": "user_123"
# }