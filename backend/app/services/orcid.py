import secrets
from urllib.parse import urlencode

import httpx

from app.config import settings

ORCID_AUTH_URL = "https://orcid.org/oauth/authorize"
ORCID_TOKEN_URL = "https://orcid.org/oauth/token"
ORCID_API_URL = "https://pub.orcid.org/v3.0"


def build_authorize_url(state: str) -> str:
    params = {
        "client_id": settings.orcid_client_id,
        "response_type": "code",
        "scope": "/authenticate",
        "redirect_uri": f"{settings.frontend_url}/auth/callback",
        "state": state,
    }
    return f"{ORCID_AUTH_URL}?{urlencode(params)}"


def generate_state() -> str:
    return secrets.token_urlsafe(32)


async def exchange_code_for_token(code: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            ORCID_TOKEN_URL,
            data={
                "client_id": settings.orcid_client_id,
                "client_secret": settings.orcid_client_secret,
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": f"{settings.frontend_url}/auth/callback",
            },
            headers={"Accept": "application/json"},
            timeout=10,
        )
        response.raise_for_status()
        return response.json()


async def fetch_user_info(orcid_id: str, access_token: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{ORCID_API_URL}/{orcid_id}/record",
            headers={
                "Accept": "application/json",
                "Authorization": f"Bearer {access_token}",
            },
            timeout=10,
        )
        response.raise_for_status()
        return response.json()
