from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

TypeMouvement = Literal[
    "ENTREE",
    "SORTIE",
    "TRANSFERT",
    "RETOUR",
    "AJUSTEMENT_POSITIF",
    "AJUSTEMENT_NEGATIF",
]


class ArticleMouvementRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    reference: str
    designation: str
    unite: str


class EmplacementMouvementRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    nom: str


class LotMouvementRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    reference_interne: str
    numero_lot_fournisseur: str
    date_peremption: date | None = None


class MouvementCreate(BaseModel):
    type: TypeMouvement
    article_id: int
    lot_id: int | None = None
    emplacement_source_id: int | None = None
    emplacement_destination_id: int | None = None
    quantite: Decimal = Field(gt=0)
    motif: str | None = Field(default=None, max_length=150)
    commentaire: str | None = None
    operateur: str | None = Field(default=None, max_length=120)

    @model_validator(mode="after")
    def valider_emplacements(self):
        if self.type in {
            "ENTREE",
            "RETOUR",
            "AJUSTEMENT_POSITIF",
        } and self.emplacement_destination_id is None:
            raise ValueError("Un emplacement de destination est obligatoire.")

        if self.type in {
            "SORTIE",
            "AJUSTEMENT_NEGATIF",
        } and self.emplacement_source_id is None:
            raise ValueError("Un emplacement source est obligatoire.")

        if self.type == "TRANSFERT":
            if (
                self.emplacement_source_id is None
                or self.emplacement_destination_id is None
            ):
                raise ValueError(
                    "Un transfert nécessite une source et une destination."
                )
            if self.emplacement_source_id == self.emplacement_destination_id:
                raise ValueError(
                    "La source et la destination doivent être différentes."
                )

        return self


class MouvementRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    reference: str
    type: str
    article_id: int
    lot_id: int | None
    emplacement_source_id: int | None
    emplacement_destination_id: int | None
    quantite: Decimal
    motif: str | None
    commentaire: str | None
    operateur: str | None
    date_creation: datetime
    article: ArticleMouvementRead
    lot: LotMouvementRead | None
    emplacement_source: EmplacementMouvementRead | None
    emplacement_destination: EmplacementMouvementRead | None
