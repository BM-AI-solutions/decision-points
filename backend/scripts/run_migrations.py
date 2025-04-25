#!/usr/bin/env python3
"""
Script to run database migrations.
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

def run_migrations():
    """Run database migrations using Alembic."""
    try:
        # Get the backend directory
        backend_dir = Path(__file__).parent.parent.absolute()
        logger.info(f"Backend directory: {backend_dir}")
        
        # Change to the backend directory
        os.chdir(backend_dir)
        
        # Run the migrations
        logger.info("Running database migrations...")
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            check=True,
            capture_output=True,
            text=True,
        )
        
        # Log the output
        logger.info(f"Migration output: {result.stdout}")
        
        logger.info("Database migrations completed successfully.")
        return True
    
    except subprocess.CalledProcessError as e:
        logger.error(f"Error running migrations: {e.stderr}")
        return False
    
    except Exception as e:
        logger.error(f"Unexpected error running migrations: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    success = run_migrations()
    sys.exit(0 if success else 1)
