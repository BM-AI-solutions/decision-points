#!/usr/bin/env python3
"""
Script to initialize the database.
"""

import os
import sys
import asyncio
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(backend_dir))

# Import the database models and engine
from app.core.db import engine, Base
from app.models import User, Workflow, WorkflowStep, AgentState, AgentTask

async def init_db():
    """Initialize the database by creating all tables."""
    try:
        logger.info("Creating database tables...")
        
        # Create all tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("Database tables created successfully.")
        return True
    
    except Exception as e:
        logger.error(f"Error initializing database: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    success = asyncio.run(init_db())
    sys.exit(0 if success else 1)
