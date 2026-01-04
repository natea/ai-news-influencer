"""Metrics and analytics API routes."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.session import get_db
from src.services.metrics import MetricsService

router = APIRouter()


@router.get("/overview")
async def get_overview(
    days: int = Query(7, ge=1, le=90),
    db: AsyncSession = Depends(get_db),
):
    """Get overview statistics for the dashboard."""
    service = MetricsService(db)
    stats = await service.get_overview_stats(days=days)
    return stats


@router.get("/trending-hashtags")
async def get_trending_hashtags(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    """Get top performing hashtags."""
    service = MetricsService(db)
    hashtags = await service.get_trending_hashtags(limit=limit)
    return {"hashtags": hashtags}


@router.get("/best-times")
async def get_best_posting_times(db: AsyncSession = Depends(get_db)):
    """Get analysis of best posting times."""
    service = MetricsService(db)
    times = await service.get_best_posting_times()
    return {"posting_times": times}


@router.post("/collect")
async def collect_metrics(db: AsyncSession = Depends(get_db)):
    """Manually trigger metrics collection for all posts."""
    from src.api.routes.auth import _stored_tokens

    service = MetricsService(db)

    if "default" in _stored_tokens:
        service._linkedin.set_tokens(_stored_tokens["default"])

    metrics = await service.collect_all_post_metrics()

    return {
        "message": "Metrics collected",
        "posts_updated": len(metrics),
    }


@router.get("/posts/{post_id}")
async def get_post_metrics(post_id: str, db: AsyncSession = Depends(get_db)):
    """Get metrics for a specific post."""
    from sqlalchemy import select
    from src.database.models import EngagementMetric

    result = await db.execute(
        select(EngagementMetric)
        .where(EngagementMetric.post_id == post_id)
        .order_by(EngagementMetric.measured_at.desc())
    )
    metrics = result.scalars().all()

    if not metrics:
        return {"post_id": post_id, "metrics": [], "message": "No metrics found"}

    latest = metrics[0]
    history = [
        {
            "measured_at": m.measured_at.isoformat(),
            "likes": m.likes,
            "comments": m.comments,
            "shares": m.shares,
            "impressions": m.impressions,
            "engagement_rate": m.engagement_rate,
        }
        for m in metrics[:10]
    ]

    return {
        "post_id": post_id,
        "latest": {
            "likes": latest.likes,
            "comments": latest.comments,
            "shares": latest.shares,
            "impressions": latest.impressions,
            "engagement_rate": latest.engagement_rate,
            "click_through_rate": latest.click_through_rate,
        },
        "history": history,
    }
