from fastapi import APIRouter, Depends

from app.schemas.search import Facets, SearchQuery, SearchResponse

router = APIRouter(prefix="/search", tags=["search"])


@router.get("/", response_model=SearchResponse)
async def search(query: SearchQuery = Depends()):
    return SearchResponse(
        hits=[],
        total=0,
        page=query.page,
        size=query.size,
        facets=Facets(),
    )


@router.get("/facets")
async def facets():
    return Facets()


@router.get("/suggest")
async def suggest(q: str = ""):
    return []
