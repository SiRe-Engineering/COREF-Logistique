from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class LotBeton(Base):
    __tablename__ = "lots_beton"
    __table_args__ = (
        UniqueConstraint(
            "article_id",
            "numero_lot_fournisseur",
            name="uq_lots_beton_article_numero_fournisseur",
        ),
        CheckConstraint(
            "date_peremption >= date_fabrication",
            name="ck_lots_beton_dates_coherentes",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    reference_interne: Mapped[str] = mapped_column(
        String(30),
        unique=True,
        server_default=text(
            "'LOT-' || lpad(nextval('lot_beton_reference_seq')::text, 6, '0')"
        ),
    )
    article_id: Mapped[int] = mapped_column(
        ForeignKey("articles.id", ondelete="RESTRICT"),
        index=True,
    )
    numero_lot_fournisseur: Mapped[str] = mapped_column(String(120))
    date_fabrication: Mapped[date] = mapped_column(Date)
    date_peremption: Mapped[date] = mapped_column(Date, index=True)
    fournisseur: Mapped[str | None] = mapped_column(String(180), nullable=True)
    certificat_reference: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    fds_reference: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    commentaire: Mapped[str | None] = mapped_column(Text, nullable=True)
    actif: Mapped[bool] = mapped_column(Boolean, default=True)
    supprime: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        index=True,
    )
    date_suppression: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    supprime_par: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )
    motif_suppression: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    date_creation: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    date_modification: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    article = relationship("Article", lazy="joined")
    stocks = relationship(
        "StockLot",
        back_populates="lot",
        order_by="StockLot.emplacement_id",
    )


class StockLot(Base):
    __tablename__ = "stocks_lots"
    __table_args__ = (
        UniqueConstraint(
            "lot_id",
            "emplacement_id",
            name="uq_stocks_lots_lot_emplacement",
        ),
        CheckConstraint(
            "quantite_physique >= 0",
            name="ck_stocks_lots_quantite_physique_positive",
        ),
        CheckConstraint(
            "quantite_reservee >= 0",
            name="ck_stocks_lots_quantite_reservee_positive",
        ),
        CheckConstraint(
            "quantite_reservee <= quantite_physique",
            name="ck_stocks_lots_reservee_inferieure_physique",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    lot_id: Mapped[int] = mapped_column(
        ForeignKey("lots_beton.id", ondelete="RESTRICT"),
        index=True,
    )
    emplacement_id: Mapped[int] = mapped_column(
        ForeignKey("emplacements.id", ondelete="RESTRICT"),
        index=True,
    )
    quantite_physique: Mapped[Decimal] = mapped_column(
        Numeric(14, 3),
        default=0,
    )
    quantite_reservee: Mapped[Decimal] = mapped_column(
        Numeric(14, 3),
        default=0,
    )
    date_modification: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    lot = relationship("LotBeton", back_populates="stocks")
    emplacement = relationship("Emplacement", lazy="joined")

    @property
    def quantite_disponible(self) -> Decimal:
        return self.quantite_physique - self.quantite_reservee
