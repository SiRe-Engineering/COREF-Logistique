from datetime import date

import pytest
from pydantic import ValidationError

from app.schemas.lot_beton import LotBetonCreate


def test_lot_dates_valides() -> None:
    lot = LotBetonCreate(
        article_id=1,
        numero_lot_fournisseur="LOT-2026-001",
        date_fabrication=date(2026, 8, 1),
        date_peremption=date(2027, 2, 1),
    )
    assert lot.numero_lot_fournisseur == "LOT-2026-001"


def test_peremption_avant_fabrication_refusee() -> None:
    with pytest.raises(ValidationError):
        LotBetonCreate(
            article_id=1,
            numero_lot_fournisseur="LOT-2026-002",
            date_fabrication=date(2026, 8, 1),
            date_peremption=date(2026, 7, 31),
        )
