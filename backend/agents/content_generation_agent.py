import asyncio
import logging
import os
import argparse
from datetime import datetime
from typing import Dict, List, Any, Optional

import uvicorn
from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel, Field

# Assuming ADK is installed and configured
from google.adk.agents import LlmAgent
from google.adk.llm import Gemini # Assuming Gemini is the intended LLM client
from google.adk.runtime import InvocationContext, Event

# Configure logging
# Use logfire if configured globally, otherwise standard logging
try:
    import logfire
    # Assuming logfire is configured elsewhere
    logger = logfire
except ImportError:
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO"))

# --- Pydantic Models ---

class ContentGenInput(BaseModel):
    """Input model for the ContentGenerationAgent /invoke endpoint."""
    action: str = Field(description="The type of content generation task (e.g., 'create_affiliate_content', 'create_course_outline', 'generate_marketing_copy').")
    # Include all potential parameters used by different actions
    niche: Optional[str] = Field("technology", description="The niche or topic for content generation.")
    quantity: Optional[int] = Field(3, description="Number of items to generate (e.g., affiliate articles).")
    focus: Optional[str] = Field("value", description="Focus for affiliate content ('value' or 'conversion').")
    modules: Optional[int] = Field(5, description="Number of modules for a course outline.")
    product_name: Optional[str] = Field("Product", description="Name of the product for marketing copy.")
    style: Optional[str] = Field("persuasive", description="Style for marketing copy (e.g., 'persuasive', 'informative', 'casual').")
    # Add any other parameters your agent might need based on actions

class ContentGenOutput(BaseModel):
    """Output model for the ContentGenerationAgent /invoke endpoint."""
    task_id: str
    action: str
    timestamp: str
    success: bool
    results: Optional[Any] = None # Can be List[Dict], Dict, etc. depending on action
    error: Optional[str] = None


# --- Agent Class ---

class ContentGenerationAgent(LlmAgent):
    """
    ADK-based agent for generating various types of content using an LLM.
    Handles tasks like creating affiliate marketing content, digital course outlines,
    and marketing copy based on instructions provided in the InvocationContext.
    """

    def __init__(self,
                 agent_id: str = "content-generation-agent",
                 model_name: Optional[str] = None):
        """
        Initializes the ContentGenerationAgent.

        Args:
            agent_id: The unique identifier for this agent instance.
            model_name: The name of the Gemini model to use. Reads from GEMINI_MODEL_NAME env var if None.
        """
        # Get config from environment variables
        effective_model_name = model_name or os.environ.get('GEMINI_MODEL_NAME', 'gemini-1.5-flash-latest') # Default model
        self.model_name = effective_model_name

        # Initialize the ADK Gemini model
        # Assumes GEMINI_API_KEY is configured via environment variable for ADK
        try:
            adk_model = Gemini(model=self.model_name)
        except Exception as e:
            logger.error(f"Failed to initialize Gemini model '{self.model_name}': {e}", exc_info=True)
            adk_model = None # Handle initialization failure

        # Call super().__init__ from LlmAgent
        super().__init__(
            agent_id=agent_id,
            model=adk_model
        )

        if not adk_model:
             logger.error("ContentGenerationAgent initialized WITHOUT a valid LLM client due to model initialization failure.")
        else:
            logger.info(f"Content Generation Agent ({self.agent_id}) initialized with model: {self.model_name}.")


    async def run_async(self, context: InvocationContext) -> Event:
        """
        Executes a content generation task based on the invocation context data.

        Args:
            context: The invocation context containing task details in context.data.

        Returns:
            An Event containing the generated content or an error.
        """
        if not isinstance(context.data, dict):
            error_msg = f"Input data is not a dictionary: {type(context.data)}"
            logger.error(error_msg)
            # Use context.create_error_event if available, otherwise manually create
            return context.create_event(event_type="adk.agent.error", data={"error": error_msg}, metadata={"status": "error"})


        action = context.data.get("action")
        task_id = context.invocation_id # Use invocation_id as task identifier
        results = None
        error_message = None

        logger.info(f"[{self.agent_id}] Received task: {action} (ID: {task_id})")

        try:
            if action == "create_affiliate_content":
                niche = context.data.get("niche", "technology")
                quantity = context.data.get("quantity", 3)
                focus = context.data.get("focus", "value")
                results = await self._generate_affiliate_content(niche, quantity, focus)

            elif action == "create_course_outline":
                niche = context.data.get("niche", "technology")
                modules = context.data.get("modules", 5)
                results = self._generate_course_outline(niche, modules) # Keep sync for now

            elif action == "generate_marketing_copy":
                product_name = context.data.get("product_name", "Product")
                niche = context.data.get("niche", "technology")
                style = context.data.get("style", "persuasive")
                results = self._generate_marketing_copy(product_name, niche, style) # Keep sync for now

            else:
                error_message = f"Unknown action requested: {action}"
                logger.warning(f"[{self.agent_id}] {error_message} (ID: {task_id})")

        except Exception as e:
            error_message = f"Error executing task '{action}': {e}"
            logger.exception(f"[{self.agent_id}] {error_message} (ID: {task_id})", exc_info=True)

        # Create and return the event using context helper
        event_data = {
            "task_id": task_id,
            "action": action,
            "timestamp": datetime.now().isoformat(),
        }
        if error_message:
            event_data["error"] = error_message
            return context.create_event(event_type="adk.agent.error", data=event_data, metadata={"status": "error"})
        elif results is not None:
            event_data["results"] = results
            return context.create_event(event_type="adk.agent.result", data=event_data, metadata={"status": "success"})
        else:
            # Task known but produced no results/error (e.g., unknown action handled above)
            event_data["error"] = "Task completed without results or explicit error."
            logger.warning(f"[{self.agent_id}] Task {action} (ID: {task_id}) finished without explicit results or error.")
            return context.create_event(event_type="adk.agent.error", data=event_data, metadata={"status": "error"})


    # --- Helper Methods (Adapted from Prototype) ---
    # ... (Keep existing helper methods _generate_affiliate_content, _generate_course_outline, etc.) ...
    # --- Make sure async helpers use self.llm_client ---

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
        if not self.llm_client:
            logger.warning(f"[{self.agent_id}] LLM client not available, falling back to mock title.")
            return f"Mock Title for {niche.title()} ({focus})"

        prompt = f"Generate a catchy {'conversion-focused' if focus == 'conversion' else 'informative'} title for an affiliate marketing article in the '{niche}' niche. Provide only the title text."
        try:
            title = await self.llm_client.generate_text_async(prompt=prompt)
            title = title.strip()
            if title.startswith('"') and title.endswith('"'): title = title[1:-1]
            if title.startswith("'") and title.endswith("'"): title = title[1:-1]
            logger.debug(f"[{self.agent_id}] Generated title: '{title}'")
            return title
        except Exception as e:
            logger.warning(f"[{self.agent_id}] LLM title generation failed for niche '{niche}', falling back to mock. Error: {e}")
            if focus == "conversion": return f"Top 5 {niche.title()} Products You Can't Miss"
            else: return f"Ultimate Guide to {niche.title()} in 2025"

    async def _generate_article_body(self, niche: str, focus: str) -> str:
        """Generates an article body using the LLM."""
        if not self.llm_client:
            logger.warning(f"[{self.agent_id}] LLM client not available, falling back to mock body.")
            return f"Mock body content about {niche.title()} focusing on {focus}."

        prompt = f"Write a compelling {'conversion-focused' if focus == 'conversion' else 'informative'} affiliate marketing article body (around 200-300 words) about the '{niche}' niche. Focus on providing value and seamlessly integrating potential affiliate links (use placeholders like '[Product Link]')."
        try:
            body = await self.llm_client.generate_text_async(prompt=prompt)
            body = body.strip()
            logger.debug(f"[{self.agent_id}] Generated article body (first 50 chars): '{body[:50]}...'")
            return body
        except Exception as e:
            logger.warning(f"[{self.agent_id}] LLM article body generation failed for niche '{niche}', falling back to mock. Error: {e}")
            intro = f"In this article, we explore the latest trends and insights in {niche}."
            if focus == "conversion": call_to_action = "Don't miss out on these exclusive deals! Check them out: [Product Link]"
            else: call_to_action = "Stay informed with these tips."
            return f"{intro}\n\n[Detailed content about {niche} trends/tips...]\n\n{call_to_action}"

    # --- Synchronous Helpers (Keep as is for now) ---
    def _generate_module_title(self, niche: str, module_number: int) -> str:
        topics = ["Fundamentals", "Advanced Techniques", "Tools", "Monetization", "Scaling", "Automation", "Case Studies"]
        topic = topics[(module_number - 1) % len(topics)]
        return f"{topic} in {niche.title()}"

    def _generate_lessons(self, niche: str, module_number: int) -> List[str]:
        return [f"Intro to Module {module_number}", f"Key Concept A for {niche.title()}", f"Practical App B in {niche.title()}", f"Exercise {module_number}", f"Module {module_number} Summary"]

    def _generate_headline(self, product_name: str, niche: str, style: str) -> str:
        if style == "persuasive": return f"Unlock {niche.title()} Potential with {product_name}!"
        elif style == "informative": return f"How {product_name} Solves {niche.title()} Challenges"
        else: return f"Level Up Your {niche.title()} with {product_name}"

    def _generate_description(self, product_name: str, niche: str, style: str) -> str:
        if style == "persuasive": return f"Stop struggling with {niche}. {product_name} provides the breakthrough. Experience rapid growth. Try it!"
        elif style == "informative": return f"Learn about {product_name}, the solution for {niche} pros. Features X, Y, Z."
        else: return f"Tired of usual {niche} tools? {product_name} is here. Easy, powerful. See the hype."


# --- FastAPI Server Setup ---

app = FastAPI(title="ContentGenerationAgent A2A Server")

# Instantiate the agent (reads env vars internally)
content_gen_agent_instance = ContentGenerationAgent()

@app.post("/invoke", response_model=ContentGenOutput) # Use output model
async def invoke_agent(request: ContentGenInput = Body(...)):
    """
    A2A endpoint to invoke the ContentGenerationAgent.
    Expects JSON body with 'action' and relevant parameters.
    """
    logger.info(f"ContentGenerationAgent /invoke called for action: {request.action}")
    # Create InvocationContext, passing data directly
    context = InvocationContext(agent_id="content-generation-agent", data=request.model_dump())

    try:
        result_event = await content_gen_agent_instance.run_async(context)
        # The run_async method now returns the full event data structure
        if result_event and isinstance(result_event.data, dict):
            # Ensure the response matches the output model structure
            output_data = ContentGenOutput(**result_event.data)
            if output_data.success:
                 logger.info(f"ContentGenerationAgent returning success result for action: {request.action}")
                 return output_data
            else:
                 logger.error(f"ContentGenerationAgent run_async returned error: {output_data.error}")
                 # Return the structured error response
                 raise HTTPException(status_code=500, detail=output_data.model_dump()) # Send full error structure
        else:
            logger.error("ContentGenerationAgent run_async returned None or invalid data")
            raise HTTPException(status_code=500, detail="Agent execution failed to return a valid event.")
    except HTTPException as http_exc:
        raise http_exc # Re-raise FastAPI exceptions
    except Exception as e:
        logger.error(f"Error during agent invocation: {e}", exc_info=True)
        # Return a structured error consistent with ContentGenOutput
        error_output = ContentGenOutput(
            task_id=context.invocation_id,
            action=request.action,
            timestamp=datetime.now().isoformat(),
            success=False,
            error=f"Internal server error: {e}"
        )
        raise HTTPException(status_code=500, detail=error_output.model_dump())


@app.get("/health")
async def health_check():
    return {"status": "ok"}

# --- Main execution block ---

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the ContentGenerationAgent A2A server.")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind the server to.")
    parser.add_argument("--port", type=int, default=8083, help="Port to run the server on (default from compose).") # Default matches compose
    args = parser.parse_args()

    print(f"Starting ContentGenerationAgent A2A server on {args.host}:{args.port}")

    uvicorn.run(app, host=args.host, port=args.port)