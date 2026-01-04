"""Image generation using DALL-E 3 with Stable Diffusion fallback."""
import asyncio
import base64
import re
from enum import Enum
from typing import Optional

import httpx
from openai import AsyncOpenAI
from pydantic import BaseModel

from src.core.config import get_settings


class ImageStyle(str, Enum):
    """Available image styles."""
    PROFESSIONAL = "professional"
    ABSTRACT = "abstract"
    INFOGRAPHIC = "infographic"
    MINIMALIST = "minimalist"


class ImageSize(str, Enum):
    """Available image sizes for LinkedIn."""
    SQUARE = "1024x1024"
    LANDSCAPE = "1792x1024"
    PORTRAIT = "1024x1792"


class GeneratedImage(BaseModel):
    """Result of image generation."""
    image_data: bytes
    prompt_used: str
    model_used: str
    revised_prompt: Optional[str] = None


class ImagePromptBuilder:
    """Builds optimized prompts for image generation."""

    STYLE_MODIFIERS = {
        ImageStyle.PROFESSIONAL: [
            "clean corporate design",
            "professional business aesthetic",
            "modern tech illustration",
            "sleek and polished"
        ],
        ImageStyle.ABSTRACT: [
            "abstract geometric shapes",
            "flowing gradients",
            "modern art style",
            "creative visualization"
        ],
        ImageStyle.INFOGRAPHIC: [
            "data visualization style",
            "clean infographic design",
            "informational layout",
            "chart and graph aesthetic"
        ],
        ImageStyle.MINIMALIST: [
            "minimalist design",
            "simple clean lines",
            "lots of white space",
            "understated elegance"
        ]
    }

    BASE_MODIFIERS = [
        "high quality",
        "4K resolution",
        "no text or words",
        "suitable for LinkedIn",
        "professional appearance"
    ]

    def build_prompt(
        self,
        content: str,
        style: ImageStyle = ImageStyle.PROFESSIONAL,
        mood: str = "innovative"
    ) -> str:
        """Build an optimized image generation prompt."""
        # Extract key concepts from content
        concepts = self._extract_concepts(content)

        # Get style modifiers
        style_mods = self.STYLE_MODIFIERS.get(style, self.STYLE_MODIFIERS[ImageStyle.PROFESSIONAL])

        # Build the prompt
        prompt_parts = [
            f"Create a {mood} image representing: {concepts}",
            ", ".join(style_mods[:2]),
            ", ".join(self.BASE_MODIFIERS[:3])
        ]

        return ". ".join(prompt_parts)

    def _extract_concepts(self, content: str) -> str:
        """Extract key concepts from content for image generation."""
        # Simple extraction - take first 200 chars and clean
        concepts = content[:200].replace("\n", " ").strip()

        # Remove hashtags
        concepts = re.sub(r"#\w+", "", concepts)

        # Remove URLs
        concepts = re.sub(r"http\S+", "", concepts)

        return concepts.strip()[:150]

    def get_negative_prompt(self, style: ImageStyle) -> str:
        """Get negative prompt to avoid unwanted elements."""
        return "text, words, letters, watermark, logo, low quality, blurry, distorted, ugly"


class DallE3Generator:
    """DALL-E 3 image generator."""

    def __init__(self):
        settings = get_settings()
        self._client = AsyncOpenAI(api_key=settings.openai_api_key)

    async def generate(
        self,
        prompt: str,
        size: ImageSize = ImageSize.LANDSCAPE,
        quality: str = "standard"
    ) -> GeneratedImage:
        """Generate an image using DALL-E 3."""
        response = await self._client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size=size.value,
            quality=quality,
            n=1,
            response_format="b64_json"
        )

        image_data = base64.b64decode(response.data[0].b64_json)

        return GeneratedImage(
            image_data=image_data,
            prompt_used=prompt,
            model_used="dall-e-3",
            revised_prompt=response.data[0].revised_prompt
        )


class StableDiffusionGenerator:
    """Stable Diffusion generator via Replicate API."""

    REPLICATE_API = "https://api.replicate.com/v1/predictions"
    MODEL_VERSION = "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b"

    def __init__(self):
        settings = get_settings()
        self._api_key = settings.replicate_api_key

    async def generate(
        self,
        prompt: str,
        negative_prompt: str = "",
        width: int = 1024,
        height: int = 1024
    ) -> GeneratedImage:
        """Generate an image using Stable Diffusion XL."""
        headers = {
            "Authorization": f"Token {self._api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "version": self.MODEL_VERSION.split(":")[-1],
            "input": {
                "prompt": prompt,
                "negative_prompt": negative_prompt or "low quality, blurry, text, watermark",
                "width": width,
                "height": height,
                "num_outputs": 1
            }
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            # Start prediction
            response = await client.post(
                self.REPLICATE_API,
                json=payload,
                headers=headers
            )
            response.raise_for_status()
            prediction = response.json()

            # Poll for completion
            prediction_url = prediction["urls"]["get"]
            while prediction["status"] not in ["succeeded", "failed"]:
                await asyncio.sleep(2)
                response = await client.get(prediction_url, headers=headers)
                prediction = response.json()

            if prediction["status"] == "failed":
                raise Exception(f"Image generation failed: {prediction.get('error')}")

            # Download image
            image_url = prediction["output"][0]
            image_response = await client.get(image_url)
            image_data = image_response.content

            return GeneratedImage(
                image_data=image_data,
                prompt_used=prompt,
                model_used="stable-diffusion-xl"
            )


class ImageGenerator:
    """Main image generation service with fallback."""

    def __init__(self):
        self._dalle = DallE3Generator()
        self._sd = StableDiffusionGenerator()
        self._prompt_builder = ImagePromptBuilder()

    async def generate_for_post(
        self,
        post_content: str,
        style: ImageStyle = ImageStyle.PROFESSIONAL,
        size: ImageSize = ImageSize.LANDSCAPE
    ) -> GeneratedImage:
        """Generate an image for a LinkedIn post."""
        # Build optimized prompt
        prompt = self._prompt_builder.build_prompt(post_content, style)

        # Try DALL-E 3 first
        try:
            return await self._dalle.generate(prompt, size)
        except Exception as dalle_error:
            print(f"DALL-E 3 failed: {dalle_error}, falling back to Stable Diffusion")

            # Fallback to Stable Diffusion
            try:
                negative_prompt = self._prompt_builder.get_negative_prompt(style)
                width, height = map(int, size.value.split("x"))
                return await self._sd.generate(prompt, negative_prompt, width, height)
            except Exception as sd_error:
                raise Exception(f"All image generators failed. DALL-E: {dalle_error}, SD: {sd_error}")

    async def generate_with_prompt(
        self,
        prompt: str,
        size: ImageSize = ImageSize.LANDSCAPE,
        use_fallback: bool = True
    ) -> GeneratedImage:
        """Generate an image with a custom prompt."""
        try:
            return await self._dalle.generate(prompt, size)
        except Exception as e:
            if use_fallback:
                return await self._sd.generate(prompt)
            raise


# Global instance
image_generator = ImageGenerator()
