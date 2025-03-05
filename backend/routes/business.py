from flask import Blueprint, request, jsonify
import uuid
from typing import Dict, Any, List

from modules.action_agent import ActionAgentManager
from utils.logger import setup_logger

bp = Blueprint('business', __name__)
logger = setup_logger('routes.business')
action_agent_manager = ActionAgentManager()

# Mock database for business models
BUSINESS_MODELS = {}

@bp.route('/implement', methods=['POST'])
async def implement_business_model():
    """Implement a business model."""
    try:
        data = request.json

        # Required parameters
        instructions = data.get('instructions')
        business_model = data.get('business_model')
        features = data.get('features')
        user_id = data.get('user_id', str(uuid.uuid4()))

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
        logger.error(f"Error implementing business model: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Error implementing business model',
            'message': str(e),
            'status': 500
        }), 500

@bp.route('/<model_id>', methods=['GET'])
def get_business_model(model_id):
    """Get a business model by ID."""
    try:
        if model_id not in BUSINESS_MODELS:
            return jsonify({
                'error': 'Business model not found',
                'status': 404
            }), 404

        model = BUSINESS_MODELS[model_id]

        logger.info(f"Retrieved business model {model_id}")
        return jsonify({
            'success': True,
            'business_model': model
        })

    except Exception as e:
        logger.error(f"Error retrieving business model: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Error retrieving business model',
            'message': str(e),
            'status': 500
        }), 500

@bp.route('/list/<user_id>', methods=['GET'])
def list_business_models(user_id):
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
        logger.error(f"Error listing business models: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Error listing business models',
            'message': str(e),
            'status': 500
        }), 500