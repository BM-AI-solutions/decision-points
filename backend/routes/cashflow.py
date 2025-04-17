from flask import Blueprint, request, jsonify
import uuid
from typing import Dict, Any, List

# Import the shared decorator
from backend.utils.decorators import require_subscription_or_local
from backend.modules.action_agent import ActionAgentManager
from backend.utils.logger import setup_logger
# Import BUSINESS_MODELS from business.py to check ownership for forecast
# This creates a dependency, consider a shared data access layer later
from .business import BUSINESS_MODELS

bp = Blueprint('cashflow', __name__, url_prefix='/api/cashflow') # Added url_prefix
logger = setup_logger('routes.cashflow')
action_agent_manager = ActionAgentManager()

@bp.route('/calculate', methods=['POST'])
@require_subscription_or_local
async def calculate_cash_flow(user_id: str): # Add user_id from decorator
    """Calculate cash flow for a business model."""
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

        # Calculate cash flow
        cash_flow = await action_agent_manager.calculate_cash_flow(
            business_model_name,
            implemented_features,
            user_id
        )

        logger.info(f"Calculated cash flow for {business_model_name} for user {user_id}")
        return jsonify({
            'success': True,
            'cash_flow': cash_flow
        })

    except Exception as e:
        logger.error(f"Error calculating cash flow for user {user_id}: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Error calculating cash flow',
            'message': str(e),
            'status': 500
        }), 500

# Changed route to remove user_id from path - get it from JWT via decorator
@bp.route('/history', methods=['GET'])
@require_subscription_or_local
def get_cash_flow_history(user_id: str): # Add user_id from decorator
    """Get cash flow history for a user."""
    try:
        # In a real application, you would retrieve the actual cash flow history
        # For this demonstration, we'll return mock data

        history = [
            {
                'date': '2023-09-01',
                'revenue': 120.50,
                'business_model': 'Digital Products',
                'sources': ['Base Sales', 'Upsell Revenue']
            },
            {
                'date': '2023-09-02',
                'revenue': 175.25,
                'business_model': 'Digital Products',
                'sources': ['Base Sales', 'Upsell Revenue', 'Affiliate Commission']
            },
            {
                'date': '2023-09-03',
                'revenue': 210.75,
                'business_model': 'Digital Products',
                'sources': ['Base Sales', 'Upsell Revenue', 'Affiliate Commission']
            }
        ]

        logger.info(f"Retrieved cash flow history for user {user_id}")
        return jsonify({
            'success': True,
            'history': history
        })

    except Exception as e:
        logger.error(f"Error retrieving cash flow history for user {user_id}: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Error retrieving cash flow history',
            'message': str(e),
            'status': 500
        }), 500

@bp.route('/forecast/<business_id>', methods=['GET'])
@require_subscription_or_local
def get_cash_flow_forecast(user_id: str, business_id: str): # Add user_id from decorator
    """Get cash flow forecast for a business model."""
    try:
        # Check ownership of the business model first
        if business_id not in BUSINESS_MODELS:
             logger.warning(f"Forecast requested for non-existent business model {business_id} by user {user_id}")
             return jsonify({'error': 'Business model not found', 'status': 404}), 404

        model = BUSINESS_MODELS[business_id]
        if model.get('user_id') != user_id:
             logger.warning(f"User {user_id} attempted to access forecast for unauthorized model {business_id} owned by {model.get('user_id')}")
             return jsonify({'error': 'Forbidden', 'status': 403}), 403

        # In a real application, you would generate an actual forecast based on the model
        # For this demonstration, we'll return mock data

        forecast = {
            'daily': [
                {'date': '2023-09-05', 'revenue': 250.0},
                {'date': '2023-09-06', 'revenue': 275.0},
                {'date': '2023-09-07', 'revenue': 300.0}
            ],
            'monthly': [
                {'month': '2023-09', 'revenue': 7500.0},
                {'month': '2023-10', 'revenue': 9000.0},
                {'month': '2023-11', 'revenue': 10500.0}
            ],
            'yearly': [
                {'year': '2023', 'revenue': 90000.0},
                {'year': '2024', 'revenue': 120000.0}
            ],
            'growth_rate': 0.15
        }

        logger.info(f"Generated cash flow forecast for business {business_id}")
        return jsonify({
            'success': True,
            'forecast': forecast
        })

    except Exception as e:
        logger.error(f"Error generating cash flow forecast for business {business_id}, user {user_id}: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Error generating cash flow forecast',
            'message': str(e),
            'status': 500
        }), 500