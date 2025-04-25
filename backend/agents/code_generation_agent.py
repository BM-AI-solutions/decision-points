"""
Code Generation Agent for Decision Points.

This agent generates code based on product specifications and branding.
It implements the A2A protocol for agent communication.
"""

import json
import logging
from typing import Dict, Any, Optional, List

import google.generativeai as genai
from google.adk.runtime import InvocationContext, Event

# A2A Imports
from python_a2a import skill

from agents.base_agent import BaseSpecializedAgent
from app.config import settings

# Configure logging
logger = logging.getLogger(__name__)

class CodeGenerationAgent(BaseSpecializedAgent):
    """
    Agent responsible for code generation.
    Generates code based on product specifications and branding.
    Implements A2A protocol for agent communication.
    """
    def __init__(
        self,
        name: str = "code_generation",
        description: str = "Generates code based on product specifications and branding",
        model_name: Optional[str] = None,
        port: Optional[int] = None,
        target_framework: str = "vite-react",
        **kwargs: Any,
    ):
        """
        Initialize the CodeGenerationAgent.

        Args:
            name: The name of the agent.
            description: The description of the agent.
            model_name: The name of the model to use. Defaults to settings.GEMINI_MODEL_NAME.
            port: The port to run the A2A server on. Defaults to settings.CODE_GENERATION_AGENT_URL port.
            target_framework: The target frontend framework (e.g., 'vite-react').
            **kwargs: Additional arguments for BaseSpecializedAgent.
        """
        # Extract port from URL if not provided
        if port is None and settings.CODE_GENERATION_AGENT_URL:
            try:
                port = int(settings.CODE_GENERATION_AGENT_URL.split(':')[-1])
            except (ValueError, IndexError):
                port = 8007  # Default port

        # Initialize BaseSpecializedAgent
        super().__init__(
            name=name,
            description=description,
            model_name=model_name,
            port=port,
            **kwargs
        )

        self.target_framework = target_framework
        logger.info(f"CodeGenerationAgent initialized with port: {self.port} for framework: {self.target_framework}")

    # --- A2A Skills ---
    @skill(
        name="generate_code",
        description="Generate code based on product specifications and branding",
        tags=["code", "generation"]
    )
    async def generate_code(self, product_spec: Dict[str, Any], branding: Dict[str, Any],
                           framework: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate code based on product specifications and branding.

        Args:
            product_spec: The product specification.
            branding: The branding package.
            framework: Optional framework to use (e.g., 'vite-react', 'next.js').
                      Defaults to the agent's target_framework.

        Returns:
            A dictionary containing the generated code structure.
        """
        logger.info(f"Generating code for product: {product_spec.get('appName', 'Unknown')}")

        if not product_spec or not branding:
            return {
                "success": False,
                "error": "Missing 'product_spec' or 'branding' in input data."
            }

        # Use specified framework or default to agent's target_framework
        target_framework = framework or self.target_framework

        try:
            # Construct the prompt for the LLM
            prompt = self._build_generation_prompt(product_spec, branding, target_framework)

            # Call the LLM
            response_text = await self.llm_client.generate_text_async(prompt=prompt)
            logger.info("LLM response received.")

            # Attempt to find JSON block within the response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1

            if json_start != -1 and json_end != -1:
                json_string = response_text[json_start:json_end]
                try:
                    generated_code = json.loads(json_string)
                    if not isinstance(generated_code, dict):
                        raise ValueError("LLM response JSON is not a dictionary.")

                    logger.info(f"Successfully parsed generated code structure for {len(generated_code)} files.")

                    return {
                        "success": True,
                        "message": f"Successfully generated code for {len(generated_code)} files.",
                        "generated_code": generated_code,
                        "framework": target_framework
                    }
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse LLM response as JSON: {e}")
                    return {
                        "success": False,
                        "error": f"Failed to parse LLM response as JSON: {str(e)}",
                        "raw_response": response_text
                    }
                except ValueError as e:
                    logger.error(f"LLM response JSON format error: {e}")
                    return {
                        "success": False,
                        "error": f"LLM response JSON format error: {str(e)}",
                        "raw_response": response_text
                    }
            else:
                logger.error("Could not find valid JSON object in LLM response.")
                return {
                    "success": False,
                    "error": "Could not find valid JSON object in LLM response.",
                    "raw_response": response_text
                }

        except Exception as e:
            logger.exception(f"Code generation failed: {e}")
            return {
                "success": False,
                "error": f"Code generation failed: {str(e)}"
            }

    @skill(
        name="generate_component",
        description="Generate a single React component based on specifications",
        tags=["code", "component"]
    )
    async def generate_component(self, component_name: str, component_description: str,
                                props: Optional[List[Dict[str, str]]] = None,
                                styling: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Generate a single React component based on specifications.

        Args:
            component_name: The name of the component.
            component_description: Description of what the component should do.
            props: Optional list of props the component should accept.
            styling: Optional styling information.

        Returns:
            A dictionary containing the generated component code.
        """
        logger.info(f"Generating component: {component_name}")

        try:
            # Construct the prompt for the LLM
            prompt = f"""
            You are an expert React developer. Your task is to generate a single React functional component based on the provided specifications.

            **Component Specifications:**
            - Name: {component_name}
            - Description: {component_description}
            - Props: {json.dumps(props) if props else "None specified"}
            - Styling: {json.dumps(styling) if styling else "Use basic inline styles or CSS modules"}

            **Instructions:**
            1. Create a React functional component using modern React practices (hooks, etc.).
            2. Include appropriate PropTypes or TypeScript types for the props.
            3. Add comments explaining the component's purpose and any complex logic.
            4. Implement the functionality described in the component description.
            5. Apply the specified styling approach.

            **Output Format:**
            Respond with ONLY the complete component code as a string. Do not include any explanations or markdown formatting.
            """

            # Call the LLM
            component_code = await self.llm_client.generate_text_async(prompt=prompt)
            logger.info(f"Successfully generated component: {component_name}")

            return {
                "success": True,
                "message": f"Successfully generated component: {component_name}",
                "component_name": component_name,
                "component_code": component_code
            }

        except Exception as e:
            logger.exception(f"Component generation failed: {e}")
            return {
                "success": False,
                "error": f"Component generation failed: {str(e)}"
            }

    async def run_async(self, context: InvocationContext) -> Event:
        """
        Executes the code generation workflow asynchronously according to ADK spec.
        Maintained for backward compatibility with ADK.

        Args:
            context: The invocation context containing the input data.

        Returns:
            An Event containing the generated code or an error.
        """
        logger.info(f"Received invocation for CodeGenerationAgent (ID: {context.instance_id})")

        try:
            # Extract input from context
            data = {}
            if hasattr(context, 'data') and isinstance(context.data, dict):
                data = context.data

            product_spec = data.get("product_spec")
            branding = data.get("branding")

            if not product_spec or not branding:
                error_msg = "Missing 'product_spec' or 'branding' in input data."
                logger.error(error_msg)
                return Event.create_error_event(error_msg)

            # Use the A2A skill
            result = await self.generate_code(
                product_spec=product_spec,
                branding=branding
            )

            # Create an event from the result
            if result.get("success", False):
                return Event.create_result_event(data={
                    "generated_code": result.get("generated_code", {})
                })
            else:
                return Event.create_error_event(result.get("error", "Code generation failed."))

        except Exception as e:
            # Catch-all for unexpected errors
            error_msg = f"Code generation failed: {e}"
            logger.exception(error_msg)
            return Event.create_error_event(error_msg)

    def _build_generation_prompt(self, product_spec: Any, branding: Any, framework: str = None) -> str:
        """
        Constructs the prompt for the LLM to generate code, focusing on feature implementation.

        Args:
            product_spec: The product specification.
            branding: The branding package.
            framework: The target framework (e.g., 'vite-react', 'next.js').
                      Defaults to the agent's target_framework.

        Returns:
            The prompt for the LLM.
        """
        # Use specified framework or default to agent's target_framework
        target_framework = framework or self.target_framework

        # Convert spec and branding to JSON strings for the prompt
        spec_json = json.dumps(product_spec, indent=2)
        branding_json = json.dumps(branding, indent=2)

        prompt = f"""
You are an expert Vite + React developer. Your task is to generate the complete codebase for a web application based on the provided Product Specification and Branding Package.

**Product Specification:**
```json
{spec_json}
```

**Branding Package:**
```json
{branding_json}
```

**Your Goal:** Generate a functional, basic Vite + React application that implements the core `features` and reflects the `usp` (Unique Selling Proposition) outlined in the Product Specification. Apply the provided `branding` elements.

**Instructions:**

1.  **Framework:** Use Vite and React with functional components and hooks.
2.  **Output Format:** Respond with **ONLY** a single JSON object.
    *   Keys must be the file paths (relative to the project root, e.g., "src/App.jsx", "src/components/FeatureComponent.jsx").
    *   Values must be the complete code content for each file as a single string.
    *   Do not include any text before or after the JSON object.
3.  **File Structure:** Create the following standard Vite/React files, plus necessary components:
    *   `package.json`:
        *   Include `react`, `react-dom`, `vite`, `@vitejs/plugin-react`.
        *   **Analyze `product_spec.features`. If multiple distinct features or pages are described, ADD `react-router-dom` to dependencies.**
        *   Set `"name"` based on `product_spec.appName` or `branding.brandName`.
        *   Include other simple dependencies ONLY if essential for a core feature (e.g., `axios` for a simple API call if specified, but avoid complex libraries).
    *   `vite.config.js`: Standard Vite config for React.
    *   `index.html`:
        *   Basic HTML structure, link CSS, include `src/main.jsx`, set `<title>` from `branding.brandName`.
        *   **CRITICAL: Add the Google Analytics (GA4) script snippet to the `<head>`. Use the placeholder `G-XXXXXXXXXX` for the Measurement ID.** Example snippet:
          ```html
          <!-- Google tag (gtag.js) -->
          <script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
          <script>
            window.dataLayer = window.dataLayer || [];
            function gtag(){{dataLayer.push(arguments);}} // Escaped braces for f-string
            gtag('js', new Date());
            gtag('config', 'G-XXXXXXXXXX');
          </script>
          ```
        *   **ALSO CRITICAL: Add the Google AdSense script snippet to the `<head>`. Use the placeholder `ca-pub-XXXXXXXXXXXXXXXX` for the Publisher ID.** Example snippet:
          ```html
          <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-XXXXXXXXXXXXXXXX"
               crossorigin="anonymous"></script>
          ```
    *   `src/main.jsx`: Render `App`. If `react-router-dom` is used, wrap `<App />` in `<BrowserRouter>`.
    *   `src/index.css`: Basic CSS reset. Define CSS variables or utility classes using `branding.colorPalette` and `branding.typography`. Apply basic global styles reflecting the brand.
    *   `src/App.jsx`:
        *   Main application shell.
        *   **If `react-router-dom` is used:** Set up `<Routes>` and `<Route>` elements to render different components based on the features/pages implied by `product_spec`. Include a basic navigation element (e.g., a simple header with links). **Consider adding a simple page view tracking mechanism using `useEffect` and `useLocation` from `react-router-dom` to send page views to GA4 on route changes.**
        *   **If no routing:** Structure the main layout, importing and arranging the feature components. **Consider adding a simple `useEffect` hook to send an initial page view event to GA4 on component mount.**
        *   Import components from `src/components/`.
        *   **AdSense Placeholder:** Include at least one placeholder Google AdSense ad unit (`<ins class="adsbygoogle">...</ins>`) in a reasonable location (e.g., below the header, in a sidebar if applicable, or between content sections). Use a placeholder `data-ad-slot`. Example:
          ```jsx
          {{/* Placeholder Ad Unit */}}
          <ins className="adsbygoogle"
               style={{{{ display: 'block' }}}} // Escaped style braces
               data-ad-client="ca-pub-XXXXXXXXXXXXXXXX"
               data-ad-slot="YYYYYYYYYY" // Placeholder Slot ID
               data-ad-format="auto"
               data-full-width-responsive="true"></ins>
          <script>
               (adsbygoogle = window.adsbygoogle || []).push({{}}); // Correctly escaped push braces
          </script>
          ```
          *(Note: You might need to wrap the script tag content in `{{{{ __html: '...' }}}}` or use `useEffect` to run the push after component mount for React compatibility)* // Escaped note braces
        *   Include comments explaining the structure and the ad placeholder.
    *   `src/components/` (Directory & Files):
        *   **CRITICAL: Create multiple React functional components here to implement EACH core `feature` and the `usp` from `product_spec`.**
        *   Name components clearly (e.g., `FeatureDisplay.jsx`, `UserInputForm.jsx`, `DashboardView.jsx`).
        *   Implement basic functionality for each feature. Use `useState` and `useEffect` for simple state management and effects where needed. **Generate functional code, not just placeholders.**
        *   Style components using CSS classes from `src/index.css` or simple inline styles if necessary. Keep styling basic but functional and brand-aligned.
        *   **AdSense Placeholders (Optional but Recommended):** If logical, you can also place additional placeholder ad units within specific feature components where appropriate (e.g., below a list, within a content area). Use the same placeholder format as above.
        *   Add comments explaining each component's purpose and any ad placeholders.

4.  **Functionality:** The generated code should represent a *working*, albeit simple, version of the application described. Features should have basic interactive elements if applicable (e.g., forms, buttons that update state).
5.  **Branding:** Integrate `branding.colorPalette` and `branding.typography` into the CSS and component styling. Use `branding.brandName`.
6.  **Code Quality:** Generate clean, readable, and commented code.

**Example JSON Output Structure:**
```json
{{
  "package.json": "...",
  "vite.config.js": "...",
  "index.html": "...",
  "src/main.jsx": "...",
  "src/App.jsx": "...",
  "src/index.css": "...",
  "src/components/FeatureComponent1.jsx": "...",
  "src/components/AnotherComponent.jsx": "..."
}}
```

Now, generate the JSON object containing the complete codebase based on the provided specifications.
"""
        return prompt

# Example of how to run this agent as a standalone A2A server
if __name__ == "__main__":
    # Create the agent
    agent = CodeGenerationAgent()

    # Run the A2A server
    agent.run_server(host="0.0.0.0", port=agent.port or 8007)