from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ArticleLotRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    reference: str
    designation: str
    unite: str


class EmplacementLotRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    nom: str


class StockLotRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    lot_id: int
    emplacement_id: int
    quantite_physique: Decimal
    quantite_reservee: Decimal
    quantite_disponible: Decimal
    date_modification: datetime
    emplacement: EmplacementLotRead


class SuppressionLotCreate(BaseModel):
    motif: str = Field(min_length=5, max_length=1000)


class LotBetonCreate(BaseModel):
    article_id: int
    numero_lot_fournisseur: str = Field(min_length=1, max_length=120)
    date_fabrication: date
    date_peremption: date
    fournisseur: str | None = Field(default=None, max_length=180)
    certificat_reference: str | None = Field(default=None, max_length=255)
    fds_reference: str | None = Field(default=None, max_length=255)
    commentaire: str | None = None

    @model_validator(mode="after")
    def valider_dates(self):
        if self.date_peremption < self.date_fabrication:
            raise ValueError(
                "La date de péremption doit être postérieure à la fabrication."
            )
        return self


class LotBetonUpdate(BaseModel):
    numero_lot_fournisseur: str | None = Field(
        default=None,
        min_length=1,
        max_length=120,
    )
    date_fabrication: date | None = None
    date_peremption: date | None = None
    fournisseur: str | None = Field(default=None, max_length=180)
    certificat_reference: str | None = Field(default=None, max_length=255)
    fds_reference: str | None = Field(default=None, max_length=255)
    commentaire: str | None = None
    actif: bool | None = None


class LotBetonRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    reference_interne: str
    article_id: int
    numero_lot_fournisseur: str
    date_fabrication: date
    date_peremption: date
    fournisseur: str | None
    certificat_reference: str | None
    fds_reference: str | None
    commentaire: str | None
    actif: bool
    supprime: bool
    date_suppression: datetime | None
    supprime_par: str | None
    motif_suppression: str | None
    date_creation: datetime
    date_modification: datetime
    article: ArticleLotRead
    stocks: list[StockLotRead] = []
