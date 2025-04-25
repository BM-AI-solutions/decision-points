"""
Agent Network Implementation using A2A Protocol.

This module implements the Agent Network for multi-agent workflow using the A2A protocol.
It provides a central registry for agents and handles routing between them.
"""

import logging
from typing import Dict, List, Optional, Any, Union

from python_a2a import AgentNetwork, A2AClient, AIAgentRouter
from google.adk.agents import Agent as AdkAgent
from google.adk.runtime import InvocationContext, Event

from app.config import settings

# Configure logging
logger = logging.getLogger(__name__)

class DecisionPointsAgentNetwork:
    """
    Agent Network for Decision Points using A2A Protocol.
    
    This class manages the network of agents and provides methods for routing
    and communication between them.
    """
    
    def __init__(self, name: Optional[str] = None):
        """
        Initialize the agent network.
        
        Args:
            name: Optional name for the agent network. Defaults to settings.A2A_NETWORK_NAME.
        """
        self.name = name or settings.A2A_NETWORK_NAME
        self.network = AgentNetwork(name=self.name)
        self.router = None
        self._initialize_network()
        logger.info(f"Agent Network '{self.name}' initialized")
    
    def _initialize_network(self) -> None:
        """Initialize the agent network with all available agents."""
        # Add orchestrator agent (self)
        self.network.add(
            "orchestrator", 
            f"http://localhost:{settings.A2A_ORCHESTRATOR_PORT}"
        )
        
        # Add specialized agents if URLs are configured
        agent_configs = [
            ("web_search", settings.AGENT_WEB_SEARCH_ID, settings.AGENT_WEB_SEARCH_URL),
            ("content_generation", settings.CONTENT_GENERATION_AGENT_ID, settings.CONTENT_GENERATION_AGENT_URL),
            ("market_research", settings.MARKET_RESEARCH_AGENT_ID, settings.MARKET_RESEARCH_AGENT_URL),
            ("improvement", settings.IMPROVEMENT_AGENT_ID, settings.IMPROVEMENT_AGENT_URL),
            ("branding", settings.BRANDING_AGENT_ID, settings.BRANDING_AGENT_URL),
            ("code_generation", settings.CODE_GENERATION_AGENT_ID, settings.CODE_GENERATION_AGENT_URL),
            ("deployment", settings.DEPLOYMENT_AGENT_ID, settings.DEPLOYMENT_AGENT_URL),
            ("marketing", settings.MARKETING_AGENT_ID, settings.MARKETING_AGENT_URL),
            ("lead_generation", settings.LEAD_GENERATION_AGENT_ID, settings.LEAD_GENERATION_AGENT_URL),
            ("freelance_tasker", settings.FREELANCE_TASKER_AGENT_ID, settings.FREELANCE_TASKER_AGENT_URL),
            ("workflow_manager", settings.WORKFLOW_MANAGER_AGENT_ID, settings.WORKFLOW_MANAGER_AGENT_URL),
        ]
        
        for name, agent_id, agent_url in agent_configs:
            if agent_url:
                self.network.add(name, agent_url)
                logger.info(f"Added agent '{name}' ({agent_id}) at {agent_url} to network")
    
    def initialize_router(self, llm_client: A2AClient) -> None:
        """
        Initialize the AI agent router.
        
        Args:
            llm_client: A2A client for the LLM used for routing decisions.
        """
        self.router = AIAgentRouter(
            llm_client=llm_client,
            agent_network=self.network
        )
        logger.info("AI Agent Router initialized")
    
    def route_query(self, query: str) -> tuple[str, float]:
        """
        Route a query to the appropriate agent.
        
        Args:
            query: The query to route.
            
        Returns:
            A tuple of (agent_name, confidence).
        """
        if not self.router:
            logger.warning("Router not initialized, defaulting to orchestrator")
            return "orchestrator", 1.0
        
        agent_name, confidence = self.router.route_query(query)
        logger.info(f"Routing query to {agent_name} with {confidence:.2f} confidence")
        return agent_name, confidence
    
    def get_agent(self, agent_name: str) -> Optional[A2AClient]:
        """
        Get an agent by name.
        
        Args:
            agent_name: The name of the agent to get.
            
        Returns:
            The agent client, or None if not found.
        """
        return self.network.get_agent(agent_name)
    
    def list_agents(self) -> List[Dict[str, Any]]:
        """
        List all available agents.
        
        Returns:
            A list of agent information dictionaries.
        """
        return self.network.list_agents()
    
    async def invoke_agent_skill(
        self, 
        agent_name: str, 
        skill_name: str, 
        input_data: Dict[str, Any],
        context: Optional[InvocationContext] = None,
        timeout_seconds: Optional[float] = None
    ) -> Union[Event, Dict[str, Any]]:
        """
        Invoke a skill on an agent.
        
        Args:
            agent_name: The name of the agent to invoke.
            skill_name: The name of the skill to invoke.
            input_data: The input data for the skill.
            context: Optional invocation context.
            timeout_seconds: Optional timeout in seconds.
            
        Returns:
            The result of the skill invocation.
        """
        agent = self.get_agent(agent_name)
        if not agent:
            logger.error(f"Agent '{agent_name}' not found in network")
            return {"error": f"Agent '{agent_name}' not found in network"}
        
        timeout = timeout_seconds or settings.AGENT_TIMEOUT_SECONDS
        
        try:
            if context:
                # Use ADK A2A protocol if context is provided
                input_event = Event(data=input_data)
                result = await context.invoke_skill(
                    target_agent_id=agent_name,
                    skill_name=skill_name,
                    input=input_event,
                    timeout_seconds=timeout
                )
                return result
            else:
                # Use python-a2a protocol if no context
                response = await agent.invoke_skill(
                    skill_name=skill_name,
                    input_data=input_data,
                    timeout=timeout
                )
                return response
        except Exception as e:
            logger.error(f"Error invoking skill '{skill_name}' on agent '{agent_name}': {e}")
            return {"error": f"Error invoking skill: {str(e)}"}

# Singleton instance
agent_network = DecisionPointsAgentNetwork()
