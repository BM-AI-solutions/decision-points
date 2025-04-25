#!/usr/bin/env python3
"""
Script to test the orchestrator agent directly.

Usage:
    python test_orchestrator.py
"""

import os
import sys
import asyncio
import logging
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

# Import the workflow manager agent
from agents.workflow_manager_agent import WorkflowManagerAgent

async def test_orchestrator():
    """Test the orchestrator agent directly."""
    try:
        # Create the orchestrator agent
        agent = WorkflowManagerAgent()
        
        # Test prompt
        prompt = "Create a passive income stream using a simple weather app that shows current weather and 5-day forecast"
        
        logger.info(f"Sending prompt to orchestrator: {prompt}")
        
        # Generate a response
        response = await agent.generate_response(prompt)
        
        logger.info(f"Response from orchestrator: {response}")
        
        return True
    
    except Exception as e:
        logger.error(f"Error testing orchestrator: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    asyncio.run(test_orchestrator())
