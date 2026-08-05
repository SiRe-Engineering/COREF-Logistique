from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    String,
    Text,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Affaire(Base):
    __tablename__ = "affaires"
    __table_args__ = (
        CheckConstraint(
            "date_fin_prevue IS NULL OR date_debut IS NULL OR date_fin_prevue >= date_debut",
            name="ck_affaires_dates_coherentes",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    reference: Mapped[str] = mapped_column(
        String(30),
        unique=True,
        server_default=text(
            "'AFF-' || lpad(nextval('affaire_reference_seq')::text, 6, '0')"
        ),
    )
    code_externe: Mapped[str | None] = mapped_column(
        String(80),
        unique=True,
        nullable=True,
    )
    nom: Mapped[str] = mapped_column(String(200))
    client: Mapped[str | None] = mapped_column(String(180), index=True)
    site: Mapped[str | None] = mapped_column(String(180), nullable=True)
    zone_intervention: Mapped[str | None] = mapped_column(
        String(180),
        nullable=True,
    )
    charge_affaires: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )
    statut: Mapped[str] = mapped_column(
        String(30),
        default="OUVERTE",
        index=True,
    )
    date_debut: Mapped[date | None] = mapped_column(Date, nullable=True)
    date_fin_prevue: Mapped[date | None] = mapped_column(Date, nullable=True)
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
