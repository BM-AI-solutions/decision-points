import logging
from flask import Blueprint, request, jsonify, current_app
from google.adk.runtime import InvocationContext, Event

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

