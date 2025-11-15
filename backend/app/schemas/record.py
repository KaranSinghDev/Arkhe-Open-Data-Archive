from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class RecordCreate(BaseModel):
    title: str
    description: Optional[str] = None
    doi: Optional[str] = None
    record_type: str
    experiment: Optional[str] = None
    year: Optional[int] = None
    license: str = "CC-BY-4.0"
    keywords: Optional[list[str]] = None


class RecordUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    record_type: Optional[str] = None
    experiment: Optional[str] = None
    year: Optional[int] = None
    license: Optional[str] = None
    keywords: Optional[list[str]] = None
    status: Optional[str] = None


class RecordRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    title: str
    description: Optional[str]
    doi: Optional[str]
    record_type: str
    experiment: Optional[str]
    year: Optional[int]
    license: str
    keywords: Optional[list[str]]
    status: str
    created_at: datetime
    updated_at: datetime


class RecordList(BaseModel):
    items: list[RecordRead]
    total: int
    page: int
    size: int
