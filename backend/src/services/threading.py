"""Conversation threading service for managing comment chains."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from src.database.models import Comment


class ThreadMessage(BaseModel):
    """A message in a conversation thread."""
    id: str
    author: str
    content: str
    is_our_response: bool
    timestamp: datetime
    parent_id: Optional[str] = None


class ConversationThread(BaseModel):
    """A complete conversation thread."""
    post_id: str
    root_comment_id: str
    messages: list[ThreadMessage]
    last_activity: datetime
    is_resolved: bool = False


class ThreadingService:
    """Service for managing conversation threads."""

    def __init__(self):
        self._threads: dict[str, ConversationThread] = {}

    def create_thread(
        self,
        post_id: str,
        comment: Comment
    ) -> ConversationThread:
        """Create a new conversation thread from a comment."""
        message = ThreadMessage(
            id=comment.id,
            author=comment.author_name,
            content=comment.content,
            is_our_response=False,
            timestamp=comment.created_at
        )

        thread = ConversationThread(
            post_id=post_id,
            root_comment_id=comment.id,
            messages=[message],
            last_activity=comment.created_at
        )

        self._threads[comment.id] = thread
        return thread

    def add_response(
        self,
        thread_id: str,
        response_id: str,
        response_content: str,
        author: str = "AI News Influencer"
    ) -> Optional[ConversationThread]:
        """Add our response to a thread."""
        thread = self._threads.get(thread_id)
        if not thread:
            return None

        message = ThreadMessage(
            id=response_id,
            author=author,
            content=response_content,
            is_our_response=True,
            timestamp=datetime.utcnow(),
            parent_id=thread.messages[-1].id
        )

        thread.messages.append(message)
        thread.last_activity = message.timestamp

        return thread

    def add_reply(
        self,
        thread_id: str,
        comment: Comment
    ) -> Optional[ConversationThread]:
        """Add a user reply to an existing thread."""
        thread = self._threads.get(thread_id)
        if not thread:
            return None

        message = ThreadMessage(
            id=comment.id,
            author=comment.author_name,
            content=comment.content,
            is_our_response=False,
            timestamp=comment.created_at,
            parent_id=thread.messages[-1].id
        )

        thread.messages.append(message)
        thread.last_activity = message.timestamp

        return thread

    def get_thread(self, thread_id: str) -> Optional[ConversationThread]:
        """Get a conversation thread."""
        return self._threads.get(thread_id)

    def get_thread_context(self, thread_id: str) -> list[dict]:
        """Get thread context for response generation."""
        thread = self._threads.get(thread_id)
        if not thread:
            return []

        return [
            {
                "role": "user" if not msg.is_our_response else "assistant",
                "content": msg.content
            }
            for msg in thread.messages
        ]

    def mark_resolved(self, thread_id: str) -> bool:
        """Mark a thread as resolved."""
        thread = self._threads.get(thread_id)
        if thread:
            thread.is_resolved = True
            return True
        return False

    def get_active_threads(self, post_id: Optional[str] = None) -> list[ConversationThread]:
        """Get all active (unresolved) threads."""
        threads = list(self._threads.values())

        if post_id:
            threads = [t for t in threads if t.post_id == post_id]

        return [t for t in threads if not t.is_resolved]


# Global instance
threading_service = ThreadingService()
