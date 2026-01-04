"""Content selector agent for ranking and selecting news to post."""
from datetime import datetime
from typing import Optional

from src.agents.base import BaseAgent, AgentContext, AgentResult
from src.agents.tools import (
    ContentRankingOutput,
    ContentSelectionInput,
    ContentSelectionOutput,
    ContentCategory,
)
from src.database.models import DecisionType, ScrapedTweet


class ContentSelectorAgent(BaseAgent[ContentSelectionInput, ContentSelectionOutput]):
    """Agent for selecting the best content to post."""

    name = "ContentSelector"
    description = "Ranks and selects the most relevant content for LinkedIn posts"
    decision_type = DecisionType.CONTENT_SELECTION

    # Keywords for topic matching
    AI_KEYWORDS = {
        "ai", "artificial intelligence", "machine learning", "ml", "deep learning",
        "neural network", "llm", "gpt", "claude", "chatgpt", "transformer",
        "generative ai", "foundation model", "language model", "diffusion",
        "reinforcement learning", "computer vision", "nlp", "rag"
    }

    TECH_KEYWORDS = {
        "startup", "funding", "acquisition", "launch", "release", "update",
        "api", "developer", "open source", "github", "platform", "cloud"
    }

    def __init__(self, context: Optional[AgentContext] = None):
        super().__init__(context)
        self._recent_topics: set[str] = set()

    async def execute(
        self, input_data: ContentSelectionInput
    ) -> AgentResult[ContentSelectionOutput]:
        """Select the best content from ranked candidates."""

        if not input_data.candidates:
            return AgentResult(
                success=True,
                output=ContentSelectionOutput(
                    selected_ids=[],
                    reasoning="No candidates provided for selection."
                ),
                reasoning="Empty candidate list"
            )

        # Filter and sort candidates
        valid_candidates = [
            c for c in input_data.candidates
            if c.should_process and c.relevance_score >= 0.5
        ]

        # Apply category preferences
        if input_data.prefer_categories:
            preferred = [c for c in valid_candidates if c.category in input_data.prefer_categories]
            if preferred:
                valid_candidates = preferred + [c for c in valid_candidates if c not in preferred]

        # Sort by relevance score
        sorted_candidates = sorted(
            valid_candidates,
            key=lambda x: (x.relevance_score * 0.4 + x.engagement_potential * 0.3 + x.timeliness * 0.3),
            reverse=True
        )

        # Select top candidates
        selected = sorted_candidates[:input_data.max_selections]
        selected_ids = [c.tweet_id for c in selected]

        reasoning = self._build_reasoning(selected, input_data)

        return AgentResult(
            success=True,
            output=ContentSelectionOutput(
                selected_ids=selected_ids,
                reasoning=reasoning
            ),
            reasoning=reasoning
        )

    async def rank_tweet(self, tweet: ScrapedTweet) -> ContentRankingOutput:
        """Rank a single tweet for relevance."""
        content_lower = tweet.content.lower()

        # Calculate topic match
        ai_matches = sum(1 for kw in self.AI_KEYWORDS if kw in content_lower)
        tech_matches = sum(1 for kw in self.TECH_KEYWORDS if kw in content_lower)
        topic_match = min(1.0, (ai_matches * 0.15 + tech_matches * 0.1))

        # Determine category
        if ai_matches > tech_matches:
            category = ContentCategory.AI_RESEARCH
        elif "launch" in content_lower or "release" in content_lower:
            category = ContentCategory.PRODUCT_LAUNCH
        else:
            category = ContentCategory.INDUSTRY_NEWS

        # Calculate timeliness (decay over 24 hours)
        timeliness = 1.0
        if tweet.posted_at:
            hours_old = (datetime.utcnow() - tweet.posted_at).total_seconds() / 3600
            timeliness = max(0.1, 1.0 - (hours_old / 48))

        # Calculate engagement potential
        total_engagement = tweet.likes + tweet.retweets * 2 + tweet.replies * 3
        engagement_potential = min(1.0, total_engagement / 10000)

        # Overall relevance
        relevance_score = (
            topic_match * 0.4 +
            timeliness * 0.3 +
            engagement_potential * 0.3
        )

        should_process = relevance_score >= 0.4 and topic_match >= 0.2

        return ContentRankingOutput(
            tweet_id=tweet.id,
            relevance_score=round(relevance_score, 3),
            topic_match=round(topic_match, 3),
            timeliness=round(timeliness, 3),
            engagement_potential=round(engagement_potential, 3),
            category=category,
            reasoning=f"AI keywords: {ai_matches}, Tech keywords: {tech_matches}, Engagement: {total_engagement}",
            should_process=should_process
        )

    def _build_reasoning(
        self,
        selected: list[ContentRankingOutput],
        input_data: ContentSelectionInput
    ) -> str:
        """Build explanation for selection."""
        if not selected:
            return "No candidates met the minimum quality threshold (0.5 relevance score)."

        reasons = []
        for i, candidate in enumerate(selected, 1):
            reasons.append(
                f"{i}. Tweet {candidate.tweet_id}: "
                f"relevance={candidate.relevance_score:.2f}, "
                f"category={candidate.category.value}"
            )

        return "Selected based on relevance and engagement potential:\n" + "\n".join(reasons)
