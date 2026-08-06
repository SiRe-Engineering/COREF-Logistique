from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
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


class Inventaire(Base):
    __tablename__ = "inventaires"

    id: Mapped[int] = mapped_column(primary_key=True)
    reference: Mapped[str] = mapped_column(
        String(30),
        unique=True,
        server_default=text(
            "'INV-' || lpad(nextval('inventaire_reference_seq')::text, 6, '0')"
        ),
    )
    nom: Mapped[str] = mapped_column(String(180))
    type: Mapped[str] = mapped_column(
        String(30),
        default="EMPLACEMENT",
        index=True,
    )
    emplacement_id: Mapped[int | None] = mapped_column(
        ForeignKey("emplacements.id", ondelete="RESTRICT"),
        index=True,
        nullable=True,
    )
    famille_id: Mapped[int | None] = mapped_column(
        ForeignKey("familles.id", ondelete="RESTRICT"),
        index=True,
        nullable=True,
    )
    statut: Mapped[str] = mapped_column(
        String(30),
        default="EN_COURS",
        index=True,
    )
    operateur: Mapped[str | None] = mapped_column(
        String(120),
        nullable=True,
    )
    valide_par: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )
    commentaire: Mapped[str | None] = mapped_column(Text, nullable=True)
    date_creation: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    date_validation: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    emplacement = relationship("Emplacement", lazy="joined")
    famille = relationship("Famille", lazy="joined")
    lignes = relationship(
        "LigneInventaire",
        back_populates="inventaire",
        cascade="all, delete-orphan",
        order_by=(
            "LigneInventaire.emplacement_id, "
            "LigneInventaire.article_id, "
            "LigneInventaire.lot_id"
        ),
    )


class LigneInventaire(Base):
    __tablename__ = "lignes_inventaire"
    __table_args__ = (
        UniqueConstraint(
            "inventaire_id",
            "emplacement_id",
            "article_id",
            "lot_id",
            name="uq_lignes_inventaire_emplacement_article_lot",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    inventaire_id: Mapped[int] = mapped_column(
        ForeignKey("inventaires.id", ondelete="CASCADE"),
        index=True,
    )
    emplacement_id: Mapped[int] = mapped_column(
        ForeignKey("emplacements.id", ondelete="RESTRICT"),
        index=True,
    )
    article_id: Mapped[int] = mapped_column(
        ForeignKey("articles.id", ondelete="RESTRICT"),
    )
    lot_id: Mapped[int | None] = mapped_column(
        ForeignKey("lots_beton.id", ondelete="RESTRICT"),
        nullable=True,
    )
    quantite_theorique: Mapped[Decimal] = mapped_column(
        Numeric(14, 3),
        default=0,
    )
    quantite_comptee: Mapped[Decimal | None] = mapped_column(
        Numeric(14, 3),
        nullable=True,
    )
    commentaire: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    inventaire = relationship("Inventaire", back_populates="lignes")
    emplacement = relationship("Emplacement", lazy="joined")
    article = relationship("Article", lazy="joined")
    lot = relationship("LotBeton", lazy="joined")

    @property
    def ecart(self) -> Decimal | None:
        if self.quantite_comptee is None:
            return None
        return self.quantite_comptee - self.quantite_theorique

    @property
    def pourcentage_ecart(self) -> Decimal | None:
        if self.quantite_comptee is None:
            return None
        if self.quantite_theorique == 0:
            return Decimal("100") if self.quantite_comptee else Decimal("0")
        return (
            (self.quantite_comptee - self.quantite_theorique)
            / self.quantite_theorique
            * Decimal("100")
        )
