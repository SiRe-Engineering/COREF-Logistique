from app.schemas.affaire import AffaireCreate, AffaireRead, AffaireUpdate
from app.schemas.article import ArticleCreate, ArticleRead, ArticleUpdate
from app.schemas.emplacement import (
    EmplacementCreate,
    EmplacementRead,
    EmplacementUpdate,
)
from app.schemas.famille import (
    FamilleCreate,
    FamilleRead,
    FamilleUpdate,
    SousFamilleCreate,
    SousFamilleRead,
    SousFamilleUpdate,
)
from app.schemas.inventaire import (
    InventaireCreate,
    InventaireRead,
    LigneInventaireUpdate,
)
from app.schemas.lot_beton import (
    LotBetonCreate,
    LotBetonRead,
    LotBetonUpdate,
)
from app.schemas.materiel import MaterielCreate, MaterielRead, MaterielUpdate
from app.schemas.mouvement import MouvementCreate, MouvementRead
from app.schemas.preparation import (
    LignePreparationCreate,
    LignePreparationRead,
    LignePreparationUpdate,
    PreparationCreate,
    PreparationRead,
    PreparationUpdate,
)
from app.schemas.reservation import NotificationRead, ReservationRead
from app.schemas.stock import StockRead, StockResume, StockSet

__all__ = [
    "AffaireCreate",
    "AffaireRead",
    "AffaireUpdate",
    "ArticleCreate",
    "ArticleRead",
    "ArticleUpdate",
    "EmplacementCreate",
    "EmplacementRead",
    "EmplacementUpdate",
    "FamilleCreate",
    "FamilleRead",
    "FamilleUpdate",
    "InventaireCreate",
    "InventaireRead",
    "LigneInventaireUpdate",
    "LignePreparationCreate",
    "LignePreparationRead",
    "LignePreparationUpdate",
    "LotBetonCreate",
    "LotBetonRead",
    "LotBetonUpdate",
    "MaterielCreate",
    "MaterielRead",
    "MaterielUpdate",
    "MouvementCreate",
    "MouvementRead",
    "NotificationRead",
    "PreparationCreate",
    "PreparationRead",
    "PreparationUpdate",
    "ReservationRead",
    "SousFamilleCreate",
    "SousFamilleRead",
    "SousFamilleUpdate",
    "StockRead",
    "StockResume",
    "StockSet",
]
