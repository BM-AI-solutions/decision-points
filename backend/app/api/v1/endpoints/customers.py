from fastapi import APIRouter, status
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

router = APIRouter()

# --- Models ---
class Customer(BaseModel):
    id: str
    name: str
    email: str
    joined_date: str
    subscription_tier: str
    lifetime_value: float
    status: str

class CustomerData(BaseModel):
    customers: List[Customer]
    segments: Dict[str, int]
    retention_rate: float
    acquisition_cost: float

# --- Endpoints ---
@router.get(
    "/",
    response_model=CustomerData,
    status_code=status.HTTP_200_OK,
    summary="Get Customer Data",
)
async def get_customer_data() -> CustomerData:
    """
    Get customer data for the dashboard.
    """
    # Mock data
    return {
        "customers": [
            {
                "id": "cust1",
                "name": "John Smith",
                "email": "john@example.com",
                "joined_date": "2023-01-15",
                "subscription_tier": "Premium",
                "lifetime_value": 450.00,
                "status": "Active"
            },
            {
                "id": "cust2",
                "name": "Sarah Johnson",
                "email": "sarah@example.com",
                "joined_date": "2023-02-28",
                "subscription_tier": "Basic",
                "lifetime_value": 120.00,
                "status": "Active"
            },
            {
                "id": "cust3",
                "name": "Michael Brown",
                "email": "michael@example.com",
                "joined_date": "2023-03-10",
                "subscription_tier": "Premium",
                "lifetime_value": 350.00,
                "status": "Active"
            },
            {
                "id": "cust4",
                "name": "Emily Davis",
                "email": "emily@example.com",
                "joined_date": "2023-01-05",
                "subscription_tier": "Enterprise",
                "lifetime_value": 1200.00,
                "status": "Active"
            },
            {
                "id": "cust5",
                "name": "Robert Wilson",
                "email": "robert@example.com",
                "joined_date": "2023-04-20",
                "subscription_tier": "Basic",
                "lifetime_value": 80.00,
                "status": "Inactive"
            }
        ],
        "segments": {
            "Basic": 45,
            "Premium": 30,
            "Enterprise": 25
        },
        "retention_rate": 0.78,
        "acquisition_cost": 42.50
    }
