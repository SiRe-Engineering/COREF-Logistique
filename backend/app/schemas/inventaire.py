from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


StatutInventaire = Literal["EN_COURS", "VALIDE", "ANNULE"]
TypeInventaire = Literal["EMPLACEMENT", "GENERAL", "FAMILLE"]


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


class FamilleInventaireRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    nom: str


class LigneInventaireRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    emplacement_id: int
    article_id: int
    lot_id: int | None
    quantite_theorique: Decimal
    quantite_comptee: Decimal | None
    ecart: Decimal | None
    pourcentage_ecart: Decimal | None
    commentaire: str | None
    emplacement: EmplacementInventaireRead
    article: ArticleInventaireRead
    lot: LotInventaireRead | None


class InventaireCreate(BaseModel):
    type: TypeInventaire = "EMPLACEMENT"
    emplacement_id: int | None = None
    famille_id: int | None = None
    operateur: str | None = Field(default=None, max_length=120)
    commentaire: str | None = None

    @model_validator(mode="after")
    def verifier_perimetre(self):
        if self.type == "EMPLACEMENT" and self.emplacement_id is None:
            raise ValueError(
                "Un emplacement est obligatoire pour ce type d’inventaire."
            )
        if self.type == "FAMILLE" and self.famille_id is None:
            raise ValueError(
                "Une famille est obligatoire pour ce type d’inventaire."
            )
        return self


class LigneInventaireUpdate(BaseModel):
    quantite_comptee: Decimal = Field(ge=0)
    commentaire: str | None = Field(default=None, max_length=255)


class InventaireRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    reference: str
    nom: str
    type: str
    emplacement_id: int | None
    famille_id: int | None
    statut: str
    operateur: str | None
    valide_par: str | None
    commentaire: str | None
    date_creation: datetime
    date_validation: datetime | None
    emplacement: EmplacementInventaireRead | None
    famille: FamilleInventaireRead | None
    lignes: list[LigneInventaireRead] = []
