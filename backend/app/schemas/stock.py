from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


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
    lot_id: int | None = None
    emplacement_id: int
    quantite_physique: Decimal = Field(ge=0)


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
