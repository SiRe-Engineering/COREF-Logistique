from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ReferentielCourt(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    nom: str


class ArticleBase(BaseModel):
    designation: str = Field(min_length=1, max_length=255)
    famille_id: int | None = None
    sous_famille_id: int | None = None
    unite: str = Field(default="unité", min_length=1, max_length=30)
    stock_minimum: Decimal = Field(default=0, ge=0)
    stock_maximum: Decimal = Field(default=0, ge=0)
    seuil_alerte: Decimal = Field(default=0, ge=0)

    @field_validator("designation", "unite")
    @classmethod
    def nettoyer_texte(cls, value: str) -> str:
        return value.strip()


class ArticleCreate(ArticleBase):
    reference: str | None = Field(default=None, min_length=1, max_length=80)

    @field_validator("reference")
    @classmethod
    def normaliser_reference(cls, value: str | None) -> str | None:
        return value.strip().upper() if value else None


class ArticleUpdate(BaseModel):
    reference: str | None = Field(default=None, min_length=1, max_length=80)
    designation: str | None = Field(default=None, min_length=1, max_length=255)
    famille_id: int | None = None
    sous_famille_id: int | None = None
    unite: str | None = Field(default=None, min_length=1, max_length=30)
    stock_minimum: Decimal | None = Field(default=None, ge=0)
    stock_maximum: Decimal | None = Field(default=None, ge=0)
    seuil_alerte: Decimal | None = Field(default=None, ge=0)
    actif: bool | None = None

    @field_validator("reference")
    @classmethod
    def normaliser_reference(cls, value: str | None) -> str | None:
        return value.strip().upper() if value else None


class ArticleRead(ArticleBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    reference: str
    actif: bool
    date_creation: datetime
    date_modification: datetime
    famille_relation: ReferentielCourt | None = None
    sous_famille_relation: ReferentielCourt | None = None
