from __future__ import annotations

import os
import json
import logging
from typing import Dict, Any, Optional, List, Union

import google.generativeai as genai
from dotenv import load_dotenv
from flask import Flask, request, jsonify, Response
from middleware.security_headers import security_headers
from flask_cors import CORS
from flask_socketio import SocketIO
from werkzeug.middleware.proxy_fix import ProxyFix

from config import Config
from utils.logger import setup_logger
from routes import auth, market, business, features, deployment, cashflow, workflows, analytics, insights, customers
from routes import auth, market, business, features, deployment, cashflow, workflows, analytics, insights, customers, revenue
from routes import orchestrator # Import the new orchestrator blueprint
from agents.orchestrator_agent import OrchestratorAgent # Import the agent
from agents.market_analysis_agent import MarketAnalysisAgent # Import the MarketAnalysisAgent
from agents.content_generation_agent import ContentGenerationAgent # Import the ContentGenerationAgent
from agents.lead_generation_agent import LeadGenerationAgent # Import the LeadGenerationAgent
from agents.freelance_task_agent import FreelanceTaskAgent # Import the FreelanceTaskAgent
from agents.web_search_agent import WebSearchAgent # Import the WebSearchAgent


# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.after_request(security_headers)
app.config.from_object(Config)



# Configure Google Generative AI
if Config.GEMINI_API_KEY:
    genai.configure(api_key=Config.GEMINI_API_KEY)
    logger.info("Google Generative AI configured successfully.")
else:
    logger.warning("GEMINI_API_KEY not found in environment variables. LLM functionality will be disabled.")

# Determine allowed origins for CORS
allowed_origins = ["https://decisionpoints.intellisol.cc"]
if (
    os.environ.get('FLASK_ENV') == 'development'
    or app.config.get('ENV') == 'development'
    or not app.config.get('BILLING_REQUIRED', True)
):
    allowed_origins.append("http://localhost:8000")
    allowed_origins.append("http://localhost:5173")

# Enable standard Flask CORS
CORS(app, resources={r"/api/*": {"origins": allowed_origins}}, supports_credentials=True)

# Initialize SocketIO with CORS settings
# Use '*' if allowing all origins in dev, otherwise use the specific list
socketio_cors_origins = allowed_origins if allowed_origins else "*"
socketio = SocketIO(app, cors_allowed_origins=socketio_cors_origins, async_mode='threading') # Using threading for simplicity, consider eventlet/gevent for production


# Initialize Agents
market_analysis_agent = MarketAnalysisAgent(model_name=Config.MARKET_ANALYSIS_MODEL if hasattr(Config, 'MARKET_ANALYSIS_MODEL') else Config.ORCHESTRATOR_MODEL) # Use specific model or fallback
content_generation_agent = ContentGenerationAgent(model_name=Config.CONTENT_GENERATION_MODEL if hasattr(Config, 'CONTENT_GENERATION_MODEL') else Config.ORCHESTRATOR_MODEL) # Use specific model or fallback
# Instantiate LeadGenerationAgent (assuming default model or no specific model needed at init)
# Get GCP Project ID for FreelanceTaskAgent
gcp_project_id = os.getenv('GCP_PROJECT_ID')
if not gcp_project_id:
    logger.warning("GCP_PROJECT_ID not found in environment variables. FreelanceTaskAgent may not function correctly.")
    freelance_task_agent_config = {}
else:
    freelance_task_agent_config = {'gcp_project_id': gcp_project_id}
freelance_task_agent = FreelanceTaskAgent(config=freelance_task_agent_config)

lead_generation_agent = LeadGenerationAgent()
web_search_agent = WebSearchAgent() # Instantiate WebSearchAgent

# Instantiate Autonomous Income Workflow Agents
# Note: These agents might require specific configurations (API keys, etc.) passed during init
# depending on their implementation, which are assumed to be handled within their constructors
# using environment variables or other config mechanisms.
market_research_agent = MarketResearchAgent() # Assuming basic init for now
improvement_agent = ImprovementAgent()       # Assuming basic init for now
branding_agent = BrandingAgent()           # Assuming basic init for now
deployment_agent = DeploymentAgent()         # Assuming basic init for now

# Instantiate Workflow Manager Agent, configuring it with other agent URLs
# Ensure the corresponding environment variables are set in Config or .env
workflow_manager_agent = WorkflowManagerAgent(
    market_research_agent_url=getattr(Config, 'MARKET_RESEARCH_AGENT_URL', None),
    improvement_agent_url=getattr(Config, 'IMPROVEMENT_AGENT_URL', None),
    branding_agent_url=getattr(Config, 'BRANDING_AGENT_URL', None),
    deployment_agent_url=getattr(Config, 'DEPLOYMENT_AGENT_URL', None),
    timeout_seconds=getattr(Config, 'AGENT_TIMEOUT_SECONDS', 300) # Use getattr for optional timeout
)
# Check if essential URLs are missing and log warnings
if not workflow_manager_agent.market_research_agent_url:
    logger.warning("MARKET_RESEARCH_AGENT_URL not configured. Workflow Manager may fail.")
if not workflow_manager_agent.improvement_agent_url:
    logger.warning("IMPROVEMENT_AGENT_URL not configured. Workflow Manager may fail.")
if not workflow_manager_agent.branding_agent_url:
    logger.warning("BRANDING_AGENT_URL not configured. Workflow Manager may fail.")
if not workflow_manager_agent.deployment_agent_url:
    logger.warning("DEPLOYMENT_AGENT_URL not configured. Workflow Manager may fail.")


agents = {
    "market_analyzer": market_analysis_agent,
    "content_generator": content_generation_agent,
    "lead_generator": lead_generation_agent,
    "freelance_tasker": freelance_task_agent,
    "web_searcher": web_search_agent,
    "workflow_manager": workflow_manager_agent, # Add the workflow manager
    # Note: Direct references to market_research, improvement, branding, deployment agents
    # are removed here as they are managed by the workflow_manager.
}

# Initialize the Orchestrator Agent with SocketIO instance and other agents
orchestrator_agent = OrchestratorAgent(socketio=socketio, model_name=Config.ORCHESTRATOR_MODEL, agents=agents)
app.orchestrator_agent = orchestrator_agent # Attach orchestrator agent to app context
# Optionally attach other agents if needed globally
# app.market_analysis_agent = market_analysis_agent

# Enable CORS (Original block moved up and logic reused)
# Allow specific origin for production, add localhost for development
allowed_origins = ["https://decisionpoints.intellisol.cc"]
# Allow development origin if FLASK_ENV is development OR if billing is not required (local dev setup)
if (
    os.environ.get('FLASK_ENV') == 'development'
    or app.config.get('ENV') == 'development'
    or not app.config.get('BILLING_REQUIRED', True)
):
    # Assuming frontend runs on port 8000 for local dev based on previous setup
    # Vite default is often 5173, adjust if needed.
    allowed_origins.append("http://localhost:8000") # Keep existing dev origin
    allowed_origins.append("http://localhost:5173") # Add Vite dev origin
    # You might need to add 'http://localhost:5173' if your Vite dev server uses that port
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
app.register_blueprint(workflows.workflows_bp) # No url_prefix needed here as it's defined in the blueprint
app.register_blueprint(analytics.bp) # Register the new analytics blueprint
app.register_blueprint(insights.insights_bp) # Register the insights blueprint
app.register_blueprint(customers.customers_bp) # Register the customers blueprint

app.register_blueprint(revenue.revenue_bp) # Register the revenue blueprint

app.register_blueprint(orchestrator.orchestrator_bp) # Register the orchestrator blueprint
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

# Add a simple SocketIO event handler example (can be moved later)
@socketio.on('connect')
def handle_connect():
    logger.info(f"Client connected: {request.sid}")

@socketio.on('disconnect')
def handle_disconnect():
    logger.info(f"Client disconnected: {request.sid}")

@socketio.on('message')
def handle_message(data):
    logger.info(f"Received message from {request.sid}: {data}")
    # Example echo back
    socketio.emit('response', {'data': f'Server received: {data}'}, room=request.sid)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    logger.info(f"Starting SocketIO server on port {port} with debug={debug}")
    # Use socketio.run to start the server
    socketio.run(app, host='0.0.0.0', port=port, debug=debug, use_reloader=debug)
