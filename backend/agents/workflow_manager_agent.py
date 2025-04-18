import os
import json
import time
import random
import httpx
import asyncio
from enum import Enum
from typing import Dict, Any, Optional, Union

from pydantic import BaseModel, Field, HttpUrl, ValidationError

from google.adk.agents import Agent
from google.adk.runtime import InvocationContext
from google.adk.runtime.event import Event, EventType

# --- Configuration ---
# URLs for the individual agent services (replace with actual URLs when deployed)
AGENT_URLS = {
    "market_research": os.getenv("MARKET_RESEARCH_AGENT_URL", "http://localhost:8001/run"),
    "improvement": os.getenv("IMPROVEMENT_AGENT_URL", "http://localhost:8002/run"),
    "branding": os.getenv("BRANDING_AGENT_URL", "http://localhost:8003/run"),
    "deployment": os.getenv("DEPLOYMENT_AGENT_URL", "http://localhost:8004/run"),
}
AGENT_TIMEOUT = int(os.getenv("AGENT_TIMEOUT_SECONDS", 300)) # Timeout for agent calls

# --- Data Models (Input/Output Schemas) ---
# These should ideally match the actual schemas defined in the respective agent files.
# Simplified versions are kept here for clarity and potential fallback.

class MarketResearchInput(BaseModel):
    initial_topic: str
    target_url: Optional[HttpUrl] = None
    num_competitors: int = 3

class MarketOpportunityReport(BaseModel):
    competitors: list = []
    analysis: dict = {}
    feature_recommendations: list = []
    target_audience_suggestions: list = []
    # Adding fields potentially used by ImprovementAgent based on old code
    competitor_weaknesses: list = Field(default_factory=list)
    market_gaps: list = Field(default_factory=list)

class ImprovementAgentInput(BaseModel):
    product_concept: str
    competitor_weaknesses: list = []
    market_gaps: list = []
    target_audience_suggestions: list = []
    feature_recommendations_from_market: list = []
    business_model_type: Optional[str] = None

class ImprovedProductSpec(BaseModel):
    product_concept: str
    target_audience: list = []
    key_features: list = []
    unique_selling_propositions: list = [] # Renamed from identified_improvements for clarity
    implementation_difficulty_estimate: Optional[int] = None
    potential_revenue_impact_estimate: Optional[str] = None

class BrandingAgentInput(BaseModel):
    product_concept: str
    target_audience: list = []
    keywords: Optional[list] = None
    business_model_type: Optional[str] = None

class BrandPackage(BaseModel):
    brand_name: str
    tagline: str
    color_scheme: dict = {}
    positioning_statement: str
    key_messages: list = []
    voice_tone: list = []
    alternative_names: list = []
    target_demographics: list = [] # Assuming this aligns with target_audience

class DeploymentAgentInput(BaseModel):
    brand_name: str
    product_concept: str
    key_features: list = []

class DeploymentResult(BaseModel):
    deployment_url: str
    status: str # e.g., "ACTIVE", "FAILED"
    brand_name: str
    features_deployed: list = []
    monitoring_url: Optional[str] = None
    deployment_details: dict = {}
    domains: list = []
    dns_settings: dict = {}

# --- Workflow State Tracking (Internal) ---
class WorkflowStage(str, Enum):
    STARTING = "STARTING"
    MARKET_RESEARCH = "MARKET_RESEARCH"
    IMPROVEMENT = "IMPROVEMENT"
    BRANDING = "BRANDING"
    DEPLOYMENT = "DEPLOYMENT"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

# --- Agent Communication Payloads ---
class AgentRequest(BaseModel):
    task_id: str # Corresponds to ADK invocation_id
    stage: str # Identifier for the agent's task
    input_data: Dict[str, Any]

class AgentResponse(BaseModel):
    task_id: str
    status: str # "success" or "failure"
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None

# --- Workflow Manager Agent ---

class WorkflowManagerAgent(Agent):
    """
    Orchestrates the 4-step autonomous income generation workflow using ADK.
    Manages state and asynchronous communication between specialized agents via REST APIs.
    """

    def __init__(self):
        super().__init__(agent_id="workflow_manager_agent")
        print("WorkflowManagerAgent initialized (ADK compliant).")
        # Async HTTP client for A2A calls
        self._http_client = httpx.AsyncClient(timeout=AGENT_TIMEOUT)

    async def close(self):
        """Clean up resources, like the HTTP client."""
        await self._http_client.aclose()
        print("WorkflowManagerAgent closed.")

    async def _async_call_agent(
        self,
        agent_name: str,
        invocation_id: str,
        stage_name: str,
        input_payload: BaseModel,
        expected_result_model: Optional[type[BaseModel]] = None
    ) -> Dict[str, Any]:
        """Helper function to call another agent asynchronously via REST API."""
        agent_url = AGENT_URLS.get(agent_name)
        if not agent_url:
            raise ValueError(f"URL for agent '{agent_name}' not configured.")

        request_body = AgentRequest(
            task_id=invocation_id,
            stage=stage_name,
            input_data=input_payload.model_dump(exclude_none=True, mode='json') # Ensure JSON serializable
        )

        print(f"[{invocation_id}] Calling {agent_name} agent at {agent_url} for stage {stage_name}...")
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}

        try:
            response = await self._http_client.post(
                agent_url,
                headers=headers,
                content=request_body.model_dump_json() # Send as JSON string
            )
            response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)

            response_data = response.json()
            agent_response = AgentResponse(**response_data)

            if agent_response.status != "success":
                error_msg = f"Agent '{agent_name}' failed: {agent_response.error_message or 'Unknown error'}"
                print(f"[{invocation_id}] {error_msg}")
                raise RuntimeError(error_msg)

            if not agent_response.result:
                 error_msg = f"Agent '{agent_name}' succeeded but returned no result data."
                 print(f"[{invocation_id}] {error_msg}")
                 raise RuntimeError(error_msg)

            # Validate the result against the expected Pydantic model if provided
            if expected_result_model:
                try:
                    validated_result = expected_result_model(**agent_response.result).model_dump()
                    print(f"[{invocation_id}] Agent '{agent_name}' succeeded.")
                    return validated_result
                except ValidationError as ve:
                    error_msg = f"Agent '{agent_name}' response validation failed: {ve}"
                    print(f"[{invocation_id}] {error_msg}")
                    raise RuntimeError(error_msg)
            else:
                 print(f"[{invocation_id}] Agent '{agent_name}' succeeded (no result validation).")
                 return agent_response.result # Return raw dict if no model provided

        except httpx.TimeoutException:
            error_msg = f"Timeout calling {agent_name} agent at {agent_url}"
            print(f"[{invocation_id}] Error: {error_msg}")
            raise TimeoutError(error_msg)
        except httpx.RequestError as e:
            error_detail = str(e)
            if e.response:
                try:
                    error_detail += f" | Response: {e.response.text}"
                except Exception: pass
            error_msg = f"HTTP error calling {agent_name} agent: {error_detail}"
            print(f"[{invocation_id}] Error: {error_msg}")
            raise ConnectionError(error_msg)
        except (json.JSONDecodeError, ValidationError, TypeError) as e:
            error_msg = f"Failed to process or validate response from {agent_name}: {e}"
            print(f"[{invocation_id}] Error: {error_msg}")
            raise ValueError(error_msg)
        except Exception as e:
            error_msg = f"Unexpected error during {agent_name} call: {e}"
            print(f"[{invocation_id}] Error: {error_msg}")
            raise e # Re-raise unexpected errors


    async def run_async(self, context: InvocationContext) -> Event:
        """
        ADK entry point to orchestrate the 4-step workflow asynchronously.
        """
        invocation_id = context.invocation_id
        print(f"[{invocation_id}] WorkflowManagerAgent run_async started.")

        # 1. Extract Initial Input
        try:
            initial_topic = context.input.data.get("initial_topic")
            target_url = context.input.data.get("target_url") # Optional
            if not initial_topic or not isinstance(initial_topic, str):
                raise ValueError("Missing or invalid 'initial_topic' in input data.")
            print(f"[{invocation_id}] Initial Topic: {initial_topic}, Target URL: {target_url}")
        except Exception as e:
            error_msg = f"Failed to parse initial input: {e}"
            print(f"[{invocation_id}] Error: {error_msg}")
            return Event(type=EventType.ERROR, data={"error": error_msg})

        current_stage = WorkflowStage.STARTING
        market_report_data: Optional[Dict] = None
        product_spec_data: Optional[Dict] = None
        brand_package_data: Optional[Dict] = None
        deployment_result_data: Optional[Dict] = None

        try:
            # --- Stage 1: Market Research ---
            current_stage = WorkflowStage.MARKET_RESEARCH
            print(f"\n[{invocation_id}] --- Starting Stage 1: {current_stage.value} ---")
            market_input = MarketResearchInput(initial_topic=initial_topic, target_url=target_url)
            market_report_data = await self._async_call_agent(
                "market_research", invocation_id, "stage_1_market_research", market_input, MarketOpportunityReport
            )
            # Ensure necessary fields exist for the next step, even if optional in the model
            market_report_data.setdefault('competitor_weaknesses', [])
            market_report_data.setdefault('market_gaps', [])
            market_report_data.setdefault('target_audience_suggestions', [])
            market_report_data.setdefault('feature_recommendations', [])
            print(f"[{invocation_id}] --- Stage 1 Complete ---")


            # --- Stage 2: Product Improvement ---
            current_stage = WorkflowStage.IMPROVEMENT
            print(f"\n[{invocation_id}] --- Starting Stage 2: {current_stage.value} ---")
            # TODO: Determine business_model_type properly if needed
            business_model_type = "saas" # Placeholder
            improvement_input = ImprovementAgentInput(
                product_concept=initial_topic, # Or derive from market_report?
                competitor_weaknesses=market_report_data['competitor_weaknesses'],
                market_gaps=market_report_data['market_gaps'],
                target_audience_suggestions=market_report_data['target_audience_suggestions'],
                feature_recommendations_from_market=market_report_data['feature_recommendations'],
                business_model_type=business_model_type
            )
            product_spec_data = await self._async_call_agent(
                "improvement", invocation_id, "stage_2_improvement", improvement_input, ImprovedProductSpec
            )
            print(f"[{invocation_id}] --- Stage 2 Complete ---")


            # --- Stage 3: Rebranding ---
            current_stage = WorkflowStage.BRANDING
            print(f"\n[{invocation_id}] --- Starting Stage 3: {current_stage.value} ---")
            # TODO: Extract keywords more intelligently
            keywords = product_spec_data['product_concept'].lower().split()[:5]
            branding_input = BrandingAgentInput(
                product_concept=product_spec_data['product_concept'],
                target_audience=product_spec_data['target_audience'],
                keywords=keywords,
                business_model_type=business_model_type # Pass from previous stage
            )
            brand_package_data = await self._async_call_agent(
                "branding", invocation_id, "stage_3_branding", branding_input, BrandPackage
            )
            print(f"[{invocation_id}] --- Stage 3 Complete ---")


            # --- Stage 4: Deployment ---
            current_stage = WorkflowStage.DEPLOYMENT
            print(f"\n[{invocation_id}] --- Starting Stage 4: {current_stage.value} ---")
            deployment_input = DeploymentAgentInput(
                brand_name=brand_package_data['brand_name'],
                product_concept=product_spec_data['product_concept'],
                key_features=product_spec_data['key_features']
            )
            deployment_result_data = await self._async_call_agent(
                "deployment", invocation_id, "stage_4_deployment", deployment_input, DeploymentResult
            )

            # Check status within the deployment result itself
            if deployment_result_data.get('status') != "ACTIVE":
                 raise RuntimeError(f"Deployment simulation resulted in status: {deployment_result_data.get('status', 'UNKNOWN')}")

            print(f"[{invocation_id}] --- Stage 4 Complete ---")


            # --- Workflow Completion ---
            current_stage = WorkflowStage.COMPLETED
            print(f"\n[{invocation_id}] --- Workflow COMPLETED Successfully ---")
            final_result = {
                "status": current_stage.value,
                "initial_topic": initial_topic,
                "deployment_details": deployment_result_data,
                # Optionally include intermediate results if needed
                # "market_report": market_report_data,
                # "product_spec": product_spec_data,
                # "brand_package": brand_package_data,
            }
            return Event(type=EventType.RESULT, data=final_result)

        except (ValueError, TypeError, ConnectionError, TimeoutError, RuntimeError, ValidationError) as e:
            # Catch errors from _async_call_agent or data processing
            error_msg = f"Workflow failed at Stage '{current_stage.value}': {e}"
            print(f"[{invocation_id}] Error: {error_msg}")
            return Event(type=EventType.ERROR, data={"error": error_msg, "stage": current_stage.value})
        except Exception as e:
            # Catch unexpected errors
            error_msg = f"Unexpected workflow error at Stage '{current_stage.value}': {e}"
            print(f"[{invocation_id}] Error: {error_msg}")
            # Consider logging the full traceback here
            return Event(type=EventType.ERROR, data={"error": "An unexpected internal error occurred.", "stage": current_stage.value})
        finally:
            # Ensure the HTTP client is closed if the agent instance is short-lived
            # (ADK might manage agent lifecycle differently, but good practice)
            # await self.close() # Closing here might be too soon if ADK reuses the instance
            pass

# Note: The `if __name__ == "__main__":` block is removed as agent execution
# is handled by the ADK runtime.
