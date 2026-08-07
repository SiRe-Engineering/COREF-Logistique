from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel


class ValorisationResumeRead(BaseModel):
    valeur_physique: Decimal
    valeur_reservee: Decimal
    valeur_disponible: Decimal
    variation_mensuelle_pct: Decimal | None


class ValorisationHistoriqueRead(BaseModel):
    mois: date
    valeur_physique: Decimal
    valeur_reservee: Decimal
    valeur_disponible: Decimal
    date_mise_a_jour: datetime


class ValorisationFamilleRead(BaseModel):
    famille_id: int | None
    famille: str
    valeur_physique: Decimal
    valeur_reservee: Decimal
    valeur_disponible: Decimal
    part_physique_pct: Decimal


class ValorisationRead(BaseModel):
    resume: ValorisationResumeRead
    historique: list[ValorisationHistoriqueRead]
    familles: list[ValorisationFamilleRead]
