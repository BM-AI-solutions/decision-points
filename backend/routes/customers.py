from flask import Blueprint, jsonify, request
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

customers_bp = Blueprint('customers_bp', __name__)

@customers_bp.route('/api/customers', methods=['GET'])
def get_customers():
    """
    Endpoint to retrieve a list of customers.
    Returns placeholder data for now.
    """
    logger.info("GET /api/customers endpoint called")
    try:
        # Placeholder data
        placeholder_customers = [
            {"id": 1, "name": "Customer A", "email": "a@example.com", "status": "Active"},
            {"id": 2, "name": "Customer B", "email": "b@example.com", "status": "Inactive"},
            {"id": 3, "name": "Customer C", "email": "c@example.com", "status": "Active"}
        ]
        logger.info(f"Returning {len(placeholder_customers)} placeholder customers.")
        return jsonify(placeholder_customers), 200
    except Exception as e:
        logger.error(f"Error fetching customers: {e}", exc_info=True)
        return jsonify({"error": "An unexpected error occurred"}), 500