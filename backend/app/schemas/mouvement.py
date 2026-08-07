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


class AffaireMouvementRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    reference: str
    code_externe: str | None
    nom: str
    client: str | None
    site: str | None


class MouvementCreate(BaseModel):
    type: TypeMouvement
    article_id: int
    lot_id: int | None = None
    affaire_id: int | None = None
    inventaire_id: int | None = None
    preparation_id: int | None = None
    ligne_preparation_id: int | None = None
    emplacement_source_id: int | None = None
    emplacement_destination_id: int | None = None
    quantite: Decimal = Field(gt=0)
    prix_unitaire_ht: Decimal | None = Field(default=None, ge=0)
    motif: str | None = Field(default=None, max_length=150)
    commentaire: str | None = None
    operateur: str | None = Field(default=None, max_length=120)
    zone_intervention: str | None = Field(default=None, max_length=180)
    charge_affaires: str | None = Field(default=None, max_length=150)
    vehicule: str | None = Field(default=None, max_length=120)
    sortie_libre: bool = False

    @model_validator(mode="after")
    def valider_mouvement(self):
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

        if self.prix_unitaire_ht is not None and self.type != "ENTREE":
            raise ValueError(
                "Le prix unitaire HT ne peut être renseigné que sur une entrée."
            )

        if self.type == "SORTIE":
            if self.affaire_id is None and not self.sortie_libre:
                raise ValueError(
                    "Une sortie doit être rattachée à une affaire ou déclarée libre."
                )

        return self


class MouvementRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    reference: str
    type: str
    article_id: int
    lot_id: int | None
    affaire_id: int | None
    inventaire_id: int | None
    preparation_id: int | None
    ligne_preparation_id: int | None
    emplacement_source_id: int | None
    emplacement_destination_id: int | None
    quantite: Decimal
    prix_unitaire_ht: Decimal | None
    cout_unitaire_applique: Decimal
    valeur_mouvement: Decimal
    motif: str | None
    commentaire: str | None
    operateur: str | None
    zone_intervention: str | None
    charge_affaires: str | None
    vehicule: str | None
    sortie_libre: bool
    date_creation: datetime
    annule: bool
    date_annulation: datetime | None
    annule_par: str | None
    motif_annulation: str | None
    article: ArticleMouvementRead
    lot: LotMouvementRead | None
    affaire: AffaireMouvementRead | None
    emplacement_source: EmplacementMouvementRead | None
    emplacement_destination: EmplacementMouvementRead | None



class AnnulationMouvementCreate(BaseModel):
    motif: str = Field(min_length=5, max_length=1000)
