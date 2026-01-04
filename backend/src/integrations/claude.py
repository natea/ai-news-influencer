"""Claude API integration with structured outputs."""
import json
from typing import Any, Type, TypeVar

from anthropic import AsyncAnthropic
from pydantic import BaseModel

from src.core.config import get_settings

T = TypeVar("T", bound=BaseModel)


class ClaudeClient:
    """Async client for Claude API with structured output support."""

    def __init__(self):
        settings = get_settings()
        self._client = AsyncAnthropic(api_key=settings.anthropic_api_key)
        self._model = settings.claude_model

    async def generate(
        self,
        prompt: str,
        system: str = "",
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> str:
        """Generate text completion."""
        messages = [{"role": "user", "content": prompt}]

        response = await self._client.messages.create(
            model=self._model,
            max_tokens=max_tokens,
            system=system if system else None,
            messages=messages,
            temperature=temperature
        )

        return response.content[0].text

    async def generate_structured(
        self,
        prompt: str,
        output_schema: Type[T],
        system: str = "",
        max_tokens: int = 1000
    ) -> T:
        """Generate structured output matching a Pydantic schema."""
        schema_json = json.dumps(output_schema.model_json_schema(), indent=2)

        structured_prompt = f"""{prompt}

Respond with valid JSON matching this schema:
{schema_json}

JSON response:"""

        response_text = await self.generate(
            prompt=structured_prompt,
            system=system,
            max_tokens=max_tokens,
            temperature=0.3  # Lower temperature for structured output
        )

        # Extract JSON from response
        json_str = self._extract_json(response_text)
        data = json.loads(json_str)

        return output_schema.model_validate(data)

    async def analyze_content(
        self,
        content: str,
        analysis_type: str = "relevance"
    ) -> dict[str, Any]:
        """Analyze content for various purposes."""
        prompts = {
            "relevance": f"""Analyze this content for AI/tech relevance:

Content: {content}

Return JSON with:
- relevance_score (0-1)
- main_topics (list)
- key_entities (list)
- sentiment (positive/negative/neutral)""",

            "quality": f"""Assess the quality of this LinkedIn post:

Content: {content}

Return JSON with:
- quality_score (0-1)
- strengths (list)
- weaknesses (list)
- suggestions (list)""",

            "intent": f"""Classify the intent of this comment:

Content: {content}

Return JSON with:
- intent (question/feedback/compliment/criticism/spam/other)
- sentiment (positive/negative/neutral)
- requires_response (boolean)
- priority (high/medium/low)"""
        }

        prompt = prompts.get(analysis_type, prompts["relevance"])
        response = await self.generate(prompt, max_tokens=500, temperature=0.2)

        return json.loads(self._extract_json(response))

    async def generate_linkedin_post(
        self,
        source_content: str,
        style: str = "informative",
        max_length: int = 3000
    ) -> dict[str, Any]:
        """Generate a LinkedIn post from source content.

        Args:
            source_content: The source tweet or content to transform
            style: Post style (informative, thought_leadership, commentary)
            max_length: Maximum post length

        Returns:
            Dict with 'content' and 'hashtags' keys
        """
        style_prompts = {
            "informative": "educational and informative, sharing key insights and facts",
            "thought_leadership": "thought-provoking with original perspectives and industry expertise",
            "commentary": "engaging commentary with personal opinions and calls to action"
        }

        style_description = style_prompts.get(style, style_prompts["informative"])

        prompt = f"""Transform this tweet into a professional LinkedIn post that is {style_description}.

Source Tweet:
{source_content}

Guidelines:
- Write in a professional but engaging tone suitable for LinkedIn
- Add value beyond the original tweet with insights or context
- Include a clear call-to-action or question to drive engagement
- Keep it under {max_length} characters
- Suggest 3-5 relevant hashtags

Respond with JSON:
{{
    "content": "The LinkedIn post text",
    "hashtags": ["hashtag1", "hashtag2", "hashtag3"]
}}"""

        response = await self.generate(prompt, max_tokens=1500, temperature=0.7)

        try:
            return json.loads(self._extract_json(response))
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            return {
                "content": response,
                "hashtags": []
            }

    def _extract_json(self, text: str) -> str:
        """Extract JSON from text that might contain other content."""
        # Try to find JSON block
        import re

        # Look for ```json block
        json_match = re.search(r"```json\s*([\s\S]*?)\s*```", text)
        if json_match:
            return json_match.group(1)

        # Look for raw JSON object or array
        json_match = re.search(r"(\{[\s\S]*\}|\[[\s\S]*\])", text)
        if json_match:
            return json_match.group(1)

        return text.strip()


# Global client instance
claude_client = ClaudeClient()
