"""Configuration management endpoints."""
from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class SystemConfig(BaseModel):
    brand_voice: str = "professional"
    posting_enabled: bool = True
    auto_approve: bool = False
    max_hashtags: int = 5
    target_accounts: list[str] = []
    topics: list[str] = []


class PromptConfig(BaseModel):
    informative: str
    thought_leadership: str
    commentary: str


@router.get("/config", response_model=SystemConfig)
async def get_config():
    """Get system configuration."""
    return SystemConfig(
        target_accounts=["@OpenAI", "@AnthropicAI", "@GoogleAI"],
        topics=["AI", "Machine Learning", "LLMs"]
    )


@router.patch("/config")
async def update_config(config: SystemConfig):
    """Update system configuration."""
    return {"status": "updated", "config": config}


@router.get("/config/prompts", response_model=PromptConfig)
async def get_prompts():
    """Get prompt templates."""
    return PromptConfig(
        informative="Transform this news into an engaging post...",
        thought_leadership="Create a thought leadership post...",
        commentary="Write a commentary on this development..."
    )


@router.patch("/config/prompts")
async def update_prompts(prompts: PromptConfig):
    """Update prompt templates."""
    return {"status": "updated"}
