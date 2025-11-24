import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4


@pytest.mark.asyncio
async def test_login_orcid_returns_url(client):
    response = await client.get("/api/auth/login/orcid")
    assert response.status_code == 200
    data = response.json()
    assert "url" in data
    assert "state" in data
    assert "orcid.org" in data["url"]


@pytest.mark.asyncio
async def test_logout_clears_cookie(client):
    response = await client.post("/api/auth/logout")
    assert response.status_code == 200
    assert response.json() == {"message": "logged out"}


@pytest.mark.asyncio
async def test_me_without_token_returns_401(client):
    response = await client.get("/api/auth/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_callback_missing_code_returns_400(client):
    response = await client.get("/api/auth/callback")
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_jwt_create_and_verify():
    from app.services.auth import create_jwt, verify_jwt
    user_id = str(uuid4())
    orcid_id = "0000-0002-1234-5678"
    token = create_jwt(user_id, orcid_id)
    payload = verify_jwt(token)
    assert payload["sub"] == user_id
    assert payload["orcid"] == orcid_id


@pytest.mark.asyncio
async def test_jwt_invalid_token_raises():
    from app.services.auth import verify_jwt
    with pytest.raises(ValueError):
        verify_jwt("not.a.valid.token")
