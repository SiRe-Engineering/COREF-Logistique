from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class ReservationArticleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    reference: str
    designation: str
    unite: str


class ReservationLotRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    numero_lot_fournisseur: str


class ReservationEmplacementRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    nom: str


class ReservationPreparationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    reference: str
    nom: str


class ReservationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    reference: str
    article_id: int
    lot_id: int | None
    emplacement_id: int
    preparation_id: int | None
    ligne_preparation_id: int | None
    quantite: Decimal
    reserve_pour: str
    reserve_par: str | None
    motif: str | None
    statut: str
    date_creation: datetime
    date_liberation: datetime | None
    article: ReservationArticleRead
    lot: ReservationLotRead | None
    emplacement: ReservationEmplacementRead
    preparation: ReservationPreparationRead | None


class NotificationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    destinataire: str
    titre: str
    message: str
    type: str
    lien: str | None
    lue: bool
    date_creation: datetime
    date_lecture: datetime | None
