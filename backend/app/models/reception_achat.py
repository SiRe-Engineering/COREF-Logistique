from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ReceptionAchat(Base):
    __tablename__ = "receptions_achat"

    id: Mapped[int] = mapped_column(primary_key=True)
    commande_id: Mapped[int] = mapped_column(
        ForeignKey("commandes_achat.id", ondelete="RESTRICT"),
        index=True,
    )
    ligne_commande_id: Mapped[int] = mapped_column(
        ForeignKey("lignes_commandes_achat.id", ondelete="RESTRICT"),
        index=True,
    )
    article_id: Mapped[int] = mapped_column(
        ForeignKey("articles.id", ondelete="RESTRICT"),
    )
    lot_beton_id: Mapped[int | None] = mapped_column(
        ForeignKey("lots_beton.id", ondelete="SET NULL"),
        nullable=True,
    )
    quantite: Mapped[Decimal] = mapped_column(Numeric(14, 3))
    bon_livraison_reference: Mapped[str | None] = mapped_column(
        String(120),
        nullable=True,
    )
    conformite_visuelle: Mapped[str] = mapped_column(String(30))
    reserve_commentaire: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    commentaire_qualite: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    fds_presente: Mapped[bool | None] = mapped_column(
        Boolean,
        nullable=True,
    )
    statut_qualite: Mapped[str] = mapped_column(
        String(30),
        index=True,
    )
    receptionne_par: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )
    date_reception: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    commande = relationship("CommandeAchat", lazy="joined")
    ligne_commande = relationship("LigneCommandeAchat", lazy="joined")
    article = relationship("Article", lazy="joined")
    lot_beton = relationship("LotBeton", lazy="joined")
