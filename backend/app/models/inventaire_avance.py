from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    Date,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class CampagneInventaireAvance(Base):
    __tablename__ = "campagnes_inventaire_avance"

    id: Mapped[int] = mapped_column(primary_key=True)
    reference: Mapped[str] = mapped_column(String(30), unique=True)
    libelle: Mapped[str] = mapped_column(String(180))
    statut: Mapped[str] = mapped_column(String(30), default="BROUILLON")
    date_creation: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    date_comptage: Mapped[date | None] = mapped_column(Date, nullable=True)
    date_validation: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    cree_par: Mapped[str | None] = mapped_column(String(150), nullable=True)
    valide_par: Mapped[str | None] = mapped_column(String(150), nullable=True)
    commentaire: Mapped[str | None] = mapped_column(Text, nullable=True)

    lignes = relationship(
        "app.models.inventaire_avance.LigneInventaireAvance",
        back_populates="campagne",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class LigneInventaireAvance(Base):
    __tablename__ = "lignes_inventaire_avance"
    __table_args__ = (
        UniqueConstraint(
            "campagne_id",
            "article_id",
            "emplacement_id",
            name="uq_inventaire_avance_article_emplacement",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    campagne_id: Mapped[int] = mapped_column(
        ForeignKey(
            "campagnes_inventaire_avance.id",
            ondelete="CASCADE",
        ),
        index=True,
    )
    article_id: Mapped[int] = mapped_column(
        ForeignKey("articles.id", ondelete="RESTRICT"),
        index=True,
    )
    emplacement_id: Mapped[int] = mapped_column(
        ForeignKey("emplacements.id", ondelete="RESTRICT")
    )
    quantite_theorique: Mapped[Decimal] = mapped_column(Numeric(14, 3))
    quantite_comptee: Mapped[Decimal | None] = mapped_column(
        Numeric(14, 3),
        nullable=True,
    )
    prix_unitaire: Mapped[Decimal] = mapped_column(
        Numeric(14, 4),
        default=0,
    )
    justification: Mapped[str | None] = mapped_column(Text, nullable=True)
    compte_par: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )
    date_comptage: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    campagne = relationship(
        "app.models.inventaire_avance.CampagneInventaireAvance",
        back_populates="lignes",
    )
    article = relationship("Article", lazy="joined")
    emplacement = relationship("Emplacement", lazy="joined")
