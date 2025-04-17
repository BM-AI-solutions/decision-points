from flask import Blueprint, request, jsonify
import uuid
from typing import Dict, Any, List

# Import the shared decorator
from backend.utils.decorators import require_subscription_or_local
from backend.modules.action_agent import ActionAgentManager
from backend.utils.logger import setup_logger

bp = Blueprint('business', __name__, url_prefix='/api/business') # Added url_prefix for consistency
logger = setup_logger('routes.business')
action_agent_manager = ActionAgentManager()

# Mock database for business models - Consider replacing with persistent storage
BUSINESS_MODELS: Dict[str, Dict[str, Any]] = {}

@bp.route('/implement', methods=['POST'])
@require_subscription_or_local
async def implement_business_model(user_id: str): # Add user_id from decorator
    """Implement a business model."""
    try:
        data = request.json

        # Required parameters
        instructions = data.get('instructions')
        business_model = data.get('business_model')
        features = data.get('features')
        # user_id is now passed as an argument by the decorator

        if not instructions:
            return jsonify({
                'error': 'Instructions are required',
                'status': 400
            }), 400

        if not business_model:
            return jsonify({
                'error': 'Business model is required',
                'status': 400
            }), 400

        if not features:
            return jsonify({
                'error': 'Features are required',
                'status': 400
            }), 400

        # Implement the business model
        implementation_result = await action_agent_manager.implement_business_model(
            instructions,
            business_model,
            features,
            user_id
        )

        # Save the business model
        model_id = str(uuid.uuid4())
        BUSINESS_MODELS[model_id] = {
            'id': model_id,
            'user_id': user_id,
            'business_model': business_model,
            'features': features,
            'implementation_result': implementation_result
        }

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
def get_business_model(user_id: str, model_id: str): # Add user_id from decorator
    """Get a business model by ID."""
    try:
        if model_id not in BUSINESS_MODELS:
            return jsonify({
                'error': 'Business model not found',
                'status': 404
            }), 404

        model = BUSINESS_MODELS[model_id]

        # Security check: Ensure the requesting user owns this model
        if model.get('user_id') != user_id:
             logger.warning(f"User {user_id} attempted to access unauthorized model {model_id} owned by {model.get('user_id')}")
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
def list_business_models(user_id: str): # Add user_id from decorator
    """List all business models for a user."""
    try:
        user_models = []

        for model_id, model in BUSINESS_MODELS.items():
            if model['user_id'] == user_id:
                user_models.append({
                    'id': model_id,
                    'business_model': model['business_model'],
                    'features': model['features']
                })

        logger.info(f"Listed business models for user {user_id}")
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