from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


StatutBesoin = Literal[
    "A_TRAITER",
    "VALIDE",
    "COMMANDE",
    "RECU",
    "ANNULE",
]


class ArticleReapproRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    reference: str
    designation: str
    unite: str
    stock_minimum: Decimal
    stock_maximum: Decimal
    seuil_alerte: Decimal
    dernier_prix_achat: Decimal | None


class SuggestionReapproRead(BaseModel):
    article: ArticleReapproRead
    quantite_physique: Decimal
    quantite_reservee: Decimal
    quantite_disponible: Decimal
    quantite_suggeree: Decimal
    niveau: str
    besoin_ouvert_id: int | None = None


class BesoinCreate(BaseModel):
    article_id: int
    quantite_demandee: Decimal | None = Field(default=None, gt=0)
    prix_unitaire_prevu: Decimal | None = Field(default=None, ge=0)
    fournisseur: str | None = Field(default=None, max_length=180)
    commentaire: str | None = None


class BesoinUpdate(BaseModel):
    quantite_demandee: Decimal | None = Field(default=None, gt=0)
    quantite_commandee: Decimal | None = Field(default=None, ge=0)
    prix_unitaire_prevu: Decimal | None = Field(default=None, ge=0)
    fournisseur: str | None = Field(default=None, max_length=180)
    reference_commande: str | None = Field(default=None, max_length=100)
    statut: StatutBesoin | None = None
    commentaire: str | None = None


class ReceptionCreate(BaseModel):
    quantite: Decimal = Field(gt=0)
    emplacement_destination_id: int
    lot_id: int | None = None
    prix_unitaire_ht: Decimal = Field(ge=0)
    commentaire: str | None = None


class BesoinRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    reference: str
    article_id: int
    quantite_suggeree: Decimal
    quantite_demandee: Decimal
    quantite_commandee: Decimal
    quantite_recue: Decimal
    prix_unitaire_prevu: Decimal | None
    fournisseur: str | None
    reference_commande: str | None
    statut: str
    commentaire: str | None
    cree_par: str | None
    date_creation: datetime
    date_modification: datetime
    date_validation: datetime | None
    date_commande: datetime | None
    date_cloture: datetime | None
    article: ArticleReapproRead
