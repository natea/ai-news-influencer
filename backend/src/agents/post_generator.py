"""Post generator agent for creating LinkedIn content."""
import re
from typing import Optional

from anthropic import AsyncAnthropic

from src.agents.base import BaseAgent, AgentContext, AgentResult
from src.agents.tools import PostGenerationInput, PostGenerationOutput, PostStyle
from src.core.config import get_settings
from src.core.prompts import PromptTemplates
from src.database.models import DecisionType


class PostGeneratorAgent(BaseAgent[PostGenerationInput, PostGenerationOutput]):
    """Agent for generating LinkedIn posts from source content."""

    name = "PostGenerator"
    description = "Generates engaging LinkedIn posts from news content"
    decision_type = DecisionType.POST_GENERATION

    def __init__(self, context: Optional[AgentContext] = None):
        super().__init__(context)
        settings = get_settings()
        self._client = AsyncAnthropic(api_key=settings.anthropic_api_key)
        self._model = settings.claude_model
        self._prompts = PromptTemplates()

    async def execute(
        self, input_data: PostGenerationInput
    ) -> AgentResult[PostGenerationOutput]:
        """Generate a LinkedIn post from source content."""

        # Build the prompt
        system_prompt = self._prompts.get_system_prompt(
            brand_voice=input_data.brand_voice,
            target_audience=input_data.target_audience
        )

        user_prompt = self._prompts.get_post_generation_prompt(
            source_content=input_data.source_content,
            source_author=input_data.source_author,
            post_style=input_data.post_style,
            include_cta=input_data.include_cta,
            max_length=input_data.max_length
        )

        try:
            response = await self._client.messages.create(
                model=self._model,
                max_tokens=1000,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}]
            )

            generated_content = response.content[0].text

            # Extract hashtags from content or generate them
            hashtags = self._extract_hashtags(generated_content)

            # Clean content (remove hashtags from body if they're at the end)
            clean_content = self._clean_content(generated_content)

            # Assess quality
            quality_score = self._assess_quality(clean_content, input_data)

            output = PostGenerationOutput(
                content=clean_content,
                hashtags=hashtags[:5],
                mentions=[],
                call_to_action=self._extract_cta(clean_content) if input_data.include_cta else None,
                quality_score=quality_score
            )

            return AgentResult(
                success=True,
                output=output,
                reasoning=f"Generated {len(clean_content)} char post with {len(hashtags)} hashtags",
                tokens_used=response.usage.input_tokens + response.usage.output_tokens
            )

        except Exception as e:
            return AgentResult(
                success=False,
                error=str(e),
                reasoning=f"Failed to generate post: {e}"
            )

    def _extract_hashtags(self, content: str) -> list[str]:
        """Extract hashtags from generated content."""
        hashtags = re.findall(r"#(\w+)", content)
        # Deduplicate while preserving order
        seen: set[str] = set()
        unique: list[str] = []
        for tag in hashtags:
            if tag.lower() not in seen:
                seen.add(tag.lower())
                unique.append(tag)
        return unique

    def _clean_content(self, content: str) -> str:
        """Clean up generated content."""
        # Remove trailing hashtag block if present
        lines = content.strip().split("\n")
        cleaned_lines: list[str] = []
        for line in lines:
            # Keep line if it's not just hashtags
            if not re.match(r"^[\s#\w]+$", line) or not line.strip().startswith("#"):
                cleaned_lines.append(line)
            elif cleaned_lines:  # Keep hashtag lines in the middle
                cleaned_lines.append(line)
        return "\n".join(cleaned_lines).strip()

    def _extract_cta(self, content: str) -> Optional[str]:
        """Extract call-to-action from content."""
        cta_patterns = [
            r"(What do you think\?.*)",
            r"(Let me know.*)",
            r"(Share your thoughts.*)",
            r"(Comment below.*)",
            r"(What's your take.*)"
        ]
        for pattern in cta_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return match.group(1)
        return None

    def _assess_quality(self, content: str, input_data: PostGenerationInput) -> float:
        """Assess the quality of generated content."""
        score = 0.5  # Base score

        # Length check
        if 200 <= len(content) <= input_data.max_length:
            score += 0.1

        # Has structure (paragraphs or line breaks)
        if "\n" in content:
            score += 0.1

        # Mentions source
        if input_data.source_author.lower() in content.lower():
            score += 0.1

        # Has engagement element
        if "?" in content:
            score += 0.1

        # Not too promotional
        promo_words = ["buy", "subscribe", "click", "link in bio"]
        if not any(word in content.lower() for word in promo_words):
            score += 0.1

        return min(1.0, score)
