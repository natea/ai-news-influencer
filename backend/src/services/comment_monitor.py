"""Comment monitoring service for LinkedIn posts."""
import asyncio
from datetime import datetime, timedelta
from typing import Optional

from pydantic import BaseModel

from src.database.models import Comment, CommentIntent, GeneratedPost
from src.integrations.linkedin import linkedin_client, LinkedInComment
from src.integrations.claude import claude_client


class CommentMonitorConfig(BaseModel):
    """Configuration for comment monitoring."""
    poll_interval_seconds: int = 900  # 15 minutes
    max_response_delay_hours: int = 24
    auto_respond: bool = False
    ignore_spam: bool = True


class ProcessedComment(BaseModel):
    """A comment with classification."""
    comment: Comment
    intent: CommentIntent
    priority: str
    requires_response: bool


class CommentMonitor:
    """Service for monitoring and processing LinkedIn comments."""

    def __init__(self, config: Optional[CommentMonitorConfig] = None):
        self.config = config or CommentMonitorConfig()
        self._running = False
        self._processed_ids: set[str] = set()

    async def start(self) -> None:
        """Start the comment monitoring loop."""
        self._running = True
        while self._running:
            try:
                await self._poll_comments()
            except Exception as e:
                print(f"Error polling comments: {e}")

            await asyncio.sleep(self.config.poll_interval_seconds)

    def stop(self) -> None:
        """Stop the monitoring loop."""
        self._running = False

    async def _poll_comments(self) -> list[ProcessedComment]:
        """Poll for new comments on recent posts."""
        # Get recent published posts (last 7 days)
        # In real implementation, this would query the database
        recent_posts = await self._get_recent_posts()

        all_comments = []
        for post in recent_posts:
            if not post.linkedin_post_id:
                continue

            try:
                comments = await linkedin_client.get_post_comments(post.linkedin_post_id)

                for linkedin_comment in comments:
                    if linkedin_comment.id in self._processed_ids:
                        continue

                    processed = await self._process_comment(linkedin_comment, post)
                    if processed:
                        all_comments.append(processed)
                        self._processed_ids.add(linkedin_comment.id)

            except Exception as e:
                print(f"Error fetching comments for post {post.id}: {e}")

        return all_comments

    async def _process_comment(
        self,
        linkedin_comment: LinkedInComment,
        post: GeneratedPost
    ) -> Optional[ProcessedComment]:
        """Process and classify a comment."""
        # Classify the comment using Claude
        try:
            classification = await claude_client.analyze_content(
                linkedin_comment.content,
                analysis_type="intent"
            )

            intent = CommentIntent(classification.get("intent", "other"))
            priority = classification.get("priority", "medium")
            requires_response = classification.get("requires_response", True)

            # Skip spam if configured
            if self.config.ignore_spam and intent == CommentIntent.SPAM:
                return None

            comment = Comment(
                id=linkedin_comment.id,
                post_id=post.id,
                author_name=linkedin_comment.author_name,
                author_id=linkedin_comment.author_id,
                content=linkedin_comment.content,
                intent=intent,
                created_at=linkedin_comment.created_at
            )

            return ProcessedComment(
                comment=comment,
                intent=intent,
                priority=priority,
                requires_response=requires_response
            )

        except Exception as e:
            print(f"Error classifying comment: {e}")
            return None

    async def _get_recent_posts(self) -> list[GeneratedPost]:
        """Get recently published posts."""
        # This would query the database in real implementation
        # For now, return empty list
        return []

    async def get_pending_comments(self) -> list[ProcessedComment]:
        """Get comments that need responses."""
        await self._poll_comments()

        # Filter for comments needing response
        # In real implementation, this would query the database
        return []


# Global instance
comment_monitor = CommentMonitor()
