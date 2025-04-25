import json
import os
import logging
import argparse # Added for server args
import asyncio
from typing import Dict, List, Any, Optional

import uvicorn # Added for server
from fastapi import FastAPI, HTTPException, Body # Added for server
from pydantic import BaseModel, Field # Added for server models

# Assuming ADK and GCP libraries are installed
from google.cloud import firestore, pubsub_v1, secretmanager
from google.adk.agents import BaseAgent # Using BaseAgent as per original
from google.adk.runtime import InvocationContext
from google.adk.runtime.events import Event, EventSeverity

# Configure logging
# Use logfire if configured globally, otherwise standard logging
try:
    import logfire
    # Assuming logfire is configured elsewhere
    logger = logfire
except ImportError:
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO"))


# --- Pydantic Models for FastAPI ---

class FreelanceTaskInput(BaseModel):
    """Input model for the /invoke endpoint."""
    action: str = Field(description="Action to perform (e.g., 'monitor_and_bid', 'execute_task', 'get_state', 'update_state').")
    user_identifier: str = Field(description="Unique identifier for the user/tenant.")
    # Optional fields used by different actions
    platform: Optional[str] = Field(None, description="Freelance platform (e.g., 'Upwork', 'Fiverr').")
    criteria: Optional[Dict[str, Any]] = Field(None, description="Criteria for monitoring/bidding.")
    secret_id_suffix: Optional[str] = Field(None, description="Suffix for Secret Manager ID (e.g., 'upwork-key').")
    task_details: Optional[Dict[str, Any]] = Field(None, description="Details of the task to execute.")
    new_state: Optional[Dict[str, Any]] = Field(None, description="New state data to update.")

# Output can be dynamic based on the event payload, often a Dict[str, Any]
# We can define a generic output or handle it in the endpoint.
class FreelanceTaskOutput(BaseModel):
    """Generic output model, actual content depends on the event payload."""
    payload: Dict[str, Any]
    message: Optional[str] = None
    severity: Optional[str] = None # Map EventSeverity enum if needed


# --- Agent Class ---

class FreelanceTaskAgent(BaseAgent):
    """
    ADK-compliant agent to monitor freelance platforms, analyze tasks, and potentially bid or execute them.
    """
    # Configuration keys (using environment variables primarily now)
    ENV_GCP_PROJECT_ID = "GCP_PROJECT_ID"
    ENV_FIRESTORE_COLLECTION = "FTA_FIRESTORE_COLLECTION"
    ENV_FIRESTORE_STATE_FIELD = "FTA_FIRESTORE_STATE_FIELD"
    ENV_PUBSUB_TOPIC = "FTA_PUBSUB_TOPIC"
    ENV_SECRET_PREFIX = "FTA_SECRET_PREFIX"

    DEFAULT_FIRESTORE_COLLECTION = "agentStates"
    DEFAULT_FIRESTORE_STATE_FIELD = "freelanceTaskState"
    DEFAULT_PUBSUB_TOPIC = "freelance-task-events"
    DEFAULT_SECRET_PREFIX = "freelance-credentials-"

    def __init__(self, agent_id: str = "freelance-task-agent"):
        """Initialize agent, reading config from environment variables."""
        super().__init__(agent_id=agent_id) # Pass agent_id
        logger.info(f"Initializing FreelanceTaskAgent ({self.agent_id})...")

        # --- Configuration from Environment ---
        self.gcp_project_id = os.environ.get(self.ENV_GCP_PROJECT_ID)
        if not self.gcp_project_id:
            # Attempt standard GCP project discovery if needed, or raise error
            logger.warning(f"{self.ENV_GCP_PROJECT_ID} not set. Attempting default discovery...")
            # For server context, explicit config is often better. Raising for now.
            raise ValueError(f"Missing required environment variable: {self.ENV_GCP_PROJECT_ID}")

        self.firestore_collection = os.environ.get(self.ENV_FIRESTORE_COLLECTION, self.DEFAULT_FIRESTORE_COLLECTION)
        self.firestore_state_field = os.environ.get(self.ENV_FIRESTORE_STATE_FIELD, self.DEFAULT_FIRESTORE_STATE_FIELD)
        self.pubsub_topic = os.environ.get(self.ENV_PUBSUB_TOPIC, self.DEFAULT_PUBSUB_TOPIC)
        self.secret_prefix = os.environ.get(self.ENV_SECRET_PREFIX, self.DEFAULT_SECRET_PREFIX)

        logger.info(f"  GCP Project: {self.gcp_project_id}")
        logger.info(f"  Firestore Collection: {self.firestore_collection}")
        logger.info(f"  Firestore State Field: {self.firestore_state_field}")
        logger.info(f"  Pub/Sub Topic: {self.pubsub_topic}")
        logger.info(f"  Secret Prefix: {self.secret_prefix}")

        # --- Client Initialization ---
        try:
            self.db = firestore.Client(project=self.gcp_project_id)
            self.pubsub_publisher = pubsub_v1.PublisherClient()
            self.secret_manager_client = secretmanager.SecretManagerServiceClient()
            logger.info("Firestore, Pub/Sub Publisher, and Secret Manager clients initialized.")
        except Exception as e:
            logger.error(f"Failed to initialize GCP clients: {e}", exc_info=True)
            raise RuntimeError(f"Failed to initialize GCP clients: {e}") from e

    async def run_async(self, context: InvocationContext) -> Event:
        """
        Main execution logic for the FreelanceTaskAgent.
        Reads parameters from context.data dictionary.
        """
        logger.info(f"[{self.agent_id}] Received invocation: {context.invocation_id} with data: {context.data}")

        if not isinstance(context.data, dict):
            return self._create_error_event(context, "Input data must be a dictionary.")

        action = context.data.get("action")
        user_identifier = context.data.get("user_identifier")

        if not user_identifier:
            return self._create_error_event(context, "Missing 'user_identifier' in input data.")
        if not action:
            return self._create_error_event(context, "Missing 'action' in input data.")

        try:
            if action == "monitor_and_bid":
                platform = context.data.get("platform")
                criteria = context.data.get("criteria")
                secret_id_suffix = context.data.get("secret_id_suffix")
                if not platform or not criteria or not secret_id_suffix:
                    return self._create_error_event(context, "Missing parameters for 'monitor_and_bid' action.")
                result_event = await self._handle_monitor_and_bid(context, user_identifier, platform, criteria, secret_id_suffix)

            elif action == "execute_task":
                task_details = context.data.get("task_details")
                if not task_details:
                     return self._create_error_event(context, "Missing 'task_details' for 'execute_task' action.")
                result_event = await self._handle_execute_task(context, user_identifier, task_details)

            elif action == "get_state":
                 state = self._get_state(user_identifier)
                 result_event = context.create_event( # Use context helper
                     event_type="adk.agent.result",
                     data={"state": state},
                     metadata={"status": "success", "message": f"Retrieved state for {user_identifier}."}
                 )

            elif action == "update_state":
                new_state = context.data.get("new_state")
                if new_state is None: # Allow empty dict {}
                    return self._create_error_event(context, "Missing 'new_state' for 'update_state' action.")
                self._update_state(user_identifier, new_state)
                result_event = context.create_event(
                    event_type="adk.agent.result",
                    data={"success": True},
                    metadata={"status": "success", "message": f"State updated successfully for {user_identifier}."}
                )
            else:
                result_event = self._create_error_event(context, f"Unsupported action: {action}")

            return result_event

        except Exception as e:
            logger.error(f"Error during run_async for invocation {context.invocation_id}: {e}", exc_info=True)
            return self._create_error_event(context, f"An unexpected error occurred: {e}")

    # --- Helper Methods (State, Credentials, Handlers) ---
    # ... (Keep existing helper methods: _get_state_ref, _get_state, _update_state, _get_platform_credentials) ...
    # ... (_handle_monitor_and_bid, _handle_execute_task, _publish_event, _create_error_event) ...
    # --- Ensure logging uses 'logger' instance ---
    def _get_state_ref(self, user_identifier: str):
        """Gets the Firestore document reference for the user's state."""
        return self.db.collection(self.firestore_collection).document(user_identifier)

    def _get_state(self, user_identifier: str) -> dict:
        """Retrieves the specific freelance state field for the user."""
        try:
            doc_ref = self._get_state_ref(user_identifier)
            doc = doc_ref.get()
            if doc.exists:
                return doc.to_dict().get(self.firestore_state_field, {})
            logger.info(f"No state document found for {user_identifier} in {self.firestore_collection}.")
            return {}
        except Exception as e:
            logger.error(f"Error fetching state for {user_identifier}: {e}", exc_info=True)
            return {"error": f"Failed to fetch state: {e}"}

    def _update_state(self, user_identifier: str, new_state_value: dict):
        """Updates the specific freelance state field for the user."""
        try:
            doc_ref = self._get_state_ref(user_identifier)
            doc_ref.set({self.firestore_state_field: new_state_value}, merge=True)
            logger.info(f"State updated for {user_identifier} in field {self.firestore_state_field}.")
        except Exception as e:
            logger.error(f"Error updating state for {user_identifier}: {e}", exc_info=True)
            raise RuntimeError(f"Failed to update state for {user_identifier}: {e}") from e

    def _get_platform_credentials(self, user_identifier: str, secret_id_suffix: str) -> str | None:
        """Retrieves platform credentials from Secret Manager."""
        secret_id = f"{self.secret_prefix}{user_identifier}-{secret_id_suffix}"
        try:
            name = f"projects/{self.gcp_project_id}/secrets/{secret_id}/versions/latest"
            logger.info(f"Attempting to access secret: {name}")
            response = self.secret_manager_client.access_secret_version(request={"name": name})
            credentials = response.payload.data.decode("UTF-8")
            logger.info(f"Successfully retrieved credentials for secret suffix {secret_id_suffix} for user {user_identifier}")
            return credentials
        except Exception as e:
            logger.error(f"Error retrieving credentials for secret {secret_id}: {e}", exc_info=True)
            return None

    async def _handle_monitor_and_bid(self, context: InvocationContext, user_identifier: str, platform: str, criteria: dict, secret_id_suffix: str) -> Event:
        """Placeholder for monitoring and bidding logic."""
        logger.info(f"[{user_identifier}] Monitoring {platform} with criteria: {criteria}")
        credentials = self._get_platform_credentials(user_identifier, secret_id_suffix)
        if not credentials:
            return self._create_error_event(context, f"Failed to retrieve credentials for platform {platform} (secret suffix: {secret_id_suffix}).")

        # TODO: Implement actual platform monitoring and bidding logic
        result_payload = {
            "status": "monitoring_started", "platform": platform, "criteria": criteria,
            "message": "Placeholder: Monitoring and bidding logic initiated."
        }
        logger.info(f"Placeholder: Monitoring complete for {platform}.")
        current_state = self._get_state(user_identifier)
        current_state.setdefault('monitoring', {})[platform] = {'status': 'active', 'last_run': firestore.SERVER_TIMESTAMP}
        self._update_state(user_identifier, current_state)
        return context.create_event(
            event_type="adk.agent.result", data=result_payload,
            metadata={"status": "success", "message": f"Monitoring and bidding initiated for {platform}."}
        )

    async def _handle_execute_task(self, context: InvocationContext, user_identifier: str, task_details: dict) -> Event:
        """Placeholder for executing a freelance task."""
        logger.info(f"[{user_identifier}] Executing task: {task_details}")
        # TODO: Implement actual task execution logic
        result_payload = {
            "status": "execution_initiated", "task_id": task_details.get("id", "unknown"),
            "message": "Placeholder: Task execution logic initiated."
        }
        logger.info(f"Placeholder: Task execution complete for task {task_details.get('id', 'unknown')}.")
        current_state = self._get_state(user_identifier)
        current_state.setdefault('tasks', {})[task_details.get('id', 'unknown')] = {'status': 'in_progress', 'last_update': firestore.SERVER_TIMESTAMP}
        self._update_state(user_identifier, current_state)
        self._publish_event(user_identifier, {"event": "task_execution_started", "task_details": task_details})
        return context.create_event(
            event_type="adk.agent.result", data=result_payload,
            metadata={"status": "success", "message": f"Task execution initiated for task {task_details.get('id', 'unknown')}."}
        )

    def _publish_event(self, user_identifier: str, event_data: dict):
        """Publishes an event to the configured Pub/Sub topic."""
        try:
            topic_path = self.pubsub_publisher.topic_path(self.gcp_project_id, self.pubsub_topic)
            future = self.pubsub_publisher.publish(
                topic_path, data=json.dumps(event_data).encode("utf-8"),
                user_identifier=user_identifier
            )
            future.result()
            logger.info(f"Published event to {self.pubsub_topic} for user {user_identifier}: {event_data.get('event')}")
        except Exception as e:
            logger.error(f"Error publishing event to {self.pubsub_topic} for {user_identifier}: {e}", exc_info=True)

    def _create_error_event(self, context: InvocationContext, message: str) -> Event:
        """Helper to create a standardized error Event using context."""
        logger.error(f"Error for invocation {context.invocation_id}: {message}")
        return context.create_event(
            event_type="adk.agent.error",
            data={"error": message},
            metadata={"status": "error", "message": message}
        )


# --- FastAPI Server Setup ---

app = FastAPI(title="FreelanceTaskAgent A2A Server")

# Instantiate the agent (reads env vars internally)
# Ensure necessary ENV VARS are set (e.g., GCP_PROJECT_ID)
try:
    freelance_agent_instance = FreelanceTaskAgent()
except ValueError as e:
    logger.critical(f"Failed to initialize FreelanceTaskAgent: {e}. Server cannot start.", exc_info=True)
    # Exit or prevent server start if agent init fails critically
    import sys
    sys.exit(f"Agent Initialization Error: {e}")


@app.post("/invoke") # Response model can be dynamic based on event payload
async def invoke_agent(request: FreelanceTaskInput = Body(...)):
    """
    A2A endpoint to invoke the FreelanceTaskAgent.
    Expects JSON body matching FreelanceTaskInput.
    Returns the payload of the resulting ADK Event.
    """
    logger.info(f"FreelanceTaskAgent /invoke called for action: {request.action}, user: {request.user_identifier}")
    invocation_id = f"freelance-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(1000,9999)}"
    context = InvocationContext(agent_id="freelance-task-agent", invocation_id=invocation_id, data=request.model_dump())

    try:
        result_event = await freelance_agent_instance.run_async(context)

        if result_event and isinstance(result_event.data, dict):
            if result_event.metadata.get("status") == "error":
                 logger.error(f"FreelanceTaskAgent run_async returned error event: {result_event.data.get('error')}")
                 # Return the error payload, potentially raising HTTPException based on severity/type
                 raise HTTPException(status_code=500, detail=result_event.data)
            else:
                 logger.info(f"FreelanceTaskAgent returning success result for action: {request.action}")
                 # Return the success payload directly
                 return result_event.data
        else:
            logger.error(f"FreelanceTaskAgent run_async returned None or invalid event data: {result_event}")
            raise HTTPException(status_code=500, detail="Agent execution failed to return a valid event.")

    except HTTPException as http_exc:
        raise http_exc # Re-raise FastAPI exceptions
    except Exception as e:
        logger.error(f"Error during agent invocation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail={"error": f"Internal server error: {e}"})


@app.get("/health")
async def health_check():
    # Add checks for GCP client connectivity if needed
    return {"status": "ok"}

# --- Main execution block ---

if __name__ == "__main__":
    # Load .env for local development if needed
    try:
        from dotenv import load_dotenv
        if load_dotenv():
             logger.info("Loaded .env file for local run.")
        else:
             logger.info("No .env file found or it was empty.")
    except ImportError:
        logger.info("dotenv library not found, skipping .env load.")

    parser = argparse.ArgumentParser(description="Run the FreelanceTaskAgent A2A server.")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind the server to.")
    parser.add_argument("--port", type=int, default=8085, help="Port to run the server on.") # Default matches compose
    args = parser.parse_args()

    # Ensure critical env var is present before starting server
    if not os.environ.get(FreelanceTaskAgent.ENV_GCP_PROJECT_ID):
         print(f"CRITICAL ERROR: Environment variable {FreelanceTaskAgent.ENV_GCP_PROJECT_ID} must be set.")
         import sys
         sys.exit(1)

    print(f"Starting FreelanceTaskAgent A2A server on {args.host}:{args.port}")

    uvicorn.run(app, host=args.host, port=args.port)