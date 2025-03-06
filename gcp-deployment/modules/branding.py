import os
import random
import string
from typing import Dict, List, Any, Optional

import httpx

from utils.logger import setup_logger

logger = setup_logger("modules.branding")

class BrandingGenerator:
    """Generator for business branding."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize the Branding Generator.

        Args:
            api_key: API key for branding services (optional)
        """
        self.api_key = api_key

    async def generate_brand_name(self, business_model: str, keywords: List[str]) -> List[Dict[str, Any]]:
        """Generate brand name options for a business model.

        Args:
            business_model: Business model name/type
            keywords: Relevant keywords for the business

        Returns:
            List of brand name suggestions with scores
        """
        logger.info(f"Generating brand names for: {business_model}")

        # In a real implementation, this might call a specialized API or use a more sophisticated algorithm

        # Create word parts from the business model and keywords
        words = []
        for word in ([business_model] + keywords):
            words.extend(word.lower().split())

        # Generate prefixes and suffixes
        prefixes = ["nova", "peak", "flux", "bright", "swift", "zenith", "agile", "prime", "nexus", "meta"]
        suffixes = ["ify", "hub", "flow", "boost", "pulse", "labs", "pro", "tech", "ize", "ly"]

        # Generate brand names
        brand_names = []
        for i in range(5):  # Generate 5 brand names
            name_type = random.choice(["prefix_word", "word_suffix", "prefix_suffix", "word_word"])

            if name_type == "prefix_word":
                prefix = random.choice(prefixes)
                word = random.choice(words)
                name = f"{prefix}{word.capitalize()}"
                rationale = f"Combines the modern prefix '{prefix}' with '{word}' from your business domain."

            elif name_type == "word_suffix":
                word = random.choice(words)
                suffix = random.choice(suffixes)
                name = f"{word}{suffix}"
                rationale = f"Takes '{word}' from your business and adds the catchy suffix '{suffix}'."

            elif name_type == "prefix_suffix":
                prefix = random.choice(prefixes)
                suffix = random.choice(suffixes)
                name = f"{prefix}{suffix}"
                rationale = f"A completely modern coined term combining '{prefix}' and '{suffix}'."

            else:  # word_word
                word1 = random.choice(words)
                word2 = random.choice(words)
                while word2 == word1:
                    word2 = random.choice(words)
                name = f"{word1}{word2.capitalize()}"
                rationale = f"Combines two key terms from your business: '{word1}' and '{word2}'."

            # Ensure first letter is capitalized
            name = name[0].upper() + name[1:]

            # Add to results
            brand_names.append({
                "name": name,
                "score": random.uniform(7.0, 9.5),
                "domain_available": random.choice([True, False]),
                "trademark_risk": random.choice(["Low", "Medium", "High"]),
                "rationale": rationale
            })

        # Sort by score
        brand_names.sort(key=lambda x: x["score"], reverse=True)
        return brand_names

    async def generate_color_scheme(self, target_demographics: List[str], industry: str) -> Dict[str, Any]:
        """Generate a color scheme based on demographics and industry.

        Args:
            target_demographics: Target demographics
            industry: Business industry

        Returns:
            Color scheme with colors and rationale
        """
        logger.info(f"Generating color scheme for demographics: {target_demographics}")

        # Map demographics to color preferences
        demographic_colors = {
            "millennials": ["#4A90E2", "#50E3C2", "#F8E71C", "#FFFFFF"],
            "gen-z": ["#9C27B0", "#FF4081", "#FFEB3B", "#FFFFFF"],
            "professionals": ["#1A2A3A", "#4A5568", "#CBD5E0", "#FFFFFF"],
            "eco-conscious consumers": ["#4CAF50", "#8BC34A", "#F1F8E9", "#FFFFFF"],
            "entrepreneurs": ["#FF5722", "#FF9800", "#FFEB3B", "#FFFFFF"],
            "content creators": ["#9C27B0", "#673AB7", "#3F51B5", "#FFFFFF"],
            "small businesses": ["#2C3E50", "#E74C3C", "#ECF0F1", "#FFFFFF"],
            "parents": ["#3498DB", "#2ECC71", "#F1C40F", "#FFFFFF"],
            "students": ["#9B59B6", "#3498DB", "#2ECC71", "#FFFFFF"],
            "seniors": ["#34495E", "#7F8C8D", "#BDC3C7", "#FFFFFF"]
        }

        # Map industries to color preferences
        industry_colors = {
            "e-commerce": ["#1E88E5", "#FF8A65", "#FFFFFF"],
            "digital products": ["#6200EA", "#00E676", "#FFFFFF"],
            "saas": ["#0D47A1", "#00ACC1", "#FFFFFF"],
            "education": ["#039BE5", "#FFB300", "#FFFFFF"],
            "health": ["#00897B", "#D4E157", "#FFFFFF"],
            "finance": ["#1565C0", "#FDD835", "#FFFFFF"],
            "creative": ["#D81B60", "#8E24AA", "#FFFFFF"],
            "food": ["#D32F2F", "#7CB342", "#FFFFFF"]
        }

        # Select colors based on demographics and industry
        selected_colors = ["#FFFFFF"]  # Start with white

        # Add demographic colors
        for demo in target_demographics:
            demo_lower = demo.lower()
            for key, colors in demographic_colors.items():
                if key in demo_lower:
                    selected_colors.extend(colors)
                    break

        # Add industry colors
        industry_lower = industry.lower()
        for key, colors in industry_colors.items():
            if key in industry_lower:
                selected_colors.extend(colors)
                break

        # Remove duplicates and limit to 5 colors
        selected_colors = list(dict.fromkeys(selected_colors))[:5]

        # Generate color scheme with primary, secondary, accent, and background colors
        color_scheme = {
            "primary": selected_colors[0] if selected_colors else "#FF3A3A",
            "secondary": selected_colors[1] if len(selected_colors) > 1 else "#262626",
            "accent": selected_colors[2] if len(selected_colors) > 2 else "#FFD700",
            "background": "#FFFFFF",
            "text": "#333333",
            "all_colors": selected_colors,
            "rationale": f"This color scheme is optimized for {', '.join(target_demographics)} in the {industry} industry. The primary color conveys trust and professionalism, while the accent color adds energy and calls-to-action."
        }

        return color_scheme

    async def generate_positioning(self, brand_name: str, business_model: str, demographics: List[str]) -> Dict[str, Any]:
        """Generate brand positioning for a business.

        Args:
            brand_name: Brand name
            business_model: Business model
            demographics: Target demographics

        Returns:
            Brand positioning details
        """
        logger.info(f"Generating positioning for brand: {brand_name}")

        # In a real implementation, this would be more sophisticated

        # Brand positioning templates
        positioning_templates = [
            "{brand_name} provides innovative {business_model} solutions for {demographics} seeking {benefit} with minimal effort.",
            "{brand_name} is the leading {business_model} platform designed specifically for {demographics} who want to {benefit}.",
            "For {demographics} who demand excellence, {brand_name} delivers premium {business_model} experiences that {benefit}.",
            "{brand_name}: Transforming how {demographics} approach {business_model} by {benefit}."
        ]

        # Brand benefits based on business model
        benefits = {
            "e-commerce": [
                "maximize their sales",
                "create seamless shopping experiences",
                "build sustainable online stores",
                "connect with their ideal customers"
            ],
            "digital products": [
                "monetize their knowledge",
                "create passive income streams",
                "share their expertise",
                "build valuable digital assets"
            ],
            "saas": [
                "streamline their workflows",
                "automate repetitive tasks",
                "gain powerful insights",
                "scale their operations efficiently"
            ]
        }

        # Determine business model category
        business_category = "digital products"  # Default
        for category in benefits.keys():
            if category in business_model.lower():
                business_category = category
                break

        # Get demographics string
        if len(demographics) == 1:
            demo_string = demographics[0]
        elif len(demographics) == 2:
            demo_string = f"{demographics[0]} and {demographics[1]}"
        else:
            demo_string = f"{', '.join(demographics[:-1])}, and {demographics[-1]}"

        # Select a benefit
        benefit = random.choice(benefits.get(business_category, benefits["digital products"]))

        # Generate positioning statement
        template = random.choice(positioning_templates)
        positioning_statement = template.format(
            brand_name=brand_name,
            business_model=business_model,
            demographics=demo_string,
            benefit=benefit
        )

        # Generate tagline options
        tagline_templates = [
            "Elevate Your {business_model_short}",
            "{business_model_short} Made Simple",
            "Revolutionary {business_model_short} for {demographic_short}",
            "The Future of {business_model_short}",
            "{benefit_short}. Effortlessly."
        ]

        business_model_short = business_model.split()[0]
        demographic_short = demographics[0].split()[0] if demographics else "Everyone"
        benefit_short = benefit.split()[0].capitalize()

        taglines = []
        for template in tagline_templates:
            taglines.append(template.format(
                business_model_short=business_model_short,
                demographic_short=demographic_short,
                benefit_short=benefit_short
            ))

        return {
            "brand_name": brand_name,
            "positioning_statement": positioning_statement,
            "tagline_options": taglines,
            "voice_characteristics": random.sample([
                "Professional", "Friendly", "Authoritative", "Approachable", 
                "Innovative", "Trustworthy", "Enthusiastic", "Calm", "Confident"
            ], 3),
            "key_messages": [
                f"We help {demographics[0] if demographics else 'people'} {benefit}",
                f"Our {business_model} is designed specifically for {demographics[0] if demographics else 'you'}",
                f"Experience the most innovative {business_model} on the market"
            ]
        }

    async def create_complete_branding(
        self, 
        business_model_name: str,
        target_demographics: List[str],
        keywords: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Create complete branding for a business model.

        Args:
            business_model_name: Business model name
            target_demographics: Target demographics
            keywords: Optional keywords

        Returns:
            Complete branding package
        """
        logger.info(f"Creating complete branding for: {business_model_name}")

        # Use provided keywords or extract from business model name
        if not keywords:
            keywords = business_model_name.lower().split()

        # Generate brand name
        brand_names = await self.generate_brand_name(business_model_name, keywords)
        selected_brand_name = brand_names[0]["name"] if brand_names else f"Brand{business_model_name.title().replace(' ', '')}"

        # Generate color scheme
        industry = "digital products"  # Default
        for keyword in ["e-commerce", "digital products", "saas", "education", "health", "finance"]:
            if keyword in business_model_name.lower():
                industry = keyword
                break

        color_scheme = await self.generate_color_scheme(target_demographics, industry)

        # Generate positioning
        positioning = await self.generate_positioning(selected_brand_name, business_model_name, target_demographics)

        # Compile complete branding
        return {
            "brand_name": selected_brand_name,
            "logo_url": None,  # Would be generated in a real implementation
            "color_scheme": color_scheme,
            "positioning_statement": positioning["positioning_statement"],
            "tagline": positioning["tagline_options"][0],
            "alternative_names": [name["name"] for name in brand_names[1:3]] if len(brand_names) > 1 else [],
            "voice_tone": positioning["voice_characteristics"],
            "key_messages": positioning["key_messages"],
            "target_demographics": target_demographics
        }