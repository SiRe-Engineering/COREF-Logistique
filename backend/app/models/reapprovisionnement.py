from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class BesoinReapprovisionnement(Base):
    __tablename__ = "besoins_reapprovisionnement"

    id: Mapped[int] = mapped_column(primary_key=True)
    reference: Mapped[str] = mapped_column(
        String(30),
        unique=True,
        server_default=text(
            "'REA-' || lpad("
            "nextval('besoin_reappro_reference_seq')::text, 6, '0')"
        ),
    )
    article_id: Mapped[int] = mapped_column(
        ForeignKey("articles.id", ondelete="RESTRICT"),
        index=True,
    )
    quantite_suggeree: Mapped[Decimal] = mapped_column(Numeric(14, 3))
    quantite_demandee: Mapped[Decimal] = mapped_column(Numeric(14, 3))
    quantite_commandee: Mapped[Decimal] = mapped_column(
        Numeric(14, 3),
        default=0,
    )
    quantite_recue: Mapped[Decimal] = mapped_column(
        Numeric(14, 3),
        default=0,
    )
    prix_unitaire_prevu: Mapped[Decimal | None] = mapped_column(
        Numeric(14, 4),
        nullable=True,
    )
    fournisseur: Mapped[str | None] = mapped_column(String(180), nullable=True)
    reference_commande: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    statut: Mapped[str] = mapped_column(
        String(30),
        default="A_TRAITER",
        index=True,
    )
    commentaire: Mapped[str | None] = mapped_column(Text, nullable=True)
    cree_par: Mapped[str | None] = mapped_column(String(150), nullable=True)
    date_creation: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    date_modification: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
    date_validation: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    date_commande: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    date_cloture: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    article = relationship("Article", lazy="joined")
