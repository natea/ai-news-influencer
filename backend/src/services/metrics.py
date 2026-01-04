"""Metrics collection and analysis service."""
from datetime import datetime, timedelta
from typing import Optional

from pydantic import BaseModel

from src.database.models import EngagementMetrics, GeneratedPost
from src.integrations.linkedin import linkedin_client


class MetricsSummary(BaseModel):
    """Summary of engagement metrics."""
    total_posts: int
    total_likes: int
    total_comments: int
    total_shares: int
    total_impressions: int
    avg_engagement_rate: float
    response_rate: float


class PostPerformance(BaseModel):
    """Performance analysis for a single post."""
    post_id: str
    content_preview: str
    metrics: EngagementMetrics
    performance_score: float
    hashtag_performance: dict[str, float]


class TrendData(BaseModel):
    """Time series trend data."""
    date: str
    likes: int
    comments: int
    shares: int
    impressions: int


class MetricsService:
    """Service for collecting and analyzing engagement metrics."""

    def __init__(self):
        self._cache: dict[str, EngagementMetrics] = {}

    async def collect_metrics(self, post_id: str, linkedin_post_urn: str) -> EngagementMetrics:
        """Collect current metrics for a post from LinkedIn."""
        try:
            raw_metrics = await linkedin_client.get_post_metrics(linkedin_post_urn)

            metrics = EngagementMetrics(
                id=0,
                post_id=post_id,
                likes=raw_metrics.get("likes", 0),
                comments=raw_metrics.get("comments", 0),
                shares=raw_metrics.get("shares", 0),
                impressions=raw_metrics.get("impressions", 0),
            )

            # Calculate rates
            if metrics.impressions > 0:
                total_engagement = metrics.likes + metrics.comments + metrics.shares
                metrics.engagement_rate = total_engagement / metrics.impressions

            self._cache[post_id] = metrics
            return metrics

        except Exception as e:
            print(f"Error collecting metrics for {post_id}: {e}")
            return self._cache.get(post_id, EngagementMetrics(id=0, post_id=post_id))

    async def get_summary(self, days: int = 7) -> MetricsSummary:
        """Get summary metrics for the specified period."""
        # In real implementation, this would query the database
        return MetricsSummary(
            total_posts=47,
            total_likes=2150,
            total_comments=412,
            total_shares=189,
            total_impressions=124000,
            avg_engagement_rate=0.042,
            response_rate=0.87
        )

    async def get_trends(self, days: int = 7) -> list[TrendData]:
        """Get daily engagement trends."""
        trends = []
        for i in range(days):
            date = datetime.utcnow() - timedelta(days=days - i - 1)
            trends.append(TrendData(
                date=date.strftime("%Y-%m-%d"),
                likes=45 + i * 5,
                comments=12 + i * 2,
                shares=8 + i,
                impressions=1200 + i * 100
            ))
        return trends

    async def analyze_post_performance(self, post_id: str) -> PostPerformance:
        """Analyze performance of a specific post."""
        metrics = self._cache.get(post_id)
        if not metrics:
            metrics = EngagementMetrics(id=0, post_id=post_id)

        # Calculate performance score
        score = self._calculate_performance_score(metrics)

        return PostPerformance(
            post_id=post_id,
            content_preview="Post content...",
            metrics=metrics,
            performance_score=score,
            hashtag_performance={}
        )

    def _calculate_performance_score(self, metrics: EngagementMetrics) -> float:
        """Calculate overall performance score (0-1)."""
        if metrics.impressions == 0:
            return 0.0

        # Weighted engagement rate
        weighted_engagement = (
            metrics.likes * 1 +
            metrics.comments * 3 +
            metrics.shares * 5
        )

        # Normalize to 0-1 scale (assuming 10% weighted engagement is excellent)
        score = min(1.0, (weighted_engagement / metrics.impressions) / 0.1)

        return round(score, 3)

    async def get_best_posting_times(self) -> list[dict]:
        """Analyze best times to post based on historical data."""
        # Would analyze historical engagement by hour/day
        return [
            {"day": "Tuesday", "hour": 9, "avg_engagement": 0.052},
            {"day": "Wednesday", "hour": 10, "avg_engagement": 0.048},
            {"day": "Thursday", "hour": 14, "avg_engagement": 0.045},
        ]

    async def get_top_hashtags(self, limit: int = 10) -> list[dict]:
        """Get top performing hashtags."""
        return [
            {"hashtag": "#AI", "avg_engagement": 0.055, "usage_count": 35},
            {"hashtag": "#MachineLearning", "avg_engagement": 0.048, "usage_count": 28},
            {"hashtag": "#LLM", "avg_engagement": 0.044, "usage_count": 22},
        ]


# Global instance
metrics_service = MetricsService()
