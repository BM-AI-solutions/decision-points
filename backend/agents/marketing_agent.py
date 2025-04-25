"""
Marketing Agent for Decision Points (ADK Version).

This agent generates marketing materials based on product specifications and branding,
delegating content creation tasks to the ContentGenerationAgent via ADK tools.
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional, Tuple

from pydantic import BaseModel, Field

# ADK Imports
from google.adk.agents import Agent # Use ADK Agent
from google.adk.tools import tool, ToolContext # Import tool decorator and context
from google.adk.events import Event # Import Event for tool return type

# Removed BaseSpecializedAgent import
from app.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Global Config ---
AGENT_ID = "marketing_adk"
# Get target agent ID from settings
CONTENT_GENERATION_AGENT_ID = settings.CONTENT_GENERATION_AGENT_ID
if not CONTENT_GENERATION_AGENT_ID:
    logger.warning("CONTENT_GENERATION_AGENT_ID not configured in settings. Marketing agent cannot function.")

# --- Pydantic Models (Keep as they define data structures) ---
class ImprovedProductSpec(BaseModel):
    product_name: str = Field(..., description="Name of the product.")
    description: str = Field(..., description="Detailed description of the product.")
    target_audience: str = Field(..., description="The intended audience for the product.")
    key_features: List[str] = Field(..., description="List of key product features.")
    unique_selling_points: List[str] = Field(..., description="Unique aspects differentiating the product.")

class BrandingPackage(BaseModel):
    brand_name: str = Field(..., description="The brand name.")
    tone_of_voice: str = Field(..., description="Desired tone for marketing communications (e.g., formal, playful).")
    keywords: List[str] = Field(..., description="Relevant keywords for the brand/product.")
    logo_description: Optional[str] = Field(None, description="Description of the brand logo.")

class MarketingMaterialsPackage(BaseModel):
    social_media_posts: List[str] = Field(..., description="Generated social media posts.")
    ad_copies: List[str] = Field(..., description="Generated short advertisement copies.")
    email_announcements: List[str] = Field(..., description="Generated brief email announcements.")

# --- Helper Function for Delegation ---

async def _invoke_content_generation_tool(
    context: ToolContext,
    prompt: str,
    request_key: str # For logging/tracking
) -> Tuple[str, Optional[str]]:
    """
    Helper: Invokes the ContentGenerationAgent's tool via ADK.

    Args:
        context: The ADK ToolContext.
        prompt: The prompt for content generation.
        request_key: Identifier for the request.

    Returns:
        Tuple of (request_key, generated_content or None).
    """
    if not CONTENT_GENERATION_AGENT_ID:
        logger.error("ContentGenerationAgent ID not configured. Cannot delegate.")
        return request_key, None

    target_adk_agent_id = "content_generation_adk" # Use the refactored ADK agent name
    # Assuming the content generation agent has a primary tool (e.g., 'generate_content_tool')
    # that takes the prompt. Adjust skill_name if needed.
    target_tool_name = "generate_content_tool" # Replace with actual tool name if different

    logger.info(f"Helper: Invoking ADK agent '{target_adk_agent_id}' tool '{target_tool_name}' for '{request_key}'...")

    try:
        # Prepare input data for the target tool
        # Adjust input structure based on the actual 'generate_content_tool' signature
        input_data = {"prompt": prompt}
        input_event = Event(data=input_data)

        # Use context.invoke_agent to call the target ADK agent's tool implicitly
        # Or use context.invoke_tool if you need to specify the tool explicitly
        response_event = await context.invoke_agent(
            target_agent_id=target_adk_agent_id,
            input=input_event,
            timeout_seconds=60.0
        )

        # Process the response event
        if response_event and response_event.actions:
            # Assuming the result is in the first part of the first action's content
            # Adjust parsing based on how content_generation_adk returns results
            action = response_event.actions[0]
            if action.content and action.content.parts:
                 part_data = action.content.parts[0].data
                 if isinstance(part_data, dict) and part_data.get("success"):
                     # Extract the actual content - adjust key based on content_gen_agent's output
                     generated_content = part_data.get("generated_text") or part_data.get("content")
                     if generated_content:
                         logger.info(f"Helper: Successfully received content from {target_adk_agent_id} for '{request_key}'.")
                         return request_key, str(generated_content) # Ensure string return
                     else:
                         logger.error(f"Helper: {target_adk_agent_id} response for '{request_key}' missing content field.")
                         return request_key, None
                 elif isinstance(part_data, dict) and not part_data.get("success"):
                     error_msg = part_data.get("error", "Unknown error from content gen tool")
                     logger.error(f"Helper: {target_adk_agent_id} tool call for '{request_key}' failed: {error_msg}")
                     return request_key, None
                 else: # Fallback if data is not a dict or structure unexpected
                      logger.warning(f"Helper: Unexpected payload structure from {target_adk_agent_id} for '{request_key}': {part_data}")
                      # Try to convert to string as a last resort
                      return request_key, str(part_data)

            # Fallback if structure is different (e.g., result directly in parts)
            elif action.parts:
                 part_data = action.parts[0].data
                 logger.warning(f"Helper: Using fallback parsing for {target_adk_agent_id} response for '{request_key}'.")
                 return request_key, str(part_data) # Convert to string

        logger.error(f"Helper: {target_adk_agent_id} invocation for '{request_key}' returned unexpected/empty response: {response_event}")
        return request_key, None

    except Exception as e:
        logger.error(f"Helper: Error invoking {target_adk_agent_id} for '{request_key}': {e}", exc_info=True)
        return request_key, None


# --- ADK Tool Definitions ---

@tool(description="Generate various marketing materials (social posts, ad copy, emails) based on product specifications and branding.")
async def generate_marketing_materials_tool(
    context: ToolContext, # Add context for invoking other agents
    product_spec: Dict[str, Any],
    branding_package: Dict[str, Any]
) -> Dict[str, Any]:
    """
    ADK Tool: Generate marketing materials by delegating to ContentGenerationAgent.
    Returns a MarketingMaterialsPackage or an error dictionary.
    """
    logger.info(f"Tool: Generating marketing materials for product: {product_spec.get('product_name', 'Unknown')}")

    try:
        # Parse input data (using Pydantic models for validation)
        try:
            product_spec_model = ImprovedProductSpec(**product_spec)
            branding_model = BrandingPackage(**branding_package)
        except (ValidationError, TypeError) as e:
            logger.error(f"Tool: Input validation failed: {e}", exc_info=True)
            return {"success": False, "error": f"Invalid input data format: {str(e)}"}

        logger.info(f"Tool: Parsed input: Product='{product_spec_model.product_name}', Brand='{branding_model.brand_name}'")

        # Formulate content requests
        content_requests = {
            "social_media_post_1": f"Generate a short, engaging social media post for {product_spec_model.product_name}. Tone: {branding_model.tone_of_voice}. Target Audience: {product_spec_model.target_audience}. Key features: {', '.join(product_spec_model.key_features)}. USP: {', '.join(product_spec_model.unique_selling_points)}. Keywords: {', '.join(branding_model.keywords)}.",
            "social_media_post_2": f"Create another distinct social media post for {product_spec_model.product_name}, focusing on its unique selling points: {', '.join(product_spec_model.unique_selling_points)}. Tone: {branding_model.tone_of_voice}. Brand: {branding_model.brand_name}.",
            "social_media_post_3": f"Write a brief social media update announcing {product_spec_model.product_name}. Highlight one key feature: {product_spec_model.key_features[0] if product_spec_model.key_features else 'a key feature'}. Tone: {branding_model.tone_of_voice}.",
            "ad_copy_1": f"Generate a concise ad copy (max 30 words) for {product_spec_model.product_name}. Focus on the main benefit for {product_spec_model.target_audience}. Tone: {branding_model.tone_of_voice}. Keywords: {', '.join(branding_model.keywords)}.",
            "ad_copy_2": f"Create a short ad copy emphasizing the unique selling points of {product_spec_model.product_name}: {', '.join(product_spec_model.unique_selling_points)}. Tone: {branding_model.tone_of_voice}.",
            "email_announcement_1": f"Draft a brief email announcement for {product_spec_model.product_name} launch/update. Target Audience: {product_spec_model.target_audience}. Include key features: {', '.join(product_spec_model.key_features)}. Tone: {branding_model.tone_of_voice}. Brand: {branding_model.brand_name}."
        }

        # Delegate concurrently using the helper
        tasks = [_invoke_content_generation_tool(context, prompt, key) for key, prompt in content_requests.items()]
        logger.info(f"Tool: Dispatching {len(tasks)} content generation tasks concurrently.")
        gathered_results = await asyncio.gather(*tasks)
        logger.info("Tool: Received responses from content generation tasks.")

        # Process results
        results = {key: content for key, content in gathered_results}
        failed_tasks = [key for key, content in results.items() if content is None]

        if failed_tasks:
            error_msg = f"Failed to generate content for: {', '.join(failed_tasks)}"
            logger.error(f"Tool: {error_msg}")
            if len(failed_tasks) == len(content_requests):
                return {"success": False, "error": "Failed to generate any marketing materials."}
            # Continue with partial results if some succeeded

        # Structure output
        try:
            marketing_package = MarketingMaterialsPackage(
                social_media_posts=[results.get(f"social_media_post_{i}") or f"[Failed: social post {i}]" for i in range(1, 4)],
                ad_copies=[results.get(f"ad_copy_{i}") or f"[Failed: ad copy {i}]" for i in range(1, 3)],
                email_announcements=[results.get("email_announcement_1") or "[Failed: email announcement]"]
            )
            logger.info("Tool: Successfully compiled MarketingMaterialsPackage.")
            return {"success": True, "marketing_materials": marketing_package.model_dump()}
        except Exception as e:
            logger.error(f"Tool: Failed to structure output package: {e}", exc_info=True)
            # Include partial results if available
            partial_results = {k: v for k, v in results.items() if v is not None}
            return {"success": False, "error": f"Failed to structure output: {str(e)}", "partial_results": partial_results}

    except Exception as e:
        logger.error(f"Tool: Error generating marketing materials: {e}", exc_info=True)
        return {"success": False, "error": f"Error generating marketing materials: {str(e)}"}

@tool(description="Generate a single social media post for a product.")
async def generate_social_media_post_tool(
    context: ToolContext, # Add context
    product_name: str,
    tone: str,
    target_audience: Optional[str] = None,
    key_features: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    ADK Tool: Generate a single social media post.
    """
    logger.info(f"Tool: Generating social media post for product: {product_name}")
    try:
        # Create prompt
        prompt = f"Generate a short, engaging social media post for {product_name}. Tone: {tone}."
        if target_audience: prompt += f" Target Audience: {target_audience}."
        if key_features: prompt += f" Key features: {', '.join(key_features)}."

        # Call ContentGenerationAgent tool using helper
        key, content = await _invoke_content_generation_tool(context, prompt, "social_media_post")

        if content:
            return {"success": True, "message": "Successfully generated social media post.", "post": content}
        else:
            return {"success": False, "error": "Failed to generate social media post from content generation agent."}

    except Exception as e:
        logger.error(f"Tool: Error generating social media post: {e}", exc_info=True)
        return {"success": False, "error": f"Error generating social media post: {str(e)}"}


# --- Instantiate the ADK Agent ---
agent = Agent(
    name=AGENT_ID,
    description="Generates marketing materials by coordinating with the Content Generation Agent.",
    tools=[
        generate_marketing_materials_tool,
        generate_social_media_post_tool,
    ],
)

# Removed A2A server specific code and old class structure
