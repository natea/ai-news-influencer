"""Prompt templates for AI agents."""
from typing import Optional

from src.agents.tools import PostStyle


class PromptTemplates:
    """Centralized prompt template management."""

    SYSTEM_PROMPTS = {
        "professional": """You are an expert LinkedIn content creator for a tech professional.
Your posts are insightful, engaging, and position the author as a thought leader in AI and technology.
You write in a clear, confident voice that balances professionalism with approachability.
You avoid jargon when simpler words work, but use technical terms accurately when needed.""",

        "casual": """You are a friendly tech enthusiast sharing interesting AI news on LinkedIn.
Your posts are conversational, relatable, and spark discussion.
You explain complex topics simply and invite engagement.""",

        "thought_leader": """You are a recognized AI industry expert sharing insights on LinkedIn.
Your posts demonstrate deep expertise, offer unique perspectives, and often challenge conventional thinking.
You back opinions with reasoning and invite intellectual discourse."""
    }

    POST_TEMPLATES = {
        PostStyle.INFORMATIVE: """Transform this AI/tech news into an engaging LinkedIn post:

Source: {source_author}
Content: {source_content}

Requirements:
- Lead with the key insight or implication for the industry
- Explain why this matters to {target_audience}
- Keep it under {max_length} characters
- Include 3-5 relevant hashtags at the end
{cta_instruction}

Write the LinkedIn post now:""",

        PostStyle.THOUGHT_LEADERSHIP: """Create a thought leadership post based on this news:

Source: {source_author}
Content: {source_content}

Requirements:
- Share a unique perspective or prediction based on this news
- Connect to broader industry trends
- Challenge the audience to think differently
- Keep it under {max_length} characters
- Include 3-5 relevant hashtags at the end
{cta_instruction}

Write the LinkedIn post now:""",

        PostStyle.COMMENTARY: """Write a commentary post on this AI/tech news:

Source: {source_author}
Content: {source_content}

Requirements:
- Give your professional take on this development
- Discuss implications for practitioners
- Be balanced but don't be afraid to have an opinion
- Keep it under {max_length} characters
- Include 3-5 relevant hashtags at the end
{cta_instruction}

Write the LinkedIn post now:""",

        PostStyle.ANNOUNCEMENT: """Craft an announcement-style post about this news:

Source: {source_author}
Content: {source_content}

Requirements:
- Present the news clearly and concisely
- Highlight what's new and significant
- Keep it under {max_length} characters
- Include 3-5 relevant hashtags at the end
{cta_instruction}

Write the LinkedIn post now:"""
    }

    RESPONSE_TEMPLATE = """You are responding to a comment on a LinkedIn post.

Original post: {original_post}

Comment from {commenter}: {comment}

Comment intent: {intent}

Requirements:
- Be {brand_voice} in tone
- Keep response under {max_length} characters
- Address their specific point
- Be genuine and helpful
{additional_context}

Write your response:"""

    def get_system_prompt(
        self,
        brand_voice: str = "professional",
        target_audience: str = "tech professionals"
    ) -> str:
        """Get the system prompt for post generation."""
        base_prompt = self.SYSTEM_PROMPTS.get(brand_voice, self.SYSTEM_PROMPTS["professional"])
        return f"{base_prompt}\n\nTarget audience: {target_audience}"

    def get_post_generation_prompt(
        self,
        source_content: str,
        source_author: str,
        post_style: PostStyle = PostStyle.INFORMATIVE,
        include_cta: bool = True,
        max_length: int = 2000,
        target_audience: str = "tech professionals"
    ) -> str:
        """Get the prompt for generating a post."""
        template = self.POST_TEMPLATES.get(post_style, self.POST_TEMPLATES[PostStyle.INFORMATIVE])

        cta_instruction = "- End with an engaging question to spark discussion" if include_cta else ""

        return template.format(
            source_content=source_content,
            source_author=source_author,
            target_audience=target_audience,
            max_length=max_length,
            cta_instruction=cta_instruction
        )

    def get_response_prompt(
        self,
        original_post: str,
        comment: str,
        commenter: str,
        intent: str,
        brand_voice: str = "professional",
        max_length: int = 500,
        additional_context: str = ""
    ) -> str:
        """Get the prompt for generating a comment response."""
        return self.RESPONSE_TEMPLATE.format(
            original_post=original_post,
            comment=comment,
            commenter=commenter,
            intent=intent,
            brand_voice=brand_voice,
            max_length=max_length,
            additional_context=additional_context
        )
