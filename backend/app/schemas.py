from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ItemBase(BaseModel):
    reference: str = Field(min_length=1, max_length=80)
    designation: str = Field(min_length=1, max_length=255)
    family: str | None = Field(default=None, max_length=120)
    subfamily: str | None = Field(default=None, max_length=120)
    unit: str = Field(default="unité", min_length=1, max_length=30)
    minimum_stock: Decimal = Field(default=0, ge=0)

    @field_validator("reference")
    @classmethod
    def normalize_reference(cls, value: str) -> str:
        return value.strip().upper()

    @field_validator("designation", "family", "subfamily", "unit")
    @classmethod
    def strip_text(cls, value: str | None) -> str | None:
        return value.strip() if value else value


class ItemCreate(ItemBase):
    pass


class ItemUpdate(BaseModel):
    reference: str | None = Field(default=None, min_length=1, max_length=80)
    designation: str | None = Field(default=None, min_length=1, max_length=255)
    family: str | None = Field(default=None, max_length=120)
    subfamily: str | None = Field(default=None, max_length=120)
    unit: str | None = Field(default=None, min_length=1, max_length=30)
    minimum_stock: Decimal | None = Field(default=None, ge=0)
    is_active: bool | None = None


class ItemRead(ItemBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
