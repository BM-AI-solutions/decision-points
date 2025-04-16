from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

class ActionResult(BaseModel):
    """Result of an action performed by the Action Agent"""
    success: bool = Field(..., description="Whether the action was successful")
    action_type: str = Field(..., description="Type of action performed")
    details: Dict[str, Any] = Field(..., description="Details of the action result")
    next_steps: List[str] = Field(..., description="Recommended next steps")
    revenue_impact: Optional[float] = Field(None, description="Estimated impact on revenue, if applicable")

class SetupResult(BaseModel):
    """Result of a setup operation performed by the Action Agent"""
    service_name: str = Field(..., description="Name of the service that was set up")
    service_url: str = Field(..., description="URL of the service dashboard")
    account_details: Dict[str, str] = Field(..., description="Details of the account that was set up")
    api_configured: bool = Field(..., description="Whether the API was successfully configured")

class DeploymentResult(BaseModel):
    """Result of a deployment operation performed by the Action Agent"""
    deployment_url: str = Field(..., description="URL where the system is deployed")
    status: str = Field(..., description="Status of the deployment")
    features_deployed: List[str] = Field(..., description="Features that were successfully deployed")
    monitoring_url: Optional[str] = Field(None, description="URL for monitoring the deployed system")

class BrandingResult(BaseModel):
    """Result of a branding operation performed by the Action Agent"""
    brand_name: str = Field(..., description="Selected brand name")
    logo_url: Optional[str] = Field(None, description="URL of the generated logo")
    color_scheme: List[str] = Field(..., description="Selected color scheme")
    positioning_statement: str = Field(..., description="Brand positioning statement")

class CashFlowUpdate(BaseModel):
    """Update on the cash flow status of the implemented system"""
    revenue_streams: List[str] = Field(..., description="Active revenue streams")
    estimated_monthly_revenue: float = Field(..., description="Estimated monthly revenue in USD")
    payment_methods: List[str] = Field(..., description="Configured payment methods")
    payout_schedule: str = Field(..., description="When payments are received")
    automated_percentage: int = Field(..., description="Percentage of the process that is automated")