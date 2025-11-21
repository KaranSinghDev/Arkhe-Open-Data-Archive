import pytest


@pytest.mark.asyncio
async def test_health_returns_ok(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_records_list_returns_empty(client):
    response = await client.get("/api/records/")
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["total"] == 0


@pytest.mark.asyncio
async def test_search_returns_empty(client):
    response = await client.get("/api/search/")
    assert response.status_code == 200
    data = response.json()
    assert data["hits"] == []
    assert data["total"] == 0
