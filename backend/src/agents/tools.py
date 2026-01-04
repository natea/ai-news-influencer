"""Pydantic tool definitions for agent capabilities."""
from enum import Enum
from typing import Literal, Optional
from pydantic import BaseModel, Field


class PostStyle(str, Enum):
    """Style of LinkedIn post to generate."""
    INFORMATIVE = "informative"
    THOUGHT_LEADERSHIP = "thought_leadership"
    COMMENTARY = "commentary"
    ANNOUNCEMENT = "announcement"


class ContentCategory(str, Enum):
    """Category of content for ranking."""
    AI_RESEARCH = "ai_research"
    PRODUCT_LAUNCH = "product_launch"
    INDUSTRY_NEWS = "industry_news"
    TUTORIAL = "tutorial"
    OPINION = "opinion"


# Content Selection Tools
class ContentRankingInput(BaseModel):
    """Input for content ranking tool."""
    tweet_id: str = Field(..., description="ID of the tweet to rank")
    content: str = Field(..., description="Tweet content text")
    author: str = Field(..., description="Tweet author handle")
    engagement: dict = Field(default_factory=dict, description="Engagement metrics")
    posted_at: Optional[str] = Field(None, description="When the tweet was posted")


class ContentRankingOutput(BaseModel):
    """Output from content ranking tool."""
    tweet_id: str
    relevance_score: float = Field(..., ge=0, le=1, description="Overall relevance 0-1")
    topic_match: float = Field(..., ge=0, le=1, description="Topic alignment score")
    timeliness: float = Field(..., ge=0, le=1, description="How recent/timely")
    engagement_potential: float = Field(..., ge=0, le=1, description="Viral potential")
    category: ContentCategory
    reasoning: str = Field(..., description="Explanation of the ranking")
    should_process: bool = Field(..., description="Whether to generate a post")


class ContentSelectionInput(BaseModel):
    """Input for selecting best content to post."""
    candidates: list[ContentRankingOutput]
    max_selections: int = Field(default=1, ge=1, le=5)
    exclude_topics: list[str] = Field(default_factory=list)
    prefer_categories: list[ContentCategory] = Field(default_factory=list)


class ContentSelectionOutput(BaseModel):
    """Output from content selection."""
    selected_ids: list[str]
    reasoning: str


# Post Generation Tools
class PostGenerationInput(BaseModel):
    """Input for generating a LinkedIn post."""
    source_tweet_id: str
    source_content: str
    source_author: str
    post_style: PostStyle = PostStyle.INFORMATIVE
    target_audience: str = "tech professionals"
    brand_voice: str = "professional"
    include_cta: bool = True
    max_length: int = Field(default=2000, description="Max post length in chars")


class PostGenerationOutput(BaseModel):
    """Output from post generation."""
    content: str = Field(..., description="Generated LinkedIn post content")
    hashtags: list[str] = Field(default_factory=list, max_length=5)
    mentions: list[str] = Field(default_factory=list)
    call_to_action: Optional[str] = None
    estimated_engagement: float = Field(default=0.5, ge=0, le=1)
    quality_score: float = Field(..., ge=0, le=1)


# Hashtag Tools
class HashtagSuggestionInput(BaseModel):
    """Input for hashtag suggestion."""
    content: str
    max_hashtags: int = Field(default=5, ge=1, le=10)
    industry_focus: list[str] = Field(default_factory=lambda: ["AI", "Tech"])
    trending_weight: float = Field(default=0.3, ge=0, le=1)


class HashtagSuggestionOutput(BaseModel):
    """Output from hashtag suggestion."""
    hashtags: list[str]
    relevance_scores: dict[str, float]
    reasoning: str


# Image Generation Tools
class ImagePromptInput(BaseModel):
    """Input for image prompt generation."""
    post_content: str
    style: Literal["professional", "abstract", "infographic", "minimalist"] = "professional"
    mood: Literal["optimistic", "serious", "innovative", "neutral"] = "innovative"
    include_text: bool = False


class ImagePromptOutput(BaseModel):
    """Output from image prompt generation."""
    prompt: str = Field(..., description="DALL-E prompt")
    negative_prompt: str = Field(default="", description="What to avoid")
    style_modifiers: list[str] = Field(default_factory=list)


# Response Generation Tools
class CommentClassificationInput(BaseModel):
    """Input for classifying a comment."""
    comment_content: str
    comment_author: str
    original_post_content: str


class CommentClassificationOutput(BaseModel):
    """Output from comment classification."""
    intent: Literal["question", "feedback", "compliment", "criticism", "spam", "other"]
    sentiment: Literal["positive", "negative", "neutral"]
    requires_response: bool
    priority: Literal["high", "medium", "low"]
    reasoning: str


class ResponseGenerationInput(BaseModel):
    """Input for generating a comment response."""
    comment_content: str
    comment_author: str
    comment_intent: str
    original_post_content: str
    conversation_history: list[dict] = Field(default_factory=list)
    brand_voice: str = "professional"
    max_length: int = 500


class ResponseGenerationOutput(BaseModel):
    """Output from response generation."""
    response: str
    tone: str
    addresses_question: bool = False
    quality_score: float = Field(..., ge=0, le=1)


# Strategy Optimization Tools
class StrategyAnalysisInput(BaseModel):
    """Input for strategy analysis."""
    recent_posts: list[dict] = Field(..., description="Recent posts with metrics")
    time_range_days: int = Field(default=7)
    metrics_to_analyze: list[str] = Field(
        default_factory=lambda: ["engagement_rate", "impressions", "comments"]
    )


class StrategyAnalysisOutput(BaseModel):
    """Output from strategy analysis."""
    best_posting_times: list[str]
    top_performing_hashtags: list[str]
    recommended_post_styles: list[PostStyle]
    content_gaps: list[str]
    improvement_suggestions: list[str]
    predicted_engagement_lift: float
