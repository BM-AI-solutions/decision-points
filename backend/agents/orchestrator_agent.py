import uuid
import google.generativeai as genai # Add import
from flask_socketio import SocketIO
from utils.logger import setup_logger

logger = setup_logger('agents.orchestrator')

class OrchestratorAgent:
    """
    Simplified orchestrator agent for handling tasks via Flask/SocketIO.
    Manages tasks and emits updates via SocketIO.
    """

    def __init__(self, socketio: SocketIO, model_name: str = 'gemini-pro'): # Add model_name parameter
        """
        Initializes the Orchestrator Agent.

        Args:
            socketio: The Flask-SocketIO instance.
            model_name: The name of the Gemini model to use.
        """
        self.socketio = socketio
        self.model_name = model_name # Store model name
        logger.info(f"OrchestratorAgent initialized with SocketIO and model: {self.model_name}.")
        # In-memory store for task statuses (replace with persistent storage if needed)
        self.tasks = {}

    def process_task(self, task_data: dict):
        """
        Processes a task request received, calls the LLM, and emits updates via SocketIO.

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

        # Emit processing update
        processing_message = f"Processing prompt with {self.model_name}..."
        self.tasks[task_id]['status'] = 'processing'
        self.tasks[task_id]['message'] = processing_message
        self.socketio.emit('task_update', {
            'task_id': task_id,
            'status': 'processing',
            'message': processing_message
        })
        logger.info(f"Emitted 'task_update' (processing) for task {task_id}")

        # --- Call Gemini LLM ---
        try:
            # Ensure API key is configured (check if genai was configured in app.py)
            # Note: A more robust check might involve trying a small API call or checking genai internal state if available
            if not genai.api_key:
                 raise ValueError("GEMINI_API_KEY not configured or google.generativeai not initialized.")

            model = genai.GenerativeModel(self.model_name)
            # Configure safety settings to be less restrictive if needed, e.g.,
            # safety_settings = {
            #     HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            #     HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            #     HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            #     HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            # }
            # response = model.generate_content(prompt, safety_settings=safety_settings)
            response = model.generate_content(prompt)


            # Check for potential issues in the response (e.g., blocked content)
            # Accessing response.text directly might raise if parts are missing/blocked
            try:
                llm_response_text = response.text
            except ValueError as ve:
                 # Handle cases where the response might be empty or blocked by safety filters
                 block_reason = getattr(response.prompt_feedback, 'block_reason', None)
                 if block_reason:
                     error_message = f"LLM response blocked due to: {block_reason.name}"
                     logger.error(f"Task {task_id} failed: {error_message}")
                     raise ValueError(error_message) from ve
                 else:
                     # General empty/invalid response case
                     error_message = f"LLM returned an unusable response: {ve}"
                     logger.error(f"Task {task_id} failed: {error_message}")
                     raise ValueError(error_message) from ve


            # Update task state with LLM response
            self.tasks[task_id]['status'] = 'completed'
            # Store the raw text response in the result field for internal tracking if needed
            # self.tasks[task_id]['result'] = {"llm_response": llm_response_text}
            self.tasks[task_id]['message'] = "Task completed successfully."

            # Emit final completion update with LLM response text
            self.socketio.emit('task_update', {
                'task_id': task_id,
                'status': 'completed',
                'message': self.tasks[task_id]['message'],
                 # Send the actual LLM text response directly in the 'result' field as requested
                'result': llm_response_text
            })
            logger.info(f"Emitted 'task_update' (completed) for task {task_id} with LLM response.")

        except Exception as e:
            error_message = f"LLM processing failed: {str(e)}"
            logger.error(f"Task {task_id} failed: {error_message}", exc_info=True)
            self.tasks[task_id]['status'] = 'error'
            self.tasks[task_id]['message'] = error_message
            self.tasks[task_id]['result'] = None # Indicate no result on error

            # Emit error update
            self.socketio.emit('task_update', {
                'task_id': task_id,
                'status': 'error',
                'message': error_message,
                'result': None # Send None for result on error
            })
            logger.info(f"Emitted 'task_update' (error) for task {task_id}")


        # Optionally clean up old tasks after some time
        # del self.tasks[task_id]

    def get_task_status(self, task_id: str):
        """Retrieves the status of a specific task."""
        return self.tasks.get(task_id, {"status": "not_found", "message": "Task ID not found."})

# Note: Removed ADK-specific code and __main__ block for this simplified version.