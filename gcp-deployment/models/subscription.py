from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr

class SubscriptionPlan(BaseModel):
    """Subscription plan details"""
    id: str = Field(..., description="Unique plan ID")
    name: str = Field(..., description="Plan name")
    description: str = Field(..., description="Plan description")
    price_monthly: float = Field(..., description="Monthly price in USD")
    price_yearly: float = Field(..., description="Yearly price in USD")
    features: List[str] = Field(..., description="Features included in the plan")
    limits: Dict[str, Any] = Field(..., description="Usage limits for the plan")

class UserSubscription(BaseModel):
    """User subscription information"""
    id: str = Field(..., description="Unique subscription ID")
    user_id: str = Field(..., description="ID of the user who owns the subscription")
    plan_id: str = Field(..., description="ID of the subscribed plan")
    status: str = Field(..., description="Subscription status")
    start_date: datetime = Field(..., description="When the subscription started")
    end_date: datetime = Field(..., description="When the subscription ends")
    auto_renew: bool = Field(default=True, description="Whether the subscription auto-renews")
    payment_method_id: str = Field(..., description="ID of the payment method")

class CreditPackage(BaseModel):
    """Credit package for purchase"""
    id: str = Field(..., description="Unique package ID")
    name: str = Field(..., description="Package name")
    description: str = Field(..., description="Package description")
    credits: int = Field(..., description="Number of credits in the package")
    price: float = Field(..., description="Package price in USD")
    bonus_credits: int = Field(default=0, description="Bonus credits included")

class CreditTransaction(BaseModel):
    """Credit transaction record"""
    id: str = Field(..., description="Unique transaction ID")
    user_id: str = Field(..., description="ID of the user")
    amount: int = Field(..., description="Number of credits added or used")
    transaction_type: str = Field(..., description="Type of transaction (purchase, usage, refund, bonus)")
    description: str = Field(..., description="Transaction description")
    related_entity_id: Optional[str] = Field(None, description="ID of related entity (project, feature, etc.)")
    timestamp: datetime = Field(default_factory=datetime.now, description="When the transaction occurred")