"""Pydantic schemas for advertisement requests and responses."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class AdvertisementCreate(BaseModel):
    """Data accepted when an advertisement is created."""

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    title: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1)
    price: Decimal = Field(ge=0, max_digits=12, decimal_places=2)
    author: str = Field(min_length=1, max_length=120)


class AdvertisementUpdate(BaseModel):
    """Fields that may be changed with a PATCH request."""

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, min_length=1)
    price: Decimal | None = Field(
        default=None,
        ge=0,
        max_digits=12,
        decimal_places=2,
    )
    author: str | None = Field(default=None, min_length=1, max_length=120)

    @model_validator(mode="after")
    def validate_changed_fields(self):
        """Require at least one non-null field in a PATCH request."""
        if not self.model_fields_set:
            raise ValueError("at least one field must be provided")

        if any(
            getattr(self, field_name) is None
            for field_name in self.model_fields_set
        ):
            raise ValueError("updated fields must not be null")

        return self


class AdvertisementResponse(BaseModel):
    """Advertisement returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    price: float
    author: str
    created_at: datetime
