from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

EtatMateriel = Literal[
    "DISPONIBLE",
    "EN_CHANTIER",
    "EN_MAINTENANCE",
    "HORS_SERVICE",
    "PERDU",
]


class EmplacementMaterielRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    nom: str


class AffaireMaterielRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    reference: str
    code_externe: str | None
    nom: str


class MaterielBase(BaseModel):
    designation: str = Field(min_length=1, max_length=200)
    categorie: str = Field(min_length=1, max_length=80)
    marque: str | None = Field(default=None, max_length=120)
    modele: str | None = Field(default=None, max_length=120)
    numero_serie: str | None = Field(default=None, max_length=150)
    etat: EtatMateriel = "DISPONIBLE"
    emplacement_id: int | None = None
    affaire_id: int | None = None
    date_achat: date | None = None
    valeur_achat: Decimal | None = Field(default=None, ge=0)
    date_dernier_controle: date | None = None
    date_prochain_controle: date | None = None
    type_controle: str | None = Field(default=None, max_length=120)
    commentaire: str | None = None

    @model_validator(mode="after")
    def valider_coherence(self):
        if (
            self.date_dernier_controle is not None
            and self.date_prochain_controle is not None
            and self.date_prochain_controle < self.date_dernier_controle
        ):
            raise ValueError(
                "La prochaine échéance doit être postérieure au dernier contrôle."
            )

        if self.etat == "EN_CHANTIER" and self.affaire_id is None:
            raise ValueError(
                "Un matériel en chantier doit être affecté à une affaire."
            )

        return self


class MaterielCreate(MaterielBase):
    pass


class MaterielUpdate(BaseModel):
    designation: str | None = Field(default=None, min_length=1, max_length=200)
    categorie: str | None = Field(default=None, min_length=1, max_length=80)
    marque: str | None = Field(default=None, max_length=120)
    modele: str | None = Field(default=None, max_length=120)
    numero_serie: str | None = Field(default=None, max_length=150)
    etat: EtatMateriel | None = None
    emplacement_id: int | None = None
    affaire_id: int | None = None
    date_achat: date | None = None
    valeur_achat: Decimal | None = Field(default=None, ge=0)
    date_dernier_controle: date | None = None
    date_prochain_controle: date | None = None
    type_controle: str | None = Field(default=None, max_length=120)
    commentaire: str | None = None
    actif: bool | None = None


class MaterielRead(MaterielBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    numero_inventaire: str
    actif: bool
    date_creation: datetime
    date_modification: datetime
    emplacement: EmplacementMaterielRead | None
    affaire: AffaireMaterielRead | None
