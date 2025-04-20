from fastapi import APIRouter

from backend.app.api.v1.endpoints import health
from backend.app.api.v1.endpoints import messages
from backend.app.api.v1.endpoints import users
from backend.app.api.v1.endpoints import login # Import the new login endpoint

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(health.router, prefix="", tags=["health"])

# Authentication/Login router
api_router.include_router(login.router, tags=["login"]) # No prefix needed as endpoint has /login

# Other resource routers
api_router.include_router(messages.router, prefix="/messages", tags=["messages"])
api_router.include_router(users.router, prefix="/users", tags=["users"])

# Add other v1 endpoint routers here in the future