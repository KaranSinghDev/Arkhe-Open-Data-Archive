import logging
from typing import Any

from opensearchpy import AsyncOpenSearch
from opensearchpy.exceptions import NotFoundError

from app.config import settings
from app.models.record import Record
from app.schemas.search import FacetBucket, Facets, SearchHit, SearchResponse

logger = logging.getLogger(__name__)

_client: AsyncOpenSearch | None = None


def get_opensearch_client() -> AsyncOpenSearch:
    global _client
    if _client is None:
        _client = AsyncOpenSearch(
            hosts=[{"host": settings.opensearch_host, "port": settings.opensearch_port}],
            use_ssl=False,
            verify_certs=False,
        )
    return _client


def _record_to_doc(record: Record) -> dict:
    return {
        "id": str(record.id),
        "title": record.title,
        "description": record.description,
        "record_type": record.record_type,
        "experiment": record.experiment,
        "year": record.year,
        "keywords": record.keywords or [],
        "license": record.license,
        "status": record.status,
        "user_id": str(record.user_id),
    }


def _parse_facets(aggs: dict) -> Facets:
    def _buckets(name: str) -> list[FacetBucket]:
        return [
            FacetBucket(key=str(b["key"]), count=b["doc_count"])
            for b in aggs.get(name, {}).get("buckets", [])
        ]
    return Facets(
        experiments=_buckets("experiments"),
        record_types=_buckets("record_types"),
        years=_buckets("years"),
    )


def format_search_response(raw: dict, page: int, size: int) -> SearchResponse:
    hits_data = raw.get("hits", {})
    total = hits_data.get("total", {}).get("value", 0)

    hits = []
    for hit in hits_data.get("hits", []):
        src = hit.get("_source", {})
        hits.append(SearchHit(
            id=hit["_id"],
            title=src.get("title", ""),
            description=src.get("description"),
            experiment=src.get("experiment"),
            record_type=src.get("record_type", ""),
            year=src.get("year"),
            keywords=src.get("keywords"),
            score=hit.get("_score") or 0.0,
        ))

    facets = _parse_facets(raw.get("aggregations", {}))
    return SearchResponse(hits=hits, total=total, page=page, size=size, facets=facets)


_AGGS = {
    "experiments": {"terms": {"field": "experiment", "size": 20}},
    "record_types": {"terms": {"field": "record_type", "size": 20}},
    "years": {"terms": {"field": "year", "size": 20, "order": {"_key": "desc"}}},
}


async def index_record(record: Record) -> None:
    client = get_opensearch_client()
    await client.index(
        index=settings.opensearch_index,
        id=str(record.id),
        body=_record_to_doc(record),
    )


async def delete_record(record_id: str) -> None:
    client = get_opensearch_client()
    try:
        await client.delete(index=settings.opensearch_index, id=record_id)
    except NotFoundError:
        pass


async def search(
    q: str = "",
    experiment: str | None = None,
    record_type: str | None = None,
    year: int | None = None,
    keywords: list[str] | None = None,
    page: int = 1,
    size: int = 20,
) -> SearchResponse:
    client = get_opensearch_client()
    must: list[dict[str, Any]] = []
    filters: list[dict[str, Any]] = [{"term": {"status": "published"}}]

    if q:
        must.append({
            "multi_match": {
                "query": q,
                "fields": ["title^3", "description", "keywords"],
                "type": "best_fields",
            }
        })
    if experiment:
        filters.append({"term": {"experiment": experiment}})
    if record_type:
        filters.append({"term": {"record_type": record_type}})
    if year:
        filters.append({"term": {"year": year}})
    if keywords:
        filters.append({"terms": {"keywords": keywords}})

    body = {
        "query": {"bool": {"must": must or [{"match_all": {}}], "filter": filters}},
        "from": (page - 1) * size,
        "size": size,
        "highlight": {"fields": {"title": {}, "description": {}}},
        "aggs": _AGGS,
    }

    raw = await client.search(index=settings.opensearch_index, body=body)
    return format_search_response(raw, page, size)


async def get_facets() -> Facets:
    client = get_opensearch_client()
    body = {
        "query": {"term": {"status": "published"}},
        "size": 0,
        "aggs": _AGGS,
    }
    raw = await client.search(index=settings.opensearch_index, body=body)
    return _parse_facets(raw.get("aggregations", {}))


async def suggest(q: str, size: int = 5) -> list[str]:
    client = get_opensearch_client()
    body = {
        "query": {
            "bool": {
                "must": [{"match_phrase_prefix": {"title": {"query": q, "max_expansions": 10}}}],
                "filter": [{"term": {"status": "published"}}],
            }
        },
        "_source": ["title"],
        "size": size,
    }
    try:
        raw = await client.search(index=settings.opensearch_index, body=body)
        return [h["_source"]["title"] for h in raw.get("hits", {}).get("hits", [])]
    except Exception:
        return []
