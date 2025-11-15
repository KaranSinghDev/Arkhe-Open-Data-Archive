from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class OrcidToken(BaseModel):
    access_token: str
    token_type: str
    orcid: str
    name: str


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    orcid_id: str
    name: str
    email: str | None
    created_at: datetime


class TokenResponse(BaseModel):
    user: UserRead
