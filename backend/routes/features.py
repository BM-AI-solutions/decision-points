from flask import Blueprint, request, jsonify
import uuid
from typing import Dict, Any, List

# Import the shared decorator
from utils.decorators import require_subscription_or_local
from modules.action_agent import ActionAgentManager
from utils.logger import setup_logger

bp = Blueprint('features', __name__)
logger = setup_logger('routes.features')
action_agent_manager = ActionAgentManager()


@bp.route('/implement', methods=['POST'])
@require_subscription_or_local
async def implement_feature(user_id: str): # Accept user_id from decorator
    """Implement a specific feature. Requires active subscription in cloud mode."""
    try:
        # user_id is passed directly by the decorator
        data = request.json

        # Required parameters
        feature = data.get('feature')
        service_name = data.get('service_name')
        # user_id is now passed as an argument

        if not feature:
            return jsonify({
                'error': 'Feature is required',
                'status': 400
            }), 400

        if not service_name:
            return jsonify({
                'error': 'Service name is required',
                'status': 400
            }), 400

        # Implement the feature
        implementation_result = await action_agent_manager.implement_feature(
            feature,
            service_name,
            user_id
        )

        logger.info(f"Implemented feature {feature.get('feature_name', 'Feature')} for user {user_id}")
        return jsonify({
            'success': True,
            'implementation_result': implementation_result
        })

    except Exception as e:
        logger.error(f"Error implementing feature: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Error implementing feature',
            'message': str(e),
            'status': 500
        }), 500

@bp.route('/branding', methods=['POST'])
@require_subscription_or_local
async def create_branding(user_id: str): # Accept user_id from decorator
    """Create branding for a business model. Requires active subscription in cloud mode."""
    try:
        # user_id is passed directly by the decorator
        data = request.json

        # Required parameters
        business_model_name = data.get('business_model_name')
        target_demographics = data.get('target_demographics')
        # user_id is now passed as an argument

        if not business_model_name:
            return jsonify({
                'error': 'Business model name is required',
                'status': 400
            }), 400

        if not target_demographics:
            return jsonify({
                'error': 'Target demographics are required',
                'status': 400
            }), 400

        # Create branding
        branding_result = await action_agent_manager.create_branding(
            business_model_name,
            target_demographics,
            user_id
        )

        logger.info(f"Created branding for {business_model_name} for user {user_id}")
        return jsonify({
            'success': True,
            'branding': branding_result
        })

    except Exception as e:
        logger.error(f"Error creating branding: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Error creating branding',
            'message': str(e),
            'status': 500
        }), 500