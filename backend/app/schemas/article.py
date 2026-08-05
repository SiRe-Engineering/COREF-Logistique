from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ArticleBase(BaseModel):
    reference: str = Field(min_length=1, max_length=80)
    designation: str = Field(min_length=1, max_length=255)
    famille: str | None = Field(default=None, max_length=120)
    sous_famille: str | None = Field(default=None, max_length=120)
    unite: str = Field(default="unité", min_length=1, max_length=30)
    stock_minimum: Decimal = Field(default=0, ge=0)

    @field_validator("reference")
    @classmethod
    def normaliser_reference(cls, value: str) -> str:
        return value.strip().upper()

    @field_validator(
        "designation",
        "famille",
        "sous_famille",
        "unite",
    )
    @classmethod
    def nettoyer_texte(cls, value: str | None) -> str | None:
        return value.strip() if value else value


class ArticleCreate(ArticleBase):
    pass


class ArticleUpdate(BaseModel):
    reference: str | None = Field(default=None, min_length=1, max_length=80)
    designation: str | None = Field(default=None, min_length=1, max_length=255)
    famille: str | None = Field(default=None, max_length=120)
    sous_famille: str | None = Field(default=None, max_length=120)
    unite: str | None = Field(default=None, min_length=1, max_length=30)
    stock_minimum: Decimal | None = Field(default=None, ge=0)
    actif: bool | None = None

    @field_validator("reference")
    @classmethod
    def normaliser_reference(cls, value: str | None) -> str | None:
        return value.strip().upper() if value else value


class ArticleRead(ArticleBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    actif: bool
    date_creation: datetime
    date_modification: datetime
