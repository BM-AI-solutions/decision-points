#!/usr/bin/env python3
"""
Script to start an agent server using ADK.

Usage:
    python start_agent_adk.py --agent <agent_name> [--port <port>]

Example:
    python start_agent_adk.py --agent market_research --port 8004
"""

import os
import sys
import argparse
import logging
import importlib
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

# Agent class mapping
AGENT_CLASSES = {
    "market_research": "MarketResearchAgent",
    "improvement": "ImprovementAgent",
    "branding": "BrandingAgent",
    "code_generation": "CodeGenerationAgent",
    "deployment": "DeploymentAgent",
    "marketing": "MarketingAgent",
    "lead_generation": "LeadGenerationAgent",
    "freelance_tasker": "FreelanceTaskAgent",
    "workflow_manager": "WorkflowManagerAgent",
    "content_generation": "ContentGenerationAgent",
}

# Agent module mapping
AGENT_MODULES = {
    "market_research": "agents.market_research_agent",
    "improvement": "agents.improvement_agent",
    "branding": "agents.branding_agent",
    "code_generation": "agents.code_generation_agent",
    "deployment": "agents.deployment_agent",
    "marketing": "agents.marketing_agent",
    "lead_generation": "agents.lead_generation_agent",
    "freelance_tasker": "agents.freelance_task_agent",
    "workflow_manager": "agents.workflow_manager_agent",
    "content_generation": "agents.content_generation_agent",
}

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Start an agent server with ADK")
    parser.add_argument("--agent", required=True, choices=AGENT_CLASSES.keys(),
                        help="The agent to start")
    parser.add_argument("--port", type=int, help="The port to run the agent on")
    return parser.parse_args()

def start_agent_with_adk(agent_name, port=None):
    """Start the specified agent with ADK."""
    try:
        # Import the agent module
        module_name = AGENT_MODULES.get(agent_name)
        if not module_name:
            logger.error(f"Unknown agent: {agent_name}")
            return False
        
        module = importlib.import_module(module_name)
        
        # Get the agent class
        class_name = AGENT_CLASSES.get(agent_name)
        if not class_name:
            logger.error(f"Unknown agent class for {agent_name}")
            return False
        
        agent_class = getattr(module, class_name)
        
        # Create the agent instance
        agent = agent_class(port=port)
        
        # Import ADK web
        from google.adk.cli.web import run_web_server
        
        # Start the ADK web server
        logger.info(f"Starting {agent_name} agent with ADK web on port {agent.port}")
        run_web_server(agent, port=agent.port)
        
        return True
    
    except Exception as e:
        logger.error(f"Error starting agent {agent_name} with ADK: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    args = parse_args()
    success = start_agent_with_adk(args.agent, args.port)
    sys.exit(0 if success else 1)
