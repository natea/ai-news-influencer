"""Background task scheduler using APScheduler."""
from datetime import datetime
from typing import Callable

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from src.core.config import get_settings


class TaskScheduler:
    """Manages background tasks for the application."""

    def __init__(self):
        self._scheduler = AsyncIOScheduler()
        self._settings = get_settings()

    def start(self) -> None:
        """Start the scheduler with default jobs."""
        # Scraping job - every 4 hours
        self._scheduler.add_job(
            self._scrape_job,
            IntervalTrigger(hours=self._settings.scrape_interval_hours),
            id="scrape_tweets",
            name="Scrape Twitter for news",
            replace_existing=True
        )

        # Post generation job - daily at 8 AM
        self._scheduler.add_job(
            self._generate_post_job,
            CronTrigger(hour=8, minute=0),
            id="generate_daily_post",
            name="Generate daily LinkedIn post",
            replace_existing=True
        )

        # Comment monitoring - every 15 minutes
        self._scheduler.add_job(
            self._monitor_comments_job,
            IntervalTrigger(minutes=15),
            id="monitor_comments",
            name="Monitor LinkedIn comments",
            replace_existing=True
        )

        # Metrics collection - daily at midnight
        self._scheduler.add_job(
            self._collect_metrics_job,
            CronTrigger(hour=0, minute=0),
            id="collect_metrics",
            name="Collect engagement metrics",
            replace_existing=True
        )

        self._scheduler.start()
        print(f"Scheduler started with {len(self._scheduler.get_jobs())} jobs")

    def shutdown(self) -> None:
        """Shutdown the scheduler."""
        self._scheduler.shutdown()

    def add_job(
        self,
        func: Callable,
        trigger: str,
        job_id: str,
        **kwargs
    ) -> None:
        """Add a custom job to the scheduler."""
        self._scheduler.add_job(
            func,
            trigger,
            id=job_id,
            replace_existing=True,
            **kwargs
        )

    def get_jobs(self) -> list[dict]:
        """Get all scheduled jobs."""
        return [
            {
                "id": job.id,
                "name": job.name,
                "next_run": job.next_run_time.isoformat() if job.next_run_time else None
            }
            for job in self._scheduler.get_jobs()
        ]

    async def _scrape_job(self) -> None:
        """Scrape tweets from target accounts."""
        print(f"[{datetime.utcnow()}] Running scrape job...")
        # Implementation would call twitter_scraper

    async def _generate_post_job(self) -> None:
        """Generate and schedule a LinkedIn post."""
        print(f"[{datetime.utcnow()}] Running post generation job...")
        # Implementation would call content selector and post generator

    async def _monitor_comments_job(self) -> None:
        """Check for new comments and generate responses."""
        print(f"[{datetime.utcnow()}] Running comment monitoring job...")
        # Implementation would call comment monitor

    async def _collect_metrics_job(self) -> None:
        """Collect engagement metrics for all posts."""
        print(f"[{datetime.utcnow()}] Running metrics collection job...")
        # Implementation would call metrics service


# Global scheduler instance
scheduler = TaskScheduler()
