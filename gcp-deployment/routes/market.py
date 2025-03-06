from flask import Blueprint, jsonify, request
import uuid
from typing import Dict, Any, List

from modules.guide_agent import GuideAgentManager
from utils.logger import setup_logger

bp = Blueprint('market', __name__)
logger = setup_logger('routes.market')
guide_agent_manager = GuideAgentManager()

@bp.route('/analyze', methods=['POST'])
async def analyze_market() -> Dict[str, Any]:
    """Analyze a market segment to find business opportunities."""
    data = request.json

    try:
        # Get the market segment from the request
        market_segment = data.get('market_segment')
        if not market_segment:
            logger.warning("Market segment not provided")
            return jsonify({
                "error": "Market segment is required",
                "status": 400
            }), 400

        # Generate a user ID if not provided
        user_id = data.get('user_id', str(uuid.uuid4()))

        # Run the market analysis
        result = await guide_agent_manager.analyze_market(market_segment, user_id)

        logger.info(f"Market analysis completed for {market_segment}")
        return jsonify({
            "success": True,
            "market_analysis": result,
            "user_id": user_id
        })

    except Exception as e:
        logger.error(f"Error analyzing market: {str(e)}", exc_info=True)
        return jsonify({
            "error": "Error analyzing market",
            "message": str(e),
            "status": 500
        }), 500

@bp.route('/features', methods=['POST'])
async def identify_features() -> Dict[str, Any]:
    """Identify revenue-generating features for a business model."""
    data = request.json

    try:
        # Get parameters from the request
        business_model_name = data.get('business_model_name')
        market_data = data.get('market_data')
        user_id = data.get('user_id', str(uuid.uuid4()))

        if not business_model_name:
            logger.warning("Business model name not provided")
            return jsonify({
                "error": "Business model name is required",
                "status": 400
            }), 400

        if not market_data:
            logger.warning("Market data not provided")
            return jsonify({
                "error": "Market data is required",
                "status": 400
            }), 400

        # Identify revenue-generating features
        features = await guide_agent_manager.identify_features(
            business_model_name, 
            market_data,
            user_id
        )

        logger.info(f"Features identified for {business_model_name}")
        return jsonify({
            "success": True,
            "features": features,
            "business_model_name": business_model_name,
            "user_id": user_id
        })

    except Exception as e:
        logger.error(f"Error identifying features: {str(e)}", exc_info=True)
        return jsonify({
            "error": "Error identifying features",
            "message": str(e),
            "status": 500
        }), 500

@bp.route('/instructions', methods=['POST'])
async def create_instructions() -> Dict[str, Any]:
    """Create implementation instructions for a business model and features."""
    data = request.json

    try:
        # Get parameters from the request
        business_model = data.get('business_model')
        selected_features = data.get('selected_features')
        user_id = data.get('user_id', str(uuid.uuid4()))

        if not business_model:
            logger.warning("Business model not provided")
            return jsonify({
                "error": "Business model is required",
                "status": 400
            }), 400

        if not selected_features:
            logger.warning("Selected features not provided")
            return jsonify({
                "error": "Selected features are required",
                "status": 400
            }), 400

        # Create implementation instructions
        instructions = await guide_agent_manager.create_instructions(
            business_model,
            selected_features,
            user_id
        )

        logger.info(f"Instructions created for {business_model.get('name', 'business model')}")
        return jsonify({
            "success": True,
            "instructions": instructions,
            "user_id": user_id
        })

    except Exception as e:
        logger.error(f"Error creating instructions: {str(e)}", exc_info=True)
        return jsonify({
            "error": "Error creating instructions",
            "message": str(e),
            "status": 500
        }), 500

@bp.route('/human-tasks', methods=['POST'])
async def identify_human_tasks() -> Dict[str, Any]:
    """Identify tasks that require human input."""
    data = request.json

    try:
        # Get parameters from the request
        business_model = data.get('business_model')
        features = data.get('features')
        user_id = data.get('user_id', str(uuid.uuid4()))

        if not business_model:
            logger.warning("Business model not provided")
            return jsonify({
                "error": "Business model is required",
                "status": 400
            }), 400

        if not features:
            logger.warning("Features not provided")
            return jsonify({
                "error": "Features are required",
                "status": 400
            }), 400

        # Identify human tasks
        human_tasks = await guide_agent_manager.identify_human_tasks(
            business_model,
            features,
            user_id
        )

        logger.info(f"Human tasks identified for {business_model.get('name', 'business model')}")
        return jsonify({
            "success": True,
            "human_tasks": human_tasks,
            "user_id": user_id
        })

    except Exception as e:
        logger.error(f"Error identifying human tasks: {str(e)}", exc_info=True)
        return jsonify({
            "error": "Error identifying human tasks",
            "message": str(e),
            "status": 500
        }), 500