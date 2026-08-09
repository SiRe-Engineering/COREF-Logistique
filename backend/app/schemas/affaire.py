from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

StatutAffaire = Literal["OUVERTE", "EN_PREPARATION", "EN_COURS", "TERMINEE", "ANNULEE"]


class AffaireBase(BaseModel):
    code_externe: str | None = Field(default=None, max_length=80)
    nom: str = Field(min_length=1, max_length=200)
    client: str | None = Field(default=None, max_length=180)
    site: str | None = Field(default=None, max_length=180)
    zone_intervention: str | None = Field(default=None, max_length=180)
    charge_affaires: str | None = Field(default=None, max_length=150)
    statut: StatutAffaire = "OUVERTE"
    date_debut: date | None = None
    date_fin_prevue: date | None = None
    commentaire: str | None = None

    @model_validator(mode="after")
    def valider_dates(self):
        if (
            self.date_debut is not None
            and self.date_fin_prevue is not None
            and self.date_fin_prevue < self.date_debut
        ):
            raise ValueError(
                "La date de fin prévue doit être postérieure à la date de début."
            )
        return self


class AffaireCreate(AffaireBase):
    pass


class AffaireUpdate(BaseModel):
    code_externe: str | None = Field(default=None, max_length=80)
    nom: str | None = Field(default=None, min_length=1, max_length=200)
    client: str | None = Field(default=None, max_length=180)
    site: str | None = Field(default=None, max_length=180)
    zone_intervention: str | None = Field(default=None, max_length=180)
    charge_affaires: str | None = Field(default=None, max_length=150)
    statut: StatutAffaire | None = None
    date_debut: date | None = None
    date_fin_prevue: date | None = None
    commentaire: str | None = None
    actif: bool | None = None


class AffaireRead(AffaireBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    reference: str
    actif: bool
    date_creation: datetime
    date_modification: datetime
