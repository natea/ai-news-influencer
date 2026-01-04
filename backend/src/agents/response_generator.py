"""Response generator agent for handling LinkedIn comments."""

from typing import Optional

from src.agents.base import AgentContext, AgentResult, BaseAgent
from src.agents.tools import (
    CommentClassificationInput,
    CommentClassificationOutput,
    ResponseGenerationInput,
    ResponseGenerationOutput,
)
from src.core.embeddings import embedding_service
from src.database.models import DecisionType
from src.integrations.claude import ClaudeClient


class ResponseGeneratorAgent(BaseAgent[ResponseGenerationInput, ResponseGenerationOutput]):
    """Agent for generating responses to LinkedIn comments."""

    name = "ResponseGenerator"
    description = "Generates contextual, professional responses to LinkedIn comments"
    decision_type = DecisionType.RESPONSE_GENERATION

    RESPONSE_TEMPLATES = {
        "question": """Respond helpfully to this question:
- Address the specific question asked
- Provide clear, accurate information
- Offer to elaborate if needed
- Keep it professional and friendly""",

        "feedback": """Respond to this feedback:
- Acknowledge their perspective
- Thank them for engaging
- Add value to the discussion
- Maintain a professional tone""",

        "compliment": """Respond to this positive comment:
- Express genuine gratitude
- Keep it brief and authentic
- Encourage continued engagement
- Avoid being overly effusive""",

        "criticism": """Respond to this critical comment:
- Acknowledge their viewpoint respectfully
- Provide clarification if needed
- Stay professional and non-defensive
- Look for common ground""",

        "other": """Respond to this comment:
- Acknowledge their engagement
- Add value to the conversation
- Keep it professional and friendly""",
    }

    def __init__(self, context: Optional[AgentContext] = None):
        super().__init__(context)
        self._claude = ClaudeClient()
        self._embedding_service = embedding_service

    async def classify_comment(
        self, input_data: CommentClassificationInput
    ) -> CommentClassificationOutput:
        """Classify a comment's intent and priority."""

        prompt = f"""Analyze this LinkedIn comment and classify it:

Comment: "{input_data.comment_content}"
Author: {input_data.comment_author}
Original Post: "{input_data.original_post_content[:200]}..."

Classify the:
1. Intent: question, feedback, compliment, criticism, spam, or other
2. Sentiment: positive, negative, or neutral
3. Whether it requires a response (true/false)
4. Priority: high, medium, or low

Respond with JSON containing: intent, sentiment, requires_response, priority, reasoning"""

        try:
            response = await self._claude.generate(
                prompt=prompt,
                system="You are a social media analyst classifying comment intents.",
                max_tokens=300,
                temperature=0.3,
            )

            import json
            import re

            json_match = re.search(r"\{[\s\S]*\}", response)
            if json_match:
                data = json.loads(json_match.group())
                return CommentClassificationOutput(
                    intent=data.get("intent", "other"),
                    sentiment=data.get("sentiment", "neutral"),
                    requires_response=data.get("requires_response", True),
                    priority=data.get("priority", "medium"),
                    reasoning=data.get("reasoning", "Classification based on content analysis"),
                )
        except Exception:
            pass

        # Default classification
        return CommentClassificationOutput(
            intent="other",
            sentiment="neutral",
            requires_response=True,
            priority="medium",
            reasoning="Default classification applied",
        )

    async def _get_rag_context(
        self,
        comment: str,
        original_post: str
    ) -> str:
        """Retrieve relevant context from past posts using RAG."""
        try:
            # Search for similar past posts
            results = await self._embedding_service.search_similar(
                query=f"{comment} {original_post}",
                k=3,
                doc_type="post"
            )

            if not results:
                return ""

            context_parts = ["Related past content:"]
            for r in results:
                context_parts.append(f"- {r['content'][:200]}...")

            return "\n".join(context_parts)

        except Exception:
            return ""

    async def execute(
        self, input_data: ResponseGenerationInput
    ) -> AgentResult[ResponseGenerationOutput]:
        """Generate a response to a comment."""

        # Get the appropriate template
        template = self.RESPONSE_TEMPLATES.get(
            input_data.comment_intent, self.RESPONSE_TEMPLATES["other"]
        )

        # Build context from conversation history
        history_context = ""
        if input_data.conversation_history:
            history_lines = []
            for item in input_data.conversation_history[-3:]:
                history_lines.append(f"- {item.get('author', 'User')}: {item.get('content', '')[:100]}")
            history_context = f"\n\nConversation context:\n" + "\n".join(history_lines)

        # Get RAG context from past posts
        rag_context = await self._get_rag_context(
            input_data.comment_content,
            input_data.original_post_content
        )
        if rag_context:
            history_context += f"\n\n{rag_context}"

        prompt = f"""{template}

Original Post: "{input_data.original_post_content[:300]}..."

Comment from {input_data.comment_author}: "{input_data.comment_content}"
{history_context}

Guidelines:
- Use a {input_data.brand_voice} tone
- Keep response under {input_data.max_length} characters
- Be authentic and add value
- Don't be overly promotional

Respond with JSON containing:
- response: The reply text
- tone: The tone used (friendly, professional, helpful, etc.)
- addresses_question: Whether you answered a question (true/false)
- quality_score: Self-assessed quality from 0-1"""

        try:
            response = await self._claude.generate(
                prompt=prompt,
                system="You are a professional social media manager responding to LinkedIn comments. Be helpful, authentic, and engaging.",
                max_tokens=500,
                temperature=0.6,
            )

            import json
            import re

            json_match = re.search(r"\{[\s\S]*\}", response)
            if json_match:
                data = json.loads(json_match.group())
            else:
                data = {
                    "response": response[:input_data.max_length],
                    "tone": input_data.brand_voice,
                    "addresses_question": False,
                    "quality_score": 0.7,
                }

            output = ResponseGenerationOutput(
                response=data.get("response", response)[:input_data.max_length],
                tone=data.get("tone", input_data.brand_voice),
                addresses_question=data.get("addresses_question", False),
                quality_score=data.get("quality_score", 0.7),
            )

            return AgentResult(
                success=True,
                output=output,
                reasoning=f"Generated {output.tone} response with quality {output.quality_score:.2f}",
            )

        except Exception as e:
            return AgentResult(
                success=False,
                error=str(e),
                reasoning=f"Failed to generate response: {str(e)}",
            )

    def should_respond(self, classification: CommentClassificationOutput) -> bool:
        """Determine if we should respond to a comment."""
        # Don't respond to spam
        if classification.intent == "spam":
            return False

        # Always respond to questions
        if classification.intent == "question":
            return True

        # Respond based on the classification
        return classification.requires_response
