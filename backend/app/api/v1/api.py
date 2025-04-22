from fastapi import APIRouter

from .endpoints import health
from .endpoints import messages
from .endpoints import users
from .endpoints import login # Import the new login endpoint
from .endpoints import agents # Import the new agents endpoint


api_router = APIRouter()

# Include endpoint routers
api_router.include_router(health.router, prefix="", tags=["health"])

# Authentication/Login router
api_router.include_router(login.router, tags=["login"]) # No prefix needed as endpoint has /login

# Other resource routers
api_router.include_router(messages.router, prefix="/messages", tags=["messages"])
api_router.include_router(users.router, prefix="/users", tags=["users"])


# Agent Orchestration router
api_router.include_router(agents.router, prefix="/agents", tags=["agents"])

# Add other v1 endpoint routers here in the future