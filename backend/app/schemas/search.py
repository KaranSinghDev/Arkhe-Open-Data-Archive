from typing import Optional

from pydantic import BaseModel


class SearchQuery(BaseModel):
    q: str = ""
    experiment: Optional[str] = None
    record_type: Optional[str] = None
    year: Optional[int] = None
    keywords: Optional[list[str]] = None
    page: int = 1
    size: int = 20


class SearchHit(BaseModel):
    id: str
    title: str
    description: Optional[str]
    experiment: Optional[str]
    record_type: str
    year: Optional[int]
    keywords: Optional[list[str]]
    score: float


class FacetBucket(BaseModel):
    key: str
    count: int


class Facets(BaseModel):
    experiments: list[FacetBucket] = []
    record_types: list[FacetBucket] = []
    years: list[FacetBucket] = []


class SearchResponse(BaseModel):
    hits: list[SearchHit]
    total: int
    page: int
    size: int
    facets: Facets
