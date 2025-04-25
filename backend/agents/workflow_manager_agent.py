"""
Workflow Manager Agent for Decision Points (ADK Version).

This agent orchestrates the multi-agent workflow for generating and deploying products using ADK tools.
"""

import json
import time
import random
import httpx
import asyncio
import uuid
import logging
import traceback
from enum import Enum
from typing import Dict, Any, Optional, Union, List

# Import SocketIO type hint if needed
try:
    from flask_socketio import SocketIO
except ImportError:
    SocketIO = Any # Fallback

# Import database service and Pydantic models
from app.services.db_service import DatabaseService
from pydantic import BaseModel, Field, HttpUrl, ValidationError

# ADK Imports
from google.adk.agents import Agent # Use ADK Agent
from google.adk.tools import tool, ToolContext # Import tool decorator and context
from google.adk.events import Event # Import Event for tool return type

# Removed BaseSpecializedAgent import
from app.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Global Config & Clients ---
AGENT_ID = "workflow_manager_adk"
DB_SERVICE = DatabaseService() # Instantiate DB service
# SocketIO instance needs to be provided/managed externally
# For this refactor, we'll assume a global SOCKETIO instance exists or is None
SOCKETIO: Optional[SocketIO] = None # Placeholder: Inject or initialize appropriately

# --- Pydantic Models (Simplified/Combined for Workflow State) ---
# Using simplified dicts for state storage, validation happens during step execution

class WorkflowStatus(str, Enum):
    STARTING = "STARTING"
    RUNNING_MARKET_RESEARCH = "RUNNING_MARKET_RESEARCH"
    PENDING_APPROVAL = "PENDING_APPROVAL" # Paused after market research
    APPROVED_RESUMING = "APPROVED_RESUMING" # Triggered by resume call
    RUNNING_IMPROVEMENT = "RUNNING_IMPROVEMENT"
    COMPLETED_IMPROVEMENT = "COMPLETED_IMPROVEMENT"
    STOPPED_LOW_POTENTIAL = "STOPPED_LOW_POTENTIAL" # Stopped after improvement check
    RUNNING_BRANDING = "RUNNING_BRANDING"
    COMPLETED_BRANDING = "COMPLETED_BRANDING"
    RUNNING_CODE_GENERATION = "RUNNING_CODE_GENERATION"
    COMPLETED_CODE_GENERATION = "COMPLETED_CODE_GENERATION"
    RUNNING_DEPLOYMENT = "RUNNING_DEPLOYMENT"
    COMPLETED_DEPLOYMENT = "COMPLETED_DEPLOYMENT"
    RUNNING_MARKETING = "RUNNING_MARKETING"
    COMPLETED_MARKETING = "COMPLETED_MARKETING"
    COMPLETED = "COMPLETED" # Final success state
    FAILED = "FAILED"

class WorkflowStep(str, Enum):
    MARKET_RESEARCH = "MARKET_RESEARCH"
    IMPROVEMENT = "IMPROVEMENT"
    BRANDING = "BRANDING"
    CODE_GENERATION = "CODE_GENERATION"
    DEPLOYMENT = "DEPLOYMENT"
    MARKETING = "MARKETING"

# Mapping from logical step to target ADK agent ID and tool name
# Ensure these match the names defined in the refactored agent files
WORKFLOW_STEPS_CONFIG = {
    WorkflowStep.MARKET_RESEARCH: {"agent_id": "market_research_adk", "tool_name": "research_market_tool"},
    WorkflowStep.IMPROVEMENT: {"agent_id": "improvement_adk", "tool_name": "improve_product_tool"},
    WorkflowStep.BRANDING: {"agent_id": "branding_adk", "tool_name": "generate_brand_tool"},
    WorkflowStep.CODE_GENERATION: {"agent_id": "code_generation_adk", "tool_name": "generate_code_tool"},
    WorkflowStep.DEPLOYMENT: {"agent_id": "deployment_adk", "tool_name": "deploy_application_tool"},
    WorkflowStep.MARKETING: {"agent_id": "marketing_adk", "tool_name": "generate_marketing_materials_tool"},
}

# --- Helper Functions ---

async def _update_workflow_state(workflow_run_id: str, state_data: Dict[str, Any]):
    """Helper to update workflow state in PostgreSQL."""
    try:
        updated = await DB_SERVICE.update_workflow_state(workflow_run_id, state_data)
        if updated:
            logger.info(f"[{workflow_run_id}] DB state updated: Status={state_data.get('status')}, Step={state_data.get('current_step')}")
            # Emit SocketIO update after successful DB update
            if SOCKETIO:
                try:
                    # Ensure data is serializable for SocketIO
                    emit_data = {'workflow_run_id': workflow_run_id, **state_data}
                    # Remove potentially large/complex objects before emitting if needed
                    emit_data.pop('market_research_result', None)
                    emit_data.pop('improvement_result', None)
                    emit_data.pop('branding_result', None)
                    emit_data.pop('code_generation_result', None)
                    emit_data.pop('deployment_result', None)
                    emit_data.pop('marketing_result', None)
                    emit_data.pop('final_result', None)
                    SOCKETIO.emit('workflow_update', emit_data)
                    logger.debug(f"[{workflow_run_id}] Emitted SocketIO update: {emit_data}")
                except Exception as sock_err:
                    logger.error(f"[{workflow_run_id}] Failed to emit SocketIO update after DB save: {sock_err}", exc_info=True)
        else:
            logger.error(f"[{workflow_run_id}] Error: Workflow not found in database. Cannot update state.")
    except Exception as e:
        logger.error(f"[{workflow_run_id}] Error updating database state: {type(e).__name__}: {e}", exc_info=True)
        # Don't re-raise here, allow workflow to potentially continue or fail gracefully

async def _handle_step_failure(workflow_run_id: str, current_step: WorkflowStep, error_details: str, agent_name: str):
    """Handles database update and SocketIO emit for a failed step."""
    logger.error(f"[{workflow_run_id}] Step {current_step.value} failed. Agent: {agent_name}. Reason: {error_details}")
    current_status = WorkflowStatus.FAILED
    await _update_workflow_state(workflow_run_id, {
        "status": current_status.value,
        "current_step": current_step.value,
        "error_message": error_details
    })
    # SocketIO emit happens within _update_workflow_state

async def _execute_workflow_step(context: ToolContext, workflow_run_id: str):
    """
    Executes the next step of the workflow based on the current state stored in the database.
    This function is intended to be run asynchronously (e.g., via asyncio.create_task).
    """
    logger.info(f"[{workflow_run_id}] Executing next workflow step...")
    current_step: Optional[WorkflowStep] = None # Track step where failure occurs
    agent_name_for_error: str = "WorkflowManager" # Default agent name for errors

    try:
        # 1. Load current state from DB
        workflow = await DB_SERVICE.get_workflow(workflow_run_id)
        if not workflow:
            raise ValueError(f"Workflow run ID '{workflow_run_id}' not found.")

        current_status = WorkflowStatus(workflow.status)
        last_completed_step = WorkflowStep(workflow.current_step) if workflow.current_step else None
        logger.info(f"[{workflow_run_id}] Loaded state: Status={current_status.value}, Last Completed Step={last_completed_step.value if last_completed_step else 'None'}")

        # --- Determine Next Step ---
        next_step: Optional[WorkflowStep] = None
        if current_status == WorkflowStatus.STARTING:
            next_step = WorkflowStep.MARKET_RESEARCH
        elif current_status == WorkflowStatus.APPROVED_RESUMING: # Resuming after approval
            next_step = WorkflowStep.IMPROVEMENT
        elif current_status == WorkflowStatus.COMPLETED_IMPROVEMENT:
            next_step = WorkflowStep.BRANDING
        elif current_status == WorkflowStatus.COMPLETED_BRANDING:
            next_step = WorkflowStep.CODE_GENERATION
        elif current_status == WorkflowStatus.COMPLETED_CODE_GENERATION:
            next_step = WorkflowStep.DEPLOYMENT
        elif current_status == WorkflowStatus.COMPLETED_DEPLOYMENT:
            next_step = WorkflowStep.MARKETING
        elif current_status == WorkflowStatus.COMPLETED_MARKETING:
             next_step = None # Workflow finished previously
             current_status = WorkflowStatus.COMPLETED
        elif current_status in [WorkflowStatus.COMPLETED, WorkflowStatus.FAILED, WorkflowStatus.STOPPED_LOW_POTENTIAL, WorkflowStatus.PENDING_APPROVAL]:
            logger.info(f"[{workflow_run_id}] Workflow is in a terminal or paused state ({current_status.value}). No action taken by _execute_workflow_step.")
            return # Nothing more to do
        else:
            # Should not happen if state transitions are correct
            raise RuntimeError(f"Workflow in unexpected status for step execution: {current_status.value}")

        if not next_step:
             logger.info(f"[{workflow_run_id}] No further steps to execute (Current Status: {current_status.value}).")
             # Ensure final status is saved if it reached COMPLETED_MARKETING
             if current_status == WorkflowStatus.COMPLETED:
                  await _update_workflow_state(workflow_run_id, {"status": WorkflowStatus.COMPLETED.value, "current_step": WorkflowStep.MARKETING.value})
             return

        current_step = next_step # Set current step for error handling
        step_config = WORKFLOW_STEPS_CONFIG[current_step]
        target_agent_id = step_config["agent_id"]
        target_tool_name = step_config["tool_name"] # Assuming one primary tool per agent step for now
        agent_name_for_error = target_agent_id # Update for specific agent errors

        logger.info(f"\n[{workflow_run_id}] --- Running Step: {current_step.value} (Agent: {target_agent_id}, Tool: {target_tool_name}) ---")
        await _update_workflow_state(workflow_run_id, {"status": f"RUNNING_{current_step.name}", "current_step": current_step.value})

        # 2. Prepare Input Payload for the Target Tool
        payload = {}
        if current_step == WorkflowStep.MARKET_RESEARCH:
            payload = {"initial_topic": workflow.initial_topic, "target_url": workflow.target_url}
        elif current_step == WorkflowStep.IMPROVEMENT:
            if not workflow.market_research_result: raise ValueError("Market research result missing.")
            # Map MarketOpportunityReport fields to ImprovementAgentInput fields
            payload = {
                "product_concept": workflow.initial_topic, # Start with initial topic
                "competitor_weaknesses": workflow.market_research_result.get('analysis', {}).get('competitor_weaknesses', []),
                "market_gaps": workflow.market_research_result.get('analysis', {}).get('market_gaps', []),
                "target_audience_suggestions": workflow.market_research_result.get('target_audience_suggestions', []),
                "feature_recommendations_from_market": workflow.market_research_result.get('feature_recommendations', [])
                # business_model_type could be added if needed
            }
        elif current_step == WorkflowStep.BRANDING:
            if not workflow.product_spec_data: raise ValueError("Improvement result (product spec) missing.")
            payload = {
                "product_concept": workflow.product_spec_data.get('product_concept', workflow.initial_topic),
                "target_audience": workflow.product_spec_data.get('target_audience', [])
                # keywords, business_model_type could be added
            }
        elif current_step == WorkflowStep.CODE_GENERATION:
             if not workflow.product_spec_data or not workflow.brand_package_data: raise ValueError("Product spec or brand package missing.")
             # Pass the full structures
             payload = {"product_spec": workflow.product_spec_data, "brand_package": workflow.brand_package_data}
        elif current_step == WorkflowStep.DEPLOYMENT:
             if not workflow.brand_package_data or not workflow.code_generation_result or not workflow.product_spec_data:
                 raise ValueError("Brand package, code generation result, or product spec missing.")
             payload = {
                 "brand_name": workflow.brand_package_data.get('brand_name', 'Unnamed Brand'),
                 "product_concept": workflow.product_spec_data.get('product_concept', workflow.initial_topic),
                 "key_features": workflow.product_spec_data.get('key_features', []),
                 "generated_code_dict": workflow.code_generation_result.get('generated_code_dict')
             }
             if not payload["generated_code_dict"]: raise ValueError("Generated code dictionary missing in code generation result.")
        elif current_step == WorkflowStep.MARKETING:
             if not workflow.product_spec_data or not workflow.brand_package_data or not workflow.deployment_result:
                 raise ValueError("Product spec, brand package, or deployment result missing.")
             payload = {
                 "product_spec": workflow.product_spec_data,
                 "brand_package": workflow.brand_package_data,
                 "deployment_url": workflow.deployment_result.get('deployment_url')
             }

        # 3. Invoke Target Agent Tool via ADK
        input_event = Event(data=payload)
        logger.debug(f"[{workflow_run_id}] Invoking agent '{target_agent_id}' with payload: {json.dumps(payload, default=str)[:500]}...") # Log truncated payload

        response_event = await context.invoke_agent(
            target_agent_id=target_agent_id,
            input=input_event,
            timeout_seconds=settings.AGENT_TIMEOUT_SECONDS * 2 # Allow longer timeout for complex steps
        )

        # 4. Process Result
        result_data = None
        step_succeeded = False
        error_details = f"Agent '{target_agent_id}' did not return a valid response."

        if response_event and response_event.actions:
             action = response_event.actions[0]
             part_data = None
             # Try extracting from content parts first
             if action.content and action.content.parts:
                 part_data = action.content.parts[0].data
             # Fallback to action parts
             elif action.parts:
                 part_data = action.parts[0].data

             if isinstance(part_data, dict):
                 result_data = part_data # Store the entire result dict
                 if result_data.get("success"):
                     step_succeeded = True
                     error_details = None # Clear error on success
                     logger.info(f"[{workflow_run_id}] Step {current_step.value} successful.")
                 else:
                     error_details = result_data.get("error", f"Agent '{target_agent_id}' reported failure.")
                     logger.error(f"[{workflow_run_id}] Step {current_step.value} failed: {error_details}")
             else:
                 # Handle cases where the tool might return non-dict data unexpectedly
                 error_details = f"Agent '{target_agent_id}' returned unexpected data type: {type(part_data)}"
                 logger.error(f"[{workflow_run_id}] Step {current_step.value} failed: {error_details}")
                 result_data = {"raw_output": str(part_data)} # Store raw output on error

        else:
            logger.error(f"[{workflow_run_id}] Step {current_step.value} failed: No valid response event actions from '{target_agent_id}'. Response: {response_event}")
            error_details = f"No valid response event from '{target_agent_id}'."
            # result_data remains None

        # 5. Update State and Handle Next Action
        if step_succeeded and result_data:
            next_status = None
            db_update_payload = {"current_step": current_step.value} # Always update the completed step

            # Store result in the correct DB field based on the step
            if current_step == WorkflowStep.MARKET_RESEARCH:
                db_update_payload["market_research_result"] = result_data.get("report") # Store the 'report' part
                next_status = WorkflowStatus.PENDING_APPROVAL
            elif current_step == WorkflowStep.IMPROVEMENT:
                db_update_payload["product_spec_data"] = result_data.get("improved_spec") # Store the 'improved_spec' part
                # Feasibility Check
                potential = result_data.get("improved_spec", {}).get("potential_rating", "Low").capitalize()
                score = result_data.get("improved_spec", {}).get("feasibility_score")
                rationale = result_data.get("improved_spec", {}).get("assessment_rationale", "N/A")
                if potential in ['Medium', 'High'] or (isinstance(score, (int, float)) and score >= 0.6):
                    logger.info(f"[{workflow_run_id}] Feasibility check passed (Potential: {potential}, Score: {score}).")
                    next_status = WorkflowStatus.COMPLETED_IMPROVEMENT
                else:
                    logger.warning(f"[{workflow_run_id}] Feasibility check failed (Potential: {potential}, Score: {score}). Stopping workflow.")
                    next_status = WorkflowStatus.STOPPED_LOW_POTENTIAL
                    db_update_payload["error_message"] = f"Workflow stopped due to low potential/feasibility. Rating: {potential}, Score: {score}. Rationale: {rationale}"
            elif current_step == WorkflowStep.BRANDING:
                db_update_payload["brand_package_data"] = result_data.get("brand_package") # Store the 'brand_package' part
                next_status = WorkflowStatus.COMPLETED_BRANDING
            elif current_step == WorkflowStep.CODE_GENERATION:
                 db_update_payload["code_generation_result"] = result_data # Store the whole result dict including 'generated_code_dict'
                 next_status = WorkflowStatus.COMPLETED_CODE_GENERATION
            elif current_step == WorkflowStep.DEPLOYMENT:
                 db_update_payload["deployment_result"] = result_data # Store the whole result dict
                 next_status = WorkflowStatus.COMPLETED_DEPLOYMENT
            elif current_step == WorkflowStep.MARKETING:
                 db_update_payload["marketing_result"] = result_data.get("marketing_materials") # Store the 'marketing_materials' part
                 next_status = WorkflowStatus.COMPLETED_MARKETING # Penultimate step
                 # This will lead to the final COMPLETED state check

            if next_status:
                db_update_payload["status"] = next_status.value
                await _update_workflow_state(workflow_run_id, db_update_payload)

                # If workflow is not in a terminal/paused state, trigger the next step
                if next_status not in [WorkflowStatus.COMPLETED, WorkflowStatus.FAILED, WorkflowStatus.STOPPED_LOW_POTENTIAL, WorkflowStatus.PENDING_APPROVAL]:
                    logger.info(f"[{workflow_run_id}] Step {current_step.value} successful. Triggering next step.")
                    asyncio.create_task(_execute_workflow_step(context, workflow_run_id))
                elif next_status == WorkflowStatus.PENDING_APPROVAL:
                     logger.info(f"[{workflow_run_id}] Workflow paused for approval after {current_step.value}.")
                     # SocketIO emit happens in _update_workflow_state
                elif next_status == WorkflowStatus.COMPLETED_MARKETING:
                     logger.info(f"[{workflow_run_id}] Marketing step complete. Finalizing workflow.")
                     # Trigger one last execution to transition to COMPLETED
                     asyncio.create_task(_execute_workflow_step(context, workflow_run_id))
                else:
                     logger.info(f"[{workflow_run_id}] Workflow reached terminal state: {next_status.value}")
                     # SocketIO emit happens in _update_workflow_state if status changed

            else:
                 # Should not happen if logic is correct
                 raise RuntimeError(f"Could not determine next status after successful step {current_step.value}")

        else:
            # Handle step failure
            await _handle_step_failure(workflow_run_id, current_step, error_details or "Unknown error", agent_name_for_error)

    except Exception as e:
        # Catch errors during state loading or step execution logic itself
        error_msg = f"Workflow execution error at step '{current_step.value if current_step else 'UNKNOWN'}': {type(e).__name__}: {e}"
        logger.critical(f"[{workflow_run_id}] CRITICAL ERROR: {error_msg}", exc_info=True)
        # Ensure state is marked as FAILED
        await _update_workflow_state(workflow_run_id, {
            "status": WorkflowStatus.FAILED.value,
            "current_step": current_step.value if current_step else None,
            "error_message": error_msg
        })
        # SocketIO emit happens within _update_workflow_state

# --- ADK Tool Definitions ---

@tool(description="Start a new multi-agent workflow to research, design, build, deploy, and market a product based on an initial topic.")
async def start_workflow_tool(context: ToolContext, initial_topic: str, target_url: Optional[str] = None) -> Dict[str, Any]:
    """
    ADK Tool: Start a new workflow.
    """
    logger.info(f"Tool: Starting new workflow for topic: {initial_topic}")
    workflow_run_id = f"wf_{uuid.uuid4().hex[:8]}" # Shorter ID
    try:
        # Create workflow in database
        await DB_SERVICE.create_workflow(
            workflow_id=workflow_run_id,
            initial_topic=initial_topic,
            target_url=target_url,
            status=WorkflowStatus.STARTING.value
        )
        logger.info(f"[{workflow_run_id}] Workflow created in database.")

        # Start the workflow execution in the background
        # Pass the ToolContext so the background task can invoke other agents
        asyncio.create_task(_execute_workflow_step(context, workflow_run_id))

        return {
            "success": True,
            "message": f"Workflow started successfully.",
            "workflow_run_id": workflow_run_id,
            "status": WorkflowStatus.STARTING.value
        }
    except Exception as e:
        logger.error(f"Tool: Error starting workflow: {e}", exc_info=True)
        return {"success": False, "error": f"Error starting workflow: {str(e)}"}

@tool(description="Get the current status and stored data for a specific workflow run.")
async def get_workflow_status_tool(workflow_run_id: str) -> Dict[str, Any]:
    """
    ADK Tool: Get the status of a workflow.
    """
    logger.info(f"Tool: Getting status for workflow: {workflow_run_id}")
    try:
        workflow = await DB_SERVICE.get_workflow(workflow_run_id)
        if not workflow:
            return {"success": False, "error": f"Workflow '{workflow_run_id}' not found."}

        # Return relevant fields from the workflow model
        return {
            "success": True,
            "workflow_run_id": workflow.id,
            "status": workflow.status,
            "current_step": workflow.current_step,
            "error_message": workflow.error_message,
            "initial_topic": workflow.initial_topic,
            "target_url": workflow.target_url,
            "created_at": workflow.created_at.isoformat() if workflow.created_at else None,
            "last_updated": workflow.last_updated.isoformat() if workflow.last_updated else None,
            # Optionally include results if needed, be mindful of size
            # "market_research_result": workflow.market_research_result,
            # "improvement_result": workflow.product_spec_data,
            # ...
        }
    except Exception as e:
        logger.error(f"Tool: Error getting workflow status for {workflow_run_id}: {e}", exc_info=True)
        return {"success": False, "error": f"Error getting workflow status: {str(e)}"}

@tool(description="Resume a workflow that is paused waiting for user approval (status PENDING_APPROVAL).")
async def resume_workflow_tool(context: ToolContext, workflow_run_id: str) -> Dict[str, Any]:
    """
    ADK Tool: Resume a paused workflow after user approval.
    """
    logger.info(f"Tool: Attempting to resume workflow: {workflow_run_id}")
    try:
        workflow = await DB_SERVICE.get_workflow(workflow_run_id)
        if not workflow:
            return {"success": False, "error": f"Workflow '{workflow_run_id}' not found."}

        if workflow.status != WorkflowStatus.PENDING_APPROVAL.value:
            return {"success": False, "error": f"Workflow not in PENDING_APPROVAL state (Current: {workflow.status}). Cannot resume."}

        # Update status to trigger resumption
        await _update_workflow_state(workflow_run_id, {"status": WorkflowStatus.APPROVED_RESUMING.value})

        # Trigger the next step execution in the background
        asyncio.create_task(_execute_workflow_step(context, workflow_run_id))

        return {
            "success": True,
            "message": f"Workflow {workflow_run_id} resumption triggered.",
            "workflow_run_id": workflow_run_id,
            "status": WorkflowStatus.APPROVED_RESUMING.value
        }
    except Exception as e:
        logger.error(f"Tool: Error resuming workflow {workflow_run_id}: {e}", exc_info=True)
        return {"success": False, "error": f"Error resuming workflow: {str(e)}"}


# --- Instantiate the ADK Agent ---
agent = Agent(
    name=AGENT_ID,
    description="Orchestrates the multi-agent workflow (Market Research -> Improvement -> Branding -> Code Gen -> Deploy -> Marketing) using ADK tools and database state.",
    tools=[
        start_workflow_tool,
        get_workflow_status_tool,
        resume_workflow_tool,
    ],
)

# Removed A2A server specific code and old class structure
