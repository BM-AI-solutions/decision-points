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
AGENT_TIMEOUT_SECONDS = int(os.getenv("AGENT_TIMEOUT_SECONDS", 300)) # Timeout for A2A calls

# --- Data Models (Input/Output Schemas) ---
# These should ideally match the actual schemas defined in the respective agent files.
# Simplified versions are kept here for clarity and potential fallback.
# NOTE: These models are used for structuring data internally within the workflow manager,
#       but the actual A2A calls will send/receive data compatible with the target agent's
#       expected input/output Event schemas.
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
        self._http_client = httpx.AsyncClient(timeout=AGENT_TIMEOUT_SECONDS)

    async def close(self):
        """Clean up resources, like the HTTP client."""
        await self._http_client.aclose()
        print("WorkflowManagerAgent closed.")

    async def _invoke_a2a_agent(
        self,
        agent_name: str,
        agent_env_var: str, # e.g., "MARKET_RESEARCH_AGENT_URL"
        endpoint_suffix: str, # e.g., "market_research"
        invocation_id: str,
        payload: Dict[str, Any],
    ) -> Event:
        """
        Helper function to invoke another agent's A2A endpoint asynchronously.

        Args:
            agent_name: User-friendly name of the agent (for logging).
            agent_env_var: Environment variable name holding the agent's base URL.
            endpoint_suffix: The specific part for the A2A route (e.g., 'market_research').
            invocation_id: The current workflow invocation ID (for logging).
            payload: The data dictionary to send as the JSON body.

        Returns:
            An Event object representing the result or error from the agent.
        """
        agent_base_url = os.getenv(agent_env_var)
        if not agent_base_url:
            error_msg = f"URL for agent '{agent_name}' ({agent_env_var}) not configured in environment."
            print(f"[{invocation_id}] Error: {error_msg}")
            return Event(type=EventType.ERROR, data={"error": error_msg})

        # Construct the full A2A endpoint URL
        endpoint_url = f"{agent_base_url.rstrip('/')}/a2a/{endpoint_suffix}/invoke"
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}

        print(f"[{invocation_id}] Invoking {agent_name} A2A endpoint at {endpoint_url}...")

        try:
            response = await self._http_client.post(
                endpoint_url,
                json=payload, # httpx handles JSON serialization
                headers=headers,
                timeout=AGENT_TIMEOUT_SECONDS # Use configured timeout
            )
            response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)

            # Deserialize response directly into an Event object
            event_data = response.json()
            result_event = Event(**event_data)

            # Basic validation: Check if it looks like a valid Event structure
            if not hasattr(result_event, 'type') or not hasattr(result_event, 'data'):
                 raise ValidationError("Response is not a valid Event structure.")

            print(f"[{invocation_id}] Agent '{agent_name}' A2A call successful. Event Type: {result_event.type}")
            return result_event

        except httpx.TimeoutException:
            error_msg = f"Timeout calling {agent_name} A2A endpoint at {endpoint_url}"
            print(f"[{invocation_id}] Error: {error_msg}")
            return Event(type=EventType.ERROR, data={"error": error_msg, "details": "Timeout"})
        except httpx.RequestError as e:
            # Includes ConnectionError, HTTPStatusError (from raise_for_status), etc.
            error_detail = str(e)
            if e.response:
                try:
                    error_detail += f" | Status: {e.response.status_code} | Response: {e.response.text[:500]}" # Limit response size
                except Exception: pass # Ignore errors reading response text
            error_msg = f"HTTP error calling {agent_name} A2A endpoint: {error_detail}"
            print(f"[{invocation_id}] Error: {error_msg}")
            return Event(type=EventType.ERROR, data={"error": error_msg, "details": "HTTP Request Error"})
        except (json.JSONDecodeError, ValidationError, TypeError) as e:
            # Handles issues with response format or deserializing into Event
            error_msg = f"Failed to process or validate A2A response from {agent_name}: {e}"
            print(f"[{invocation_id}] Error: {error_msg}")
            return Event(type=EventType.ERROR, data={"error": error_msg, "details": "Invalid Response Format"})
        except Exception as e:
            # Catch unexpected errors during the call
            error_msg = f"Unexpected error during {agent_name} A2A call: {type(e).__name__}: {e}"
            print(f"[{invocation_id}] Error: {error_msg}")
            # Consider logging the full traceback here
            return Event(type=EventType.ERROR, data={"error": error_msg, "details": "Unexpected Error"})


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
            # Prepare payload for Market Research Agent A2A call
            market_research_payload = MarketResearchInput(
                initial_topic=initial_topic,
                target_url=target_url
            ).model_dump(exclude_none=True)

            market_event = await self._invoke_a2a_agent(
                agent_name="Market Research",
                agent_env_var="MARKET_RESEARCH_AGENT_URL",
                endpoint_suffix="market_research",
                invocation_id=invocation_id,
                payload=market_research_payload,
            )

            if market_event.type == EventType.ERROR:
                raise RuntimeError(f"Market Research Agent failed: {market_event.data.get('error', 'Unknown error')}")
            if not market_event.data:
                 raise RuntimeError("Market Research Agent returned no data.")

            # Use the internal model for structure, but data comes from the event
            try:
                market_report = MarketOpportunityReport(**market_event.data)
                market_report_data = market_report.model_dump() # Keep data as dict for consistency
            except ValidationError as ve:
                raise RuntimeError(f"Market Research Agent response validation failed: {ve}")

            print(f"[{invocation_id}] --- Stage 1 Complete ---")


            # --- Stage 2: Product Improvement ---
            current_stage = WorkflowStage.IMPROVEMENT
            print(f"\n[{invocation_id}] --- Starting Stage 2: {current_stage.value} ---")
            # Prepare payload for Improvement Agent A2A call
            # Ensure necessary fields exist, providing defaults if missing from market report
            improvement_payload = ImprovementAgentInput(
                product_concept=initial_topic, # Base concept
                competitor_weaknesses=market_report_data.get('competitor_weaknesses', []),
                market_gaps=market_report_data.get('market_gaps', []),
                target_audience_suggestions=market_report_data.get('target_audience_suggestions', []),
                feature_recommendations_from_market=market_report_data.get('feature_recommendations', []),
                business_model_type="saas" # Placeholder - should ideally be determined earlier or passed in
            ).model_dump(exclude_none=True)

            improvement_event = await self._invoke_a2a_agent(
                agent_name="Improvement",
                agent_env_var="IMPROVEMENT_AGENT_URL",
                endpoint_suffix="improvement",
                invocation_id=invocation_id,
                payload=improvement_payload,
            )

            if improvement_event.type == EventType.ERROR:
                raise RuntimeError(f"Improvement Agent failed: {improvement_event.data.get('error', 'Unknown error')}")
            if not improvement_event.data:
                 raise RuntimeError("Improvement Agent returned no data.")

            try:
                product_spec = ImprovedProductSpec(**improvement_event.data)
                product_spec_data = product_spec.model_dump()
            except ValidationError as ve:
                raise RuntimeError(f"Improvement Agent response validation failed: {ve}")

            print(f"[{invocation_id}] --- Stage 2 Complete ---")


            # --- Stage 3: Rebranding ---
            current_stage = WorkflowStage.BRANDING
            print(f"\n[{invocation_id}] --- Starting Stage 3: {current_stage.value} ---")
            # Prepare payload for Branding Agent A2A call
            # Extract keywords simply for now
            keywords = product_spec_data.get('product_concept', '').lower().split()[:5]
            branding_payload = BrandingAgentInput(
                product_concept=product_spec_data.get('product_concept', initial_topic),
                target_audience=product_spec_data.get('target_audience', []),
                keywords=keywords,
                business_model_type=improvement_payload.get('business_model_type') # Pass from previous input
            ).model_dump(exclude_none=True)

            branding_event = await self._invoke_a2a_agent(
                agent_name="Branding",
                agent_env_var="BRANDING_AGENT_URL",
                endpoint_suffix="branding",
                invocation_id=invocation_id,
                payload=branding_payload,
            )

            if branding_event.type == EventType.ERROR:
                raise RuntimeError(f"Branding Agent failed: {branding_event.data.get('error', 'Unknown error')}")
            if not branding_event.data:
                 raise RuntimeError("Branding Agent returned no data.")

            try:
                brand_package = BrandPackage(**branding_event.data)
                brand_package_data = brand_package.model_dump()
            except ValidationError as ve:
                raise RuntimeError(f"Branding Agent response validation failed: {ve}")

            print(f"[{invocation_id}] --- Stage 3 Complete ---")


            # --- Stage 4: Deployment ---
            current_stage = WorkflowStage.DEPLOYMENT
            print(f"\n[{invocation_id}] --- Starting Stage 4: {current_stage.value} ---")
            # Prepare payload for Deployment Agent A2A call
            deployment_payload = DeploymentAgentInput(
                brand_name=brand_package_data.get('brand_name', 'Unnamed Brand'),
                product_concept=product_spec_data.get('product_concept', initial_topic),
                key_features=product_spec_data.get('key_features', [])
            ).model_dump(exclude_none=True)

            deployment_event = await self._invoke_a2a_agent(
                agent_name="Deployment",
                agent_env_var="DEPLOYMENT_AGENT_URL",
                endpoint_suffix="deployment",
                invocation_id=invocation_id,
                payload=deployment_payload,
            )

            if deployment_event.type == EventType.ERROR:
                raise RuntimeError(f"Deployment Agent failed: {deployment_event.data.get('error', 'Unknown error')}")
            if not deployment_event.data:
                 raise RuntimeError("Deployment Agent returned no data.")

            try:
                # DeploymentResult is used internally, data comes from event
                deployment_result = DeploymentResult(**deployment_event.data)
                deployment_result_data = deployment_result.model_dump()
            except ValidationError as ve:
                 raise RuntimeError(f"Deployment Agent response validation failed: {ve}")

            # Check status within the deployment result itself
            # Assuming the Deployment Agent returns status in its Event data
            if deployment_result_data.get('status', '').upper() != "ACTIVE":
                 raise RuntimeError(f"Deployment Agent reported non-ACTIVE status: {deployment_result_data.get('status', 'UNKNOWN')}")

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
