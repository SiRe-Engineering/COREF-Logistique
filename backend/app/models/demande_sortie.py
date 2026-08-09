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


class DemandeSortie(Base):
    __tablename__ = "demandes_sortie"
    __table_args__ = (
        CheckConstraint(
            "quantite > 0",
            name="ck_demandes_sortie_quantite_positive",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    reference: Mapped[str] = mapped_column(
        String(30),
        unique=True,
        server_default=text(
            "'DS-' || lpad(nextval('demande_sortie_reference_seq')::text, 6, '0')"
        ),
    )
    demandeur_id: Mapped[int] = mapped_column(
        ForeignKey("utilisateurs.id", ondelete="RESTRICT"),
        index=True,
    )
    validateur_id: Mapped[int | None] = mapped_column(
        ForeignKey("utilisateurs.id", ondelete="RESTRICT"),
        index=True,
        nullable=True,
    )
    article_id: Mapped[int] = mapped_column(
        ForeignKey("articles.id", ondelete="RESTRICT"),
    )
    lot_id: Mapped[int | None] = mapped_column(
        ForeignKey("lots_beton.id", ondelete="RESTRICT"),
        nullable=True,
    )
    emplacement_source_id: Mapped[int] = mapped_column(
        ForeignKey("emplacements.id", ondelete="RESTRICT"),
    )
    affaire_id: Mapped[int | None] = mapped_column(
        ForeignKey("affaires.id", ondelete="RESTRICT"),
        nullable=True,
    )
    quantite: Mapped[Decimal] = mapped_column(Numeric(14, 3))
    vehicule: Mapped[str | None] = mapped_column(String(120), nullable=True)
    motif: Mapped[str] = mapped_column(String(255))
    commentaire: Mapped[str | None] = mapped_column(Text, nullable=True)
    statut: Mapped[str] = mapped_column(String(30), default="EN_ATTENTE", index=True)
    date_creation: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    date_decision: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    motif_refus: Mapped[str | None] = mapped_column(Text, nullable=True)

    demandeur = relationship("Utilisateur", foreign_keys=[demandeur_id], lazy="joined")
    validateur = relationship("Utilisateur", foreign_keys=[validateur_id], lazy="joined")
    article = relationship("Article", lazy="joined")
    lot = relationship("LotBeton", lazy="joined")
    emplacement_source = relationship("Emplacement", lazy="joined")
    affaire = relationship("Affaire", lazy="joined")
