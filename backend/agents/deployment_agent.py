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
import argparse # Added for command-line args
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

import httpx
import uvicorn # Added for server
from fastapi import FastAPI, HTTPException, Body # Added for server
from pydantic import BaseModel, Field, HttpUrl, ValidationError

# Assuming ADK is installed and configured
from google.adk.agents import Agent
from google.adk.runtime import InvocationContext
from google.adk.runtime.events import Event

# Configure logging
# Use logfire if configured globally, otherwise standard logging
try:
    import logfire
    # Assuming logfire is configured elsewhere
    logger = logfire
except ImportError:
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO"))


# --- Data Models (Input/Output) ---

class DeploymentAgentInputData(BaseModel):
    """Expected data structure for the /invoke endpoint request body."""
    brand_name: str = Field(description="The final brand name for the product.")
    product_concept: str = Field(description="Description of the product being deployed.")
    key_features: List[Dict[str, Any]] = Field(description="List of features included in the deployment.")
    deployment_target: str = Field(default='vercel', description="Deployment target ('vercel' or 'netlify').")
    generated_code_dict: Dict[str, str] = Field(description="Dictionary mapping file paths to code content, provided by CodeGenerationAgent.")
    # Optional: Add vercel_project_name, deployment_environment etc. if needed

class VercelDeploymentDetails(BaseModel):
    vercel_deployment_id: str
    project_name: str
    deployment_time_utc: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())
    region: str = "default"

class NetlifyDeploymentDetails(BaseModel):
    netlify_deployment_id: str
    site_id: str
    deployment_time_utc: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())

class DeploymentResultPayload(BaseModel):
    """Payload for the successful deployment event and /invoke response."""
    deployment_url: HttpUrl
    status: str = "READY"
    brand_name: str
    features_deployed: List[str]
    platform: str
    deployment_details: Union[VercelDeploymentDetails, NetlifyDeploymentDetails]

class DeploymentFailedPayload(BaseModel):
    """Payload for the failed deployment event and /invoke error response."""
    brand_name: str
    platform: str
    reason: str
    error_details: Optional[Dict[str, Any]] = None
    vercel_deployment_id: Optional[str] = None
    netlify_site_id: Optional[str] = None
    netlify_deployment_id: Optional[str] = None


# --- Agent Class ---

class DeploymentAgent(Agent):
    """
    ADK Agent responsible for Stage 4: Deployment.
    Deploys generated code to Vercel or Netlify.
    Requires VERCEL_API_TOKEN or NETLIFY_AUTH_TOKEN environment variables.
    """
    VERCEL_API_BASE_URL = "https://api.vercel.com"
    NETLIFY_API_BASE_URL = "https://api.netlify.com/api/v1"
    POLL_INTERVAL_SECONDS = 5
    MAX_POLL_ATTEMPTS = 24 # 2 minutes total

    def __init__(self, agent_id: str = "deployment-agent"):
        """Initialize the Deployment Agent."""
        super().__init__(agent_id=agent_id) # Pass agent_id to parent
        logger.info(f"DeploymentAgent ({self.agent_id}) initialized.")
        self.vercel_api_token = os.environ.get("VERCEL_API_TOKEN")
        self.vercel_team_id = os.environ.get("VERCEL_TEAM_ID")
        self.netlify_auth_token = os.environ.get("NETLIFY_AUTH_TOKEN")
        self.netlify_site_id = os.environ.get("NETLIFY_SITE_ID")

        # Initialize clients here
        self.vercel_client = None
        if self.vercel_api_token:
            self.vercel_client = httpx.AsyncClient(
                base_url=self.VERCEL_API_BASE_URL,
                headers={"Authorization": f"Bearer {self.vercel_api_token}", "Content-Type": "application/json"},
                timeout=30.0
            )
            logger.info("Vercel client configured.")
        else:
            logger.warning("VERCEL_API_TOKEN not set. Vercel deployment will fail.")

        self.netlify_client = None
        if self.netlify_auth_token:
            self.netlify_client = httpx.AsyncClient(
                base_url=self.NETLIFY_API_BASE_URL,
                headers={"Authorization": f"Bearer {self.netlify_auth_token}"},
                timeout=60.0
            )
            logger.info("Netlify client configured.")
        else:
            logger.warning("NETLIFY_AUTH_TOKEN not set. Netlify deployment will fail.")

    # --- Helper Methods ---
    def _generate_vercel_project_name(self, brand_name: str) -> str:
        """Generates a Vercel-compatible project name."""
        sanitized = ''.join(c for c in brand_name.lower() if c.isalnum() or c == '-')
        sanitized = sanitized.replace(' ', '-')
        sanitized = sanitized.strip('-')[:90]
        if not sanitized:
            sanitized = f"deployment-{random.randint(1000, 9999)}"
        return sanitized

    def _generate_netlify_site_name(self, brand_name: str) -> str:
        """Generates a potential Netlify site name (subdomain)."""
        sanitized = ''.join(c for c in brand_name.lower() if c.isalnum())
        sanitized = sanitized.replace(' ', '')
        sanitized = sanitized.strip('-')[:60]
        if not sanitized:
            sanitized = f"adk-site-{random.randint(1000, 9999)}"
        return sanitized

    async def _prepare_files_from_dict(self, temp_dir: Path, generated_code_dict: Dict[str, str]) -> Dict[str, Dict[str, Any]]:
        """Creates files from the provided dictionary and returns Vercel file structure."""
        logger.info(f"Preparing files from generated_code_dict in {temp_dir}")
        file_data = {}
        try:
            for relative_path_str, code_content in generated_code_dict.items():
                if relative_path_str.startswith('/'): relative_path_str = relative_path_str[1:]
                absolute_path = temp_dir / relative_path_str
                logger.debug(f"  Processing: {relative_path_str} -> {absolute_path}")
                absolute_path.parent.mkdir(parents=True, exist_ok=True)
                content_bytes = code_content.encode('utf-8')
                absolute_path.write_bytes(content_bytes)
                digest = hashlib.sha1(content_bytes).hexdigest()
                size = len(content_bytes)
                file_data[relative_path_str] = {"file": relative_path_str, "sha": digest, "size": size, "path": absolute_path}
                logger.debug(f"    Prepared: {relative_path_str} (Size: {size}, SHA: {digest[:7]}...)")

            if "vercel.json" not in file_data:
                 logger.info("  Adding default vercel.json as it was not provided.")
                 vercel_json_content = """{"framework": "vite"}"""
                 vercel_json_path = temp_dir / "vercel.json"
                 content_bytes = vercel_json_content.encode('utf-8')
                 vercel_json_path.write_bytes(content_bytes)
                 digest = hashlib.sha1(content_bytes).hexdigest()
                 size = len(content_bytes)
                 file_data["vercel.json"] = {"file": "vercel.json", "sha": digest, "size": size, "path": vercel_json_path}
                 logger.debug(f"    Prepared: vercel.json (Size: {size}, SHA: {digest[:7]}...)")
            return file_data
        except OSError as e:
            logger.error(f"Error creating deployment files/directories from dict: {e}", exc_info=True)
            raise ValueError(f"Failed to prepare deployment files from dict: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error preparing deployment files from dict: {e}", exc_info=True)
            raise ValueError(f"Unexpected error preparing deployment files from dict: {e}") from e

    async def _upload_file_to_vercel(self, file_info: Dict[str, Any]):
        """Uploads a single file to Vercel using the dedicated client."""
        if not self.vercel_client: raise RuntimeError("Vercel client not initialized.")
        upload_url = f"{self.VERCEL_API_BASE_URL}/v2/files" # Use base URL from client implicitly? No, keep explicit.
        headers = {
            "Authorization": f"Bearer {self.vercel_api_token}", # Re-add auth header
            "Content-Length": str(file_info["size"]),
            "x-vercel-digest": file_info["sha"],
        }
        if self.vercel_team_id: headers["TeamId"] = self.vercel_team_id

        try:
            file_bytes = file_info["path"].read_bytes()
            response = await self.vercel_client.post(upload_url, headers=headers, content=file_bytes) # Use instance client
            if response.status_code == 200:
                logger.debug(f"Successfully uploaded file: {file_info['file']}")
                return True
            else:
                error_content = response.text
                logger.error(f"Error uploading file {file_info['file']}: {response.status_code} - {error_content}")
                return False
        except httpx.RequestError as e:
            logger.error(f"HTTP error uploading file {file_info['file']}: {e}", exc_info=True)
            return False
        except Exception as e:
            logger.error(f"Unexpected error uploading file {file_info['file']}: {e}", exc_info=True)
            return False

    async def _prepare_zip_from_dict(self, temp_dir: Path, project_name: str, generated_code_dict: Dict[str, str]) -> Path:
        """Creates files from the provided dictionary within a site_root and zips it for Netlify."""
        logger.info(f"Preparing Netlify source zip from generated_code_dict for '{project_name}' in {temp_dir}")
        site_root_dir = temp_dir / "site_root"
        try:
            site_root_dir.mkdir(parents=True, exist_ok=True)
            for relative_path_str, code_content in generated_code_dict.items():
                if relative_path_str.startswith('/'): relative_path_str = relative_path_str[1:]
                absolute_path = site_root_dir / relative_path_str
                logger.debug(f"  Processing for zip: {relative_path_str} -> {absolute_path}")
                absolute_path.parent.mkdir(parents=True, exist_ok=True)
                absolute_path.write_text(code_content, encoding='utf-8')

            zip_filename = f"{project_name}-netlify-src.zip"
            zip_path = temp_dir / zip_filename
            logger.info(f"Creating Netlify deployment source zip: {zip_path}")
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in site_root_dir.rglob('*'):
                    if file_path.is_file():
                        relative_path = file_path.relative_to(site_root_dir)
                        zipf.write(file_path, relative_path)
                        logger.debug(f"    Adding to zip: {relative_path}")
            logger.info(f"  Created deployment source zip: {zip_path} (Size: {zip_path.stat().st_size} bytes)")
            logger.info("  NOTE: Netlify site must be configured with appropriate build command and publish directory if build is needed.")
            return zip_path
        except OSError as e:
            logger.error(f"Error creating Netlify zip files/directories from dict: {e}", exc_info=True)
            raise ValueError(f"Failed to prepare Netlify zip from dict: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error preparing Netlify zip from dict: {e}", exc_info=True)
            raise ValueError(f"Unexpected error preparing Netlify zip from dict: {e}") from e

    async def _trigger_vercel_deployment(self, project_name: str, files_data: List[Dict[str, Any]], target_environment: str) -> Optional[Dict[str, Any]]:
        """Triggers the Vercel deployment with uploaded file details and target environment."""
        if not self.vercel_client: raise RuntimeError("Vercel client not initialized.")
        deployment_url = "/v13/deployments" # Relative to base_url
        params = {}
        if self.vercel_team_id: params["teamId"] = self.vercel_team_id
        payload = {
            "name": project_name,
            "files": [{"file": f_data["file"], "sha": f_data["sha"], "size": f_data["size"]} for f_data in files_data],
            "projectSettings": {"framework": "vite"},
            "target": target_environment,
            "project": project_name
        }
        try:
            response = await self.vercel_client.post(deployment_url, params=params, json=payload)
            response.raise_for_status()
            deployment_data = response.json()
            logger.info(f"Successfully initiated Vercel deployment: ID {deployment_data.get('id')} for project '{project_name}' to target '{target_environment}'")
            return deployment_data
        except httpx.HTTPStatusError as e:
            error_details = {"raw_content": e.response.text}
            try: error_details = e.response.json()
            except json.JSONDecodeError: pass
            logger.error(f"HTTP error triggering Vercel deployment for project '{project_name}': {e.response.status_code} - {error_details}", exc_info=True)
            return {"error": "trigger_failed", "status_code": e.response.status_code, "details": error_details}
        except httpx.RequestError as e:
            logger.error(f"Network error triggering Vercel deployment for project '{project_name}': {e}", exc_info=True)
            return {"error": "network_error", "details": str(e)}
        except Exception as e:
            logger.error(f"Unexpected error triggering Vercel deployment for project '{project_name}': {e}", exc_info=True)
            return {"error": "unexpected", "details": str(e)}

    async def _monitor_vercel_deployment(self, deployment_id: str, project_name: str) -> Optional[Dict[str, Any]]:
        """Monitors a Vercel deployment until it succeeds or fails."""
        if not self.vercel_client: raise RuntimeError("Vercel client not initialized.")
        status_url = f"/v13/deployments/{deployment_id}" # Relative
        params = {}
        if self.vercel_team_id: params["teamId"] = self.vercel_team_id
        logger.info(f"Monitoring Vercel deployment {deployment_id} for project '{project_name}'...")
        for attempt in range(self.MAX_POLL_ATTEMPTS):
            try:
                await asyncio.sleep(self.POLL_INTERVAL_SECONDS) # Wait first
                response = await self.vercel_client.get(status_url, params=params)
                response.raise_for_status()
                status_data = response.json()
                state = status_data.get("readyState")
                logger.info(f"  Attempt {attempt + 1}/{self.MAX_POLL_ATTEMPTS}: Project '{project_name}', Deployment {deployment_id}, State = {state}")
                if state == "READY":
                    logger.info(f"Deployment successful for project '{project_name}'!")
                    return status_data
                elif state in ["ERROR", "CANCELED"]:
                    logger.error(f"Deployment failed or canceled for project '{project_name}'. State: {state}")
                    return {"error": "deployment_failed", "state": state, "details": status_data.get("error")}
                elif state not in ["BUILDING", "QUEUED", "INITIALIZING"]:
                    logger.warning(f"Unknown deployment state encountered for project '{project_name}': {state}")
            except httpx.HTTPStatusError as e:
                error_details = {"raw_content": e.response.text}
                try: error_details = e.response.json()
                except json.JSONDecodeError: pass
                logger.error(f"HTTP error monitoring deployment {deployment_id} for project '{project_name}': {e.response.status_code} - {error_details}", exc_info=True)
                if attempt == self.MAX_POLL_ATTEMPTS - 1: return {"error": "monitoring_http_error", "status_code": e.response.status_code, "details": error_details}
            except httpx.RequestError as e:
                logger.error(f"Network error monitoring deployment {deployment_id} for project '{project_name}': {e}", exc_info=True)
                if attempt == self.MAX_POLL_ATTEMPTS - 1: return {"error": "monitoring_network_error", "details": str(e)}
            except Exception as e:
                 logger.error(f"Unexpected error monitoring deployment {deployment_id} for project '{project_name}': {e}", exc_info=True)
                 if attempt == self.MAX_POLL_ATTEMPTS - 1: return {"error": "monitoring_unexpected_error", "details": str(e)}
        logger.error(f"Deployment monitoring timed out for project '{project_name}'.")
        return {"error": "timeout", "details": f"Deployment {deployment_id} did not reach READY state after {self.MAX_POLL_ATTEMPTS * self.POLL_INTERVAL_SECONDS} seconds."}

    async def _create_netlify_site(self, brand_name: str) -> str:
        """Creates a new site on Netlify and returns the site ID."""
        if not self.netlify_client: raise RuntimeError("Netlify client not initialized.")
        site_name = self._generate_netlify_site_name(brand_name)
        create_url = "/sites"
        payload = {"name": site_name}
        logger.info(f"Attempting to create Netlify site with suggested name: {site_name}")
        try:
            response = await self.netlify_client.post(create_url, json=payload)
            response.raise_for_status()
            site_data = response.json()
            site_id = site_data.get("site_id")
            if not site_id: raise ValueError("Netlify API did not return a site_id after creation.")
            logger.info(f"Successfully created Netlify site: ID {site_id}, Name {site_data.get('name')}")
            return site_id
        except httpx.HTTPStatusError as e:
            error_details = {"raw_content": e.response.text}
            try:
                error_details = e.response.json()
                if e.response.status_code == 422 and "name already exists" in str(error_details).lower():
                     logger.warning(f"Netlify site name '{site_name}' likely taken. Consider providing NETLIFY_SITE_ID or using a more unique brand name.")
            except json.JSONDecodeError: pass
            logger.error(f"HTTP error creating Netlify site: {e.response.status_code} - {error_details}", exc_info=True)
            raise ValueError(f"Failed to create Netlify site: {error_details}") from e
        except httpx.RequestError as e:
            logger.error(f"Network error creating Netlify site: {e}", exc_info=True)
            raise ValueError(f"Network error creating Netlify site: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error creating Netlify site: {e}", exc_info=True)
            raise ValueError(f"Unexpected error creating Netlify site: {e}") from e

    async def _upload_and_deploy_netlify(self, site_id: str, zip_path: Path) -> Dict[str, Any]:
        """Uploads the site zip and triggers a deployment on Netlify."""
        if not self.netlify_client: raise RuntimeError("Netlify client not initialized.")
        deploy_url = f"/sites/{site_id}/deploys"
        logger.info(f"Uploading deployment zip '{zip_path.name}' to Netlify site {site_id}...")
        headers = {"Authorization": f"Bearer {self.netlify_auth_token}", "Content-Type": "application/zip"}
        try:
            async with zip_path.open("rb") as f: zip_content = await f.read()
            response = await self.netlify_client.post(deploy_url, headers=headers, content=zip_content)
            response.raise_for_status()
            deploy_data = response.json()
            deployment_id = deploy_data.get("id")
            required_files = deploy_data.get("required", [])
            if not deployment_id: raise ValueError("Netlify API did not return a deployment ID after upload.")
            if required_files: logger.warning(f"Netlify requires additional files: {required_files}. Deployment might be incomplete.")
            logger.info(f"Successfully initiated Netlify deployment: ID {deployment_id} for site {site_id}")
            return deploy_data
        except httpx.HTTPStatusError as e:
            error_details = {"raw_content": e.response.text}
            try: error_details = e.response.json()
            except json.JSONDecodeError: pass
            logger.error(f"HTTP error deploying to Netlify site {site_id}: {e.response.status_code} - {error_details}", exc_info=True)
            raise ValueError(f"Failed to deploy to Netlify: {error_details}") from e
        except httpx.RequestError as e:
            logger.error(f"Network error deploying to Netlify site {site_id}: {e}", exc_info=True)
            raise ValueError(f"Network error deploying to Netlify: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error deploying to Netlify site {site_id}: {e}", exc_info=True)
            raise ValueError(f"Unexpected error deploying to Netlify: {e}") from e

    async def _monitor_netlify_deployment(self, site_id: str, deployment_id: str) -> Dict[str, Any]:
        """Monitors a Netlify deployment until it succeeds or fails."""
        if not self.netlify_client: raise RuntimeError("Netlify client not initialized.")
        status_url = f"/sites/{site_id}/deploys/{deployment_id}"
        logger.info(f"Monitoring Netlify deployment {deployment_id} for site {site_id}...")
        for attempt in range(self.MAX_POLL_ATTEMPTS):
            try:
                await asyncio.sleep(self.POLL_INTERVAL_SECONDS) # Wait first
                response = await self.netlify_client.get(status_url)
                response.raise_for_status()
                status_data = response.json()
                state = status_data.get("state")
                logger.info(f"  Attempt {attempt + 1}/{self.MAX_POLL_ATTEMPTS}: Site {site_id}, Deployment {deployment_id}, State = {state}")
                if state == "ready":
                    logger.info(f"Netlify deployment successful for site {site_id}!")
                    return status_data
                elif state in ["error", "failed"]:
                    error_message = status_data.get("error_message", "Unknown error")
                    logger.error(f"Netlify deployment failed for site {site_id}. State: {state}, Reason: {error_message}")
                    return {"error": "deployment_failed", "state": state, "details": error_message}
                elif state not in ["building", "uploading", "processing", "new"]:
                    logger.warning(f"Unknown Netlify deployment state encountered for site {site_id}: {state}")
            except httpx.HTTPStatusError as e:
                error_details = {"raw_content": e.response.text}
                try: error_details = e.response.json()
                except json.JSONDecodeError: pass
                logger.error(f"HTTP error monitoring Netlify deployment {deployment_id}: {e.response.status_code} - {error_details}", exc_info=True)
                if attempt == self.MAX_POLL_ATTEMPTS - 1: return {"error": "monitoring_http_error", "status_code": e.response.status_code, "details": error_details}
            except httpx.RequestError as e:
                logger.error(f"Network error monitoring Netlify deployment {deployment_id}: {e}", exc_info=True)
                if attempt == self.MAX_POLL_ATTEMPTS - 1: return {"error": "monitoring_network_error", "details": str(e)}
            except Exception as e:
                 logger.error(f"Unexpected error monitoring Netlify deployment {deployment_id}: {e}", exc_info=True)
                 if attempt == self.MAX_POLL_ATTEMPTS - 1: return {"error": "monitoring_unexpected_error", "details": str(e)}
        logger.error(f"Netlify deployment monitoring timed out for site {site_id}, deployment {deployment_id}.")
        return {"error": "timeout", "details": f"Deployment {deployment_id} did not reach 'ready' state after {self.MAX_POLL_ATTEMPTS * self.POLL_INTERVAL_SECONDS} seconds."}

    # --- Main Agent Logic ---
    async def run_async(self, context: InvocationContext) -> Event:
        """Executes the deployment workflow based on context data."""
        logger.info(f"DeploymentAgent ({self.agent_id}) run_async started. Invocation ID: {context.invocation_id}")
        brand_name_for_error = "Unknown (Input Error)"
        deployment_target = "unknown"
        temp_dir_obj = None # Define here for finally block

        try:
            # 1. Validate and parse input from context.data
            if not isinstance(context.data, dict):
               raise TypeError(f"Expected context.data to be a dict, got {type(context.data)}")
            input_data = DeploymentAgentInputData(**context.data)
            brand_name_for_error = input_data.brand_name
            deployment_target = input_data.deployment_target.lower()
            generated_code_dict = input_data.generated_code_dict
            if not generated_code_dict:
                raise ValueError("Input data is missing the required 'generated_code_dict'.")
            logger.info(f"Input validated for brand '{brand_name_for_error}', target '{deployment_target}'. Code dict has {len(generated_code_dict)} files.")

            # Create temp dir for file operations
            temp_dir_obj = tempfile.TemporaryDirectory()
            temp_dir = Path(temp_dir_obj.name)

            # 2. Dispatch to Platform-Specific Logic
            # The helper methods will now emit the final event
            if deployment_target == 'netlify':
                logger.info(f"Starting Netlify deployment process...")
                if not self.netlify_client: raise ValueError("Netlify client not initialized (NETLIFY_AUTH_TOKEN missing?).")
                await self._deploy_to_netlify(context, input_data, generated_code_dict, temp_dir)

            elif deployment_target == 'vercel':
                logger.info(f"Starting Vercel deployment process...")
                if not self.vercel_client: raise ValueError("Vercel client not initialized (VERCEL_API_TOKEN missing?).")
                vercel_project_name = self._generate_vercel_project_name(input_data.brand_name)
                vercel_target_env = "production" # Default, adjust if needed from input
                await self._deploy_to_vercel(context, input_data, generated_code_dict, vercel_project_name, vercel_target_env, temp_dir)

            else:
                raise ValueError(f"Unsupported deployment_target: '{deployment_target}'. Must be 'vercel' or 'netlify'.")

            # 3. If we reach here, the helper should have emitted the event.
            # Return a simple confirmation event, or potentially the last emitted event if needed.
            logger.info(f"Deployment process completed for target '{deployment_target}'. Final event emitted by helper.")
            # Returning a generic result event as run_async needs to return an Event
            return context.create_event(event_type="adk.agent.result", data={"status": "completed", "target": deployment_target}, metadata={"status": "success"})


        except (ValidationError, TypeError, ValueError) as e:
            logger.error(f"Deployment failed due to input/config error: {e}", exc_info=True)
            error_payload = DeploymentFailedPayload(
                brand_name=brand_name_for_error, platform=deployment_target,
                reason=f"Input/Configuration Error: {e}",
                error_details={"validation_errors": e.errors() if isinstance(e, ValidationError) else str(e)}
            )
            # Emit the error event *before* returning it
            error_event = context.create_event(event_type="deployment.failed", data=error_payload.model_dump(exclude_none=True), metadata={"status": "error"})
            await context.emit(error_event) # Ensure the event is emitted via context if possible
            return error_event # Return the created error event
        except Exception as e:
            logger.error(f"Unexpected error during deployment: {e}", exc_info=True)
            error_payload = DeploymentFailedPayload(
                brand_name=brand_name_for_error, platform=deployment_target,
                reason=f"Unexpected Error: {e}", error_details={"exception": str(e)}
            )
            error_event = context.create_event(event_type="deployment.failed", data=error_payload.model_dump(exclude_none=True), metadata={"status": "error"})
            await context.emit(error_event)
            return error_event
        finally:
            # Cleanup temp dir
            if temp_dir_obj:
                try:
                    temp_dir_obj.cleanup()
                    logger.info(f"Cleaned up temporary directory: {temp_dir_obj.name}")
                except Exception as e:
                    logger.warning(f"Failed to clean up temporary directory {temp_dir_obj.name}: {e}")
            # Clients are long-lived with the agent instance in this server setup
            logger.info(f"DeploymentAgent ({self.agent_id}) run_async finished.")


    # --- Refactored Platform Deployment Methods ---
    async def _deploy_to_netlify(self, context: InvocationContext, input_data: DeploymentAgentInputData, generated_code_dict: Dict[str, str], temp_dir: Path):
        """Handles the Netlify deployment process within run_async and emits final event."""
        brand_name = input_data.brand_name
        site_id = self.netlify_site_id
        netlify_deployment_id = None
        try:
            netlify_project_name = self._generate_netlify_site_name(brand_name)
            zip_path = await self._prepare_zip_from_dict(temp_dir, netlify_project_name, generated_code_dict)
            if not site_id:
                logger.info("NETLIFY_SITE_ID not provided, creating new site...")
                site_id = await self._create_netlify_site(brand_name)
            else:
                logger.info(f"Using provided NETLIFY_SITE_ID: {site_id}")

            deploy_result = await self._upload_and_deploy_netlify(site_id, zip_path)
            netlify_deployment_id = deploy_result.get("id")
            if not netlify_deployment_id: raise ValueError("Failed to get deployment ID from Netlify after upload.")

            if deploy_result.get("state") == "ready": monitor_result = deploy_result
            else: monitor_result = await self._monitor_netlify_deployment(site_id, netlify_deployment_id)

            if not monitor_result or monitor_result.get("error"):
                reason = f"Netlify deployment failed: {monitor_result.get('error', 'Unknown monitoring error')}"
                raise RuntimeError(reason, monitor_result.get("details")) # Raise exception

            deployment_url = monitor_result.get("ssl_url") or monitor_result.get("deploy_ssl_url") or monitor_result.get("url")
            if not deployment_url:
                 site_info_url = f"/sites/{site_id}"
                 try:
                     site_info_resp = await self.netlify_client.get(site_info_url)
                     site_info_resp.raise_for_status()
                     site_info = site_info_resp.json()
                     deployment_url = site_info.get("ssl_url") or site_info.get("url")
                     if not deployment_url: raise ValueError("Could not determine deployment URL from Netlify site info.")
                     logger.warning(f"Deployment URL not in monitor result, using site URL: {deployment_url}")
                 except Exception as site_info_err:
                     logger.error(f"Error fetching site info to get URL: {site_info_err}", exc_info=True)
                     raise ValueError("Could not determine deployment URL from Netlify response or site info.") from site_info_err

            features_deployed = [f.get("feature_name", f"Unnamed Feature {i+1}") for i, f in enumerate(input_data.key_features)]
            success_payload = DeploymentResultPayload(
                deployment_url=deployment_url, brand_name=brand_name, platform='netlify',
                status=monitor_result.get("state", "READY").upper(), features_deployed=features_deployed,
                deployment_details=NetlifyDeploymentDetails(netlify_deployment_id=netlify_deployment_id, site_id=site_id)
            )
            await context.emit(Event(type="deployment.succeeded", payload=success_payload.model_dump(exclude_none=True)))
            logger.info(f"Netlify deployment finished successfully for site '{site_id}'. Status: {success_payload.status}, URL: {deployment_url}")

        except Exception as e:
            logger.error(f"Error during Netlify deployment helper: {e}", exc_info=True)
            error_payload = DeploymentFailedPayload(
                brand_name=brand_name, platform='netlify', reason=f"Error during Netlify deployment: {e}",
                error_details={"exception": str(e)}, netlify_site_id=site_id, netlify_deployment_id=netlify_deployment_id
            )
            await context.emit(Event(type="deployment.failed", data=error_payload.model_dump(exclude_none=True), metadata={"status": "error"}))
            # Do not re-raise here, let the main run_async return the error event


    async def _deploy_to_vercel(self, context: InvocationContext, input_data: DeploymentAgentInputData, generated_code_dict: Dict[str, str], project_name: str, deployment_target_env: str, temp_dir: Path):
        """Handles the Vercel deployment process within run_async and emits final event."""
        brand_name = input_data.brand_name
        vercel_deployment_id = None
        try:
            files_data_map = await self._prepare_files_from_dict(temp_dir, generated_code_dict)
            if not files_data_map: raise ValueError("File preparation step from dict returned no files.")
            files_list = list(files_data_map.values())

            logger.info(f"Uploading {len(files_list)} files to Vercel for project '{project_name}'...")
            upload_results = await asyncio.gather(*[self._upload_file_to_vercel(file_info) for file_info in files_list])
            if not all(upload_results):
                failed_files = [files_list[i]["file"] for i, success in enumerate(upload_results) if not success]
                raise RuntimeError(f"File upload failed for: {', '.join(failed_files)}", {"failed_files": failed_files})

            logger.info(f"Triggering Vercel deployment for project: {project_name} to {deployment_target_env}")
            trigger_result = await self._trigger_vercel_deployment(project_name, files_list, deployment_target_env)
            if not trigger_result or trigger_result.get("error"):
                raise RuntimeError(f"Failed to trigger Vercel deployment: {trigger_result.get('error', 'Unknown trigger error')}", trigger_result.get("details"))

            vercel_deployment_id = trigger_result.get("id")
            if not vercel_deployment_id: raise ValueError("Vercel API did not return a deployment ID after trigger.", trigger_result)

            monitor_result = await self._monitor_vercel_deployment(vercel_deployment_id, project_name)
            if not monitor_result or monitor_result.get("error"):
                raise RuntimeError(f"Deployment failed during monitoring: {monitor_result.get('error', 'Unknown monitoring error')}", monitor_result.get("details"))

            deployment_url = f"https://{monitor_result.get('url')}"
            features_deployed = [f.get("feature_name", f"Unnamed Feature {i+1}") for i, f in enumerate(input_data.key_features)]
            success_payload = DeploymentResultPayload(
                deployment_url=deployment_url, brand_name=brand_name, platform='vercel', features_deployed=features_deployed,
                deployment_details=VercelDeploymentDetails(
                    vercel_deployment_id=vercel_deployment_id, project_name=project_name,
                    region=monitor_result.get("regions", ["default"])[0]
                )
            )
            await context.emit(Event(type="deployment.succeeded", payload=success_payload.model_dump(exclude_none=True)))
            logger.info(f"Vercel deployment finished successfully for project '{project_name}'. Status: READY, URL: {deployment_url}")

        except Exception as e:
            logger.error(f"Error during Vercel deployment helper: {e}", exc_info=True)
            error_details = {"exception": str(e)}
            if isinstance(e, RuntimeError) and len(e.args) > 1: error_details = e.args[1]
            error_payload = DeploymentFailedPayload(
                brand_name=brand_name, platform='vercel', reason=f"Error during Vercel deployment: {e.args[0] if e.args else e}",
                error_details=error_details, vercel_deployment_id=vercel_deployment_id
            )
            await context.emit(Event(type="deployment.failed", data=error_payload.model_dump(exclude_none=True), metadata={"status": "error"}))
            # Do not re-raise here


# --- FastAPI Server Setup ---

app = FastAPI(title="DeploymentAgent A2A Server")

# Instantiate the agent
deployment_agent_instance = DeploymentAgent()

@app.post("/invoke") # Response model is dynamic (success or failure payload)
async def invoke_agent(request: DeploymentAgentInputData = Body(...)):
    """
    A2A endpoint to invoke the DeploymentAgent.
    Expects JSON body matching DeploymentAgentInputData.
    Returns DeploymentResultPayload on success, or raises HTTPException with DeploymentFailedPayload on error.
    """
    logger.info(f"DeploymentAgent /invoke called for target: {request.deployment_target}, brand: {request.brand_name}")
    invocation_id = f"deploy-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(1000,9999)}"
    # Create a mock context that can capture emitted events if needed, or use a real one if available
    # For simplicity, we'll rely on run_async returning the final event.
    context = InvocationContext(agent_id="deployment-agent", invocation_id=invocation_id, data=request.model_dump())
    # Add a way for the context to store the last emitted event if run_async doesn't return it
    # context.last_event = None
    # async def mock_emit(event: Event): context.last_event = event
    # context.emit = mock_emit # Monkey-patch emit if needed

    try:
        final_event = await deployment_agent_instance.run_async(context)

        # Check the event returned by run_async (or context.last_event if patched)
        if final_event and final_event.metadata.get("status") == "success":
             # Check if it's the expected success event type
             if final_event.type == "deployment.succeeded":
                 logger.info(f"DeploymentAgent returning success result for brand: {request.brand_name}")
                 try:
                     success_payload = DeploymentResultPayload(**final_event.payload)
                     return success_payload # Return the validated payload
                 except ValidationError as val_err:
                     logger.error(f"Success event payload validation failed: {val_err}. Payload: {final_event.payload}")
                     raise HTTPException(status_code=500, detail={"error": "Internal validation error on success payload.", "details": val_err.errors()})
             elif final_event.type == "adk.agent.result": # Handle the generic result from run_async itself
                 logger.info(f"DeploymentAgent run_async completed, final status emitted by helper. Returning completion status.")
                 # This path might be hit if helpers emit the definitive event.
                 # We might need to query the actual result if the caller needs the URL.
                 # For now, return a simple success confirmation.
                 return {"status": "completed", "target": request.deployment_target, "invocation_id": invocation_id}
             else:
                  logger.error(f"DeploymentAgent returned unexpected success event type: {final_event.type}")
                  raise HTTPException(status_code=500, detail={"error": "Agent finished with unexpected success event type."})

        elif final_event and final_event.metadata.get("status") == "error":
             logger.error(f"DeploymentAgent run_async returned failure event for brand: {request.brand_name}")
             try:
                 # Assume payload matches DeploymentFailedPayload structure
                 failed_payload = DeploymentFailedPayload(**final_event.payload)
                 raise HTTPException(status_code=500, detail=failed_payload.model_dump(exclude_none=True))
             except ValidationError as val_err:
                 logger.error(f"Failure event payload validation failed: {val_err}. Payload: {final_event.payload}")
                 raise HTTPException(status_code=500, detail={"error": "Internal validation error on failure payload.", "original_payload": final_event.payload})
        else:
            logger.error(f"DeploymentAgent run_async returned unexpected or None event: {final_event}")
            raise HTTPException(status_code=500, detail={"error": "Agent execution finished with unexpected state.", "event": str(final_event)})

    except HTTPException as http_exc:
        raise http_exc # Re-raise FastAPI exceptions
    except Exception as e:
        logger.error(f"Error during agent invocation: {e}", exc_info=True)
        failed_payload = DeploymentFailedPayload(
            brand_name=request.brand_name, platform=request.deployment_target,
            reason=f"Internal Server Error: {e}", error_details={"exception": str(e)}
        )
        raise HTTPException(status_code=500, detail=failed_payload.model_dump(exclude_none=True))
    finally:
         # Ensure clients are closed if they were opened by the agent instance
         # This might be better handled at server shutdown depending on agent lifecycle
         if deployment_agent_instance.vercel_client and not deployment_agent_instance.vercel_client.is_closed:
             await deployment_agent_instance.vercel_client.aclose()
             logger.debug("Closed Vercel client after request.")
         if deployment_agent_instance.netlify_client and not deployment_agent_instance.netlify_client.is_closed:
             await deployment_agent_instance.netlify_client.aclose()
             logger.debug("Closed Netlify client after request.")


@app.get("/health")
async def health_check():
    # Basic health check
    return {"status": "ok"}

# --- Main execution block ---

if __name__ == "__main__":
    # Load .env for local development if needed
    try:
        from dotenv import load_dotenv
        if load_dotenv():
             logger.info("Loaded .env file for local run.")
        else:
             logger.info("No .env file found or it was empty.")
    except ImportError:
        logger.info("dotenv library not found, skipping .env load.")

    parser = argparse.ArgumentParser(description="Run the DeploymentAgent A2A server.")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind the server to.")
    parser.add_argument("--port", type=int, default=8084, help="Port to run the server on.") # Default matches compose
    args = parser.parse_args()

    print(f"Starting DeploymentAgent A2A server on {args.host}:{args.port}")

    # Instantiate agent here if needed globally, or rely on instance created for endpoint
    # deployment_agent_instance = DeploymentAgent() # Global instance

    uvicorn.run(app, host=args.host, port=args.port)