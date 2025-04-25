"""
Marketing Agent for Decision Points.

This agent generates marketing materials based on product specifications and branding.
It implements the A2A protocol for agent communication.
"""

import asyncio
import httpx
import logging
from typing import List, Dict, Any, Optional

from pydantic import BaseModel, Field

# ADK Imports
from google.adk.runtime import InvocationContext, Event, Status

# A2A Imports
from python_a2a import skill

from agents.base_agent import BaseSpecializedAgent
from app.config import settings

# Configure logging
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

class MarketingAgent(BaseSpecializedAgent):
    """
    Agent responsible for marketing.
    Generates various marketing copy snippets by leveraging the ContentGenerationAgent.
    Implements A2A protocol for agent communication.
    """

    def __init__(
        self,
        name: str = "marketing",
        description: str = "Generates marketing materials based on product specifications and branding",
        model_name: Optional[str] = None,
        port: Optional[int] = None,
        **kwargs: Any,
    ):
        """
        Initialize the MarketingAgent.

        Args:
            name: The name of the agent.
            description: The description of the agent.
            model_name: The name of the model to use. Defaults to settings.GEMINI_MODEL_NAME.
            port: The port to run the A2A server on. Defaults to settings.MARKETING_AGENT_URL port.
            **kwargs: Additional arguments for BaseSpecializedAgent.
        """
        # Extract port from URL if not provided
        if port is None and settings.MARKETING_AGENT_URL:
            try:
                port = int(settings.MARKETING_AGENT_URL.split(':')[-1])
            except (ValueError, IndexError):
                port = 8009  # Default port

        # Initialize BaseSpecializedAgent
        super().__init__(
            name=name,
            description=description,
            model_name=model_name,
            port=port,
            **kwargs
        )

        # Get agent ID from settings
        self.content_generation_agent_id = settings.CONTENT_GENERATION_AGENT_ID
        if not self.content_generation_agent_id:
            logger.warning("CONTENT_GENERATION_AGENT_ID not configured in settings. Content generation will be limited.")

        logger.info(f"MarketingAgent initialized with port: {self.port}")


    async def _invoke_content_generation_skill(self, prompt: str, request_key: str) -> tuple[str, Optional[str]]:
        """
        Invokes the ContentGenerationAgent's 'generate' skill and returns the result.

        Args:
            prompt: The prompt for the content generation.
            request_key: An identifier for the request (for logging/mapping results).

        Returns:
            A tuple containing the request_key and the generated content (str) or None if failed.
        """
        logger.info(f"Invoking ContentGenerationAgent skill 'generate' for '{request_key}' via agent network...")

        try:
            from agents.agent_network import agent_network

            # Get the agent from the network
            agent = agent_network.get_agent("content_generation")
            if not agent:
                logger.error("ContentGenerationAgent not found in agent network.")
                return request_key, None

            # Invoke the generate skill
            result = await agent.invoke_skill(
                skill_name="generate",
                input_data={"prompt": prompt},
                timeout=60.0
            )

            if result and "generated_content" in result:
                logger.info(f"Successfully received content from ContentGenerationAgent skill for '{request_key}'.")
                return request_key, result["generated_content"]
            else:
                logger.error(f"ContentGenerationAgent skill call for '{request_key}' returned unexpected payload.")
                return request_key, None

        except Exception as e:
            logger.error(f"Error calling ContentGenerationAgent for '{request_key}': {e}", exc_info=True)
            return request_key, None

    # --- A2A Skills ---
    @skill(
        name="generate_marketing_materials",
        description="Generate marketing materials based on product specifications and branding",
        tags=["marketing", "content"]
    )
    async def generate_marketing_materials(self, product_spec: Dict[str, Any], branding_package: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate marketing materials based on product specifications and branding.

        Args:
            product_spec: The product specification.
            branding_package: The branding package.

        Returns:
            A dictionary containing the generated marketing materials.
        """
        logger.info(f"Generating marketing materials for product: {product_spec.get('product_name', 'Unknown')}")

        try:
            # Parse input data
            try:
                product_spec_model = ImprovedProductSpec(**product_spec)
                branding_model = BrandingPackage(**branding_package)
            except Exception as e:
                logger.error(f"Failed to parse input data: {e}", exc_info=True)
                return {
                    "success": False,
                    "error": f"Invalid input data format: {str(e)}"
                }

            logger.info(f"Parsed input: Product='{product_spec_model.product_name}', Brand='{branding_model.brand_name}'")

            # Formulate content requests
            content_requests = {
                "social_media_post_1": f"Generate a short, engaging social media post for {product_spec_model.product_name}. Tone: {branding_model.tone_of_voice}. Target Audience: {product_spec_model.target_audience}. Key features: {', '.join(product_spec_model.key_features)}. USP: {', '.join(product_spec_model.unique_selling_points)}. Keywords: {', '.join(branding_model.keywords)}.",
                "social_media_post_2": f"Create another distinct social media post for {product_spec_model.product_name}, focusing on its unique selling points: {', '.join(product_spec_model.unique_selling_points)}. Tone: {branding_model.tone_of_voice}. Brand: {branding_model.brand_name}.",
                "social_media_post_3": f"Write a brief social media update announcing {product_spec_model.product_name}. Highlight one key feature: {product_spec_model.key_features[0] if product_spec_model.key_features else 'a key feature'}. Tone: {branding_model.tone_of_voice}.",
                "ad_copy_1": f"Generate a concise ad copy (max 30 words) for {product_spec_model.product_name}. Focus on the main benefit for {product_spec_model.target_audience}. Tone: {branding_model.tone_of_voice}. Keywords: {', '.join(branding_model.keywords)}.",
                "ad_copy_2": f"Create a short ad copy emphasizing the unique selling points of {product_spec_model.product_name}: {', '.join(product_spec_model.unique_selling_points)}. Tone: {branding_model.tone_of_voice}.",
                "email_announcement_1": f"Draft a brief email announcement for {product_spec_model.product_name} launch/update. Target Audience: {product_spec_model.target_audience}. Include key features: {', '.join(product_spec_model.key_features)}. Tone: {branding_model.tone_of_voice}. Brand: {branding_model.brand_name}."
            }

            # Delegate to ContentGenerationAgent concurrently
            tasks = []
            for key, prompt in content_requests.items():
                tasks.append(self._invoke_content_generation_skill(prompt, key))

            logger.info(f"Dispatching {len(tasks)} content generation skill invocations concurrently.")
            gathered_results = await asyncio.gather(*tasks)
            logger.info("Received responses from ContentGenerationAgent skill invocations.")

            # Process results into a dictionary
            results = {}
            for key, content in gathered_results:
                results[key] = content

            # Check for failures
            failed_tasks = [key for key, content in results.items() if content is None]
            if failed_tasks:
                error_msg = f"Failed to generate content for: {', '.join(failed_tasks)}"
                logger.error(error_msg)

                # If all tasks failed, return an error
                if len(failed_tasks) == len(content_requests):
                    return {
                        "success": False,
                        "error": "Failed to generate any marketing materials."
                    }

            # Structure output
            try:
                marketing_package = MarketingMaterialsPackage(
                    social_media_posts=[results.get(f"social_media_post_{i}") or f"[Failed to generate social media post {i}]" for i in range(1, 4)],
                    ad_copies=[results.get(f"ad_copy_{i}") or f"[Failed to generate ad copy {i}]" for i in range(1, 3)],
                    email_announcements=[results.get("email_announcement_1") or "[Failed to generate email announcement]"]
                )
                logger.info("Successfully compiled MarketingMaterialsPackage.")

                return {
                    "success": True,
                    "message": "Successfully generated marketing materials.",
                    **marketing_package.model_dump()
                }
            except Exception as e:
                logger.error(f"Failed to structure output package: {e}", exc_info=True)
                return {
                    "success": False,
                    "error": f"Failed to structure output: {str(e)}"
                }

        except Exception as e:
            logger.error(f"Error generating marketing materials: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"Error generating marketing materials: {str(e)}"
            }

    @skill(
        name="generate_social_media_post",
        description="Generate a social media post for a product",
        tags=["marketing", "social"]
    )
    async def generate_social_media_post(self, product_name: str, tone: str,
                                        target_audience: Optional[str] = None,
                                        key_features: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Generate a social media post for a product.

        Args:
            product_name: The name of the product.
            tone: The tone of voice for the post.
            target_audience: Optional target audience for the post.
            key_features: Optional list of key features to highlight.

        Returns:
            A dictionary containing the generated social media post.
        """
        logger.info(f"Generating social media post for product: {product_name}")

        try:
            # Create prompt
            prompt = f"Generate a short, engaging social media post for {product_name}. Tone: {tone}."
            if target_audience:
                prompt += f" Target Audience: {target_audience}."
            if key_features:
                prompt += f" Key features: {', '.join(key_features)}."

            # Call ContentGenerationAgent
            _, content = await self._invoke_content_generation_skill(prompt, "social_media_post")

            if content:
                return {
                    "success": True,
                    "message": "Successfully generated social media post.",
                    "post": content
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to generate social media post."
                }

        except Exception as e:
            logger.error(f"Error generating social media post: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"Error generating social media post: {str(e)}"
            }


    async def run_async(self, context: InvocationContext) -> Event:
        """
        Executes the marketing content generation workflow asynchronously according to ADK spec.
        Maintained for backward compatibility with ADK.

        Args:
            context: The invocation context containing the input data.

        Returns:
            An Event containing the marketing materials or an error.
        """
        logger.info(f"Received invocation for MarketingAgent (ID: {context.invocation_id})")

        try:
            # Extract input from context
            if not hasattr(context, 'data') or not context.data:
                logger.error("Input data is missing in the invocation context.")
                return Event.create_failure(
                    invocation_id=context.invocation_id,
                    agent_id=self.name,
                    error_message="Input data is missing."
                )

            # Use the A2A skill
            result = await self.generate_marketing_materials(
                product_spec=context.data.get("product_spec", {}),
                branding_package=context.data.get("branding_package", {})
            )

            # Create an event from the result
            if result.get("success", False):
                return Event.create_success(
                    invocation_id=context.invocation_id,
                    agent_id=self.name,
                    data={k: v for k, v in result.items() if k != "success" and k != "message"}
                )
            else:
                return Event.create_failure(
                    invocation_id=context.invocation_id,
                    agent_id=self.name,
                    error_message=result.get("error", "Marketing materials generation failed.")
                )

        except Exception as e:
            # Catch-all for unexpected errors
            logger.error(f"Unexpected error in MarketingAgent: {e}", exc_info=True)
            return Event.create_failure(
                invocation_id=context.invocation_id,
                agent_id=self.name,
                error_message=f"An unexpected error occurred: {str(e)}"
            )

# Example of how to run this agent as a standalone A2A server
if __name__ == "__main__":
    # Create the agent
    agent = MarketingAgent()

    # Run the A2A server
    agent.run_server(host="0.0.0.0", port=agent.port or 8009)