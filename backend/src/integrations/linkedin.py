"""LinkedIn API integration for OAuth and posting."""
import json
from datetime import datetime, timedelta
from typing import Optional
from urllib.parse import urlencode

import httpx
from pydantic import BaseModel

from src.core.config import get_settings


class LinkedInTokens(BaseModel):
    """LinkedIn OAuth tokens."""
    access_token: str
    expires_in: int
    refresh_token: Optional[str] = None
    expires_at: Optional[datetime] = None


class LinkedInPost(BaseModel):
    """LinkedIn post structure."""
    content: str
    visibility: str = "PUBLIC"
    media_ids: list[str] = []


class LinkedInComment(BaseModel):
    """A comment on a LinkedIn post."""
    id: str
    author_name: str
    author_id: str
    content: str
    created_at: datetime


class LinkedInClient:
    """Client for LinkedIn API operations."""

    AUTHORIZATION_URL = "https://www.linkedin.com/oauth/v2/authorization"
    TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"
    API_BASE = "https://api.linkedin.com/v2"

    SCOPES = [
        "r_liteprofile",
        "w_member_social",
    ]

    def __init__(self):
        settings = get_settings()
        self.client_id = settings.linkedin_client_id
        self.client_secret = settings.linkedin_client_secret
        self.redirect_uri = settings.linkedin_redirect_uri
        self._tokens: Optional[LinkedInTokens] = None
        self._user_urn: Optional[str] = None

    def get_authorization_url(self, state: str = "") -> str:
        """Get the OAuth authorization URL."""
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": " ".join(self.SCOPES),
            "state": state
        }
        return f"{self.AUTHORIZATION_URL}?{urlencode(params)}"

    async def exchange_code(self, code: str) -> LinkedInTokens:
        """Exchange authorization code for access tokens."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.TOKEN_URL,
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": self.redirect_uri,
                    "client_id": self.client_id,
                    "client_secret": self.client_secret
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            response.raise_for_status()
            data = response.json()

            self._tokens = LinkedInTokens(
                access_token=data["access_token"],
                expires_in=data["expires_in"],
                expires_at=datetime.utcnow() + timedelta(seconds=data["expires_in"])
            )

            return self._tokens

    def set_tokens(self, tokens: LinkedInTokens) -> None:
        """Set tokens from stored values."""
        self._tokens = tokens

    async def get_profile(self) -> dict:
        """Get the current user's profile."""
        if not self._tokens:
            raise ValueError("Not authenticated. Call exchange_code first.")

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.API_BASE}/me",
                headers=self._auth_headers()
            )
            response.raise_for_status()
            data = response.json()

            self._user_urn = f"urn:li:person:{data['id']}"
            return data

    async def create_post(
        self,
        content: str,
        visibility: str = "PUBLIC",
        media_ids: Optional[list[str]] = None
    ) -> str:
        """Create a LinkedIn post."""
        if not self._tokens:
            raise ValueError("Not authenticated.")

        if not self._user_urn:
            await self.get_profile()

        post_data = {
            "author": self._user_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": content
                    },
                    "shareMediaCategory": "NONE" if not media_ids else "IMAGE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": visibility
            }
        }

        # Add media if provided
        if media_ids:
            post_data["specificContent"]["com.linkedin.ugc.ShareContent"]["media"] = [
                {
                    "status": "READY",
                    "media": media_id
                }
                for media_id in media_ids
            ]
            post_data["specificContent"]["com.linkedin.ugc.ShareContent"]["shareMediaCategory"] = "IMAGE"

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.API_BASE}/ugcPosts",
                json=post_data,
                headers=self._auth_headers()
            )
            response.raise_for_status()

            # Return the post URN
            return response.headers.get("x-restli-id", "")

    async def upload_image(self, image_data: bytes) -> str:
        """Upload an image and return the media ID."""
        if not self._tokens:
            raise ValueError("Not authenticated.")

        if not self._user_urn:
            await self.get_profile()

        # Step 1: Register upload
        register_data = {
            "registerUploadRequest": {
                "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
                "owner": self._user_urn,
                "serviceRelationships": [
                    {
                        "relationshipType": "OWNER",
                        "identifier": "urn:li:userGeneratedContent"
                    }
                ]
            }
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.API_BASE}/assets?action=registerUpload",
                json=register_data,
                headers=self._auth_headers()
            )
            response.raise_for_status()
            upload_info = response.json()

            upload_url = upload_info["value"]["uploadMechanism"][
                "com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"
            ]["uploadUrl"]
            asset = upload_info["value"]["asset"]

            # Step 2: Upload image
            await client.put(
                upload_url,
                content=image_data,
                headers={
                    "Authorization": f"Bearer {self._tokens.access_token}",
                    "Content-Type": "image/png"
                }
            )

            return asset

    async def get_post_comments(self, post_urn: str) -> list[LinkedInComment]:
        """Get comments on a post."""
        if not self._tokens:
            raise ValueError("Not authenticated.")

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.API_BASE}/socialActions/{post_urn}/comments",
                headers=self._auth_headers()
            )
            response.raise_for_status()
            data = response.json()

            comments = []
            for element in data.get("elements", []):
                comments.append(LinkedInComment(
                    id=element.get("$URN", ""),
                    author_name=element.get("actor", {}).get("name", "Unknown"),
                    author_id=element.get("actor", {}).get("urn", ""),
                    content=element.get("message", {}).get("text", ""),
                    created_at=datetime.fromtimestamp(
                        element.get("created", {}).get("time", 0) / 1000
                    )
                ))

            return comments

    async def reply_to_comment(self, post_urn: str, comment_urn: str, text: str) -> str:
        """Reply to a comment on a post."""
        if not self._tokens:
            raise ValueError("Not authenticated.")

        if not self._user_urn:
            await self.get_profile()

        reply_data = {
            "actor": self._user_urn,
            "message": {"text": text},
            "parentComment": comment_urn
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.API_BASE}/socialActions/{post_urn}/comments",
                json=reply_data,
                headers=self._auth_headers()
            )
            response.raise_for_status()

            return response.headers.get("x-restli-id", "")

    async def get_post_metrics(self, post_urn: str) -> dict:
        """Get engagement metrics for a post."""
        if not self._tokens:
            raise ValueError("Not authenticated.")

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.API_BASE}/socialActions/{post_urn}",
                headers=self._auth_headers()
            )
            response.raise_for_status()
            data = response.json()

            return {
                "likes": data.get("likesSummary", {}).get("totalLikes", 0),
                "comments": data.get("commentsSummary", {}).get("totalFirstLevelComments", 0),
                "shares": data.get("sharesSummary", {}).get("totalShares", 0)
            }

    def _auth_headers(self) -> dict:
        """Get authorization headers."""
        return {
            "Authorization": f"Bearer {self._tokens.access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0"
        }


# Global client instance
linkedin_client = LinkedInClient()
