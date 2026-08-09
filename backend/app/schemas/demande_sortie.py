from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    nom_complet: str
    role: str


class ArticleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    reference: str
    designation: str
    unite: str


class LotRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    numero_lot_fournisseur: str


class EmplacementRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    code: str
    nom: str


class AffaireRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    reference: str
    code_externe: str | None
    nom: str


class DemandeSortieCreate(BaseModel):
    article_id: int
    lot_id: int | None = None
    emplacement_source_id: int
    affaire_id: int | None = None
    quantite: Decimal = Field(gt=0)
    vehicule: str | None = Field(default=None, max_length=120)
    motif: str = Field(min_length=2, max_length=255)
    commentaire: str | None = None


class RefusDemande(BaseModel):
    motif_refus: str = Field(min_length=2, max_length=1000)


class DemandeSortieRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    reference: str
    demandeur_id: int
    validateur_id: int | None
    article_id: int
    lot_id: int | None
    emplacement_source_id: int
    affaire_id: int | None
    quantite: Decimal
    vehicule: str | None
    motif: str
    commentaire: str | None
    statut: str
    date_creation: datetime
    date_decision: datetime | None
    motif_refus: str | None
    demandeur: UserRead
    validateur: UserRead | None
    article: ArticleRead
    lot: LotRead | None
    emplacement_source: EmplacementRead
    affaire: AffaireRead | None
