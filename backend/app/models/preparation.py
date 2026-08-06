from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    Date,
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


class Preparation(Base):
    __tablename__ = "preparations"

    id: Mapped[int] = mapped_column(primary_key=True)
    reference: Mapped[str] = mapped_column(
        String(30),
        unique=True,
        server_default=text(
            "'PREP-' || lpad(nextval('preparation_reference_seq')::text, 6, '0')"
        ),
    )
    affaire_id: Mapped[int] = mapped_column(
        ForeignKey("affaires.id", ondelete="RESTRICT"),
        index=True,
    )
    nom: Mapped[str] = mapped_column(String(200))
    statut: Mapped[str] = mapped_column(
        String(30),
        default="BROUILLON",
        index=True,
    )
    date_besoin: Mapped[date | None] = mapped_column(Date, nullable=True)
    demandeur: Mapped[str | None] = mapped_column(String(120), nullable=True)
    preparateur: Mapped[str | None] = mapped_column(String(120), nullable=True)
    vehicule: Mapped[str | None] = mapped_column(String(120), nullable=True)
    commentaire: Mapped[str | None] = mapped_column(Text, nullable=True)
    date_creation: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    date_validation: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    date_expedition: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    affaire = relationship("Affaire", lazy="joined")
    lignes = relationship(
        "LignePreparation",
        back_populates="preparation",
        cascade="all, delete-orphan",
        order_by="LignePreparation.id",
    )


class LignePreparation(Base):
    __tablename__ = "lignes_preparation"
    __table_args__ = (
        CheckConstraint(
            "quantite_demandee > 0",
            name="ck_lignes_preparation_quantite_demandee_positive",
        ),
        CheckConstraint(
            "quantite_preparee >= 0",
            name="ck_lignes_preparation_quantite_preparee_positive",
        ),
        CheckConstraint(
            "quantite_manquante >= 0",
            name="ck_lignes_preparation_quantite_manquante_positive",
        ),
        CheckConstraint(
            "statut IN ("
            "'A_PREPARER', "
            "'PREPAREE', "
            "'PARTIELLE', "
            "'INDISPONIBLE', "
            "'EXPEDIEE'"
            ")",
            name="ck_lignes_preparation_statut_execution",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    preparation_id: Mapped[int] = mapped_column(
        ForeignKey("preparations.id", ondelete="CASCADE"),
        index=True,
    )
    article_id: Mapped[int] = mapped_column(
        ForeignKey("articles.id", ondelete="RESTRICT"),
    )
    lot_id: Mapped[int | None] = mapped_column(
        ForeignKey("lots_beton.id", ondelete="RESTRICT"),
        nullable=True,
    )
    emplacement_source_id: Mapped[int | None] = mapped_column(
        ForeignKey("emplacements.id", ondelete="RESTRICT"),
        nullable=True,
    )
    quantite_demandee: Mapped[Decimal] = mapped_column(Numeric(14, 3))
    quantite_preparee: Mapped[Decimal] = mapped_column(
        Numeric(14, 3),
        default=0,
    )
    quantite_manquante: Mapped[Decimal] = mapped_column(
        Numeric(14, 3),
        default=0,
    )
    statut: Mapped[str] = mapped_column(
        String(30),
        default="A_PREPARER",
        index=True,
    )
    commentaire: Mapped[str | None] = mapped_column(String(255), nullable=True)
    motif_ecart: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )
    date_debut_preparation: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    date_fin_preparation: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    preparation = relationship("Preparation", back_populates="lignes")
    article = relationship("Article", lazy="joined")
    lot = relationship("LotBeton", lazy="joined")
    emplacement_source = relationship("Emplacement", lazy="joined")
