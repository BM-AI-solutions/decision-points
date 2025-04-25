import logging
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional

import google.generativeai as genai
from google.adk.agents import Agent # Use ADK Agent

from google.adk.events import Event # Import Event for tool return type

from app.config import settings

logger = logging.getLogger(__name__)

# --- LLM Initialization (Moved outside class for tool access) ---
# Configure Gemini API Key
try:
    genai.configure(api_key=settings.GEMINI_API_KEY)
    # Initialize a model instance if tools need direct access
    # Choose a model suitable for content generation tasks
    gemini_model_name = settings.GEMINI_MODEL_NAME # Or a specific one like 'gemini-1.5-flash'
    gemini_model = genai.GenerativeModel(
        gemini_model_name,
        generation_config=genai.types.GenerationConfig(temperature=0.7)
    )
    logger.info(f"Direct Gemini model {gemini_model_name} initialized for content generation tools.")
except Exception as e:
    logger.error(f"Failed to initialize direct Gemini model: {e}")
    gemini_model = None

# --- Tool Definitions ---

@tool(description="Generate affiliate marketing content based on niche, quantity, and focus (value/conversion).")
async def create_affiliate_content_tool(niche: str, quantity: int = 3, focus: str = "value") -> List[Dict[str, Any]]:
    """
    Generate affiliate marketing content.

    Args:
        niche: The niche for the content.
        quantity: The number of content pieces to generate.
        focus: The focus of the content (value or conversion).

    Returns:
        A list of content pieces.
    """
    logger.info(f"Tool: Generating {quantity} affiliate content pieces for '{niche}' (focus: {focus})")
    return await _generate_affiliate_content(niche, quantity, focus)

@tool(description="Generate a digital course outline based on niche and number of modules.")
async def create_course_outline_tool(niche: str, modules: int = 5) -> Dict[str, Any]:
    """
    Generate a digital course outline.

    Args:
        niche: The niche for the course.
        modules: The number of modules in the course.

    Returns:
        A course outline.
    """
    logger.info(f"Tool: Generating course outline for '{niche}' ({modules} modules)")
    # Note: Original helper was synchronous, keeping it that way for now
    # If LLM is needed here, it should be made async
    return _generate_course_outline(niche, modules)

@tool(description="Generate marketing copy for a product in a specific niche and style (persuasive/informative/casual).")
async def generate_marketing_copy_tool(product_name: str, niche: str, style: str = "persuasive") -> Dict[str, str]:
    """
    Generate marketing copy.

    Args:
        product_name: The name of the product.
        niche: The niche for the marketing copy.
        style: The style of the marketing copy.

    Returns:
        Marketing copy.
    """
    logger.info(f"Tool: Generating {style} marketing copy for '{product_name}' in '{niche}'")
    # Note: Original helper was synchronous, keeping it that way for now
    return _generate_marketing_copy(product_name, niche, style)


# --- Helper Methods (Adapted from original class, now standalone) ---

async def _generate_affiliate_content(niche: str, quantity: int, focus: str) -> List[Dict[str, Any]]:
    """Generates multiple affiliate marketing content pieces."""
    agent_id = "content_generation_adk" # Use ADK agent name for logging
    logger.info(f"[{agent_id}] Generating {quantity} affiliate content pieces for '{niche}' (focus: {focus})")
    contents = []
    for _ in range(quantity):
        # Use the standalone helper functions
        title = await _generate_title(niche, focus)
        body = await _generate_article_body(niche, focus)
        contents.append({
            "title": title,
            "body": body,
            "created_at": datetime.now().isoformat()
        })
    logger.info(f"[{agent_id}] Finished generating affiliate content for '{niche}'.")
    return contents

def _generate_course_outline(niche: str, modules: int) -> Dict[str, Any]:
    """Generates a digital course outline (synchronous)."""
    agent_id = "content_generation_adk"
    logger.info(f"[{agent_id}] Generating course outline for '{niche}' ({modules} modules)")
    outline = {
        "title": f"Mastering {niche.title()}",
        "modules": []
    }
    for i in range(1, modules + 1):
        module_title = f"Module {i}: {_generate_module_title(niche, i)}"
        outline["modules"].append({
            "title": module_title,
            "lessons": _generate_lessons(niche, i)
        })
    logger.info(f"[{agent_id}] Finished generating course outline for '{niche}'.")
    return outline

def _generate_marketing_copy(product_name: str, niche: str, style: str) -> Dict[str, str]:
    """Generates marketing copy (synchronous)."""
    agent_id = "content_generation_adk"
    logger.info(f"[{agent_id}] Generating {style} marketing copy for '{product_name}' in '{niche}'")
    headline = _generate_headline(product_name, niche, style)
    description = _generate_description(product_name, niche, style)
    copy = {
        "headline": headline,
        "description": description
    }
    logger.info(f"[{agent_id}] Finished generating marketing copy for '{product_name}'.")
    return copy

async def _generate_title(niche: str, focus: str) -> str:
    """Generates a content title using the shared Gemini model."""
    agent_id = "content_generation_adk"
    prompt = f"Generate a catchy {'conversion-focused' if focus == 'conversion' else 'informative'} title for an affiliate marketing article in the '{niche}' niche. Provide only the title text."
    if not gemini_model:
        logger.warning(f"[{agent_id}] Gemini model not available for title generation, falling back to mock.")
        # Fallback mock logic
        if focus == "conversion":
            return f"Top 5 {niche.title()} Products You Can't Miss"
        else:
            return f"Ultimate Guide to {niche.title()} in 2025"
    try:
        response = await gemini_model.generate_content_async(prompt)
        title = response.text.strip()
        # Basic cleanup
        if title.startswith('"') and title.endswith('"'): title = title[1:-1]
        if title.startswith("'") and title.endswith("'"): title = title[1:-1]
        logger.debug(f"[{agent_id}] Generated title: '{title}'")
        return title
    except Exception as e:
        logger.warning(f"[{agent_id}] LLM title generation failed for niche '{niche}', falling back to mock. Error: {e}")
        # Fallback mock logic
        if focus == "conversion":
            return f"Top 5 {niche.title()} Products You Can't Miss"
        else:
            return f"Ultimate Guide to {niche.title()} in 2025"

async def _generate_article_body(niche: str, focus: str) -> str:
    """Generates an article body using the shared Gemini model."""
    agent_id = "content_generation_adk"
    prompt = f"Write a compelling {'conversion-focused' if focus == 'conversion' else 'informative'} affiliate marketing article body (around 200-300 words) about the '{niche}' niche. Focus on providing value and seamlessly integrating potential affiliate links (use placeholders like '[Product Link]')."
    if not gemini_model:
        logger.warning(f"[{agent_id}] Gemini model not available for body generation, falling back to mock.")
        # Fallback mock logic
        intro = f"In this article, we explore the latest trends and insights in {niche}."
        call_to_action = "Don't miss out..." if focus == "conversion" else "Stay informed..."
        return f"{intro}\n\n[Detailed content about {niche}...]\n\n{call_to_action}"
    try:
        response = await gemini_model.generate_content_async(prompt)
        body = response.text.strip()
        logger.debug(f"[{agent_id}] Generated article body (first 50 chars): '{body[:50]}...'")
        return body
    except Exception as e:
        logger.warning(f"[{agent_id}] LLM article body generation failed for niche '{niche}', falling back to mock. Error: {e}")
        # Fallback mock logic
        intro = f"In this article, we explore the latest trends and insights in {niche}."
        call_to_action = "Don't miss out..." if focus == "conversion" else "Stay informed..."
        return f"{intro}\n\n[Detailed content about {niche}...]\n\n{call_to_action}"

# --- Synchronous Helpers (Directly from Prototype - no LLM needed) ---

def _generate_module_title(niche: str, module_number: int) -> str:
    """Generates a module title for a course."""
    topics = ["Fundamentals", "Advanced Techniques", "Tools", "Monetization", "Scaling", "Automation", "Case Studies"]
    topic = topics[(module_number - 1) % len(topics)]
    return f"{topic} in {niche.title()}"

def _generate_lessons(niche: str, module_number: int) -> List[str]:
    """Generates lesson titles for a module."""
    return [
        f"Intro to Module {module_number}", f"Key Concept A for {niche.title()}",
        f"Practical Application B", f"Exercise {module_number}", f"Summary & Next Steps"
    ]

def _generate_headline(product_name: str, niche: str, style: str) -> str:
    """Generates a marketing headline."""
    if style == "persuasive": return f"Unlock {niche.title()} Potential with {product_name}!"
    if style == "informative": return f"How {product_name} Solves {niche.title()} Challenges"
    return f"Level Up Your {niche.title()} Game with {product_name}" # casual

def _generate_description(product_name: str, niche: str, style: str) -> str:
    """Generates a marketing description."""
    if style == "persuasive": return f"Stop struggling. {product_name} delivers results. Try it!"
    if style == "informative": return f"Learn about {product_name}, designed for {niche}. Features X, Y, Z."
    return f"Tired of {niche} tools? {product_name} is different. Easy & powerful." # casual


# --- Instantiate the ADK Agent ---
# This instance will be discovered by `adk web`
agent = Agent(
    name="content_generation_adk", # ADK specific name
    description="Generates various types of content (affiliate, course outlines, marketing copy) using ADK tools.",
    # No model needed directly for Agent, tools handle LLM calls if necessary
    tools=[
        create_affiliate_content_tool,
        create_course_outline_tool,
        generate_marketing_copy_tool,
    ],
)

# Removed A2A server specific code (__init__, run_async, if __name__ == "__main__")
