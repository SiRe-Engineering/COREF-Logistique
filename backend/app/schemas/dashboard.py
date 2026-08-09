from datetime import date
from decimal import Decimal

from pydantic import BaseModel


class DashboardKpiRead(BaseModel):
    articles_actifs: int
    ruptures: int
    stocks_sous_seuil: int
    lots_a_perimer: int
    preparations_a_traiter: int
    preparations_en_retard: int
    inventaires_en_cours: int
    retours_en_attente: int
    valeur_stock_physique: Decimal
    valeur_stock_reservee: Decimal
    valeur_stock_disponible: Decimal
    valeur_lots_a_perimer: Decimal


class DashboardStockAlerteRead(BaseModel):
    article_id: int
    reference: str
    designation: str
    unite: str
    disponible: Decimal
    seuil: Decimal
    niveau: str


class DashboardLotAlerteRead(BaseModel):
    lot_id: int
    reference_interne: str
    numero_lot_fournisseur: str
    article_reference: str
    article_designation: str
    date_peremption: date
    jours_restants: int
    quantite_physique: Decimal
    niveau: str


class DashboardPreparationRead(BaseModel):
    id: int
    reference: str
    nom: str
    statut: str
    date_besoin: date | None
    demandeur: str | None
    preparateur: str | None
    en_retard: bool
    lignes_bloquees: int


class DashboardInventaireRead(BaseModel):
    id: int
    reference: str
    nom: str
    operateur: str | None
    lignes_total: int
    lignes_comptees: int


class DashboardRead(BaseModel):
    date_reference: date
    kpis: DashboardKpiRead
    stocks: list[DashboardStockAlerteRead]
    lots: list[DashboardLotAlerteRead]
    preparations: list[DashboardPreparationRead]
    inventaires: list[DashboardInventaireRead]
