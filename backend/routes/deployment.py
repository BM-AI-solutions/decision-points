from flask import Blueprint, request, jsonify
import uuid
from typing import Dict, Any, List

# Import the shared decorator
from backend.utils.decorators import require_subscription_or_local
from backend.modules.action_agent import ActionAgentManager
from backend.utils.logger import setup_logger

bp = Blueprint('deployment', __name__, url_prefix='/api/deployment') # Added url_prefix
logger = setup_logger('routes.deployment')
action_agent_manager = ActionAgentManager()

@bp.route('/deploy', methods=['POST'])
@require_subscription_or_local
async def deploy_system(user_id: str): # Add user_id from decorator
    """Deploy a business system."""
    try:
        data = request.json

        # Required parameters
        business_model_name = data.get('business_model_name')
        implemented_features = data.get('implemented_features')
        # user_id is now passed as an argument

        if not business_model_name:
            return jsonify({
                'error': 'Business model name is required',
                'status': 400
            }), 400

        if not implemented_features:
            return jsonify({
                'error': 'Implemented features are required',
                'status': 400
            }), 400

        # Deploy the system
        deployment_result = await action_agent_manager.deploy_system(
            business_model_name,
            implemented_features,
            user_id
        )

        logger.info(f"Deployed system for {business_model_name} for user {user_id}")
        return jsonify({
            'success': True,
            'deployment': deployment_result
        })

    except Exception as e:
        logger.error(f"Error deploying system for user {user_id}: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Error deploying system',
            'message': str(e),
            'status': 500
        }), 500

@bp.route('/status/<path:deployment_url>', methods=['GET']) # Use path converter for URLs
@require_subscription_or_local
def get_deployment_status(user_id: str, deployment_url: str): # Add user_id from decorator
    """Get the status of a deployment."""
    try:
        # In a real application, you would check the actual deployment status
        # For this demonstration, we'll return a mock status

        # Sanitize the URL
        sanitized_url = deployment_url.replace('https://', '').replace('http://', '')

        status = {
            'url': f"https://{sanitized_url}",
            'status': 'ACTIVE',
            'uptime': '99.9%',
            'last_checked': '2023-09-01T12:00:00Z',
            'metrics': {
                'visitors': 120,
                'conversions': 15,
                'revenue': 850.0
            }
        }

        # Note: Current implementation doesn't link deployment_url to user_id for ownership check.
        # This would require storing deployment info linked to users/business models.
        # For now, the decorator ensures the user is authenticated and subscribed (if cloud).
        logger.info(f"Retrieved deployment status for {deployment_url} by user {user_id}")
        return jsonify({
            'success': True,
            'deployment_status': status
        })

    except Exception as e:
        logger.error(f"Error retrieving deployment status for {deployment_url}, user {user_id}: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Error retrieving deployment status',
            'message': str(e),
            'status': 500
        }), 500