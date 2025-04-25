import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

from google.adk.runtime import InvocationContext, Event
from python_a2a import skill

from agents.base_agent import BaseSpecializedAgent
from app.config import settings

logger = logging.getLogger(__name__)

class ContentGenerationAgent(BaseSpecializedAgent):
    """
    Agent for generating various types of content using an LLM.
    Implements A2A protocol for agent communication.

    Handles tasks like creating affiliate marketing content, digital course outlines,
    and marketing copy based on instructions provided in the InvocationContext.
    """

    def __init__(
        self,
        name: str = "content_generator",
        description: str = "Generates various types of content using an LLM",
        model_name: Optional[str] = None,
        port: Optional[int] = None,
        **kwargs: Any,
    ):
        """
        Initialize the ContentGenerationAgent.

        Args:
            name: The name of the agent.
            description: The description of the agent.
            model_name: The name of the model to use. Defaults to settings.GEMINI_MODEL_NAME.
            port: The port to run the A2A server on. Defaults to settings.CONTENT_GENERATION_AGENT_URL port.
            **kwargs: Additional arguments for BaseSpecializedAgent.
        """
        # Extract port from URL if not provided
        if port is None and settings.CONTENT_GENERATION_AGENT_URL:
            try:
                port = int(settings.CONTENT_GENERATION_AGENT_URL.split(':')[-1])
            except (ValueError, IndexError):
                port = 8003  # Default port

        super().__init__(
            name=name,
            description=description,
            model_name=model_name,
            port=port,
            **kwargs
        )

        logger.info(f"ContentGenerationAgent initialized with port: {self.port}")

    @skill(
        name="create_affiliate_content",
        description="Generate affiliate marketing content",
        tags=["content", "affiliate", "marketing"]
    )
    async def create_affiliate_content(self, niche: str, quantity: int = 3, focus: str = "value") -> List[Dict[str, Any]]:
        """
        Generate affiliate marketing content.

        Args:
            niche: The niche for the content.
            quantity: The number of content pieces to generate.
            focus: The focus of the content (value or conversion).

        Returns:
            A list of content pieces.
        """
        logger.info(f"Generating {quantity} affiliate content pieces for '{niche}' (focus: {focus})")
        return await self._generate_affiliate_content(niche, quantity, focus)

    @skill(
        name="create_course_outline",
        description="Generate a digital course outline",
        tags=["content", "course", "outline"]
    )
    async def create_course_outline(self, niche: str, modules: int = 5) -> Dict[str, Any]:
        """
        Generate a digital course outline.

        Args:
            niche: The niche for the course.
            modules: The number of modules in the course.

        Returns:
            A course outline.
        """
        logger.info(f"Generating course outline for '{niche}' ({modules} modules)")
        return self._generate_course_outline(niche, modules)

    @skill(
        name="generate_marketing_copy",
        description="Generate marketing copy",
        tags=["content", "marketing", "copy"]
    )
    async def generate_marketing_copy(self, product_name: str, niche: str, style: str = "persuasive") -> Dict[str, str]:
        """
        Generate marketing copy.

        Args:
            product_name: The name of the product.
            niche: The niche for the marketing copy.
            style: The style of the marketing copy.

        Returns:
            Marketing copy.
        """
        logger.info(f"Generating {style} marketing copy for '{product_name}' in '{niche}'")
        return self._generate_marketing_copy(product_name, niche, style)

    async def run_async(self, context: InvocationContext) -> Optional[Event]:
        """
        Executes a content generation task based on the invocation context.
        Maintained for backward compatibility with ADK.

        The context should contain an 'action' key specifying the type of content
        to generate (e.g., 'create_affiliate_content', 'create_course_outline',
        'generate_marketing_copy') and relevant parameters for that action.

        Args:
            context: The invocation context containing task details.

        Returns:
            An Event containing the generated content or an error, or None if no
            specific action is requested or an error occurs before event creation.
        """
        # Extract action and parameters from context
        action = None
        if hasattr(context, 'get_input'):
            action = context.get_input("action")
            task_id = context.invocation_id
        elif hasattr(context, 'data') and isinstance(context.data, dict):
            action = context.data.get("action")
            task_id = getattr(context, 'invocation_id', str(id(context)))
        elif hasattr(context, 'input_event') and hasattr(context.input_event, 'data'):
            action = context.input_event.data.get("action")
            task_id = getattr(context.input_event, 'invocation_id', str(id(context)))
        else:
            logger.warning(f"Could not extract action from context: {context}")
            return Event(data={"error": "Could not extract action from context"})

        results = None
        error_message = None

        logger.info(f"[{self.name}] Received task: {action} (ID: {task_id})")

        try:
            if action == "create_affiliate_content":
                # Extract parameters
                niche = "technology"
                quantity = 3
                focus = "value"

                if hasattr(context, 'get_input'):
                    niche = context.get_input("niche", niche)
                    quantity = context.get_input("quantity", quantity)
                    focus = context.get_input("focus", focus)
                elif hasattr(context, 'data') and isinstance(context.data, dict):
                    niche = context.data.get("niche", niche)
                    quantity = context.data.get("quantity", quantity)
                    focus = context.data.get("focus", focus)
                elif hasattr(context, 'input_event') and hasattr(context.input_event, 'data'):
                    niche = context.input_event.data.get("niche", niche)
                    quantity = context.input_event.data.get("quantity", quantity)
                    focus = context.input_event.data.get("focus", focus)

                # Use the A2A skill
                results = await self.create_affiliate_content(niche, quantity, focus)

            elif action == "create_course_outline":
                # Extract parameters
                niche = "technology"
                modules = 5

                if hasattr(context, 'get_input'):
                    niche = context.get_input("niche", niche)
                    modules = context.get_input("modules", modules)
                elif hasattr(context, 'data') and isinstance(context.data, dict):
                    niche = context.data.get("niche", niche)
                    modules = context.data.get("modules", modules)
                elif hasattr(context, 'input_event') and hasattr(context.input_event, 'data'):
                    niche = context.input_event.data.get("niche", niche)
                    modules = context.input_event.data.get("modules", modules)

                # Use the A2A skill
                results = await self.create_course_outline(niche, modules)

            elif action == "generate_marketing_copy":
                # Extract parameters
                product_name = "Product"
                niche = "technology"
                style = "persuasive"

                if hasattr(context, 'get_input'):
                    product_name = context.get_input("product_name", product_name)
                    niche = context.get_input("niche", niche)
                    style = context.get_input("style", style)
                elif hasattr(context, 'data') and isinstance(context.data, dict):
                    product_name = context.data.get("product_name", product_name)
                    niche = context.data.get("niche", niche)
                    style = context.data.get("style", style)
                elif hasattr(context, 'input_event') and hasattr(context.input_event, 'data'):
                    product_name = context.input_event.data.get("product_name", product_name)
                    niche = context.input_event.data.get("niche", niche)
                    style = context.input_event.data.get("style", style)

                # Use the A2A skill
                results = await self.generate_marketing_copy(product_name, niche, style)

            else:
                error_message = f"Unknown action requested: {action}"
                logger.warning(f"[{self.name}] {error_message} (ID: {task_id})")

        except Exception as e:
            error_message = f"Error executing task '{action}': {e}"
            logger.exception(f"[{self.name}] {error_message} (ID: {task_id})", exc_info=True)

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
            logger.warning(f"[{self.name}] Task {action} (ID: {task_id}) finished without explicit results or error.")

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
            # Use the LlmAgent's client
            title = await self.llm_client.generate_text_async(prompt=prompt)
            # Accessing text might differ based on the exact LLM client response structure
            # Assuming response.text or similar attribute holds the generated text
            # title = response.text.strip() if hasattr(response, 'text') else str(response).strip() # generate_text_async returns string directly
            title = title.strip() # Clean whitespace
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
            # Assuming max_tokens or similar parameter can be passed via generate_text_async options
            # Note: ADK's generate_text_async might not directly support generation_config like this.
            # If specific config is needed, might need to use generate_content_async or adjust model defaults.
            # For now, assume default config is sufficient or handled by model init.
            body = await self.llm_client.generate_text_async(prompt=prompt) # Removed generation_config for now
            # body = response.text.strip() if hasattr(response, 'text') else str(response).strip() # generate_text_async returns string directly
            body = body.strip() # Clean whitespace
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

# Example of how to run this agent as a standalone A2A server
if __name__ == "__main__":
    # Create the agent
    agent = ContentGenerationAgent()

    # Run the A2A server
    agent.run_server(host="0.0.0.0", port=agent.port or 8003)