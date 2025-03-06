from typing import List, Optional
from pydantic import BaseModel, Field

class BusinessModel(BaseModel):
    """A potential business model identified by the Guide Agent"""
    name: str = Field(..., description="Name of the business model")
    type: str = Field(..., description="Type of business model (e.g., e-commerce, SaaS, etc.)")
    potential_revenue: float = Field(..., description="Estimated monthly revenue potential in USD")
    implementation_difficulty: int = Field(..., description="Difficulty to implement on a scale of 1-10")
    market_saturation: int = Field(..., description="Market saturation level on a scale of 1-10")
    required_apis: List[str] = Field(default_factory=list, description="List of APIs needed to implement this model")

class MarketResearchResult(BaseModel):
    """Results of market research conducted by the Guide Agent"""
    top_performing_models: List[BusinessModel] = Field(..., description="List of top performing business models")
    trending_keywords: List[str] = Field(..., description="Trending keywords in this market")
    target_demographics: List[str] = Field(..., description="Target demographics for these business models")
    revenue_generating_features: List[str] = Field(..., description="Features that are most effective at generating revenue")

class FeatureImplementation(BaseModel):
    """A feature implementation plan created by the Guide Agent"""
    feature_name: str = Field(..., description="Name of the feature to implement")
    description: str = Field(..., description="Description of the feature and its benefits")
    implementation_steps: List[str] = Field(..., description="Step-by-step guide to implement this feature")
    required_apis: List[str] = Field(default_factory=list, description="List of APIs needed for this feature")
    estimated_implementation_time: str = Field(..., description="Estimated time to implement (e.g., '2 hours')")

class HumanTaskRequest(BaseModel):
    """A request for the human to perform a necessary task"""
    task_title: str = Field(..., description="Short title of the task")
    task_description: str = Field(..., description="Detailed description of what the human needs to do")
    api_service_name: str = Field(..., description="Name of the service/API that requires setup")
    signup_url: str = Field(..., description="URL where the human can sign up or complete the task")
    required_fields: List[str] = Field(..., description="List of fields or information the human needs to provide")
    environment_variable_name: str = Field(..., description="Name of the environment variable to store the API key/credentials")

class GuideInstruction(BaseModel):
    """An instruction from the Guide Agent to the Action Agent"""
    instruction_type: str = Field(..., description="Type of instruction (e.g., MARKET_RESEARCH, FEATURE_IMPLEMENTATION)")
    description: str = Field(..., description="Detailed description of what should be done")
    steps: List[str] = Field(..., description="Specific steps to follow")
    success_criteria: List[str] = Field(..., description="How to determine if the task was successful")
    expected_output: str = Field(..., description="Description of the expected output format")