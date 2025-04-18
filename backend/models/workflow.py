from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

class Workflow(BaseModel):
    """Represents an automated workflow configured by a user."""
    id: str = Field(..., description="Unique workflow ID")
    user_id: str = Field(..., description="ID of the user who owns the workflow")
    name: str = Field(..., description="Name of the workflow")
    description: Optional[str] = Field(None, description="Optional description for the workflow")
    trigger_type: str = Field(..., description="Type of trigger that starts the workflow")
    action_type: str = Field(..., description="Type of action the workflow performs")
    created_at: datetime = Field(default_factory=datetime.now, description="When the workflow was created")
    updated_at: datetime = Field(default_factory=datetime.now, description="When the workflow was last updated")

    class Config:
        # Example configuration if needed, e.g., for ORM mode if integrating later
        # orm_mode = True 
        # For now, just a standard Pydantic model
        pass