#!/usr/bin/env python
"""
Script to start all agents in the multi-agent workflow.

This script starts all specialized agents as separate processes,
each listening on a different port for A2A protocol communication.
"""

import os
import sys
import time
import argparse
import subprocess
from typing import List, Dict, Optional

# Add the parent directory to the path so we can import from the backend package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import settings

# Define agent configurations
AGENT_CONFIGS = [
    {
        "name": "web_searcher",
        "module": "agents.web_search",
        "class": "WebSearchAgent",
        "port": 8002,
        "env_id": "AGENT_WEB_SEARCH_ID",
        "env_url": "AGENT_WEB_SEARCH_URL",
    },
    {
        "name": "content_generator",
        "module": "agents.content_generation_agent",
        "class": "ContentGenerationAgent",
        "port": 8003,
        "env_id": "CONTENT_GENERATION_AGENT_ID",
        "env_url": "CONTENT_GENERATION_AGENT_URL",
    },
    {
        "name": "market_research",
        "module": "agents.market_research_agent",
        "class": "MarketResearchAgent",
        "port": 8004,
        "env_id": "MARKET_RESEARCH_AGENT_ID",
        "env_url": "MARKET_RESEARCH_AGENT_URL",
    },
    {
        "name": "improvement",
        "module": "agents.improvement_agent",
        "class": "ImprovementAgent",
        "port": 8005,
        "env_id": "IMPROVEMENT_AGENT_ID",
        "env_url": "IMPROVEMENT_AGENT_URL",
    },
    {
        "name": "branding",
        "module": "agents.branding_agent",
        "class": "BrandingAgent",
        "port": 8006,
        "env_id": "BRANDING_AGENT_ID",
        "env_url": "BRANDING_AGENT_URL",
    },
    {
        "name": "code_generation",
        "module": "agents.code_generation_agent",
        "class": "CodeGenerationAgent",
        "port": 8007,
        "env_id": "CODE_GENERATION_AGENT_ID",
        "env_url": "CODE_GENERATION_AGENT_URL",
    },
    {
        "name": "deployment",
        "module": "agents.deployment_agent",
        "class": "DeploymentAgent",
        "port": 8008,
        "env_id": "DEPLOYMENT_AGENT_ID",
        "env_url": "DEPLOYMENT_AGENT_URL",
    },
    {
        "name": "marketing",
        "module": "agents.marketing_agent",
        "class": "MarketingAgent",
        "port": 8009,
        "env_id": "MARKETING_AGENT_ID",
        "env_url": "MARKETING_AGENT_URL",
    },
    {
        "name": "lead_generator",
        "module": "agents.lead_generation_agent",
        "class": "LeadGenerationAgent",
        "port": 8010,
        "env_id": "LEAD_GENERATION_AGENT_ID",
        "env_url": "LEAD_GENERATION_AGENT_URL",
    },
    {
        "name": "freelance_tasker",
        "module": "agents.freelance_task_agent",
        "class": "FreelanceTaskAgent",
        "port": 8011,
        "env_id": "FREELANCE_TASKER_AGENT_ID",
        "env_url": "FREELANCE_TASKER_AGENT_URL",
    },
    {
        "name": "workflow_manager",
        "module": "agents.workflow_manager_agent",
        "class": "WorkflowManagerAgent",
        "port": 8012,
        "env_id": "WORKFLOW_MANAGER_AGENT_ID",
        "env_url": "WORKFLOW_MANAGER_AGENT_URL",
    },
]

def start_agent(agent_config: Dict[str, str], debug: bool = False) -> Optional[subprocess.Popen]:
    """
    Start an agent as a separate process.
    
    Args:
        agent_config: The agent configuration.
        debug: Whether to run in debug mode.
        
    Returns:
        The subprocess.Popen object for the agent process, or None if the agent failed to start.
    """
    name = agent_config["name"]
    module = agent_config["module"]
    class_name = agent_config["class"]
    port = agent_config["port"]
    
    # Create a Python script to run the agent
    script = f"""
import os
import sys
import asyncio
from {module} import {class_name}
from app.config import settings

async def main():
    # Initialize the agent
    agent = {class_name}(
        name="{name}",
        description="Specialized agent for {name} tasks",
        port={port}
    )
    
    # Run the A2A server
    agent.run_server(host="0.0.0.0", port={port})

if __name__ == "__main__":
    asyncio.run(main())
"""
    
    # Write the script to a temporary file
    script_path = f"/tmp/agent_{name}.py"
    with open(script_path, "w") as f:
        f.write(script)
    
    # Start the agent process
    cmd = [sys.executable, script_path]
    if debug:
        print(f"Starting agent {name} with command: {' '.join(cmd)}")
    
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE if not debug else None,
            stderr=subprocess.PIPE if not debug else None,
            text=True,
        )
        print(f"Started agent {name} on port {port} (PID: {process.pid})")
        return process
    except Exception as e:
        print(f"Failed to start agent {name}: {e}")
        return None

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Start all agents in the multi-agent workflow.")
    parser.add_argument("--debug", action="store_true", help="Run in debug mode")
    parser.add_argument("--agents", nargs="+", help="Specific agents to start (default: all)")
    args = parser.parse_args()
    
    # Filter agents if specified
    configs = AGENT_CONFIGS
    if args.agents:
        configs = [c for c in AGENT_CONFIGS if c["name"] in args.agents]
        if not configs:
            print(f"No valid agents specified. Available agents: {', '.join(c['name'] for c in AGENT_CONFIGS)}")
            return
    
    # Start agents
    processes = []
    for config in configs:
        process = start_agent(config, args.debug)
        if process:
            processes.append((config["name"], process))
    
    if not processes:
        print("No agents started.")
        return
    
    print(f"Started {len(processes)} agents. Press Ctrl+C to stop all agents.")
    
    try:
        # Keep the script running until interrupted
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping all agents...")
        for name, process in processes:
            print(f"Stopping agent {name} (PID: {process.pid})...")
            process.terminate()
        
        # Wait for all processes to terminate
        for name, process in processes:
            process.wait()
            print(f"Agent {name} stopped.")
    
    print("All agents stopped.")

if __name__ == "__main__":
    main()
