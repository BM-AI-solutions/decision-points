from fastapi import APIRouter

from .endpoints import health
from .endpoints import messages
from .endpoints import users
from .endpoints import agents # Import the new agents endpoint
from .endpoints import market
from .endpoints import business
from .endpoints import analytics
from .endpoints import insights
from .endpoints import customers
from .endpoints import revenue
from .endpoints import orchestrator


api_router = APIRouter()

# Include endpoint routers
api_router.include_router(health.router, prefix="", tags=["health"])

# Authentication/Login router
# Other resource routers
api_router.include_router(messages.router, prefix="/messages", tags=["messages"])
api_router.include_router(users.router, prefix="/users", tags=["users"])


# Agent Orchestration router
api_router.include_router(agents.router, prefix="/agents", tags=["agents"])

# Business functionality routers
api_router.include_router(market.router, prefix="/market", tags=["market"])
api_router.include_router(business.router, prefix="/business", tags=["business"])
# Dashboard data routers
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(insights.router, prefix="/insights", tags=["insights"])
api_router.include_router(customers.router, prefix="/customers", tags=["customers"])
api_router.include_router(revenue.router, prefix="/revenue", tags=["revenue"])

# Orchestrator router
api_router.include_router(orchestrator.router, prefix="/orchestrator", tags=["orchestrator"])

# Add other v1 endpoint routers here in the future