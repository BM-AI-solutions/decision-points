from fastapi import APIRouter, status
from pydantic import BaseModel

router = APIRouter()

class HealthCheck(BaseModel):
    """Response model for the health check endpoint."""
    status: str = "OK"

@router.get(
    "/health",
    response_model=HealthCheck,
    status_code=status.HTTP_200_OK,
    tags=["health"],
    summary="Perform a Health Check",
    response_description="Returns the health status of the API.",
)
def perform_health_check() -> HealthCheck:
    """
    Simple endpoint to confirm the API is running and responsive.
    """
    return HealthCheck(status="OK")