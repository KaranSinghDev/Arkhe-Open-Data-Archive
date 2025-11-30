import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from uuid import uuid4


@pytest.mark.asyncio
async def test_list_files_returns_empty(client):
    record_id = uuid4()
    response = await client.get(f"/api/records/{record_id}/files/")
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["total"] == 0


@pytest.mark.asyncio
async def test_upload_file_without_auth_returns_401(client):
    record_id = uuid4()
    response = await client.post(
        f"/api/records/{record_id}/files/",
        files={"file": ("test.csv", b"a,b,c\n1,2,3", "text/csv")},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_download_missing_file_returns_404(client):
    record_id = uuid4()
    file_id = uuid4()
    response = await client.get(
        f"/api/records/{record_id}/files/{file_id}/download",
        follow_redirects=False,
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_file_without_auth_returns_401(client):
    record_id = uuid4()
    file_id = uuid4()
    response = await client.delete(f"/api/records/{record_id}/files/{file_id}")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_storage_build_object_key():
    from app.services.storage import build_object_key
    key = build_object_key("abc-123", "my file.csv")
    assert key == "records/abc-123/my_file.csv"
    assert " " not in key
