#!/usr/bin/env python3
"""
Script to start the Orchestrator Agent using ADK web interface.

Usage:
    python start_orchestrator_adk.py [--port <port>]

Example:
    python start_orchestrator_adk.py --port 8001
"""

import os
import sys
import argparse
import logging
import asyncio
from pathlib import Path

# Add the parent directory to the Python path
parent_dir = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(parent_dir))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Import necessary components
from app.core.socketio import websocket_manager
from app.config import settings
from agents.orchestrator_agent import OrchestratorAgent
from agents.agent_network import agent_network

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Start the Orchestrator Agent with ADK web interface")
    parser.add_argument("--port", type=int, default=settings.A2A_ORCHESTRATOR_PORT,
                        help=f"The port to run the agent on (default: {settings.A2A_ORCHESTRATOR_PORT})")
    return parser.parse_args()

async def start_orchestrator_with_adk(port=None):
    """Start the Orchestrator Agent with ADK web interface."""
    try:
        # Define the agent IDs mapping using settings
        agent_ids = {
            "web_searcher": settings.AGENT_WEB_SEARCH_ID,
            "content_generator": settings.CONTENT_GENERATION_AGENT_ID,
            "market_research": settings.MARKET_RESEARCH_AGENT_ID,
            "improvement": settings.IMPROVEMENT_AGENT_ID,
            "branding": settings.BRANDING_AGENT_ID,
            "code_generation": settings.CODE_GENERATION_AGENT_ID,
            "deployment": settings.DEPLOYMENT_AGENT_ID,
            "marketing": settings.MARKETING_AGENT_ID,
            "lead_generator": settings.LEAD_GENERATION_AGENT_ID,
            "freelance_tasker": settings.FREELANCE_TASKER_AGENT_ID,
            "workflow_manager": settings.WORKFLOW_MANAGER_AGENT_ID,
        }
        # Filter out None values in case some IDs are not set
        filtered_agent_ids = {k: v for k, v in agent_ids.items() if v is not None}

        # Use the effective port
        effective_port = port or settings.A2A_ORCHESTRATOR_PORT

        logger.info(f"Instantiating OrchestratorAgent with WebSocket Manager and agent IDs: {filtered_agent_ids}")
        orchestrator_agent = OrchestratorAgent(
            websocket_manager=websocket_manager,
            agent_ids=filtered_agent_ids,
            model_name=settings.GEMINI_MODEL_NAME,
            instruction="Process user requests and delegate to specialized agents when appropriate. Use the agent network for routing."
        )

        # Import ADK web
        from google.adk.cli.web import run_web_server
        
        # Start the ADK web server
        logger.info(f"Starting Orchestrator Agent with ADK web on port {effective_port}")
        
        # Initialize the agent network router with the orchestrator as the LLM client
        orchestrator_agent.a2a_client = orchestrator_agent
        agent_network.initialize_router(orchestrator_agent.a2a_client)
        
        # Run the web server
        run_web_server(orchestrator_agent, port=effective_port)
        
        return True
    
    except Exception as e:
        logger.error(f"Error starting Orchestrator Agent with ADK: {e}", exc_info=True)
        return False

def main():
    """Main entry point."""
    args = parse_args()
    asyncio.run(start_orchestrator_with_adk(args.port))

if __name__ == "__main__":
    main()
