import time
import uuid
from flask_socketio import SocketIO
from utils.logger import setup_logger

logger = setup_logger('agents.orchestrator')

class OrchestratorAgent:
    """
    Simplified orchestrator agent for handling tasks via Flask/SocketIO.
    Manages tasks and emits updates via SocketIO.
    """

    def __init__(self, socketio: SocketIO):
        """
        Initializes the Orchestrator Agent.

        Args:
            socketio: The Flask-SocketIO instance.
        """
        self.socketio = socketio
        logger.info("OrchestratorAgent initialized with SocketIO.")
        # In-memory store for task statuses (replace with persistent storage if needed)
        self.tasks = {}

    def process_task(self, task_data: dict):
        """
        Processes a task request received, logs it, and emits updates via SocketIO.

        Args:
            task_data: A dictionary containing task details (e.g., 'prompt').
        """
        task_id = str(uuid.uuid4()) # Generate a unique ID for the task
        prompt = task_data.get("prompt", "No prompt provided")
        logger.info(f"OrchestratorAgent received task {task_id} with prompt: '{prompt}'")

        # Store initial task state
        self.tasks[task_id] = {"status": "received", "prompt": prompt}

        # Emit initial acknowledgment via SocketIO
        self.socketio.emit('task_update', {
            'task_id': task_id,
            'status': 'received',
            'message': f"Task received: {prompt}"
        })
        logger.info(f"Emitted 'task_update' (received) for task {task_id}")

        # Simulate some processing time
        time.sleep(2) # Simulate work being done

        # TODO: Replace with actual task processing logic (e.g., calling other agents/services)
        processed_message = f"Processing complete for prompt: '{prompt}'"
        self.tasks[task_id]['status'] = 'processing'
        self.tasks[task_id]['message'] = processed_message

        # Emit processing update
        self.socketio.emit('task_update', {
            'task_id': task_id,
            'status': 'processing',
            'message': processed_message
        })
        logger.info(f"Emitted 'task_update' (processing) for task {task_id}")

        # Simulate more processing time
        time.sleep(3)

        # Final result (placeholder)
        final_result = {"details": "Placeholder result after processing."}
        self.tasks[task_id]['status'] = 'completed'
        self.tasks[task_id]['result'] = final_result
        self.tasks[task_id]['message'] = "Task completed successfully (Placeholder)."


        # Emit final completion update
        self.socketio.emit('task_update', {
            'task_id': task_id,
            'status': 'completed',
            'message': self.tasks[task_id]['message'],
            'result': final_result
        })
        logger.info(f"Emitted 'task_update' (completed) for task {task_id}")

        # Optionally clean up old tasks after some time
        # del self.tasks[task_id]

    def get_task_status(self, task_id: str):
        """Retrieves the status of a specific task."""
        return self.tasks.get(task_id, {"status": "not_found", "message": "Task ID not found."})

# Note: Removed ADK-specific code and __main__ block for this simplified version.