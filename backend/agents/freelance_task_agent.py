"""
Freelance Task Agent for Decision Points (ADK Version).

This agent monitors freelance platforms, analyzes tasks, and potentially bids or executes them using ADK tools.
"""

import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

# Removed google.cloud.secretmanager import
from google.adk.agents import Agent # Use ADK Agent
from google.adk.tools import tool # Import tool decorator

# Removed A2A and BaseSpecializedAgent imports
from app.config import settings
from app.services.db_service import DatabaseService # Keep DB service for state

# Configure logging
logger = logging.getLogger(__name__)

# --- Constants ---
AGENT_NAME = "freelance_tasker_adk" # ADK specific name
STATE_KEY = "freelance_state" # Key for storing state in DB
# Removed SECRET_PREFIX constant

# --- Global Clients (Consider better dependency injection for production) ---
# Removed GCP_PROJECT_ID constant
DB_SERVICE = DatabaseService() # Instantiate DB service

# Removed SECRET_MANAGER_CLIENT initialization

# --- Helper Functions ---

# Removed _get_platform_credentials helper function

async def _get_state(user_identifier: str) -> dict:
    """Retrieves the agent's state for a specific user from PostgreSQL."""
    try:
        # Use the global DB_SERVICE instance
        state_data = await DB_SERVICE.get_agent_state(
            agent_id=AGENT_NAME, # Use the ADK agent name
            user_identifier=user_identifier,
            state_key=STATE_KEY
        )
        if not state_data:
            logger.info(f"No state found for {user_identifier}. Returning empty state.")
            return {}
        return state_data
    except Exception as e:
        logger.error(f"Error retrieving state for {user_identifier}: {e}", exc_info=True)
        # Return error dict to be handled by the tool
        return {"error": f"Failed to fetch state: {e}"}

async def _update_state(user_identifier: str, new_state_value: dict) -> bool:
    """Updates the agent's state for a specific user in PostgreSQL."""
    try:
        # Use the global DB_SERVICE instance
        await DB_SERVICE.update_agent_state(
            agent_id=AGENT_NAME, # Use the ADK agent name
            user_identifier=user_identifier,
            state_key=STATE_KEY,
            state_data=new_state_value
        )
        logger.info(f"State updated for {user_identifier}.")
        return True
    except Exception as e:
        logger.error(f"Error updating state for {user_identifier}: {e}", exc_info=True)
        return False # Indicate failure to the tool

# --- ADK Tool Definitions ---

@tool(description="Monitor freelance platforms (e.g., Upwork) based on criteria and potentially bid on matching tasks.")
async def monitor_and_bid_tool(
    user_identifier: str,
    platform: str,
    criteria: Dict[str, Any],
    # Removed secret_id_suffix parameter
) -> Dict[str, Any]:
    """
    ADK Tool: Monitor freelance platforms and bid on matching tasks.
    Reads credentials from environment variables via settings.
    """
    logger.info(f"Tool: [{user_identifier}] Monitoring {platform} with criteria: {criteria}")

    # Read credentials directly from settings (populated by environment variables)
    # Assuming settings has attributes like UPWORK_API_KEY, FIVERR_API_KEY etc.
    # This needs to be mapped based on the 'platform' input.
    credentials = None
    if platform.lower() == 'upwork':
        credentials = settings.UPWORK_API_KEY # Assuming this exists in settings
    elif platform.lower() == 'fiverr':
        credentials = settings.FIVERR_API_KEY # Assuming this exists in settings
    # Add other platforms as needed

    if not credentials:
        return {"success": False, "error": f"Credentials for platform '{platform}' not found in environment variables."}

    try:
        # TODO: Implement actual platform monitoring and bidding logic using credentials
        logger.warning("Placeholder: Actual platform monitoring and bidding logic not implemented.")
        bids_placed_count = 0 # Placeholder

        # Update state (example)
        current_state = await _get_state(user_identifier)
        if "error" in current_state: # Handle state retrieval error
             return {"success": False, "error": f"Failed to get current state: {current_state['error']}"}

        current_state.setdefault('monitoring', {})[platform] = {'status': 'active', 'last_run': datetime.now().isoformat()}
        if not await _update_state(user_identifier, current_state):
             # Log warning but proceed, state update isn't critical for the *result* here
             logger.warning(f"Failed to update state for {user_identifier} after monitoring.")

        # TODO: Consider replacing Pub/Sub with ADK event emission if appropriate for the workflow

        return {
            "success": True,
            "message": f"Placeholder: Monitoring and bidding initiated for {platform}. Bids placed (placeholder): {bids_placed_count}",
            "status": "monitoring_started",
            "platform": platform,
            "criteria": criteria,
            "bids_placed_count": bids_placed_count
        }

    except Exception as e:
        logger.error(f"Tool: Error monitoring and bidding on {platform}: {e}", exc_info=True)
        return {"success": False, "error": f"Error monitoring/bidding on {platform}: {str(e)}"}

@tool(description="Execute a freelance task based on provided details.")
async def execute_task_tool(
    user_identifier: str,
    task_details: Dict[str, Any]
) -> Dict[str, Any]:
    """
    ADK Tool: Execute a freelance task.
    """
    task_id = task_details.get("id", "unknown")
    logger.info(f"Tool: [{user_identifier}] Executing task: {task_id} - {task_details.get('description', 'No description')}")

    try:
        # TODO: Implement actual task execution logic.
        # This might involve LLMs, other agents (via context.invoke_agent), platform APIs.
        logger.warning("Placeholder: Actual task execution logic not implemented.")
        task_result_summary = "Placeholder: Task completed successfully." # Placeholder

        # Update state (example)
        current_state = await _get_state(user_identifier)
        if "error" in current_state:
             return {"success": False, "error": f"Failed to get current state before task update: {current_state['error']}"}

        current_state.setdefault('tasks', {})[task_id] = {
            'status': 'completed', # Assuming completion for placeholder
            'last_update': datetime.now().isoformat(),
            'result_summary': task_result_summary
        }
        if not await _update_state(user_identifier, current_state):
             logger.warning(f"Failed to update state for {user_identifier} after task execution.")

        # TODO: Consider replacing Pub/Sub with ADK event emission

        return {
            "success": True,
            "message": f"Placeholder: Task execution completed for task {task_id}.",
            "status": "execution_completed",
            "task_id": task_id,
            "result_summary": task_result_summary
        }

    except Exception as e:
        logger.error(f"Tool: Error executing task {task_id}: {e}", exc_info=True)
        # Attempt to update state to failed
        try:
            current_state = await _get_state(user_identifier)
            if "error" not in current_state:
                 current_state.setdefault('tasks', {})[task_id] = {
                     'status': 'failed',
                     'last_update': datetime.now().isoformat(),
                     'error': str(e)
                 }
                 await _update_state(user_identifier, current_state)
        except Exception as state_e:
             logger.error(f"Tool: Failed to update state to FAILED for task {task_id}: {state_e}")

        return {"success": False, "error": f"Error executing task {task_id}: {str(e)}"}

@tool(description="Get the stored state for a specific user.")
async def get_state_tool(user_identifier: str) -> Dict[str, Any]:
    """
    ADK Tool: Get the state for a user.
    """
    logger.info(f"Tool: Getting state for user: {user_identifier}")
    try:
        state = await _get_state(user_identifier)
        if "error" in state:
             return {"success": False, "error": state["error"]}
        else:
             return {"success": True, "message": f"Retrieved state for {user_identifier}.", "state": state}
    except Exception as e:
        logger.error(f"Tool: Error getting state for {user_identifier}: {e}", exc_info=True)
        return {"success": False, "error": f"Error getting state: {str(e)}"}

@tool(description="Update the stored state for a specific user.")
async def update_state_tool(user_identifier: str, new_state: Dict[str, Any]) -> Dict[str, Any]:
    """
    ADK Tool: Update the state for a user.
    """
    logger.info(f"Tool: Updating state for user: {user_identifier}")
    try:
        if not isinstance(new_state, dict):
             return {"success": False, "error": "Invalid 'new_state' provided. Must be a dictionary."}

        success = await _update_state(user_identifier, new_state)
        if success:
            return {"success": True, "message": f"State updated successfully for {user_identifier}."}
        else:
            return {"success": False, "error": f"Failed to update state for {user_identifier} (database error)."}
    except Exception as e:
        logger.error(f"Tool: Error updating state for {user_identifier}: {e}", exc_info=True)
        return {"success": False, "error": f"Error updating state: {str(e)}"}


# --- Instantiate the ADK Agent ---
agent = Agent(
    name=AGENT_NAME,
    description="Monitors freelance platforms, analyzes tasks, manages state, and potentially bids or executes tasks.",
    tools=[
        monitor_and_bid_tool,
        execute_task_tool,
        get_state_tool,
        update_state_tool,
    ],
)

# Removed A2A server specific code and old class structure
