#!/usr/bin/env python3
"""
Script to start all agent servers.

Usage:
    python start_all_agents.py
"""

import os
import sys
import subprocess
import logging
import time
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Agent configuration
AGENTS = [
    {"name": "market_research", "port": 8004},
    {"name": "improvement", "port": 8005},
    {"name": "branding", "port": 8006},
    {"name": "code_generation", "port": 8007},
    {"name": "deployment", "port": 8008},
    {"name": "marketing", "port": 8009},
    {"name": "lead_generation", "port": 8010},
    {"name": "freelance_tasker", "port": 8011},
    {"name": "workflow_manager", "port": 8012},
    {"name": "content_generation", "port": 8003},
]

def start_agents():
    """Start all agent servers."""
    # Get the script directory
    script_dir = Path(__file__).parent.absolute()
    start_agent_script = script_dir / "start_agent.py"
    
    # Make the script executable
    os.chmod(start_agent_script, 0o755)
    
    # Start each agent in a separate process
    processes = []
    for agent in AGENTS:
        try:
            logger.info(f"Starting {agent['name']} agent on port {agent['port']}")
            cmd = [
                sys.executable,
                str(start_agent_script),
                "--agent", agent["name"],
                "--port", str(agent["port"])
            ]
            
            # Start the process
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
            )
            
            processes.append({
                "name": agent["name"],
                "port": agent["port"],
                "process": process
            })
            
            # Wait a bit to avoid overwhelming the system
            time.sleep(1)
            
        except Exception as e:
            logger.error(f"Error starting {agent['name']} agent: {e}", exc_info=True)
    
    # Monitor the processes
    try:
        while True:
            for p in processes:
                # Check if the process is still running
                if p["process"].poll() is not None:
                    logger.error(f"{p['name']} agent exited with code {p['process'].returncode}")
                    # Read any output
                    stdout, stderr = p["process"].communicate()
                    if stdout:
                        logger.info(f"{p['name']} stdout: {stdout}")
                    if stderr:
                        logger.error(f"{p['name']} stderr: {stderr}")
                    
                    # Restart the process
                    logger.info(f"Restarting {p['name']} agent")
                    cmd = [
                        sys.executable,
                        str(start_agent_script),
                        "--agent", p["name"],
                        "--port", str(p["port"])
                    ]
                    p["process"] = subprocess.Popen(
                        cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        bufsize=1,
                    )
            
            # Sleep for a bit
            time.sleep(5)
    
    except KeyboardInterrupt:
        logger.info("Stopping all agents...")
        for p in processes:
            if p["process"].poll() is None:
                p["process"].terminate()
        
        # Wait for processes to terminate
        for p in processes:
            try:
                p["process"].wait(timeout=5)
            except subprocess.TimeoutExpired:
                p["process"].kill()
        
        logger.info("All agents stopped")

if __name__ == "__main__":
    start_agents()
