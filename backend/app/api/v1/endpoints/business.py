from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

router = APIRouter()

# --- Models ---
class BusinessModel(BaseModel):
    id: str
    name: str
    description: str
    revenue_potential: int
    automation_level: int
    implementation_difficulty: int
    features: List[str]

class BusinessModelCreate(BaseModel):
    name: str
    description: str
    revenue_potential: int
    automation_level: int
    implementation_difficulty: int
    features: List[str]

# --- Mock Data ---
MOCK_BUSINESS_MODELS = [
    {
        "id": "model1",
        "name": "Membership Site",
        "description": "Recurring membership site with premium digital content and tiered access levels.",
        "revenue_potential": 3500,
        "automation_level": 8,
        "implementation_difficulty": 7,
        "features": ["Content Management", "User Authentication", "Payment Processing", "Member Portal"]
    },
    {
        "id": "model2",
        "name": "Digital Course Platform",
        "description": "Educational platform with automated course delivery and student management.",
        "revenue_potential": 4200,
        "automation_level": 7,
        "implementation_difficulty": 8,
        "features": ["Course Creation", "Student Management", "Progress Tracking", "Certificate Generation"]
    },
    {
        "id": "model3",
        "name": "Template Marketplace",
        "description": "Marketplace selling digital templates with instant delivery and no inventory.",
        "revenue_potential": 2800,
        "automation_level": 9,
        "implementation_difficulty": 6,
        "features": ["Product Listing", "Digital Delivery", "Seller Dashboard", "Review System"]
    }
]

# --- Endpoints ---
@router.get(
    "/list",
    response_model=List[BusinessModel],
    status_code=status.HTTP_200_OK,
    summary="List Business Models",
)
async def list_business_models() -> List[BusinessModel]:
    """
    List all available business models.
    """
    return MOCK_BUSINESS_MODELS

@router.get(
    "/models/{model_id}",
    response_model=BusinessModel,
    status_code=status.HTTP_200_OK,
    summary="Get Business Model",
)
async def get_business_model(model_id: str) -> BusinessModel:
    """
    Get a specific business model by ID.
    """
    for model in MOCK_BUSINESS_MODELS:
        if model["id"] == model_id:
            return model
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Business model with ID {model_id} not found"
    )

@router.post(
    "/models",
    response_model=BusinessModel,
    status_code=status.HTTP_201_CREATED,
    summary="Create Business Model",
)
async def create_business_model(model: BusinessModelCreate) -> BusinessModel:
    """
    Create a new business model.
    """
    # In a real implementation, this would save to a database
    # For now, just return a mock response with a generated ID
    new_model = model.dict()
    new_model["id"] = f"model{len(MOCK_BUSINESS_MODELS) + 1}"
    
    return new_model
