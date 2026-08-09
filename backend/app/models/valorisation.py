from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, Numeric, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class SnapshotValorisationStock(Base):
    __tablename__ = "snapshots_valorisation_stock"
    __table_args__ = (
        UniqueConstraint(
            "mois",
            name="uq_snapshots_valorisation_stock_mois",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    mois: Mapped[date] = mapped_column(Date, unique=True, index=True)
    valeur_physique: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        default=0,
        nullable=False,
    )
    valeur_reservee: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        default=0,
        nullable=False,
    )
    valeur_disponible: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        default=0,
        nullable=False,
    )
    date_mise_a_jour: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
