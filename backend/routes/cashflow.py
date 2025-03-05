from flask import Blueprint, request, jsonify
import uuid
from typing import Dict, Any, List

from modules.action_agent import ActionAgentManager
from utils.logger import setup_logger

bp = Blueprint('cashflow', __name__)
logger = setup_logger('routes.cashflow')
action_agent_manager = ActionAgentManager()

@bp.route('/calculate', methods=['POST'])
async def calculate_cash_flow():
    """Calculate cash flow for a business model."""
    try:
        data = request.json

        # Required parameters
        business_model_name = data.get('business_model_name')
        implemented_features = data.get('implemented_features')
        user_id = data.get('user_id', str(uuid.uuid4()))

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
        logger.error(f"Error calculating cash flow: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Error calculating cash flow',
            'message': str(e),
            'status': 500
        }), 500

@bp.route('/history/<user_id>', methods=['GET'])
def get_cash_flow_history(user_id):
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
        logger.error(f"Error retrieving cash flow history: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Error retrieving cash flow history',
            'message': str(e),
            'status': 500
        }), 500

@bp.route('/forecast/<business_id>', methods=['GET'])
def get_cash_flow_forecast(business_id):
    """Get cash flow forecast for a business model."""
    try:
        # In a real application, you would generate an actual forecast
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
        logger.error(f"Error generating cash flow forecast: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Error generating cash flow forecast',
            'message': str(e),
            'status': 500
        }), 500