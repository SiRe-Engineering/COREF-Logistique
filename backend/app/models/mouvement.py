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
    affaire_id: Mapped[int | None] = mapped_column(
        ForeignKey("affaires.id", ondelete="RESTRICT"),
        index=True,
        nullable=True,
    )
    inventaire_id: Mapped[int | None] = mapped_column(
        ForeignKey("inventaires.id", ondelete="RESTRICT"),
        index=True,
        nullable=True,
    )
    preparation_id: Mapped[int | None] = mapped_column(
        ForeignKey("preparations.id", ondelete="RESTRICT"),
        index=True,
        nullable=True,
    )
    besoin_reapprovisionnement_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "besoins_reapprovisionnement.id",
            ondelete="RESTRICT",
        ),
        index=True,
        nullable=True,
    )
    ligne_preparation_id: Mapped[int | None] = mapped_column(
        ForeignKey("lignes_preparation.id", ondelete="RESTRICT"),
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
    prix_unitaire_ht: Mapped[Decimal | None] = mapped_column(
        Numeric(14, 4),
        nullable=True,
    )
    cout_unitaire_applique: Mapped[Decimal] = mapped_column(
        Numeric(14, 4),
        default=0,
        nullable=False,
    )
    valeur_mouvement: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        default=0,
        nullable=False,
    )
    motif: Mapped[str | None] = mapped_column(String(150), nullable=True)
    commentaire: Mapped[str | None] = mapped_column(Text, nullable=True)
    operateur: Mapped[str | None] = mapped_column(String(120), nullable=True)
    zone_intervention: Mapped[str | None] = mapped_column(
        String(180),
        nullable=True,
    )
    charge_affaires: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )
    vehicule: Mapped[str | None] = mapped_column(String(120), nullable=True)
    sortie_libre: Mapped[bool] = mapped_column(Boolean, default=False)
    annule: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        index=True,
    )
    date_annulation: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    annule_par: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )
    motif_annulation: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    date_creation: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True,
    )

    article = relationship("Article", lazy="joined")
    lot = relationship("LotBeton", lazy="joined")
    affaire = relationship("Affaire", lazy="joined")
    inventaire = relationship(
        "Inventaire",
        foreign_keys=[inventaire_id],
        lazy="joined",
    )
    preparation = relationship(
        "Preparation",
        foreign_keys=[preparation_id],
        lazy="joined",
    )
    besoin_reapprovisionnement = relationship(
        "BesoinReapprovisionnement",
        foreign_keys=[besoin_reapprovisionnement_id],
        lazy="joined",
    )
    ligne_preparation = relationship(
        "LignePreparation",
        foreign_keys=[ligne_preparation_id],
        lazy="joined",
    )
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
