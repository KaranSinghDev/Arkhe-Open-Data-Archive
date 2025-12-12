from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.search import Facets, SearchQuery, SearchResponse
from app.services import search as search_service

router = APIRouter(prefix="/search", tags=["search"])


@router.get("/", response_model=SearchResponse)
async def search(query: SearchQuery = Depends()):
    try:
        return await search_service.search(
            q=query.q,
            experiment=query.experiment,
            record_type=query.record_type,
            year=query.year,
            keywords=query.keywords,
            page=query.page,
            size=query.size,
        )
    except Exception:
        return SearchResponse(
            hits=[],
            total=0,
            page=query.page,
            size=query.size,
            facets=Facets(),
        )


@router.get("/facets", response_model=Facets)
async def facets():
    try:
        return await search_service.get_facets()
    except Exception:
        return Facets()


@router.get("/suggest")
async def suggest(q: str = ""):
    if not q or len(q) < 2:
        return []
    try:
        return await search_service.suggest(q)
    except Exception:
        return []
