# This file makes the 'agents' directory a Python package.

# Import agent instances to make them discoverable by ADK web
from .agent_web_search import agent as web_search_adk
from .branding_agent import agent as branding_adk
from .code_generation_agent import agent as code_generation_adk
from .content_generation_agent import agent as content_generation_adk
from .deployment_agent import agent as deployment_adk
from .freelance_task_agent import agent as freelance_tasker_adk
from .improvement_agent import agent as improvement_adk
from .lead_generation_agent import agent as lead_generation_adk
from .market_analysis_agent import agent as market_analysis_adk
from .market_research_agent import agent as market_research_adk
from .marketing_agent import agent as marketing_adk
from .orchestrator_agent import agent as orchestrator_adk
from .workflow_manager_agent import agent as workflow_manager_adk

# Optionally, you can define __all__ to explicitly list the agents to be exported
__all__ = [
    "web_search_adk",
    "branding_adk",
    "code_generation_adk",
    "content_generation_adk",
    "deployment_adk",
    "freelance_tasker_adk",
    "improvement_adk",
    "lead_generation_adk",
    "market_analysis_adk",
    "market_research_adk",
    "marketing_adk",
    "orchestrator_adk",
    "workflow_manager_adk",
]
