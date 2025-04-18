from flask import Blueprint, request, jsonify, abort
import uuid
import jwt
import os
from datetime import datetime
from config import Config
from utils.logger import setup_logger
from models.workflow import Workflow # Import Workflow model

# Only import Google Cloud libraries if billing is required
if Config.BILLING_REQUIRED:
    from google.cloud import datastore
else:
    datastore = None # Mock datastore if not required

# Define the Blueprint for workflow routes
workflows_bp = Blueprint('workflows_bp', __name__, url_prefix='/api/workflows')

logger = setup_logger('routes.workflows')

# Initialize datastore client or in-memory storage
if Config.BILLING_REQUIRED:
    datastore_client = datastore.Client()
    WORKFLOWS = None # Not used when Datastore is active
    WORKFLOW_IDS = None
else:
    datastore_client = None
    WORKFLOWS = {} # workflow_id -> workflow_dict
    WORKFLOW_IDS = {} # user_id -> list of workflow_ids (optional, for potential future lookups)


@workflows_bp.route('/', methods=['POST'])
def create_workflow():
    """
    Handles the creation of a new workflow.
    Receives workflow data, validates it, authenticates the user,
    saves it to the database (Datastore or in-memory), and returns a response.
    """
    # 1. Authentication
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        logger.warning("Missing or invalid Authorization header")
        return jsonify({'error': 'Authorization required', 'status': 401}), 401

    token = auth_header.split(' ')[1]
    secret_key = os.environ.get('JWT_SECRET_KEY', 'dev-jwt-secret-change-in-production')

    try:
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        user_id = payload['user_id']
        logger.info(f"Authenticated user_id: {user_id}")
    except jwt.ExpiredSignatureError:
        logger.warning("JWT token expired")
        return jsonify({'error': 'Token expired', 'status': 401}), 401
    except jwt.InvalidTokenError as e:
        logger.error(f"Invalid JWT token: {str(e)}")
        return jsonify({'error': 'Invalid token', 'status': 401}), 401
    except Exception as e:
         logger.error(f"Error decoding JWT token: {str(e)}", exc_info=True)
         return jsonify({'error': 'Authentication error', 'status': 500}), 500


    # 2. Get and Validate Data
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    # Map frontend names to model names if necessary and validate
    # Assuming frontend sends: workflowName, description, triggerType, actionType
    # Model expects: name, description, trigger_type, action_type
    required_fields = ['workflowName', 'triggerType', 'actionType'] # description is optional
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

    # 3. Generate ID and Create Workflow Instance
    workflow_id = str(uuid.uuid4())
    now = datetime.utcnow()

    try:
        new_workflow = Workflow(
            id=workflow_id,
            user_id=user_id,
            name=data['workflowName'],
            description=data.get('description'), # Optional
            trigger_type=data['triggerType'],
            action_type=data['actionType'],
            created_at=now, # Handled by default_factory, but can be explicit
            updated_at=now  # Handled by default_factory, but can be explicit
        )
        logger.info(f"Created Workflow instance for user {user_id}: ID {workflow_id}")
    except Exception as e: # Catch potential Pydantic validation errors
        logger.error(f"Error creating Workflow instance: {str(e)}", exc_info=True)
        return jsonify({"error": "Invalid workflow data", "details": str(e)}), 400


    # 4. Persist Data
    try:
        if Config.BILLING_REQUIRED:
            logger.info(f"Attempting to save workflow {workflow_id} to Datastore.")
            # Assume .to_entity() exists and works like in auth.py
            # The entity kind is typically the class name, 'Workflow'
            workflow_entity = new_workflow.to_entity(datastore_client, name=workflow_id) # Use workflow_id as key name
            datastore_client.put(workflow_entity)
            logger.info(f"Workflow {workflow_id} saved to Datastore.")
        else:
            logger.info(f"Saving workflow {workflow_id} to in-memory store.")
            # Store as dict for simplicity in local mode
            WORKFLOWS[workflow_id] = new_workflow.dict()
            if user_id not in WORKFLOW_IDS:
                WORKFLOW_IDS[user_id] = []
            WORKFLOW_IDS[user_id].append(workflow_id)
            logger.info(f"Workflow {workflow_id} saved in-memory.")
            logger.debug(f"Current WORKFLOWS keys: {list(WORKFLOWS.keys())}")


        # 5. Return Success Response
        return jsonify({
            "message": "Workflow created successfully",
            "workflow_id": workflow_id
        }), 201

    except AttributeError as e:
         # Specific handling if .to_entity() is indeed missing at runtime
         logger.error(f"Missing '.to_entity()' method on Workflow model: {e}", exc_info=True)
         # Potentially abort or return a specific error indicating a server configuration issue
         return jsonify({"error": "Server configuration error: Persistence method missing."}), 500
    except Exception as e:
        logger.error(f"Error saving workflow {workflow_id}: {str(e)}", exc_info=True)
        # Handle potential Datastore or other persistence errors
        return jsonify({"error": "Failed to save workflow", "details": str(e)}), 500


@workflows_bp.route('/', methods=['GET'])
def get_workflows():
    """
    Handles fetching all workflows for the authenticated user.
    Authenticates the user, queries the datastore/in-memory storage,
    and returns a list of workflows.
    """
    # 1. Authentication (Same as POST)
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        logger.warning("GET /workflows: Missing or invalid Authorization header")
        return jsonify({'error': 'Authorization required', 'status': 401}), 401

    token = auth_header.split(' ')[1]
    secret_key = os.environ.get('JWT_SECRET_KEY', 'dev-jwt-secret-change-in-production')

    try:
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        user_id = payload['user_id']
        logger.info(f"GET /workflows: Authenticated user_id: {user_id}")
    except jwt.ExpiredSignatureError:
        logger.warning("GET /workflows: JWT token expired")
        return jsonify({'error': 'Token expired', 'status': 401}), 401
    except jwt.InvalidTokenError as e:
        logger.error(f"GET /workflows: Invalid JWT token: {str(e)}")
        return jsonify({'error': 'Invalid token', 'status': 401}), 401
    except Exception as e:
         logger.error(f"GET /workflows: Error decoding JWT token: {str(e)}", exc_info=True)
         return jsonify({'error': 'Authentication error', 'status': 500}), 500

    # 2. Fetch Data
    user_workflows = []
    try:
        if Config.BILLING_REQUIRED:
            logger.info(f"GET /workflows: Fetching workflows for user {user_id} from Datastore.")
            query = datastore_client.query(kind='Workflow')
            query.add_filter('user_id', '=', user_id)
            results = list(query.fetch())
            logger.info(f"GET /workflows: Found {len(results)} workflows in Datastore for user {user_id}.")
            # Convert entities to dicts (assuming entities are dict-like or have a method)
            # We might need a Workflow.from_entity method if it exists, or handle manually
            for entity in results:
                # Basic conversion, might need adjustment based on actual entity structure
                workflow_data = dict(entity)
                # Add the key/id if it's not automatically included
                if 'id' not in workflow_data and entity.key:
                    workflow_data['id'] = entity.key.name # Assuming ID was stored as key name
                user_workflows.append(workflow_data)

        else:
            logger.info(f"GET /workflows: Fetching workflows for user {user_id} from in-memory store.")
            # Iterate through the main WORKFLOWS dict and filter by user_id
            for wf_id, wf_data in WORKFLOWS.items():
                if wf_data.get('user_id') == user_id:
                    # Ensure the ID is part of the returned dict
                    if 'id' not in wf_data:
                         wf_data['id'] = wf_id
                    user_workflows.append(wf_data)
            logger.info(f"GET /workflows: Found {len(user_workflows)} workflows in-memory for user {user_id}.")
            logger.debug(f"GET /workflows: In-memory WORKFLOWS keys: {list(WORKFLOWS.keys())}")

        # 3. Return Response
        return jsonify(user_workflows), 200

    except Exception as e:
        logger.error(f"GET /workflows: Error fetching workflows for user {user_id}: {str(e)}", exc_info=True)
        return jsonify({"error": "Failed to fetch workflows", "details": str(e)}), 500
