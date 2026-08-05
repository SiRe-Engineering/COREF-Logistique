from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class SousFamilleBase(BaseModel):
    code: str = Field(min_length=2, max_length=10)
    nom: str = Field(min_length=1, max_length=120)

    @field_validator("code")
    @classmethod
    def normaliser_code(cls, value: str) -> str:
        return value.strip().upper()

    @field_validator("nom")
    @classmethod
    def nettoyer_nom(cls, value: str) -> str:
        return value.strip()


class SousFamilleCreate(SousFamilleBase):
    famille_id: int


class SousFamilleUpdate(BaseModel):
    code: str | None = Field(default=None, min_length=2, max_length=10)
    nom: str | None = Field(default=None, min_length=1, max_length=120)
    actif: bool | None = None


class SousFamilleRead(SousFamilleBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    famille_id: int
    actif: bool
    date_creation: datetime
    date_modification: datetime


class FamilleBase(BaseModel):
    code: str = Field(min_length=2, max_length=10)
    nom: str = Field(min_length=1, max_length=120)

    @field_validator("code")
    @classmethod
    def normaliser_code(cls, value: str) -> str:
        return value.strip().upper()

    @field_validator("nom")
    @classmethod
    def nettoyer_nom(cls, value: str) -> str:
        return value.strip()


class FamilleCreate(FamilleBase):
    pass


class FamilleUpdate(BaseModel):
    code: str | None = Field(default=None, min_length=2, max_length=10)
    nom: str | None = Field(default=None, min_length=1, max_length=120)
    actif: bool | None = None


class FamilleRead(FamilleBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    actif: bool
    date_creation: datetime
    date_modification: datetime
    sous_familles: list[SousFamilleRead] = []
