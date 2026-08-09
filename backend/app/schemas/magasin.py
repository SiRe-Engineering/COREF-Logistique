from decimal import Decimal

from pydantic import BaseModel


class ScanEmplacementRead(BaseModel):
    id: int
    code: str
    nom: str
    quantite_physique: Decimal
    quantite_reservee: Decimal
    quantite_disponible: Decimal


class ScanLotRead(BaseModel):
    id: int
    reference_interne: str
    numero_lot_fournisseur: str
    article_id: int
    article_reference: str
    article_designation: str
    unite: str
    date_peremption: str
    emplacements: list[ScanEmplacementRead]


class ScanArticleRead(BaseModel):
    id: int
    reference: str
    designation: str
    unite: str
    famille: str | None
    sous_famille: str | None
    quantite_physique: Decimal
    quantite_reservee: Decimal
    quantite_disponible: Decimal
    emplacements: list[ScanEmplacementRead]


class ScanResultatRead(BaseModel):
    type: str
    valeur: str
    article: ScanArticleRead | None = None
    lot: ScanLotRead | None = None
