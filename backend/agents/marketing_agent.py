import asyncio
import httpx
import logging
import os # Added for environment variables
import argparse # Added for server args
from typing import List, Dict, Any, Optional

import uvicorn # Added for server
from fastapi import FastAPI, HTTPException, Body # Added for server
from pydantic import BaseModel, Field # Added for server models

# Assuming ADK is installed
from google.adk.agents import Agent
from google.adk.runtime import InvocationContext
from google.adk.runtime.events import Event, EventSeverity # Use EventSeverity


# Configure logging
# Use logfire if configured globally, otherwise standard logging
try:
    import logfire
    logger = logfire
except ImportError:
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO"))

# --- Pydantic Models ---

# Input models based on what run_async expects
class ImprovedProductSpecInput(BaseModel):
    """Represents the improved product specification input."""
    product_name: str = Field(description="Name of the product.")
    description: str = Field(description="Detailed description of the product.")
    target_audience: str = Field(description="The intended audience for the product.")
    key_features: List[str] = Field(description="List of key product features.")
    unique_selling_points: List[str] = Field(description="Unique aspects differentiating the product.")

class BrandingPackageInput(BaseModel):
    """Represents the branding guidelines and assets input."""
    brand_name: str = Field(description="The brand name.")
    tone_of_voice: str = Field(description="Desired tone for marketing communications (e.g., formal, playful).")
    keywords: List[str] = Field(description="Relevant keywords for the brand/product.")
    logo_description: Optional[str] = Field(None, description="Description of the brand logo.")

class MarketingAgentInput(BaseModel):
    """Input model for the /invoke endpoint."""
    product_spec: ImprovedProductSpecInput = Field(description="The improved product specification.")
    branding_package: BrandingPackageInput = Field(description="The branding package.")

# Output model
class MarketingMaterialsPackage(BaseModel):
    """Structured output containing generated marketing materials."""
    social_media_posts: List[str] = Field(description="Generated social media posts.")
    ad_copies: List[str] = Field(description="Generated short advertisement copies.")
    email_announcements: List[str] = Field(description="Generated brief email announcements.")

class MarketingAgentErrorOutput(BaseModel):
    """Output model for the /invoke endpoint on failure."""
    error: str
    details: Optional[Any] = None


# --- Marketing Agent ---

class MarketingAgent(Agent):
    """
    Generates various marketing copy snippets by leveraging the ContentGenerationAgent via A2A.
    """
    ENV_CONTENT_GENERATION_AGENT_URL = "CONTENT_GENERATION_AGENT_URL"

    def __init__(self, agent_id: str = "marketing-agent"):
        """
        Initializes the MarketingAgent.
        Retrieves the ContentGenerationAgent URL from environment variables.
        """
        super().__init__(agent_id=agent_id) # Pass agent_id
        # Get agent URL from environment variable
        self.content_generation_agent_url = os.environ.get(self.ENV_CONTENT_GENERATION_AGENT_URL)
        if not self.content_generation_agent_url:
            logger.error(f"{self.ENV_CONTENT_GENERATION_AGENT_URL} not configured.")
            raise ValueError(f"{self.ENV_CONTENT_GENERATION_AGENT_URL} must be configured")

        # Initialize httpx client for A2A calls
        self.http_client = httpx.AsyncClient(timeout=60.0) # Increased timeout for LLM calls

        logger.info(f"MarketingAgent ({self.agent_id}) initialized. ContentGenerationAgent URL: {self.content_generation_agent_url}")


    async def _call_content_generation_agent(self, prompt: str, request_key: str) -> tuple[str, Optional[str]]:
        """
        Calls the ContentGenerationAgent via A2A HTTP call and returns the generated content.
        """
        if not self.http_client or not self.content_generation_agent_url:
            logger.error("HTTP client or ContentGenerationAgent URL not configured.")
            return request_key, None

        # Assuming ContentGenerationAgent has an /invoke endpoint that takes a prompt
        # and returns a result payload with a 'generated_content' key.
        invoke_url = f"{self.content_generation_agent_url.rstrip('/')}/invoke"
        logger.info(f"Calling ContentGenerationAgent A2A at {invoke_url} for '{request_key}'...")

        # Prepare payload for ContentGenerationAgent (assuming it takes 'action' and 'prompt')
        # The ContentGenerationAgent was refactored to take 'action' and other params directly.
        # We need to adapt the call here to match its expected input structure.
        # Let's assume ContentGenerationAgent has a generic 'generate_text' action
        # that takes a 'prompt' and returns {'generated_content': '...'}
        # OR, more likely, it has specific actions like 'generate_marketing_copy'
        # We need to align this call with the ContentGenerationAgent's actual API.

        # Based on the ContentGenerationAgent refactor, it takes an 'action' and other params.
        # Let's assume we need to call it with action 'generate_marketing_copy' and pass the prompt.
        # This might require restructuring the prompt or adding more context data.
        # For now, let's simplify and assume ContentGenAgent has a generic 'generate_text' action
        # that just takes a prompt and returns raw text. If not, this needs adjustment.

        # Re-evaluating ContentGenerationAgent's refactored /invoke endpoint:
        # It takes ContentGenInput (action, niche, quantity, focus, product_name, style).
        # It returns ContentGenOutput (task_id, action, timestamp, success, results, error).
        # The 'generate_marketing_copy' action takes product_name, niche, style.
        # The prompt logic here is generating specific snippets (social, ad, email).
        # It seems the ContentGenerationAgent's actions are too high-level for generating snippets.
        # The original approach of passing a specific prompt to ContentGenAgent's 'generate' skill
        # (which likely used an LLM directly) was more suitable.

        # Let's revert to the assumption that ContentGenAgent has a skill/endpoint
        # that takes a raw prompt and returns generated text. If the refactored
        # ContentGenAgent doesn't support this, this agent will need further adjustment
        # or ContentGenAgent needs a new endpoint/action.

        # Assuming a generic 'generate_text' action on ContentGenAgent
        payload = {
            "action": "generate_marketing_copy", # Using the action name from ContentGenAgent
            "prompt": prompt, # Pass the specific snippet prompt
            # Add other required params for generate_marketing_copy if needed by ContentGenAgent
            # e.g., "product_name": "...", "niche": "...", "style": "..."
            # This means the prompt formulation needs to change, or ContentGenAgent needs a simpler action.
            # Let's assume ContentGenAgent has a simple 'generate_text' action that takes just 'prompt'.
            "action": "generate_text", # Assuming a simple action exists
            "prompt": prompt
        }

        try:
            response = await self.http_client.post(invoke_url, json=payload)
            response.raise_for_status()
            response_data = response.json()

            # Assuming ContentGenAgent's success response includes the generated text
            # Let's check the ContentGenOutput model: it has 'results'.
            # If action was 'generate_text', maybe 'results' contains the string?
            # Or maybe it's nested? Let's assume 'results' is the string for 'generate_text'.
            if response_data.get("success") and "results" in response_data:
                 generated_content = response_data["results"]
                 if isinstance(generated_content, str):
                     logger.info(f"Successfully received content from ContentGenerationAgent for '{request_key}'.")
                     return request_key, generated_content
                 else:
                     logger.warning(f"ContentGenerationAgent returned non-string results for '{request_key}'. Data: {response_data}")
                     return request_key, None
            else:
                error_msg = response_data.get("error", "Unknown error from ContentGenerationAgent")
                logger.error(f"ContentGenerationAgent A2A call failed for '{request_key}': {error_msg}. Response: {response_data}")
                return request_key, None

        except httpx.RequestError as e:
            logger.error(f"HTTP request error calling ContentGenerationAgent for '{request_key}': {e}", exc_info=True)
            return request_key, None
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP status error calling ContentGenerationAgent for '{request_key}': {e.response.status_code} - {e.response.text}", exc_info=True)
            return request_key, None
        except Exception as e:
            logger.error(f"Unexpected error calling ContentGenerationAgent for '{request_key}': {e}", exc_info=True)
            return request_key, None


    async def run_async(self, context: InvocationContext) -> Event:
        """
        Executes the marketing content generation workflow.
        Reads input from context.data.
        """
        logger.info(f"MarketingAgent run_async invoked with context ID: {context.invocation_id}")
        agent_id = context.agent_id
        invocation_id = context.invocation_id

        try:
            # 1. Parse Input Data from context.data
            if not isinstance(context.data, dict):
                raise ValueError("Input data must be a dictionary.")

            try:
                # Use the input models defined for the FastAPI endpoint
                input_data = MarketingAgentInput(**context.data)
                product_spec = input_data.product_spec
                branding = input_data.branding_package
            except ValidationError as e:
                logger.error(f"Input validation failed: {e}", exc_info=True)
                return context.create_event(
                    event_type="adk.agent.error",
                    data={"error": "Input Validation Error", "details": e.errors()},
                    metadata={"status": "error"}
                )
            except Exception as e:
                logger.error(f"Failed to parse input data: {e}", exc_info=True)
                return context.create_event(
                    event_type="adk.agent.error",
                    data={"error": "Input Parsing Error", "details": str(e)},
                    metadata={"status": "error"}
                )

            logger.info(f"Parsed input: Product='{product_spec.product_name}', Brand='{branding.brand_name}'")

            # 2. Formulate Content Requests
            content_requests = {
                "social_media_post_1": f"Generate a short, engaging social media post for {product_spec.product_name}. Tone: {branding.tone_of_voice}. Target Audience: {product_spec.target_audience}. Key features: {', '.join(product_spec.key_features)}. USP: {', '.join(product_spec.unique_selling_points)}. Keywords: {', '.join(branding.keywords)}.",
                "social_media_post_2": f"Create another distinct social media post for {product_spec.product_name}, focusing on its unique selling points: {', '.join(product_spec.unique_selling_points)}. Tone: {branding.tone_of_voice}. Brand: {branding.brand_name}.",
                "social_media_post_3": f"Write a brief social media update announcing {product_spec.product_name}. Highlight one key feature: {product_spec.key_features[0] if product_spec.key_features else 'a key feature'}. Tone: {branding.tone_of_voice}.",
                "ad_copy_1": f"Generate a concise ad copy (max 30 words) for {product_spec.product_name}. Focus on the main benefit for {product_spec.target_audience}. Tone: {branding.tone_of_voice}. Keywords: {', '.join(branding.keywords)}.",
                "ad_copy_2": f"Create a short ad copy emphasizing the unique selling points of {product_spec.product_name}: {', '.join(product_spec.unique_selling_points)}. Tone: {branding.tone_of_voice}.",
                "email_announcement_1": f"Draft a brief email announcement for {product_spec.product_name} launch/update. Target Audience: {product_spec.target_audience}. Include key features: {', '.join(product_spec.key_features)}. Tone: {branding.tone_of_voice}. Brand: {branding.brand_name}."
            }

            # 3. Delegate to ContentGenerationAgent Concurrently using A2A HTTP calls
            tasks = []
            for key, prompt in content_requests.items():
                # Create a task for each content request using the HTTP helper
                tasks.append(self._call_content_generation_agent(prompt, key)) # Pass prompt and key

            logger.info(f"Dispatching {len(tasks)} content generation A2A calls concurrently.")
            # Gather results. Each result is a tuple: (request_key, content_or_none)
            gathered_results = await asyncio.gather(*tasks)
            logger.info("Received responses from ContentGenerationAgent A2A calls.")

            # Process results into a dictionary
            results = {}
            failed_tasks = []
            for key, content in gathered_results:
                results[key] = content
                if content is None:
                    failed_tasks.append(key)

            if failed_tasks:
                error_msg = f"Failed to generate content for: {', '.join(failed_tasks)}"
                logger.error(error_msg)
                # Return error event if any task failed
                return context.create_event(
                    event_type="adk.agent.error",
                    data={"error": "Content Generation Failed", "details": error_msg, "failed_tasks": failed_tasks},
                    metadata={"status": "error"}
                )

            # 4. Structure Output
            try:
                marketing_package = MarketingMaterialsPackage(
                    social_media_posts=[results[f"social_media_post_{i}"] for i in range(1, 4)],
                    ad_copies=[results[f"ad_copy_{i}"] for i in range(1, 3)],
                    email_announcements=[results["email_announcement_1"]]
                )
                logger.info("Successfully compiled MarketingMaterialsPackage.")
            except Exception as e:
                 logger.error(f"Failed to structure output package: {e}", exc_info=True)
                 return context.create_event(
                    event_type="adk.agent.error",
                    data={"error": "Output Structuring Failed", "details": str(e)},
                    metadata={"status": "error"}
                 )

            # 5. Return Success Event
            logger.info("Marketing content generation finished successfully.")
            return context.create_event(
                event_type="marketing.materials.generated", # Specific event type
                data=marketing_package.model_dump(), # Use model_dump for Pydantic v2
                metadata={"status": "success"}
            )

        except Exception as e:
            logger.error(f"An unexpected error occurred in MarketingAgent: {e}", exc_info=True)
            return context.create_event(
                event_type="adk.agent.error",
                data={"error": "Unexpected Agent Error", "details": str(e)},
                metadata={"status": "error"}
            )

    async def close_clients(self):
        """Close any open HTTP clients."""
        if self.http_client and not self.http_client.is_closed:
            await self.http_client.aclose()
            logger.info("Closed httpx client.")


# --- FastAPI Server Setup ---

app = FastAPI(title="MarketingAgent A2A Server")

# Instantiate the agent (reads env vars internally)
try:
    marketing_agent_instance = MarketingAgent()
except ValueError as e:
    logger.critical(f"Failed to initialize MarketingAgent: {e}. Server cannot start.", exc_info=True)
    import sys
    sys.exit(f"Agent Initialization Error: {e}")


@app.post("/invoke", response_model=MarketingMaterialsPackage, responses={500: {"model": MarketingAgentErrorOutput}})
async def invoke_agent(request: MarketingAgentInput = Body(...)):
    """
    A2A endpoint to invoke the MarketingAgent.
    Expects JSON body matching MarketingAgentInput.
    Returns MarketingMaterialsPackage on success, or raises HTTPException on error.
    """
    logger.info(f"MarketingAgent /invoke called for product: {request.product_spec.product_name}")
    invocation_id = f"marketing-{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(1000,9999)}"
    context = InvocationContext(agent_id="marketing-agent", invocation_id=invocation_id, data=request.model_dump())

    try:
        result_event = await marketing_agent_instance.run_async(context)

        if result_event and isinstance(result_event.data, dict):
            if result_event.metadata.get("status") == "error":
                 error_msg = result_event.data.get("error", "Unknown agent error")
                 error_details = result_event.data.get("details")
                 logger.error(f"MarketingAgent run_async returned error event: {error_msg}")
                 raise HTTPException(status_code=500, detail=MarketingAgentErrorOutput(error=error_msg, details=error_details).model_dump(exclude_none=True))
            else:
                 # Validate success payload against MarketingMaterialsPackage
                 try:
                     output_payload = MarketingMaterialsPackage(**result_event.data)
                     logger.info(f"MarketingAgent returning success result.")
                     return output_payload
                 except ValidationError as val_err:
                     logger.error(f"Success event payload validation failed: {val_err}. Payload: {result_event.data}")
                     raise HTTPException(status_code=500, detail=MarketingAgentErrorOutput(error="Internal validation error on success payload.", details=val_err.errors()).model_dump(exclude_none=True))
        else:
            logger.error(f"MarketingAgent run_async returned None or invalid event data: {result_event}")
            raise HTTPException(status_code=500, detail=MarketingAgentErrorOutput(error="Agent execution failed to return a valid event.").model_dump())

    except HTTPException as http_exc:
        raise http_exc # Re-raise FastAPI exceptions
    except Exception as e:
        logger.error(f"Error during agent invocation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=MarketingAgentErrorOutput(error=f"Internal server error: {e}").model_dump())

@app.get("/health")
async def health_check():
    # Add checks for ContentGenerationAgent URL presence if needed
    return {"status": "ok"}

# --- Server Shutdown Hook ---
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down MarketingAgent server...")
    await marketing_agent_instance.close_clients() # Close httpx client

# --- Main execution block ---

if __name__ == "__main__":
    # Load .env for local development if needed
    try:
        from dotenv import load_dotenv
        if load_dotenv(): logger.info("Loaded .env file for local run.")
        else: logger.info("No .env file found or it was empty.")
    except ImportError: logger.info("dotenv library not found, skipping .env load.")

    parser = argparse.ArgumentParser(description="Run the MarketingAgent A2A server.")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind the server to.")
    parser.add_argument("--port", type=int, default=8090, help="Port to run the server on.") # Default matches compose
    args = parser.parse_args()

    # Optional: Check for CONTENT_GENERATION_AGENT_URL before starting
    # if not os.environ.get(MarketingAgent.ENV_CONTENT_GENERATION_AGENT_URL):
    #     print(f"CRITICAL ERROR: Environment variable {MarketingAgent.ENV_CONTENT_GENERATION_AGENT_URL} must be set.")
    #     import sys
    #     sys.exit(1)

    print(f"Starting MarketingAgent A2A server on {args.host}:{args.port}")

    uvicorn.run(app, host=args.host, port=args.port)