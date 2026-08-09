from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    Text,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ReservationStock(Base):
    __tablename__ = "reservations_stock"
    __table_args__ = (
        CheckConstraint(
            "quantite > 0",
            name="ck_reservations_quantite_positive",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    reference: Mapped[str] = mapped_column(
        String(30),
        unique=True,
        server_default=text(
            "'RES-' || lpad(nextval('reservation_reference_seq')::text, 6, '0')"
        ),
    )
    article_id: Mapped[int] = mapped_column(
        ForeignKey("articles.id", ondelete="RESTRICT"),
        index=True,
    )
    lot_id: Mapped[int | None] = mapped_column(
        ForeignKey("lots_beton.id", ondelete="RESTRICT"),
        nullable=True,
    )
    emplacement_id: Mapped[int] = mapped_column(
        ForeignKey("emplacements.id", ondelete="RESTRICT"),
        index=True,
    )
    preparation_id: Mapped[int | None] = mapped_column(
        ForeignKey("preparations.id", ondelete="CASCADE"),
        index=True,
        nullable=True,
    )
    ligne_preparation_id: Mapped[int | None] = mapped_column(
        ForeignKey("lignes_preparation.id", ondelete="CASCADE"),
        unique=True,
        nullable=True,
    )
    quantite: Mapped[Decimal] = mapped_column(Numeric(14, 3))
    reserve_pour: Mapped[str] = mapped_column(String(200))
    reserve_par: Mapped[str | None] = mapped_column(String(120), nullable=True)
    motif: Mapped[str | None] = mapped_column(String(255), nullable=True)
    statut: Mapped[str] = mapped_column(String(30), default="ACTIVE", index=True)
    date_creation: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    date_liberation: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    article = relationship("Article", lazy="joined")
    lot = relationship("LotBeton", lazy="joined")
    emplacement = relationship("Emplacement", lazy="joined")
    preparation = relationship("Preparation", lazy="joined")


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(primary_key=True)
    destinataire: Mapped[str] = mapped_column(String(120), index=True)
    titre: Mapped[str] = mapped_column(String(180))
    message: Mapped[str] = mapped_column(Text)
    type: Mapped[str] = mapped_column(String(40), default="INFORMATION")
    lien: Mapped[str | None] = mapped_column(String(255), nullable=True)
    lue: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    date_creation: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    date_lecture: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
