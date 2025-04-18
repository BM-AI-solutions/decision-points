import os
import random
import string
import datetime
import asyncio
import json
import time
import tempfile
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional

import httpx # For Vercel API calls
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

# --- Data Models (Output structure for Event payload) ---
# Refined for Vercel deployment

class VercelDeploymentDetails(BaseModel):
    """Specific details about the Vercel deployment."""
    vercel_deployment_id: str
    project_name: str # Name used in Vercel
    deployment_time_utc: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())
    region: str = "default" # Vercel might provide this, default for now

class DeploymentResultPayload(BaseModel):
    """Payload for the successful deployment event."""
    deployment_url: HttpUrl # The primary URL provided by Vercel
    status: str = "READY" # Vercel uses READY for successful deployments
    brand_name: str
    features_deployed: List[str] # List of feature names deployed (from input)
    vercel_details: VercelDeploymentDetails

class DeploymentFailedPayload(BaseModel):
    """Payload for the failed deployment event."""
    brand_name: str
    reason: str
    error_details: Optional[Dict[str, Any]] = None # To capture Vercel API error specifics
    vercel_deployment_id: Optional[str] = None # If deployment was initiated but failed

# --- Agent Class ---

class DeploymentAgent(Agent):
    """
    ADK Agent responsible for Stage 4: Deployment.
    Deploys a simple placeholder application to Vercel based on branding info.
    Reads input from context, interacts with Vercel API, emits 'deployment.succeeded' or 'deployment.failed'.
    Requires VERCEL_API_TOKEN and optionally VERCEL_TEAM_ID environment variables.
    """
    VERCEL_API_BASE_URL = "https://api.vercel.com"
    # Deployment polling settings
    POLL_INTERVAL_SECONDS = 5
    MAX_POLL_ATTEMPTS = 24 # 2 minutes total

    def __init__(self):
        """Initialize the Deployment Agent and load Vercel credentials."""
        super().__init__()
        print("DeploymentAgent initialized.")
        self.vercel_api_token = os.environ.get("VERCEL_API_TOKEN")
        self.vercel_team_id = os.environ.get("VERCEL_TEAM_ID") # Optional team context
        self.http_client = httpx.AsyncClient(
            headers={
                "Authorization": f"Bearer {self.vercel_api_token}",
                "Content-Type": "application/json"
            },
            timeout=30.0 # Set a reasonable timeout for API calls
        )
        if not self.vercel_api_token:
            print("WARNING: VERCEL_API_TOKEN environment variable not set. Deployment will fail.")
        # TODO: Consider adding a check or method to validate the token early if needed

    def _generate_project_name(self, brand_name: str) -> str:
        """Generates a Vercel-compatible project name."""
        sanitized = ''.join(c for c in brand_name.lower() if c.isalnum() or c == '-')
        sanitized = sanitized.replace(' ', '-')
        # Ensure it doesn't start/end with hyphen and is within length limits (e.g., < 100)
        sanitized = sanitized.strip('-')[:90] # Apply length limit, adjust as needed
        if not sanitized:
            sanitized = f"deployment-{random.randint(1000, 9999)}" # Fallback
        return sanitized

    async def _prepare_deployment_files(self, temp_dir: Path, brand_name: str) -> Dict[str, Dict[str, Any]]:
        """Creates placeholder files and returns Vercel file structure."""
        files_to_deploy = {}
        file_data = {}

        # 1. Create index.html
        index_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{brand_name}</title>
    <style>
        body {{ font-family: sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; background-color: #f0f0f0; }}
        h1 {{ color: #333; }}
    </style>
</head>
<body>
    <h1>Welcome to {brand_name}!</h1>
    <p>Deployment successful via ADK Agent.</p>
</body>
</html>"""
        index_path = temp_dir / "index.html"
        index_path.write_text(index_content, encoding='utf-8')
        files_to_deploy["index.html"] = index_path

        # 2. Create vercel.json (minimal)
        vercel_config = {
            "version": 2,
            "builds": [{"src": "index.html", "use": "@vercel/static"}]
            # Add more config if needed (e.g., routes, env vars)
        }
        vercel_json_path = temp_dir / "vercel.json"
        vercel_json_path.write_text(json.dumps(vercel_config, indent=2), encoding='utf-8')
        files_to_deploy["vercel.json"] = vercel_json_path

        # 3. Calculate hashes and sizes for Vercel API
        for name, path in files_to_deploy.items():
            content = path.read_bytes()
            digest = hashlib.sha1(content).hexdigest()
            file_data[name] = {
                "file": name,
                "sha": digest,
                "size": len(content),
                "path": path # Keep path for upload step
            }
        return file_data

    async def _upload_file_to_vercel(self, file_info: Dict[str, Any]):
        """Uploads a single file to Vercel."""
        upload_url = f"{self.VERCEL_API_BASE_URL}/v2/files"
        headers = {
            "Authorization": f"Bearer {self.vercel_api_token}",
            "Content-Length": str(file_info["size"]),
            "x-vercel-digest": file_info["sha"],
            # Potentially add 'x-vercel-content-type' if needed
        }
        if self.vercel_team_id:
            headers["TeamId"] = self.vercel_team_id

        try:
            async with self.http_client.stream("POST", upload_url, headers=headers, data=file_info["path"].read_bytes()) as response:
                if response.status_code == 200:
                    print(f"Successfully uploaded file: {file_info['file']}")
                    return True
                else:
                    error_content = await response.aread()
                    print(f"Error uploading file {file_info['file']}: {response.status_code} - {error_content.decode()}")
                    return False
        except httpx.RequestError as e:
            print(f"HTTP error uploading file {file_info['file']}: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error uploading file {file_info['file']}: {e}")
            return False

    async def _trigger_vercel_deployment(self, project_name: str, files_data: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Triggers the Vercel deployment with uploaded file details."""
        deployment_url = f"{self.VERCEL_API_BASE_URL}/v13/deployments"
        params = {}
        if self.vercel_team_id:
            params["teamId"] = self.vercel_team_id

        payload = {
            "name": project_name, # Vercel uses 'name' for the project identifier
            "files": [
                {"file": f_data["file"], "sha": f_data["sha"], "size": f_data["size"]}
                for f_data in files_data
            ],
            "projectSettings": { # Basic settings, can be expanded
                "framework": None # Explicitly null for static deployment
            },
            "target": "production" # Deploy directly to production
            # Add 'gitSource', 'env', etc. if needed
        }

        try:
            response = await self.http_client.post(deployment_url, params=params, json=payload)
            response.raise_for_status() # Raise HTTPStatusError for bad responses (4xx or 5xx)
            deployment_data = response.json()
            print(f"Successfully initiated Vercel deployment: ID {deployment_data.get('id')}")
            return deployment_data
        except httpx.HTTPStatusError as e:
            error_details = None
            try:
                error_details = e.response.json()
            except json.JSONDecodeError:
                error_details = {"raw_content": e.response.text}
            print(f"HTTP error triggering Vercel deployment: {e.response.status_code} - {error_details}")
            return {"error": "trigger_failed", "status_code": e.response.status_code, "details": error_details}
        except httpx.RequestError as e:
            print(f"Network error triggering Vercel deployment: {e}")
            return {"error": "network_error", "details": str(e)}
        except Exception as e:
            print(f"Unexpected error triggering Vercel deployment: {e}")
            return {"error": "unexpected", "details": str(e)}

    async def _monitor_vercel_deployment(self, deployment_id: str) -> Optional[Dict[str, Any]]:
        """Polls Vercel API for deployment status."""
        status_url = f"{self.VERCEL_API_BASE_URL}/v13/deployments/{deployment_id}"
        params = {}
        if self.vercel_team_id:
            params["teamId"] = self.vercel_team_id

        print(f"Monitoring Vercel deployment {deployment_id}...")
        for attempt in range(self.MAX_POLL_ATTEMPTS):
            try:
                response = await self.http_client.get(status_url, params=params)
                response.raise_for_status()
                status_data = response.json()
                state = status_data.get("readyState")
                print(f"  Attempt {attempt + 1}/{self.MAX_POLL_ATTEMPTS}: Deployment state = {state}")

                if state == "READY":
                    print("Deployment successful!")
                    return status_data
                elif state in ["ERROR", "CANCELED"]:
                    print(f"Deployment failed or canceled. State: {state}")
                    return {"error": "deployment_failed", "state": state, "details": status_data.get("error")}
                elif state == "BUILDING" or state == "QUEUED" or state == "INITIALIZING":
                    # Continue polling
                    await asyncio.sleep(self.POLL_INTERVAL_SECONDS)
                else:
                    print(f"Unknown deployment state encountered: {state}")
                    # Decide whether to treat as failure or keep polling
                    await asyncio.sleep(self.POLL_INTERVAL_SECONDS) # Poll anyway for now

            except httpx.HTTPStatusError as e:
                error_details = None
                try:
                    error_details = e.response.json()
                except json.JSONDecodeError:
                    error_details = {"raw_content": e.response.text}
                print(f"HTTP error monitoring deployment {deployment_id}: {e.response.status_code} - {error_details}")
                # Consider if this is a terminal failure or worth retrying
                if attempt == self.MAX_POLL_ATTEMPTS - 1:
                    return {"error": "monitoring_http_error", "status_code": e.response.status_code, "details": error_details}
                await asyncio.sleep(self.POLL_INTERVAL_SECONDS) # Retry after error
            except httpx.RequestError as e:
                print(f"Network error monitoring deployment {deployment_id}: {e}")
                if attempt == self.MAX_POLL_ATTEMPTS - 1:
                    return {"error": "monitoring_network_error", "details": str(e)}
                await asyncio.sleep(self.POLL_INTERVAL_SECONDS) # Retry after error
            except Exception as e:
                 print(f"Unexpected error monitoring deployment {deployment_id}: {e}")
                 if attempt == self.MAX_POLL_ATTEMPTS - 1:
                     return {"error": "monitoring_unexpected_error", "details": str(e)}
                 await asyncio.sleep(self.POLL_INTERVAL_SECONDS) # Retry after error

        print("Deployment monitoring timed out.")
        return {"error": "timeout", "details": f"Deployment did not reach READY state after {self.MAX_POLL_ATTEMPTS * self.POLL_INTERVAL_SECONDS} seconds."}


    async def run_async(self, context: InvocationContext):
        """Executes the Vercel deployment workflow."""
        print("DeploymentAgent run_async started.")
        deployment_id = None # Track deployment ID for potential failure reporting

        # 1. Check Credentials
        if not self.vercel_api_token:
            print("Deployment failed: VERCEL_API_TOKEN is not configured.")
            await context.emit(Event(
                type="deployment.failed",
                payload=DeploymentFailedPayload(
                    brand_name="Unknown (Config Error)",
                    reason="Vercel API token not configured in environment variables.",
                ).model_dump()
            ))
            return

        # 2. Validate and parse input
        try:
            input_data = DeploymentAgentInputData(**context.input.data)
            print(f"Starting Vercel deployment for brand: {input_data.brand_name}")
        except ValidationError as e:
            print(f"Input validation failed: {e}")
            await context.emit(Event(
                type="deployment.failed",
                payload=DeploymentFailedPayload(
                    brand_name="Unknown (Input Error)",
                    reason=f"Invalid input data: {e}",
                    error_details={"validation_errors": e.errors()}
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
                    error_details={"exception": str(e)}
                ).model_dump()
            ))
            return

        # --- Vercel Deployment Logic ---
        temp_dir_obj = None
        try:
            # 3. Prepare Files in a Temporary Directory
            temp_dir_obj = tempfile.TemporaryDirectory()
            temp_dir = Path(temp_dir_obj.name)
            print(f"Preparing deployment files in temporary directory: {temp_dir}")
            files_data_map = await self._prepare_deployment_files(temp_dir, input_data.brand_name)
            files_list = list(files_data_map.values()) # List format needed for trigger

            # 4. Upload Files to Vercel
            print("Uploading files to Vercel...")
            upload_tasks = [self._upload_file_to_vercel(file_info) for file_info in files_list]
            upload_results = await asyncio.gather(*upload_tasks)

            if not all(upload_results):
                failed_files = [files_list[i]["file"] for i, success in enumerate(upload_results) if not success]
                print(f"Deployment failed: File upload failed for: {', '.join(failed_files)}")
                await context.emit(Event(
                    type="deployment.failed",
                    payload=DeploymentFailedPayload(
                        brand_name=input_data.brand_name,
                        reason="Failed to upload one or more files to Vercel.",
                        error_details={"failed_files": failed_files}
                    ).model_dump()
                ))
                return # Exit early

            print("All files uploaded successfully.")

            # 5. Trigger Deployment
            project_name = self._generate_project_name(input_data.brand_name)
            print(f"Triggering Vercel deployment for project: {project_name}")
            trigger_result = await self._trigger_vercel_deployment(project_name, files_list)

            if not trigger_result or trigger_result.get("error"):
                reason = f"Failed to trigger Vercel deployment: {trigger_result.get('error', 'Unknown trigger error')}"
                print(f"Deployment failed: {reason}")
                await context.emit(Event(
                    type="deployment.failed",
                    payload=DeploymentFailedPayload(
                        brand_name=input_data.brand_name,
                        reason=reason,
                        error_details=trigger_result.get("details")
                    ).model_dump()
                ))
                return

            deployment_id = trigger_result.get("id")
            if not deployment_id:
                 print(f"Deployment failed: Trigger response missing deployment ID.")
                 await context.emit(Event(
                    type="deployment.failed",
                    payload=DeploymentFailedPayload(
                        brand_name=input_data.brand_name,
                        reason="Vercel API did not return a deployment ID after trigger.",
                        error_details=trigger_result # Include full trigger response
                    ).model_dump()
                ))
                 return

            # 6. Monitor Deployment Status
            monitor_result = await self._monitor_vercel_deployment(deployment_id)

            if not monitor_result or monitor_result.get("error"):
                reason = f"Deployment failed during monitoring: {monitor_result.get('error', 'Unknown monitoring error')}"
                print(f"Deployment failed: {reason}")
                await context.emit(Event(
                    type="deployment.failed",
                    payload=DeploymentFailedPayload(
                        brand_name=input_data.brand_name,
                        reason=reason,
                        error_details=monitor_result.get("details"),
                        vercel_deployment_id=deployment_id
                    ).model_dump()
                ))
                return

            # 7. Deployment Succeeded - Construct Payload and Emit Event
            deployment_url = f"https://{monitor_result.get('url')}" # Vercel provides the final URL
            features_deployed = [f.get("feature_name", "Unknown Feature") for f in input_data.key_features]

            success_payload = DeploymentResultPayload(
                deployment_url=deployment_url,
                brand_name=input_data.brand_name,
                features_deployed=features_deployed,
                vercel_details=VercelDeploymentDetails(
                    vercel_deployment_id=deployment_id,
                    project_name=project_name, # Use the name we sent
                    region=monitor_result.get("regions", ["default"])[0] # Get region if available
                )
            )

            await context.emit(Event(
                type="deployment.succeeded",
                payload=success_payload.model_dump()
            ))
            print(f"Vercel deployment finished successfully. Status: READY, URL: {deployment_url}")

        except httpx.HTTPStatusError as e:
            error_details = None
            try:
                error_details = e.response.json()
            except json.JSONDecodeError:
                 error_details = {"raw_content": e.response.text}
            print(f"HTTP Status Error during deployment for {input_data.brand_name}: {e.response.status_code} - {error_details}")
            await context.emit(Event(
                type="deployment.failed",
                payload=DeploymentFailedPayload(
                    brand_name=input_data.brand_name,
                    reason=f"Vercel API request failed with status {e.response.status_code}.",
                    error_details=error_details,
                    vercel_deployment_id=deployment_id
                ).model_dump()
            ))
        except httpx.RequestError as e:
            print(f"Network error during deployment for {input_data.brand_name}: {e}")
            await context.emit(Event(
                type="deployment.failed",
                payload=DeploymentFailedPayload(
                    brand_name=input_data.brand_name,
                    reason=f"Network error communicating with Vercel API: {e}",
                    error_details={"exception": str(e)},
                    vercel_deployment_id=deployment_id
                ).model_dump()
            ))
        except Exception as e:
            # Catch unexpected errors during the deployment logic
            print(f"Unexpected error during Vercel deployment for {input_data.brand_name}: {e}")
            import traceback
            traceback.print_exc() # Print stack trace for debugging
            await context.emit(Event(
                type="deployment.failed",
                payload=DeploymentFailedPayload(
                    brand_name=input_data.brand_name,
                    reason=f"Unexpected runtime error during deployment: {e}",
                    error_details={"exception": str(e), "trace": traceback.format_exc()},
                    vercel_deployment_id=deployment_id
                ).model_dump()
            ))
        finally:
            # 8. Clean up temporary directory
            if temp_dir_obj:
                try:
                    temp_dir_obj.cleanup()
                    print(f"Cleaned up temporary directory: {temp_dir}")
                except Exception as e:
                    print(f"Warning: Failed to clean up temporary directory {temp_dir}: {e}")
            # Close the httpx client
            await self.http_client.aclose()
            print("Closed httpx client.")

        print("DeploymentAgent run_async finished.")


# --- Example Usage (ADK context simulation - for local testing) ---
# Note: This requires google-adk library and httpx to be installed.
# You also need to set VERCEL_API_TOKEN environment variable.
async def run_agent_locally():
    print("Running DeploymentAgent example locally (simulating ADK context)...")

    # Ensure VERCEL_API_TOKEN is set for local testing
    if not os.environ.get("VERCEL_API_TOKEN"):
        print("\nERROR: Set the VERCEL_API_TOKEN environment variable to run this local test.")
        print("Example: export VERCEL_API_TOKEN='your_token_here'")
        return

    agent = DeploymentAgent()

    # Example Input Data (matching DeploymentAgentInputData)
    test_input_data = {
        "brand_name": f"ADK Test Deploy {random.randint(1000, 9999)}", # Unique name
        "product_concept": "Test deployment from ADK Agent local run",
        "key_features": [
            {"feature_name": "Basic HTML", "desc": "A simple test page."},
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
            # Pretty print payload
            try:
                payload_str = json.dumps(event.payload, indent=2)
            except TypeError: # Handle non-serializable types if any sneak in
                payload_str = str(event.payload)
            print(f"Payload:\n{payload_str}")
            print("--------------------------")
            self.emitted_events.append(event)

    mock_context = MockInvocationContext()

    try:
        await agent.run_async(mock_context)
        print("\nAgent execution finished locally.")
        # You can inspect mock_context.emitted_events here if needed
    except Exception as e:
        print(f"Agent execution failed locally: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # To run the async local test:
    try:
        # Load .env file if present for local testing convenience
        from dotenv import load_dotenv
        load_dotenv()
        print("Attempted to load .env file for local run.")
    except ImportError:
        print("dotenv library not found, skipping .env load for local run.")

    try:
        asyncio.run(run_agent_locally())
    except ImportError as e:
        print(f"\nNote: Cannot run local async test. Required library not found: {e}")
        print("Ensure 'google-adk', 'httpx', and 'python-dotenv' are installed.")