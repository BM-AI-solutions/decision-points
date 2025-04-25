import asyncio
import json
import logging
import os
import argparse
from typing import Dict, Any, Optional

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
    # Assuming logfire is configured elsewhere (e.g., main backend or globally)
    logger = logfire # Use logfire directly if available
except ImportError:
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO"))

# --- Pydantic Models ---

# Define a generic input model as the exact structures aren't imported/defined here
class CodeGenInput(BaseModel):
    product_spec: Dict[str, Any] = Field(description="The improved product specification.")
    branding: Dict[str, Any] = Field(description="The branding package.")

# Define output model (assuming the agent returns a dict mapping filenames to code)
class CodeGenOutput(BaseModel):
    generated_code: Dict[str, str] = Field(description="Dictionary mapping file paths to their generated code content.")


# --- Agent Class ---

class CodeGenerationAgent(LlmAgent):
    """
    An agent responsible for generating initial project code based on specifications.
    """

    def __init__(self,
                 agent_id: str = "code-generation-agent", # Hyphenated convention
                 model_name: Optional[str] = None,
                 target_framework: str = "vite-react"):
        """
        Initializes the CodeGenerationAgent.

        Args:
            agent_id: The unique identifier for this agent instance.
            model_name: The name of the Gemini model to use. Reads from GEMINI_MODEL_NAME env var if None.
            target_framework: The target frontend framework (e.g., 'vite-react').
        """
        # Get config from environment variables
        effective_model_name = model_name or os.environ.get('GEMINI_MODEL_NAME', 'gemini-1.5-flash-latest') # Default model
        self.model_name = effective_model_name
        self.target_framework = target_framework

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
             logger.error("CodeGenerationAgent initialized WITHOUT a valid LLM client due to model initialization failure.")
        else:
            logger.info(f"CodeGenerationAgent initialized with model: {self.model_name} for framework: {self.target_framework}")


    async def run_async(self, context: InvocationContext) -> Event:
        """
        Generates project code based on ImprovedProductSpec and BrandingPackage.

        Args:
            context: The invocation context containing input data.
                     Expected data: {'product_spec': Dict, 'branding': Dict}

        Returns:
            An Event containing the generated code structure (Dict[str, str]) on success,
            or an error Event on failure.
        """
        logger.info(f"CodeGenerationAgent run_async invoked for instance: {context.instance_id}")

        if not isinstance(context.data, dict):
            error_msg = f"Input data is not a dictionary: {type(context.data)}"
            logger.error(error_msg)
            return context.create_error_event(error_msg)

        product_spec = context.data.get("product_spec")
        branding = context.data.get("branding")

        if not product_spec or not branding:
            error_msg = "Missing 'product_spec' or 'branding' in input data."
            logger.error(error_msg)
            return context.create_error_event(error_msg)

        logger.debug(f"Received Product Spec keys: {list(product_spec.keys())}")
        logger.debug(f"Received Branding Package keys: {list(branding.keys())}")

        try:
            # 1. Construct the prompt for the LLM
            prompt = self._build_generation_prompt(product_spec, branding)
            logger.debug("Constructed LLM Prompt.") # Avoid logging full prompt by default

            # 2. Call the LLM
            if not self.llm_client:
                 logger.error("LLM client is not initialized. Cannot generate code.")
                 raise RuntimeError("LLM client not initialized.")

            logger.info("Sending request to LLM for code generation.")
            # Use the LlmAgent's client
            response_text = await self.llm_client.generate_text_async(prompt=prompt)
            logger.info("LLM response received.")
            logger.debug(f"Raw LLM Response Text length: {len(response_text)}")

            # 3. Parse LLM Response (JSON object mapping file paths to content)
            json_string = self._extract_json(response_text)
            if not json_string:
                 error_msg = f"Could not find valid JSON object in LLM response.\nFirst 500 chars: {response_text[:500]}"
                 logger.error(error_msg)
                 return context.create_error_event(error_msg)

            try:
                generated_code = json.loads(json_string)
                if not isinstance(generated_code, dict):
                    raise ValueError("LLM response JSON is not a dictionary.")
                # Basic validation: check if values are strings
                for k, v in generated_code.items():
                    if not isinstance(v, str):
                        raise ValueError(f"Value for key '{k}' is not a string.")
                logger.info(f"Successfully parsed generated code structure for {len(generated_code)} files.")
            except json.JSONDecodeError as e:
                error_msg = f"Failed to parse LLM response as JSON: {e}\nExtracted JSON string: {json_string[:500]}..."
                logger.error(error_msg)
                return context.create_error_event(error_msg)
            except ValueError as e:
                error_msg = f"LLM response JSON format error: {e}\nExtracted JSON string: {json_string[:500]}..."
                logger.error(error_msg)
                return context.create_error_event(error_msg)

            # 4. Return success event with generated code
            logger.info("Code generation successful.")
            return context.create_result_event(data={"generated_code": generated_code})

        except Exception as e:
            error_msg = f"Code generation failed: {e}"
            logger.exception(error_msg) # Log full traceback
            return context.create_error_event(error_msg)

    def _extract_json(self, text: str) -> Optional[str]:
        """Attempts to extract a JSON object string from the LLM response."""
        try:
            # Find the first '{' and the last '}'
            json_start = text.find('{')
            json_end = text.rfind('}') + 1
            if json_start != -1 and json_end != -1 and json_start < json_end:
                 potential_json = text[json_start:json_end]
                 # Basic validation: try parsing it
                 json.loads(potential_json)
                 return potential_json
            else:
                 # Look for markdown code fences
                 fence_start = text.find("```json")
                 if fence_start != -1:
                     fence_end = text.find("```", fence_start + 7)
                     if fence_end != -1:
                         potential_json = text[fence_start + 7:fence_end].strip()
                         json.loads(potential_json)
                         return potential_json
        except (json.JSONDecodeError, Exception):
            logger.warning("Could not extract valid JSON from text.", exc_info=True)
            return None
        return None


    def _build_generation_prompt(self, product_spec: Any, branding: Any) -> str:
        """
        Constructs the prompt for the LLM to generate code.
        (Using the detailed prompt from the previous version)
        """
        # Convert spec and branding to JSON strings for the prompt
        try:
            spec_json = json.dumps(product_spec, indent=2)
            branding_json = json.dumps(branding, indent=2)
        except Exception as e:
            logger.error(f"Failed to serialize product_spec or branding to JSON: {e}")
            # Fallback or raise error - using basic string representation as fallback
            spec_json = str(product_spec)
            branding_json = str(branding)

        # --- Using the detailed prompt from the previous file content ---
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

# --- FastAPI Server Setup ---

app = FastAPI(title="CodeGenerationAgent A2A Server")

# Instantiate the agent (reads env vars internally)
code_gen_agent_instance = CodeGenerationAgent()

@app.post("/invoke", response_model=CodeGenOutput) # Use output model for response validation
async def invoke_agent(request: CodeGenInput = Body(...)):
    """
    A2A endpoint to invoke the CodeGenerationAgent.
    Expects JSON body with 'product_spec' and 'branding'.
    """
    logger.info("CodeGenerationAgent /invoke called.")
    # Create InvocationContext, passing data directly
    context = InvocationContext(agent_id="code-generation-agent", data=request.model_dump())

    try:
        result_event = await code_gen_agent_instance.run_async(context)
        if result_event and result_event.metadata.get("status") != "error": # Check for non-error status
            logger.info("CodeGenerationAgent returning success result.")
            # Validate the structure before returning
            if "generated_code" in result_event.data and isinstance(result_event.data["generated_code"], dict):
                 return result_event.data # Return the data part of the event
            else:
                 logger.error(f"Agent returned success status but data format is incorrect: {result_event.data}")
                 raise HTTPException(status_code=500, detail="Agent returned success but data format is invalid.")
        elif result_event:
             error_details = result_event.data.get("details", "Unknown agent error")
             logger.error(f"CodeGenerationAgent run_async returned error event: {error_details}")
             raise HTTPException(status_code=500, detail=f"Agent execution failed: {error_details}")
        else:
            logger.error("CodeGenerationAgent run_async returned None")
            raise HTTPException(status_code=500, detail="Agent execution failed to return an event.")
    except Exception as e:
        logger.error(f"Error during agent invocation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

@app.get("/health")
async def health_check():
    return {"status": "ok"}

# --- Main execution block ---

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the CodeGenerationAgent A2A server.")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind the server to.")
    parser.add_argument("--port", type=int, default=8082, help="Port to run the server on (default from compose).") # Default matches compose
    args = parser.parse_args()

    print(f"Starting CodeGenerationAgent A2A server on {args.host}:{args.port}")

    uvicorn.run(app, host=args.host, port=args.port)