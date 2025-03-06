from __future__ import annotations

import os
import json
import logging
from typing import Dict, Any, Optional, List, Union

from dotenv import load_dotenv
from flask import Flask, request, jsonify, Response
from middleware.security_headers import security_headers
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix

from config import Config
from utils.logger import setup_logger
from routes import auth, market, business, features, deployment, cashflow

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.after_request(security_headers)
app.config.from_object(Config)

# Enable CORS
CORS(app, resources={r"/api/*": {"origins": ["https://decisionpoints.intellisol.cc"]}})

# Fix for proxies
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

# Set up logging
logger = setup_logger()

# Register blueprints
app.register_blueprint(auth.bp, url_prefix='/api/auth')
app.register_blueprint(market.bp, url_prefix='/api/market')
app.register_blueprint(business.bp, url_prefix='/api/business')
app.register_blueprint(features.bp, url_prefix='/api/features')
app.register_blueprint(deployment.bp, url_prefix='/api/deployment')
app.register_blueprint(cashflow.bp, url_prefix='/api/cashflow')

@app.route('/api/health', methods=['GET'])
def health_check() -> Dict[str, str]:
    """Health check endpoint."""
    logger.info("Health check request received")
    return jsonify({"status": "healthy", "version": "1.0.0"})

@app.errorhandler(404)
def not_found(e) -> Response:
    """Handle 404 errors."""
    logger.warning(f"404 error: {request.path}")
    return jsonify({"error": "Not found", "status": 404}), 404

@app.errorhandler(500)
def server_error(e) -> Response:
    """Handle 500 errors."""
    logger.error(f"Server error: {str(e)}", exc_info=True)
    return jsonify({"error": "Internal server error", "status": 500}), 500

@app.route('/api/config', methods=['GET'])
def get_public_config() -> Dict[str, Any]:
    """Provide public configuration settings to the frontend."""
    return jsonify({
        "marketSegments": [
            {"id": "digital-products", "name": "Digital Products"},
            {"id": "e-commerce", "name": "E-Commerce"},
            {"id": "saas", "name": "SaaS Applications"},
            {"id": "online-education", "name": "Online Education"},
            {"id": "affiliate-marketing", "name": "Affiliate Marketing"}
        ],
        "businessPreferences": [
            {"id": "highest-revenue", "name": "Highest Revenue Potential"},
            {"id": "lowest-effort", "name": "Lowest Human Effort"},
            {"id": "fastest-implementation", "name": "Fastest Implementation"},
            {"id": "lowest-startup-cost", "name": "Lowest Startup Cost"}
        ],
        "apiVersion": "1.0.0",
        "contactEmail": "support@intellisol.cc"
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)
