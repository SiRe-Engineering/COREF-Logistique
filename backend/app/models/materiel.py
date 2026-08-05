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
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Materiel(Base):
    __tablename__ = "materiels"
    __table_args__ = (
        CheckConstraint(
            "date_prochain_controle IS NULL OR date_dernier_controle IS NULL OR date_prochain_controle >= date_dernier_controle",
            name="ck_materiels_dates_controle",
        ),
        CheckConstraint(
            "valeur_achat IS NULL OR valeur_achat >= 0",
            name="ck_materiels_valeur_positive",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    numero_inventaire: Mapped[str] = mapped_column(
        String(30),
        unique=True,
        server_default=text(
            "'MAT-' || lpad(nextval('materiel_reference_seq')::text, 6, '0')"
        ),
    )
    designation: Mapped[str] = mapped_column(String(200), index=True)
    categorie: Mapped[str] = mapped_column(String(80), index=True)
    marque: Mapped[str | None] = mapped_column(String(120), nullable=True)
    modele: Mapped[str | None] = mapped_column(String(120), nullable=True)
    numero_serie: Mapped[str | None] = mapped_column(
        String(150),
        unique=True,
        nullable=True,
    )
    etat: Mapped[str] = mapped_column(
        String(30),
        default="DISPONIBLE",
        index=True,
    )
    emplacement_id: Mapped[int | None] = mapped_column(
        ForeignKey("emplacements.id", ondelete="RESTRICT"),
        index=True,
        nullable=True,
    )
    affaire_id: Mapped[int | None] = mapped_column(
        ForeignKey("affaires.id", ondelete="RESTRICT"),
        index=True,
        nullable=True,
    )
    date_achat: Mapped[date | None] = mapped_column(Date, nullable=True)
    valeur_achat: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2),
        nullable=True,
    )
    date_dernier_controle: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )
    date_prochain_controle: Mapped[date | None] = mapped_column(
        Date,
        index=True,
        nullable=True,
    )
    type_controle: Mapped[str | None] = mapped_column(
        String(120),
        nullable=True,
    )
    commentaire: Mapped[str | None] = mapped_column(Text, nullable=True)
    actif: Mapped[bool] = mapped_column(Boolean, default=True)
    date_creation: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    date_modification: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    emplacement = relationship("Emplacement", lazy="joined")
    affaire = relationship("Affaire", lazy="joined")
