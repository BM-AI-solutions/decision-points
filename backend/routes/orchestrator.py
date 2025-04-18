from flask import Blueprint, request, jsonify, current_app
import jwt
import os
import uuid
from datetime import datetime

from utils.logger import setup_logger
from google.adk.runtime import InvocationContext # Import ADK InvocationContext
# Import necessary components from the main app
# We will instantiate the agent in app.py and import it here
# from backend.app import socketio, orchestrator_agent # Adjusted import path

# Define the Blueprint for orchestrator routes
orchestrator_bp = Blueprint('orchestrator_bp', __name__, url_prefix='/api/orchestrator')

logger = setup_logger('routes.orchestrator')

# Note: Agent instantiation moved to app.py to ensure single instance with socketio

@orchestrator_bp.route('/tasks', methods=['POST'])
def create_orchestrator_task():
    """
    Handles the creation of a new task for the Orchestrator Agent.
    Authenticates the user, validates input, and forwards the task
    to the Orchestrator Agent via a background task.
    Returns an immediate acknowledgment; results are sent via WebSocket.
    """
    # Import here to avoid circular dependency issues at module load time
    # and ensure we get the initialized instances from app context
    try:
        socketio = current_app.extensions['socketio']
        orchestrator_agent = current_app.orchestrator_agent
    except AttributeError:
         logger.error("SocketIO or OrchestratorAgent not initialized or attached to Flask app context.")
         return jsonify({"error": "Server configuration error"}), 500


    # 1. Authentication (Keep existing logic)
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        logger.warning("Orchestrator Task: Missing or invalid Authorization header")
        return jsonify({'error': 'Authorization required', 'status': 401}), 401

    token = auth_header.split(' ')[1]
    secret_key = os.environ.get('JWT_SECRET_KEY', 'dev-jwt-secret-change-in-production')

    try:
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        user_id = payload['user_id']
        logger.info(f"Orchestrator Task: Authenticated user_id: {user_id}")
    except jwt.ExpiredSignatureError:
        logger.warning("Orchestrator Task: JWT token expired")
        return jsonify({'error': 'Token expired', 'status': 401}), 401
    except jwt.InvalidTokenError as e:
        logger.error(f"Orchestrator Task: Invalid JWT token: {str(e)}")
        return jsonify({'error': 'Invalid token', 'status': 401}), 401
    except Exception as e:
         logger.error(f"Orchestrator Task: Error decoding JWT token: {str(e)}", exc_info=True)
         return jsonify({'error': 'Authentication error', 'status': 500}), 500

    # 2. Get and Validate Data
    data = request.get_json()
    # Expect 'prompt' instead of 'goal'
    if not data or 'prompt' not in data:
        logger.warning(f"Orchestrator Task: Missing 'prompt' in request data from user {user_id}")
        return jsonify({"error": "Missing 'prompt' in request data"}), 400

    prompt = data.get('prompt')
    # Add user_id to task_data if needed by the agent later
    task_data = {"prompt": prompt, "user_id": user_id}
    logger.info(f"Orchestrator Task: Received prompt '{prompt}' from user {user_id}")

    # 3. Forward Task to Orchestrator Agent (Run in Background)
    try:
        logger.info(f"Orchestrator Task: Forwarding task for prompt '{prompt}' to Orchestrator Agent using run_async...")

        # Create InvocationContext for ADK agent
        invocation_id = str(uuid.uuid4())
        context = InvocationContext(
            invocation_id=invocation_id,
            invocation_data=task_data # Pass prompt and user_id
        )
        logger.debug(f"Orchestrator Task: Created InvocationContext with ID {invocation_id} and data: {task_data}")

        # Use socketio.start_background_task to run the agent's run_async
        # without blocking the HTTP response.
        socketio.start_background_task(orchestrator_agent.run_async, context)
        logger.info(f"Orchestrator Task: Background task started for invocation_id {invocation_id} (prompt: '{prompt}').")

    except Exception as e:
        logger.error(f"Orchestrator Task: Failed to create context or start background task for agent: {str(e)}", exc_info=True)
        return jsonify({"error": "Failed to submit task to orchestrator"}), 500

    # 4. Return Immediate Acknowledgment
    logger.info(f"Orchestrator Task: Task for prompt '{prompt}' submitted successfully by user {user_id}.")
    # Return 202 Accepted: Request accepted, processing initiated.
    # Client should listen on WebSocket for updates.
    return jsonify({
        "status": "Task received",
        "message": "Task processing initiated. Listen for updates via WebSocket."
    }), 202

# TODO: Add GET /tasks/{taskId} endpoint (could use agent.get_task_status)
# TODO: Add GET /agents endpoint (optional)