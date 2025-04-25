"""
Deployment Agent for Decision Points.

This agent deploys applications to Vercel or Netlify based on generated code.
It implements the A2A protocol for agent communication.
"""

import os
import random
import string
import datetime
import asyncio
import json
import time
import tempfile
import hashlib
import zipfile
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

import httpx
from pydantic import BaseModel, Field, HttpUrl, ValidationError

# ADK Imports
from google.adk.runtime import InvocationContext
from google.adk.runtime.events import Event

# A2A Imports
from python_a2a import skill

from agents.base_agent import BaseSpecializedAgent
from app.config import settings

# Configure logging
logger = logging.getLogger(__name__)


# --- Data Models (Input structure expected in context.input.data) ---

class DeploymentAgentInputData(BaseModel):
    """Expected data structure within context.input.data."""
    brand_name: str = Field(description="The final brand name for the product.")
    product_concept: str = Field(description="Description of the product being deployed.")
    key_features: List[Dict[str, Any]] = Field(description="List of features included in the deployment.")
    deployment_target: str = Field(default='vercel', description="Deployment target ('vercel' or 'netlify').")
    generated_code_dict: Optional[Dict[str, str]] = Field(default=None, description="Dictionary mapping file paths to code content, provided by CodeGenerationAgent.")
    # Optional: Add vercel_project_name, deployment_environment etc. if needed for Vercel

# --- Data Models (Output structure for Event payload) ---

# --- Data Models (Output structure for Event payload) ---
# Refined for Vercel deployment

class VercelDeploymentDetails(BaseModel):
    """Specific details about the Vercel deployment."""
    vercel_deployment_id: str
    project_name: str # Name used in Vercel
    deployment_time_utc: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())
    region: str = "default" # Vercel might provide this, default for now

class NetlifyDeploymentDetails(BaseModel):
    """Specific details about the Netlify deployment."""
    netlify_deployment_id: str
    site_id: str # The Netlify site ID used or created
    deployment_time_utc: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())
    # Add other relevant Netlify details if available, e.g., deploy_ssl_url

class DeploymentResultPayload(BaseModel):
    """Payload for the successful deployment event."""
    deployment_url: HttpUrl # The primary URL provided by the platform
    status: str = "READY" # Common status for successful deployments
    brand_name: str
    features_deployed: List[str] # List of feature names deployed (from input)
    platform: str = Field(description="The platform deployed to ('vercel' or 'netlify')")
    deployment_details: Union[VercelDeploymentDetails, NetlifyDeploymentDetails]

class DeploymentFailedPayload(BaseModel):
    """Payload for the failed deployment event."""
    brand_name: str
    platform: str = Field(description="The platform attempted ('vercel' or 'netlify')")
    reason: str
    error_details: Optional[Dict[str, Any]] = None # To capture API error specifics
    vercel_deployment_id: Optional[str] = None # If deployment was initiated but failed
    netlify_site_id: Optional[str] = None # If site was targeted/created
    netlify_deployment_id: Optional[str] = None # If deployment was initiated but failed

# --- Agent Class ---

class DeploymentAgent(BaseSpecializedAgent):
    """
    Agent responsible for deployment.
    Deploys applications to Vercel or Netlify based on generated code.
    Implements A2A protocol for agent communication.
    """
    VERCEL_API_BASE_URL = "https://api.vercel.com"
    NETLIFY_API_BASE_URL = "https://api.netlify.com/api/v1"
    # Deployment polling settings
    POLL_INTERVAL_SECONDS = 5
    MAX_POLL_ATTEMPTS = 24 # 2 minutes total

    def __init__(
        self,
        name: str = "deployment",
        description: str = "Deploys applications to Vercel or Netlify based on generated code",
        model_name: Optional[str] = None,
        port: Optional[int] = None,
        **kwargs: Any,
    ):
        """
        Initialize the DeploymentAgent.

        Args:
            name: The name of the agent.
            description: The description of the agent.
            model_name: The name of the model to use. Defaults to settings.GEMINI_MODEL_NAME.
            port: The port to run the A2A server on. Defaults to settings.DEPLOYMENT_AGENT_URL port.
            **kwargs: Additional arguments for BaseSpecializedAgent.
        """
        # Extract port from URL if not provided
        if port is None and settings.DEPLOYMENT_AGENT_URL:
            try:
                port = int(settings.DEPLOYMENT_AGENT_URL.split(':')[-1])
            except (ValueError, IndexError):
                port = 8008  # Default port

        # Initialize BaseSpecializedAgent
        super().__init__(
            name=name,
            description=description,
            model_name=model_name,
            port=port,
            **kwargs
        )

        logger.info("DeploymentAgent initialized.")
        self.vercel_api_token = os.environ.get("VERCEL_API_TOKEN") or settings.VERCEL_API_TOKEN
        self.vercel_team_id = os.environ.get("VERCEL_TEAM_ID") or settings.VERCEL_TEAM_ID
        self.netlify_auth_token = os.environ.get("NETLIFY_AUTH_TOKEN") or settings.NETLIFY_AUTH_TOKEN
        self.netlify_site_id = os.environ.get("NETLIFY_SITE_ID") or settings.NETLIFY_SITE_ID

        # Client for Vercel
        self.vercel_client = httpx.AsyncClient(
            base_url=self.VERCEL_API_BASE_URL,
            headers={
                "Authorization": f"Bearer {self.vercel_api_token}",
                "Content-Type": "application/json"
            },
            timeout=30.0 # Set a reasonable timeout for API calls
        )
        # Client for Netlify
        self.netlify_client = httpx.AsyncClient(
            base_url=self.NETLIFY_API_BASE_URL,
            headers={
                "Authorization": f"Bearer {self.netlify_auth_token}",
                # Content-Type might vary per request (e.g., application/zip for deploy)
            },
            timeout=60.0 # Potentially longer timeout for uploads
        )

        if not self.vercel_api_token:
            logger.warning("VERCEL_API_TOKEN not configured. Vercel deployment will fail.")
        if not self.netlify_auth_token:
            logger.warning("NETLIFY_AUTH_TOKEN not configured. Netlify deployment will fail.")

        logger.info(f"DeploymentAgent initialized with port: {self.port}")

    def _generate_vercel_project_name(self, brand_name: str) -> str:
        """Generates a Vercel-compatible project name."""
        sanitized = ''.join(c for c in brand_name.lower() if c.isalnum() or c == '-')
        sanitized = sanitized.replace(' ', '-')
        # Ensure it doesn't start/end with hyphen and is within length limits (e.g., < 100)
        sanitized = sanitized.strip('-')[:90] # Apply length limit, adjust as needed
        if not sanitized:
            sanitized = f"deployment-{random.randint(1000, 9999)}" # Fallback
        return sanitized

    def _generate_netlify_site_name(self, brand_name: str) -> str:
        """Generates a potential Netlify site name (subdomain)."""
        sanitized = ''.join(c for c in brand_name.lower() if c.isalnum()) # Netlify prefers just alphanumeric
        sanitized = sanitized.replace(' ', '') # No spaces
        sanitized = sanitized.strip('-')[:60] # Apply length limit
        if not sanitized:
            sanitized = f"adk-site-{random.randint(1000, 9999)}" # Fallback
        # Netlify might add suffixes if name is taken, this is just a suggestion
        return sanitized

    async def _prepare_files_from_dict(self, temp_dir: Path, generated_code_dict: Dict[str, str]) -> Dict[str, Dict[str, Any]]:
        """Creates files from the provided dictionary and returns Vercel file structure."""
        print(f"Preparing files from generated_code_dict in {temp_dir}")
        file_data = {}

        try:
            for relative_path_str, code_content in generated_code_dict.items():
                # Ensure relative paths are handled correctly (no leading '/')
                if relative_path_str.startswith('/'):
                    relative_path_str = relative_path_str[1:]

                absolute_path = temp_dir / relative_path_str
                print(f"  Processing: {relative_path_str} -> {absolute_path}")

                # Create parent directories if they don't exist
                absolute_path.parent.mkdir(parents=True, exist_ok=True)

                # Write file content (assuming text, adjust if binary needed)
                # Vercel API needs bytes for hash/upload, so encode here
                content_bytes = code_content.encode('utf-8')
                absolute_path.write_bytes(content_bytes)

                # Calculate hash and size for Vercel API
                digest = hashlib.sha1(content_bytes).hexdigest()
                size = len(content_bytes)

                file_data[relative_path_str] = {
                    "file": relative_path_str, # Use the relative path as the key Vercel expects
                    "sha": digest,
                    "size": size,
                    "path": absolute_path # Keep absolute path for reading during upload
                }
                print(f"    Prepared: {relative_path_str} (Size: {size}, SHA: {digest[:7]}...)")

            # Add vercel.json if not provided by the generator, as it's often needed
            if "vercel.json" not in file_data:
                 print("  Adding default vercel.json as it was not provided.")
                 vercel_json_content = """{"framework": "vite"}""" # Minimal default
                 vercel_json_path = temp_dir / "vercel.json"
                 content_bytes = vercel_json_content.encode('utf-8')
                 vercel_json_path.write_bytes(content_bytes)
                 digest = hashlib.sha1(content_bytes).hexdigest()
                 size = len(content_bytes)
                 file_data["vercel.json"] = {
                     "file": "vercel.json",
                     "sha": digest,
                     "size": size,
                     "path": vercel_json_path
                 }
                 print(f"    Prepared: vercel.json (Size: {size}, SHA: {digest[:7]}...)")


            return file_data

        except OSError as e:
            print(f"Error creating deployment files/directories from dict: {e}")
            raise ValueError(f"Failed to prepare deployment files from dict: {e}") from e
        except Exception as e:
            print(f"Unexpected error preparing deployment files from dict: {e}")
            import traceback
            traceback.print_exc()
            raise ValueError(f"Unexpected error preparing deployment files from dict: {e}") from e

    async def _upload_file_to_vercel(self, file_info: Dict[str, Any]):
        """Uploads a single file to Vercel using the dedicated client."""
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
            # Read bytes directly from the path stored in file_info
            file_bytes = file_info["path"].read_bytes()
            # Use httpx client directly for streaming upload
            response = await self.vercel_client.post(upload_url, headers=headers, content=file_bytes)

            if response.status_code == 200:
                print(f"Successfully uploaded file: {file_info['file']}")
                return True
            else:
                error_content = response.text # Read text directly
                print(f"Error uploading file {file_info['file']}: {response.status_code} - {error_content}")
                return False
        except httpx.RequestError as e:
            print(f"HTTP error uploading file {file_info['file']}: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error uploading file {file_info['file']}: {e}")
            import traceback
            traceback.print_exc()
            return False


    # --- Netlify file preparation (Zip from Dict) ---
    async def _prepare_zip_from_dict(self, temp_dir: Path, project_name: str, generated_code_dict: Dict[str, str]) -> Path:
        """Creates files from the provided dictionary within a site_root and zips it for Netlify."""
        print(f"Preparing Netlify source zip from generated_code_dict for '{project_name}' in {temp_dir}")
        site_root_dir = temp_dir / "site_root" # Root of the zip content

        try:
            # Create the base directory for zip contents
            site_root_dir.mkdir(parents=True, exist_ok=True)

            # --- Create Files from Dictionary ---
            for relative_path_str, code_content in generated_code_dict.items():
                # Ensure relative paths are handled correctly (no leading '/')
                if relative_path_str.startswith('/'):
                    relative_path_str = relative_path_str[1:]

                absolute_path = site_root_dir / relative_path_str
                print(f"  Processing for zip: {relative_path_str} -> {absolute_path}")

                # Create parent directories if they don't exist within site_root_dir
                absolute_path.parent.mkdir(parents=True, exist_ok=True)

                # Write file content (assuming text)
                absolute_path.write_text(code_content, encoding='utf-8')

            # --- Create the zip archive ---
            zip_filename = f"{project_name}-netlify-src.zip"
            zip_path = temp_dir / zip_filename
            print(f"Creating Netlify deployment source zip: {zip_path}")

            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in site_root_dir.rglob('*'):
                    if file_path.is_file():
                        # Add file to zip using relative path from site_root_dir
                        relative_path = file_path.relative_to(site_root_dir)
                        zipf.write(file_path, relative_path)
                        print(f"    Adding to zip: {relative_path}")

            print(f"  Created deployment source zip: {zip_path} (Size: {zip_path.stat().st_size} bytes)")
            # Reminder about Netlify build config is still relevant
            print("  NOTE: Netlify site must be configured with appropriate build command and publish directory if build is needed.")
            return zip_path

        except OSError as e:
            print(f"Error creating Netlify zip files/directories from dict: {e}")
            raise ValueError(f"Failed to prepare Netlify zip from dict: {e}") from e
        except Exception as e:
            print(f"Unexpected error preparing Netlify zip from dict: {e}")
            import traceback
            traceback.print_exc()
            raise ValueError(f"Unexpected error preparing Netlify zip from dict: {e}") from e


    async def _trigger_vercel_deployment(self, project_name: str, files_data: List[Dict[str, Any]], target_environment: str) -> Optional[Dict[str, Any]]:
        """Triggers the Vercel deployment with uploaded file details and target environment."""
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
                "framework": "vite" # Hint Vercel to use Vite build presets
            },
            "target": target_environment, # Use the provided environment
            # Add 'gitSource', 'env', etc. if needed
            "project": project_name # Associate with an existing project or let Vercel create one
        }

        try:
            response = await self.vercel_client.post(deployment_url, params=params, json=payload)
            response.raise_for_status() # Raise HTTPStatusError for bad responses (4xx or 5xx)
            deployment_data = response.json()
            print(f"Successfully initiated Vercel deployment: ID {deployment_data.get('id')} for project '{project_name}' to target '{target_environment}'")
            return deployment_data
        except httpx.HTTPStatusError as e:
            error_details = None
            try:
                error_details = e.response.json()
            except json.JSONDecodeError:
                error_details = {"raw_content": e.response.text}
            print(f"HTTP error triggering Vercel deployment for project '{project_name}': {e.response.status_code} - {error_details}")
            return {"error": "trigger_failed", "status_code": e.response.status_code, "details": error_details}
        except httpx.RequestError as e:
            print(f"Network error triggering Vercel deployment for project '{project_name}': {e}")
            return {"error": "network_error", "details": str(e)}
        except Exception as e:
            print(f"Unexpected error triggering Vercel deployment for project '{project_name}': {e}")
            return {"error": "unexpected", "details": str(e)}

    # --- _monitor_vercel_deployment remains the same ---
    async def _monitor_vercel_deployment(self, deployment_id: str, project_name: str) -> Optional[Dict[str, Any]]:
        # ... (No changes needed here, but add project_name to logging) ...
        status_url = f"{self.VERCEL_API_BASE_URL}/v13/deployments/{deployment_id}"
        params = {}
        if self.vercel_team_id:
            params["teamId"] = self.vercel_team_id

        print(f"Monitoring Vercel deployment {deployment_id} for project '{project_name}'...")
        for attempt in range(self.MAX_POLL_ATTEMPTS):
            try:
                response = await self.vercel_client.get(status_url, params=params)
                response.raise_for_status()
                status_data = response.json()
                state = status_data.get("readyState")
                print(f"  Attempt {attempt + 1}/{self.MAX_POLL_ATTEMPTS}: Project '{project_name}', Deployment {deployment_id}, State = {state}")

                if state == "READY":
                    print(f"Deployment successful for project '{project_name}'!")
                    return status_data
                elif state in ["ERROR", "CANCELED"]:
                    print(f"Deployment failed or canceled for project '{project_name}'. State: {state}")
                    return {"error": "deployment_failed", "state": state, "details": status_data.get("error")}
                elif state in ["BUILDING", "QUEUED", "INITIALIZING"]:
                    # Continue polling
                    await asyncio.sleep(self.POLL_INTERVAL_SECONDS)
                else:
                    print(f"Unknown deployment state encountered for project '{project_name}': {state}")
                    # Decide whether to treat as failure or keep polling
                    await asyncio.sleep(self.POLL_INTERVAL_SECONDS) # Poll anyway for now

            except httpx.HTTPStatusError as e:
                error_details = None
                try:
                    error_details = e.response.json()
                except json.JSONDecodeError:
                    error_details = {"raw_content": e.response.text}
                print(f"HTTP error monitoring deployment {deployment_id} for project '{project_name}': {e.response.status_code} - {error_details}")
                # Consider if this is a terminal failure or worth retrying
                if attempt == self.MAX_POLL_ATTEMPTS - 1:
                    return {"error": "monitoring_http_error", "status_code": e.response.status_code, "details": error_details}
                await asyncio.sleep(self.POLL_INTERVAL_SECONDS) # Retry after error
            except httpx.RequestError as e:
                print(f"Network error monitoring deployment {deployment_id} for project '{project_name}': {e}")
                if attempt == self.MAX_POLL_ATTEMPTS - 1:
                    return {"error": "monitoring_network_error", "details": str(e)}
                await asyncio.sleep(self.POLL_INTERVAL_SECONDS) # Retry after error
            except Exception as e:
                 print(f"Unexpected error monitoring deployment {deployment_id} for project '{project_name}': {e}")
                 if attempt == self.MAX_POLL_ATTEMPTS - 1:
                     return {"error": "monitoring_unexpected_error", "details": str(e)}
                 await asyncio.sleep(self.POLL_INTERVAL_SECONDS) # Retry after error

        print(f"Deployment monitoring timed out for project '{project_name}'.")
        return {"error": "timeout", "details": f"Deployment {deployment_id} did not reach READY state after {self.MAX_POLL_ATTEMPTS * self.POLL_INTERVAL_SECONDS} seconds."}


    # --- Netlify API Helpers ---

    async def _create_netlify_site(self, brand_name: str) -> str:
        """Creates a new site on Netlify and returns the site ID."""
        site_name = self._generate_netlify_site_name(brand_name)
        create_url = "/sites"
        payload = {"name": site_name} # Basic site creation, can add more config
        print(f"Attempting to create Netlify site with suggested name: {site_name}")

        try:
            response = await self.netlify_client.post(create_url, json=payload)
            response.raise_for_status()
            site_data = response.json()
            site_id = site_data.get("site_id")
            if not site_id:
                raise ValueError("Netlify API did not return a site_id after creation.")
            print(f"Successfully created Netlify site: ID {site_id}, Name {site_data.get('name')}")
            return site_id
        except httpx.HTTPStatusError as e:
            error_details = None
            try:
                error_details = e.response.json()
                # Check for name conflict specifically
                if e.response.status_code == 422 and "name already exists" in str(error_details).lower():
                     print(f"Netlify site name '{site_name}' likely taken. Consider providing NETLIFY_SITE_ID or using a more unique brand name.")
                     # Could potentially retry with a different generated name here if desired
            except json.JSONDecodeError:
                error_details = {"raw_content": e.response.text}
            print(f"HTTP error creating Netlify site: {e.response.status_code} - {error_details}")
            raise ValueError(f"Failed to create Netlify site: {error_details}") from e
        except httpx.RequestError as e:
            print(f"Network error creating Netlify site: {e}")
            raise ValueError(f"Network error creating Netlify site: {e}") from e
        except Exception as e:
            print(f"Unexpected error creating Netlify site: {e}")
            raise ValueError(f"Unexpected error creating Netlify site: {e}") from e

    async def _upload_and_deploy_netlify(self, site_id: str, zip_path: Path) -> Dict[str, Any]:
        """Uploads the site zip and triggers a deployment on Netlify."""
        deploy_url = f"/sites/{site_id}/deploys"
        print(f"Uploading deployment zip '{zip_path.name}' to Netlify site {site_id}...")

        headers = {
            "Authorization": f"Bearer {self.netlify_auth_token}",
            "Content-Type": "application/zip", # Crucial for zip deploy
        }

        try:
            async with zip_path.open("rb") as f:
                zip_content = await f.read()

            response = await self.netlify_client.post(deploy_url, headers=headers, content=zip_content)
            response.raise_for_status()
            deploy_data = response.json()
            deployment_id = deploy_data.get("id")
            required_files = deploy_data.get("required", []) # Netlify might ask for specific files if zip is incomplete

            if not deployment_id:
                 raise ValueError("Netlify API did not return a deployment ID after upload.")
            if required_files:
                 # This indicates an issue with the zip or Netlify needing specific files uploaded individually
                 # For simple static sites, this shouldn't happen often if zip is correct
                 print(f"Warning: Netlify requires additional files: {required_files}. Deployment might be incomplete.")
                 # Handle this case if necessary - might involve uploading individual files based on 'required' list

            print(f"Successfully initiated Netlify deployment: ID {deployment_id} for site {site_id}")
            return deploy_data
        except httpx.HTTPStatusError as e:
            error_details = None
            try:
                error_details = e.response.json()
            except json.JSONDecodeError:
                error_details = {"raw_content": e.response.text}
            print(f"HTTP error deploying to Netlify site {site_id}: {e.response.status_code} - {error_details}")
            raise ValueError(f"Failed to deploy to Netlify: {error_details}") from e
        except httpx.RequestError as e:
            print(f"Network error deploying to Netlify site {site_id}: {e}")
            raise ValueError(f"Network error deploying to Netlify: {e}") from e
        except Exception as e:
            print(f"Unexpected error deploying to Netlify site {site_id}: {e}")
            raise ValueError(f"Unexpected error deploying to Netlify: {e}") from e


    async def _monitor_netlify_deployment(self, site_id: str, deployment_id: str) -> Dict[str, Any]:
        """Monitors a Netlify deployment until it succeeds or fails."""
        # Note: Netlify deployments are often very fast, but monitoring is good practice.
        # The deploy endpoint response might already contain the final state for simple deploys.
        status_url = f"/sites/{site_id}/deploys/{deployment_id}"
        print(f"Monitoring Netlify deployment {deployment_id} for site {site_id}...")

        for attempt in range(self.MAX_POLL_ATTEMPTS):
            try:
                response = await self.netlify_client.get(status_url)
                response.raise_for_status()
                status_data = response.json()
                state = status_data.get("state")
                print(f"  Attempt {attempt + 1}/{self.MAX_POLL_ATTEMPTS}: Site {site_id}, Deployment {deployment_id}, State = {state}")

                if state == "ready":
                    print(f"Netlify deployment successful for site {site_id}!")
                    return status_data
                elif state in ["error", "failed"]: # Check Netlify's specific failure states
                    error_message = status_data.get("error_message", "Unknown error")
                    print(f"Netlify deployment failed for site {site_id}. State: {state}, Reason: {error_message}")
                    return {"error": "deployment_failed", "state": state, "details": error_message}
                elif state in ["building", "uploading", "processing", "new"]: # Check Netlify's pending states
                    # Continue polling
                    await asyncio.sleep(self.POLL_INTERVAL_SECONDS)
                else:
                    print(f"Unknown Netlify deployment state encountered for site {site_id}: {state}")
                    await asyncio.sleep(self.POLL_INTERVAL_SECONDS) # Poll anyway

            except httpx.HTTPStatusError as e:
                error_details = None
                try:
                    error_details = e.response.json()
                except json.JSONDecodeError:
                    error_details = {"raw_content": e.response.text}
                print(f"HTTP error monitoring Netlify deployment {deployment_id}: {e.response.status_code} - {error_details}")
                if attempt == self.MAX_POLL_ATTEMPTS - 1:
                    return {"error": "monitoring_http_error", "status_code": e.response.status_code, "details": error_details}
                await asyncio.sleep(self.POLL_INTERVAL_SECONDS)
            except httpx.RequestError as e:
                print(f"Network error monitoring Netlify deployment {deployment_id}: {e}")
                if attempt == self.MAX_POLL_ATTEMPTS - 1:
                    return {"error": "monitoring_network_error", "details": str(e)}
                await asyncio.sleep(self.POLL_INTERVAL_SECONDS)
            except Exception as e:
                 print(f"Unexpected error monitoring Netlify deployment {deployment_id}: {e}")
                 if attempt == self.MAX_POLL_ATTEMPTS - 1:
                     return {"error": "monitoring_unexpected_error", "details": str(e)}
                 await asyncio.sleep(self.POLL_INTERVAL_SECONDS)

        print(f"Netlify deployment monitoring timed out for site {site_id}, deployment {deployment_id}.")
        return {"error": "timeout", "details": f"Deployment {deployment_id} did not reach 'ready' state after {self.MAX_POLL_ATTEMPTS * self.POLL_INTERVAL_SECONDS} seconds."}


    async def run_async(self, context: InvocationContext):
        """Executes the deployment workflow for the specified target (Vercel or Netlify)."""
        print("DeploymentAgent run_async started.")
        platform_deployment_id = None # Track deployment ID for potential failure reporting
        project_name = "Unknown Project" # Default project name for logging/errors
        brand_name_for_error = "Unknown (Input Error)" # Default brand name for errors

        # 1. Validate and parse input
        try:
            # Ensure context.input.data is a dictionary before passing to Pydantic
            if not isinstance(context.input.data, dict):
               raise TypeError(f"Expected context.input.data to be a dict, got {type(context.input.data)}")

            input_data = DeploymentAgentInputData(**context.input.data)
            brand_name = input_data.brand_name
            brand_name_for_error = brand_name # Update for subsequent error reporting
            deployment_target = input_data.deployment_target.lower() # Normalize to lowercase
            generated_code_dict = input_data.generated_code_dict

            # --- NEW: Check if code dictionary is provided ---
            if not generated_code_dict:
                raise ValueError("Input data is missing the required 'generated_code_dict'.")
            print(f"Received generated_code_dict with {len(generated_code_dict)} files.")
            # --- End NEW ---

            """ # TODO: Re-integrate these if needed from previous version
            # Determine Vercel project name
            project_name = input_data.vercel_project_name or self._generate_project_name(branding.brand_name)
            deployment_target = input_data.deployment_environment

            print(f"Starting Vercel deployment for brand: '{branding.brand_name}'")
            print(f"  Project Name: '{project_name}'")
            print(f"  Target Environment: '{deployment_target}'")
            """

        except (ValidationError, TypeError, ValueError) as e: # Added ValueError
            print(f"Input validation/processing failed: {e}")
            await context.emit(Event(
                type="deployment.failed",
                payload=DeploymentFailedPayload(
                    reason=f"Invalid or missing input data: {e}",
                    error_details={"validation_errors": e.errors() if isinstance(e, ValidationError) else str(e)},
                    # project_name_attempted=project_name, # Add if relevant
                    brand_name=brand_name_for_error # Might still be default here
                ).model_dump(exclude_none=True)
            ))
            return
        except Exception as e:
            print(f"Unexpected error processing input: {e}")
            import traceback
            traceback.print_exc()
            await context.emit(Event(
                type="deployment.failed",
                payload=DeploymentFailedPayload(
                    reason=f"Unexpected error processing input: {e}",
                    error_details={"exception": str(e), "trace": traceback.format_exc()},
                    # project_name_attempted=project_name,
                    brand_name=brand_name_for_error
                ).model_dump(exclude_none=True)
            ))
            return

        # --- Dispatch to Platform-Specific Logic ---
        try:
            if deployment_target == 'netlify':
                print(f"Starting Netlify deployment for brand: '{brand_name}'")
                if not self.netlify_auth_token:
                    raise ValueError("NETLIFY_AUTH_TOKEN is not configured.")
                # Pass generated_code_dict
                await self._deploy_to_netlify(context, input_data, generated_code_dict)

            elif deployment_target == 'vercel':
                print(f"Starting Vercel deployment for brand: '{brand_name}'")
                if not self.vercel_api_token:
                    raise ValueError("VERCEL_API_TOKEN is not configured.")
                # TODO: Determine Vercel project name and target environment from input_data if needed
                vercel_project_name = self._generate_vercel_project_name(brand_name) # Example
                vercel_target_env = "production" # Example, get from input if available
                # Pass generated_code_dict
                await self._deploy_to_vercel(context, input_data, generated_code_dict, vercel_project_name, vercel_target_env)

            else:
                raise ValueError(f"Unsupported deployment_target: '{deployment_target}'. Must be 'vercel' or 'netlify'.")

        except Exception as e:
            # Catch errors from platform-specific logic or credential checks
            print(f"Deployment failed for target '{deployment_target}': {e}")
            import traceback
            traceback.print_exc()
            await context.emit(Event(
                type="deployment.failed",
                payload=DeploymentFailedPayload(
                    brand_name=brand_name_for_error,
                    platform=deployment_target,
                    reason=f"Error during {deployment_target} deployment: {e}",
                    error_details={"exception": str(e), "trace": traceback.format_exc()},
                    # Add platform specific IDs if available at this stage
                ).model_dump(exclude_none=True)
            ))
        finally:
            # Close httpx clients
            if hasattr(self, 'vercel_client') and self.vercel_client and not self.vercel_client.is_closed:
                await self.vercel_client.aclose()
                print("Closed Vercel httpx client.")
            if hasattr(self, 'netlify_client') and self.netlify_client and not self.netlify_client.is_closed:
                await self.netlify_client.aclose()
                print("Closed Netlify httpx client.")

        print("DeploymentAgent run_async finished.")

    # --- Netlify Deployment Logic (Updated) ---
    async def _deploy_to_netlify(self, context: InvocationContext, input_data: DeploymentAgentInputData, generated_code_dict: Dict[str, str]):
        """Handles the entire Netlify deployment process using provided code."""
        print("Executing Netlify deployment...")
        brand_name = input_data.brand_name
        temp_dir_obj = None
        site_id = self.netlify_site_id # Use provided site ID if available
        netlify_deployment_id = None

        try:
            # 1. Prepare files from dict and zip them
            temp_dir_obj = tempfile.TemporaryDirectory()
            temp_dir = Path(temp_dir_obj.name)
            # Generate a project name suitable for the zip filename etc.
            netlify_project_name = self._generate_netlify_site_name(brand_name) # Reuse site name logic for consistency
            # Use the new preparation method
            zip_path = await self._prepare_zip_from_dict(temp_dir, netlify_project_name, generated_code_dict)

            # 2. Determine Site ID (Create if necessary)
            if not site_id:
                print("NETLIFY_SITE_ID not provided, attempting to create a new site...")
                site_id = await self._create_netlify_site(brand_name)
                # Store the created site_id for potential error reporting
                # Note: This assignment won't persist across agent runs, but helps within this run.
                # Consider storing created site IDs externally if persistence is needed.
            else:
                print(f"Using provided NETLIFY_SITE_ID: {site_id}")


            # 3. Upload Zip and Trigger Deployment
            deploy_result = await self._upload_and_deploy_netlify(site_id, zip_path)
            netlify_deployment_id = deploy_result.get("id")
            if not netlify_deployment_id:
                 raise ValueError("Failed to get deployment ID from Netlify after upload.")

            # 4. Monitor Deployment (Optional but recommended)
            # Check if deploy_result already indicates readiness (common for simple static deploys)
            if deploy_result.get("state") == "ready":
                print("Netlify deployment reported as 'ready' immediately after upload.")
                monitor_result = deploy_result
            else:
                monitor_result = await self._monitor_netlify_deployment(site_id, netlify_deployment_id)

            if not monitor_result or monitor_result.get("error"):
                reason = f"Netlify deployment failed: {monitor_result.get('error', 'Unknown monitoring error')}"
                print(f"Deployment failed: {reason}")
                await context.emit(Event(
                    type="deployment.failed",
                    payload=DeploymentFailedPayload(
                        brand_name=brand_name,
                        platform='netlify',
                        reason=reason,
                        error_details=monitor_result.get("details"),
                        netlify_site_id=site_id,
                        netlify_deployment_id=netlify_deployment_id
                    ).model_dump(exclude_none=True)
                ))
                return

            # 5. Emit Success Event
            # Prefer ssl_url or deploy_ssl_url if available
            deployment_url = monitor_result.get("ssl_url") or monitor_result.get("deploy_ssl_url") or monitor_result.get("url")
            if not deployment_url:
                # Fallback to default site URL if deploy URL isn't immediately available
                site_info_url = f"/sites/{site_id}"
                try:
                    site_info_resp = await self.netlify_client.get(site_info_url)
                    site_info_resp.raise_for_status()
                    site_info = site_info_resp.json()
                    deployment_url = site_info.get("ssl_url") or site_info.get("url")
                    if not deployment_url:
                        raise ValueError("Could not determine deployment URL from Netlify site info.")
                    print(f"Warning: Deployment URL not in monitor result, using site URL: {deployment_url}")
                except Exception as site_info_err:
                    print(f"Error fetching site info to get URL: {site_info_err}")
                    raise ValueError("Could not determine deployment URL from Netlify response or site info.") from site_info_err


            features_deployed = [f.get("feature_name", f"Unnamed Feature {i+1}") for i, f in enumerate(input_data.key_features)]

            success_payload = DeploymentResultPayload(
                deployment_url=deployment_url,
                brand_name=brand_name,
                platform='netlify',
                status=monitor_result.get("state", "READY").upper(), # Use Netlify state or default
                features_deployed=features_deployed,
                deployment_details=NetlifyDeploymentDetails(
                    netlify_deployment_id=netlify_deployment_id,
                    site_id=site_id,
                    # deployment_time_utc handled by default factory
                )
            )

            await context.emit(Event(
                type="deployment.succeeded",
                payload=success_payload.model_dump(exclude_none=True)
            ))
            print(f"Netlify deployment finished successfully for site '{site_id}'. Status: {success_payload.status}, URL: {deployment_url}")

        # Error handling is now done in the main run_async try/except block
        # except ValueError as e: ... # Handled in run_async
        finally:
            if temp_dir_obj:
                try:
                    temp_dir_obj.cleanup()
                    print(f"Cleaned up Netlify temp directory: {temp_dir_obj.name}")
                except Exception as e:
                    print(f"Warning: Failed to clean up Netlify temporary directory {temp_dir_obj.name}: {e}")

    # --- Vercel Deployment Logic (Refactored) ---
    async def _deploy_to_vercel(self, context: InvocationContext, input_data: DeploymentAgentInputData, generated_code_dict: Dict[str, str], project_name: str, deployment_target_env: str):
        """Handles the entire Vercel deployment process using provided code."""
        print(f"Executing Vercel deployment for project '{project_name}' to '{deployment_target_env}'...")
        brand_name = input_data.brand_name
        vercel_deployment_id = None
        temp_dir_obj = None
        try:
            # 3. Prepare Files in a Temporary Directory from Dict
            temp_dir_obj = tempfile.TemporaryDirectory()
            temp_dir = Path(temp_dir_obj.name)
            print(f"Preparing deployment files from dict in temporary directory: {temp_dir}")
            # Use the new preparation method
            files_data_map = await self._prepare_files_from_dict(temp_dir, generated_code_dict)
            if not files_data_map:
                 raise ValueError("File preparation step from dict returned no files.")
            files_list = list(files_data_map.values()) # Vercel API needs list of file info dicts

            # 4. Upload Files to Vercel
            print(f"Uploading {len(files_list)} files to Vercel for project '{project_name}'...")
            upload_tasks = [self._upload_file_to_vercel(file_info) for file_info in files_list]
            upload_results = await asyncio.gather(*upload_tasks)

            if not all(upload_results):
                failed_files = [files_list[i]["file"] for i, success in enumerate(upload_results) if not success]
                reason = f"File upload failed for: {', '.join(failed_files)}"
                print(f"Deployment failed: {reason}")
                await context.emit(Event(
                    type="deployment.failed",
                    payload=DeploymentFailedPayload( # Use the updated model
                        brand_name=brand_name,
                        platform='vercel',
                        reason=reason,
                        error_details={"failed_files": failed_files}
                        # project_name_attempted=project_name # Removed, project name is part of Vercel details
                    ).model_dump(exclude_none=True)
                ))
                return # Exit early

            print(f"All files uploaded successfully for project '{project_name}'.")

            # 5. Trigger Deployment
            print(f"Triggering Vercel deployment for project: {project_name} to {deployment_target_env}")
            trigger_result = await self._trigger_vercel_deployment(project_name, files_list, deployment_target_env)

            if not trigger_result or trigger_result.get("error"):
                reason = f"Failed to trigger Vercel deployment: {trigger_result.get('error', 'Unknown trigger error')}"
                print(f"Deployment failed: {reason}")
                await context.emit(Event(
                    type="deployment.failed",
                    payload=DeploymentFailedPayload( # Use the updated model
                        brand_name=brand_name,
                        platform='vercel',
                        reason=reason,
                        error_details=trigger_result.get("details")
                        # project_name_attempted=project_name
                    ).model_dump(exclude_none=True)
                ))
                return

            vercel_deployment_id = trigger_result.get("id") # Corrected variable name
            if not vercel_deployment_id:
                 reason = "Vercel API did not return a deployment ID after trigger."
                 print(f"Deployment failed: {reason}")
                 await context.emit(Event(
                    type="deployment.failed",
                    payload=DeploymentFailedPayload( # Use the updated model
                        brand_name=brand_name,
                        platform='vercel',
                        reason=reason,
                        error_details=trigger_result
                        # project_name_attempted=project_name
                    ).model_dump(exclude_none=True)
                ))
                 return

            # 6. Monitor Deployment Status
            # Pass project_name for better logging
            monitor_result = await self._monitor_vercel_deployment(vercel_deployment_id, project_name)

            if not monitor_result or monitor_result.get("error"):
                reason = f"Deployment failed during monitoring: {monitor_result.get('error', 'Unknown monitoring error')}"
                print(f"Deployment failed: {reason}")
                await context.emit(Event(
                    type="deployment.failed",
                    payload=DeploymentFailedPayload( # Use the updated model
                        brand_name=brand_name,
                        platform='vercel',
                        reason=reason,
                        error_details=monitor_result.get("details"),
                        vercel_deployment_id=vercel_deployment_id, # Corrected variable name
                        # project_name_attempted=project_name
                    ).model_dump(exclude_none=True)
                ))
                return

            # 7. Deployment Succeeded - Construct Payload and Emit Event
            deployment_url = f"https://{monitor_result.get('url')}" # Vercel provides the final URL
            # Extract feature names from the improved spec
            features_deployed = [f.get("feature_name", f"Unnamed Feature {i+1}") for i, f in enumerate(input_data.key_features)]

            success_payload = DeploymentResultPayload(
                deployment_url=deployment_url,
                brand_name=brand_name,
                platform='vercel',
                features_deployed=features_deployed,
                deployment_details=VercelDeploymentDetails( # Assign to the Union field
                    vercel_deployment_id=vercel_deployment_id, # Corrected variable name
                    project_name=project_name, # Use the actual project name used
                    region=monitor_result.get("regions", ["default"])[0], # Get region if available
                    # environment=monitor_result.get("target", deployment_target_env) # Reflect actual env - Removed, not in VercelDeploymentDetails
                    # deployment_time_utc is handled by default_factory
                )
            )

            await context.emit(Event(
                type="deployment.succeeded",
                payload=success_payload.model_dump(exclude_none=True)
            ))
            print(f"Vercel deployment finished successfully for project '{project_name}'. Status: READY, URL: {deployment_url}")

        # Error handling is now done in the main run_async try/except block
        # except httpx.HTTPStatusError as e: ...
        # except httpx.RequestError as e: ...
        # except Exception as e: ...
        finally:
            # 8. Clean up temporary directory
            if temp_dir_obj:
                try:
                    temp_dir_obj.cleanup()
                    print(f"Cleaned up temporary directory: {temp_dir}")
                except Exception as e:
                    print(f"Warning: Failed to clean up temporary directory {temp_dir}: {e}")
            # Closing the client is handled in run_async's finally block



# --- Example Usage (ADK context simulation - needs update) ---
async def run_agent_locally():
    print("Running DeploymentAgent example locally (simulating ADK context)...")

    # Ensure API tokens are set for local testing
    print("NOTE: Ensure relevant API tokens (VERCEL_API_TOKEN/NETLIFY_AUTH_TOKEN) are set in .env for local testing.")
    # Example check (optional):
    # if not os.environ.get("VERCEL_API_TOKEN") and not os.environ.get("NETLIFY_AUTH_TOKEN"):
    #     print("\nERROR: Set at least one API token (VERCEL_API_TOKEN or NETLIFY_AUTH_TOKEN) in .env to run.")
    #     return

    agent = DeploymentAgent() # Re-initialize agent here to ensure client is fresh

    # Example Input Data (matching DeploymentAgentInputData)
    test_brand_name = f"ADK Dynamic Test {random.randint(1000, 9999)}"
    test_input_data = {
        "brand_name": test_brand_name,
        "product_concept": "A dynamically generated test deployment from ADK Agent local run.",
        "key_features": [
            {"feature_name": "Dynamic HTML", "desc": "Index page generated with brand name."},
            {"feature_name": "Basic CSS", "desc": "Simple styling."},
        ],
        # Optional config examples:
        # "vercel_project_name": "my-specific-test-project", # Override generated name
        # "deployment_environment": "preview" # Vercel specific, handle if needed
        "deployment_target": "vercel" # Change to "netlify" to test Netlify path (once implemented)
    }

    # Simulate ADK InvocationContext and Input Event
    class MockInputEvent:
        def __init__(self, data):
            self.data = data # Store the provided data

    class MockInvocationContext:
        def __init__(self, input_data):
            self.input = MockInputEvent(input_data) # Pass data during init
            self.emitted_events = []

        async def emit(self, event: Event):
            print(f"\n--- Agent Emitted Event ---")
            print(f"Type: {event.type}")
            # Pretty print payload
            try:
                # Use exclude_none=True for cleaner output if models were dumped with it
                payload_str = json.dumps(event.payload, indent=2)
            except TypeError: # Handle non-serializable types if any sneak in
                payload_str = str(event.payload)
            print(f"Payload:\n{payload_str}")
            print("--------------------------")
            self.emitted_events.append(event)

    mock_context = MockInvocationContext(test_input_data) # Pass test data here

    try:
        await agent.run_async(mock_context)
        print("\nAgent execution finished locally.")
        # You can inspect mock_context.emitted_events here if needed
    except Exception as e:
        print(f"\nAgent execution failed locally: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Ensure client is closed even if run_async fails before its finally block
        if hasattr(agent, 'vercel_client') and agent.vercel_client and not agent.vercel_client.is_closed:
             await agent.vercel_client.aclose()
             print("Ensured Vercel httpx client closed after local run.")
        if hasattr(agent, 'netlify_client') and agent.netlify_client and not agent.netlify_client.is_closed:
             await agent.netlify_client.aclose()
             print("Ensured Netlify httpx client closed after local run.")


# Example of how to run this agent as a standalone A2A server
if __name__ == "__main__":
    try:
        from dotenv import load_dotenv
        if load_dotenv():
            logger.info("Loaded .env file for local run.")
        else:
            logger.info("No .env file found or it was empty.")
    except ImportError:
        logger.info("dotenv library not found, skipping .env load for local run.")

    # Create the agent
    agent = DeploymentAgent()

    # Run the A2A server
    agent.run_server(host="0.0.0.0", port=agent.port or 8008)