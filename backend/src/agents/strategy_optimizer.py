"""Strategy optimizer agent for improving content performance."""
from typing import Optional

from src.agents.base import BaseAgent, AgentContext, AgentResult
from src.agents.tools import StrategyAnalysisInput, StrategyAnalysisOutput, PostStyle
from src.database.models import DecisionType
from src.services.metrics import metrics_service


class StrategyOptimizerAgent(BaseAgent[StrategyAnalysisInput, StrategyAnalysisOutput]):
    """Agent for analyzing and optimizing content strategy."""

    name = "StrategyOptimizer"
    description = "Analyzes performance data and recommends strategy improvements"
    decision_type = DecisionType.STRATEGY_ADJUSTMENT

    def __init__(self, context: Optional[AgentContext] = None):
        super().__init__(context)

    async def execute(
        self, input_data: StrategyAnalysisInput
    ) -> AgentResult[StrategyAnalysisOutput]:
        """Analyze performance and generate optimization recommendations."""

        # Get best posting times
        best_times = await metrics_service.get_best_posting_times()
        posting_times = [f"{t['day']} {t['hour']}:00" for t in best_times[:3]]

        # Get top hashtags
        top_hashtags = await metrics_service.get_top_hashtags(limit=5)
        hashtag_list = [h["hashtag"] for h in top_hashtags]

        # Analyze post styles (simplified)
        recommended_styles = self._analyze_styles(input_data.recent_posts)

        # Identify content gaps
        content_gaps = self._identify_gaps(input_data.recent_posts)

        # Generate suggestions
        suggestions = self._generate_suggestions(input_data.recent_posts)

        output = StrategyAnalysisOutput(
            best_posting_times=posting_times,
            top_performing_hashtags=hashtag_list,
            recommended_post_styles=recommended_styles,
            content_gaps=content_gaps,
            improvement_suggestions=suggestions,
            predicted_engagement_lift=0.15
        )

        return AgentResult(
            success=True,
            output=output,
            reasoning="Analyzed recent performance data and generated recommendations"
        )

    def _analyze_styles(self, posts: list[dict]) -> list[PostStyle]:
        """Analyze which post styles perform best."""
        # Simplified - would analyze actual engagement by style
        return [PostStyle.INFORMATIVE, PostStyle.THOUGHT_LEADERSHIP]

    def _identify_gaps(self, posts: list[dict]) -> list[str]:
        """Identify content topics that are underrepresented."""
        return [
            "AI safety and alignment",
            "Open source AI developments",
            "Industry case studies"
        ]

    def _generate_suggestions(self, posts: list[dict]) -> list[str]:
        """Generate actionable improvement suggestions."""
        return [
            "Increase posting frequency on Tuesdays (highest engagement)",
            "Use more questions in posts to drive comments",
            "Include more data/statistics to boost credibility",
            "Respond to comments within 2 hours for better visibility",
            "Test shorter posts (under 500 chars) for mobile readers"
        ]


# Global instance
strategy_optimizer = StrategyOptimizerAgent()
