# NOTE: For production, consider offloading long-running content generation tasks to a background queue (e.g., Celery, RQ, or similar) to avoid blocking requests.

"""
Content Generation Agent - Specialized AI agent for content creation.

This module implements the Content Generation Agent, which:
1. Generates affiliate marketing content
2. Creates digital course outlines
3. Produces marketing copy and assets
4. Leverages LLM APIs (OpenRouter, Gemini) for high-quality content
5. Reports results back to the Orchestrator
"""

import json
import logging
import random
import time
from datetime import datetime
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
from backend.app import socketio

logger = logging.getLogger(__name__)

class ContentGenerationAgent:
    """
    The Content Generation Agent creates content for various business models,
    including affiliate marketing, digital products, and SaaS.
    """
    
    def __init__(self, llm_api=None):
        """
        Initialize the Content Generation Agent.
        
        Args:
            llm_api: Optional LLM API client (e.g., OpenRouter, Gemini)
        """
        self.llm_api = llm_api
        logger.info("Content Generation Agent initialized")
    
    async def generate_affiliate_content(self, niche: str, quantity: int = 3, focus: str = "value") -> List[Dict[str, Any]]:
        """
        Generate affiliate marketing content pieces.
        
        Args:
            niche: Market niche
            quantity: Number of content pieces
            focus: Content focus ("value" or "conversion")
            
        Returns:
            List of content dictionaries
        """
        socketio.emit('content_status', {
            'status': 'started',
            'niche': niche,
            'quantity': quantity,
            'focus': focus,
            'timestamp': datetime.now().isoformat()
        })

        logger.info(f"Generating {quantity} affiliate content pieces for {niche} with focus on {focus}")
        contents = []
        for _ in range(quantity):
            title = await self._generate_title(niche, focus)
            body = await self._generate_article_body(niche, focus)
            contents.append({
                "title": title,
                "body": body,
                "created_at": datetime.now().isoformat()
            })
        socketio.emit('content_status', {
            'status': 'completed',
            'niche': niche,
            'quantity': quantity,
            'focus': focus,
            'timestamp': datetime.now().isoformat(),
            'contents': contents
        })

        return contents
    
    def generate_course_outline(self, niche: str, modules: int = 5) -> Dict[str, Any]:
        """
        Generate a digital course outline.
        
        Args:
            niche: Course niche
            modules: Number of modules
            
        Returns:
            Course outline dictionary
        """
        logger.info(f"Generating course outline for {niche} with {modules} modules")
        outline = {
            "title": f"Mastering {niche.title()}",
            "modules": []
        }
        for i in range(1, modules + 1):
            module_title = f"Module {i}: {self._generate_module_title(niche, i)}"
            outline["modules"].append({
                "title": module_title,
                "lessons": self._generate_lessons(niche, i)
            })
        return outline
    
    def generate_marketing_copy(self, product_name: str, niche: str, style: str = "persuasive") -> Dict[str, str]:
        """
        Generate marketing copy for a product.
        
        Args:
            product_name: Name of the product
            niche: Product niche
            style: Copy style ("persuasive", "informative", "casual")
            
        Returns:
            Dictionary with headline and description
        """
        logger.info(f"Generating {style} marketing copy for {product_name} in {niche}")
        headline = self._generate_headline(product_name, niche, style)
        description = self._generate_description(product_name, niche, style)
        return {
            "headline": headline,
            "description": description
        }
    
    def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a content generation task assigned by the Orchestrator.
        
        Args:
            task: Task dictionary
            
        Returns:
            Results dictionary
        """
        action = task.get("action")
        try:
            if action == "create_affiliate_content":
                niche = task.get("niche", "technology")
                quantity = task.get("quantity", 3)
                focus = task.get("focus", "value")
                contents = self.generate_affiliate_content(niche, quantity, focus)
                return {
                    "task_id": task.get("id", "unknown"),
                    "action": action,
                    "results": contents,
                    "success": True,
                    "timestamp": datetime.now().isoformat()
                }
            elif action == "create_course_outline":
                niche = task.get("niche", "technology")
                modules = task.get("modules", 5)
                outline = self.generate_course_outline(niche, modules)
                return {
                    "task_id": task.get("id", "unknown"),
                    "action": action,
                    "results": outline,
                    "success": True,
                    "timestamp": datetime.now().isoformat()
                }
            elif action == "generate_marketing_copy":
                product_name = task.get("product_name", "Product")
                niche = task.get("niche", "technology")
                style = task.get("style", "persuasive")
                copy = self.generate_marketing_copy(product_name, niche, style)
                return {
                    "task_id": task.get("id", "unknown"),
                    "action": action,
                    "results": copy,
                    "success": True,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                logger.warning(f"Unknown content generation action: {action}")
                return {
                    "task_id": task.get("id", "unknown"),
                    "action": action,
                    "success": False,
                    "error": f"Unknown action: {action}",
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            logger.error(f"Error executing content generation task: {e}")
            return {
                "task_id": task.get("id", "unknown"),
                "action": action,
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def _generate_title(self, niche: str, focus: str) -> str:
        """
        Generate a content title, using LLM if available.
        """
        if self.llm_api:
            prompt = f"Generate a catchy {'conversion-focused' if focus=='conversion' else 'informative'} title for affiliate marketing in the {niche} niche."
            try:
                response = await self.llm_api.generate_content(prompt)
                if response:
                    return response.strip()
            except Exception as e:
                logger.warning(f"LLM title generation failed, falling back to mock. Error: {e}")
        # fallback mock
        if focus == "conversion":
            return f"Top 5 {niche.title()} Products You Can't Miss"
        else:
            return f"Ultimate Guide to {niche.title()} in 2025"
    
    async def _generate_article_body(self, niche: str, focus: str) -> str:
        """
        Generate a content article body, using LLM if available.
        """
        if self.llm_api:
            prompt = f"Write a compelling {'conversion-focused' if focus=='conversion' else 'informative'} affiliate marketing article about {niche}."
            try:
                response = await self.llm_api.generate_content(prompt, max_tokens=300)
                if response:
                    return response.strip()
            except Exception as e:
                logger.warning(f"LLM article body generation failed, falling back to mock. Error: {e}")
        # fallback mock
        intro = f"In this article, we explore the latest trends and insights in {niche}."
        if focus == "conversion":
            call_to_action = "Don't miss out on these exclusive deals and offers!"
        else:
            call_to_action = "Stay informed and ahead in your niche with these tips."
        return f"{intro}\n\n{call_to_action}"
    
    def _generate_module_title(self, niche: str, module_number: int) -> str:
        """
        Generate a module title for a course.
        """
        topics = [
            "Fundamentals", "Advanced Techniques", "Tools & Platforms",
            "Monetization Strategies", "Scaling Up", "Automation", "Case Studies"
        ]
        topic = topics[(module_number - 1) % len(topics)]
        return f"{topic} in {niche.title()}"
    
    def _generate_lessons(self, niche: str, module_number: int) -> List[str]:
        """
        Generate lesson titles for a module.
        """
        lessons = [
            f"Introduction to {niche.title()}",
            f"Key Concepts in {niche.title()}",
            f"Practical Applications of {niche.title()}",
            f"Common Challenges in {niche.title()}",
            f"Future Trends in {niche.title()}"
        ]
        return lessons
    
    def _generate_headline(self, product_name: str, niche: str, style: str) -> str:
        """
        Generate a marketing headline.
        """
        if style == "persuasive":
            return f"Unlock the Power of {product_name} for {niche.title()} Success!"
        elif style == "informative":
            return f"Everything You Need to Know About {product_name} in {niche.title()}"
        else:
            return f"Check Out {product_name} - The Latest in {niche.title()}"
    
    def _generate_description(self, product_name: str, niche: str, style: str) -> str:
        """
        Generate a marketing description.
        """
        if style == "persuasive":
            return f"Transform your {niche} journey with {product_name}. Get started today and see the difference!"
        elif style == "informative":
            return f"{product_name} offers comprehensive solutions for all your {niche} needs. Learn more inside."
        else:
            return f"{product_name} is making waves in {niche}. Don't miss out!"

# Example usage
if __name__ == "__main__":
    agent = ContentGenerationAgent()
    
    # Generate affiliate content
    contents = agent.generate_affiliate_content("technology", quantity=2, focus="conversion")
    print(json.dumps(contents, indent=2))
    
    # Generate course outline
    outline = agent.generate_course_outline("health", modules=3)
    print(json.dumps(outline, indent=2))
    
    # Generate marketing copy
    copy = agent.generate_marketing_copy("SuperApp", "productivity", style="informative")
    print(json.dumps(copy, indent=2))