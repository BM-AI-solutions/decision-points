from fastapi import APIRouter, status
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

router = APIRouter()

# --- Models ---
class AnalyticsData(BaseModel):
    revenue_data: Dict[str, List[int]]
    user_data: Dict[str, List[int]]
    conversion_rates: Dict[str, float]
    growth_metrics: Dict[str, float]

# --- Endpoints ---
@router.get(
    "/",
    response_model=AnalyticsData,
    status_code=status.HTTP_200_OK,
    summary="Get Analytics Data",
)
async def get_analytics_data() -> AnalyticsData:
    """
    Get analytics data for the dashboard.
    """
    # Mock data
    return {
        "revenue_data": {
            "labels": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
            "values": [1200, 1900, 2400, 2800, 3500, 4200]
        },
        "user_data": {
            "labels": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
            "values": [50, 120, 180, 250, 310, 420]
        },
        "conversion_rates": {
            "signup_to_paid": 0.28,
            "visitor_to_signup": 0.12,
            "overall": 0.034
        },
        "growth_metrics": {
            "revenue_growth": 0.24,
            "user_growth": 0.35,
            "retention_rate": 0.87
        }
    }
