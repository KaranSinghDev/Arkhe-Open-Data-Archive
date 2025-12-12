import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4


def _make_raw_response(hits=None, total=0, aggs=None):
    return {
        "hits": {
            "total": {"value": total},
            "hits": hits or [],
        },
        "aggregations": aggs or {},
    }


def test_format_search_response_empty():
    from app.services.search import format_search_response
    raw = _make_raw_response()
    result = format_search_response(raw, page=1, size=20)
    assert result.total == 0
    assert result.hits == []
    assert result.facets.experiments == []


def test_format_search_response_with_hits():
    from app.services.search import format_search_response
    raw = _make_raw_response(
        hits=[{
            "_id": "abc",
            "_score": 1.5,
            "_source": {
                "title": "LHC Run 3 data",
                "description": "Proton collision dataset",
                "record_type": "dataset",
                "experiment": "CMS",
                "year": 2023,
                "keywords": ["cms", "proton"],
            },
        }],
        total=1,
        aggs={
            "experiments": {"buckets": [{"key": "CMS", "doc_count": 1}]},
            "record_types": {"buckets": [{"key": "dataset", "doc_count": 1}]},
            "years": {"buckets": [{"key": 2023, "doc_count": 1}]},
        },
    )
    result = format_search_response(raw, page=1, size=20)
    assert result.total == 1
    assert result.hits[0].title == "LHC Run 3 data"
    assert result.hits[0].score == 1.5
    assert result.hits[0].experiment == "CMS"
    assert result.facets.experiments[0].key == "CMS"
    assert result.facets.experiments[0].count == 1
    assert result.facets.years[0].key == "2023"


def test_parse_facets_empty():
    from app.services.search import _parse_facets
    facets = _parse_facets({})
    assert facets.experiments == []
    assert facets.record_types == []
    assert facets.years == []


@pytest.mark.asyncio
async def test_search_endpoint_returns_200(client):
    response = await client.get("/api/search/")
    assert response.status_code == 200
    data = response.json()
    assert "hits" in data
    assert "total" in data
    assert "facets" in data


@pytest.mark.asyncio
async def test_search_with_query_param(client):
    response = await client.get("/api/search/?q=LHC&experiment=CMS")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_facets_endpoint_returns_200(client):
    response = await client.get("/api/search/facets")
    assert response.status_code == 200
    data = response.json()
    assert "experiments" in data
    assert "record_types" in data
    assert "years" in data


@pytest.mark.asyncio
async def test_suggest_empty_query_returns_empty(client):
    response = await client.get("/api/search/suggest?q=")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_suggest_short_query_returns_empty(client):
    response = await client.get("/api/search/suggest?q=a")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_fair_metadata_missing_record_returns_404(client):
    record_id = uuid4()
    response = await client.get(f"/api/records/{record_id}/metadata.json")
    assert response.status_code == 404
