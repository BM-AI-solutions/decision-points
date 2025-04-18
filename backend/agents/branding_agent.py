import os
import random
import string
import json # Added for potential context data parsing
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field

# Import ADK components
from google.adk.agents import LlmAgent
from google.adk.runtime import InvocationContext
from google.adk.runtime.events import Event

# Assuming ImprovedProductSpec structure is available or defined elsewhere
# Define input based on what BrandingAgent needs from ImprovedProductSpec
class BrandingAgentInput(BaseModel):
    """Input for the Branding Agent."""
    product_concept: str = Field(description="Description of the core product/model.")
    target_audience: List[str] = Field(description="Defined target demographics.")
    keywords: Optional[List[str]] = Field(None, description="Optional keywords related to the product/concept.")
    business_model_type: Optional[str] = Field(None, description="Optional: Type of business model (e.g., 'saas', 'e-commerce') to guide branding.")

# Define output based on the architecture plan
class ColorScheme(BaseModel):
    primary: str
    secondary: str
    accent: str
    background: str
    text: str
    all_colors: List[str]
    rationale: str

class BrandPackage(BaseModel):
    """Output schema for the Branding Agent, aligning with the architecture plan."""
    brand_name: str
    tagline: str
    color_scheme: ColorScheme
    positioning_statement: str
    key_messages: List[str]
    voice_tone: List[str]
    # Added from prototype for completeness
    alternative_names: List[str] = []
    target_demographics: List[str] # From input

# --- Agent Class ---

class BrandingAgent(LlmAgent): # Inherit from LlmAgent
    """
    ADK Agent responsible for Stage 3: Rebranding.
    Generates a brand identity based on the improved product specification.
    """
    def __init__(self, agent_id: str = "branding_agent"): # Add agent_id and call parent init
        """Initialize the Branding Agent."""
        super().__init__(agent_id=agent_id)
        # Load branding generation components (based on branding.py logic)
        self._load_branding_elements()
        # Removed print statement

    def _load_branding_elements(self):
        """Loads predefined elements used in branding generation."""
        self.prefixes = ["nova", "peak", "flux", "bright", "swift", "zenith", "agile", "prime", "nexus", "meta", "sync", "quantum", "evolve"]
        self.suffixes = ["ify", "hub", "flow", "boost", "pulse", "labs", "pro", "tech", "ize", "ly", "spark", "wave", "gen"]
        self.positioning_templates = [
            "{brand_name} provides innovative {business_model} solutions for {demographics} seeking {benefit} with minimal effort.",
            "{brand_name} is the leading {business_model} platform designed specifically for {demographics} who want to {benefit}.",
            "For {demographics} who demand excellence, {brand_name} delivers premium {business_model} experiences that {benefit}.",
            "{brand_name}: Transforming how {demographics} approach {business_model} by {benefit}."
        ]
        self.benefits_by_model = {
            "generic": [
                "achieve their goals faster", "simplify complex tasks", "unlock new potential", "boost their productivity"
            ],
            "e-commerce": [
                "maximize their sales", "create seamless shopping experiences", "build sustainable online stores", "connect with their ideal customers"
            ],
            "digital_products": [
                "monetize their knowledge", "create passive income streams", "share their expertise", "build valuable digital assets"
            ],
            "saas": [
                "streamline their workflows", "automate repetitive tasks", "gain powerful insights", "scale their operations efficiently"
            ]
        }
        self.tagline_templates = [
            "Elevate Your {business_model_short}", "{business_model_short} Made Simple",
            "Revolutionary {business_model_short} for {demographic_short}", "The Future of {business_model_short}",
            "{benefit_short}. Effortlessly.", "Powering Your {business_model_short}", "Smart {business_model_short} Solutions"
        ]
        self.voice_characteristics = [
            "Professional", "Friendly", "Authoritative", "Approachable", "Innovative",
            "Trustworthy", "Enthusiastic", "Calm", "Confident", "Witty", "Empathetic"
        ]
        # Simplified color logic from branding.py
        self.demographic_colors = {
            "default": ["#4A90E2", "#50E3C2", "#F8E71C", "#FFFFFF"], # Millennials as default
            "gen-z": ["#9C27B0", "#FF4081", "#FFEB3B", "#FFFFFF"],
            "professionals": ["#1A2A3A", "#4A5568", "#CBD5E0", "#FFFFFF"],
        }
        self.industry_colors = {
             "default": ["#6200EA", "#00E676", "#FFFFFF"], # Digital products as default
            "e-commerce": ["#1E88E5", "#FF8A65", "#FFFFFF"],
            "saas": ["#0D47A1", "#00ACC1", "#FFFFFF"],
        }
        # Removed print statement


    def _generate_brand_name(self, concept: str, keywords: List[str]) -> List[Dict[str, Any]]:
        """Generates brand name options."""
        # Removed print statement
        words = concept.lower().split() + [k.lower() for k in keywords]
        words = list(set(w for w in words if len(w) > 2)) # Use unique words > 2 chars

        if not words: # Fallback if no suitable words
            words = ['solution', 'system', 'app']

        brand_names = []
        attempts = 0
        while len(brand_names) < 5 and attempts < 20:
            attempts += 1
            name_type = random.choice(["prefix_word", "word_suffix", "prefix_suffix", "word_word"])
            name = ""
            rationale = ""

            try:
                if name_type == "prefix_word" and self.prefixes and words:
                    prefix = random.choice(self.prefixes)
                    word = random.choice(words)
                    name = f"{prefix}{word.capitalize()}"
                    rationale = f"Combines modern prefix '{prefix}' with keyword '{word}'."
                elif name_type == "word_suffix" and words and self.suffixes:
                    word = random.choice(words)
                    suffix = random.choice(self.suffixes)
                    name = f"{word.capitalize()}{suffix}"
                    rationale = f"Combines keyword '{word}' with suffix '{suffix}'."
                elif name_type == "prefix_suffix" and self.prefixes and self.suffixes:
                    prefix = random.choice(self.prefixes)
                    suffix = random.choice(self.suffixes)
                    name = f"{prefix.capitalize()}{suffix}"
                    rationale = f"Coined term combining prefix '{prefix}' and suffix '{suffix}'."
                elif name_type == "word_word" and len(words) >= 2:
                    word1, word2 = random.sample(words, 2)
                    name = f"{word1.capitalize()}{word2.capitalize()}"
                    rationale = f"Combines keywords '{word1}' and '{word2}'."
                else: # Fallback if lists are empty or word_word fails
                     name = f"{random.choice(self.prefixes).capitalize()}{random.choice(words).capitalize()}"
                     rationale = "Generated fallback name."

                # Basic validation
                if 3 < len(name) < 15 and name not in [b['name'] for b in brand_names]:
                    brand_names.append({
                        "name": name,
                        "score": random.uniform(7.0, 9.5), # Placeholder score
                        "rationale": rationale
                    })
            except IndexError: # Catch errors if lists are unexpectedly empty
                self.logger.warning("Could not generate name due to empty lists.") # Use logger
                continue


        brand_names.sort(key=lambda x: x["score"], reverse=True)
        # Removed print statement
        return brand_names

    def _generate_color_scheme(self, target_demographics: List[str], business_model: Optional[str]) -> ColorScheme:
        """Generates a color scheme."""
        # Removed print statement
        selected_colors = ["#FFFFFF", "#333333"] # Start with white & dark text

        # Simplified selection logic
        demo_key = target_demographics[0].lower() if target_demographics else "default"
        industry_key = business_model.lower() if business_model else "default"

        selected_colors.extend(self.demographic_colors.get(demo_key, self.demographic_colors["default"]))
        selected_colors.extend(self.industry_colors.get(industry_key, self.industry_colors["default"]))

        # Ensure unique colors, prioritize, limit to 5 (+ white/black)
        unique_colors = list(dict.fromkeys(selected_colors))
        final_colors = unique_colors[:5] # Primary, Secondary, Accent + White/Black

        # Assign roles (simple assignment)
        primary = final_colors[2] if len(final_colors) > 2 else "#4A90E2"
        secondary = final_colors[3] if len(final_colors) > 3 else "#50E3C2"
        accent = final_colors[4] if len(final_colors) > 4 else "#F8E71C"
        background = "#FFFFFF"
        text = "#333333"

        rationale = f"Color scheme optimized for {', '.join(target_demographics)} in the {business_model or 'general'} market. Primary: {primary}, Secondary: {secondary}, Accent: {accent}."

        scheme = ColorScheme(
            primary=primary, secondary=secondary, accent=accent,
            background=background, text=text,
            all_colors=final_colors, rationale=rationale
        )
        # Removed print statement
        return scheme

    def _generate_positioning(self, brand_name: str, concept: str, demographics: List[str], business_model: Optional[str]) -> Dict[str, Any]:
        """Generates brand positioning elements."""
        # Removed print statement
        model_key = business_model.lower() if business_model else "generic"
        benefit = random.choice(self.benefits_by_model.get(model_key, self.benefits_by_model["generic"]))

        if len(demographics) == 1:
            demo_string = demographics[0]
        elif len(demographics) == 2:
            demo_string = f"{demographics[0]} and {demographics[1]}"
        else:
            demo_string = f"{', '.join(demographics[:-1])}, and {demographics[-1]}" if demographics else "forward-thinking individuals"

        template = random.choice(self.positioning_templates)
        positioning_statement = template.format(
            brand_name=brand_name,
            business_model=business_model or "solutions",
            demographics=demo_string,
            benefit=benefit
        )

        # Generate tagline
        business_model_short = (business_model or concept).split()[0]
        demographic_short = demographics[0].split()[0] if demographics else "You"
        benefit_short = benefit.split()[0].capitalize()
        tagline_template = random.choice(self.tagline_templates)
        tagline = tagline_template.format(
            business_model_short=business_model_short,
            demographic_short=demographic_short,
            benefit_short=benefit_short
        )

        # Select voice characteristics
        voice = random.sample(self.voice_characteristics, 3)

        # Generate key messages
        key_messages = [
            f"We help {demo_string} {benefit}.",
            f"Our {business_model or 'platform'} is designed specifically for your needs.",
            f"Experience the future of {business_model or concept.split()[0]} with {brand_name}."
        ]
        # Removed print statement
        return {
            "positioning_statement": positioning_statement,
            "tagline": tagline,
            "voice_tone": voice,
            "key_messages": key_messages
        }

    async def run_async(self, context: InvocationContext) -> Event: # Changed signature
        """Executes the branding generation workflow."""
        self.logger.info(f"Starting branding generation for context: {context.invocation_id}") # Use logger

        try:
            # 1. Parse Input from context
            if not isinstance(context.input.data, dict):
                 # Attempt to parse if it's a JSON string
                try:
                    input_data = json.loads(context.input.data)
                except json.JSONDecodeError:
                    raise ValueError("Input data is not a valid dictionary or JSON string.")
            else:
                input_data = context.input.data

            inputs = BrandingAgentInput(**input_data)
            self.logger.info(f"Parsed input: Concept='{inputs.product_concept}', Audience='{inputs.target_audience}'")

            # 2. Generate Brand Name Options
            keywords = inputs.keywords or inputs.product_concept.lower().split()
            brand_names = self._generate_brand_name(inputs.product_concept, keywords)
            if not brand_names:
                # Fallback if generation completely fails
                selected_brand_name = f"{inputs.product_concept.split()[0].capitalize()}Gen"
                alt_names = []
                self.logger.warning("Brand name generation failed, using fallback.")
            else:
                selected_brand_name = brand_names[0]["name"]
                alt_names = [b["name"] for b in brand_names[1:3]]
                self.logger.info(f"Selected brand name: {selected_brand_name}")


            # 3. Generate Color Scheme
            color_scheme = self._generate_color_scheme(inputs.target_audience, inputs.business_model_type)
            self.logger.info(f"Generated color scheme with primary: {color_scheme.primary}")

            # 4. Generate Positioning, Tagline, Voice, Messages
            positioning_elements = self._generate_positioning(
                selected_brand_name,
                inputs.product_concept,
                inputs.target_audience,
                inputs.business_model_type
            )
            self.logger.info("Generated positioning elements.")

            # 5. Assemble Brand Package
            brand_package = BrandPackage(
                brand_name=selected_brand_name,
                tagline=positioning_elements["tagline"],
                color_scheme=color_scheme,
                positioning_statement=positioning_elements["positioning_statement"],
                key_messages=positioning_elements["key_messages"],
                voice_tone=positioning_elements["voice_tone"],
                alternative_names=alt_names,
                target_demographics=inputs.target_audience
            )

            self.logger.info("Branding generation finished successfully.")
            # 6. Return result as an Event
            return Event(
                event_type="adk.agent.result",
                data=brand_package.model_dump(), # Serialize the Pydantic model
                metadata={"status": "success"}
            )

        except Exception as e:
            self.logger.error(f"BrandingAgent execution failed: {e}", exc_info=True)
            # Return an error Event
            return Event(
                event_type="adk.agent.error",
                data={"error": str(e), "details": "Failed during branding generation process."},
                metadata={"status": "error"}
            )

# Removed the if __name__ == "__main__": block