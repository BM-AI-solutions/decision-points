"""
Deployment Agent for Decision Points (ADK Version).

This agent deploys applications to Vercel or Netlify based on generated code using ADK tools.
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
import traceback # Import traceback for detailed error logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

import httpx
from pydantic import BaseModel, Field, HttpUrl, ValidationError

# ADK Imports
from google.adk.agents import Agent # Use ADK Agent

from google.adk.events import Event # Import Event for tool return type

# Removed A2A and BaseSpecializedAgent imports
from app.config import settings

# Configure logging
logger = logging.getLogger(__name__)

# --- Constants ---
VERCEL_API_BASE_URL = "https://api.vercel.com"
NETLIFY_API_BASE_URL = "https://api.netlify.com/api/v1"
POLL_INTERVAL_SECONDS = 5
MAX_POLL_ATTEMPTS = 24 # 2 minutes total

# --- API Tokens (Loaded once) ---
VERCEL_API_TOKEN = os.environ.get("VERCEL_API_TOKEN") or settings.VERCEL_API_TOKEN
VERCEL_TEAM_ID = os.environ.get("VERCEL_TEAM_ID") or settings.VERCEL_TEAM_ID
NETLIFY_AUTH_TOKEN = os.environ.get("NETLIFY_AUTH_TOKEN") or settings.NETLIFY_AUTH_TOKEN
NETLIFY_SITE_ID = os.environ.get("NETLIFY_SITE_ID") or settings.NETLIFY_SITE_ID # Optional: Pre-configured site

if not VERCEL_API_TOKEN:
    logger.warning("VERCEL_API_TOKEN not configured. Vercel deployment will fail.")
if not NETLIFY_AUTH_TOKEN:
    logger.warning("NETLIFY_AUTH_TOKEN not configured. Netlify deployment will fail.")

# --- Data Models (Keep as they define data structures) ---

class DeploymentAgentInputData(BaseModel):
    """Expected data structure for the deployment tool."""
    brand_name: str = Field(description="The final brand name for the product.")
    product_concept: str = Field(description="Description of the product being deployed.")
    key_features: List[Dict[str, Any]] = Field(description="List of features included in the deployment.")
    deployment_target: str = Field(default='vercel', description="Deployment target ('vercel' or 'netlify').")
    generated_code_dict: Dict[str, str] = Field(description="Dictionary mapping file paths to code content.")
    # Optional: Add vercel_project_name, deployment_environment etc. if needed

class VercelDeploymentDetails(BaseModel):
    """Specific details about the Vercel deployment."""
    vercel_deployment_id: str
    project_name: str
    deployment_time_utc: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())
    region: str = "default"

class NetlifyDeploymentDetails(BaseModel):
    """Specific details about the Netlify deployment."""
    netlify_deployment_id: str
    site_id: str
    deployment_time_utc: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())

class DeploymentResultPayload(BaseModel):
    """Payload for the successful deployment result."""
    success: bool = True
    deployment_url: HttpUrl
    status: str = "READY"
    brand_name: str
    features_deployed: List[str]
    platform: str
    deployment_details: Union[VercelDeploymentDetails, NetlifyDeploymentDetails]

class DeploymentFailedPayload(BaseModel):
    """Payload for the failed deployment result."""
    success: bool = False
    brand_name: str
    platform: str
    reason: str
    error_details: Optional[Dict[str, Any]] = None
    vercel_deployment_id: Optional[str] = None
    netlify_site_id: Optional[str] = None
    netlify_deployment_id: Optional[str] = None

# --- Helper Functions (Moved outside class, made async where needed) ---

def _generate_vercel_project_name(brand_name: str) -> str:
    """Generates a Vercel-compatible project name."""
    sanitized = ''.join(c for c in brand_name.lower() if c.isalnum() or c == '-')
    sanitized = sanitized.replace(' ', '-')
    sanitized = sanitized.strip('-')[:90]
    if not sanitized: sanitized = f"deployment-{random.randint(1000, 9999)}"
    return sanitized

def _generate_netlify_site_name(brand_name: str) -> str:
    """Generates a potential Netlify site name (subdomain)."""
    sanitized = ''.join(c for c in brand_name.lower() if c.isalnum())
    sanitized = sanitized.replace(' ', '')
    sanitized = sanitized.strip('-')[:60]
    if not sanitized: sanitized = f"adk-site-{random.randint(1000, 9999)}"
    return sanitized

async def _prepare_files_from_dict(temp_dir: Path, generated_code_dict: Dict[str, str]) -> Dict[str, Dict[str, Any]]:
    """Creates files from dict and returns Vercel file structure."""
    logger.debug(f"Preparing files from generated_code_dict in {temp_dir}")
    file_data = {}
    try:
        for relative_path_str, code_content in generated_code_dict.items():
            if relative_path_str.startswith('/'): relative_path_str = relative_path_str[1:]
            absolute_path = temp_dir / relative_path_str
            absolute_path.parent.mkdir(parents=True, exist_ok=True)
            content_bytes = code_content.encode('utf-8')
            absolute_path.write_bytes(content_bytes)
            digest = hashlib.sha1(content_bytes).hexdigest()
            size = len(content_bytes)
            file_data[relative_path_str] = {"file": relative_path_str, "sha": digest, "size": size, "path": absolute_path}
            logger.debug(f"  Prepared: {relative_path_str} (Size: {size}, SHA: {digest[:7]}...)")

        if "vercel.json" not in file_data:
             logger.debug("  Adding default vercel.json.")
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
        logger.error(f"Error creating deployment files/directories from dict: {e}")
        raise ValueError(f"Failed to prepare deployment files from dict: {e}") from e
    except Exception as e:
        logger.error(f"Unexpected error preparing deployment files from dict: {e}", exc_info=True)
        raise ValueError(f"Unexpected error preparing deployment files from dict: {e}") from e

async def _upload_file_to_vercel(client: httpx.AsyncClient, file_info: Dict[str, Any]) -> bool:
    """Uploads a single file to Vercel."""
    upload_url = f"{VERCEL_API_BASE_URL}/v2/files"
    headers = {
        "Authorization": f"Bearer {VERCEL_API_TOKEN}",
        "Content-Length": str(file_info["size"]),
        "x-vercel-digest": file_info["sha"],
    }
    if VERCEL_TEAM_ID: headers["TeamId"] = VERCEL_TEAM_ID
    try:
        file_bytes = file_info["path"].read_bytes()
        response = await client.post(upload_url, headers=headers, content=file_bytes)
        if response.status_code == 200:
            logger.debug(f"Successfully uploaded file: {file_info['file']}")
            return True
        else:
            logger.error(f"Error uploading file {file_info['file']}: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        logger.error(f"Exception uploading file {file_info['file']}: {e}", exc_info=True)
        return False

async def _prepare_zip_from_dict(temp_dir: Path, project_name: str, generated_code_dict: Dict[str, str]) -> Path:
    """Creates files from dict within a site_root and zips it for Netlify."""
    logger.debug(f"Preparing Netlify source zip for '{project_name}' in {temp_dir}")
    site_root_dir = temp_dir / "site_root"
    try:
        site_root_dir.mkdir(parents=True, exist_ok=True)
        for relative_path_str, code_content in generated_code_dict.items():
            if relative_path_str.startswith('/'): relative_path_str = relative_path_str[1:]
            absolute_path = site_root_dir / relative_path_str
            absolute_path.parent.mkdir(parents=True, exist_ok=True)
            absolute_path.write_text(code_content, encoding='utf-8')
            logger.debug(f"  Added to zip source: {relative_path_str}")

        zip_filename = f"{project_name}-netlify-src.zip"
        zip_path = temp_dir / zip_filename
        logger.debug(f"Creating Netlify deployment source zip: {zip_path}")
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in site_root_dir.rglob('*'):
                if file_path.is_file():
                    relative_path = file_path.relative_to(site_root_dir)
                    zipf.write(file_path, relative_path)
        logger.debug(f"  Created deployment source zip: {zip_path} (Size: {zip_path.stat().st_size} bytes)")
        logger.debug("  NOTE: Netlify site must be configured with appropriate build command/publish dir if build needed.")
        return zip_path
    except OSError as e:
        logger.error(f"Error creating Netlify zip files/directories from dict: {e}")
        raise ValueError(f"Failed to prepare Netlify zip from dict: {e}") from e
    except Exception as e:
        logger.error(f"Unexpected error preparing Netlify zip from dict: {e}", exc_info=True)
        raise ValueError(f"Unexpected error preparing Netlify zip from dict: {e}") from e

async def _trigger_vercel_deployment(client: httpx.AsyncClient, project_name: str, files_data: List[Dict[str, Any]], target_environment: str) -> Optional[Dict[str, Any]]:
    """Triggers the Vercel deployment."""
    deployment_url = f"{VERCEL_API_BASE_URL}/v13/deployments"
    params = {}
    if VERCEL_TEAM_ID: params["teamId"] = VERCEL_TEAM_ID
    payload = {
        "name": project_name,
        "files": [{"file": f["file"], "sha": f["sha"], "size": f["size"]} for f in files_data],
        "projectSettings": {"framework": "vite"},
        "target": target_environment,
        "project": project_name
    }
    try:
        response = await client.post(deployment_url, params=params, json=payload)
        response.raise_for_status()
        deployment_data = response.json()
        logger.info(f"Successfully initiated Vercel deployment: ID {deployment_data.get('id')} for project '{project_name}' to target '{target_environment}'")
        return deployment_data
    except httpx.HTTPStatusError as e:
        error_details = {"raw_content": e.response.text}
        try: error_details = e.response.json()
        except json.JSONDecodeError: pass
        logger.error(f"HTTP error triggering Vercel deployment for '{project_name}': {e.response.status_code} - {error_details}")
        return {"error": "trigger_failed", "status_code": e.response.status_code, "details": error_details}
    except Exception as e:
        logger.error(f"Unexpected error triggering Vercel deployment for '{project_name}': {e}", exc_info=True)
        return {"error": "unexpected", "details": str(e)}

async def _monitor_vercel_deployment(client: httpx.AsyncClient, deployment_id: str, project_name: str) -> Optional[Dict[str, Any]]:
    """Monitors a Vercel deployment."""
    status_url = f"{VERCEL_API_BASE_URL}/v13/deployments/{deployment_id}"
    params = {}
    if VERCEL_TEAM_ID: params["teamId"] = VERCEL_TEAM_ID
    logger.info(f"Monitoring Vercel deployment {deployment_id} for project '{project_name}'...")
    for attempt in range(MAX_POLL_ATTEMPTS):
        try:
            await asyncio.sleep(POLL_INTERVAL_SECONDS) # Wait before checking
            response = await client.get(status_url, params=params)
            response.raise_for_status()
            status_data = response.json()
            state = status_data.get("readyState")
            logger.debug(f"  Attempt {attempt + 1}/{MAX_POLL_ATTEMPTS}: Project '{project_name}', Deployment {deployment_id}, State = {state}")
            if state == "READY":
                logger.info(f"Deployment successful for project '{project_name}'!")
                return status_data
            elif state in ["ERROR", "CANCELED"]:
                logger.error(f"Deployment failed/canceled for project '{project_name}'. State: {state}")
                return {"error": "deployment_failed", "state": state, "details": status_data.get("error")}
            elif state not in ["BUILDING", "QUEUED", "INITIALIZING"]:
                logger.warning(f"Unknown deployment state for project '{project_name}': {state}")
        except Exception as e:
            logger.error(f"Error monitoring deployment {deployment_id} for project '{project_name}' (Attempt {attempt+1}): {e}", exc_info=True)
            if attempt == MAX_POLL_ATTEMPTS - 1:
                return {"error": "monitoring_error", "details": str(e)}
    logger.error(f"Deployment monitoring timed out for project '{project_name}'.")
    return {"error": "timeout", "details": f"Deployment {deployment_id} did not reach READY state."}

async def _create_netlify_site(client: httpx.AsyncClient, brand_name: str) -> str:
    """Creates a new site on Netlify."""
    site_name = _generate_netlify_site_name(brand_name)
    create_url = "/sites"
    payload = {"name": site_name}
    logger.info(f"Attempting to create Netlify site with suggested name: {site_name}")
    try:
        response = await client.post(create_url, json=payload)
        response.raise_for_status()
        site_data = response.json()
        site_id = site_data.get("site_id")
        if not site_id: raise ValueError("Netlify API did not return a site_id.")
        logger.info(f"Successfully created Netlify site: ID {site_id}, Name {site_data.get('name')}")
        return site_id
    except httpx.HTTPStatusError as e:
        error_details = {"raw_content": e.response.text}
        try: error_details = e.response.json()
        except json.JSONDecodeError: pass
        logger.error(f"HTTP error creating Netlify site: {e.response.status_code} - {error_details}")
        raise ValueError(f"Failed to create Netlify site: {error_details}") from e
    except Exception as e:
        logger.error(f"Unexpected error creating Netlify site: {e}", exc_info=True)
        raise ValueError(f"Unexpected error creating Netlify site: {e}") from e

async def _upload_and_deploy_netlify(client: httpx.AsyncClient, site_id: str, zip_path: Path) -> Dict[str, Any]:
    """Uploads the site zip and triggers deployment on Netlify."""
    deploy_url = f"/sites/{site_id}/deploys"
    logger.info(f"Uploading deployment zip '{zip_path.name}' to Netlify site {site_id}...")
    headers = {"Authorization": f"Bearer {NETLIFY_AUTH_TOKEN}", "Content-Type": "application/zip"}
    try:
        async with zip_path.open("rb") as f: zip_content = await f.read()
        response = await client.post(deploy_url, headers=headers, content=zip_content)
        response.raise_for_status()
        deploy_data = response.json()
        deployment_id = deploy_data.get("id")
        if not deployment_id: raise ValueError("Netlify API did not return deployment ID.")
        logger.info(f"Successfully initiated Netlify deployment: ID {deployment_id} for site {site_id}")
        return deploy_data
    except httpx.HTTPStatusError as e:
        error_details = {"raw_content": e.response.text}
        try: error_details = e.response.json()
        except json.JSONDecodeError: pass
        logger.error(f"HTTP error deploying to Netlify site {site_id}: {e.response.status_code} - {error_details}")
        raise ValueError(f"Failed to deploy to Netlify: {error_details}") from e
    except Exception as e:
        logger.error(f"Unexpected error deploying to Netlify site {site_id}: {e}", exc_info=True)
        raise ValueError(f"Unexpected error deploying to Netlify: {e}") from e

async def _monitor_netlify_deployment(client: httpx.AsyncClient, site_id: str, deployment_id: str) -> Dict[str, Any]:
    """Monitors a Netlify deployment."""
    status_url = f"/sites/{site_id}/deploys/{deployment_id}"
    logger.info(f"Monitoring Netlify deployment {deployment_id} for site {site_id}...")
    for attempt in range(MAX_POLL_ATTEMPTS):
        try:
            await asyncio.sleep(POLL_INTERVAL_SECONDS) # Wait before checking
            response = await client.get(status_url)
            response.raise_for_status()
            status_data = response.json()
            state = status_data.get("state")
            logger.debug(f"  Attempt {attempt + 1}/{MAX_POLL_ATTEMPTS}: Site {site_id}, Deployment {deployment_id}, State = {state}")
            if state == "ready":
                logger.info(f"Netlify deployment successful for site {site_id}!")
                return status_data
            elif state in ["error", "failed"]:
                error_message = status_data.get("error_message", "Unknown error")
                logger.error(f"Netlify deployment failed for site {site_id}. State: {state}, Reason: {error_message}")
                return {"error": "deployment_failed", "state": state, "details": error_message}
            elif state not in ["building", "uploading", "processing", "new"]:
                logger.warning(f"Unknown Netlify deployment state for site {site_id}: {state}")
        except Exception as e:
            logger.error(f"Error monitoring Netlify deployment {deployment_id} (Attempt {attempt+1}): {e}", exc_info=True)
            if attempt == MAX_POLL_ATTEMPTS - 1:
                return {"error": "monitoring_error", "details": str(e)}
    logger.error(f"Netlify deployment monitoring timed out for site {site_id}, deployment {deployment_id}.")
    return {"error": "timeout", "details": f"Deployment {deployment_id} did not reach 'ready' state."}

# --- ADK Tool Definition ---

@tool(description="Deploys an application to Vercel or Netlify using generated code.")
async def deploy_application_tool(
    brand_name: str,
    product_concept: str,
    key_features: List[Dict[str, Any]],
    generated_code_dict: Dict[str, str],
    deployment_target: str = 'vercel',
    # Add other optional inputs like vercel_project_name if needed
) -> Dict[str, Any]:
    """
    ADK Tool: Deploys application code to Vercel or Netlify.
    Returns a dictionary representing DeploymentResultPayload or DeploymentFailedPayload.
    """
    logger.info(f"Tool: Starting deployment for brand '{brand_name}' to target '{deployment_target}'")
    deployment_target = deployment_target.lower()
    temp_dir_obj = None
    vercel_client = None
    netlify_client = None

    try:
        # Validate input data structure (Pydantic model helps here)
        input_data = DeploymentAgentInputData(
            brand_name=brand_name,
            product_concept=product_concept,
            key_features=key_features,
            deployment_target=deployment_target,
            generated_code_dict=generated_code_dict
        )

        if not generated_code_dict:
            raise ValueError("Input data is missing the required 'generated_code_dict'.")
        logger.debug(f"Tool: Received generated_code_dict with {len(generated_code_dict)} files.")

        # Initialize necessary client
        if deployment_target == 'vercel':
            if not VERCEL_API_TOKEN: raise ValueError("VERCEL_API_TOKEN is not configured.")
            vercel_client = httpx.AsyncClient(base_url=VERCEL_API_BASE_URL, headers={"Authorization": f"Bearer {VERCEL_API_TOKEN}"}, timeout=30.0)
        elif deployment_target == 'netlify':
            if not NETLIFY_AUTH_TOKEN: raise ValueError("NETLIFY_AUTH_TOKEN is not configured.")
            netlify_client = httpx.AsyncClient(base_url=NETLIFY_API_BASE_URL, headers={"Authorization": f"Bearer {NETLIFY_AUTH_TOKEN}"}, timeout=60.0)
        else:
            raise ValueError(f"Unsupported deployment_target: '{deployment_target}'. Must be 'vercel' or 'netlify'.")

        # --- Platform-Specific Logic ---
        temp_dir_obj = tempfile.TemporaryDirectory()
        temp_dir = Path(temp_dir_obj.name)
        result_payload = None

        if deployment_target == 'netlify':
            logger.info(f"Tool: Executing Netlify deployment for '{brand_name}'...")
            site_id = NETLIFY_SITE_ID # Use pre-configured if available
            netlify_deployment_id = None
            try:
                netlify_project_name = _generate_netlify_site_name(brand_name)
                zip_path = await _prepare_zip_from_dict(temp_dir, netlify_project_name, generated_code_dict)
                if not site_id:
                    logger.info("Tool: NETLIFY_SITE_ID not provided, creating new site...")
                    site_id = await _create_netlify_site(netlify_client, brand_name)
                else:
                    logger.info(f"Tool: Using provided NETLIFY_SITE_ID: {site_id}")

                deploy_result = await _upload_and_deploy_netlify(netlify_client, site_id, zip_path)
                netlify_deployment_id = deploy_result.get("id")
                if not netlify_deployment_id: raise ValueError("Failed to get deployment ID from Netlify.")

                monitor_result = deploy_result if deploy_result.get("state") == "ready" else await _monitor_netlify_deployment(netlify_client, site_id, netlify_deployment_id)

                if not monitor_result or monitor_result.get("error"):
                    raise ValueError(f"Netlify deployment failed: {monitor_result.get('error', 'Unknown monitoring error')}", monitor_result.get("details"))

                deployment_url = monitor_result.get("ssl_url") or monitor_result.get("deploy_ssl_url") or monitor_result.get("url")
                if not deployment_url:
                     # Try fetching site info as fallback
                     try:
                         site_info_resp = await netlify_client.get(f"/sites/{site_id}")
                         site_info_resp.raise_for_status()
                         site_info = site_info_resp.json()
                         deployment_url = site_info.get("ssl_url") or site_info.get("url")
                         if not deployment_url: raise ValueError("Could not determine URL from site info.")
                         logger.warning(f"Tool: Using site URL as fallback: {deployment_url}")
                     except Exception as site_err:
                         raise ValueError("Could not determine deployment URL.") from site_err

                features = [f.get("feature_name", f"F{i+1}") for i, f in enumerate(key_features)]
                result_payload = DeploymentResultPayload(
                    deployment_url=deployment_url, brand_name=brand_name, platform='netlify',
                    status=monitor_result.get("state", "READY").upper(), features_deployed=features,
                    deployment_details=NetlifyDeploymentDetails(netlify_deployment_id=netlify_deployment_id, site_id=site_id)
                ).model_dump(exclude_none=True)

            except Exception as e: # Catch errors specific to Netlify flow
                logger.error(f"Tool: Netlify deployment flow failed: {e}", exc_info=True)
                result_payload = DeploymentFailedPayload(
                    brand_name=brand_name, platform='netlify', reason=f"Error during Netlify deployment: {e}",
                    error_details={"exception": str(e), "trace": traceback.format_exc()},
                    netlify_site_id=site_id, netlify_deployment_id=netlify_deployment_id
                ).model_dump(exclude_none=True)


        elif deployment_target == 'vercel':
            logger.info(f"Tool: Executing Vercel deployment for '{brand_name}'...")
            vercel_project_name = _generate_vercel_project_name(brand_name) # Example name generation
            vercel_target_env = "production" # Example target
            vercel_deployment_id = None
            try:
                files_data_map = await _prepare_files_from_dict(temp_dir, generated_code_dict)
                if not files_data_map: raise ValueError("File preparation returned no files.")
                files_list = list(files_data_map.values())

                logger.info(f"Tool: Uploading {len(files_list)} files to Vercel for '{vercel_project_name}'...")
                upload_tasks = [_upload_file_to_vercel(vercel_client, file_info) for file_info in files_list]
                upload_results = await asyncio.gather(*upload_tasks)
                if not all(upload_results):
                    failed_files = [files_list[i]["file"] for i, success in enumerate(upload_results) if not success]
                    raise ValueError(f"File upload failed for: {', '.join(failed_files)}")

                logger.info(f"Tool: Triggering Vercel deployment for '{vercel_project_name}' to '{vercel_target_env}'...")
                trigger_result = await _trigger_vercel_deployment(vercel_client, vercel_project_name, files_list, vercel_target_env)
                if not trigger_result or trigger_result.get("error"):
                    raise ValueError(f"Failed to trigger Vercel deployment: {trigger_result.get('error', 'Unknown')}", trigger_result.get("details"))

                vercel_deployment_id = trigger_result.get("id")
                if not vercel_deployment_id: raise ValueError("Vercel API did not return deployment ID.")

                monitor_result = await _monitor_vercel_deployment(vercel_client, vercel_deployment_id, vercel_project_name)
                if not monitor_result or monitor_result.get("error"):
                    raise ValueError(f"Deployment failed during monitoring: {monitor_result.get('error', 'Unknown')}", monitor_result.get("details"))

                deployment_url = f"https://{monitor_result.get('url')}"
                features = [f.get("feature_name", f"F{i+1}") for i, f in enumerate(key_features)]
                result_payload = DeploymentResultPayload(
                    deployment_url=deployment_url, brand_name=brand_name, platform='vercel',
                    features_deployed=features,
                    deployment_details=VercelDeploymentDetails(
                        vercel_deployment_id=vercel_deployment_id, project_name=vercel_project_name,
                        region=monitor_result.get("regions", ["default"])[0]
                    )
                ).model_dump(exclude_none=True)

            except Exception as e: # Catch errors specific to Vercel flow
                logger.error(f"Tool: Vercel deployment flow failed: {e}", exc_info=True)
                # If details are available (e.g., from ValueError), include them
                error_details = getattr(e, 'args')[1] if len(getattr(e, 'args', [])) > 1 else {"exception": str(e), "trace": traceback.format_exc()}
                result_payload = DeploymentFailedPayload(
                    brand_name=brand_name, platform='vercel', reason=f"Error during Vercel deployment: {getattr(e, 'args')[0] if e.args else e}",
                    error_details=error_details,
                    vercel_deployment_id=vercel_deployment_id
                ).model_dump(exclude_none=True)

        # Return the constructed payload (success or failure)
        return result_payload

    except (ValidationError, TypeError, ValueError) as e:
        logger.error(f"Tool: Input validation/processing failed: {e}", exc_info=True)
        # Construct failure payload for validation errors
        return DeploymentFailedPayload(
            brand_name=brand_name, # Use brand_name if available from input
            platform=deployment_target,
            reason=f"Invalid or missing input data: {e}",
            error_details={"validation_errors": e.errors() if isinstance(e, ValidationError) else str(e)}
        ).model_dump(exclude_none=True)
    except Exception as e:
        logger.error(f"Tool: Unexpected error during deployment: {e}", exc_info=True)
        # Construct failure payload for unexpected errors
        return DeploymentFailedPayload(
            brand_name=brand_name, # Use brand_name if available
            platform=deployment_target,
            reason=f"Unexpected error during deployment: {e}",
            error_details={"exception": str(e), "trace": traceback.format_exc()}
        ).model_dump(exclude_none=True)
    finally:
        # Ensure clients are closed
        if vercel_client and not vercel_client.is_closed:
            await vercel_client.aclose()
            logger.debug("Tool: Closed Vercel httpx client.")
        if netlify_client and not netlify_client.is_closed:
            await netlify_client.aclose()
            logger.debug("Tool: Closed Netlify httpx client.")
        # Clean up temp directory
        if temp_dir_obj:
            try:
                temp_dir_obj.cleanup()
                logger.debug(f"Tool: Cleaned up temp directory: {temp_dir_obj.name}")
            except Exception as e_clean:
                logger.warning(f"Tool: Failed to clean up temp directory {temp_dir_obj.name}: {e_clean}")


# --- Instantiate the ADK Agent ---
agent = Agent(
    name="deployment_adk", # ADK specific name
    description="Deploys applications to Vercel or Netlify.",
    tools=[
        deploy_application_tool,
    ],
)

# Removed A2A server specific code and old class structure
