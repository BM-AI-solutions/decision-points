import os
import random
import string
import datetime
import asyncio # Added for potential async operations
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field, HttpUrl, ValidationError

# ADK Imports
from google.adk.agents import Agent
from google.adk.runtime import InvocationContext
from google.adk.runtime.events import Event

# --- Data Models (Input structure expected in context.input.data) ---

class DeploymentAgentInputData(BaseModel):
    """Expected data structure within context.input.data."""
    brand_name: str = Field(description="The final brand name for the product.")
    product_concept: str = Field(description="Description of the product being deployed.")
    key_features: List[Dict[str, Any]] = Field(description="List of features included in the deployment.")
    # Optional: Add other relevant info if needed, e.g., target audience for configuration
    # target_audience: List[str] = Field(default=[])

# --- Data Models (Output structure for Event payload) ---

class DeploymentDetails(BaseModel):
    hosting_provider: str
    deployment_date: str
    environment: str
    resources: Dict[str, str]
    security: Dict[str, Any]

class DnsSettings(BaseModel):
    provider: str
    records: List[Dict[str, str]]

class DeploymentResultPayload(BaseModel):
    """Payload for the successful deployment event."""
    deployment_url: HttpUrl
    status: str # e.g., "ACTIVE"
    brand_name: str
    features_deployed: List[str] # List of feature names deployed
    monitoring_url: Optional[HttpUrl] = None
    deployment_details: DeploymentDetails
    domains: List[HttpUrl]
    dns_settings: DnsSettings

class DeploymentFailedPayload(BaseModel):
    """Payload for the failed deployment event."""
    brand_name: str
    reason: str
    deployment_details: Optional[DeploymentDetails] = None # Include partial details if available
    dns_settings: Optional[DnsSettings] = None

# --- Agent Class ---

class DeploymentAgent(Agent):
    """
    ADK Agent responsible for Stage 4: Deployment.
    Simulates the deployment of the product based on branding and features.
    Reads input from context, emits 'deployment.succeeded' or 'deployment.failed' events.
    """
    def __init__(self):
        """Initialize the Deployment Agent."""
        super().__init__() # Initialize the base Agent class
        print("DeploymentAgent initialized.")
        # Potential place for API clients (e.g., Vercel, AWS) if not simulated
        self.hosting_providers = ["AWS", "DigitalOcean", "Google Cloud", "Cloudflare", "Vercel", "Netlify"]
        self.dns_providers = ["Cloudflare", "AWS Route 53", "Google Cloud DNS"]
        # TODO: Load necessary API keys/credentials from environment variables here

    def _generate_domain_name(self, brand_name: str) -> str:
        """Generates a plausible domain name from the brand name."""
        sanitized_name = ''.join(c for c in brand_name.lower() if c.isalnum() or c == ' ')
        sanitized_name = sanitized_name.replace(' ', '-')
        tld = random.choice([".com", ".ai", ".io", ".app", ".co", ".tech"])
        if '.' in sanitized_name.split('-')[-1]:
            return f"https://{sanitized_name}"
        else:
            return f"https://{sanitized_name}{tld}"

    async def run_async(self, context: InvocationContext):
        """Executes the simulated deployment workflow using ADK context."""
        print("DeploymentAgent run_async started.")

        try:
            # 1. Validate and parse input from context
            input_data = DeploymentAgentInputData(**context.input.data)
            print(f"Starting simulated deployment for brand: {input_data.brand_name}")
        except ValidationError as e:
            print(f"Input validation failed: {e}")
            await context.emit(Event(
                type="deployment.failed",
                payload=DeploymentFailedPayload(
                    brand_name="Unknown (Input Error)",
                    reason=f"Invalid input data: {e}",
                ).model_dump()
            ))
            return
        except Exception as e:
            print(f"Error processing input: {e}")
            await context.emit(Event(
                type="deployment.failed",
                payload=DeploymentFailedPayload(
                    brand_name="Unknown (Input Error)",
                    reason=f"Unexpected error processing input: {e}",
                ).model_dump()
            ))
            return

        # --- Simulation Logic ---
        # (Keep simulation for now, replace with real calls later)
        try:
            # 2. Generate Deployment URL
            deployment_url = self._generate_domain_name(input_data.brand_name)
            monitoring_url = f"{deployment_url}/dashboard"

            # 3. Simulate Deployment Details
            hosting_provider = random.choice(self.hosting_providers)
            deployment_date = datetime.datetime.now(datetime.timezone.utc).isoformat()
            environment = "Production" # Could be configurable via context/env vars
            resources = {
                "cpu": f"{random.choice([1, 2, 4])} vCPU",
                "memory": f"{random.choice([2, 4, 8])} GB RAM",
                "storage": f"{random.choice([25, 50, 100])} GB SSD"
            }
            security = {
                "ssl_enabled": True,
                "ddos_protection": random.choice([True, False]),
                "firewall_rules": random.randint(5, 20)
            }
            deployment_details = DeploymentDetails(
                hosting_provider=hosting_provider,
                deployment_date=deployment_date,
                environment=environment,
                resources=resources,
                security=security
            )

            # 4. Simulate Domain/DNS Setup
            base_domain = deployment_url.replace("https://", "")
            domains = [deployment_url]
            if not base_domain.startswith("www."):
                domains.append(f"https://www.{base_domain}")

            dns_settings = DnsSettings(
                provider=random.choice(self.dns_providers),
                records=[
                    {"type": "A", "name": "@", "value": f"192.0.2.{random.randint(1, 254)}"},
                    {"type": "CNAME", "name": "www", "value": "@"}
                ]
            )

            # 5. Extract Feature Names
            features_deployed = [f.get("feature_name", "Unknown Feature") for f in input_data.key_features]

            # 6. Determine Status (Simulated)
            # TODO: Replace with actual deployment success/failure check
            deployment_succeeded = random.random() > 0.05 # 95% success chance

            if not deployment_succeeded:
                failure_reason = "Simulated random deployment failure."
                print(f"Simulated deployment FAILED for {input_data.brand_name}: {failure_reason}")
                await context.emit(Event(
                    type="deployment.failed",
                    payload=DeploymentFailedPayload(
                        brand_name=input_data.brand_name,
                        reason=failure_reason,
                        deployment_details=deployment_details, # Include partial details
                        dns_settings=dns_settings
                    ).model_dump()
                ))
                return

            # 7. Construct Success Payload and Emit Event
            success_payload = DeploymentResultPayload(
                deployment_url=deployment_url,
                status="ACTIVE",
                brand_name=input_data.brand_name,
                features_deployed=features_deployed,
                monitoring_url=monitoring_url,
                deployment_details=deployment_details,
                domains=domains,
                dns_settings=dns_settings
            )

            await context.emit(Event(
                type="deployment.succeeded",
                payload=success_payload.model_dump()
            ))
            print(f"Simulated deployment finished. Status: ACTIVE, URL: {deployment_url}")

        except Exception as e:
            # Catch unexpected errors during the simulation/deployment logic
            print(f"Unexpected error during deployment simulation for {input_data.brand_name}: {e}")
            await context.emit(Event(
                type="deployment.failed",
                payload=DeploymentFailedPayload(
                    brand_name=input_data.brand_name,
                    reason=f"Unexpected runtime error: {e}",
                    # Attempt to include partial details if available before error
                    deployment_details=deployment_details if 'deployment_details' in locals() else None,
                    dns_settings=dns_settings if 'dns_settings' in locals() else None
                ).model_dump()
            ))

        print("DeploymentAgent run_async finished.")


# --- Example Usage (ADK context simulation - for local testing) ---
# Note: This requires google-adk library to be installed.
# You would typically run this within an ADK environment.
async def run_agent_locally():
    print("Running DeploymentAgent example locally (simulating ADK context)...")
    agent = DeploymentAgent()

    # Example Input Data (matching DeploymentAgentInputData)
    test_input_data = {
        "brand_name": "NovaSpark AI",
        "product_concept": "Improved AI Agent Framework for Autonomous Income",
        "key_features": [
            {"feature_name": "Visual Workflow Builder", "desc": "..."},
            {"feature_name": "Pre-built Income Templates", "desc": "..."},
            {"feature_name": "Automated Deployment to Vercel", "desc": "..."},
            {"feature_name": "Analytics Dashboard", "desc": "..."}
        ]
    }

    # Simulate ADK InvocationContext and Input Event
    class MockInputEvent:
        data = test_input_data

    class MockInvocationContext:
        def __init__(self):
            self.input = MockInputEvent()
            self.emitted_events = []

        async def emit(self, event: Event):
            print(f"\n--- Agent Emitted Event ---")
            print(f"Type: {event.type}")
            print(f"Payload: {event.payload}")
            print("--------------------------")
            self.emitted_events.append(event)

    mock_context = MockInvocationContext()

    try:
        await agent.run_async(mock_context)
        print("\nAgent execution finished locally.")
        # You can inspect mock_context.emitted_events here if needed
    except Exception as e:
        print(f"Agent execution failed locally: {e}")

if __name__ == "__main__":
    # To run the async local test:
    try:
        asyncio.run(run_agent_locally())
    except ImportError:
        print("\nNote: Cannot run local async test. 'google-adk' library not found.")
        print("The agent code structure is updated, but local execution requires the ADK.")