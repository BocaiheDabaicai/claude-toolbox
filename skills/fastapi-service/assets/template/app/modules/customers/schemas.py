from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class CustomerInput(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    phone: str | None = Field(default=None, max_length=32)
    email: EmailStr | None = None
    company: str | None = Field(default=None, max_length=200)
    note: str | None = Field(default=None, max_length=2000)
    status: Literal["active", "inactive"] = "active"

    @field_validator("name", mode="before")
    @classmethod
    def strip_name(cls, value):
        if isinstance(value, str):
            return value.strip()
        return value

    @field_validator("phone", "company", "note", mode="before")
    @classmethod
    def empty_to_none(cls, value):
        if isinstance(value, str):
            value = value.strip()
            return value or None
        return value

    @field_validator("email", mode="before")
    @classmethod
    def empty_email_to_none(cls, value):
        if isinstance(value, str):
            value = value.strip()
            return value or None
        return value


class CustomerOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    name: str
    phone: str | None
    email: str | None
    company: str | None
    note: str | None
    status: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    deleted_at: datetime | None = Field(default=None, alias="deletedAt")
