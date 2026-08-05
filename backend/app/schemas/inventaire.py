from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

StatutInventaire = Literal["BROUILLON", "EN_COURS", "VALIDE", "ANNULE"]


class ArticleInventaireRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    reference: str
    designation: str
    unite: str


class LotInventaireRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    reference_interne: str
    numero_lot_fournisseur: str


class EmplacementInventaireRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    nom: str


class LigneInventaireRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    article_id: int
    lot_id: int | None
    quantite_theorique: Decimal
    quantite_comptee: Decimal | None
    ecart: Decimal | None
    commentaire: str | None
    article: ArticleInventaireRead
    lot: LotInventaireRead | None


class InventaireCreate(BaseModel):
    nom: str = Field(min_length=1, max_length=180)
    emplacement_id: int
    operateur: str | None = Field(default=None, max_length=120)
    commentaire: str | None = None


class LigneInventaireUpdate(BaseModel):
    quantite_comptee: Decimal = Field(ge=0)
    commentaire: str | None = Field(default=None, max_length=255)


class InventaireRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    reference: str
    nom: str
    emplacement_id: int
    statut: str
    operateur: str | None
    commentaire: str | None
    date_creation: datetime
    date_validation: datetime | None
    emplacement: EmplacementInventaireRead
    lignes: list[LigneInventaireRead] = []
