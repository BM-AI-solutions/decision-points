import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

from google.adk.agents import LlmAgent
from google.adk.runtime import InvocationContext, Event

logger = logging.getLogger(__name__)

class ContentGenerationAgent(LlmAgent):
    """
    ADK-based agent for generating various types of content using an LLM.

    Handles tasks like creating affiliate marketing content, digital course outlines,
    and marketing copy based on instructions provided in the InvocationContext.
    """

    def __init__(self, agent_id: str = "content-generation-agent"):
        """
        Initializes the ContentGenerationAgent.

        Args:
            agent_id: The unique identifier for this agent instance.
        """
        super().__init__(agent_id=agent_id)
        logger.info(f"Content Generation Agent ({self.agent_id}) initialized.")

    async def run_async(self, context: InvocationContext) -> Optional[Event]:
        """
        Executes a content generation task based on the invocation context.

        The context should contain an 'action' key specifying the type of content
        to generate (e.g., 'create_affiliate_content', 'create_course_outline',
        'generate_marketing_copy') and relevant parameters for that action.

        Args:
            context: The invocation context containing task details.

        Returns:
            An Event containing the generated content or an error, or None if no
            specific action is requested or an error occurs before event creation.
        """
        action = context.get_input("action")
        task_id = context.invocation_id # Use invocation_id as task identifier
        results = None
        error_message = None

        logger.info(f"[{self.agent_id}] Received task: {action} (ID: {task_id})")

        try:
            if action == "create_affiliate_content":
                niche = context.get_input("niche", "technology")
                quantity = context.get_input("quantity", 3)
                focus = context.get_input("focus", "value")
                results = await self._generate_affiliate_content(niche, quantity, focus)

            elif action == "create_course_outline":
                niche = context.get_input("niche", "technology")
                modules = context.get_input("modules", 5)
                # Note: Course outline generation in prototype was synchronous, adapting.
                # If LLM is needed here in future, make helper async.
                results = self._generate_course_outline(niche, modules)

            elif action == "generate_marketing_copy":
                product_name = context.get_input("product_name", "Product")
                niche = context.get_input("niche", "technology")
                style = context.get_input("style", "persuasive")
                # Note: Marketing copy generation in prototype was synchronous, adapting.
                # If LLM is needed here in future, make helper async.
                results = self._generate_marketing_copy(product_name, niche, style)

            else:
                error_message = f"Unknown action requested: {action}"
                logger.warning(f"[{self.agent_id}] {error_message} (ID: {task_id})")

        except Exception as e:
            error_message = f"Error executing task '{action}': {e}"
            logger.exception(f"[{self.agent_id}] {error_message} (ID: {task_id})", exc_info=True)

        # Create and return the event
        event_data = {
            "task_id": task_id,
            "action": action,
            "timestamp": datetime.now().isoformat(),
        }
        if error_message:
            event_data["success"] = False
            event_data["error"] = error_message
        elif results is not None:
            event_data["success"] = True
            event_data["results"] = results
        else:
            # Should not happen if action is known and no exception occurred, but handle defensively
            event_data["success"] = False
            event_data["error"] = "Task completed without results or error."
            logger.warning(f"[{self.agent_id}] Task {action} (ID: {task_id}) finished without explicit results or error.")

        return Event(data=event_data)


    # --- Helper Methods (Adapted from Prototype) ---

    async def _generate_affiliate_content(self, niche: str, quantity: int, focus: str) -> List[Dict[str, Any]]:
        """Generates multiple affiliate marketing content pieces."""
        logger.info(f"[{self.agent_id}] Generating {quantity} affiliate content pieces for '{niche}' (focus: {focus})")
        contents = []
        for _ in range(quantity):
            title = await self._generate_title(niche, focus)
            body = await self._generate_article_body(niche, focus)
            contents.append({
                "title": title,
                "body": body,
                "created_at": datetime.now().isoformat()
            })
        logger.info(f"[{self.agent_id}] Finished generating affiliate content for '{niche}'.")
        return contents

    def _generate_course_outline(self, niche: str, modules: int) -> Dict[str, Any]:
        """Generates a digital course outline (currently synchronous)."""
        logger.info(f"[{self.agent_id}] Generating course outline for '{niche}' ({modules} modules)")
        outline = {
            "title": f"Mastering {niche.title()}",
            "modules": []
        }
        for i in range(1, modules + 1):
            module_title = f"Module {i}: {self._generate_module_title(niche, i)}"
            outline["modules"].append({
                "title": module_title,
                "lessons": self._generate_lessons(niche, i) # Assuming synchronous helper
            })
        logger.info(f"[{self.agent_id}] Finished generating course outline for '{niche}'.")
        return outline

    def _generate_marketing_copy(self, product_name: str, niche: str, style: str) -> Dict[str, str]:
        """Generates marketing copy (currently synchronous)."""
        logger.info(f"[{self.agent_id}] Generating {style} marketing copy for '{product_name}' in '{niche}'")
        headline = self._generate_headline(product_name, niche, style) # Assuming synchronous helper
        description = self._generate_description(product_name, niche, style) # Assuming synchronous helper
        copy = {
            "headline": headline,
            "description": description
        }
        logger.info(f"[{self.agent_id}] Finished generating marketing copy for '{product_name}'.")
        return copy

    async def _generate_title(self, niche: str, focus: str) -> str:
        """Generates a content title using the LLM."""
        prompt = f"Generate a catchy {'conversion-focused' if focus == 'conversion' else 'informative'} title for an affiliate marketing article in the '{niche}' niche. Provide only the title text."
        try:
            response = await self.llm.generate_content_async(prompt)
            # Accessing text might differ based on the exact LLM client response structure
            # Assuming response.text or similar attribute holds the generated text
            title = response.text.strip() if hasattr(response, 'text') else str(response).strip()
            # Basic cleanup: remove quotes if the LLM wrapped the title
            if title.startswith('"') and title.endswith('"'):
                title = title[1:-1]
            if title.startswith("'") and title.endswith("'"):
                title = title[1:-1]
            logger.debug(f"[{self.agent_id}] Generated title: '{title}'")
            return title
        except Exception as e:
            logger.warning(f"[{self.agent_id}] LLM title generation failed for niche '{niche}', falling back to mock. Error: {e}")
            # Fallback mock logic from prototype
            if focus == "conversion":
                return f"Top 5 {niche.title()} Products You Can't Miss"
            else:
                return f"Ultimate Guide to {niche.title()} in 2025"

    async def _generate_article_body(self, niche: str, focus: str) -> str:
        """Generates an article body using the LLM."""
        prompt = f"Write a compelling {'conversion-focused' if focus == 'conversion' else 'informative'} affiliate marketing article body (around 200-300 words) about the '{niche}' niche. Focus on providing value and seamlessly integrating potential affiliate links (use placeholders like '[Product Link]')."
        try:
            # Assuming max_tokens or similar parameter can be passed via generate_content_async options
            response = await self.llm.generate_content_async(prompt, generation_config={"max_output_tokens": 350})
            body = response.text.strip() if hasattr(response, 'text') else str(response).strip()
            logger.debug(f"[{self.agent_id}] Generated article body (first 50 chars): '{body[:50]}...'")
            return body
        except Exception as e:
            logger.warning(f"[{self.agent_id}] LLM article body generation failed for niche '{niche}', falling back to mock. Error: {e}")
            # Fallback mock logic from prototype
            intro = f"In this article, we explore the latest trends and insights in {niche}."
            if focus == "conversion":
                call_to_action = "Don't miss out on these exclusive deals and offers! Check them out here: [Product Link]"
            else:
                call_to_action = "Stay informed and ahead in your niche with these tips."
            return f"{intro}\n\n[Detailed content about {niche} trends/tips goes here...]\n\n{call_to_action}"

    # --- Synchronous Helpers (Directly from Prototype - consider making async if LLM needed) ---

    def _generate_module_title(self, niche: str, module_number: int) -> str:
        """Generates a module title for a course."""
        topics = [
            "Fundamentals", "Advanced Techniques", "Tools & Platforms",
            "Monetization Strategies", "Scaling Up", "Automation", "Case Studies"
        ]
        topic = topics[(module_number - 1) % len(topics)]
        return f"{topic} in {niche.title()}"

    def _generate_lessons(self, niche: str, module_number: int) -> List[str]:
        """Generates lesson titles for a module."""
        # Simple mock generation
        base_lessons = [
            f"Introduction to Module {module_number}",
            f"Key Concept A for {niche.title()}",
            f"Practical Application B in {niche.title()}",
            f"Exercise/Walkthrough for Module {module_number}",
            f"Module {module_number} Summary & Next Steps"
        ]
        return base_lessons

    def _generate_headline(self, product_name: str, niche: str, style: str) -> str:
        """Generates a marketing headline."""
        # Simple mock generation based on style
        if style == "persuasive":
            return f"Unlock Your Potential in {niche.title()} with {product_name}!"
        elif style == "informative":
            return f"Discover How {product_name} Solves Key Challenges in {niche.title()}"
        else: # casual
            return f"Level Up Your {niche.title()} Game with {product_name}"

    def _generate_description(self, product_name: str, niche: str, style: str) -> str:
        """Generates a marketing description."""
        # Simple mock generation based on style
        if style == "persuasive":
            return f"Stop struggling with {niche}. {product_name} provides the breakthrough you need. Experience rapid growth and efficiency. Try it now!"
        elif style == "informative":
            return f"Learn about {product_name}, the comprehensive solution designed for {niche} professionals. Features include X, Y, and Z to streamline your workflow."
        else: # casual
            return f"Tired of the usual {niche} tools? {product_name} is here to shake things up. Easy to use, powerful results. See what the hype is about."