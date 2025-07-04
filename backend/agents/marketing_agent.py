import os
import asyncio
import httpx
import logging
from typing import List, Dict, Any, Optional

from pydantic import BaseModel, Field
from google.adk.agents import Agent
from google.adk.runtime import InvocationContext, Event, Status

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Placeholder Data Models ---
# These should ideally be defined in a shared models directory
# and imported, but are included here for completeness.

class ImprovedProductSpec(BaseModel):
    """Represents the improved product specification."""
    product_name: str = Field(..., description="Name of the product.")
    description: str = Field(..., description="Detailed description of the product.")
    target_audience: str = Field(..., description="The intended audience for the product.")
    key_features: List[str] = Field(..., description="List of key product features.")
    unique_selling_points: List[str] = Field(..., description="Unique aspects differentiating the product.")

class BrandingPackage(BaseModel):
    """Represents the branding guidelines and assets."""
    brand_name: str = Field(..., description="The brand name.")
    tone_of_voice: str = Field(..., description="Desired tone for marketing communications (e.g., formal, playful).")
    keywords: List[str] = Field(..., description="Relevant keywords for the brand/product.")
    logo_description: Optional[str] = Field(None, description="Description of the brand logo.") # Assuming logo itself isn't passed

class MarketingMaterialsPackage(BaseModel):
    """Structured output containing generated marketing materials."""
    social_media_posts: List[str] = Field(..., description="Generated social media posts.")
    ad_copies: List[str] = Field(..., description="Generated short advertisement copies.")
    email_announcements: List[str] = Field(..., description="Generated brief email announcements.")

# --- Marketing Agent ---

class MarketingAgent(Agent):
    """
    Generates various marketing copy snippets by leveraging the ContentGenerationAgent.
    """

    def __init__(self):
        """
        Initializes the MarketingAgent.
        Retrieves the ContentGenerationAgent URL from environment variables.
        """
        super().__init__(unique_id="marketing_agent")
        self.content_generation_agent_url = os.getenv("CONTENT_GENERATION_AGENT_URL")
        if not self.content_generation_agent_url:
            logger.error("CONTENT_GENERATION_AGENT_URL environment variable not set.")
            raise ValueError("CONTENT_GENERATION_AGENT_URL must be set")
        # Ensure the URL ends with the specific A2A endpoint
        if not self.content_generation_agent_url.endswith('/a2a/content_generation/invoke'):
             self.content_generation_agent_url = self.content_generation_agent_url.rstrip('/') + '/a2a/content_generation/invoke'
        logger.info(f"MarketingAgent initialized. ContentGenerationAgent URL: {self.content_generation_agent_url}")


    async def generate_content(self, client: httpx.AsyncClient, prompt: str, context_data: Dict[str, Any]) -> Optional[str]:
        """
        Helper function to make a single A2A call to the ContentGenerationAgent.
        """
        payload = InvocationContext(
            invocation_id="marketing_to_contentgen_" + context_data.get("original_invocation_id", "unknown"), # Add traceability
            agent_id="content_generation", # Target agent ID
            data={"prompt": prompt} # Data payload for the target agent
        )
        try:
            logger.info(f"Sending request to ContentGenerationAgent: {prompt[:100]}...")
            response = await client.post(
                self.content_generation_agent_url,
                json=payload.model_dump(mode='json'), # Use model_dump for Pydantic v2
                timeout=60.0 # Set a reasonable timeout
            )
            response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)
            event_data = response.json()
            event = Event(**event_data)

            if event.status == Status.SUCCESS and event.data and "generated_content" in event.data:
                logger.info("Successfully received content from ContentGenerationAgent.")
                return event.data["generated_content"]
            else:
                logger.error(f"ContentGenerationAgent returned status {event.status} or missing data. Error: {event.error_message}")
                return None
        except httpx.RequestError as e:
            logger.error(f"HTTP request error calling ContentGenerationAgent: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error calling ContentGenerationAgent: {e}")
            return None


    async def run_async(self, context: InvocationContext) -> Event:
        """
        Executes the marketing content generation workflow.
        """
        logger.info(f"MarketingAgent run_async invoked with context ID: {context.invocation_id}")

        try:
            # 1. Parse Input Data
            if not context.data:
                logger.error("Input data is missing in the invocation context.")
                return Event.create_failure(
                    invocation_id=context.invocation_id,
                    agent_id=self.unique_id,
                    error_message="Input data is missing."
                )

            try:
                product_spec = ImprovedProductSpec(**context.data.get("product_spec", {}))
                branding = BrandingPackage(**context.data.get("branding_package", {}))
            except Exception as e:
                logger.error(f"Failed to parse input data: {e}", exc_info=True)
                return Event.create_failure(
                    invocation_id=context.invocation_id,
                    agent_id=self.unique_id,
                    error_message=f"Invalid input data format: {e}"
                )

            logger.info(f"Parsed input: Product='{product_spec.product_name}', Brand='{branding.brand_name}'")

            # 2. Formulate Content Requests
            # Define the types and number of marketing materials needed
            content_requests = {
                "social_media_post_1": f"Generate a short, engaging social media post for {product_spec.product_name}. Tone: {branding.tone_of_voice}. Target Audience: {product_spec.target_audience}. Key features: {', '.join(product_spec.key_features)}. USP: {', '.join(product_spec.unique_selling_points)}. Keywords: {', '.join(branding.keywords)}.",
                "social_media_post_2": f"Create another distinct social media post for {product_spec.product_name}, focusing on its unique selling points: {', '.join(product_spec.unique_selling_points)}. Tone: {branding.tone_of_voice}. Brand: {branding.brand_name}.",
                "social_media_post_3": f"Write a brief social media update announcing {product_spec.product_name}. Highlight one key feature: {product_spec.key_features[0] if product_spec.key_features else 'a key feature'}. Tone: {branding.tone_of_voice}.",
                "ad_copy_1": f"Generate a concise ad copy (max 30 words) for {product_spec.product_name}. Focus on the main benefit for {product_spec.target_audience}. Tone: {branding.tone_of_voice}. Keywords: {', '.join(branding.keywords)}.",
                "ad_copy_2": f"Create a short ad copy emphasizing the unique selling points of {product_spec.product_name}: {', '.join(product_spec.unique_selling_points)}. Tone: {branding.tone_of_voice}.",
                "email_announcement_1": f"Draft a brief email announcement for {product_spec.product_name} launch/update. Target Audience: {product_spec.target_audience}. Include key features: {', '.join(product_spec.key_features)}. Tone: {branding.tone_of_voice}. Brand: {branding.brand_name}."
            }

            # 3. Delegate to ContentGenerationAgent Concurrently
            results = {}
            async with httpx.AsyncClient() as client:
                tasks = []
                for key, prompt in content_requests.items():
                    # Pass original invocation ID for traceability if available
                    helper_context = {"original_invocation_id": context.invocation_id}
                    tasks.append(self.generate_content(client, prompt, helper_context))

                logger.info(f"Dispatching {len(tasks)} content generation tasks concurrently.")
                generated_contents = await asyncio.gather(*tasks)
                logger.info("Received responses from ContentGenerationAgent tasks.")

                # Map results back to keys
                results = dict(zip(content_requests.keys(), generated_contents))

            # Check for failures
            failed_tasks = [key for key, content in results.items() if content is None]
            if failed_tasks:
                error_msg = f"Failed to generate content for: {', '.join(failed_tasks)}"
                logger.error(error_msg)
                # Decide if partial results are acceptable or if it's a total failure
                # For now, let's return failure if any task failed.
                return Event.create_failure(
                    invocation_id=context.invocation_id,
                    agent_id=self.unique_id,
                    error_message=error_msg
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
                 return Event.create_failure(
                    invocation_id=context.invocation_id,
                    agent_id=self.unique_id,
                    error_message=f"Failed to structure output: {e}"
                )

            # 5. Return Success Event
            return Event.create_success(
                invocation_id=context.invocation_id,
                agent_id=self.unique_id,
                data=marketing_package.model_dump(mode='json') # Use model_dump for Pydantic v2
            )

        except Exception as e:
            logger.error(f"An unexpected error occurred in MarketingAgent: {e}", exc_info=True)
            return Event.create_failure(
                invocation_id=context.invocation_id,
                agent_id=self.unique_id,
                error_message=f"An unexpected error occurred: {str(e)}"
            )

# Example of how to potentially register the agent (if using a framework that supports it)
# This part might live elsewhere (e.g., in app.py or main.py) depending on the application structure.
# from google.adk.runtime import AgentRegistry
# agent_registry = AgentRegistry()
# agent_registry.register(MarketingAgent())