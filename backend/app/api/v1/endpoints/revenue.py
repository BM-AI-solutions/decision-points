from fastapi import APIRouter, status, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

router = APIRouter()

# --- Models ---
class RevenueData(BaseModel):
    monthly_revenue: Dict[str, List[Any]]
    revenue_sources: Dict[str, float]
    growth_rate: float
    projected_annual: float
    comparison_to_target: float

class CashflowForecast(BaseModel):
    months: List[str]
    revenue: List[float]
    expenses: List[float]
    profit: List[float]
    cumulative: List[float]

# --- Endpoints ---
@router.get(
    "/",
    response_model=RevenueData,
    status_code=status.HTTP_200_OK,
    summary="Get Revenue Data",
)
async def get_revenue_data() -> RevenueData:
    """
    Get revenue data for the dashboard.
    """
    # Mock data
    return {
        "monthly_revenue": {
            "labels": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
            "values": [12000, 15000, 18000, 22000, 25000, 31000]
        },
        "revenue_sources": {
            "Subscriptions": 65.0,
            "One-time Sales": 20.0,
            "Affiliate": 10.0,
            "Other": 5.0
        },
        "growth_rate": 0.24,
        "projected_annual": 350000.0,
        "comparison_to_target": 1.15
    }

@router.get(
    "/forecast/{business_id}",
    response_model=CashflowForecast,
    status_code=status.HTTP_200_OK,
    summary="Get Cashflow Forecast",
)
async def get_cashflow_forecast(business_id: str) -> CashflowForecast:
    """
    Get cashflow forecast for a specific business.
    """
    # Mock data - in a real implementation, this would vary by business_id
    if business_id not in ["model1", "model2", "model3"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Business with ID {business_id} not found"
        )
    
    return {
        "months": ["Month 1", "Month 2", "Month 3", "Month 4", "Month 5", "Month 6"],
        "revenue": [5000, 7500, 10000, 12500, 15000, 17500],
        "expenses": [4000, 4500, 5000, 5500, 6000, 6500],
        "profit": [1000, 3000, 5000, 7000, 9000, 11000],
        "cumulative": [1000, 4000, 9000, 16000, 25000, 36000]
    }
