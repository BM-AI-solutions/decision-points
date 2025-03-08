from __future__ import annotations

import os
import json
from typing import Dict, List, Any, Optional

from flask import Blueprint, request, jsonify, current_app
from pydantic import BaseModel, Field

from modules.archon_agent import ArchonAgent

# Create blueprint
archon_bp = Blueprint('archon', __name__, url_prefix='/api/archon')

# Initialize the Archon Agent
archon_agent = ArchonAgent(api_key=os.getenv("OPENAI_API_KEY"), debug_mode=True)

@archon_bp.route('/income-streams', methods=['GET'])
def get_income_streams():
    """
    Get all income streams
    """
    return jsonify({
        "success": True,
        "data": archon_agent.income_streams
    })

@archon_bp.route('/income-streams', methods=['POST'])
def create_income_stream():
    """
    Create a new income stream
    """
    data = request.json
    
    # Validate required fields
    required_fields = ['stream_type', 'name', 'description']
    for field in required_fields:
        if field not in data:
            return jsonify({
                "success": False,
                "error": f"Missing required field: {field}"
            }), 400
    
    try:
        stream = archon_agent.create_income_stream(
            stream_type=data['stream_type'],
            name=data['name'],
            description=data['description'],
            automation_level=data.get('automation_level', 8),
            required_services=data.get('required_services', [])
        )
        
        return jsonify({
            "success": True,
            "data": stream
        })
    except ValueError as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400
    except Exception as e:
        current_app.logger.error(f"Error creating income stream: {str(e)}")
        return jsonify({
            "success": False,
            "error": "An unexpected error occurred"
        }), 500

@archon_bp.route('/subscription-tiers', methods=['POST'])
def create_subscription_tier():
    """
    Create a new subscription tier
    """
    data = request.json
    
    # Validate required fields
    required_fields = ['name', 'price', 'features']
    for field in required_fields:
        if field not in data:
            return jsonify({
                "success": False,
                "error": f"Missing required field: {field}"
            }), 400
    
    try:
        tier = archon_agent.create_subscription_tier(
            name=data['name'],
            price=float(data['price']),
            features=data['features'],
            billing_cycle=data.get('billing_cycle', 'monthly')
        )
        
        return jsonify({
            "success": True,
            "data": tier
        })
    except ValueError as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400
    except Exception as e:
        current_app.logger.error(f"Error creating subscription tier: {str(e)}")
        return jsonify({
            "success": False,
            "error": "An unexpected error occurred"
        }), 500

@archon_bp.route('/stripe/integrate', methods=['POST'])
def integrate_stripe():
    """
    Integrate Stripe payment processing
    """
    data = request.json
    
    # Validate required fields
    if 'api_key' not in data:
        return jsonify({
            "success": False,
            "error": "Missing required field: api_key"
        }), 400
    
    try:
        integration = archon_agent.integrate_stripe(
            api_key=data['api_key'],
            webhook_secret=data.get('webhook_secret')
        )
        
        return jsonify({
            "success": True,
            "data": integration
        })
    except Exception as e:
        current_app.logger.error(f"Error integrating Stripe: {str(e)}")
        return jsonify({
            "success": False,
            "error": "An unexpected error occurred"
        }), 500

@archon_bp.route('/forecast', methods=['POST'])
def forecast_revenue():
    """
    Forecast revenue for income streams
    """
    data = request.json
    
    try:
        forecast = archon_agent.forecast_revenue(
            months=int(data.get('months', 12)),
            growth_rate=float(data.get('growth_rate', 5.0))
        )
        
        return jsonify({
            "success": True,
            "data": forecast
        })
    except Exception as e:
        current_app.logger.error(f"Error forecasting revenue: {str(e)}")
        return jsonify({
            "success": False,
            "error": "An unexpected error occurred"
        }), 500

@archon_bp.route('/income-streams/<int:income_stream_id>/implement', methods=['POST'])
def implement_income_stream(income_stream_id):
    """
    Implement an income stream
    """
    try:
        implementation = archon_agent.implement_income_stream(income_stream_id)
        
        return jsonify({
            "success": True,
            "data": implementation
        })
    except ValueError as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 404
    except Exception as e:
        current_app.logger.error(f"Error implementing income stream: {str(e)}")
        return jsonify({
            "success": False,
            "error": "An unexpected error occurred"
        }), 500

@archon_bp.route('/income-streams/<int:income_stream_id>/deployment-guide', methods=['POST'])
def generate_deployment_guide(income_stream_id):
    """
    Generate a deployment guide for an income stream
    """
    data = request.json
    
    try:
        guide = archon_agent.generate_deployment_guide(
            income_stream_id=income_stream_id,
            implementation_result=data.get('implementation_result')
        )
        
        return jsonify({
            "success": True,
            "data": guide
        })
    except ValueError as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 404
    except Exception as e:
        current_app.logger.error(f"Error generating deployment guide: {str(e)}")
        return jsonify({
            "success": False,
            "error": "An unexpected error occurred"
        }), 500

@archon_bp.route('/run-agent', methods=['POST'])
def run_archon_agent():
    """Run an Archon agent through the MCP server."""
    data = request.json

    if not data or 'income_stream_id' not in data:
        return jsonify({"success": False, "error": "Missing income_stream_id"}), 400

    income_stream_id = data['income_stream_id']
    try:
        income_stream = next((s for s in archon_agent.income_streams if s["id"] == income_stream_id), None)

        
        if not income_stream:
            return jsonify({
                "success": False,
                "error": f"Income stream with ID {income_stream_id} not found"
            }), 404
        
        # TODO: Call Archon agent via MCP here
        
        return jsonify({
            "success": True,
            "message": "This endpoint would run the Archon agent with the provided configuration.",
            "data": {
                "income_stream": income_stream
            }
        })
    except Exception as e:
        current_app.logger.error(f"Error running Archon agent: {str(e)}")
        return jsonify({
            "success": False,
            "error": "An unexpected error occurred"
        }), 500
