"""Database models for the AI news aggregator."""
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


# SQL Schema for SQLite database
SQL_SCHEMA = """
-- Scraped tweets from Twitter/X
CREATE TABLE IF NOT EXISTS scraped_tweets (
    id TEXT PRIMARY KEY,
    author_handle TEXT NOT NULL,
    content TEXT NOT NULL,
    posted_at TIMESTAMP,
    likes INTEGER DEFAULT 0,
    retweets INTEGER DEFAULT 0,
    replies INTEGER DEFAULT 0,
    media_urls TEXT,
    hashtags TEXT,
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Generated LinkedIn posts
CREATE TABLE IF NOT EXISTS generated_posts (
    id TEXT PRIMARY KEY,
    content TEXT NOT NULL,
    status TEXT DEFAULT 'draft',
    source_tweet_ids TEXT,
    linkedin_post_id TEXT,
    image_url TEXT,
    hashtags TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    published_at TIMESTAMP,
    engagement_metrics TEXT
);

-- Comments on LinkedIn posts
CREATE TABLE IF NOT EXISTS comments (
    id TEXT PRIMARY KEY,
    post_id TEXT NOT NULL,
    author_name TEXT NOT NULL,
    author_id TEXT NOT NULL,
    content TEXT NOT NULL,
    intent TEXT DEFAULT 'other',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    responded INTEGER DEFAULT 0,
    response_text TEXT,
    responded_at TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES generated_posts(id)
);

-- Engagement metrics history
CREATE TABLE IF NOT EXISTS engagement_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id TEXT NOT NULL,
    likes INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    shares INTEGER DEFAULT 0,
    impressions INTEGER DEFAULT 0,
    engagement_rate REAL DEFAULT 0.0,
    measured_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES generated_posts(id)
);

-- Agent decisions for traceability
CREATE TABLE IF NOT EXISTS agent_decisions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    decision_type TEXT NOT NULL,
    input_context TEXT,
    decision TEXT,
    reasoning TEXT,
    outcome TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- A/B test configurations
CREATE TABLE IF NOT EXISTS ab_tests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    test_name TEXT NOT NULL,
    variant_a TEXT NOT NULL,
    variant_b TEXT NOT NULL,
    start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_date TIMESTAMP,
    status TEXT DEFAULT 'active',
    winner TEXT,
    statistical_significance REAL
);

-- Post embeddings for RAG
CREATE TABLE IF NOT EXISTS post_embeddings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id TEXT NOT NULL,
    embedding BLOB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES generated_posts(id)
);

-- Content embeddings for similarity search
CREATE TABLE IF NOT EXISTS content_embeddings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content_id TEXT NOT NULL,
    content_type TEXT NOT NULL,
    embedding BLOB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- LinkedIn OAuth tokens
CREATE TABLE IF NOT EXISTS oauth_tokens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    provider TEXT NOT NULL,
    access_token TEXT NOT NULL,
    refresh_token TEXT,
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Target Twitter accounts to scrape
CREATE TABLE IF NOT EXISTS target_accounts (
    handle TEXT PRIMARY KEY,
    name TEXT,
    category TEXT DEFAULT 'ai_news',
    priority INTEGER DEFAULT 1,
    active INTEGER DEFAULT 1,
    last_scraped TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for common queries
CREATE INDEX IF NOT EXISTS idx_tweets_author ON scraped_tweets(author_handle);
CREATE INDEX IF NOT EXISTS idx_tweets_scraped_at ON scraped_tweets(scraped_at);
CREATE INDEX IF NOT EXISTS idx_posts_status ON generated_posts(status);
CREATE INDEX IF NOT EXISTS idx_posts_created_at ON generated_posts(created_at);
CREATE INDEX IF NOT EXISTS idx_comments_post_id ON comments(post_id);
CREATE INDEX IF NOT EXISTS idx_metrics_post_id ON engagement_metrics(post_id);
CREATE INDEX IF NOT EXISTS idx_target_accounts_active ON target_accounts(active);
"""


# Placeholder for SQLAlchemy Base (for compatibility)
Base = None


async def init_database(db_path: str = "./data/app.db") -> None:
    """Initialize the database with schema."""
    import aiosqlite
    from pathlib import Path

    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    async with aiosqlite.connect(db_path) as db:
        await db.executescript(SQL_SCHEMA)
        await db.commit()


class DecisionType(str, Enum):
    """Types of decisions made by agents."""
    CONTENT_SELECTION = "content_selection"
    POST_GENERATION = "post_generation"
    RESPONSE_GENERATION = "response_generation"
    COMMENT_CLASSIFICATION = "comment_classification"
    STRATEGY_OPTIMIZATION = "strategy_optimization"
    STRATEGY_ADJUSTMENT = "strategy_adjustment"


class AgentDecision(BaseModel):
    """Record of a decision made by an agent."""
    id: int
    decision_type: DecisionType
    input_context: dict[str, Any] = Field(default_factory=dict)
    decision: dict[str, Any] = Field(default_factory=dict)
    reasoning: str = ""
    outcome: str = ""
    created_at: datetime = Field(default_factory=datetime.utcnow)


class TargetAccount(BaseModel):
    """Model representing a target Twitter account to scrape."""

    handle: str = Field(..., description="Twitter handle (primary key)")
    name: Optional[str] = Field(None, description="Display name")
    category: str = Field(default="ai_news", description="Account category")
    priority: int = Field(default=1, description="Scraping priority (higher = more important)")
    active: bool = Field(default=True, description="Whether to actively scrape this account")
    last_scraped: Optional[datetime] = Field(None, description="Last scrape timestamp")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="When account was added")


class ScrapedTweet(BaseModel):
    """Model representing a scraped tweet from X/Twitter."""

    id: str = Field(..., description="Unique tweet ID")
    author_handle: str = Field(..., description="Twitter handle with @ prefix")
    content: str = Field(..., description="Tweet text content")
    posted_at: Optional[datetime] = Field(None, description="When the tweet was posted")
    likes: int = Field(default=0, description="Number of likes")
    retweets: int = Field(default=0, description="Number of retweets")
    replies: int = Field(default=0, description="Number of replies")
    media_urls: list[str] = Field(default_factory=list, description="URLs of attached media")
    hashtags: list[str] = Field(default_factory=list, description="Hashtags in the tweet")
    scraped_at: datetime = Field(default_factory=datetime.utcnow, description="When the tweet was scraped")

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "id": "1234567890",
                "author_handle": "@OpenAI",
                "content": "Introducing GPT-5! #AI #MachineLearning",
                "posted_at": "2024-01-15T12:00:00Z",
                "likes": 15000,
                "retweets": 5000,
                "replies": 1200,
                "media_urls": ["https://pbs.twimg.com/media/example.jpg"],
                "hashtags": ["AI", "MachineLearning"],
                "scraped_at": "2024-01-15T13:00:00Z"
            }
        }


class PostStatus(str, Enum):
    """Status of a generated post."""
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    PUBLISHED = "published"
    REJECTED = "rejected"


class GeneratedPost(BaseModel):
    """Model representing a generated LinkedIn post."""

    id: str = Field(..., description="Unique post ID")
    content: str = Field(..., description="Post content text")
    status: PostStatus = Field(default=PostStatus.DRAFT, description="Current post status")
    source_tweet_ids: list[str] = Field(default_factory=list, description="IDs of source tweets")
    linkedin_post_id: Optional[str] = Field(None, description="LinkedIn post URN after publishing")
    image_url: Optional[str] = Field(None, description="Generated image URL")
    hashtags: list[str] = Field(default_factory=list, description="Hashtags to include")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="When the post was created")
    published_at: Optional[datetime] = Field(None, description="When the post was published")
    engagement_metrics: dict = Field(default_factory=dict, description="Engagement metrics after publishing")

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "id": "post-123",
                "content": "Exciting developments in AI...",
                "status": "published",
                "source_tweet_ids": ["1234567890"],
                "linkedin_post_id": "urn:li:share:123456",
                "image_url": "https://example.com/image.png",
                "hashtags": ["AI", "Innovation"],
                "created_at": "2024-01-15T12:00:00Z",
                "published_at": "2024-01-15T14:00:00Z",
                "engagement_metrics": {"likes": 50, "comments": 10, "shares": 5}
            }
        }


class CommentIntent(str, Enum):
    """Classification of comment intent."""
    QUESTION = "question"
    FEEDBACK = "feedback"
    COMPLIMENT = "compliment"
    CRITICISM = "criticism"
    SPAM = "spam"
    OTHER = "other"


class Comment(BaseModel):
    """Model representing a comment on a LinkedIn post."""

    id: str = Field(..., description="Unique comment ID")
    post_id: str = Field(..., description="ID of the parent post")
    author_name: str = Field(..., description="Name of the comment author")
    author_id: str = Field(..., description="LinkedIn ID of the author")
    content: str = Field(..., description="Comment text content")
    intent: CommentIntent = Field(default=CommentIntent.OTHER, description="Classified intent")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="When the comment was created")
    responded: bool = Field(default=False, description="Whether a response was sent")
    response_text: Optional[str] = Field(None, description="Text of the response if sent")
    responded_at: Optional[datetime] = Field(None, description="When the response was sent")

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "id": "comment-123",
                "post_id": "post-123",
                "author_name": "John Doe",
                "author_id": "urn:li:person:abc123",
                "content": "Great insights! What tools do you recommend?",
                "intent": "question",
                "created_at": "2024-01-15T15:00:00Z",
                "responded": True,
                "response_text": "Thanks John! I recommend...",
                "responded_at": "2024-01-15T16:00:00Z"
            }
        }


class EngagementMetrics(BaseModel):
    """Engagement metrics for a LinkedIn post."""

    id: int = Field(..., description="Unique metric record ID")
    post_id: str = Field(..., description="ID of the associated post")
    likes: int = Field(default=0, description="Number of likes")
    comments: int = Field(default=0, description="Number of comments")
    shares: int = Field(default=0, description="Number of shares")
    impressions: int = Field(default=0, description="Number of impressions")
    engagement_rate: float = Field(default=0.0, description="Engagement rate")
    measured_at: datetime = Field(default_factory=datetime.utcnow, description="When metrics were measured")

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "id": 1,
                "post_id": "post-123",
                "likes": 150,
                "comments": 25,
                "shares": 10,
                "impressions": 5000,
                "engagement_rate": 0.037,
                "measured_at": "2024-01-15T18:00:00Z"
            }
        }


class ABTest(BaseModel):
    """A/B test configuration and results."""

    id: int = Field(..., description="Unique test ID")
    test_name: str = Field(..., description="Name of the A/B test")
    variant_a: dict = Field(..., description="Configuration for variant A")
    variant_b: dict = Field(..., description="Configuration for variant B")
    start_date: datetime = Field(default_factory=datetime.utcnow, description="Test start date")
    end_date: Optional[datetime] = Field(None, description="Test end date")
    status: str = Field(default="active", description="Test status (active/completed/cancelled)")
    winner: Optional[str] = Field(None, description="Winning variant (A/B)")
    statistical_significance: Optional[float] = Field(None, description="Statistical significance level")

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "id": 1,
                "test_name": "CTA Button Test",
                "variant_a": {"cta_text": "Learn More"},
                "variant_b": {"cta_text": "Read Now"},
                "start_date": "2024-01-15T00:00:00Z",
                "end_date": "2024-01-22T00:00:00Z",
                "status": "completed",
                "winner": "B",
                "statistical_significance": 0.95
            }
        }
