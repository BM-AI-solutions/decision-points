"""
Code Generation Agent for Decision Points (ADK Version).

This agent generates code based on product specifications and branding using ADK tools.
"""

import json
import logging
from typing import Dict, Any, Optional, List

import google.generativeai as genai
from google.adk.agents import Agent # Use ADK Agent
from google.adk.tools import tool # Import tool decorator

# Removed A2A and BaseSpecializedAgent imports
from app.config import settings

# Configure logging
logger = logging.getLogger(__name__)

# --- LLM Initialization ---
try:
    genai.configure(api_key=settings.GEMINI_API_KEY)
    # Use a model suitable for code generation
    gemini_model_name = settings.GEMINI_MODEL_NAME # Or a specific code-tuned model if available
    gemini_model = genai.GenerativeModel(gemini_model_name)
    logger.info(f"Direct Gemini model {gemini_model_name} initialized for code generation tools.")
except Exception as e:
    logger.error(f"Failed to initialize direct Gemini model: {e}")
    gemini_model = None

# --- Helper Function ---
def _build_generation_prompt(product_spec: Any, branding: Any, framework: str) -> str:
    """
    Constructs the prompt for the LLM to generate code.
    (Moved outside the class/tool for potential reuse if needed)
    """
    spec_json = json.dumps(product_spec, indent=2)
    branding_json = json.dumps(branding, indent=2)

    prompt = f"""
You are an expert {framework} developer. Your task is to generate the complete codebase for a web application based on the provided Product Specification and Branding Package.

**Product Specification:**
```json
{spec_json}
```

**Branding Package:**
```json
{branding_json}
```

**Your Goal:** Generate a functional, basic {framework} application that implements the core `features` and reflects the `usp` (Unique Selling Proposition) outlined in the Product Specification. Apply the provided `branding` elements.

**Instructions:**

1.  **Framework:** Use {framework} with functional components and hooks (if applicable).
2.  **Output Format:** Respond with **ONLY** a single JSON object.
    *   Keys must be the file paths (relative to the project root, e.g., "src/App.jsx", "src/components/FeatureComponent.jsx").
    *   Values must be the complete code content for each file as a single string.
    *   Do not include any text before or after the JSON object.
3.  **File Structure:** Create standard {framework} files, plus necessary components:
    *   `package.json`: Include necessary dependencies (`react`, `react-dom`, `vite`, `@vitejs/plugin-react` for Vite/React). Analyze `product_spec.features` for routing needs (e.g., add `react-router-dom`). Set `"name"`. Include minimal essential dependencies.
    *   `vite.config.js` (or framework equivalent): Standard config.
    *   `index.html`: Basic structure, link CSS, include entry script, set `<title>`. **CRITICAL: Add GA4 (G-XXXXXXXXXX) and AdSense (ca-pub-XXXXXXXXXXXXXXXX) script placeholders to `<head>`.**
    *   `src/main.jsx` (or framework equivalent): Render root component, setup router if needed.
    *   `src/index.css`: Basic reset, CSS variables/utilities from `branding.colorPalette`/`typography`. Global styles.
    *   `src/App.jsx` (or framework equivalent): Main shell. Setup routing if needed (incl. page view tracking). Arrange components. **Include at least one placeholder AdSense ad unit (`<ins class="adsbygoogle">...`)**. Add comments.
    *   `src/components/`: Create multiple functional components implementing EACH core `feature` and `usp`. Name clearly. Implement basic functionality. Style using CSS/inline styles. Add comments. Optionally include more AdSense placeholders.

4.  **Functionality:** Generate *working*, simple code. Features should have basic interactivity if applicable.
5.  **Branding:** Integrate `branding.colorPalette`, `typography`, `brandName`.
6.  **Code Quality:** Generate clean, readable, commented code.

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

# --- ADK Tool Definitions ---

@tool(description="Generate a complete codebase structure (as JSON mapping file paths to content) based on product specifications and branding.")
async def generate_code_tool(
    product_spec: Dict[str, Any],
    branding: Dict[str, Any],
    framework: str = "vite-react" # Default framework
) -> Dict[str, Any]:
    """
    ADK Tool: Generate code based on product specifications and branding.
    """
    logger.info(f"Tool: Generating code for product: {product_spec.get('appName', 'Unknown')} using framework {framework}")

    if not gemini_model:
        return {"success": False, "error": "Gemini model not initialized"}
    if not product_spec or not branding:
        return {"success": False, "error": "Missing 'product_spec' or 'branding' in input data."}

    try:
        prompt = _build_generation_prompt(product_spec, branding, framework)
        response = await gemini_model.generate_content_async(prompt)
        response_text = response.text
        logger.info("Tool: LLM response received for code generation.")

        # Attempt to find JSON block
        json_start = response_text.find('{')
        json_end = response_text.rfind('}') + 1

        if json_start != -1 and json_end != -1:
            json_string = response_text[json_start:json_end]
            try:
                generated_code = json.loads(json_string)
                if not isinstance(generated_code, dict):
                    raise ValueError("LLM response JSON is not a dictionary.")
                logger.info(f"Tool: Successfully parsed generated code structure for {len(generated_code)} files.")
                return {
                    "success": True,
                    "message": f"Successfully generated code for {len(generated_code)} files.",
                    "generated_code": generated_code, # This is the dict {filepath: content}
                    "framework": framework
                }
            except (json.JSONDecodeError, ValueError) as e:
                logger.error(f"Tool: Failed to parse LLM response JSON: {e}")
                return {"success": False, "error": f"Failed to parse LLM response JSON: {str(e)}", "raw_response": response_text}
        else:
            logger.error("Tool: Could not find valid JSON object in LLM response.")
            return {"success": False, "error": "Could not find valid JSON object in LLM response.", "raw_response": response_text}

    except Exception as e:
        logger.exception(f"Tool: Code generation failed: {e}")
        return {"success": False, "error": f"Code generation failed: {str(e)}"}

@tool(description="Generate a single React component based on name, description, props, and styling info.")
async def generate_component_tool(
    component_name: str,
    component_description: str,
    props: Optional[List[Dict[str, str]]] = None,
    styling: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """
    ADK Tool: Generate a single React component.
    """
    logger.info(f"Tool: Generating component: {component_name}")

    if not gemini_model:
        return {"success": False, "error": "Gemini model not initialized"}

    try:
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

        response = await gemini_model.generate_content_async(prompt)
        component_code = response.text
        logger.info(f"Tool: Successfully generated component: {component_name}")

        return {
            "success": True,
            "message": f"Successfully generated component: {component_name}",
            "component_name": component_name,
            "component_code": component_code # The generated code string
        }

    except Exception as e:
        logger.exception(f"Tool: Component generation failed: {e}")
        return {"success": False, "error": f"Component generation failed: {str(e)}"}


# --- Instantiate the ADK Agent ---
agent = Agent(
    name="code_generation_adk", # ADK specific name
    description="Generates code structures or individual components based on specifications.",
    tools=[
        generate_code_tool,
        generate_component_tool,
    ],
)

# Removed A2A server specific code and old class structure
