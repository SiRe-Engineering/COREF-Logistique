from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
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


class MouvementStock(Base):
    __tablename__ = "mouvements_stock"
    __table_args__ = (
        CheckConstraint(
            "quantite > 0",
            name="ck_mouvements_quantite_positive",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    reference: Mapped[str] = mapped_column(
        String(30),
        unique=True,
        server_default=text(
            "'MVT-' || lpad(nextval('mouvement_reference_seq')::text, 6, '0')"
        ),
    )
    type: Mapped[str] = mapped_column(String(30), index=True)
    article_id: Mapped[int] = mapped_column(
        ForeignKey("articles.id", ondelete="RESTRICT"),
        index=True,
    )
    lot_id: Mapped[int | None] = mapped_column(
        ForeignKey("lots_beton.id", ondelete="RESTRICT"),
        index=True,
        nullable=True,
    )
    emplacement_source_id: Mapped[int | None] = mapped_column(
        ForeignKey("emplacements.id", ondelete="RESTRICT"),
        index=True,
        nullable=True,
    )
    emplacement_destination_id: Mapped[int | None] = mapped_column(
        ForeignKey("emplacements.id", ondelete="RESTRICT"),
        index=True,
        nullable=True,
    )
    quantite: Mapped[Decimal] = mapped_column(Numeric(14, 3))
    motif: Mapped[str | None] = mapped_column(String(150), nullable=True)
    commentaire: Mapped[str | None] = mapped_column(Text, nullable=True)
    operateur: Mapped[str | None] = mapped_column(String(120), nullable=True)
    date_creation: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True,
    )

    article = relationship("Article", lazy="joined")
    lot = relationship("LotBeton", lazy="joined")
    emplacement_source = relationship(
        "Emplacement",
        foreign_keys=[emplacement_source_id],
        lazy="joined",
    )
    emplacement_destination = relationship(
        "Emplacement",
        foreign_keys=[emplacement_destination_id],
        lazy="joined",
    )
