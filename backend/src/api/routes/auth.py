"""Authentication routes for LinkedIn OAuth."""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from src.integrations.linkedin import LinkedInClient, LinkedInTokens

router = APIRouter()

# Store tokens in memory (use proper storage in production)
_stored_tokens: dict[str, LinkedInTokens] = {}


class AuthorizationResponse(BaseModel):
    """Response with authorization URL."""
    authorization_url: str
    state: str


class TokenResponse(BaseModel):
    """Response with token information."""
    access_token: str
    expires_in: int
    message: str


@router.get("/linkedin/authorize", response_model=AuthorizationResponse)
async def get_linkedin_auth_url(state: str = Query(default="random_state")):
    """Get LinkedIn OAuth authorization URL."""
    client = LinkedInClient()
    auth_url = client.get_authorization_url(state=state)

    return AuthorizationResponse(
        authorization_url=auth_url,
        state=state,
    )


@router.get("/linkedin/callback", response_model=TokenResponse)
async def linkedin_callback(
    code: str = Query(..., description="Authorization code from LinkedIn"),
    state: str = Query(default=""),
):
    """Handle LinkedIn OAuth callback and exchange code for tokens."""
    client = LinkedInClient()

    try:
        tokens = await client.exchange_code(code)

        # Store tokens (use proper secure storage in production)
        _stored_tokens["default"] = tokens

        return TokenResponse(
            access_token=tokens.access_token[:20] + "...",  # Truncated for security
            expires_in=tokens.expires_in,
            message="Successfully authenticated with LinkedIn",
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to exchange code: {str(e)}")


@router.get("/linkedin/status")
async def check_auth_status():
    """Check if LinkedIn authentication is active."""
    if "default" in _stored_tokens:
        tokens = _stored_tokens["default"]
        return {
            "authenticated": True,
            "expires_at": tokens.expires_at.isoformat() if tokens.expires_at else None,
        }
    return {"authenticated": False}


@router.post("/linkedin/refresh")
async def refresh_tokens():
    """Refresh LinkedIn access tokens."""
    if "default" not in _stored_tokens:
        raise HTTPException(status_code=401, detail="Not authenticated")

    # LinkedIn doesn't support refresh tokens for most apps
    # In a real implementation, you'd handle token refresh here
    raise HTTPException(
        status_code=501,
        detail="Token refresh not implemented. Re-authenticate via /authorize"
    )
