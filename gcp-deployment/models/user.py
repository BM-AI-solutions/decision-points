from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr

class UserProfile(BaseModel):
    """User profile information"""
    id: str = Field(..., description="Unique user ID")
    email: EmailStr = Field(..., description="User's email address")
    name: str = Field(..., description="User's full name")
    created_at: datetime = Field(default_factory=datetime.now, description="When the user account was created")
    subscription_type: Optional[str] = Field(None, description="User's subscription type")
    subscription_expires: Optional[datetime] = Field(None, description="When the subscription expires")
    credits_remaining: int = Field(default=0, description="Remaining credits for the user")
    api_keys: Dict[str, str] = Field(default_factory=dict, description="User's API keys for various services")

class UserPreferences(BaseModel):
    """User preferences for the application"""
    market_interests: List[str] = Field(default_factory=list, description="Market segments the user is interested in")
    preferred_business_types: List[str] = Field(default_factory=list, description="Types of businesses the user prefers")
    implementation_priority: str = Field(default="balanced", description="User's priority for implementation (speed, revenue, automation)")
    max_difficulty: Optional[int] = Field(None, description="Maximum implementation difficulty the user is willing to tackle")
    notification_preferences: Dict[str, bool] = Field(default_factory=dict, description="User's notification preferences")

class UserProject(BaseModel):
    """A business project created by the user"""
    id: str = Field(..., description="Unique project ID")
    user_id: str = Field(..., description="ID of the user who owns the project")
    name: str = Field(..., description="Project name")
    business_model: Dict[str, Any] = Field(..., description="Business model details")
    features: List[Dict[str, Any]] = Field(default_factory=list, description="Features implemented in the project")
    branding: Optional[Dict[str, Any]] = Field(None, description="Branding information")
    deployment: Optional[Dict[str, Any]] = Field(None, description="Deployment information")
    cash_flow: Optional[Dict[str, Any]] = Field(None, description="Cash flow information")
    status: str = Field(default="created", description="Project status")
    created_at: datetime = Field(default_factory=datetime.now, description="When the project was created")
    updated_at: datetime = Field(default_factory=datetime.now, description="When the project was last updated")

class UserAuth(BaseModel):
    """User authentication information"""
    id: str = Field(..., description="Unique user ID")
    email: EmailStr = Field(..., description="User's email address")
    hashed_password: str = Field(..., description="Hashed password")
    salt: str = Field(..., description="Password salt")
    reset_token: Optional[str] = Field(None, description="Password reset token")
    reset_token_expires: Optional[datetime] = Field(None, description="When the reset token expires")
    last_login: Optional[datetime] = Field(None, description="When the user last logged in")