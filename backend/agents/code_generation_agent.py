import json
import logging
from typing import Dict, Any

from google import genai
from google.adk.agents import LlmAgent
from google.adk.runtime import InvocationContext, Event

# Configure logging
logger = logging.getLogger(__name__)

# TODO: Configure Gemini API key (likely handled globally or via env vars)
# genai.configure(api_key="YOUR_GEMINI_API_KEY")

class CodeGenerationAgent(LlmAgent):
    """
    An agent responsible for generating initial project code based on specifications.
    """

    def __init__(self,
                 agent_id: str = "code_generation_agent",
                 model_name: Optional[str] = None, # Added model_name parameter
                 target_framework: str = "vite-react"):
        """
        Initializes the CodeGenerationAgent.

        Args:
            agent_id: The unique identifier for this agent instance.
            model_name: The name of the Gemini model to use (e.g., 'gemini-1.5-flash-latest').
                        Defaults to a suitable model if None.
            target_framework: The target frontend framework (e.g., 'vite-react').
        """
        # Determine the model name to use
        effective_model_name = model_name if model_name else 'gemini-1.5-flash-latest' # Default for specialized agent
        self.model_name = effective_model_name # Store the actual model name used

        # Initialize the ADK Gemini model
        adk_model = Gemini(model=self.model_name)

        # Call super().__init__ from LlmAgent, passing the model
        super().__init__(
            agent_id=agent_id,
            model=adk_model # Pass the initialized ADK model object
            # instruction can be set here if needed, or rely on default/prompt
        )
        self.target_framework = target_framework
        # self.llm_model = genai.GenerativeModel('gemini-pro') # Removed direct instantiation
        logger.info(f"CodeGenerationAgent initialized with model: {self.model_name} for framework: {self.target_framework}")

    async def run_async(self, context: InvocationContext) -> Event:
        """
        Generates project code based on ImprovedProductSpec and BrandingPackage.

        Args:
            context: The invocation context containing input data.
                     Expected data: {'product_spec': ImprovedProductSpec, 'branding': BrandingPackage}

        Returns:
            An Event containing the generated code structure (Dict[str, str]) on success,
            or an error Event on failure.
        """
        logger.info(f"CodeGenerationAgent run_async invoked for instance: {context.instance_id}")

        product_spec = context.data.get("product_spec")
        branding = context.data.get("branding")

        if not product_spec or not branding:
            error_msg = "Missing 'product_spec' or 'branding' in input data."
            logger.error(error_msg)
            return Event.create_error_event(error_msg)

        logger.debug(f"Received Product Spec: {product_spec}")
        logger.debug(f"Received Branding Package: {branding}")

        try:
            # 1. Construct the prompt for the LLM
            prompt = self._build_generation_prompt(product_spec, branding)
            logger.debug(f"Constructed LLM Prompt:\n{prompt}")

            # 2. Call the LLM
            # TODO: Add retry logic, more sophisticated error handling for LLM calls
            # Use the LlmAgent's client, configured with the correct model
            response_text = await self.llm_client.generate_text_async(prompt=prompt)
            logger.info("LLM response received.")
            # Assuming the LLM returns a JSON string mapping file paths to content
            # Need robust parsing and validation here
            # response_text = response.text.strip() # Already have response_text
            logger.debug(f"Raw LLM Response Text:\n{response_text}")

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
                 except json.JSONDecodeError as e:
                     error_msg = f"Failed to parse LLM response as JSON: {e}\nResponse: {response_text}"
                     logger.error(error_msg)
                     return Event.create_error_event(error_msg)
                 except ValueError as e:
                     error_msg = f"LLM response JSON format error: {e}\nResponse: {response_text}"
                     logger.error(error_msg)
                     return Event.create_error_event(error_msg)
            else:
                 error_msg = f"Could not find valid JSON object in LLM response.\nResponse: {response_text}"
                 logger.error(error_msg)
                 return Event.create_error_event(error_msg)


            # 4. Return success event with generated code
            logger.info("Code generation successful.")
            return Event.create_result_event(data={"generated_code": generated_code})

        except Exception as e:
            error_msg = f"Code generation failed: {e}"
            logger.exception(error_msg) # Log full traceback
            return Event.create_error_event(error_msg)

    def _build_generation_prompt(self, product_spec: Any, branding: Any) -> str:
        """
        Constructs the prompt for the LLM to generate code, focusing on feature implementation.
        """
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

# Example Usage (for testing purposes, would not be in production agent code)
if __name__ == '__main__':
    # This block allows for testing the agent logic locally if needed
    # You would need to mock InvocationContext, Event, product_spec, branding
    # and potentially the LLM call.
    print("CodeGenerationAgent defined. Run integration tests for actual execution.")

    # Mock data example:
    mock_spec = {
        "appName": "Idea Spark",
        "concept": "A simple web app to capture and organize ideas.",
        "features": ["Input field for new ideas", "List display of ideas", "Ability to delete ideas"],
        "targetAudience": "Individuals"
    }
    mock_branding = {
        "brandName": "Idea Spark",
        "logoDescription": "A lightbulb icon",
        "colorPalette": {
            "primary": "#4A90E2", # Blue
            "secondary": "#F5A623", # Orange
            "background": "#FFFFFF", # White
            "text": "#333333" # Dark Gray
        },
        "typography": {
            "fontFamily": "Arial, sans-serif",
            "headings": "bold"
        }
    }

    # Note: Direct instantiation and running like this bypasses the ADK runtime.
    # Use 'adk run' or proper testing frameworks for real execution.
    # agent = CodeGenerationAgent()
    # prompt = agent._build_generation_prompt(mock_spec, mock_branding)
    # print("\n--- Example Prompt ---")
    # print(prompt)
    # print("\n--- End Example Prompt ---")