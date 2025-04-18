from flask import Blueprint, request, jsonify
import uuid
from typing import Dict, Any, List

# Import the shared decorator
from utils.decorators import require_subscription_or_local
from modules.action_agent import ActionAgentManager
from utils.logger import setup_logger

bp = Blueprint('business', __name__, url_prefix='/api/business') # Added url_prefix for consistency
logger = setup_logger('routes.business')
action_agent_manager = ActionAgentManager()

# Mock database for business models - Consider replacing with persistent storage
BUSINESS_MODELS: Dict[str, Dict[str, Any]] = {}

# Add some sample business models for testing
def initialize_sample_business_models():
    """Initialize sample business models for testing."""
    logger.info("Initializing sample business models")
    
    # Sample model 1
    model_id1 = str(uuid.uuid4())
    BUSINESS_MODELS[model_id1] = {
        'id': model_id1,
        'user_id': 'all_users',  # Special ID that will match any user for demo purposes
        'business_model': 'SaaS Subscription',
        'features': ['User Authentication', 'Payment Processing', 'Dashboard'],
        'implementation_result': 'Successfully implemented SaaS subscription model'
    }
    
    # Sample model 2
    model_id2 = str(uuid.uuid4())
    BUSINESS_MODELS[model_id2] = {
        'id': model_id2,
        'user_id': 'all_users',  # Special ID that will match any user for demo purposes
        'business_model': 'E-commerce Store',
        'features': ['Product Catalog', 'Shopping Cart', 'Checkout'],
        'implementation_result': 'Successfully implemented e-commerce store model'
    }
    
    logger.info(f"Added {len(BUSINESS_MODELS)} sample business models")

# Initialize sample data
initialize_sample_business_models()

@bp.route('/implement', methods=['POST'])
@require_subscription_or_local
async def implement_business_model(user_id: str): # Already async, just adding more logging
    """Implement a business model."""
    try:
        logger.info(f"Implementing business model for user {user_id}")
        data = request.json
        logger.debug(f"Request data: {data}")

        # Required parameters
        instructions = data.get('instructions')
        business_model = data.get('business_model')
        features = data.get('features')
        # user_id is now passed as an argument by the decorator
        
        logger.info(f"Business model: {business_model}, Features count: {len(features) if features else 0}")

        if not instructions:
            logger.warning("Missing instructions parameter")
            return jsonify({
                'error': 'Instructions are required',
                'status': 400
            }), 400

        if not business_model:
            logger.warning("Missing business_model parameter")
            return jsonify({
                'error': 'Business model is required',
                'status': 400
            }), 400

        if not features:
            logger.warning("Missing features parameter")
            return jsonify({
                'error': 'Features are required',
                'status': 400
            }), 400

        # Implement the business model
        logger.info(f"Calling action_agent_manager.implement_business_model")
        implementation_result = await action_agent_manager.implement_business_model(
            instructions,
            business_model,
            features,
            user_id
        )
        logger.debug(f"Implementation result: {implementation_result}")

        # Save the business model
        model_id = str(uuid.uuid4())
        BUSINESS_MODELS[model_id] = {
            'id': model_id,
            'user_id': user_id,
            'business_model': business_model,
            'features': features,
            'implementation_result': implementation_result
        }
        logger.info(f"Saved business model with ID: {model_id}")
        logger.debug(f"BUSINESS_MODELS now contains {len(BUSINESS_MODELS)} models")

        logger.info(f"Business model implemented for user {user_id}")
        return jsonify({
            'success': True,
            'implementation_result': implementation_result,
            'business_model_id': model_id
        })

    except Exception as e:
        logger.error(f"Error implementing business model for user {user_id}: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Error implementing business model',
            'message': str(e),
            'status': 500
        }), 500

@bp.route('/<model_id>', methods=['GET'])
@require_subscription_or_local
async def get_business_model(user_id: str, model_id: str): # Changed to async to match decorator
    """Get a business model by ID."""
    try:
        logger.info(f"Getting business model {model_id} for user {user_id}")
        
        if model_id not in BUSINESS_MODELS:
            logger.warning(f"Business model {model_id} not found")
            return jsonify({
                'error': 'Business model not found',
                'status': 404
            }), 404

        model = BUSINESS_MODELS[model_id]
        logger.debug(f"Found model: {model}")

        # Security check: Ensure the requesting user owns this model or it's a sample model
        model_user_id = model.get('user_id')
        if model_user_id != user_id and model_user_id != 'all_users':
             logger.warning(f"User {user_id} attempted to access unauthorized model {model_id} owned by {model_user_id}")
             return jsonify({'error': 'Forbidden', 'status': 403}), 403

        logger.info(f"Retrieved business model {model_id} for user {user_id}")
        return jsonify({
            'success': True,
            'business_model': model
        })

    except Exception as e:
        logger.error(f"Error retrieving business model {model_id} for user {user_id}: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Error retrieving business model',
            'message': str(e),
            'status': 500
        }), 500

# Changed route to remove user_id from path - get it from JWT via decorator
@bp.route('/list', methods=['GET'])
@require_subscription_or_local
async def list_business_models(user_id: str): # Changed to async to match decorator
    """List all business models for a user."""
    try:
        logger.info(f"Listing business models for user {user_id}")
        logger.info(f"BUSINESS_MODELS contains {len(BUSINESS_MODELS)} models")
        logger.debug(f"BUSINESS_MODELS keys: {list(BUSINESS_MODELS.keys())}")
        
        user_models = []

        for model_id, model in BUSINESS_MODELS.items():
            model_user_id = model.get('user_id')
            logger.debug(f"Checking model {model_id} with user_id {model_user_id}")
            
            # Include models that belong to this user OR have the special 'all_users' ID
            if model_user_id == user_id or model_user_id == 'all_users':
                logger.info(f"Found model {model_id} for user {user_id}")
                user_models.append({
                    'id': model_id,
                    'business_model': model.get('business_model', 'Unknown'),
                    'features': model.get('features', [])
                })

        logger.info(f"Listed {len(user_models)} business models for user {user_id}")
        return jsonify({
            'success': True,
            'business_models': user_models
        })

    except Exception as e:
        logger.error(f"Error listing business models for user {user_id}: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Error listing business models',
            'message': str(e),
            'status': 500
        }), 500