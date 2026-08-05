from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ArticleStockRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    reference: str
    designation: str
    unite: str
    stock_minimum: Decimal
    stock_maximum: Decimal
    seuil_alerte: Decimal


class EmplacementStockRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    nom: str
    type: str


class StockSet(BaseModel):
    article_id: int
    emplacement_id: int
    quantite_physique: Decimal = Field(ge=0)
    quantite_reservee: Decimal = Field(default=0, ge=0)

    @model_validator(mode="after")
    def valider_quantites(self):
        if self.quantite_reservee > self.quantite_physique:
            raise ValueError(
                "La quantité réservée ne peut pas dépasser la quantité physique."
            )
        return self


class StockRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    article_id: int
    emplacement_id: int
    quantite_physique: Decimal
    quantite_reservee: Decimal
    quantite_disponible: Decimal
    date_modification: datetime
    article: ArticleStockRead
    emplacement: EmplacementStockRead


class StockResume(BaseModel):
    lignes_stock: int
    articles_stockes: int
    ruptures: int
    alertes: int
