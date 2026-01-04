"""Application configuration using Pydantic Settings."""
from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "AI News Influencer"
    app_version: str = "0.1.0"
    debug: bool = False

    # API Keys
    anthropic_api_key: str = ""
    openai_api_key: str = ""
    replicate_api_key: str = ""

    # LinkedIn OAuth
    linkedin_client_id: str = ""
    linkedin_client_secret: str = ""
    linkedin_redirect_uri: str = "http://localhost:8000/api/v1/auth/linkedin/callback"

    # Database
    database_url: str = "sqlite+aiosqlite:///./data/app.db"

    # Configuration
    post_frequency_hours: int = 24
    max_posts_per_day: int = 1
    approval_required: bool = True
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"

    # Scraping
    scrape_interval_hours: int = 4
    max_tweets_per_account: int = 50
    rate_limit_delay: float = 2.0

    # Content Generation
    claude_model: str = "claude-3-5-sonnet-20241022"
    embedding_model: str = "text-embedding-3-small"
    image_model: str = "dall-e-3"

    # Image Generation
    image_generation_provider: Literal["dalle3", "stable_diffusion"] = "dalle3"
    image_style: Literal["professional", "abstract", "infographic", "minimalist"] = "professional"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Convenience accessor
settings = get_settings()
