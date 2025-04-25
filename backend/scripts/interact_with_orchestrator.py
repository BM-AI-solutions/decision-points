#!/usr/bin/env python3
"""
Script to interact with the orchestrator agent via HTTP.

Usage:
    python interact_with_orchestrator.py
"""

import os
import sys
import asyncio
import logging
import httpx
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

async def interact_with_orchestrator():
    """Interact with the orchestrator agent via HTTP."""
    try:
        # Orchestrator API endpoint
        url = "http://localhost:8001/api/v1/agents/orchestrator/prompt"
        
        # Test prompt
        prompt = "Create a passive income stream using a simple weather app that shows current weather and 5-day forecast"
        
        logger.info(f"Sending prompt to orchestrator API: {prompt}")
        
        # Send the request
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json={"prompt": prompt}
            )
            
            # Check the response
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Response from orchestrator API: {result}")
                return True
            else:
                logger.error(f"Error from orchestrator API: {response.status_code} - {response.text}")
                return False
    
    except Exception as e:
        logger.error(f"Error interacting with orchestrator: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    asyncio.run(interact_with_orchestrator())
