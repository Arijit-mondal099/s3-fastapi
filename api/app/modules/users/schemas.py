import uuid
from datetime import datetime
from typing import Annotated, Literal

from pydantic import (
    ConfigDict,
    Field,
    StringConstraints,
    field_validator,
    model_validator,
)

from app.core.config import settings
from app.core.schemas import CamelModel

Name = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=60)
]


class UserOut(CamelModel):
    id: uuid.UUID
    email: str
    name: str
    bio: str | None
    avatar_url: str | None
    created_at: datetime


class UpdateProfileRequest(CamelModel):
    model_config = ConfigDict(
        extra="forbid"
    )  # can't PATCH password_hash, avatar_key, etc.

    name: Name | None = None
    bio: (
        Annotated[str, StringConstraints(strip_whitespace=True, max_length=280)] | None
    ) = None

    @field_validator("name")
    @classmethod
    def name_not_null(cls, v):
        if v is None:
            raise ValueError("name cannot be null")
        return v

    @model_validator(mode="after")
    def not_empty(self):
        if not self.model_fields_set:
            raise ValueError("Nothing to update")
        return self


class AvatarPresignRequest(CamelModel):
    content_type: Literal["image/jpeg", "image/png", "image/webp"]
    size: int = Field(
        gt=0, le=settings.upload_max_bytes
    )


class AvatarPresignResponse(CamelModel):
    url: str
    fields: dict[str, str]
    key: str


class AvatarConfirmRequest(CamelModel):
    key: str = Field(min_length=1, max_length=300)
