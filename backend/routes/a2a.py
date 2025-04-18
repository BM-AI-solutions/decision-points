import logging
from flask import Blueprint, request, jsonify, current_app
from google.adk.runtime import InvocationContext, Event
from backend.agents.code_generation_agent import CodeGenerationAgent
# Firestore and SocketIO are accessed via current_app, specific imports might not be needed here
# but ensure they are initialized in app.py

# Configure logging
logger = logging.getLogger(__name__)

a2a_bp = Blueprint('a2a', __name__, url_prefix='/a2a')

@a2a_bp.route('/market_research/invoke', methods=['POST'])
async def invoke_market_research():
    """
    Endpoint for invoking the MarketResearchAgent via A2A communication.
    Expects a JSON payload representing the InvocationContext.
    Returns the resulting Event serialized as JSON.
    """
    logger.info("Received A2A request for MarketResearchAgent invocation.")
    try:
        context_data = request.get_json()
        if not context_data:
            logger.warning("A2A request received with empty payload.")
            return jsonify({"error": "Request body must contain JSON data."}), 400

        logger.debug(f"Received context data: {context_data}")

        # Deserialize the context
        try:
            context = InvocationContext(**context_data)
            logger.info("Successfully deserialized InvocationContext.")
        except Exception as e:
            logger.error(f"Error deserializing InvocationContext: {e}", exc_info=True)
            return jsonify({"error": f"Invalid InvocationContext format: {e}"}), 400

        # Get the agent instance
        try:
            agent = current_app.market_research_agent
            if agent is None:
                 logger.error("MarketResearchAgent not found in current_app context.")
                 return jsonify({"error": "MarketResearchAgent not configured."}), 500
            logger.info("Retrieved MarketResearchAgent instance.")
        except AttributeError:
             logger.error("market_research_agent attribute not found on current_app.", exc_info=True)
             return jsonify({"error": "MarketResearchAgent not available."}), 500


        # Invoke the agent
        try:
            logger.info(f"Invoking MarketResearchAgent with context ID: {context.invocation_id}")
            result_event: Event = await agent.run_async(context)
            logger.info(f"MarketResearchAgent invocation completed successfully. Result Event ID: {result_event.event_id}")

            # Serialize the result event
            # Assuming Event has a .model_dump() method (like Pydantic models)
            try:
                response_data = result_event.model_dump(mode='json') # Use mode='json' for better serialization
                logger.debug(f"Serialized result event: {response_data}")
            except AttributeError:
                 logger.error("Result event object does not have model_dump method. Manual serialization needed.")
                 # Fallback manual serialization (adjust based on actual Event structure)
                 response_data = {
                     "event_id": str(result_event.event_id),
                     "event_type": result_event.event_type,
                     "data": result_event.data,
                     "metadata": result_event.metadata,
                     # Add other relevant fields from the Event object
                 }
            except Exception as e:
                logger.error(f"Error serializing result event: {e}", exc_info=True)
                return jsonify({"error": f"Could not serialize result event: {e}"}), 500


            return jsonify(response_data), 200

        except Exception as e:
            logger.error(f"Error during MarketResearchAgent invocation: {e}", exc_info=True)
            return jsonify({"error": f"Agent invocation failed: {e}"}), 500

    except Exception as e:
        logger.exception("An unexpected error occurred in the A2A market research endpoint.")
        return jsonify({"error": f"An unexpected server error occurred: {e}"}), 500


@a2a_bp.route('/improvement/invoke', methods=['POST'])
async def invoke_improvement_agent():
    """
    Endpoint for invoking the ImprovementAgent via A2A communication.
    Expects a JSON payload representing the InvocationContext.
    Returns the resulting Event serialized as JSON.
    """
    logger.info("Received A2A request for ImprovementAgent invocation.")
    try:
        context_data = request.get_json()
        if not context_data:
            logger.warning("A2A request received with empty payload for ImprovementAgent.")
            return jsonify({"error": "Request body must contain JSON data."}), 400

        logger.debug(f"Received context data for ImprovementAgent: {context_data}")

        # Deserialize the context
        try:
            context = InvocationContext(**context_data)
            logger.info("Successfully deserialized InvocationContext for ImprovementAgent.")
        except Exception as e:
            logger.error(f"Error deserializing InvocationContext for ImprovementAgent: {e}", exc_info=True)
            return jsonify({"error": f"Invalid InvocationContext format: {e}"}), 400

        # Get the agent instance
        try:
            agent = current_app.improvement_agent
            if agent is None:
                 logger.error("ImprovementAgent not found in current_app context.")
                 return jsonify({"error": "ImprovementAgent not configured."}), 500
            logger.info("Retrieved ImprovementAgent instance.")
        except AttributeError:
             logger.error("improvement_agent attribute not found on current_app.", exc_info=True)
             return jsonify({"error": "ImprovementAgent not available."}), 500


        # Invoke the agent
        try:
            logger.info(f"Invoking ImprovementAgent with context ID: {context.invocation_id}")
            result_event: Event = await agent.run_async(context)
            logger.info(f"ImprovementAgent invocation completed successfully. Result Event ID: {result_event.event_id}")

            # Serialize the result event
            try:
                # Assuming Event has a .model_dump() method (like Pydantic models)
                response_data = result_event.model_dump(mode='json') # Use mode='json' for better serialization
                logger.debug(f"Serialized result event from ImprovementAgent: {response_data}")
            except AttributeError:
                 logger.error("Result event object from ImprovementAgent does not have model_dump method. Manual serialization needed.")
                 # Fallback manual serialization (adjust based on actual Event structure)
                 response_data = {
                     "event_id": str(result_event.event_id),
                     "event_type": result_event.event_type,
                     "data": result_event.data,
                     "metadata": result_event.metadata,
                     # Add other relevant fields from the Event object
                 }
            except Exception as e:
                logger.error(f"Error serializing result event from ImprovementAgent: {e}", exc_info=True)
                return jsonify({"error": f"Could not serialize result event: {e}"}), 500


            return jsonify(response_data), 200

        except Exception as e:
            logger.error(f"Error during ImprovementAgent invocation: {e}", exc_info=True)
            return jsonify({"error": f"Agent invocation failed: {e}"}), 500

    except Exception as e:
        logger.exception("An unexpected error occurred in the A2A improvement agent endpoint.")
        return jsonify({"error": f"An unexpected server error occurred: {e}"}), 500


@a2a_bp.route('/branding/invoke', methods=['POST'])
async def invoke_branding_agent():
    """
    Endpoint for invoking the BrandingAgent via A2A communication.
    Expects a JSON payload representing the InvocationContext.
    Returns the resulting Event serialized as JSON.
    """
    logger.info("Received A2A request for BrandingAgent invocation.")
    try:
        context_data = request.get_json()
        if not context_data:
            logger.warning("A2A request received with empty payload for BrandingAgent.")
            return jsonify({"error": "Request body must contain JSON data."}), 400

        logger.debug(f"Received context data for BrandingAgent: {context_data}")

        # Deserialize the context
        try:
            context = InvocationContext(**context_data)
            logger.info("Successfully deserialized InvocationContext for BrandingAgent.")
        except Exception as e:
            logger.error(f"Error deserializing InvocationContext for BrandingAgent: {e}", exc_info=True)
            return jsonify({"error": f"Invalid InvocationContext format: {e}"}), 400

        # Get the agent instance
        try:
            agent = current_app.branding_agent
            if agent is None:
                 logger.error("BrandingAgent not found in current_app context.")
                 return jsonify({"error": "BrandingAgent not configured."}), 500
            logger.info("Retrieved BrandingAgent instance.")
        except AttributeError:
             logger.error("branding_agent attribute not found on current_app.", exc_info=True)
             return jsonify({"error": "BrandingAgent not available."}), 500


        # Invoke the agent
        try:
            logger.info(f"Invoking BrandingAgent with context ID: {context.invocation_id}")
            result_event: Event = await agent.run_async(context)
            logger.info(f"BrandingAgent invocation completed successfully. Result Event ID: {result_event.event_id}")

            # Serialize the result event
            try:
                # Assuming Event has a .model_dump() method (like Pydantic models)
                response_data = result_event.model_dump(mode='json') # Use mode='json' for better serialization
                logger.debug(f"Serialized result event from BrandingAgent: {response_data}")
            except AttributeError:
                 logger.error("Result event object from BrandingAgent does not have model_dump method. Manual serialization needed.")
                 # Fallback manual serialization (adjust based on actual Event structure)
                 response_data = {
                     "event_id": str(result_event.event_id),
                     "event_type": result_event.event_type,
                     "data": result_event.data,
                     "metadata": result_event.metadata,
                     # Add other relevant fields from the Event object
                 }
            except Exception as e:
                logger.error(f"Error serializing result event from BrandingAgent: {e}", exc_info=True)
                return jsonify({"error": f"Could not serialize result event: {e}"}), 500


            return jsonify(response_data), 200

        except Exception as e:
            logger.error(f"Error during BrandingAgent invocation: {e}", exc_info=True)
            return jsonify({"error": f"Agent invocation failed: {e}"}), 500

    except Exception as e:
        logger.exception("An unexpected error occurred in the A2A branding agent endpoint.")
        return jsonify({"error": f"An unexpected server error occurred: {e}"}), 500



@a2a_bp.route('/deployment/invoke', methods=['POST'])
async def invoke_deployment_agent():
    """
    Endpoint for invoking the DeploymentAgent via A2A communication.
    Expects a JSON payload representing the InvocationContext.
    Returns the resulting Event serialized as JSON.
    """
    logger.info("Received A2A request for DeploymentAgent invocation.")
    try:
        context_data = request.get_json()
        if not context_data:
            logger.warning("A2A request received with empty payload for DeploymentAgent.")
            return jsonify({"error": "Request body must contain JSON data."}), 400

        logger.debug(f"Received context data for DeploymentAgent: {context_data}")

        # Deserialize the context
        try:
            context = InvocationContext(**context_data)
            logger.info("Successfully deserialized InvocationContext for DeploymentAgent.")
        except Exception as e:
            logger.error(f"Error deserializing InvocationContext for DeploymentAgent: {e}", exc_info=True)
            return jsonify({"error": f"Invalid InvocationContext format: {e}"}), 400

        # Get the agent instance
        try:
            agent = current_app.deployment_agent # Changed agent name
            if agent is None:
                 logger.error("DeploymentAgent not found in current_app context.")
                 return jsonify({"error": "DeploymentAgent not configured."}), 500
            logger.info("Retrieved DeploymentAgent instance.")
        except AttributeError:
             logger.error("deployment_agent attribute not found on current_app.", exc_info=True) # Changed agent name
             return jsonify({"error": "DeploymentAgent not available."}), 500


        # Invoke the agent
        try:
            logger.info(f"Invoking DeploymentAgent with context ID: {context.invocation_id}")
            result_event: Event = await agent.run_async(context)
            logger.info(f"DeploymentAgent invocation completed successfully. Result Event ID: {result_event.event_id}")

            # Serialize the result event
            try:
                # Assuming Event has a .model_dump() method (like Pydantic models)
                response_data = result_event.model_dump(mode='json') # Use mode='json' for better serialization
                logger.debug(f"Serialized result event from DeploymentAgent: {response_data}")
            except AttributeError:
                 logger.error("Result event object from DeploymentAgent does not have model_dump method. Manual serialization needed.")
                 # Fallback manual serialization (adjust based on actual Event structure)
                 response_data = {
                     "event_id": str(result_event.event_id),
                     "event_type": result_event.event_type,
                     "data": result_event.data,
                     "metadata": result_event.metadata,
                     # Add other relevant fields from the Event object
                 }
            except Exception as e:
                logger.error(f"Error serializing result event from DeploymentAgent: {e}", exc_info=True)
                return jsonify({"error": f"Could not serialize result event: {e}"}), 500


            return jsonify(response_data), 200

        except Exception as e:
            logger.error(f"Error during DeploymentAgent invocation: {e}", exc_info=True)
            return jsonify({"error": f"Agent invocation failed: {e}"}), 500

    except Exception as e:
        logger.exception("An unexpected error occurred in the A2A deployment agent endpoint.")
        return jsonify({"error": f"An unexpected server error occurred: {e}"}), 500




@a2a_bp.route('/content_generation/invoke', methods=['POST'])
async def invoke_content_generation_agent():
    """
    Endpoint for invoking the ContentGenerationAgent via A2A communication.
    Expects a JSON payload representing the InvocationContext.
    Returns the resulting Event serialized as JSON.
    """
    logger.info("Received A2A request for ContentGenerationAgent invocation.")
    try:
        context_data = request.get_json()
        if not context_data:
            logger.warning("A2A request received with empty payload for ContentGenerationAgent.")
            return jsonify({"error": "Request body must contain JSON data."}), 400

        logger.debug(f"Received context data for ContentGenerationAgent: {context_data}")

        # Deserialize the context
        try:
            context = InvocationContext(**context_data)
            logger.info("Successfully deserialized InvocationContext for ContentGenerationAgent.")
        except Exception as e:
            logger.error(f"Error deserializing InvocationContext for ContentGenerationAgent: {e}", exc_info=True)
            return jsonify({"error": f"Invalid InvocationContext format: {e}"}), 400

        # Get the agent instance
        try:
            agent = current_app.content_generation_agent # Changed agent name
            if agent is None:
                 logger.error("ContentGenerationAgent not found in current_app context.")
                 return jsonify({"error": "ContentGenerationAgent not configured."}), 500
            logger.info("Retrieved ContentGenerationAgent instance.")
        except AttributeError:
             logger.error("content_generation_agent attribute not found on current_app.", exc_info=True) # Changed agent name
             return jsonify({"error": "ContentGenerationAgent not available."}), 500


        # Invoke the agent
        try:
            logger.info(f"Invoking ContentGenerationAgent with context ID: {context.invocation_id}")
            result_event: Event = await agent.run_async(context)
            logger.info(f"ContentGenerationAgent invocation completed successfully. Result Event ID: {result_event.event_id}")

            # Serialize the result event
            try:
                # Assuming Event has a .model_dump() method (like Pydantic models)
                response_data = result_event.model_dump(mode='json') # Use mode='json' for better serialization
                logger.debug(f"Serialized result event from ContentGenerationAgent: {response_data}")
            except AttributeError:
                 logger.error("Result event object from ContentGenerationAgent does not have model_dump method. Manual serialization needed.")
                 # Fallback manual serialization (adjust based on actual Event structure)
                 response_data = {
                     "event_id": str(result_event.event_id),
                     "event_type": result_event.event_type,
                     "data": result_event.data,
                     "metadata": result_event.metadata,
                     # Add other relevant fields from the Event object
                 }
            except Exception as e:
                logger.error(f"Error serializing result event from ContentGenerationAgent: {e}", exc_info=True)
                return jsonify({"error": f"Could not serialize result event: {e}"}), 500


            return jsonify(response_data), 200

        except Exception as e:
            logger.error(f"Error during ContentGenerationAgent invocation: {e}", exc_info=True)
            return jsonify({"error": f"Agent invocation failed: {e}"}), 500

    except Exception as e:
        logger.exception("An unexpected error occurred in the A2A content generation agent endpoint.")
        return jsonify({"error": f"An unexpected server error occurred: {e}"}), 500



@a2a_bp.route('/code_generation/invoke', methods=['POST'])
async def invoke_code_generation_agent():
    """
    Endpoint for invoking the CodeGenerationAgent via A2A communication.
    Expects a JSON payload representing the InvocationContext.
    Returns the resulting Event serialized as JSON.
    """
    logger.info("Received A2A request for CodeGenerationAgent invocation.")
    try:
        context_data = request.get_json()
        if not context_data:
            logger.warning("A2A request received with empty payload for CodeGenerationAgent.")
            return jsonify({"error": "Request body must contain JSON data."}), 400

        logger.debug(f"Received context data for CodeGenerationAgent: {context_data}")

        # Deserialize the context
        try:
            context = InvocationContext(**context_data)
            logger.info("Successfully deserialized InvocationContext for CodeGenerationAgent.")
        except Exception as e:
            logger.error(f"Error deserializing InvocationContext for CodeGenerationAgent: {e}", exc_info=True)
            return jsonify({"error": f"Invalid InvocationContext format: {e}"}), 400

        # Get the agent instance
        try:
            agent = current_app.code_generation_agent # Agent name specific to this endpoint
            if agent is None:
                 logger.error("CodeGenerationAgent not found in current_app context.")
                 return jsonify({"error": "CodeGenerationAgent not configured."}), 500
            logger.info("Retrieved CodeGenerationAgent instance.")
        except AttributeError:
             logger.error("code_generation_agent attribute not found on current_app.", exc_info=True) # Agent name specific to this endpoint
             return jsonify({"error": "CodeGenerationAgent not available."}), 500


        # Invoke the agent
        try:
            logger.info(f"Invoking CodeGenerationAgent with context ID: {context.invocation_id}")
            result_event: Event = await agent.run_async(context)
            logger.info(f"CodeGenerationAgent invocation completed successfully. Result Event ID: {result_event.event_id}")

            # Serialize the result event
            try:
                # Assuming Event has a .model_dump() method (like Pydantic models)
                response_data = result_event.model_dump(mode='json') # Use mode='json' for better serialization
                logger.debug(f"Serialized result event from CodeGenerationAgent: {response_data}")
            except AttributeError:
                 logger.error("Result event object from CodeGenerationAgent does not have model_dump method. Manual serialization needed.")
                 # Fallback manual serialization (adjust based on actual Event structure)
                 response_data = {
                     "event_id": str(result_event.event_id),
                     "event_type": result_event.event_type,
                     "data": result_event.data,
                     "metadata": result_event.metadata,
                     # Add other relevant fields from the Event object
                 }
            except Exception as e:
                logger.error(f"Error serializing result event from CodeGenerationAgent: {e}", exc_info=True)
                return jsonify({"error": f"Could not serialize result event: {e}"}), 500


            return jsonify(response_data), 200

        except Exception as e:
            logger.error(f"Error during CodeGenerationAgent invocation: {e}", exc_info=True)
            return jsonify({"error": f"Agent invocation failed: {e}"}), 500

    except Exception as e:
        logger.exception("An unexpected error occurred in the A2A code generation agent endpoint.")
        return jsonify({"error": f"An unexpected server error occurred: {e}"}), 500



@a2a_bp.route('/marketing/invoke', methods=['POST'])
async def invoke_marketing_agent():
    """
    Endpoint for invoking the MarketingAgent via A2A communication.
    Expects a JSON payload representing the InvocationContext.
    Returns the resulting Event serialized as JSON.
    """
    logger.info("Received A2A request for MarketingAgent invocation.")
    try:
        context_data = request.get_json()
        if not context_data:
            logger.warning("A2A request received with empty payload for MarketingAgent.")
            return jsonify({"error": "Request body must contain JSON data."}), 400

        logger.debug(f"Received context data for MarketingAgent: {context_data}")

        # Deserialize the context
        try:
            context = InvocationContext(**context_data)
            logger.info("Successfully deserialized InvocationContext for MarketingAgent.")
        except Exception as e:
            logger.error(f"Error deserializing InvocationContext for MarketingAgent: {e}", exc_info=True)
            return jsonify({"error": f"Invalid InvocationContext format: {e}"}), 400

        # Get the agent instance
        try:
            agent = current_app.marketing_agent # Agent name specific to this endpoint
            if agent is None:
                 logger.error("MarketingAgent not found in current_app context.")
                 return jsonify({"error": "MarketingAgent not configured."}), 500
            logger.info("Retrieved MarketingAgent instance.")
        except AttributeError:
             logger.error("marketing_agent attribute not found on current_app.", exc_info=True) # Agent name specific to this endpoint
             return jsonify({"error": "MarketingAgent not available."}), 500


        # Invoke the agent
        try:
            logger.info(f"Invoking MarketingAgent with context ID: {context.invocation_id}")
            result_event: Event = await agent.run_async(context)
            logger.info(f"MarketingAgent invocation completed successfully. Result Event ID: {result_event.event_id}")

            # Serialize the result event
            try:
                # Assuming Event has a .model_dump() method (like Pydantic models)
                response_data = result_event.model_dump(mode='json') # Use mode='json' for better serialization
                logger.debug(f"Serialized result event from MarketingAgent: {response_data}")
            except AttributeError:
                 logger.error("Result event object from MarketingAgent does not have model_dump method. Manual serialization needed.")
                 # Fallback manual serialization (adjust based on actual Event structure)
                 response_data = {
                     "event_id": str(result_event.event_id),
                     "event_type": result_event.event_type,
                     "data": result_event.data,
                     "metadata": result_event.metadata,
                     # Add other relevant fields from the Event object
                 }
            except Exception as e:
                logger.error(f"Error serializing result event from MarketingAgent: {e}", exc_info=True)
                return jsonify({"error": f"Could not serialize result event: {e}"}), 500


            return jsonify(response_data), 200

        except Exception as e:
            logger.error(f"Error during MarketingAgent invocation: {e}", exc_info=True)
            return jsonify({"error": f"Agent invocation failed: {e}"}), 500

    except Exception as e:
        logger.exception("An unexpected error occurred in the A2A marketing agent endpoint.")
        return jsonify({"error": f"An unexpected server error occurred: {e}"}), 500


@a2a_bp.route('/workflow/<string:workflow_run_id>/resume', methods=['POST'])
async def resume_workflow(workflow_run_id): # Make async
    """
    Endpoint for resuming or rejecting a paused workflow step.
    Expects a JSON payload with a 'decision' field ('approved' or 'rejected').
    Updates Firestore state and triggers agent resumption via SocketIO if approved.
    """
    logger.info(f"Received request to resume/reject workflow: {workflow_run_id}")
    try:
        # Get decision from request body
        data = request.get_json()
        if not data or 'decision' not in data:
            logger.warning(f"Missing 'decision' in request body for workflow {workflow_run_id}")
            return jsonify({"error": "Request body must contain a 'decision' field ('approved' or 'rejected')."}), 400

        decision = data.get('decision')
        logger.debug(f"Received decision '{decision}' for workflow {workflow_run_id}")

        # Get Firestore client and SocketIO instance from app context
        try:
            db = current_app.firestore_db
            socketio = current_app.socketio
            workflow_collection_name = current_app.config['WORKFLOW_COLLECTION']
            agent = current_app.workflow_manager_agent # Get agent instance
        except AttributeError as e:
             logger.error(f"App context missing required component (firestore_db, socketio, WORKFLOW_COLLECTION, or workflow_manager_agent): {e}", exc_info=True)
             return jsonify({"error": "Server configuration error."}), 500
        except KeyError as e:
            logger.error(f"App config missing required key 'WORKFLOW_COLLECTION': {e}", exc_info=True)
            return jsonify({"error": "Server configuration error (missing WORKFLOW_COLLECTION)."}), 500

        if not all([db, socketio, workflow_collection_name, agent]):
             logger.error("One or more required components (db, socketio, collection name, agent) are None.")
             return jsonify({"error": "Server configuration error (component not initialized)."}), 500


        # Get workflow document reference
        doc_ref = db.collection(workflow_collection_name).document(workflow_run_id)

        # Get the document snapshot
        try:
            doc = await doc_ref.get()
            if not doc.exists:
                logger.warning(f"Workflow document {workflow_run_id} not found in Firestore.")
                return jsonify({'error': f'Workflow {workflow_run_id} not found.'}), 404

            workflow_data = doc.to_dict()
            current_status = workflow_data.get('status')
            logger.debug(f"Current status for workflow {workflow_run_id}: {current_status}")

            # Check if the workflow is actually pending approval
            if current_status != 'pending_approval':
                logger.warning(f"Workflow {workflow_run_id} is not pending approval (status: {current_status}). Cannot resume/reject.")
                return jsonify({'error': f'Workflow is not pending approval (current status: {current_status}).'}), 409 # Conflict

        except Exception as e:
            logger.error(f"Error fetching workflow document {workflow_run_id} from Firestore: {e}", exc_info=True)
            return jsonify({"error": f"Failed to retrieve workflow state: {e}"}), 500


        # Process decision
        if decision == 'approved':
            try:
                logger.info(f"Approving workflow {workflow_run_id}. Updating Firestore status to 'approved_resuming'.")
                await doc_ref.update({'status': 'approved_resuming'})

                # Prepare context for agent resumption
                resume_context = InvocationContext(
                    invocation_id=f"resume-{workflow_run_id}",
                    data={'workflow_run_id': workflow_run_id, 'resume': True}
                )
                logger.info(f"Prepared resume context for agent: {resume_context.invocation_id}")

                # Asynchronously invoke the agent's run method
                logger.info(f"Starting background task to resume WorkflowManagerAgent for {workflow_run_id}")
                socketio.start_background_task(agent.run_async, resume_context)

                logger.info(f"Workflow {workflow_run_id} approved and agent resumption triggered.")
                return jsonify({'status': 'Workflow approved and resuming'})

            except Exception as e:
                logger.error(f"Error during approval process for workflow {workflow_run_id}: {e}", exc_info=True)
                # Attempt to revert status if update failed but context prepared? Or just log?
                # For now, just log and return error. Consider more robust error handling/rollback if needed.
                return jsonify({"error": f"Failed to process approval: {e}"}), 500

        elif decision == 'rejected':
            try:
                logger.info(f"Rejecting workflow {workflow_run_id}. Updating Firestore status to 'rejected'.")
                await doc_ref.update({'status': 'rejected'})

                # Optional: Emit SocketIO event for rejection notification
                # socketio.emit('workflow_rejected', {'workflow_run_id': workflow_run_id}, room=workflow_run_id) # Example room

                logger.info(f"Workflow {workflow_run_id} rejected and state updated in Firestore.")
                return jsonify({'status': 'Workflow rejected and stopped'})

            except Exception as e:
                logger.error(f"Error updating Firestore status to rejected for workflow {workflow_run_id}: {e}", exc_info=True)
                return jsonify({"error": f"Failed to update workflow status to rejected: {e}"}), 500

        else:
            logger.warning(f"Invalid decision '{decision}' received for workflow {workflow_run_id}")
            return jsonify({"error": "Invalid decision. Must be 'approved' or 'rejected'."}), 400

    except Exception as e:
        logger.exception(f"An unexpected error occurred processing resume/reject for workflow {workflow_run_id}.")
        return jsonify({"error": f"An unexpected server error occurred: {e}"}), 500

