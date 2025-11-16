from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class FileRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    record_id: UUID
    filename: str
    content_type: str
    size_bytes: Optional[int]
    parsed_metadata: Optional[Any]
    created_at: datetime


class FileList(BaseModel):
    items: list[FileRead]
    total: int
